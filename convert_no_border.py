#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BrachioGraph Bild-zu-JSON Konverter OHNE automatischen Rahmen.

Laedt ein Bild, erzeugt die JSON via linedraw, und entfernt danach
automatisch erkannte Rahmen-Linien aus der JSON.

Verwendung:
    python3 convert_no_border.py <eingabe.jpg> [aufloesung] [ausgabe.json]

Beispiel:
    python3 convert_no_border.py vespa.jpg 1024 plot.json
"""

import sys
import os
import shutil

from PIL import Image, ImageOps


def preprocess_and_convert(input_path, resolution=1024, output_json=None, border_percent=2):
    """
    Laedt Bild, entfernt Rand, erzeugt JSON fuer BrachioGraph.
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Bild nicht gefunden: {input_path}")

    print(f"Laede Bild: {input_path}")
    image = Image.open(input_path)

    # Graustufen + Kontrast
    image = image.convert("L")
    image = ImageOps.autocontrast(image, 5)

    # Rand abschneiden (reduziert automatischen Rahmen)
    w, h = image.size
    border = int(min(w, h) * (border_percent / 100.0)) + 1
    print(f"Bildgroesse: {w}x{h}, Rand wird um {border}px beschnitten...")
    image = image.crop((border, border, w - border, h - border))

    # Temporaer abspeichern (linedraw erwartet Dateiname)
    temp_dir = os.path.join(os.getcwd(), "images")
    os.makedirs(temp_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    temp_name = f"{base_name}_noborder"
    temp_path = os.path.join(temp_dir, f"{temp_name}.jpg")

    image.save(temp_path)
    print(f"Vorverarbeitetes Bild: {temp_path}")

    # linedraw importieren
    try:
        import linedraw
    except ImportError:
        print("\nFEHLER: 'linedraw.py' nicht gefunden.")
        print("Bitte sicherstellen, dass linedraw.py im gleichen Ordner liegt")
        print("oder das BrachioGraph-Repo installiert ist.")
        sys.exit(1)

    # --- PATCH: find_edges ueberschreiben, Rand auf schwarz setzen ---
    _original_find_edges = linedraw.find_edges

    def find_edges_patched(image):
        result = _original_find_edges(image)
        # Nur die aussenliegenden Pixel auf schwarz setzen (kein Crop!)
        px = result.load()
        w, h = result.size
        edge = 4
        for x in range(w):
            for y in range(edge):
                px[x, y] = 0
                px[x, h - 1 - y] = 0
        for y in range(h):
            for x in range(edge):
                px[x, y] = 0
                px[w - 1 - x, y] = 0
        return result

    linedraw.find_edges = find_edges_patched
    # --- ENDE PATCH ---

    print("Vektorisiere... (das kann einen Moment dauern)")
    lines = linedraw.vectorise(
        image_filename=temp_name,
        resolution=resolution,
        draw_contours=2,
        repeat_contours=1,
        draw_hatch=16,
        repeat_hatch=1,
    )

    # --- POST-PROCESSING: Rahmen-Linien entfernen ---
    print(f"Vor Filterung: {len(lines)} Linien")
    lines = remove_border_lines(lines)
    print(f"Nach Filterung: {len(lines)} Linien")

    # --- JSON erzeugen ---
    if output_json is None:
        output_json = os.path.join(os.getcwd(), f"{base_name}.json")
    linedraw.lines_to_file(lines, output_json)

    # --- SVG erzeugen ---
    svg_path = os.path.join(os.getcwd(), f"{base_name}.svg")
    with open(svg_path, "w") as f:
        f.write(linedraw.makesvg(lines))

    # Temporaere Dateien aufraeumen
    if os.path.exists(temp_path):
        os.remove(temp_path)

    # Auch die von linedraw selbst erzeugte SVG/JSON loeschen (liegen in images/)
    for ext in [".json", ".svg"]:
        p = os.path.join(temp_dir, f"{temp_name}{ext}")
        if os.path.exists(p):
            os.remove(p)

    print(f"\nJSON erfolgreich erzeugt: {output_json}")
    print(f"SVG erfolgreich erzeugt:  {svg_path}")
    print(f"  Aufloesung: {resolution}")
    print(f"  Rand-Beschnitt: {border}px ({border_percent}%)")


def remove_border_lines(lines, margin=5):
    """
    Entfernt Linien, die offensichtlich der automatische Rahmen der Edge-Detection sind.
    """
    if not lines:
        return []

    # Bounding Box aller Linien
    all_x = [p[0] for line in lines for p in line]
    all_y = [p[1] for line in lines for p in line]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)

    total_width = max_x - min_x
    total_height = max_y - min_y

    filtered = []

    for line in lines:
        if len(line) < 2:
            continue

        line_min_x = min(p[0] for p in line)
        line_max_x = max(p[0] for p in line)
        line_min_y = min(p[1] for p in line)
        line_max_y = max(p[1] for p in line)
        line_width = line_max_x - line_min_x
        line_height = line_max_y - line_min_y

        # --- Test 1: Geschlossenes Rechteck, das fast die ganze Bildflaeche umfasst ---
        is_closed = (
            abs(line[0][0] - line[-1][0]) <= margin * 2
            and abs(line[0][1] - line[-1][1]) <= margin * 2
        )
        if is_closed and line_width > total_width * 0.85 and line_height > total_height * 0.85:
            continue

        # --- Test 2: Linie komplett auf einer Seite und mindestens 70% lang ---
        on_left = all(p[0] <= min_x + margin for p in line)
        on_right = all(p[0] >= max_x - margin for p in line)
        on_top = all(p[1] <= min_y + margin for p in line)
        on_bottom = all(p[1] >= max_y - margin for p in line)

        if on_left and line_height > total_height * 0.7:
            continue
        if on_right and line_height > total_height * 0.7:
            continue
        if on_top and line_width > total_width * 0.7:
            continue
        if on_bottom and line_width > total_width * 0.7:
            continue

        # --- Test 3: Jeder Punkt liegt in einer der 4 Ecken (diagonale Rahmen) ---
        in_corner = all(
            (p[0] <= min_x + margin or p[0] >= max_x - margin)
            and (p[1] <= min_y + margin or p[1] >= max_y - margin)
            for p in line
        )
        if in_corner and len(line) > 4:
            continue

        filtered.append(line)

    return filtered


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_file = sys.argv[1]
    resolution = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    preprocess_and_convert(input_file, resolution, output_file)
