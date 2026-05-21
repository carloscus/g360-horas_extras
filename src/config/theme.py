"""
G360 Horas Extras - Theme Configuration
Paleta de colores, fuentes y constantes de estilo centralizadas.
"""

# ============================================================
#  G360 BRAND COLORS (UI)
# ============================================================
G360_GREEN = "#00d084"      # Primary brand color (G360 glow)
G360_DARK = "#0c0c0c"       # Main background
G360_CARD_BG = "#1a1a1a"    # Card/surface background
G360_TEXT = "#ffffff"       # Primary text
G360_GRAY = "#a0a0a0"       # Secondary/muted text (brighter for dark bg contrast)
G360_RED = "#ff4444"        # Error states
G360_BLUE = "#4488ff"       # Accent

# ============================================================
#  EXCEL CORPORATE PALETTE (suavizada)
# ============================================================
BG_LABORABLE = '#F5F5F5'    # Monday-Friday (gris muy suave)
BG_SABADO = '#D6E4F0'       # Saturday (azul corporativo suave)
BG_DOMINGO = '#FCE4E4'      # Sunday (rojo suave)
BG_FERIADO = '#E74C3C'      # Holiday (rojo corporativo)

COLOR_LABORABLE_TEXTO = '#333333'  # Texto oscuro sobre gris
COLOR_SABADO_TEXTO = '#2C3E50'     # Texto oscuro sobre azul
COLOR_DOMINGO_TEXTO = '#C0392B'    # Texto oscuro sobre rojo suave
COLOR_FERIADO_TEXTO = '#FFFFFF'    # Texto blanco sobre rojo corporativo

# ============================================================
#  HOVER/INTERACTIVE STATES
# ============================================================
G360_GREEN_HOVER = "#00b370"  # Darker green for hover

# ============================================================
#  FONT CONFIGURATION
# ============================================================
FONT_FAMILY_PRIMARY = "Segoe UI"    # Primary font (Windows)
FONT_FAMILY_FALLBACK = "Arial"      # Fallback for cross-platform
FONT_FAMILY_MONO = "Consolas"       # Monospace for data

FONT_SIZE_HEADER = 28
FONT_SIZE_TITLE = 18
FONT_SIZE_BODY = 15
FONT_SIZE_SMALL = 13

# ============================================================
#  LAYOUT CONSTANTS (optimizado para pantallas pequeñas 720p/12-13")
# ============================================================
WINDOW_WIDTH = 620
WINDOW_HEIGHT = 580
WINDOW_RESIZABLE = True

CARD_CORNER_RADIUS = 12
BUTTON_HEIGHT = 40
BUTTON_HEIGHT_LARGE = 44

PADDING_X = 16
PADDING_Y = 12

# ============================================================
#  LEGEND COLORS (for calendar picker info)
# ============================================================
LEGEND_ITEMS = [
    (G360_GREEN, "Feriado"),
    (G360_RED, "Domingo"),
    (G360_BLUE, "Sábado"),
    ("#ffffff", "Laboral")
]
