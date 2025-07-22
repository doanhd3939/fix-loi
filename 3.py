import os
import re
import time
import json
import threading
import requests
import asyncio
import random
import string
import logging

from flask import Flask, request, jsonify, render_template_string
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ========== CẤU HÌNH ==========
LINK4M_API_TOKEN = "687c5ee5378e1071b4481530"
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8029254946:AAE8Upy5LoYIYsmcm8Y117Esm_-_MF0-ChA')

DEFAULT_KEY_LIFETIME = 86400  # 1 ngày
MASTER_ADMIN_ID = 7509896689

BYPASS_TYPES = [
    "m88", "fb88", "188bet", "w88", "v9bet", "bk8",
    "88betag", "w88abc", "v9betlg", "bk8xo", "vn88ie", "w88xlm"
]

# ========== CẤU HÌNH LOGGING ==========
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ========== CÁC FILE LƯU TRỮ ==========
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

VALID_KEYS_FILE = os.path.join(DATA_DIR, "valid_keys.json")
USER_KEYS_FILE = os.path.join(DATA_DIR, "user_keys.json")
KEY_DEVICES_FILE = os.path.join(DATA_DIR, "key_devices.json")  # Lưu thông tin thiết bị đang sử dụng key
ADMINS_FILE = os.path.join(DATA_DIR, "admins.json")
BAN_LIST_FILE = os.path.join(DATA_DIR, "ban_list.json")

# ========== BIẾN TOÀN CỤC ==========
VALID_KEYS = {}    # key -> (timestamp tạo, thời gian sống giây)
USER_KEYS = {}     # user_id -> key đã xác nhận
KEY_DEVICES = {}   # key -> user_id đang sử dụng key này
KEY_COOLDOWN = {}  # user_id -> last_time dùng lệnh /key (giây)
ADMINS = set([MASTER_ADMIN_ID])
ADMINS_LOCK = threading.Lock()
SPAM_COUNTER = {}
BAN_LIST = {}
USER_LOCKS = threading.Lock()
DATA_LOCK = threading.Lock()  # Lock để đồng bộ khi lưu/đọc dữ liệu

# ========== FLASK APP ==========
app = Flask(__name__)

# ========== HƯỚNG DẪN ADMIN ==========
ADMIN_GUIDE = (
    "<b>👑 HƯỚNG DẪN QUẢN TRỊ VIÊN</b>\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "<b>CÁC LỆNH QUẢN TRỊ:</b>\n"
    "<code>/ban &lt;user_id&gt; &lt;phút&gt;</code> – Ban user X phút\n"
    "<code>/unban &lt;user_id&gt;</code> – Gỡ ban user\n"
    "<code>/addadmin &lt;user_id&gt;</code> – Thêm admin mới (CHỈ MASTER ADMIN)\n"
    "<code>/deladmin &lt;user_id&gt;</code> – Xoá quyền admin (CHỈ MASTER ADMIN)\n"
    "<code>/taokey &lt;số ngày&gt;</code> – Admin tạo KEY với hạn sử dụng\n"
    "<code>/listkey</code> – Xem danh sách user đang sử dụng KEY\n"
    "<code>/checkkey</code> – Kiểm tra thời gian còn lại của KEY\n"
    "<code>/savedata</code> - Lưu dữ liệu thủ công\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "<b>LƯU Ý:</b>\n"
    "- Mỗi KEY chỉ được sử dụng bởi 1 thiết bị/người dùng duy nhất.\n"
    "- KEY có thể sử dụng nhiều lần trong thời gian hiệu lực.\n"
    "- Khi còn KEY hợp lệ, không thể nhập KEY mới.\n"
    "- Ban thủ công sẽ ghi đè ban tự động.\n"
    "- /unban sẽ gỡ mọi loại ban.\n"
    "<b>Ví dụ:</b>\n"
    "<code>/ban 123456789 10</code> – Ban user 123456789 trong 10 phút\n"
    "<code>/unban 123456789</code> – Gỡ ban user\n"
    "<code>/taokey 3</code> – Tạo key sống 3 ngày, chỉ 1 thiết bị sử dụng\n"
)

# ========== CÁC HÀM LƯU TRỮ ==========
def save_valid_keys():
    with DATA_LOCK:
        data = {}
        for key, (timestamp, lifetime) in VALID_KEYS.items():
            data[key] = [timestamp, lifetime]
        with open(VALID_KEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f)

def load_valid_keys():
    global VALID_KEYS
    with DATA_LOCK:
        if os.path.exists(VALID_KEYS_FILE):
            try:
                with open(VALID_KEYS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, (timestamp, lifetime) in data.items():
                        VALID_KEYS[key] = (timestamp, lifetime)
            except Exception as e:
                logger.error(f"Lỗi khi đọc file VALID_KEYS_FILE: {e}")

def save_user_keys():
    with DATA_LOCK:
        # Chuyển đổi user_id từ string sang int khi load
        data = {str(user_id): key for user_id, key in USER_KEYS.items()}
        with open(USER_KEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f)

def load_user_keys():
    global USER_KEYS
    with DATA_LOCK:
        if os.path.exists(USER_KEYS_FILE):
            try:
                with open(USER_KEYS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Chuyển đổi user_id từ string sang int khi load
                    USER_KEYS = {int(user_id): key for user_id, key in data.items()}
            except Exception as e:
                logger.error(f"Lỗi khi đọc file USER_KEYS_FILE: {e}")

def save_key_devices():
    with DATA_LOCK:
        # Chuyển đổi user_id sang string để lưu vào JSON
        data = {key: str(user_id) for key, user_id in KEY_DEVICES.items()}
        with open(KEY_DEVICES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f)

def load_key_devices():
    global KEY_DEVICES
    with DATA_LOCK:
        if os.path.exists(KEY_DEVICES_FILE):
            try:
                with open(KEY_DEVICES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Chuyển đổi user_id từ string sang int khi load
                    KEY_DEVICES = {key: int(user_id) for key, user_id in data.items()}
            except Exception as e:
                logger.error(f"Lỗi khi đọc file KEY_DEVICES_FILE: {e}")

def save_admins():
    with DATA_LOCK:
        with ADMINS_LOCK:
            with open(ADMINS_FILE, 'w', encoding='utf-8') as f:
                # Chuyển set thành list để lưu vào JSON
                json.dump(list(ADMINS), f)

def load_admins():
    global ADMINS
    with DATA_LOCK:
        if os.path.exists(ADMINS_FILE):
            try:
                with open(ADMINS_FILE, 'r', encoding='utf-8') as f:
                    # Đảm bảo MASTER_ADMIN_ID luôn có trong danh sách
                    admin_list = json.load(f)
                    with ADMINS_LOCK:
                        ADMINS = set(admin_list)
                        ADMINS.add(MASTER_ADMIN_ID)
            except Exception as e:
                logger.error(f"Lỗi khi đọc file ADMINS_FILE: {e}")
                with ADMINS_LOCK:
                    ADMINS = set([MASTER_ADMIN_ID])

def save_ban_list():
    with DATA_LOCK:
        data = {}
        for user_id, ban_info in BAN_LIST.items():
            # Chuyển đổi thông tin ban để có thể lưu vào JSON
            data[str(user_id)] = {
                'until': ban_info['until'],
                'manual': ban_info['manual']
            }
        with open(BAN_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f)

def load_ban_list():
    global BAN_LIST
    with DATA_LOCK:
        if os.path.exists(BAN_LIST_FILE):
            try:
                with open(BAN_LIST_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Lọc ra những ban đã hết hạn
                    now = time.time()
                    for user_id_str, ban_info in data.items():
                        if ban_info['until'] > now:
                            BAN_LIST[int(user_id_str)] = ban_info
            except Exception as e:
                logger.error(f"Lỗi khi đọc file BAN_LIST_FILE: {e}")

def save_all_data():
    save_valid_keys()
    save_user_keys()
    save_key_devices()
    save_admins()
    save_ban_list()
    logger.info(f"Đã lưu dữ liệu thành công!")

def load_all_data():
    load_valid_keys()
    load_user_keys()
    load_key_devices()
    load_admins()
    load_ban_list()
    logger.info(f"Đã tải dữ liệu thành công!")

# Luồng tự động lưu dữ liệu định kỳ
def auto_save_data_loop():
    while True:
        time.sleep(300)  # Lưu dữ liệu 5 phút một lần
        try:
            save_all_data()
        except Exception as e:
            logger.error(f"Lỗi khi tự động lưu dữ liệu: {e}")

# ========== CÁC HÀM HỖ TRỢ ==========
def admin_notify(msg: str) -> str:
    return (
        "<b>👑 QUẢN TRỊ VIÊN</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{msg}\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )

def is_admin(user_id):
    with ADMINS_LOCK:
        return user_id in ADMINS

def is_master_admin(user_id):
    return user_id == MASTER_ADMIN_ID

def tao_key(songay=1):
    key = "VIP2025-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    lifetime = int(songay) * 86400
    VALID_KEYS[key] = (time.time(), lifetime)
    save_valid_keys()
    return key, lifetime

def check_key(key):
    data = VALID_KEYS.get(key)
    if not data:
        return False
    
    t, living = data
    
    # Kiểm tra thời gian
    if time.time() - t > living:
        VALID_KEYS.pop(key, None)
        KEY_DEVICES.pop(key, None)
        for uid, k in list(USER_KEYS.items()):
            if k == key:
                USER_KEYS.pop(uid, None)
        save_valid_keys()
        save_key_devices()
        save_user_keys()
        return False
    
    return True

def bind_key_to_device(key, user_id):
    """Gắn key với một thiết bị/user_id cụ thể"""
    KEY_DEVICES[key] = user_id
    save_key_devices()

def can_use_key(key, user_id):
    """Kiểm tra xem user_id có quyền sử dụng key này không"""
    # Nếu key chưa được gắn với thiết bị nào
    if key not in KEY_DEVICES:
        bind_key_to_device(key, user_id)
        return True
    
    # Nếu key đã được gắn với thiết bị này
    return KEY_DEVICES[key] == user_id

def get_key_info(key):
    data = VALID_KEYS.get(key)
    if not data:
        return None
    t, living = data
    remaining_time = max(0, t + living - time.time())
    days = int(remaining_time // 86400)
    hours = int((remaining_time % 86400) // 3600)
    minutes = int((remaining_time % 3600) // 60)
    
    bound_device = KEY_DEVICES.get(key, None)
    
    return {
        "time_remaining": f"{days} ngày, {hours} giờ, {minutes} phút",
        "bound_device": bound_device,
        "expired": remaining_time <= 0
    }

def check_user_key(user_id):
    key = USER_KEYS.get(user_id)
    return key if key and check_key(key) else None

def xacnhan_key(user_id, key):
    # Kiểm tra xem user đã có key hợp lệ chưa
    current_key = USER_KEYS.get(user_id)
    if current_key and check_key(current_key):
        return "already_have_key"
    
    if check_key(key):
        # Kiểm tra xem key đã được gắn với thiết bị khác chưa
        if key in KEY_DEVICES and KEY_DEVICES[key] != user_id:
            return "key_bound_to_other_device"
        
        # Nếu key chưa được gắn với thiết bị nào hoặc đã gắn với thiết bị này
        USER_KEYS[user_id] = key
        bind_key_to_device(key, user_id)
        save_user_keys()
        save_key_devices()
        return "success"
    return "invalid_key"

def upload(key):
    nd = f"🔑 KEY CỦA BẠN:\n{key}\n➡️ Dán vào TOOL để sử dụng!"
    try:
        data = {
            'content': nd,
            'syntax': 'text',
            'expiry_days': 1
        }
        res = requests.post("https://dpaste.org/api/", data=data, timeout=5)
        if res.status_code == 200:
            return res.text.strip().strip('"')
    except Exception as e:
        logger.error(f"❌ Lỗi upload: {e}")
    return None

def rutgon(url):
    """Hàm rút gọn URL sử dụng API Link4m"""
    try:
        # Log thông tin gửi đi để debug
        logger.info(f"Gửi yêu cầu rút gọn URL: {url}")
        encoded = requests.utils.quote(url, safe='')
        api_url = f"https://link4m.co/api-shorten/v2?api={LINK4M_API_TOKEN}&url={encoded}"
        logger.info(f"API URL: {api_url}")
        
        res = requests.get(api_url, timeout=10)
        logger.info(f"Phản hồi từ Link4m: Status={res.status_code}, Content={res.text}")
        
        if res.status_code != 200:
            logger.error(f"Link4m API trả về status code không thành công: {res.status_code}")
            return url  # Trả về URL gốc nếu có lỗi
        
        try:
            js = res.json()
            if js.get("status") == "success":
                return js["shortenedUrl"]
            else:
                logger.error(f"Link4m API trả về lỗi: {js.get('message', 'Unknown error')}")
        except Exception as e:
            logger.error(f"Lỗi khi parse JSON từ Link4m: {e}")
        
        # Thử các dịch vụ rút gọn URL thay thế
        return rutgon_tinyurl(url)
    except Exception as e:
        logger.error(f"❌ Lỗi rút gọn Link4m: {e}")
        # Thử sử dụng dịch vụ rút gọn URL thay thế
        return rutgon_tinyurl(url)

def rutgon_tinyurl(url):
    """Hàm rút gọn URL thay thế sử dụng TinyURL API"""
    try:
        api_url = f"https://tinyurl.com/api-create.php?url={requests.utils.quote(url, safe='')}"
        logger.info(f"Thử TinyURL API: {api_url}")
        res = requests.get(api_url, timeout=10)
        if res.status_code == 200:
            return res.text
        else:
            logger.error(f"TinyURL API trả về status code không thành công: {res.status_code}")
    except Exception as e:
        logger.error(f"❌ Lỗi rút gọn TinyURL: {e}")
    
    # Nếu tất cả đều thất bại, trả về URL gốc
    return url

def auto_unban_loop():
    while True:
        now = time.time()
        to_del = []
        for user_id, ban in list(BAN_LIST.items()):
            if ban['until'] <= now:
                to_del.append(user_id)
        
        if to_del:
            for user_id in to_del:
                del BAN_LIST[user_id]
            save_ban_list()
        
        time.sleep(5)

def pre_check(user_id):
    if is_admin(user_id):
        return {"status": "ok"}
    ban = BAN_LIST.get(user_id)
    if ban and ban['until'] > time.time():
        return {"status": "banned", "msg": "Bạn đang bị cấm."}
    now = time.time()
    cnts = SPAM_COUNTER.setdefault(user_id, [])
    cnts = [t for t in cnts if now - t < 60]
    cnts.append(now)
    SPAM_COUNTER[user_id] = cnts
    if len(cnts) > 3:
        BAN_LIST[user_id] = {'until': now + 300, 'manual': False}
        save_ban_list()
        return {"status": "spam", "msg": "Bạn đã bị tự động ban 5 phút do spam."}
    return {"status": "ok"}

async def send_admin_notify_key(context, message):
    try:
        await context.bot.send_message(
            chat_id=MASTER_ADMIN_ID,
            text=message,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Lỗi gửi thông báo admin: {e}")

def handle_admin_command(current_user_id, cmd, args):
    try:
        # Chỉ MASTER ADMIN được phép add/del admin
        if cmd in ["/addadmin", "/deladmin"]:
            if not is_master_admin(current_user_id):
                return {"status": "error", "msg": admin_notify("❌ <b>Bạn không có quyền thực hiện lệnh này! Chỉ master admin được phép.</b>")}
        if not is_admin(current_user_id):
            return {"status": "error", "msg": admin_notify("❌ <b>Bạn không có quyền quản trị viên!</b>")}
        
        if cmd == "/ban":
            if len(args) < 2:
                return {"status": "error", "msg": admin_notify("❌ <b>Cú pháp đúng:</b> <code>/ban &lt;user_id&gt; &lt;số_phút&gt;</code>")}
            target = int(args[0])
            mins = int(args[1])
            now = time.time()
            was_banned = BAN_LIST.get(target)
            BAN_LIST[target] = {'until': now + mins * 60, 'manual': True}
            save_ban_list()
            if was_banned:
                return {"status": "ok", "msg": admin_notify(f"🔁 <b>Đã cập nhật lại thời gian ban <code>{target}</code> thành <b>{mins} phút</b>.</b>")}
            else:
                return {"status": "ok", "msg": admin_notify(f"🔒 <b>Đã ban <code>{target}</code> trong <b>{mins} phút</b>.</b>")}
        
        elif cmd == "/unban":
            if len(args) < 1:
                return {"status": "error", "msg": admin_notify("❌ <b>Cú pháp đúng:</b> <code>/unban &lt;user_id&gt;</code>")}
            target = int(args[0])
            if target in BAN_LIST:
                del BAN_LIST[target]
                save_ban_list()
                return {"status": "ok", "msg": admin_notify(f"🔓 <b>Đã gỡ ban <code>{target}</code>.</b>")}
            return {"status": "ok", "msg": admin_notify(f"ℹ️ <b>User <code>{target}</code> không bị cấm.</b>")}
        
        elif cmd == "/addadmin":
            if len(args) < 1:
                return {"status": "error", "msg": admin_notify("❌ <b>Cú pháp đúng:</b> <code>/addadmin &lt;user_id&gt;</code>")}
            target = int(args[0])
            with ADMINS_LOCK:
                ADMINS.add(target)
            save_admins()
            return {"status": "ok", "msg": admin_notify(f"✨ <b>Đã thêm admin <code>{target}</code>.</b>")}
        
        elif cmd == "/deladmin":
            if len(args) < 1:
                return {"status": "error", "msg": admin_notify("❌ <b>Cú pháp đúng:</b> <code>/deladmin &lt;user_id&gt;</code>")}
            target = int(args[0])
            with ADMINS_LOCK:
                if target == current_user_id and len(ADMINS) == 1:
                    return {"status": "error", "msg": admin_notify("⚠️ <b>Không thể xoá admin cuối cùng!</b>")}
                ADMINS.discard(target)
            save_admins()
            return {"status": "ok", "msg": admin_notify(f"🗑️ <b>Đã xoá quyền admin <code>{target}</code>.</b>")}
        
        elif cmd == "/savedata":
            save_all_data()
            return {"status": "ok", "msg": admin_notify("💾 <b>Đã lưu dữ liệu thành công!</b>")}
        
        elif cmd == "/adminguide":
            return {"status": "ok", "msg": ADMIN_GUIDE}
        
        else:
            return {"status": "error", "msg": admin_notify("❌ <b>Lệnh quản trị không hợp lệ!</b>")}
    
    except Exception as e:
        return {"status": "error", "msg": admin_notify(f"Lỗi hệ thống: {e}")}

# ========== CÁC LỆNH BOT ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>🤖 BOT LẤY MÃ AUTO - ĐẲNG CẤP VIP</b>\n"
        "<i>Hỗ trợ lấy mã tự động, xác nhận KEY, quản trị, chống spam, bảo mật cao!</i>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<b>🔑 LỆNH NGƯỜI DÙNG:</b>\n"
        "▪️ <b>Tạo key:</b> <code>/key</code>\n"
        "▪️ <b>Xác nhận key:</b> <code>/xacnhankey &lt;KEY&gt;</code>\n"
        "▪️ <b>Kiểm tra key:</b> <code>/checkkey</code>\n"
        "▪️ <b>Lấy mã:</b> <code>/ym &lt;loại&gt;</code>\n"
        "▪️ <b>Loại mã:</b> <code>" + ", ".join(BYPASS_TYPES) + "</code>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<b>👑 LỆNH ADMIN:</b>\n"
        "▪️ <code>/ban &lt;user_id&gt; &lt;phút&gt;</code> - Ban user\n"
        "▪️ <code>/unban &lt;user_id&gt;</code> - Gỡ ban\n"
        "▪️ <code>/addadmin &lt;user_id&gt;</code> - Thêm admin (chỉ master)\n"
        "▪️ <code>/deladmin &lt;user_id&gt;</code> - Xóa admin (chỉ master)\n"
        "▪️ <code>/taokey &lt;số ngày&gt;</code> - Tạo key (chỉ 1 thiết bị dùng)\n"
        "▪️ <code>/listkey</code> - Danh sách user dùng key\n"
        "▪️ <code>/savedata</code> - Lưu dữ liệu thủ công\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<b>⚠️ LƯU Ý:</b> Mỗi KEY chỉ được <b>một thiết bị</b> sử dụng nhưng có thể dùng nhiều lần trong thời gian hiệu lực!"
    )
    await update.message.reply_html(text)

async def key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    check = pre_check(user_id)
    if check["status"] != "ok":
        await update.message.reply_html(f"❌ <b>Lỗi:</b> {check.get('msg', '')}")
        return

    if not is_admin(user_id):
        now = time.time()
        LAST = KEY_COOLDOWN.get(user_id, 0)
        WAIT = 300 - (now - LAST)
        if WAIT > 0:
            phut = int(WAIT // 60)
            giay = int(WAIT % 60)
            await update.message.reply_html(
                f"⏳ <b>Bạn vừa tạo key, vui lòng đợi <i>{phut} phút {giay} giây</i> nữa!</b>"
            )
            return
        KEY_COOLDOWN[user_id] = now

    processing_msg = await update.message.reply_html("⏳ <i>Đang xử lý tạo KEY...</i>")
    loop = asyncio.get_running_loop()
    key, lifetime = await loop.run_in_executor(None, tao_key, 1)
    if is_admin(user_id):
        msg = (
            f"<b>🎁 KEY ADMIN:</b>\n"
            f"🔑 <code>{key}</code>\n"
            f"⏳ <b>Hiệu lực:</b> <code>1 ngày</code>\n"
            f"🔄 <b>Giới hạn:</b> <code>Chỉ 1 thiết bị sử dụng</code>\n"
            "➡️ Dán vào TOOL hoặc dùng lệnh <code>/xacnhankey &lt;KEY&gt;</code> để xác nhận!"
        )
        await processing_msg.edit_text(msg, parse_mode="HTML")
        notify_msg = (
            f"<b>🔔 ADMIN vừa tạo KEY:</b> <code>{key}</code>\n"
            f"Hiệu lực: 1 ngày\n"
            f"Giới hạn: Chỉ 1 thiết bị sử dụng\n"
            f"User tạo: <code>{user_id}</code>"
        )
        await send_admin_notify_key(context, notify_msg)
        return
    
    try:
        # Upload KEY lên dpaste và nhận URL
        link_raw = await loop.run_in_executor(None, upload, key)
        if not link_raw:
            await processing_msg.edit_text("❌ <b>Lỗi upload KEY. Thử lại sau!</b>", parse_mode="HTML")
            return
        
        # Log raw URL để debug
        logger.info(f"Raw URL từ dpaste.org: {link_raw}")
        
        # Rút gọn URL và log kết quả
        short = await loop.run_in_executor(None, rutgon, link_raw)
        logger.info(f"Shortened URL: {short}")
        
        # Nếu short là None hoặc rỗng, sử dụng URL gốc
        final_url = short if short else link_raw
        
        msg = (
            f"<b>🔗 LINK KÍCH HOẠT KEY:</b>\n"
            f"<code>{final_url}</code>\n"
            "➡️ Truy cập link này để lấy KEY sử dụng!\n"
            "Dán KEY vào TOOL hoặc dùng lệnh <code>/xacnhankey &lt;KEY&gt;</code> để xác nhận!\n"
            "<b>⚠️ Lưu ý:</b> KEY chỉ được <b>một thiết bị</b> sử dụng nhưng có thể dùng nhiều lần trong thời gian hiệu lực!"
        )
        await processing_msg.edit_text(msg, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Lỗi khi tạo KEY: {e}")
        await processing_msg.edit_text(
            f"❌ <b>Lỗi xảy ra khi tạo KEY:</b> {str(e)}\n"
            f"<b>KEY của bạn:</b> <code>{key}</code>\n"
            "Vui lòng sử dụng lệnh <code>/xacnhankey {key}</code> để kích hoạt.",
            parse_mode="HTML"
        )

async def taokey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_html("🚫 <b>Lệnh này chỉ dành cho admin!</b>")
        return
    
    args = update.message.text.split()
    if len(args) < 2:
        await update.message.reply_html(
            "❗️ <b>Cú pháp:</b> <code>/taokey số_ngày</code>\n"
            "<i>Ví dụ:</i> <code>/taokey 5</code> (tạo key sống 5 ngày, chỉ 1 thiết bị sử dụng)"
        )
        return
    
    try:
        songay = int(args[1])
        if songay < 1 or songay > 365:
            await update.message.reply_html("❗️ <b>Số ngày phải từ 1 đến 365!</b>")
            return
    except:
        await update.message.reply_html("❗️ <b>Số ngày không hợp lệ!</b>")
        return

    processing_msg = await update.message.reply_html("⏳ <i>Đang xử lý tạo KEY...</i>")
    loop = asyncio.get_running_loop()
    key, lifetime = await loop.run_in_executor(None, tao_key, songay)
    
    msg = (
        f"<b>🎁 KEY ADMIN TẠO:</b>\n"
        f"🔑 <code>{key}</code>\n"
        f"⏳ <b>Hiệu lực:</b> <code>{songay} ngày</code>\n"
        f"🔄 <b>Giới hạn:</b> <code>Chỉ 1 thiết bị sử dụng</code>\n"
        "➡️ Dán vào TOOL hoặc dùng lệnh <code>/xacnhankey &lt;KEY&gt;</code> để xác nhận!"
    )
    await processing_msg.edit_text(msg, parse_mode="HTML")
    
    # Gửi thông báo về MASTER_ADMIN_ID
    notify_msg = (
        f"<b>🔔 ADMIN vừa tạo KEY:</b> <code>{key}</code>\n"
        f"Hiệu lực: {songay} ngày\n"
        f"Giới hạn: Chỉ 1 thiết bị sử dụng\n"
        f"User tạo: <code>{user_id}</code>"
    )
    await send_admin_notify_key(context, notify_msg)

async def xacnhankey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = update.message.text.split()
    if len(args) < 2:
        await update.message.reply_html("❗️ <b>Cú pháp:</b> <code>/xacnhankey &lt;KEY&gt;</code>")
        return
    key = args[1]
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, xacnhan_key, user_id, key)
    
    if result == "success":
        key_info = get_key_info(key)
        await update.message.reply_html(
            "✅ <b>Đã xác nhận KEY thành công!</b>\n"
            f"⏳ <b>Thời gian còn lại:</b> <code>{key_info['time_remaining']}</code>\n"
            f"🔄 <b>Giới hạn:</b> <code>Chỉ thiết bị của bạn mới có thể sử dụng</code>\n"
            "Bạn có thể dùng lệnh <code>/ym &lt;loại&gt;</code> để lấy mã.\n"
            "<b>⚠️ Lưu ý:</b> KEY có thể sử dụng nhiều lần trong thời gian hiệu lực!"
        )
    elif result == "already_have_key":
        current_key = USER_KEYS.get(user_id)
        key_info = get_key_info(current_key)
        await update.message.reply_html(
            "⚠️ <b>Bạn đã có KEY hợp lệ!</b>\n"
            f"🔑 <b>KEY hiện tại:</b> <code>{current_key}</code>\n"
            f"⏳ <b>Thời gian còn lại:</b> <code>{key_info['time_remaining']}</code>\n"
            f"🔄 <b>Giới hạn:</b> <code>Chỉ thiết bị của bạn mới có thể sử dụng</code>\n"
            "Bạn không thể nhập KEY mới khi còn KEY hợp lệ!"
        )
    elif result == "key_bound_to_other_device":
        await update.message.reply_html(
            "❌ <b>KEY này đã được sử dụng bởi thiết bị/người dùng khác!</b>\n"
            "Mỗi KEY chỉ có thể được một thiết bị sử dụng.\n"
            "Vui lòng tạo KEY mới bằng lệnh <code>/key</code>."
        )
    else:
        await update.message.reply_html(
            "❌ <b>KEY không hợp lệ hoặc đã hết hạn.</b>\n"
            "Vui lòng thử lại hoặc tạo KEY mới bằng lệnh <code>/key</code>."
        )

async def checkkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    key = USER_KEYS.get(user_id)
    
    if not key:
        await update.message.reply_html(
            "❌ <b>Bạn chưa có KEY nào!</b>\n"
            "Sử dụng lệnh <code>/key</code> để tạo KEY mới."
        )
        return
    
    key_info = get_key_info(key)
    if not key_info or key_info["expired"]:
        await update.message.reply_html(
            "❌ <b>KEY của bạn đã hết hạn!</b>\n"
            "Sử dụng lệnh <code>/key</code> để tạo KEY mới."
        )
        return
    
    bound_status = "Thiết bị của bạn" if key_info["bound_device"] == user_id else "Chưa gắn với thiết bị nào"
    
    msg = (
        f"<b>🔍 THÔNG TIN KEY CỦA BẠN</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔑 <b>KEY:</b> <code>{key}</code>\n"
        f"⏳ <b>Thời gian còn lại:</b> <code>{key_info['time_remaining']}</code>\n"
        f"📱 <b>Đang được sử dụng bởi:</b> <code>{bound_status}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        "<b>✅ KEY có thể sử dụng để lấy mã nhiều lần!</b>"
    )
    
    await update.message.reply_html(msg)

async def ym_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text
    if message.startswith(('/ban', '/unban', '/addadmin', '/deladmin', '/adminguide', '/savedata')):
        parts = message.split()
        result = await asyncio.get_running_loop().run_in_executor(None, handle_admin_command, user_id, parts[0], parts[1:])
        await update.message.reply_html(result["msg"])
        return
    check = pre_check(user_id)
    if check["status"] != "ok":
        await update.message.reply_html(
            f"❌ <b>Lỗi:</b> {check.get('msg', '')}"
        )
        return
    args = message.split()
    if len(args) < 2 or args[1].lower() not in BYPASS_TYPES:
        await update.message.reply_html(
            "📌 <b>Hướng dẫn sử dụng:</b>\n"
            + "\n".join([f"<code>/ym {t}</code>" for t in BYPASS_TYPES])
            + "\nBạn phải xác nhận KEY trước bằng lệnh <code>/xacnhankey &lt;KEY&gt;</code>!"
        )
        return
    key_of_user = check_user_key(user_id)
    if not key_of_user:
        await update.message.reply_html("❌ Bạn phải xác nhận KEY hợp lệ trước! Dùng lệnh <code>/xacnhankey &lt;KEY&gt;</code>.\nDùng /key để lấy KEY mới nếu cần.")
        return
    
    # Kiểm tra xem user này có quyền sử dụng key không
    if not can_use_key(key_of_user, user_id):
        await update.message.reply_html(
            "❌ <b>KEY này đã được sử dụng bởi thiết bị/người dùng khác!</b>\n"
            "Mỗi KEY chỉ có thể được một thiết bị sử dụng.\n"
            "Vui lòng tạo KEY mới bằng lệnh <code>/key</code>."
        )
        return
    
    type = args[1].lower()
    
    sent = await update.message.reply_html(
        "⏳ <b>Đã nhận lệnh!</b>\n"
        "🤖 <i>Bot đang xử lý yêu cầu của bạn, vui lòng chờ <b>70 giây</b>...</i>\n"
        "<b>⏱️ Đang lấy mã, xin đừng gửi lệnh mới...</b>\n"
        "<b>Còn lại: <code>70</code> giây...</b>"
    )
    async def delay_and_reply():
        start_time = time.time()
        result = None
        def get_code():
            nonlocal result
            try:
                resp = requests.post("http://localhost:5000/bypass", json={"type": type, "user_id": user_id, "key": key_of_user, "message": f"/ym {type}"})
                data = resp.json()
                if "code" in data or "codes" in data:
                    if "codes" in data:
                        result = f'✅ <b>{type.upper()}</b> | <b style="color:#32e1b7;">Mã</b>: <code>{", ".join(data["codes"])}</code>'
                    else:
                        result = f'✅ <b>{type.upper()}</b> | <b style="color:#32e1b7;">Mã</b>: <code>{data["code"]}</code>'
                else:
                    result = f'❌ <b>Lỗi:</b> {data.get("error", "Không lấy được mã")}'
            except Exception as e:
                result = f"❌ <b>Lỗi hệ thống:</b> <code>{e}</code>"
        t = threading.Thread(target=get_code)
        t.start()
        for remain in range(65, 0, -5):
            await asyncio.sleep(5)
            try:
                await sent.edit_text(
                    "⏳ <b>Đã nhận lệnh!</b>\n"
                    "🤖 <i>Bot đang xử lý yêu cầu của bạn, vui lòng chờ <b>70 giây</b>...</i>\n"
                    "<b>⏱️ Đang lấy mã, xin đừng gửi lệnh mới...</b>\n"
                    f"<b>Còn lại: <code>{remain}</code> giây...</b>",
                    parse_mode="HTML"
                )
            except Exception:
                pass
        t.join()
        await asyncio.sleep(max(0, 70 - (time.time() - start_time)))
        
        key_info_msg = "\n<b>🟢 KEY của bạn vẫn có thể sử dụng tiếp!</b>"
        
        await sent.edit_text(
            f"<b>🎉 KẾT QUẢ LẤY MÃ</b>\n<b>─────────────────────────────</b>\n{result if result else '<b>Không lấy được kết quả</b>'}{key_info_msg}\n<b>─────────────────────────────</b>",
            parse_mode="HTML"
        )
    asyncio.create_task(delay_and_reply())

# Lệnh lưu dữ liệu thủ công
async def savedata_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_html("🚫 <b>Lệnh này chỉ dành cho admin!</b>")
        return
    
    try:
        save_all_data()
        await update.message.reply_html("💾 <b>Đã lưu tất cả dữ liệu thành công!</b>")
    except Exception as e:
        await update.message.reply_html(f"❌ <b>Lỗi khi lưu dữ liệu:</b> <code>{str(e)}</code>")

# LỆNH /listkey: DANH SÁCH USER ĐANG SỬ DỤNG KEY
async def listkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_html(
            "🚫 <b><i>Lệnh này chỉ dành cho admin!</i></b>"
        )
        return
    msg = "<b>💎 DANH SÁCH NGƯỜI DÙNG ĐANG SỬ DỤNG KEY</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    has_user = False
    for idx, (uid, key) in enumerate(USER_KEYS.items(), 1):
        if check_key(key):
            has_user = True
            key_info = get_key_info(key)
            bound_to = f"User ID: {key_info['bound_device']}" if key_info['bound_device'] else "Chưa gắn với thiết bị"
            
            msg += (
                f"🔹 <b>#{idx}</b> <b>User:</b> <code>{uid}</code>\n"
                f"  <b>KEY:</b> <code>{key}</code>\n"
                f"  <b>Thời gian còn lại:</b> {key_info['time_remaining']}\n"
                f"  📱 <b>Đang sử dụng bởi:</b> {bound_to}\n"
                "-------------------------\n"
            )
    if not has_user:
        msg += "📭 <b>Không có user nào đang sử dụng KEY hợp lệ.</b>"
    else:
        msg += "━━━━━━━━━━━━━━━━━━━━"
    await update.message.reply_html(msg)

# ========== FLASK ROUTES (API) ==========
@app.route('/bypass', methods=['POST'])
def k():
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'Không có dữ liệu'}), 400
        type = json_data.get('type')
        user_id = json_data.get('user_id')
        key = json_data.get('key') or None
        
        # Nếu không có key từ request, lấy key từ user
        if key is None and user_id is not None:
            key = USER_KEYS.get(user_id)
        
        if not type:
            return jsonify({'error': 'Thiếu trường type'}), 400
        if not key or not check_key(key):
            return jsonify({'error': 'Bạn phải xác nhận KEY hợp lệ trước khi sử dụng!'}), 403

        # Kiểm tra key có thuộc về user này không
        if not can_use_key(key, user_id):
            return jsonify({'error': 'KEY này đã được sử dụng bởi thiết bị/người dùng khác!'}), 403

        URL_MAP = {
            "m88": ("GET_MA.php", "taodeptrai", "https://bet88ec.com/cach-danh-bai-sam-loc", "https://bet88ec.com/"),
            "fb88": ("GET_MA.php", "taodeptrai", "https://fb88mg.com/ty-le-cuoc-hong-kong-la-gi", "https://fb88mg.com/"),
            "188bet": ("GET_MA.php", "taodeptrailamnhe", "https://88betag.com/cach-choi-game-bai-pok-deng", "https://88betag.com/"),
            "w88": ("GET_MA.php", "taodeptrai", "https://188.166.185.213/tim-hieu-khai-niem-3-bet-trong-poker-la-gi", "https://188.166.185.213/"),
            "v9bet": ("GET_MA.php", "taodeptrai", "https://v9betho.com/ca-cuoc-bong-ro-ao", "https://v9betho.com/"),
            "bk8": ("GET_MA.php", "taodeptrai", "https://bk8ze.com/cach-choi-bai-catte", "https://bk8ze.com/"),
            "88betag": ("GET_MD.php", "bomaylavua", "https://88betag.com/keo-chau-a-la-gi", "https://88betag.com/"),
            "w88abc": ("GET_MD.php", "bomaylavua", "https://w88abc.com/cach-choi-ca-cuoc-lien-quan-mobile", "https://w88abc.com/"),
            "v9betlg": ("GET_MD.php", "bomaylavua", "https://v9betlg.com/phuong-phap-cuoc-flat-betting", "https://v9betlg.com/"),
            "bk8xo": ("GET_MD.php", "bomaylavua", "https://bk8xo.com/lo-ba-cang-la-gi", "https://bk8xo.com/"),
            "vn88ie": ("GET_MD.php", "bomaylavua", "https://vn88ie.com/cach-nuoi-lo-khung", "https://vn88ie.com/"),
            "w88xlm": ("GET_MA.php", "taodeptrai", "https://w88xlm.com/cach-choi-bai-solitaire", "https://w88xlm.com/"),
        }
        if type not in URL_MAP:
            return jsonify({'error': 'Loại không hợp lệ'}), 400

        endpoint, codex, url, ref = URL_MAP[type]
        post_url = f"https://traffic-user.net/{endpoint}?codexn{'' if endpoint=='GET_MA.php' else 'd'}={codex}&url={url}&loai_traffic={ref}&clk=1000"
        response = requests.post(post_url, timeout=20)
        html = response.text

        if endpoint == "GET_MA.php":
            match = re.search(r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>', html)
        else:
            match = re.search(r'<span id="layma_me_tfudirect"[^>]*>\s*(\d+)\s*</span>', html)
        if match:
            code = match.group(1)
            return jsonify({'code': code}), 200
        else:
            return jsonify({'error': 'Không tìm thấy mã'}), 400
    except Exception as e:
        logger.error(f"Lỗi bypass: {e}")
        return jsonify({'error': f"Lỗi hệ thống: {str(e)}"}), 500

@app.route('/genkey', methods=['POST', 'GET'])
def apikey():
    try:
        key, lifetime = tao_key()
        link_raw = upload(key)
        if not link_raw:
            return jsonify({'error': 'Không upload được lên Dpaste.org'}), 500
        short = rutgon(link_raw)
        return jsonify({
            'short_link': short if short else link_raw,
            'original_link': link_raw,
            'key': key
        }), 200
    except Exception as e:
        logger.error(f"Lỗi genkey: {e}")
        return jsonify({'error': f"Lỗi hệ thống: {str(e)}"}), 500

@app.route('/', methods=['GET'])
def index():
    return render_template_string("<h2>API lấy mã & tạo KEY đang hoạt động!<br>Muốn sử dụng phải xác nhận KEY!</h2>")

def start_flask():
    app.run(host="0.0.0.0", port=5000, threaded=True)

# ========== ĐĂNG KÝ LỆNH BOT ==========
async def set_bot_commands(application):
    commands = [
        BotCommand("start", "Khởi động bot"),
        BotCommand("ym", "Lấy mã tự động (phải xác nhận KEY)"),
        BotCommand("key", "Tạo KEY ngẫu nhiên (chỉ 1 thiết bị dùng)"),
        BotCommand("taokey", "Admin tạo KEY số ngày tuỳ ý (chỉ 1 thiết bị dùng)"),
        BotCommand("listkey", "Xem danh sách user đang sử dụng key"),
        BotCommand("checkkey", "Kiểm tra thời gian còn lại của KEY"),
        BotCommand("xacnhankey", "Xác nhận KEY để sử dụng"),
        BotCommand("savedata", "Lưu dữ liệu thủ công"),
        BotCommand("ban", "Ban người dùng"),
        BotCommand("unban", "Gỡ ban người dùng"),
        BotCommand("addadmin", "Thêm admin (chỉ master admin)"),
        BotCommand("deladmin", "Xóa admin (chỉ master admin)"),
        BotCommand("adminguide", "Hướng dẫn quản trị"),
    ]
    await application.bot.set_my_commands(commands)

# ========== CHẠY BOT & FLASK ==========
if __name__ == "__main__":
    # Tải dữ liệu từ file khi khởi động
    load_all_data()
    
    # Khởi động luồng tự động lưu dữ liệu
    threading.Thread(target=auto_save_data_loop, daemon=True).start()
    
    # Khởi động luồng tự động unban
    threading.Thread(target=auto_unban_loop, daemon=True).start()
    
    # Khởi động Flask API server
    threading.Thread(target=start_flask, daemon=True).start()
    
    # Khởi động bot
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ym", ym_command))
    application.add_handler(CommandHandler("key", key_command))
    application.add_handler(CommandHandler("taokey", taokey_command))
    application.add_handler(CommandHandler("listkey", listkey_command))
    application.add_handler(CommandHandler("checkkey", checkkey_command))
    application.add_handler(CommandHandler("xacnhankey", xacnhankey_command))
    application.add_handler(CommandHandler("savedata", savedata_command))
    application.add_handler(CommandHandler(["ban", "unban", "addadmin", "deladmin", "adminguide"], ym_command))
    application.post_init = set_bot_commands
    
    logger.info(f"Bot đã khởi động!")
    application.run_polling()