# 🎯 YeuMoney Code Generator Pro v3.0.0

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.0-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](docker-compose.yml)

> **🚀 Professional Multi-Service Code Generation Platform**  
> Supporting 13+ traffic sources with Web Dashboard, Telegram Bot, and CLI interfaces

## ✨ Tính Năng Chuyên Nghiệp

🌐 **Web Interface Hiện Đại** - Dashboard Bootstrap 5 với analytics real-time  
🤖 **Telegram Bot Nâng Cao** - Bot tương tác với tính năng admin  
💻 **CLI Interface Đẹp** - Giao diện terminal với Rich formatting  
🔒 **Bảo Mật Doanh Nghiệp** - API keys, rate limiting, IP blocking  
📊 **Thống Kê Chuyên Nghiệp** - Analytics và monitoring toàn diện  
🗄️ **Quản Lý Database** - SQLite với ORM patterns và backup  
🐳 **Docker Ready** - Hỗ trợ containerization hoàn chỉnh  
⚙️ **Cấu Hình Tập Trung** - Quản lý config JSON chuyên nghiệp

### 🚀 Phiên Bản Cơ Bản (`yeumoney.py`)
- ✅ Cấu trúc code chuyên nghiệp với OOP
- ✅ Xử lý lỗi toàn diện với retry mechanism
- ✅ Logging chi tiết
- ✅ Giao diện terminal thân thiện
- ✅ Hỗ trợ 13 loại quest khác nhau
- ✅ Validation input và timeout handling
- ✅ Lưu log tự động

### 🎨 Phiên Bản Nâng Cao (`yeumoney_enhanced.py`)
- ✅ Tất cả tính năng của phiên bản cơ bản
- ✅ Giao diện màu sắc đẹp mắt với Rich library
- ✅ Progress bar và spinner effects
- ✅ Bảng hiển thị quest với mô tả chi tiết
- ✅ Interactive prompts thông minh
- ✅ Fallback tự động về giao diện cơ bản

## 🎮 Các Loại Quest Được Hỗ Trợ

| STT | API | Mã Quest | Tên | Mô tả |
|-----|-----|----------|-----|-------|
| 1 | 🔵 MA | m88 | M88 Betting | Cá cược thể thao và casino trực tuyến |
| 2 | 🔵 MA | fb88 | FB88 Sports | Cá cược golf và thể thao |
| 3 | 🔵 MA | 188bet | 188BET Casino | Game bài Pok Deng online |
| 4 | 🔵 MA | w88 | W88 Poker | Poker và game bài chuyên nghiệp |
| 5 | 🔵 MA | v9bet | V9BET Basketball | Cá cược bóng rổ ảo |
| 6 | 🔵 MA | vn88 | VN88 Card Games | Game bài Gao Gae truyền thống |
| 7 | 🔵 MA | bk8 | BK8 Card Games | Game bài Catte online |
| 8 | 🔵 MA | w88xlm | W88XLM Solitaire | Game bài Solitaire kinh điển |
| 9 | 🟢 MD | 88betag | 88BET AG Direct | Kèo châu Á chuyên nghiệp |
| 10 | 🟢 MD | w88abc | W88ABC Mobile Gaming | Cá cược Liên Quân Mobile |
| 11 | 🟢 MD | v9betlg | V9BET Flat Betting | Phương pháp cược Flat Betting |
| 12 | 🟢 MD | bk8xo | BK8XO Lottery | Lô ba càng và xổ số |
| 13 | 🟢 MD | vn88ie | VN88IE Lottery System | Nuôi lô khung chuyên nghiệp |

## 🚀 Cài Đặt Nhanh

### Cách 1: Cài Đặt Tự Động (Khuyến Nghị)
```bash
# Clone repository
git clone https://github.com/doanhd3939/fix-loi.git
cd fix-loi

# Chạy script cài đặt
chmod +x install.sh
./install.sh

# Cấu hình settings
cp config.json.example config.json
nano config.json  # Thêm Telegram bot token

# Khởi chạy tất cả services
python main.py all
```

### Cách 2: Cài Đặt Thủ Công
```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình ứng dụng
cp config.json.example config.json
# Chỉnh sửa config.json với settings của bạn

# Khởi tạo và chạy
python main.py all
```

## 🎯 Cách Sử Dụng

### 🌐 Web Interface
```bash
python main.py web
# Truy cập: http://localhost:5000
```
- **Dashboard**: Tổng quan và thao tác nhanh
- **API Keys**: Tạo và quản lý keys  
- **Statistics**: Thống kê real-time
- **Admin Panel**: Quản trị hệ thống

### 🤖 Telegram Bot
```bash
python main.py bot
```
**Commands:**
- `/start` - Chào mừng và hướng dẫn
- `/key` - Tạo API key
- `/check <key>` - Kiểm tra key
- `/stats` - Xem thống kê (admin)
- `/help` - Tham khảo lệnh

### 💻 CLI Interface  
```bash
python main.py cli
```
**Tính năng:**
- Menu tương tác với rich formatting
- Quản lý key hoàn chỉnh
- Kiểm tra trạng thái hệ thống
- Xem cấu hình
- Giao diện terminal chuyên nghiệp

### 🐳 Docker Deployment
```bash
# Sử dụng Docker Compose (khuyến nghị)
docker-compose up -d

# Docker thủ công
docker build -t yeumoney-pro .
docker run -d -p 5000:5000 yeumoney-pro
```

#### Cài Đặt Cơ Bản
```bash
pip3 install requests
```

#### Cài Đặt Nâng Cao (Giao Diện Đẹp)
```bash
pip3 install -r requirements.txt
```

### Chạy Chương Trình

#### Phiên Bản Cơ Bản
```bash
python3 yeumoney.py
```

#### Phiên Bản Nâng Cao
```bash
python3 yeumoney_enhanced.py
```

## 📖 Hướng Dẫn Sử Dụng

1. **Khởi chạy chương trình**
   ```bash
   python3 yeumoney.py
   ```

2. **Xem danh sách quest**
   - Chương trình sẽ hiển thị tất cả các loại quest khả dụng
   - Mỗi quest có mã riêng (ví dụ: m88, fb88, v9bet...)

3. **Nhập loại quest**
   ```
   🎯 Nhập loại quest: m88
   ```

4. **Chờ kết quả**
   - Chương trình sẽ xử lý và hiển thị mã code
   - Thời gian chờ khoảng 80 giây

5. **Lặp lại hoặc thoát**
   - Chọn `y` để tạo mã khác
   - Chọn `n` hoặc nhập `exit` để thoát

## 📊 Các Tập Tin Được Tạo

- `yeumoney.log` - Log chi tiết của phiên bản cơ bản
- `yeumoney_enhanced.log` - Log chi tiết của phiên bản nâng cao
- `code_generation_log.json` - Lịch sử tạo mã (100 lần gần nhất)

## 🛠️ Cấu Trúc Dự Án

```
fix-loi/
├── yeumoney.py              # Phiên bản chính nâng cấp
├── yeumoney_enhanced.py     # Phiên bản giao diện đẹp
├── 13.py                    # File bot Telegram (không thay đổi)
├── requirements.txt         # Dependencies cho UI nâng cao
├── config.json             # Cấu hình ứng dụng
├── setup.sh                # Script cài đặt tự động
├── README.md               # Tài liệu này
└── logs/                   # Thư mục chứa log files
```

## 🔧 Tính Năng Kỹ Thuật

### 🏗️ Kiến Trúc
- **OOP Design**: Class-based architecture với separation of concerns
- **Error Handling**: Comprehensive exception handling với retry mechanism
- **Logging**: Structured logging với file rotation
- **Configuration**: JSON-based configuration management
- **Type Hints**: Full type annotations cho better IDE support

### 🔒 Bảo Mật & Reliability
- **Request Timeout**: Tự động timeout sau 30 giây
- **Retry Logic**: Tự động thử lại tối đa 3 lần khi thất bại
- **Session Management**: Persistent HTTP sessions với proper headers
- **Input Validation**: Kiểm tra và validate tất cả input từ user
- **Graceful Shutdown**: Xử lý Ctrl+C và các interrupt signals

### 🚀 Performance
- **Connection Pooling**: Sử dụng session để tái sử dụng kết nối
- **Efficient Regex**: Optimized regex patterns cho parsing
- **Memory Management**: Proper cleanup và resource management
- **Async-Ready**: Cấu trúc sẵn sàng cho async/await upgrade

## 🎨 UI/UX Enhancements

### Phiên Bản Cơ Bản
- Clean terminal interface
- Colored output (với colorama)
- Progress indicators
- Clear error messages
- Interactive prompts

### Phiên Bản Nâng Cao
- Beautiful tables với Rich library
- Progress bars và spinners
- Panels và styled output
- Interactive confirmation prompts
- Fallback graceful về basic UI

## 🐛 Troubleshooting

### Lỗi Import
```bash
# Nếu gặp lỗi import rich/colorama
pip3 install rich colorama

# Hoặc chỉ cài cơ bản
pip3 install requests
```

### Lỗi Permission
```bash
# Nếu không thể chạy setup.sh
chmod +x setup.sh
```

### Lỗi Network
- Kiểm tra kết nối internet
- Chương trình sẽ tự động retry 3 lần
- Xem log file để biết chi tiết lỗi

## 📝 Changelog

### Version 2.0.0 (Current)
- ✅ Hoàn toàn refactor code với OOP
- ✅ Thêm error handling toàn diện
- ✅ Thêm logging system
- ✅ Thêm retry mechanism
- ✅ Thêm phiên bản UI nâng cao
- ✅ Thêm configuration management
- ✅ Thêm type hints và documentation
- ✅ Thêm setup script tự động

### Version 1.0.0 (Original)
- ✅ Basic functionality với if-elif chains
- ✅ Hỗ trợ 13 loại quest
- ✅ Simple terminal interface

## 🤝 Contributing

Mọi đóng góp đều được chào đón! Hãy tạo issue hoặc pull request.

## 📄 License

Dự án này được phát triển cho mục đích học tập và sử dụng cá nhân.

## 👨‍💻 Author

- **Original**: YeuMoney Team
- **Upgraded**: AI Assistant with professional enhancements

---

*🎯 YeuMoney Code Generator - Making code generation simple and professional!*