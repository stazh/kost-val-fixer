import os
import subprocess
import config
from services.xml.logging import add_log

# TODO: If Audio file create MP3 File otherwise create MP4 File

def run_vlc_to_mp4(input_path: str, output_path: str) -> bool:
    vlc = config.VLC_MEDIA_PLAYER_PATH

    if not os.path.exists(vlc):
        add_log("VLC nicht gefunden")
        return False

    cmd = [
        vlc,
        input_path,
        "--sout",
        f"#transcode{{vcodec=h264,acodec=mp4a}}:std{{access=file,mux=mp4,dst={output_path}}}",
        "vlc://quit"
    ]

    add_log(f"VLC Command: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0


def convert(file_path: str) -> bool:
    """
    Konvertiert Datei zu MP4 und löscht danach die Originaldatei.
    """
    try:
        folder = os.path.dirname(file_path)
        base = os.path.splitext(os.path.basename(file_path))[0]

        output_file = os.path.join(folder, base + ".mp4")

        # falls alte MP4 existiert → löschen
        if os.path.exists(output_file):
            os.remove(output_file)

        ok = run_vlc_to_mp4(file_path, output_file)

        if not ok:
            add_log(f"VLC Konvertierung fehlgeschlagen: {file_path}")
            return False

        if not os.path.exists(output_file):
            add_log(f"Output fehlt: {output_file}")
            return False

        # Original löschen
        try:
            os.remove(file_path)
            add_log(f"Original gelöscht: {file_path}")
        except Exception as e:
            add_log(f"Warnung: Original konnte nicht gelöscht werden: {e}")

        add_log(f"MP4 erstellt: {output_file}")
        return True

    except Exception as e:
        add_log(f"Fehler beim Konvertieren: {e}")
        return False