# Building the Windows installer (.exe)

This folder contains everything needed to turn `client.py` into a real,
double-clickable Windows installer. **These scripts must be run on a
Windows machine** (PyInstaller doesn't cross-compile from Linux/Mac).

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
- produce `dist\SyncMPV.exe`, a standalone executable (the mpv DLL is
  bundled inside it).

You can already distribute `dist\SyncMPV.exe` as-is — it works without
installation, portable-style.

### 3. (Optional but recommended) Build a real installer

For an installer with Desktop/Start Menu shortcuts and clean
uninstall through Control Panel:

1. Install **Inno Setup**: https://jrsoftware.org/isdl.php
2. Make sure `icon.ico`, `wizard-image.bmp` and `wizard-small-image.bmp`
   (included with the project — the SyncMPV logo) are in the same
   folder as `installer.iss`.
3. Run `build_installer.bat`, or open `installer.iss` directly in Inno
   Setup Compiler and hit *Build > Compile*.
4. Result: `Output\SyncMPV-Setup.exe` — that's the file to distribute
   to users.

The installer shows a language picker (English / French) right at
launch, and a custom logo (icon + side banner).

## Overall flow

```
client.py  --(PyInstaller, build_exe.bat)-->  dist\SyncMPV.exe
dist\SyncMPV.exe  --(Inno Setup, build_installer.bat)-->  Output\SyncMPV-Setup.exe
```

## The server (`server.py`) doesn't need packaging

`server.py` doesn't need to be turned into a `.exe` — it's typically
something you run on a VPS/server or in the background on an
always-on machine. If you want a `.exe` for the server too (e.g. so a
non-technical user can host it), the same `build_exe.bat` works with
`server.py` instead of `client.py` (drop `--windowed` and the mpv DLL,
neither is needed server-side).
