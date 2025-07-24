"""
Configuration management system
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from src.models.models import TrafficConfig, APIType

class ConfigManager:
    """Professional configuration manager"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = {}
        self.load_config()
        
    def load_config(self) -> None:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = self.get_default_config()
                self.save_config()
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            self.config = self.get_default_config()
    
    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error saving config: {e}")
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "app_config": {
                "name": "YeuMoney Code Generator Pro",
                "version": "3.0.0",
                "description": "Professional code generator with advanced features",
                "author": "Professional Team",
                "debug": False
            },
            "api_config": {
                "base_url": "https://traffic-user.net",
                "request_timeout": 30,
                "max_retries": 3,
                "retry_delay": 2,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "rate_limit": {
                    "requests_per_minute": 60,
                    "requests_per_hour": 1000
                }
            },
            "bot_config": {
                "token": os.getenv('BOT_TOKEN', ''),
                "master_admin_id": 7509896689,
                "key_lifetime_hours": 24,
                "max_keys_per_user": 1,
                "cooldown_minutes": 60,
                "spam_protection": {
                    "max_messages_per_minute": 10,
                    "ban_duration_minutes": 60
                }
            },
            "web_config": {
                "host": "0.0.0.0",
                "port": 5000,
                "debug": False,
                "secret_key": os.getenv('SECRET_KEY', 'your-secret-key-here'),
                "max_content_length": 16 * 1024 * 1024  # 16MB
            },
            "database_config": {
                "type": "sqlite",
                "path": "data/yeumoney.db",
                "backup_interval_hours": 6,
                "max_backups": 10
            },
            "logging_config": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "logs/yeumoney.log",
                "max_size_mb": 100,
                "backup_count": 5
            },
            "security_config": {
                "enable_rate_limiting": True,
                "enable_ip_blocking": True,
                "max_failed_attempts": 5,
                "block_duration_minutes": 30,
                "allowed_origins": ["*"],
                "encryption_key": os.getenv('ENCRYPTION_KEY', '')
            },
            "traffic_sources": self.get_default_traffic_configs()
        }
    
    def get_default_traffic_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get default traffic source configurations"""
        return {
            "m88": {
                "name": "M88 Betting",
                "api_type": "GET_MA",
                "codexn": "taodeptrai",
                "url": "https://bet88ec.com/cach-danh-bai-sam-loc",
                "loai_traffic": "https://bet88ec.com/",
                "regex_pattern": r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
                "clk": 1000,
                "timeout": 30,
                "max_retries": 3,
                "description": "Cá cược thể thao và casino trực tuyến"
            },
            "fb88": {
                "name": "FB88 Sports",
                "api_type": "GET_MA",
                "codexn": "taodeptrai",
                "url": "https://fb88dq.com/cach-choi-ca-cuoc-golf",
                "loai_traffic": "https://fb88dq.com/",
                "regex_pattern": r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
                "clk": 1000,
                "timeout": 30,
                "max_retries": 3,
                "description": "Cá cược golf và thể thao"
            },
            "188bet": {
                "name": "188BET Casino",
                "api_type": "GET_MA",
                "codexn": "taodeptrailamnhe",
                "url": "https://88betag.com/cach-choi-game-bai-pok-deng",
                "loai_traffic": "https://88betag.com/",
                "regex_pattern": r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
                "clk": 1000,
                "timeout": 30,
                "max_retries": 3,
                "description": "Game bài Pok Deng online"
            },
            "w88": {
                "name": "W88 Poker",
                "api_type": "GET_MA",
                "codexn": "taodeptrai",
                "url": "https://188.166.185.213/tim-hieu-khai-niem-3-bet-trong-poker-la-gi",
                "loai_traffic": "https://188.166.185.213/",
                "regex_pattern": r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
                "clk": 1000,
                "timeout": 30,
                "max_retries": 3,
                "description": "Poker và game bài chuyên nghiệp"
            },
            "v9bet": {
                "name": "V9BET Basketball",
                "api_type": "GET_MA",
                "codexn": "taodeptrai",
                "url": "https://v9betho.com/ca-cuoc-bong-ro-ao",
                "loai_traffic": "https://v9betho.com/",
                "regex_pattern": r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
                "clk": 1000,
                "timeout": 30,
                "max_retries": 3,
                "description": "Cá cược bóng rổ ảo"
            },
            "vn88": {
                "name": "VN88 Card Games",
                "api_type": "GET_MA",
                "codexn": "taodeptrai",
                "url": "https://vn88ie.com/game-bai-gao-gae",
                "loai_traffic": "https://vn88ie.com/",
                "regex_pattern": r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
                "clk": 1000,
                "timeout": 30,
                "max_retries": 3,
                "description": "Game bài Gao Gae truyền thống"
            },
            "bk8": {
                "name": "BK8 Card Games",
                "api_type": "GET_MA",
                "codexn": "taodeptrai",
                "url": "https://bk8xo.com/game-bai-catte",
                "loai_traffic": "https://bk8xo.com/",
                "regex_pattern": r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
                "clk": 1000,
                "timeout": 30,
                "max_retries": 3,
                "description": "Game bài Catte online"
            },
            "w88xlm": {
                "name": "W88XLM Solitaire",
                "api_type": "GET_MA",
                "codexn": "taodeptrai",
                "url": "https://w88xlm.com/game-bai-solitaire",
                "loai_traffic": "https://w88xlm.com/",
                "regex_pattern": r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
                "clk": 1000,
                "timeout": 30,
                "max_retries": 3,
                "description": "Game bài Solitaire kinh điển"
            },
            "88betag": {
                "name": "88BET AG Direct",
                "api_type": "GET_MD",
                "codexn": "taodeptrai",
                "url": "https://88betag.com/keo-chau-a",
                "loai_traffic": "https://88betag.com/",
                "regex_pattern": r'<span id="layma_md_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
                "clk": 1000,
                "timeout": 30,
                "max_retries": 3,
                "description": "Kèo châu Á chuyên nghiệp"
            },
            "w88abc": {
                "name": "W88ABC Mobile Gaming",
                "api_type": "GET_MD",
                "codexn": "taodeptrai",
                "url": "https://w88abc.com/ca-cuoc-lien-quan-mobile",
                "loai_traffic": "https://w88abc.com/",
                "regex_pattern": r'<span id="layma_md_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
                "clk": 1000,
                "timeout": 30,
                "max_retries": 3,
                "description": "Cá cược Liên Quân Mobile"
            },
            "v9betlg": {
                "name": "V9BET Flat Betting",
                "api_type": "GET_MD",
                "codexn": "taodeptrai",
                "url": "https://v9betlg.com/phuong-phap-cuoc-flat-betting",
                "loai_traffic": "https://v9betlg.com/",
                "regex_pattern": r'<span id="layma_md_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
                "clk": 1000,
                "timeout": 30,
                "max_retries": 3,
                "description": "Phương pháp cược Flat Betting"
            },
            "bk8xo": {
                "name": "BK8XO Lottery",
                "api_type": "GET_MD",
                "codexn": "taodeptrai",
                "url": "https://bk8xo.com/lo-ba-cang",
                "loai_traffic": "https://bk8xo.com/",
                "regex_pattern": r'<span id="layma_md_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
                "clk": 1000,
                "timeout": 30,
                "max_retries": 3,
                "description": "Lô ba càng và xổ số"
            },
            "vn88ie": {
                "name": "VN88IE Lottery System",
                "api_type": "GET_MD",
                "codexn": "taodeptrai",
                "url": "https://vn88ie.com/nuoi-lo-khung",
                "loai_traffic": "https://vn88ie.com/",
                "regex_pattern": r'<span id="layma_md_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
                "clk": 1000,
                "timeout": 30,
                "max_retries": 3,
                "description": "Nuôi lô khung chuyên nghiệp"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def get_traffic_config(self, traffic_type: str) -> Optional[TrafficConfig]:
        """Get traffic configuration as TrafficConfig object"""
        config_data = self.get(f'traffic_sources.{traffic_type}')
        if not config_data:
            return None
        
        try:
            return TrafficConfig(
                name=config_data['name'],
                api_type=APIType(config_data['api_type']),
                codexn=config_data['codexn'],
                url=config_data['url'],
                loai_traffic=config_data['loai_traffic'],
                regex_pattern=config_data['regex_pattern'],
                clk=config_data.get('clk', 1000),
                timeout=config_data.get('timeout', 30),
                max_retries=config_data.get('max_retries', 3),
                description=config_data.get('description', '')
            )
        except Exception as e:
            logging.error(f"Error creating TrafficConfig for {traffic_type}: {e}")
            return None
    
    def get_all_traffic_types(self) -> list:
        """Get all available traffic types"""
        return list(self.get('traffic_sources', {}).keys())

# Global configuration instance
config = ConfigManager()
