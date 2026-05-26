import subprocess
import config

from services.xml.logging import add_log

def validate_files(invalid_validations: list):
    """
    Führt den Validator-Command für alle Dateien in invalid_validations aus
    und sammelt die Ausgabe in der zentralen Log-Liste.
    """
    try:
        for error in invalid_validations:
            file_path = str(error["filePath"])
            add_log(f"Starte Validierung für Datei: {file_path}")

            try:
                command = config.VALIDATE_FORMAT.replace("Pfad", file_path)
                add_log(f"Führe Validator aus: {command}")

                result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=config.VALIDATOR_PATH)

                if result.stdout:
                    add_log(f"Validator Ausgabe ({file_path}): {result.stdout.strip()}")
                if result.stderr:
                    add_log(f"Validator Fehler ({file_path}): {result.stderr.strip()}")

            except Exception as e:
                add_log(f"Fehler beim Validator-Aufruf für {file_path}: {e}")

    except Exception as e:
        add_log(f"Fehler beim Validieren der Dateien: {e}")