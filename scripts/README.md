# Automation Scripts

**English | [Deutsch](README.de.md)**

## stop_charging.sh

**Properly stop the battery charger with graceful shutdown.**

This script sends SIGTERM (instead of SIGKILL) to allow cleanup handlers to run, ensuring the PSU output is turned OFF.

### Usage

```bash
cd ~/battery-charger/scripts
./stop_charging.sh
```

**What it does:**
1. Finds the charger process
2. Sends SIGTERM for graceful shutdown
3. Waits up to 10 seconds for cleanup
4. PSU output is turned OFF safely
5. MQTT and logs are closed properly

**⚠️ DO NOT use `screen -X quit`** - it sends SIGKILL which prevents cleanup!

**Alternative methods:**
```bash
# Via MQTT (if enabled)
mosquitto_pub -h localhost -t 'battery-charger/cmd/stop' -m ''

# Manual (not recommended - use script instead)
pkill -TERM -f charger_main.py
```

---

## auto_conditioning.sh

Automated conditioning sequence that handles the complete workflow:

1. Stops any active charging
2. Lets battery rest (default: 2 hours)
3. Runs diagnostic mode to check resting voltage
4. Starts conditioning mode (15.5V for 24-48h)

### Usage

**Default (2-hour rest):**
```bash
cd ~/battery-charger/scripts
./auto_conditioning.sh
```

**Custom rest duration:**
```bash
# 1 hour rest
./auto_conditioning.sh 3600

# 30 minutes rest (for testing)
./auto_conditioning.sh 1800

# 4 hours rest
./auto_conditioning.sh 14400
```

**Run in background (nohup):**
```bash
nohup ./auto_conditioning.sh &
# Monitor progress:
tail -f /tmp/auto_conditioning.log
```

**Run in screen session:**
```bash
screen -dmS auto_cond ./auto_conditioning.sh
# Monitor progress:
screen -r auto_cond
# Detach: Ctrl+A, D
```

### Monitoring

**Check progress:**
```bash
tail -f /tmp/auto_conditioning.log
```

**Check if conditioning is running:**
```bash
screen -ls | grep charging
```

**Monitor conditioning via MQTT:**
```bash
mosquitto_sub -h localhost -t 'battery-charger/status/#'
```

**Attach to conditioning session:**
```bash
screen -r charging
# Detach: Ctrl+A, D
```

### Stop Conditioning

```bash
screen -S charging -X quit
```

### Example Output

```
[2025-10-31 23:59:00] =========================================
[2025-10-31 23:59:00] Starting automated conditioning sequence
[2025-10-31 23:59:00] Rest duration: 7200 seconds (2 hours)
[2025-10-31 23:59:00] =========================================
[2025-10-31 23:59:00] Step 1: Stopping any active charging session...
[2025-10-31 23:59:03] Step 2: Battery resting for 2 hours...
[2025-10-31 23:59:03] Rest will complete at: 2025-11-01 01:59:03
[2025-11-01 00:14:03] Resting... 1h 45m remaining
[2025-11-01 00:29:03] Resting... 1h 30m remaining
...
[2025-11-01 01:59:03] Step 2: Rest period complete
[2025-11-01 01:59:03] Step 3: Running diagnostic mode to check resting voltage...
[2025-11-01 01:59:13] Step 3: Diagnostic complete (check log above for voltage reading)
[2025-11-01 01:59:13] Step 4: Starting conditioning mode (15.5V for 24-48h)...
[2025-11-01 01:59:18] Step 4: Conditioning mode started successfully!
[2025-11-01 01:59:18] =========================================
[2025-11-01 01:59:18] Automated conditioning sequence complete
[2025-11-01 01:59:18] =========================================
```
