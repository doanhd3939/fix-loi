# YeuMoney Code Generator Pro v3.0.0

## 🚀 Professional Multi-Service Application

YeuMoney Pro is a comprehensive code generation system supporting 13+ traffic sources with professional-grade architecture, multiple interfaces, and enterprise features.

### ✨ Key Features

- **🌐 Web Interface**: Modern Bootstrap 5 dashboard
- **🤖 Telegram Bot**: Advanced bot with inline keyboards  
- **💻 CLI Interface**: Rich terminal interface with Beautiful UI
- **🔒 Security**: Rate limiting, IP blocking, API key management
- **📊 Analytics**: Comprehensive statistics and monitoring
- **🗄️ Database**: Professional SQLite with ORM patterns
- **⚙️ Configuration**: Centralized JSON-based config system
- **📝 Logging**: Structured logging with rotation

### 🏗️ Architecture

```
src/
├── core/          # Core system components
│   ├── config.py    # Configuration management
│   ├── database.py  # Database operations
│   └── cli.py       # CLI interface
├── models/        # Data models and structures
│   └── models.py    # User, APIKey, Request models
├── api/           # API client and external services
│   └── client.py    # Traffic source API client
├── bot/           # Telegram bot implementation
│   └── telegram_bot.py
├── web/           # Web interface
│   └── app.py       # Flask web application
└── utils/         # Utility modules
    ├── security.py  # Security and rate limiting
    └── helpers.py   # Helper functions
```

### 🎯 Supported Traffic Sources

1. **TrafficForce** - Adult traffic platform
2. **PopUnder** - Pop-under advertising
3. **PropellerAds** - Native and push ads
4. **ExoClick** - Adult advertising network
5. **JuicyAds** - Adult ad network
6. **EroAdvertising** - Adult content ads
7. **TrafficStars** - Adult traffic network
8. **ClickDealer** - Performance marketing
9. **AdCash** - Display advertising
10. **BidVertiser** - PPC advertising
11. **PopAds** - Pop advertising network
12. **AdMaven** - Pop and push ads
13. **HilltopAds** - Multiple ad formats

## 🔧 Installation

### Prerequisites

- **Python 3.8+** required
- **Virtual environment** recommended
- **SQLite 3** for database
- **Redis** (optional, for caching)

### Step 1: Environment Setup

```bash
# Clone or download the project
cd yeumoney-pro

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration

```bash
# Copy example configuration
cp config.json.example config.json

# Edit configuration
nano config.json
```

**Important Configuration Values:**

```json
{
  "bot_config": {
    "token": "YOUR_TELEGRAM_BOT_TOKEN",
    "admin_users": [YOUR_TELEGRAM_USER_ID],
    "key_lifetime_hours": 24,
    "max_keys_per_user": 1
  },
  "web_config": {
    "host": "127.0.0.1",
    "port": 5000,
    "secret_key": "your-secret-key-here",
    "admin_password": "your-admin-password"
  },
  "api_config": {
    "base_url": "https://api.yeumoney.pro",
    "request_timeout": 30,
    "max_retries": 3
  }
}
```

### Step 3: Database Setup

```bash
# Initialize database (automatic on first run)
python main.py --status
```

## 🚀 Running the Application

### All Services (Recommended)

```bash
# Start all services
python main.py all

# Or simply
python main.py
```

This starts:
- 🌐 Web interface at `http://localhost:5000`
- 🤖 Telegram bot (if configured)
- 📊 Background monitoring

### Individual Services

```bash
# Web interface only
python main.py web

# Telegram bot only  
python main.py bot

# CLI interface only
python main.py cli
```

### System Commands

```bash
# Check system status
python main.py --status

# Show version
python main.py --version

# Use custom config
python main.py --config /path/to/config.json
```

## 🌐 Web Interface

Access the web dashboard at `http://localhost:5000`:

- **🏠 Dashboard**: Overview and quick actions
- **🔑 API Keys**: Manage user keys
- **📊 Statistics**: System analytics
- **⚙️ Admin Panel**: Administrative functions
- **📖 Documentation**: API reference

### API Endpoints

```
GET  /                 # Dashboard
GET  /keys             # Manage API keys
POST /api/generate     # Generate code
GET  /api/stats        # System statistics
POST /admin/login      # Admin authentication
```

## 🤖 Telegram Bot

### Setup Bot

1. Create bot with [@BotFather](https://t.me/botfather)
2. Get bot token
3. Add token to `config.json`
4. Add your Telegram ID to `admin_users`

### Bot Commands

- `/start` - Welcome and instructions
- `/help` - Show available commands
- `/key` - Generate new API key
- `/check <key>` - Validate API key
- `/stats` - View statistics (admin only)
- `/users` - Manage users (admin only)
- `/config` - System configuration (admin only)

### Bot Features

- **🔐 Key Management**: Create and validate API keys
- **📊 Statistics**: Usage analytics
- **👥 User Management**: User registration and tracking
- **⚙️ Admin Controls**: System administration
- **🎛️ Inline Keyboards**: Interactive buttons
- **🔒 Security**: Rate limiting and validation

## 💻 CLI Interface

Interactive command-line interface with rich formatting:

```bash
python main.py cli
```

### CLI Features

- **🎨 Rich UI**: Beautiful terminal interface
- **🔑 Key Management**: Create, validate, and manage keys
- **📊 Statistics**: View system analytics
- **🔍 System Status**: Health checks
- **⚙️ Configuration**: View settings
- **📖 Help System**: Comprehensive help

### CLI Menu

```
1. Generate Code      # Generate codes from traffic sources
2. Manage API Keys    # Key creation and management
3. View Statistics    # System analytics
4. System Status      # Health and status checks
5. Configuration      # View current settings
6. Help              # Documentation and tips
0. Exit              # Exit application
```

## 🔒 Security Features

### API Key System

- **🔐 Secure Generation**: Cryptographically secure keys
- **⏰ Expiration**: Configurable key lifetime
- **📊 Usage Tracking**: Monitor key usage
- **🚫 Validation**: Comprehensive key validation
- **👤 User Binding**: Keys tied to specific users

### Rate Limiting

- **🔢 Request Limits**: Per-IP and per-key limits
- **🕐 Time Windows**: Sliding window rate limiting
- **🚫 IP Blocking**: Automatic suspicious IP blocking
- **📊 Monitoring**: Rate limit analytics

### Web Security

- **🔒 HTTPS Ready**: SSL/TLS support
- **🛡️ Security Headers**: Comprehensive security headers
- **🔐 Admin Auth**: Password-protected admin areas
- **🚫 Input Validation**: All inputs validated and sanitized

## 📊 Monitoring & Analytics

### System Statistics

- **👥 User Metrics**: Active users, registrations
- **🔑 Key Metrics**: Active keys, usage patterns
- **📈 Request Analytics**: Success rates, error patterns
- **⚡ Performance**: Response times, throughput

### Logging

- **📝 Structured Logs**: JSON-formatted logs
- **🔄 Log Rotation**: Automatic log rotation
- **📊 Log Levels**: Configurable verbosity
- **🔍 Error Tracking**: Detailed error information

### Health Checks

```bash
# System health check
curl http://localhost:5000/health

# Detailed status
python main.py --status
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker

```bash
# Build image
docker build -t yeumoney-pro .

# Run container
docker run -d \
  --name yeumoney-pro \
  -p 5000:5000 \
  -v $(pwd)/config.json:/app/config.json \
  -v $(pwd)/logs:/app/logs \
  yeumoney-pro
```

## 🔧 Configuration Reference

### Complete Configuration

```json
{
  "app_config": {
    "name": "YeuMoney Pro",
    "version": "3.0.0",
    "environment": "production",
    "debug": false
  },
  "bot_config": {
    "token": "YOUR_BOT_TOKEN",
    "admin_users": [123456789],
    "key_lifetime_hours": 24,
    "max_keys_per_user": 1,
    "rate_limit": {
      "messages_per_minute": 20,
      "commands_per_hour": 100
    }
  },
  "web_config": {
    "host": "0.0.0.0",
    "port": 5000,
    "secret_key": "your-secret-key",
    "admin_password": "secure-admin-password",
    "rate_limit": {
      "requests_per_minute": 60,
      "requests_per_hour": 1000
    }
  },
  "api_config": {
    "base_url": "https://api.yeumoney.pro",
    "request_timeout": 30,
    "max_retries": 3,
    "retry_delay": 1.0
  },
  "database_config": {
    "url": "sqlite:///yeumoney.db",
    "backup_enabled": true,
    "backup_interval_hours": 24
  },
  "logging_config": {
    "level": "INFO",
    "file": "logs/yeumoney.log",
    "max_size_mb": 10,
    "backup_count": 5
  }
}
```

### Traffic Sources Configuration

Each traffic source supports:

```json
{
  "traffic_source_name": {
    "name": "Display Name",
    "api_type": "http|websocket|custom",
    "description": "Traffic source description",
    "endpoint": "https://api.example.com",
    "auth_required": true,
    "rate_limit": 100,
    "timeout": 30
  }
}
```

## 🛠️ Development

### Project Structure

```
yeumoney-pro/
├── src/                 # Source code
├── templates/           # HTML templates
├── static/             # CSS, JS, images
├── logs/               # Application logs
├── tests/              # Test files
├── config.json         # Configuration
├── requirements.txt    # Python dependencies
├── main.py            # Application entry point
├── docker-compose.yml # Docker configuration
├── Dockerfile         # Docker image
└── README.md          # Documentation
```

### Adding New Traffic Sources

1. **Define Configuration**:
```json
{
  "new_source": {
    "name": "New Traffic Source",
    "api_type": "http",
    "description": "Description here",
    "endpoint": "https://api.newsource.com"
  }
}
```

2. **Update API Client**:
```python
# In src/api/client.py
def handle_new_source(self, config, user_id):
    # Implementation here
    pass
```

3. **Test Integration**:
```bash
python main.py cli
# Use option 1 to test new source
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

## 📚 API Documentation

### Generate Code Endpoint

```
POST /api/generate
Content-Type: application/json

{
  "api_key": "your-api-key",
  "traffic_type": "trafficforce",
  "parameters": {
    "custom_param": "value"
  }
}
```

**Response:**
```json
{
  "success": true,
  "code": "generated-code-here",
  "processing_time": 0.45,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Statistics Endpoint

```
GET /api/stats
Authorization: Bearer your-api-key
```

**Response:**
```json
{
  "total_users": 150,
  "active_keys": 89,
  "total_requests": 5420,
  "success_rate": 94.2,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

## 🆘 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Missing dependencies
pip install -r requirements.txt

# Virtual environment issues
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

#### 2. Database Issues
```bash
# Reset database
rm yeumoney.db
python main.py --status  # Recreates database
```

#### 3. Configuration Problems
```bash
# Validate configuration
python -c "import json; json.load(open('config.json'))"

# Use default config
mv config.json config.json.backup
python main.py  # Creates default config
```

#### 4. Bot Token Issues
```bash
# Test bot token
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"
```

#### 5. Permission Issues
```bash
# Fix file permissions
chmod 755 main.py
chmod 644 config.json
```

### Logs and Debugging

```bash
# View logs
tail -f logs/yeumoney.log

# Debug mode
python main.py web --debug

# Verbose logging
export LOG_LEVEL=DEBUG
python main.py
```

## 🔄 Updates and Maintenance

### Updating the Application

```bash
# Backup current version
cp -r yeumoney-pro yeumoney-pro-backup

# Update code
git pull origin main  # If using git

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart services
python main.py all
```

### Database Maintenance

```bash
# Backup database
cp yeumoney.db yeumoney.db.backup

# Clean old logs
find logs/ -name "*.log.*" -mtime +30 -delete

# Optimize database
sqlite3 yeumoney.db "VACUUM;"
```

### Log Rotation

Automatic log rotation is configured, but manual cleanup:

```bash
# Clean old logs (older than 30 days)
find logs/ -name "*.log.*" -mtime +30 -delete

# Compress large logs
gzip logs/yeumoney.log.old
```

## 📞 Support

- **📧 Email**: support@yeumoney.pro
- **💬 Telegram**: [@YeuMoneySupport](https://t.me/YeuMoneySupport)
- **🌐 Website**: [https://yeumoney.pro](https://yeumoney.pro)
- **📖 Documentation**: [https://docs.yeumoney.pro](https://docs.yeumoney.pro)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**YeuMoney Pro v3.0.0** - Professional Code Generation System 🚀
