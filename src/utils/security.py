"""
Security utilities for YeuMoney system
"""

import hashlib
import hmac
import time
import logging
from typing import Dict, Set, Optional
from datetime import datetime, timedelta
import ipaddress
from collections import defaultdict

from src.core.config import config

class SecurityManager:
    """Professional security manager"""
    
    def __init__(self):
        self.rate_limits = defaultdict(list)  # ip -> [timestamps]
        self.failed_attempts = defaultdict(int)  # ip -> count
        self.blocked_ips: Set[str] = set()
        self.blocked_until = {}  # ip -> datetime
        
        # Security settings
        self.max_requests_per_minute = config.get('security_config.max_requests_per_minute', 60)
        self.max_failed_attempts = config.get('security_config.max_failed_attempts', 5)
        self.block_duration_minutes = config.get('security_config.block_duration_minutes', 30)
        self.enable_rate_limiting = config.get('security_config.enable_rate_limiting', True)
        self.enable_ip_blocking = config.get('security_config.enable_ip_blocking', True)
        
        logging.info("SecurityManager initialized")
    
    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed"""
        if not self.enable_ip_blocking:
            return True
        
        # Check if IP is currently blocked
        if ip_address in self.blocked_ips:
            # Check if block has expired
            if ip_address in self.blocked_until:
                if datetime.now() > self.blocked_until[ip_address]:
                    self.unblock_ip(ip_address)
                    return True
                return False
            return False
        
        return True
    
    def check_rate_limit(self, ip_address: str) -> bool:
        """Check if IP is within rate limits"""
        if not self.enable_rate_limiting:
            return True
        
        now = time.time()
        minute_ago = now - 60
        
        # Clean old entries
        self.rate_limits[ip_address] = [
            timestamp for timestamp in self.rate_limits[ip_address]
            if timestamp > minute_ago
        ]
        
        # Check current count
        current_count = len(self.rate_limits[ip_address])
        
        if current_count >= self.max_requests_per_minute:
            self.record_failed_attempt(ip_address)
            return False
        
        # Add current request
        self.rate_limits[ip_address].append(now)
        return True
    
    def record_failed_attempt(self, ip_address: str) -> None:
        """Record a failed attempt for IP"""
        self.failed_attempts[ip_address] += 1
        
        if self.failed_attempts[ip_address] >= self.max_failed_attempts:
            self.block_ip(ip_address, self.block_duration_minutes)
            logging.warning(f"IP {ip_address} blocked due to excessive failed attempts")
    
    def block_ip(self, ip_address: str, duration_minutes: int) -> None:
        """Block an IP address"""
        self.blocked_ips.add(ip_address)
        self.blocked_until[ip_address] = datetime.now() + timedelta(minutes=duration_minutes)
        logging.info(f"IP {ip_address} blocked for {duration_minutes} minutes")
    
    def unblock_ip(self, ip_address: str) -> None:
        """Unblock an IP address"""
        self.blocked_ips.discard(ip_address)
        self.blocked_until.pop(ip_address, None)
        self.failed_attempts.pop(ip_address, None)
        logging.info(f"IP {ip_address} unblocked")
    
    def reset_failed_attempts(self, ip_address: str) -> None:
        """Reset failed attempts for IP"""
        self.failed_attempts.pop(ip_address, None)
    
    def is_valid_ip(self, ip_address: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False
    
    def get_client_ip(self, request_headers: Dict[str, str]) -> str:
        """Extract client IP from request headers"""
        # Check various headers for real IP
        ip_headers = [
            'X-Forwarded-For',
            'X-Real-IP',
            'X-Client-IP',
            'CF-Connecting-IP',  # Cloudflare
            'True-Client-IP',
            'X-Forwarded',
            'Forwarded-For',
            'Forwarded'
        ]
        
        for header in ip_headers:
            if header in request_headers:
                ip = request_headers[header].split(',')[0].strip()
                if self.is_valid_ip(ip) and not self.is_private_ip(ip):
                    return ip
        
        return '127.0.0.1'  # Fallback
    
    def is_private_ip(self, ip_address: str) -> bool:
        """Check if IP is private/internal"""
        try:
            ip = ipaddress.ip_address(ip_address)
            return ip.is_private or ip.is_loopback or ip.is_link_local
        except ValueError:
            return False
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token"""
        secret_key = config.get('security_config.encryption_key', 'default-secret')
        timestamp = str(int(time.time()))
        
        message = f"{session_id}:{timestamp}"
        signature = hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}:{signature}"
    
    def validate_csrf_token(self, token: str, session_id: str, max_age: int = 3600) -> bool:
        """Validate CSRF token"""
        try:
            timestamp_str, signature = token.split(':', 1)
            timestamp = int(timestamp_str)
            
            # Check if token is expired
            if time.time() - timestamp > max_age:
                return False
            
            # Recreate expected signature
            secret_key = config.get('security_config.encryption_key', 'default-secret')
            message = f"{session_id}:{timestamp_str}"
            expected_signature = hmac.new(
                secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except (ValueError, IndexError):
            return False
    
    def sanitize_input(self, input_text: str) -> str:
        """Sanitize user input"""
        if not isinstance(input_text, str):
            return ""
        
        # Remove control characters
        sanitized = ''.join(char for char in input_text if ord(char) >= 32 or char in '\n\r\t')
        
        # Limit length
        max_length = 1000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    def is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is suspicious"""
        if not user_agent:
            return True
        
        suspicious_patterns = [
            'bot', 'crawler', 'spider', 'scraper',
            'curl', 'wget', 'python-requests',
            'postman', 'insomnia'
        ]
        
        user_agent_lower = user_agent.lower()
        return any(pattern in user_agent_lower for pattern in suspicious_patterns)
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
    
    def log_security_event(self, event_type: str, ip_address: str, details: str = "") -> None:
        """Log security events"""
        logging.warning(f"SECURITY EVENT: {event_type} from {ip_address} - {details}")
    
    def get_blocked_ips(self) -> Dict[str, str]:
        """Get currently blocked IPs with reasons"""
        blocked = {}
        for ip in self.blocked_ips:
            if ip in self.blocked_until:
                blocked[ip] = f"Blocked until {self.blocked_until[ip]}"
            else:
                blocked[ip] = "Permanently blocked"
        return blocked
    
    def cleanup_old_data(self) -> None:
        """Clean up old security data"""
        now = time.time()
        hour_ago = now - 3600
        
        # Clean rate limit data
        for ip in list(self.rate_limits.keys()):
            self.rate_limits[ip] = [
                timestamp for timestamp in self.rate_limits[ip]
                if timestamp > hour_ago
            ]
            if not self.rate_limits[ip]:
                del self.rate_limits[ip]
        
        # Clean expired blocks
        current_time = datetime.now()
        for ip in list(self.blocked_until.keys()):
            if current_time > self.blocked_until[ip]:
                self.unblock_ip(ip)
