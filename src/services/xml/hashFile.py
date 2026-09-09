import hashlib

import config

from services.xml.logging import (
    info,
    warning,
    error,
    success
)


def calculate_md5(file_path: str, chunk_size: int = 8192) -> str:
    """
    Calculates and returns the MD5 hash of a file.

    Args:
        file_path: Path to the file.
        chunk_size: Number of bytes to read per iteration.

    Returns:
        The MD5 hash as a hexadecimal string.
    """
    md5 = hashlib.md5()

    with open(file_path, "rb") as file:
        while chunk := file.read(chunk_size):
            md5.update(chunk)

    return md5.hexdigest()


def hasher(file_path: str) -> str:
    """
    Calculates the MD5 hash of a file and returns it.
    """
    if not file_path:
        warning("Keine Datei ausgewählt.")
        return ""

    info(f"Datei ausgewählt: {file_path}")

    try:
        md5_hash = calculate_md5(file_path)

        info(f"MD5 Hash der Datei: {md5_hash}")

        return md5_hash

    except FileNotFoundError:
        error(f"Datei nicht gefunden: {file_path}")
        return ""

    except PermissionError:
        error(f"Keine Berechtigung zum Lesen der Datei: {file_path}")
        return ""

    except OSError as exc:
        error(f"Fehler beim Lesen der Datei: {exc}")
        return ""
