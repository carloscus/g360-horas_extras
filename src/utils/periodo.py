#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utils - Gestión de Períodos.
Maneja la lógica de fechas para el ciclo del 21 al 20 del mes siguiente.
"""

from datetime import datetime, timedelta

def calcular_siguiente_periodo(mes: int, anio: int) -> tuple[int, int]:
    """
    Calcula el mes y año final del período (siempre el mes siguiente).
    
    Args:
        mes: Mes actual (1-12)
        anio: Año actual
        
    Returns:
        Tupla (mes_fin, anio_fin)
    """
    if mes == 12:
        return 1, anio + 1
    return mes + 1, anio

def obtener_periodo(mes: int, anio: int) -> list[datetime]:
    """
    Genera una lista de objetos datetime desde el 21 del mes indicado
    hasta el 20 del mes siguiente.
    
    Args:
        mes: Mes de inicio (1-12)
        anio: Año de inicio
        
    Returns:
        Lista de fechas del período.
    """
    # Normalizar año
    if anio < 100:
        anio += 2000
        
    fecha_inicio = datetime(anio, mes, 21)
    
    # Calcular mes fin para determinar cuántos días iterar
    mes_fin, anio_fin = calcular_siguiente_periodo(mes, anio)
    fecha_fin = datetime(anio_fin, mes_fin, 20)
    
    fechas = []
    current = fecha_inicio
    while current <= fecha_fin:
        fechas.append(current)
        current += timedelta(days=1)
        
    return fechas
