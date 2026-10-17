#!/usr/bin/env python3
"""
NeonSyncs Client
================
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
  - Barre de progression glissable (au-dessus des boutons) : cliquez
    ou faites-la glisser pour aller directement où vous voulez dans
    la vidéo. Synchronisée avec les autres participants dès que vous
    relâchez.

Mot de passe serveur :
  - Champ optionnel dans le panneau de connexion.
  - Utile si le serveur est exposé sur internet via un service
    comme No-IP/DynDNS : lancez le serveur avec
    `python3 server.py --password votremotdepasse`
    et remplissez le même mot de passe côté client.
"""
import sys
import os
import json
import socket
import threading
import time

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QFileDialog, QListWidget, QSplitter, QFrame,
    QShortcut, QSlider, QComboBox, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QKeySequence, QIcon, QColor, QFontDatabase, QFont, QPixmap, QImage, QPainter
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QUrl, pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtSvg import QSvgRenderer

if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("neonsyncs.watchparty.client")
    except Exception:
        pass
    _dll_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
    if os.path.exists(_dll_dir):
        os.environ["PATH"] = _dll_dir + os.pathsep + os.environ.get("PATH", "")
        if hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(_dll_dir)
            except Exception:
                pass

import mpv


# ---------------------------------------------------------------------------
# Identité de l'application & Internationalisation
# ---------------------------------------------------------------------------
APP_NAME = "NeonSyncs"
APP_URL = "https://neonsyncs.com"

STRINGS = {
    "fr": {
        "window_title": f"{APP_NAME} — lecture synchronisée",
        "open_file": "Ouvrir un fichier…",
        "back_30": "⏪ 30s",
        "back_10": "⏪ 10s",
        "play_pause": "Lecture / Pause",
        "fwd_10": "10s ⏩",
        "fwd_30": "30s ⏩",
        "fullscreen": "Plein écran (F11)",
        "section_server": "SERVEUR",
        "label_host": "Hôte",
        "label_port": "Port",
        "label_room": "Salon",
        "label_user": "Pseudo",
        "label_password": "Mot de passe",
        "password_placeholder": "(optionnel)",
        "connect": "Se connecter",
        "disconnect": "Se déconnecter",
        "status_disconnected": "Déconnecté",
        "status_connected": "Connecté",
        "status_error": "Erreur : {message}",
        "status_disconnected_lost": "Déconnecté (connexion perdue)",
        "section_users": "UTILISATEURS",
        "section_chat": "CHAT",
        "chat_placeholder": "Écrire un message…",
        "send": "Envoyer",
        "chat_not_connected": "⚠ Non connecté — connectez-vous d'abord à un salon ou un serveur.",
        "mode_p2p": "P2P (recommandé)",
        "mode_server": "Serveur",
        "create_room": "Créer un salon",
        "join_room": "Rejoindre",
        "room_id": "ID du salon",
        "room_id_placeholder": "ex: neonsyncs-xxxxxx",
        "copy_id": "Copier",
        "id_copied": "Copié !",
        "status_reconnecting": "Reconnexion…",
        "status_creating": "Création du salon…",
        "status_joining": "Connexion au salon…",
        "host_left": "L'hôte a quitté le salon",
        "p2p_error_signaling": "Serveur de signalement injoignable",
        "p2p_error_no_turn": "Connexion impossible (probable NAT sans TURN)",
        "p2p_error_peer_unavailable": "Salon introuvable ou hôte déconnecté",
        "error_wrong_password": "Mot de passe incorrect",
        "p2p_error_connection_failed": "Échec de connexion (délai dépassé ou NAT strict)",
        "p2p_retry": "Réessayer",
        "section_connection": "CONNEXION",
        "label_mode": "Mode",
        "leave_room": "Quitter le salon",
        "warning_no_file": "Aucun fichier ouvert. L'hôte lit : {file}",
        "warning_different_file": "Fichier différent de l'hôte ({details}) — synchronisation suspendue.",
    },
    "en": {
        "window_title": f"{APP_NAME} — synchronized playback",
        "open_file": "Open a file…",
        "back_30": "⏪ 30s",
        "back_10": "⏪ 10s",
        "play_pause": "Play / Pause",
        "fwd_10": "10s ⏩",
        "fwd_30": "30s ⏩",
        "fullscreen": "Fullscreen (F11)",
        "section_server": "SERVER",
        "label_host": "Host",
        "label_port": "Port",
        "label_room": "Room",
        "label_user": "Username",
        "label_password": "Password",
        "password_placeholder": "(optional)",
        "connect": "Connect",
        "disconnect": "Disconnect",
        "status_disconnected": "Disconnected",
        "status_connected": "Connected",
        "status_error": "Error: {message}",
        "status_disconnected_lost": "Disconnected (connection lost)",
        "section_users": "USERS",
        "section_chat": "CHAT",
        "chat_placeholder": "Type a message…",
        "send": "Send",
        "chat_not_connected": "⚠ Not connected — connect to a room or server first.",
        "mode_p2p": "P2P (recommended)",
        "mode_server": "Server",
        "create_room": "Create Room",
        "join_room": "Join",
        "room_id": "Room ID",
        "room_id_placeholder": "e.g. neonsyncs-xxxxxx",
        "copy_id": "Copy",
        "id_copied": "Copied!",
        "status_reconnecting": "Reconnecting…",
        "status_creating": "Creating room…",
        "status_joining": "Joining room…",
        "host_left": "Host left the room",
        "p2p_error_signaling": "Signaling server unreachable",
        "p2p_error_no_turn": "Connection failed (probable NAT without TURN)",
        "p2p_error_peer_unavailable": "Room not found or host disconnected",
        "error_wrong_password": "Incorrect password",
        "p2p_error_connection_failed": "Connection failed (timeout or strict NAT)",
        "p2p_retry": "Retry",
        "section_connection": "CONNECTION",
        "label_mode": "Mode",
        "leave_room": "Leave Room",
        "warning_no_file": "No file open. Host is playing: {file}",
        "warning_different_file": "Different file from host ({details}) — sync suspended.",
    },
}


def _base_dir():
    """Dossier contenant l'exécutable (ou le script, si lancé depuis les
    sources) — c'est là où l'installateur place icon.ico et lang.txt."""
    return os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))


def resource_path(rel_path):
    """Résout le chemin d'une ressource (police, image, html, icône) que l'application
    soit exécutée depuis les sources ou packagée avec PyInstaller (--onefile / sys._MEIPASS)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        p = os.path.join(sys._MEIPASS, rel_path)
        if os.path.exists(p):
            return p
    p = os.path.join(_base_dir(), rel_path)
    if os.path.exists(p):
        return p
    return os.path.abspath(rel_path)


_get_asset_path = resource_path


def load_application_fonts():
    """Charge les polices embarquées (Orbitron et Rajdhani) depuis assets/fonts/."""
    fonts_dir = resource_path(os.path.join("assets", "fonts"))
    if not os.path.isdir(fonts_dir):
        return
    for font_file in os.listdir(fonts_dir):
        if font_file.lower().endswith((".ttf", ".otf")):
            path = os.path.join(fonts_dir, font_file)
            try:
                QFontDatabase.addApplicationFont(path)
            except Exception:
                pass


def make_neon_glow(color_str, blur_radius=14):
    """Crée un halo néon discret pour un widget via QGraphicsDropShadowEffect."""
    effect = QGraphicsDropShadowEffect()
    effect.setColor(QColor(color_str))
    effect.setBlurRadius(blur_radius)
    effect.setOffset(0, 0)
    return effect


def _detect_language():
    """Langue choisie à l'installation (fichier lang.txt écrit par Inno
    Setup à côté de l'exécutable), sinon français par défaut."""
    try:
        lang_file = os.path.join(_base_dir(), "lang.txt")
        with open(lang_file, "r", encoding="utf-8") as f:
            content = f.read().strip().lower()
        if "english" in content or content == "en":
            return "en"
        if "french" in content or content == "fr":
            return "fr"
    except Exception:
        pass
    return "fr"


LANG = _detect_language()

ICON_PATH = resource_path("icon.ico")


def tr(key, **kwargs):
    text = STRINGS.get(LANG, STRINGS["fr"]).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text


# ---------------------------------------------------------------------------
# Section THEME — Palette extraite de BRAND.md (https://neonsyncs.com)
# ---------------------------------------------------------------------------
THEME = {
    # Arrière-plans
    "bg_window": "#08070d",             # Fond principal (noir profond bleuté/violacé)
    "bg_panel": "#0e091a",              # Fond du panneau latéral et de la barre de contrôle
    "bg_surface": "#0a0716",            # Fond des listes (chat, utilisateurs)
    "bg_card": "#0e091c",               # Fond des cartes et conteneurs
    "bg_input": "#080812",              # Fond des QLineEdit / QComboBox
    "bg_input_focus": "#0c0a18",        # Fond QLineEdit au focus
    "bg_video": "#000000",              # Fond du lecteur vidéo MPV
    "bg_slider_groove": "#141224",      # Rail de la barre de progression

    # Bordures
    "border_default": "rgba(0, 240, 255, 0.18)",  # Bordure cyan subtile standard
    "border_subtle": "rgba(0, 240, 255, 0.12)",   # Séparateurs très discrets
    "border_card": "rgba(0, 240, 255, 0.20)",     # Bordures de cartes
    "border_focus": "rgba(0, 240, 255, 0.60)",    # Bordure active au focus / survol

    # Accents & Lueurs
    "accent_primary": "#00f0ff",        # Cyan néon (accent principal du site)
    "accent_secondary": "#a855f7",      # Violet néon (accent secondaire du site)
    "accent_pink": "#ec4899",           # Rose néon (thème synthwave / gradient logo)
    "glow_primary": "rgba(0, 240, 255, 0.70)",     # Lueur cyan
    "glow_secondary": "rgba(168, 85, 247, 0.70)", # Lueur violette

    # Textes
    "text_primary": "#eaeaf6",          # Texte principal (blanc chaud néon)
    "text_white": "#ffffff",            # Blanc pur éclatant (survol boutons néon)
    "text_muted": "#8383a6",            # Texte estompé / labels
    "text_dim": "#525270",              # Texte très estompé

    # Statuts de connexion & alertes
    "status_connected": "#00ff9d",          # Vert néon (Connecté / OK)
    "status_connected_bg": "rgba(0, 255, 157, 0.10)",
    "status_connected_border": "rgba(0, 255, 157, 0.30)",
    "status_error": "#ff3860",              # Rouge néon (Erreurs / Déconnecté perdu)
    "status_error_bg": "rgba(255, 56, 96, 0.10)",
    "status_error_border": "rgba(255, 56, 96, 0.30)",
    "status_reconnecting": "#ffb627",       # Ambre néon (Reconnexion)
    "status_reconnecting_bg": "rgba(255, 182, 39, 0.10)",
    "status_reconnecting_border": "rgba(255, 182, 39, 0.30)",
    "status_disconnected": "#8383a6",       # Gris néon (Déconnecté normal)

    # Boutons néon cyan (Action principale)
    "btn_neon_border": "rgba(0, 240, 255, 0.45)",
    "btn_neon_border_hover": "rgba(0, 240, 255, 0.90)",
    "btn_neon_bg_top": "rgba(0, 240, 255, 0.12)",
    "btn_neon_bg_bottom": "rgba(0, 240, 255, 0.03)",
    "btn_neon_hover_top": "rgba(0, 240, 255, 0.26)",
    "btn_neon_hover_bottom": "rgba(0, 240, 255, 0.10)",

    # Boutons néon rose/violet (Action alternative / Rejoindre)
    "btn_pink_border": "rgba(229, 9, 20, 0.50)",
    "btn_pink_border_hover": "rgba(229, 9, 20, 0.90)",
    "btn_pink_bg_top": "rgba(229, 9, 20, 0.14)",
    "btn_pink_bg_bottom": "rgba(229, 9, 20, 0.04)",
    "btn_pink_hover_top": "rgba(229, 9, 20, 0.30)",
    "btn_pink_hover_bottom": "rgba(229, 9, 20, 0.12)",

    # Polices
    "font_body": "'Rajdhani', 'Segoe UI', Arial, sans-serif",
    "font_display": "'Orbitron', 'Segoe UI', Arial, sans-serif",
    "font_mono": "'Orbitron', 'Consolas', monospace",
}


# ---------------------------------------------------------------------------
# Thème visuel QSS généré dynamiquement à partir des tokens THEME
# ---------------------------------------------------------------------------
STYLE_SHEET = f"""
QWidget {{
    background-color: {THEME['bg_window']};
    color: {THEME['text_primary']};
    font-family: {THEME['font_body']};
    font-size: 10.5pt;
    font-weight: 500;
}}
QLabel {{
    color: {THEME['text_muted']};
    font-family: {THEME['font_body']};
}}
QLabel[role="section"] {{
    color: {THEME['accent_primary']};
    font-family: {THEME['font_display']};
    font-weight: 700;
    font-size: 8.5pt;
    letter-spacing: 1px;
    padding-top: 8px;
}}
QLabel[role="brand"] {{
    font-family: {THEME['font_display']};
    font-size: 13pt;
    font-weight: 900;
    letter-spacing: 1.5px;
}}
QLabel[role="website_link"] {{
    font-family: {THEME['font_display']};
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 1px;
    padding-top: 6px;
    color: {THEME['text_muted']};
}}
QLabel[role="website_link"]:hover {{
    color: {THEME['accent_primary']};
}}
QLabel[role="status"] {{
    color: {THEME['text_primary']};
    font-weight: 600;
    padding: 4px 0;
}}
QLabel[role="status"][state="connected"] {{
    color: {THEME['status_connected']};
}}
QLabel[role="status"][state="error"] {{
    color: {THEME['status_error']};
}}
QLabel[role="status"][state="reconnecting"] {{
    color: {THEME['status_reconnecting']};
}}
QLabel[role="status"][state="disconnected"] {{
    color: {THEME['status_disconnected']};
}}

QLineEdit {{
    background-color: {THEME['bg_input']};
    border: 1px solid {THEME['border_default']};
    border-radius: 8px;
    padding: 7px 10px;
    color: {THEME['text_primary']};
    font-family: {THEME['font_body']};
    font-size: 10.5pt;
    selection-background-color: {THEME['accent_primary']};
    selection-color: {THEME['bg_window']};
}}
QLineEdit:focus {{
    border: 1px solid {THEME['border_focus']};
    background-color: {THEME['bg_input_focus']};
}}

QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 240, 255, 0.08), stop:1 rgba(0, 240, 255, 0.02));
    border: 1px solid rgba(0, 240, 255, 0.25);
    border-radius: 8px;
    padding: 8px 14px;
    color: {THEME['text_primary']};
    font-family: {THEME['font_display']};
    font-size: 9.5pt;
    font-weight: 600;
}}
QPushButton:hover {{
    border: 1px solid {THEME['accent_primary']};
    color: {THEME['accent_primary']};
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 240, 255, 0.18), stop:1 rgba(0, 240, 255, 0.05));
}}
QPushButton:pressed {{
    background: {THEME['bg_window']};
}}

QPushButton[role="primary"] {{
    border: 1px solid {THEME['btn_neon_border']};
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {THEME['btn_neon_bg_top']}, stop:1 {THEME['btn_neon_bg_bottom']});
    color: {THEME['accent_primary']};
    font-family: {THEME['font_display']};
    font-weight: 700;
    letter-spacing: 0.5px;
}}
QPushButton[role="primary"]:hover {{
    border: 1px solid {THEME['btn_neon_border_hover']};
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {THEME['btn_neon_hover_top']}, stop:1 {THEME['btn_neon_hover_bottom']});
    color: {THEME['text_white']};
}}

QPushButton[role="pink"] {{
    border: 1px solid {THEME['btn_pink_border']};
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {THEME['btn_pink_bg_top']}, stop:1 {THEME['btn_pink_bg_bottom']});
    color: {THEME['accent_secondary']};
    font-family: {THEME['font_display']};
    font-weight: 700;
}}
QPushButton[role="pink"]:hover {{
    border: 1px solid {THEME['btn_pink_border_hover']};
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {THEME['btn_pink_hover_top']}, stop:1 {THEME['btn_pink_hover_bottom']});
    color: {THEME['text_white']};
}}

QPushButton[role="small"] {{
    padding: 5px 10px;
    font-size: 8.5pt;
}}

QPushButton[role="danger"] {{
    background: rgba(239, 68, 68, 0.12);
    border: 1px solid {THEME['status_error']};
    color: {THEME['status_error']};
    font-family: {THEME['font_display']};
    font-weight: 600;
}}
QPushButton[role="danger"]:hover {{
    background: rgba(239, 68, 68, 0.25);
    color: {THEME['text_white']};
}}

QComboBox {{
    background-color: {THEME['bg_input']};
    border: 1px solid {THEME['border_default']};
    border-radius: 8px;
    padding: 7px 10px;
    color: {THEME['text_primary']};
    font-family: {THEME['font_body']};
}}
QComboBox:focus, QComboBox:hover {{
    border: 1px solid {THEME['border_focus']};
}}
QComboBox::drop-down {{
    border: none;
    width: 22px;
}}
QComboBox QAbstractItemView {{
    background-color: {THEME['bg_panel']};
    border: 1px solid {THEME['border_default']};
    selection-background-color: rgba(0, 240, 255, 0.20);
    selection-color: {THEME['accent_primary']};
    color: {THEME['text_primary']};
    padding: 4px;
}}

QListWidget {{
    background-color: {THEME['bg_surface']};
    border: 1px solid {THEME['border_default']};
    border-radius: 10px;
    padding: 6px;
    outline: none;
    font-family: {THEME['font_body']};
    font-size: 10pt;
}}
QListWidget::item {{
    padding: 4px 6px;
    border-radius: 5px;
}}
QListWidget::item:selected {{
    background-color: rgba(0, 240, 255, 0.18);
    color: {THEME['accent_primary']};
}}

QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: rgba(0, 240, 255, 0.25);
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: rgba(0, 240, 255, 0.55);
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QFrame#videoFrame {{
    background-color: {THEME['bg_video']};
    border: none;
}}
QWidget#panel {{
    background-color: {THEME['bg_panel']};
    border-left: 1px solid {THEME['border_subtle']};
}}
QWidget#controlsBar {{
    background-color: {THEME['bg_panel']};
    border-top: 1px solid {THEME['border_subtle']};
}}
QLabel#timeLabel {{
    color: {THEME['text_muted']};
    font-family: {THEME['font_display']};
    font-size: 8.5pt;
    font-weight: 600;
    min-width: 48px;
}}

QSlider::groove:horizontal {{
    height: 6px;
    background: {THEME['bg_slider_groove']};
    border-radius: 3px;
}}
QSlider::sub-page:horizontal {{
    height: 6px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {THEME['accent_secondary']}, stop:1 {THEME['accent_primary']});
    border-radius: 3px;
}}
QSlider::add-page:horizontal {{
    height: 6px;
    background: {THEME['bg_slider_groove']};
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    width: 14px;
    height: 14px;
    margin: -4px 0;
    background: {THEME['text_primary']};
    border: 2px solid {THEME['accent_primary']};
    border-radius: 7px;
}}
QSlider::handle:horizontal:hover {{
    background: {THEME['accent_primary']};
    border: 2px solid {THEME['text_white']};
}}
"""


def _apply_dark_titlebar(widget):
    """Sur Windows 10/11, force la barre de titre native en mode sombre
    pour rester cohérent avec le thème de l'application. No-op ailleurs
    ou si l'API n'est pas disponible (echoue silencieusement)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        import ctypes.wintypes

        hwnd = int(widget.winId())
        dwm = ctypes.windll.dwmapi
        dwm.DwmSetWindowAttribute.argtypes = [
            ctypes.wintypes.HWND,
            ctypes.wintypes.DWORD,
            ctypes.c_void_p,
            ctypes.wintypes.DWORD,
        ]
        dwm.DwmSetWindowAttribute.restype = ctypes.c_long

        value = ctypes.c_int(1)
        for attr in (20, 19):  # DWMWA_USE_IMMERSIVE_DARK_MODE (20 = Win10 20H1+ / Win11, 19 = versions antérieures)
            res = dwm.DwmSetWindowAttribute(
                hwnd, attr, ctypes.byref(value), ctypes.sizeof(value)
            )
            if res == 0:
                break

        # Redessin forcé de la zone non cliente pour corriger le rendu initial de la barre de titre
        SWP_NOSIZE = 0x0001
        SWP_NOMOVE = 0x0002
        SWP_NOZORDER = 0x0004
        SWP_NOACTIVATE = 0x0010
        SWP_FRAMECHANGED = 0x0020
        flags = SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE

        user32 = ctypes.windll.user32
        user32.SetWindowPos.argtypes = [
            ctypes.wintypes.HWND,
            ctypes.wintypes.HWND,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.wintypes.UINT,
        ]
        user32.SetWindowPos.restype = ctypes.wintypes.BOOL
        user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, flags)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Réglages de synchronisation
# ---------------------------------------------------------------------------
SEEK_THRESHOLD = 1.0       # secondes d'écart tolérées avant de resynchroniser
STATE_SEND_INTERVAL = 3.0  # envoi périodique de l'état même sans événement
IGNORE_ECHO_WINDOW = 0.8   # évite de renvoyer un état qu'on vient de recevoir
MIN_CORRECTION_INTERVAL = 2.0  # anti-rebond : pas 2 corrections en moins de 2s
BIG_JUMP_THRESHOLD = 10.0      # au-dela, on corrige immediatement (vrai seek)
SEEK_BAR_RESOLUTION = 2000     # precision interne de la barre de progression
PROGRESS_UPDATE_INTERVAL = 400  # ms entre deux rafraichissements de la barre


def format_time(seconds):
    """Formate des secondes en 'm:ss' ou 'h:mm:ss'."""
    try:
        seconds = max(0, int(seconds))
    except (TypeError, ValueError):
        seconds = 0
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


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
        self.estimated_latency = 0.0  # secondes, mise a jour via ping/pong

    def connect_to(self, host, port, room, username, password=""):
        try:
            self.sock = socket.create_connection((host, port), timeout=5)
            self.sock.settimeout(None)
            # Desactive l'algorithme de Nagle : sans ca, de petits messages
            # JSON envoyes frequemment peuvent etre mis en attente/regroupes
            # par le systeme, ajoutant une latence supplementaire qui nuit
            # a la synchronisation.
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
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
                if msg.get("type") == "pong":
                    try:
                        rtt = time.time() - float(msg.get("t", 0))
                        if 0 <= rtt < 5:  # ignore les valeurs aberrantes
                            one_way = rtt / 2
                            # moyenne mobile pour lisser les variations
                            self.estimated_latency = (
                                0.7 * self.estimated_latency + 0.3 * one_way
                            )
                    except (TypeError, ValueError):
                        pass
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


class P2PBridge(QObject):
    """Pont de communication entre JavaScript (PeerJS) et Python via QWebChannel."""
    def __init__(self, client):
        super().__init__()
        self.client = client

    @pyqtSlot()
    def onBridgeReady(self):
        self.client._on_bridge_ready()

    @pyqtSlot(str)
    def onRoomCreated(self, room_id):
        self.client._on_room_created(room_id)

    @pyqtSlot(str)
    def onConnectionState(self, state):
        self.client._on_connection_state(state)

    @pyqtSlot(float, float)
    def onClockSync(self, offset_ms, rtt_ms):
        self.client._on_clock_sync(offset_ms, rtt_ms)

    @pyqtSlot(str)
    def onMessage(self, msg_str):
        self.client._on_message(msg_str)

    @pyqtSlot(str)
    def onError(self, err_msg):
        self.client._on_error(err_msg)

    @pyqtSlot(str, str)
    def onPeerJoined(self, peer_id, username):
        self.client._on_peer_joined(peer_id, username)

    @pyqtSlot(str)
    def onPeerLeft(self, peer_id):
        pass

    @pyqtSlot(str)
    def jsLog(self, msg):
        role = "HOST" if getattr(self.client, 'is_host', False) else "GUEST"
        print(f"[JS {role}] {msg}")


class P2PClient(QObject):
    """Gère la connexion P2P WebRTC via PeerJS dans un QWebEngineView caché."""
    message_received = pyqtSignal(dict)
    connected_signal = pyqtSignal(bool, str)
    disconnected_signal = pyqtSignal()
    room_created_signal = pyqtSignal(str)
    peer_joined_signal = pyqtSignal(str, str)
    reconnecting_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
        self.estimated_latency = 0.0
        self.clock_offset_ms = 0.0
        self.rtt_ms = 0.0
        self.is_host = False
        self.bridge_ready = False
        self.pending_action = None
        self.current_room_id = None

        self.view = QWebEngineView()
        self.channel = QWebChannel()
        self.bridge = P2PBridge(self)
        self.channel.registerObject("bridge", self.bridge)
        self.view.page().setWebChannel(self.channel)

        html_path = resource_path(os.path.join("p2p", "p2p.html"))
        self.view.load(QUrl.fromLocalFile(os.path.abspath(html_path)))

    def _on_bridge_ready(self):
        self.bridge_ready = True
        ice_path = resource_path(os.path.join("p2p", "ice_servers.json"))
        if os.path.exists(ice_path):
            try:
                with open(ice_path, "r", encoding="utf-8") as f:
                    ice_json = f.read()
                self.view.page().runJavaScript(f"window.p2p.setIceServers({json.dumps(ice_json)});")
            except Exception:
                pass

        if self.pending_action:
            action, args = self.pending_action
            self.pending_action = None
            if action == "create":
                self.create_room(*args)
            elif action == "join":
                self.join_room(*args)

    def create_room(self, username, password=""):
        self.is_host = True
        self.clock_offset_ms = 0.0
        if not self.bridge_ready:
            self.pending_action = ("create", (username, password))
            return
        self.view.page().runJavaScript(
            f"window.p2p.createRoom({json.dumps(username)}, {json.dumps(password)});"
        )

    def join_room(self, room_id, username, password=""):
        self.is_host = False
        if not self.bridge_ready:
            self.pending_action = ("join", (room_id, username, password))
            return
        self.view.page().runJavaScript(
            f"window.p2p.joinRoom({json.dumps(room_id)}, {json.dumps(username)}, {json.dumps(password)});"
        )

    def send(self, obj: dict):
        if not self.running and obj.get("type") != "hello":
            return
        try:
            self.view.page().runJavaScript(f"window.p2p.send({json.dumps(obj)});" )
        except Exception:
            pass

    def _on_room_created(self, room_id):
        self.current_room_id = room_id
        self.running = True
        self.is_host = True
        self.clock_offset_ms = 0.0
        self.room_created_signal.emit(room_id)
        self.connected_signal.emit(True, room_id)

    def _on_clock_sync(self, offset_ms, rtt_ms):
        self.clock_offset_ms = float(offset_ms)
        self.rtt_ms = float(rtt_ms)
        self.estimated_latency = (float(rtt_ms) / 2.0) / 1000.0

    def get_host_time_ms(self):
        """Retourne l'heure de référence de l'hôte en millisecondes."""
        if self.is_host:
            return time.time() * 1000.0
        return (time.time() * 1000.0) + self.clock_offset_ms

    def _on_connection_state(self, state):
        if state == "connected":
            self.running = True
            self.connected_signal.emit(True, "connecté")
        elif state == "reconnecting":
            self.reconnecting_signal.emit()
        elif state == "disconnected":
            was_running = self.running
            self.running = False
            self.current_room_id = None
            self.is_host = False
            self.clock_offset_ms = 0.0
            if was_running:
                self.disconnected_signal.emit()

    def _on_message(self, msg_str):
        try:
            msg = json.loads(msg_str)
        except Exception:
            return
        if msg.get("type") == "pong":
            try:
                rtt = time.time() - float(msg.get("t", 0))
                if 0 <= rtt < 5:
                    one_way = rtt / 2
                    self.estimated_latency = 0.7 * self.estimated_latency + 0.3 * one_way
            except (TypeError, ValueError):
                pass
            return
        self.message_received.emit(msg)

    def _on_peer_joined(self, peer_id, username):
        self.peer_joined_signal.emit(peer_id, username)

    def _on_error(self, err_msg):
        self.running = False
        self.connected_signal.emit(False, err_msg)

    def close(self):
        was_running = self.running
        self.running = False
        self.current_room_id = None
        self.is_host = False
        self.clock_offset_ms = 0.0
        if self.bridge_ready:
            self.view.page().runJavaScript("window.p2p.leave();")
        if was_running:
            self.disconnected_signal.emit()


class NeonSyncsWindow(QWidget):
    fs_toggle_requested = pyqtSignal()
    fs_exit_requested = pyqtSignal()
    seek_requested = pyqtSignal(float)
    pause_toggle_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("window_title"))
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        self.resize(1100, 650)

        self.net_server = NetworkClient()
        self.net_p2p = P2PClient(self)
        self.active_net = self.net_p2p

        self.net_server.message_received.connect(self.on_message)
        self.net_server.connected_signal.connect(self.on_connected)
        self.net_server.disconnected_signal.connect(self.on_disconnected)

        self.net_p2p.message_received.connect(self.on_message)
        self.net_p2p.connected_signal.connect(self.on_connected)
        self.net_p2p.disconnected_signal.connect(self.on_disconnected)
        self.net_p2p.room_created_signal.connect(self.on_room_created)
        self.net_p2p.peer_joined_signal.connect(self.on_peer_joined)
        self.net_p2p.reconnecting_signal.connect(self.on_reconnecting)

        self.last_remote_state_at = 0.0
        self.last_correction_at = 0.0
        self.applying_remote = False  # évite les boucles d'écho
        self.current_file = None
        self.current_duration = 0.0
        self.is_fullscreen = False
        self.is_seeking_via_slider = False
        self.shown_warnings = set()
        self.scheduled_action_id = 0

        self._build_ui()
        self._init_mpv()
        self.setStyleSheet(STYLE_SHEET)

        # Le signal permet de basculer le plein écran en toute sécurité
        # depuis le thread interne de mpv (les callbacks mpv ne tournent
        # pas dans le thread Qt principal).
        self.fs_toggle_requested.connect(self.toggle_fullscreen)
        self.fs_exit_requested.connect(self.exit_fullscreen)
        self.seek_requested.connect(self.seek_relative)
        self.pause_toggle_requested.connect(self.toggle_pause)

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

        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress_ui)
        self.progress_timer.start(PROGRESS_UPDATE_INTERVAL)

        # Mesure reguliere de la latence reseau (ping/pong), utilisee pour
        # compenser le retard des positions recues des autres participants.
        self.ping_timer = QTimer(self)
        self.ping_timer.timeout.connect(self.send_ping)
        self.ping_timer.start(2000)

    @property
    def net(self):
        return self.active_net

    def is_p2p_active(self):
        return self.combo_mode.currentIndex() == 0 and self.net_p2p.running

    def get_host_time_ms(self):
        if self.is_p2p_active():
            return self.net_p2p.get_host_time_ms()
        return time.time() * 1000.0

    def request_scheduled_action(self, action: str, target_time: float, paused: bool):
        try:
            duration = float(self.player.duration or self.current_duration or 0.0)
        except Exception:
            duration = 0.0
        self.net.send({
            "type": "action_request",
            "action": action,
            "targetTime": target_time,
            "paused": paused,
            "file": self.current_file,
            "duration": duration,
        })

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
        controls_container = QVBoxLayout(self.controls_widget)
        controls_container.setContentsMargins(10, 6, 10, 8)
        controls_container.setSpacing(4)

        # --- Barre de progression (glissable) + temps écoulé / durée ---
        progress_row = QHBoxLayout()
        self.time_current_label = QLabel("0:00")
        self.time_current_label.setObjectName("timeLabel")
        self.seek_slider = QSlider(Qt.Horizontal)
        self.seek_slider.setRange(0, SEEK_BAR_RESOLUTION)
        self.seek_slider.setValue(0)
        self.seek_slider.sliderPressed.connect(self.on_slider_pressed)
        self.seek_slider.sliderReleased.connect(self.on_slider_released)
        self.time_total_label = QLabel("0:00")
        self.time_total_label.setObjectName("timeLabel")
        progress_row.addWidget(self.time_current_label)
        progress_row.addWidget(self.seek_slider, stretch=1)
        progress_row.addWidget(self.time_total_label)
        controls_container.addLayout(progress_row)

        # --- Boutons (ouvrir, avance/retour, lecture, plein écran) ---
        controls = QHBoxLayout()
        self.btn_open = QPushButton(tr("open_file"))
        self.btn_open.clicked.connect(self.open_file)
        self.btn_back30 = QPushButton(tr("back_30"))
        self.btn_back30.clicked.connect(lambda: self.seek_relative(-30))
        self.btn_back10 = QPushButton(tr("back_10"))
        self.btn_back10.clicked.connect(lambda: self.seek_relative(-10))
        self.btn_play = QPushButton(tr("play_pause"))
        self.btn_play.setProperty("role", "primary")
        self.btn_play.setGraphicsEffect(make_neon_glow(THEME["accent_primary"], blur_radius=12))
        self.btn_play.clicked.connect(self.toggle_pause)
        self.btn_fwd10 = QPushButton(tr("fwd_10"))
        self.btn_fwd10.clicked.connect(lambda: self.seek_relative(10))
        self.btn_fwd30 = QPushButton(tr("fwd_30"))
        self.btn_fwd30.clicked.connect(lambda: self.seek_relative(30))
        self.btn_fullscreen = QPushButton(tr("fullscreen"))
        self.btn_fullscreen.clicked.connect(self.toggle_fullscreen)
        controls.addWidget(self.btn_open)
        controls.addWidget(self.btn_back30)
        controls.addWidget(self.btn_back10)
        controls.addWidget(self.btn_play)
        controls.addWidget(self.btn_fwd10)
        controls.addWidget(self.btn_fwd30)
        controls.addWidget(self.btn_fullscreen)
        controls_container.addLayout(controls)

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

        # En-tête de marque NeonSyncs (logo discret + titre officiel)
        brand_header = QWidget()
        brand_layout = QHBoxLayout(brand_header)
        brand_layout.setContentsMargins(0, 0, 0, 6)
        brand_layout.setSpacing(8)

        logo_label = QLabel()
        logo_svg = resource_path(os.path.join("brand", "favicon.svg"))
        if os.path.exists(logo_svg):
            renderer = QSvgRenderer(logo_svg)
            logo_img = QImage(28, 28, QImage.Format_ARGB32_Premultiplied)
            logo_img.fill(QColor(0, 0, 0, 0))
            lp = QPainter(logo_img)
            lp.setRenderHint(QPainter.Antialiasing)
            renderer.render(lp)
            lp.end()
            logo_label.setPixmap(QPixmap.fromImage(logo_img))
        logo_label.setFixedSize(28, 28)
        logo_label.setGraphicsEffect(make_neon_glow(THEME["accent_primary"], blur_radius=10))
        brand_layout.addWidget(logo_label)

        c_prim = THEME["accent_primary"]
        c_sec = THEME["accent_secondary"]
        brand_title = QLabel(f'<span style="color:{c_prim}; font-weight:900;">NEON</span><span style="color:{c_sec}; font-weight:900;">SYNCS</span>')
        brand_title.setProperty("role", "brand")
        brand_layout.addWidget(brand_title)
        brand_layout.addStretch(1)
        right.addWidget(brand_header)

        lbl_conn = QLabel(tr("section_connection"))
        lbl_conn.setProperty("role", "section")
        right.addWidget(lbl_conn)

        # Sélecteur de mode (P2P / Serveur)
        self.combo_mode = QComboBox()
        self.combo_mode.addItem(tr("mode_p2p"))
        self.combo_mode.addItem(tr("mode_server"))
        self.combo_mode.currentIndexChanged.connect(self.on_mode_changed)
        right.addWidget(self.combo_mode)

        # Champs communs (Pseudo & Mot de passe)
        self.input_user = QLineEdit("invite")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText(tr("password_placeholder"))

        right.addWidget(QLabel(tr("label_user")))
        right.addWidget(self.input_user)
        right.addWidget(QLabel(tr("label_password")))
        right.addWidget(self.input_password)

        # --- Conteneur Mode P2P ---
        self.p2p_container = QWidget()
        p2p_layout = QVBoxLayout(self.p2p_container)
        p2p_layout.setContentsMargins(0, 4, 0, 0)
        p2p_layout.setSpacing(6)

        self.btn_create_room = QPushButton(tr("create_room"))
        self.btn_create_room.setProperty("role", "primary")
        self.btn_create_room.setGraphicsEffect(make_neon_glow(THEME["accent_primary"], blur_radius=14))
        self.btn_create_room.clicked.connect(self.do_create_room)
        p2p_layout.addWidget(self.btn_create_room)

        p2p_layout.addWidget(QLabel(tr("room_id")))
        join_row = QHBoxLayout()
        self.input_room_id = QLineEdit()
        self.input_room_id.setPlaceholderText(tr("room_id_placeholder"))
        self.btn_join_room = QPushButton(tr("join_room"))
        self.btn_join_room.setProperty("role", "pink")
        self.btn_join_room.setGraphicsEffect(make_neon_glow(THEME["accent_secondary"], blur_radius=14))
        self.btn_join_room.clicked.connect(self.do_join_room)
        join_row.addWidget(self.input_room_id, stretch=1)
        join_row.addWidget(self.btn_join_room)
        p2p_layout.addLayout(join_row)

        self.room_info_widget = QWidget()
        room_info_layout = QHBoxLayout(self.room_info_widget)
        room_info_layout.setContentsMargins(0, 0, 0, 0)
        room_info_layout.setSpacing(4)
        self.input_my_room_id = QLineEdit()
        self.input_my_room_id.setReadOnly(True)
        self.btn_copy_id = QPushButton(tr("copy_id"))
        self.btn_copy_id.setProperty("role", "small")
        self.btn_copy_id.clicked.connect(self.copy_room_id)
        room_info_layout.addWidget(self.input_my_room_id, stretch=1)
        room_info_layout.addWidget(self.btn_copy_id)
        self.room_info_widget.hide()
        p2p_layout.addWidget(self.room_info_widget)

        self.btn_leave_p2p = QPushButton(tr("leave_room"))
        self.btn_leave_p2p.setProperty("role", "danger")
        self.btn_leave_p2p.clicked.connect(self.do_leave_p2p)
        self.btn_leave_p2p.hide()
        p2p_layout.addWidget(self.btn_leave_p2p)

        right.addWidget(self.p2p_container)

        # --- Conteneur Mode Serveur ---
        self.server_container = QWidget()
        server_layout = QVBoxLayout(self.server_container)
        server_layout.setContentsMargins(0, 4, 0, 0)
        server_layout.setSpacing(6)

        self.input_host = QLineEdit("127.0.0.1")
        self.input_port = QLineEdit("8999")
        self.input_room = QLineEdit("salon1")

        for w, label in [
            (self.input_host, tr("label_host")),
            (self.input_port, tr("label_port")),
            (self.input_room, tr("label_room")),
        ]:
            server_layout.addWidget(QLabel(label))
            server_layout.addWidget(w)

        self.btn_connect = QPushButton(tr("connect"))
        self.btn_connect.setProperty("role", "primary")
        self.btn_connect.setGraphicsEffect(make_neon_glow(THEME["accent_primary"], blur_radius=14))
        self.btn_connect.clicked.connect(self.do_connect)
        server_layout.addWidget(self.btn_connect)

        self.server_container.hide()
        right.addWidget(self.server_container)

        # État de connexion
        self.status_label = QLabel(tr("status_disconnected"))
        self.status_label.setProperty("role", "status")
        self.status_label.setWordWrap(True)
        right.addWidget(self.status_label)

        self.btn_retry_p2p = QPushButton(tr("p2p_retry"))
        self.btn_retry_p2p.setProperty("role", "small")
        self.btn_retry_p2p.clicked.connect(self.retry_p2p_action)
        self.btn_retry_p2p.hide()
        right.addWidget(self.btn_retry_p2p)

        # Utilisateurs
        lbl_users = QLabel(tr("section_users"))
        lbl_users.setProperty("role", "section")
        right.addWidget(lbl_users)
        self.user_list = QListWidget()
        self.user_list.setMaximumHeight(110)
        right.addWidget(self.user_list)

        # Chat
        lbl_chat = QLabel(tr("section_chat"))
        lbl_chat.setProperty("role", "section")
        right.addWidget(lbl_chat)
        self.chat_list = QListWidget()
        right.addWidget(self.chat_list, stretch=1)
        chat_row = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText(tr("chat_placeholder"))
        self.chat_input.returnPressed.connect(self.send_chat)
        btn_send = QPushButton(tr("send"))
        btn_send.setProperty("role", "primary")
        btn_send.setGraphicsEffect(make_neon_glow(THEME["accent_primary"], blur_radius=10))
        btn_send.clicked.connect(self.send_chat)
        chat_row.addWidget(self.chat_input)
        chat_row.addWidget(btn_send)
        right.addLayout(chat_row)

        # Lien discret vers le site officiel https://neonsyncs.com
        c_muted = THEME["text_muted"]
        lbl_site = QLabel(f'<a href="{APP_URL}" style="color:{c_muted}; text-decoration:none;">neonsyncs.com</a>')
        lbl_site.setOpenExternalLinks(True)
        lbl_site.setAlignment(Qt.AlignCenter)
        lbl_site.setCursor(Qt.PointingHandCursor)
        lbl_site.setProperty("role", "website_link")
        right.addWidget(lbl_site)

        root.addWidget(self.right_panel, stretch=0)

    def _init_mpv(self):
        # Intègre mpv directement dans le QFrame (pas de fenêtre externe)
        # NOTE : hwdec="no" desactive le decodage materiel (GPU). C'est
        # volontaire : avec l'integration via "wid", le decodage materiel
        # (hwdec="auto") provoque un ECRAN NOIR sur pas mal de cartes
        # graphiques/pilotes — probleme connu de libmpv en mode embarque.
        # Cout : un peu plus de charge CPU, mais une compatibilite bien
        # plus large et fiable.
        self.player = mpv.MPV(
            wid=str(int(self.video_frame.winId())),
            input_default_bindings=True,
            input_vo_keyboard=True,
            osc=True,
            hwdec="no",
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
        for key in ("f", "F11", "MBTN_LEFT_DBL", "SPACE"):
            try:
                self.player.command("keybind", key, "ignore")
            except Exception:
                pass

        @self.player.on_key_press("SPACE")
        def _mpv_toggle_pause():
            self.pause_toggle_requested.emit()

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
        self.shown_warnings.clear()
        self.player.play(path)
        if self.is_p2p_active() and not self.net_p2p.is_host:
            self.net.send({"type": "get_state"})
        else:
            self.push_state(force=True)

    def toggle_pause(self):
        new_paused = not bool(self.player.pause)
        action = "pause" if new_paused else "play"
        try:
            current_pos = float(self.player.time_pos or 0.0)
        except Exception:
            current_pos = 0.0

        if self.is_p2p_active():
            self.request_scheduled_action(action, current_pos, new_paused)
        else:
            self.player.pause = new_paused

    def seek_relative(self, seconds: float):
        """Avance ou recule dans la vidéo (secondes positives = avance)."""
        try:
            current_pos = float(self.player.time_pos or 0.0)
            duration = float(self.player.duration or 0.0)
        except Exception:
            current_pos, duration = 0.0, 0.0

        now = time.time()
        if hasattr(self, "_last_seek_req_time") and (now - self._last_seek_req_time < 0.6) and hasattr(self, "_last_seek_target"):
            base_pos = self._last_seek_target
        else:
            base_pos = current_pos

        target = max(0.0, base_pos + seconds)
        if duration > 0:
            target = min(target, duration)

        self._last_seek_target = target
        self._last_seek_req_time = now

        if self.is_p2p_active():
            paused = bool(self.player.pause)
            self.request_scheduled_action("seek", target, paused)
        else:
            try:
                self.player.seek(seconds, reference="relative")
            except Exception:
                return
            self.push_state(force=True)

    def on_slider_pressed(self):
        # Pendant que l'utilisateur fait glisser la barre, on arrête de
        # la mettre à jour automatiquement (sinon ça "combat" son geste).
        self.is_seeking_via_slider = True

    def on_slider_released(self):
        self.is_seeking_via_slider = False
        try:
            duration = float(self.player.duration or 0.0)
        except Exception:
            duration = 0.0
        if duration <= 0:
            return
        fraction = self.seek_slider.value() / SEEK_BAR_RESOLUTION
        target = max(0.0, min(fraction * duration, duration))

        if self.is_p2p_active():
            paused = bool(self.player.pause)
            self.request_scheduled_action("seek", target, paused)
        else:
            try:
                self.player.seek(target, reference="absolute")
            except Exception:
                return
            self.push_state(force=True)

    def update_progress_ui(self):
        """Rafraîchit la barre de progression et les labels de temps.
        N'est PAS appliqué pendant que l'utilisateur fait glisser la
        barre lui-même (voir on_slider_pressed)."""
        if self.is_seeking_via_slider:
            return
        try:
            pos = float(self.player.time_pos or 0.0)
            duration = float(self.player.duration or 0.0)
        except Exception:
            pos, duration = 0.0, 0.0

        self.time_current_label.setText(format_time(pos))
        self.time_total_label.setText(format_time(duration))

        if duration > 0:
            value = int((pos / duration) * SEEK_BAR_RESOLUTION)
            self.seek_slider.blockSignals(True)
            self.seek_slider.setValue(max(0, min(value, SEEK_BAR_RESOLUTION)))
            self.seek_slider.blockSignals(False)

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

    def set_status_state(self, state: str):
        self.status_label.setProperty("state", state)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def on_mode_changed(self, index):
        if self.active_net.running:
            self.active_net.close()
        self.user_list.clear()
        self.btn_retry_p2p.hide()
        self.set_status_state("disconnected")
        self.status_label.setText(tr("status_disconnected"))
        if index == 0:  # P2P
            self.active_net = self.net_p2p
            self.p2p_container.show()
            self.server_container.hide()
        else:  # Serveur
            self.active_net = self.net_server
            self.p2p_container.hide()
            self.server_container.show()

    def do_create_room(self):
        user = self.input_user.text().strip() or "Hote"
        password = self.input_password.text()
        self.last_p2p_action = ("create", user, password)
        self.btn_retry_p2p.hide()
        self.set_status_state("reconnecting")
        self.status_label.setText(tr("status_creating"))
        self.btn_create_room.setEnabled(False)
        self.btn_join_room.setEnabled(False)
        self.net_p2p.create_room(user, password)

    def do_join_room(self):
        room_id = self.input_room_id.text().strip()
        if not room_id:
            self.set_status_state("error")
            self.status_label.setText(tr("status_error", message="ID du salon requis"))
            return
        user = self.input_user.text().strip() or "Invite"
        password = self.input_password.text()
        self.last_p2p_action = ("join", room_id, user, password)
        self.btn_retry_p2p.hide()
        self.set_status_state("reconnecting")
        self.status_label.setText(tr("status_joining"))
        self.btn_create_room.setEnabled(False)
        self.btn_join_room.setEnabled(False)
        self.net_p2p.join_room(room_id, user, password)

    def retry_p2p_action(self):
        self.btn_retry_p2p.hide()
        if hasattr(self, "last_p2p_action") and self.last_p2p_action:
            action = self.last_p2p_action[0]
            if action == "create":
                self.do_create_room()
            elif action == "join":
                self.do_join_room()

    def do_leave_p2p(self):
        self.net_p2p.close()
        self.room_info_widget.hide()
        self.btn_leave_p2p.hide()
        self.btn_retry_p2p.hide()
        self.btn_create_room.setEnabled(True)
        self.btn_join_room.setEnabled(True)
        self.set_status_state("disconnected")
        self.status_label.setText(tr("status_disconnected"))
        self.user_list.clear()

    def on_room_created(self, room_id):
        self.input_my_room_id.setText(room_id)
        self.room_info_widget.show()
        self.btn_leave_p2p.show()
        self.btn_retry_p2p.hide()
        self.btn_create_room.setEnabled(False)
        self.btn_join_room.setEnabled(False)

    def copy_room_id(self):
        text = self.input_my_room_id.text().strip()
        if text:
            QApplication.clipboard().setText(text)
            self.btn_copy_id.setText(tr("id_copied"))
            QTimer.singleShot(2000, lambda: self.btn_copy_id.setText(tr("copy_id")))

    def do_connect(self):
        if self.net_server.running:
            self.net_server.close()
            self.btn_connect.setText(tr("connect"))
            self.btn_connect.setProperty("role", "primary")
            self.btn_connect.style().unpolish(self.btn_connect)
            self.btn_connect.style().polish(self.btn_connect)
            self.set_status_state("disconnected")
            return
        host = self.input_host.text().strip()
        try:
            port = int(self.input_port.text().strip())
        except ValueError:
            port = 8999
        room = self.input_room.text().strip()
        user = self.input_user.text().strip() or "invite"
        password = self.input_password.text()
        self.net_server.connect_to(host, port, room, user, password)

    def on_connected(self, ok, message):
        if ok:
            self.set_status_state("connected")
            self.status_label.setText(tr("status_connected"))
            self.btn_retry_p2p.hide()
            if self.combo_mode.currentIndex() == 0:  # P2P
                self.btn_leave_p2p.show()
                self.btn_create_room.setEnabled(False)
                self.btn_join_room.setEnabled(False)
            else:  # Serveur
                self.btn_connect.setText(tr("disconnect"))
                self.btn_connect.setProperty("role", "danger")
                self.btn_connect.style().unpolish(self.btn_connect)
                self.btn_connect.style().polish(self.btn_connect)
        else:
            self.set_status_state("error")
            friendly_msg = tr(message) if message in STRINGS.get(LANG, STRINGS["fr"]) else message
            self.status_label.setText(tr("status_error", message=friendly_msg))
            if self.combo_mode.currentIndex() == 0:  # P2P
                self.btn_create_room.setEnabled(True)
                self.btn_join_room.setEnabled(True)
                self.btn_leave_p2p.hide()
                self.room_info_widget.hide()
                self.btn_retry_p2p.show()
            else:
                self.btn_connect.setText(tr("connect"))
                self.btn_connect.setProperty("role", "primary")
                self.btn_connect.style().unpolish(self.btn_connect)
                self.btn_connect.style().polish(self.btn_connect)

    def on_reconnecting(self):
        self.set_status_state("reconnecting")
        self.status_label.setText(tr("status_reconnecting"))

    def on_disconnected(self):
        self.set_status_state("disconnected")
        self.status_label.setText(tr("status_disconnected_lost"))
        self.user_list.clear()
        if self.combo_mode.currentIndex() == 0:  # P2P
            self.btn_create_room.setEnabled(True)
            self.btn_join_room.setEnabled(True)
            self.btn_leave_p2p.hide()
            self.room_info_widget.hide()
            if hasattr(self, "last_p2p_action") and self.last_p2p_action:
                self.btn_retry_p2p.show()
        else:
            self.btn_connect.setText(tr("connect"))
            self.btn_connect.setProperty("role", "primary")
            self.btn_connect.style().unpolish(self.btn_connect)
            self.btn_connect.style().polish(self.btn_connect)

    def send_chat(self):
        text = self.chat_input.text().strip()
        if not text:
            return
        if not self.net.running:
            self.chat_list.addItem(tr("chat_not_connected"))
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
        now_host_ms = self.get_host_time_ms()
        self.net.send({
            "type": "state",
            "paused": paused,
            "position": position,
            "file": self.current_file,
            "duration": duration,
            "targetTime": position,
            "executeAt": now_host_ms,
            "periodic": not force,
        })

    def periodic_state_push(self):
        if self.net.running:
            # En mode P2P, seul l'hôte diffuse l'état périodique (toutes les 3s)
            if self.is_p2p_active() and not self.net_p2p.is_host:
                return
            self.push_state()

    def send_ping(self):
        if self.net.running:
            self.net.send({"type": "ping", "t": time.time()})

    def on_peer_joined(self, peer_id, username):
        if self.is_p2p_active() and self.net_p2p.is_host:
            # Un invité vient d'entrer : on lui transmet immédiatement notre état actuel
            self.push_state(force=True)

    def on_message(self, msg: dict):
        mtype = msg.get("type")
        if mtype == "state":
            self.apply_remote_state(msg)
        elif mtype == "get_state":
            if self.is_p2p_active() and self.net_p2p.is_host:
                self.push_state(force=True)
        elif mtype == "userlist":
            self.user_list.clear()
            self.user_list.addItems(msg.get("users", []))
        elif mtype == "chat":
            self.chat_list.addItem(f"{msg.get('from')}: {msg.get('message')}")
            self.chat_list.scrollToBottom()
        elif mtype == "error":
            self.status_label.setText(tr("status_error", message=msg.get('message', '')))
            self.net.close()

    def apply_remote_state(self, msg: dict):
        action = msg.get("action")
        execute_at = msg.get("executeAt")

        # En mode P2P, l'hôte est la source de référence pour la lecture :
        # il n'applique pas les corrections de dérive périodiques ni les états passifs des invités.
        # Seules les actions planifiées (play / pause / seek avec executeAt) sont exécutées.
        if self.is_p2p_active() and self.net_p2p.is_host:
            if not (action in ("play", "pause", "seek") and execute_at is not None):
                return

        # 1. Vérification fichier distinct (exigence 4)
        remote_file = msg.get("file")
        remote_duration = float(msg.get("duration") or 0.0)

        if remote_file:
            remote_base = os.path.basename(remote_file).lower()
            local_base = os.path.basename(self.current_file).lower() if self.current_file else ""

            if not self.current_file:
                warn_key = f"no_file_{remote_base}"
                if warn_key not in self.shown_warnings:
                    self.shown_warnings.add(warn_key)
                    self.chat_list.addItem(f"⚠ {tr('warning_no_file', file=os.path.basename(remote_file))}")
                    self.chat_list.scrollToBottom()
                return

            name_diff = (remote_base != local_base)
            try:
                local_duration = float(self.player.duration or self.current_duration or 0.0)
            except Exception:
                local_duration = 0.0
            duration_diff = (remote_duration > 0 and local_duration > 0 and abs(remote_duration - local_duration) > 2.0)

            if name_diff or duration_diff:
                warn_key = f"diff_{remote_base}_{local_base}"
                if warn_key not in self.shown_warnings:
                    self.shown_warnings.add(warn_key)
                    reasons = []
                    if name_diff:
                        reasons.append(f"{os.path.basename(remote_file)} ≠ {os.path.basename(self.current_file)}")
                    if duration_diff:
                        reasons.append(f"{format_time(remote_duration)} ≠ {format_time(local_duration)}")
                    self.chat_list.addItem(f"⚠ {tr('warning_different_file', details=', '.join(reasons))}")
                    self.chat_list.scrollToBottom()
                return  # Ne force PAS la synchronisation sur un fichier différent

        # 2. Action planifiée (play / pause / seek avec executeAt) (exigence 2)
        if action in ("play", "pause", "seek") and execute_at is not None:
            host_now_ms = self.get_host_time_ms()
            delay_ms = float(execute_at) - host_now_ms
            delay_ms = max(0.0, min(delay_ms, 1000.0))

            target_time = float(msg.get("targetTime", msg.get("position", 0.0)))
            paused = msg.get("paused")

            self.scheduled_action_id += 1
            current_action_id = self.scheduled_action_id

            def _execute_action():
                if current_action_id != self.scheduled_action_id:
                    return
                self.applying_remote = True
                try:
                    try:
                        self.player.seek(target_time, reference="absolute")
                    except Exception:
                        pass
                    try:
                        if paused is not None:
                            self.player.pause = bool(paused)
                        elif action == "play":
                            self.player.pause = False
                        elif action == "pause":
                            self.player.pause = True
                        self.player.speed = 1.0
                    except Exception:
                        pass
                    self.last_correction_at = time.time()
                    self._last_seek_target = target_time
                finally:
                    self.last_remote_state_at = time.time()
                    QTimer.singleShot(400, lambda: setattr(self, "applying_remote", False))

            if delay_ms <= 0:
                _execute_action()
            else:
                QTimer.singleShot(int(delay_ms), _execute_action)
            return

        # 3. Correction de dérive sur state périodique (exigence 3)
        if msg.get("periodic") and execute_at is not None:
            remote_paused = msg.get("paused")
            if remote_paused is not None and bool(remote_paused) != bool(self.player.pause):
                self.player.pause = bool(remote_paused)
                self.player.speed = 1.0

            try:
                local_pos = float(self.player.time_pos or 0.0)
            except Exception:
                local_pos = 0.0

            if bool(self.player.pause):
                target_time = float(msg.get("targetTime", msg.get("position", 0.0)))
                if abs(local_pos - target_time) > SEEK_THRESHOLD:
                    self.applying_remote = True
                    self.player.seek(target_time, reference="absolute")
                    self.player.speed = 1.0
                    self.last_remote_state_at = time.time()
                    QTimer.singleShot(400, lambda: setattr(self, "applying_remote", False))
                return

            now_host_sec = self.get_host_time_ms() / 1000.0
            execute_at_sec = float(execute_at) / 1000.0
            target_time = float(msg.get("targetTime", msg.get("position", 0.0)))
            elapsed = max(0.0, now_host_sec - execute_at_sec)
            theo_pos = target_time + elapsed

            diff = theo_pos - local_pos
            gap = abs(diff)

            if gap < 0.05:
                if self.player.speed != 1.0:
                    self.player.speed = 1.0
            elif gap < 1.0:
                # Écart < 1s : ajustement fluide de vitesse (0.97 à 1.03) sans seek
                if diff > 0:
                    new_speed = min(1.03, 1.0 + max(0.01, diff * 0.04))
                else:
                    new_speed = max(0.97, 1.0 - max(0.01, gap * 0.04))
                self.player.speed = round(new_speed, 3)
            else:
                # Écart >= 1s : seek direct
                now = time.time()
                if gap > BIG_JUMP_THRESHOLD or (now - self.last_correction_at > MIN_CORRECTION_INTERVAL):
                    self.applying_remote = True
                    try:
                        self.player.seek(theo_pos, reference="absolute")
                        self.player.speed = 1.0
                        self.last_correction_at = now
                    except Exception:
                        pass
                    finally:
                        self.last_remote_state_at = now
                        QTimer.singleShot(400, lambda: setattr(self, "applying_remote", False))
            return

        # 4. Fallback classique (mode Serveur ou message direct sans executeAt)
        remote_position = msg.get("position")
        remote_paused = msg.get("paused")
        self.applying_remote = True
        try:
            if remote_position is not None:
                try:
                    local_pos = float(self.player.time_pos or 0.0)
                except Exception:
                    local_pos = 0.0
                gap = abs(local_pos - remote_position)
                now = time.time()
                if gap > SEEK_THRESHOLD:
                    big_jump = gap > BIG_JUMP_THRESHOLD
                    time_since_last = now - self.last_correction_at
                    if big_jump or time_since_last > MIN_CORRECTION_INTERVAL:
                        self.player.seek(remote_position, reference="absolute")
                        self.last_correction_at = now
            if remote_paused is not None:
                self.player.pause = bool(remote_paused)
        except Exception:
            pass
        finally:
            self.last_remote_state_at = time.time()
            QTimer.singleShot(400, lambda: setattr(self, "applying_remote", False))

    def closeEvent(self, event):
        self.net_server.close()
        self.net_p2p.close()
        try:
            self.player.terminate()
        except Exception:
            pass
        event.accept()


SyncMPVWindow = NeonSyncsWindow


def main():
    app = QApplication(sys.argv)
    load_application_fonts()
    app.setStyleSheet(STYLE_SHEET)
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))
    win = NeonSyncsWindow()
    win.winId()
    _apply_dark_titlebar(win)
    win.show()
    QTimer.singleShot(0, lambda: _apply_dark_titlebar(win))
    QTimer.singleShot(150, lambda: _apply_dark_titlebar(win))
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
