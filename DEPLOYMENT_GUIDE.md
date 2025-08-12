# 🐧 Ubuntu Server Deployment Guide

## Hướng dẫn triển khai Enterprise Monitor trên Ubuntu Server

### 📋 Yêu cầu hệ thống

- **OS**: Ubuntu 20.04+ (hoặc Debian 11+)
- **RAM**: Tối thiểu 2GB, khuyến nghị 4GB
- **CPU**: 2 cores
- **Disk**: Tối thiểu 10GB trống
- **Network**: Kết nối internet ổn định

### 🚀 Cài đặt tự động (Khuyến nghị)

```bash
# 1. Clone hoặc upload project lên server
git clone <your-repo> /tmp/enterprise-monitor
cd /tmp/enterprise-monitor

# 2. Chạy script setup tự động
chmod +x ubuntu_setup.sh
./ubuntu_setup.sh

# 3. Cấu hình config.py
sudo nano /opt/enterprise-monitor/config.py
# Cập nhật telegram bot_token và chat_id

# 4. Khởi động service
sudo systemctl start enterprise-monitor
sudo systemctl status enterprise-monitor
```

### ⚙️ Cài đặt thủ công

#### Bước 1: Cài đặt dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python và dependencies
sudo apt install -y python3 python3-pip python3-venv wget curl unzip xvfb

# Install Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update && sudo apt install google-chrome-stable -y
```

#### Bước 2: Setup project

```bash
# Tạo user và directory
sudo useradd -r -s /bin/bash -d /opt/enterprise-monitor -m enterprise-monitor
sudo mkdir -p /opt/enterprise-monitor
sudo chown enterprise-monitor:enterprise-monitor /opt/enterprise-monitor

# Copy files
sudo cp -r ./* /opt/enterprise-monitor/
sudo chown -R enterprise-monitor:enterprise-monitor /opt/enterprise-monitor

# Setup Python environment
sudo -u enterprise-monitor python3 -m venv /opt/enterprise-monitor/venv
sudo -u enterprise-monitor /opt/enterprise-monitor/venv/bin/pip install selenium webdriver-manager requests python-telegram-bot beautifulsoup4 lxml
```

#### Bước 3: Cấu hình systemd

```bash
# Copy service file
sudo cp /opt/enterprise-monitor/enterprise-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable enterprise-monitor
```

### 🔧 Cấu hình

#### Config.py quan trọng:

```python
'telegram': {
    'bot_token': 'YOUR_BOT_TOKEN',  # Thay bằng token thật
    'chat_id': 'YOUR_CHAT_ID',      # Thay bằng chat ID thật
    'enabled': True
},
'browser': {
    'headless': True,      # REQUIRED cho server
    'server_mode': True,   # REQUIRED cho server
    'disable_gpu': True,   # REQUIRED cho server
    'no_sandbox': True     # REQUIRED cho server
}
```

### 🎮 Quản lý service

```bash
# Khởi động
sudo systemctl start enterprise-monitor

# Dừng
sudo systemctl stop enterprise-monitor

# Restart
sudo systemctl restart enterprise-monitor

# Xem status
sudo systemctl status enterprise-monitor

# Xem logs
sudo journalctl -u enterprise-monitor -f

# Xem logs file
tail -f /var/log/enterprise-monitor.log
```

### 🐛 Troubleshooting

#### Chrome không khởi động được:

```bash
# Kiểm tra Chrome
google-chrome --version

# Test headless
google-chrome --headless --no-sandbox --disable-gpu --dump-dom https://google.com

# Kiểm tra display
echo $DISPLAY
ps aux | grep Xvfb
```

#### Permission issues:

```bash
# Fix permissions
sudo chown -R enterprise-monitor:enterprise-monitor /opt/enterprise-monitor
sudo chmod +x /opt/enterprise-monitor/server_launcher.py
sudo chmod +x /opt/enterprise-monitor/server_main.py
```

#### Memory issues:

```bash
# Check memory
free -h
top -p $(pgrep chrome)

# Adjust service limits in enterprise-monitor.service:
MemoryMax=4G
CPUQuota=100%
```

### 📊 Monitoring

```bash
# Real-time logs
sudo journalctl -u enterprise-monitor -f

# Performance monitoring
htop
iotop

# Check downloads
ls -la /opt/enterprise-monitor/downloads/

# Check service health
systemctl is-active enterprise-monitor
systemctl is-enabled enterprise-monitor
```

### 🔒 Security

#### Firewall (nếu cần):

```bash
# Basic firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow out 80,443  # HTTP/HTTPS outbound
```

#### Log rotation:

Log rotation đã được cấu hình tự động trong `/etc/logrotate.d/enterprise-monitor`

### 📞 Support

Khi gặp vấn đề, thu thập thông tin sau:

```bash
# System info
uname -a
lsb_release -a
free -h
df -h

# Service status
sudo systemctl status enterprise-monitor
sudo journalctl -u enterprise-monitor --no-pager -l

# Process info
ps aux | grep chrome
ps aux | grep python
```
