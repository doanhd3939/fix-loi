#!/bin/bash

# YeuMoney Pro Installer Script
# Professional installation and setup

set -e

echo "🚀 YeuMoney Pro Installation Script"
echo "==================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.8+ is installed
check_python() {
    print_status "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD=python3
    elif command -v python &> /dev/null; then
        PYTHON_CMD=python
    else
        print_error "Python is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python $PYTHON_VERSION found, but 3.8+ is required"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Skipping creation."
    else
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Virtual environment activated"
    else
        print_error "Virtual environment not found"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Create configuration file
create_config() {
    print_status "Setting up configuration..."
    
    if [ -f "config.json" ]; then
        print_warning "Configuration file already exists. Skipping creation."
        return
    fi
    
    # Create default configuration
    cat > config.json << EOF
{
  "app_config": {
    "name": "YeuMoney Pro",
    "version": "3.0.0",
    "environment": "production",
    "debug": false
  },
  "bot_config": {
    "token": "",
    "admin_users": [],
    "key_lifetime_hours": 24,
    "max_keys_per_user": 1,
    "rate_limit": {
      "messages_per_minute": 20,
      "commands_per_hour": 100
    }
  },
  "web_config": {
    "host": "127.0.0.1",
    "port": 5000,
    "secret_key": "$(openssl rand -hex 32)",
    "admin_password": "admin123",
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
  },
  "traffic_sources": {
    "trafficforce": {
      "name": "TrafficForce",
      "api_type": "http",
      "description": "Adult traffic platform with high-quality visitors"
    },
    "popunder": {
      "name": "PopUnder",
      "api_type": "http", 
      "description": "Pop-under advertising network"
    },
    "propellerads": {
      "name": "PropellerAds",
      "api_type": "http",
      "description": "Native and push notification ads"
    },
    "exoclick": {
      "name": "ExoClick",
      "api_type": "http",
      "description": "Premium adult advertising network"
    },
    "juicyads": {
      "name": "JuicyAds",
      "api_type": "http",
      "description": "Adult ad network with high payouts"
    },
    "eroadvertising": {
      "name": "EroAdvertising",
      "api_type": "http",
      "description": "Adult content advertising platform"
    },
    "trafficstars": {
      "name": "TrafficStars",
      "api_type": "http",
      "description": "Adult traffic network with premium inventory"
    },
    "clickdealer": {
      "name": "ClickDealer",
      "api_type": "http",
      "description": "Performance marketing platform"
    },
    "adcash": {
      "name": "AdCash",
      "api_type": "http",
      "description": "Display advertising network"
    },
    "bidvertiser": {
      "name": "BidVertiser",
      "api_type": "http",
      "description": "PPC advertising platform"
    },
    "popads": {
      "name": "PopAds",
      "api_type": "http",
      "description": "Pop advertising network"
    },
    "admaven": {
      "name": "AdMaven",
      "api_type": "http",
      "description": "Pop and push advertising network"
    },
    "hilltopads": {
      "name": "HilltopAds",
      "api_type": "http",
      "description": "Multiple ad formats network"
    }
  }
}
EOF
    
    print_success "Configuration file created"
    print_warning "Please edit config.json to add your Telegram bot token and other settings"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p backups
    mkdir -p temp
    
    print_success "Directories created"
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    
    $PYTHON_CMD main.py --status > /dev/null 2>&1 || true
    
    if [ -f "yeumoney.db" ]; then
        print_success "Database initialized"
    else
        print_warning "Database initialization may have failed. Check logs."
    fi
}

# Set permissions
set_permissions() {
    print_status "Setting file permissions..."
    
    chmod +x main.py
    chmod +x install.sh
    chmod 644 config.json
    chmod -R 755 src/
    
    print_success "Permissions set"
}

# Create systemd service (Linux only)
create_service() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_status "Creating systemd service..."
        
        SERVICE_FILE="/etc/systemd/system/yeumoney-pro.service"
        CURRENT_DIR=$(pwd)
        USER=$(whoami)
        
        if [ "$EUID" -eq 0 ]; then
            cat > $SERVICE_FILE << EOF
[Unit]
Description=YeuMoney Pro - Code Generation Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/venv/bin
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/main.py all
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
            
            systemctl daemon-reload
            systemctl enable yeumoney-pro.service
            
            print_success "Systemd service created and enabled"
            print_status "Use 'sudo systemctl start yeumoney-pro' to start the service"
        else
            print_warning "Run as root to create systemd service"
        fi
    fi
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    # Test basic functionality
    if $PYTHON_CMD main.py --version > /dev/null 2>&1; then
        print_success "Basic functionality test passed"
    else
        print_error "Basic functionality test failed"
        return 1
    fi
    
    # Test configuration loading
    if $PYTHON_CMD -c "from src.core.config import config; config.get('app_config.name')" > /dev/null 2>&1; then
        print_success "Configuration loading test passed"
    else
        print_error "Configuration loading test failed"
        return 1
    fi
    
    print_success "Installation tests passed!"
}

# Main installation process
main() {
    echo
    print_status "Starting YeuMoney Pro installation..."
    echo
    
    # Check system requirements
    check_python
    
    # Setup Python environment
    create_venv
    activate_venv
    install_dependencies
    
    # Setup application
    create_config
    create_directories
    init_database
    set_permissions
    
    # Optional: Create system service
    read -p "Create systemd service? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_service
    fi
    
    # Test installation
    test_installation
    
    echo
    print_success "🎉 YeuMoney Pro installation completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Edit config.json to add your Telegram bot token"
    echo "2. Configure admin users and other settings"
    echo "3. Run: python main.py all"
    echo
    echo "For help: python main.py --help"
    echo "Documentation: README_PRO.md"
    echo
}

# Run installation if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
