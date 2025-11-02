# Batterietyp-Identifikationsleitfaden

**[English](BATTERY_TYPES.md) | Deutsch**

**KRITISCH:** Die Verwendung falscher Ladespannungen kann Ihre Batterie beschädigen oder verhindern, dass sie ordnungsgemäß lädt!

Dieser Leitfaden hilft Ihnen, Ihren Batterietyp zu identifizieren und die richtige Konfiguration auszuwählen.

---

## Schnell-Identifikation

### Ist Ihre Batterie Blei-Kalzium oder Blei-Antimon?

```
┌─────────────────────────────────────────┐
│  Wann wurde Ihre Batterie hergestellt?  │
└─────────────────┬───────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
    Vor 2010          2010 oder später
         │                 │
         ▼                 ▼
   BLEI-ANTIMON      BLEI-KALZIUM
         │                 │
         │                 │
   Konfig:           Konfig:
   lead_antimony     lead_calcium
   14,4V Ladung      15,2V Ladung
```

---

## Detaillierte Identifikation

### Methode 1: Herstellungsdatum prüfen

**Suchen Sie nach Datumscode auf Batterieetikett:**
- Format variiert: "C15" (März 2015), "05/2018", "2019-07", etc.
- Oft gestempelt oder graviert auf Ober- oder Seitenseite

**Entscheidung:**
- **Vor 2010** → Blei-Antimon (Legacy)
- **2010 oder später** → Blei-Kalzium (Modern)

### Methode 2: Batterieetikett prüfen

**Suchen Sie nach diesen Kennzeichnungen:**

#### Blei-Kalzium-Indikatoren:
- "Calcium" oder "Ca/Ca"
- "Wartungsfrei" / "Maintenance Free"
- "MF" (Maintenance Free)
- "Sealed" / "Geschlossen" (aber nicht AGM)
- Keine abnehmbaren Kappen (oder versiegelte Stopfen)
- "Low Self-Discharge" / "Geringe Selbstentladung"

#### Blei-Antimon-Indikatoren:
- "Sb" oder "Antimon" / "Antimony"
- "Conventional" / "Konventionell"
- "Low Maintenance" / "Wartungsarm" (benötigt paradoxerweise MEHR Wartung)
- Abnehmbare Kappen zum Nachfüllen von Wasser
- "Add Water Only" / "Nur Wasser nachfüllen"

### Methode 3: Physische Inspektion

#### Blei-Kalzium-Batterie:
- **Kappen:** Versiegelt oder nur dekorativ (können nicht entfernt werden)
- **Oberseite:** Glatt, keine Öffnungen
- **Etikett:** "Nicht öffnen", "Sealed for life"
- **Gewicht:** Leichter für gleiche Kapazität
- **Erscheinungsbild:** Saubere Oberseite, keine Korrosion

#### Blei-Antimon-Batterie:
- **Kappen:** 6 abnehmbare Schraubkappen (eine pro Zelle)
- **Oberseite:** Einzelne Zellen sichtbar
- **Etikett:** Anleitung zum Nachfüllen von Wasser
- **Gewicht:** Schwerer
- **Erscheinungsbild:** Kann Säurereste/Korrosion auf Oberseite haben

### Methode 4: Ruhespannung messen

**Wichtig:** Batterie 2+ Stunden ohne Laden ruhen lassen

| Ruhespannung | Blei-Antimon | Blei-Kalzium |
|--------------|--------------|--------------|
| 12,8V | ~95% Ladung | ~100% Ladung |
| 12,6V | ~85% Ladung | ~90% Ladung |
| 12,4V | ~70% Ladung | ~75% Ladung |

Blei-Kalzium-Batterien zeigen typischerweise etwas niedrigere Ruhespannung für denselben Ladezustand.

### Methode 5: Fahrzeugjahr (für Autobatterien)

| Fahrzeugjahr | Standard-Batterietyp |
|--------------|---------------------|
| Vor 1996 | Blei-Antimon |
| 1996-2009 | Übergang (Etikett prüfen) |
| 2010+ | Blei-Kalzium |

**VW:** Blei-Kalzium ab 1996
**BMW:** Blei-Kalzium ab 2000
**Mercedes:** Blei-Kalzium ab 1998
**Audi:** Blei-Kalzium ab 1996
**Ford:** Blei-Kalzium ab 1997
**Andere Hersteller:** Meist 2000-2010

---

## Detaillierte Chemie-Erklärung

### Blei-Kalzium (Ca/Ca) - Moderne Batterien

**Elektrodenmaterial:** Blei-Kalzium-Legierung

**Eigenschaften:**
- Wartungsfrei (kein Wasserverlust)
- Geringe Selbstentladung (1 Jahr Standby)
- Längere Lebensdauer (6-10+ Jahre)
- Geschlossene Konstruktion
- Taschen-Separatoren (pocket separators)
- Höhere Ladespannungen erforderlich
- Empfindlich gegenüber Tiefentladung unter 50%
- Säureschichtung bei Tiefentladung

**Ladespannungen:**
| Stufe | Spannung |
|-------|----------|
| Bulk/Absorption (geschlossen) | 15,0-15,4V (Ziel: 15,2V) |
| Bulk/Absorption (Nasszelle) | 16,0-16,5V (Ziel: 16,2V) |
| Float | 13,5-13,8V |
| Ausgleich | NICHT empfohlen für geschlossen |

**Typische Anwendungen:**
- Moderne Autobatterien (2010+)
- Start-Stopp-Fahrzeuge
- Premium-Autobatterien
- USV-Systeme

---

### Blei-Antimon (Sb) - Legacy-Batterien

**Elektrodenmaterial:** Blei-Antimon-Legierung

**Eigenschaften:**
- Verträgt Tiefentladung besser
- Niedrigere Ladespannungen
- Einfacher zu rekonditionieren
- Erfordert regelmäßiges Nachfüllen von Wasser
- Hohe Selbstentladung (3 Monate Standby)
- Kürzere Lebensdauer (3-5 Jahre)
- Produziert mehr Gas beim Laden

**Ladespannungen:**
| Stufe | Spannung |
|-------|----------|
| Bulk/Absorption | 14,4-14,8V |
| Float | 13,5-13,8V |
| Ausgleich | 15,5-16,0V (empfohlen) |

**Typische Anwendungen:**
- Ältere Fahrzeuge (vor 2010)
- Traktionsbatterien
- Gabelstapler
- Wartbare "Konventionelle" Batterien

---

## Spezielle Batterietypen

### AGM (Absorbed Glass Mat)

**Technologie:** Elektrolyt in Glasfasermatten absorbiert

**Eigenschaften:**
- Vollständig versiegelt
- Auslaufsicher
- Kann in jeder Position montiert werden
- Niedrige Selbstentladung
- Höhere Leistungsabgabe
- Empfindlich gegen Überladung

**Ladespannungen:**
| Stufe | Spannung |
|-------|----------|
| Bulk/Absorption | 14,4-15,2V (Hersteller prüfen) |
| Float | 13,4-13,7V |

**Anwendungen:**
- Motorräder
- Wohnmobile
- Marine-Anwendungen
- Start-Stopp-Systeme (EFB)

### Gel-Batterien

**Technologie:** Elektrolyt als Gel gebunden

**Eigenschaften:**
- Vollständig versiegelt
- Sehr empfindlich gegen Überladung
- Hervorragend für Tiefentladungs-Zyklen
- Längste Lebensdauer bei richtigem Laden
- Niedrigste Ladespannungen erforderlich

**Ladespannungen:**
| Stufe | Spannung |
|-------|----------|
| Bulk/Absorption | 14,1-14,4V (NIEDRIG halten!) |
| Float | 13,5-13,8V |

**Anwendungen:**
- Solar-Speichersysteme
- Rollstühle
- Elektromobile
- Kritische Backup-Systeme

---

## Konfigurationsdateien verwenden

### Für Blei-Kalzium (Standard - Empfohlen für moderne Batterien)

```bash
# Standard-Konfig verwenden (bereits für Blei-Kalzium eingerichtet)
python3 src/charger_main.py

# Oder explizit angeben:
python3 src/charger_main.py --config config/charging_config.yaml
```

**Konfig-Datei:** `config/charging_config.yaml`
```yaml
battery:
  type: "lead_calcium_flooded"    # Oder lead_calcium_sealed
  chemistry: "lead_calcium"

charging:
  IUoU:
    absorption_voltage: 15.2      # Für geschlossen (sealed)
    # oder 16.2 für Nasszelle (flooded)
    float_voltage: 13.8
```

### Für Blei-Antimon (Legacy)

```bash
# Legacy-Konfig verwenden
python3 src/charger_main.py --config config/charging_config_lead_antimony.yaml
```

**Konfig-Datei:** `config/charging_config_lead_antimony.yaml`
```yaml
battery:
  type: "lead_antimony_flooded"
  chemistry: "lead_antimony"

charging:
  IUoU:
    absorption_voltage: 14.4      # Niedriger für Antimon
    float_voltage: 13.6
```

---

## Falsche Spannungen - Was passiert?

### Zu niedrige Spannung (14,4V auf Blei-Kalzium)

**Symptome:**
- Batterie erreicht nie 100% Ladung
- Ruhespannung bleibt unter 12,7V
- Kapazität nimmt über Zeit ab
- Frühzeitiger Batterieausfall (1-2 Jahre statt 6-10)

**Warum:**
Blei-Kalzium-Batterien benötigen höhere Spannung um vollständig zu laden. 14,4V reicht nur für ~90% Ladung. Die oberen 10% werden nie erreicht, was zu Sulfatierung führt.

**Ergebnis:** UNTERLADUNG (gefährlich für Batterielebensdauer)

### Zu hohe Spannung (15,2V auf Blei-Antimon)

**Symptome:**
- Übermäßige Gasung während Ladung
- Wasserspiegel sinkt schnell
- Batterie wird heiß
- Säureaustritt möglich
- Positive Platten können korrodieren

**Warum:**
Blei-Antimon-Batterien haben niedrigere Gasungsspannung. Bei 15,2V tritt übermäßige Elektrolyse auf, was Wasser in Wasserstoff und Sauerstoff spaltet.

**Ergebnis:** ÜBERLADUNG (aber weniger gefährlich als Unterladung)

---

## Testen Sie Ihre Batterie

### Ladungsakzeptanztest

1. **Vollständig laden** mit korrekter Spannung für Ihren Typ
2. **24 Stunden ruhen lassen** ohne Last
3. **Ruhespannung messen:**
   - Blei-Kalzium: Sollte 12,7-12,8V sein
   - Blei-Antimon: Sollte 12,6-12,7V sein
4. **Wenn niedriger:** Batterie akzeptiert möglicherweise keine vollständige Ladung

### Kapazitätstest

1. **Vollständig laden** mit korrekter Konfig
2. **Bekannte Last anwenden** (z.B. 5A Glühlampe)
3. **Messen wie lange** bis Spannung auf 10,5V fällt
4. **Berechnen:** Kapazität = Strom × Zeit
5. **Vergleichen** mit nomineller Kapazität

**Beispiel:**
- 5A Last für 15 Stunden = 75Ah
- Nominell 95Ah → Batterie bei ~79% Kapazität

---

## Häufige Fehler

### Fehler 1: Annahme alle 12V Batterien sind gleich

**Problem:** Verwendung von 14,4V für alle 12V Batterien

**Realität:**
- Moderne Batterien: 15,2-16,2V benötigt
- Legacy-Batterien: 14,4V korrekt
- Unterschied ist KRITISCH

### Fehler 2: Batteriejahr ignorieren

**Problem:** "Meine Batterie sieht wartungsfrei aus, also ist sie Kalzium"

**Realität:** Alte Batterien (vor 2010) sind wahrscheinlich Antimon, selbst wenn versiegelt

**Lösung:** IMMER Herstellungsdatum prüfen

### Fehler 3: Gasung als normal ansehen

**Problem:** "Alle Batterien gasen beim Laden"

**Realität:**
- Leichte Gasung: Normal für Nasszellen bei Absorption
- Übermäßige Gasung: Zu hohe Spannung
- Keine Gasung: Kann auf Unterladung hinweisen

### Fehler 4: Alle geschlossenen Batterien als AGM behandeln

**Problem:** AGM-Einstellungen für geschlossene Blei-Kalzium verwenden

**Realität:**
- Geschlossene Blei-Kalzium: 15,2V
- AGM: 14,4-14,7V (variiert nach Hersteller)
- NICHT dieselben Anforderungen

---

## Schnellreferenz-Tabelle

| Batterietyp | Herstellungsjahr | Ladespannung | Float | Wassernachfüllung | Typische Lebensdauer |
|-------------|------------------|--------------|-------|-------------------|---------------------|
| **Blei-Kalzium Geschlossen** | 2010+ | 15,2V | 13,8V | Nein | 6-10 Jahre |
| **Blei-Kalzium Nasszelle** | 2010+ | 16,2V | 13,8V | Selten | 6-10 Jahre |
| **Blei-Antimon** | Vor 2010 | 14,4V | 13,6V | Häufig | 3-5 Jahre |
| **AGM** | Beliebig | 14,7V | 13,5V | Nein | 5-8 Jahre |
| **Gel** | Beliebig | 14,2V | 13,6V | Nein | 8-12 Jahre |

---

## Weitere Hilfe

**Noch unsicher?**

1. **Etikett fotografieren** und Markierungen prüfen
2. **Herstellungsdatum finden** - Dies ist der beste Indikator
3. **Mit niedriger Spannung beginnen** (14,4V), dann beobachten:
   - Wenn Ruhespannung nicht 12,7V erreicht → Höhere Spannung versuchen
   - Wenn übermäßige Gasung → Spannung reduzieren
4. **Foren konsultieren** mit Batteriefoto und Markierungen

**Ressourcen:**
- [Deutsches Batterie-Technik-Wiki](https://wiki.w311.info/index.php?title=Batterie_Heute) - Vollständige technische Details
- [Microcharge Forum](https://www.microcharge.de/forum/) - Experten-Community
- [GitHub Issues](https://github.com/packerlschupfer/scpi-battery-charger/issues) - Projektspezifische Hilfe

---

## Zusammenfassung

**Wichtigste Punkte:**

1. **Herstellungsjahr ist Schlüsselindikator**
   - Vor 2010 = wahrscheinlich Blei-Antimon (14,4V)
   - 2010+ = wahrscheinlich Blei-Kalzium (15,2V)

2. **Falsche Spannung = Batterieschaden**
   - Zu niedrig: Niemals vollständig geladen, früher Tod
   - Zu hoch: Übermäßige Gasung, Wasserverlust

3. **Im Zweifelsfall:**
   - Standard-Konfig (Blei-Kalzium) für moderne Batterien verwenden
   - Legacy-Konfig für alte Batterien (vor 2010)
   - Ergebnisse beobachten und anpassen

4. **Die meisten "toten" Batterien brauchen nur die richtige Ladespannung!**

---

**Haben Sie Ihre Batterie identifiziert?**

→ Siehe [README.md](../README.de.md) für vollständige Installations- und Konfigurationsanleitung
→ Siehe [CHARGING_MODES.md](CHARGING_MODES.de.md) für Lademodi-Details
