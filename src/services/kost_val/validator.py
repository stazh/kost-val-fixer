import json
import subprocess
import os
from tkinter import Tk, filedialog, messagebox
from pathlib import Path

import config

from services.xml.logging import info, warning, error, success

def validate_files(invalid_validations: list) -> None:
    """
    Führt den Validator-Command für alle Dateien in invalid_validations aus
    und protokolliert die Ergebnisse sauber.
    """
    try:
        for error_entry in invalid_validations:
            file_path = str(error_entry["filePath"])
            info(f"Starte Validierung für Datei: {file_path}")

            try:
                command = create_validator_command(file_path)
                info(f"Führe Validator aus: {command}")

                # subprocess ohne shell=True für Sicherheit, split cmd falls nötig
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=config.VALIDATOR_PATH
                )

                # Prüfe stdout und stderr
                if result.stdout and result.stdout.strip():
                    info(f"Validator Ausgabe ({file_path}): {result.stdout.strip()}")

                if result.stderr and result.stderr.strip():
                    warning(f"Validator Fehler ({file_path}): {result.stderr.strip()}")

                if result.returncode == 0:
                    success(f"Validierung erfolgreich: {file_path}")
                else:
                    error(f"Validator beendet mit Fehlercode {result.returncode}: {file_path}")

            except Exception as ex:
                error(f"Fehler beim Validator-Aufruf für {file_path}: {ex}")

        read_log_file(files = invalid_validations, first_validation = True)

    except Exception as e:
        error(f"Fehler beim Validieren der Dateien: {e}")

    
def validate_files_from_folder() -> None:
    root = Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory(title="Ordner auswählen")

    if not folder_path:
        messagebox.showwarning("Abbruch", "Kein Ordner ausgewählt.")
        return

    command = create_validator_command(folder_path)

    try:
        subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=config.VALIDATOR_PATH
        )

    except Exception:
        messagebox.showerror("Fehler", "Fehler beim Ausführen des Validators.")
        return

    read_log_file(folder_path = folder_path, first_validation = True)

    messagebox.showinfo(
        "Fertig",
        f"Validierung abgeschlossen\n\nSiehe Liste für Details"
    )


def create_validator_command(path: str) -> str:
    """
    Erstellt den Validator-Befehl basierend auf dem gegebenen Pfad.
    """
    command = config.VALIDATE_FORMAT.replace("Pfad", path)

    correctSIPStructure = False
    sipFolderName = False
    isFolder = os.path.isdir(path)

    if isFolder:
        top_folders = {
            item.lower()
            for item in os.listdir(path)
            if os.path.isdir(os.path.join(path, item))
        }
        correctSIPStructure = {"content", "header"}.issubset(top_folders)

    if os.path.basename(path).startswith("SIP"):
        sipFolderName = True

    if correctSIPStructure and sipFolderName:
        command = command.replace("Switch", "sip")
    else:
        command = command.replace("Switch", "format")

    return command


def read_log_file(files = [], folder_path = None, first_validation = False) -> None:
    """
    Liest die Log-Datei des Validators aus und extrahiert die relevanten Informationen.
    Gibt eine Liste von Validierungsergebnissen zurück. Löscht die Log-Dateien, wo nur eine Datei validiert wurde.
    """

    results = []
    user_home = os.path.expanduser("~")
    json_data_path = create_json_file()

    try:
        from services.xml.reader import read_log_file_content
        if len(files) > 0:
            for file in files:
                log_file_path = os.path.join(user_home, config.LOG_FOLDER_PATH, f"{os.path.basename(file)}{config.LOG_FILE_EXTENSION}")
                if os.path.exists(log_file_path):
                    results = read_log_file_content(log_file_path)
                    os.remove(log_file_path)

        if folder_path is not None:
            log_file_path = os.path.join(user_home, config.LOG_FOLDER_PATH, f"{os.path.basename(folder_path)}{config.LOG_FILE_EXTENSION}")
            if os.path.exists(log_file_path):
                results = read_log_file_content(log_file_path)

        with open(json_data_path, "r", encoding="utf-8") as datei:
            content = json.load(datei)
        
        content["first_validation" if first_validation else "second_validation"] = results

        with open(json_data_path, "w", encoding="utf-8") as datei:
            json.dump(content, datei, indent=4)

    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Lesen der Log-Datei: {e}")


def create_json_file() -> str:
    user_home = Path.home()
    new_folder = user_home / "DATA_KOST_VAL_FIXER"
    new_folder.mkdir(parents=True, exist_ok=True)

    json_data_path = new_folder / "data.json"

    data_structure = {
        "first_validation": [],
        "second_validation": [],
        "converted_files": []
    }

    if not json_data_path.exists():
        with open(json_data_path, "w", encoding="utf-8") as datei:
            json.dump(data_structure, datei, indent=4)

    return json_data_path