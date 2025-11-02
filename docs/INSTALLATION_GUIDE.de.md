# Vollständiger Installationsleitfaden - Anfängerfreundlich

**[English](INSTALLATION_GUIDE.md) | Deutsch**

Dieser Leitfaden führt Sie durch die komplette Einrichtung von Grund auf, selbst wenn Sie neu bei Raspberry Pi oder Linux sind.

## Inhaltsverzeichnis

1. [Was Sie benötigen](#was-sie-benötigen)
2. [Schritt 1: Raspberry Pi Einrichtung](#schritt-1-raspberry-pi-einrichtung)
3. [Schritt 2: Batterieladegerät-Software installieren](#schritt-2-batterieladegerät-software-installieren)
4. [Schritt 3: Hardware anschließen](#schritt-3-hardware-anschließen)
5. [Schritt 4: Für Ihre Batterie konfigurieren](#schritt-4-für-ihre-batterie-konfigurieren)
6. [Schritt 5: Erster Testlauf](#schritt-5-erster-testlauf)
7. [Schritt 6: Als Auto-Start-Dienst installieren](#schritt-6-als-auto-start-dienst-installieren)
8. [Schritt 7: Fernüberwachung (Optional)](#schritt-7-fernüberwachung-optional)
9. [Fehlerbehebung](#fehlerbehebung)

---

## Was Sie benötigen

### Hardware

1. **Raspberry Pi** (jedes Modell mit USB-Port)
   - Raspberry Pi 4 empfohlen (4GB RAM)
   - Raspberry Pi 3 oder Zero 2 W funktionieren auch
   - Inkl.: SD-Karte (16GB+), Netzteil, Gehäuse

2. **OWON Netzteil** (eines dieser Modelle):
   - SPE3102 (30V / 10A / 200W) - für Batterien bis 70-80Ah
   - SPE3103 (30V / 10A / 300W) - für Batterien bis 70-80Ah
   - SPE6103 (60V / 10A / 300W) - für Batterien bis 70-80Ah
   - SPE6205 (60V / 20A / 500W) - für größere Batterien (95Ah+)

3. **USB-Kabel** - USB-A zu USB-B (Druckerkabel) zur Verbindung Netzteil mit Raspberry Pi

4. **Netzwerkverbindung** - Ethernet-Kabel ODER WiFi (für Fernzugriff)

5. **Batteriekabel** - Kabel mit passender Stärke mit Batterieanschlüssen

### Software (installieren wir zusammen)

- Raspberry Pi OS Lite (64-bit empfohlen)
- Python 3
- MQTT Broker (Mosquitto)

---

## Schritt 1: Raspberry Pi Einrichtung

### 1.1 Raspberry Pi Imager herunterladen

**Windows/Mac/Linux:**
1. Gehen Sie zu: https://www.raspberrypi.com/software/
2. Laden Sie "Raspberry Pi Imager" herunter
3. Installieren und öffnen Sie es

### 1.2 Raspberry Pi OS flashen

1. **SD-Karte einlegen** in Ihren Computer
2. **Raspberry Pi Imager öffnen**
3. **Gerät wählen**: Wählen Sie Ihr Raspberry Pi Modell
4. **Betriebssystem wählen**:
   - Klicken Sie auf "Raspberry Pi OS (other)"
   - Wählen Sie "Raspberry Pi OS Lite (64-bit)" - KEIN Desktop benötigt!
5. **Speicher wählen**: Wählen Sie Ihre SD-Karte
6. **Einstellungen** (⚙️ Zahnrad-Symbol):
   - **Hostname setzen**: `chargeberry` (oder wie Sie möchten)
   - **SSH aktivieren**: Passwort-Authentifizierung verwenden
   - **Benutzername und Passwort setzen**:
     - Benutzername: `pi` (empfohlen)
     - Passwort: (wählen Sie ein sicheres Passwort)
   - **WiFi konfigurieren** (falls nicht Ethernet):
     - SSID: Ihr WiFi-Name
     - Passwort: Ihr WiFi-Passwort
     - Land: Ihr Ländercode
   - **Locale-Einstellungen setzen**: Ihre Zeitzone und Tastaturbelegung
7. **Schreiben** und auf Fertigstellung warten (5-10 Minuten)
8. **SD-Karte sicher auswerfen**

### 1.3 Raspberry Pi booten

1. **SD-Karte einlegen** in Raspberry Pi
2. **Netzwerkkabel anschließen** (falls Ethernet verwendet)
3. **Stromversorgung anschließen** - Pi bootet automatisch
4. **2-3 Minuten warten** für ersten Boot

### 1.4 Raspberry Pi im Netzwerk finden

**Option A: Wenn Sie Hostname auf `chargeberry` gesetzt haben**
```bash
ping chargeberry.local
```

**Option B: Router-Weboberfläche prüfen**
- Suchen Sie nach Gerät namens "chargeberry" oder "raspberrypi"
- Notieren Sie die IP-Adresse (z.B. 192.168.1.50)

**Option C: Netzwerk-Scanner verwenden**
- Windows: "Advanced IP Scanner" verwenden
- Mac: "LanScan" verwenden

### 1.5 Via SSH verbinden

**Windows (PuTTY oder Windows Terminal verwenden):**
```
ssh pi@chargeberry.local
```

**Mac/Linux (Terminal verwenden):**
```bash
ssh pi@chargeberry.local
```

Falls Hostname nicht funktioniert, IP-Adresse verwenden:
```bash
ssh pi@192.168.1.50
```

**Beim ersten Verbinden:**
- Sie sehen "authenticity of host... can't be established"
- Tippen Sie `yes` und drücken Enter
- Geben Sie das zuvor gesetzte Passwort ein

**Sie sollten jetzt sehen:**
```
pi@chargeberry:~ $
```

✅ Erfolg! Sie sind mit Ihrem Raspberry Pi verbunden!

---

## Schritt 2: Batterieladegerät-Software installieren

### 2.1 System aktualisieren

Zuerst Raspberry Pi aktualisieren:

```bash
sudo apt update
sudo apt upgrade -y
```

Dies dauert 5-15 Minuten. Warten Sie bis zur Fertigstellung.

### 2.2 Erforderliche Pakete installieren

```bash
sudo apt install -y python3 python3-serial python3-paho-mqtt python3-yaml git mosquitto mosquitto-clients
```

Dies installiert:
- Python 3 (Programmiersprache)
- python3-serial (für OWON-Kommunikation)
- python3-paho-mqtt (für MQTT)
- python3-yaml (zum Lesen von Konfigurationsdateien)
- git (Versionskontrolle - zum Herunterladen des Projekts)
- mosquitto (MQTT Broker für Überwachung)
- mosquitto-clients (MQTT Test-Tools)

### 2.3 Batterieladegerät-Projekt herunterladen

```bash
cd ~
git clone https://github.com/packerlschupfer/scpi-battery-charger.git battery-charger
cd battery-charger
```

---

## Schritt 3: Hardware anschließen

### 3.1 Benutzer zur dialout-Gruppe hinzufügen

Dies erlaubt dem `pi`-Benutzer Zugriff auf USB-Seriell-Geräte:

```bash
sudo usermod -a -G dialout $USER
```

**Wichtig:** Sie müssen sich ab- und wieder anmelden damit dies wirksam wird:

```bash
exit
```

Dann erneut via SSH verbinden:
```bash
ssh pi@chargeberry.local
```

### 3.2 OWON Netzteil anschließen

1. **USB-Kabel anschließen**: OWON Netzteil → Raspberry Pi
2. **OWON Netzteil einschalten**
3. **Prüfen ob erkannt**:

```bash
ls -l /dev/ttyUSB0
```

Sie sollten sehen:
```
crw-rw---- 1 root dialout 188, 0 Nov  1 12:00 /dev/ttyUSB0
```

✅ Wenn Sie dies sehen, funktioniert die USB-Verbindung!

❌ Falls Sie "No such file or directory" erhalten:
- Versuchen Sie USB-Kabel ab- und wieder anzustecken
- Versuchen Sie einen anderen USB-Port
- Prüfen Sie `ls /dev/ttyUSB*` ob es unter anderer Nummer ist

### 3.3 SCPI-Kommunikation testen (Optional aber empfohlen)

Überprüfen wir ob wir mit dem Netzteil kommunizieren können:

```bash
cd ~/battery-charger
python3 << 'EOF'
import serial
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=2)
ser.write(b'*IDN?\n')
response = ser.readline().decode().strip()
print(f"Netzteil antwortete: {response}")
ser.close()
EOF
```

Sie sollten etwas sehen wie:
```
Netzteil antwortete: OWON,SPE6205,SN123456789,V1.0
```

✅ Großartig! Kommunikation funktioniert!

---

## Schritt 4: Für Ihre Batterie konfigurieren

### 4.1 Konfigurationsvorlage wählen

Basierend auf Ihrem Netzteil-Modell, kopieren Sie die passende Vorlage:

**Für SPE3102:**
```bash
cp config/psu_templates/SPE3102_config.yaml config/charging_config.yaml
```

**Für SPE3103:**
```bash
cp config/psu_templates/SPE3103_config.yaml config/charging_config.yaml
```

**Für SPE6103:**
```bash
cp config/psu_templates/SPE6103_config.yaml config/charging_config.yaml
```

**Für SPE6205:**
```bash
cp config/psu_templates/SPE6205_config.yaml config/charging_config.yaml
```

### 4.2 Konfiguration für Ihre Batterie bearbeiten

```bash
nano config/charging_config.yaml
```

**Nano Editor Grundlagen:**
- Pfeiltasten zum Navigieren
- Tippen zum Bearbeiten
- `Strg+O` dann `Enter` zum Speichern
- `Strg+X` zum Beenden

**Wichtige Einstellungen zum Bearbeiten:**

```yaml
# Batterie-Spezifikationen
battery:
  type: "lead_calcium_flooded"    # Für moderne Batterie (2010+)
  nominal_voltage: 12.0           # V - Ihre Batteriespannung
  capacity: 95.0                  # Ah - IHRE BATTERIEKAPAZITÄT HIER
  chemistry: "lead_calcium"       # Oder "lead_antimony" für alte Batterien
  manufacture_year: 2015          # Ungefähres Herstellungsjahr

# Ladekonfiguration
charging:
  IUoU:
    bulk_current: 9.5             # A - C/10 Rate (Kapazität / 10)
                                   # Für 95Ah: 9.5A
                                   # Für 50Ah: 5.0A
                                   # Für 200Ah: 20.0A (falls Netzteil unterstützt)
    
    absorption_voltage: 15.2      # V - KRITISCH!
                                   # Moderne Blei-Kalzium: 15.2V (geschlossen) oder 16.2V (Nasszelle)
                                   # Alte Blei-Antimon: 14.4V
    
    float_voltage: 13.8           # V - Erhaltungsspannung
    absorption_current_threshold: 1.0  # A - Wann zu Float wechseln
```

**Wichtig:**
- **capacity**: Setzen Sie auf Ihre Batterie-Ah-Zahl (steht auf Etikett)
- **bulk_current**: Setzen Sie auf Kapazität / 10 (C/10 Rate ist sicher)
- **absorption_voltage**: 
  - **15.2V** für moderne geschlossene Batterien (2010+)
  - **16.2V** für moderne Nasszellen (2010+)
  - **14.4V** für alte Batterien (vor 2010)

Siehe [BATTERY_TYPES.md](BATTERY_TYPES.de.md) für Details zur Batterietyp-Identifikation.

Nach Bearbeitung:
- `Strg+O` drücken, dann `Enter` (speichern)
- `Strg+X` (beenden)

---

## Schritt 5: Erster Testlauf

### 5.1 KRITISCH: Sicherheitsprüfungen vor dem Start

**BEVOR** Sie den Charger starten:

1. ✅ Batterie ist ANgeschlossen an Netzteil
2. ✅ Korrekte Polarität (+ zu +, - zu -)
3. ✅ Batteriekabel haben passende Stärke (mindestens 2.5mm² für 10A)
4. ✅ Netzteilausgang ist AUS (nicht manuell eingeschaltet)
5. ✅ Gut belüfteter Bereich (Batterien können gasen)
6. ✅ Konfiguration überprüft (richtige Spannung für Ihren Batterietyp!)

### 5.2 Charger manuell starten

```bash
cd ~/battery-charger
python3 src/charger_main.py --auto-start
```

**Was Sie sehen sollten:**

```
[INFO] Batterieladegerät startet...
[INFO] OWON SPE6205 verbunden: SN123456789
[INFO] Batteriespannung: 12.45V
[INFO] Lademodus: IUoU
[INFO] Laden startet automatisch...
[INFO] Stufe: Bulk | Spannung: 12.52V | Strom: 9.48A | Fortschritt: 5%
```

✅ **Erfolg!** Der Charger läuft!

### 5.3 Überwachen Sie den ersten Ladevorgang

Lassen Sie das Terminal offen und beobachten Sie 10-15 Minuten:

**Normale Anzeichen:**
- Spannung steigt allmählich (12.0V → 14.0V → 15.2V)
- Strom bleibt konstant während Bulk-Phase (~9.5A)
- Fortschritt erhöht sich
- Keine Fehlermeldungen

**Warnsignale - STOPPEN wenn Sie sehen:**
- Batterie wird SEHR heiß (>45°C)
- Übermäßige Gasung (spritzende Säure)
- Spannung steigt zu schnell (>1V in 5 Minuten)
- Fehlermeldungen über Sicherheitsgrenzen

**Zum Stoppen:**
- Drücken Sie `Strg+C`
- Oder in anderem Terminal: `mosquitto_pub -h localhost -t "battery-charger/cmd/stop" -m ""`

### 5.4 Über MQTT überwachen (in neuem Terminal/Fenster)

Öffnen Sie ein neues SSH-Fenster und führen Sie aus:

```bash
mosquitto_sub -h localhost -t "battery-charger/status/#" -v
```

Sie sehen Live-Updates:
```
battery-charger/status/voltage 12.52
battery-charger/status/current 9.48
battery-charger/status/progress 5
battery-charger/status/stage bulk
```

Dies ist wie Sie remote überwachen!

---

## Schritt 6: Als Auto-Start-Dienst installieren

Wenn der Testlauf erfolgreich war, richten wir Auto-Start ein.

### 6.1 Stoppen Sie den manuellen Lauf

Wenn der Charger noch läuft:
```bash
# Drücken Sie Strg+C im Charger-Terminal
```

### 6.2 Systemd-Dienst installieren

```bash
cd ~/battery-charger
sudo cp battery-charger.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### 6.3 Dienst aktivieren und starten

```bash
# Aktivieren (startet bei jedem Boot)
sudo systemctl enable battery-charger

# Jetzt starten
sudo systemctl start battery-charger
```

### 6.4 Überprüfen ob es läuft

```bash
sudo systemctl status battery-charger
```

Sie sollten sehen:
```
● battery-charger.service - SCPI Battery Charger
   Loaded: loaded (/etc/systemd/system/battery-charger.service; enabled)
   Active: active (running) since...
```

✅ Dienst läuft und wird automatisch bei jedem Neustart starten!

### 6.5 Logs ansehen

```bash
# Live-Logs ansehen
sudo journalctl -u battery-charger -f

# Letzte 50 Zeilen
sudo journalctl -u battery-charger -n 50
```

Zum Beenden von Live-Logs: `Strg+C`

---

## Schritt 7: Fernüberwachung (Optional)

### 7.1 Home Assistant einrichten

Falls Sie Home Assistant haben, fügen Sie zu `configuration.yaml` hinzu:

```yaml
mqtt:
  sensor:
    - name: "Batteriespannung"
      state_topic: "battery-charger/status/voltage"
      unit_of_measurement: "V"
      device_class: voltage

    - name: "Batteriestrom"
      state_topic: "battery-charger/status/current"
      unit_of_measurement: "A"
      device_class: current

    - name: "Ladefortschritt"
      state_topic: "battery-charger/status/progress"
      unit_of_measurement: "%"

  switch:
    - name: "Batterieladegerät"
      command_topic: "battery-charger/cmd/start"
      state_topic: "battery-charger/status/state"
      payload_on: ""
      state_on: "charging"
      state_off: "idle"
```

Siehe [HOME_ASSISTANT.md](HOME_ASSISTANT.md) (Englisch) für vollständige Integration.

### 7.2 MQTT von Ihrem Computer

**Von Windows/Mac/Linux:**

Installieren Sie einen MQTT-Client wie MQTT Explorer:
- Herunterladen: http://mqtt-explorer.com/
- Verbinden zu: `chargeberry.local` (oder IP-Adresse)
- Port: 1883
- Sehen Sie alle `battery-charger/#` Topics

**Von Kommandozeile:**

```bash
# Alle Status-Updates sehen
mosquitto_sub -h chargeberry.local -t "battery-charger/#" -v

# Laden starten
mosquitto_pub -h chargeberry.local -t "battery-charger/cmd/start" -m ""

# Laden stoppen
mosquitto_pub -h chargeberry.local -t "battery-charger/cmd/stop" -m ""
```

---

## Fehlerbehebung

### Problem: Kann Raspberry Pi nicht finden

**Lösung:**
1. Prüfen Sie grüne LED blinkt am Pi (Aktivität)
2. Prüfen Sie Router-Weboberfläche für verbundene Geräte
3. Versuchen Sie Ethernet statt WiFi
4. Warten Sie 5 Minuten nach erstem Boot
5. Versuchen Sie `raspberrypi.local` statt `chargeberry.local`

### Problem: "Permission denied" beim USB-Zugriff

**Lösung:**
```bash
# Gruppen prüfen
groups

# Sollte "dialout" beinhalten
# Falls nicht:
sudo usermod -a -G dialout $USER

# MUSS ab- und wieder anmelden:
exit
# Dann erneut via SSH verbinden
```

### Problem: OWON reagiert nicht

**Lösung:**
1. USB-Kabel ab- und wieder anstecken
2. OWON Netzteil aus- und einschalten
3. Prüfen `/dev/ttyUSB*`: `ls -l /dev/ttyUSB*`
4. Versuchen Sie `/dev/ttyUSB1` falls mehrere Geräte
5. Anderes USB-Kabel versuchen (einige sind nur für Stromversorgung)

### Problem: Dienst startet nicht

**Lösung:**
```bash
# Detaillierte Fehler sehen
sudo journalctl -u battery-charger -n 100

# Häufige Probleme:
# - Konfig-Datei-Fehler: Überprüfen Sie charging_config.yaml Syntax
# - USB-Berechtigung: Prüfen Sie dialout-Gruppe
# - Port falsch: Ändern Sie port in Konfig zu /dev/ttyUSB1
```

### Problem: Batterie lädt nicht vollständig

**Lösung:**
1. Prüfen Sie `absorption_voltage` in Konfig:
   - Moderne Batterien (2010+): Benötigen 15.2V (geschlossen) oder 16.2V (Nasszelle)
   - Alte Batterien (vor 2010): 14.4V ist korrekt
2. Siehe [BATTERY_TYPES.md](BATTERY_TYPES.de.md) für Identifikation
3. Erhöhen Sie `absorption_timeout` falls zu kurz (Standard 2h)

### Problem: Batterie wird zu heiß

**Lösung:**
1. **SOFORT LADEN STOPPEN:**
   ```bash
   mosquitto_pub -h localhost -t "battery-charger/cmd/stop" -m ""
   ```
2. Ladestrom reduzieren (z.B. von 9.5A zu 5.0A)
3. Belüftung verbessern
4. Prüfen Sie auf defekte Batterie

### Problem: Übermäßige Gasung

**Lösung:**
- Zu hohe Spannung für Ihren Batterietyp
- Reduzieren Sie `absorption_voltage`:
  - Falls bei 16.2V: Versuchen Sie 15.2V
  - Falls bei 15.2V: Versuchen Sie 14.4V (alte Batterie?)
- Siehe [BATTERY_TYPES.md](BATTERY_TYPES.de.md)

### Problem: MQTT verbindet nicht

**Lösung:**
```bash
# Mosquitto läuft prüfen
sudo systemctl status mosquitto

# Falls gestoppt:
sudo systemctl start mosquitto
sudo systemctl enable mosquitto

# Firewall prüfen (falls vorhanden):
sudo ufw allow 1883/tcp
```

---

## Nächste Schritte

✅ **Installation abgeschlossen!**

**Weiterführende Lektüre:**
- [CHARGING_MODES.md](CHARGING_MODES.de.md) - Verstehen Sie verschiedene Lademodi
- [BATTERY_TYPES.md](BATTERY_TYPES.de.md) - Identifizieren Sie Ihren Batterietyp
- [MQTT_API.md](MQTT_API.md) - Vollständige MQTT-Befehle (Englisch)
- [HOME_ASSISTANT.md](HOME_ASSISTANT.md) - Home Assistant einrichten (Englisch)

**Empfohlene Praxis:**
1. **Ersten Ladezyklus überwachen** - Beobachten Sie Spannung/Strom/Temperatur
2. **Logs überprüfen** - `sudo journalctl -u battery-charger -f`
3. **Ruhespannung testen** - Nach Ladung 24h warten, sollte 12.7-12.8V sein
4. **Batteriegesundheit verfolgen** - Siehe `logs/battery_history.json`

**Viel Erfolg mit Ihrem Batterieladegerät!**

Für Unterstützung:
- GitHub Issues: https://github.com/packerlschupfer/scpi-battery-charger/issues
- Microcharge Forum: https://www.microcharge.de/forum/
