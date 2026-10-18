#!/usr/bin/env python3
"""
tools/check_i18n.py
===================
Linter for NeonSyncs internationalization (i18n).
Fails (exit code 1) if:
  1. A key is missing in any language (EN, FR, RU, AR).
  2. A language has unexpected extra keys.
  3. Any translation value is empty.
  4. Format placeholders ({id}, {message}, etc.) differ across languages.
  5. User-visible hardcoded strings remain in client.py widget calls.
"""
import sys
import os
import re
import json
import ast

SUPPORTED_LANGS = ("en", "fr", "ru", "ar")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N_DIR = os.path.join(BASE_DIR, "i18n")


def extract_format_params(s: str) -> set:
    """Finds all {param} tokens in a string."""
    return set(re.findall(r"\{([a-zA-Z0-9_]+)\}", s))


def check_catalogs():
    errors = []
    catalogs = {}

    for lang in SUPPORTED_LANGS:
        file_path = os.path.join(I18N_DIR, f"{lang}.json")
        if not os.path.isfile(file_path):
            errors.append(f"Missing translation file: {file_path}")
            continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                catalogs[lang] = json.load(f)
        except Exception as e:
            errors.append(f"Error parsing JSON in {file_path}: {e}")

    if errors:
        return errors, catalogs

    en_keys = set(catalogs["en"].keys())

    # 1. Check for missing/extra keys & empty values
    for lang in SUPPORTED_LANGS:
        lang_keys = set(catalogs[lang].keys())

        missing = en_keys - lang_keys
        if missing:
            errors.append(f"[{lang}] Missing {len(missing)} key(s): {sorted(missing)}")

        extra = lang_keys - en_keys
        if extra:
            errors.append(f"[{lang}] Extra {len(extra)} key(s) not in en.json: {sorted(extra)}")

        for key, val in catalogs[lang].items():
            if not isinstance(val, str) or not val.strip():
                errors.append(f"[{lang}] Empty or non-string value for key: '{key}'")

    # 2. Check format parameter consistency across languages
    for key in sorted(en_keys):
        expected_params = extract_format_params(catalogs["en"].get(key, ""))
        for lang in ("fr", "ru", "ar"):
            if key in catalogs.get(lang, {}):
                lang_params = extract_format_params(catalogs[lang][key])
                if lang_params != expected_params:
                    errors.append(
                        f"Format parameter mismatch for '{key}': "
                        f"EN has {expected_params}, but {lang} has {lang_params}"
                    )

    return errors, catalogs


def check_hardcoded_strings():
    errors = []
    client_path = os.path.join(BASE_DIR, "client.py")
    if not os.path.isfile(client_path):
        return [f"client.py not found at {client_path}"]

    with open(client_path, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.splitlines()

    target_functions = {
        "QLabel", "QPushButton", "setText", "setPlaceholderText",
        "setWindowTitle", "addItem", "addItems", "getOpenFileName",
        "setToolTip"
    }

    # Legitimate non-translatable tokens/patterns
    allowed_literals = {
        "", " ", ":", "-", "127.0.0.1", "8999", "videoFrame", "controlsBar",
        "timeLabel", "panel", "brand", "section", "primary", "pink", "small",
        "danger", "website_link", "status", "connected", "reconnecting",
        "disconnected", "error", "SPACE", "F11", "ESC", "MBTN_LEFT_DBL",
        "RIGHT", "LEFT", "UP", "DOWN", "neonsyncs.watchparty.client",
        "English", "Français", "Русский", "العربية", "en", "fr", "ru", "ar",
        "langSelector"
    }

    try:
        tree = ast.parse(content, filename=client_path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn_name = ""
                if isinstance(node.func, ast.Name):
                    fn_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    fn_name = node.func.attr

                if fn_name in target_functions:
                    for i, arg in enumerate(node.args):
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            val = arg.value.strip()
                            # Allow safe tokens or rich-text brand header
                            if val in allowed_literals:
                                continue
                            if val.startswith("<span") or val.startswith("<a href="):
                                continue
                            # If it looks like natural human language, flag it
                            if re.search(r"[a-zA-Z\u00C0-\u017F]{2,}", val):
                                line_no = node.lineno
                                line_str = lines[line_no - 1].strip() if line_no <= len(lines) else ""
                                errors.append(
                                    f"Hardcoded string in {fn_name}() at client.py:{line_no}: "
                                    f"'{val}' | Line: {line_str}"
                                )
    except Exception as e:
        errors.append(f"AST parse error in client.py: {e}")

    return errors


def check_retranslate_ui():
    """Verifies that NeonSyncsWindow defines retranslate_ui and covers all visible widgets."""
    errors = []
    client_path = os.path.join(BASE_DIR, "client.py")
    if not os.path.isfile(client_path):
        return [f"client.py not found at {client_path}"]

    with open(client_path, "r", encoding="utf-8") as f:
        content = f.read()

    required_retranslate_targets = [
        "setWindowTitle", "btn_open", "btn_back30", "btn_back10", "btn_play",
        "btn_fwd10", "btn_fwd30", "btn_fullscreen", "lbl_conn", "combo_mode",
        "lbl_user", "lbl_password", "input_password", "input_user", "btn_create_room",
        "lbl_room_id", "input_room_id", "btn_join_room", "btn_copy_id",
        "btn_leave_p2p", "btn_retry_p2p", "lbl_host", "lbl_port", "lbl_room", "input_room",
        "btn_connect", "status_label", "lbl_users", "lbl_chat", "chat_input",
        "btn_send", "refresh_chat_display"
    ]

    try:
        tree = ast.parse(content, filename=client_path)
        found_method = False
        retranslate_body = ""

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "retranslate_ui":
                found_method = True
                # Extract text for the function body
                lines = content.splitlines()
                retranslate_body = "\n".join(lines[node.lineno - 1:node.end_lineno])
                break

        if not found_method:
            errors.append("retranslate_ui() method is missing from client.py")
            return errors

        for target in required_retranslate_targets:
            if target not in retranslate_body:
                errors.append(f"retranslate_ui() does not update required target: '{target}'")
    except Exception as e:
        errors.append(f"Error parsing client.py for retranslate_ui check: {e}")

    return errors


def check_hot_language_switch(catalogs):
    """For each pair of languages (A -> B, 12 transitions), switches from A to B
    and verifies that no UI string unique to A remains visible in the interface
    (excluding brand names like NeonSyncs and URLs).
    Also checks default input values (username, room name, status, placeholders)
    and verifies that manual user edits are not overwritten upon language switch.
    """
    errors = []
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)

    try:
        import client
        from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QLineEdit, QComboBox
        from i18n import SUPPORTED_LANGUAGES, set_language, tr
    except Exception as e:
        return [f"Unable to import client or PyQt5 for hot switch test: {e}"]

    try:
        app = QApplication.instance() or QApplication([sys.argv[0]])
        win = client.NeonSyncsWindow()
    except Exception as e:
        return [f"Failed to instantiate NeonSyncsWindow: {e}"]

    # Proper names, invariant technical strings, and media symbols
    allowed_invariants = {
        "NeonSyncs", "neonsyncs.com", "https://neonsyncs.com",
        "127.0.0.1", "8999", "0:00",
        "10s ⏩", "30s ⏩", "⏪ 10s", "⏪ 30s",
        "English", "Français", "Русский", "العربية",
        "EN ▾", "FR ▾", "RU ▾", "AR ▾", "▾ AR"
    }

    def collect_ui_texts(window):
        items = {}
        if window.windowTitle():
            items["windowTitle"] = window.windowTitle()
        for idx, child in enumerate(window.findChildren(QLabel)):
            txt = child.text()
            if txt:
                items[f"QLabel_{child.objectName() or idx}"] = txt
        for idx, child in enumerate(window.findChildren(QPushButton)):
            txt = child.text()
            if txt:
                items[f"QPushButton_{child.objectName() or idx}"] = txt
        for idx, child in enumerate(window.findChildren(QLineEdit)):
            txt = child.text()
            if txt:
                items[f"QLineEdit_text_{child.objectName() or idx}"] = txt
            ph = child.placeholderText()
            if ph:
                items[f"QLineEdit_ph_{child.objectName() or idx}"] = ph
        for idx, child in enumerate(window.findChildren(QComboBox)):
            if child is not getattr(window, "combo_lang", None):
                for i in range(child.count()):
                    items[f"QComboBox_{child.objectName() or idx}_{i}"] = child.itemText(i)
        return items

    # 1. Test all 12 pairwise transitions
    for lang_a in SUPPORTED_LANGS:
        for lang_b in SUPPORTED_LANGS:
            if lang_a == lang_b:
                continue

            # Start in language A
            set_language(lang_a)
            win.retranslate_ui()

            # Switch hot to language B
            set_language(lang_b)
            win.retranslate_ui()

            # Check default username
            expected_user = tr("default_username", id=win._default_suffix)
            if win.input_user.text() != expected_user:
                errors.append(
                    f"[{lang_a} -> {lang_b}] input_user has '{win.input_user.text()}', expected '{expected_user}'"
                )

            # Check default room name
            expected_room = tr("default_room_name", id=win._default_room_suffix)
            if win.input_room.text() != expected_room:
                errors.append(
                    f"[{lang_a} -> {lang_b}] input_room has '{win.input_room.text()}', expected '{expected_room}'"
                )

            # Check default status
            expected_status = tr("status_disconnected")
            if win.status_label.text() != expected_status:
                errors.append(
                    f"[{lang_a} -> {lang_b}] status_label has '{win.status_label.text()}', expected '{expected_status}'"
                )

            # Collect all UI texts in language B
            ui_items = collect_ui_texts(win)

            # Verify no string unique to language A remains
            for widget_id, val in ui_items.items():
                if val in allowed_invariants or val.startswith("<span") or val.startswith("<a href="):
                    continue

                for k, t_a in catalogs.get(lang_a, {}).items():
                    t_b = catalogs.get(lang_b, {}).get(k, "")
                    if t_a != t_b:
                        if "{" in t_a:
                            prefix_a = t_a.split("{")[0]
                            prefix_b = t_b.split("{")[0]
                            if prefix_a and len(prefix_a) >= 3 and prefix_a in val and prefix_a != prefix_b:
                                errors.append(
                                    f"[{lang_a} -> {lang_b}] {widget_id} contains old language {lang_a} "
                                    f"prefix '{prefix_a}' from key '{k}': '{val}'"
                                )
                        else:
                            if val == t_a and t_a not in allowed_invariants:
                                errors.append(
                                    f"[{lang_a} -> {lang_b}] {widget_id} displays untranslated text from {lang_a} "
                                    f"for key '{k}': '{val}' (should be '{t_b}')"
                                )

    # 2. Test manual typing and clearing behavior
    win.input_user.setText("CustomPlayer42")
    win._on_user_text_edited("CustomPlayer42")
    if win._username_is_default:
        errors.append("Flag _username_is_default should be False after user edits text")

    set_language("fr")
    win.retranslate_ui()
    if win.input_user.text() != "CustomPlayer42":
        errors.append(f"Custom username was overwritten on language switch: '{win.input_user.text()}'")

    win.input_user.setText("")
    win._on_user_text_edited("")
    if not win._username_is_default:
        errors.append("Flag _username_is_default should be True after clearing field")
    expected_default_fr = tr("default_username", id=win._default_suffix)
    if win.input_user.text() != expected_default_fr:
        errors.append(f"Cleared username did not regenerate default: '{win.input_user.text()}' (expected '{expected_default_fr}')")

    set_language("ru")
    win.retranslate_ui()
    expected_default_ru = tr("default_username", id=win._default_suffix)
    if win.input_user.text() != expected_default_ru:
        errors.append(f"Regenerated username was not translated to Russian: '{win.input_user.text()}'")

    # 3. Test dynamic error status translation
    win.set_status("status_error", state="error", message="error_room_id_required")
    set_language("en")
    win.retranslate_ui()
    if "Room ID is required" not in win.status_label.text():
        errors.append(f"Error status was not retranslated to English: '{win.status_label.text()}'")

    set_language("fr")
    win.retranslate_ui()
    if "requis" not in win.status_label.text():
        errors.append(f"Error status was not retranslated to French: '{win.status_label.text()}'")

    return errors


def main():
    print("=" * 60)
    print("NeonSyncs Internationalization (i18n) Linter")
    print("=" * 60)

    cat_errors, catalogs = check_catalogs()
    code_errors = check_hardcoded_strings()
    retranslate_errors = check_retranslate_ui()
    hot_switch_errors = check_hot_language_switch(catalogs)

    all_errors = cat_errors + code_errors + retranslate_errors + hot_switch_errors

    if all_errors:
        print(f"\nFAILED: Found {len(all_errors)} i18n issue(s):\n")
        for err in all_errors:
            print(f"  [ERROR] {err}")
        print("\nPlease fix the issues above.")
        sys.exit(1)

    print("\nSUCCESS: All catalogs and source files passed i18n checks!")
    for lang in SUPPORTED_LANGS:
        print(f"  - [{lang}] {len(catalogs.get(lang, {}))} keys verified")
    print("  - client.py: No hardcoded user-visible UI strings detected.")
    print("  - client.py: retranslate_ui() verified (all visible UI widgets covered).")
    print("  - client.py: Hot language switching tested across all 12 language pairs (EN, FR, RU, AR).")
    print("  - client.py: Default username & room name retranslation and user edit persistence verified.")
    print("  - client.py: Dynamic status bar retranslation verified.")
    sys.exit(0)


if __name__ == "__main__":
    main()
