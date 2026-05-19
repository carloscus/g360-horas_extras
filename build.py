#!/usr/bin/env python3
"""
Build script para empaquetar G360 Horas Extras con PyInstaller.
Modo: One Directory (recomendado para apps con assets)
"""
import os
import sys
import subprocess

def build():
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    print("=" * 50)
    print("  G360 Horas Extras - PyInstaller Build")
    print("=" * 50)
    
    icon_path = os.path.join(project_root, "assets", "images", "icon.ico")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=G360-Horas-Extras",
        "--onedir",
        "--windowed",
        f"--icon={icon_path}",
        "--add-data=assets/images/logo-g360.png;assets/images",
        "--add-data=feriados.json;.",
        "--hidden-import=tkcalendar",
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=xlsxwriter",
        "--hidden-import=src.core.excel_generator",
        "--hidden-import=src.utils.feriados",
        "--hidden-import=src.utils.periodo",
        "--hidden-import=src.config.theme",
        "--hidden-import=src.ui.feriados_manager",
        "--noconfirm",
        "--clean",
        "src/main.py"
    ]
    
    print(f"\nEjecutando: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode == 0:
        print("\n" + "=" * 50)
        print("  Build exitoso!")
        print("  Output: dist/G360-Horas-Extras/")
        print("=" * 50)
    else:
        print("\nBuild fallido. Revisa los errores arriba.")
        sys.exit(1)

if __name__ == "__main__":
    build()
