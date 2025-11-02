# Leitfaden für neue Funktionen

**[English](NEW_FEATURES.md) | Deutsch**

Dieses Dokument beschreibt die neuen Funktionen, die zum Batterieladegerät-System hinzugefügt wurden.

## Funktionsübersicht

1. **Verbesserte Fortschrittsberechnung** - Sanfterer, genauerer Ladefortschritt
2. **Batterieprofil-Umschaltung** - Zwischen Batterien über MQTT wechseln
3. **Lade-Zeitplanung** - Ladesitzungen planen
4. **Fehlerwiederherstellung** - Automatische Wiederverbindung Netzteil/MQTT
5. **Batterieverlauf & Gesundheit** - Ladezyklen und Batteriegesundheit verfolgen

---

## 1. Verbesserte Fortschrittsberechnung

**Was sich geändert hat:**
- Fortschritt läuft jetzt 0→70% (Bulk) → 70→95% (Absorption) → 100% (Float)
- Vorher: 0→60% → 60→84% → 100% (mit Sprüngen)
- Bessere Stromabnehm-Berechnung (Schwelle × 10 statt × 3)

**Keine Aktion erforderlich** - gilt automatisch für alle Ladesitzungen.

---

## 2. Batterieprofil-Umschaltung via MQTT

**Verfügbare Profile:**
- `4max_100ah` - 4MAX 100Ah Batterie
- `lucas_44ah` - Lucas Premium LP063 44Ah
- `banner_44ah` - Banner 544 09 44Ah
- `default` - Generische Blei-Kalzium 95Ah
- `lead_antimony` - Legacy Blei-Antimon-Chemie
- `lead_calcium` - Moderne Blei-Kalzium-Chemie
- `conditioning` - Tom's Conditioning-Modus

Und 16 zusätzliche vorkonfigurierte Profile für verschiedene Spannungen und Kapazitäten (2V/6V/12V/24V).

**Verwendung via MQTT:**
```bash
# Zu Lucas 44Ah Batterie wechseln
mosquitto_pub -h localhost -t 'battery-charger/cmd/profile' -m 'lucas_44ah'

# Zu 12V 20Ah geschlossener Batterie wechseln
mosquitto_pub -h localhost -t 'battery-charger/cmd/profile' -m '12v_sealed_20ah'
```

**Regeln:**
- Kann wechseln wenn im Leerlauf (nicht ladend)
- Nicht möglich während Laden (Sicherheit)
- Lädt automatisch batteriespezifische Einstellungen (Kapazität, Spannung, Strom)

---

## 3. Lade-Zeitplanung

**Modul:** `src/charge_scheduler.py`

**Funktionen:**
- Laden zu bestimmter Zeit starten
- Zeitbegrenzung setzen
- Automatischer Batterieprofil-Wechsel
- Einmalige oder wiederkehrende Zeitpläne

**Beispiel-Verwendung via MQTT:**
```bash
# Heute um 14:30 laden, Lucas-Profil, 2 Stunden Begrenzung
mosquitto_pub -h localhost -t 'battery-charger/cmd/schedule' \
  -m '{"start_time": "14:30", "duration": "2h", "profile": "lucas_44ah"}'

# Zeitplan abbrechen
mosquitto_pub -h localhost -t 'battery-charger/cmd/schedule/cancel' -m ''
```

**Zeitformate:**
- `"now"` - Sofort starten
- `"14:30"` - Heute um 14:30 (oder morgen falls schon vorbei)
- `"2025-11-02 14:30"` - Spezifisches Datum/Zeit

**Zeitdauer-Formate:**
- `"1h"` - 1 Stunde
- `"30m"` - 30 Minuten
- `"3600"` - 3600 Sekunden

---

## 4. Fehlerwiederherstellung

**Modul:** `src/error_recovery.py`

**Funktionen:**
- Automatische Netzteil-Wiederverbindung bei USB-Trennung
- Automatische MQTT-Broker-Wiederverbindung bei Netzwerkproblemen
- Verfolgt Trennungszähler
- Konfigurierbare Prüfintervalle

**Vorteile:**
- Zuverlässiger Betrieb trotz USB/Netzwerkproblemen
- Automatische Wiederherstellung ohne manuelle Eingriffe
- Protokollierung von Verbindungsproblemen für Diagnose

---

## 5. Batterieverlauf & Gesundheits-Verfolgung

**Modul:** `src/battery_history.py`

**Funktionen:**
- Verfolgt alle Ladesitzungen pro Batterie
- Berechnet Batteriegesundheit (Kapazitätsabbau)
- Statistiken: Gesamt Ah/Wh, Durchschnitt pro Sitzung
- Export zu CSV
- JSON-Speicherformat

**Beispiel-Ausgabe:**
```json
{
  "lucas_44ah": {
    "sessions": [...],
    "stats": {
      "total_sessions": 42,
      "total_ah_delivered": 185.4,
      "total_wh_delivered": 2786.2,
      "avg_ah_per_session": 4.41,
      "estimated_health": 96.5
    }
  }
}
```

**Gesundheitsberechnung:**
- Vergleicht kürzlichen Durchschnitts-Ah mit historischem Durchschnitt
- 100% = Batterie akzeptiert gleiche Ladung wie zuvor
- <90% = Kapazitätsabbau erkannt
- Hilft Batterieaustausch-Bedarf vorherzusagen

**Datei-Speicherort:** `~/battery-charger/logs/battery_history.json`

---

## MQTT-Befehle

### Batterieprofil wechseln
```bash
mosquitto_pub -h localhost -t 'battery-charger/cmd/profile' -m '<profil_name>'
```

**Verfügbare Profilnamen:**
- Spezifische Batterien: `lucas_44ah`, `banner_44ah`, `4max_100ah`
- Nach Spannung: `12v_sealed_20ah`, `12v_flooded_75ah`, `6v_flooded_200ah`, `2v_sealed_100ah`
- Nach Chemie: `lead_calcium`, `lead_antimony`
- Siehe `config/` Verzeichnis für alle 26 verfügbaren Profile

### Laden planen
```bash
# JSON-Format
mosquitto_pub -h localhost -t 'battery-charger/cmd/schedule' \
  -m '{"start_time": "02:00", "duration": "3h", "profile": "lucas_44ah"}'

# Zeitplan abbrechen
mosquitto_pub -h localhost -t 'battery-charger/cmd/schedule/cancel' -m ''
```

---

## Vorteile

1. **Fortschrittsberechnung:** Genauere Fortschrittsanzeige, keine Sprünge
2. **Profil-Umschaltung:** Schneller Batteriewechsel ohne Konfig-Bearbeitung
3. **Zeitplanung:** Laden während Schwachlastzeiten, Zeitbegrenzungen setzen
4. **Fehlerwiederherstellung:** Zuverlässiger Betrieb trotz USB/Netzwerkproblemen
5. **Verlaufs-Verfolgung:** Batteriegesundheit überwachen, Austausch vorhersagen

Alle Funktionen sind modular und können unabhängig aktiviert/deaktiviert werden.

---

## Integration

Diese Funktionen sind bereits in `src/charger_main.py` integriert und aktiv:

- Batterieprofil-Umschaltung über MQTT-Befehle
- Lade-Zeitplanung über MQTT-Befehle
- Fehlerwiederherstellung läuft automatisch
- Batterieverlauf wird bei jeder Ladesitzung aufgezeichnet

**Keine manuelle Konfiguration erforderlich** - alle Funktionen sind einsatzbereit!

---

## Weiterführende Dokumentation

- [README.md](../README.de.md) - Hauptdokumentation
- [CHARGING_MODES.md](CHARGING_MODES.de.md) - Lademodi-Details
- [BATTERY_TYPES.md](BATTERY_TYPES.de.md) - Batterietyp-Identifikation
