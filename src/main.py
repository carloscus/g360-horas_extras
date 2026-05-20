#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G360 Horas Extras - Interfaz Gráfica Avanzada + Picker de Calendario
Branding: G360 Ecosystem - Green Glow

Incluye calendario picker moderno (tkcalendar), visualización del período
y listado de SOLO los feriados que caen dentro del período seleccionado.
Distingue colores: Feriado (verde), Sábado (azul), Domingo (rojo).
"""

import sys
import os

# ------------------------------------------------------------------
#  Agregar la raíz del proyecto al sys.path para importar src/
#  Soporte PyInstaller (sys._MEIPASS) y desarrollo normal
# ------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    # Ejecutable PyInstaller
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    project_root = base_path
else:
    # Desarrollo normal
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

import tkinter as tk
from pathlib import Path
from datetime import datetime

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
from tkcalendar import Calendar
import babel.numbers  # Asegura que babel se incluya en el build

from src.core.excel_generator import generar_excel_horas_extras
from src.utils.feriados import get_calendario, refresh_calendario
from src.ui.feriados_manager import FeriadosManager
from src.config.theme import (
    G360_GREEN, G360_DARK, G360_CARD_BG, G360_TEXT, G360_GRAY, G360_RED, G360_BLUE,
    G360_GREEN_HOVER, LEGEND_ITEMS,
    FONT_FAMILY_PRIMARY, FONT_SIZE_HEADER, FONT_SIZE_TITLE, FONT_SIZE_BODY, FONT_SIZE_SMALL,
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_RESIZABLE,
    CARD_CORNER_RADIUS, BUTTON_HEIGHT, BUTTON_HEIGHT_LARGE, PADDING_X, PADDING_Y
)

# ============================================================
#  CUSTOMTKINTER SETUP
# ============================================================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


# ============================================================
#  PICKER CALENDARIO (tkcalendar integrado)
# ============================================================
class G360CalendarPicker(tk.Toplevel):
    """
    Ventana emergente con calendario para seleccionar rango de fechas del período.
    Usa tk.Toplevel para máxima compatibilidad con tkcalendar en Windows/PyInstaller.
    """

    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.title("G360 - Seleccionar Período")
        self.geometry("450x520")
        self.configure(bg=G360_CARD_BG)
        self.resizable(False, False)
        
        # Centrar ventana y Focus
        self.transient(parent)
        self.attributes("-topmost", True)
        
        # Header
        ctk.CTkLabel(
            self, text="SELECCIONAR PERÍODO",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_TITLE, weight="bold"),
            text_color=G360_GREEN, fg_color=G360_CARD_BG
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            self, text="Seleccione cualquier fecha del período",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL), 
            text_color=G360_GRAY, fg_color=G360_CARD_BG
        ).pack(pady=(0, 15))

        # Contenedor del Calendario
        cal_frame = tk.Frame(self, bg=G360_DARK, padx=15, pady=15, highlightbackground=G360_GREEN, highlightthickness=1)
        cal_frame.pack(padx=30, pady=5)

        self.calendar = Calendar(
            cal_frame,
            selectmode="day",
            showweeknumbers=False,
            firstweekday="monday",
            background=G360_DARK,
            foreground=G360_TEXT,
            bordercolor=G360_DARK,
            selectbackground=G360_GREEN,
            selectforeground=G360_DARK,
            normalbackground=G360_DARK,
            normalforeground=G360_TEXT,
            headersbackground=G360_DARK,
            headersforeground=G360_GREEN,
            weekendbackground=G360_DARK,
            weekendforeground=G360_RED,
            othermonthbackground=G360_DARK,
            othermonthforeground=G360_GRAY,
            font="Arial 10",
            headersfont="Arial 10 bold",
            cursor="hand2"
        )
        self.calendar.pack()

        # Caja de información (Período calculado)
        info_container = tk.Frame(self, bg=G360_DARK, height=45)
        info_container.pack(fill="x", padx=50, pady=(15, 5))
        info_container.pack_propagate(False)

        self.info_label = ctk.CTkLabel(
            info_container, text="Seleccione una fecha", 
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_BODY, weight="bold"),
            text_color=G360_GREEN, fg_color=G360_DARK
        )
        self.info_label.pack(expand=True)

        # Botones
        btns_frame = tk.Frame(self, bg=G360_CARD_BG)
        btns_frame.pack(fill="x", padx=50, pady=(20, 20))

        ctk.CTkButton(
            btns_frame, text="Cancelar", width=100, height=BUTTON_HEIGHT,
            fg_color="transparent", border_width=1, border_color=G360_GRAY,
            text_color=G360_GRAY, hover_color=G360_DARK,
            command=self.destroy
        ).pack(side="left")

        ctk.CTkButton(
            btns_frame, text="Confirmar Período", height=BUTTON_HEIGHT,
            fg_color=G360_GREEN, hover_color=G360_GREEN_HOVER,
            text_color=G360_DARK, font=ctk.CTkFont(weight="bold"),
            command=self._confirmar
        ).pack(side="right", fill="x", expand=True, padx=(12, 0))

        # Eventos y Foco
        self.calendar.bind("<<CalendarSelected>>", self._on_day_selected)
        self.fecha_seleccionada = None
        
        self.after(100, lambda: [self.grab_set(), self.focus_force()])

    def _on_day_selected(self, event=None):
        """Calcula el período 21/mm al 20/mm+1."""
        fecha = self.calendar.selection_get()
        self.fecha_seleccionada = fecha
        
        dia, mes, anio = fecha.day, fecha.month, fecha.year
        nom_meses = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun",
                     "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        
        if dia >= 21:
            mes_i, anio_i = mes, anio
        else:
            mes_i = mes - 1 if mes > 1 else 12
            anio_i = anio if mes > 1 else anio - 1
        
        mes_f = mes_i + 1 if mes_i < 12 else 1
        anio_f = anio_i if mes_i < 12 else anio_i + 1
        
        preview = f"Período: 21/{nom_meses[mes_i]}/{str(anio_i)[-2:]}  →  20/{nom_meses[mes_f]}/{str(anio_f)[-2:]}"
        self.info_label.configure(text=preview)

    def _confirmar(self):
        """Callback de retorno."""
        if self.fecha_seleccionada is None:
            messagebox.showwarning("Selección Requerida", "Por favor seleccione una fecha.")
            return
            
        d, m, a = self.fecha_seleccionada.day, self.fecha_seleccionada.month, self.fecha_seleccionada.year
        mes_i = m if d >= 21 else (m - 1 if m > 1 else 12)
        anio_i = a if (d >= 21 or m > 1) else a - 1
        
        if self.callback:
            self.callback(mes_i, anio_i)
        self.destroy()


# ============================================================
#  MAIN APPLICATION CLASS
# ============================================================

class G360HorasExtrasApp(ctk.CTk):
    """Ventana principal de la aplicación G360 Horas Extras."""

    def __init__(self):
        super().__init__()

        self.title("G360 - Generador de Planillas de Horas Extras")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.configure(fg_color=G360_DARK)
        self.resizable(WINDOW_RESIZABLE, WINDOW_RESIZABLE)

        # Configurar Icono de Ventana
        self._configurar_icono()

        # Variables de estado
        self.mes_seleccionado = ctk.StringVar(value="")
        self.anio_seleccionado = ctk.StringVar(value="")
        
        # Logo image cache
        self.logo_image = None

        self._crear_header()
        self._crear_formulario()
        self._crear_panel_feriados()
        self._crear_footer()

        # Iniciar con fecha actual
        hoy = datetime.now()
        self._procesar_periodo(hoy.month, hoy.year)

    def _configurar_icono(self):
        """Configura el icono de la ventana (.ico) para Windows."""
        if getattr(sys, 'frozen', False):
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            icon_path = Path(base_path) / "assets" / "images" / "favicon.ico"
        else:
            icon_path = Path(__file__).parent.parent / "assets" / "images" / "favicon.ico"

        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception as e:
                print(f"Warning: Could not load window icon: {e}")

    def _procesar_periodo(self, mes, anio):
        """Actualiza la UI con el mes y año seleccionados."""
        self.mes_seleccionado.set(str(mes))
        self.anio_seleccionado.set(str(anio))
        self._actualizar_preview()
        self._actualizar_lista_feriados()

    def _crear_header(self):
        """Crea el encabezado con logo G360 y título al lado."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=PADDING_X, pady=(10, 0))

        if getattr(sys, 'frozen', False):
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            logo_path = Path(base_path) / "assets" / "images" / "logo-g360.png"
        else:
            logo_path = Path(__file__).parent.parent / "assets" / "images" / "logo-g360.png"
        
        if logo_path.exists():
            try:
                self.logo_image = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(110, 28)
                )
                ctk.CTkLabel(header, image=self.logo_image, text="").pack(side="left", padx=(0, 10))
            except Exception as e:
                print(f"Warning: Could not load logo: {e}")

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="y")

        ctk.CTkLabel(
            title_frame, text="Horas Extras",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_HEADER, weight="bold"),
            text_color=G360_GREEN
        ).pack(anchor="w")

    def _crear_formulario(self):
        """Crea el formulario de configuración del período."""
        form_container = ctk.CTkFrame(self, fg_color=G360_CARD_BG, corner_radius=CARD_CORNER_RADIUS)
        form_container.pack(fill="x", padx=PADDING_X, pady=(10, 8))

        ctk.CTkLabel(
            form_container, text="CONFIGURACIÓN DEL PERÍODO",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_BODY, weight="bold"),
            text_color=G360_GREEN
        ).pack(anchor="w", padx=15, pady=(10, 3))

        display_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        display_frame.pack(fill="x", padx=15, pady=6)

        self.display_periodo = ctk.CTkLabel(
            display_frame, text="No seleccionado",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_TITLE, weight="bold"),
            text_color=G360_TEXT, fg_color=G360_DARK,
            corner_radius=8, padx=12, pady=8, width=280
        )
        self.display_periodo.pack(side="left", fill="x", expand=True, padx=(0, 8))

        buttons_frame = ctk.CTkFrame(display_frame, fg_color="transparent")
        buttons_frame.pack(side="right")

        ctk.CTkButton(
            buttons_frame, text="⚙️ Feriados",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL), width=90, height=BUTTON_HEIGHT,
            fg_color="transparent", border_width=1, border_color=G360_GRAY,
            text_color=G360_GRAY, hover_color=G360_CARD_BG,
            command=self._abrir_feriados
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            buttons_frame, text="📅 Seleccionar",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_BODY), width=130, height=BUTTON_HEIGHT_LARGE,
            fg_color=G360_GREEN, hover_color=G360_GREEN_HOVER,
            text_color=G360_DARK, command=self._abrir_picker
        ).pack(side="left")

        self.preview_label = ctk.CTkLabel(
            form_container, text="", 
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_BODY), 
            text_color=G360_GRAY
        )
        self.preview_label.pack(anchor="w", padx=15, pady=2)

        legend_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        legend_frame.pack(anchor="w", padx=15, pady=3)

        for color, texto in LEGEND_ITEMS:
            frame = ctk.CTkFrame(legend_frame, fg_color="transparent")
            frame.pack(side="left", padx=4)
            ctk.CTkLabel(frame, text="   ", fg_color=color, width=12, height=12, corner_radius=3).pack(side="left")
            ctk.CTkLabel(frame, text=texto, font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL), text_color=G360_GRAY).pack(side="left", padx=2)

        ctk.CTkButton(
            form_container, text="Generar Planilla Excel",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_BODY, weight="bold"),
            fg_color=G360_GREEN, hover_color=G360_GREEN_HOVER,
            text_color=G360_DARK, height=BUTTON_HEIGHT, width=230,
            command=self._generar
        ).pack(pady=10)

        self.status_label = ctk.CTkLabel(
            form_container, text="", 
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_BODY)
        )
        self.status_label.pack()

    def _abrir_picker(self):
        """Abre el picker de calendario."""
        G360CalendarPicker(self, callback=self._procesar_periodo)

    def _abrir_feriados(self):
        """Abre el gestor de feriados."""
        FeriadosManager(self)

    def _crear_panel_feriados(self):
        """Crea un panel informativo con feriados del período seleccionado."""
        panel = ctk.CTkFrame(self, fg_color=G360_CARD_BG, corner_radius=CARD_CORNER_RADIUS)
        panel.pack(fill="x", padx=PADDING_X, pady=(0, 6))

        ctk.CTkLabel(
            panel, text="FERIADOS DEL PERÍODO",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_BODY, weight="bold"),
            text_color=G360_GREEN
        ).pack(anchor="w", padx=15, pady=(6, 0))

        self.feriados_text = ctk.CTkTextbox(
            panel, height=75, fg_color="transparent", text_color=G360_GRAY,
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL), 
            wrap="word"
        )
        self.feriados_text.pack(fill="x", padx=15, pady=(5, 10))

    def _actualizar_lista_feriados(self):
        """Muestra SOLO los feriados que caen dentro del período seleccionado."""
        try:
            val_mes = self.mes_seleccionado.get()
            val_anio = self.anio_seleccionado.get()
            if not val_mes or not val_anio:
                self.feriados_text.delete("0.0", "end")
                self.feriados_text.insert("0.0", "Seleccione un período...")
                return
            mes = int(val_mes)
            anio = int(val_anio)
        except (ValueError, TypeError):
            self.feriados_text.delete("0.0", "end")
            return

        calendario = get_calendario()
        total_feriados = calendario.obtener_feriados(anio)
        mes_fin = 1 if mes == 12 else mes + 1

        feriados_en_periodo = []
        for feriado in total_feriados:
            f_m, f_d = feriado["mes"], feriado["dia"]
            if (f_m == mes and f_d >= 21) or (f_m == mes_fin and f_d <= 20):
                feriados_en_periodo.append(feriado)

        self.feriados_text.delete("0.0", "end")
        if feriados_en_periodo:
            texto = ["Feriados dentro del período:"]
            for f in feriados_en_periodo:
                texto.append(f"  • {f['dia']:02d}/{f['mes']:02d}  {f['nombre']}")
            self.feriados_text.insert("0.0", "\n".join(texto))
        else:
            self.feriados_text.insert("0.0", "No hay feriados en este período.")

    def _actualizar_preview(self):
        """Actualiza el texto del preview de período."""
        try:
            mes = int(self.mes_seleccionado.get())
            anio = int(self.anio_seleccionado.get())
            if anio < 100: anio += 2000

            nom_meses = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun",
                         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
            mes_f = 1 if mes == 12 else mes + 1
            anio_f = anio + 1 if mes == 12 else anio

            preview = f"Período: 21/{nom_meses[mes]}/{str(anio)[-2:]}  →  20/{nom_meses[mes_f]}/{str(anio_f)[-2:]}"
            self.preview_label.configure(text=preview)
            self.display_periodo.configure(text=f"{nom_meses[mes].upper()} {anio}")
        except:
            self.preview_label.configure(text="")

    def _generar(self):
        """Ejecuta la generación del archivo Excel."""
        try:
            mes = int(self.mes_seleccionado.get())
            anio = int(self.anio_seleccionado.get())

            self.status_label.configure(text="Generando...", text_color=G360_GREEN)
            self.update_idletasks()

            archivo = generar_excel_horas_extras(mes, anio)
            nombre_archivo = os.path.basename(archivo)
            self.status_label.configure(text=f" Listo: {nombre_archivo}", text_color=G360_GREEN)

            if messagebox.askyesno("G360 - Éxito", f"Planilla generada: {nombre_archivo}\n\n¿Abrir carpeta?"):
                os.startfile(os.path.dirname(archivo))

        except Exception as e:
            messagebox.showerror("G360 - Error", f"Error: {e}")
            self.status_label.configure(text="", text_color=G360_RED)

    def _crear_footer(self):
        """Crea el pie de página con créditos."""
        footer = ctk.CTkFrame(self, fg_color="transparent", height=30)
        footer.pack(fill="x", padx=PADDING_X, pady=(5, 10))
        ctk.CTkLabel(
            footer, text="Powered by G360",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_SMALL), 
            text_color=G360_GRAY
        ).pack(side="right")


if __name__ == "__main__":
    app = G360HorasExtrasApp()
    app.mainloop()
