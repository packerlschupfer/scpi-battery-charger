# Batterieladegerät als Systemd-Dienst ausführen

**[English](SYSTEMD_SERVICE.md) | Deutsch**

Dieser Leitfaden erklärt, wie das Batterieladegerät automatisch als systemd-Dienst eingerichtet wird.

## Schnell-Setup

### 1. Aktuelle Screen-Sitzung stoppen

```bash
# Manuelle Screen-Sitzung stoppen
screen -S charging -X quit
```

### 2. Dienst installieren

```bash
cd ~/battery-charger

# Dienst-Datei zu systemd kopieren
sudo cp battery-charger.service /etc/systemd/system/

# Systemd neu laden
sudo systemctl daemon-reload

# Dienst aktivieren (bei Boot starten)
sudo systemctl enable battery-charger

# Dienst jetzt starten
sudo systemctl start battery-charger
```

### 3. Status prüfen

```bash
# Prüfen ob Dienst läuft
sudo systemctl status battery-charger

# Live-Logs ansehen
sudo journalctl -u battery-charger -f

# Neueste Logs ansehen
sudo journalctl -u battery-charger -n 50
```

## Dienst-Steuerung

### Start/Stopp/Neustart

```bash
# Dienst starten
sudo systemctl start battery-charger

# Dienst stoppen
sudo systemctl stop battery-charger

# Dienst neu starten
sudo systemctl restart battery-charger

# Konfiguration neu laden (ohne Neustart)
sudo systemctl reload-or-restart battery-charger
```

### Auto-Start aktivieren/deaktivieren

```bash
# Auto-Start bei Boot aktivieren
sudo systemctl enable battery-charger

# Auto-Start bei Boot deaktivieren
sudo systemctl disable battery-charger

# Prüfen ob aktiviert
systemctl is-enabled battery-charger
```

## Konfigurationsoptionen

### Auto-Start vs Manueller Start

`/etc/systemd/system/battery-charger.service` bearbeiten:

**Option A: Laden sofort automatisch starten**
```ini
ExecStart=/usr/bin/python3 /home/mrnice/battery-charger/src/charger_main.py --config /home/mrnice/battery-charger/config/charging_config.yaml --auto-start
```

**Option B: Auf MQTT-Befehl warten (empfohlen für Sicherheit)**
```ini
ExecStart=/usr/bin/python3 /home/mrnice/battery-charger/src/charger_main.py --config /home/mrnice/battery-charger/config/charging_config.yaml
```

Nach Bearbeitung neu laden:
```bash
sudo systemctl daemon-reload
sudo systemctl restart battery-charger
```

### Konfigurationsdatei ändern

Um verschiedene Konfig zu verwenden (z.B. für andere Batterie):

```bash
# Dienst-Datei bearbeiten
sudo nano /etc/systemd/system/battery-charger.service

# Diese Zeile ändern:
ExecStart=... --config /home/mrnice/battery-charger/config/charging_config_ANDERE.yaml

# Neu laden und neu starten
sudo systemctl daemon-reload
sudo systemctl restart battery-charger
```

## Protokollierung

### Logs ansehen

```bash
# Live tail (Strg+C zum Beenden)
sudo journalctl -u battery-charger -f

# Letzte 50 Zeilen
sudo journalctl -u battery-charger -n 50

# Heutige Logs
sudo journalctl -u battery-charger --since today

# Logs der letzten Stunde
sudo journalctl -u battery-charger --since "1 hour ago"

# Logs mit Zeitstempeln
sudo journalctl -u battery-charger -o short-iso

# Alle Logs (kann sehr lang sein!)
sudo journalctl -u battery-charger --no-pager
```

### CSV Daten-Logs

Dienst schreibt auch CSV-Logs (nicht von journald betroffen):

```bash
# Neuestes CSV-Log ansehen
tail -f ~/battery-charger/logs/charge_*.csv

# Alle Log-Dateien auflisten
ls -lh ~/battery-charger/logs/
```

## MQTT-Steuerung

Auch wenn als Dienst läuft, können Sie über MQTT steuern:

```bash
# Laden starten
mosquitto_pub -h localhost -t "battery-charger/cmd/start" -m ""

# Laden stoppen
mosquitto_pub -h localhost -t "battery-charger/cmd/stop" -m ""

# Modus ändern
mosquitto_pub -h localhost -t "battery-charger/cmd/mode" -m "Conditioning"

# Status überwachen
mosquitto_sub -h localhost -t "battery-charger/status/#" -v
```

## Fehlerbehebung

### Dienst startet nicht

```bash
# Dienst-Status prüfen
sudo systemctl status battery-charger

# Detaillierte Logs prüfen
sudo journalctl -u battery-charger -n 100

# Häufige Probleme:
# 1. Benutzer/Pfade falsch - User= und WorkingDirectory= in Dienst-Datei prüfen
# 2. System-Pakete fehlen - python3-serial, python3-paho-mqtt, python3-yaml installiert?
# 3. USB-Berechtigungen - Benutzer in 'dialout' Gruppe:
groups mrnice
# Falls nicht in dialout:
sudo usermod -a -G dialout mrnice
# Ab- und wieder anmelden
```

### Dienst startet ständig neu

```bash
# Logs nach Fehler durchsuchen
sudo journalctl -u battery-charger | grep -i error

# Neustart temporär deaktivieren zum Debuggen
sudo systemctl stop battery-charger
# Manuell ausführen um Fehler zu sehen:
cd ~/battery-charger
python3 src/charger_main.py --config config/charging_config.yaml --verbose
```

### Aktualisieren nach Code-Änderungen

```bash
# Nach Code-Update via git pull oder rsync:
sudo systemctl restart battery-charger

# Prüfen ob korrekt neu gestartet:
sudo systemctl status battery-charger
sudo journalctl -u battery-charger -n 20
```

## Dienst vs Screen-Sitzung

| Funktion | Systemd-Dienst | Screen-Sitzung |
|---------|----------------|----------------|
| Auto-Start bei Boot | ✅ Ja | ❌ Nein |
| Überlebt Abmeldung | ✅ Ja | ✅ Ja |
| Automatischer Neustart bei Absturz | ✅ Ja | ❌ Nein |
| System-Protokollierung (journald) | ✅ Ja | ❌ Nein |
| Einfaches Debugging | Schwieriger | ✅ Einfacher |
| Produktions-Einsatz | ✅ Empfohlen | ❌ Nicht empfohlen |

**Empfehlung:** Systemd-Dienst für normalen Betrieb verwenden, Screen für Testen/Debugging.

## Dienst deinstallieren

```bash
# Stoppen und deaktivieren
sudo systemctl stop battery-charger
sudo systemctl disable battery-charger

# Dienst-Datei entfernen
sudo rm /etc/systemd/system/battery-charger.service

# Systemd neu laden
sudo systemctl daemon-reload
```

## Beispiel: Vollständiges Setup von Grund auf

```bash
# 1. System installieren (falls nicht bereits erledigt)
cd ~/battery-charger
sudo apt install python3-serial python3-paho-mqtt python3-yaml

# 2. Zuerst manuell testen
python3 src/charger_main.py --config config/charging_config.yaml

# 3. Falls funktioniert, Dienst installieren
sudo cp battery-charger.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable battery-charger
sudo systemctl start battery-charger

# 4. Überwachen
sudo journalctl -u battery-charger -f
```

## Sicherheitshinweis

Der Dienst läuft mit eingeschränkten Rechten:
- `NoNewPrivileges=true` - Kann keine neuen Rechte erlangen
- `PrivateTmp=true` - Privates /tmp Verzeichnis
- `MemoryLimit=512M` - Speicherbegrenzung
- `CPUQuota=50%` - CPU-Begrenzung

Diese Einstellungen schützen das System vor außer Kontrolle geratenen Prozessen.

## Nützliche Befehle

### Dienst-Informationen

```bash
# Dienst-Datei-Inhalt ansehen
systemctl cat battery-charger

# Alle Dienst-Eigenschaften anzeigen
systemctl show battery-charger

# Nur wichtige Eigenschaften
systemctl show battery-charger -p ActiveState,SubState,MainPID
```

### Log-Filter

```bash
# Nur Fehler anzeigen
sudo journalctl -u battery-charger -p err

# Nur Warnungen und Fehler
sudo journalctl -u battery-charger -p warning

# Bestimmte Zeitspanne
sudo journalctl -u battery-charger --since "2025-11-01" --until "2025-11-02"
```

### Performance-Überwachung

```bash
# Dienst-Ressourcen-Verwendung
systemctl status battery-charger

# Detaillierte Ressourcen-Info
systemd-cgtop

# Nur battery-charger anzeigen
systemctl show battery-charger -p MemoryCurrent,CPUUsageNSec
```

## Weitere Dokumentation

- [README.md](../README.de.md) - Hauptdokumentation
- [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.de.md) - Installations-Leitfaden
- [MQTT_API.md](MQTT_API.md) - MQTT-Befehle (Englisch)
