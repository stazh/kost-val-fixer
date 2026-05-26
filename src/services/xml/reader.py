from tkinter import filedialog
import xml.etree.ElementTree as ET

import config
from app import root

from services.xml.logging import add_log, save_logs
from services.kost_val.validator import validate_files

def execute_convert(fixer, file_path: str) -> bool:
    return fixer.convert.convert(file_path)


def execute_print(fixer, file_path: str) -> bool:
    return fixer.print.createPDF(file_path)


ACTION_MAPPING = {
    config.CONVERT: execute_convert,
    config.PRINT: execute_print
}


def get_file_handler(file_path: str):
    """
    Ermittelt Dateityp und zuständigen Fixer
    anhand der Dateiendung.
    """
    file_path_lower = file_path.lower()

    for extension, (file_type, fixer) in config.FILE_TYPE_MAPPING.items():
        if file_path_lower.endswith(extension):
            return file_type, fixer

    return None, None


def fix_formats() -> None:
    """
    Behebt automatisch die Formatierungsfehler
    in der XML-Datei und trägt alle Module ein.
    """
    try:
        file_path = filedialog.askopenfilename(
            title="Wählen Sie eine XML-Datei aus",
            filetypes=[("XML files", "*.xml")],
            parent=root
        )

        if not file_path:
            add_log("Keine Datei ausgewählt: Vorgang abgebrochen.")
            return

        add_log(f"Datei ausgewählt: {file_path}")

        tree = ET.parse(file_path)
        root_element = tree.getroot()

        invalid_validations = []

        for format_section in root_element.findall(".//Format"):
            for validation in format_section.findall("Validation"):
                invalid_tag = validation.find("Invalid")
                not_accepted_tag = validation.find("Notaccepted")

                is_invalid = (
                    invalid_tag is not None
                    and str(invalid_tag.text).lower() == "invalid"
                )

                is_not_accepted = (
                    not_accepted_tag is not None
                    and str(not_accepted_tag.text).lower() == "not accepted"
                )

                if not (is_invalid or is_not_accepted):
                    continue

                val_file = validation.findtext("ValFile", default="").replace("->", "").strip()

                messages = []
                modules = set()

                for error in validation.findall("Error"):
                    modul_tag = error.find("Modul")

                    if modul_tag is not None and modul_tag.text:
                        modules.add(modul_tag.text.strip())

                    for msg in error.findall("Message"):
                        if msg.text:
                            messages.append(msg.text.strip())

                combined_messages = " ".join(messages)

                invalid_validations.append({
                    "filePath": val_file,
                    "modul": list(modules),
                    "message": combined_messages
                })

        add_log(f"Nicht bestandene Validierungen gefunden: "f"{len(invalid_validations)} Dateien.")

        if invalid_validations:
            add_log("Starte Sortierung und mögliche Reparaturen der Dateien:")
            sort_validations_by_file(invalid_validations)
            add_log("Starte Validierung der Dateien mit KOST-Val:")
            validate_files(invalid_validations)

        else:
            add_log("Keine ungültigen Validierungen gefunden.")

        save_logs()

    except Exception as e:
        add_log(f"Fehler beim Verarbeiten der XML-Datei: {e}")
        save_logs()


def sort_validations_by_file(invalid_validations: list) -> None:
    """
    Sortiert die ungültigen Validierungen
    nach Dateityp und Modul und führt
    definierte Aktionen aus.
    """

    try:
        for error in invalid_validations:
            file_path = str(error["filePath"])
            error_message = str(error["message"])
            modules = error.get("modul", [])

            add_log(f"Sortiere Datei: {file_path} | "f"Module: {modules}")

            file_type, fixer = get_file_handler(file_path)

            if not file_type:
                add_log(f"Korrektur erforderlich: "f"Nicht unterstützter Dateityp: "f"{file_path}")
                continue
            
            solved = False

            for modul in modules:
                action = (config.SUPPORTED_ERRORS.get(file_type, {}).get(modul))

                if not action:
                    add_log(f"{file_type} Datei {file_path} "f"Modul '{modul}' "f"hat keine definierte Aktion.")
                    continue

                # PDF Font Sonderfall
                if (action == config.PRINT and config.PDF_FONT_MESSAGE in error_message):
                    add_log(f"{file_type} Datei {file_path} "f"übersprungen wegen "f"PDF_FONT_MESSAGE.")
                    continue

                # Action ausführen
                try:
                    solved = ACTION_MAPPING[action](fixer, file_path)
                    add_log(f"{file_type} Datei {file_path} "f"Modul '{modul}' "f"mit '{action}' verarbeitet: "f"{'erfolgreich' if solved else 'nicht erfolgreich'}")

                    if solved:
                        break

                except Exception as action_error:
                    add_log(f"Fehler bei Aktion '{action}' "f"für Datei {file_path}: "f"{action_error}")

    except Exception as e:
        add_log(f"Fehler beim Sortieren "f"der Validierungen: {e}")