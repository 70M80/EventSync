#!/bin/sh
set -e

echo "=== Certbot service started for ${DOMAIN} ==="

mkdir -p /var/www/certbot /etc/letsencrypt/live/${DOMAIN}

if [ ! -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
    echo "=== Requesting initial Let's Encrypt certificate for ${DOMAIN} ==="
    
    certbot certonly --webroot \
        -w /var/www/certbot \
        --email "${CERTBOT_EMAIL}" \
        --agree-tos \
        --no-eff-email \
        -d "${DOMAIN}" \
        --non-interactive \
        --quiet || echo "=== Certificate request failed or already exists ==="
else
    echo "=== Certificate already exists, skipping initial request ==="
fi

echo "=== Starting renewal loop ==="
while :; do
    echo "=== Running certbot renew check at $(date) ==="
    certbot renew --webroot -w /var/www/certbot --quiet || true
    sleep 12h
done