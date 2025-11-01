# Running Battery Charger as Systemd Service

This guide explains how to set up the battery charger to run automatically as a systemd service.

## Quick Setup

### 1. Stop Current Screen Session

```bash
# Stop the manual screen session
screen -S charging -X quit
```

### 2. Install Service

```bash
cd ~/battery-charger

# Copy service file to systemd
sudo cp battery-charger.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable battery-charger

# Start service now
sudo systemctl start battery-charger
```

### 3. Check Status

```bash
# Check if service is running
sudo systemctl status battery-charger

# View live logs
sudo journalctl -u battery-charger -f

# View recent logs
sudo journalctl -u battery-charger -n 50
```

## Service Control

### Start/Stop/Restart

```bash
# Start service
sudo systemctl start battery-charger

# Stop service
sudo systemctl stop battery-charger

# Restart service
sudo systemctl restart battery-charger

# Reload configuration (without restart)
sudo systemctl reload-or-restart battery-charger
```

### Enable/Disable Auto-Start

```bash
# Enable auto-start on boot
sudo systemctl enable battery-charger

# Disable auto-start on boot
sudo systemctl disable battery-charger

# Check if enabled
systemctl is-enabled battery-charger
```

## Configuration Options

### Auto-Start vs Manual Start

Edit `/etc/systemd/system/battery-charger.service`:

**Option A: Auto-start charging immediately**
```ini
ExecStart=/home/mrnice/battery-charger/venv/bin/python3 /home/mrnice/battery-charger/src/charger_main.py --config /home/mrnice/battery-charger/config/charging_config_banner_44ah.yaml --auto-start
```

**Option B: Wait for MQTT command (recommended for safety)**
```ini
ExecStart=/home/mrnice/battery-charger/venv/bin/python3 /home/mrnice/battery-charger/src/charger_main.py --config /home/mrnice/battery-charger/config/charging_config_banner_44ah.yaml
```

After editing, reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart battery-charger
```

### Change Configuration File

To use a different config (e.g., for different battery):

```bash
# Edit service file
sudo nano /etc/systemd/system/battery-charger.service

# Change this line:
ExecStart=... --config /home/mrnice/battery-charger/config/charging_config_OTHER.yaml

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart battery-charger
```

## Logging

### View Logs

```bash
# Live tail (Ctrl+C to exit)
sudo journalctl -u battery-charger -f

# Last 50 lines
sudo journalctl -u battery-charger -n 50

# Today's logs
sudo journalctl -u battery-charger --since today

# Logs from last hour
sudo journalctl -u battery-charger --since "1 hour ago"

# Logs with timestamps
sudo journalctl -u battery-charger -o short-iso

# All logs (can be very long!)
sudo journalctl -u battery-charger --no-pager
```

### CSV Data Logs

Service also writes CSV logs (not affected by journald):

```bash
# View latest CSV log
tail -f ~/battery-charger/logs/charge_*.csv

# List all log files
ls -lh ~/battery-charger/logs/
```

## MQTT Control

Even when running as service, you can control via MQTT:

```bash
# Start charging
mosquitto_pub -h localhost -t "battery-charger/cmd/start" -m ""

# Stop charging
mosquitto_pub -h localhost -t "battery-charger/cmd/stop" -m ""

# Change mode
mosquitto_pub -h localhost -t "battery-charger/cmd/mode" -m "Conditioning"

# Monitor status
mosquitto_sub -h localhost -t "battery-charger/status/#" -v
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status battery-charger

# Check detailed logs
sudo journalctl -u battery-charger -n 100

# Common issues:
# 1. User/paths wrong - check User= and WorkingDirectory= in service file
# 2. Virtual environment missing - check venv/bin/python3 exists
# 3. USB permissions - check user is in 'dialout' group:
groups mrnice
# If not in dialout:
sudo usermod -a -G dialout mrnice
# Log out and back in
```

### Service Keeps Restarting

```bash
# Check logs for error
sudo journalctl -u battery-charger | grep -i error

# Disable restart temporarily for debugging
sudo systemctl stop battery-charger
# Run manually to see errors:
cd ~/battery-charger
source venv/bin/activate
python3 src/charger_main.py --config config/charging_config_banner_44ah.yaml --verbose
```

### Update After Code Changes

```bash
# After updating code via git pull or rsync:
sudo systemctl restart battery-charger

# Check it restarted correctly:
sudo systemctl status battery-charger
sudo journalctl -u battery-charger -n 20
```

## Service vs Screen Session

| Feature | Systemd Service | Screen Session |
|---------|----------------|----------------|
| Auto-start on boot | ✅ Yes | ❌ No |
| Survives logout | ✅ Yes | ✅ Yes |
| Automatic restart on crash | ✅ Yes | ❌ No |
| System logging (journald) | ✅ Yes | ❌ No |
| Easy debugging | ⚠️ Harder | ✅ Easier |
| Production use | ✅ Recommended | ❌ Not recommended |

**Recommendation:** Use systemd service for normal operation, screen for testing/debugging.

## Uninstall Service

```bash
# Stop and disable
sudo systemctl stop battery-charger
sudo systemctl disable battery-charger

# Remove service file
sudo rm /etc/systemd/system/battery-charger.service

# Reload systemd
sudo systemctl daemon-reload
```

## Example: Full Setup from Scratch

```bash
# 1. Install system (if not already done)
cd ~/battery-charger
python3 -m venv venv
source venv/bin/activate
pip install pyserial paho-mqtt pyyaml

# 2. Test manually first
python3 src/charger_main.py --config config/charging_config_banner_44ah.yaml

# 3. If working, install service
sudo cp battery-charger.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable battery-charger
sudo systemctl start battery-charger

# 4. Monitor
sudo journalctl -u battery-charger -f
```

## Security Note

The service runs with limited privileges:
- `NoNewPrivileges=true` - Cannot gain new privileges
- `PrivateTmp=true` - Private /tmp directory
- `MemoryLimit=512M` - Memory limit
- `CPUQuota=50%` - CPU limit

These settings protect the system from runaway processes.
