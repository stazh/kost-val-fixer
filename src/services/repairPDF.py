import config
import os
import shutil
import time
import win32print

def repair_pdf_file(file_path: str, error_message: str) -> None:
    """Repariert automatisch die PDF-Datei basierend auf bekannten Fehlern."""
    try:
        solution = None
        # Alle bekannten PDF-Fehler prüfen
        for error in config.SUPPORTED_PDF_ERRORS:
            if error["MESSAGE"] in error_message:
                solution = error["SOLUTION"]
                break
        
        solved = False

        if solution == config.CONVERT:
            solved = convert(file_path)
        elif solution == config.PRINT:
            solved = printPDF(file_path)
        else:
            print(f"Korrektur erforderlich: Dieser Fehler wird zurzeit nicht unterstützt (PDF):\nDatei: {file_path}\nFehlermeldung: {error_message}")

        if solved:
            print(f"PDF repariert: {file_path}")

    except Exception as e:
       print(f'Fehler: Fehler beim Verarbeiten der Datei: {e}')


def convert(file_path: str) -> bool:
    """Konvertiert die PDF-Datei in ein unterstütztes Format, um den Fehler zu beheben."""
    try:
        input_folder = config.INPUT_FOLDER_PATH
        output_folder = config.OUTPUT_FOLDER_PATH
        file_name = os.path.basename(file_path)
        input_path = os.path.join(input_folder, file_name)
        output_path = os.path.join(output_folder, file_name)
        # Input-Ordner erstellen, falls er nicht existiert
        os.makedirs(input_folder, exist_ok=True)
        # Datei kopieren in den Input-Ordner
        shutil.copy(file_path, input_path)
        # Überwache Output-Ordner für bis zu 10 Sekunden
        found = False
        for _ in range(10):
            if os.path.exists(output_path):
                found = True
                break
            time.sleep(1)
        if not found:
            print(f"Die Datei konnte nicht konvertiert werden, weil sie im Output-Ordner nicht gefunden wurde: {output_path}")
            return False
        
        # Konvertierte Datei zurück an Originalpfad verschieben (ersetzen)
        shutil.move(output_path, file_path)
        return True
    
    except Exception as e:
        print(f"Fehler: Fehler beim Konvertieren der Datei: {e}")


def printPDF(file_path: str) -> bool:
    """Druckt die PDF-Datei über Adobe Acrobat, um sie zu reparieren, und ruft danach convert auf."""
    try:
        temp_output_folder = config.TEMP_OUTPUT_FOLDER
        os.makedirs(temp_output_folder, exist_ok=True)

        file_name = os.path.basename(file_path)
        printed_file_path = os.path.join(temp_output_folder, file_name)

        # os.startfile kann "print" ausführen
        # Achtung: Hier wird der Standarddrucker genutzt
        os.startfile(file_path, "print")

        # Warte kurz, bis der Druckauftrag durch ist
        time.sleep(5)

        shutil.copy(file_path, printed_file_path)
        convert(file_path)

        return True
        
    except Exception as e:
        print(f"Fehler: Fehler beim Drucken der Datei: {e}")
        return False
