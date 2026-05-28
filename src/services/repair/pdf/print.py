import os
import shutil
import time

import win32print
import win32ui

import config

from services.repair.pdf.convert import convert

from services.xml.logging import (
    info,
    warning,
    error,
    success
)


def createPDF(file_path: str) -> bool:
    try:
        os.makedirs(
            config.TEMP_OUTPUT_FOLDER,
            exist_ok=True
        )

        file_name = os.path.basename(file_path)

        printed_file_path = os.path.join(
            config.TEMP_OUTPUT_FOLDER,
            file_name
        )

        printer_name = config.PRINTER_PDF

        hprinter = win32print.OpenPrinter(printer_name)

        printer_info = win32print.GetPrinter(hprinter, 2)

        devmode = printer_info["pDevMode"]

        devmode.PrintFileName = printed_file_path
        devmode.Fields |= win32print.DM_PRINTFILE

        win32print.SetPrinter(hprinter, 2, printer_info, 0)

        win32print.ClosePrinter(hprinter)

        pdf_dc = win32ui.CreateDC()

        pdf_dc.CreatePrinterDC(printer_name)

        pdf_dc.StartDoc({'DocName': file_name})

        pdf_dc.StartPage()
        pdf_dc.EndPage()
        pdf_dc.EndDoc()

        pdf_dc.DeleteDC()

        info(f"PDF gedruckt: {file_name}")

        for _ in range(5):
            if os.path.exists(printed_file_path):
                break

            time.sleep(1)

        else:
            warning(f"PDF-Ausgabe nicht erstellt: {printed_file_path}")
            return False

        shutil.move(printed_file_path, file_path)
        success(f"PDF zurückverschoben: {file_name}")
        return convert(file_path)

    except Exception as e:
        error(f"Fehler beim Drucken von {file_path}: {e}")
        return False