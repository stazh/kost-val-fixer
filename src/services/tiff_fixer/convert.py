
import config
import os
import subprocess

from services.logStorage import add_log


def convert(file_path: str) -> bool:
    """
    Konvertiert die TIF-Datei mit IrfanView und ersetzt die Originaldatei.
    """
    try:
        irfanview_path = config.IRFANVIEW_PATH
        if not os.path.exists(irfanview_path):
            add_log(f"Fehler: IrfanView nicht gefunden unter {irfanview_path}")
            return False

        folder = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        base_name, ext = os.path.splitext(file_name)
        temp_file_path = os.path.join(folder, f"temp_{base_name}.tif")

        # Kommando als einzelner String, Pfade gequotet
        cmd = f'"{irfanview_path}" "{file_path}" /convert="{temp_file_path}" /silent'
        add_log(f"Starte TIF-Konvertierung: {cmd}")

        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            add_log(f"Fehler: IrfanView beendet mit Code {result.returncode} für Datei {file_path}")
            return False

        # Originaldatei ersetzen
        if os.path.exists(temp_file_path):
            os.replace(temp_file_path, file_path)
            add_log(f"TIF konvertiert und Original ersetzt: {file_path}")
            return True
        else:
            add_log(f"Fehler: Konvertierte Datei nicht gefunden: {temp_file_path}")
            return False

    except Exception as e:
        add_log(f"Fehler beim Konvertieren der Datei {file_path}: {e}")
        return False