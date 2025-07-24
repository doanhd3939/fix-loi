#!/bin/bash
# Setup script for YeuMoney Generator

echo "🎯 YeuMoney Generator - Setup Script"
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

echo "✅ Python3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 found"

# Install basic requirements
echo "📦 Installing basic requirements..."
pip3 install requests>=2.31.0

# Ask if user wants enhanced UI
read -p "🎨 Do you want to install enhanced UI libraries? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Installing enhanced UI libraries..."
    pip3 install rich colorama
    echo "✅ Enhanced UI libraries installed!"
    echo "💡 You can now run: python3 yeumoney_enhanced.py"
else
    echo "📦 Basic installation completed!"
    echo "💡 You can run: python3 yeumoney.py"
fi

echo ""
echo "🚀 Setup completed! Available scripts:"
echo "   • python3 yeumoney.py (Basic version)"
echo "   • python3 yeumoney_enhanced.py (Enhanced UI version)"
echo ""
echo "📝 Note: Enhanced version will fall back to basic UI if libraries are not installed"
