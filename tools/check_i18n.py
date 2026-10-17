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
        "RIGHT", "LEFT", "UP", "DOWN", "neonsyncs.watchparty.client"
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


def main():
    print("=" * 60)
    print("NeonSyncs Internationalization (i18n) Linter")
    print("=" * 60)

    cat_errors, catalogs = check_catalogs()
    code_errors = check_hardcoded_strings()

    all_errors = cat_errors + code_errors

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
    sys.exit(0)


if __name__ == "__main__":
    main()
