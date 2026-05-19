
import config
import os
import subprocess


def repair_tif_file(file_path: str, error_message: str) -> None:
    """Repariert automatisch die TIF-Datei, falls eine bekannte Lösung existiert."""
    try:
        solution = None
        # Alle bekannten TIF-Fehler prüfen
        for error in config.SUPPORTED_TIF_ERRORS:
            if error["MESSAGE"] in error_message:
                solution = error["SOLUTION"]
                break 
        
        solved = False

        if solution == config.CONVERT:
            solved = convert(file_path)
        else:
            print(f"Korrektur erforderlich: Dieser Fehler wird zurzeit nicht unterstützt (TIF):\nDatei: {file_path}\nFehlermeldung: {error_message}")

        if solved:
            print(f"TIF repariert: {file_path}")

    except Exception as e:
        print(f"Fehler: Fehler beim Verarbeiten der Datei: {e}")


def convert(file_path: str) -> bool:
    """Konvertiert die Datei in ein TIF-Format mit IrfanView und ersetzt die Originaldatei."""
    try:
        irfanview_path = config.IRFANVIEW_PATH
        if not os.path.exists(irfanview_path):
            print(f"Fehler: IrfanView nicht gefunden unter {irfanview_path}")
            return False

        # Dateiname und Ordner
        folder = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        base_name, ext = os.path.splitext(file_name)
        temp_file_path = os.path.join(folder, f"temp_{base_name}.tif")

        # Kommando als einzelner String, Pfade gequotet
        cmd = f'"{irfanview_path}" "{file_path}" /convert="{temp_file_path}" /silent'

        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            print(f"Fehler: IrfanView exited mit {result.returncode}")
            return False

        # Originaldatei ersetzen
        if os.path.exists(temp_file_path):
            os.replace(temp_file_path, file_path)
            return True
        else:
            print(f"Fehler: Konvertierte Datei wurde nicht gefunden: {temp_file_path}")
            return False

    except Exception as e:
        print(f"Fehler: Fehler beim Konvertieren der Datei: {e}")
        return False