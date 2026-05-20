#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI - Gestor de Feriados
Modal para agregar, eliminar y gestionar feriados fijos.
Los feriados calculados (Semana Santa) se muestran pero no son editables.
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from src.utils.feriados import get_calendario, refresh_calendario, get_user_config_path

# Importar constantes del theme
from src.config.theme import (
    G360_GREEN, G360_DARK, G360_CARD_BG, G360_TEXT, G360_GRAY, G360_RED,
    G360_GREEN_HOVER, FONT_FAMILY_PRIMARY, FONT_SIZE_BODY, FONT_SIZE_SMALL
)

NOMBRES_MESES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


class FeriadosManager(ctk.CTkToplevel):
    """
    Ventana modal para gestionar feriados fijos.
    Permite agregar nuevos feriados y eliminar existentes.
    Los feriados calculados (Semana Santa) son de solo lectura.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.title("G360 - Gestionar Feriados")
        self.geometry("520x480")
        self.configure(fg_color=G360_CARD_BG)
        self.resizable(False, False)
        self.transient(parent)
        
        self.after(10, self._setup_grab)
        
        self._crear_ui()
        self._cargar_feriados()

    def _setup_grab(self):
        """Configura el grab después de que la ventana esté viewable."""
        try:
            self.grab_set()
        except tk.TclError:
            self.after(50, self._setup_grab)

    def _crear_ui(self):
        """Construye la interfaz del modal."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header, text="GESTIONAR FERIADOS",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_BODY, weight="bold"),
            text_color=G360_GREEN
        ).pack(side="left")

        # Config path info
        config_path = get_user_config_path()
        ctk.CTkLabel(
            header, text=f"Config: {config_path}",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL), text_color=G360_GRAY
        ).pack(side="right")

        # Leyenda
        legend_frame = ctk.CTkFrame(self, fg_color="transparent")
        legend_frame.pack(fill="x", padx=20, pady=(0, 8))

        leyendas = [
            (G360_GREEN, "Fijo (editable)"),
            (G360_GRAY, "Calculado (Semana Santa)"),
        ]
        for color, texto in leyendas:
            frame = ctk.CTkFrame(legend_frame, fg_color="transparent")
            frame.pack(side="left", padx=8)
            ctk.CTkLabel(frame, text="   ", fg_color=color, width=12, height=12, corner_radius=3).pack(side="left")
            ctk.CTkLabel(frame, text=texto, font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL), text_color=G360_GRAY).pack(side="left", padx=2)

        # Lista de feriados
        list_frame = ctk.CTkFrame(self, fg_color=G360_DARK, corner_radius=8)
        list_frame.pack(fill="both", expand=True, padx=20, pady=5)

        # Scrollable frame para la lista
        self.scroll_frame = ctk.CTkScrollableFrame(
            list_frame, fg_color="transparent", width=440, height=260
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Contenedor para items (se llena dinámicamente)
        self.feriados_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.feriados_container.pack(fill="x")

        # Formulario agregar
        add_frame = ctk.CTkFrame(self, fg_color="transparent")
        add_frame.pack(fill="x", padx=20, pady=(8, 5))

        ctk.CTkLabel(
            add_frame, text="Agregar feriado:",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL, weight="bold"),
            text_color=G360_TEXT
        ).pack(anchor="w")

        form_row = ctk.CTkFrame(add_frame, fg_color="transparent")
        form_row.pack(fill="x", pady=5)

        # Día
        self.entry_dia = ctk.CTkEntry(
            form_row, width=50, placeholder_text="Día",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL)
        )
        self.entry_dia.pack(side="left", padx=(0, 5))

        # Mes
        self.entry_mes = ctk.CTkOptionMenu(
            form_row, width=110, values=NOMBRES_MESES[1:],
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL),
            fg_color=G360_DARK, button_color=G360_CARD_BG
        )
        self.entry_mes.set("Mes")
        self.entry_mes.pack(side="left", padx=(0, 5))

        # Nombre
        self.entry_nombre = ctk.CTkEntry(
            form_row, placeholder_text="Nombre del feriado",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL), width=200
        )
        self.entry_nombre.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Botón agregar
        ctk.CTkButton(
            form_row, text="+ Agregar", width=90, height=30,
            fg_color=G360_GREEN, hover_color=G360_GREEN_HOVER,
            text_color=G360_DARK, font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL, weight="bold"),
            command=self._agregar_feriado
        ).pack(side="right")

        # Footer con botones
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(5, 15))

        ctk.CTkButton(
            footer, text="Restaurar Default", width=120, height=32,
            fg_color="transparent", border_width=1, border_color=G360_GRAY,
            text_color=G360_GRAY, hover_color=G360_CARD_BG,
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL),
            command=self._restaurar_default
        ).pack(side="left")

        ctk.CTkButton(
            footer, text="Cerrar", width=100, height=32,
            fg_color=G360_GREEN, hover_color=G360_GREEN_HOVER,
            text_color=G360_DARK, font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL, weight="bold"),
            command=self.destroy
        ).pack(side="right")

    def _cargar_feriados(self):
        """Carga y muestra la lista de feriados."""
        # Limpiar container
        for widget in self.feriados_container.winfo_children():
            widget.destroy()

        calendario = get_calendario()
        feriados = calendario.obtener_feriados(2026)
        calculados = {
            (f["dia"], f["mes"]) for f in calendario._get_semana_santa(2026)
        }

        # Ordenar por mes y día
        feriados.sort(key=lambda f: (f["mes"], f["dia"]))

        if not feriados:
            ctk.CTkLabel(
                self.feriados_container, text="No hay feriados configurados.",
                font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL), 
                text_color=G360_GRAY
            ).pack(pady=20)
            return

        for i, feriado in enumerate(feriados):
            es_calculado = (feriado["dia"], feriado["mes"]) in calculados
            self._crear_feriado_item(feriado, i, es_calculado)

    def _crear_feriado_item(self, feriado, index, es_calculado):
        """Crea un item visual para un feriado en la lista."""
        color_indicador = G360_GRAY if es_calculado else G360_GREEN
        
        item = ctk.CTkFrame(self.feriados_container, fg_color=G360_CARD_BG, corner_radius=6)
        item.pack(fill="x", pady=2, padx=2)

        # Indicador de color
        ctk.CTkLabel(
            item, text="", fg_color=color_indicador, width=4, height=30, corner_radius=2
        ).pack(side="left", padx=(8, 10))

        # Fecha
        fecha_str = f"{feriado['dia']:02d}/{feriado['mes']:02d}"
        ctk.CTkLabel(
            item, text=fecha_str, width=40,
            font=ctk.CTkFont(family="Consolas", size=FONT_SIZE_SMALL, weight="bold"),
            text_color=G360_TEXT
        ).pack(side="left", padx=(0, 10))

        # Nombre
        ctk.CTkLabel(
            item, text=feriado["nombre"],
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL), 
            text_color=G360_TEXT,
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        # Botón eliminar (solo si no es calculado)
        if not es_calculado:
            ctk.CTkButton(
                item, text="✕", width=28, height=28,
                fg_color="transparent", text_color=G360_RED,
                hover_color="red",
                font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_BODY),
                command=lambda f=feriado: self._eliminar_feriado(f)
            ).pack(side="right", padx=(0, 5))
        else:
            ctk.CTkLabel(
                item, text="auto",
                font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL), text_color=G360_GRAY
            ).pack(side="right", padx=(0, 8))

    def _agregar_feriado(self):
        """Agrega un nuevo feriado fijo."""
        try:
            dia = int(self.entry_dia.get())
            if not 1 <= dia <= 31:
                raise ValueError("Día inválido")
        except (ValueError, TypeError):
            messagebox.showwarning("Error", "Ingresa un día válido (1-31).")
            return

        mes_nombre = self.entry_mes.get()
        if mes_nombre == "Mes":
            messagebox.showwarning("Error", "Selecciona un mes.")
            return
        
        mes = NOMBRES_MESES.index(mes_nombre)
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Error", "Ingresa el nombre del feriado.")
            return

        # Guardar
        calendario = get_calendario()
        calendario.agregar_feriado(dia, mes, nombre)
        
        # Limpiar formulario
        self.entry_dia.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_mes.set("Mes")

        # Recargar lista
        refresh_calendario()
        self._cargar_feriados()

    def _eliminar_feriado(self, feriado):
        """Elimina un feriado fijo."""
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{feriado['nombre']}'?"):
            calendario = get_calendario()
            calendario.eliminar_feriado(feriado["dia"], feriado["mes"])
            refresh_calendario()
            self._cargar_feriados()

    def _restaurar_default(self):
        """Restaura los feriados al archivo JSON original."""
        if messagebox.askyesno("Confirmar", "¿Restaurar feriados por defecto?\nSe perderán los cambios personalizados."):
            calendario = get_calendario()
            calendario.restaurar_default()
            refresh_calendario()
            self._cargar_feriados()
