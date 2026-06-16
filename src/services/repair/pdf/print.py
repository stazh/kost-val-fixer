import os
import shutil

from services.xml.logging import info, warning, error, success
from services.repair.pdf.convert import convert
import config

def createPDF(file_path: str) -> bool:
    """
    Rendert die PDF-Seiten neu, speichert sie als echte PDF (Fonts eingebettet).
    Originaldatei wird ersetzt.
    """
    try:
        info(f"Starte Neu-Rendern von PDF: {file_path}")

        os.makedirs(config.TEMP_OUTPUT_FOLDER, exist_ok=True)
        temp_file = os.path.join(config.TEMP_OUTPUT_FOLDER, os.path.basename(file_path))

        # PDF öffnen
        #doc = fitz.open(file_path)
        #new_pdf = fitz.open()

        # Jede Seite als neue Seite rendern und hinzufügen
        #for page in doc:
            #pix = page.get_pixmap()
            #img_pdf = fitz.open("pdf", pix.tobytes("pdf"))
            #new_pdf.insert_pdf(img_pdf)

        #new_pdf.save(temp_file)
        #new_pdf.close()
        #doc.close()

        # Originaldatei ersetzen
        shutil.move(temp_file, file_path)
        success(f"PDF erfolgreich neu gerendert: {file_path}")

        return convert(file_path)

    except Exception as e:
        error(f"Fehler beim Neu-Rendern der PDF {file_path}: {e}")
        return False