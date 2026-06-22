#!/bin/bash
echo "Starting UmbrellaOS..."

kill -9 $(lsof -t -i:8765) 2>/dev/null
kill -9 $(lsof -t -i:3000) 2>/dev/null
pkill -f cloudflared 2>/dev/null
sleep 2

cd /workspaces/UmbrellaOS/files/umbrella-core
source venv/bin/activate
sudo service postgresql start > /dev/null 2>&1
python -m uvicorn main:app --host 0.0.0.0 --port 8765 --reload > /tmp/backend.log 2>&1 &
echo "Waiting for backend..."
sleep 6
tail -5 /tmp/backend.log

cd /workspaces/UmbrellaOS/Dashboard
pnpm dev > /tmp/dashboard.log 2>&1 &
echo "Waiting for dashboard..."
sleep 5
tail -5 /tmp/dashboard.log

echo "Setting port visibility to public..."
gh codespace ports visibility 8765:public 3000:public -c $CODESPACE_NAME
if [ $? -ne 0 ]; then
    echo "WARNING: failed to set port visibility — set manually in Ports tab."
fi

echo "Starting Cloudflare tunnel..."
/workspaces/UmbrellaOS/cloudflared tunnel --url http://localhost:8765 --no-autoupdate > /tmp/cf.log 2>&1 &

CF_URL=""
for i in $(seq 1 20); do
    CF_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /tmp/cf.log 2>/dev/null | head -1)
    [ -n "$CF_URL" ] && break
    sleep 1
done

if [ -n "$CF_URL" ]; then
    echo "Cloudflare tunnel: $CF_URL"

    PLUGIN_CONFIG="/workspaces/UmbrellaOS/minecraft-plugin/src/main/resources/config.yml"
    sed -i "s|core_url:.*|core_url: \"$CF_URL\"|g" "$PLUGIN_CONFIG"
    echo "Plugin config updated"

    BOT_ENV="/workspaces/UmbrellaOS/discord-bot/.env"
    if [ -f "$BOT_ENV" ]; then
        if grep -q "^BACKEND_URL=" "$BOT_ENV"; then
            sed -i "s|^BACKEND_URL=.*|BACKEND_URL=$CF_URL|g" "$BOT_ENV"
        else
            echo "BACKEND_URL=$CF_URL" >> "$BOT_ENV"
        fi
        echo "Bot .env updated"
    fi

    echo ""
    echo "==========================================="
    echo "  TUNNEL URL: $CF_URL"
    echo "  Paste into Pterodactyl:"
    echo "  plugins/UmbrellaOS/config.yml"
    echo "  core_url: \"$CF_URL\""
    echo "==========================================="
    echo ""
else
    echo "WARNING: tunnel URL not detected — check /tmp/cf.log"
fi

cd /workspaces/UmbrellaOS/discord-bot
PYTHONUNBUFFERED=1 python main.py > /tmp/bot.log 2>&1 &
echo "Waiting for bot..."
sleep 3
tail -5 /tmp/bot.log

echo "All services started!"
