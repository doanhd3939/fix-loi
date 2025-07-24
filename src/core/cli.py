"""
Command Line Interface for YeuMoney Code Generator Pro
"""

import os
import sys
import time
import logging
from typing import Optional, Dict, List
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import track
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from src.core.config import config
from src.core.database import db
from src.api.client import api_client
from src.models.models import User, APIKey, UserRole, KeyStatus
from src.utils.helpers import format_datetime, generate_key

class CLIInterface:
    """Professional command line interface"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.running = True
        
        if RICH_AVAILABLE:
            self.console.print("\n[bold green]YeuMoney Code Generator Pro - CLI Mode[/bold green]")
            self.console.print("[dim]Professional command line interface[/dim]\n")
        else:
            print("\n🎯 YeuMoney Code Generator Pro - CLI Mode")
            print("Professional command line interface\n")
    
    def print_message(self, message: str, style: str = ""):
        """Print message with optional styling"""
        if self.console and style:
            self.console.print(message, style=style)
        else:
            print(message)
    
    def print_panel(self, content: str, title: str = "", style: str = "blue"):
        """Print content in a panel"""
        if self.console:
            self.console.print(Panel(content, title=title, border_style=style))
        else:
            print(f"\n=== {title} ===")
            print(content)
            print("=" * (len(title) + 8))
    
    def get_input(self, prompt: str, default: str = "") -> str:
        """Get user input with optional default"""
        if RICH_AVAILABLE:
            return Prompt.ask(prompt, default=default) if default else Prompt.ask(prompt)
        else:
            user_input = input(f"{prompt}: ")
            return user_input if user_input else default
    
    def get_confirmation(self, prompt: str) -> bool:
        """Get yes/no confirmation from user"""
        if RICH_AVAILABLE:
            return Confirm.ask(prompt)
        else:
            while True:
                response = input(f"{prompt} (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                else:
                    print("Please enter 'y' for yes or 'n' for no.")
    
    def show_menu(self):
        """Show main menu"""
        menu_items = [
            "1. Generate Code",
            "2. Manage API Keys", 
            "3. View Statistics",
            "4. System Status",
            "5. Configuration",
            "6. Help",
            "0. Exit"
        ]
        
        if self.console:
            table = Table(title="Main Menu", show_header=False, box=None)
            table.add_column("Options", style="cyan")
            
            for item in menu_items:
                table.add_row(item)
            
            self.console.print(table)
        else:
            print("\n=== Main Menu ===")
            for item in menu_items:
                print(item)
            print("=" * 18)
    
    def generate_code_menu(self):
        """Code generation menu"""
        self.print_panel("Code Generation", "Generate Code", "green")
        
        # Get available traffic types
        traffic_types = config.get_all_traffic_types()
        
        if not traffic_types:
            self.print_message("❌ No traffic types configured!", "red")
            return
        
        # Show traffic types
        if self.console:
            table = Table(title="Available Traffic Types")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green") 
            table.add_column("Type", style="yellow")
            table.add_column("Description", style="dim")
            
            for i, traffic_type in enumerate(traffic_types, 1):
                traffic_config = config.get_traffic_config(traffic_type)
                if traffic_config:
                    table.add_row(
                        str(i),
                        traffic_config.name,
                        traffic_config.api_type.value,
                        traffic_config.description
                    )
            
            self.console.print(table)
        else:
            print("\nAvailable Traffic Types:")
            for i, traffic_type in enumerate(traffic_types, 1):
                traffic_config = config.get_traffic_config(traffic_type)
                if traffic_config:
                    print(f"{i}. {traffic_config.name} ({traffic_config.api_type.value})")
        
        # Get user selection
        try:
            choice = int(self.get_input("Select traffic type (number)"))
            if 1 <= choice <= len(traffic_types):
                selected_type = traffic_types[choice - 1]
                self.generate_code(selected_type)
            else:
                self.print_message("❌ Invalid selection!", "red")
        except ValueError:
            self.print_message("❌ Please enter a valid number!", "red")
    
    def generate_code(self, traffic_type: str):
        """Generate code for specific traffic type"""
        traffic_config = config.get_traffic_config(traffic_type)
        if not traffic_config:
            self.print_message(f"❌ Traffic type '{traffic_type}' not found!", "red")
            return
        
        # Get API key
        api_key = self.get_input("Enter API Key")
        if not api_key:
            self.print_message("❌ API Key is required!", "red")
            return
        
        # Validate key
        key_obj = db.get_api_key(api_key)
        if not key_obj or not key_obj.is_valid():
            self.print_message("❌ Invalid or expired API key!", "red")
            return
        
        # Generate code
        self.print_message(f"🔄 Generating code for {traffic_config.name}...", "yellow")
        
        try:
            if RICH_AVAILABLE:
                with self.console.status("[bold green]Processing..."):
                    response = api_client.generate_code(traffic_config, key_obj.user_id)
            else:
                response = api_client.generate_code(traffic_config, key_obj.user_id)
            
            if response.success:
                # Update key usage
                key_obj.usage_count += 1
                db.update_api_key(key_obj)
                
                # Show success
                success_content = f"""
[bold green]✅ Code Generated Successfully![/bold green]

[bold]Traffic:[/bold] {traffic_config.name}
[bold]Code:[/bold] [cyan]{response.code}[/cyan]
[bold]Processing Time:[/bold] {response.processing_time:.2f}s
[bold]Key Usage:[/bold] {key_obj.usage_count} times
                """.strip()
                
                self.print_panel(success_content, "Success", "green")
                
                # Copy option
                if self.get_confirmation("Copy code to clipboard?"):
                    try:
                        import pyperclip
                        pyperclip.copy(response.code)
                        self.print_message("✅ Code copied to clipboard!", "green")
                    except ImportError:
                        self.print_message("❌ Clipboard functionality not available (install pyperclip)", "yellow")
                
            else:
                error_content = f"""
[bold red]❌ Code Generation Failed![/bold red]

[bold]Traffic:[/bold] {traffic_config.name}
[bold]Error:[/bold] {response.error_message}
[bold]Processing Time:[/bold] {response.processing_time:.2f}s
                """.strip()
                
                self.print_panel(error_content, "Error", "red")
                
        except Exception as e:
            self.print_message(f"💥 Unexpected error: {e}", "red")
    
    def manage_keys_menu(self):
        """API key management menu"""
        self.print_panel("API Key Management", "Manage Keys", "blue")
        
        key_menu = [
            "1. View My Keys",
            "2. Create New Key", 
            "3. Validate Key",
            "4. Key Statistics",
            "0. Back to Main Menu"
        ]
        
        if self.console:
            for item in key_menu:
                self.console.print(f"  {item}")
        else:
            for item in key_menu:
                print(f"  {item}")
        
        choice = self.get_input("Select option")
        
        if choice == "1":
            self.view_keys()
        elif choice == "2":
            self.create_key()
        elif choice == "3":
            self.validate_key()
        elif choice == "4":
            self.key_statistics()
        elif choice == "0":
            return
        else:
            self.print_message("❌ Invalid option!", "red")
    
    def view_keys(self):
        """View user's API keys"""
        user_id = self.get_user_id()
        if not user_id:
            return
        
        keys = db.get_user_keys(user_id)
        
        if not keys:
            self.print_message("📭 No API keys found for this user.", "yellow")
            return
        
        if self.console:
            table = Table(title=f"API Keys for User {user_id}")
            table.add_column("Key", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Created", style="dim")
            table.add_column("Expires", style="yellow")
            table.add_column("Usage", style="blue")
            
            for key in keys:
                status = "✅ Active" if key.is_valid() else "❌ Invalid"
                expires = format_datetime(key.expires_at) if key.expires_at else "Never"
                
                table.add_row(
                    key.key[:20] + "...",
                    status,
                    format_datetime(key.created_at),
                    expires,
                    str(key.usage_count)
                )
            
            self.console.print(table)
        else:
            print(f"\nAPI Keys for User {user_id}:")
            print("-" * 60)
            for i, key in enumerate(keys, 1):
                status = "Active" if key.is_valid() else "Invalid"
                expires = format_datetime(key.expires_at) if key.expires_at else "Never"
                
                print(f"{i}. Key: {key.key[:20]}...")
                print(f"   Status: {status}")
                print(f"   Created: {format_datetime(key.created_at)}")
                print(f"   Expires: {expires}")
                print(f"   Usage: {key.usage_count} times")
                print()
    
    def create_key(self):
        """Create new API key"""
        self.print_message("🔑 Creating new API key...", "yellow")
        
        user_id = self.get_user_id()
        if not user_id:
            return
        
        # Check existing keys
        existing_keys = db.get_user_keys(user_id)
        active_keys = [k for k in existing_keys if k.is_valid()]
        
        max_keys = config.get('bot_config.max_keys_per_user', 1)
        if len(active_keys) >= max_keys:
            self.print_message(f"❌ User already has maximum number of keys ({max_keys})", "red")
            return
        
        # Create key
        new_key = generate_key()
        lifetime_hours = config.get('bot_config.key_lifetime_hours', 24)
        expires_at = datetime.now().replace(microsecond=0) + \
                    datetime.timedelta(hours=lifetime_hours)
        
        api_key = APIKey(
            key=new_key,
            user_id=user_id,
            expires_at=expires_at,
            metadata={
                'created_by': 'cli',
                'created_via': 'command_line'
            }
        )
        
        if db.create_api_key(api_key):
            success_content = f"""
[bold green]✅ API Key Created Successfully![/bold green]

[bold]Key:[/bold] [cyan]{new_key}[/cyan]
[bold]User ID:[/bold] {user_id}
[bold]Expires:[/bold] {format_datetime(expires_at)}
[bold]Lifetime:[/bold] {lifetime_hours} hours

[yellow]⚠️ Save this key securely. It cannot be recovered![/yellow]
            """.strip()
            
            self.print_panel(success_content, "New API Key", "green")
        else:
            self.print_message("❌ Failed to create API key!", "red")
    
    def validate_key(self):
        """Validate an API key"""
        api_key = self.get_input("Enter API Key to validate")
        if not api_key:
            return
        
        key_obj = db.get_api_key(api_key)
        
        if not key_obj:
            self.print_message("❌ Key not found!", "red")
            return
        
        is_valid = key_obj.is_valid()
        
        if self.console:
            status_style = "green" if is_valid else "red"
            status_text = "✅ Valid" if is_valid else "❌ Invalid"
            
            validation_content = f"""
[bold]Key:[/bold] {api_key}
[bold]Status:[/bold] [{status_style}]{status_text}[/{status_style}]
[bold]User ID:[/bold] {key_obj.user_id}
[bold]Created:[/bold] {format_datetime(key_obj.created_at)}
[bold]Expires:[/bold] {format_datetime(key_obj.expires_at) if key_obj.expires_at else 'Never'}
[bold]Usage Count:[/bold] {key_obj.usage_count}
[bold]Current Status:[/bold] {key_obj.status.value}
            """.strip()
            
            self.print_panel(validation_content, "Key Validation", status_style)
        else:
            status_text = "Valid" if is_valid else "Invalid"
            print(f"\nKey Validation Result:")
            print(f"Key: {api_key}")
            print(f"Status: {status_text}")
            print(f"User ID: {key_obj.user_id}")
            print(f"Created: {format_datetime(key_obj.created_at)}")
            print(f"Expires: {format_datetime(key_obj.expires_at) if key_obj.expires_at else 'Never'}")
            print(f"Usage Count: {key_obj.usage_count}")
    
    def key_statistics(self):
        """Show key statistics"""
        stats = db.get_system_stats()
        
        stats_content = f"""
[bold blue]📊 Key Statistics[/bold blue]

[bold]Active Keys:[/bold] {stats.active_keys:,}
[bold]Total Users:[/bold] {stats.total_users:,}
[bold]Total Requests:[/bold] {stats.total_requests:,}
[bold]Success Rate:[/bold] {stats.success_rate():.1f}%
[bold]Last Updated:[/bold] {format_datetime(stats.last_updated)}
        """.strip()
        
        self.print_panel(stats_content, "Statistics", "blue")
    
    def get_user_id(self) -> Optional[int]:
        """Get user ID from input"""
        try:
            user_id = int(self.get_input("Enter User ID"))
            return user_id
        except ValueError:
            self.print_message("❌ Invalid User ID!", "red")
            return None
    
    def view_statistics(self):
        """View system statistics"""
        self.print_message("📊 Loading statistics...", "yellow")
        
        try:
            stats = db.get_system_stats()
            
            if self.console:
                table = Table(title="System Statistics")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Total Users", f"{stats.total_users:,}")
                table.add_row("Active Keys", f"{stats.active_keys:,}")
                table.add_row("Total Requests", f"{stats.total_requests:,}")
                table.add_row("Successful Requests", f"{stats.successful_requests:,}")
                table.add_row("Failed Requests", f"{stats.failed_requests:,}")
                table.add_row("Success Rate", f"{stats.success_rate():.1f}%")
                table.add_row("Last Updated", format_datetime(stats.last_updated))
                
                self.console.print(table)
            else:
                print("\n=== System Statistics ===")
                print(f"Total Users: {stats.total_users:,}")
                print(f"Active Keys: {stats.active_keys:,}")
                print(f"Total Requests: {stats.total_requests:,}")
                print(f"Successful Requests: {stats.successful_requests:,}")
                print(f"Failed Requests: {stats.failed_requests:,}")
                print(f"Success Rate: {stats.success_rate():.1f}%")
                print(f"Last Updated: {format_datetime(stats.last_updated)}")
                print("=" * 26)
                
        except Exception as e:
            self.print_message(f"❌ Error loading statistics: {e}", "red")
    
    def system_status(self):
        """Show system status"""
        self.print_message("🔍 Checking system status...", "yellow")
        
        # Check API health
        try:
            health = api_client.get_health_status()
            api_status = "✅ Healthy" if health.get('healthy', False) else "❌ Unhealthy"
            response_time = health.get('response_time', 0)
        except Exception as e:
            api_status = f"❌ Error: {e}"
            response_time = 0
        
        # Check database
        try:
            db.get_system_stats()
            db_status = "✅ Connected"
        except Exception as e:
            db_status = f"❌ Error: {e}"
        
        status_content = f"""
[bold blue]🔍 System Status[/bold blue]

[bold]API Status:[/bold] {api_status}
[bold]Response Time:[/bold] {response_time:.3f}s
[bold]Database:[/bold] {db_status}
[bold]Configuration:[/bold] ✅ Loaded
[bold]Timestamp:[/bold] {format_datetime(datetime.now())}
        """.strip()
        
        self.print_panel(status_content, "System Status", "blue")
    
    def show_configuration(self):
        """Show current configuration"""
        config_content = f"""
[bold blue]⚙️ Configuration[/bold blue]

[bold]App Version:[/bold] {config.get('app_config.version', 'Unknown')}
[bold]API Base URL:[/bold] {config.get('api_config.base_url', 'Not set')}
[bold]Request Timeout:[/bold] {config.get('api_config.request_timeout', 30)}s
[bold]Max Retries:[/bold] {config.get('api_config.max_retries', 3)}
[bold]Key Lifetime:[/bold] {config.get('bot_config.key_lifetime_hours', 24)}h
[bold]Max Keys per User:[/bold] {config.get('bot_config.max_keys_per_user', 1)}
[bold]Traffic Sources:[/bold] {len(config.get_all_traffic_types())}
        """.strip()
        
        self.print_panel(config_content, "Configuration", "blue")
    
    def show_help(self):
        """Show help information"""
        help_content = """
[bold green]📖 YeuMoney CLI Help[/bold green]

[bold]Main Features:[/bold]
• Generate codes from 13+ traffic sources
• Manage API keys (create, validate, view)
• View system statistics and status
• Configuration management

[bold]Getting Started:[/bold]
1. Create an API key using option 2
2. Use the key to generate codes with option 1
3. Monitor usage with statistics (option 3)

[bold]Tips:[/bold]
• Keep your API keys secure
• Keys expire after 24 hours by default
• Each user can have 1 active key at a time
• Use Telegram bot for easier key management

[bold]Support:[/bold]
• Telegram: @YeuMoneySupport
• Website: https://yeumoney.pro
        """.strip()
        
        self.print_panel(help_content, "Help", "green")
    
    def run(self):
        """Main CLI loop"""
        try:
            while self.running:
                self.show_menu()
                
                choice = self.get_input("\nSelect option")
                
                if choice == "1":
                    self.generate_code_menu()
                elif choice == "2":
                    self.manage_keys_menu()
                elif choice == "3":
                    self.view_statistics()
                elif choice == "4":
                    self.system_status()
                elif choice == "5":
                    self.show_configuration()
                elif choice == "6":
                    self.show_help()
                elif choice == "0":
                    if self.get_confirmation("Are you sure you want to exit?"):
                        self.running = False
                else:
                    self.print_message("❌ Invalid option! Please try again.", "red")
                
                if self.running:
                    input("\nPress Enter to continue...")
                    if self.console:
                        self.console.clear()
                    else:
                        os.system('cls' if os.name == 'nt' else 'clear')
        
        except KeyboardInterrupt:
            self.print_message("\n\n👋 Goodbye!", "yellow")
        except Exception as e:
            self.print_message(f"\n💥 Unexpected error: {e}", "red")
            logging.error(f"CLI error: {e}")
        finally:
            self.running = False
