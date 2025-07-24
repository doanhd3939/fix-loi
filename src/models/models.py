"""
Data models for YeuMoney system
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import json

class APIType(Enum):
    """API types for different traffic sources"""
    GET_MA = "GET_MA"
    GET_MD = "GET_MD"

class UserRole(Enum):
    """User roles in the system"""
    USER = "user"
    ADMIN = "admin" 
    MASTER_ADMIN = "master_admin"

class KeyStatus(Enum):
    """Key status enumeration"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"

@dataclass
class TrafficConfig:
    """Configuration for traffic sources"""
    name: str
    api_type: APIType
    codexn: str
    url: str
    loai_traffic: str
    regex_pattern: str
    clk: int = 1000
    timeout: int = 30
    max_retries: int = 3
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'api_type': self.api_type.value,
            'codexn': self.codexn,
            'url': self.url,
            'loai_traffic': self.loai_traffic,
            'regex_pattern': self.regex_pattern,
            'clk': self.clk,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'description': self.description
        }

@dataclass
class User:
    """User model"""
    user_id: int
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    role: UserRole = UserRole.USER
    is_banned: bool = False
    ban_until: Optional[datetime] = None
    ban_reason: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.value,
            'is_banned': self.is_banned,
            'ban_until': self.ban_until.isoformat() if self.ban_until else None,
            'ban_reason': self.ban_reason,
            'created_at': self.created_at.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'usage_count': self.usage_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create from dictionary"""
        user = cls(
            user_id=data['user_id'],
            username=data.get('username', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role=UserRole(data.get('role', UserRole.USER.value)),
            is_banned=data.get('is_banned', False),
            ban_reason=data.get('ban_reason', ''),
            usage_count=data.get('usage_count', 0)
        )
        
        if data.get('ban_until'):
            user.ban_until = datetime.fromisoformat(data['ban_until'])
        if data.get('created_at'):
            user.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('last_seen'):
            user.last_seen = datetime.fromisoformat(data['last_seen'])
            
        return user

@dataclass
class APIKey:
    """API Key model"""
    key: str
    user_id: int
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    status: KeyStatus = KeyStatus.ACTIVE
    usage_count: int = 0
    max_usage: Optional[int] = None
    device_info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Check if key is valid"""
        if self.status != KeyStatus.ACTIVE:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        if self.max_usage and self.usage_count >= self.max_usage:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'key': self.key,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'status': self.status.value,
            'usage_count': self.usage_count,
            'max_usage': self.max_usage,
            'device_info': self.device_info,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIKey':
        """Create from dictionary"""
        key = cls(
            key=data['key'],
            user_id=data['user_id'],
            status=KeyStatus(data.get('status', KeyStatus.ACTIVE.value)),
            usage_count=data.get('usage_count', 0),
            max_usage=data.get('max_usage'),
            device_info=data.get('device_info', {}),
            metadata=data.get('metadata', {})
        )
        
        if data.get('created_at'):
            key.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('expires_at'):
            key.expires_at = datetime.fromisoformat(data['expires_at'])
            
        return key

@dataclass
class CodeRequest:
    """Code generation request model"""
    user_id: int
    traffic_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    ip_address: str = ""
    user_agent: str = ""
    success: bool = False
    error_message: str = ""
    generated_code: str = ""
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'traffic_type': self.traffic_type,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'success': self.success,
            'error_message': self.error_message,
            'generated_code': self.generated_code,
            'processing_time': self.processing_time
        }

@dataclass
class SystemStats:
    """System statistics model"""
    total_users: int = 0
    active_keys: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    uptime: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_users': self.total_users,
            'active_keys': self.active_keys,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': self.success_rate(),
            'uptime': self.uptime,
            'last_updated': self.last_updated.isoformat()
        }
