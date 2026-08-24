import os
import shutil
import time
import ctypes
from pathlib import Path
from tkinter import Tk, filedialog

from pywinauto import Application, Desktop, keyboard

from services.xml.logging import info, warning, error, success
from services.repair.pdf.convert import convert
import config

user32 = ctypes.windll.user32


def pdf_auswaehlen():
    root = Tk()
    root.withdraw()

    pdf = filedialog.askopenfilename(
        title="PDF auswählen",
        filetypes=[("PDF Dateien", "*.pdf")]
    )

    root.destroy()
    return pdf


def drucken(dialog):
    try:
        dialog.child_window(
            title_re=".*Drucken.*",
            control_type="Button"
        ).click()

        info("Drucken-Button erfolgreich geklickt.")
        return True

    except Exception as e:
        error(f"Drucken fehlgeschlagen: {e}")
        return False


def get_window_title(hwnd):
    try:
        length = user32.GetWindowTextLengthW(hwnd)

        if length <= 0:
            return ""

        buffer = ctypes.create_unicode_buffer(length + 1)

        user32.GetWindowTextW(
            hwnd,
            buffer,
            length + 1
        )

        return buffer.value

    except Exception:
        return ""


def get_window_class(hwnd):
    try:
        buffer = ctypes.create_unicode_buffer(512)

        user32.GetClassNameW(
            hwnd,
            buffer,
            512
        )

        return buffer.value

    except Exception:
        return ""


def speicherfenster_finden(acrobat_hwnd):
    info("Warte auf Speicherdialog...")

    for _ in range(60):

        # Vordergrundfenster prüfen
        try:
            hwnd = user32.GetForegroundWindow()

            if hwnd and hwnd != acrobat_hwnd:

                title = get_window_title(hwnd)
                cls = get_window_class(hwnd)

                info(
                    f"Aktives Fenster: Titel={title!r}, "
                    f"Klasse={cls!r}, Handle={hwnd}"
                )

                text = title.lower()

                if (
                    "druckausgabe" in text
                    or "speichern" in text
                    or "save" in text
                ):
                    info(
                        f"Speicherdialog gefunden: "
                        f"Titel={title!r}, "
                        f"Klasse={cls!r}, "
                        f"Handle={hwnd}"
                    )

                    return Desktop(
                        backend="uia"
                    ).window(
                        handle=hwnd
                    )

        except Exception as e:
            warning(
                f"Fehler bei der Prüfung des Vordergrundfensters: {e}"
            )

        # Zusätzlich alle Fenster prüfen
        try:
            for window in Desktop(
                backend="uia"
            ).windows():

                try:
                    hwnd = window.handle
                    title = window.window_text()
                    cls = window.class_name()

                    if hwnd == acrobat_hwnd:
                        continue

                    text = (
                        title + " " + cls
                    ).lower()

                    if (
                        "druckausgabe" in text
                        or "speichern unter" in text
                        or "speichern" in text
                        or "save as" in text
                        or "save" in text
                    ):
                        info(
                            f"Speicherdialog gefunden: "
                            f"Titel={title!r}, "
                            f"Klasse={cls!r}, "
                            f"Handle={hwnd}"
                        )

                        return window

                except Exception:
                    pass

        except Exception as e:
            warning(
                f"Fehler beim Durchsuchen der Fenster: {e}"
            )

        time.sleep(0.5)

    warning("Kein Speicherdialog gefunden.")
    return None


def speichern(dialog, datei):
    try:
        info("Steuere Speicherdialog direkt, ohne TAB-Navigation.")

        dialog.set_focus()

        edits = dialog.descendants(
            control_type="Edit"
        )

        if not edits:
            error("Kein Eingabefeld im Speicherdialog gefunden.")
            return False

        info(
            f"{len(edits)} Eingabefeld(er) im Speicherdialog gefunden."
        )

        # Dateiname-Feld
        filename = edits[-1]

        try:
            filename.click_input()
            filename.set_edit_text(str(datei))

        except Exception:
            # Fallback über Clipboard
            info(
                "Direktes Setzen des Dateinamens fehlgeschlagen. "
                "Verwende Clipboard-Fallback."
            )

            filename.click_input()
            keyboard.send_keys("^a")

            import pyperclip
            pyperclip.copy(str(datei))
            keyboard.send_keys("^v")

        info(f"Dateiname gesetzt: {datei}")

        # Speichern-Button
        button = dialog.child_window(
            title_re=r"^(Speichern|Save)$",
            control_type="Button"
        )

        button.wait(
            "enabled",
            timeout=5
        )

        button.click()

        success("Speichern erfolgreich ausgelöst.")
        return True

    except Exception as e:
        error(f"Speichern fehlgeschlagen: {e}")
        return False


def warte_auf_datei(datei, timeout=60):
    info(f"Warte auf erzeugte Datei: {datei}")

    start = time.time()

    while time.time() - start < timeout:

        if datei.exists():

            try:
                size = datei.stat().st_size

                if size > 0:
                    success(
                        f"Datei gefunden: {datei} "
                        f"({size} Bytes)"
                    )
                    return True

            except Exception as e:
                warning(
                    f"Datei gefunden, konnte aber nicht geprüft werden: {e}"
                )

        time.sleep(1)

    warning(
        f"Datei wurde innerhalb von {timeout} Sekunden "
        f"nicht gefunden: {datei}"
    )

    return False


def acrobat_schliessen(app):
    info("Schließe Adobe Acrobat...")

    try:
        app.kill()
        time.sleep(2)

        success("Adobe Acrobat wurde geschlossen.")

    except Exception as e:
        error(
            f"Adobe Acrobat konnte nicht geschlossen werden: {e}"
        )


def createPDF(file_path: str) -> tuple[bool, str]:
    """
    Rendert die PDF-Seiten über Adobe Acrobat neu,
    speichert sie als PDF und ersetzt anschließend die Originaldatei.
    """

    try:
        info(
            f"Starte Neu-Rendern von PDF: {file_path}"
        )

        pdf = pdf_auswaehlen()

        if not pdf:
            warning("Keine PDF ausgewählt.")
            return False, "Keine PDF ausgewählt."

        original = Path(pdf)

        input_ordner = Path(
            config.INPUT_FOLDER_PATH
        )

        output_ordner = Path(
            config.OUTPUT_FOLDER_PATH
        )

        input = input_ordner / original.name
        output = output_ordner / original.name

        info(f"Quelle: {original}")
        info(f"Output: {output}")

        info("Öffne PDF mit Adobe Acrobat...")

        os.startfile(
            str(original)
        )

        time.sleep(8)

        try:
            info("Verbinde mit Adobe Acrobat...")

            app = Application(
                backend="uia"
            ).connect(
                path="Acrobat.exe",
                timeout=30
            )

            acrobat = app.top_window()
            acrobat_hwnd = acrobat.handle

            info(
                f"Acrobat gefunden: "
                f"Titel={acrobat.window_text()!r}, "
                f"Handle={acrobat_hwnd}"
            )

        except Exception as e:
            error(
                f"Adobe Acrobat konnte nicht gefunden werden: {e}"
            )
            return False, file_path

        info("Öffne Druckdialog...")

        keyboard.send_keys("^p")
        time.sleep(5)

        try:
            druck = acrobat.child_window(
                title="Drucken",
                control_type="Window"
            )

            druck.wait(
                "visible",
                timeout=15
            )

            info("Druckdialog gefunden.")

        except Exception as e:
            error(
                f"Druckdialog nicht gefunden: {e}"
            )

            acrobat_schliessen(app)

            return False, file_path

        if not drucken(druck):

            acrobat_schliessen(app)

            return False, file_path

        time.sleep(3)

        dialog = speicherfenster_finden(
            acrobat_hwnd
        )

        if dialog is None:

            error(
                "Speicherdialog konnte nicht gefunden werden."
            )

            acrobat_schliessen(app)

            return False, file_path

        if not speichern(
            dialog,
            input
        ):

            error(
                "Speichervorgang konnte nicht ausgelöst werden."
            )

            acrobat_schliessen(app)

            return False, file_path

        if not warte_auf_datei(
            output,
            timeout=60
        ):

            error(
                f"Erzeugte PDF wurde nicht gefunden: {output}"
            )

            acrobat_schliessen(app)

            return False, file_path

        acrobat_schliessen(app)

        try:

            if original.exists():

                info(
                    f"Lösche Originaldatei: {original}"
                )

                os.remove(
                    original
                )

            shutil.move(
                output,
                original
            )

            success(
                f"PDF erfolgreich neu gerendert: {original}"
            )

        except Exception as e:

            error(
                f"Fehler beim Ersetzen der Originaldatei: {e}"
            )

            return False, file_path

        return convert(file_path)

    except Exception as e:

        error(
            f"Fehler beim Neu-Rendern der PDF "
            f"{file_path}: {e}"
        )

        return False, file_path
