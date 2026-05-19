#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core - Generador de planillas Excel de horas extras.

Este módulo contiene la lógica principal para generar archivos Excel
con formato profesional para registro de horas extras, incluyendo
feriados, fines de semana y totales automáticos.
"""

import os
import xlsxwriter
from datetime import datetime
from src.utils.periodo import calcular_siguiente_periodo, obtener_periodo
from src.utils.feriados import get_calendario


# ============================================================
#  CONSTANTES DE FORMATO - PALETA CORPORATIVA SUAVIZADA
# ============================================================

BG_LABORABLE = '#F5F5F5'           # Lunes-Viernes (gris muy suave)
BG_SABADO = '#D6E4F0'              # Sábado (azul corporativo suave)
BG_DOMINGO = '#FCE4E4'             # Domingo (rojo suave)
BG_FERIADO = '#E74C3C'             # Feriado (rojo corporativo)

COLOR_LABORABLE_TEXTO = '#333333'  # Texto oscuro sobre gris
COLOR_SABADO_TEXTO = '#2C3E50'     # Texto oscuro sobre azul
COLOR_DOMINGO_TEXTO = '#C0392B'    # Texto oscuro sobre rojo suave
COLOR_FERIADO_TEXTO = '#FFFFFF'    # Texto blanco sobre rojo corporativo

NOMBRES_MESES = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun",
                 "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

DIAS_SEMANA = {
    0: 'Lunes', 1: 'Martes', 2: 'Miércoles',
    3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
}


def _make_format(workbook, num_format=None, align=None, bg=None, font_color=None):
    """Helper para crear formatos xlsxwriter evitando repetición."""
    fmt = {'border': 1}
    if num_format:
        fmt['num_format'] = num_format
    if align:
        fmt['align'] = align
    if bg:
        fmt['bg_color'] = bg
    if font_color:
        fmt['font_color'] = font_color
    return workbook.add_format(fmt)


def _crear_familias_formatos(workbook):
    """
    Crea diccionario con las 4 familias de formato: laboral, sabado, domingo, feriado.
    Cada familia contiene: fecha, texto, hora, numero.
    Paleta corporativa suavizada.
    """
    return {
        'laborable': {
            'fecha': _make_format(workbook, num_format='dd/mm/yyyy', bg=BG_LABORABLE, font_color=COLOR_LABORABLE_TEXTO),
            'texto': _make_format(workbook, bg=BG_LABORABLE, font_color=COLOR_LABORABLE_TEXTO),
            'hora': _make_format(workbook, num_format='hh:mm', align='center', bg=BG_LABORABLE, font_color=COLOR_LABORABLE_TEXTO),
            'numero': _make_format(workbook, num_format='0.00', align='center', bg=BG_LABORABLE, font_color=COLOR_LABORABLE_TEXTO)
        },
        'sabado': {
            'fecha': _make_format(workbook, num_format='dd/mm/yyyy', bg=BG_SABADO, font_color=COLOR_SABADO_TEXTO),
            'texto': _make_format(workbook, bg=BG_SABADO, font_color=COLOR_SABADO_TEXTO),
            'hora': _make_format(workbook, num_format='hh:mm', align='center', bg=BG_SABADO, font_color=COLOR_SABADO_TEXTO),
            'numero': _make_format(workbook, num_format='0.00', align='center', bg=BG_SABADO, font_color=COLOR_SABADO_TEXTO)
        },
        'domingo': {
            'fecha': _make_format(workbook, num_format='dd/mm/yyyy', bg=BG_DOMINGO, font_color=COLOR_DOMINGO_TEXTO),
            'texto': _make_format(workbook, bg=BG_DOMINGO, font_color=COLOR_DOMINGO_TEXTO),
            'hora': _make_format(workbook, num_format='hh:mm', align='center', bg=BG_DOMINGO, font_color=COLOR_DOMINGO_TEXTO),
            'numero': _make_format(workbook, num_format='0.00', align='center', bg=BG_DOMINGO, font_color=COLOR_DOMINGO_TEXTO)
        },
        'feriado': {
            'fecha': _make_format(workbook, num_format='dd/mm/yyyy', bg=BG_FERIADO, font_color=COLOR_FERIADO_TEXTO),
            'texto': _make_format(workbook, bg=BG_FERIADO, font_color=COLOR_FERIADO_TEXTO),
            'hora': _make_format(workbook, num_format='hh:mm', align='center', bg=BG_FERIADO, font_color=COLOR_FERIADO_TEXTO),
            'numero': _make_format(workbook, num_format='0.00', align='center', bg=BG_FERIADO, font_color=COLOR_FERIADO_TEXTO)
        }
    }


# ============================================================
#  FUNCIÓN PRINCIPAL
# ============================================================

def generar_excel_horas_extras(mes: int, anio: int, dias_feriados: list[int] = None) -> str:
    """
    Genera la planilla Excel de horas extras para el período indicado.

    Args:
        mes: Mes de inicio del período (1-12). El período siempre comienza el día 21.
        anio: Año del período (>= 2000 si llega de  2 dígitos se normaliza)
        dias_feriados: Lista opcional de números de día feriados (legacy). 
                       Se fusiona con feriados del calendario JSON.

    Returns:
        Nombre del archivo generado.

    Raises:
        ValueError: Si mes o año no son válidos.
    """

    # ------------------------------------------------------------------
    #  1. VALIDACIÓN Y PREPARACIÓN DE DATOS
    # ------------------------------------------------------------------
    dias_feriados = dias_feriados or []

    # Normalizar año de 2 dígitos a 4
    if anio < 100:
        anio += 2000

    if not 1 <= mes <= 12:
        raise ValueError("Mes debe estar entre 1 y 12")
    if anio < 2000:
        raise ValueError("Año debe ser >= 2000")

    mes_fin, anio_fin = calcular_siguiente_periodo(mes, anio)

    # Generar nombre del archivo
    nom_mes_1 = NOMBRES_MESES[mes]
    nom_mes_2 = NOMBRES_MESES[mes_fin]
    anio_corto = str(anio_fin)[-2:]
    nombre_archivo = f"Horas_Extras_{nom_mes_1}_{nom_mes_2}_{anio_corto}.xlsx"
    
    # Guardar en el Escritorio
    escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
    ruta_completa = os.path.join(escritorio, nombre_archivo)

    # Obtener lista de fechas del período
    fechas = obtener_periodo(mes, anio)

    # Preparar calendario de feriados (desde JSON + calculados)
    calendario = get_calendario()
    feriados_dict = calendario.obtener_feriados(anio)

    # ------------------------------------------------------------------
    #  2. CREAR WORKBOOK Y FORMATOS
    # ------------------------------------------------------------------
    workbook = xlsxwriter.Workbook(ruta_completa)

    # === HOJA 1: REGISTRO ===
    worksheet = workbook.add_worksheet("Registro")

    # Formatos encabezado
    fmt_titulo = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter'})
    fmt_etiqueta = workbook.add_format({'bold': True, 'align': 'right'})
    fmt_info = workbook.add_format({'bottom': 1, 'align': 'left'})
    fmt_numero_base = _make_format(workbook, num_format='0.00', align='center')

    # Familias de formato (laborable, sabado, domingo, feriado)
    familias = _crear_familias_formatos(workbook)

    # ------------------------------------------------------------------
    #  3. ENCABEZADO GENERAL
    # ------------------------------------------------------------------
    worksheet.merge_range('A1:H2', "REPORTE DE HORAS EXTRAS", fmt_titulo)
    
    # Fila de datos: Código | Nombre | Período
    worksheet.write('A4', "CÓDIGO:", fmt_etiqueta)
    worksheet.merge_range('B4:C4', "", fmt_info)
    
    worksheet.write('D4', "NOMBRE:", fmt_etiqueta)
    worksheet.merge_range('E4:F4', "", fmt_info)
    
    periodo_str = f"Del 21/{mes}/{anio}  al  20/{mes_fin}/{anio_fin}"
    worksheet.write('G4', "PERIODO:", fmt_etiqueta)
    worksheet.write('H4', periodo_str, fmt_info)

    # ------------------------------------------------------------------
    #  4. DEFINICIÓN DE TABLA
    # ------------------------------------------------------------------
    row_header = 5
    fila_inicio_datos = row_header + 1
    num_dias = len(fechas)
    fila_fin = fila_inicio_datos + num_dias - 1

    worksheet.add_table(row_header, 0, fila_fin + 1, 7, {
        'total_row': True,
        'banded_rows': False,
        'columns': [
            {'header': 'Fecha', 'total_string': 'Total'},
            {'header': 'Día'},
            {'header': 'Desde (Inicio)'},
            {'header': 'Hasta (Salida)'},
            {'header': 'Horas Extras', 'total_function': 'sum', 'format': fmt_numero_base},
            {'header': '25%', 'total_function': 'sum', 'format': fmt_numero_base},
            {'header': '35%', 'total_function': 'sum', 'format': fmt_numero_base},
            {'header': 'Comentarios'}
        ],
        'style': 'Table Style Medium 2'
    })

    # ------------------------------------------------------------------
    #  5. ESCRIBIR DATOS - CON COLORES DIFERENCIADOS
    # ------------------------------------------------------------------
    for idx, fecha in enumerate(fechas):
        fila = fila_inicio_datos + idx
        dia_semana = DIAS_SEMANA.get(fecha.weekday(), 'Desconocido')
        dia_numero = fecha.weekday()

        # Verificar si es feriado usando el calendario (incluye Semana Santa)
        es_feriado = calendario.is_feriado(fecha, anio)
        nombre_feriado = calendario.get_nombre_feriado(fecha, anio) if es_feriado else None

        # También verificar lista legacy de días feriados (compatibilidad)
        if not es_feriado and fecha.day in dias_feriados:
            es_feriado = True
            nombre_feriado = "Feriado (manual)"

        # --- Seleccionar familia de formato con COLORES DIFERENCIADOS ---
        # Prioridad: Feriado > Domingo > Sábado > Laborable
        if es_feriado:
            tipo = 'feriado'
        elif dia_numero == 6:  # Domingo
            tipo = 'domingo'
        elif dia_numero == 5:  # Sábado
            tipo = 'sabado'
        else:
            tipo = 'laborable'
        
        familia = familias[tipo]

        # --- Columna A: Fecha ---
        worksheet.write_datetime(fila, 0, fecha, familia['fecha'])
        # --- Columna B: Día semana ---
        worksheet.write(fila, 1, dia_semana, familia['texto'])

        # --- Columna C: Desde (Inicio) ---
        hora_inicio_str = "" if (dia_numero >= 5 or es_feriado) else "17:30"
        worksheet.write(fila, 2, hora_inicio_str, familia['hora'])

        # --- Columna D: Hasta (Salida) ---
        worksheet.write(fila, 3, "", familia['hora'])

        # --- Columnas E-G: Fórmulas automáticas ---
        c_inicio = f"C{fila + 1}"
        c_fin = f"D{fila + 1}"
        c_total = f"E{fila + 1}"

        formula_total = f'=IF(AND({c_inicio}\u003c\u003e{c_fin}, {c_inicio}\u003c\u003e"", {c_fin}\u003c\u003e""), ({c_fin}-{c_inicio})*24, 0)'
        worksheet.write_formula(fila, 4, formula_total, familia['numero'])

        formula_25 = f'=IF({c_total}>0, MIN(2, {c_total}), 0)'
        worksheet.write_formula(fila, 5, formula_25, familia['numero'])

        formula_35 = f'=IF({c_total}>2, {c_total}-2, 0)'
        worksheet.write_formula(fila, 6, formula_35, familia['numero'])

        # --- Columna H: Comentarios ---
        if es_feriado and nombre_feriado:
            texto_comment = f"NO LABORABLE - {nombre_feriado}"
        elif es_feriado:
            texto_comment = "NO LABORABLE"
        else:
            texto_comment = ""
        worksheet.write(fila, 7, texto_comment, familia['texto'])

    # ------------------------------------------------------------------
    #  6. SECCIÓN OBSERVACIONES GENERALES
    # ------------------------------------------------------------------
    fila_totales = fila_fin + 1
    fila_comentario = fila_totales + 2

    fmt_titulo_obs = workbook.add_format({'bold': True, 'align': 'left', 'bg_color': '#D9D9D9', 'border': 1})
    fmt_caja_obs = workbook.add_format({'align': 'left', 'valign': 'top', 'text_wrap': True, 'border': 1})

    worksheet.merge_range(fila_comentario, 0, fila_comentario, 7, "OBSERVACIONES GENERALES / JUSTIFICACIÓN DEL PERÍODO:", fmt_titulo_obs)
    worksheet.merge_range(fila_comentario + 1, 0, fila_comentario + 4, 7, "", fmt_caja_obs)

    # ------------------------------------------------------------------
    #  7. ANCHOS DE COLUMNA Y CIERRE
    # ------------------------------------------------------------------
    worksheet.set_column('A:A', 10)  # Código
    worksheet.set_column('B:C', 12)  # Nombre
    worksheet.set_column('D:D', 10)  # Nombre label
    worksheet.set_column('E:F', 14)  # Nombre value
    worksheet.set_column('G:G', 10)  # Período label
    worksheet.set_column('H:H', 22)  # Período value
    
    workbook.close()
    print(f"Archivo '{ruta_completa}' creado exitosamente.")
    return ruta_completa
