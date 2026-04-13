#!/bin/sh
set -e

echo "Configuring Nginx..."

envsubst '$DOMAIN' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

echo "Starting Nginx..."

exec nginx -g 'daemon off;'