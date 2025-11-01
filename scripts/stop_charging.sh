#!/bin/bash
#
# Properly stop battery charger with graceful shutdown
# Sends SIGTERM instead of SIGKILL to allow cleanup
#

set -e

echo "Stopping battery charger..."

# Find the Python process running charger_main.py
PID=$(pgrep -f "charger_main.py" || true)

if [ -z "$PID" ]; then
    echo "Battery charger is not running"
    exit 0
fi

echo "Found charger process (PID: $PID)"
echo "Sending SIGTERM for graceful shutdown..."

# Send SIGTERM (allows cleanup handlers to run)
kill -TERM $PID

# Wait up to 10 seconds for graceful shutdown
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "Charger stopped gracefully"
        exit 0
    fi
    sleep 1
    echo "Waiting for shutdown... ($i/10)"
done

# If still running after 10 seconds, force kill
if ps -p $PID > /dev/null 2>&1; then
    echo "WARNING: Graceful shutdown timeout, forcing..."
    kill -KILL $PID
    echo "Charger force-killed (PSU output may still be ON!)"
    exit 1
fi

echo "Charger stopped"
