import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

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

progress_var = tk.DoubleVar(value=0)

# -----------------------------
# UI BASE
# -----------------------------
main = tk.Frame(root, bg="#f4f6f8", padx=20, pady=20)
main.pack(fill="both", expand=True)


def card(parent):
    frame = tk.Frame(parent, bg="white", padx=15, pady=15)
    frame.pack(fill="x", pady=10)
    return frame


# -----------------------------
# HELPERS
# -----------------------------
def refresh_source_display():
    entry_source.delete(0, tk.END)

    if not source_paths:
        entry_source.insert(0, "<< noch keine Quelle ausgewählt >>")
    elif len(source_paths) == 1:
        entry_source.insert(0, source_paths[0])
    else:
        entry_source.insert(0, f"{len(source_paths)} Elemente ausgewählt")


def select_source():
    global source_paths

    if mode_var.get() == "directory":
        folder = filedialog.askdirectory()
        if folder:
            source_paths = [folder]
            refresh_source_display()

    else:
        files = filedialog.askopenfilenames()
        if files:
            source_paths = list(files)
            refresh_source_display()


def select_dest():
    folder = filedialog.askdirectory()
    if folder:
        entry_dest.delete(0, tk.END)
        entry_dest.insert(0, folder)


# -----------------------------
# BUILD RCLONE COMMAND
# -----------------------------
def build_command():
    dest = entry_dest.get().strip()

    fixed_sources = [p.replace("\\", "/") for p in source_paths]
    fixed_dest = dest.replace("\\", "/")

    cmd = [
        config.RCLONE_PATH,
        transfer_mode.get(),
    ]

    # COPY / MOVE LOGIC
    for src in fixed_sources:
        cmd.append(src)

        # ORDNER-LOGIK: Ordnername behalten
        if os.path.isdir(src):
            folder_name = os.path.basename(src.rstrip("/"))
            cmd.append(os.path.join(fixed_dest, folder_name).replace("\\", "/"))
        else:
            cmd.append(fixed_dest)

    # REMOVE FLAG für MOVE
    if transfer_mode.get() == "move":
        cmd.append("--delete-after")

    cmd += ["--progress"]

    return cmd


# -----------------------------
# RUN PROCESS + PROGRESS
# -----------------------------
def start_transfer():
    if not source_paths:
        messagebox.showerror("Fehler", "Quelle fehlt")
        return

    dest = entry_dest.get().strip()
    if not dest:
        messagebox.showerror("Fehler", "Ziel fehlt")
        return

    if not os.path.exists(config.RCLONE_PATH):
        messagebox.showerror("Fehler", "Rclone nicht gefunden")
        return

    def worker():
        try:
            cmd = build_command()

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            for line in process.stdout:
                print(line.strip())

                # SIMPLE PROGRESS SIMULATION
                if "%" in line:
                    try:
                        percent = float(line.split("%")[0].split()[-1])
                        root.after(0, lambda p=percent: progress_var.set(p))
                    except:
                        pass

            process.wait()

            if process.returncode == 0:
                root.after(0, lambda: messagebox.showinfo("OK", "Fertig"))
                root.after(0, lambda: progress_var.set(100))
            else:
                root.after(0, lambda: messagebox.showerror("Fehler", "Rclone Fehler"))

        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Fehler", str(e)))

    threading.Thread(target=worker, daemon=True).start()


# -----------------------------
# UI
# -----------------------------
c1 = card(main)

tk.Label(c1, text="Quelle", bg="white", font=("Arial", 11, "bold")).pack(anchor="w")

entry_source = tk.Entry(c1)
entry_source.pack(fill="x", pady=5)

tk.Button(c1, text="Quelle auswählen", command=select_source).pack(anchor="w")


c2 = card(main)

tk.Label(c2, text="Ziel", bg="white", font=("Arial", 11, "bold")).pack(anchor="w")

entry_dest = tk.Entry(c2)
entry_dest.pack(fill="x", pady=5)

tk.Button(c2, text="Ziel auswählen", command=select_dest).pack(anchor="w")


c3 = card(main)

tk.Label(c3, text="Modus", bg="white").pack(anchor="w")

tk.Radiobutton(c3, text="Ordner", variable=mode_var, value="directory").pack(anchor="w")
tk.Radiobutton(c3, text="Dateien", variable=mode_var, value="files").pack(anchor="w")


c4 = card(main)

tk.Label(c4, text="Transfer", bg="white").pack(anchor="w")

tk.Radiobutton(c4, text="Copy", variable=transfer_mode, value="copy").pack(anchor="w")
tk.Radiobutton(c4, text="Move", variable=transfer_mode, value="move").pack(anchor="w")


# -----------------------------
# PROGRESS BAR
# -----------------------------
tk.Label(main, text="Fortschritt", bg="#f4f6f8").pack(anchor="w")

ttk.Progressbar(
    main,
    variable=progress_var,
    maximum=100
).pack(fill="x", pady=10)


tk.Button(
    main,
    text="Start Transfer",
    bg="#1f6feb",
    fg="white",
    height=2,
    command=start_transfer
).pack(fill="x", pady=15)


root.mainloop()