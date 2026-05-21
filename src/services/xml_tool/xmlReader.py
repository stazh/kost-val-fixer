from tkinter import filedialog
import config
import xml.etree.ElementTree as ET
from app import root

from services.logStorage import add_log, save_logs
from services.kost_val.validator import validate_files
from services import pdf_fixer, tiff_fixer, xlsx_fixer

def fix_formats() -> None:
    """Behebt automatisch die Formatierungsfehler in der XML-Datei und trägt alle Module ein"""
    try:
        file_path = filedialog.askopenfilename(
            title="Wählen Sie eine XML-Datei aus",
            filetypes=[("XML files", "*.xml")],
            parent=root
        )

        if not file_path:
            add_log("Keine Datei ausgewählt: Vorgang abgebrochen.")
            return

        file_path = str(file_path)
        add_log(f"Datei ausgewählt: {file_path}")

        tree = ET.parse(file_path)
        root_element = tree.getroot()

        invalid_validations = []

        # XML durchlaufen und ungültige Validierungen sammeln
        for format_section in root_element.findall(".//Format"):
            for section in format_section.findall("Validation"):
                invalid_tag = section.find("Invalid")
                not_accepted_tag = section.find("Notaccepted")

                if (invalid_tag is not None and str(invalid_tag.text).lower() == "invalid") \
                   or (not_accepted_tag is not None and str(not_accepted_tag.text).lower() == "not accepted"):

                    val_file = section.findtext("ValFile", default="").replace("->", "").strip()

                    messages = []
                    modules = set()

                    for error in section.findall("Error"):
                        modul_tag = error.find("Modul")
                        if modul_tag is not None and modul_tag.text:
                            modules.add(modul_tag.text.strip())

                        for msg in error.findall("Message"):
                            if msg.text:
                                messages.append(str(msg.text).strip())

                    combined_messages = " ".join(messages)

                    invalid_validations.append({
                        "filePath": val_file,
                        "modul": list(modules),
                        "message": combined_messages
                    })

        add_log(f"Nicht bestandene Validierungen gefunden: {len(invalid_validations)} Dateien.")

        if invalid_validations:
            add_log("Starte Sortierung und mögliche Reparaturen der Dateien:")
            sort_validations_by_file(invalid_validations)

            add_log("Starte Validierung der Dateien mit KOST-Val:")
            validate_files(invalid_validations)
        else:
            add_log("Keine ungültigen Validierungen gefunden. Alles in Ordnung.")

        save_logs()

    except Exception as e:
        add_log(f"Fehler beim Verarbeiten der XML-Datei: {e}")
        save_logs()

def sort_validations_by_file(invalid_validations: list) -> None:
    """
    Sortiert die ungültigen Validierungen nach Dateityp und Modul
    und führt die in config.SUPPORTED_ERRORS definierte Aktion aus.
    """
    try:
        for error in invalid_validations:
            solved = False
            file_path = str(error["filePath"])
            error_message = str(error["message"])
            modules = error.get("modul", [])
            file_path_lower = file_path.lower()
            add_log(f"Sortiere Datei: {file_path} | Module: {modules}")

            # Dateityp per 'endswith' prüfen (wie endswitch)
            match True:
                case _ if file_path_lower.endswith(".pdf"):
                    file_type = "PDF"
                    fixer = pdf_fixer
                case _ if file_path_lower.endswith(".tif") or file_path_lower.endswith(".tiff"):
                    file_type = "TIFF"
                    fixer = tiff_fixer
                case _ if file_path_lower.endswith(".xls"):
                    file_type = "XLS"
                    fixer = xlsx_fixer
                case _:
                    add_log(f"Korrektur erforderlich: Dieser Dateityp wird noch nicht unterstützt: {file_path}")
                    continue

            # Module durchgehen und Aktion ausführen
            for modul in modules:
                action = config.SUPPORTED_ERRORS.get(file_type, {}).get(modul, None)
                if action == config.PRINT and not config.PDF_FONT_MESSAGE in error_message:
                    solved = fixer.print.printPDF(file_path)
                    add_log(f"{file_type} Datei {file_path} Modul '{modul}' mit 'print' verarbeitet {'erfolgreich' if solved else 'nicht erfolgreich'}")
                    break
                elif action == config.CONVERT:
                    solved = fixer.convert.convert(file_path)
                    add_log(f"{file_type} Datei {file_path} Modul '{modul}' mit 'convert' verarbeitet: {'erfolgreich' if solved else 'nicht erfolgreich'}")
                    break
                else:
                    add_log(f"{file_type} Datei {file_path} Modul '{modul}' hat keine definierte Aktion, Korrektur erforderlich.")
                    break

    except Exception as e:
        add_log(f"Fehler beim Sortieren der Validierungen: {e}")