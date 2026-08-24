import os
import shutil
import time
import ctypes
from pathlib import Path

from pywinauto import Application, Desktop, keyboard

from services.xml.logging import info, warning, error, success
import config


user32 = ctypes.windll.user32


def drucken(dialog):
    """
    Versucht den Drucken-Button im Acrobat-Druckdialog
    zuverlässig auszulösen.
    """

    try:
        info(
            f"Steuere Druckdialog: "
            f"Titel={dialog.window_text()!r}, "
            f"Handle={dialog.handle}"
        )

        dialog.wait(
            "visible",
            timeout=10
        )

        dialog.set_focus()

        time.sleep(0.5)

        # -------------------------------------------------
        # Alle Buttons protokollieren
        # -------------------------------------------------

        try:
            buttons = dialog.descendants(
                control_type="Button"
            )

            info(
                f"Buttons im Druckdialog: {len(buttons)}"
            )

            for i, button in enumerate(buttons):
                try:
                    info(
                        f"Button[{i}]: "
                        f"title={button.window_text()!r}, "
                        f"class={button.class_name()!r}, "
                        f"enabled={button.is_enabled()}, "
                        f"visible={button.is_visible()}"
                    )
                except Exception:
                    pass

        except Exception as e:
            warning(
                f"Buttons konnten nicht aufgelistet werden: {e}"
            )

        # -------------------------------------------------
        # Drucken-Button suchen
        # -------------------------------------------------

        button = dialog.child_window(
            title_re=r".*Drucken.*",
            control_type="Button"
        )

        button.wait(
            "visible",
            timeout=10
        )

        button.wait(
            "enabled",
            timeout=10
        )

        info(
            f"Drucken-Button gefunden: "
            f"{button.window_text()!r}"
        )

        # -------------------------------------------------
        # Button fokussieren
        # -------------------------------------------------

        try:
            button.set_focus()
            time.sleep(0.5)

        except Exception as e:
            warning(
                f"Drucken-Button konnte nicht fokussiert werden: {e}"
            )

        # -------------------------------------------------
        # Methode 1: UIA InvokePattern
        # -------------------------------------------------

        try:
            info(
                "Versuche Drucken über invoke()..."
            )

            button.invoke()

            info(
                "Drucken über invoke() ausgelöst."
            )

            return True

        except Exception as e:
            warning(
                f"invoke() fehlgeschlagen: {e}"
            )

        # -------------------------------------------------
        # Methode 2: echter Mausklick
        # -------------------------------------------------

        try:
            info(
                "Versuche Drucken über click_input()..."
            )

            button.click_input()

            info(
                "Drucken über click_input() ausgelöst."
            )

            return True

        except Exception as e:
            warning(
                f"click_input() fehlgeschlagen: {e}"
            )

        # -------------------------------------------------
        # Methode 3: pywinauto click()
        # -------------------------------------------------

        try:
            info(
                "Versuche Drucken über click()..."
            )

            button.click()

            info(
                "Drucken über click() ausgelöst."
            )

            return True

        except Exception as e:
            warning(
                f"click() fehlgeschlagen: {e}"
            )

        # -------------------------------------------------
        # Alles fehlgeschlagen
        # -------------------------------------------------

        error(
            "Drucken konnte nicht ausgelöst werden."
        )

        return False

    except Exception as e:

        error(
            f"Drucken fehlgeschlagen: {e}"
        )

        return False


def get_window_title(hwnd):
    try:
        length = user32.GetWindowTextLengthW(hwnd)

        if length <= 0:
            return ""

        buffer = ctypes.create_unicode_buffer(
            length + 1
        )

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
        buffer = ctypes.create_unicode_buffer(
            512
        )

        user32.GetClassNameW(
            hwnd,
            buffer,
            512
        )

        return buffer.value

    except Exception:
        return ""


def speicherfenster_finden(acrobat_hwnd):

    info(
        "Warte auf Speicherdialog..."
    )

    for _ in range(60):

        # -------------------------------------------------
        # Vordergrundfenster prüfen
        # -------------------------------------------------

        try:

            hwnd = user32.GetForegroundWindow()

            if hwnd and hwnd != acrobat_hwnd:

                title = get_window_title(hwnd)
                cls = get_window_class(hwnd)

                info(
                    f"Aktives Fenster: "
                    f"Titel={title!r}, "
                    f"Klasse={cls!r}, "
                    f"Handle={hwnd}"
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
                f"Fehler bei der Prüfung des "
                f"Vordergrundfensters: {e}"
            )

        # -------------------------------------------------
        # Zusätzlich alle Fenster prüfen
        # -------------------------------------------------

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
                f"Fehler beim Durchsuchen "
                f"der Fenster: {e}"
            )

        time.sleep(0.5)

    warning(
        "Kein Speicherdialog gefunden."
    )

    return None


def speichern(dialog, datei):

    try:

        info(
            "Steuere Speicherdialog direkt, "
            "ohne TAB-Navigation."
        )

        dialog.set_focus()

        edits = dialog.descendants(
            control_type="Edit"
        )

        if not edits:

            error(
                "Kein Eingabefeld im "
                "Speicherdialog gefunden."
            )

            return False

        info(
            f"{len(edits)} Eingabefeld(er) "
            f"im Speicherdialog gefunden."
        )

        # -------------------------------------------------
        # Dateiname-Feld
        # -------------------------------------------------

        filename = edits[len(edits) - 2]

        try:

            filename.click_input()

            filename.set_edit_text(
                str(datei)
            )

        except Exception:

            error(
                "Fehler beim Setzen des "
                "Dateinamens im Speicherdialog."
            )

            return False

        info(
            f"Dateiname gesetzt: {datei}"
        )

        # -------------------------------------------------
        # Speichern-Button
        # -------------------------------------------------

        button = dialog.child_window(
            title_re=r"^(Speichern|Save)$",
            control_type="Button"
        )

        button.wait(
            "visible",
            timeout=5
        )

        button.wait(
            "enabled",
            timeout=5
        )

        button.click_input()

        success(
            "Speichern erfolgreich ausgelöst."
        )

        return True

    except Exception as e:

        error(
            f"Speichern fehlgeschlagen: {e}"
        )

        return False


def warte_auf_datei(datei, timeout=60):

    info(
        f"Warte auf erzeugte Datei: {datei}"
    )

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
                    "Datei gefunden, konnte aber "
                    f"nicht geprüft werden: {e}"
                )

        time.sleep(1)

    warning(
        f"Datei wurde innerhalb von "
        f"{timeout} Sekunden nicht gefunden: "
        f"{datei}"
    )

    return False


def acrobat_schliessen(app):

    info(
        "Schließe Adobe Acrobat..."
    )

    try:

        app.kill()

        time.sleep(2)

        success(
            "Adobe Acrobat wurde geschlossen."
        )

    except Exception as e:

        error(
            f"Adobe Acrobat konnte nicht "
            f"geschlossen werden: {e}"
        )


def createPDF(file_path: str) -> tuple[bool, str]:

    """
    Rendert die PDF-Seiten über Adobe Acrobat neu,
    speichert sie als PDF und ersetzt anschließend
    die Originaldatei.
    """

    try:

        info(
            f"Starte Neu-Rendern von PDF: "
            f"{file_path}"
        )

        pdf = file_path

        if not pdf:

            warning(
                "Keine PDF ausgewählt."
            )

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

        info(
            f"Quelle: {original}"
        )

        info(
            f"Output: {output}"
        )

        # -------------------------------------------------
        # PDF öffnen
        # -------------------------------------------------

        info(
            "Öffne PDF mit Adobe Acrobat..."
        )

        os.startfile(
            str(original)
        )

        time.sleep(4)

        # -------------------------------------------------
        # Acrobat verbinden
        # -------------------------------------------------

        try:

            info(
                "Verbinde mit Adobe Acrobat..."
            )

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
                f"Adobe Acrobat konnte nicht "
                f"gefunden werden: {e}"
            )

            return False, file_path

        # -------------------------------------------------
        # Acrobat fokussieren
        # -------------------------------------------------

        try:

            acrobat.set_focus()

            time.sleep(1)

        except Exception as e:

            warning(
                f"Acrobat konnte nicht "
                f"fokussiert werden: {e}"
            )

        # -------------------------------------------------
        # Druckdialog öffnen
        # -------------------------------------------------

        info(
            "Öffne Druckdialog..."
        )

        try:

            keyboard.send_keys(
                "^p"
            )

            info(
                "Strg+P wurde gesendet."
            )

        except Exception as e:

            error(
                f"Strg+P fehlgeschlagen: {e}"
            )

            acrobat_schliessen(app)

            return False, file_path

        time.sleep(5)

        # -------------------------------------------------
        # Druckdialog suchen
        # -------------------------------------------------

        try:

            druck = acrobat.child_window(
                title="Drucken",
                control_type="Window"
            )

            druck.wait(
                "visible",
                timeout=6
            )

            druck.set_focus()

            info(
                f"Druckdialog gefunden: "
                f"Titel={druck.window_text()!r}, "
                f"Handle={druck.handle}"
            )

        except Exception as e:

            error(
                f"Druckdialog nicht gefunden: {e}"
            )

            acrobat_schliessen(app)

            return False, file_path

        # -------------------------------------------------
        # DRUCKEN
        # -------------------------------------------------

        if not drucken(druck):

            error(
                "Drucken konnte nicht ausgelöst werden."
            )

            acrobat_schliessen(app)

            return False, file_path

        # -------------------------------------------------
        # Warten bis Speicherdialog erscheint
        # -------------------------------------------------

        time.sleep(3)

        dialog = speicherfenster_finden(
            acrobat_hwnd
        )

        if dialog is None:

            error(
                "Speicherdialog konnte nicht "
                "gefunden werden."
            )

            acrobat_schliessen(app)

            return False, file_path

        # -------------------------------------------------
        # SPEICHERN
        # -------------------------------------------------

        if not speichern(
            dialog,
            input
        ):

            error(
                "Speichervorgang konnte nicht "
                "ausgelöst werden."
            )

            acrobat_schliessen(app)

            return False, file_path

        # -------------------------------------------------
        # Auf Datei warten
        # -------------------------------------------------

        if not warte_auf_datei(
            output,
            timeout=60
        ):

            error(
                f"Erzeugte PDF wurde nicht "
                f"gefunden: {output}"
            )

            acrobat_schliessen(app)

            return False, file_path

        # -------------------------------------------------
        # Acrobat schließen
        # -------------------------------------------------

        acrobat_schliessen(
            app
        )

        # -------------------------------------------------
        # Original ersetzen
        # -------------------------------------------------

        try:

            if original.exists():

                info(
                    f"Lösche Originaldatei: "
                    f"{original}"
                )

                os.remove(
                    original
                )

            shutil.move(
                output,
                original
            )

            success(
                f"PDF erfolgreich neu gerendert: "
                f"{original}"
            )

            return True, str(original)

        except Exception as e:

            error(
                f"Fehler beim Ersetzen "
                f"der Originaldatei: {e}"
            )

            return False, file_path

    except Exception as e:

        error(
            f"Fehler beim Neu-Rendern der PDF "
            f"{file_path}: {e}"
        )

        return False, file_path
