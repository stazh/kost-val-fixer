import os
from services.xml.logging import add_log


def convert(file_path: str) -> bool:
    """
    Konvertiert XLS -> XLSX mit Microsoft Excel.
    - Originaldatei wird gelöscht
    - Basisname bleibt gleich
    """

    excel = None
    workbook = None
    try:
        if not os.path.exists(file_path):
            add_log(f"Datei nicht gefunden: {file_path}")
            return False

        folder = os.path.dirname(file_path)

        file_name = os.path.basename(file_path)
        base_name, ext = os.path.splitext(file_name)

        ext = ext.lower()

        # nur XLS konvertieren
        if ext != ".xls":
            add_log(f"Keine XLS-Datei: {file_path}")
            return False

        output_file = os.path.join(folder, f"{base_name}.xlsx")

        add_log(f"Starte XLS -> XLSX Konvertierung: {file_path}")

        # Excel starten
        from win32com.client import Dispatch
        excel = Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False

        # Workbook öffnen
        workbook = excel.Workbooks.Open(os.path.abspath(file_path))

        # FileFormat=51 => XLSX
        workbook.SaveAs(os.path.abspath(output_file), FileFormat=51)

        workbook.Close(False)
        workbook = None

        excel.Quit()
        excel = None

        # prüfen ob Output existiert
        if not os.path.exists(output_file):
            add_log(f"XLSX-Datei wurde nicht erstellt: {output_file}")
            return False

        # Original löschen
        os.remove(file_path)

        add_log(f"XLS erfolgreich konvertiert: {output_file}")

        return True

    except Exception as e:
        add_log(f"Fehler beim Konvertieren der Datei {file_path}: {e}")
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