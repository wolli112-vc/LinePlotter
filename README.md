<img width="504" height="672" alt="IMG_4248" src="https://github.com/user-attachments/assets/2bdb57b8-e7c4-4074-ad8b-80173cf37aa9" />


# LinePlotter

Deutschsprachiger Fork des **BrachioGraph** – dem wohl einfachsten Zeichenroboter der Welt.
Ein Raspberry Pi, drei Servos, zwei Eisstiele, eine Waescheklammer und etwas Heisskleber – mehr braucht es nicht.

> Original: [evildmp/BrachioGraph](https://github.com/evildmp/BrachioGraph)
> Make Magazin Fork: [MakeMagazinDE/BrachioGraph](https://github.com/MakeMagazinDE/BrachioGraph)

## Was ist das?

Ein einfacher **Pen-Plotter** (Zeichenroboter), der Bilder in Linien umwandelt und mit einem Stift auf Papier zeichnet.

## Die zwei wichtigsten Skripte

| Skript | Zweck |
|--------|-------|
| `convert_no_border.py` | Bild (JPG/PNG) → JSON/SVG umwandeln |
| `plot_start.py` | JSON-Datei auf dem Plotter ausgeben |

## Workflow: Bild → Plotter

### Schritt 1: Bild vorbereiten

```bash
python3 convert_no_border.py vespa.jpg
```

Mit optionalen Parametern:
```bash
python3 convert_no_border.py vespa.jpg 1024 plot.json
#            Bild       Aufloesung   Ausgabe-Datei
```

Ausgabe:
- `vespa.json` – Liniendaten fuer den Plotter
- `vespa.svg`  – Vorschau zum Pruefen

**Problem geloest:** Der originale `linedraw`-Konverter erzeugt oft einen **automatischen Rahmen** am Bildrand. `convert_no_border.py` entfernt diesen Rahmen automatisch.

### Vor dem Plotten: pigpiod starten

Der Servo-Treiber (`pigpio`) muss im Hintergrund laufen:

```bash
sudo pigpiod
```

Das ist ein Daemon – er läuft bis zum Neustart oder bis Du ihn mit `sudo killall pigpiod` beendest.

### Schritt 2: Auf dem Plotter ausgeben

```bash
python3 plot_start.py
```

Das Skript fragt nach der JSON-Datei:
```
Pfad zur JSON-Datei eingeben (z.B. bild.json): vespa.json
Starte Plot: vespa.json
...
Fertig.
```

## Konfiguration

Die Servo-Werte sind in `plot_start.py` angepasst. Bei Bedarf dort aendern:

```python
bg = BrachioGraph(
    inner_arm=8,            # Oberarmlaenge in cm
    outer_arm=8,            # Unterarmlaenge in cm
    bounds=(-8, 4, 4, 13),  # Zeichenbereich (x_min, y_min, x_max, y_max)
    servo_1_degree_ms=-10,  # Bewegung Schulterservo
    servo_2_degree_ms=10,   # Bewegung Ellenbogenservo
    servo_1_centre=1600,    # Mittelstellung Schulter
    servo_2_centre=1610,    # Mittelstellung Ellenbogen
    pw_down=1850,           # Stift unten (Pulse-Width)
    pw_up=1500,             # Stift angehoben (Pulse-Width)
)
```

## Weitere Dateien

| Datei | Beschreibung |
|-------|-------------|
| `brachiograph.py` | Hauptklasse – Servo-Steuerung und Geometrie |
| `linedraw.py` | Original Bild-zu-Linien Konverter (bitmap → JSON/SVG) |
| `requirements.txt` | Python-Abhaengigkeiten |
| `LICENSE` | MIT Lizenz |

## Kalibrierung

```python
# Servo-Winkel kalibrieren
bg.calibrate(servo=1)
bg.calibrate(servo=2)

# Stifthoehe kalibrieren
bg.pen.calibrate()

# Test-Muster zeichnen
bg.box()
bg.test_pattern()
```

## Abhaengigkeiten

```bash
pip install -r requirements.txt
```

Wichtige Pakete:
- `pigpio` – Servo-Steuerung auf dem Raspberry Pi
- `Pillow` – Bildverarbeitung
- `numpy` – Mathematische Berechnungen
- `tqdm` – Fortschrittsbalken
- `readchar` – Tastatureingaben (Kalibrierung)

## Hardware

- **Raspberry Pi** (Zero reicht)
- **3x SG90 Servo** (oder aehnliche)
- **2x Eisstiele / Holzleisten** (Arme)
- **1x Waescheklammer** (Stifthalter)
- **Heisskleber, Kabel, Breadboard**

## Lizenz

MIT License – siehe [LICENSE](LICENSE)

## Links

- [Original-Dokumentation](https://www.brachiograph.art/)
- [Make Magazin Artikel](https://heise.de/-4653323/)
