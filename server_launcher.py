#!/usr/bin/env python3
# server_launcher.py - Ubuntu Server Launcher

import os
import sys
import subprocess
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/enterprise-monitor.log'),
        logging.StreamHandler()
    ]
)

def setup_display():
    """Setup virtual display for headless Chrome"""
    try:
        # Set DISPLAY for Xvfb
        os.environ['DISPLAY'] = ':99'
        
        # Start Xvfb in background
        subprocess.Popen([
            'Xvfb', ':99', 
            '-screen', '0', '1366x768x24',
            '-ac', '+extension', 'GLX'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        logging.info("✅ Virtual display setup completed")
        return True
    except Exception as e:
        logging.error(f"❌ Virtual display setup failed: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are available"""
    required_commands = ['google-chrome', 'Xvfb']
    
    for cmd in required_commands:
        try:
            subprocess.run(['which', cmd], check=True, capture_output=True)
            logging.info(f"✅ {cmd} found")
        except subprocess.CalledProcessError:
            logging.error(f"❌ {cmd} not found. Please install it.")
            return False
    
    return True

def setup_directories():
    """Setup required directories with correct permissions"""
    directories = [
        '/opt/enterprise-monitor/downloads',
        '/opt/enterprise-monitor/logs',
        '/var/log/enterprise-monitor'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            os.chmod(directory, 0o755)
            logging.info(f"✅ Directory created: {directory}")
        except Exception as e:
            logging.error(f"❌ Failed to create {directory}: {e}")
            return False
    
    return True

def main():
    """Main server launcher"""
    logging.info("🚀 Starting Enterprise Monitor on Ubuntu Server")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup directories
    if not setup_directories():
        sys.exit(1)
    
    # Setup virtual display
    if not setup_display():
        sys.exit(1)
    
    # Set server environment variables
    os.environ['ENTERPRISE_MONITOR_SERVER'] = 'true'
    os.environ['CHROME_NO_SANDBOX'] = 'true'
    
    # Change to project directory
    project_dir = '/opt/enterprise-monitor'
    os.chdir(project_dir)
    
    # Activate virtual environment and run main
    venv_python = os.path.join(project_dir, 'venv', 'bin', 'python')
    
    try:
        logging.info("🔄 Starting main application...")
        subprocess.run([venv_python, 'main.py'], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Application failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logging.info("🛑 Application stopped by user")
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
