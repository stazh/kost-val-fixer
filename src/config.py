# ------------------------
# 1. Pfade und Dateitypen
# ------------------------
from services.repair import media, pdf, picture, excel


SOURCE_FOLDER_PATH = r"\src"
SUPPORTED_FILE_TYPES = { "PDF": ".pdf", "TIF": ".tif", "AVI": ".avi", "VOB": ".vob" }
INPUT_FOLDER_PATH = r"S:\STAZH_ePDF\3_Überlieferungsbildung\Input (PDFA-2)"
OUTPUT_FOLDER_PATH = r"S:\STAZH_ePDF\3_Überlieferungsbildung\Output"
ADOBE_PATH = r"C:\Program Files (x86)\Adobe\Acrobat DC\Acrobat\Acrobat.exe"
PRINTER_NAME = "Adobe PDF"
TEMP_OUTPUT_FOLDER = r"Dokumente\TempPDFRepairOutput"
IRFANVIEW_PATH = r"C:\Program Files\IrfanView\i_view64.exe"
VALIDATOR_PATH = r"C:\Program Files\KOST-CECO\KOST-Tools\tools\KOST-Val"
VLC_MEDIA_PLAYER_PATH = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
RCLONE_PATH = r"C:\Program Files (x86)\RClone\rclone.exe"
LOG_FOLDER_PATH = r".kost-val_2x\logs"
LOG_FILE_EXTENSION = ".kost-val.log.xml"
DATA_FOLDER_PATH = r"I:\08_Zwischenablage_Mitarbeiter\Changten_Tseten_cen\Projekte\Kost-Val-Fixer\background-processes"

# ------------------------
# 2. Supported Errors
# ------------------------
SUPPORTED_ERRORS = {
    "PDF": {
        "A) Allgemeines": "convert",
        "A) Erkennung und Akzeptanz": "print",
        "D) Schriften": "print",
        "H) Metadaten": "convert",
        "K) Schrift-Validierung": "convert"
    },
    "TIFF": {"C) Komprimierung": "convert"},
    "AVI": {"3B) Zusaetzliche Formate": "convert"},
    "VOB": {"3B) Zusaetzliche Formate": "convert"},
    "GIF": {"A) Erkennung und Akzeptanz": "convert"},
    "JPG": {"A) Erkennung und Akzeptanz": "convert", "3B) Zusaetzliche Formate": "convert"},
    "PNG": {"A) Erkennung und Akzeptanz": "convert"},
    "MPG": {"A) Erkennung und Akzeptanz": "convert"},
    "XLS": {"A) Erkennung und Akzeptanz": "convert"},
    "DOC": {"A) Erkennung und Akzeptanz": "convert"},
    "DOCX": {"A) Erkennung und Akzeptanz": "convert"},
    "MSG": {"A) Erkennung und Akzeptanz": "convert"},
    "PPT": {"A) Erkennung und Akzeptanz": "convert"},
    "MOV": {"A) Erkennung und Akzeptanz": "convert"},
    "WMV": {"A) Erkennung und Akzeptanz": "convert"}
}

FILE_TYPE_MAPPING = {
    ".pdf": ("PDF", pdf),
    ".tif": ("TIFF", picture),
    ".tiff": ("TIFF", picture),
    ".xls": ("XLS", excel),
    ".avi": ("AVI", media),
    ".vob": ("VOB", media),
    ".gif": ("GIF", picture),
    ".jpg": ("JPG", picture),
    ".png": ("PNG", picture),
    ".mpg": ("MPG", media),
    ".doc": ("DOC", pdf),
    ".docx": ("DOCX", pdf),
    ".msg": ("MSG", pdf),
    ".ppt": ("PPT", pdf),
    ".mov": ("MOV", media),
    ".wmv": ("WMV", media)
}

UMLAUT_MAP = {
    'ä': 'ae',
    'ö': 'oe',
    'ü': 'ue',
    'Ä': 'Ae',
    'Ö': 'Oe',
    'Ü': 'Ue',
    'ß': 'ss'
}

# ------------------------
# 3. Processesing Commands
# ------------------------
CONVERT = "convert"
PRINT = "print"
PRINTER_PDF = "Microsoft Print to PDF"
VALIDATE_FORMAT = "..\\Liberica_JRE\\bin\\java.exe -Xms2g -Xmx6g -XX:+UseG1GC -XX:MaxGCPauseMillis=200 -jar cmd_KOST-Val.jar --Switch \"Pfad\" --de --xml"

# ------------------------
# 4. Messages
# ------------------------
PDF_FONT_MESSAGE = "Es wurde keine Fontvalidierung durchgefuehrt, da die Module A bis I nicht bestanden haben."
STATS = {
    "converted_success": 0,
    "converted_failed": 0,
    "validated_valid": 0,
    "validated_invalid": 0,
    "unsupported": 0,
    "errors": 0
}