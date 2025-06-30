#!/bin/sh

# Exit on any error
set -e

echo "Starting VPN Bot Manager..."

# Wait for network to be available (with timeout)
timeout=30
while ! ping -c 1 google.com &> /dev/null && [ $timeout -gt 0 ]; do
    echo "Waiting for network connection... ($timeout seconds remaining)"
    sleep 2
    timeout=$((timeout - 2))
done

if [ $timeout -le 0 ]; then
    echo "Network connection timeout. Starting bot anyway..."
fi

echo "Network is available. Starting bot..."

# Run the bot
exec python3 main.py