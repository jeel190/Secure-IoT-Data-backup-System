#!/bin/bash
# =====================================================================
# Cloud VM Deployment Automation Script
# Assignment 18: Secure IoT Data Backup System
# Student: Vasani Jeel | Reg. No: 24UG00241
# Target OS: Ubuntu 22.04 LTS / 24.04 LTS on AWS EC2 / Azure VM
# =====================================================================

set -e

echo "[+] Updating operating system packages..."
sudo apt-get update -y && sudo apt-get upgrade -y

echo "[+] Installing Python 3, pip, nginx, and git..."
sudo apt-get install -y python3 python3-pip python3-venv nginx git curl

echo "[+] Creating application directory..."
APP_DIR="/opt/secure-iot-backup"
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

echo "[+] Copying application code to $APP_DIR..."
cp -r ./* $APP_DIR/
cd $APP_DIR

echo "[+] Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[+] Configuring systemd daemon service..."
sudo bash -c "cat > /etc/systemd/system/iot-backup.service << 'EOF'
[Unit]
Description=Secure IoT Data Backup Flask Service
After=network.target

[Service]
User=$USER
WorkingDirectory=/opt/secure-iot-backup
Environment=\"PATH=/opt/secure-iot-backup/venv/bin\"
ExecStart=/opt/secure-iot-backup/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF"

echo "[+] Starting and enabling systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable iot-backup
sudo systemctl restart iot-backup

echo "[+] Configuring Nginx Reverse Proxy..."
sudo bash -c "cat > /etc/nginx/sites-available/iot-backup << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF"

sudo ln -sf /etc/nginx/sites-available/iot-backup /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo "[+] Deployment completed successfully!"
echo "[+] Application is live on port 80 at http://$(curl -s http://checkip.amazonaws.com || echo 'YOUR_VM_PUBLIC_IP')"
