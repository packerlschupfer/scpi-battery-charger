# Complete Installation Guide - Beginner Friendly

This guide walks you through the complete setup from scratch, even if you're new to Raspberry Pi or Linux.

## Table of Contents

1. [What You Need](#what-you-need)
2. [Step 1: Raspberry Pi Setup](#step-1-raspberry-pi-setup)
3. [Step 2: Install the Battery Charger Software](#step-2-install-the-battery-charger-software)
4. [Step 3: Connect the Hardware](#step-3-connect-the-hardware)
5. [Step 4: Configure for Your Battery](#step-4-configure-for-your-battery)
6. [Step 5: First Test Run](#step-5-first-test-run)
7. [Step 6: Install as Auto-Start Service](#step-6-install-as-auto-start-service)
8. [Step 7: Remote Monitoring (Optional)](#step-7-remote-monitoring-optional)
9. [Troubleshooting](#troubleshooting)

---

## What You Need

### Hardware

1. **Raspberry Pi** (any model with USB port)
   - Raspberry Pi 4 recommended (4GB RAM)
   - Raspberry Pi 3 or Zero 2 W also work fine
   - Includes: SD card (16GB+), power supply, case

2. **OWON Power Supply** (one of these models):
   - SPE3102 (30V / 10A / 200W) - for batteries up to 70-80Ah
   - SPE3103 (30V / 10A / 300W) - for batteries up to 70-80Ah
   - SPE6103 (60V / 10A / 300W) - for batteries up to 70-80Ah
   - SPE6205 (60V / 20A / 500W) - for larger batteries (95Ah+)

3. **USB Cable** - USB-A to USB-B (printer cable) to connect PSU to Raspberry Pi

4. **Network Connection** - Ethernet cable OR WiFi (for remote access)

5. **Battery Cables** - Appropriate gauge wire with battery terminals

### Software (we'll install this together)

- Raspberry Pi OS Lite (64-bit recommended)
- Python 3
- MQTT broker (Mosquitto)

---

## Step 1: Raspberry Pi Setup

### 1.1 Download Raspberry Pi Imager

**Windows/Mac/Linux:**
1. Go to: https://www.raspberrypi.com/software/
2. Download "Raspberry Pi Imager"
3. Install and open it

### 1.2 Flash Raspberry Pi OS

1. **Insert SD card** into your computer
2. **Open Raspberry Pi Imager**
3. **Choose Device**: Select your Raspberry Pi model
4. **Choose OS**:
   - Click "Raspberry Pi OS (other)"
   - Select "Raspberry Pi OS Lite (64-bit)" - NO desktop needed!
5. **Choose Storage**: Select your SD card
6. **Settings** (⚙️ gear icon):
   - ✅ **Set hostname**: `chargeberry` (or whatever you like)
   - ✅ **Enable SSH**: Use password authentication
   - ✅ **Set username and password**:
     - Username: `pi` (recommended)
     - Password: (choose a secure password)
   - ✅ **Configure WiFi** (if not using Ethernet):
     - SSID: Your WiFi name
     - Password: Your WiFi password
     - Country: Your country code
   - ✅ **Set locale settings**: Your timezone and keyboard layout
7. **Write** and wait for completion (5-10 minutes)
8. **Eject** SD card safely

### 1.3 Boot Raspberry Pi

1. **Insert SD card** into Raspberry Pi
2. **Connect network cable** (if using Ethernet)
3. **Connect power** - Pi will boot automatically
4. **Wait 2-3 minutes** for first boot

### 1.4 Find Raspberry Pi on Network

**Option A: If you set hostname to `chargeberry`**
```bash
ping chargeberry.local
```

**Option B: Check your router's web interface**
- Look for device named "chargeberry" or "raspberrypi"
- Note the IP address (e.g., 192.168.1.50)

**Option C: Use network scanner**
- Windows: Use "Advanced IP Scanner"
- Mac: Use "LanScan"

### 1.5 Connect via SSH

**Windows (use PuTTY or Windows Terminal):**
```
ssh pi@chargeberry.local
```

**Mac/Linux (use Terminal):**
```bash
ssh pi@chargeberry.local
```

If hostname doesn't work, use IP address:
```bash
ssh pi@192.168.1.50
```

**First time connecting:**
- You'll see "authenticity of host... can't be established"
- Type `yes` and press Enter
- Enter the password you set earlier

**You should now see:**
```
pi@chargeberry:~ $
```

✅ Success! You're connected to your Raspberry Pi!

---

## Step 2: Install the Battery Charger Software

### 2.1 Update System

First, update the Raspberry Pi:

```bash
sudo apt update
sudo apt upgrade -y
```

This takes 5-15 minutes. Wait for it to complete.

### 2.2 Install Required Packages

```bash
sudo apt install -y python3 python3-pip python3-venv git mosquitto mosquitto-clients
```

This installs:
- Python 3 (programming language)
- pip (Python package installer)
- venv (virtual environment)
- git (version control - to download the project)
- mosquitto (MQTT broker for monitoring)
- mosquitto-clients (MQTT testing tools)

### 2.3 Download Battery Charger Project

```bash
cd ~
git clone https://github.com/packerlschupfer/scpi-battery-charger.git battery-charger
cd battery-charger
```

### 2.4 Create Python Virtual Environment

A virtual environment keeps the project's Python packages separate from the system.

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your command prompt:
```
(venv) pi@chargeberry:~/battery-charger $
```

### 2.5 Install Python Dependencies

```bash
pip install pyserial paho-mqtt pyyaml
```

This installs:
- `pyserial` - to communicate with OWON PSU
- `paho-mqtt` - for remote monitoring
- `pyyaml` - to read configuration files

---

## Step 3: Connect the Hardware

### 3.1 Add User to dialout Group

This allows the `pi` user to access USB serial devices:

```bash
sudo usermod -a -G dialout $USER
```

**Important:** You must log out and log back in for this to take effect:

```bash
exit
```

Then reconnect via SSH:
```bash
ssh pi@chargeberry.local
```

### 3.2 Connect OWON PSU

1. **Connect USB cable**: OWON PSU → Raspberry Pi
2. **Power on** the OWON PSU
3. **Check if detected**:

```bash
ls -l /dev/ttyUSB0
```

You should see:
```
crw-rw---- 1 root dialout 188, 0 Nov  1 12:00 /dev/ttyUSB0
```

✅ If you see this, USB connection works!

❌ If you get "No such file or directory":
- Try unplugging and replugging the USB cable
- Try a different USB port
- Check `ls /dev/ttyUSB*` to see if it's on a different number

### 3.3 Test SCPI Communication (Optional but Recommended)

Let's verify we can talk to the PSU:

```bash
cd ~/battery-charger
source venv/bin/activate
python3 << 'EOF'
import serial
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=2)
ser.write(b'*IDN?\n')
response = ser.readline().decode().strip()
print(f"PSU responded: {response}")
ser.close()
EOF
```

You should see something like:
```
PSU responded: OWON,SPE6205,SN123456789,V1.0
```

✅ Great! Communication works!

---

## Step 4: Configure for Your Battery

### 4.1 Choose Configuration Template

Based on your PSU model, copy the appropriate template:

**For SPE3102:**
```bash
cp config/psu_templates/SPE3102_config.yaml config/charging_config.yaml
```

**For SPE3103:**
```bash
cp config/psu_templates/SPE3103_config.yaml config/charging_config.yaml
```

**For SPE6103:**
```bash
cp config/psu_templates/SPE6103_config.yaml config/charging_config.yaml
```

**For SPE6205:**
```bash
cp config/psu_templates/SPE6205_config.yaml config/charging_config.yaml
```

### 4.2 Edit Configuration for Your Battery

```bash
nano config/charging_config.yaml
```

**Nano editor basics:**
- Arrow keys to navigate
- Type to edit
- `Ctrl+O` then `Enter` to save
- `Ctrl+X` to exit

**Change these values for YOUR battery:**

```yaml
battery:
  capacity: 95.0                  # YOUR battery Ah (e.g., 44, 70, 95)
  manufacture_year: 2020          # YOUR battery year
  chemistry: "lead_calcium"       # or "lead_antimony" for old batteries

charging:
  IUoU:
    bulk_current: 9.5             # 0.1 × YOUR battery capacity
                                   # Example: 44Ah → 4.4A
                                   #          70Ah → 7.0A
                                   #          95Ah → 9.5A
```

**For modern batteries (2010+):** Keep default voltages (15.2V absorption)
**For old batteries (pre-2010):** See `CONFIGURATION_SUMMARY.md` for voltage changes

Save with `Ctrl+O`, `Enter`, then exit with `Ctrl+X`.

---

## Step 5: First Test Run

### 5.1 Safety Check

Before connecting the battery:

1. ✅ OWON PSU output is **OFF**
2. ✅ Battery **NOT** connected yet
3. ✅ Fire extinguisher nearby (safety first!)
4. ✅ Ventilated area (batteries produce gas when charging)

### 5.2 Run Manual Test (NO BATTERY YET!)

```bash
cd ~/battery-charger
source venv/bin/activate
python3 src/charger_main.py
```

You should see:
```
INFO - Initializing battery charger...
INFO - Connected to OWON SPE6205
INFO - MQTT client connected
INFO - Ready for charging commands
```

Press `Ctrl+C` to stop.

✅ If you see these messages, software is working!

### 5.3 Monitor MQTT (Open New Terminal)

Open a **second SSH connection** in a new window:

```bash
ssh pi@chargeberry.local
mosquitto_sub -h localhost -t 'battery-charger/#' -v
```

This will show all MQTT messages from the charger.

### 5.4 Connect Battery and Start Charging

**In the first terminal:**

```bash
cd ~/battery-charger
source venv/bin/activate
python3 src/charger_main.py --auto-start
```

**You should see:**
- Voltage measurements
- Current flow starting
- MQTT updates in the second terminal
- PSU display showing voltage/current

**Watch for 5-10 minutes** to ensure:
- Voltage is rising slowly
- Current is stable at configured value
- No error messages
- MQTT updates arriving

Press `Ctrl+C` in BOTH terminals to stop.

---

## Step 6: Install as Auto-Start Service

Once you've verified everything works, install it as a systemd service to start automatically on boot.

### 6.1 Edit Service File

```bash
nano battery-charger.service
```

**Verify these paths are correct** (they should be already):
```ini
WorkingDirectory=/home/pi/battery-charger
ExecStart=/home/pi/battery-charger/venv/bin/python3 /home/pi/battery-charger/src/charger_main.py --config /home/pi/battery-charger/config/charging_config.yaml
```

If your username is **not** `pi`, change `/home/pi/` to `/home/YOUR_USERNAME/`.

Save with `Ctrl+O`, `Enter`, exit with `Ctrl+X`.

### 6.2 Install Service

```bash
sudo cp battery-charger.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable battery-charger
```

### 6.3 Start Service

```bash
sudo systemctl start battery-charger
```

### 6.4 Check Status

```bash
sudo systemctl status battery-charger
```

You should see:
```
● battery-charger.service - Battery Charger Controller
   Loaded: loaded
   Active: active (running)
```

✅ Service is running!

### 6.5 View Logs

```bash
sudo journalctl -u battery-charger -f
```

Press `Ctrl+C` to stop viewing logs.

---

## Step 7: Remote Monitoring (Optional)

### 7.1 Using Command Line

**From any computer on the same network:**

```bash
# Watch all status updates
mosquitto_sub -h chargeberry.local -t 'battery-charger/#' -v

# Check voltage
mosquitto_sub -h chargeberry.local -t 'battery-charger/status/voltage'

# Start charging
mosquitto_pub -h chargeberry.local -t 'battery-charger/cmd/start' -m ''

# Stop charging
mosquitto_pub -h chargeberry.local -t 'battery-charger/cmd/stop' -m ''
```

### 7.2 Home Assistant Integration

See main README.md for Home Assistant configuration examples.

---

## Troubleshooting

### Problem: Can't connect via SSH

**Solutions:**
1. Check Raspberry Pi has power (red LED on)
2. Check network cable is connected (green LED blinking)
3. Try IP address instead of hostname
4. Check your router's device list for the Pi
5. Re-flash SD card and try again

### Problem: /dev/ttyUSB0 not found

**Solutions:**
```bash
# Check all USB devices
ls /dev/ttyUSB*

# Check if it's on a different number
ls /dev/tty*

# Unplug and replug USB cable, then check again
ls -l /dev/ttyUSB0

# Make sure you're in dialout group
groups
# Should show: pi adm dialout ... sudo ...

# If dialout is missing, add it
sudo usermod -a -G dialout $USER
# Then log out and back in
```

### Problem: SCPI communication fails

**Solutions:**
1. Check USB cable (try a different one)
2. Check OWON PSU is powered on
3. Try unplugging and replugging USB
4. Restart Raspberry Pi: `sudo reboot`
5. Check baudrate in config is 115200

### Problem: Service won't start

**Check logs:**
```bash
sudo journalctl -u battery-charger -n 100 --no-pager
```

**Common issues:**
- Path to venv wrong (check username is correct)
- Config file missing (check `ls config/charging_config.yaml`)
- Permission denied on /dev/ttyUSB0 (add to dialout group)

**Test manually first:**
```bash
cd ~/battery-charger
source venv/bin/activate
python3 src/charger_main.py
# Watch for error messages
```

### Problem: MQTT not working

**Check mosquitto is running:**
```bash
sudo systemctl status mosquitto
```

**Restart mosquitto:**
```bash
sudo systemctl restart mosquitto
```

**Test MQTT locally:**
```bash
# Terminal 1:
mosquitto_sub -h localhost -t 'test' -v

# Terminal 2:
mosquitto_pub -h localhost -t 'test' -m 'hello'

# You should see "test hello" in Terminal 1
```

### Problem: Battery not charging

**Checklist:**
1. OWON PSU output is enabled (check front panel)
2. Battery cables connected correctly (red=+, black=-)
3. Battery voltage above 10.5V (measure with multimeter)
4. Config file has correct current setting
5. No error messages in logs

---

## Next Steps

1. ✅ Let it run a complete charge cycle
2. ✅ Monitor via MQTT or logs
3. ✅ Check battery resting voltage after charging (should be 12.6-13.3V)
4. ✅ Set up Home Assistant integration (optional)
5. ✅ Configure email/notifications (optional)
6. ✅ Fine-tune charging parameters if needed

## Getting Help

- **Config issues**: See `CONFIGURATION_SUMMARY.md`
- **Battery chemistry**: See main `README.md`
- **MQTT topics**: See main `README.md`
- **GitHub Issues**: https://github.com/packerlschupfer/scpi-battery-charger/issues

---

**You're done! The battery charger should now be running and accessible remotely via MQTT.**

Happy charging! ⚡🔋
