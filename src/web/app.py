"""
Professional web interface for YeuMoney system
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional

from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash

from src.core.config import config
from src.core.database import db
from src.api.client import api_client
from src.models.models import User, APIKey, CodeRequest, UserRole
from src.utils.security import SecurityManager
from src.utils.helpers import format_datetime, generate_key

class WebInterface:
    """Professional web interface"""
    
    def __init__(self):
        self.app = Flask(__name__, 
                        template_folder='../../templates',
                        static_folder='../../static')
        
        # Configuration
        self.app.config['SECRET_KEY'] = config.get('web_config.secret_key', 'your-secret-key-here')
        self.app.config['MAX_CONTENT_LENGTH'] = config.get('web_config.max_content_length', 16 * 1024 * 1024)
        
        # Security
        self.security = SecurityManager()
        
        # Rate limiting
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["100 per hour", "20 per minute"]
        )
        
        # Register routes
        self._register_routes()
        
        # Register error handlers
        self._register_error_handlers()
        
        logging.info("WebInterface initialized")
    
    def _register_routes(self):
        """Register all routes"""
        # Main routes
        self.app.route('/', methods=['GET'])(self.index)
        self.app.route('/generator', methods=['GET', 'POST'])(self.generator)
        self.app.route('/api/generate', methods=['POST'])(self.api_generate)
        self.app.route('/api/validate-key', methods=['POST'])(self.api_validate_key)
        self.app.route('/stats', methods=['GET'])(self.stats)
        self.app.route('/about', methods=['GET'])(self.about)
        
        # API routes
        self.app.route('/api/health', methods=['GET'])(self.api_health)
        self.app.route('/api/traffic-types', methods=['GET'])(self.api_traffic_types)
        
        # Admin routes
        self.app.route('/admin', methods=['GET'])(self.admin_dashboard)
        self.app.route('/admin/login', methods=['GET', 'POST'])(self.admin_login)
        self.app.route('/admin/logout', methods=['GET'])(self.admin_logout)
        self.app.route('/admin/users', methods=['GET'])(self.admin_users)
        self.app.route('/admin/keys', methods=['GET'])(self.admin_keys)
        
        # Add security headers to all responses
        @self.app.after_request
        def add_security_headers(response):
            headers = self.security.get_security_headers()
            for header, value in headers.items():
                response.headers[header] = value
            return response
    
    def _register_error_handlers(self):
        """Register error handlers"""
        @self.app.errorhandler(404)
        def not_found(error):
            return render_template('error.html', 
                                 error_code=404, 
                                 error_message="Trang không tồn tại"), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return render_template('error.html', 
                                 error_code=500, 
                                 error_message="Lỗi hệ thống"), 500
        
        @self.app.errorhandler(429)
        def rate_limit_handler(error):
            return render_template('error.html', 
                                 error_code=429, 
                                 error_message="Vượt quá giới hạn request"), 429
    
    def index(self):
        """Home page"""
        return render_template('index.html')
    
    @limiter.limit("10 per minute")
    def generator(self):
        """Code generator page"""
        if request.method == 'GET':
            traffic_types = config.get_all_traffic_types()
            traffic_configs = {}
            
            for traffic_type in traffic_types:
                traffic_config = config.get_traffic_config(traffic_type)
                if traffic_config:
                    traffic_configs[traffic_type] = {
                        'name': traffic_config.name,
                        'description': traffic_config.description,
                        'api_type': traffic_config.api_type.value
                    }
            
            return render_template('generator.html', traffic_types=traffic_configs)
        
        # POST request - generate code
        api_key = request.form.get('api_key', '').strip()
        traffic_type = request.form.get('traffic_type', '').strip()
        
        if not api_key or not traffic_type:
            flash('Vui lòng nhập đầy đủ thông tin!', 'error')
            return redirect(url_for('generator'))
        
        # Validate API key
        key_obj = db.get_api_key(api_key)
        if not key_obj or not key_obj.is_valid():
            flash('API Key không hợp lệ hoặc đã hết hạn!', 'error')
            return redirect(url_for('generator'))
        
        # Get traffic config
        traffic_config = config.get_traffic_config(traffic_type)
        if not traffic_config:
            flash('Loại traffic không hợp lệ!', 'error')
            return redirect(url_for('generator'))
        
        # Check rate limit and security
        client_ip = self.security.get_client_ip(dict(request.headers))
        if not self.security.is_ip_allowed(client_ip):
            flash('IP của bạn đã bị chặn!', 'error')
            return redirect(url_for('generator'))
        
        if not self.security.check_rate_limit(client_ip):
            flash('Bạn đã vượt quá giới hạn request!', 'error')
            return redirect(url_for('generator'))
        
        # Generate code
        try:
            response = api_client.generate_code(traffic_config, key_obj.user_id)
            
            if response.success:
                # Update key usage
                key_obj.usage_count += 1
                db.update_api_key(key_obj)
                
                return render_template('generator.html', 
                                     success=True,
                                     generated_code=response.code,
                                     traffic_name=traffic_config.name,
                                     processing_time=response.processing_time)
            else:
                flash(f'Lỗi tạo code: {response.error_message}', 'error')
                return redirect(url_for('generator'))
                
        except Exception as e:
            logging.error(f"Error generating code: {e}")
            flash('Lỗi hệ thống! Vui lòng thử lại sau.', 'error')
            return redirect(url_for('generator'))
    
    @limiter.limit("20 per minute")
    def api_generate(self):
        """API endpoint for code generation"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'Invalid JSON data'}), 400
            
            api_key = data.get('api_key', '').strip()
            traffic_type = data.get('traffic_type', '').strip()
            
            if not api_key or not traffic_type:
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
            # Security checks
            client_ip = self.security.get_client_ip(dict(request.headers))
            if not self.security.is_ip_allowed(client_ip):
                return jsonify({'success': False, 'message': 'IP blocked'}), 403
            
            if not self.security.check_rate_limit(client_ip):
                return jsonify({'success': False, 'message': 'Rate limit exceeded'}), 429
            
            # Validate API key
            key_obj = db.get_api_key(api_key)
            if not key_obj or not key_obj.is_valid():
                return jsonify({'success': False, 'message': 'Invalid or expired API key'}), 401
            
            # Get traffic config
            traffic_config = config.get_traffic_config(traffic_type)
            if not traffic_config:
                return jsonify({'success': False, 'message': 'Invalid traffic type'}), 400
            
            # Generate code
            response = api_client.generate_code(traffic_config, key_obj.user_id)
            
            if response.success:
                # Update key usage
                key_obj.usage_count += 1
                db.update_api_key(key_obj)
                
                return jsonify({
                    'success': True,
                    'code': response.code,
                    'traffic_type': traffic_config.name,
                    'processing_time': response.processing_time,
                    'key_usage_count': key_obj.usage_count
                })
            else:
                return jsonify({
                    'success': False,
                    'message': response.error_message,
                    'processing_time': response.processing_time
                }), 500
                
        except Exception as e:
            logging.error(f"API generate error: {e}")
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
    
    def api_validate_key(self):
        """API endpoint for key validation"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'valid': False, 'message': 'Invalid JSON data'}), 400
            
            api_key = data.get('api_key', '').strip()
            if not api_key:
                return jsonify({'valid': False, 'message': 'API key required'}), 400
            
            # Get key info
            key_obj = db.get_api_key(api_key)
            if not key_obj:
                return jsonify({'valid': False, 'message': 'Key not found'}), 404
            
            is_valid = key_obj.is_valid()
            
            response_data = {
                'valid': is_valid,
                'key': api_key,
                'created_at': format_datetime(key_obj.created_at),
                'expires_at': format_datetime(key_obj.expires_at) if key_obj.expires_at else None,
                'usage_count': key_obj.usage_count,
                'status': key_obj.status.value
            }
            
            if not is_valid:
                if key_obj.expires_at and datetime.now() > key_obj.expires_at:
                    response_data['message'] = 'Key expired'
                elif key_obj.status.value != 'active':
                    response_data['message'] = f'Key status: {key_obj.status.value}'
                else:
                    response_data['message'] = 'Key invalid'
            
            return jsonify(response_data)
            
        except Exception as e:
            logging.error(f"API validate key error: {e}")
            return jsonify({'valid': False, 'message': 'Internal server error'}), 500
    
    def stats(self):
        """Statistics page"""
        try:
            system_stats = db.get_system_stats()
            
            # Get traffic type usage stats
            traffic_stats = {}
            for traffic_type in config.get_all_traffic_types():
                traffic_config = config.get_traffic_config(traffic_type)
                if traffic_config:
                    traffic_stats[traffic_type] = {
                        'name': traffic_config.name,
                        'description': traffic_config.description,
                        'api_type': traffic_config.api_type.value
                    }
            
            return render_template('stats.html', 
                                 stats=system_stats,
                                 traffic_stats=traffic_stats)
                                 
        except Exception as e:
            logging.error(f"Stats page error: {e}")
            flash('Lỗi khi tải thống kê!', 'error')
            return redirect(url_for('index'))
    
    def about(self):
        """About page"""
        return render_template('about.html')
    
    def api_health(self):
        """API health endpoint"""
        try:
            health_status = api_client.get_health_status()
            db_stats = db.get_system_stats()
            
            return jsonify({
                'status': 'healthy' if health_status.get('healthy', False) else 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'api': health_status,
                'database': {
                    'total_users': db_stats.total_users,
                    'active_keys': db_stats.active_keys,
                    'total_requests': db_stats.total_requests
                },
                'version': config.get('app_config.version', '3.0.0')
            })
            
        except Exception as e:
            logging.error(f"Health check error: {e}")
            return jsonify({
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }), 500
    
    def api_traffic_types(self):
        """API endpoint for traffic types"""
        try:
            traffic_types = config.get_all_traffic_types()
            traffic_data = {}
            
            for traffic_type in traffic_types:
                traffic_config = config.get_traffic_config(traffic_type)
                if traffic_config:
                    traffic_data[traffic_type] = {
                        'name': traffic_config.name,
                        'description': traffic_config.description,
                        'api_type': traffic_config.api_type.value
                    }
            
            return jsonify({
                'success': True,
                'traffic_types': traffic_data,
                'total': len(traffic_data)
            })
            
        except Exception as e:
            logging.error(f"Traffic types API error: {e}")
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
    
    # Admin routes
    def admin_login(self):
        """Admin login"""
        if request.method == 'GET':
            return render_template('admin/login.html')
        
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Simple admin authentication (enhance this in production)
        admin_username = config.get('admin.username', 'admin')
        admin_password = config.get('admin.password', 'admin123')
        
        if username == admin_username and password == admin_password:
            session['admin_logged_in'] = True
            session['admin_user'] = username
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'error')
            return redirect(url_for('admin_login'))
    
    def admin_logout(self):
        """Admin logout"""
        session.pop('admin_logged_in', None)
        session.pop('admin_user', None)
        flash('Đã đăng xuất!', 'info')
        return redirect(url_for('admin_login'))
    
    def admin_required(self, f):
        """Decorator for admin routes"""
        def decorated_function(*args, **kwargs):
            if not session.get('admin_logged_in'):
                return redirect(url_for('admin_login'))
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    
    def admin_dashboard(self):
        """Admin dashboard"""
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        try:
            stats = db.get_system_stats()
            recent_users = db.get_all_users()[:10]  # Get first 10 users
            active_keys = db.get_all_active_keys()[:10]  # Get first 10 active keys
            
            return render_template('admin/dashboard.html',
                                 stats=stats,
                                 recent_users=recent_users,
                                 active_keys=active_keys)
                                 
        except Exception as e:
            logging.error(f"Admin dashboard error: {e}")
            flash('Lỗi khi tải dashboard!', 'error')
            return render_template('admin/dashboard.html')
    
    def admin_users(self):
        """Admin users management"""
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        try:
            users = db.get_all_users()
            return render_template('admin/users.html', users=users)
        except Exception as e:
            logging.error(f"Admin users error: {e}")
            flash('Lỗi khi tải danh sách users!', 'error')
            return render_template('admin/users.html', users=[])
    
    def admin_keys(self):
        """Admin keys management"""
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        try:
            active_keys = db.get_all_active_keys()
            return render_template('admin/keys.html', keys=active_keys)
        except Exception as e:
            logging.error(f"Admin keys error: {e}")
            flash('Lỗi khi tải danh sách keys!', 'error')
            return render_template('admin/keys.html', keys=[])
    
    def run(self, host=None, port=None, debug=None):
        """Run the web application"""
        host = host or config.get('web_config.host', '0.0.0.0')
        port = port or config.get('web_config.port', 5000)
        debug = debug if debug is not None else config.get('web_config.debug', False)
        
        logging.info(f"Starting web interface on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug, threaded=True)

# Global web interface instance
web_interface = WebInterface()
