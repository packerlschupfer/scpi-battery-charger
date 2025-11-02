# Lademodi-Leitfaden

**[English](CHARGING_MODES.md) | Deutsch**

Detaillierte Erklärung aller Lademodi, wann sie verwendet werden sollten und wie sie funktionieren.

## Übersicht

Das Batterieladegerät unterstützt 4 Lademodi:

1. **IUoU (3-Stufen)** - Empfohlen für reguläres Laden
2. **CV (Konstantspannung)** - Einfache Erhaltungsladung
3. **Pulse (Puls)** - Wiederherstellung und Entsulfatierung
4. **Trickle (Erhaltungsladung)** - Langzeit-Lagerungswartung

---

## IUoU-Modus (3-Stufen-Ladung)

**Empfohlen für:** Reguläres Batterieladen, optimal für Blei-Säure-Batterien

### Wie es funktioniert

IUoU-Ladung besteht aus drei aufeinanderfolgenden Stufen:

```
Bulk (I) → Absorption (Uo) → Float (U)
```

### Stufe 1: Bulk-Ladung (Konstantstrom)

**Dauer:** Bis Absorptionsspannung erreicht
**Spannung:** Steigt von Batteriespannung zu Absorptionsspannung
**Strom:** Konstant (z.B. 4,75A für 95Ah Batterie)

```
Zeit:     0s ─────────────────────────→ Variabel
Spannung: 12,0V ─────────────────────→ 14,4V
Strom:    4,75A ══════════════════════ 4,75A (konstant)
```

**Was passiert:**
- Netzteil läuft im Konstantstrom-Modus (CC)
- Batteriespannung steigt allmählich
- Hauptteil der Ladung wird hier abgegeben (~60% der Gesamtladung)
- Schnellste Ladestufe

**Übergang:** Wenn Spannung Absorptionsspannung erreicht (14,4V ± 0,1V)

### Stufe 2: Absorption (Konstantspannung)

**Dauer:** Bis Strom unter Schwellwert fällt ODER Timeout (2 Stunden)
**Spannung:** Konstant bei Absorptionsspannung (14,4V)
**Strom:** Nimmt allmählich ab

```
Zeit:     0s ─────────────────────────→ ~2h max
Spannung: 14,4V ══════════════════════ 14,4V (konstant)
Strom:    4,75A ─────────────────────→ <1,0A
```

**Was passiert:**
- Netzteil läuft im Konstantspannungs-Modus (CV)
- Strom nimmt natürlich ab während Batterie sich füllt
- Nachladung, letzte ~30% der Ladung
- Kritisch für Batterielebensdauer

**Übergang:** Wenn Strom unter Schwellwert fällt (z.B. 1,0A) ODER Timeout

### Stufe 3: Float (Erhaltung)

**Dauer:** Unbegrenzt (oder bis manuell gestoppt)
**Spannung:** Konstant bei Float-Spannung (13,6V)
**Strom:** Sehr niedrig (<0,5A)

```
Zeit:     0s ─────────────────────────→ ∞
Spannung: 13,6V ══════════════════════ 13,6V (konstant)
Strom:    <0,5A ══════════════════════ <0,5A
```

**Was passiert:**
- Netzteil hält sichere Float-Spannung
- Kompensiert Selbstentladung
- Kann unbegrenzt angeschlossen bleiben
- Letzte ~10% der Ladung

**Übergang:** Manueller Stopp oder Ausschalten

### Konfiguration

```yaml
charging:
  IUoU:
    bulk_current: 4.75              # A - Ladestrom (0,05C für 95Ah)
    absorption_voltage: 14.4        # V - Bulk/Absorptionsspannung
    float_voltage: 13.6             # V - Erhaltungsspannung
    absorption_current_threshold: 1.0  # A - Schwelle für Wechsel zu Float
    absorption_timeout: 7200        # s - Max. Absorptionszeit (2h)
    enable_float: true              # Float-Stufe aktivieren
```

### Spannungsrichtlinien nach Batterietyp

**WICHTIG: Moderne Batterien (ab 2010) verwenden Blei-Kalzium-Chemie und benötigen HÖHERE Spannungen!**

**Blei-Kalzium (Modern, ab 2010):**
- Bulk/Absorption: 15,0 - 15,4V (geschlossen: 15,2V, Nasszelle: 16,2V)
- Float: 13,5 - 13,8V

**Blei-Antimon (Legacy, vor 2010):**
- Bulk/Absorption: 14,4 - 14,8V
- Float: 13,5 - 13,8V

**AGM/Gel (Geschlossen):**
- Bulk/Absorption: 14,4 - 15,2V (Herstellerspezifikationen prüfen)
- Float: 13,4 - 13,7V

**Hinweis:** Die Beispiele in diesem Dokument verwenden aus Gründen der Einfachheit Legacy-14,4V-Werte. Für moderne Blei-Kalzium-Batterien verwenden Sie 15,2V für geschlossene oder 16,2V für Nasszellen. Siehe Haupt-README.md für detaillierte Batterietyp-Identifikation.

### Typischer Zeitplan

**Beispiel: 95Ah Batterie bei 50% Entladung**

| Stufe | Dauer | Ladung hinzugefügt |
|-------|-------|--------------------|
| Bulk | 6 Stunden | ~28,5Ah (60%) |
| Absorption | 2 Stunden | ~14,3Ah (30%) |
| Float | Laufend | ~4,8Ah (10%) |
| **Gesamt** | **~8 Stunden** | **~47,5Ah** |

---

## CV-Modus (Konstantspannung)

**Empfohlen für:** Einfaches Laden, Wartung, Nachladung

### Wie es funktioniert

Einstufige Konstantspannungsladung. Einfachste Methode.

```
Zeit:     0s ─────────────────────────→ Variabel
Spannung: 13,8V ══════════════════════ 13,8V (konstant)
Strom:    9,5A ──────────────────────→ <0,5A (nimmt natürlich ab)
```

**Was passiert:**
- Netzteil hält konstante Spannung (z.B. 13,8V)
- Strom startet hoch, nimmt allmählich ab
- Batterie lädt bis Strom auf Minimum fällt
- Stoppt automatisch wenn vollständig

### Konfiguration

```yaml
charging:
  CV:
    voltage: 13.8          # V - Bei dieser Spannung halten
    max_current: 4.0       # A - Strombegrenzung
    min_current: 0.5       # A - Vollständig wenn darunter
```

### Wann zu verwenden

**Gut für:**
- Teilweise geladene Batterie nachladen
- Erhaltungsladung
- Einfache Bedienung
- Ältere Batterien die hohe Spannung nicht vertragen

**Nicht ideal für:**
- Tiefentladungs-Wiederherstellung
- Schnellladung
- Präziser Ladezustand

### Vergleich zu IUoU

| Eigenschaft | CV | IUoU |
|-------------|----|----- |
| Geschwindigkeit | Langsamer | Schneller |
| Komplexität | Einfach | Erweitert |
| Batterielebensdauer | Gut | Am besten |
| Tiefentladung | Ausreichend | Optimal |

---

## Pulse-Modus (Pulsladung/Entsulfatierung)

**Empfohlen für:** Sulfatierte Batterien, Wiederherstellung, alte Batterien

### Wie es funktioniert

Wechselt zwischen Hochspannungsimpulsen und Ruhepausen.

```
Zyklus 1:  Impuls (30s) ─→ Ruhe (30s)
Zyklus 2:  Impuls (30s) ─→ Ruhe (30s)
...
Zyklus 20: Impuls (30s) ─→ Ruhe (30s) ─→ Vollständig
```

**Impuls-Phase:**
```
Spannung: 15,5V (hoch!)
Strom:    9,5A (typisch)
Dauer:    30s
```

**Ruhe-Phase:**
```
Spannung: 13,0V (niedrig)
Strom:    0,1A (minimal)
Dauer:    30s
```

### Was ist Sulfatierung?

Blei-Säure-Batterien entwickeln Bleisulfatkristalle im Laufe der Zeit, besonders wenn:
- Entladen gelagert
- Wiederholt unterladen
- Gealterte Batterien

Sulfatierung reduziert Kapazität und Leistung.

### Wie Pulsladung hilft

Hochspannungsimpulse können:
- Sulfatkristalle aufbrechen
- Etwas verlorene Kapazität wiederherstellen
- Batteriereaktion verbessern
- KEIN WUNDERMITTEL - kann 10-30% helfen

### Konfiguration

```yaml
charging:
  Pulse:
    pulse_voltage: 15.5      # V - Hohe Impulsspannung
    pulse_current: 9.5       # A - Impulsstrom (C/10 Rate für 95Ah)
    rest_voltage: 13.0       # V - Ruhespannung
    pulse_duration: 30       # s - Impulszeit
    rest_duration: 30        # s - Ruhezeit
    max_cycles: 20           # Anzahl der Impulszyklen
```

### Sicherheitshinweise

**WICHTIG:**
- 15,5V ist HOCH für 12V Batterie
- Kann Gasung verursachen (Wasserstofffreisetzung)
- NICHT bei AGM/Gel verwenden ohne Recherche
- Nur in gut belüftetem Bereich verwenden
- Batterietemperatur überwachen
- Nicht für reguläres Laden

### Wann zu verwenden

**Puls-Modus versuchen wenn:**
- Batterie hält Ladung nicht
- Kapazität deutlich reduziert
- Batterie wurde entladen gelagert
- Vor Austausch alter Batterie

**Nicht verwenden für:**
- Reguläres Laden
- Neue Batterien
- Geschlossene AGM/Gel (Spezifikationen zuerst prüfen)
- Hohe Temperaturbedingungen

### Erwartete Ergebnisse

- **Bester Fall:** 20-30% Kapazitätswiederherstellung
- **Typisch:** 10-15% Verbesserung
- **Schlechtester Fall:** Keine Verbesserung (Batterie zu weit hinüber)

---

## Trickle-Modus (Erhaltungsladung für Lagerung)

**Empfohlen für:** Langzeitlagerung, Saisonfahrzeuge, Backup-Batterien

### Wie es funktioniert

Sehr niedriger Strom, niedrige Spannungs-Erhaltungsladung.

```
Zeit:     0s ─────────────────────────→ ∞
Spannung: 13,5V ══════════════════════ 13,5V (konstant)
Strom:    0,5A ═══════════════════════ 0,5A (konstant)
```

**Was passiert:**
- Kompensiert Selbstentladung
- Verhindert Sulfatierung während Lagerung
- Sicher für monatelanges Anschließen
- Sehr schonend für Batterie

### Konfiguration

```yaml
charging:
  Trickle:
    voltage: 13.5          # V - Erhaltungsspannung
    current: 0.5           # A - Niedriger Strom
```

### Wann zu verwenden

**Perfekt für:**
- Winter-Fahrzeuglagerung (3-6 Monate)
- Backup-Stromversorgungssysteme
- Saisonale Ausrüstung (Boot, Wohnmobil, Motorrad)
- Vollgeladene Batterie erhalten

**Nicht für:**
- Entladene Batterie laden (zu langsam)
- Schnellladung benötigt
- Aktiv genutzte Fahrzeuge

### Float vs Trickle

| Eigenschaft | Float (IUoU) | Trickle |
|-------------|--------------|---------|
| Spannung | 13,6V | 13,5V |
| Strom | Variabel (<0,5A) | Fest (0,5A) |
| Verwendung | Nach vollständiger Ladung | Langzeitlagerung |
| Start | Nach IUoU vollständig | Jederzeit |

---

## Den richtigen Modus wählen

### Entscheidungsbaum

```
Ist Batterie tief entladen? (< 12,0V)
├─ JA → IUoU-Modus (beste Wiederherstellung)
└─ NEIN → Ist Batterie sulfatiert/alt?
    ├─ JA → Pulse-Modus zuerst versuchen, dann IUoU
    └─ NEIN → Was ist Ihr Ziel?
        ├─ Schnellladung → IUoU-Modus
        ├─ Einfache Erhaltung → CV-Modus
        └─ Lagerung (Wochen/Monate) → Trickle-Modus
```

### Schnellreferenz

| Situation | Empfohlener Modus | Alternative |
|-----------|-------------------|-------------|
| Tote Batterie (< 11,5V) | IUoU | CV |
| Reguläres Laden | IUoU | CV |
| Erhaltung | CV oder Trickle | IUoU Float |
| Lagerung (> 1 Monat) | Trickle | CV |
| Alte/sulfatierte Batterie | Pulse → IUoU | CV |
| Schnelle Nachladung | CV | IUoU |
| Winterlagerung | Trickle | CV |

---

## Ladezeiten

**Ungefähre Zeiten für 95Ah Batterie:**

| Modus | 50% Entladen | 80% Entladen |
|------|--------------|--------------|
| IUoU @ 4,75A | ~8 Stunden | ~14 Stunden |
| CV @ 3,8V, 4A | ~10 Stunden | ~18 Stunden |
| Pulse (Wiederherstellung) | ~10 Stunden | Nicht empfohlen |
| Trickle @ 0,5A | ~95 Stunden | ~152 Stunden |

**Hinweis:** Zeiten sind Schätzungen. Tatsächliche Zeit hängt ab von:
- Batteriezustand und Alter
- Temperatur
- Früherer Ladeverlauf
- Batteriechemie

---

## Sicherheitsrichtlinien

### Spannungsgrenzen

**Empfohlene Ladespannungen für 12V Batterie:**
- Blei-Kalzium Nasszelle (modern): 16,2V Absorption, 17,0V absolutes Maximum
- Blei-Kalzium Geschlossen (modern): 15,2V Absorption, 16,5V absolutes Maximum
- Blei-Antimon (legacy): 14,4-14,8V Absorption, 15,5V absolutes Maximum
- AGM/Gel (geschlossen): 14,1-15,2V (Spezifikationen prüfen), 15,5V absolutes Maximum

**Konfigurierte Sicherheitsgrenze:**
```yaml
safety:
  absolute_max_voltage: 16.5  # Für geschlossenes Blei-Kalzium
  # 17,0 für Blei-Kalzium Nasszelle verwenden
  # 15,5 für Legacy Blei-Antimon verwenden
```

### Stromgrenzen

**Hardware-Grenzen nach Modell:**
- SPE3102/SPE3103: 10A Maximum
- SPE6103: 10A Maximum
- SPE6205: 20A Maximum

**Empfohlen nach Batteriekapazität:**
- C/10 Rate = Kapazität / 10 (z.B. 95Ah / 10 = 9,5A) - Standard-Rate
- C/20 Rate = Kapazität / 20 (z.B. 95Ah / 20 = 4,75A) - Sanfter/langsamer

**Für 95Ah Batterie mit SPE6205:**
- Sanft: 4,75A (C/20)
- Standard: 9,5A (C/10) - empfohlen
- Maximum: 20A (Hardware-Limit, nicht empfohlen für Batterielebensdauer)

### Temperatur

**Sicherer Ladebereich:**
- Minimum: 0°C (32°F) - Laden erzeugt Wärme
- Maximum: 45°C (113°F) - kann Batterie beschädigen

**Unter 0°C:** Nicht laden (interner Widerstand zu hoch)
**Über 45°C:** Laden sofort stoppen

### Belüftung

**WARNUNG: Nasszellen produzieren Wasserstoffgas beim Laden**

Anforderungen:
- Gut belüfteter Bereich
- Keine Funken oder Flammen in der Nähe
- Niemals in geschlossenem Behälter laden
- Besonders wichtig während:
  - Absorptionsstufe (Gasung)
  - Pulse-Modus (hohe Gasung)

---

## Ladefortschritt überwachen

### Spannungsindikatoren

**Während IUoU-Modus:**
- 12,0-12,5V: Start (Bulk)
- 12,5-14,0V: Bulk-Ladung
- 14,0-14,4V: Nähert sich Absorption
- 14,4V (stabil): Absorptionsstufe
- 13,6V (stabil): Float-Stufe

### Stromindikatoren

**Bulk-Stufe:** Strom konstant bei Sollwert
**Absorptionsstufe:** Strom nimmt allmählich ab
**Float-Stufe:** Sehr niedriger Strom (<0,5A)

### Abschlusszeichen

**Batterie ist voll wenn:**
1. IUoU: Float-Stufe erreicht
2. CV: Strom unter min_current gefallen
3. Pulse: Alle Zyklen abgeschlossen
4. Trickle: Unbegrenzte Erhaltung

---

## Erweiterte Themen

### Temperaturkompensation

**Derzeit nicht implementiert**, aber Standard ist:
- -3mV pro °C pro Zelle
- Für 6-Zellen 12V Batterie: -18mV/°C
- Beispiel: Bei 30°C Absorptionsspannung um 0,18V reduzieren

### Ausgleichsladung

**Derzeit nicht implementiert**, aber für Nasszellen:
- Periodische Hochspannungsladung (15,5V)
- Gleicht Zellenspannungen aus
- Verhindert Schichtung
- Nur für Nasszellen, nicht AGM/Gel

### Ladezustand (SOC) Schätzung

**Grobe spannungsbasierte SOC (in Ruhe):**
- 12,7V+ = 100%
- 12,5V = 75%
- 12,3V = 50%
- 12,1V = 25%
- 11,9V = 0%

**Hinweis:** Spannung während des Ladens ist NICHT genau für SOC

---

## Fehlerbehebung

### Laden wird nie vollständig

**Mögliche Ursachen:**
- Batteriekapazitätsverlust (hohes Alter)
- Hohe Selbstentladung (interner Kurzschluss)
- Absorptionsstrom-Schwelle zu niedrig

**Lösungen:**
- `absorption_current_threshold` auf 1,5A erhöhen
- `absorption_timeout` reduzieren wenn zu lange gewartet wird
- Batterieaustausch erwägen wenn sehr alt

### Batterie wird heiß

**Normal:** Leichte Erwärmung während Laden
**Problem:** Heiß bei Berührung (> 45°C)

**Maßnahmen:**
1. Laden sofort stoppen
2. Belüftung prüfen
3. Ladestrom reduzieren
4. Auf internen Kurzschluss prüfen
5. Kann auf defekte Batterie hinweisen

### Spannung erreicht Ziel nicht

**Mögliche Ursachen:**
- Schwere Last angeschlossen
- Batterie sulfatiert
- Schlechte Verbindungen (Spannungsabfall)

**Lösungen:**
1. Lasten trennen
2. Verbindungen prüfen und reinigen
3. Pulse-Modus für Sulfatierung versuchen
4. Netzteilausgang mit Multimeter überprüfen

---

## Siehe auch

- [README.md](../README.de.md) - Hauptdokumentation (Deutsch)
- [MQTT_API.md](MQTT_API.md) - MQTT-Steuerungsreferenz (Englisch)
- [HOME_ASSISTANT.md](HOME_ASSISTANT.md) - Home Assistant Integration (Englisch)
