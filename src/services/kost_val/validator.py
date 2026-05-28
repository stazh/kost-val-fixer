import subprocess
import config

from services.xml.logging import info, warning, error, success


def validate_files(invalid_validations: list):
    """
    Führt den Validator-Command für alle Dateien in invalid_validations aus
    und protokolliert die Ergebnisse sauber.
    """
    try:
        for error_entry in invalid_validations:
            file_path = str(error_entry["filePath"])
            info(f"Starte Validierung für Datei: {file_path}")

            try:
                command = config.VALIDATE_FORMAT.replace("Pfad", file_path)
                info(f"Führe Validator aus: {command}")

                # subprocess ohne shell=True für Sicherheit, split cmd falls nötig
                result = subprocess.run(
                    command,
                    shell=True,  # Kann bleiben, falls VALIDATE_FORMAT ein String ist
                    capture_output=True,
                    text=True,
                    cwd=config.VALIDATOR_PATH
                )

                # Prüfe stdout und stderr
                if result.stdout and result.stdout.strip():
                    info(f"Validator Ausgabe ({file_path}): {result.stdout.strip()}")

                if result.stderr and result.stderr.strip():
                    warning(f"Validator Fehler ({file_path}): {result.stderr.strip()}")

                if result.returncode == 0:
                    success(f"Validierung erfolgreich: {file_path}")
                else:
                    error(f"Validator beendet mit Fehlercode {result.returncode}: {file_path}")

            except Exception as ex:
                error(f"Fehler beim Validator-Aufruf für {file_path}: {ex}")

    except Exception as e:
        error(f"Fehler beim Validieren der Dateien: {e}")