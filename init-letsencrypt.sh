#!/bin/sh
set -e

# ===== Let's Encrypt Initial Setup =====
# This script should be run ONCE before first deployment.
# It obtains the initial SSL certificate using HTTP-only Nginx,
# then the production Nginx config (with HTTPS) can be used.
#
# Prerequisites:
#   - DNS record for your domain pointing to this server's IP
#   - Ports 80 and 443 open on the firewall
#   - .env file configured with DOMAIN and CERTBOT_EMAIL

echo "========================================="
echo " Let's Encrypt Initial Setup"
echo "========================================="

# Load .env.production
if [ ! -f .env.production ]; then
    echo "Error: .env.production file not found!"
    echo "Copy .env.production.example to .env.production and fill in your values."
    exit 1
fi

set -a
source .env.production
set +a

if [ -z "$DOMAIN" ] || [ -z "$CERTBOT_EMAIL" ]; then
    echo "Error: DOMAIN and CERTBOT_EMAIL must be set in .env.production"
    exit 1
fi

echo "Domain: $DOMAIN"
echo "Email:  $CERTBOT_EMAIL"
echo ""

# ===== Step 1: Start Nginx with HTTP-only config =====
echo "[1/4] Starting Nginx with HTTP-only config for ACME challenge..."

# Override the Nginx command to use the init config
docker compose --env-file .env.production run --rm --no-deps \
    -p 80:80 \
    -v "$(pwd)/nginx/nginx-init.conf:/etc/nginx/nginx.conf:ro" \
    -v webroot:/var/www/certbot \
    --entrypoint /bin/sh nginx \
    -c "nginx -c /etc/nginx/nginx.conf && sleep infinity" &

NGINX_PID=$!
sleep 3

# ===== Step 2: Request certificate =====
echo "[2/4] Requesting Let's Encrypt certificate..."
docker compose --env-file .env.production run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$CERTBOT_EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN"

# ===== Step 3: Stop temporary Nginx =====
echo "[3/4] Stopping temporary Nginx..."
kill $NGINX_PID 2>/dev/null || true
wait $NGINX_PID 2>/dev/null || true

# ===== Step 4: Done =====
echo "[4/4] Certificate obtained successfully!"
echo ""
echo "========================================="
echo " ✅ SSL certificate ready for: $DOMAIN"
echo "========================================="
echo ""
echo "Now start all services with:"
echo "  docker compose --env-file .env.production up -d"
echo ""
echo "Nginx will automatically use the certificate"
echo "and Certbot will handle renewals automatically."