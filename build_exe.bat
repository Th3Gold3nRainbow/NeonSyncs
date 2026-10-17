@echo off
setlocal

REM ============================================================
REM  build_exe.bat - a executer sur une machine WINDOWS
REM  Compile client.py en un .exe autonome grace a PyInstaller.
REM ============================================================

echo [1/5] Verification de Python...
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo ERREUR: Python n'est pas installe ou pas dans le PATH.
    echo Installez Python depuis https://www.python.org/downloads/
    echo IMPORTANT: cochez "Add python.exe to PATH" pendant l'installation.
    echo.
    pause
    exit /b 1
)
echo OK.

echo.
if not exist venv\Scripts\python.exe (
    echo [2/5] Creation de l'environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo ERREUR: la creation de l'environnement virtuel a echoue.
        echo.
        pause
        exit /b 1
    )
) else (
    echo [2/5] Environnement virtuel existant detecte.
)

call venv\Scripts\activate.bat
set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

echo OK.

echo.
echo [3/5] Verification des dependances...
"%PYTHON_EXE%" -m pip install -r requirements.txt >nul 2>nul
"%PYTHON_EXE%" -m pip install pyinstaller >nul 2>nul
echo OK.

echo.
echo [4/5] Verification des fichiers necessaires...

set MISSING=0

if not exist mpv-2.dll (
    echo ATTENTION: mpv-2.dll est introuvable dans ce dossier.
    echo Le programme ne fonctionnera pas sans elle.
    echo Telechargez libmpv pour Windows, voir docs/building-windows.md
    set MISSING=1
)

if not exist icon.ico (
    echo ATTENTION: icon.ico est introuvable dans ce dossier.
    echo L'executable sera compile avec l'icone Windows par defaut.
    set MISSING=1
)

if not exist p2p\p2p.html (
    echo ATTENTION: p2p\p2p.html est introuvable.
    echo Le mode P2P ne pourra pas fonctionner.
    set MISSING=1
)

if not exist p2p\peerjs.min.js (
    echo ATTENTION: p2p\peerjs.min.js est introuvable.
    echo Le mode P2P ne pourra pas fonctionner.
    set MISSING=1
)

if not exist assets\fonts\Orbitron-Bold.ttf (
    echo ATTENTION: assets\fonts\Orbitron-Bold.ttf est introuvable.
    echo L'application utilisera la police systeme par defaut.
    set MISSING=1
)

if not exist assets\fonts\Rajdhani-Medium.ttf (
    echo ATTENTION: assets\fonts\Rajdhani-Medium.ttf est introuvable.
    echo L'application utilisera la police systeme par defaut.
    set MISSING=1
)

if not exist i18n\en.json (
    echo ATTENTION: i18n\en.json est introuvable.
    echo Les traductions de l'application seront manquantes.
    set MISSING=1
)

if "%MISSING%"=="1" (
    echo.
    echo Vous pouvez continuer sans ces fichiers, mais le resultat sera incomplet.
    echo Appuyez sur une touche pour continuer quand meme, ou fermez cette
    echo fenetre pour ajouter les fichiers manquants avant de relancer.
    pause
)

echo.
echo [5/5] Compilation avec PyInstaller...
set "PYQT5_DIR=venv\Lib\site-packages\PyQt5"

"%PYTHON_EXE%" -m PyInstaller --noconfirm --onefile --windowed --name NeonSyncs --icon icon.ico ^
    --add-binary "mpv-2.dll;." ^
    --add-data "p2p;p2p" ^
    --add-data "assets;assets" ^
    --add-data "brand;brand" ^
    --add-data "i18n\*.json;i18n" ^
    --add-binary "%PYQT5_DIR%\Qt5\bin\QtWebEngineProcess.exe;PyQt5\Qt5\bin" ^
    --add-data "%PYQT5_DIR%\Qt5\resources;PyQt5\Qt5\resources" ^
    --add-data "%PYQT5_DIR%\Qt5\translations\qtwebengine_locales;PyQt5\Qt5\translations\qtwebengine_locales" ^
    --collect-all PyQt5.QtWebEngineWidgets ^
    --collect-all PyQtWebEngine ^
    client.py
if errorlevel 1 (
    echo.
    echo ERREUR: la compilation PyInstaller a echoue.
    echo Faites defiler vers le haut pour voir le detail de l'erreur.
    echo.
    pause
    exit /b 1
)

if exist icon.ico copy /y icon.ico dist\icon.ico >nul

echo.
echo ============================================================
echo Termine ! L'executable se trouve dans dist\NeonSyncs.exe
echo Vous pouvez maintenant lancer build_installer.bat (Inno Setup)
echo pour generer un vrai installeur Windows.
echo ============================================================
echo.
pause
