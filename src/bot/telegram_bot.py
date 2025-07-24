"""
Professional Telegram Bot for YeuMoney system
"""

import os
import asyncio
import logging
import time
import string
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.constants import ParseMode

from src.models.models import User, APIKey, UserRole, KeyStatus
from src.core.config import config
from src.core.database import db
from src.api.client import api_client
from src.utils.security import SecurityManager
from src.utils.helpers import format_datetime, generate_key

class TelegramBot:
    """Professional Telegram Bot"""
    
    def __init__(self):
        self.token = config.get('bot_config.token')
        self.master_admin_id = config.get('bot_config.master_admin_id', 7509896689)
        self.key_lifetime_hours = config.get('bot_config.key_lifetime_hours', 24)
        self.max_keys_per_user = config.get('bot_config.max_keys_per_user', 1)
        self.cooldown_minutes = config.get('bot_config.cooldown_minutes', 60)
        
        self.security = SecurityManager()
        self.application = None
        self.user_cooldowns = {}  # user_id -> last_command_time
        
        if not self.token:
            raise ValueError("Bot token not configured")
        
        logging.info("TelegramBot initialized")
    
    async def initialize(self):
        """Initialize the bot application"""
        self.application = ApplicationBuilder().token(self.token).build()
        
        # Register command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("key", self.key_command))
        self.application.add_handler(CommandHandler("mykeys", self.mykeys_command))
        self.application.add_handler(CommandHandler("generate", self.generate_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        
        # Admin commands
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("taokey", self.create_key_command))
        self.application.add_handler(CommandHandler("listkey", self.list_keys_command))
        self.application.add_handler(CommandHandler("deletekey", self.delete_key_command))
        self.application.add_handler(CommandHandler("keyinfo", self.key_info_command))
        self.application.add_handler(CommandHandler("ban", self.ban_command))
        self.application.add_handler(CommandHandler("unban", self.unban_command))
        self.application.add_handler(CommandHandler("broadcast", self.broadcast_command))
        self.application.add_handler(CommandHandler("addadmin", self.add_admin_command))
        self.application.add_handler(CommandHandler("deladmin", self.del_admin_command))
        self.application.add_handler(CommandHandler("listadmin", self.list_admin_command))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Set bot commands
        await self.set_bot_commands()
        
        logging.info("Bot handlers registered")
    
    async def set_bot_commands(self):
        """Set bot commands menu"""
        commands = [
            BotCommand("start", "🚀 Bắt đầu sử dụng bot"),
            BotCommand("help", "❓ Hướng dẫn sử dụng"),
            BotCommand("key", "🔑 Tạo KEY sử dụng"),
            BotCommand("mykeys", "📋 Xem KEY của tôi"),
            BotCommand("generate", "⚡ Tạo mã code"),
            BotCommand("stats", "📊 Thống kê hệ thống"),
        ]
        
        await self.application.bot.set_my_commands(commands)
    
    async def start(self):
        """Start the bot"""
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(
            allowed_updates=Update.ALL_TYPES
        )
        logging.info("Bot started successfully")
    
    async def stop(self):
        """Stop the bot"""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
        logging.info("Bot stopped")
    
    # Utility methods
    def get_or_create_user(self, telegram_user) -> User:
        """Get or create user from Telegram user object"""
        user = db.get_user(telegram_user.id)
        if not user:
            user = User(
                user_id=telegram_user.id,
                username=telegram_user.username or "",
                first_name=telegram_user.first_name or "",
                last_name=telegram_user.last_name or "",
                role=UserRole.MASTER_ADMIN if telegram_user.id == self.master_admin_id else UserRole.USER
            )
            db.create_user(user)
        else:
            # Update user info
            user.username = telegram_user.username or ""
            user.first_name = telegram_user.first_name or ""
            user.last_name = telegram_user.last_name or ""
            user.last_seen = datetime.now()
            db.update_user(user)
        
        return user
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        user = db.get_user(user_id)
        return user and user.role in [UserRole.ADMIN, UserRole.MASTER_ADMIN]
    
    def is_master_admin(self, user_id: int) -> bool:
        """Check if user is master admin"""
        return user_id == self.master_admin_id
    
    def check_cooldown(self, user_id: int) -> bool:
        """Check if user is in cooldown"""
        if user_id in self.user_cooldowns:
            last_time = self.user_cooldowns[user_id]
            if time.time() - last_time < self.cooldown_minutes * 60:
                return False
        return True
    
    def set_cooldown(self, user_id: int):
        """Set cooldown for user"""
        self.user_cooldowns[user_id] = time.time()
    
    async def send_typing(self, update: Update):
        """Send typing indicator"""
        await update.effective_chat.send_action("typing")
    
    # Command handlers
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = self.get_or_create_user(update.effective_user)
        
        if user.is_banned:
            if user.ban_until and datetime.now() > user.ban_until:
                # Unban expired bans
                user.is_banned = False
                user.ban_until = None
                user.ban_reason = ""
                db.update_user(user)
            else:
                await update.message.reply_text(
                    f"🚫 Bạn đã bị cấm sử dụng bot!\n"
                    f"Lý do: {user.ban_reason}\n"
                    f"Hết hạn: {format_datetime(user.ban_until) if user.ban_until else 'Vĩnh viễn'}"
                )
                return
        
        welcome_text = (
            "🎯 <b>Chào mừng đến với YeuMoney Code Generator Pro!</b>\n\n"
            "🔥 <b>Tính năng nổi bật:</b>\n"
            "• 🚀 Tạo code từ 13+ nguồn traffic\n"
            "• 🔑 Hệ thống KEY bảo mật cao\n"
            "• ⚡ Xử lý nhanh chóng, ổn định\n"
            "• 📊 Thống kê chi tiết\n"
            "• 👨‍💼 Hỗ trợ 24/7\n\n"
            "📝 <b>Bắt đầu:</b>\n"
            "1️⃣ Dùng /key để tạo KEY\n"
            "2️⃣ Dùng /generate để tạo code\n"
            "3️⃣ Dùng /help để xem hướng dẫn\n\n"
            "💡 <i>Tip: Sử dụng menu lệnh bên dưới để truy cập nhanh!</i>"
        )
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔑 Tạo KEY", callback_data="create_key"),
                InlineKeyboardButton("⚡ Tạo Code", callback_data="generate_code")
            ],
            [
                InlineKeyboardButton("📋 My KEYs", callback_data="my_keys"),
                InlineKeyboardButton("📊 Thống kê", callback_data="stats")
            ],
            [
                InlineKeyboardButton("❓ Hướng dẫn", callback_data="help"),
                InlineKeyboardButton("🌐 Website", url="https://yeumoney.pro")
            ]
        ])
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "📖 <b>HƯỚNG DẪN SỬ DỤNG BOT</b>\n"
            "═══════════════════════════════\n\n"
            "🔑 <b>QUẢN LÝ KEY</b>\n"
            "• <code>/key</code> - Tạo KEY mới (24h)\n"
            "• <code>/mykeys</code> - Xem KEY của bạn\n\n"
            "⚡ <b>TẠO CODE</b>\n"
            "• <code>/generate &lt;loại&gt;</code> - Tạo code\n"
            "• Ví dụ: <code>/generate m88</code>\n\n"
            "📊 <b>THÔNG TIN</b>\n"
            "• <code>/stats</code> - Thống kê hệ thống\n"
            "• <code>/help</code> - Hiển thị hướng dẫn\n\n"
            "🎯 <b>CÁC LOẠI TRAFFIC ĐƯỢC HỖ TRỢ:</b>\n"
            "┌─────────────────────────────────┐\n"
            "│ <b>API MA:</b> m88, fb88, 188bet, w88,   │\n"
            "│ v9bet, vn88, bk8, w88xlm        │\n"
            "│                                 │\n"
            "│ <b>API MD:</b> 88betag, w88abc, v9betlg, │\n"
            "│ bk8xo, vn88ie                   │\n"
            "└─────────────────────────────────┘\n\n"
            "⚠️ <b>LƯU Ý:</b>\n"
            "• Mỗi KEY có thời hạn 24 giờ\n"
            "• Mỗi user chỉ có 1 KEY active\n"
            "• Cooldown tạo KEY: 1 giờ\n"
            "• Cần KEY để tạo code\n\n"
            "🆘 <b>Hỗ trợ:</b> @YeuMoneySupport"
        )
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔑 Tạo KEY ngay", callback_data="create_key"),
                InlineKeyboardButton("⚡ Tạo Code", callback_data="generate_menu")
            ]
        ])
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
    
    async def key_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /key command"""
        user = self.get_or_create_user(update.effective_user)
        
        if user.is_banned:
            await update.message.reply_text("🚫 Bạn đã bị cấm sử dụng bot!")
            return
        
        # Check cooldown
        if not self.check_cooldown(user.user_id):
            remaining = self.cooldown_minutes * 60 - (time.time() - self.user_cooldowns[user.user_id])
            await update.message.reply_text(
                f"⏰ Bạn cần chờ {int(remaining/60)} phút {int(remaining%60)} giây để tạo KEY mới!"
            )
            return
        
        await self.send_typing(update)
        
        # Check existing keys
        existing_keys = db.get_user_keys(user.user_id)
        active_keys = [k for k in existing_keys if k.is_valid()]
        
        if len(active_keys) >= self.max_keys_per_user:
            await update.message.reply_text(
                f"🔑 Bạn đã có {len(active_keys)} KEY active!\n"
                f"Sử dụng /mykeys để xem chi tiết."
            )
            return
        
        # Create new key
        new_key = generate_key()
        expires_at = datetime.now() + timedelta(hours=self.key_lifetime_hours)
        
        api_key = APIKey(
            key=new_key,
            user_id=user.user_id,
            expires_at=expires_at,
            metadata={
                'created_by': 'user_command',
                'username': user.username,
                'created_via': 'telegram'
            }
        )
        
        if db.create_api_key(api_key):
            self.set_cooldown(user.user_id)
            
            success_text = (
                f"🎉 <b>KEY được tạo thành công!</b>\n\n"
                f"🔑 <code>{new_key}</code>\n\n"
                f"⏰ <b>Thời hạn:</b> {self.key_lifetime_hours} giờ\n"
                f"📅 <b>Hết hạn:</b> {format_datetime(expires_at)}\n"
                f"🔄 <b>Cooldown:</b> {self.cooldown_minutes} phút\n\n"
                f"💡 <i>Lưu KEY này để sử dụng tạo code!</i>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⚡ Tạo Code ngay", callback_data=f"generate_{new_key}")]
            ])
            
            await update.message.reply_text(
                success_text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
        else:
            await update.message.reply_text("❌ Lỗi khi tạo KEY. Vui lòng thử lại!")
    
    async def mykeys_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mykeys command"""
        user = self.get_or_create_user(update.effective_user)
        
        if user.is_banned:
            await update.message.reply_text("🚫 Bạn đã bị cấm sử dụng bot!")
            return
        
        await self.send_typing(update)
        
        keys = db.get_user_keys(user.user_id)
        
        if not keys:
            await update.message.reply_text(
                "🔑 Bạn chưa có KEY nào!\n\n"
                "Sử dụng /key để tạo KEY mới."
            )
            return
        
        response = "🔑 <b>DANH SÁCH KEY CỦA BẠN</b>\n"
        response += "═══════════════════════════════\n\n"
        
        for i, key in enumerate(keys, 1):
            status_emoji = "✅" if key.is_valid() else "❌"
            status_text = key.status.value.upper()
            
            if key.expires_at:
                if datetime.now() > key.expires_at:
                    status_emoji = "⏰"
                    status_text = "EXPIRED"
            
            response += f"{i}. {status_emoji} <b>KEY #{i}</b>\n"
            response += f"   🔑 <code>{key.key}</code>\n"
            response += f"   📊 Status: {status_text}\n"
            response += f"   📅 Tạo: {format_datetime(key.created_at)}\n"
            
            if key.expires_at:
                response += f"   ⏰ Hết hạn: {format_datetime(key.expires_at)}\n"
            
            response += f"   🔢 Đã dùng: {key.usage_count} lần\n\n"
        
        # Add action buttons
        buttons = []
        active_key = next((k for k in keys if k.is_valid()), None)
        if active_key:
            buttons.append([
                InlineKeyboardButton("⚡ Tạo Code", callback_data=f"generate_{active_key.key}")
            ])
        
        buttons.append([
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_keys"),
            InlineKeyboardButton("🔑 Tạo KEY mới", callback_data="create_key")
        ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        await update.message.reply_text(
            response,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
    
    async def generate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /generate command"""
        user = self.get_or_create_user(update.effective_user)
        
        if user.is_banned:
            await update.message.reply_text("🚫 Bạn đã bị cấm sử dụng bot!")
            return
        
        # Check if user has valid key
        keys = db.get_user_keys(user.user_id)
        valid_key = next((k for k in keys if k.is_valid()), None)
        
        if not valid_key:
            await update.message.reply_text(
                "🔑 Bạn cần có KEY để sử dụng tính năng này!\n\n"
                "Sử dụng /key để tạo KEY mới."
            )
            return
        
        # Get traffic type from command
        args = context.args
        if not args:
            # Show traffic types menu
            await self.show_traffic_menu(update)
            return
        
        traffic_type = args[0].lower()
        await self.generate_code_for_type(update, user, valid_key, traffic_type)
    
    async def show_traffic_menu(self, update: Update):
        """Show traffic types selection menu"""
        traffic_types = config.get_all_traffic_types()
        
        text = (
            "⚡ <b>CHỌN LOẠI TRAFFIC</b>\n"
            "═══════════════════════════\n\n"
            "📝 <b>Cách sử dụng:</b>\n"
            "<code>/generate &lt;loại&gt;</code>\n\n"
            "🎯 <b>Các loại có sẵn:</b>\n"
        )
        
        # Group traffic types
        ma_types = []
        md_types = []
        
        for traffic_type in traffic_types:
            traffic_config = config.get_traffic_config(traffic_type)
            if traffic_config:
                if traffic_config.api_type.value == "GET_MA":
                    ma_types.append(f"• <code>{traffic_type}</code> - {traffic_config.description}")
                else:
                    md_types.append(f"• <code>{traffic_type}</code> - {traffic_config.description}")
        
        text += "\n🔵 <b>API MA:</b>\n" + "\n".join(ma_types[:4]) + "\n"
        if len(ma_types) > 4:
            text += "\n".join(ma_types[4:]) + "\n"
        
        text += "\n🟢 <b>API MD:</b>\n" + "\n".join(md_types) + "\n"
        
        text += f"\n💡 <i>Ví dụ: /generate m88</i>"
        
        # Create inline keyboard with traffic types
        buttons = []
        for i in range(0, len(traffic_types), 2):
            row = []
            for j in range(2):
                if i + j < len(traffic_types):
                    traffic_type = traffic_types[i + j]
                    row.append(InlineKeyboardButton(
                        traffic_type.upper(),
                        callback_data=f"gen_{traffic_type}"
                    ))
            buttons.append(row)
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        await update.message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
    
    async def generate_code_for_type(self, update: Update, user: User, api_key: APIKey, traffic_type: str):
        """Generate code for specific traffic type"""
        traffic_config = config.get_traffic_config(traffic_type)
        
        if not traffic_config:
            available_types = ", ".join(config.get_all_traffic_types())
            await update.message.reply_text(
                f"❌ Loại traffic '{traffic_type}' không hợp lệ!\n\n"
                f"Các loại có sẵn: {available_types}"
            )
            return
        
        await self.send_typing(update)
        
        # Show processing message
        processing_msg = await update.message.reply_text(
            f"⚡ <b>Đang tạo code {traffic_config.name}...</b>\n"
            f"🔄 Vui lòng chờ trong vài giây...",
            parse_mode=ParseMode.HTML
        )
        
        # Generate code
        try:
            response = api_client.generate_code(traffic_config, user.user_id)
            
            if response.success:
                # Update key usage
                api_key.usage_count += 1
                db.update_api_key(api_key)
                
                # Update user usage
                user.usage_count += 1
                db.update_user(user)
                
                success_text = (
                    f"🎉 <b>Code được tạo thành công!</b>\n\n"
                    f"🎯 <b>Loại:</b> {traffic_config.name}\n"
                    f"💰 <b>Code:</b> <code>{response.code}</code>\n"
                    f"⏱️ <b>Thời gian xử lý:</b> {response.processing_time:.2f}s\n"
                    f"🔑 <b>KEY đã dùng:</b> {api_key.usage_count} lần\n\n"
                    f"💡 <i>Copy code và sử dụng ngay!</i>"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🔄 Tạo lại", callback_data=f"gen_{traffic_type}"),
                        InlineKeyboardButton("📋 Menu Traffic", callback_data="traffic_menu")
                    ]
                ])
                
                await processing_msg.edit_text(
                    success_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard
                )
            else:
                error_text = (
                    f"❌ <b>Không thể tạo code!</b>\n\n"
                    f"🎯 <b>Loại:</b> {traffic_config.name}\n"
                    f"⚠️ <b>Lỗi:</b> {response.error_message}\n"
                    f"⏱️ <b>Thời gian:</b> {response.processing_time:.2f}s\n\n"
                    f"💡 <i>Vui lòng thử lại sau ít phút!</i>"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🔄 Thử lại", callback_data=f"gen_{traffic_type}"),
                        InlineKeyboardButton("📋 Chọn khác", callback_data="traffic_menu")
                    ]
                ])
                
                await processing_msg.edit_text(
                    error_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard
                )
                
        except Exception as e:
            logging.error(f"Error generating code: {e}")
            await processing_msg.edit_text(
                f"💥 <b>Lỗi hệ thống!</b>\n\n"
                f"⚠️ <b>Chi tiết:</b> {str(e)}\n\n"
                f"🆘 Vui lòng liên hệ admin nếu lỗi tiếp tục xảy ra!",
                parse_mode=ParseMode.HTML
            )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        user = self.get_or_create_user(update.effective_user)
        
        await self.send_typing(update)
        
        # Get system stats
        stats = db.get_system_stats()
        
        # Get user-specific stats
        user_keys = db.get_user_keys(user.user_id)
        user_requests = db.get_user_requests(user.user_id, 10)
        
        response = (
            f"📊 <b>THỐNG KÊ HỆ THỐNG</b>\n"
            f"═══════════════════════════════\n\n"
            f"👥 <b>Tổng người dùng:</b> {stats.total_users:,}\n"
            f"🔑 <b>KEY đang hoạt động:</b> {stats.active_keys:,}\n"
            f"📈 <b>Tổng requests:</b> {stats.total_requests:,}\n"
            f"✅ <b>Thành công:</b> {stats.successful_requests:,}\n"
            f"❌ <b>Thất bại:</b> {stats.failed_requests:,}\n"
            f"📊 <b>Tỷ lệ thành công:</b> {stats.success_rate():.1f}%\n\n"
            f"👤 <b>THỐNG KÊ CÁ NHÂN</b>\n"
            f"═══════════════════════════════\n"
            f"🔑 <b>KEY của bạn:</b> {len(user_keys)}\n"
            f"⚡ <b>Lần sử dụng:</b> {user.usage_count}\n"
            f"📅 <b>Tham gia:</b> {format_datetime(user.created_at)}\n"
            f"🕐 <b>Hoạt động cuối:</b> {format_datetime(user.last_seen)}\n\n"
            f"🔄 <b>Cập nhật:</b> {format_datetime(stats.last_updated)}"
        )
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats"),
                InlineKeyboardButton("📋 My Keys", callback_data="my_keys")
            ]
        ])
        
        await update.message.reply_text(
            response,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
    
    # Admin commands
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("🚫 Bạn không có quyền admin!")
            return
        
        admin_text = (
            "👑 <b>BẢNG ĐIỀU KHIỂN ADMIN</b>\n"
            "═══════════════════════════════\n\n"
            "🔑 <b>QUẢN LÝ KEY</b>\n"
            "• <code>/taokey &lt;số_ngày&gt;</code> - Tạo KEY VIP\n"
            "• <code>/listkey</code> - Danh sách KEY\n"
            "• <code>/deletekey &lt;key&gt;</code> - Xóa KEY\n"
            "• <code>/keyinfo &lt;key&gt;</code> - Chi tiết KEY\n\n"
            "👥 <b>QUẢN LÝ USER</b>\n"
            "• <code>/ban &lt;user_id&gt; &lt;phút&gt;</code> - Ban user\n"
            "• <code>/unban &lt;user_id&gt;</code> - Gỡ ban\n"
            "• <code>/broadcast &lt;tin nhắn&gt;</code> - Gửi thông báo\n\n"
            "👑 <b>MASTER ADMIN</b> (Chỉ Master)\n"
            "• <code>/addadmin &lt;user_id&gt;</code> - Thêm admin\n"
            "• <code>/deladmin &lt;user_id&gt;</code> - Xóa admin\n"
            "• <code>/listadmin</code> - Danh sách admin\n\n"
            "📊 <b>Sử dụng /stats để xem thống kê chi tiết</b>"
        )
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔑 Tạo KEY VIP", callback_data="admin_create_key"),
                InlineKeyboardButton("📋 List KEYs", callback_data="admin_list_keys")
            ],
            [
                InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
                InlineKeyboardButton("👥 Users", callback_data="admin_users")
            ]
        ])
        
        await update.message.reply_text(
            admin_text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
    
    async def create_key_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /taokey command (admin only)"""
        if not self.is_admin(update.effective_user.id):
            await update.message.reply_text("🚫 Bạn không có quyền admin!")
            return
        
        args = context.args
        if not args:
            await update.message.reply_text(
                "📝 <b>Cách sử dụng:</b>\n"
                "<code>/taokey &lt;số_ngày&gt;</code>\n\n"
                "💡 <b>Ví dụ:</b>\n"
                "<code>/taokey 7</code> - Tạo KEY 7 ngày",
                parse_mode=ParseMode.HTML
            )
            return
        
        try:
            days = int(args[0])
            if days <= 0 or days > 365:
                await update.message.reply_text("❌ Số ngày phải từ 1 đến 365!")
                return
        except ValueError:
            await update.message.reply_text("❌ Số ngày không hợp lệ!")
            return
        
        await self.send_typing(update)
        
        # Create VIP key
        new_key = f"VIP{datetime.now().strftime('%Y%m%d')}-{generate_key(8)}"
        expires_at = datetime.now() + timedelta(days=days)
        
        api_key = APIKey(
            key=new_key,
            user_id=0,  # VIP key not bound to user
            expires_at=expires_at,
            metadata={
                'created_by': 'admin',
                'admin_id': update.effective_user.id,
                'is_vip': True,
                'days': days
            }
        )
        
        if db.create_api_key(api_key):
            success_text = (
                f"🎉 <b>KEY VIP được tạo thành công!</b>\n\n"
                f"🔑 <code>{new_key}</code>\n\n"
                f"⏰ <b>Thời hạn:</b> {days} ngày\n"
                f"📅 <b>Hết hạn:</b> {format_datetime(expires_at)}\n"
                f"👑 <b>Loại:</b> VIP Key\n"
                f"🆔 <b>Admin tạo:</b> {update.effective_user.id}\n\n"
                f"💡 <i>KEY này có thể được sử dụng bởi bất kỳ ai!</i>"
            )
            
            await update.message.reply_text(
                success_text,
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text("❌ Lỗi khi tạo KEY VIP!")
    
    # Callback query handler
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user = self.get_or_create_user(query.from_user)
        
        if data == "create_key":
            # Simulate /key command
            await self.key_command(update, context)
        
        elif data == "generate_code" or data == "traffic_menu":
            await self.show_traffic_menu(update)
        
        elif data.startswith("gen_"):
            traffic_type = data[4:]
            keys = db.get_user_keys(user.user_id)
            valid_key = next((k for k in keys if k.is_valid()), None)
            
            if not valid_key:
                await query.edit_message_text(
                    "🔑 Bạn cần có KEY để sử dụng tính năng này!\n\n"
                    "Sử dụng /key để tạo KEY mới."
                )
                return
            
            await self.generate_code_for_type(update, user, valid_key, traffic_type)
        
        elif data == "my_keys":
            await self.mykeys_command(update, context)
        
        elif data == "stats":
            await self.stats_command(update, context)
        
        elif data == "help":
            await self.help_command(update, context)
        
        elif data == "refresh_keys":
            await self.mykeys_command(update, context)
        
        elif data == "refresh_stats":
            await self.stats_command(update, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        user = self.get_or_create_user(update.effective_user)
        
        if user.is_banned:
            return
        
        message_text = update.message.text.lower()
        
        # Auto-responses for common queries
        if any(word in message_text for word in ['help', 'hướng dẫn', 'giúp']):
            await self.help_command(update, context)
        elif any(word in message_text for word in ['key', 'tạo key']):
            await update.message.reply_text(
                "🔑 Để tạo KEY, hãy sử dụng lệnh /key\n"
                "💡 Hoặc nhấn nút bên dưới:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔑 Tạo KEY", callback_data="create_key")]
                ])
            )
        elif any(word in message_text for word in ['code', 'tạo code', 'generate']):
            await update.message.reply_text(
                "⚡ Để tạo code, hãy sử dụng lệnh /generate\n"
                "💡 Hoặc nhấn nút bên dưới:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⚡ Tạo Code", callback_data="generate_code")]
                ])
            )
        else:
            # Generic response
            await update.message.reply_text(
                "👋 Xin chào! Tôi là YeuMoney Bot.\n\n"
                "Sử dụng /help để xem hướng dẫn hoặc /start để bắt đầu!"
            )

# Global bot instance
telegram_bot = TelegramBot()
