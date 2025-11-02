# OWON OEL1530 Elektronische Last Integration

**[English](OEL1530_INTEGRATION.md) | Deutsch**

Integrationsleitfaden zum Hinzufügen der OWON OEL1530 elektronischen Last zum Batterietest-System.

## Hardware-Übersicht

**OWON OEL1530 Spezifikationen:**
- Leistung: 300W kontinuierlich
- Spannung: 0-150V
- Strom: 0-30A
- Auflösung: 1mV / 1mA
- Anstiegsrate: Bis zu 2A/μs
- Dynamischer Modus: 5kHz
- Display: 2,8" LCD
- Steuerung: USB, RS232, RS485

**Eingebaute Funktionen:**
- Batterie-Entladungstest-Modus
- OCP-Test (Überstromschutz)
- OPP-Test (Überleistungsschutz)
- Fernkompensation (Kelvin-Messung)
- Direkte Bananenstecker-Anschlüsse

---

## Physische Verbindungen

### Basis-Setup (Manuelles Umschalten)

```
Lademodus:
┌─────────────┐
│  SPE6205    │ (Netzteil)
│   60V 20A   │
└──┬──────┬───┘
   │ ROT  │ SCHWARZ
   ↓      ↓
┌──●──────●───┐
│   Batterie  │
│   95Ah 12V  │
└─────────────┘

Entladungsmodus:
┌─────────────┐
│  Batterie   │
│   95Ah 12V  │
└──┬──────┬───┘
   │ ROT  │ SCHWARZ
   ↓      ↓
┌──●──────●───┐
│  OEL1530    │ (Elektronische Last)
│   300W      │
└─────────────┘
```

**Manueller Betrieb:**
1. Netzteil-Bananenstecker von Batterie trennen
2. Last-Bananenstecker an Batterie anschließen
3. Entladungstest durchführen
4. Last trennen
5. Netzteil zum Laden wieder anschließen

### Erweitertes Setup (Relais-Umschaltung)

```
                   SPE6205 (Netzteil)
                       ↓
                   ┌───●───┐
                   │ Relais│ (DPDT-Relais)
                   └───┬───┘
                       ↓
                   ┌───●───┐
                   │Batterie│
                   └───┬───┘
                       ↓
                   ┌───●───┐
                   │ Relais│ (DPDT-Relais)
                   └───┬───┘
                       ↓
                   OEL1530 (Last)

Gesteuert durch Raspberry Pi GPIO
```

**Vorteile:**
- Automatische Umschaltung
- Kein manuelles Kabelwechseln
- Vollständig unbeaufsichtigtes Testen
- Sicherheits-Verriegelungen

---

## Software-Integration

### Elektronische Last Treiber

**Datei:** `src/owon_load.py`

```python
"""
OWON OEL1530 Elektronische Last Treiber
"""

import serial
import time
import logging

logger = logging.getLogger(__name__)


class OwonLoad:
    """Treiber für OWON OEL1530 elektronische Last."""

    def __init__(self, port: str = '/dev/ttyUSB1', baudrate: int = 115200):
        """
        Elektronische Last initialisieren.

        Args:
            port: Serieller Port (z.B. /dev/ttyUSB1)
            baudrate: Kommunikationsgeschwindigkeit
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self._connected = False

    def connect(self) -> bool:
        """Mit elektronischer Last verbinden."""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=5.0
            )
            time.sleep(0.5)

            # Verbindung testen
            identity = self.identify()
            if identity:
                logger.info(f"Verbunden mit: {identity}")
                self._connected = True
                return True

            return False

        except Exception as e:
            logger.error(f"Verbindung fehlgeschlagen: {e}")
            return False

    def identify(self) -> str:
        """Geräteidentifikation abrufen."""
        return self._query("*IDN?")

    def set_mode(self, mode: str):
        """
        Betriebsmodus setzen.

        Args:
            mode: CC, CV, CR, CP, BATT (Batterie-Entladung)
        """
        self._send(f"MODE {mode}")

    def set_current(self, current: float):
        """Konstantstrom setzen (CC-Modus)."""
        self._send(f"CURR {current:.3f}")

    def set_voltage(self, voltage: float):
        """Konstantspannung setzen (CV-Modus)."""
        self._send(f"VOLT {voltage:.3f}")

    def enable_load(self):
        """Last aktivieren (Strom senken starten)."""
        self._send("LOAD ON")

    def disable_load(self):
        """Last deaktivieren (Strom senken stoppen)."""
        self._send("LOAD OFF")

    def measure_voltage(self) -> float:
        """Spannung über Last messen."""
        response = self._query("MEAS:VOLT?")
        return float(response)

    def measure_current(self) -> float:
        """Strom durch Last messen."""
        response = self._query("MEAS:CURR?")
        return float(response)

    def measure_power(self) -> float:
        """Leistungsaufnahme messen."""
        response = self._query("MEAS:POW?")
        return float(response)

    # Batterie-Entladungsmodus
    def setup_battery_test(
        self,
        discharge_current: float,
        cutoff_voltage: float,
        capacity_limit: float = 0
    ):
        """
        Batterie-Entladungstest einrichten.

        Args:
            discharge_current: Entladestrom in A
            cutoff_voltage: Abschaltspannung in V
            capacity_limit: Optionale Kapazitätsgrenze in Ah (0 = keine Grenze)
        """
        self._send("MODE BATT")
        self._send(f"BATT:CURR {discharge_current:.3f}")
        self._send(f"BATT:CUTOFF {cutoff_voltage:.3f}")

        if capacity_limit > 0:
            self._send(f"BATT:CAP {capacity_limit:.3f}")

    def start_battery_test(self):
        """Batterie-Entladungstest starten."""
        self._send("BATT:START")

    def get_battery_test_status(self) -> dict:
        """
        Batterie-Teststatus abrufen.

        Returns:
            Wörterbuch mit Testfortschritt
        """
        voltage = self.measure_voltage()
        current = self.measure_current()
        capacity = float(self._query("BATT:CAP?"))  # Ah entladen
        elapsed = float(self._query("BATT:TIME?"))  # Sekunden

        return {
            'voltage': voltage,
            'current': current,
            'capacity_ah': capacity,
            'elapsed_time': elapsed,
            'running': self._query("BATT:STAT?") == "RUN"
        }

    def _send(self, command: str):
        """Befehl an Last senden."""
        if not self._connected:
            raise RuntimeError("Nicht mit Last verbunden")

        cmd_bytes = f"{command}\n".encode('utf-8')
        self.serial.write(cmd_bytes)
        self.serial.flush()
        time.sleep(0.05)

    def _query(self, command: str) -> str:
        """Abfrage senden und Antwort lesen."""
        if not self._connected:
            raise RuntimeError("Nicht mit Last verbunden")

        self.serial.reset_input_buffer()
        self._send(command)

        time.sleep(0.1)
        response = b''
        while self.serial.in_waiting:
            response += self.serial.read(self.serial.in_waiting)
            time.sleep(0.05)

        return response.decode('utf-8').strip()

    def disconnect(self):
        """Von Last trennen."""
        if self.serial:
            self.disable_load()
            self.serial.close()
            self._connected = False
```

---

## Vollständiger Batterietest-Workflow

### Automatisierter Kapazitätstest

```python
def full_capacity_test(battery_capacity_ah: float = 95):
    """
    Vollständiger Batterie-Kapazitätstest.

    1. Batterie auf 100% laden
    2. Ruhephase
    3. Entladen bis Abschaltspannung
    4. Kapazität und Gesundheit berechnen
    """

    # Schritt 1: Vollständig laden
    print("Schritt 1: Batterie auf 100% laden...")
    psu = OwonPSU('/dev/ttyUSB0')
    psu.connect()

    charger = BatteryCharger(psu)
    charger.charge_IUoU()  # Vollständiger IUoU-Ladezyklus

    psu.disconnect()
    print("✓ Laden abgeschlossen")

    # Schritt 2: Ruhephase (2 Stunden)
    print("\nSchritt 2: Ruhephase (2 Stunden)...")
    time.sleep(7200)
    print("✓ Ruhe abgeschlossen")

    # Schritt 3: Entladungstest
    print("\nSchritt 3: Entladungs-Kapazitätstest...")
    load = OwonLoad('/dev/ttyUSB1')
    load.connect()

    # Test einrichten: C/20-Rate (4,75A), Abschaltung bei 10,5V
    discharge_rate = battery_capacity_ah / 20  # C/20
    load.setup_battery_test(
        discharge_current=discharge_rate,
        cutoff_voltage=10.5
    )

    # Test starten
    load.start_battery_test()
    print(f"  Entladung mit {discharge_rate:.2f}A bis 10,5V")

    # Fortschritt überwachen
    start_time = time.time()
    while True:
        status = load.get_battery_test_status()

        if not status['running']:
            break

        print(f"  {status['voltage']:.2f}V, "
              f"{status['current']:.2f}A, "
              f"{status['capacity_ah']:.2f}Ah, "
              f"{status['elapsed_time']/3600:.1f}h")

        time.sleep(60)  # Jede Minute aktualisieren

    # Endergebnisse abrufen
    final_status = load.get_battery_test_status()
    actual_capacity = final_status['capacity_ah']

    load.disconnect()

    # Schritt 4: Gesundheit berechnen
    health_percent = (actual_capacity / battery_capacity_ah) * 100

    print("\n" + "="*60)
    print("KAPAZITÄTSTEST-ERGEBNISSE")
    print("="*60)
    print(f"Nennkapazität:    {battery_capacity_ah:.1f} Ah")
    print(f"Tatsächl. Kapaz.: {actual_capacity:.2f} Ah")
    print(f"Batteriegesundh.: {health_percent:.1f}%")

    if health_percent >= 80:
        print("Status: GUT ✓")
    elif health_percent >= 50:
        print("Status: MITTEL")
    else:
        print("Status: SCHLECHT (Austausch erwägen)")

    print("="*60)

    return {
        'rated_capacity': battery_capacity_ah,
        'actual_capacity': actual_capacity,
        'health_percent': health_percent,
        'discharge_time': final_status['elapsed_time']
    }
```

---

## Eingebaute Testfunktionen

### 1. Batterie-Entladungstest (Eingebauter Modus)

**Vorteile:**
- Vollständig automatisiert durch OEL1530-Firmware
- Keine Notwendigkeit, Messungen abzufragen
- Genaue Ah-Berechnung
- Auto-Stopp bei Abschaltspannung

**Verwendung:**
```python
load.set_mode("BATT")
load.set_discharge_current(4.75)  # A (C/20)
load.set_cutoff_voltage(10.5)     # V
load.start()

# Auf Abschluss warten
while load.is_running():
    time.sleep(60)

capacity = load.get_capacity()  # Ah
```

### 2. OCP-Test (Überstromschutz)

Testet ob Ihr Netzteil (SPE6205) Strombegrenzung korrekt funktioniert:

```python
# Last so einstellen, dass sie mehr als Netzteil-Grenze zieht
load.set_current(25.0)  # Versuche 25A zu ziehen
psu.set_current(20.0)   # Netzteil begrenzt auf 20A

# Netzteil sollte bei 20A begrenzen (OCP funktioniert)
measured = psu.measure_current()
# Sollte 20A sein, nicht 25A
```

### 3. OPP-Test (Überleistungsschutz)

Testet ob Netzteil-Leistungsgrenze funktioniert:

```python
# Versuche Leistungsgrenze zu überschreiten
load.set_current(20.0)  # 20A
psu.set_voltage(60.0)   # 60V = 1200W (max für SPE6205)

# Netzteil sollte sich selbst schützen
```

---

## MQTT-Integration

Entladungstest-Topics hinzufügen:

```
battery-charger/discharge/running        # true/false
battery-charger/discharge/voltage        # V
battery-charger/discharge/current        # A
battery-charger/discharge/capacity       # Ah
battery-charger/discharge/elapsed        # Sekunden
battery-charger/discharge/progress       # %
```

---

## Sicherheitsüberlegungen

### 1. Wärmeableitung

**300W = erhebliche Wärme!**

OEL1530 bei Volllast:
- 12V × 25A = 300W
- Erzeugt Wärme (Kühlventilator enthalten)
- Gute Belüftung sicherstellen
- Lüftungsschlitze nicht blockieren

### 2. Umschalten zwischen Netzteil und Last

**NIEMALS beide gleichzeitig anschließen!**

```python
def switch_to_discharge():
    # 1. Netzteil-Ausgang deaktivieren
    psu.disable_output()
    time.sleep(2)

    # 2. Relais umschalten ODER Kabel manuell wechseln
    # relay.set_mode("DISCHARGE")

    # 3. Last verbinden
    load.enable_load()

def switch_to_charge():
    # 1. Last deaktivieren
    load.disable_load()
    time.sleep(2)

    # 2. Relais umschalten ODER Kabel manuell wechseln
    # relay.set_mode("CHARGE")

    # 3. Netzteil aktivieren
    psu.enable_output()
```

### 3. Tiefentladungsschutz

**Nicht unter 10,5V entladen:**
- Permanente Batterieschädigung unter 10V
- Abschaltspannung mindestens auf 10,5V setzen
- Spannung kontinuierlich überwachen

---

## Kosteneffektives Setup

Wie in der Beschreibung erwähnt:
**"kompakte und kostengünstige Last"**

**Gesamtsystem-Kosten:**
- OWON SPE6205: ~200-300€
- OWON OEL1530: ~150-200€
- Raspberry Pi 3: ~35€
- Kabel, Sensor: ~20€
- **Gesamt: ~400-550€**

**Vergleichbarer kommerzieller Batterie-Analysator: 1000-3000€+**

Sie bauen ein professionelles System für einen Bruchteil der Kosten!

---

## Nächste Schritte

1. **OEL1530 kaufen**
2. **An Raspberry Pi über zweiten USB-Port anschließen**
3. **SCPI-Kommunikation testen** (ähnlich wie Netzteil)
4. **owon_load.py Treiber implementieren**
5. **Ersten Kapazitätstest durchführen**
6. **Automatisierte Lade-/Entlade-Zyklen hinzufügen**

---

## Referenzen

- OWON OEL1530 Spezifikationen
- Batterie-Entladungstest-Standards
- Kapazitätsmessungs-Methoden
- Heimlabor-Batterietest Best Practices

**Die OEL1530 ist die perfekte Ergänzung zu Ihrer SPE6205!**
