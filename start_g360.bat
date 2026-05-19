@echo off
chcp 65001 >nul
title G360 - Generador de Horas Extras
color 0A

echo.
echo  ============================================
echo   G360 - Generador de Plantillas de Horas Extras
echo   Powered by OpenCode Agent
echo  ============================================
echo.

cd /d "%~dp0"

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo Por favor instale Python 3.8+ desde https://python.org
    pause
    exit /b 1
)

REM Verificar entorno virtual o instalar dependencias
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [INFO] Entorno virtual activado.
) else (
    echo [INFO] Verificando dependencias...
    pip install -q customtkinter xlsxwriter tkcalendar babel Pillow
)

REM Verificar dependencias clave
python -c "import customtkinter, xlsxwriter, tkcalendar, PIL" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando dependencias necesarias...
    pip install -q customtkinter xlsxwriter tkcalendar babel Pillow
)

echo [INFO] Iniciando aplicacion G360 Horas Extras...
echo.

python src\main.py

if errorlevel 1 (
    echo.
    echo [ERROR] La aplicacion finalizo con errores.
    pause
)

echo.
echo [INFO] Cerrando sesion G360...
timeout /t 2 >nul
