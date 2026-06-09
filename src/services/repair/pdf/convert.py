import os
import shutil
import time

import config
from services.xml.logging import info, warning, error, success

def convert(file_path: str) -> bool:
    try:
        input_folder = config.INPUT_FOLDER_PATH
        output_folder = config.OUTPUT_FOLDER_PATH

        file_name = os.path.basename(file_path)
        base_name = os.path.splitext(file_name)[0]

        input_path = os.path.join(input_folder, file_name)
        output_path = os.path.join(output_folder, f"{base_name}.pdf")
        target_path = os.path.splitext(file_path)[0] + ".pdf"

        os.makedirs(input_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)

        shutil.copy(file_path, input_path)
        info(f"Datei zur Konvertierung vorbereitet: {input_path}")

        timeout_seconds = 25

        for _ in range(timeout_seconds):
            if os.path.exists(output_path):
                # Verschieben der konvertierten Datei
                shutil.move(output_path, target_path)
                success(f"{file_name} erfolgreich konvertiert: {target_path}")

                # Alte temporäre Dateien löschen
                if os.path.exists(input_path):
                    os.remove(input_path)
                    info(f"Temporäre Eingabedatei gelöscht: {input_path}")
                if os.path.exists(output_path):
                    os.remove(output_path)
                    info(f"Temporäre Ausgabedatei gelöscht: {output_path}")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    info(f"Originale Datei gelöscht: {file_path}")

                return True
            time.sleep(1)

        warning(f"Keine konvertierte Datei gefunden: {output_path}")
        return False

    except Exception as e:
        error(f"Fehler beim Konvertieren von {file_path}: {e}")
        return False