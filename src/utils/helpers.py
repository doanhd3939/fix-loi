"""
Helper utilities for YeuMoney system
"""

import random
import string
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import json
import os
import re
from pathlib import Path

def generate_key(length: int = 12) -> str:
    """Generate a random key"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def format_datetime(dt: Optional[datetime]) -> str:
    """Format datetime for display"""
    if not dt:
        return "N/A"
    
    # Convert to local timezone if needed
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.strftime("%d/%m/%Y %H:%M:%S")

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    filename = ''.join(char for char in filename if ord(char) >= 32)
    
    # Limit length
    max_length = 255
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext
    
    return filename.strip()

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(data: Any, indent: int = None) -> str:
    """Safely dump data to JSON string"""
    try:
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
    except (TypeError, ValueError) as e:
        logging.error(f"Error serializing JSON: {e}")
        return "{}"

def ensure_directory(path: str) -> bool:
    """Ensure directory exists"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Error creating directory {path}: {e}")
        return False

def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except (OSError, FileNotFoundError):
        return 0

def format_file_size(size_bytes: int) -> str:
    """Format file size to human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to specified length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def is_valid_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_url(url: str) -> bool:
    """Validate URL format"""
    pattern = r'^https?:\/\/(?:[-\w.])+(?:\:[0-9]+)?(?:\/(?:[\w\/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
    return re.match(pattern, url) is not None

def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return ""

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and special characters"""
    if not isinstance(text, str):
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove control characters except newline and tab
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    return text.strip()

def generate_random_string(length: int = 8, use_digits: bool = True, use_symbols: bool = False) -> str:
    """Generate random string with specified criteria"""
    characters = string.ascii_letters
    
    if use_digits:
        characters += string.digits
    
    if use_symbols:
        characters += "!@#$%^&*"
    
    return ''.join(random.choice(characters) for _ in range(length))

def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data showing only first and last few characters"""
    if len(data) <= visible_chars * 2:
        return "*" * len(data)
    
    return data[:visible_chars] + "*" * (len(data) - visible_chars * 2) + data[-visible_chars:]

def parse_duration_string(duration_str: str) -> int:
    """Parse duration string to seconds (e.g., '1h30m', '45s', '2d')"""
    pattern = r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
    match = re.match(pattern, duration_str.lower())
    
    if not match:
        return 0
    
    days, hours, minutes, seconds = match.groups()
    
    total_seconds = 0
    if days:
        total_seconds += int(days) * 86400
    if hours:
        total_seconds += int(hours) * 3600
    if minutes:
        total_seconds += int(minutes) * 60
    if seconds:
        total_seconds += int(seconds)
    
    return total_seconds

def get_system_info() -> Dict[str, Any]:
    """Get basic system information"""
    import platform
    import psutil
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': cpu_percent,
            'memory_total': memory.total,
            'memory_available': memory.available,
            'memory_percent': memory.percent,
            'disk_total': disk.total,
            'disk_free': disk.free,
            'disk_percent': (disk.used / disk.total) * 100,
        }
    except ImportError:
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
        }

def validate_traffic_type(traffic_type: str) -> bool:
    """Validate traffic type format"""
    # Should be lowercase alphanumeric with possible numbers
    pattern = r'^[a-z0-9]+$'
    return bool(re.match(pattern, traffic_type)) and len(traffic_type) <= 20

def format_success_rate(successful: int, total: int) -> str:
    """Format success rate as percentage"""
    if total == 0:
        return "0.0%"
    
    rate = (successful / total) * 100
    return f"{rate:.1f}%"

def create_backup_filename(base_name: str, extension: str = ".bak") -> str:
    """Create backup filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(base_name)
    return f"{name}_{timestamp}{extension}"

def retry_operation(func, max_retries: int = 3, delay: float = 1.0):
    """Retry operation with exponential backoff"""
    import time
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                raise e
            
            wait_time = delay * (2 ** attempt)
            logging.warning(f"Operation failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
            time.sleep(wait_time)

def batch_process(items: List[Any], batch_size: int = 100):
    """Process items in batches"""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]

def hash_string(text: str, algorithm: str = 'sha256') -> str:
    """Hash string using specified algorithm"""
    import hashlib
    
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode('utf-8'))
    return hash_obj.hexdigest()

class RateLimiter:
    """Simple rate limiter implementation"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def is_allowed(self) -> bool:
        """Check if request is allowed"""
        import time
        
        now = time.time()
        # Remove old requests
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            return False
        
        self.requests.append(now)
        return True

def get_client_info(headers: Dict[str, str]) -> Dict[str, str]:
    """Extract client information from headers"""
    return {
        'user_agent': headers.get('User-Agent', ''),
        'accept_language': headers.get('Accept-Language', ''),
        'accept_encoding': headers.get('Accept-Encoding', ''),
        'connection': headers.get('Connection', ''),
        'referer': headers.get('Referer', ''),
        'origin': headers.get('Origin', ''),
    }
