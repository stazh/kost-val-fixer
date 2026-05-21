import config
import os
import shutil
import time

from services.logStorage import add_log


def convert(file_path: str) -> bool:
    """Konvertiert die PDF-Datei in ein unterstütztes Format, um den Fehler zu beheben."""
    try:
        input_folder = config.INPUT_FOLDER_PATH
        output_folder = config.OUTPUT_FOLDER_PATH
        file_name = os.path.basename(file_path)
        input_path = os.path.join(input_folder, file_name)
        output_path = os.path.join(output_folder, file_name)

        # Input-Ordner erstellen, falls nicht vorhanden
        os.makedirs(input_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)

        # Datei kopieren in Input-Ordner
        shutil.copy(file_path, input_path)
        add_log(f"PDF zur Konvertierung vorbereitet: {input_path}")

        # Output-Ordner überwachen (max 10 Sekunden)
        found = False
        for _ in range(10):
            if os.path.exists(output_path):
                found = True
                break
            time.sleep(1)

        if not found:
            add_log(f"Die Datei konnte nicht konvertiert werden, Output nicht gefunden: {output_path}")
            return False

        # Konvertierte Datei zurück an Originalpfad verschieben
        shutil.move(output_path, file_path)
        add_log(f"PDF konvertiert und Original ersetzt: {file_path}")
        return True

    except Exception as e:
        add_log(f"Fehler beim Konvertieren der Datei {file_path}: {e}")
        return False