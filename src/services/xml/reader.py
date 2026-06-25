import json
import os
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET

import config

from app import root

from services.kost_val.validator import create_json_file, validate_files

from services.xml.logging import (
    info,
    warning,
    error,
    success,
    save_logs,
    unsupported_file,
    conversion_result
)

def execute_convert(fixer, file_path: str) -> bool:
    return fixer.convert.convert(file_path)


def execute_print(fixer, file_path: str) -> bool:
    return fixer.print.createPDF(file_path)


ACTION_MAPPING = {
    config.CONVERT: execute_convert,
    config.PRINT: execute_print
}


def get_file_handler(file_path: str):
    file_path_lower = file_path.lower()

    for extension, (file_type, fixer) in config.FILE_TYPE_MAPPING.items():
        if file_path_lower.endswith(extension):
            return file_type, fixer

    return None, None


def fix_formats() -> None:
    try:
        file_path = filedialog.askopenfilename(
            title="Wählen Sie eine XML-Datei aus",
            filetypes=[("XML files", "*.xml")],
            parent=root
        )

        if not file_path:
            warning("Keine Datei ausgewählt.")
            return

        info(f"XML-Datei ausgewählt: {file_path}")

        tree = ET.parse(file_path)
        root_element = tree.getroot()

        invalid_validations = extract_invalid_validations(root_element)

        info(f"{len(invalid_validations)} ungültige Validierungen gefunden.", console=True)

        if invalid_validations:
            converted_files = process_validations(invalid_validations)

            info("Starte KOST-Val Revalidierung...")
            validate_files(converted_files)

        else:
            success("Keine ungültigen Validierungen gefunden.", console=True)

    except Exception as e:
        error(f"Fehler beim Verarbeiten der XML-Datei: {e}")

    finally:
        save_logs()


def extract_invalid_validations(root_element) -> list:
    invalid_validations = []

    for format_section in root_element.findall(".//Format"):

        for validation in format_section.findall("Validation"):

            invalid_tag = validation.findtext("Invalid", default="")
            not_accepted_tag = validation.findtext("Notaccepted", default="")

            is_invalid = invalid_tag.lower() == "invalid"
            is_not_accepted = not_accepted_tag.lower() == "not accepted"

            if not (is_invalid or is_not_accepted):
                continue

            file_path = (
                validation.findtext("ValFile", default="")
                .replace("->", "")
                .strip()
            )

            modules = set()
            messages = []

            for error_tag in validation.findall("Error"):
                modul = error_tag.findtext("Modul")
                if modul:
                    modules.add(modul.strip())

                for message in error_tag.findall("Message"):
                    if message.text:
                        messages.append(message.text.strip())

            invalid_validations.append({
                "filePath": file_path,
                "modul": list(modules),
                "message": " ".join(messages)
            })

    return invalid_validations


def process_validations(invalid_validations: list) -> list:
    results= []
    json_data_path = create_json_file()
    for validation in invalid_validations:
        file_path = str(validation["filePath"])
        modules = validation.get("modul", [])
        error_message = str(validation["message"])

        info(f"Verarbeite Datei: {file_path} | Module: {modules}")

        file_type, fixer = get_file_handler(file_path)

        if not file_type:
            results.append((
                file_path, "Nicht unterstützt", "Übersprungen (wird zurzeit nicht unterstützt)"
            ))
            unsupported_file(file_path)
            continue

        solved = False

        for modul in modules:
            action = (
                config.SUPPORTED_ERRORS
                .get(file_type, {})
                .get(modul)
            )

            if not action:
                warning(f"{file_type}: Keine Aktion definiert für Modul '{modul}'")
                continue

            # PDF Font Sonderfall
            if (
                action == config.PRINT
                and config.PDF_FONT_MESSAGE in error_message
            ):
                results.append((
                    file_path, "Nicht unterstützt", "Übersprungen (wird zurzeit nicht unterstützt)"
                ))
                warning(f"{file_path} übersprungen (PDF_FONT_MESSAGE)")
                continue

            try:
                solved = ACTION_MAPPING[action](
                    fixer,
                    file_path
                )

                conversion_result(file_path, solved)

                if solved:
                    results.append((
                        file_path, "Konvertiert", None
                    ))
                    break

            except Exception as action_error:
                results.append((
                    file_path, "Fehler", action_error
                ))
                error(f"Fehler bei Aktion '{action}' für {file_path}: {action_error}")

    with open(json_data_path, "r", encoding="utf-8") as datei:
        content = json.load(datei)
        
    content["converted_files"] = results

    with open(json_data_path, "w", encoding="utf-8") as datei:
        json.dump(content, datei, indent=4)

    return results


def read_log_file_content(log_file_path: str) -> list:
    try:
        tree = ET.parse(log_file_path)
        root_element = tree.getroot()

        results = []

        for format_section in root_element.findall(".//Format"):

            for validation in format_section.findall("Validation"):

                path = (
                    validation.findtext("ValFile", default="")
                    .replace("->", "")
                    .strip()
                )
                if validation.find("Valid") is not None:
                    status = "Valid"

                elif validation.find("Invalid") is not None:
                    status = "Invalid"

                elif validation.find("Notaccepted") is not None:
                    status = "NotAccepted"

                elif validation.find("Accepted") is not None:
                    status = "Accepted"
                    
                else:
                    status = "None"

                error_text = None

                error_tag = validation.find(".//Error/Message")
                if error_tag is not None and error_tag.text:
                    error_text = error_tag.text.strip()

                results.append((
                    path, status, error_text
                ))

        return results

    except Exception as e:
        error(f"Fehler beim Lesen der Log-Datei {log_file_path}: {e}")
        return []