# Third-Party Software Notices

NeonSyncs incorporates or links against open-source third-party software components. This document lists these components, their authors, source locations, and licenses.

## License Compatibility Notice

The NeonSyncs source code is licensed under the MIT License (see `LICENSE`).

Pre-compiled binary releases (such as `NeonSyncs.exe` and `NeonSyncs-Setup.exe`) bundle or link dynamically with components licensed under the GNU General Public License version 3 (PyQt5, PyQtWebEngine) and GNU General Public License version 2 or later (libmpv builds compiled with GPL FFmpeg).

Under the terms of the GNU General Public License version 3, any binary distribution that combines MIT-licensed source code with GPLv3 components constitutes a combined work and must be distributed under the terms of the GNU General Public License version 3. Users who receive such binary distributions are entitled to obtain the complete corresponding source code under GPLv3.

---

## Bundled and Linked Components

### libmpv / mpv
- Project: mpv media player library
- Source: https://github.com/mpv-player/mpv
- Windows builds: https://github.com/shinchiro/mpv-winbuild-cmake
- License: GNU General Public License v2+ / v3 (when compiled with GPL FFmpeg options)

### PyQt5
- Project: PyQt5 Python bindings for Qt5
- Author: Riverbank Computing Limited
- Source: https://riverbankcomputing.com/software/pyqt/
- License: GNU General Public License version 3 (GPLv3)

### PyQtWebEngine
- Project: PyQtWebEngine Python bindings for QtWebEngine
- Author: Riverbank Computing Limited
- Source: https://riverbankcomputing.com/software/pyqtwebengine/
- License: GNU General Public License version 3 (GPLv3)

### python-mpv
- Project: Python ctypes wrapper for libmpv
- Author: Jonas Kümmerlin
- Source: https://github.com/jaseg/python-mpv
- License: GNU Affero General Public License v3 or later (AGPLv3+) / LGPLv2.1+ option

### PeerJS
- Project: PeerJS WebRTC client library
- Authors: The PeerJS Team
- Source: https://github.com/peers/peerjs
- License: MIT License

### Orbitron Font
- Designer: Matt McInerney
- Source: https://fonts.google.com/specimen/Orbitron
- License: SIL Open Font License, Version 1.1 (OFL-1.1)
- License text: `assets/fonts/Orbitron-OFL.txt`

### Rajdhani Font
- Designer: Indian Type Foundry
- Source: https://fonts.google.com/specimen/Rajdhani
- License: SIL Open Font License, Version 1.1 (OFL-1.1)
- License text: `assets/fonts/Rajdhani-OFL.txt`

### Inno Setup
- Author: Jordan Russell, Martijn Laan
- Source: https://jrsoftware.org/isinfo.php
- License: Inno Setup License (modified BSD license)
