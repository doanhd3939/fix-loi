#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YeuMoney Code Generator Pro - Main Entry Point
==============================================

Professional multi-service application launcher with:
- Web interface
- Telegram bot  
- Command line interface
- Background services

Usage:
    python main.py --help
    python main.py web
    python main.py bot
    python main.py cli
    python main.py all

Author: Professional Team
Version: 3.0.0
"""

import os
import sys
import asyncio
import logging
import argparse
import threading
import signal
import time
from typing import Optional, List
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.core.config import config
    from src.core.database import db
    from src.utils.helpers import format_datetime, ensure_directory
    from src.utils.security import SecurityManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔧 Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

class YeuMoneyLauncher:
    """Professional application launcher"""
    
    def __init__(self):
        self.services = {}
        self.running = False
        self.setup_logging()
        self.setup_signal_handlers()
        
        print(self.get_banner())
        logging.info("YeuMoney Pro Launcher initialized")
    
    def get_banner(self) -> str:
        """Get application banner"""
        return """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    ╔╗  ╔╗            ╔═══╗                               ╔═══╗              ║
║    ║╚╗╔╝║            ║╔═╗║                               ║╔═╗║              ║
║    ╚╗╚╝╔╝╔══╗╔╗╔╣    ║║ ║║╔══╗╔═╗╔══╗╔╗ ╔╗    ╔═══╗╔══╗║║ ║║╔══╗╔══╗       ║
║     ╚╗╔╝ ║╔╗║║║║║    ║║ ║║║╔╗║║╔╗╣║╔╗║║║ ║║    ║╔═╗║║╔╗║║║ ║║║╔╗║║╔╗║       ║
║      ║║  ║║═╣║╚╝║    ║╚═╝║║║═╣║║║║║║═╣║╚═╝║    ║╚═╝║║║═╣║╚═╝║║║═╣║║═╣       ║
║      ╚╝  ╚══╝╚══╝    ╚═══╝╚══╝╚╝╚╝╚══╝╚═╗╔╝    ║╔══╝╚══╝╚═══╝╚══╝╚══╝       ║
║                                        ╔═╝║     ║║                          ║
║                                        ╚══╝     ╚╝                          ║
║                                                                              ║
║                         Code Generator Professional                          ║
║                               Version 3.0.0                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
    
    def setup_logging(self):
        """Setup professional logging"""
        log_dir = Path("logs")
        ensure_directory(str(log_dir))
        
        log_file = log_dir / "yeumoney.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Reduce noise from external libraries
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('telegram').setLevel(logging.INFO)
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logging.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.stop()
    
    def start_web_service(self):
        """Start web interface"""
        try:
            from src.web.app import web_interface
            
            host = config.get('web_config.host', '0.0.0.0')
            port = config.get('web_config.port', 5000)
            debug = config.get('web_config.debug', False)
            
            logging.info(f"🌐 Starting web interface on {host}:{port}")
            print(f"🌐 Web interface: http://{host}:{port}")
            
            def run_web():
                web_interface.run(host=host, port=port, debug=debug)
            
            web_thread = threading.Thread(target=run_web, daemon=True)
            web_thread.start()
            
            self.services['web'] = {
                'thread': web_thread,
                'name': 'Web Interface',
                'status': 'running',
                'url': f"http://{host}:{port}"
            }
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to start web service: {e}")
            return False
    
    def start_bot_service(self):
        """Start Telegram bot"""
        try:
            from src.bot.telegram_bot import telegram_bot
            
            bot_token = config.get('bot_config.token')
            if not bot_token:
                logging.error("❌ Bot token not configured!")
                return False
            
            logging.info("🤖 Starting Telegram bot...")
            print("🤖 Telegram bot starting...")
            
            async def run_bot():
                await telegram_bot.initialize()
                await telegram_bot.start()
            
            def bot_wrapper():
                asyncio.run(run_bot())
            
            bot_thread = threading.Thread(target=bot_wrapper, daemon=True)
            bot_thread.start()
            
            self.services['bot'] = {
                'thread': bot_thread,
                'name': 'Telegram Bot',
                'status': 'running',
                'token': bot_token[:10] + "..."
            }
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to start bot service: {e}")
            return False
    
    def start_cli_service(self):
        """Start CLI interface"""
        try:
            from src.core.cli import CLIInterface
            
            logging.info("💻 Starting CLI interface...")
            print("💻 CLI interface ready")
            
            cli = CLIInterface()
            
            def run_cli():
                cli.run()
            
            cli_thread = threading.Thread(target=run_cli, daemon=True)
            cli_thread.start()
            
            self.services['cli'] = {
                'thread': cli_thread,
                'name': 'CLI Interface',
                'status': 'running'
            }
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to start CLI service: {e}")
            return False
    
    def start_background_services(self):
        """Start background maintenance services"""
        try:
            logging.info("🔧 Starting background services...")
            
            def cleanup_task():
                while self.running:
                    try:
                        # Cleanup expired keys
                        cleaned = db.cleanup_expired_keys()
                        if cleaned > 0:
                            logging.info(f"Cleaned up {cleaned} expired keys")
                        
                        # Create backup
                        backup_path = db.create_backup()
                        if backup_path:
                            logging.info(f"Database backup created: {backup_path}")
                        
                        # Security cleanup
                        security = SecurityManager()
                        security.cleanup_old_data()
                        
                        time.sleep(300)  # Run every 5 minutes
                        
                    except Exception as e:
                        logging.error(f"Background task error: {e}")
                        time.sleep(60)  # Retry after 1 minute
            
            cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
            cleanup_thread.start()
            
            self.services['background'] = {
                'thread': cleanup_thread,
                'name': 'Background Services',
                'status': 'running'
            }
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to start background services: {e}")
            return False
    
    def show_status(self):
        """Show service status"""
        print("\n" + "="*80)
        print("📊 SERVICE STATUS")
        print("="*80)
        
        if not self.services:
            print("❌ No services running")
            return
        
        for service_id, service_info in self.services.items():
            status_icon = "✅" if service_info['status'] == 'running' else "❌"
            print(f"{status_icon} {service_info['name']}")
            
            if 'url' in service_info:
                print(f"   🔗 URL: {service_info['url']}")
            if 'token' in service_info:
                print(f"   🔑 Token: {service_info['token']}")
        
        print("\n📈 SYSTEM STATS")
        print("-"*40)
        
        try:
            stats = db.get_system_stats()
            print(f"👥 Total users: {stats.total_users:,}")
            print(f"🔑 Active keys: {stats.active_keys:,}")
            print(f"📊 Total requests: {stats.total_requests:,}")
            print(f"✅ Success rate: {stats.success_rate():.1f}%")
        except Exception as e:
            print(f"❌ Could not load stats: {e}")
        
        print("="*80)
    
    def stop(self):
        """Stop all services"""
        self.running = False
        
        print("\n🛑 Stopping services...")
        logging.info("Stopping all services...")
        
        for service_id, service_info in self.services.items():
            try:
                service_info['status'] = 'stopping'
                logging.info(f"Stopping {service_info['name']}...")
                
                # Give services time to cleanup
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Error stopping {service_info['name']}: {e}")
        
        logging.info("All services stopped")
        print("✅ Shutdown complete")
    
    def run_web(self):
        """Run web interface only"""
        self.running = True
        if self.start_web_service():
            self.keep_alive()
    
    def run_bot(self):
        """Run Telegram bot only"""
        self.running = True
        if self.start_bot_service():
            self.keep_alive()
    
    def run_cli(self):
        """Run CLI interface only"""
        self.running = True
        if self.start_cli_service():
            self.keep_alive()
    
    def run_all(self):
        """Run all services"""
        self.running = True
        
        print("🚀 Starting all services...")
        
        # Start services
        services_started = []
        
        if self.start_web_service():
            services_started.append("Web")
        
        if self.start_bot_service():
            services_started.append("Bot")
        
        if self.start_background_services():
            services_started.append("Background")
        
        if services_started:
            print(f"✅ Started services: {', '.join(services_started)}")
            self.show_status()
            self.keep_alive()
        else:
            print("❌ Failed to start any services")
            sys.exit(1)
    
    def keep_alive(self):
        """Keep the application running"""
        try:
            print(f"\n🎯 YeuMoney Pro is running! Press Ctrl+C to stop")
            print(f"📝 Logs: logs/yeumoney.log")
            print(f"⏰ Started: {format_datetime(None)}")
            
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="YeuMoney Code Generator Pro - Professional Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py web          # Start web interface only
  python main.py bot          # Start Telegram bot only  
  python main.py cli          # Start CLI interface only
  python main.py all          # Start all services (recommended)
  python main.py --status     # Show system status

For more information, visit: https://yeumoney.pro
        """
    )
    
    parser.add_argument(
        'service',
        nargs='?',
        choices=['web', 'bot', 'cli', 'all'],
        default='all',
        help='Service to run (default: all)'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show system status and exit'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f"YeuMoney Pro {config.get('app_config.version', '3.0.0')}"
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    # Initialize launcher
    launcher = YeuMoneyLauncher()
    
    try:
        if args.status:
            launcher.show_status()
            return
        
        # Run selected service
        if args.service == 'web':
            launcher.run_web()
        elif args.service == 'bot':
            launcher.run_bot()
        elif args.service == 'cli':
            launcher.run_cli()
        elif args.service == 'all':
            launcher.run_all()
        
    except Exception as e:
        logging.error(f"Critical error: {e}")
        print(f"💥 Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
