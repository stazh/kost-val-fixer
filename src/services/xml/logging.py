import datetime
import os
import config

LOGS = []


def _timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(level: str, message: str, console: bool = False):
    """
    Zentrales Logging.

    console=True:
        Ausgabe zusätzlich im Terminal.
    """

    entry = f"[{_timestamp()}] [{level}] {message}"
    LOGS.append(entry)

    if console:
        print(message)


def info(message: str, console: bool = False):
    log("INFO", message, console)


def success(message: str, console: bool = False):
    log("SUCCESS", message, console)


def warning(message: str, console: bool = False):
    log("WARNING", message, console)


def error(message: str, console: bool = True):
    config.STATS["errors"] += 1
    log("ERROR", message, console)


def conversion_result(file_name: str, success_state: bool):
    if success_state:
        config.STATS["converted_success"] += 1

        msg = f"{file_name} konvertiert = erfolgreich"

        success(msg, console=True)

    else:
        config.STATS["converted_failed"] += 1

        msg = f"{file_name} konvertiert = nicht erfolgreich"

        warning(msg, console=True)


def validation_result(file_name: str, valid: bool):
    if valid:
        config.STATS["validated_valid"] += 1

        msg = f"Validiere {file_name} = valide"

        success(msg, console=True)

    else:
        config.STATS["validated_invalid"] += 1

        msg = f"Validiere {file_name} = invalide"

        warning(msg, console=True)


def unsupported_file(file_name: str):
    config.STATS["unsupported"] += 1

    warning(
        f"{file_name} ist nicht unterstützt",
        console=True
    )


def save_logs(addSummary: bool = True):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    os.makedirs("logs", exist_ok=True)

    filename = f"../logs/log_{timestamp}.txt"
    summary = []

    if addSummary:
        summary = [
            "",
            "=" * 60,
            "ZUSAMMENFASSUNG",
            "=" * 60,
            f"Konvertiert erfolgreich : {config.STATS['converted_success']}",
            f"Konvertierung fehlgeschlagen : {config.STATS['converted_failed']}",
            f"Valide Dateien : {config.STATS['validated_valid']}",
            f"Invalide Dateien : {config.STATS['validated_invalid']}",
            f"Nicht unterstützt : {config.STATS['unsupported']}",
            f"Fehler : {config.STATS['errors']}",
            "=" * 60,
        ]

    with open(filename, "w", encoding="utf-8") as f:
        for entry in LOGS:
            f.write(entry + "\n")

        for line in summary:
            f.write(line + "\n")

    if addSummary:
        print("\n===== ZUSAMMENFASSUNG =====")
        print(f"{config.STATS['converted_success']} Dateien konvertiert")
        print(f"{config.STATS['validated_invalid']} Dateien sind invalide")
        print(f"{config.STATS['errors']} Dateien haben Fehler")
        print(f"{config.STATS['unsupported']} Dateien nicht unterstützt")
        print("===========================\n")
        print(f"Logs gespeichert in: {filename}")