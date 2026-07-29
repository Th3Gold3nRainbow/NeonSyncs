#!/usr/bin/env python3
"""
SyncMPV Client
==============
Client de lecture synchronisée avec lecteur MPV intégré dans la fenêtre
(via python-mpv / libmpv, pas de fenêtre externe comme le fait
Syncplay avec MPC/VLC).

Dépendances système :
  - libmpv (ex: `sudo apt install libmpv2` ou `libmpv-dev` selon distro)

Dépendances Python :
  pip install python-mpv PyQt5

Lancement :
  python3 client.py

Plein écran :
  - Touche F ou F11, ou double-clic sur la vidéo, pour basculer.
  - Échap pour quitter le plein écran.
  - En plein écran : aucune barre, aucun panneau, aucune bordure —
    uniquement l'image vidéo.
  - IMPORTANT : après toute modification de ce fichier, il faut
    recompiler l'exécutable (build_exe.bat) puis réinstaller, sinon
    l'ancienne version reste utilisée.

Avancer / reculer :
  - Boutons ⏪10s / ⏪30s / 30s⏩ / 10s⏩ dans la barre de contrôle.
  - Flèches gauche/droite (±10s) et haut/bas (±60s) du clavier,
    liées explicitement (fiables même quand la vidéo a le focus),
    synchronisées avec les autres participants.

Mot de passe serveur :
  - Champ optionnel dans le panneau de connexion.
  - Utile si le serveur est exposé sur internet via un service
    comme No-IP/DynDNS : lancez le serveur avec
    `python3 server.py --password votremotdepasse`
    et remplissez le même mot de passe côté client.
"""
import sys
import json
import socket
import threading
import time

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QFileDialog, QListWidget, QSplitter, QFrame,
    QShortcut
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject

import mpv


# ---------------------------------------------------------------------------
# Thème visuel — sombre avec accent néon unique (pas de surcharge de couleurs)
# ---------------------------------------------------------------------------
STYLE_SHEET = """
QWidget {
    background-color: #0b0d12;
    color: #e4e6eb;
    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
    font-size: 10pt;
}
QLabel {
    color: #7b8394;
}
QLabel[role="section"] {
    color: #39f2c8;
    font-weight: 700;
    font-size: 9pt;
    padding-top: 6px;
}
QLabel[role="status"] {
    color: #e4e6eb;
    font-weight: 600;
    padding: 4px 0;
}
QLineEdit {
    background-color: #161a22;
    border: 1px solid #242a35;
    border-radius: 6px;
    padding: 7px 9px;
    color: #e4e6eb;
    selection-background-color: #39f2c8;
    selection-color: #0b0d12;
}
QLineEdit:focus {
    border: 1px solid #39f2c8;
}
QPushButton {
    background-color: #161a22;
    border: 1px solid #242a35;
    border-radius: 8px;
    padding: 8px 14px;
    color: #e4e6eb;
}
QPushButton:hover {
    border: 1px solid #39f2c8;
    color: #39f2c8;
}
QPushButton:pressed {
    background-color: #0e1116;
}
QPushButton[role="primary"] {
    background-color: #10312c;
    border: 1px solid #39f2c8;
    color: #39f2c8;
    font-weight: 600;
}
QPushButton[role="primary"]:hover {
    background-color: #14403a;
}
QListWidget {
    background-color: #10131a;
    border: 1px solid #1c2028;
    border-radius: 8px;
    padding: 4px;
    outline: none;
}
QListWidget::item {
    padding: 3px 4px;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: #14403a;
    color: #39f2c8;
}
QScrollBar:vertical {
    background: #10131a;
    width: 10px;
    margin: 0;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #242a35;
    border-radius: 5px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background: #39f2c8;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QFrame#videoFrame {
    background-color: #000000;
    border: none;
}
QWidget#panel {
    background-color: #0e1016;
}
QWidget#controlsBar {
    background-color: #0e1016;
}
"""


def _apply_dark_titlebar(widget):
    """Sur Windows 10/11, force la barre de titre native en mode sombre
    pour rester cohérent avec le thème de l'application. No-op ailleurs
    ou si l'API n'est pas disponible (echoue silencieusement)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        hwnd = int(widget.winId())
        value = ctypes.c_int(1)
        for attr in (20, 19):  # DWMWA_USE_IMMERSIVE_DARK_MODE (20 = Win10 20H1+, 19 = versions plus anciennes)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, attr, ctypes.byref(value), ctypes.sizeof(value)
            )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Réglages de synchronisation
# ---------------------------------------------------------------------------
SEEK_THRESHOLD = 1.0       # secondes d'écart tolérées avant de resynchroniser
STATE_SEND_INTERVAL = 3.0  # envoi périodique de l'état même sans événement
IGNORE_ECHO_WINDOW = 0.8   # évite de renvoyer un état qu'on vient de recevoir


class NetworkClient(QObject):
    """Gère la connexion TCP au serveur dans un thread séparé,
    et relaie les messages reçus vers le thread Qt via un signal."""
    message_received = pyqtSignal(dict)
    connected_signal = pyqtSignal(bool, str)
    disconnected_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.sock = None
        self.buf = b""
        self.running = False
        self.lock = threading.Lock()

    def connect_to(self, host, port, room, username, password=""):
        try:
            self.sock = socket.create_connection((host, port), timeout=5)
            # IMPORTANT : create_connection() applique le timeout de connexion
            # (5s) au socket de façon PERMANENTE tant qu'on ne le desactive pas.
            # Sans cette ligne, recv() finit par lever une exception "timeout"
            # des qu'aucune donnee n'arrive pendant 5s (ex: quand on est seul
            # dans le salon) — ce qui etait pris a tort pour une deconnexion.
            self.sock.settimeout(None)
        except OSError as e:
            self.connected_signal.emit(False, str(e))
            return
        self.running = True
        self.connected_signal.emit(True, "connecté")
        self.send({"type": "hello", "room": room, "username": username, "password": password})
        threading.Thread(target=self._recv_loop, daemon=True).start()

    def send(self, obj: dict):
        if not self.sock:
            return
        try:
            data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
            with self.lock:
                self.sock.sendall(data)
        except OSError:
            pass

    def _recv_loop(self):
        while self.running:
            try:
                chunk = self.sock.recv(4096)
            except OSError:
                break
            if not chunk:
                break
            self.buf += chunk
            while b"\n" in self.buf:
                line, self.buf = self.buf.split(b"\n", 1)
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line.decode("utf-8"))
                except json.JSONDecodeError:
                    continue
                self.message_received.emit(msg)
        was_running = self.running
        self.running = False
        if was_running:
            self.disconnected_signal.emit()

    def close(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass


class SyncMPVWindow(QWidget):
    fs_toggle_requested = pyqtSignal()
    fs_exit_requested = pyqtSignal()
    seek_requested = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SyncMPV — lecture synchronisée")
        self.resize(1100, 650)

        self.net = NetworkClient()
        self.net.message_received.connect(self.on_message)
        self.net.connected_signal.connect(self.on_connected)
        self.net.disconnected_signal.connect(self.on_disconnected)

        self.last_remote_state_at = 0.0
        self.applying_remote = False  # évite les boucles d'écho
        self.current_file = None
        self.current_duration = 0.0
        self.is_fullscreen = False

        self._build_ui()
        self._init_mpv()
        self.setStyleSheet(STYLE_SHEET)

        # Le signal permet de basculer le plein écran en toute sécurité
        # depuis le thread interne de mpv (les callbacks mpv ne tournent
        # pas dans le thread Qt principal).
        self.fs_toggle_requested.connect(self.toggle_fullscreen)
        self.fs_exit_requested.connect(self.exit_fullscreen)
        self.seek_requested.connect(self.seek_relative)

        # Raccourcis clavier côté Qt (utile si le focus est hors de la
        # zone vidéo, par ex. sur le panneau latéral).
        QShortcut(QKeySequence(Qt.Key_F11), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("F"), self, self.toggle_fullscreen)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.exit_fullscreen)
        QShortcut(QKeySequence(Qt.Key_Right), self, lambda: self.seek_relative(10))
        QShortcut(QKeySequence(Qt.Key_Left), self, lambda: self.seek_relative(-10))
        QShortcut(QKeySequence(Qt.Key_Up), self, lambda: self.seek_relative(60))
        QShortcut(QKeySequence(Qt.Key_Down), self, lambda: self.seek_relative(-60))

        self.send_timer = QTimer(self)
        self.send_timer.timeout.connect(self.periodic_state_push)
        self.send_timer.start(int(STATE_SEND_INTERVAL * 1000))

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Colonne vidéo
        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(0)
        self.video_frame = QFrame(self)
        self.video_frame.setObjectName("videoFrame")
        self.video_frame.setFrameShape(QFrame.NoFrame)
        left.addWidget(self.video_frame, stretch=1)

        # Barre de contrôle (masquée en plein écran)
        self.controls_widget = QWidget(self)
        self.controls_widget.setObjectName("controlsBar")
        controls = QHBoxLayout(self.controls_widget)
        self.btn_open = QPushButton("Ouvrir un fichier…")
        self.btn_open.clicked.connect(self.open_file)
        self.btn_back30 = QPushButton("⏪ 30s")
        self.btn_back30.clicked.connect(lambda: self.seek_relative(-30))
        self.btn_back10 = QPushButton("⏪ 10s")
        self.btn_back10.clicked.connect(lambda: self.seek_relative(-10))
        self.btn_play = QPushButton("Lecture / Pause")
        self.btn_play.clicked.connect(self.toggle_pause)
        self.btn_fwd10 = QPushButton("10s ⏩")
        self.btn_fwd10.clicked.connect(lambda: self.seek_relative(10))
        self.btn_fwd30 = QPushButton("30s ⏩")
        self.btn_fwd30.clicked.connect(lambda: self.seek_relative(30))
        self.btn_fullscreen = QPushButton("Plein écran (F11)")
        self.btn_fullscreen.clicked.connect(self.toggle_fullscreen)
        controls.addWidget(self.btn_open)
        controls.addWidget(self.btn_back30)
        controls.addWidget(self.btn_back10)
        controls.addWidget(self.btn_play)
        controls.addWidget(self.btn_fwd10)
        controls.addWidget(self.btn_fwd30)
        controls.addWidget(self.btn_fullscreen)
        left.addWidget(self.controls_widget)

        left_widget = QWidget(self)
        left_widget.setLayout(left)
        root.addWidget(left_widget, stretch=3)

        # Colonne réseau / chat (masquée en plein écran)
        self.right_panel = QWidget(self)
        self.right_panel.setObjectName("panel")
        self.right_panel.setFixedWidth(280)
        right = QVBoxLayout(self.right_panel)
        right.setContentsMargins(14, 14, 14, 14)
        right.setSpacing(6)

        lbl_server = QLabel("SERVEUR")
        lbl_server.setProperty("role", "section")
        right.addWidget(lbl_server)

        self.input_host = QLineEdit("127.0.0.1")
        self.input_port = QLineEdit("8999")
        self.input_room = QLineEdit("salon1")
        self.input_user = QLineEdit("invite")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText("(optionnel)")
        for w, label in [
            (self.input_host, "Hôte"),
            (self.input_port, "Port"),
            (self.input_room, "Salon"),
            (self.input_user, "Pseudo"),
            (self.input_password, "Mot de passe"),
        ]:
            right.addWidget(QLabel(label))
            right.addWidget(w)

        self.btn_connect = QPushButton("Se connecter")
        self.btn_connect.setProperty("role", "primary")
        self.btn_connect.clicked.connect(self.do_connect)
        right.addWidget(self.btn_connect)

        self.status_label = QLabel("Déconnecté")
        self.status_label.setProperty("role", "status")
        right.addWidget(self.status_label)

        lbl_users = QLabel("UTILISATEURS")
        lbl_users.setProperty("role", "section")
        right.addWidget(lbl_users)
        self.user_list = QListWidget()
        self.user_list.setMaximumHeight(110)
        right.addWidget(self.user_list)

        lbl_chat = QLabel("CHAT")
        lbl_chat.setProperty("role", "section")
        right.addWidget(lbl_chat)
        self.chat_list = QListWidget()
        right.addWidget(self.chat_list, stretch=1)
        chat_row = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Écrire un message…")
        self.chat_input.returnPressed.connect(self.send_chat)
        btn_send = QPushButton("Envoyer")
        btn_send.clicked.connect(self.send_chat)
        chat_row.addWidget(self.chat_input)
        chat_row.addWidget(btn_send)
        right.addLayout(chat_row)

        root.addWidget(self.right_panel, stretch=0)

    def _init_mpv(self):
        # Intègre mpv directement dans le QFrame (pas de fenêtre externe)
        self.player = mpv.MPV(
            wid=str(int(self.video_frame.winId())),
            input_default_bindings=True,
            input_vo_keyboard=True,
            osc=True,
        )

        @self.player.property_observer("pause")
        def _on_pause_change(_name, value):
            if self.applying_remote or value is None:
                return
            self.push_state()

        @self.player.event_callback("seek")
        def _on_seek(_event):
            if self.applying_remote:
                return
            self.push_state()

        # mpv capte le clavier/souris de sa propre fenêtre embarquée
        # (input_vo_keyboard=True) : on enregistre donc les raccourcis
        # directement côté mpv, et on relaie vers Qt via un signal
        # (les callbacks mpv tournent dans un thread séparé).
        # mpv capte le clavier/souris de sa propre fenêtre embarquée
        # (input_vo_keyboard=True). input_default_bindings=True lie déjà
        # 'f'/'F11'/double-clic à SON PROPRE mode plein écran interne
        # (inutile ici, puisqu'on est intégré via wid) : on désactive
        # d'abord ces raccourcis par défaut, puis on enregistre les nôtres,
        # pour éviter tout conflit.
        for key in ("f", "F11", "MBTN_LEFT_DBL"):
            try:
                self.player.command("keybind", key, "ignore")
            except Exception:
                pass

        @self.player.on_key_press("f")
        def _mpv_toggle_fs():
            self.fs_toggle_requested.emit()

        @self.player.on_key_press("F11")
        def _mpv_toggle_fs11():
            self.fs_toggle_requested.emit()

        @self.player.on_key_press("ESC")
        def _mpv_exit_fs():
            self.fs_exit_requested.emit()

        @self.player.on_key_press("MBTN_LEFT_DBL")
        def _mpv_dbl_click():
            self.fs_toggle_requested.emit()

        # Avancer / reculer au clavier : on lie ces touches directement
        # côté mpv (comme pour le plein écran, mpv capte le clavier de
        # sa fenêtre embarquée) et on relaie vers notre propre fonction
        # de seek pour garantir la synchronisation immédiate avec les
        # autres participants.
        @self.player.on_key_press("RIGHT")
        def _mpv_seek_fwd():
            self.seek_requested.emit(10)

        @self.player.on_key_press("LEFT")
        def _mpv_seek_back():
            self.seek_requested.emit(-10)

        @self.player.on_key_press("UP")
        def _mpv_seek_fwd_big():
            self.seek_requested.emit(60)

        @self.player.on_key_press("DOWN")
        def _mpv_seek_back_big():
            self.seek_requested.emit(-60)

    # ------------------------------------------------------------------
    # Actions locales
    # ------------------------------------------------------------------
    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir une vidéo")
        if not path:
            return
        self.current_file = path
        self.player.play(path)
        self.push_state(force=True)

    def toggle_pause(self):
        self.player.pause = not self.player.pause

    def seek_relative(self, seconds: float):
        """Avance ou recule dans la vidéo (secondes positives = avance)."""
        try:
            self.player.seek(seconds, reference="relative")
        except Exception:
            return
        # Synchronise immédiatement les autres participants, sans
        # attendre l'événement 'seek' ou le prochain envoi périodique.
        self.push_state(force=True)

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()

    def enter_fullscreen(self):
        if self.is_fullscreen:
            return
        self.is_fullscreen = True
        self.right_panel.hide()
        self.controls_widget.hide()
        self.showFullScreen()

    def exit_fullscreen(self):
        if not self.is_fullscreen:
            return
        self.is_fullscreen = False
        self.right_panel.show()
        self.controls_widget.show()
        self.showNormal()

    def do_connect(self):
        host = self.input_host.text().strip()
        port = int(self.input_port.text().strip())
        room = self.input_room.text().strip()
        user = self.input_user.text().strip()
        password = self.input_password.text()
        self.net.connect_to(host, port, room, user, password)

    def on_connected(self, ok, message):
        self.status_label.setText("Connecté" if ok else f"Erreur: {message}")

    def on_disconnected(self):
        self.status_label.setText("Déconnecté (connexion perdue)")
        self.user_list.clear()

    def send_chat(self):
        text = self.chat_input.text().strip()
        if not text:
            return
        if not self.net.running:
            self.chat_list.addItem("⚠ Non connecté — connectez-vous d'abord au serveur.")
            self.chat_list.scrollToBottom()
            return
        self.net.send({"type": "chat", "message": text})
        self.chat_input.clear()

    # ------------------------------------------------------------------
    # Synchronisation
    # ------------------------------------------------------------------
    def push_state(self, force=False):
        """Envoie l'état local au serveur (sauf juste après avoir appliqué
        un état distant, pour éviter les allers-retours inutiles)."""
        if time.time() - self.last_remote_state_at < IGNORE_ECHO_WINDOW and not force:
            return
        try:
            paused = bool(self.player.pause)
            position = float(self.player.time_pos or 0.0)
            duration = float(self.player.duration or 0.0)
        except Exception:
            return
        self.net.send({
            "type": "state",
            "paused": paused,
            "position": position,
            "file": self.current_file,
            "duration": duration,
        })

    def periodic_state_push(self):
        if self.net.running:
            self.push_state()

    def on_message(self, msg: dict):
        mtype = msg.get("type")
        if mtype == "state":
            self.apply_remote_state(msg)
        elif mtype == "userlist":
            self.user_list.clear()
            self.user_list.addItems(msg.get("users", []))
        elif mtype == "chat":
            self.chat_list.addItem(f"{msg.get('from')}: {msg.get('message')}")
            self.chat_list.scrollToBottom()
        elif mtype == "error":
            self.status_label.setText(f"Erreur: {msg.get('message', '')}")
            self.net.close()

    def apply_remote_state(self, msg: dict):
        remote_paused = msg.get("paused")
        remote_position = msg.get("position")
        remote_file = msg.get("file")

        self.applying_remote = True
        try:
            if remote_file and remote_file != self.current_file:
                self.current_file = remote_file
                self.player.play(remote_file)

            if remote_position is not None:
                try:
                    local_pos = float(self.player.time_pos or 0.0)
                except Exception:
                    local_pos = 0.0
                if abs(local_pos - remote_position) > SEEK_THRESHOLD:
                    self.player.seek(remote_position, reference="absolute")

            if remote_paused is not None:
                self.player.pause = bool(remote_paused)
        except Exception:
            pass
        finally:
            self.last_remote_state_at = time.time()
            self.applying_remote = False

    def closeEvent(self, event):
        self.net.close()
        try:
            self.player.terminate()
        except Exception:
            pass
        event.accept()


def main():
    app = QApplication(sys.argv)
    win = SyncMPVWindow()
    win.show()
    _apply_dark_titlebar(win)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
