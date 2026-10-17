# Localization and Language Priority

NeonSyncs is fully internationalized across **4 languages**:
- **English** (`en`)
- **Français** (`fr`)
- **Русский** (`ru`)
- **العربية** (`ar`, with native Right-To-Left layout and proper bidirectional Unicode isolation)

## Language Selection & Priority Order

1. **In-App Hot Switching**: Users can change language on the fly via the dropdown in the application header. The entire UI updates dynamically without restarting or interrupting active P2P watchparties.
2. **Persistent Settings**: User choices are saved in `%APPDATA%\NeonSyncs\settings.json`.
3. **Installer Language**: Selected during setup and written to `{app}\lang.txt` (read-only for the application; the app never modifies it).
4. **Startup Priority**:
   - **a.** Manual user selection in `settings.json`, unless the installer was re-run since;
   - **b.** Installer language from `lang.txt` (if the installer was re-run with another language, it takes precedence and resets manual choice);
   - **c.** Operating system locale (`QLocale.system()`);
   - **d.** Fallback to English (`en`).
5. **Uninstaller Cleanup**: During uninstall, the user is prompted whether to remove user settings in `%APPDATA%\NeonSyncs`.

## Translation Validation

Before building, verify all translation catalogs and UI strings with the i18n validator:

```bash
python tools/check_i18n.py
```

For detailed linguistic review notes on Russian and Arabic translations, see [docs/translation-review.md](translation-review.md).

