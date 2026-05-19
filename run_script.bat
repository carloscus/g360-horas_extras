@echo off
chcp 65001 >nul
title G360 - CLI Generador de Horas Extras
color 0A

echo.
echo  ============================================
echo   G360 - CLI Generador de Horas Extras
echo  ============================================
echo.

cd /d "%~dp0"

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    pause
    exit /b 1
)

REM Verificar dependencias
python -c "import xlsxwriter" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando dependencias...
    pip install -q xlsxwriter
)

echo [INFO] Iniciando generador CLI...
echo.

python src\cli.py %*

if errorlevel 1 (
    echo.
    echo [ERROR] Error al generar la planilla.
    pause
)
