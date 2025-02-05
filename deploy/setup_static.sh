#!/bin/bash

# Exit on error
set -e

PROJECT_PATH="/home/seodashboard/htdocs/seodashboard.technotch.dev/pythonseodash2"

# Create directories if they don't exist
echo "Creating static and media directories..."
mkdir -p $PROJECT_PATH/static
mkdir -p $PROJECT_PATH/media

# Set correct permissions
echo "Setting permissions..."
sudo chown -R www-data:www-data $PROJECT_PATH/static
sudo chown -R www-data:www-data $PROJECT_PATH/media
sudo chmod -R 755 $PROJECT_PATH/static
sudo chmod -R 755 $PROJECT_PATH/media

echo "Static and media directories setup complete!" 