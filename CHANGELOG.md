# Changelog

All notable changes to NeonSyncs are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.0] - 2026-10-18

### Added
- Language selector button in the sidebar header with a native language dropdown menu (English, Français, Русский, العربية) and globe icon.
- Local volume control button and slider with mute toggle and persistent volume settings in `%APPDATA%\NeonSyncs\settings.json`.
- Fullscreen mode toggle by double-clicking the video display area, debounced to prevent re-triggering during window transitions.

### Changed
- Restricted Windows installer packaging to include only compiled translation files (`i18n\*.json`).
- Cleaned up repository structure and updated internal documentation.

### Fixed
- Brand name "NEONSYNCS" display in the application header aligned with the new language button.
- Installer language selection reliably enforced on subsequent installations by recording a unique session token in `lang.txt`.

## [2.2.0] - 2026-10-17

### Added
- Peer-to-peer room connectivity using WebRTC via PeerJS and QtWebEngine.
- Room creation with generated short room IDs and optional password protection.
- Host-relayed star topology synchronization for rooms with more than two participants.
- Ping-based network latency estimation and scheduled playback actions.
- Playback drift correction with jump thresholds and interval cooldowns.
- Full internationalization across four languages: English, French, Russian, and Arabic.
- Right-to-left (RTL) layout support for Arabic with bidirectional Unicode isolates.
- In-app hot language switcher preserving active P2P connections without restart.
- Multi-language Inno Setup Windows installer with branded neon wizard graphics.
- Cyber Cyan visual theme with custom QSS styling, Orbitron and Rajdhani typography.
- STUN and TURN server configuration support via `p2p/ice_servers.json`.
- Automated internationalization test suite verifying all 12 pairwise language transitions.

### Changed
- Rebranded application, executable, installer, and documentation from SyncMPV to NeonSyncs.
- Default input values, field placeholders, and dynamic status bar messages now translate on language changes.
- Stored user preferences in `%APPDATA%\NeonSyncs\settings.json`.

### Fixed
- Windows non-client title bar rendering glitch on initial launch.

## [1.1.0] - 2026-08-01

### Added
- Seekable progress slider in the playback controls bar.
- Dedicated 10s and 30s seek buttons and keyboard arrow shortcuts (10s, 60s).
- Fullscreen mode (F, F11, or double-click) with auto-hiding interface.
- Time display labels showing current position and total duration.
- Network latency compensation through periodic ping/pong requests.
- Minimum correction interval and big jump threshold constants to prevent playback stuttering.
- Optional server password protection (`--password`).
- Bilingual Windows installer (English and French language picker).

### Changed
- Disabled hardware decoding in mpv integration (`hwdec="no"`) to resolve GPU driver conflicts.
- Chat automatically scrolls to latest message.

### Fixed
- Black screen issue when embedding mpv into Qt widget by disabling hardware decoding fallback.
- Asynchronous echo loop when applying remote playback states by introducing a delayed debounce before clearing the remote application flag.
- Connection status remaining stuck on "Connected" when connection dropped.
- Desktop shortcut displaying generic Windows icon instead of application logo.
- Warning displayed when trying to send chat messages before connecting.

## [1.0.0] - 2026-07-29

### Added
- Initial release of synchronized video player for local files (formerly SyncMPV).
- Embedded libmpv window integrated via Qt window handle (`wid`).
- Client-server synchronization protocol over TCP sockets (`server.py`).
- Integrated chat panel and connected user list.
