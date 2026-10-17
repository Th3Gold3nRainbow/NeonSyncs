# NeonSyncs — Internationalization Audit (i18n)

This document contains the complete audit of all user-visible strings across the NeonSyncs codebase (`client.py`, `p2p/p2p.html`, `server.py`, and build scripts), grouped by category.

---

## 1. Summary by Category

| # | Category | Number of Strings / Keys | Description |
|---|---|:---:|---|
| 1 | **Player Controls & Window** | 9 | Window title, playback buttons, fullscreen, time indicators |
| 2 | **Sidebar & Connection Form** | 12 | Connection sections, mode selector, host/port/room inputs, connect/disconnect |
| 3 | **P2P Room Management** | 8 | Create room, join room, room ID placeholder, copy ID button, retry |
| 4 | **Default Values** | 4 | Localized & randomized username, room name, P2P host/guest fallbacks |
| 5 | **Status Bar** | 7 | Disconnected, connected, reconnecting, creating, joining, lost, error format |
| 6 | **Network & P2P Error Codes** | 14 | Wrong password, NAT/TURN, signaling unreachable, peer unavailable, timeouts |
| 7 | **Chat & User Notifications** | 8 | Chat panel, placeholder, send button, warnings (no file, different file) |
| 8 | **Dialogs & File Pickers** | 2 | Video file picker window title and file extension filters |
| 9 | **mpv Embedded Player (OSD/OSC)** | N/A | Analysis of embedded libmpv on-screen controller and status displays |
| **Total** | **All Categories** | **64 keys** | Exhaustive coverage across the entire application |

---

## 2. Exhaustive Key Catalog

### Category 1: Player Controls & Window (9 keys)
| Key | English (en) | French (fr) | Context & Code Location |
|---|---|---|---|
| `window_title` | NeonSyncs — synchronized playback | NeonSyncs — lecture synchronisée | Main window title (`client.py:setWindowTitle`) |
| `open_file` | Open a file… | Ouvrir un fichier… | Main playback toolbar button (`client.py:btn_open`) |
| `back_30` | ⏪ 30s | ⏪ 30s | Rewind 30s button (`client.py:btn_back30`) |
| `back_10` | ⏪ 10s | ⏪ 10s | Rewind 10s button (`client.py:btn_back10`) |
| `play_pause` | Play / Pause | Lecture / Pause | Play/pause toggle button (`client.py:btn_play`) |
| `fwd_10` | 10s ⏩ | 10s ⏩ | Fast-forward 10s button (`client.py:btn_fwd10`) |
| `fwd_30` | 30s ⏩ | 30s ⏩ | Fast-forward 30s button (`client.py:btn_fwd30`) |
| `fullscreen` | Fullscreen (F11) | Plein écran (F11) | Fullscreen button (`client.py:btn_fullscreen`) |
| `time_default` | 0:00 | 0:00 | Default time display before media is loaded (`client.py`) |

### Category 2: Sidebar & Connection Form (12 keys)
| Key | English (en) | French (fr) | Context & Code Location |
|---|---|---|---|
| `section_connection` | CONNECTION | CONNEXION | Sidebar header for connection section (`client.py`) |
| `label_mode` | Mode | Mode | Label for connection mode selector (`client.py`) |
| `mode_p2p` | P2P (recommended) | P2P (recommandé) | ComboBox item for P2P mode (`client.py:combo_mode`) |
| `mode_server` | Server | Serveur | ComboBox item for Server mode (`client.py:combo_mode`) |
| `label_user` | Username | Pseudo | Label for username input field (`client.py`) |
| `label_password` | Password | Mot de passe | Label for password input field (`client.py`) |
| `password_placeholder` | (optional) | (optionnel) | Placeholder for password field (`client.py:input_password`) |
| `section_server` | SERVER | SERVEUR | Sidebar header for server mode fields (`client.py`) |
| `label_host` | Host | Hôte | Label for server IP/host input (`client.py`) |
| `label_port` | Port | Port | Label for server port input (`client.py`) |
| `label_room` | Room | Salon | Label for server room input (`client.py`) |
| `connect` | Connect | Se connecter | Server connect button (`client.py:btn_connect`) |
| `disconnect` | Disconnect | Se déconnecter | Server disconnect button (`client.py:btn_connect`) |

### Category 3: P2P Room Management (8 keys)
| Key | English (en) | French (fr) | Context & Code Location |
|---|---|---|---|
| `create_room` | Create Room | Créer un salon | Button to create P2P room (`client.py:btn_create_room`) |
| `join_room` | Join | Rejoindre | Button to join P2P room (`client.py:btn_join_room`) |
| `room_id` | Room ID | ID du salon | Label for room ID field (`client.py`) |
| `room_id_placeholder` | e.g. neonsyncs-xxxxxx | ex: neonsyncs-xxxxxx | Placeholder for room ID input (`client.py:input_room_id`) |
| `copy_id` | Copy | Copier | Copy room ID button (`client.py:btn_copy_id`) |
| `id_copied` | Copied! | Copié ! | Confirmation when room ID copied (`client.py:btn_copy_id`) |
| `leave_room` | Leave Room | Quitter le salon | Button to leave P2P room (`client.py:btn_leave_p2p`) |
| `p2p_retry` | Retry | Réessayer | Retry button on connection failure (`client.py:btn_retry_p2p`) |

### Category 4: Default Values (Localized & Randomized) (4 keys)
| Key | English (en) | French (fr) | Context & Code Location |
|---|---|---|---|
| `default_username` | Guest-{id} | Invité-{id} | Default username initialized with 4 random digits (`client.py`) |
| `default_room_name` | room-{id} | salon-{id} | Default server room name initialized with 4 digits (`client.py`) |
| `default_p2p_host` | Host | Hôte | Fallback username in P2P bridge if empty (`p2p/p2p.html`) |
| `default_p2p_guest` | Guest_{id} | Invité_{id} | Fallback guest name in P2P bridge if empty (`p2p/p2p.html`) |

### Category 5: Connection Status Bar (7 keys)
| Key | English (en) | French (fr) | Context & Code Location |
|---|---|---|---|
| `status_disconnected` | Disconnected | Déconnecté | Status label when idle (`client.py:status_label`) |
| `status_connected` | Connected | Connecté | Status label when connected (`client.py:status_label`) |
| `status_reconnecting` | Reconnecting… | Reconnexion… | Status label during reconnect attempts (`client.py:status_label`) |
| `status_creating` | Creating room… | Création du salon… | Status label while negotiating peer ID (`client.py:status_label`) |
| `status_joining` | Joining room… | Connexion au salon… | Status label while connecting to host (`client.py:status_label`) |
| `status_disconnected_lost` | Disconnected (connection lost) | Déconnecté (connexion perdue) | Status label upon sudden disconnect (`client.py:status_label`) |
| `status_error` | Error: {message} | Erreur : {message} | Formatted error status (`client.py:status_label`) |

### Category 6: Network & Error Codes (14 keys)
*Note: All error propagation between Python, PeerJS, and server.py now uses discrete error codes, translated locally by `tr()`.*

| Error Code / Key | English (en) | French (fr) | Context & Trigger Condition |
|---|---|---|---|
| `error_room_id_required` | Room ID is required | ID du salon requis | Attempting to join P2P with empty room ID |
| `error_wrong_password` | Incorrect password | Mot de passe incorrect | Wrong password provided to host or server |
| `host_left` | Host left the room | L'hôte a quitté le salon | Host closed the room or lost connection |
| `p2p_error_signaling` | Signaling server unreachable | Serveur de signalement injoignable | PeerJS Cloud signaling server connection failure |
| `p2p_error_no_turn` | Connection failed (probable NAT without TURN) | Connexion impossible (probable NAT sans TURN) | Direct WebRTC ICE candidate pairing failed |
| `p2p_error_peer_unavailable` | Room not found or host disconnected | Salon introuvable ou hôte déconnecté | Target peer ID does not exist on signaling server |
| `p2p_error_connection_failed` | Connection failed (timeout or strict NAT) | Échec de connexion (délai dépassé ou NAT strict) | DataChannel negotiation timeout |
| `p2p_error_room_id_generation` | Failed to generate a unique room ID | Impossible de générer un ID de salon unique | 5 consecutive collision attempts on room ID creation |
| `p2p_error_invalid_id` | Invalid room ID format | ID de salon invalide | Malformed room ID passed to PeerJS |
| `p2p_error_id_taken` | Room ID is already in use | ID de salon déjà utilisé | Room ID collision error from signaling server |
| `p2p_error_browser_incompatible` | Browser WebRTC engine incompatible | Moteur WebRTC incompatible | QtWebEngine WebRTC initialization failure |
| `p2p_error_disconnected` | Disconnected from signaling network | Déconnecté du réseau de signalement | PeerJS signaling socket terminated |
| `net_error_connection_refused` | Connection refused by server | Connexion refusée par le serveur | TCP connection refused on target IP/port |
| `net_error_connection_lost` | Connection lost with server | Connexion perdue avec le serveur | Unexpected TCP socket closure in server mode |

### Category 7: Chat & System Notifications (8 keys)
| Key | English (en) | French (fr) | Context & Code Location |
|---|---|---|---|
| `section_users` | USERS | UTILISATEURS | Sidebar header for participant list (`client.py`) |
| `section_chat` | CHAT | CHAT | Sidebar header for chat panel (`client.py`) |
| `chat_placeholder` | Type a message… | Écrire un message… | Chat input placeholder (`client.py:chat_input`) |
| `send` | Send | Envoyer | Chat send button (`client.py:btn_send`) |
| `chat_not_connected` | ⚠ Not connected — connect to a room or server first. | ⚠ Non connecté — connectez-vous d'abord à un salon ou un serveur. | Warning when attempting to send offline (`client.py`) |
| `warning_no_file` | No file open. Host is playing: {file} | Aucun fichier ouvert. L'hôte lit : {file} | Notification when guest has no media loaded (`client.py`) |
| `warning_different_file` | Different file from host ({details}) — sync suspended. | Fichier différent de l'hôte ({details}) — synchronisation suspendue. | Warning on filename/duration mismatch (`client.py`) |
| `system_chat_format` | ⚠ {message} | ⚠ {message} | Format for automated system warnings in chat |

### Category 8: Dialogs & File Pickers (2 keys)
| Key | English (en) | French (fr) | Context & Code Location |
|---|---|---|---|
| `dialog_open_video_title` | Select a video file | Choisir un fichier vidéo | QFileDialog window title (`client.py:open_file_dialog`) |
| `dialog_open_video_filter` | Video files (*.mp4 *.mkv *.avi *.mov *.webm *.flv *.ts *.m4v);;All files (*.*) | Fichiers vidéo (*.mp4 *.mkv *.avi *.mov *.webm *.flv *.ts *.m4v);;Tous les fichiers (*.*) | QFileDialog file type filter (`client.py`) |

---

## 3. Embedded mpv Player (OSD & OSC) Analysis

### Current Status
- In [`client.py`](file:///c:/Users/Twix/Desktop/Sync/client.py#L1296-L1302), mpv is instantiated with:
  ```python
  self.player = mpv.MPV(
      wid=str(int(self.video_frame.winId())),
      input_default_bindings=True,
      input_vo_keyboard=True,
      osc=True,
      hwdec="no",
  )
  ```
- **On-Screen Controller (OSC)**: When `osc=True`, moving the cursor over the embedded video displays mpv's built-in bottom control bar (seek bar, time counter, play/pause icon, volume slider).
- **On-Screen Display (OSD)**: Displays transient textual notifications when adjusting volume (`Volume: 100%`), seeking, or toggling mute.
- **Language**: Because `mpv-2.dll` on Windows is a precompiled native binary without embedded external gettext catalog files, these internal mpv texts default strictly to **English** (e.g. `Volume`, `Mute: yes`).
- **Recommendation**: As requested, mpv's OSC/OSD is **preserved intact without disabling it**. Because NeonSyncs provides its own rich, stylized Cyberpunk UI below the video (buttons, progress bar, time labels in the user's chosen language), the mpv OSC serves as a convenient secondary overlay.
