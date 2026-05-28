import os
import subprocess
import config

from services.xml.logging import (
    info,
    warning,
    error,
    success
)


def run_vlc_to_mp4(input_path: str, output_path: str) -> bool:
    """
    Führt VLC aus, um eine Video- oder Audiodatei in MP4 zu konvertieren.
    """
    vlc_path = config.VLC_MEDIA_PLAYER_PATH

    if not os.path.isfile(vlc_path):
        error(f"VLC nicht gefunden: {vlc_path}")
        return False

    cmd = [
        vlc_path,
        input_path,
        "--sout",
        f"#transcode{{vcodec=h264,acodec=mp4a}}:std{{access=file,mux=mp4,dst={output_path}}}",
        "vlc://quit"
    ]

    info(f"Starte VLC Konvertierung: {os.path.basename(input_path)}")

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            error(f"VLC Fehlercode {result.returncode} bei {os.path.basename(input_path)} | STDERR: {result.stderr.strip()}")
            return False

        if not os.path.exists(output_path):
            warning(f"Output-Datei wurde nicht erstellt: {output_path}")
            return False

        success(f"VLC Konvertierung erfolgreich: {os.path.basename(output_path)}")
        return True

    except Exception as e:
        error(f"Fehler bei VLC Konvertierung: {e}")
        return False


def convert(file_path: str) -> bool:
    """
    Konvertiert Datei zu MP4 und löscht die Originaldatei.
    """
    try:
        folder = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = os.path.join(folder, f"{base_name}.mp4")

        # Falls alte MP4 existiert → löschen
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
                info(f"Alte MP4 gelöscht: {output_file}")
            except Exception as e:
                warning(f"Alte MP4 konnte nicht gelöscht werden: {e}")

        ok = run_vlc_to_mp4(file_path, output_file)

        if not ok:
            error(f"VLC Konvertierung fehlgeschlagen: {file_path}")
            return False

        # Originaldatei löschen
        try:
            os.remove(file_path)
            info(f"Original gelöscht: {file_path}")
        except Exception as e:
            warning(f"Original konnte nicht gelöscht werden: {e}")

        success(f"MP4 erstellt: {output_file}")
        return True

    except Exception as e:
        error(f"Fehler beim Konvertieren: {e}")
        return False