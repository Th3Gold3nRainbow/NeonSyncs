# Building the Windows installer (.exe)

This guide documents how to build `client.py` into a standalone executable and a Windows installer for **NeonSyncs**. **These scripts must be run on a Windows machine** (PyInstaller does not cross-compile from Linux or macOS).

Official website: **https://neonsyncs.com**

For multi-language architecture, language priority, and runtime switching details, see [docs/localization.md](localization.md).

## Steps

### 1. Get libmpv for Windows

`python-mpv` requires the native `libmpv` DLL. Download it from:
https://github.com/shinchiro/mpv-winbuild-cmake/releases

Download an `mpv-dev-x86_64-...7z` (or `mpv-x86_64-...7z`) archive, extract `libmpv-2.dll`, and place it in the repository root directory as `mpv-2.dll` (or `mpv-1.dll` depending on the `python-mpv` version).

### 2. Build the .exe

Run `build_exe.bat` from the repository root:
- Creates a Python virtual environment (`venv`).
- Installs dependencies from `requirements.txt` and `pyinstaller`.
- Produces `dist\NeonSyncs.exe`, a standalone executable bundling the mpv DLL, translation catalogs (`i18n/*.json`), WebEngine, and brand assets.

You can run or distribute `dist\NeonSyncs.exe` directly as a portable build.

### 3. Build the Windows Installer

To produce a full Windows setup with Desktop and Start Menu shortcuts and Control Panel uninstall:

1. Install **Inno Setup 6**: https://jrsoftware.org/isdl.php
2. Ensure the installer assets are in place:
   - `icon.ico` (multi-resolution icon in the repository root)
   - `wizard-image.bmp` (164x314 px, repository root)
   - `wizard-small-image.bmp` (55x58 px, repository root)
   - `brand\logo.ico` and `brand\logo.svg` (in `brand\`)
   *(All installer visuals can be regenerated automatically by running `python assets/make_logo.py`)*
3. Run `build_installer.bat` (which auto-detects Inno Setup 6 in `%LOCALAPPDATA%` or `Program Files`), or compile `installer.iss` directly with Inno Setup Compiler.
4. Output: `Output\NeonSyncs-Setup.exe` — the production installer for distribution.

The installer provides a 4-language picker (English, Français, Русский, العربية) at launch and configures `{app}\lang.txt`.

## Overall flow

```
client.py  --(PyInstaller, build_exe.bat)-->  dist\NeonSyncs.exe
dist\NeonSyncs.exe  --(Inno Setup, build_installer.bat)-->  Output\NeonSyncs-Setup.exe
```

## Translation Validation

Before building, verify all translation catalogs and UI strings with the i18n validator:

```bash
python tools/check_i18n.py
```

## Server Packaging

`server.py` does not require Windows packaging for standard operation — it is typically run on a server or VPS. If a standalone Windows executable is needed for the server, `build_exe.bat` can be adapted for `server.py` by removing `--windowed` and omitting the mpv DLL.
