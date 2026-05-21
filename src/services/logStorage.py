import datetime

logs = []

def add_log(message):
    """Fügt eine Nachricht zum zentralen Log hinzu"""
    print(message)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logs.append(f"{timestamp} - {message}")

def save_logs():
    """Speichert alle gesammelten Logs in eine Datei"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"logs_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for entry in logs:
            f.write(entry + "\n")
    print(f"Logs gespeichert in {filename}")