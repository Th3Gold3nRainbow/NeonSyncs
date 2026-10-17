# Building the Windows installer (.exe)

This folder contains everything needed to turn `client.py` into a real,
double-clickable Windows installer for **NeonSyncs**. **These scripts must be run on a
Windows machine** (PyInstaller doesn't cross-compile from Linux/Mac).

Official website: **https://neonsyncs.com**

## Multi-Language Support (4 Languages)

NeonSyncs is fully internationalized across **4 languages**:
- **English** (`en`)
- **Français** (`fr`)
- **Русский** (`ru`)
- **العربية** (`ar`, with native Right-To-Left layout and proper bidirectional Unicode isolation)

### Language Selection & Priority Order
1. **In-App Hot Switching**: Users can change language on the fly via the dropdown in the application header. The entire UI updates dynamically without restarting or interrupting active P2P watchparties.
2. **Persistent Settings**: User choices are saved in `%APPDATA%\NeonSyncs\settings.json`.
3. **Installer Language**: Selected during setup and written to `{app}\lang.txt` (read-only for the application; the app never modifies it).
4. **Startup Priority**:
   - **a.** Manual user selection in `settings.json`, unless the installer was re-run since;
   - **b.** Installer language from `lang.txt` (if the installer was re-run with another language, it takes precedence and resets manual choice);
   - **c.** Operating system locale (`QLocale.system()`);
   - **d.** Fallback to English (`en`).
5. **Uninstaller Cleanup**: During uninstall, the user is prompted whether to remove user settings in `%APPDATA%\NeonSyncs`.

## Steps

### 1. Get libmpv for Windows

`python-mpv` needs the native `libmpv` DLL. Download it here:
https://github.com/shinchiro/mpv-winbuild-cmake/releases

Grab an `mpv-dev-x86_64-...7z` (or `mpv-x86_64-...7z`) archive, extract
`libmpv-2.dll` from it, and **place it in this same folder, renamed to
`mpv-2.dll`** (or `mpv-1.dll` depending on your installed `python-mpv`
version — the error message at launch will tell you which one it's
looking for if you need to adjust).

### 2. Build the .exe

Double-click `build_exe.bat` (or run it from a terminal). It will:
- create a Python virtual environment,
- install dependencies (`PyQt5`, `python-mpv`, `pyinstaller`),
- produce `dist\NeonSyncs.exe`, a standalone executable (the mpv DLL,
  translation catalogs `i18n/*.json`, and WebEngine/assets are bundled inside it).

You can already distribute `dist\NeonSyncs.exe` as-is — it works without
installation, portable-style.

### 3. Build the Windows Installer

For an installer with Desktop/Start Menu shortcuts and clean
uninstall through Control Panel:

1. Install **Inno Setup 6**: https://jrsoftware.org/isdl.php
2. Make sure `brand\logo.ico`, `wizard-image.bmp` and `wizard-small-image.bmp`
   are in their expected folders.
3. Run `build_installer.bat` (which auto-detects Inno Setup 6 in `%LOCALAPPDATA%` or `Program Files`), or open `installer.iss` directly in Inno Setup Compiler and hit *Build > Compile*.
4. Result: `Output\NeonSyncs-Setup.exe` — that's the production file to distribute
   to users.

The installer shows a language picker with all 4 languages (English, Français, Русский, العربية)
right at launch, styled with custom cyberpunk neon artwork and logo.

## Overall flow

```
client.py  --(PyInstaller, build_exe.bat)-->  dist\NeonSyncs.exe
dist\NeonSyncs.exe  --(Inno Setup, build_installer.bat)-->  Output\NeonSyncs-Setup.exe
```

## Translation Validation

Before building, verify all translation catalogs and UI strings with the i18n validator:
```bash
python tools\check_i18n.py
```

## The server (`server.py`) doesn't need packaging

`server.py` doesn't need to be turned into a `.exe` — it's typically
something you run on a VPS/server or in the background on an
always-on machine. If you want a `.exe` for the server too (e.g. so a
non-technical user can host it), the same `build_exe.bat` works with
`server.py` instead of `client.py` (drop `--windowed` and the mpv DLL,
neither is needed server-side).

