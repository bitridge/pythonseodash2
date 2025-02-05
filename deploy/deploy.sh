#!/bin/bash

# Exit on error
set -e

echo "Starting deployment of SEO Dashboard..."

# Define paths
PROJECT_PATH="/home/seodashboard/htdocs/seodashboard.technotch.dev/pythonseodash2"
NGINX_AVAILABLE="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"

# Create necessary directories if they don't exist
echo "Setting up directories..."
sudo mkdir -p /home/seodashboard/logs/nginx
sudo chown -R $USER:$USER /home/seodashboard/logs/nginx

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Check for SSL certificates
if [ ! -f /etc/nginx/ssl-certificates/seodashboard.technotch.dev.crt ] || [ ! -f /etc/nginx/ssl-certificates/seodashboard.technotch.dev.key ]; then
    echo "SSL certificates not found!"
    echo "Please ensure your SSL certificates are in place:"
    echo "- /etc/nginx/ssl-certificates/seodashboard.technotch.dev.crt"
    echo "- /etc/nginx/ssl-certificates/seodashboard.technotch.dev.key"
    exit 1
fi

# Create production environment file if it doesn't exist
if [ ! -f .env.prod ]; then
    echo "Creating production environment file..."
    cp .env.prod.example .env.prod
    echo "Please update .env.prod with your production settings"
fi

# Copy Nginx configuration
echo "Setting up Nginx configuration..."
sudo cp deploy/seodashboard.technotch.dev.conf $NGINX_AVAILABLE/seodashboard.technotch.dev.conf
sudo ln -sf $NGINX_AVAILABLE/seodashboard.technotch.dev.conf $NGINX_ENABLED/

# Test Nginx configuration
echo "Testing Nginx configuration..."
sudo nginx -t

# Stop existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down --remove-orphans

# Build and start containers
echo "Building and starting containers..."
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Apply migrations
echo "Applying database migrations..."
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files
echo "Collecting static files..."
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input

# Set correct permissions
echo "Setting correct permissions..."
sudo chown -R www-data:www-data $PROJECT_PATH/static
sudo chown -R www-data:www-data $PROJECT_PATH/media

# Restart Nginx
echo "Restarting Nginx..."
sudo systemctl restart nginx

echo "Deployment completed successfully!"
echo "Please ensure:"
echo "1. Your .env.prod file has the correct settings"
echo "2. Your database connection details are correct"
echo "3. Your domain DNS is properly configured"
echo "4. Your firewall allows ports 80 and 443" 