# Docker Deployment Guide

## Prerequisites
- Docker and Docker Compose installed on VPS
- Domain name pointed to your VPS IP

## Quick Deployment Steps

1. **Initial Server Setup**
```bash
# Update system and install Docker
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose -y
```

2. **Project Setup**
```bash
# Clone repository
git clone your_repository_url /opt/django-app
cd /opt/django-app

# Create .env file
cp .env.example .env
```

3. **Configure Environment Variables**
Edit `.env` file:
```
DEBUG=False
ALLOWED_HOSTS=your_domain.com
SECRET_KEY=your_secure_key
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password
```

4. **Deploy**
```bash
# Start services
docker-compose up -d

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

5. **SSL Setup**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your_domain.com
```

## Maintenance Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
```

### Update Application
```bash
git pull
docker-compose build web
docker-compose up -d
```

### Database Backup
```bash
docker-compose exec db pg_dump -U your_db_user your_db_name > backup.sql
```

### Scale Application
```bash
# Scale web service
docker-compose up -d --scale web=3
``` 