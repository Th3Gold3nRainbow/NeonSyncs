#!/usr/bin/env python3
"""
NeonSyncs i18n module
=====================
Internationalization engine supporting English, French, Russian, and Arabic.
Provides fallback to English for missing keys and missing-key logging.
"""
import os
import sys
import json
import logging
from typing import Dict, Any

log = logging.getLogger("neonsyncs.i18n")

SUPPORTED_LANGUAGES = ("en", "fr", "ru", "ar")
DEFAULT_LANGUAGE = "en"

# Cache of loaded translations
_CATALOGS: Dict[str, Dict[str, str]] = {}
_CURRENT_LANGUAGE = DEFAULT_LANGUAGE


def _base_dir() -> str:
    """Returns directory containing executable or script."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def _resource_path(rel_path: str) -> str:
    """Resolves resource path across frozen onefile and source execution."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_path)


def load_catalogs():
    """Loads all translation catalogs from the i18n directory."""
    global _CATALOGS
    for lang in SUPPORTED_LANGUAGES:
        path = _resource_path(os.path.join("i18n", f"{lang}.json"))
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    _CATALOGS[lang] = json.load(f)
            except Exception as e:
                log.error("Failed to load translation file %s: %e", path, e)
                _CATALOGS[lang] = {}
        else:
            log.warning("Translation file not found: %s", path)
            _CATALOGS[lang] = {}


def _detect_system_language() -> str:
    """Detects system language via QLocale if available, otherwise locale module."""
    try:
        from PyQt5.QtCore import QLocale
        name = QLocale.system().name().lower()
        if name.startswith("fr"):
            return "fr"
        if name.startswith("ru"):
            return "ru"
        if name.startswith("ar"):
            return "ar"
        if name.startswith("en"):
            return "en"
    except Exception:
        pass

    try:
        import locale
        loc = (locale.getdefaultlocale()[0] or "").lower()
        if loc.startswith("fr"):
            return "fr"
        if loc.startswith("ru"):
            return "ru"
        if loc.startswith("ar"):
            return "ar"
        if loc.startswith("en"):
            return "en"
    except Exception:
        pass

    return DEFAULT_LANGUAGE


def detect_language() -> str:
    """Reads language chosen at installation from lang.txt, or falls back to system."""
    try:
        lang_file = os.path.join(_base_dir(), "lang.txt")
        if os.path.exists(lang_file):
            with open(lang_file, "r", encoding="utf-8") as f:
                content = f.read().strip().lower()
            if "english" in content or content == "en":
                return "en"
            if "french" in content or content == "fr":
                return "fr"
            if "russian" in content or content == "ru":
                return "ru"
            if "arabic" in content or content == "ar":
                return "ar"
    except Exception as e:
        log.warning("Could not read lang.txt: %s", e)

    return _detect_system_language()


def init_i18n(preferred_lang: str = None) -> str:
    """Initializes the translation catalogs and sets current language."""
    global _CURRENT_LANGUAGE
    load_catalogs()
    lang = preferred_lang or detect_language()
    set_language(lang)
    return _CURRENT_LANGUAGE


def set_language(lang: str):
    """Sets active language if supported."""
    global _CURRENT_LANGUAGE
    if lang in SUPPORTED_LANGUAGES:
        _CURRENT_LANGUAGE = lang
    else:
        log.warning("Unsupported language '%s', defaulting to '%s'", lang, DEFAULT_LANGUAGE)
        _CURRENT_LANGUAGE = DEFAULT_LANGUAGE


def get_language() -> str:
    """Returns current active language code."""
    return _CURRENT_LANGUAGE


def is_rtl() -> bool:
    """Returns True if active language requires Right-To-Left layout."""
    return _CURRENT_LANGUAGE == "ar"


def tr(key: str, **params: Any) -> str:
    """Translates a key into the active language, falling back to English.
    Interpolates format parameters safely.
    """
    catalog = _CATALOGS.get(_CURRENT_LANGUAGE, {})
    text = catalog.get(key)

    if text is None:
        if _CURRENT_LANGUAGE != "en":
            log.warning("Missing translation key '%s' for language '%s', falling back to English", key, _CURRENT_LANGUAGE)
        en_catalog = _CATALOGS.get("en", {})
        text = en_catalog.get(key)

    if text is None:
        log.warning("Unknown translation key '%s'", key)
        text = key

    if params:
        try:
            return text.format(**params)
        except Exception as e:
            log.error("Failed to format key '%s' with params %s: %s", key, params, e)
            return text

    return text


# Initialize on module load
init_i18n()
