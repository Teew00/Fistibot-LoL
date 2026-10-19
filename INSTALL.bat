@echo off
REM Script d'installation automatisé pour FistiBot
REM À lancer une seule fois au premier démarrage

setlocal enabledelayedexpansion

echo.
echo =========================================
echo     FistiBot - Installation
echo =========================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo.
    echo Télécharge Python depuis: https://www.python.org/downloads/
    echo Assure-toi de cocher "Add Python to PATH" lors de l'installation!
    echo.
    pause
    exit /b 1
)

echo ✓ Python trouvé
echo.

REM Créer l'environnement virtuel
if not exist ".venv" (
    echo 🔨 Création de l'environnement virtuel...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ Erreur lors de la création de l'environnement virtuel
        pause
        exit /b 1
    )
    echo ✓ Environnement virtuel créé
) else (
    echo ✓ Environnement virtuel déjà existant
)

echo.
echo 📦 Installation des dépendances...

REM Activer l'environnement virtuel
call ".venv\Scripts\activate.bat"

REM Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Erreur lors de l'installation des dépendances
    pause
    exit /b 1
)

echo.
echo ✅ Installation réussie!
echo.
echo 📋 Prochaines étapes:
echo   1. Configure les clés API (Discord Token, Riot API Keys)
echo   2. Lance FistiBot.bat pour démarrer le bot
echo.
pause
