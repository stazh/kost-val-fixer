
import config
import os
import subprocess

from services.xml.logging import add_log


def convert(file_path: str) -> bool:
    """
    Konvertiert Bilder mit IrfanView.

    - GIF -> PNG
    - andere Formate behalten ihre Endung

    Originaldatei wird gelöscht.
    """
    try:
        irfanview_path = config.IRFANVIEW_PATH

        if not os.path.exists(irfanview_path):
            add_log(f"IrfanView nicht gefunden: {irfanview_path}")
            return False

        folder = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)

        base_name, ext = os.path.splitext(file_name)
        ext = ext.lower()

        # GIF -> PNG
        output_ext = ".png" if ext == ".gif" else ext

        # temporäre Datei
        temp_file_path = os.path.join(
            folder,
            f"temp_{base_name}{output_ext}"
        )

        # finale Datei
        final_output_path = os.path.join(
            folder,
            f"{base_name}{output_ext}"
        )

        cmd = (
            f'"{irfanview_path}" '
            f'"{file_path}" '
            f'/convert="{temp_file_path}" '
            f'/silent'
        )

        add_log(f"Starte Bild-Konvertierung: {cmd}")

        result = subprocess.run(cmd, shell=True)

        if result.returncode != 0:
            add_log(
                f"IrfanView Fehlercode {result.returncode} "
                f"bei Datei {file_path}"
            )
            return False

        if not os.path.exists(temp_file_path):
            add_log(f"Temp-Datei fehlt: {temp_file_path}")
            return False

        # Original löschen
        os.remove(file_path)

        # temp -> finale Datei
        os.replace(temp_file_path, final_output_path)

        add_log(f"Bild erfolgreich konvertiert: {final_output_path}")

        return True

    except Exception as e:
        add_log(f"Fehler beim Konvertieren der Datei {file_path}: {e}")
        return False