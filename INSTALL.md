# SEO Dashboard Installation Guide

## System Requirements

- Python 3.8 or higher
- MySQL 5.7+ or PostgreSQL 10+
- Nginx or Apache web server
- Ubuntu 20.04 LTS or higher

## Pre-installation Steps

1. Update system packages:
```bash
sudo apt update
sudo apt upgrade
```

2. Install required system packages:
```bash
sudo apt install python3-pip python3-venv nginx mysql-server
sudo apt install python3-dev default-libmysqlclient-dev build-essential pkg-config
```

3. Create MySQL database and user:
```bash
sudo mysql
mysql> CREATE DATABASE seodash CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
mysql> CREATE USER 'seodash'@'localhost' IDENTIFIED BY 'your_password';
mysql> GRANT ALL PRIVILEGES ON seodash.* TO 'seodash'@'localhost';
mysql> FLUSH PRIVILEGES;
mysql> EXIT;
```

## Installation Process

1. Clone the repository:
```bash
git clone https://github.com/yourusername/seodash.git
cd seodash
```

2. Run the installation wizard:
```bash
python3 install.py
```

3. Follow the prompts to:
   - Create virtual environment
   - Install dependencies
   - Configure database settings
   - Create superuser account
   - Set up file permissions

## Web Server Configuration

### Nginx Configuration

1. Create Nginx configuration file:
```bash
sudo nano /etc/nginx/sites-available/seodash
```

2. Add the following configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/your/seodash;
    }

    location /media/ {
        root /path/to/your/seodash;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

3. Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/seodash /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### Gunicorn Setup

1. Create Gunicorn service file:
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

2. Add the following configuration:
```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/seodash
ExecStart=/path/to/your/seodash/venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/run/gunicorn.sock \
    seo_dashboard.wsgi:application

[Install]
WantedBy=multi-user.target
```

3. Start Gunicorn:
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

## SSL Configuration

1. Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx
```

2. Obtain SSL certificate:
```bash
sudo certbot --nginx -d your-domain.com
```

## Post-Installation Steps

1. Update `.env` file with your domain:
```bash
nano .env
```
- Set `ALLOWED_HOSTS` to your domain
- Configure email settings
- Set `CSRF_TRUSTED_ORIGINS` to your domain

2. Restart services:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

## Maintenance

### Backup Database
```bash
mysqldump -u seodash -p seodash > backup.sql
```

### Update Application
```bash
cd /path/to/your/seodash
source venv/bin/activate
git pull
python manage.py migrate
python manage.py collectstatic
sudo systemctl restart gunicorn
```

## Troubleshooting

1. Check logs:
```bash
sudo tail -f /var/log/nginx/error.log
sudo journalctl -u gunicorn
```

2. Check permissions:
```bash
sudo chown -R www-data:www-data /path/to/your/seodash/media
sudo chown -R www-data:www-data /path/to/your/seodash/staticfiles
```

3. Test Gunicorn directly:
```bash
gunicorn --bind 0.0.0.0:8000 seo_dashboard.wsgi:application
```

## Security Recommendations

1. Enable firewall:
```bash
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

2. Set up regular backups
3. Keep system and packages updated
4. Monitor server resources
5. Configure fail2ban for protection against brute force attacks

## Support

For issues and support:
1. Check the logs
2. Review the troubleshooting section
3. Open an issue on GitHub
4. Contact support at support@your-domain.com 