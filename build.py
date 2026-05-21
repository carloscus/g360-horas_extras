#!/usr/bin/env python3
"""
Build script para empaquetar G360 Horas Extras con PyInstaller.
Modo: One Directory (recomendado para apps con assets)
"""
import os
import sys
import subprocess
import shutil

def build():
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    print("=" * 50)
    print("  G360 Horas Extras - PyInstaller Build")
    print("=" * 50)
    
    icon_path = os.path.join(project_root, "assets", "images", "favicon.ico")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=G360-Horas-Extras",
        "--onedir",
        "--windowed",
        f"--icon={icon_path}",
        "--paths=.",
        "--add-data=assets/images/logo-g360.png;assets/images",
        "--add-data=assets/images/favicon.ico;assets/images",
        "--add-data=feriados.json;.",
        "--hidden-import=tkcalendar",
        "--hidden-import=babel.numbers",
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=xlsxwriter",
        "--noconfirm",
        "--clean",
        "run.py"
    ]
    
    print(f"\nEjecutando: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode == 0:
        dist_folder = os.path.join(project_root, "dist", "G360-Horas-Extras")
        instrucciones_src = os.path.join(project_root, "INSTRUCCIONES.txt")
        instrucciones_dst = os.path.join(dist_folder, "INSTRUCCIONES.txt")
        
        if os.path.exists(instrucciones_src):
            shutil.copy2(instrucciones_src, instrucciones_dst)
            print(f"\n  INSTRUCCIONES.txt copiado a {dist_folder}/")
        
        print("\n" + "=" * 50)
        print("  Build exitoso!")
        print("  Output: dist/G360-Horas-Extras/")
        print("=" * 50)
    else:
        print("\nBuild fallido. Revisa los errores arriba.")
        sys.exit(1)

if __name__ == "__main__":
    build()
