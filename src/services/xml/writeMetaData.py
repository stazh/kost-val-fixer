import config
import os

import xml.etree.ElementTree as ET

from services.xml.logging import (
    info,
    warning,
    error,
    success
)
from services.xml.hashFile import hasher


def writeData(metaDataPath: str, filePath: str) -> None:
    """
    Sucht rekursiv in der XML-Datei nach einem <datei>-Element,
    dessen <originalName> dem fileName entspricht.

    Anschließend wird die zugehörige <pruefsumme> mit dem
    übergebenen MD5-Hash ersetzt.
    """

    try:
        fileName = os.path.basename(filePath)

        md5_hash = hasher(filePath)

        tree = ET.parse(metaDataPath)
        root = tree.getroot()

        namespace = {
            "ns": "http://bar.admin.ch/arelda/v4"
        }

        dateien = root.findall(".//ns:datei", namespace)

        info(
            f"{len(dateien)} Dateien in der XML-Struktur gefunden."
        )

        for datei in dateien:
            original_name = datei.find(
                "ns:originalName",
                namespace
            )

            if original_name is None:
                continue

            if original_name.text != fileName:
                continue

            pruefsumme = datei.find(
                "ns:pruefsumme",
                namespace
            )

            if pruefsumme is None:
                warning(
                    f"Datei '{fileName}' gefunden, "
                    f"aber keine <pruefsumme> vorhanden."
                )
                return

            alte_pruefsumme = pruefsumme.text
            pruefsumme.text = md5_hash

            tree.write(
                metaDataPath,
                encoding="UTF-8",
                xml_declaration=True
            )

            success(
                f"Prüfsumme für '{fileName}' erfolgreich aktualisiert."
            )

            info(
                f"Alt: {alte_pruefsumme}"
            )

            info(
                f"Neu: {md5_hash}"
            )

            return

        warning(
            f"Keine Datei mit originalName '{fileName}' gefunden."
        )

    except ET.ParseError as e:
        error(
            f"XML konnte nicht gelesen werden: {e}"
        )

    except OSError as e:
        error(
            f"Fehler beim Zugriff auf '{metaDataPath}': {e}"
        )

    except Exception as e:
        error(
            f"Fehler beim Aktualisieren der Prüfsumme: {e}"
        )
