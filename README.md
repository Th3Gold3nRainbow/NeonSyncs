# SyncMPV

Watch videos in perfect sync with friends anywhere — built-in mpv player,
real-time playback sync, chat, and fullscreen. No fuss, no external
player window.

A PyQt5 client + Python asyncio server for watching videos together,
staying perfectly in sync (play, pause, seek) no matter where everyone
is, with built-in chat.

## Features

- mpv video player embedded directly in the interface (no separate
  window to juggle)
- Automatic sync of play/pause/position across everyone in a room
- Built-in text chat
- Fullscreen (`F` / `F11` key, double-click, `Esc` to exit)
- Fast forward/rewind (⏪10s/30s, 30s/10s⏩ buttons, or arrow keys
  ←/→ ±10s, ↑/↓ ±60s)
- Optional server password (useful for a server exposed on the
  internet via No-IP/DynDNS)
- Dark UI with a neon accent
- Windows packaging included: build a `.exe` (PyInstaller) and a full
  installer (Inno Setup) with icon and English/French language choice

## Architecture

- `server.py` — central server (asyncio). Manages "rooms" and
  broadcasts playback state to every client connected to the same
  room.
- `client.py` — PyQt5 client. The video player is an `mpv.MPV`
  instance embedded directly into a `QFrame` (via its `winId()`),
  alongside a side panel for connecting, the user list, and chat.

## Installation (Linux / macOS)

### 1. System dependency: libmpv

```bash
# Debian / Ubuntu
sudo apt install libmpv2   # or libmpv-dev / libmpv1 depending on your distro

# Arch
sudo pacman -S mpv

# macOS (Homebrew)
brew install mpv
```

### 2. Python dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Installation (Windows)

See [README_WINDOWS.md](README_WINDOWS.md) to build a `.exe` and a full
Windows installer (icon, language choice, shortcuts).

## Usage

### Start the server

```bash
python3 server.py --host 0.0.0.0 --port 8999
```

If the server is exposed to the internet (e.g. via a dynamic DNS
service like No-IP), add a password so random people can't join your
room:

```bash
python3 server.py --host 0.0.0.0 --port 8999 --password yourpassword
```

### Start a client

```bash
python3 client.py
```

In the window:
1. Fill in the server host/port, a room name (same for everyone), a
   username, and the password if the server requires one, then click
   **Connect**.
2. Click **Open a file…** to pick a local video (each participant
   needs the same file on their own disk — like Syncplay, only
   playback state is synced, not the video stream itself).
3. Play, pause, and seeking are automatically mirrored to every other
   participant in the room.

## How the sync works

- Each client sends its state (pause/position/file) to the server
  whenever a local event happens (pause, seek), or every 3 seconds
  otherwise.
- The server keeps the room's last known state, hands it to any new
  client that joins, then rebroadcasts every update to the others.
- A client receiving a remote state only re-seeks if the gap is more
  than 1 second, to avoid micro-stutters.

## Known limitations / possible improvements

- No fine-grained network latency compensation yet (a basic ping/pong
  already exists in the protocol, but isn't used yet to correct exact
  position).
- No shared playlist, one file at a time only.
- No end-to-end encryption: use on a trusted network, or put it behind
  a TLS reverse proxy for internet-facing use.
- Not compatible with the official public Syncplay server (different
  protocol) — you need to host your own instance of `server.py`.

## License

[MIT](LICENSE)
