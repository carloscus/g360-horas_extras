#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de detección de feriados Perú - G360 Ecosystem
Maneja feriados fijos y cálculo de Semana Santa.
"""

import json
import os
import sys
from datetime import datetime, timedelta


def calcular_pascua(anio: int) -> datetime:
    """
    Calcula el domingo de Pascua (Easter Sunday).
    Usa el algoritmo de Meeus/Jones/Butcher (más preciso que Buteo).
    Fuente: https://en.wikipedia.org/wiki/Computus#Meeus'_algorithm
    """
    a = anio % 19
    b = anio // 100
    c = anio % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(anio, mes, dia)


def get_semana_santa(anio: int) -> list[dict]:
    """
    Calcula los días feriados de Semana Santa.
    Retorna lista de dicts con formato: {'dia': int, 'mes': int, 'nombre': str}
    """
    pascua = calcular_pascua(anio)

    semana_santa = [
        (pascua - timedelta(days=3), "Jueves Santo"),
        (pascua - timedelta(days=2), "Viernes Santo"),
    ]

    return [
        {
            "dia": fecha.day,
            "mes": fecha.month,
            "nombre": nombre
        }
        for fecha, nombre in semana_santa
    ]


class CalendarioFeriados:
    """
    Gestiona el calendario de feriados de Perú.
    Compu Documents/Carga desde JSON + Cálculo automático de Semana Santa.
    """

    def __init__(self, json_path: str = None):
        """
        Inicializa el calendario cargando feriados fijos desde un archivo JSON.

        Args:
            json_path: Ruta al archivo feriados.json. Si es None, busca en el directorio del proyecto.
        """
        self.json_path = json_path or self._default_json_path()
        self.feriados_fijos = []
        self._cargar_json()

    def _default_json_path(self) -> str:
        """Determina la ruta por defecto al archivo feriados.json."""
        if getattr(sys, 'frozen', False):
            # Ejecutable PyInstaller
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            return os.path.join(base_path, "feriados.json")
        else:
            # Desarrollo
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            return os.path.join(base_dir, "feriados.json")

    def _cargar_json(self) -> None:
        """Carga los feriados desde el archivo JSON."""
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"No se encontró el archivo de feriados: {self.json_path}")

        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.feriados_fijos = data.get("feriados", [])

    def obtener_feriados(self, anio: int) -> list[dict]:
        """
        Retorna todos los feriados del año (fijos + Semana Santa).

        Args:
            anio: Año para calcular los feriados.

        Returns:
            Lista de dicts con claves: dia, mes, nombre
        """
        feriados = self.feriados_fijos.copy()
        feriados.extend(get_semana_santa(anio))
        return feriados

    def obtener_dias_feriados(self, anio: int) -> list[int]:
        """
        Retorna solo los números de día de los feriados (para compatibilidad con generador_planilla).
        Nota: Esto asume que todos los feriados están en el mismo mes del período.
        Considerar usar is_feriado() para mayor precisión.
        
        Args:
            anio: Año para calcular los feriados.

        Returns:
            Lista de días (int) de los feriados.
        """
        all_feriados = self.obtener_feriados(anio)
        return sorted([f["dia"] for f in all_feriados])

    def is_feriado(self, fecha: datetime, anio: int = None) -> bool:
        """
        Verifica si una fecha específica es feriado (incluyendo mes).
        Usa set lookup para O(1) en lugar de iterar lista.

        Args:
            fecha: Fecha a verificar.
            anio: Opcional, para forzar el año de referencia (cálculo de Semana Santa).

        Returns:
            True si es feriado, False en caso contrario.
        """
        if anio is None:
            anio = fecha.year

        feriados = self.obtener_feriados(anio)
        feriados_set = {(f["dia"], f["mes"]) for f in feriados}
        return (fecha.day, fecha.month) in feriados_set

    def get_nombre_feriado(self, fecha: datetime, anio: int = None) -> str | None:
        """
        Retorna el nombre del feriado si la fecha coincide, None si no.

        Args:
            fecha: Fecha a verificar.
            anio: Opcional, fuerza el año de referencia.

        Returns:
            Nombre del feriado o None.
        """
        if anio is None:
            anio = fecha.year

        feriados = self.obtener_feriados(anio)
        for feriado in feriados:
            if fecha.day == feriado["dia"] and fecha.month == feriado["mes"]:
                return feriado["nombre"]
        return None


# ============================================================
#  SINGLETON GLOBAL
# ============================================================

_calendario_cache = None


def get_calendario() -> CalendarioFeriados:
    """Obtiene el calendario global (singleton), creándolo si es necesario."""
    global _calendario_cache
    if _calendario_cache is None:
        _calendario_cache = CalendarioFeriados()
    return _calendario_cache


def refresh_calendario() -> CalendarioFeriados:
    """
    Fuerza la recarga del calendario desde el archivo JSON.
    Útil cuando se han editado los feriados fijos manualmente.
    """
    global _calendario_cache
    _calendario_cache = CalendarioFeriados()
    return _calendario_cache
