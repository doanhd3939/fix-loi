#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YeuMoney Code Generator - Professional Version
Author: Upgraded by AI Assistant
Description: Generates codes from various traffic sources with improved error handling and structure
"""

import requests
import re
import time
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import os

# ========== CONFIGURATION ==========
class APIType(Enum):
    """Enum for different API types"""
    GET_MA = "GET_MA"
    GET_MD = "GET_MD"

@dataclass
class TrafficConfig:
    """Configuration for each traffic source"""
    name: str
    api_type: APIType
    codexn: str
    url: str
    loai_traffic: str
    regex_pattern: str
    clk: int = 1000

# ========== LOGGING CONFIGURATION ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('yeumoney.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class YeuMoneyGenerator:
    """Professional code generator class"""
    
    BASE_URL = "https://traffic-user.net"
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    
    # Configuration for all traffic sources
    TRAFFIC_CONFIGS: Dict[str, TrafficConfig] = {
        "m88": TrafficConfig(
            name="M88 Betting",
            api_type=APIType.GET_MA,
            codexn="taodeptrai",
            url="https://bet88ec.com/cach-danh-bai-sam-loc",
            loai_traffic="https://bet88ec.com/",
            regex_pattern=r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>'
        ),
        
        "fb88": TrafficConfig(
            name="FB88 Sports",
            api_type=APIType.GET_MA,
            codexn="taodeptrai",
            url="https://fb88dq.com/cach-choi-ca-cuoc-golf",
            loai_traffic="https://fb88dq.com/",
            regex_pattern=r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>'
        ),
        
        "188bet": TrafficConfig(
            name="188BET Casino",
            api_type=APIType.GET_MA,
            codexn="taodeptrailamnhe",
            url="https://88betag.com/cach-choi-game-bai-pok-deng",
            loai_traffic="https://88betag.com/",
            regex_pattern=r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>'
        ),
        
        "w88": TrafficConfig(
            name="W88 Poker",
            api_type=APIType.GET_MA,
            codexn="taodeptrai",
            url="https://188.166.185.213/tim-hieu-khai-niem-3-bet-trong-poker-la-gi",
            loai_traffic="https://188.166.185.213/",
            regex_pattern=r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>'
        ),
        
        "v9bet": TrafficConfig(
            name="V9BET Basketball",
            api_type=APIType.GET_MA,
            codexn="taodeptrai",
            url="https://v9betho.com/ca-cuoc-bong-ro-ao",
            loai_traffic="https://v9betho.com/",
            regex_pattern=r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>'
        ),
        
        "vn88": TrafficConfig(
            name="VN88 Card Games",
            api_type=APIType.GET_MA,
            codexn="bomaydeptrai",
            url="https://vn88sv.com/cach-choi-bai-gao-gae",
            loai_traffic="https://vn88sv.com/",
            regex_pattern=r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>'
        ),
        
        "bk8": TrafficConfig(
            name="BK8 Card Games",
            api_type=APIType.GET_MA,
            codexn="taodeptrai",
            url="https://bk8ze.com/cach-choi-bai-catte",
            loai_traffic="https://bk8ze.com/",
            regex_pattern=r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>'
        ),
        
        "88betag": TrafficConfig(
            name="88BET AG Direct",
            api_type=APIType.GET_MD,
            codexn="bomaylavua",
            url="https://88betag.com/keo-chau-a-la-gi",
            loai_traffic="https://88betag.com/",
            regex_pattern=r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>'
        ),
        
        "w88abc": TrafficConfig(
            name="W88ABC Mobile Gaming",
            api_type=APIType.GET_MD,
            codexn="bomaylavua",
            url="https://w88abc.com/cach-choi-ca-cuoc-lien-quan-mobile",
            loai_traffic="https://w88abc.com/",
            regex_pattern=r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>'
        ),
        
        "v9betlg": TrafficConfig(
            name="V9BET Flat Betting",
            api_type=APIType.GET_MD,
            codexn="bomaylavua",
            url="https://v9betlg.com/phuong-phap-cuoc-flat-betting",
            loai_traffic="https://v9betlg.com/",
            regex_pattern=r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>'
        ),
        
        "bk8xo": TrafficConfig(
            name="BK8XO Lottery",
            api_type=APIType.GET_MD,
            codexn="bomaylavua",
            url="https://bk8xo.com/lo-ba-cang-la-gi",
            loai_traffic="https://bk8xo.com/",
            regex_pattern=r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>'
        ),
        
        "vn88ie": TrafficConfig(
            name="VN88IE Lottery System",
            api_type=APIType.GET_MD,
            codexn="bomaylavua",
            url="https://vn88ie.com/cach-nuoi-lo-khung",
            loai_traffic="https://vn88ie.com/",
            regex_pattern=r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>'
        ),
        
        "w88xlm": TrafficConfig(
            name="W88XLM Solitaire",
            api_type=APIType.GET_MA,
            codexn="taodeptrai",
            url="https://w88xlm.com/cach-choi-bai-solitaire",
            loai_traffic="https://w88xlm.com/",
            regex_pattern=r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>'
        )
    }
    
    def __init__(self):
        """Initialize the generator"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        logger.info("YeuMoney Generator initialized successfully")
    
    def display_welcome_message(self) -> None:
        """Display welcome message and instructions"""
        print("=" * 60)
        print("🎯 YEUMONEY CODE GENERATOR - PROFESSIONAL VERSION 🎯")
        print("=" * 60)
        print("📋 Hướng dẫn sử dụng:")
        print("   • Chọn loại quest từ danh sách bên dưới")
        print("   • Chờ khoảng 80 giây để lấy mã")
        print("   • Nhập mã vào hệ thống để hoàn thành quest")
        print("=" * 60)
        print()
    
    def display_available_types(self) -> None:
        """Display all available traffic types"""
        print("🎮 CÁC LOẠI QUEST KHẢ DỤNG:")
        print("-" * 40)
        
        for i, (key, config) in enumerate(self.TRAFFIC_CONFIGS.items(), 1):
            api_badge = "🔵 MA" if config.api_type == APIType.GET_MA else "🟢 MD"
            print(f"{i:2d}. {api_badge} {key:<12} - {config.name}")
        
        print("-" * 40)
        print("💡 Mẹo: Nhập chính xác tên quest (ví dụ: m88, fb88, v9bet...)")
        print()
    
    def validate_quest_type(self, quest_type: str) -> bool:
        """Validate if quest type is supported"""
        # Handle special cases
        if quest_type == "188.166.185.213":
            return True
        return quest_type.lower() in self.TRAFFIC_CONFIGS
    
    def get_quest_config(self, quest_type: str) -> Optional[TrafficConfig]:
        """Get configuration for quest type"""
        # Handle special case for IP address
        if quest_type == "188.166.185.213":
            return self.TRAFFIC_CONFIGS.get("w88abc")
        return self.TRAFFIC_CONFIGS.get(quest_type.lower())
    
    def make_request_with_retry(self, url: str, params: Dict) -> Optional[str]:
        """Make HTTP request with retry mechanism"""
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Attempting request (attempt {attempt + 1}/{self.MAX_RETRIES})")
                
                response = self.session.post(
                    url, 
                    data=params, 
                    timeout=self.REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                logger.info(f"Request successful (status: {response.status_code})")
                return response.text
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.MAX_RETRIES - 1:
                    logger.info(f"Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    logger.error("All retry attempts failed")
                    return None
    
    def extract_code_from_html(self, html: str, pattern: str) -> Optional[str]:
        """Extract code from HTML using regex pattern"""
        try:
            match = re.search(pattern, html)
            if match:
                code = match.group(1).strip()
                logger.info(f"Code extracted successfully: {code}")
                return code
            else:
                logger.warning("No code found in HTML response")
                return None
        except Exception as e:
            logger.error(f"Error extracting code: {str(e)}")
            return None
    
    def generate_code(self, quest_type: str) -> Tuple[bool, str]:
        """Generate code for specified quest type"""
        try:
            # Validate quest type
            if not self.validate_quest_type(quest_type):
                return False, f"❌ Loại quest '{quest_type}' không được hỗ trợ!"
            
            # Get configuration
            config = self.get_quest_config(quest_type)
            if not config:
                return False, f"❌ Không tìm thấy cấu hình cho '{quest_type}'"
            
            # Build API URL
            api_endpoint = f"{config.api_type.value}.php"
            api_url = f"{self.BASE_URL}/{api_endpoint}"
            
            # Build parameters
            codexn_param = "codexn" if config.api_type == APIType.GET_MA else "codexnd"
            params = {
                codexn_param: config.codexn,
                "url": config.url,
                "loai_traffic": config.loai_traffic,
                "clk": config.clk
            }
            
            logger.info(f"Generating code for {config.name} ({quest_type})")
            print(f"🔄 Đang xử lý quest: {config.name}")
            print("⏳ Vui lòng chờ khoảng 80 giây...")
            
            # Make request
            html_response = self.make_request_with_retry(api_url, params)
            if not html_response:
                return False, "❌ Không thể kết nối đến server hoặc request thất bại"
            
            # Extract code
            code = self.extract_code_from_html(html_response, config.regex_pattern)
            if code:
                success_msg = f"✅ Mã code thành công: {code}"
                logger.info(f"Code generation successful for {quest_type}: {code}")
                return True, success_msg
            else:
                return False, "❌ Không tìm thấy mã trong phản hồi từ server"
                
        except Exception as e:
            error_msg = f"❌ Lỗi không mong muốn: {str(e)}"
            logger.error(f"Unexpected error in generate_code: {str(e)}")
            return False, error_msg
    
    def save_generation_log(self, quest_type: str, success: bool, code: Optional[str] = None) -> None:
        """Save generation log to file"""
        try:
            log_data = {
                "timestamp": time.time(),
                "quest_type": quest_type,
                "success": success,
                "code": code
            }
            
            log_file = "code_generation_log.json"
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_data)
            
            # Keep only last 100 logs
            if len(logs) > 100:
                logs = logs[-100:]
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to save generation log: {str(e)}")
    
    def run_interactive_mode(self) -> None:
        """Run the generator in interactive mode"""
        self.display_welcome_message()
        
        while True:
            try:
                self.display_available_types()
                
                quest_type = input("🎯 Nhập loại quest (hoặc 'exit' để thoát): ").strip()
                
                if quest_type.lower() in ['exit', 'quit', 'q']:
                    print("👋 Cảm ơn bạn đã sử dụng YeuMoney Generator!")
                    break
                
                if not quest_type:
                    print("⚠️  Vui lòng nhập loại quest!")
                    continue
                
                print("\n" + "="*50)
                success, message = self.generate_code(quest_type)
                print(message)
                print("="*50 + "\n")
                
                # Save log
                code = message.split(": ")[-1] if success else None
                self.save_generation_log(quest_type, success, code)
                
                # Ask if user wants to continue
                continue_choice = input("🔄 Bạn có muốn tạo mã khác không? (y/n): ").strip().lower()
                if continue_choice not in ['y', 'yes', '']:
                    print("👋 Cảm ơn bạn đã sử dụng YeuMoney Generator!")
                    break
                    
                print("\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Cảm ơn bạn đã sử dụng YeuMoney Generator!")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {str(e)}")
                print(f"❌ Lỗi không mong muốn: {str(e)}")
                continue

def main():
    """Main function"""
    try:
        generator = YeuMoneyGenerator()
        generator.run_interactive_mode()
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        print(f"❌ Lỗi nghiêm trọng: {str(e)}")

if __name__ == "__main__":
    main()
