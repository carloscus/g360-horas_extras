#!/usr/bin/env python3
"""
Genera icono .ico desde logo-g360.png
Crea versión cuadrada centrada con fondo transparente.
"""
from PIL import Image
import os

SIZES = [16, 32, 48, 64, 128, 256]
INPUT = "assets/images/logo-g360.png"
OUTPUT = "assets/images/icon.ico"

img = Image.open(INPUT).convert("RGBA")

# Crear versión cuadrada: recortar centro del logo
width, height = img.size
size = min(width, height)
left = (width - size) // 2
top = (height - size) // 2
square = img.crop((left, top, left + size, top + size))

# Generar resoluciones
icons = []
for s in SIZES:
    icons.append(square.resize((s, s), Image.LANCZOS))

# Guardar como .ico
icons[0].save(
    OUTPUT,
    format="ICO",
    sizes=[(i.size[0], i.size[1]) for i in icons],
    append_images=icons[1:]
)

print(f"Icono generado: {OUTPUT}")
print(f"Resoluciones: {', '.join(f'{s}x{s}' for s in SIZES)}")
