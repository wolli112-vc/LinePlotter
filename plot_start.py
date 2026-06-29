#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plot_start.py – BrachioGraph Plotter-Startskript
Fragt nach der JSON-Datei und startet den Plotvorgang.
"""

from brachiograph import BrachioGraph


bg = BrachioGraph(
    inner_arm=8,           # Oberarmlaenge cm
    outer_arm=8,           # Unterarmlaenge cm
    bounds=(-8, 4, 4, 13), # Koordinaten Zeichenbereich
    servo_1_degree_ms=-10, # Bewegung Schulterservo
    servo_2_degree_ms=10,  # Bewegung Ellenbogenservo
    servo_1_centre=1600,   # Mittelstellung Schulter
    servo_2_centre=1610,     # Mittelstellung Ellenbogen
    pw_down=1850,          # Position Stift unten
    pw_up=1500,            # Position Stift angehoben
)


if __name__ == "__main__":

    # Abfrage des JSON-Pfads
    datei = input("Pfad zur JSON-Datei eingeben (z.B. bild.json): ").strip()

    if not datei:
        print("Keine Datei angegeben. Abbruch.")
        exit(1)

    # Falls nur Dateiname ohne Pfad, im aktuellen Verzeichnis suchen
    import os
    if not os.path.exists(datei):
        alt = os.path.join(os.getcwd(), datei)
        if os.path.exists(alt):
            datei = alt

    print(f"Starte Plot: {datei}")
    bg.plot_file(datei)
    print("Fertig.")
