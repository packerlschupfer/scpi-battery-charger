# Home Assistant Integrationsleitfaden

**[English](HOME_ASSISTANT.md) | Deutsch**

Vollständiger Leitfaden zur Integration des Batterieladegeräts mit Home Assistant über MQTT.

## Voraussetzungen

- Batterieladegerät läuft und ist mit MQTT-Broker verbunden
- Home Assistant mit MQTT-Integration konfiguriert
- MQTT-Broker von Home Assistant aus erreichbar

## MQTT-Integrations-Setup

### 1. MQTT in Home Assistant konfigurieren

Falls noch nicht konfiguriert, MQTT-Integration hinzufügen:

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Klicken Sie auf **Integration hinzufügen**
3. Suchen Sie nach **MQTT**
4. Geben Sie Ihre MQTT-Broker-Details ein (normalerweise `localhost` oder `192.168.x.x`)

### 2. Batterieladegerät-Entitäten hinzufügen

Zu Ihrer `configuration.yaml` hinzufügen:

```yaml
mqtt:
  sensor:
    # Spannungssensor
    - name: "Batteriespannung"
      state_topic: "battery-charger/status/voltage"
      unit_of_measurement: "V"
      device_class: voltage
      state_class: measurement
      value_template: "{{ value | float | round(2) }}"

    # Stromsensor
    - name: "Batteriestrom"
      state_topic: "battery-charger/status/current"
      unit_of_measurement: "A"
      device_class: current
      state_class: measurement
      value_template: "{{ value | float | round(2) }}"

    # Ladezustand
    - name: "Batterieladezustand"
      state_topic: "battery-charger/status/state"
      icon: mdi:battery-charging

    # Lademodus
    - name: "Batterielademodus"
      state_topic: "battery-charger/status/mode"
      icon: mdi:cog

    # Ladestufe (IUoU-Modus)
    - name: "Batterieladestufe"
      state_topic: "battery-charger/status/stage"
      icon: mdi:stairs

    # Verstrichene Zeit
    - name: "Batterieladung verstrichene Zeit"
      state_topic: "battery-charger/status/elapsed"
      unit_of_measurement: "s"
      device_class: duration
      state_class: measurement
      icon: mdi:timer

    # Fortschritt
    - name: "Batterieladefortschritt"
      state_topic: "battery-charger/status/progress"
      unit_of_measurement: "%"
      icon: mdi:percent

    # Online-Status
    - name: "Batterieladegerät Online"
      state_topic: "battery-charger/status/online"
      payload_on: "true"
      payload_off: "false"
      device_class: connectivity

  # Leistungsberechnung (V × A = W)
  - name: "Batterieladeleistung"
    state_topic: "battery-charger/status/json"
    unit_of_measurement: "W"
    device_class: power
    state_class: measurement
    value_template: >
      {% set data = value_json %}
      {{ (data.voltage | float * data.current | float) | round(1) }}

  switch:
    # Start/Stopp-Schalter
    - name: "Batterieladegerät"
      command_topic: "battery-charger/cmd/start"
      state_topic: "battery-charger/status/state"
      payload_on: ""
      payload_off: ""
      state_on: "charging"
      state_off: "idle"
      optimistic: false
      icon: mdi:battery-charging

  select:
    # Lademodus-Auswahl
    - name: "Batterielademodus Auswahl"
      command_topic: "battery-charger/cmd/mode"
      state_topic: "battery-charger/status/mode"
      options:
        - "IUoU"
        - "CV"
        - "Pulse"
        - "Trickle"
      icon: mdi:cog

  number:
    # Stromanpassung (an Ihr Netzteil-Modell anpassen)
    - name: "Batterieladestrom"
      command_topic: "battery-charger/cmd/current"
      state_topic: "battery-charger/status/current"
      min: 0.5
      max: 20.0  # SPE6205: 20A, SPE3102/3103/6103: 10A
      step: 0.1
      unit_of_measurement: "A"
      device_class: current
      icon: mdi:current-dc
```

### 3. Home Assistant neu starten

Nach Hinzufügen der Konfiguration:
1. Gehen Sie zu **Entwicklerwerkzeuge** → **YAML**
2. Klicken Sie auf **Konfiguration prüfen**
3. Falls gültig, klicken Sie auf **Neu starten**

## Dashboard-Karten

### Entitäten-Karte - Status-Übersicht

```yaml
type: entities
title: Batterieladegerät Status
entities:
  - entity: sensor.batterieladegerat_online
    name: Online
  - entity: sensor.batterieladezustand
    name: Zustand
  - entity: sensor.batterielademodus
    name: Modus
  - entity: sensor.batterieladestufe
    name: Stufe
  - entity: sensor.batterieladefortschritt
    name: Fortschritt
  - type: divider
  - entity: sensor.batteriespannung
    name: Spannung
  - entity: sensor.batteriestrom
    name: Strom
  - entity: sensor.batterieladeleistung
    name: Leistung
  - type: divider
  - entity: sensor.batterieladung_verstrichene_zeit
    name: Verstrichene Zeit
```

### Mess-Karten - Spannung und Strom

```yaml
type: horizontal-stack
cards:
  - type: gauge
    entity: sensor.batteriespannung
    name: Spannung
    min: 10
    max: 16
    needle: true
    severity:
      green: 12
      yellow: 14
      red: 15

  - type: gauge
    entity: sensor.batteriestrom
    name: Strom
    min: 0
    max: 20  # An Ihr Netzteil-Modell anpassen
    needle: true
    severity:
      green: 0
      yellow: 10
      red: 18
```

### Fortschrittsbalken

```yaml
type: custom:bar-card
entity: sensor.batterieladefortschritt
name: Ladefortschritt
unit_of_measurement: "%"
min: 0
max: 100
severity:
  - color: '#f44336'
    from: 0
    to: 33
  - color: '#ff9800'
    from: 33
    to: 66
  - color: '#4caf50'
    from: 66
    to: 100
```

### Steuerungs-Karte

```yaml
type: entities
title: Batterieladegerät Steuerung
entities:
  - entity: switch.batterieladegerat
    name: Laden
  - entity: select.batterielademodus_auswahl
    name: Modus
  - entity: number.batterieladestrom
    name: Strombegrenzung
```

### Verlaufs-Diagramm

```yaml
type: history-graph
title: Ladeverlauf
hours_to_show: 12
entities:
  - entity: sensor.batteriespannung
    name: Spannung
  - entity: sensor.batteriestrom
    name: Strom
  - entity: sensor.batterieladeleistung
    name: Leistung
```

## Automatisierungen

### Auto-Start bei niedriger Spannung

```yaml
automation:
  - alias: "Batterieladegerät - Auto Start"
    trigger:
      - platform: numeric_state
        entity_id: sensor.batteriespannung
        below: 12.5
    condition:
      - condition: state
        entity_id: sensor.batterieladezustand
        state: "idle"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.batterieladegerat
      - service: notify.mobile_app
        data:
          message: "Batteriespannung niedrig ({{ states('sensor.batteriespannung') }}V), starte Ladegerät"
```

### Laden stoppen wenn vollständig

```yaml
automation:
  - alias: "Batterieladegerät - Benachrichtigung vollständig"
    trigger:
      - platform: state
        entity_id: sensor.batterieladezustand
        to: "completed"
    action:
      - service: notify.mobile_app
        data:
          message: "Batterieladung vollständig"
      - service: switch.turn_off
        target:
          entity_id: switch.batterieladegerat
```

### Warnung bei Sicherheitsproblemen

```yaml
automation:
  - alias: "Batterieladegerät - Sicherheitswarnung"
    trigger:
      - platform: numeric_state
        entity_id: sensor.batteriespannung
        above: 16.5  # An Batterietyp anpassen (geschlossen: 16.5V, Nasszelle: 17.0V, Legacy: 15.5V)
    action:
      - service: notify.mobile_app
        data:
          message: "WARNUNG: Batteriespannung hoch ({{ states('sensor.batteriespannung') }}V)"
          title: "Batterieladegerät Sicherheit"
      - service: switch.turn_off
        target:
          entity_id: switch.batterieladegerat
```

### Geplante Wartungsladung

```yaml
automation:
  - alias: "Batterieladegerät - Wöchentliche Wartung"
    trigger:
      - platform: time
        at: "02:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: select.select_option
        target:
          entity_id: select.batterielademodus_auswahl
        data:
          option: "Trickle"
      - service: switch.turn_on
        target:
          entity_id: switch.batterieladegerat
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

## Fehlerbehebung

### Entitäten erscheinen nicht

1. MQTT-Verbindung prüfen: **Einstellungen** → **Geräte & Dienste** → **MQTT**
2. Topics mit MQTT Explorer oder Kommandozeile überprüfen:
   ```bash
   mosquitto_sub -h localhost -t "battery-charger/#" -v
   ```
3. `configuration.yaml` Syntax prüfen
4. Home Assistant neu starten

### Schalter funktioniert nicht

- Überprüfen ob Ladegerät online: `sensor.batterieladegerat_online` sollte `true` sein
- MQTT-Broker-Logs prüfen
- Manuell testen:
  ```bash
  mosquitto_pub -h localhost -t "battery-charger/cmd/start" -m ""
  ```

### Werte aktualisieren nicht

- `update_interval` in Ladegerät-Konfiguration prüfen
- Überprüfen ob Ladegerät läuft: `sudo systemctl status battery-charger`
- Ladegerät-Logs prüfen: `sudo journalctl -u battery-charger -f`

## Erweiterte Funktionen

### Template-Sensoren

Abgeleitete Sensoren erstellen:

```yaml
template:
  - sensor:
      # Verbrauchte Energie (ungefähr)
      - name: "Batterie geladene Energie"
        unit_of_measurement: "Wh"
        state: >
          {% set power = states('sensor.batterieladeleistung') | float %}
          {% set time = states('sensor.batterieladung_verstrichene_zeit') | float / 3600 %}
          {{ (power * time) | round(1) }}

      # Geschätzte verbleibende Zeit (sehr ungefähr)
      - name: "Batterieladung verbleibende Zeit"
        unit_of_measurement: "min"
        state: >
          {% set progress = states('sensor.batterieladefortschritt') | float %}
          {% set elapsed = states('sensor.batterieladung_verstrichene_zeit') | float / 60 %}
          {% if progress > 5 %}
            {{ ((elapsed / progress * 100) - elapsed) | round(0) }}
          {% else %}
            unknown
          {% endif %}
```

## Support

Für Probleme mit Home Assistant Integration:
1. MQTT-Verbindung prüfen
2. Überprüfen ob Topic-Namen mit Konfiguration übereinstimmen
3. Home Assistant Logs prüfen
4. MQTT manuell mit mosquitto_sub/pub testen

Für Ladegerät-Probleme siehe Haupt-README.md Fehlerbehebungs-Abschnitt.

---

## Vollständige Dashboard-Konfiguration

```yaml
type: vertical-stack
cards:
  # Status
  - type: entities
    title: Batterieladegerät
    entities:
      - entity: sensor.batterieladegerat_online
      - entity: sensor.batterieladezustand
      - entity: sensor.batterielademodus
      - entity: sensor.batterieladestufe

  # Messgeräte
  - type: horizontal-stack
    cards:
      - type: gauge
        entity: sensor.batteriespannung
        name: Spannung
        min: 10
        max: 16
        needle: true

      - type: gauge
        entity: sensor.batteriestrom
        name: Strom
        min: 0
        max: 20
        needle: true

  # Fortschritt
  - type: entities
    entities:
      - entity: sensor.batterieladefortschritt
      - entity: sensor.batterieladung_verstrichene_zeit

  # Steuerung
  - type: entities
    title: Steuerung
    entities:
      - entity: switch.batterieladegerat
      - entity: select.batterielademodus_auswahl
      - entity: number.batterieladestrom

  # Verlauf
  - type: history-graph
    hours_to_show: 6
    entities:
      - entity: sensor.batteriespannung
      - entity: sensor.batteriestrom
```

## Weitere Dokumentation

- [README.md](../README.de.md) - Hauptdokumentation
- [MQTT_API.md](MQTT_API.md) - MQTT-Topic-Referenz (Englisch)
- [CHARGING_MODES.md](CHARGING_MODES.de.md) - Lademodi-Details
