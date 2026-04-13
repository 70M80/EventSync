#!/bin/sh
set -e

echo "=== Nginx entrypoint started ==="

mkdir -p /etc/letsencrypt/live/${DOMAIN} /var/www/certbot /var/www/vue

if [ ! -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
    echo "⚠️  No certificate found → Starting HTTP-only mode for Let's Encrypt"
    envsubst '${DOMAIN}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
    sed -i '/listen 443 ssl http2;/,/^    }/d' /etc/nginx/nginx.conf
else
    echo "✅ Certificate exists → Starting full HTTPS mode"
    envsubst '${DOMAIN}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
fi

echo "Starting Nginx..."
exec nginx -g 'daemon off;'