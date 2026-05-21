# ------------------------
# 1. Pfade und Dateitypen
# ------------------------
SOURCE_FOLDER_PATH = "\\src"
SUPPORTED_FILE_TYPES = { "PDF": ".pdf", "TIF": ".tif" }
INPUT_FOLDER_PATH = r"S:\STAZH_ePDF\3_Überlieferungsbildung\Input (PDFA-2)"
OUTPUT_FOLDER_PATH = r"S:\STAZH_ePDF\3_Überlieferungsbildung\Output"
ADOBE_PATH = r"C:\Program Files (x86)\Adobe\Acrobat DC\Acrobat\Acrobat.exe"
PRINTER_NAME = "Adobe PDF"
TEMP_OUTPUT_FOLDER = r"Dokumente\TempPDFRepairOutput"
IRFANVIEW_PATH = r"C:\Program Files\IrfanView\i_view64.exe"
VALIDATOR_PATH = "C:\\Program Files\\KOST-CECO\\KOST-Tools\\tools\\KOST-Val"

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
    "TIFF": {"C) Komprimierung": "convert"}
}

# ------------------------
# 3. Processesing Commands
# ------------------------
CONVERT = "convert"
PRINT = "print"
PRINTER_PDF = "Microsoft Print to PDF"
VALIDATE_FORMAT = "..\\Liberica_JRE\\bin\\java.exe -Xms2g -Xmx6g -XX:+UseG1GC -XX:MaxGCPauseMillis=200 -jar cmd_KOST-Val.jar --sip \"Pfad\" --de --xml"

# ------------------------
# 4. Messages
# ------------------------
PDF_FONT_MESSAGE = "Es wurde keine Fontvalidierung durchgefuehrt, da die Module A bis I nicht bestanden haben."