# Experten-Batterieladungs-Leitfaden

**[English](EXPERT_CHARGING_GUIDE.md) | Deutsch**

Traditionelle Batterieladungs-Weisheit aus 150 Jahren Erfahrung mit Blei-Säure-Batterien.

**Quellen:** Deutsche Batterie-Forum Experten-Empfehlungen
- **Forum-Thread:** https://www.microcharge.de/forum/forum/thread/847-hochspannungsladung-von-bleiakkus
- **Technische Referenz:** https://wiki.w311.info/index.php?title=Batterie_Heute

## Die traditionelle Methode: Konstantstrom-Ladung

### Experten-Zitat

> "Die Stromladung ist die schnellste und sicherste Methode eine Batterie aufzuladen. Das wurde 150 Jahre lang so gemacht."

### Warum Konstantstrom?

**Die Batterie ist ein Speicher für elektrische Arbeit:**
- `Kapazität = Strom × Zeit` (Ah = A × h)
- Der Batterie konstanten Strom zu geben liefert genau was sie braucht
- Spannung ist eine Folge, nicht der Steuerparameter
- Konstantspannungs-Ladung kam später nur für **geschlossene Batterien** und **Bordladung im Fahrzeug** um Überladung zu verhindern

### Methode für offene (Nasszellen) Batterien

1. **Anfangsphase:** 10% der Kapazität (C/10)
   - Für 44Ah Batterie: 4,4A
   - Für 95Ah Batterie: 9,5A
   - Fortsetzen bis Gasung beginnt

2. **Abschlussphase:** 5% der Kapazität (C/20)
   - Für 44Ah Batterie: 2,2A
   - Für 95Ah Batterie: 4,75A
   - Fortsetzen bis Spannung ein Plateau erreicht

3. **Überwachung:** Spannung alle 2 Stunden prüfen
   - Wenn Spannung aufhört zu steigen → Batterie ist voll
   - Wenn Spannung fällt → Batterie ist voll
   - Batterie sollte handwarm sein, aber nicht heiß

4. **Ladeschlussspannung:**
   - Neue Batterie: 17-17,5V
   - Ältere Batterie (Sulfatierung, Dendriten): 16V oder weniger

5. **Nach der Ladung:**
   - Mit destilliertem oder entionisiertem Wasser auffüllen
   - Leitungswasser nur 1-2 Mal akzeptabel

## Ladezustand - Ruhespannung

**Nach 2+ Stunden Ruhe, kein Laden oder Entladen:**

### Nasszellen Blei-Kalzium Batterien

| SOC | Spannung | Säuredichte |
|-----|----------|-------------|
| 100% | 12,7V | 1,28 g/cm³ |
| 90% | 12,6V | 1,26 g/cm³ |
| 80% | 12,5V | 1,24 g/cm³ |
| 70% | 12,4V | 1,22 g/cm³ |
| 60% | 12,3V | 1,20 g/cm³ |
| 50% | 12,2V | 1,18 g/cm³ |
| 40% | 12,1V | - |
| 30% | 11,9V | - |
| 20% | 11,8V | 1,10 g/cm³ |
| 0-10% | 11,5V | 1,05 g/cm³ |

### AGM Batterien

AGM Batterien haben etwas höhere Ruhespannungen:

| SOC | Spannung |
|-----|----------|
| 100% | >12,9V |
| 90% | >12,75V |
| 80% | >12,65V |
| 70% | >12,50V |
| 60% | >12,40V |
| 50% | >12,25V |
| 20% | >11,80V |
| 0-10% | >10,50V |

## Kritische Schwellwerte

### 12,5V Warnung - Sofort laden!

**Wenn Ruhespannung auf 12,5V fällt (80% SOC), sofort laden!**
- Risiko permanenter Schäden bei weiterer Entladung
- Sulfatierung beschleunigt sich unter diesem Punkt
- Laut deutschem Technik-Diagramm: "Batterie sofort laden!"

### Ladespannungen nach Batterietyp

**Nasszellen/Flooded:** 14,4V (geschlossene Kappen) bis 17-17,5V (offene Kappen)
**AGM:** 14,8V
**Blei-Kalzium (PbCa):** 15,4V (geschlossen) bis 16,2V (Nasszelle)

**Nasszellen mit offenen Kappen:** 17-17,5V (Ladeschlussspannung)

## Säuredichte-Formeln

### Zellenspannung aus Säuredichte

```
Zellspannung = 0,84 + (Säuredichte in g/cm³)
```

**Beispiel:**
- Säuredichte = 1,28 g/cm³ → Zellenspannung = 2,12V → Batterie = 12,72V (6 Zellen)
- Säuredichte = 1,24 g/cm³ → Zellenspannung = 2,08V → Batterie = 12,48V

### Säuredichte aus Zellenspannung

```
Säuredichte = Zellenspannung - 0,84
Säuredichte = (Batteriespannung / 6) - 0,84
```

## Batteriegesundheits-Tests

### Ruhestrom-Test (Dendriten-Erkennung)

**Nach vollständiger Ladung, 14,5V Konstantspannung anlegen:**

Strom messen nach Stabilisierung (1 Stunde):
- **Gesunde Batterie (44-110Ah):** ≤10mA
- **Erhöht:** 10-20mA (akzeptabel)
- **Verdacht auf Dendriten:** >20mA
- **Schlecht:** >50mA (interne Kurzschlüsse)

**Hoher Strom zeigt an:**
1. Dendriten-Bildung (interne Kurzschlüsse)
2. Batterie lädt noch (länger warten)
3. Sulfatierung

### Spannungsabfall-Test (Selbstentladung)

**Nach vollständiger Ladung, Spannung über Zeit messen:**

| Zeit | Erwartete Spannung | Status |
|------|-------------------|--------|
| Tag 1-2 | 13,0V | Normale Beruhigung |
| Woche 1 | 12,9-12,8V | Gut |
| Woche 4 | 12,7-12,8V | Gesund |

**Schneller Spannungsabfall zeigt an:**
- Dendriten entladen die Batterie
- Interne Kurzschlüsse
- Bei täglicher Nutzung spielen Dendriten keine Rolle (ständig nachgeladen)

## Warum Konstantspannung später kam

### Historischer Kontext

**Ursprüngliche Methode (150 Jahre):** Konstantstrom
- **Verwendet:** Überall, von allen
- **Vorteile:** Direkt, einfach, was Batterien brauchen
- **Nachteil:** Erfordert Überwachung (Gasungs-Erkennung)

**Moderne Methode:** Konstantspannung (CC+CV)
- **Verwendet:** In Fahrzeugen, geschlossenen Batterien
- **Grund:** Verhindert Überladung wenn unbeaufsichtigt
- **Nachteil:** Langsamer, Strom nimmt ab, lädt möglicherweise nicht vollständig

### Für offene Batterien: Konstantstrom verwenden

Wenn Sie können:
1. Ventilkappen öffnen
2. Belüftung bereitstellen
3. Ladung überwachen

**Dann Konstantstrom verwenden!** Es ist schneller, sicherer und seit 150 Jahren bewährt.

## Entsulfatierung (Wiederherstellungs-Ladung)

**Für tief entladene oder vernachlässigte Batterien:**

1. **Methode:** Konstantstrom bei 1% der Kapazität
   - Für 44Ah: 0,44A
   - Für 95Ah: 0,95A

2. **Dauer:** Verlängert (Tage bis Wochen)

3. **Zweck:** Sulfatkristalle auf Platten aufbrechen

4. **Alternative:** Pulsladung bei höherer Spannung

## Warnung vor hohen Spannungen

**Niemals >15V bei geschlossenen AGM Batterien verwenden!**
- AGM verträgt: 14,8V
- Nasszelle: 15,4V (geschlossene Kappen)
- **Nasszelle mit offenen Kappen: 17-17,5V** (Experten-Methode)

**Die meisten AGM Batterien haben Öffnungsschrauben** (VARTA, Banner, Moll)
- Unter Etiketten nach Schrauben suchen
- Falls gefunden, können höhere Spannungen mit offenen Kappen verwendet werden

## Tom's erweiterte Conditioning-Methode

### Verlängerte Hochspannungs-Konditionierung (15,4-15,6V für 24-48h)

**Quelle:** Forum-Experte Tom's Felderfahrung mit Problem-Batterien

**Problem:** Batterie hält Ladung nicht richtig
- Ruhespannung fällt schnell
- Zeigt gute Spannung direkt nach Ladung
- Versagt innerhalb von Stunden oder Tagen

**Traditionelle Lösung:**
- Auf 14,4V laden (nach Mainstream-Anleitungen)
- Batterie erscheint geladen aber versagt schnell

**Tom's Entdeckung:**
- 15,4-15,6V kontinuierlich für 24-48 Stunden anlegen
- Strom überwachen (sollte fallen während Batterie lädt)
- Ergebnis: Ruhespannung verbessert sich von 12,6V → 13,3V
- Batterie hält Ladung viel besser

### Kritische Überwachung während Conditioning

**Elektrolyse-Erkennung:**
- Normal: Strom fällt über Zeit während Batterie lädt
- Warnung: Strom bleibt hoch (>1A) für längere Zeit (>1 Stunde)
- Hoher anhaltender Strom = Wasser-Elektrolyse (Wasserverlust), nicht Laden
- Aktion: Wasserstand prüfen, Spannung reduzieren wenn übermäßig

**Gasungs-Schwelle:**
- Schlechte Batterie: Beginnt bei 14,7V zu gasen (degradiert)
- Gesunde Batterie: Gast nur über 15,8V
- Test verfügbar um Batteriegesundheit zu bestimmen

### Float-Spannungs-Warnung - Gitter-Korrosion

**Problem:** Kontinuierliche 13,8V Float-Ladung
- Verursacht positive Gitter-Korrosion
- Batterie versagt in ~1,5 Jahren
- Häufig bei immer angeschlossenen Ladegeräten

**Lösung:**
1. **Für täglich gefahrene Fahrzeuge:** Float ganz deaktivieren
   - Lichtmaschine bietet Erhaltungsladung
   - Nur gelegentlich tiefenladen

2. **Für Lagerung:** Float-Spannung senken
   - Maximum 13,5V verwenden (nicht 13,8V)
   - Oder periodisches Conditioning stattdessen (15,5V für 24h monatlich)

3. **Für Standby-Batterien:** Periodisches Conditioning
   - Besser als kontinuierliche Float-Ladung
   - 15,5V für 24h alle 2-4 Wochen
   - Verhindert Sulfatierung und erhält Kapazität

### Warum Conditioning funktioniert

Aus traditioneller Batterie-Wartung:
- Entfernt leichte Sulfatierung
- Gleicht Zellenspannungen aus
- Aktiviert Plattenmaterial
- Verbessert Elektrolyt-Mischung (durch Gasung)
- Stellt verlorene Kapazität wieder her

## Umsetzung in diesem System

### Verfügbare Lademodi

1. **CC (Konstantstrom)** - Reine traditionelle Methode
   - Empfohlen für offene Nasszellen
   - Verwendet Plateau-Erkennung statt Spannungsgrenze
   - 150 Jahre bewährte Methode

2. **IUoU (3-Stufen)** - Moderner CC+CV Hybrid
   - Gut für geschlossene Batterien
   - Bulk (CC) + Absorption (CV) + Float
   - Automatische Übergänge
   - **Aktualisiert:** Float-Spannung auf 13,5V reduziert (war 13,8V)

3. **Conditioning (Tom's Methode)** - Verlängerte Hochspannungs-Wartung
   - 15,4-15,6V für 24-48 Stunden
   - Für Batterien die Ladung nicht halten
   - Beinhaltet Elektrolyse-Erkennung
   - Besser als kontinuierliche Float-Ladung für Lagerung

4. **CV (Konstantspannung)** - Einfache Wartung
   - Gut für nachgeladene Batterien
   - Sanftes Laden

5. **Pulse (Puls)** - Entsulfatierungs-Modus
   - Zur Wiederherstellung vernachlässigter Batterien

### Sicherheitsfunktionen

- **12,5V Warnung** - Kritische Nachlade-Schwelle
- **Spannungsplateau-Erkennung** - Auto-Stopp für CC-Modus
- **Energiebilanzierung** - Ah abgegeben vs. gespeichert verfolgen (83% Effizienz)
- **Ruhestrom-Test** - Dendriten-Erkennung bei 14,5V (gesund: ≤10mA)
- **Gasungs-Schwellen-Test** - Batteriegesundheit bestimmen (schlecht: 14,7V, gut: >15,8V)
- **Elektrolyse-Überwachung** - Wasserverlust während Conditioning erkennen
- **SOC-Tabellen** - Für Nasszellen und AGM Batterien
- **Säuredichte-Rechner** - Spannung ↔ Säuredichte Umrechnung
- **Gitter-Korrosions-Vorbeugung** - Reduzierte Float-Spannung (13,5V)

## Praktische Tipps

### Vor der Ladung

1. Wasserstand prüfen (bedeckt Platten?)
2. Ventilkappen öffnen falls Nasszelle
3. Belüftung sicherstellen
4. Klemmen reinigen
5. Ruhespannung und Säuredichte messen

### Während der Ladung

1. Temperatur überwachen (handwarm OK, heiß = Problem)
2. Auf Gasung achten (normal über 15,8V für Ca-Ca)
3. Spannung alle 2 Stunden prüfen
4. Nach Plateau suchen (Spannung hört auf zu steigen)

### Nach der Ladung

1. 1-2 Stunden ruhen lassen
2. Endspannung messen (sollte 12,7-12,8V sein)
3. Wasser nachfüllen falls nötig
4. Säurereste reinigen
5. Ventilkappen schließen
6. Säuredichte testen (sollte 1,265-1,280 sein)

### Langzeit-Wartung

1. Spannung wöchentlich messen
2. Bei 12,5V nachladen (nicht warten!)
3. Monatlich: Säuredichte prüfen
4. Jährlich: Ruhestrom-Test durchführen
5. Sauber und trocken halten

## Referenzen

- **Technisches Wiki:** https://wiki.w311.info/index.php?title=Batterie_Heute
- **150 Jahre Erfahrung:** Traditionelle Konstantstrom-Methode
- **Moderne Sicherheit:** Spannungsplateau-Erkennung, automatische Überwachung
- **Das Beste aus beiden Welten:** CC-Modus mit intelligenter Elektronik

## Zusammenfassung

**Wichtigste Erkenntnisse:**

1. **Konstantstrom ist die bewährte Methode** - 150 Jahre Erfahrung
2. **12,5V ist kritisch** - Sofort laden bei diesem Wert
3. **Float-Spannung niedrig halten** - 13,5V statt 13,8V um Gitterkorrosion zu vermeiden
4. **Conditioning hilft** - 15,4-15,6V für 24-48h bei Problem-Batterien
5. **Für offene Batterien** - Hohe Spannungen (17-17,5V) sind normal und sicher

**Diese Software implementiert traditionelle Weisheit mit moderner Sicherheit!**
