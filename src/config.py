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

# ------------------------
# 2. Supported Errors
# ------------------------
SUPPORTED_PDF_ERRORS = [
    {"MESSAGE": "The processing instruction target matching \"[xX][mM][lL]\" is not allowed.", "SOLUTION": "convert"},
    {"MESSAGE": "Eine Datei, die mit Level A konform ist, muss den Wert von pdfaid:conformance als A angeben. Eine Datei, die mit Level B konform ist, muss den Wert von pdfaid:conformance als B angeben. Eine mit Level U konforme Datei muss den Wert von pdfaid:conformance als U angeben.", "SOLUTION": "convert" },
    {"MESSAGE": "Der Wert von pdfaid:part muss die Teilenummer von ISO 19005 sein, der die Datei entspricht.", "SOLUTION": "convert" },
    {"MESSAGE": "Die PDF Datei wird nicht akzeptiert.", "SOLUTION": "print"},
    {"MESSAGE": "Informationen sind hier ersichtlich: https://kost-ceco.ch/cms/pdf-nicht-durchsuchbar.html", "SOLUTION": "print"}
]
SUPPORTED_TIF_ERRORS = [
    {"MESSAGE": "CompressionScheme: ISO JPEG ist nicht zulaessig.", "SOLUTION": "convert"}
]

# ------------------------
# 3. Processesing Commands
# ------------------------
CONVERT = "convert"
PRINT = "print"
PRINTER_PDF = "Microsoft Print to PDF"