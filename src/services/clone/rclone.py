import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

import config

root = tk.Tk()
root.title("Rclone Transfer")
root.geometry("720x640")
root.configure(bg="#f4f6f8")

# -----------------------------
# STATE
# -----------------------------
source_paths = []

entry_source = None
entry_dest = None

mode_var = tk.StringVar(value="directory")
transfer_mode = tk.StringVar(value="copy")

# -----------------------------
# MAIN
# -----------------------------
main = tk.Frame(root, bg="#f4f6f8", padx=20, pady=20)
main.pack(fill="both", expand=True)


# -----------------------------
# CARD
# -----------------------------
def card(parent):
    frame = tk.Frame(parent, bg="white", padx=15, pady=15)
    frame.pack(fill="x", pady=10)
    return frame


# -----------------------------
# DISPLAY UPDATE
# -----------------------------
def refresh_source_display():
    entry_source.delete(0, tk.END)

    if not source_paths:
        entry_source.insert(0, "<< noch keine Quelle ausgewählt >>")
    elif len(source_paths) == 1:
        entry_source.insert(0, source_paths[0])
    else:
        entry_source.insert(0, f"{len(source_paths)} Elemente ausgewählt")


# -----------------------------
# SOURCE SELECT
# -----------------------------
def select_source():
    global source_paths

    if mode_var.get() == "directory":
        folder = filedialog.askdirectory(title="Quellordner auswählen")
        if folder:
            source_paths = [folder]
            refresh_source_display()

    else:
        files = filedialog.askopenfilenames(title="Dateien auswählen")
        if files:
            source_paths = list(files)
            refresh_source_display()


# -----------------------------
# DEST SELECT
# -----------------------------
def select_dest():
    folder = filedialog.askdirectory(title="Zielordner auswählen")
    if folder:
        entry_dest.delete(0, tk.END)
        entry_dest.insert(0, folder)


# -----------------------------
# BUILD COMMAND (WICHTIG)
# -----------------------------
def build_command():
    dest = entry_dest.get().strip()

    fixed_sources = [p.replace("\\", "/") for p in source_paths]
    fixed_dest = dest.replace("\\", "/")

    cmd = [
        config.RCLONE_PATH,
        transfer_mode.get(),
    ]

    # COPY / MOVE LOGIK
    if mode_var.get() == "directory":
        # 1 Ordner → inkl. Name
        src = fixed_sources[0]
        folder_name = os.path.basename(src.rstrip("/"))
        cmd += [src, os.path.join(fixed_dest, folder_name).replace("\\", "/")]

    else:
        # Dateien → direkt in Ziel
        cmd += fixed_sources
        cmd += [fixed_dest]

    return cmd


# -----------------------------
# RUN
# -----------------------------
def start_transfer():
    if not source_paths:
        messagebox.showerror("Fehler", "Bitte Quelle auswählen")
        return

    dest = entry_dest.get().strip()
    if not dest:
        messagebox.showerror("Fehler", "Bitte Ziel auswählen")
        return

    if not os.path.exists(config.RCLONE_PATH):
        messagebox.showerror("Fehler", "Rclone nicht gefunden")
        return

    cmd = build_command()

    print("COMMAND:", cmd)

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )

        messagebox.showinfo("Erfolg", "Transfer abgeschlossen")

    except subprocess.CalledProcessError as e:
        messagebox.showerror(
            "Rclone Fehler",
            f"Exit Code: {e.returncode}\n\n{e.stderr or e.stdout}"
        )


# -----------------------------
# UI
# -----------------------------

c1 = card(main)
tk.Label(c1, text="Quelle", bg="white", font=("Arial", 11, "bold")).pack(anchor="w")

entry_source = tk.Entry(c1)
entry_source.pack(fill="x", pady=5)

tk.Button(
    c1,
    text="Quelle auswählen",
    bg="#2f80ed",
    fg="white",
    command=select_source
).pack(anchor="w", pady=5)


c2 = card(main)
tk.Label(c2, text="Ziel", bg="white", font=("Arial", 11, "bold")).pack(anchor="w")

entry_dest = tk.Entry(c2)
entry_dest.pack(fill="x", pady=5)

tk.Button(
    c2,
    text="Ziel auswählen",
    bg="#2f80ed",
    fg="white",
    command=select_dest
).pack(anchor="w", pady=5)


c3 = card(main)
tk.Label(c3, text="Quelle Typ", bg="white", font=("Arial", 11, "bold")).pack(anchor="w")

tk.Radiobutton(c3, text="Ordner", variable=mode_var, value="directory", bg="white").pack(anchor="w")
tk.Radiobutton(c3, text="Dateien", variable=mode_var, value="files", bg="white").pack(anchor="w")


c4 = card(main)
tk.Label(c4, text="Transfer Modus", bg="white", font=("Arial", 11, "bold")).pack(anchor="w")

tk.Radiobutton(c4, text="Copy", variable=transfer_mode, value="copy", bg="white").pack(anchor="w")
tk.Radiobutton(c4, text="Move", variable=transfer_mode, value="move", bg="white").pack(anchor="w")


tk.Button(
    main,
    text="Start Transfer",
    bg="#1f6feb",
    fg="white",
    height=2,
    command=start_transfer
).pack(fill="x", pady=15)

root.mainloop()