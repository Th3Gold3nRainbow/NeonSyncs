# Changelog

All notable changes to NeonSyncs are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-10-17

### Added
- Peer-to-peer room connectivity using WebRTC via PeerJS and QtWebEngine.
- Room creation with generated short room IDs and optional password protection.
- Host-relayed multi-peer mesh synchronization for rooms with more than two participants.
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
- Black screen issue when embedding mpv into Qt widget by disabling hardware decoding fallback.
- Asynchronous echo loop when applying remote playback states.
- Windows non-client title bar rendering glitch on initial launch.

## [1.1.0] - 2026-08-01

### Added
- Seekable progress slider in the playback controls bar.
- Network latency compensation through periodic ping/pong requests.
- Minimum correction interval and big jump threshold constants to prevent playback stuttering.
- Time display labels showing current position and total duration.

### Changed
- Disabled hardware decoding in mpv integration to resolve driver rendering conflicts.

## [1.0.0] - 2026-07-29

### Added
- Initial release of synchronized video player for local files.
- Embedded libmpv window integrated via Qt window handle.
- Client-server synchronization protocol over TCP sockets (`server.py`).
- Integrated chat panel and connected user list.
- Fullscreen playback mode and keyboard shortcuts for seeking and pausing.
