# SCPI Batterieladegerät - Raspberry Pi + OWON SPE Serie

**[English](README.md) | Deutsch**

Professionelle intelligente Batterieladegerät-Steuerung für **OWON SPE Serie** programmierbare Netzteile auf Raspberry Pi.

**Unterstützte Modelle**: SPE3102, SPE3103, SPE6103, SPE6205 (und wahrscheinlich andere SCPI-kompatible Netzteile)

**Headless-Betrieb - vollständig über MQTT steuerbar und fernüberwachbar.**

## Funktionen

### Grundfunktionen
- **OWON SPE Serie Support** - Vollständige SCPI-Steuerung (SPE3102/3103/6103/6205)
- **Mehrere Lademodi** - IUoU (3-Stufen), CV, Puls, Erhaltungsladung
- **MQTT Integration** - Vollständige Überwachung und Steuerung
- **Energiebilanzierung** - Ah/Wh abgegeben und gespeichert (Coulomb-Zählung)
- **Sicherheitsüberwachung** - Mehrschichtiger Schutz mit automatischer Abschaltung
- **Datenprotokollierung** - CSV-Protokolle mit vollständigem Ladeverlauf

### Erweiterte Funktionen
- **26 Batterieprofile** - Vorkonfiguriert für 2V/6V/12V/24V Batterien (geschlossen & offen)
- **Batterieprofil-Umschaltung** - Batterie über MQTT wechseln ohne Konfig-Bearbeitung
- **Lade-Zeitplanung** - Ladevorgang mit Startzeit und Zeitbegrenzung planen
- **Batterieverlauf-Verfolgung** - Ladezyklen, Kapazität und Gesundheit über Zeit verfolgen
- **Fehlerwiederherstellung** - Automatische Wiederverbindung von Netzteil und MQTT
- **Multi-Spannungs-Unterstützung** - 0,01V bis 60V (2V Zellen bis 48V Batteriepacks)
- **Spannungsplateau-Erkennung** - Auto-Stopp für Hochspannungs-Nasszellenladung
- **Leistungsüberwachung** - Echtzeit V/A/W Messungen
- **Temperatursensor** - Optionale DS18B20 Unterstützung für Batterietemperatur
- **Ladeeffizienz-Verfolgung** - Berücksichtigt 17% Verluste (Wärme/Gas)
- **Verbesserte Fortschrittsberechnung** - Sanftere 0→70%→95%→100% Progression
- **Systemd Service** - Auto-Start, Watchdog, automatischer Neustart

### Integration
- **Home Assistant** - Vollständige Integration mit Sensoren und Schaltern
- **Fernsteuerung** - MQTT-Steuerung von jedem Client
- **Web-Dashboards** - Kompatibel mit Node-RED, Grafana, etc.
- **SSH-Zugriff** - Vollständiges Linux-Debugging und -Überwachung

## KRITISCH: Batterietyp-Konfiguration

**Moderne Batterien benötigen ANDERE Spannungen als alte Batterien!**

Dieses Projekt enthält **ZWEI Konfigurationen**:

1. **Blei-Kalzium (Ca/Ca)** - Moderne Batterien (ab 2010)
   - Verwendet **15,2V** zum Laden
   - Standardkonfiguration
   - Die meisten Autobatterien seit 2010

2. **Blei-Antimon (Sb)** - Legacy Batterien (vor 2010)
   - Verwendet **14,4V** zum Laden
   - Separate Konfigurationsdatei
   - Ältere wartbare Batterien

### Wie Sie Ihre Batterie prüfen

**Schnellprüfung:** Wann wurde Ihre Batterie hergestellt?
- **2010 oder später** → Standard-Konfig verwenden (Blei-Kalzium)
- **Vor 2010** → `charging_config_lead_antimony.yaml` verwenden

**Etikett-Prüfung:** Suchen Sie nach diesen Kennzeichnungen:
- "Calcium", "Ca/Ca", "Wartungsfrei" → Blei-Kalzium (15,2V)
- "Sb", "Antimon", abnehmbare Kappen → Blei-Antimon (14,4V)

**Vollständiger Leitfaden:** Siehe [docs/BATTERY_TYPES.md](docs/BATTERY_TYPES.md) (Englisch) für detaillierte Identifikation

### Warum das wichtig ist

Falsche Spannungen verwenden:
- **14,4V bei Blei-Kalzium** → Batterie lädt nie vollständig → vorzeitiger Ausfall
- **15,2V bei Blei-Antimon** → Übermäßige Gasung → Wasserverlust

**Die meisten "toten" Batterien brauchen nur die richtige Ladespannung!**

### Konfigurationsdateien

```bash
# Moderne Blei-Kalzium Batterie (STANDARD)
config/charging_config.yaml                    # 15,2V Ladung

# Legacy Blei-Antimon Batterie
config/charging_config_lead_antimony.yaml      # 14,4V Ladung

# Um Legacy-Konfig zu verwenden:
python3 src/charger_main.py --config config/charging_config_lead_antimony.yaml
```

**Technische Referenzen:**
- [Deutsches Batterie-Technik-Wiki](https://wiki.w311.info/index.php?title=Batterie_Heute) - Vollständige technische Spezifikationen
- [Microcharge Forum: Hochspannungsladung](https://www.microcharge.de/forum/forum/thread/847-hochspannungsladung-von-bleiakkus) - Experten-Lademethoden
- [OWON SPE/SP/SPS Programmierhandbuch](https://files.owon.com.cn/software/Application/SP_and_SPE_SPS_programming_manual.pdf) - Offizielle SCPI-Befehlsreferenz

Diese Quellen erklären:
- Unterschiede zwischen Blei-Kalzium und Blei-Antimon Chemie
- Korrekte Ladespannungen (Ladeschlussspannung: 17-17,5V für Nasszellen)
- Traditionelle Konstantstrom-Methode (150 Jahre bewährt)
- Ladezustand-Spannungstabellen
- 12,5V kritische Schwelle (80% SOC - sofort nachladen)
- Ladeeffizienz und Verluste

---

## Hardware-Aufbau

```
OWON SPE Serie USB → Raspberry Pi USB-Port (/dev/ttyUSB0)
                        ↓
                   Ethernet/WiFi
                        ↓
                    MQTT Broker
                        ↓
              Home Assistant / Dashboard
```

### Das richtige Netzteil wählen

| Modell | Spannung | Strom | Leistung | Am besten für |
|-------|---------|---------|-------|----------|
| **SPE3102** | 30V | 10A | 200W | Batterien bis 70-80Ah (nur 12V) |
| **SPE3103** | 30V | 10A | 300W | Batterien bis 70-80Ah (nur 12V) |
| **SPE6103** | 60V | 10A | 300W | Batterien bis 70-80Ah (12V, 24V, 48V) |
| **SPE6205** | 60V | 20A | 500W | Batterien bis 200Ah+ (12V, 24V, 48V) |

**Konfigurationsvorlagen** sind in `config/psu_templates/` für jedes Modell verfügbar.

Siehe `config/psu_templates/README.md` für detaillierten Netzteil-Auswahlführer.

## Schnellstart

**Neu bei Raspberry Pi oder Linux?** → Siehe **[Vollständiger Installationsführer](docs/INSTALLATION_GUIDE.md)** (Englisch) für Schritt-für-Schritt-Anleitung!

**Erfahrene Benutzer:**

```bash
# 1. Abhängigkeiten installieren
sudo apt update
sudo apt install python3 python3-serial python3-paho-mqtt python3-yaml git mosquitto mosquitto-clients

# 2. Projekt klonen
cd ~
git clone https://github.com/packerlschupfer/scpi-battery-charger.git battery-charger
cd battery-charger

# 3. Benutzer zur dialout-Gruppe hinzufügen (für USB-Zugriff)
sudo usermod -a -G dialout $USER
# Aus- und wieder einloggen damit dies wirksam wird

# 4. Netzteil-Vorlage wählen und für Ihre Batterie konfigurieren
cp config/psu_templates/SPE6205_config.yaml config/charging_config.yaml
nano config/charging_config.yaml  # Batteriekapazität und Strom bearbeiten

# 5. Zuerst manuell testen
python3 src/charger_main.py --auto-start

# 6. Als systemd-Dienst installieren (nach dem Testen!)
sudo cp battery-charger.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable battery-charger
sudo systemctl start battery-charger
```

## Konfiguration

`config/charging_config.yaml` bearbeiten:

```yaml
# Netzteil
power_supply:
  model: "OWON SPE6205"
  port: "/dev/ttyUSB0"
  baudrate: 115200
  max_voltage: 60.0  # SPE6205: 60V max (0,01-60V Bereich)
  max_current: 20.0  # SPE6205: 20A max (0,001-20A Bereich)

# Batterie
battery:
  type: "lead_calcium_flooded"  # Moderne Batterie (ab 2010)
  nominal_voltage: 12.0         # V
  capacity: 95.0                # Ah
  chemistry: "lead_calcium"     # Ca/Ca Elektroden
  manufacture_year: 2015        # Ungefähr (an Ihre Batterie anpassen)

# Ladekonfiguration
charging:
  default_mode: "IUoU"
  IUoU:
    bulk_current: 9.5             # A - 0,1C für 95Ah (C/10 Rate)
    absorption_voltage: 15.2      # V - Blei-Kalzium braucht 15-15,4V!
    float_voltage: 13.8           # V
    absorption_current_threshold: 1.0
    enable_float: true

# Sicherheitsgrenzen
safety:
  absolute_max_voltage: 16.5  # Sicher für Blei-Kalzium
  absolute_max_current: 20.0  # Hardware-Limit
  max_charging_duration: 43200  # 12 Stunden

# MQTT
mqtt:
  enabled: true
  broker: "localhost"
  port: 1883
  base_topic: "battery-charger"
  update_interval: 5.0  # Sekunden
```

## MQTT Topics

### Status (Alle 5 Sekunden veröffentlicht)

```
battery-charger/status/online         # "true" / "false"
battery-charger/status/voltage        # 13.45 (V)
battery-charger/status/current        # 4.23 (A)
battery-charger/status/power          # 56.79 (W)
battery-charger/status/mode           # "IUoU"
battery-charger/status/state          # "charging" / "idle" / "completed"
battery-charger/status/stage          # "bulk" / "absorption" / "float"
battery-charger/status/elapsed        # 3600 (Sekunden)
battery-charger/status/progress       # 75 (%)

# Energiebilanzierung (Coulomb-Zählung)
battery-charger/status/ah_delivered   # 12.345 (Ah vom Netzteil)
battery-charger/status/wh_delivered   # 175.23 (Wh verbrauchte Energie)
battery-charger/status/ah_stored      # 10.246 (Ah in Batterie gespeichert, 83% Effizienz)

# Vollständiger JSON-Status
battery-charger/status/json           # Vollständiger Status als JSON
```

### Befehle (Abonniert)

```
battery-charger/cmd/start             # Payload: "" (Laden starten)
battery-charger/cmd/stop              # Payload: "" (Laden stoppen)
battery-charger/cmd/mode              # Payload: "IUoU" / "CV" / "Pulse" / "Trickle"
battery-charger/cmd/current           # Payload: "5.0" (Strom in A setzen)
battery-charger/cmd/profile           # Payload: "12v_sealed_20ah" (Batterieprofil wechseln)

# Lade-Zeitplanung
battery-charger/cmd/schedule          # Payload: JSON {"start_time": "14:30", "duration": "2h", "profile": "lucas_44ah"}
battery-charger/cmd/schedule/cancel   # Payload: "" (geplanten Ladevorgang abbrechen)
```

**Batterieprofil-Beispiele:**
- `12v_sealed_20ah` - 12V 20Ah geschlossene/AGM Batterie
- `12v_flooded_75ah` - 12V 75Ah Nasszellen-Batterie
- `6v_flooded_200ah` - 6V 200Ah Golfwagen-Batterie
- `2v_sealed_100ah` - 2V 100Ah Industrie-Zelle
- `24v_battery` - 24V Batteriepack
- `lucas_44ah` - Lucas Premium LP063 44Ah (spezifische Batterie)

**26 Profile verfügbar** - Siehe `config/` Verzeichnis oder [NEW_FEATURES.md](docs/NEW_FEATURES.md) (Englisch)

## Home Assistant Integration

Zu `configuration.yaml` hinzufügen:

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

    - name: "Ladezustand"
      state_topic: "battery-charger/status/state"

    - name: "Ladefortschritt"
      state_topic: "battery-charger/status/progress"
      unit_of_measurement: "%"

  switch:
    - name: "Batterieladegerät"
      command_topic: "battery-charger/cmd/start"
      state_topic: "battery-charger/status/state"
      payload_on: ""
      payload_off: ""
      state_on: "charging"
      state_off: "idle"
```

## Überwachung

### Via MQTT Kommandozeile

```bash
# Alle Topics abonnieren
mosquitto_sub -h localhost -t "battery-charger/#" -v

# Laden starten
mosquitto_pub -h localhost -t "battery-charger/cmd/start" -m ""

# Laden stoppen
mosquitto_pub -h localhost -t "battery-charger/cmd/stop" -m ""

# Modus ändern
mosquitto_pub -h localhost -t "battery-charger/cmd/mode" -m "CV"
```

### Via Logs

```bash
# Echtzeit-Logs
sudo journalctl -u battery-charger -f

# CSV Daten-Logs
tail -f ~/battery-charger/logs/charge_*.csv
```

## Sicherheitsfunktionen

### Mehrschichtiger Schutz
- **Spannungsgrenzen** - Absolutes Maximum (18V), Betriebsmaximum (17,2V), Warnung (12,5V)
- **Stromgrenzen** - Hardware-erzwungen (20A max vom SPE6205)
- **Leistungsüberwachung** - Echtzeit V×A Berechnung
- **Timeout-Schutz** - Konfigurierbare maximale Ladedauer (Standard 12 Stunden)
- **Temperaturüberwachung** - Optionaler DS18B20 Sensor mit Hoch/Tief-Grenzen
- **Spannungsplateau-Erkennung** - Auto-Stopp für Nasszellen über 16V
- **12,5V Warnschwelle** - Kritische SOC-Warnung (80% - sofort nachladen)

### Zuverlässigkeitsfunktionen
- **Automatische Abschaltung** - Bei Sicherheitsverletzungen, Abschluss oder Fehlern
- **Systemd Watchdog** - Auto-Neustart bei Absturz
- **MQTT Status** - Echtzeit-Gesundheitsüberwachung
- **Last Will Testament** - Offline-Erkennung
- **Vollständige Protokollierung** - Alle Sitzungen in CSV mit vollständigem Verlauf protokolliert
- **Energiebilanzierung** - Ah/Wh abgegeben und gespeichert verfolgen

## Lademodi

### IUoU (3-Stufen) - Empfohlen für die meisten Fälle
- Bulk: Konstantstrom (C/10) bis Absorptionsspannung
- Absorption: Absorptionsspannung halten bis Strom abnimmt
- Float: 13,5V halten (reduziert von 13,8V zur Vermeidung von Gitterkorrosion)
- Automatische Übergänge zwischen Stufen

### CC (Konstantstrom) - Traditionelle 150-Jahre-Methode
- Reine Konstantstromladung (C/10 Rate)
- Am besten für offene Nasszellen
- Verwendet Spannungsplateau-Erkennung für Auto-Stopp
- Batterie erreicht natürlich 17-17,5V wenn voll

### Conditioning (Tom's Methode) - Erweiterte Wartung
- Verlängerte Hochspannung (15,4-15,6V) für 24-48 Stunden
- Für Batterien die Ladung nicht richtig halten
- Verbessert Ruhespannung und Ladungserhaltung
- Beinhaltet Elektrolyse-Erkennung
- Besser als kontinuierliche Float-Ladung für Lagerbatterien

### CV (Konstantspannung)
- Zielspannung halten, Strom nimmt natürlich ab
- Gut für Erhaltungsladung

### Pulse (Puls)
- Entsulfatierungs-Modus für vernachlässigte Batterien
- Spannungsimpulse mit Ruhepausen
- Zur Wiederherstellung sulfatierter Batterien

### Trickle (Erhaltungsladung)
- Niedrige Strom-Erhaltung
- Verwendet jetzt 13,5V (reduziert von 13,8V)
- Für Langzeitlagerung

## Fehlerbehebung

### Dienst startet nicht

```bash
# Status prüfen
sudo systemctl status battery-charger

# Logs prüfen
sudo journalctl -u battery-charger -n 50

# Manuell ausführen um Fehler zu sehen
cd ~/battery-charger
python3 src/charger_main.py
```

### OWON nicht gefunden

```bash
# USB-Gerät prüfen
ls -l /dev/ttyUSB0

# Berechtigungen prüfen
sudo usermod -a -G dialout pi
# Aus- und wieder einloggen

# SCPI testen
python3 /tmp/test_owon.py
```

### MQTT funktioniert nicht

```bash
# Mosquitto läuft prüfen
sudo systemctl status mosquitto

# Manuell testen
mosquitto_pub -h localhost -t "test" -m "hello"
mosquitto_sub -h localhost -t "test"
```

## Dateistruktur

```
scpi-battery-charger/
├── README.md              # Englische Dokumentation
├── README.de.md           # Deutsche Dokumentation
├── battery-charger.service   # Systemd-Dienstdatei
├── requirements.txt          # Python-Abhängigkeiten
│
├── src/
│   ├── charger_main.py       # Haupteinstiegspunkt
│   ├── owon_psu.py           # OWON SCPI-Treiber
│   ├── charging_modes.py     # Ladealgorithmen
│   ├── safety_monitor.py     # Sicherheitsprüfungen
│   └── mqtt_client.py        # MQTT-Integration
│
├── config/
│   └── charging_config.yaml  # Hauptkonfiguration
│
├── logs/                     # Daten-Logs (automatisch erstellt)
│   └── charge_*.csv
│
└── docs/
    ├── CHARGING_MODES.md     # Modus-Details (Englisch)
    └── MQTT_API.md           # MQTT-Topic-Referenz (Englisch)
```

## Dokumentation

### Erste Schritte
- **[Installationsführer](docs/INSTALLATION_GUIDE.md)** (Englisch) - Vollständiger anfängerfreundlicher Setup-Leitfaden
- **[Netzteil-Auswahlführer](config/psu_templates/README.md)** (Englisch) - Das richtige OWON-Modell wählen
- **[Batterietypen-Leitfaden](CONFIGURATION_SUMMARY.md)** (Englisch) - Blei-Kalzium vs Blei-Antimon
- **[Systemd-Dienst-Setup](docs/SYSTEMD_SERVICE.md)** (Englisch) - Auto-Start-Konfiguration

### Neue Funktionen (2025)
- **[NEW_FEATURES.md](docs/NEW_FEATURES.md)** (Englisch) - Batterieprofile, Zeitplanung, Verlaufsverfolgung, Fehlerwiederherstellung
- **26 Batterieprofile** - `config/charging_config_*.yaml` Dateien für 2V-24V Batterien
  - 12V Geschlossen (AGM/Gel): 7Ah, 12Ah, 20Ah, 35Ah, 75Ah, 100Ah
  - 12V Nasszellen: 45Ah, 60Ah, 75Ah, 100Ah, 200Ah
  - 6V Golfwagen: 200Ah, 250Ah
  - 2V Industrie: 100Ah, 200Ah, 600Ah
  - 24V Batteriepacks, plus spezifische Batterien (Lucas, Banner, 4MAX)

## Support & Community

- **GitHub Issues**: https://github.com/packerlschupfer/scpi-battery-charger/issues
- **Konfigurationshilfe**: Siehe `config/psu_templates/README.md` (Englisch)
- **Logs**: `~/battery-charger/logs/` und `journalctl -u battery-charger -f`
- **MQTT-Tests**: `mosquitto_sub -h localhost -t 'battery-charger/#' -v`

## Lizenz

MIT-Lizenz - Siehe LICENSE-Datei für Details
