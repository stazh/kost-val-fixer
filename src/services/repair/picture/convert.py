import os
import subprocess

import config

from services.xml.logging import (
    info,
    warning,
    error,
    success
)


def convert(file_path: str) -> bool:
    """
    Konvertiert Bilder mit IrfanView.

    Unterstützt:
    - GIF -> PNG
    - andere Formate behalten ihre Endung

    Die Originaldatei wird ersetzt.
    """

    try:
        irfanview_path = config.IRFANVIEW_PATH

        if not os.path.isfile(irfanview_path):

            error(f"IrfanView nicht gefunden: {irfanview_path}")
            return False

        folder = os.path.dirname(file_path)

        file_name = os.path.basename(file_path)

        base_name, extension = os.path.splitext(
            file_name
        )

        extension = extension.lower()

        # GIF -> PNG
        output_extension = (
            ".png"
            if extension == ".gif"
            else extension
        )

        temp_output_path = os.path.join(
            folder,
            f"temp_{base_name}{output_extension}"
        )

        final_output_path = os.path.join(
            folder,
            f"{base_name}{output_extension}"
        )

        info(f"Starte Bild-Konvertierung: {file_name}")

        command = [
            irfanview_path,
            file_path,
            f'/convert={temp_output_path}',
            '/silent'
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            error(f"IrfanView Fehler bei {file_name} | Code: {result.returncode} | STDERR: {result.stderr.strip()}")

            return False

        if not os.path.exists(temp_output_path):

            warning(
                f"Konvertierte Datei fehlt: "
                f"{temp_output_path}"
            )

            return False

        # Original löschen
        if os.path.exists(file_path):
            os.remove(file_path)

        # temp -> final
        os.replace(
            temp_output_path,
            final_output_path
        )

        success(f"Bild erfolgreich konvertiert: {os.path.basename(final_output_path)}")
        return True

    except Exception as e:
        error(f"Fehler bei Bild-Konvertierung von {file_path}: {e}")
        return False