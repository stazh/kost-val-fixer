import os
import shutil
import time

import config

from services.xml.logging import (
    info,
    warning,
    error,
    success
)

def convert(file_path: str) -> bool:
    try:
        input_folder = config.INPUT_FOLDER_PATH
        output_folder = config.OUTPUT_FOLDER_PATH

        file_name = os.path.basename(file_path)

        input_path = os.path.join(
            input_folder,
            file_name
        )

        output_path = os.path.join(
            output_folder,
            file_name
        )

        os.makedirs(input_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)
        shutil.copy(file_path, input_path)

        info(f"Datei zur Konvertierung vorbereitet: {input_path}")
        timeout_seconds = 10

        for _ in range(timeout_seconds):
            if os.path.exists(output_path):
                shutil.move(output_path, file_path)
                success(f"{file_name} erfolgreich konvertiert.")
                return True

            time.sleep(1)

        warning(f"Keine konvertierte Datei gefunden: {output_path}")
        return False

    except Exception as e:
        error(f"Fehler beim Konvertieren von {file_path}: {e}")
        return False