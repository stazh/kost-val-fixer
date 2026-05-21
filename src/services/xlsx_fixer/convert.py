from services.logStorage import add_log


def convert(file_path: str) -> bool:
    """
    Konvertiert die XLS-Datei mit Excel und ersetzt die Originaldatei.
    """
    try:
        return True  # Platzhalter

    except Exception as e:
        add_log(f"Fehler beim Konvertieren der Datei {file_path}: {e}")
        return False