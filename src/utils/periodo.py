#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helpers para manejo de períodos mensuales tipo 21-al-20.
"""

from datetime import datetime, timedelta


def calcular_siguiente_periodo(mes: int, anio: int) -> tuple[int, int]:
    """
    Dado un mes/año de inicio (inicio en día 21), retorna mes y año del fin (día 20).

    Args:
        mes: Mes de inicio (1-12)
        anio: Año de inicio

    Returns:
        Tuple (mes_fin, anio_fin)
    """
    if mes == 12:
        return 1, anio + 1
    return mes + 1, anio


def obtener_periodo(mes_inicio: int, anio_inicio: int) -> list[datetime]:
    """
    Genera una lista de fechas desde el día 21 del mes_inicio
    hasta el día 20 del siguiente mes.

    Args:
        mes_inicio: Mes del período (1-12)
        anio_inicio: Año del período

    Returns:
        Lista de objetos datetime (un día por elemento)
    """
    fecha_inicio = datetime(anio_inicio, mes_inicio, 21)
    mes_fin, anio_fin = calcular_siguiente_periodo(mes_inicio, anio_inicio)
    fecha_fin = datetime(anio_fin, mes_fin, 20)

    delta = fecha_fin - fecha_inicio
    return [fecha_inicio + timedelta(days=i) for i in range(delta.days + 1)]
