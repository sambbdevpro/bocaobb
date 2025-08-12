#!/bin/bash
# ubuntu_setup.sh - Ubuntu Server Setup Script

set -e  # Exit on any error

echo "🐧 Starting Ubuntu Server Setup for Enterprise Monitor..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "Please don't run this script as root. Run as regular user with sudo access."
   exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install basic dependencies
print_status "Installing basic dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    curl \
    unzip \
    xvfb \
    libxss1 \
    libappindicator1 \
    libindicator7 \
    fonts-liberation \
    libasound2 \
    libnspr4 \
    libnss3 \
    libxrandr2 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    ca-certificates \
    supervisor

# Install Google Chrome
print_status "Installing Google Chrome..."
if ! command -v google-chrome &> /dev/null; then
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    sudo apt update
    sudo apt install google-chrome-stable -y
    print_status "Chrome installed successfully"
else
    print_status "Chrome already installed"
fi

# Create system user
print_status "Creating system user..."
if ! id "enterprise-monitor" &>/dev/null; then
    sudo useradd -r -s /bin/bash -d /opt/enterprise-monitor -m enterprise-monitor
    print_status "User 'enterprise-monitor' created"
else
    print_status "User 'enterprise-monitor' already exists"
fi

# Create project directory
print_status "Setting up project directory..."
sudo mkdir -p /opt/enterprise-monitor
sudo chown enterprise-monitor:enterprise-monitor /opt/enterprise-monitor

# Copy project files (assuming current directory has the project)
print_status "Copying project files..."
sudo cp -r ./* /opt/enterprise-monitor/
sudo chown -R enterprise-monitor:enterprise-monitor /opt/enterprise-monitor

# Create Python virtual environment
print_status "Setting up Python virtual environment..."
sudo -u enterprise-monitor python3 -m venv /opt/enterprise-monitor/venv

# Install Python dependencies
print_status "Installing Python dependencies..."
sudo -u enterprise-monitor /opt/enterprise-monitor/venv/bin/pip install --upgrade pip
sudo -u enterprise-monitor /opt/enterprise-monitor/venv/bin/pip install \
    selenium \
    webdriver-manager \
    requests \
    python-telegram-bot \
    beautifulsoup4 \
    lxml

# Create log directories
print_status "Creating log directories..."
sudo mkdir -p /var/log/enterprise-monitor
sudo chown enterprise-monitor:enterprise-monitor /var/log/enterprise-monitor

# Install systemd service
print_status "Installing systemd service..."
sudo cp /opt/enterprise-monitor/enterprise-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable enterprise-monitor

# Create logrotate config
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/enterprise-monitor > /dev/null <<EOF
/var/log/enterprise-monitor/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 enterprise-monitor enterprise-monitor
    postrotate
        systemctl reload enterprise-monitor > /dev/null 2>&1 || true
    endscript
}
EOF

# Set executable permissions
print_status "Setting permissions..."
sudo chmod +x /opt/enterprise-monitor/server_launcher.py
sudo chmod +x /opt/enterprise-monitor/ubuntu_setup.sh

print_status "✅ Ubuntu setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit /opt/enterprise-monitor/config.py with your settings"
echo "2. Start the service: sudo systemctl start enterprise-monitor"
echo "3. Check status: sudo systemctl status enterprise-monitor"
echo "4. View logs: sudo journalctl -u enterprise-monitor -f"
echo ""
print_warning "Don't forget to configure your Telegram bot token and chat ID in config.py!"
