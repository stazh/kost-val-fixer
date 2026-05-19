import sys
import os
import importlib
import argparse
import tkinter as tk

# Globales Root-Fenster für alle MessageBoxen
root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)

# Aktuelles Arbeitsverzeichnis
current_dir = os.path.dirname(os.path.abspath(__file__))

# Pfade für Bibliotheken und Dienste
services_path = os.path.join(current_dir, 'services')
config_path = os.path.join(current_dir.replace('\main.pyz', ''))

import config
if getattr(sys, 'frozen', False):
    scripts_dir = os.path.dirname(sys.executable).replace(config.SOURCE_FOLDER_PATH, '')
    PROJECT_DIR = os.path.dirname(scripts_dir)
else:
    scripts_dir = os.path.dirname(os.path.abspath(__file__)).replace(config.SOURCE_FOLDER_PATH, '')
    PROJECT_DIR = os.path.dirname(scripts_dir)

os.chdir(PROJECT_DIR)

# Kommando-Mapping für verschiedene Aktionen
COMMANDS = {
    'fix-formats': ('xmlReader', 'fix_formats', 'Behebt automatisch die Formatierungsfehler in den XML-Dateien.'),
}

def execute_command(command: str) -> None:
    """Führt das angegebene Kommando aus, indem die zugehörige Funktion importiert und aufgerufen wird."""
    if command in COMMANDS:
        file_name, function_name, _ = COMMANDS[command]
        try:
            module = importlib.import_module(file_name)  # Modul dynamisch importieren
            func = getattr(module, function_name)  # Funktion aus dem Modul holen
            func()  # Funktion ausführen
        except ModuleNotFoundError as e:
            print(f'Fehler: Die Datei \'{file_name}.py\' wurde im services-Ordner nicht gefunden. Fehler: {e}')
        except AttributeError as e:
            print(f'Fehler: Die Funktion \'{function_name}\' wurde in der Datei \'{file_name}.py\' nicht gefunden. Fehler: {e}')
        except Exception as e:
            print(f'Fehler: Es ist ein Fehler aufgetreten: {e}')
    else:
        print(f'Fehler: Der Befehl \'{command}\' ist nicht im Mapping definiert.')

def main() -> None:
    """Hauptfunktion, die das Kommando aus der Kommandozeile verarbeitet und ausführt."""
    try:
        # Pfade zu den Bibliotheken und Diensten zum sys.path hinzufügen
        sys.path.append(services_path)
        sys.path.append(config_path)

        # Kommandozeilenparser initialisieren
        parser = argparse.ArgumentParser(description="CLI für das KOST_VAl Fixer: Ruft die passende Funktion der richtigen Datei auf.")
        parser.add_argument('command', type=str, help='Der Befehl, der die zugehörige Datei und Funktion bestimmt.')
        args = parser.parse_args()
        
        # Funktion basierend auf dem Kommando ausführen
        execute_command(args.command)
    except Exception as e:
       print(f'Fehler: Es ist ein Fehler aufgetreten: {e}')

# Startet das Skript, wenn es direkt ausgeführt wird
if __name__ == '__main__':
    ret_code = main()
    sys.exit(ret_code)