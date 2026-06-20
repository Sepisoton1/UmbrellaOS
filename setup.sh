#!/bin/bash
# setup.sh — run once on each fresh Codespace before start.sh
set -e

CODESPACE_URL_BASE="https://${CODESPACE_NAME}"

echo ""
echo "=== UmbrellaOS Codespace Setup ==="
echo ""

# 1. Start Postgres
echo "[1/5] Starting PostgreSQL..."
sudo service postgresql start > /dev/null 2>&1
sleep 2

# 2. Create DB user/database if they don't exist
echo "[2/5] Ensuring database exists..."
sudo su -c 'su postgres -c "psql -c \"CREATE USER umbrella WITH PASSWORD 'changeme';\"" 2>/dev/null || true'
sudo su -c 'su postgres -c "psql -c \"CREATE DATABASE umbrella_core OWNER umbrella;\"" 2>/dev/null || true'
sudo su -c 'su postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE umbrella_core TO umbrella;\"" 2>/dev/null || true'

# Verify connection
PGPASSWORD=changeme psql -h localhost -U umbrella -d umbrella_core -c "SELECT 1;" > /dev/null 2>&1 \
  && echo "    DB connection OK" \
  || echo "    WARNING: DB connection failed - check postgres logs"

# 3. Recreate backend .env if missing real secrets
echo "[3/5] Checking backend .env..."
ENV_FILE="/workspaces/UmbrellaOS/files/umbrella-core/.env"
if ! grep -q "^DISCORD_BOT_TOKEN=" "$ENV_FILE" 2>/dev/null || grep -q "your_.*_here" "$ENV_FILE" 2>/dev/null; then
  echo ""
  echo "    WARNING: Backend .env is missing or has placeholder values."
  echo "    Please fill in: $ENV_FILE"
  echo "    Required keys:"
  echo "      ADMIN_KEY=umbrella-admin-key-local"
  echo "      DISCORD_CLIENT_ID=..."
  echo "      DISCORD_CLIENT_SECRET=..."
  echo "      DISCORD_BOT_TOKEN=..."
  echo "      INITIAL_ADMIN_DISCORD_ID=986672767971758102"
  echo ""
else
  echo "    Backend .env OK"
fi

# 4. Recreate Dashboard .env.local
echo "[4/5] Writing Dashboard .env.local..."
cat > /workspaces/UmbrellaOS/Dashboard/.env.local << EOF
NEXT_PUBLIC_UMBRELLA_API_URL=https://${CODESPACE_NAME}-8765.app.github.dev/api/v1
NEXT_PUBLIC_UMBRELLA_ADMIN_KEY=umbrella-admin-key-local
EOF
echo "    Dashboard .env.local written"
echo "    Backend URL: ${CODESPACE_URL_BASE}-8765.app.github.dev/api/v1"

# 5. Discord OAuth redirect reminder
echo "[5/5] Manual steps required:"
echo ""
echo "  a) In VS Code Ports tab:"
echo "     - Right-click port 8765 -> Port Visibility -> Public"
echo "     - Right-click port 3000 -> Port Visibility -> Public"
echo ""
echo "  b) In Discord Developer Portal (if this is a NEW Codespace):"
echo "     Add this redirect URI to your OAuth2 app:"
echo "     ${CODESPACE_URL_BASE}-3000.app.github.dev/login"
echo ""
echo "=== Setup complete. Now run: bash start.sh ==="
echo ""
