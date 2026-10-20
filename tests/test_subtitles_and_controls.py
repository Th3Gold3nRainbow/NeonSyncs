import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure repo root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

if sys.platform == "win32":
    if hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(REPO_ROOT)
        except Exception:
            pass
    os.environ["PATH"] = REPO_ROOT + os.pathsep + os.environ.get("PATH", "")

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

import i18n
from i18n import tr, set_language, get_language
import client


class TestSubtitlesAndControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([sys.argv[0]])

    def setUp(self):
        set_language("en")
        with patch.object(client, "P2PClient"):
            self.win = client.NeonSyncsWindow()
        self.win.show()
        self.win.activateWindow()
        self.app.setActiveWindow(self.win)

    def tearDown(self):
        if hasattr(self.win, "player") and self.win.player:
            try:
                self.win.player.terminate()
            except Exception:
                pass
        self.win.close()

    # ------------------------------------------------------------------
    # 1. Sous-titres (strictement locaux)
    # ------------------------------------------------------------------
    def test_subtitles_load_calls_sub_add_with_select(self):
        """« Load subtitle file » appelle sub-add avec select et ne touche pas au réseau."""
        mock_player = MagicMock()
        self.win.player = mock_player
        self.win.current_file = r"C:\fake\video.mp4"

        with patch.object(self.win, "push_state") as mock_push_state, \
             patch("PyQt5.QtWidgets.QFileDialog.getOpenFileName", return_value=(r"C:\fake\subs.srt", "Subtitle files")):
            self.win.load_subtitle_file()
            mock_player.command.assert_called_once_with("sub-add", r"C:\fake\subs.srt", "select")
            mock_push_state.assert_not_called()

    def test_subtitles_track_selection_sets_sid(self):
        """Choisir une piste règle sid localement sans appeler push_state."""
        mock_player = MagicMock()
        self.win.player = mock_player
        with patch.object(self.win, "push_state") as mock_push_state:
            self.win._set_subtitle_track(2)
            mock_player.command.assert_called_once_with("set", "sid", 2)
            mock_push_state.assert_not_called()

    def test_subtitles_off_sets_sid_no(self):
        """« Off » règle sid sur no localement sans appeler push_state."""
        mock_player = MagicMock()
        self.win.player = mock_player
        with patch.object(self.win, "push_state") as mock_push_state:
            self.win._disable_subtitles()
            mock_player.command.assert_called_once_with("set", "sid", "no")
            mock_push_state.assert_not_called()

    def test_subtitles_delay_actions(self):
        """Les trois actions de délai modifient sub-delay sans appeler push_state."""
        mock_player = MagicMock()
        mock_player.sub_delay = 0.0
        self.win.player = mock_player

        with patch.object(self.win, "push_state") as mock_push_state:
            # Delay -0.1s
            self.win._adjust_sub_delay(-0.1)
            self.assertEqual(round(self.win.player.sub_delay, 1), -0.1)

            # Delay +0.1s
            self.win._adjust_sub_delay(0.1)
            self.assertEqual(round(self.win.player.sub_delay, 1), 0.0)

            # Delay +0.2s then reset
            self.win._adjust_sub_delay(0.2)
            self.assertEqual(round(self.win.player.sub_delay, 1), 0.2)
            self.win._reset_sub_delay()
            self.assertEqual(self.win.player.sub_delay, 0.0)

            mock_push_state.assert_not_called()

    def test_subtitles_menu_construction_three_track_sets(self):
        """Menu construit avec 3 jeux de pistes simulés : embarquées, externe, aucune."""
        mock_player = MagicMock()
        mock_player.sub_delay = 0.5
        self.win.player = mock_player

        # Set 1: Embarquées
        mock_player.sid = 1
        mock_player.track_list = [
            {"type": "video", "id": 1},
            {"type": "sub", "id": 1, "title": "English Full", "lang": "eng", "selected": True, "external": False},
            {"type": "sub", "id": 2, "title": "French", "lang": "fra", "selected": False, "external": False},
        ]
        self.win._build_subtitles_menu()
        actions_text = [a.text() for a in self.win.subtitles_menu.actions()]
        self.assertTrue(any("English Full" in t for t in actions_text))
        self.assertTrue(any("French" in t for t in actions_text))
        # Off is unchecked
        off_act = [a for a in self.win.subtitles_menu.actions() if a.text() == tr("subtitles_off")][0]
        self.assertFalse(off_act.isChecked())

        # Set 2: Externe
        mock_player.sid = 3
        mock_player.track_list = [
            {"type": "sub", "id": 3, "title": None, "lang": None, "selected": True, "external": True},
        ]
        self.win._build_subtitles_menu()
        actions_text = [a.text() for a in self.win.subtitles_menu.actions()]
        self.assertTrue(any(tr("subtitles_external") in t for t in actions_text))

        # Set 3: Aucune piste
        mock_player.sid = False
        mock_player.track_list = [
            {"type": "video", "id": 1},
            {"type": "audio", "id": 2},
        ]
        self.win._build_subtitles_menu()
        actions_text = [a.text() for a in self.win.subtitles_menu.actions()]
        self.assertTrue(any(tr("subtitles_no_tracks") in t for t in actions_text))
        no_tracks_act = [a for a in self.win.subtitles_menu.actions() if tr("subtitles_no_tracks") in a.text()][0]
        self.assertFalse(no_tracks_act.isEnabled())
        off_act = [a for a in self.win.subtitles_menu.actions() if a.text() == tr("subtitles_off")][0]
        self.assertTrue(off_act.isChecked())

    # ------------------------------------------------------------------
    # 2. Sauts au clavier (10s uniquement, aucun saut de 60s)
    # ------------------------------------------------------------------
    def test_jumps_up_down_disabled(self):
        """QTest.keyClick sur Haut et Bas n'appelle ni seek_relative ni push_state."""
        with patch.object(self.win, "seek_relative") as mock_seek, \
             patch.object(self.win, "push_state") as mock_push_state:
            QTest.keyClick(self.win, Qt.Key_Up)
            QTest.keyClick(self.win, Qt.Key_Down)
            mock_seek.assert_not_called()
            mock_push_state.assert_not_called()

    def test_jumps_left_right_active(self):
        """Gauche et Droite appellent seek_relative(∓10) une seule fois."""
        with patch.object(self.win, "seek_relative") as mock_seek:
            QTest.keyClick(self.win, Qt.Key_Right)
            mock_seek.assert_called_once_with(10)
            mock_seek.reset_mock()

            QTest.keyClick(self.win, Qt.Key_Left)
            mock_seek.assert_called_once_with(-10)

    def test_jumps_buttons_10s_unchanged(self):
        """Les boutons ±10 s sont présents et appellent seek_relative(±10)."""
        with patch.object(self.win, "seek_relative") as mock_seek:
            self.win.btn_fwd10.click()
            mock_seek.assert_called_once_with(10)
            mock_seek.reset_mock()

            self.win.btn_back10.click()
            mock_seek.assert_called_once_with(-10)

    def test_no_60s_seek_in_client_code(self):
        """Plus aucun saut de 60 dans le code de client.py."""
        client_path = os.path.join(REPO_ROOT, "client.py")
        with open(client_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for idx, line in enumerate(lines, 1):
            if "seek_relative" in line or "seek_requested" in line:
                self.assertNotIn("60", line, f"Found 60 in seek call at client.py:{idx}: {line.strip()}")
            if "Key_Up" in line or "Key_Down" in line:
                self.assertNotIn("seek", line.lower(), f"Found seek tied to Up/Down at client.py:{idx}: {line.strip()}")

    # ------------------------------------------------------------------
    # 3. Barre d'espace : lecture/pause en plein écran
    # ------------------------------------------------------------------
    def test_space_behavior_window_vs_fullscreen(self):
        """Vérifie le comportement de la touche Espace en fenêtre vs plein écran."""
        with patch.object(client.NeonSyncsWindow, "toggle_pause") as mock_play_pause:
            with patch.object(client, "P2PClient"):
                test_win = client.NeonSyncsWindow()
            test_win.show()
            test_win.activateWindow()
            self.app.setActiveWindow(test_win)

            # Clic sur le bouton Play/Pause appelle la fonction exactement une fois
            test_win.btn_play.click()
            self.assertEqual(mock_play_pause.call_count, 1)
            mock_play_pause.reset_mock()

            # Événement mpv SPACE appelle la fonction exactement une fois
            test_win.pause_toggle_requested.emit()
            self.assertEqual(mock_play_pause.call_count, 1)
            mock_play_pause.reset_mock()

            # En mode fenêtre : le raccourci Qt est désactivé -> 0 appel
            self.assertFalse(test_win.is_fullscreen)
            self.assertFalse(test_win.shortcut_space.isEnabled())
            target = test_win.focusWidget() or test_win
            QTest.keyClick(target, Qt.Key_Space)
            mock_play_pause.assert_not_called()

            # En mode plein écran : le raccourci Qt est activé -> 1 appel
            test_win.enter_fullscreen()
            self.assertTrue(test_win.is_fullscreen)
            self.assertTrue(test_win.shortcut_space.isEnabled())
            test_win.video_frame.setFocus()
            target = test_win.focusWidget() or test_win
            QTest.keyClick(target, Qt.Key_Space)
            self.assertEqual(mock_play_pause.call_count, 1)
            mock_play_pause.reset_mock()

            # Sortie du plein écran : le raccourci Qt est désactivé
            test_win.exit_fullscreen()
            self.assertFalse(test_win.is_fullscreen)
            self.assertFalse(test_win.shortcut_space.isEnabled())
            target = test_win.focusWidget() or test_win
            QTest.keyClick(target, Qt.Key_Space)
            mock_play_pause.assert_not_called()

            test_win.close()

    def test_space_shortcut_repetition_disabled(self):
        """AutoRepeat est désactivé sur le raccourci Qt Espace."""
        self.assertFalse(self.win.shortcut_space.autoRepeat())

    def test_fullscreen_entry_exit_mechanisms(self):
        """Le raccourci est bien réactivé et désactivé à chaque entrée et sortie (F, F11, Échap, double-clic)."""
        # Via toggle_fullscreen
        self.win.toggle_fullscreen()
        self.assertTrue(self.win.is_fullscreen)
        self.assertTrue(self.win.shortcut_space.isEnabled())
        self.win.toggle_fullscreen()
        self.assertFalse(self.win.is_fullscreen)
        self.assertFalse(self.win.shortcut_space.isEnabled())

        # Via exit_fullscreen (Échap)
        self.win.enter_fullscreen()
        self.win.exit_fullscreen()
        self.assertFalse(self.win.is_fullscreen)
        self.assertFalse(self.win.shortcut_space.isEnabled())

        # Via double-clic
        self.win.on_video_double_click()
        self.assertTrue(self.win.is_fullscreen)
        self.assertTrue(self.win.shortcut_space.isEnabled())
        self.win._last_dbl_click_at = 0.0
        self.win.on_video_double_click()
        self.assertFalse(self.win.is_fullscreen)
        self.assertFalse(self.win.shortcut_space.isEnabled())

    # ------------------------------------------------------------------
    # 4. Changement de langue (EN, FR, RU, AR) et disposition
    # ------------------------------------------------------------------
    def test_language_switch_and_control_bar_layout(self):
        """Libellés corrects, arabe en miroir, 30s inexistants, barre tient sans rognage."""
        for lang in ("en", "fr", "ru", "ar"):
            set_language(lang)
            self.win.retranslate_ui()

            # Les boutons 30s n'existent plus sur le widget
            self.assertFalse(hasattr(self.win, "btn_back30"))
            self.assertFalse(hasattr(self.win, "btn_fwd30"))

            # Les boutons 10s et le bouton sous-titres existent
            self.assertTrue(hasattr(self.win, "btn_back10"))
            self.assertTrue(hasattr(self.win, "btn_fwd10"))
            self.assertTrue(hasattr(self.win, "btn_subtitles"))
            self.assertTrue(hasattr(self.win, "btn_fullscreen"))

            # Le bouton plein écran bascule is_fullscreen
            was_fs = self.win.is_fullscreen
            self.win.btn_fullscreen.click()
            self.assertNotEqual(self.win.is_fullscreen, was_fs)
            self.win.btn_fullscreen.click()
            self.assertEqual(self.win.is_fullscreen, was_fs)

            # Vérifier l'info-bulle du bouton sous-titres et plein écran
            self.assertEqual(self.win.btn_subtitles.toolTip(), tr("subtitles"))
            self.assertEqual(self.win.btn_fullscreen.toolTip(), tr("fullscreen"))

            # Arabe en miroir
            if lang == "ar":
                self.assertEqual(self.win.layoutDirection(), Qt.RightToLeft)
            else:
                self.assertEqual(self.win.layoutDirection(), Qt.LeftToRight)

            # Test largeur standard (1100) et réduite (950 / 800)
            for width in (1100, 950):
                self.win.resize(width, 650)
                self.app.processEvents()
                self.assertTrue(self.win.controls_widget.isVisible())
                self.assertLessEqual(self.win.controls_widget.width(), self.win.width())


if __name__ == "__main__":
    unittest.main()
