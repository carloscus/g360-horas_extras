# G360 Horas Extras 🚀

> Generador de planillas de horas extras en formato Excel corporativo. Forma parte de la familia de microherramientas G360 para gestión de tiempos y planificación.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

---

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Características](#características)
- [Tecnologías](#tecnologías)
- [Instalación](#instalación)
- [Uso](#uso)
- [Build](#build)
- [Estructura](#estructura)
- [Configuración de Tema](#configuración-de-tema)
- [Feriados](#feriados)
- [Paleta de Colores Excel](#paleta-de-colores-excel)
- [Familia G360](#familia-g360)

---

## 📝 Descripción

Aplicación de escritorio (Python + CustomTkinter) que genera archivos Excel profesionales para el registro de horas extras. Incluye un calendario picker intuitivo, gestión de feriados personalizables y formato corporativo con colores diferenciados por tipo de día.

**Tipo**: Desktop App / Generator  
**Plataforma**: Python 3.13+ (Windows, macOS, Linux)  
**Distribución**: Ejecutable PyInstaller (--onedir)

---

## ✨ Características

### 📅 Picker de Calendario
- Selección visual del período con `tkcalendar`
- Regla automática: 21/mm → 20/mm+1
- Preview del período en tiempo real
- Leyenda de colores (feriado, sábado, domingo, laboral)

### 🎯 Gestión de Feriados
- Modal dedicado para agregar/eliminar feriados fijos
- Feriados calculados (Semana Santa) en solo lectura
- Persistencia en `%APPDATA%/G360-Horas-Extras/feriados.json`
- Opción de restaurar valores por defecto

### 📊 Excel Corporativo
- Días laborables: fondo gris suave
- Sábados: fondo azul corporativo
- Domingos: fondo rojo suave
- Feriados: fondo rojo corporativo con texto blanco
- Autor del archivo: `ccusi`

### 🎨 Branding G360
- Logo G360 en encabezado
- Paleta de colores oficial (#00d084)
- Firma "Powered G360" en footer

---

## 🛠️ Tecnologías

- **Python 3.13+** - Lenguaje principal
- **CustomTkinter** - GUI moderna con tema oscuro
- **tkcalendar** - Widget de calendario
- **XlsxWriter** - Generación de archivos Excel
- **Pillow** - Procesamiento de imágenes (logo)
- **PyInstaller** - Empaquetado en ejecutable

---

## 📦 Instalación

### Requisitos

- Python 3.13+
- pip

### Instalación

```bash
# Clonar repositorio
git clone <repository-url>
cd g360-Horas_Extras

# Instalar dependencias
pip install -r requirements.txt
```

---

## 🎯 Uso

### Modo desarrollo

```bash
python src/main.py
```

O ejecutar `start_g360.bat` (Windows).

### Ejecutable

El ejecutable se encuentra en `dist/G360-Horas-Extras/G360-Horas-Extras.exe`

### Flujo de uso

1. **Seleccionar período**: Click en "📅 Seleccionar" y elegir cualquier fecha del período deseado
2. **Verificar feriados**: Revisar el panel "FERIADOS DEL PERÍODO"
3. **Gestionar feriados** (opcional): Click en "⚙️ Feriados" para agregar/eliminar
4. **Generar planilla**: Click en "Generar Planilla Excel"
5. **Abrir carpeta**: Confirmar para abrir la carpeta con el archivo generado

---

## 🔧 Build

```bash
python build.py
```

Genera el ejecutable en modo `--onedir` con todos los assets empaquetados en `dist/G360-Horas-Extras/`.

---

## 📂 Estructura

```
g360-Horas_Extras/
├── assets/
│   └── images/
│       └── logo-g360.png
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── theme.py          # Colores, fuentes y constantes de estilo
│   ├── core/
│   │   └── excel_generator.py # Lógica de generación Excel
│   ├── ui/
│   │   └── feriados_manager.py # Modal de gestión de feriados
│   ├── utils/
│   │   └── feriados.py        # Cálculo de feriados (fijos + Semana Santa)
│   └── main.py                # Entry point de la aplicación
├── feriados.json              # Feriados por defecto
├── build.py                   # Script de build PyInstaller
├── requirements.txt
├── start_g360.bat
└── run_script.bat
```

---

## 🎨 Configuración de Tema

### Jerarquía Tipográfica

| Constante | Tamaño | Uso |
|---|---|---|
| `FONT_SIZE_HEADER` | 24 | Título principal |
| `FONT_SIZE_TITLE` | 14 | Secciones |
| `FONT_SIZE_BODY` | 12 | Texto general, botones, status |
| `FONT_SIZE_SMALL` | 10 | Leyendas, detalles |

### Colores G360 (UI)

| Constante | Valor | Uso |
|---|---|---|
| `G360_GREEN` | `#00d084` | Primary brand color |
| `G360_DARK` | `#0c0c0c` | Main background |
| `G360_CARD_BG` | `#1a1a1a` | Card/surface background |
| `G360_TEXT` | `#ffffff` | Primary text |
| `G360_GRAY` | `#a0a0a0` | Secondary/muted text |
| `G360_RED` | `#ff4444` | Error states |
| `G360_BLUE` | `#4488ff` | Accent |

---

## 📅 Feriados

Los feriados se cargan desde `feriados.json` (defecto) y se complementan con la configuración del usuario en `%APPDATA%/G360-Horas-Extras/feriados.json`.

### Feriados Fijos (editables)

| Fecha | Feriado |
|---|---|
| 01/01 | Año Nuevo |
| 01/05 | Día del Trabajo |
| 29/06 | San Pedro y San Pablo |
| 28/07 | Fiestas Patrias |
| 29/07 | Fiestas Patrias |
| 30/08 | Santa Rosa de Lima |
| 08/10 | Combate de Angamos |
| 01/11 | Día de Todos los Santos |
| 08/12 | Inmaculada Concepción |
| 09/12 | Batalla de Ayacucho |
| 25/12 | Navidad |

### Feriados Calculados (solo lectura)

- **Jueves Santo**: Variable (algoritmo de Meeus/Jones/Butcher)
- **Viernes Santo**: Variable (algoritmo de Meeus/Jones/Butcher)

---

## 🎨 Paleta de Colores Excel

| Tipo | Fondo | Texto |
|---|---|---|
| Laborable | `#F5F5F5` | `#333333` |
| Sábado | `#D6E4F0` | `#2C3E50` |
| Domingo | `#FCE4E4` | `#C0392B` |
| Feriado | `#E74C3C` | `#FFFFFF` |

---

## 🤝 Familia G360

Este proyecto forma parte de la familia de microherramientas **G360** para apoyo CRM y gestión de datos en escritorio.

### Herramientas Relacionadas

- **[g360-cli](https://github.com/carloscus/g360-cli)**: Bootstrap de proyectos G360
- **[g360-signature](https://github.com/carloscus/g360-signature)**: Web component de branding
- **[g360-day-calculator](https://github.com/carloscus/g360-day-calculator)**: Calculadora de días laborables
- **[g360-nc-sustentor](https://github.com/carloscus/g360-nc-sustentor)**: Generación de sustento para NC
- **[g360-order-xlsx](https://github.com/carloscus/g360-order-xlsx)**: Procesador de cotizaciones Excel

---

**Marca**: G360  
**Isotipo**: 3 puntos verticales (gris-verde-gris) + chevron `>`  
**Autor**: Carlos Cusi  
**Desarrollo**: Con asistencia de herramientas de código IA (Vibe Code)  
**Powered by**: [g360-signature](https://github.com/carloscus/g360-signature)
