#!/bin/bash

# Exit on error
set -e

# Update system
echo "Updating system..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required packages
echo "Installing required packages..."
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    python3-pip \
    python3-dev \
    nginx \
    git

# Create necessary directories
echo "Creating necessary directories..."
sudo mkdir -p /home/seodashboard/logs/nginx
sudo mkdir -p /etc/nginx/ssl-certificates
sudo chown -R $USER:$USER /home/seodashboard/logs/nginx

# Install Docker
echo "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
echo "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

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

echo "Deployment completed successfully!"
echo "Please ensure to:"
echo "1. Update .env.prod with your production settings"
echo "2. Your SSL certificates are properly configured"
echo "3. Your firewall allows ports 80 and 443"
echo "4. DNS records are properly configured for seodashboard.technotch.dev"

# Test Nginx configuration
echo "Testing Nginx configuration..."
docker-compose -f docker-compose.prod.yml exec nginx nginx -t 