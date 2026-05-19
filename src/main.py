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
    project_root = os.path.dirname(sys.executable)
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

from src.core.excel_generator import generar_excel_horas_extras
from src.utils.feriados import get_calendario
from src.config.theme import (
    G360_GREEN, G360_DARK, G360_CARD_BG, G360_TEXT, G360_GRAY, G360_RED, G360_BLUE,
    G360_GREEN_HOVER, LEGEND_ITEMS,
    FONT_FAMILY_PRIMARY, FONT_SIZE_HEADER, FONT_SIZE_TITLE, FONT_SIZE_BODY, FONT_SIZE_SMALL, FONT_SIZE_LABEL,
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
from tkcalendar import Calendar


class G360CalendarPicker(ctk.CTkToplevel):
    """
    Ventana emergente con calendario para seleccionar rango de fechas del período.
    Rango mínimo: 21 de un mes. Rango máximo: 20 del mes siguiente.
    """

    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.title("G360 - Seleccionar Período")
        self.geometry("400x500")
        self.configure(fg_color=G360_CARD_BG)
        self.resizable(False, False)
        self.transient(parent)
        
        # Delay grab_set until window is viewable
        self.after(10, self._setup_grab)
        
        # Header
        ctk.CTkLabel(
            self, text="SELECCIONAR PERÍODO",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_TITLE, weight="bold"),
            text_color=G360_GREEN
        ).pack(pady=(15, 0))

        ctk.CTkLabel(
            self, text="Seleccione cualquier fecha\ndel período deseado (21 a 20)",
            font=ctk.CTkFont(size=FONT_SIZE_SMALL), text_color=G360_GRAY
        ).pack(pady=5)

        # Calendario integrado tkcalendar con estilos G360
        cal_frame = ctk.CTkFrame(self, fg_color="transparent")
        cal_frame.pack(padx=15, pady=10)

        self.calendar = Calendar(
            cal_frame,
            selectmode="day",
            locale="es_ES",
            background=G360_CARD_BG,
            foreground=G360_TEXT,
            bordercolor=G360_GREEN,
            selectbackground=G360_GREEN,
            selectforeground=G360_DARK,
            disabledbackground=G360_DARK,
            disabledforeground=G360_GRAY,
            weekendbackground=G360_CARD_BG,
            weekendforeground=G360_RED,
            othermonthforeground=G360_GRAY,
            othermonthbackground=G360_DARK,
            font="Segoe 10",
            headersbackground=G360_GREEN,
            headersforeground=G360_DARK,
            cursor="hand2",
            headersfont="Segoe 10 bold"
        )
        self.calendar.pack()

        # Info del período seleccionado
        self.info_label = ctk.CTkLabel(
            self, text="Seleccione cualquier fecha del período", 
            font=ctk.CTkFont(size=FONT_SIZE_BODY, weight="bold"),
            text_color=G360_GREEN
        )
        self.info_label.pack(pady=5)

        # Botón confirmar
        ctk.CTkButton(
            self, text="Confirmar Período", fg_color=G360_GREEN,
            text_color=G360_DARK, hover_color=G360_GREEN_HOVER,
            command=self._confirmar
        ).pack(pady=15)

        # Vincular selección de día
        self.calendar.bind("<<CalendarSelected>>", self._on_day_selected)

        # Variables para el período calculado
        self.fecha_seleccionada = None

    def _setup_grab(self):
        """Configura el grab después de que la ventana esté viewable"""
        try:
            self.grab_set()
        except tk.TclError:
            # Si falla, intentar de nuevo después de un breve retraso
            self.after(50, self._setup_grab)

    def _on_day_selected(self, event=None):
        """Maneja la selección de una fecha y calcula el período 21/mm al 20/mm+1."""
        fecha = self.calendar.selection_get()
        self.fecha_seleccionada = fecha
        
        # Determinar el período: si la fecha es >= 21, usar su mes como inicio
        # Si es < 21, usar el mes anterior (pero ajustar)
        dia = fecha.day
        mes = fecha.month
        anio = fecha.year
        
        # El período siempre empieza el 21 de un mes y termina 20 del siguiente
        nom_meses = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun",
                     "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        
        if dia >= 21:
            # La fecha está en el período de 21 a 20
            mes_inicio = mes
            anio_inicio = anio
        else:
            # La fecha está antes del 21, pertenece al período anterior
            mes_inicio = mes - 1 if mes > 1 else 12
            anio_inicio = anio if mes > 1 else anio - 1
        
        # Calcular mes fin del período
        mes_fin = mes_inicio + 1 if mes_inicio < 12 else 1
        anio_fin = anio_inicio if mes_inicio < 12 else anio_inicio + 1
        
        preview = f"Período: 21/{nom_meses[mes_inicio]}/{str(anio_inicio)[-2:]}  →  20/{nom_meses[mes_fin]}/{str(anio_fin)[-2:]}"
        self.info_label.configure(text=preview, text_color=G360_GREEN)

    def _confirmar(self):
        """Envía el período calculado a través del callback."""
        if self.fecha_seleccionada is None:
            messagebox.showwarning("Selección Requerida", "Por favor seleccione una fecha.")
            return
            
        fecha = self.fecha_seleccionada
        dia = fecha.day
        mes = fecha.month
        anio = fecha.year
        
        # Determinar el período basado en la regla 21 a 20
        if dia >= 21:
            mes_inicio = mes
            anio_inicio = anio
        else:
            mes_inicio = mes - 1 if mes > 1 else 12
            anio_inicio = anio if mes > 1 else anio - 1
        
        if self.callback:
            self.callback(mes_inicio, anio_inicio)
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

    def _procesar_periodo(self, mes, anio):
        """Actualiza la UI con el mes y año seleccionados."""
        self.mes_seleccionado.set(str(mes))
        self.anio_seleccionado.set(str(anio))
        self._actualizar_preview()
        self._actualizar_lista_feriados()

    # ------------------------------------------------------------------
    #  HEADER
    # ------------------------------------------------------------------
    def _crear_header(self):
        """Crea el encabezado con logo G360 y título al lado."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=PADDING_X, pady=(10, 0))

        # Logo (soporte PyInstaller + desarrollo)
        if getattr(sys, 'frozen', False):
            # Ejecutable: assets están en _MEIPASS
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            logo_path = os.path.join(base_path, "assets", "images", "logo-g360.png")
        else:
            # Desarrollo
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

        # Título al lado del logo
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="y")

        ctk.CTkLabel(
            title_frame, text="Horas Extras",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_HEADER, weight="bold"),
            text_color=G360_GREEN
        ).pack(anchor="w")

    # ------------------------------------------------------------------
    #  FORMULARIO PRINCIPAL
    # ------------------------------------------------------------------
    def _crear_formulario(self):
        """Crea el formulario de configuración del período con picker de calendario."""
        form_container = ctk.CTkFrame(self, fg_color=G360_CARD_BG, corner_radius=CARD_CORNER_RADIUS)
        form_container.pack(fill="x", padx=PADDING_X, pady=(10, 8))

        # Título sección
        ctk.CTkLabel(
            form_container, text="CONFIGURACIÓN DEL PERÍODO",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_BODY, weight="bold"),
            text_color=G360_GREEN
        ).pack(anchor="w", padx=15, pady=(10, 3))

        # Display de período + Botón picker
        display_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        display_frame.pack(fill="x", padx=15, pady=6)

        # Card que muestra el período seleccionado
        self.display_periodo = ctk.CTkLabel(
            display_frame, text="No seleccionado",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_TITLE, weight="bold"),
            text_color=G360_TEXT, fg_color=G360_DARK,
            corner_radius=8, padx=12, pady=8, width=280
        )
        self.display_periodo.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Botón con icono
        ctk.CTkButton(
            display_frame, text="📅  Seleccionar",
            font=ctk.CTkFont(size=FONT_SIZE_BODY), width=130, height=BUTTON_HEIGHT_LARGE,
            fg_color=G360_GREEN, hover_color=G360_GREEN_HOVER,
            text_color=G360_DARK, command=self._abrir_picker
        ).pack(side="right")

        # Preview del período (21 al 20)
        self.preview_label = ctk.CTkLabel(
            form_container, text="", font=ctk.CTkFont(size=FONT_SIZE_BODY), text_color=G360_GRAY
        )
        self.preview_label.pack(anchor="w", padx=15, pady=2)

        # Leyenda de colores
        legend_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        legend_frame.pack(anchor="w", padx=15, pady=3)

        for color, texto in LEGEND_ITEMS:
            frame = ctk.CTkFrame(legend_frame, fg_color="transparent")
            frame.pack(side="left", padx=4)
            ctk.CTkLabel(frame, text="   ", fg_color=color, width=12, height=12, corner_radius=3).pack(side="left")
            ctk.CTkLabel(frame, text=texto, font=ctk.CTkFont(size=8), text_color=G360_GRAY).pack(side="left", padx=2)

        # Botón Acción
        ctk.CTkButton(
            form_container, text="Generar Planilla Excel",
            font=ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=FONT_SIZE_BODY, weight="bold"),
            fg_color=G360_GREEN, hover_color=G360_GREEN_HOVER,
            text_color=G360_DARK, height=BUTTON_HEIGHT, width=230,
            command=self._generar
        ).pack(pady=10)

        # Status
        self.status_label = ctk.CTkLabel(
            form_container, text="", font=ctk.CTkFont(size=FONT_SIZE_LABEL)
        )
        self.status_label.pack()

    def _abrir_picker(self):
        """Abre el picker de calendario."""
        picker = G360CalendarPicker(self, callback=self._procesar_periodo)
        picker.deiconify()  # Ensure window is shown
        # No llamar a mainloop() en ventanas Toplevel - solo en la ventana raíz

    # ------------------------------------------------------------------
    #  PANEL DE FERIADOS
    # ------------------------------------------------------------------
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
            panel, height=70, fg_color="transparent", text_color=G360_GRAY,
            font=ctk.CTkFont(size=FONT_SIZE_SMALL), wrap="word"
        )
        self.feriados_text.pack(fill="x", padx=12, pady=6)

    def _actualizar_lista_feriados(self):
        """Muestra SOLO los feriados que caen dentro del período seleccionado."""
        try:
            mes = int(self.mes_seleccionado.get())
            anio = int(self.anio_seleccionado.get())
            if not mes or not anio:
                self.feriados_text.delete("0.0", "end")
                self.feriados_text.insert("0.0", "Seleccione un período...")
                return
        except (ValueError, TypeError):
            self.feriados_text.delete("0.0", "end")
            return

        calendario = get_calendario()
        total_feriados = calendario.obtener_feriados(anio)

        # Calcular mes fin del período
        mes_fin = 1 if mes == 12 else mes + 1

        feriados_en_periodo = []
        for feriado in total_feriados:
            f_mes = feriado["mes"]
            f_dia = feriado["dia"]

            # Verificar si cae en el período 21/mm al 20/mm+1
            en_periodo = False
            if f_mes == mes and f_dia >= 21:
                en_periodo = True
            elif f_mes == mes_fin and f_dia <= 20:
                en_periodo = True

            if en_periodo:
                feriados_en_periodo.append(feriado)

        self.feriados_text.delete("0.0", "end")
        if feriados_en_periodo:
            texto = ["Feriados dentro del período:"]
            for f in feriados_en_periodo:
                texto.append(f"  • {f['dia']:02d}/{f['mes']:02d}  {f['nombre']}")
            self.feriados_text.insert("0.0", "\n".join(texto))
        else:
            self.feriados_text.insert("0.0", "No hay feriados en este período.")

    # ------------------------------------------------------------------
    #  PREVIEW DEL PERÍODO
    # ------------------------------------------------------------------
    def _actualizar_preview(self):
        """Actualiza el texto del preview de período."""
        try:
            mes = int(self.mes_seleccionado.get())
            anio = int(self.anio_seleccionado.get())
            if anio < 100:
                anio += 2000

            nom_meses = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun",
                         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
            mes_fin = 1 if mes == 12 else mes + 1
            anio_fin = anio + 1 if mes == 12 else anio

            preview = f"Período: 21/{nom_meses[mes]}/{str(anio)[-2:]}  →  20/{nom_meses[mes_fin]}/{str(anio_fin)[-2:]}"
            self.preview_label.configure(text=preview)
            self.display_periodo.configure(text=f"{nom_meses[mes].upper()} {anio}")
        except (ValueError, IndexError, TypeError):
            self.preview_label.configure(text="")

    # ------------------------------------------------------------------
    #  GENERACIÓN
    # ------------------------------------------------------------------
    def _generar(self):
        """Ejecuta la generación del archivo Excel."""
        try:
            mes = int(self.mes_seleccionado.get())
            if not mes:
                raise ValueError("Seleccione un período")
            anio = int(self.anio_seleccionado.get())

            self.status_label.configure(text="Generando...", text_color=G360_GREEN)
            self.update_idletasks()

            archivo = generar_excel_horas_extras(mes, anio)
            
            # Get just the filename for display
            nombre_archivo = os.path.basename(archivo)
            self.status_label.configure(text=f" Listo: {nombre_archivo}", text_color=G360_GREEN)

            if messagebox.askyesno("G360 - Éxito", f"Planilla generada: {nombre_archivo}\n\n¿Abrir carpeta contenedora?"):
                try:
                    os.startfile(os.path.dirname(archivo))
                except AttributeError:
                    # Cross-platform fallback
                    import subprocess
                    if sys.platform == "darwin":  # macOS
                        subprocess.run(["open", os.path.dirname(archivo)])
                    else:  # Linux
                        subprocess.run(["xdg-open", os.path.dirname(archivo)])

        except ValueError as e:
            messagebox.showerror("G360 - Error", f"Dato inválido: {e}")
            self.status_label.configure(text="", text_color=G360_RED)
        except Exception as e:
            messagebox.showerror("G360 - Error", f"Error inesperado: {e}")
            self.status_label.configure(text="", text_color=G360_RED)

    # ------------------------------------------------------------------
    #  FOOTER
    # ------------------------------------------------------------------
    def _crear_footer(self):
        """Crea el pie de página con créditos."""
        footer = ctk.CTkFrame(self, fg_color="transparent", height=25)
        footer.pack(fill="x", padx=PADDING_X, pady=(5, 8))
        ctk.CTkLabel(
            footer, text="Powered G360",
            font=ctk.CTkFont(size=FONT_SIZE_SMALL), text_color=G360_GRAY
        ).pack(side="right")


# ============================================================
#  ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app = G360HorasExtrasApp()
    app.mainloop()
