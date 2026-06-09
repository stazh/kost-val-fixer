import os
import time
import shutil
import win32api
import pyautogui

from services.xml.logging import info, warning, error, success
from services.repair.pdf.convert import convert

import config

def createPDF(file_path: str) -> bool:
    """
    Druckt eine bestehende PDF neu über Microsoft Print to PDF,
    automatisiert den Speichern-Dialog mit pyautogui und ersetzt die Originaldatei.
    """
    try:
        file_name = os.path.basename(file_path)
        printed_file_path = os.path.join(config.TEMP_OUTPUT_FOLDER, file_name)

        # Temporären Ordner sicherstellen
        os.makedirs(config.TEMP_OUTPUT_FOLDER, exist_ok=True)

        printer_name = config.PRINTER_PDF

        info(f"Starte Druck von: {file_path} über {printer_name}")

        # Druck starten (öffnet den Speichern-unter-Dialog)
        win32api.ShellExecute(
            0,
            "printto",
            file_path,
            f'"{printer_name}"',
            ".",
            0
        )

        # Kurze Wartezeit, bis der Dialog erscheint
        time.sleep(2)

        # Pfad für die neue PDF automatisch eintippen
        pyautogui.write(printed_file_path)
        pyautogui.press("enter")

        # Warten, bis die PDF erstellt wurde
        for _ in range(20):
            if os.path.exists(printed_file_path):
                break
            time.sleep(1)
        else:
            warning(f"PDF-Ausgabe nicht erstellt: {printed_file_path}")
            return False

        # Originaldatei ersetzen
        shutil.move(printed_file_path, file_path)
        success(f"PDF zurückverschoben: {file_name}")
        return convert(file_path)

    except Exception as e:
        error(f"Fehler beim Drucken von {file_path}: {e}")
        return False