import os
from tkinter import filedialog, Tk

import config
from services.xml.logging import info, warning, error, success, save_logs


def replace_umlauts(name: str) -> str:
    """Ersetzt Umlaute im Namen anhand config.UMLAUT_MAP."""
    for umlaut, replacement in config.UMLAUT_MAP.items():
        name = name.replace(umlaut, replacement)
    return name


def rename_recursive(folder: str) -> bool:
    """
    Benennt rekursiv alle Dateien und Ordner um:
    ä -> ae, ö -> oe, ü -> ue usw.
    """

    if not folder or not os.path.isdir(folder):
        warning("Kein gültiger Ordner angegeben.")
        return False

    info(f"Starte Umlaut-Rename für: {folder}")

    try:
        # bottom-up ist wichtig, sonst kollidieren Ordnernamen beim Rename
        for current_root, dirs, files in os.walk(folder, topdown=False):

            # Dateien zuerst
            for file_name in files:
                old_path = os.path.join(current_root, file_name)
                new_name = replace_umlauts(file_name)
                new_path = os.path.join(current_root, new_name)

                if old_path != new_path:
                    if os.path.exists(new_path):
                        warning(f"Ziel existiert bereits, überspringe: {new_path}")
                        continue

                    os.rename(old_path, new_path)
                    info(f"Datei umbenannt: {old_path} -> {new_path}")

            # danach Ordner
            for dir_name in dirs:
                old_path = os.path.join(current_root, dir_name)
                new_name = replace_umlauts(dir_name)
                new_path = os.path.join(current_root, new_name)

                if old_path != new_path:
                    if os.path.exists(new_path):
                        warning(f"Ziel existiert bereits, überspringe: {new_path}")
                        continue

                    os.rename(old_path, new_path)
                    info(f"Ordner umbenannt: {old_path} -> {new_path}")

        success("Umlaut-Rename abgeschlossen.")
        save_logs(False)
        return True

    except Exception as e:
        error(f"Fehler beim Umlaut-Rename: {e}")
        save_logs(False)
        return False


def select_and_run_rename() -> bool:
    """
    Öffnet Dialog und startet Rename.
    """
    root = Tk()
    root.withdraw()

    folder = filedialog.askdirectory(title="Ordner auswählen")

    if not folder:
        warning("Kein Ordner ausgewählt.")
        return False

    return rename_recursive(folder)