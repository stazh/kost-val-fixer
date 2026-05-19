from tkinter import filedialog
import config
import xml.etree.ElementTree as ET
from app import root

def fix_formats() -> None:
    """Behebt automatisch die Formatierungsfehler in der XML-Datei"""
    try:
        file_path = filedialog.askopenfilename(
            title="Wählen Sie eine XML-Datei aus",
            filetypes=[("XML files", "*.xml")],
            parent=root
        )

        if not file_path:
            print("Keine Datei: Es wurde keine Datei ausgewählt.")
            return
        
        file_path = str(file_path)
        print(f"Datei ausgewählt: {file_path}")
        tree = ET.parse(file_path)
        root_element = tree.getroot()

        invalid_validations = []

        for format_section in root_element.findall(".//Format"):
            for section in format_section.findall("Validation"):
                invalid_tag = section.find("Invalid")
                not_accepted_tag = section.find("Notaccepted")

                if (invalid_tag is not None and str(invalid_tag.text).lower() == "invalid") \
                   or (not_accepted_tag is not None and str(not_accepted_tag.text).lower() == "not accepted"):

                    val_file = section.findtext("ValFile", default="")
                    val_file = str(val_file).replace("->", "").strip()

                    messages = []
                    for error in section.findall("Error"):
                        for msg in error.findall("Message"):
                            if msg.text:
                                messages.append(str(msg.text).strip())

                    if messages:
                        combined_messages = " ".join(messages)
                        invalid_validations.append({
                            "filePath": val_file,
                            "message": combined_messages
                        })
        sort_validations_by_file(invalid_validations)

    except Exception as e:
        print(f"Fehler beim Lesen der Datei: {e}")

def sort_validations_by_file(invalid_validations: list) -> None:
    """Sortiert die ungültigen Validierungen mit filePath in die richtige Funktion"""
    try:
        for error in invalid_validations:
            file_path = str(error["filePath"])
            error_message = str(error["message"])
            fp_lower = file_path.lower()

            match True:
                case _ if config.SUPPORTED_FILE_TYPES["PDF"] in fp_lower:
                    from repairPDF import repair_pdf_file
                    repair_pdf_file(file_path, error_message)
                case _ if config.SUPPORTED_FILE_TYPES["TIF"] in fp_lower:
                    from repairTIF import repair_tif_file
                    repair_tif_file(file_path, error_message)
                case _:
                    print(f"Korrektur erforderlich: Dieser Dateityp wird noch nicht unterstützt: {file_path}\nFehlermeldung: {error_message}")
    except Exception as e:
        print(f"Fehler beim Sortieren der Validierungen: {e}")