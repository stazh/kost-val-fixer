import config
import os
import shutil
import time
import win32print
import win32ui

from services.xml.logging import add_log
from services.repair.pdf.convert import convert

def createPDF(file_path: str) -> bool:
    """Druckt die PDF-Datei über Microsoft Print to PDF und ruft danach convert auf."""
    try:
        temp_output_folder = config.TEMP_OUTPUT_FOLDER
        os.makedirs(temp_output_folder, exist_ok=True)

        file_name = os.path.basename(file_path)
        printed_file_path = os.path.join(temp_output_folder, file_name)

        printer_name = config.PRINTER_PDF

        # Printer DC vorbereiten
        hprinter = win32print.OpenPrinter(printer_name)
        printer_info = win32print.GetPrinter(hprinter, 2)
        devmode = printer_info["pDevMode"]

        # Ausgabe-Dateipfad setzen
        devmode.PrintFileName = printed_file_path
        devmode.Fields |= win32print.DM_PRINTFILE
        win32print.SetPrinter(hprinter, 2, printer_info, 0)
        win32print.ClosePrinter(hprinter)

        # PDF drucken
        pdf_dc = win32ui.CreateDC()
        pdf_dc.CreatePrinterDC(printer_name)
        pdf_dc.StartDoc({'DocName': file_name})
        pdf_dc.StartPage()
        pdf_dc.EndPage()
        pdf_dc.EndDoc()
        pdf_dc.DeleteDC()

        add_log(f"PDF über Microsoft Print to PDF gedruckt: {file_path}")

        # Kurze Pause, damit die Datei geschrieben wird
        for _ in range(5):
            if os.path.exists(printed_file_path):
                break
            time.sleep(1)
        else:
            add_log(f"Fehler: Die gedruckte Datei wurde nicht erstellt: {printed_file_path}")
            return False

        # Datei zurück an Originalpfad verschieben
        shutil.move(printed_file_path, file_path)
        add_log(f"Gedruckte PDF zurückverschoben: {file_path}")

        # Danach Konvertierung durchführen
        convert(file_path)

        return True

    except Exception as e:
        add_log(f"Fehler beim Drucken der Datei {file_path}: {e}")
        return False
