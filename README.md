# NeonSyncs

Watch videos in perfect sync with friends anywhere — built-in mpv player, real-time peer-to-peer playback sync, text chat, and fullscreen. No port forwarding, no server hosting, and no external player windows.

Official website: **[https://neonsyncs.com](https://neonsyncs.com)**

NeonSyncs supports modern **serverless Peer-to-Peer (WebRTC)** mode by default, while retaining the classic Python asyncio server mode for dedicated or local network setups.

---

## Download

Windows users: grab the latest installer from the **[Releases page](https://github.com/Th3Gold3nRainbow/SyncMPV/releases)** or via **[neonsyncs.com](https://neonsyncs.com)** — no Python setup needed.

---

## Key Features

- **Peer-to-Peer (P2P) by default**: Create a room, share the generated Room ID (`neonsyncs-xxxxxx`), and connect directly without port forwarding, dynamic DNS, or self-hosting a server.
- **Microsecond Clock Synchronization**: NTP-style clock sync at handshake (5 pings, lowest RTT measurement, re-synced every 30s) to align system clocks across different computers.
- **Scheduled Actions**: Play, pause, and seek actions are scheduled with a 500 ms execution window (`executeAt = hostNow + 500ms`) so all clients trigger seek and playback at the exact same physical instant.
- **Smart Drift Correction**: Dynamic playback speed adjustment (between 0.97× and 1.03×) for sub-second drift (< 1s) to eliminate stutter and audio cuts. Automatic seek catch-up for larger desyncs (≥ 1s).
- **Different File Protection**: Alerts participants in the chat if a guest opens a different video file or version (different filename or duration difference > 2s) instead of corrupting playback positions.
- **Classic Server Mode**: Switch anytime to centralized `server.py` mode for LAN parties or dedicated VPS hosting.
- **Embedded mpv Player**: Direct libmpv integration (no separate external window to manage).
- **Rich Controls**: Progress bar seeking, fast forward/rewind buttons (⏪10s/30s, 10s/30s⏩), keyboard arrow shortcuts (←/→ ±10s, ↑/↓ ±60s), Spacebar toggle, and Fullscreen (`F` / `F11` / double-click).
- **Integrated Chat & Dark Neon Theme**: Built-in side-panel chat, user list, Orbitron/Rajdhani cyberpunk styling, and French / English localization.

---

## Quick Start (P2P Mode — Recommended)

No port forwarding or server hosting required!

1. **Launch NeonSyncs**.
2. **Host a room**:
   - Keep the mode on **P2P (recommended)**.
   - Enter your username and optional password.
   - Click **Create Room**.
   - Click **Copy** to copy your unique Room ID (e.g. `neonsyncs-a3b7k9`).
3. **Join a room**:
   - Guests enter their username, paste the Room ID into the **Room ID** field, and click **Join**.
4. **Open a video**:
   - Each participant clicks **Open a file…** to select their local video file (NeonSyncs synchronizes playback control, not the video file stream itself).
   - Play, pause, and seeks are synchronized automatically in real time!

---

## Server Mode (Optional)

If you prefer self-hosting a dedicated central server (e.g., on a local LAN or private VPS):

### 1. Run the server

```bash
python server.py --host 0.0.0.0 --port 8999
# Or with an optional password:
python server.py --host 0.0.0.0 --port 8999 --password yourpassword
```

### 2. Connect clients

In NeonSyncs, switch the dropdown to **Server**, enter the server IP/Port and room name, then click **Connect**.

---

## How Synchronization Works

1. **Handshake & Clock Sync**:
   Upon joining, the guest exchanges 5 sequential pings with the host to determine the exact round-trip time (RTT) and time offset:
   $$\text{offset} = \text{hostTime} - \left(t_0 + \frac{\text{RTT}}{2}\right)$$
   The offset with the lowest RTT is retained, and refreshed every 30 seconds.

2. **Scheduled Actions**:
   When any participant interacts with the player (Play/Pause button, Spacebar, progress bar slider, ±10/30s buttons, or keyboard arrows), a request is routed to the host, which timestamps the action at $t = \text{hostNow} + 500\text{ ms}$. Each peer converts this timestamp using their clock offset and schedules execution via high-precision timers.

3. **Continuous Drift Adjustment**:
   The host broadcasts its state periodically every 3 seconds. Guests compute the theoretical playback position:
   $$\text{theo\_pos} = \text{targetTime} + (\text{now}_{\text{host}} - \text{executeAt})$$
   - **Gap < 0.05 s**: Normal 1.0× speed.
   - **0.05 s ≤ Gap < 1.0 s**: Smooth speed adjustment ($0.97\times$ to $1.03\times$) without seeking or audio glitches.
   - **Gap ≥ 1.0 s**: Instant seek to the theoretical position with anti-echo and anti-bounce protections.

---

## Known Limitations & Technical Details

- **PeerJS Cloud Signaling**: The P2P mode utilizes the public PeerJS Cloud signaling server exclusively for the initial WebRTC connection handshake (exchanging SDP offer/answers). Once connected, video control data channels flow directly peer-to-peer; no media or chat is routed through third-party servers.
- **Symmetric NATs & TURN**: P2P connections use standard STUN servers (Google STUN). In rare restricted network environments (such as certain strict corporate/university firewalls or symmetric NATs), direct P2P connections may fail without a relay (TURN) server. In this case, an explicit error is displayed and the classic Server mode can be used as a fallback.
- **Installer Size**: The Windows installer is larger (~150 MB+) because it embeds both `libmpv` (video decoding engine) and `PyQtWebEngine` (Chromium runtime required for the headless WebRTC PeerJS stack).

---

## Building from Source

### Requirements
- Python 3.8+
- `libmpv` (e.g. `mpv-2.dll` on Windows, `libmpv2` on Debian/Ubuntu, `mpv` via Homebrew on macOS)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python client.py
```

### Windows Executable & Installer
Run `build_exe.bat` to compile `dist\NeonSyncs.exe` using PyInstaller, then compile `installer.iss` with Inno Setup to generate `Output\NeonSyncs-Setup.exe`.

---

## License

[MIT](LICENSE)
