# MQTT API Referenz

**[English](MQTT_API.md) | Deutsch**

Vollständige MQTT-Topic- und Nachrichten-Referenz für Batterieladegerät-Controller.

## Basis-Topic

Standard: `battery-charger`

Konfigurierbar in `config/charging_config.yaml`:
```yaml
mqtt:
  base_topic: "battery-charger"
```

## Topic-Struktur

```
battery-charger/
├── status/          # Vom Ladegerät veröffentlicht (nur lesen)
│   ├── online
│   ├── voltage
│   ├── current
│   ├── mode
│   ├── state
│   ├── stage
│   ├── elapsed
│   ├── progress
│   └── json
└── cmd/             # Befehle an Ladegerät (schreiben)
    ├── start
    ├── stop
    ├── mode
    └── current
```

---

## Status-Topics (Veröffentlicht)

Diese Topics werden vom Ladegerät veröffentlicht. Abonnieren um Status zu überwachen.

### `battery-charger/status/online`

Ladegerät Online/Offline-Status (Last Will and Testament).

**Typ:** Boolean-String
**Retain:** Ja
**QoS:** 1
**Update:** Bei Verbindung/Trennung

**Werte:**
- `"true"` - Ladegerät online und läuft
- `"false"` - Ladegerät offline oder getrennt

**Beispiel:**
```bash
mosquitto_sub -h localhost -t "battery-charger/status/online"
```

---

### `battery-charger/status/voltage`

Aktuelle Batteriespannungs-Messung.

**Typ:** Float-String
**Einheit:** Volt (V)
**Retain:** Ja
**QoS:** 1
**Update:** Alle 5 Sekunden (konfigurierbar)

**Bereich:** 0.0 - 62.0 (abhängig vom Netzteil-Modell)

**Beispiel:**
```
13.45
14.12
12.98
```

---

### `battery-charger/status/current`

Aktuelle Ladestrom-Messung.

**Typ:** Float-String
**Einheit:** Ampere (A)
**Retain:** Ja
**QoS:** 1
**Update:** Alle 5 Sekunden

**Bereich:** 0.0 - 20.0 (SPE6205: 20A, SPE3102/3103/6103: 10A)

**Beispiel:**
```
4.23
2.15
0.87
```

---

### `battery-charger/status/mode`

Aktiver Lademodus.

**Typ:** String
**Retain:** Ja
**QoS:** 1
**Update:** Bei Moduswechsel

**Werte:**
- `"IUoU"` - 3-Stufen-Ladung (Bulk/Absorption/Float)
- `"CV"` - Konstantspannung
- `"Pulse"` - Pulsladung (Entsulfatierung)
- `"Trickle"` - Erhaltungsladung

**Beispiel:**
```
IUoU
```

---

### `battery-charger/status/state`

Aktueller Ladezustand.

**Typ:** String
**Retain:** Ja
**QoS:** 1
**Update:** Bei Zustandswechsel

**Werte:**
- `"idle"` - Lädt nicht
- `"charging"` - Lädt aktiv
- `"completed"` - Ladung abgeschlossen
- `"error"` - Fehler aufgetreten
- `"stopped"` - Manuell gestoppt

**Beispiel:**
```
charging
```

---

### `battery-charger/status/stage`

Aktuelle Stufe innerhalb des Lademodus (nur IUoU).

**Typ:** String
**Retain:** Ja
**QoS:** 1
**Update:** Bei Stufenwechsel

**Werte (IUoU-Modus):**
- `"bulk"` - Konstantstrom-Phase
- `"absorption"` - Konstantspannungs-Phase
- `"float"` - Erhaltungs-Phase

**Werte (Pulse-Modus):**
- `"pulse"` - Hochspannungs-Puls
- `"rest"` - Ruhephase

**Andere Modi:** Leerer String

**Beispiel:**
```
absorption
```

---

### `battery-charger/status/elapsed`

Verstrichene Ladezeit seit Start.

**Typ:** Integer-String
**Einheit:** Sekunden
**Retain:** Ja
**QoS:** 1
**Update:** Alle 5 Sekunden

**Bereich:** 0 - 43200 (max 12 Stunden standardmäßig)

**Beispiel:**
```
3600
7234
```

**In Zeit umrechnen:**
```python
stunden = elapsed // 3600
minuten = (elapsed % 3600) // 60
```

---

### `battery-charger/status/progress`

Geschätzter Ladefortschritt.

**Typ:** Integer-String
**Einheit:** Prozent (%)
**Retain:** Ja
**QoS:** 1
**Update:** Alle 5 Sekunden

**Bereich:** 0 - 100

**Fortschritts-Schätzung:**
- **IUoU:** Bulk 0-60%, Absorption 60-90%, Float 90-100%
- **CV:** Basierend auf Strom-Abnahme
- **Pulse:** Basierend auf Zyklus-Anzahl
- **Trickle:** Fest bei 50% (Wartung)

**Beispiel:**
```
75
```

---

### `battery-charger/status/json`

Vollständiger Status als JSON-Objekt.

**Typ:** JSON-String
**Retain:** Nein
**QoS:** 1
**Update:** Alle 5 Sekunden

**Felder:**
```json
{
  "voltage": 13.45,
  "current": 4.23,
  "mode": "IUoU",
  "state": "charging",
  "stage": "bulk",
  "elapsed": 3600,
  "progress": 45,
  "bulk_current": 4.75,
  "absorption_voltage": 14.4,
  "float_voltage": 13.6
}
```

**Beispiel-Verwendung:**
```bash
mosquitto_sub -h localhost -t "battery-charger/status/json" | jq
```

---

## Befehls-Topics (Abonniert)

Diese Topics akzeptieren Befehle. Veröffentlichen um Ladegerät zu steuern.

### `battery-charger/cmd/start`

Ladung mit aktuellem Modus starten.

**Payload:** Leerer String (jeder Payload akzeptiert)
**QoS:** 1
**Antwort:** Aktualisiert `status/state` auf `"charging"`

**Beispiel:**
```bash
mosquitto_pub -h localhost -t "battery-charger/cmd/start" -m ""
```

**Ergebnis:**
- Netzteil-Ausgang aktiviert
- Ladung beginnt mit konfiguriertem Modus
- Status-Updates werden veröffentlicht

---

### `battery-charger/cmd/stop`

Ladung sofort stoppen.

**Payload:** Leerer String (jeder Payload akzeptiert)
**QoS:** 1
**Antwort:** Aktualisiert `status/state` auf `"stopped"`

**Beispiel:**
```bash
mosquitto_pub -h localhost -t "battery-charger/cmd/stop" -m ""
```

**Ergebnis:**
- Netzteil-Ausgang deaktiviert
- Ladung stoppt
- Sicherheits-Überwachung stoppt

---

### `battery-charger/cmd/mode`

Lademodus ändern.

**Payload:** Modus-Name-String
**QoS:** 1
**Antwort:** Aktualisiert `status/mode`

**Gültige Werte:**
- `"IUoU"` - Zu 3-Stufen-Ladung wechseln
- `"CV"` - Zu Konstantspannung wechseln
- `"Pulse"` - Zu Pulsladung wechseln
- `"Trickle"` - Zu Erhaltungsladung wechseln

**Beispiel:**
```bash
mosquitto_pub -h localhost -t "battery-charger/cmd/mode" -m "CV"
```

**Verhalten:**
- Stoppt aktuelle Ladung falls aktiv
- Erstellt neue Modus-Instanz mit Konfiguration
- Startet Ladung NICHT automatisch
- Senden Sie `cmd/start` um mit neuem Modus zu beginnen

---

### `battery-charger/cmd/current`

Ladestrom-Grenze anpassen.

**Payload:** Strom-Wert als Float-String
**Einheit:** Ampere (A)
**QoS:** 1
**Antwort:** Aktualisiert `status/current` (falls lädt)

**Bereich:** 0.5 - 20.0 (SPE6205: 20A max, an Ihr Netzteil-Modell anpassen)

**Beispiel:**
```bash
mosquitto_pub -h localhost -t "battery-charger/cmd/current" -m "3.5"
```

**Verhalten:**
- Falls lädt: Aktualisiert Netzteil-Strom-Grenze sofort
- Falls idle: Keine Wirkung (verwendet Konfiguration bei nächstem Start)
- Sicherheits-Grenzen gelten weiterhin

---

## QoS-Stufen

**QoS 0 (Höchstens einmal):** Nicht verwendet
**QoS 1 (Mindestens einmal):** Verwendet für alle Topics (Standard)
**QoS 2 (Genau einmal):** Unterstützt, konfigurierbar

Konfigurieren in `charging_config.yaml`:
```yaml
mqtt:
  qos: 1  # 0, 1, oder 2
```

---

## Retain-Flag

**Status-Topics:** Retained (letzter Wert sofort nach Abonnieren verfügbar)
**Befehls-Topics:** Nicht retained
**Online-Status (LWT):** Retained

Konfigurieren in `charging_config.yaml`:
```yaml
mqtt:
  retain: true
```

---

## Update-Intervalle

**Status-Updates:** 5 Sekunden (Standard)
**CSV-Protokollierung:** 60 Sekunden (Standard)

Konfigurieren in `charging_config.yaml`:
```yaml
mqtt:
  update_interval: 5.0  # Sekunden

safety:
  measurement_interval: 5.0  # Sekunden
  log_interval: 60.0  # Sekunden
```

---

## Beispiel-Workflows

### Alle Topics überwachen

```bash
mosquitto_sub -h localhost -t "battery-charger/#" -v
```

### IUoU-Ladung starten

```bash
# Modus setzen
mosquitto_pub -h localhost -t "battery-charger/cmd/mode" -m "IUoU"

# Ladung starten
mosquitto_pub -h localhost -t "battery-charger/cmd/start" -m ""
```

### Schnelle Status-Prüfung

```bash
mosquitto_sub -h localhost -t "battery-charger/status/json" -C 1 | jq
```

### Spannung und Strom überwachen

```bash
mosquitto_sub -h localhost -t "battery-charger/status/voltage" -t "battery-charger/status/current" -v
```

### Notfall-Stopp

```bash
mosquitto_pub -h localhost -t "battery-charger/cmd/stop" -m ""
```

### Strom während Ladung ändern

```bash
# Strom auf 2A reduzieren
mosquitto_pub -h localhost -t "battery-charger/cmd/current" -m "2.0"
```

---

## Python-Beispiel

```python
import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    print(f"Verbunden mit Ergebnis-Code {rc}")
    # Alle Status-Topics abonnieren
    client.subscribe("battery-charger/status/#")

def on_message(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")

    # JSON-Status parsen
    if msg.topic == "battery-charger/status/json":
        status = json.loads(msg.payload.decode())
        print(f"Spannung: {status['voltage']}V")
        print(f"Strom: {status['current']}A")
        print(f"Fortschritt: {status['progress']}%")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

# Ladung starten
client.publish("battery-charger/cmd/start", "")

# Schleife ausführen
client.loop_forever()
```

---

## Node-RED Flow

```json
[
    {
        "id": "mqtt_in",
        "type": "mqtt in",
        "topic": "battery-charger/status/json",
        "qos": "1",
        "broker": "mqtt_broker",
        "outputs": 1
    },
    {
        "id": "json_parse",
        "type": "json"
    },
    {
        "id": "debug",
        "type": "debug",
        "name": "Batterie-Status"
    }
]
```

---

## Sicherheit

### Authentifizierung

Benutzername/Passwort in `charging_config.yaml` konfigurieren:

```yaml
mqtt:
  username: "charger"
  password: "sicheres_passwort_hier"
```

### TLS/SSL

Für sichere Verbindungen, Broker-Einstellungen aktualisieren:

```yaml
mqtt:
  broker: "mqtt.example.com"
  port: 8883  # TLS-Port
  # Zertifikatspfade falls nötig hinzufügen
```

### Zugriffskontrolle (Mosquitto)

ACL-Datei `/etc/mosquitto/acl` erstellen:

```
# Batterieladegerät-Zugriff
user charger
topic write battery-charger/cmd/#
topic read battery-charger/status/#

# Home Assistant-Zugriff
user homeassistant
topic read battery-charger/#
topic write battery-charger/cmd/#
```

---

## Fehlerbehebung

### Keine Nachrichten empfangen

```bash
# Broker-Status prüfen
sudo systemctl status mosquitto

# Broker testen
mosquitto_pub -h localhost -t "test" -m "hallo"
mosquitto_sub -h localhost -t "test"

# Ladegerät-Status prüfen
sudo systemctl status battery-charger

# Ladegerät-Logs prüfen
sudo journalctl -u battery-charger -f
```

### Nachrichten nicht retained

`retain`-Einstellung in Konfiguration prüfen und überprüfen mit:

```bash
# Abonnieren um retained Nachrichten sofort zu sehen
mosquitto_sub -h localhost -t "battery-charger/status/voltage"
```

Sollte letzte Spannung sofort anzeigen, nicht auf Update warten.

### Befehle funktionieren nicht

```bash
# Befehl manuell testen
mosquitto_pub -h localhost -t "battery-charger/cmd/start" -m "" -d

# Ladegerät-Logs auf empfangenen Befehl prüfen
sudo journalctl -u battery-charger | grep "MQTT command"
```

---

## Siehe auch

- [README.md](../README.de.md) - Hauptdokumentation
- [HOME_ASSISTANT.md](HOME_ASSISTANT.de.md) - Home Assistant Integration
- [CHARGING_MODES.md](CHARGING_MODES.de.md) - Lade-Algorithmen
