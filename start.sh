#!/bin/bash
echo "Starting UmbrellaOS..."

echo "Cleaning up project ports..."

# Target ONLY the specific ports your backend and frontend use
kill -9 $(lsof -t -i:8765) 2>/dev/null
kill -9 $(lsof -t -i:3000) 2>/dev/null

# Target ONLY the exact workspace files for the bot and backend reloader
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "/workspaces/UmbrellaOS/discord-bot/main.py" 2>/dev/null
sleep 2

# 1. Start the PostgreSQL Database and Python Backend
cd /workspaces/UmbrellaOS/files/umbrella-core
source venv/bin/activate
sudo service postgresql start > /dev/null 2>&1
python -m uvicorn main:app --host 0.0.0.0 --port 8765 --reload > /tmp/backend.log 2>&1 &
echo "Waiting for backend..."
sleep 6
tail -5 /tmp/backend.log

# 2. Start the Front-end Dashboard
cd /workspaces/UmbrellaOS/Dashboard
pnpm dev > /tmp/dashboard.log 2>&1 &
echo "Waiting for dashboard..."
sleep 5
tail -5 /tmp/dashboard.log

# 3. Configure GitHub Codespace Network Security Options
echo "Setting port visibility to public..."
gh codespace ports visibility 8765:public 3000:public -c $CODESPACE_NAME 2>/dev/null
if [ $? -ne 0 ]; then
    echo "WARNING: failed to set port visibility — set manually in Ports tab."
fi

pkill -f "python main.py" 2>/dev/null
# 4. Start the Discord Bot
cd /workspaces/UmbrellaOS/discord-bot
PYTHONUNBUFFERED=1 python main.py > /tmp/bot.log 2>&1 &
echo "Waiting for bot..."
sleep 3
tail -5 /tmp/bot.log
echo "All services started safely!"
