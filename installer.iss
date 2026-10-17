; ============================================================
;  installer.iss — NeonSyncs Inno Setup Script
;  Professional Windows installer for NeonSyncs with full i18n
;  (English, French, Russian, Arabic RTL).
; ============================================================

#define MyAppName "NeonSyncs"
#define MyAppVersion "2.2.0"
#define MyAppPublisher "NeonSyncs"
#define MyAppURL "https://neonsyncs.com"
#define MyAppExeName "NeonSyncs.exe"

[Setup]
AppId={{B6E3C6C1-9B7A-4F1E-8B6E-SYNCMPV00001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=NeonSyncs-Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=icon.ico
WizardImageFile=wizard-image.bmp
WizardSmallImageFile=wizard-small-image.bmp
WizardImageStretch=no
ShowLanguageDialog=yes
PrivilegesRequiredOverridesAllowed=commandline

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"

[CustomMessages]
; --- English ---
english.CreateDesktopIcon=Create a &desktop shortcut
english.AdditionalIcons=Additional shortcuts:
english.LaunchProgram=Launch {#MyAppName}
english.AppRunningWarning={#MyAppName} is currently running. Please close the application before continuing.
english.VisitWebsite=Visit {#MyAppName} official website
english.RemoveSettingsPrompt=Do you also want to remove your personal settings and data in %APPDATA%\NeonSyncs?

; --- French ---
french.CreateDesktopIcon=Créer un raccourci sur le &bureau
french.AdditionalIcons=Raccourcis supplémentaires :
french.LaunchProgram=Lancer {#MyAppName}
french.AppRunningWarning={#MyAppName} est actuellement en cours d'exécution. Veuillez fermer l'application avant de continuer.
french.VisitWebsite=Visiter le site officiel de {#MyAppName}
french.RemoveSettingsPrompt=Souhaitez-vous également supprimer vos paramètres et données personnelles dans %APPDATA%\NeonSyncs ?

; --- Russian ---
russian.CreateDesktopIcon=Создать ярлык на &Рабочем столе
russian.AdditionalIcons=Дополнительные ярлыки:
russian.LaunchProgram=Запустить {#MyAppName}
russian.AppRunningWarning=Приложение {#MyAppName} запущено. Пожалуйста, закройте его перед продолжением.
russian.VisitWebsite=Посетить официальный сайт {#MyAppName}
russian.RemoveSettingsPrompt=Удалить также ваши персональные настройки и данные в %APPDATA%\NeonSyncs?

; --- Arabic ---
arabic.CreateDesktopIcon=إنشاء اختصار على &سطح المكتب
arabic.AdditionalIcons=اختصارات إضافية:
arabic.LaunchProgram=تشغيل {#MyAppName}
arabic.AppRunningWarning=تطبيق {#MyAppName} قيد التشغيل حالياً. يرجى إغلاق البرنامج قبل المتابعة.
arabic.VisitWebsite=زيارة الموقع الرسمي لـ {#MyAppName}
arabic.RemoveSettingsPrompt=هل ترغب أيضاً في حذف إعداداتك وبياناتك الشخصية في %APPDATA%\NeonSyncs؟

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\NeonSyncs.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "brand\logo.ico"; DestDir: "{app}\brand"; Flags: ignoreversion
Source: "brand\logo.svg"; DestDir: "{app}\brand"; Flags: ignoreversion
Source: "i18n\*.json"; DestDir: "{app}\i18n"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{group}\{cm:VisitWebsite}"; Filename: "{#MyAppURL}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\lang.txt"

[Code]
// Writes the language chosen during setup into lang.txt next to the executable.
// client.py reads this file on startup to match the installer's language.
procedure CurStepChanged(CurStep: TSetupStep);
var
  LangFile: string;
  LangCode: string;
begin
  if CurStep = ssPostInstall then
  begin
    LangFile := ExpandConstant('{app}\lang.txt');
    if ActiveLanguage() = 'french' then
      LangCode := 'fr'
    else if ActiveLanguage() = 'russian' then
      LangCode := 'ru'
    else if ActiveLanguage() = 'arabic' then
      LangCode := 'ar'
    else
      LangCode := 'en';
    SaveStringToFile(LangFile, LangCode, False);
  end;
end;

// Prompts user during uninstallation to cleanly remove %APPDATA%\NeonSyncs if desired.
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppDataDir: string;
begin
  if CurUninstallStep = usUninstall then
  begin
    AppDataDir := ExpandConstant('{userappdata}\{#MyAppName}');
    if DirExists(AppDataDir) then
    begin
      if MsgBox(CustomMessage('RemoveSettingsPrompt'), mbConfirmation, MB_YESNO) = IDYES then
      begin
        DelTree(AppDataDir, True, True, True);
      end;
    end;
  end;
end;
