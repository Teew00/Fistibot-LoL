@echo off
REM Launcher pour FistiBot avec gestion de l'environnement virtuel
REM Ce script active l'environnement virtuel et lance le GUI

setlocal enabledelayedexpansion

REM Déterminer le répertoire du script
set SCRIPT_DIR=%~dp0

REM Vérifier que l'environnement virtuel existe
if not exist "%SCRIPT_DIR%.venv\Scripts\activate.bat" (
    echo.
    echo ❌ Erreur: L'environnement virtuel n'a pas été trouvé!
    echo.
    echo Pour configurer l'environnement:
    echo   1. Ouvre PowerShell dans ce dossier
    echo   2. Lance: python -m venv .venv
    echo   3. Lance: .venv\Scripts\Activate.ps1
    echo   4. Lance: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activer l'environnement virtuel
call "%SCRIPT_DIR%.venv\Scripts\activate.bat"

REM Changer de répertoire
cd /d "%SCRIPT_DIR%"

REM Lancer le GUI
python gui.py

pause
