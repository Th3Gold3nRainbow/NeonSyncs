@echo off
REM ============================================================
REM  build_installer.bat — a executer APRES build_exe.bat
REM  Compile installer.iss en un installeur Windows via Inno Setup.
REM ============================================================

set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if not exist %ISCC% (
    echo ERREUR: Inno Setup n'est pas trouve a l'emplacement attendu.
    echo Installez-le depuis https://jrsoftware.org/isdl.php
    echo puis relancez ce script, ou ouvrez installer.iss directement
    echo avec l'application Inno Setup Compiler.
    pause
    exit /b 1
)

if not exist dist\SyncMPV.exe (
    echo ERREUR: dist\SyncMPV.exe est introuvable.
    echo Executez d'abord build_exe.bat
    pause
    exit /b 1
)

%ISCC% installer.iss

echo.
echo Installeur genere dans Output\SyncMPV-Setup.exe
pause
