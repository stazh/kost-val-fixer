import json
import os
import subprocess
import tkinter as tk
import threading
from tkinter import ttk, messagebox

# =====================================================
# APP
# =====================================================
root = tk.Tk()
root.title("Interface Kost Val Fixer and Create SIP")
root.geometry("1200x960")
root.configure(bg="#eef2f7")

# =====================================================
# SCROLLABLE MAIN AREA
# =====================================================
canvas = tk.Canvas(root, bg="#eef2f7", highlightthickness=0)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scroll_frame = tk.Frame(canvas, bg="#eef2f7")

scroll_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

container = tk.Frame(scroll_frame, bg="#eef2f7")
container.pack(fill="both", expand=True, padx=20, pady=20)

# =====================================================
# GLOBAL DATA
# =====================================================
data_step3 = []
data_step5_validate = []
data_step4_convert = []

# =====================================================
# FILTER
# =====================================================
def filter_tree(tree, data, col, value):
    tree.delete(*tree.get_children())

    for item in data:
        if value == "ALL" or item[col] == value:
            tree.insert("", "end", values=item)

# =====================================================
# LOAD DATA
# =====================================================
def load_data():
    global data_step3, data_step5_validate, data_step4_convert

    path = os.path.join(os.path.expanduser("~"), "DATA_KOST_VAL_FIXER", "data.json")

    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as f:
        content = json.load(f)

    data_step3 = content.get("first_validation", [])
    data_step5_validate = content.get("second_validation", [])
    data_step4_convert = content.get("converted_files", [])

# =====================================================
# DOUBLE CLICK HANDLER
# =====================================================

def on_double_click(event):
    tree = event.widget

    row = tree.identify_row(event.y)
    col = tree.identify_column(event.x)

    if not row:
        return

    values = tree.item(row, "values")

    # Datei-Spalte
    if col == "#1":
        file_path = values[0]

        folder = os.path.dirname(file_path)

        subprocess.run(["explorer", folder])

    elif col == "#3":
        text = values[2]

        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()

        messagebox.showinfo("Kopiert", "Text kopiert")

# =====================================================
# REFRESH UI (IMPORTANT FIX)
# =====================================================
def refresh_ui():
    apply_step3()
    apply_step4()
    apply_step5()

# =====================================================
# RUN COMMAND
# =====================================================
def run_cmd(command):
    def worker():
        try:
            subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )

            root.after(0, lambda: [
                load_data(),
                refresh_ui(),
                messagebox.showinfo("OK", "Fertig ausgeführt")
            ])

        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Fehler", str(e)))

    threading.Thread(target=worker, daemon=True).start()

# =====================================================
# CARD UI
# =====================================================
def card(title):
    frame = tk.Frame(container, bg="white", bd=1, relief="solid")
    frame.pack(fill="x", pady=10)

    header = tk.Frame(frame, bg="#2f80ed")
    header.pack(fill="x")

    tk.Label(
        header,
        text=title,
        bg="#2f80ed",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        padx=10,
        pady=8
    ).pack(side="left")

    body = tk.Frame(frame, bg="white")
    body.pack(fill="both", padx=10, pady=10)

    return body

# =====================================================
# STEP 1
# =====================================================
b1 = card("Schritt 1: Kopie der Daten erstellen")

tk.Button(
    b1,
    text="Kopie erstellen",
    bg="#2f80ed",
    fg="white",
    command=lambda: run_cmd(".venv\\Scripts\\python.exe main.pyz rclone")
).pack(anchor="w")

# =====================================================
# STEP 2
# =====================================================
b2 = card("Schritt 2: Umlaute entfernen")

tk.Button(
    b2,
    text="Umlaute entfernen",
    bg="#2f80ed",
    fg="white",
    command=lambda: run_cmd(".venv\\Scripts\\python.exe main.pyz normalize")
).pack(anchor="w")

# =====================================================
# STEP 3
# =====================================================
b3 = card("Schritt 3: Dateien validieren")

row = tk.Frame(b3, bg="white")
row.pack(fill="x")

tk.Button(
    row,
    text="Dateien validieren",
    bg="#2f80ed",
    fg="white",
    command=lambda: run_cmd(".venv\\Scripts\\python.exe main.pyz validate")
).pack(side="left")

tk.Button(
    row,
    text="Report erstellen",
    bg="#205ba8",
    fg="white",
    command=lambda: run_cmd(".venv\\Scripts\\python.exe main.pyz create-report")
).pack(side="right")

tree3 = ttk.Treeview(b3, columns=("file", "status", "message"), show="headings", height=6)

tree3.heading("file", text="Datei")
tree3.heading("status", text="Status")
tree3.heading("message", text="Nachricht")

tree3.column("file", width=600)
tree3.column("status", width=100, stretch=False)
tree3.column("message", width=400)

tree3.pack(fill="x", pady=10)

step3_filter = ttk.Combobox(b3, values=["ALL", "Valid", "Accepted", "Invalid", "NotAccepted"])
step3_filter.set("ALL")
step3_filter.pack(anchor="w")

def apply_step3(event=None):
    filter_tree(tree3, data_step3, 1, step3_filter.get())

tree3.bind("<Double-1>", on_double_click)
step3_filter.bind("<<ComboboxSelected>>", apply_step3)
# =====================================================
# STEP 4
# =====================================================
b4 = card("Schritt 4: Formatfehler beheben")

tk.Button(
    b4,
    text="Formatfehler beheben",
    bg="#2f80ed",
    fg="white",
    command=lambda: run_cmd(".venv\\Scripts\\python.exe main.pyz fix-formats")
).pack(anchor="w")

content = tk.Frame(b4, bg="white")
content.pack(fill="both", expand=True)

# =====================================================
# CARD (Konvertierung)
# =====================================================
left_card = tk.Frame(content, bg="white", bd=1, relief="solid")
left_card.pack(fill="x", pady=10)

left_header = tk.Frame(left_card, bg="#2f80ed")
left_header.pack(fill="x")

tk.Label(
    left_header,
    text="Konvertierung",
    bg="#2f80ed",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    padx=10,
    pady=6
).pack(side="left")

left_body = tk.Frame(left_card, bg="white")
left_body.pack(fill="both", padx=10, pady=10)

tree4 = ttk.Treeview(
    left_body,
    columns=("file", "status", "message"),
    show="headings",
    height=6
)

tree4.heading("file", text="Datei")
tree4.heading("status", text="Status")
tree4.heading("message", text="Nachricht")

tree4.column("file", width=600)
tree4.column("status", width=100, stretch=False)
tree4.column("message", width=400)

tree4.pack(fill="x", pady=10)

step4_filter = ttk.Combobox(
    left_body,
    values=["ALL", "Konvertiert", "Fehler", "Nicht unterstützt"]
)
step4_filter.set("ALL")
step4_filter.pack(anchor="w")


def apply_step4(event=None):
    filter_tree(tree4, data_step4_convert, 1, step4_filter.get())

tree4.bind("<Double-1>", on_double_click)
step4_filter.bind("<<ComboboxSelected>>", apply_step4)

# =====================================================
# CARD (Validierung)
# =====================================================
right_card = tk.Frame(content, bg="white", bd=1, relief="solid")
right_card.pack(fill="x", pady=10)

right_header = tk.Frame(right_card, bg="#2f80ed")
right_header.pack(fill="x")

tk.Label(
    right_header,
    text="Validierung",
    bg="#2f80ed",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    padx=10,
    pady=6
).pack(side="left")

right_body = tk.Frame(right_card, bg="white")
right_body.pack(fill="both", padx=10, pady=10)

tree5 = ttk.Treeview(
    right_body,
    columns=("file", "status", "message"),
    show="headings",
    height=6
)

tree5.heading("file", text="Datei")
tree5.heading("status", text="Status")
tree5.heading("message", text="Nachricht")

tree5.column("file", width=600)
tree5.column("status", width=100, stretch=False)
tree5.column("message", width=400)

tree5.pack(fill="x", pady=10)

step5_filter = ttk.Combobox(
    right_body,
    values=["ALL", "Valid", "Accepted", "Invalid", "NotAccepted"]
)
step5_filter.set("ALL")
step5_filter.pack(anchor="w")


def apply_step5(event=None):
    filter_tree(tree5, data_step5_validate, 1, step5_filter.get())

tree5.bind("<Double-1>", on_double_click)
step5_filter.bind("<<ComboboxSelected>>", apply_step5)

# INIT
load_data()
refresh_ui()

root.mainloop()