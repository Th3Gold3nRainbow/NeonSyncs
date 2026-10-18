import os
import sys
import json
import shutil
import tempfile
import unittest

# Ensure repo root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import i18n


class TestInstallerLanguage(unittest.TestCase):
    def setUp(self):
        # Create an isolated temporary directory for both APPDATA and app base dir
        self.test_dir = tempfile.mkdtemp(prefix="neonsyncs_test_")
        self.temp_appdata = os.path.join(self.test_dir, "appdata")
        self.temp_base = os.path.join(self.test_dir, "appbase")
        os.makedirs(self.temp_appdata, exist_ok=True)
        os.makedirs(self.temp_base, exist_ok=True)

        # Override APPDATA environment variable
        self._orig_appdata = os.environ.get("APPDATA")
        os.environ["APPDATA"] = self.temp_appdata

        # Override i18n._base_dir to point to temp_base
        self._orig_base_dir = i18n._base_dir
        i18n._base_dir = lambda: self.temp_base

    def tearDown(self):
        # Restore environment and base_dir
        if self._orig_appdata is not None:
            os.environ["APPDATA"] = self._orig_appdata
        else:
            os.environ.pop("APPDATA", None)
        i18n._base_dir = self._orig_base_dir

        # Cleanup temp directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def write_lang_txt(self, content: str):
        path = os.path.join(self.temp_base, "lang.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def write_settings(self, data: dict):
        sdir = os.path.join(self.temp_appdata, "NeonSyncs")
        os.makedirs(sdir, exist_ok=True)
        with open(os.path.join(sdir, "settings.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def read_settings(self) -> dict:
        path = os.path.join(self.temp_appdata, "NeonSyncs", "settings.json")
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # 1. Pas de settings.json, lang.txt anglais avec jeton : anglais
    def test_no_settings_english_with_token(self):
        self.write_lang_txt("en\n20261018120000_12345\n")
        lang = i18n.detect_language()
        self.assertEqual(lang, "en")
        settings = self.read_settings()
        self.assertEqual(settings.get("last_installer_lang"), "en")
        self.assertEqual(settings.get("last_installer_token"), "20261018120000_12345")
        self.assertNotIn("language", settings)

    # 2. Choix manuel arabe, meme jeton que lors du dernier lancement : arabe conserve
    def test_manual_arabic_same_token_preserved(self):
        self.write_lang_txt("en\n20261018120000_12345\n")
        self.write_settings({
            "language": "ar",
            "last_installer_lang": "en",
            "last_installer_token": "20261018120000_12345",
            "volume": 85,
            "muted": False,
        })
        lang = i18n.detect_language()
        self.assertEqual(lang, "ar")
        settings = self.read_settings()
        self.assertEqual(settings.get("language"), "ar")
        self.assertEqual(settings.get("volume"), 85)
        self.assertFalse(settings.get("muted"))

    # 3. Choix manuel arabe, lang.txt anglais avec nouveau jeton, meme langue qu'avant (le symptome):
    # anglais, choix manuel efface, jeton enregistre
    def test_symptom_manual_arabic_new_token_english_wins(self):
        self.write_lang_txt("en\n20261018130000_67890\n")
        self.write_settings({
            "language": "ar",
            "last_installer_lang": "en",
            "last_installer_token": "20261018120000_12345",
            "volume": 85,
            "muted": False,
        })
        lang = i18n.detect_language()
        self.assertEqual(lang, "en")
        settings = self.read_settings()
        self.assertNotIn("language", settings)
        self.assertEqual(settings.get("last_installer_lang"), "en")
        self.assertEqual(settings.get("last_installer_token"), "20261018130000_67890")
        self.assertEqual(settings.get("volume"), 85)
        self.assertFalse(settings.get("muted"))

    # 4. Meme scenario avec les 4 langues installees
    def test_all_four_languages_installer_override(self):
        for code in ["en", "fr", "ru", "ar"]:
            prev_manual = "ru" if code != "ru" else "en"
            old_token = f"token_old_{code}"
            new_token = f"token_new_{code}"

            self.write_lang_txt(f"{code}\n{new_token}\n")
            self.write_settings({
                "language": prev_manual,
                "last_installer_lang": code,
                "last_installer_token": old_token,
                "volume": 70,
            })

            lang = i18n.detect_language()
            self.assertEqual(lang, code, f"Expected {code} when installer was re-run in {code}")
            settings = self.read_settings()
            self.assertNotIn("language", settings)
            self.assertEqual(settings.get("last_installer_lang"), code)
            self.assertEqual(settings.get("last_installer_token"), new_token)
            self.assertEqual(settings.get("volume"), 70)

    # Noms complets avec jeton (ex. french\ntoken)
    def test_full_language_names_with_token(self):
        self.write_lang_txt("french\ntoken_french_1\n")
        lang = i18n.detect_language()
        self.assertEqual(lang, "fr")
        settings = self.read_settings()
        self.assertEqual(settings.get("last_installer_lang"), "fr")
        self.assertEqual(settings.get("last_installer_token"), "token_french_1")

    # 5. lang.txt ancien sans jeton avec choix manuel : comportement inchange
    def test_legacy_lang_txt_without_token(self):
        # Case A: meme langue installateur, choix manuel conserve
        self.write_lang_txt("en\n")
        self.write_settings({
            "language": "ar",
            "last_installer_lang": "en",
        })
        lang = i18n.detect_language()
        self.assertEqual(lang, "ar")

        # Case B: reinstallation dans une autre langue sans jeton : l'installateur l'emporte
        self.write_lang_txt("fr\n")
        self.write_settings({
            "language": "ar",
            "last_installer_lang": "en",
        })
        lang = i18n.detect_language()
        self.assertEqual(lang, "fr")
        settings = self.read_settings()
        self.assertNotIn("language", settings)
        self.assertEqual(settings.get("last_installer_lang"), "fr")

    # 6. lang.txt illisible ou settings.json corrompu : repli sans erreur
    def test_corrupted_settings_json(self):
        self.write_lang_txt("en\ntoken_123\n")
        sdir = os.path.join(self.temp_appdata, "NeonSyncs")
        os.makedirs(sdir, exist_ok=True)
        with open(os.path.join(sdir, "settings.json"), "w", encoding="utf-8") as f:
            f.write("{corrupted json not valid...")

        lang = i18n.detect_language()
        self.assertEqual(lang, "en")

    def test_unreadable_or_missing_lang_txt(self):
        # Pas de lang.txt -> choix manuel respecte
        self.write_settings({"language": "fr"})
        lang = i18n.detect_language()
        self.assertEqual(lang, "fr")

    def test_unreadable_lang_txt_no_settings_falls_back(self):
        # lang.txt avec contenu invalide -> repli sur langue valide sans erreur
        path = os.path.join(self.temp_base, "lang.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("unknown_random_garbage\n")
        lang = i18n.detect_language()
        self.assertIn(lang, i18n.SUPPORTED_LANGUAGES)


if __name__ == "__main__":
    unittest.main()
