#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Legacy - Generador de Planillas de Horas Extras
(backward compatible, usa el core modular de src/)
"""

import sys
import os

# ------------------------------------------------------------------
#  Agregar la raíz del proyecto al sys.path para importar src/
# ------------------------------------------------------------------
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.excel_generator import generar_excel_horas_extras
from src.utils.feriados import get_calendario


if __name__ == "__main__":
    print("--- Generador de Plantilla de Horas Extras (CLI) ---")

    if len(sys.argv) == 3:
        try:
            m = int(sys.argv[1])
            a = int(sys.argv[2])
            print(f"Usando argumentos: Mes {m}, Año {a}")
            generar_excel_horas_extras(m, a)
        except ValueError as e:
            print(f"Error en argumentos: {e}")
    else:
        try:
            m = int(input("Ingrese el número del mes de INICIO del periodo (1-12): "))
            a = int(input("Ingrese el año (e.g. 2024): "))
            generar_excel_horas_extras(m, a)
        except ValueError:
            print("Error: Por favor ingrese números válidos.")
