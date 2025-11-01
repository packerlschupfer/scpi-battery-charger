#!/bin/bash
# Battery Charger Installation Script for Raspberry Pi

set -e  # Exit on error

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Battery Charger - Installation Script"
echo "OWON SPE6205 + Raspberry Pi"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo -e "${YELLOW}Warning: This doesn't appear to be a Raspberry Pi${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Determine installation directory
if [ -d "/home/pi" ]; then
    INSTALL_DIR="/home/pi/battery-charger"
    SERVICE_USER="pi"
else
    INSTALL_DIR="$HOME/battery-charger"
    SERVICE_USER="$USER"
fi

echo -e "${GREEN}Installation directory: $INSTALL_DIR${NC}"
echo ""

# Check for required system packages
echo "Checking system packages..."
MISSING_PACKAGES=()

for pkg in python3 python3-venv python3-pip; do
    if ! dpkg -l | grep -q "^ii  $pkg "; then
        MISSING_PACKAGES+=($pkg)
    fi
done

if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
    echo -e "${YELLOW}Missing packages: ${MISSING_PACKAGES[*]}${NC}"
    echo "Installing packages (requires sudo)..."
    sudo apt-get update
    sudo apt-get install -y "${MISSING_PACKAGES[@]}"
else
    echo -e "${GREEN}All system packages installed${NC}"
fi

# Copy files to installation directory
echo ""
echo "Copying files to $INSTALL_DIR..."

if [ ! -d "$INSTALL_DIR" ]; then
    mkdir -p "$INSTALL_DIR"
fi

# Copy project files (assuming script is run from project directory)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"

echo -e "${GREEN}Files copied${NC}"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
cd "$INSTALL_DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Install Python packages
echo ""
echo "Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo -e "${GREEN}Python packages installed${NC}"

# Check USB device permissions
echo ""
echo "Checking USB device permissions..."

if [ -e "/dev/ttyUSB0" ]; then
    echo -e "${GREEN}Found /dev/ttyUSB0${NC}"

    # Check if user is in dialout group
    if groups $SERVICE_USER | grep -q "dialout"; then
        echo -e "${GREEN}User $SERVICE_USER is in dialout group${NC}"
    else
        echo -e "${YELLOW}Adding $SERVICE_USER to dialout group...${NC}"
        sudo usermod -a -G dialout $SERVICE_USER
        echo -e "${YELLOW}You must log out and back in for group changes to take effect${NC}"
    fi
else
    echo -e "${YELLOW}Warning: /dev/ttyUSB0 not found. Make sure OWON PSU is connected.${NC}"
fi

# Test PSU connection (optional)
echo ""
read -p "Test connection to OWON PSU now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Testing PSU connection..."
    if source venv/bin/activate && python3 -c "
import sys
sys.path.insert(0, 'src')
from owon_psu import OwonPSU
psu = OwonPSU('/dev/ttyUSB0')
if psu.connect():
    print('✓ Successfully connected to PSU')
    print('  Device:', psu.identify())
    psu.disconnect()
    sys.exit(0)
else:
    print('✗ Failed to connect to PSU')
    sys.exit(1)
"; then
        echo -e "${GREEN}PSU connection test passed${NC}"
    else
        echo -e "${RED}PSU connection test failed${NC}"
        echo "Check:"
        echo "  - OWON PSU is powered on"
        echo "  - USB cable is connected"
        echo "  - /dev/ttyUSB0 exists and has correct permissions"
    fi
fi

# Configure systemd service
echo ""
read -p "Install systemd service? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing systemd service..."

    # Update service file with correct paths
    sed -i "s|/home/pi/battery-charger|$INSTALL_DIR|g" "$INSTALL_DIR/battery-charger.service"
    sed -i "s|User=pi|User=$SERVICE_USER|g" "$INSTALL_DIR/battery-charger.service"

    # Install service
    sudo cp "$INSTALL_DIR/battery-charger.service" /etc/systemd/system/
    sudo systemctl daemon-reload

    echo -e "${GREEN}Systemd service installed${NC}"
    echo ""
    echo "To enable auto-start on boot:"
    echo "  sudo systemctl enable battery-charger"
    echo ""
    echo "To start service now:"
    echo "  sudo systemctl start battery-charger"
    echo ""
    echo "To check status:"
    echo "  sudo systemctl status battery-charger"
    echo ""
    echo "To view logs:"
    echo "  sudo journalctl -u battery-charger -f"
fi

# Check for MQTT broker
echo ""
echo "Checking for MQTT broker..."
if systemctl is-active --quiet mosquitto; then
    echo -e "${GREEN}Mosquitto MQTT broker is running${NC}"
else
    echo -e "${YELLOW}Mosquitto MQTT broker not running${NC}"
    read -p "Install and start mosquitto? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo apt-get install -y mosquitto mosquitto-clients
        sudo systemctl enable mosquitto
        sudo systemctl start mosquitto
        echo -e "${GREEN}Mosquitto installed and started${NC}"
    fi
fi

# Create logs directory
mkdir -p "$INSTALL_DIR/logs"

echo ""
echo "=========================================="
echo -e "${GREEN}Installation Complete!${NC}"
echo "=========================================="
echo ""
echo "Installation directory: $INSTALL_DIR"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit configuration:"
echo "   nano $INSTALL_DIR/config/charging_config.yaml"
echo ""
echo "2. Test manually:"
echo "   cd $INSTALL_DIR"
echo "   source venv/bin/activate"
echo "   python3 src/charger_main.py"
echo ""
echo "3. Monitor MQTT:"
echo "   mosquitto_sub -h localhost -t 'battery-charger/#' -v"
echo ""
echo "4. Install systemd service (if not done):"
echo "   sudo cp battery-charger.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable battery-charger"
echo "   sudo systemctl start battery-charger"
echo ""
echo "5. Check service status:"
echo "   sudo systemctl status battery-charger"
echo "   sudo journalctl -u battery-charger -f"
echo ""
echo "For Home Assistant integration, see:"
echo "   $INSTALL_DIR/docs/HOME_ASSISTANT.md"
echo ""
