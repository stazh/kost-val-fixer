import os
from win32com.client import Dispatch
from services.xml.logging import info, warning, error, success

def convert(file_path: str) -> bool:
    excel = None
    workbook = None

    try:
        if not os.path.isfile(file_path):
            error(f"Datei nicht gefunden: {file_path}")
            return False

        folder = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = os.path.join(folder, f"{base_name}.xlsx")

        info(f"Starte Konvertierung: {file_path}")

        excel = Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        excel.ScreenUpdating = False

        workbook = excel.Workbooks.Open(os.path.abspath(file_path), UpdateLinks=0, ReadOnly=False)

        # Berechne alle Formeln
        info("Berechne Formeln...")
        workbook.Application.CalculateFull()

        # Exportiere als XLSX
        workbook.SaveAs(os.path.abspath(output_file), FileFormat=51, Local=True)
        info(f"XLSX erstellt: {output_file}")

        workbook.Close(False)
        success(f"Konvertierung erfolgreich: {output_file}")

        # Optional: Original löschen
        try:
            os.remove(file_path)
            info(f"Original gelöscht: {file_path}")
        except Exception as e:
            warning(f"Original konnte nicht gelöscht werden: {e}")

        return True

    except Exception as e:
        error(f"Fehler bei der Konvertierung: {e}")
        return False

    finally:
        try:
            if workbook:
                workbook.Close(False)
        except:
            pass
        try:
            if excel:
                excel.Quit()
        except:
            pass