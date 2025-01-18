# Deployment Guide for Hostinger VPS

## Prerequisites
- Ubuntu Server (recommended 20.04 LTS or higher)
- Python 3.8+
- PostgreSQL
- Nginx
- Domain name pointed to your VPS IP

## Step 1: Initial Server Setup

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib -y
sudo apt install python3-dev libpq-dev
```

## Step 2: Create Database
```bash
sudo -u postgres psql

CREATE DATABASE your_db_name;
CREATE USER your_db_user WITH PASSWORD 'your_password';
ALTER ROLE your_db_user SET client_encoding TO 'utf8';
ALTER ROLE your_db_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE your_db_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE your_db_name TO your_db_user;
\q
```

## Step 3: Project Setup
```bash
# Create project directory
sudo mkdir -p /var/www/your_project
sudo chown -R $USER:$USER /var/www/your_project

# Clone your repository
git clone your_repository_url /var/www/your_project

# Setup virtual environment
cd /var/www/your_project
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create .env file
cp .env.example .env
# Edit .env with production settings
```

## Step 4: Django Setup
```bash
# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Step 5: Gunicorn Setup
```bash
# Copy Gunicorn configurations
sudo cp deployment/gunicorn/gunicorn.socket /etc/systemd/system/
sudo cp deployment/gunicorn/gunicorn.service /etc/systemd/system/

# Start Gunicorn
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
```

## Step 6: Nginx Setup
```bash
# Copy Nginx configuration
sudo cp deployment/nginx/django.conf /etc/nginx/sites-available/django
sudo ln -s /etc/nginx/sites-available/django /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## Step 7: SSL Setup (Optional but Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your_domain.com
```

## Step 8: Firewall Setup
```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw enable
```

## Environment Variables
Make sure to set these environment variables in your production .env file:
- DEBUG=False
- ALLOWED_HOSTS=your_domain.com
- DATABASE_URL=postgres://your_db_user:your_password@localhost:5432/your_db_name
- SECRET_KEY=your_secure_secret_key

## Maintenance Commands

### Restart Services
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### View Logs
```bash
sudo journalctl -u gunicorn
sudo tail -f /var/log/nginx/error.log
```

### Update Application
```bash
cd /var/www/your_project
source venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
sudo systemctl restart gunicorn
``` 