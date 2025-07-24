"""
Professional database manager for YeuMoney system
"""

import sqlite3
import json
import logging
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import shutil
from contextlib import contextmanager

from src.models.models import User, APIKey, CodeRequest, SystemStats, UserRole, KeyStatus
from src.core.config import config

class DatabaseManager:
    """Professional database management system"""
    
    def __init__(self):
        self.db_path = config.get('database_config.path', 'data/yeumoney.db')
        self.backup_interval = config.get('database_config.backup_interval_hours', 6)
        self.max_backups = config.get('database_config.max_backups', 10)
        self._lock = threading.RLock()
        
        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.init_database()
        
    def init_database(self) -> None:
        """Initialize database with all required tables"""
        try:
            with self.get_connection() as conn:
                # Users table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        role TEXT DEFAULT 'user',
                        is_banned BOOLEAN DEFAULT 0,
                        ban_until TIMESTAMP,
                        ban_reason TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        usage_count INTEGER DEFAULT 0
                    )
                ''')
                
                # API Keys table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS api_keys (
                        key TEXT PRIMARY KEY,
                        user_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        status TEXT DEFAULT 'active',
                        usage_count INTEGER DEFAULT 0,
                        max_usage INTEGER,
                        device_info TEXT,
                        metadata TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Code requests table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS code_requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        traffic_type TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ip_address TEXT,
                        user_agent TEXT,
                        success BOOLEAN,
                        error_message TEXT,
                        generated_code TEXT,
                        processing_time REAL,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # System logs table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS system_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        level TEXT,
                        message TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        user_id INTEGER,
                        extra_data TEXT
                    )
                ''')
                
                # Settings table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                conn.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_users_banned ON users(is_banned)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_keys_user ON api_keys(user_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_keys_status ON api_keys(status)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_keys_expires ON api_keys(expires_at)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_requests_user ON code_requests(user_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_requests_timestamp ON code_requests(timestamp)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON system_logs(timestamp)')
                
                conn.commit()
                logging.info("Database initialized successfully")
                
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path, timeout=30.0)
                conn.row_factory = sqlite3.Row
                yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logging.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    # User management methods
    def create_user(self, user: User) -> bool:
        """Create a new user"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, role, is_banned, 
                     ban_until, ban_reason, created_at, last_seen, usage_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user.user_id, user.username, user.first_name, user.last_name,
                    user.role.value, user.is_banned,
                    user.ban_until.isoformat() if user.ban_until else None,
                    user.ban_reason, user.created_at.isoformat(),
                    user.last_seen.isoformat(), user.usage_count
                ))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error creating user {user.user_id}: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            with self.get_connection() as conn:
                row = conn.execute(
                    'SELECT * FROM users WHERE user_id = ?', (user_id,)
                ).fetchone()
                
                if row:
                    return User.from_dict(dict(row))
                return None
        except Exception as e:
            logging.error(f"Error getting user {user_id}: {e}")
            return None
    
    def update_user(self, user: User) -> bool:
        """Update user information"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    UPDATE users SET 
                    username = ?, first_name = ?, last_name = ?, role = ?,
                    is_banned = ?, ban_until = ?, ban_reason = ?,
                    last_seen = ?, usage_count = ?
                    WHERE user_id = ?
                ''', (
                    user.username, user.first_name, user.last_name, user.role.value,
                    user.is_banned,
                    user.ban_until.isoformat() if user.ban_until else None,
                    user.ban_reason, user.last_seen.isoformat(), user.usage_count,
                    user.user_id
                ))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error updating user {user.user_id}: {e}")
            return False
    
    def get_all_users(self, role: Optional[UserRole] = None) -> List[User]:
        """Get all users, optionally filtered by role"""
        try:
            with self.get_connection() as conn:
                if role:
                    rows = conn.execute(
                        'SELECT * FROM users WHERE role = ?', (role.value,)
                    ).fetchall()
                else:
                    rows = conn.execute('SELECT * FROM users').fetchall()
                
                return [User.from_dict(dict(row)) for row in rows]
        except Exception as e:
            logging.error(f"Error getting users: {e}")
            return []
    
    def ban_user(self, user_id: int, duration_minutes: int, reason: str = "") -> bool:
        """Ban a user"""
        try:
            ban_until = datetime.now() + timedelta(minutes=duration_minutes)
            with self.get_connection() as conn:
                conn.execute('''
                    UPDATE users SET is_banned = 1, ban_until = ?, ban_reason = ?
                    WHERE user_id = ?
                ''', (ban_until.isoformat(), reason, user_id))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error banning user {user_id}: {e}")
            return False
    
    def unban_user(self, user_id: int) -> bool:
        """Unban a user"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    UPDATE users SET is_banned = 0, ban_until = NULL, ban_reason = ''
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error unbanning user {user_id}: {e}")
            return False
    
    # API Key management methods
    def create_api_key(self, api_key: APIKey) -> bool:
        """Create a new API key"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO api_keys 
                    (key, user_id, created_at, expires_at, status, usage_count,
                     max_usage, device_info, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    api_key.key, api_key.user_id,
                    api_key.created_at.isoformat(),
                    api_key.expires_at.isoformat() if api_key.expires_at else None,
                    api_key.status.value, api_key.usage_count, api_key.max_usage,
                    json.dumps(api_key.device_info),
                    json.dumps(api_key.metadata)
                ))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error creating API key {api_key.key}: {e}")
            return False
    
    def get_api_key(self, key: str) -> Optional[APIKey]:
        """Get API key by key string"""
        try:
            with self.get_connection() as conn:
                row = conn.execute(
                    'SELECT * FROM api_keys WHERE key = ?', (key,)
                ).fetchone()
                
                if row:
                    data = dict(row)
                    data['device_info'] = json.loads(data['device_info'] or '{}')
                    data['metadata'] = json.loads(data['metadata'] or '{}')
                    return APIKey.from_dict(data)
                return None
        except Exception as e:
            logging.error(f"Error getting API key {key}: {e}")
            return None
    
    def get_user_keys(self, user_id: int) -> List[APIKey]:
        """Get all keys for a user"""
        try:
            with self.get_connection() as conn:
                rows = conn.execute(
                    'SELECT * FROM api_keys WHERE user_id = ?', (user_id,)
                ).fetchall()
                
                keys = []
                for row in rows:
                    data = dict(row)
                    data['device_info'] = json.loads(data['device_info'] or '{}')
                    data['metadata'] = json.loads(data['metadata'] or '{}')
                    keys.append(APIKey.from_dict(data))
                
                return keys
        except Exception as e:
            logging.error(f"Error getting keys for user {user_id}: {e}")
            return []
    
    def update_api_key(self, api_key: APIKey) -> bool:
        """Update API key"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    UPDATE api_keys SET 
                    expires_at = ?, status = ?, usage_count = ?, max_usage = ?,
                    device_info = ?, metadata = ?
                    WHERE key = ?
                ''', (
                    api_key.expires_at.isoformat() if api_key.expires_at else None,
                    api_key.status.value, api_key.usage_count, api_key.max_usage,
                    json.dumps(api_key.device_info),
                    json.dumps(api_key.metadata),
                    api_key.key
                ))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error updating API key {api_key.key}: {e}")
            return False
    
    def delete_api_key(self, key: str) -> bool:
        """Delete API key"""
        try:
            with self.get_connection() as conn:
                conn.execute('DELETE FROM api_keys WHERE key = ?', (key,))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error deleting API key {key}: {e}")
            return False
    
    def get_all_active_keys(self) -> List[APIKey]:
        """Get all active API keys"""
        try:
            with self.get_connection() as conn:
                rows = conn.execute('''
                    SELECT * FROM api_keys 
                    WHERE status = 'active' AND (expires_at IS NULL OR expires_at > ?)
                ''', (datetime.now().isoformat(),)).fetchall()
                
                keys = []
                for row in rows:
                    data = dict(row)
                    data['device_info'] = json.loads(data['device_info'] or '{}')
                    data['metadata'] = json.loads(data['metadata'] or '{}')
                    keys.append(APIKey.from_dict(data))
                
                return keys
        except Exception as e:
            logging.error(f"Error getting active keys: {e}")
            return []
    
    def cleanup_expired_keys(self) -> int:
        """Clean up expired keys"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    UPDATE api_keys SET status = 'expired'
                    WHERE expires_at < ? AND status = 'active'
                ''', (datetime.now().isoformat(),))
                
                count = cursor.rowcount
                conn.commit()
                return count
        except Exception as e:
            logging.error(f"Error cleaning up expired keys: {e}")
            return 0
    
    # Code request logging
    def log_code_request(self, request: CodeRequest) -> bool:
        """Log a code generation request"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO code_requests 
                    (user_id, traffic_type, timestamp, ip_address, user_agent,
                     success, error_message, generated_code, processing_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    request.user_id, request.traffic_type,
                    request.timestamp.isoformat(), request.ip_address,
                    request.user_agent, request.success, request.error_message,
                    request.generated_code, request.processing_time
                ))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error logging code request: {e}")
            return False
    
    def get_user_requests(self, user_id: int, limit: int = 100) -> List[CodeRequest]:
        """Get recent requests for a user"""
        try:
            with self.get_connection() as conn:
                rows = conn.execute('''
                    SELECT * FROM code_requests 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (user_id, limit)).fetchall()
                
                return [CodeRequest(**dict(row)) for row in rows]
        except Exception as e:
            logging.error(f"Error getting user requests: {e}")
            return []
    
    # System statistics
    def get_system_stats(self) -> SystemStats:
        """Get system statistics"""
        try:
            with self.get_connection() as conn:
                # Get total users
                total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
                
                # Get active keys
                active_keys = conn.execute('''
                    SELECT COUNT(*) FROM api_keys 
                    WHERE status = 'active' AND (expires_at IS NULL OR expires_at > ?)
                ''', (datetime.now().isoformat(),)).fetchone()[0]
                
                # Get request statistics
                total_requests = conn.execute('SELECT COUNT(*) FROM code_requests').fetchone()[0]
                successful_requests = conn.execute(
                    'SELECT COUNT(*) FROM code_requests WHERE success = 1'
                ).fetchone()[0]
                failed_requests = total_requests - successful_requests
                
                return SystemStats(
                    total_users=total_users,
                    active_keys=active_keys,
                    total_requests=total_requests,
                    successful_requests=successful_requests,
                    failed_requests=failed_requests,
                    last_updated=datetime.now()
                )
        except Exception as e:
            logging.error(f"Error getting system stats: {e}")
            return SystemStats()
    
    # Backup methods
    def create_backup(self) -> str:
        """Create database backup"""
        try:
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"yeumoney_backup_{timestamp}.db"
            
            shutil.copy2(self.db_path, backup_path)
            
            # Clean old backups
            self._cleanup_old_backups(backup_dir)
            
            logging.info(f"Database backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logging.error(f"Error creating backup: {e}")
            return ""
    
    def _cleanup_old_backups(self, backup_dir: Path) -> None:
        """Clean up old backup files"""
        try:
            backups = sorted(backup_dir.glob("yeumoney_backup_*.db"))
            while len(backups) > self.max_backups:
                oldest = backups.pop(0)
                oldest.unlink()
                logging.info(f"Deleted old backup: {oldest}")
        except Exception as e:
            logging.error(f"Error cleaning up backups: {e}")

# Global database instance
db = DatabaseManager()
