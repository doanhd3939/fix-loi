#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YeuMoney Code Generator - Enhanced UI Version
Author: Upgraded by AI Assistant
Description: Professional code generator with colored UI and enhanced features
"""

import requests
import re
import time
import json
import logging
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Try importing optional dependencies for enhanced UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init()
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

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
    description: str = ""

class EnhancedYeuMoneyGenerator:
    """Enhanced code generator with beautiful UI"""
    
    BASE_URL = "https://traffic-user.net"
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    
    # Enhanced configuration with descriptions
    TRAFFIC_CONFIGS: Dict[str, TrafficConfig] = {
        "m88": TrafficConfig(
            name="M88 Betting",
            api_type=APIType.GET_MA,
            codexn="taodeptrai",
            url="https://bet88ec.com/cach-danh-bai-sam-loc",
            loai_traffic="https://bet88ec.com/",
            regex_pattern=r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
            description="Cá cược thể thao và casino trực tuyến"
        ),
        
        "fb88": TrafficConfig(
            name="FB88 Sports",
            api_type=APIType.GET_MA,
            codexn="taodeptrai",
            url="https://fb88dq.com/cach-choi-ca-cuoc-golf",
            loai_traffic="https://fb88dq.com/",
            regex_pattern=r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
            description="Cá cược golf và thể thao"
        ),
        
        "188bet": TrafficConfig(
            name="188BET Casino",
            api_type=APIType.GET_MA,
            codexn="taodeptrailamnhe",
            url="https://88betag.com/cach-choi-game-bai-pok-deng",
            loai_traffic="https://88betag.com/",
            regex_pattern=r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
            description="Game bài Pok Deng online"
        ),
        
        "w88": TrafficConfig(
            name="W88 Poker",
            api_type=APIType.GET_MA,
            codexn="taodeptrai",
            url="https://188.166.185.213/tim-hieu-khai-niem-3-bet-trong-poker-la-gi",
            loai_traffic="https://188.166.185.213/",
            regex_pattern=r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
            description="Poker và game bài chuyên nghiệp"
        ),
        
        "v9bet": TrafficConfig(
            name="V9BET Basketball",
            api_type=APIType.GET_MA,
            codexn="taodeptrai",
            url="https://v9betho.com/ca-cuoc-bong-ro-ao",
            loai_traffic="https://v9betho.com/",
            regex_pattern=r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
            description="Cá cược bóng rổ ảo"
        ),
        
        "vn88": TrafficConfig(
            name="VN88 Card Games",
            api_type=APIType.GET_MA,
            codexn="bomaydeptrai",
            url="https://vn88sv.com/cach-choi-bai-gao-gae",
            loai_traffic="https://vn88sv.com/",
            regex_pattern=r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
            description="Game bài Gao Gae truyền thống"
        ),
        
        "bk8": TrafficConfig(
            name="BK8 Card Games",
            api_type=APIType.GET_MA,
            codexn="taodeptrai",
            url="https://bk8ze.com/cach-choi-bai-catte",
            loai_traffic="https://bk8ze.com/",
            regex_pattern=r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
            description="Game bài Catte online"
        ),
        
        "88betag": TrafficConfig(
            name="88BET AG Direct",
            api_type=APIType.GET_MD,
            codexn="bomaylavua",
            url="https://88betag.com/keo-chau-a-la-gi",
            loai_traffic="https://88betag.com/",
            regex_pattern=r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>',
            description="Kèo châu Á chuyên nghiệp"
        ),
        
        "w88abc": TrafficConfig(
            name="W88ABC Mobile Gaming",
            api_type=APIType.GET_MD,
            codexn="bomaylavua",
            url="https://w88abc.com/cach-choi-ca-cuoc-lien-quan-mobile",
            loai_traffic="https://w88abc.com/",
            regex_pattern=r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>',
            description="Cá cược Liên Quân Mobile"
        ),
        
        "v9betlg": TrafficConfig(
            name="V9BET Flat Betting",
            api_type=APIType.GET_MD,
            codexn="bomaylavua",
            url="https://v9betlg.com/phuong-phap-cuoc-flat-betting",
            loai_traffic="https://v9betlg.com/",
            regex_pattern=r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>',
            description="Phương pháp cược Flat Betting"
        ),
        
        "bk8xo": TrafficConfig(
            name="BK8XO Lottery",
            api_type=APIType.GET_MD,
            codexn="bomaylavua",
            url="https://bk8xo.com/lo-ba-cang-la-gi",
            loai_traffic="https://bk8xo.com/",
            regex_pattern=r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>',
            description="Lô ba càng và xổ số"
        ),
        
        "vn88ie": TrafficConfig(
            name="VN88IE Lottery System",
            api_type=APIType.GET_MD,
            codexn="bomaylavua",
            url="https://vn88ie.com/cach-nuoi-lo-khung",
            loai_traffic="https://vn88ie.com/",
            regex_pattern=r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>',
            description="Nuôi lô khung chuyên nghiệp"
        ),
        
        "w88xlm": TrafficConfig(
            name="W88XLM Solitaire",
            api_type=APIType.GET_MA,
            codexn="taodeptrai",
            url="https://w88xlm.com/cach-choi-bai-solitaire",
            loai_traffic="https://w88xlm.com/",
            regex_pattern=r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>',
            description="Game bài Solitaire kinh điển"
        )
    }
    
    def __init__(self):
        """Initialize the generator"""
        self.console = Console() if RICH_AVAILABLE else None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('yeumoney_enhanced.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Enhanced YeuMoney Generator initialized successfully")
    
    def print_colored(self, text: str, color: str = "white") -> None:
        """Print colored text if colorama is available"""
        if COLORAMA_AVAILABLE:
            colors = {
                "red": Fore.RED,
                "green": Fore.GREEN,
                "yellow": Fore.YELLOW,
                "blue": Fore.BLUE,
                "magenta": Fore.MAGENTA,
                "cyan": Fore.CYAN,
                "white": Fore.WHITE,
                "bright_green": Fore.LIGHTGREEN_EX,
                "bright_red": Fore.LIGHTRED_EX,
                "bright_yellow": Fore.LIGHTYELLOW_EX
            }
            print(f"{colors.get(color, Fore.WHITE)}{text}{Style.RESET_ALL}")
        else:
            print(text)
    
    def display_welcome_message(self) -> None:
        """Display enhanced welcome message"""
        if RICH_AVAILABLE:
            welcome_panel = Panel.fit(
                "[bold blue]🎯 YEUMONEY CODE GENERATOR - ENHANCED VERSION 🎯[/bold blue]\n"
                "[green]📋 Hướng dẫn sử dụng:[/green]\n"
                "   • Chọn loại quest từ danh sách bên dưới\n"
                "   • Chờ khoảng 80 giây để lấy mã\n"
                "   • Nhập mã vào hệ thống để hoàn thành quest\n"
                "[yellow]💡 Phiên bản nâng cấp với giao diện đẹp và xử lý lỗi tốt hơn[/yellow]",
                title="[bold magenta]YeuMoney Generator[/bold magenta]",
                border_style="blue"
            )
            self.console.print(welcome_panel)
        else:
            self.print_colored("=" * 60, "cyan")
            self.print_colored("🎯 YEUMONEY CODE GENERATOR - ENHANCED VERSION 🎯", "bright_yellow")
            self.print_colored("=" * 60, "cyan")
            self.print_colored("📋 Hướng dẫn sử dụng:", "green")
            print("   • Chọn loại quest từ danh sách bên dưới")
            print("   • Chờ khoảng 80 giây để lấy mã")
            print("   • Nhập mã vào hệ thống để hoàn thành quest")
            self.print_colored("💡 Phiên bản nâng cấp với giao diện đẹp và xử lý lỗi tốt hơn", "yellow")
            self.print_colored("=" * 60, "cyan")
            print()
    
    def display_available_types(self) -> None:
        """Display available types with enhanced formatting"""
        if RICH_AVAILABLE:
            table = Table(title="🎮 CÁC LOẠI QUEST KHẢ DỤNG", title_style="bold magenta")
            table.add_column("STT", style="cyan", width=4)
            table.add_column("API", style="green", width=6)
            table.add_column("Mã Quest", style="yellow", width=12)
            table.add_column("Tên", style="blue", width=20)
            table.add_column("Mô tả", style="white", width=30)
            
            for i, (key, config) in enumerate(self.TRAFFIC_CONFIGS.items(), 1):
                api_badge = "🔵 MA" if config.api_type == APIType.GET_MA else "🟢 MD"
                table.add_row(
                    str(i),
                    api_badge,
                    key,
                    config.name,
                    config.description
                )
            
            self.console.print(table)
            self.console.print("[bold yellow]💡 Mẹo: Nhập chính xác tên quest (ví dụ: m88, fb88, v9bet...)[/bold yellow]")
        else:
            self.print_colored("🎮 CÁC LOẠI QUEST KHẢ DỤNG:", "bright_yellow")
            self.print_colored("-" * 80, "cyan")
            
            for i, (key, config) in enumerate(self.TRAFFIC_CONFIGS.items(), 1):
                api_badge = "🔵 MA" if config.api_type == APIType.GET_MA else "🟢 MD"
                self.print_colored(f"{i:2d}. {api_badge} {key:<12} - {config.name:<20} | {config.description}", "white")
            
            self.print_colored("-" * 80, "cyan")
            self.print_colored("💡 Mẹo: Nhập chính xác tên quest (ví dụ: m88, fb88, v9bet...)", "yellow")
            print()
    
    def validate_quest_type(self, quest_type: str) -> bool:
        """Validate if quest type is supported"""
        if quest_type == "188.166.185.213":
            return True
        return quest_type.lower() in self.TRAFFIC_CONFIGS
    
    def get_quest_config(self, quest_type: str) -> Optional[TrafficConfig]:
        """Get configuration for quest type"""
        if quest_type == "188.166.185.213":
            return self.TRAFFIC_CONFIGS.get("w88abc")
        return self.TRAFFIC_CONFIGS.get(quest_type.lower())
    
    def make_request_with_retry(self, url: str, params: Dict) -> Optional[str]:
        """Make HTTP request with retry mechanism and progress indication"""
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Đang gửi yêu cầu...", total=None)
                
                for attempt in range(self.MAX_RETRIES):
                    try:
                        progress.update(task, description=f"Thử lần {attempt + 1}/{self.MAX_RETRIES}...")
                        
                        response = self.session.post(
                            url, 
                            data=params, 
                            timeout=self.REQUEST_TIMEOUT,
                            allow_redirects=True
                        )
                        response.raise_for_status()
                        
                        progress.update(task, description="✅ Yêu cầu thành công!")
                        time.sleep(0.5)  # Show success message briefly
                        return response.text
                        
                    except requests.exceptions.RequestException as e:
                        self.logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                        if attempt < self.MAX_RETRIES - 1:
                            progress.update(task, description=f"❌ Thất bại, thử lại sau {self.RETRY_DELAY}s...")
                            time.sleep(self.RETRY_DELAY)
                        else:
                            progress.update(task, description="❌ Tất cả các lần thử đều thất bại")
                            time.sleep(0.5)
                            return None
        else:
            for attempt in range(self.MAX_RETRIES):
                try:
                    self.print_colored(f"🔄 Đang thử lần {attempt + 1}/{self.MAX_RETRIES}...", "yellow")
                    
                    response = self.session.post(
                        url, 
                        data=params, 
                        timeout=self.REQUEST_TIMEOUT,
                        allow_redirects=True
                    )
                    response.raise_for_status()
                    
                    self.print_colored("✅ Yêu cầu thành công!", "green")
                    return response.text
                    
                except requests.exceptions.RequestException as e:
                    self.logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                    if attempt < self.MAX_RETRIES - 1:
                        self.print_colored(f"❌ Thất bại, thử lại sau {self.RETRY_DELAY} giây...", "red")
                        time.sleep(self.RETRY_DELAY)
                    else:
                        self.print_colored("❌ Tất cả các lần thử đều thất bại", "bright_red")
                        return None
    
    def extract_code_from_html(self, html: str, pattern: str) -> Optional[str]:
        """Extract code from HTML using regex pattern"""
        try:
            match = re.search(pattern, html)
            if match:
                code = match.group(1).strip()
                self.logger.info(f"Code extracted successfully: {code}")
                return code
            else:
                self.logger.warning("No code found in HTML response")
                return None
        except Exception as e:
            self.logger.error(f"Error extracting code: {str(e)}")
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
            
            self.logger.info(f"Generating code for {config.name} ({quest_type})")
            
            if RICH_AVAILABLE:
                self.console.print(f"🔄 Đang xử lý quest: [bold blue]{config.name}[/bold blue]")
                self.console.print("⏳ Vui lòng chờ khoảng 80 giây...")
            else:
                self.print_colored(f"🔄 Đang xử lý quest: {config.name}", "blue")
                self.print_colored("⏳ Vui lòng chờ khoảng 80 giây...", "yellow")
            
            # Make request
            html_response = self.make_request_with_retry(api_url, params)
            if not html_response:
                return False, "❌ Không thể kết nối đến server hoặc request thất bại"
            
            # Extract code
            code = self.extract_code_from_html(html_response, config.regex_pattern)
            if code:
                success_msg = f"✅ Mã code thành công: {code}"
                self.logger.info(f"Code generation successful for {quest_type}: {code}")
                return True, success_msg
            else:
                return False, "❌ Không tìm thấy mã trong phản hồi từ server"
                
        except Exception as e:
            error_msg = f"❌ Lỗi không mong muốn: {str(e)}"
            self.logger.error(f"Unexpected error in generate_code: {str(e)}")
            return False, error_msg
    
    def run_interactive_mode(self) -> None:
        """Run the generator in enhanced interactive mode"""
        self.display_welcome_message()
        
        while True:
            try:
                self.display_available_types()
                
                if RICH_AVAILABLE:
                    quest_type = Prompt.ask(
                        "🎯 Nhập loại quest (hoặc 'exit' để thoát)",
                        console=self.console
                    ).strip()
                else:
                    quest_type = input("🎯 Nhập loại quest (hoặc 'exit' để thoát): ").strip()
                
                if quest_type.lower() in ['exit', 'quit', 'q']:
                    if RICH_AVAILABLE:
                        self.console.print("👋 Cảm ơn bạn đã sử dụng YeuMoney Generator!", style="bold green")
                    else:
                        self.print_colored("👋 Cảm ơn bạn đã sử dụng YeuMoney Generator!", "green")
                    break
                
                if not quest_type:
                    if RICH_AVAILABLE:
                        self.console.print("⚠️  Vui lòng nhập loại quest!", style="bold yellow")
                    else:
                        self.print_colored("⚠️  Vui lòng nhập loại quest!", "yellow")
                    continue
                
                # Generate code
                if RICH_AVAILABLE:
                    self.console.print(Panel("", title="[bold blue]Đang xử lý...[/bold blue]"))
                else:
                    self.print_colored("\n" + "="*50, "cyan")
                
                success, message = self.generate_code(quest_type)
                
                if RICH_AVAILABLE:
                    if success:
                        self.console.print(Panel(message, title="[bold green]Kết quả[/bold green]", border_style="green"))
                    else:
                        self.console.print(Panel(message, title="[bold red]Lỗi[/bold red]", border_style="red"))
                else:
                    if success:
                        self.print_colored(message, "bright_green")
                    else:
                        self.print_colored(message, "bright_red")
                    self.print_colored("="*50 + "\n", "cyan")
                
                # Ask if user wants to continue
                if RICH_AVAILABLE:
                    continue_choice = Confirm.ask("🔄 Bạn có muốn tạo mã khác không?", console=self.console)
                else:
                    continue_input = input("🔄 Bạn có muốn tạo mã khác không? (y/n): ").strip().lower()
                    continue_choice = continue_input in ['y', 'yes', '']
                
                if not continue_choice:
                    if RICH_AVAILABLE:
                        self.console.print("👋 Cảm ơn bạn đã sử dụng YeuMoney Generator!", style="bold green")
                    else:
                        self.print_colored("👋 Cảm ơn bạn đã sử dụng YeuMoney Generator!", "green")
                    break
                    
                print("\n")
                
            except KeyboardInterrupt:
                if RICH_AVAILABLE:
                    self.console.print("\n\n👋 Cảm ơn bạn đã sử dụng YeuMoney Generator!", style="bold green")
                else:
                    self.print_colored("\n\n👋 Cảm ơn bạn đã sử dụng YeuMoney Generator!", "green")
                break
            except Exception as e:
                self.logger.error(f"Error in interactive mode: {str(e)}")
                if RICH_AVAILABLE:
                    self.console.print(f"❌ Lỗi không mong muốn: {str(e)}", style="bold red")
                else:
                    self.print_colored(f"❌ Lỗi không mong muốn: {str(e)}", "bright_red")
                continue

def main():
    """Main function"""
    try:
        generator = EnhancedYeuMoneyGenerator()
        generator.run_interactive_mode()
    except Exception as e:
        print(f"❌ Lỗi nghiêm trọng: {str(e)}")

if __name__ == "__main__":
    main()
