# OWON Netzteil-Konfigurationsvorlagen

**[English](README.md) | Deutsch**

Dieses Verzeichnis enthält Konfigurationsvorlagen für verschiedene OWON SPE-Serie Netzteile.

## Unterstützte Modelle

| Modell | Spannung | Strom | Leistung | Empfohlene Batteriegröße |
|--------|----------|-------|----------|--------------------------|
| **SPE3102** | 30V | 10A | 200W | Bis zu 70-80Ah (nur 12V) |
| **SPE3103** | 30V | 10A | 300W | Bis zu 70-80Ah (nur 12V) |
| **SPE6103** | 60V | 10A | 300W | Bis zu 70-80Ah (12V, 24V, 48V) |
| **SPE6205** | 60V | 20A | 500W | Bis zu 200Ah+ (12V, 24V, 48V) |

## Verwendung

### 1. Wählen Sie Ihre Netzteil-Vorlage

Wählen Sie die Vorlage, die zu Ihrem Netzteil passt:

```bash
# Für SPE3102-Benutzer:
cp config/psu_templates/SPE3102_config.yaml config/charging_config.yaml

# Für SPE3103-Benutzer:
cp config/psu_templates/SPE3103_config.yaml config/charging_config.yaml

# Für SPE6103-Benutzer:
cp config/psu_templates/SPE6103_config.yaml config/charging_config.yaml

# Für SPE6205-Benutzer:
cp config/psu_templates/SPE6205_config.yaml config/charging_config.yaml
```

### 2. Für Ihre Batterie anpassen

Bearbeiten Sie `config/charging_config.yaml` und passen Sie diese Werte für IHRE spezifische Batterie an:

**Batterie-Spezifikationen:**
```yaml
battery:
  capacity: 95.0                  # IHRE Batterie-Ah-Nennwert
  manufacture_year: 2015          # IHRE Batterie-Jahr
  chemistry: "lead_calcium"       # oder "lead_antimony" für alte Batterien
```

**Ladestrom (0,1C-Regel):**
```yaml
charging:
  IUoU:
    bulk_current: 9.5             # 0,1 × IHRE Batteriekapazität
                                   # Beispiel: 44Ah → 4,4A
                                   #          70Ah → 7,0A
                                   #          95Ah → 9,5A
```

### 3. Wichtig: Batteriegrößen-Grenzen

**SPE3102/3103 (10A-Modelle):**
- **Empfohlenes Maximum**: 70-80Ah Batterien
- **Absolutes Maximum**: 100Ah (läuft aber bei 100% Dauerlast)
- **Warum**: 0,1C-Ladung für 100Ah = 10A (an Netzteil-Grenze)

**SPE6103 (60V / 10A):**
- Gleiche Stromgrenze wie SPE3102/3103
- Kann 12V, 24V oder 48V Batterien laden
- Batteriegrößen-Grenze wie oben

**SPE6205 (60V / 20A):**
- Kann bis zu 200Ah Batterien bequem handhaben
- 0,1C für 200Ah = 20A (an Netzteil-Grenze)
- Empfohlen: 150Ah max für Dauerbetrieb

## Batteriespannungs-Systeme

Alle Vorlagen sind standardmäßig für **12V-Batterien** konfiguriert.

### Für 24V-Batterien

Alle Spannungen mit 2 multiplizieren:
```yaml
charging:
  IUoU:
    absorption_voltage: 30.4      # 15,2V × 2
    float_voltage: 27.0           # 13,5V × 2

safety:
  absolute_max_voltage: 33.0      # 16,5V × 2
  min_voltage: 21.0               # 10,5V × 2
  warning_voltage: 25.0           # 12,5V × 2
```

### Für 48V-Batterien

Alle Spannungen mit 4 multiplizieren:
```yaml
charging:
  IUoU:
    absorption_voltage: 60.8      # 15,2V × 4 (durch Netzteil auf 60V begrenzt)
    float_voltage: 54.0           # 13,5V × 4

safety:
  absolute_max_voltage: 60.0      # Durch Netzteil begrenzt (16,5V × 4 = 66V würde überschreiten)
  min_voltage: 42.0               # 10,5V × 4
  warning_voltage: 50.0           # 12,5V × 4
```

**Hinweis**: SPE3102 und SPE3103 sind auf 30V begrenzt, daher können sie **keine** 24V- oder 48V-Batterien laden!

## Kompatibilität

Alle OWON SPE-Serie Netzteile verwenden das gleiche SCPI-Protokoll, daher sollten diese Vorlagen ohne Code-Änderungen funktionieren.

**Andere SCPI-Netzteile könnten auch funktionieren** - erstellen Sie einfach eine benutzerdefinierte Konfigurationsdatei mit den korrekten Spannungs-/Strom-/Leistungsgrenzen.

## Beispiel: Banner 544 09 (44Ah) mit SPE3102

```yaml
power_supply:
  model: "OWON SPE3102"
  max_voltage: 30.0
  max_current: 10.0
  max_power: 200.0

battery:
  capacity: 44.0                  # 44Ah Batterie
  chemistry: "lead_calcium"

charging:
  IUoU:
    bulk_current: 4.4             # 0,1C = 4,4A
    absorption_voltage: 15.2      # Blei-Kalzium Standard
```

**Netzteil-Last**: 4,4A / 10A = 44% - Perfekt für Dauerbetrieb!

## Beispiel: Exide EA954 (95Ah) mit SPE6205

```yaml
power_supply:
  model: "OWON SPE6205"
  max_voltage: 60.0
  max_current: 20.0
  max_power: 500.0

battery:
  capacity: 95.0                  # 95Ah Batterie
  chemistry: "lead_calcium"

charging:
  IUoU:
    bulk_current: 9.5             # 0,1C = 9,5A
    absorption_voltage: 15.2      # Blei-Kalzium Standard
```

**Netzteil-Last**: 9,5A / 20A = 47,5% - Ausgezeichnet für Dauerbetrieb!

## Warum SPE6205 für größere Batterien?

Wenn Sie eine 95Ah Batterie haben:
- **SPE3102/3103**: Würde 9,5A benötigen (95% Last) - läuft sehr heiß während 24-48h Conditioning
- **SPE6205**: Verwendet 9,5A (47,5% Last) - bleibt kühl, längere Lebensdauer

**Auch nützlich für**:
- Laden mehrerer kleinerer Batterien
- Andere Projekte mit höherem Leistungsbedarf
- Zukünftige Erweiterung

## Hilfe benötigt?

Siehe Hauptdokumentation:
- `docs/SYSTEMD_SERVICE.de.md` - Installationsleitfaden
- `README.de.md` - Hauptdokumentation
- `CONFIGURATION_SUMMARY.de.md` - Batteriechemie-Leitfaden

GitHub: https://github.com/packerlschupfer/scpi-battery-charger
