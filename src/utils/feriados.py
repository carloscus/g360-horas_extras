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

NOMBRES_MESES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def get_user_config_path() -> str:
    """Obtiene la ruta del archivo de feriados del usuario."""
    if sys.platform == "win32":
        base = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "G360-Horas-Extras")
    elif sys.platform == "darwin":
        base = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "G360-Horas-Extras")
    else:
        base = os.path.join(os.path.expanduser("~"), ".config", "g360-horas-extras")
    
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "feriados.json")


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
    Carga desde JSON del usuario (prioridad) o bundled JSON.
    Permite agregar/eliminar feriados fijos con persistencia.
    """

    def __init__(self, json_path: str = None):
        """
        Inicializa el calendario cargando feriados fijos desde un archivo JSON.

        Args:
            json_path: Ruta al archivo feriados.json. Si es None, busca config usuario primero.
        """
        self.json_path = json_path or self._default_json_path()
        self.bundled_path = self._bundled_json_path()
        self.feriados_fijos = []
        self._cargar_json()

    def _default_json_path(self) -> str:
        """Determina la ruta por defecto: config usuario primero."""
        return get_user_config_path()

    def _bundled_json_path(self) -> str:
        """Ruta al feriados.json empaquetado (fallback)."""
        if getattr(sys, 'frozen', False):
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            return os.path.join(base_path, "feriados.json")
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            return os.path.join(base_dir, "feriados.json")

    def _cargar_json(self) -> None:
        """Carga los feriados desde config usuario, fallback a bundled."""
        if os.path.exists(self.json_path):
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.feriados_fijos = data.get("feriados", [])
        elif os.path.exists(self.bundled_path):
            with open(self.bundled_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.feriados_fijos = data.get("feriados", [])
        else:
            self.feriados_fijos = []

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

    def agregar_feriado(self, dia: int, mes: int, nombre: str) -> bool:
        """
        Agrega un nuevo feriado fijo y persiste en config usuario.
        
        Args:
            dia: Día del mes (1-31)
            mes: Mes (1-12)
            nombre: Nombre del feriado
            
        Returns:
            True si se agregó, False si ya existía.
        """
        for f in self.feriados_fijos:
            if f["dia"] == dia and f["mes"] == mes:
                return False
        
        self.feriados_fijos.append({"dia": dia, "mes": mes, "nombre": nombre})
        self._guardar_json()
        return True

    def eliminar_feriado(self, dia: int, mes: int) -> bool:
        """
        Elimina un feriado fijo y persiste en config usuario.
        
        Args:
            dia: Día del mes
            mes: Mes
            
        Returns:
            True si se eliminó, False si no existía.
        """
        original_len = len(self.feriados_fijos)
        self.feriados_fijos = [
            f for f in self.feriados_fijos 
            if not (f["dia"] == dia and f["mes"] == mes)
        ]
        if len(self.feriados_fijos) < original_len:
            self._guardar_json()
            return True
        return False

    def restaurar_default(self) -> None:
        """Restaura feriados desde el JSON bundled original."""
        if os.path.exists(self.bundled_path):
            with open(self.bundled_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.feriados_fijos = data.get("feriados", [])
            self._guardar_json()

    def _guardar_json(self) -> None:
        """Guarda feriados fijos en config del usuario."""
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
        data = {
            "descripcion": "Feriados personalizados G360 Horas Extras",
            "version": "2026",
            "feriados": self.feriados_fijos
        }
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

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

    def _get_semana_santa(self, anio: int) -> list[dict]:
        """Retorna feriados de Semana Santa calculados (para UI)."""
        return get_semana_santa(anio)


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
