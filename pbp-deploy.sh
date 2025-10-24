#!/bin/bash
# Deployment script for PWS
# This script runs automatically during deployment

set -e  # Exit on error

echo "=== PWS Deployment Script ==="
echo "Starting deployment for Becathlon..."

# Create necessary directories
echo "Creating directories..."
mkdir -p /tmp/staticfiles
mkdir -p /tmp/media

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

echo "=== Deployment Complete ==="
