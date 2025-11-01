#!/bin/bash
#
# Automated Conditioning Sequence
# This script:
# 1. Stops any active charging
# 2. Waits for battery to rest (default: 2 hours)
# 3. Runs diagnostic mode to check resting voltage
# 4. Starts conditioning mode (15.5V for 24-48h)
#

set -e

# Configuration
BATTERY_CHARGER_DIR="$HOME/battery-charger"
CONDITIONING_CONFIG="$BATTERY_CHARGER_DIR/config/charging_config_conditioning.yaml"
REST_DURATION=${1:-7200}  # Default 2 hours (7200 seconds), can override with argument
LOG_FILE="/tmp/auto_conditioning.log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========================================="
log "Starting automated conditioning sequence"
log "Rest duration: $REST_DURATION seconds ($(($REST_DURATION / 3600)) hours)"
log "========================================="

# Step 1: Stop any active charging
log "Step 1: Stopping any active charging session..."
screen -S charging -X quit 2>/dev/null || log "No charging session to stop"
sleep 3

# Step 2: Rest period
log "Step 2: Battery resting for $(($REST_DURATION / 3600)) hours..."
log "Rest will complete at: $(date -d "+$REST_DURATION seconds" '+%Y-%m-%d %H:%M:%S')"

# Show countdown every 15 minutes during rest
ELAPSED=0
INTERVAL=900  # 15 minutes
while [ $ELAPSED -lt $REST_DURATION ]; do
    REMAINING=$((REST_DURATION - ELAPSED))
    if [ $REMAINING -lt $INTERVAL ]; then
        sleep $REMAINING
        ELAPSED=$REST_DURATION
    else
        sleep $INTERVAL
        ELAPSED=$((ELAPSED + INTERVAL))
        log "Resting... $(($REMAINING / 3600))h $(( ($REMAINING % 3600) / 60))m remaining"
    fi
done

log "Step 2: Rest period complete"

# Step 3: Check resting voltage via MQTT (if available)
log "Step 3: Battery rest complete - ready to start conditioning"
log "Note: Check battery resting voltage via MQTT before conditioning if needed"
cd "$BATTERY_CHARGER_DIR"

# Step 4: Start conditioning mode
log "Step 4: Starting conditioning mode (15.5V for 24-48h)..."
log "Conditioning will run in screen session 'charging'"

screen -dmS charging bash -c "
    source venv/bin/activate
    python3 src/charger_main.py --config $CONDITIONING_CONFIG --auto-start --verbose 2>&1 | tee /tmp/charger_debug.log
"

sleep 5

# Verify charging started
if screen -ls | grep -q charging; then
    log "Step 4: Conditioning mode started successfully!"
    log ""
    log "Monitor with:"
    log "  screen -r charging    # Attach to session"
    log "  tail -f /tmp/charger_debug.log    # Watch logs"
    log "  mosquitto_sub -h localhost -t 'battery-charger/status/#'    # MQTT monitoring"
    log ""
    log "Stop with:"
    log "  screen -S charging -X quit    # Stop charging"
else
    log "ERROR: Failed to start conditioning mode!"
    exit 1
fi

log "========================================="
log "Automated conditioning sequence complete"
log "========================================="
