# Automatisierungs-Skripte

**[English](README.md) | Deutsch**

## stop_charging.sh

**Batterieladegerät ordnungsgemäß mit sauberem Herunterfahren stoppen.**

Dieses Skript sendet SIGTERM (statt SIGKILL), um Aufräum-Handler auszuführen und sicherzustellen, dass der Netzteil-Ausgang AUS geschaltet wird.

### Verwendung

```bash
cd ~/battery-charger/scripts
./stop_charging.sh
```

**Was es tut:**
1. Findet den Ladegerät-Prozess
2. Sendet SIGTERM für sauberes Herunterfahren
3. Wartet bis zu 10 Sekunden auf Aufräumen
4. Netzteil-Ausgang wird sicher AUS geschaltet
5. MQTT und Logs werden ordnungsgemäß geschlossen

**⚠️ VERWENDEN SIE NICHT `screen -X quit`** - sendet SIGKILL, was Aufräumen verhindert!

**Alternative Methoden:**
```bash
# Via MQTT (falls aktiviert)
mosquitto_pub -h localhost -t 'battery-charger/cmd/stop' -m ''

# Manuell (nicht empfohlen - verwenden Sie stattdessen Skript)
pkill -TERM -f charger_main.py
```

---

## auto_conditioning.sh

Automatisierte Conditioning-Sequenz, die den kompletten Workflow handhabt:

1. Stoppt jede aktive Ladung
2. Lässt Batterie ruhen (Standard: 2 Stunden)
3. Führt Diagnosemodus aus um Ruhespannung zu prüfen
4. Startet Conditioning-Modus (15,5V für 24-48h)

### Verwendung

**Standard (2-Stunden-Ruhe):**
```bash
cd ~/battery-charger/scripts
./auto_conditioning.sh
```

**Benutzerdefinierte Ruhedauer:**
```bash
# 1 Stunde Ruhe
./auto_conditioning.sh 3600

# 30 Minuten Ruhe (zum Testen)
./auto_conditioning.sh 1800

# 4 Stunden Ruhe
./auto_conditioning.sh 14400
```

**Im Hintergrund ausführen (nohup):**
```bash
nohup ./auto_conditioning.sh &
# Fortschritt überwachen:
tail -f /tmp/auto_conditioning.log
```

**In Screen-Sitzung ausführen:**
```bash
screen -dmS auto_cond ./auto_conditioning.sh
# Fortschritt überwachen:
screen -r auto_cond
# Trennen: Strg+A, D
```

### Überwachung

**Fortschritt prüfen:**
```bash
tail -f /tmp/auto_conditioning.log
```

**Prüfen ob Conditioning läuft:**
```bash
screen -ls | grep charging
```

**Conditioning via MQTT überwachen:**
```bash
mosquitto_sub -h localhost -t 'battery-charger/status/#'
```

**An Conditioning-Sitzung anhängen:**
```bash
screen -r charging
# Trennen: Strg+A, D
```

### Conditioning stoppen

```bash
screen -S charging -X quit
```

### Beispiel-Ausgabe

```
[2025-10-31 23:59:00] =========================================
[2025-10-31 23:59:00] Starte automatisierte Conditioning-Sequenz
[2025-10-31 23:59:00] Ruhedauer: 7200 Sekunden (2 Stunden)
[2025-10-31 23:59:00] =========================================
[2025-10-31 23:59:00] Schritt 1: Stoppe jede aktive Ladesitzung...
[2025-10-31 23:59:03] Schritt 2: Batterie ruht für 2 Stunden...
[2025-10-31 23:59:03] Ruhe endet um: 2025-11-01 01:59:03
[2025-11-01 00:14:03] Ruht... 1h 45m verbleibend
[2025-11-01 00:29:03] Ruht... 1h 30m verbleibend
...
[2025-11-01 01:59:03] Schritt 2: Ruhephase abgeschlossen
[2025-11-01 01:59:03] Schritt 3: Führe Diagnosemodus aus um Ruhespannung zu prüfen...
[2025-11-01 01:59:13] Schritt 3: Diagnose abgeschlossen (prüfe Log oben für Spannungswert)
[2025-11-01 01:59:13] Schritt 4: Starte Conditioning-Modus (15,5V für 24-48h)...
[2025-11-01 01:59:18] Schritt 4: Conditioning-Modus erfolgreich gestartet!
[2025-11-01 01:59:18] =========================================
[2025-11-01 01:59:18] Automatisierte Conditioning-Sequenz abgeschlossen
[2025-11-01 01:59:18] =========================================
```
