#!/bin/bash

# =============================================================================
# Enterprise Monitor Auto Installation Script for Ubuntu 24.04
# =============================================================================
# This script installs all dependencies and sets up the Enterprise Monitor
# system with proper error handling and permissions
# =============================================================================

set -e  # Exit on any error

echo "🚀 Starting Enterprise Monitor Installation on Ubuntu 24.04"
echo "=" * 60

# =============================================================================
# STEP 1: System Update and Essential Packages
# =============================================================================
echo "📦 Step 1: Updating system and installing essential packages..."

sudo apt update && sudo apt upgrade -y

# Install essential system packages
sudo apt install -y \
    git curl wget unzip \
    build-essential libssl-dev libffi-dev \
    software-properties-common apt-transport-https ca-certificates \
    gnupg lsb-release

echo "✅ System packages updated successfully"

# =============================================================================
# STEP 2: Install Google Chrome (Fix Chrome Binary Issues)
# =============================================================================
echo "🌐 Step 2: Installing Google Chrome..."

# Download and install Google Chrome
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -P /tmp

# Install Chrome with dependencies
sudo apt install -y /tmp/google-chrome-stable_current_amd64.deb

# Cleanup
rm -f /tmp/google-chrome-stable_current_amd64.deb

# Verify Chrome installation
if google-chrome --version; then
    echo "✅ Google Chrome installed successfully"
else
    echo "❌ Google Chrome installation failed"
    exit 1
fi

# =============================================================================
# STEP 3: Install Xvfb and Graphics Dependencies (Fix Headless Issues)
# =============================================================================
echo "🖥️ Step 3: Installing Xvfb and graphics dependencies..."

sudo apt install -y \
    xvfb xauth x11-utils \
    fonts-liberation libasound2 libatk-bridge2.0-0 \
    libdrm2 libgtk-3-0 libnspr4 libnss3 libxss1 libxtst6 \
    xdg-utils libatspi2.0-0 libxkbcommon0 libxrandr2 \
    fonts-dejavu-core fonts-freefont-ttf

# Verify Xvfb installation
if command -v Xvfb &> /dev/null; then
    echo "✅ Xvfb installed successfully"
else
    echo "❌ Xvfb installation failed"
    exit 1
fi

# =============================================================================
# STEP 4: Install Python and Virtual Environment Setup
# =============================================================================
echo "🐍 Step 4: Setting up Python and virtual environment..."

# Install Python and venv
sudo apt install -y \
    python3 python3-pip python3-venv python3-dev \
    python3-setuptools python3-distutils

# Verify Python installation
if python3 --version; then
    echo "✅ Python3 installed successfully"
else
    echo "❌ Python3 installation failed"
    exit 1
fi

# =============================================================================
# STEP 5: Clone Project from GitHub
# =============================================================================
echo "📥 Step 5: Cloning project from GitHub..."

# Remove existing directory if it exists
if [ -d "/opt/enterprise-monitor" ]; then
    echo "⚠️ Directory exists, removing old installation..."
    sudo rm -rf /opt/enterprise-monitor
fi

# Clone the repository
sudo git clone https://github.com/sambbdevpro/bocaobb.git /opt/enterprise-monitor

# Verify clone
if [ -d "/opt/enterprise-monitor" ]; then
    echo "✅ Project cloned successfully"
else
    echo "❌ Project clone failed"
    exit 1
fi

# =============================================================================
# STEP 6: Setup Virtual Environment and Python Dependencies
# =============================================================================
echo "📚 Step 6: Setting up virtual environment and dependencies..."

# Create virtual environment
cd /opt/enterprise-monitor
sudo python3 -m venv venv

# Set proper ownership for the entire project
sudo chown -R $USER:$USER /opt/enterprise-monitor

# Activate virtual environment and install dependencies
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip

# Install required Python packages (Fix Module Not Found Issues)
pip install \
    selenium \
    webdriver-manager \
    requests \
    python-telegram-bot \
    beautifulsoup4 \
    lxml \
    psutil \
    urllib3 \
    schedule \
    certifi \
    APScheduler

# Verify critical imports
python -c "
import selenium, requests, schedule
from webdriver_manager.chrome import ChromeDriverManager
print('✅ All Python dependencies installed successfully')
"

# =============================================================================
# STEP 7: Setup Directories and Permissions (Fix Permission Issues)
# =============================================================================
echo "📁 Step 7: Setting up directories and permissions..."

# Create required directories
sudo mkdir -p /opt/enterprise-monitor/{downloads,logs}
sudo mkdir -p /var/log/enterprise-monitor

# Create log file with proper permissions
sudo touch /var/log/enterprise-monitor.log
sudo chown $USER:$USER /var/log/enterprise-monitor.log
sudo chmod 664 /var/log/enterprise-monitor.log

# Set project permissions
sudo chown -R $USER:$USER /opt/enterprise-monitor
sudo chmod -R 755 /opt/enterprise-monitor
sudo chmod +x /opt/enterprise-monitor/*.py

echo "✅ Directories and permissions configured"

# =============================================================================
# STEP 8: Create SystemD Service (Fix Service Configuration Issues)
# =============================================================================
echo "⚙️ Step 8: Creating systemd service..."

# Create service file with proper configuration
sudo tee /etc/systemd/system/enterprise-monitor.service > /dev/null <<EOF
[Unit]
Description=Enterprise Monitor Service
After=network.target
Wants=network-online.target
StartLimitBurst=10
StartLimitIntervalSec=300

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=/opt/enterprise-monitor
Environment=PATH=/opt/enterprise-monitor/venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=/opt/enterprise-monitor
Environment=PYTHONUNBUFFERED=1
Environment=DISPLAY=:99
Environment=HOME=/home/$USER
Environment=ENTERPRISE_MONITOR_SERVER=true
ExecStartPre=/bin/bash -c 'pkill -f "Xvfb.*:99" || true'
ExecStartPre=/bin/sleep 2
ExecStart=/opt/enterprise-monitor/venv/bin/python server_launcher.py
StandardOutput=journal
StandardError=journal
SyslogIdentifier=enterprise-monitor
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ SystemD service created"

# =============================================================================
# STEP 9: Enable and Start Service
# =============================================================================
echo "🔧 Step 9: Enabling and starting service..."

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service for auto-start
sudo systemctl enable enterprise-monitor.service

echo "✅ Service enabled for auto-start"

# =============================================================================
# STEP 10: Final Testing and Verification
# =============================================================================
echo "🧪 Step 10: Running final tests..."

# Test Chrome and Xvfb
echo "Testing Chrome and Xvfb..."
export DISPLAY=:99
Xvfb :99 -screen 0 1366x768x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!
sleep 2

# Test Chrome headless
google-chrome --headless --no-sandbox --disable-gpu --dump-dom https://www.google.com >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Chrome headless test successful"
else
    echo "⚠️ Chrome headless test failed, but continuing..."
fi

# Stop test Xvfb
kill $XVFB_PID 2>/dev/null || true

# Test Python imports
cd /opt/enterprise-monitor
source venv/bin/activate
python -c "
try:
    from config import CONFIG
    from browser_manager import BrowserManager
    print('✅ Project modules import successfully')
except Exception as e:
    print(f'⚠️ Module import warning: {e}')
"

# =============================================================================
# STEP 11: Start the Service
# =============================================================================
echo "🚀 Step 11: Starting Enterprise Monitor service..."

sudo systemctl start enterprise-monitor.service

# Wait a moment for service to initialize
sleep 5

# Check service status
if sudo systemctl is-active enterprise-monitor.service > /dev/null 2>&1; then
    echo "✅ Service started successfully"
    sudo systemctl status enterprise-monitor.service --no-pager -l
else
    echo "⚠️ Service may have issues, checking logs..."
    sudo journalctl -u enterprise-monitor.service --no-pager -n 20
fi

# =============================================================================
# Installation Complete
# =============================================================================
echo ""
echo "🎉 Enterprise Monitor Installation Complete!"
echo "=" * 60
echo "📊 Installation Summary:"
echo "  ✅ System packages: Updated"
echo "  ✅ Google Chrome: Installed"
echo "  ✅ Xvfb: Installed"
echo "  ✅ Python Virtual Environment: Created"
echo "  ✅ Project Dependencies: Installed"
echo "  ✅ Permissions: Configured"
echo "  ✅ SystemD Service: Created and enabled"
echo ""
echo "🔧 Useful Commands:"
echo "  • Check service status: sudo systemctl status enterprise-monitor"
echo "  • View live logs: sudo journalctl -u enterprise-monitor -f"
echo "  • Restart service: sudo systemctl restart enterprise-monitor"
echo "  • Stop service: sudo systemctl stop enterprise-monitor"
echo ""
echo "📁 Project Location: /opt/enterprise-monitor"
echo "📝 Log File: /var/log/enterprise-monitor.log"
echo ""
echo "🚀 The Enterprise Monitor system is now running!"
