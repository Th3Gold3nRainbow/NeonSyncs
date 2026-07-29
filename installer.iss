; ============================================================
;  installer.iss — script Inno Setup
;  Genere un installeur Windows classique (setup.exe) pour SyncMPV.
;
;  Pre-requis :
;    1. Avoir deja execute build_exe.bat (dist\SyncMPV.exe doit exister)
;    2. Installer Inno Setup : https://jrsoftware.org/isdl.php
;    3. Placer icon.ico, wizard-image.bmp et wizard-small-image.bmp
;       dans le MEME dossier que ce fichier .iss (fournis avec le projet)
;    4. Ouvrir ce fichier avec Inno Setup Compiler, puis "Build > Compile"
;       (ou en ligne de commande : ISCC.exe installer.iss)
;
;  L'installeur propose maintenant un choix de langue (Anglais / Francais)
;  des le lancement de setup.exe, et affiche un logo moderne (icone +
;  bandeau lateral) genere pour SyncMPV.
;
;  Le resultat (Output\SyncMPV-Setup.exe) est l'installeur final
;  a distribuer : double-clic -> installation -> raccourcis ->
;  desinstallation propre via le Panneau de configuration.
; ============================================================

#define MyAppName "SyncMPV"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Th3Gold3nRainbow"
#define MyAppExeName "SyncMPV.exe"

[Setup]
AppId={{B6E3C6C1-9B7A-4F1E-8B6E-SYNCMPV00001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=SyncMPV-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=icon.ico
WizardImageFile=wizard-image.bmp
WizardSmallImageFile=wizard-small-image.bmp
WizardImageStretch=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\SyncMPV.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; La DLL mpv est deja embarquee dans l'exe via --add-binary,
; mais si vous ne l'avez pas embarquee, decommentez la ligne suivante :
; Source: "mpv-2.dll"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
