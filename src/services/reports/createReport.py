#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KOST-Val Log-XML (KOSTValLog) -> lesbarer HTML-Report (paper-like)

Workflow:
- Lege *.kost-val.log.xml in den gleichen Ordner wie dieses Script
- Starte: python kostval_logs_to_reports.py
- Output: ./reports (im Script-Ordner), inkl. index.html
"""

from __future__ import annotations

import html
import tkinter as tk
from tkinter import filedialog, simpledialog
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import xml.etree.ElementTree as ET


# -----------------------------
# Datenmodelle
# -----------------------------

@dataclass
class LogError:
    module: str
    messages: List[str] = field(default_factory=list)

@dataclass
class ValidationEntry:
    val_type: str
    val_file: str
    format_vl: Optional[str] = None
    status: str = "unknown"  # valid | invalid | warning | accepted | unknown
    warnings_count: int = 0
    errors: List[LogError] = field(default_factory=list)

@dataclass
class KostValReport:
    source_path: str
    start: Optional[str] = None
    end: Optional[str] = None
    summary: Optional[str] = None
    format_val_on: Optional[str] = None
    format_rec_on: Optional[str] = None
    info_text: Optional[str] = None
    configuration: Optional[str] = None
    format_validations: List[ValidationEntry] = field(default_factory=list)
    sip_validation: Optional[ValidationEntry] = None


# -----------------------------
# XML Helpers
# -----------------------------

def _safe_text(s: Optional[str]) -> str:
    return (s or "").strip()

def _find_text(parent: ET.Element, path: str) -> str:
    el = parent.find(path)
    return _safe_text(el.text if el is not None else "")

def _parse_xml_resilient(path: Path) -> ET.Element:
    """
    Robust gegen ISO-8859-1 / cp1252 / utf-8 (KOST-Logs sind oft nicht UTF-8).
    """
    try:
        tree = ET.parse(path)
        return tree.getroot()
    except ET.ParseError:
        pass

    data = path.read_bytes()
    for enc in ("utf-8", "iso-8859-1", "cp1252"):
        try:
            text = data.decode(enc)
            return ET.fromstring(text)
        except Exception:
            continue

    raise ValueError(f"Konnte XML nicht parsen: {path}")


# -----------------------------
# KOST-Val Parsing
# -----------------------------

def _detect_status(v: ET.Element) -> Tuple[str, int]:
    warnings = len(v.findall("Warning"))
    if v.find("Invalid") is not None:
        return ("invalid", warnings)
    if warnings > 0:
        return ("warning", warnings)
    if v.find("Valid") is not None:
        return ("valid", warnings)
    if v.find("Accepted") is not None:
        return ("accepted", warnings)
    return ("unknown", warnings)

def _parse_validation(v: ET.Element) -> ValidationEntry:
    status, warnings_count = _detect_status(v)

    entry = ValidationEntry(
        val_type=_find_text(v, "ValType"),
        val_file=_find_text(v, "ValFile"),
        format_vl=_safe_text(_find_text(v, "FormatVL")) or None,
        status=status,
        warnings_count=warnings_count,
    )

    for err in v.findall("Error"):
        module = _find_text(err, "Modul")
        msgs = [_safe_text(m.text) for m in err.findall("Message") if _safe_text(m.text)]
        if module or msgs:
            entry.errors.append(LogError(module=module, messages=msgs))

    return entry

def parse_kostval_log(xml_path: Path) -> KostValReport:
    root = _parse_xml_resilient(xml_path)

    report = KostValReport(source_path=str(xml_path))
    if root.tag != "KOSTValLog":
        return report

    infos = root.find("Infos")
    if infos is not None:
        report.start = _find_text(infos, "Start") or None
        report.end = _find_text(infos, "End") or None
        report.format_val_on = _find_text(infos, "FormatValOn") or None
        report.format_rec_on = _find_text(infos, "FormatRecOn") or None
        report.info_text = _find_text(infos, "Info") or None

    report.configuration = _safe_text(_find_text(root, "configuration")) or None

    fmt = root.find("Format")
    if fmt is not None:
        report.summary = _find_text(fmt, "Infos/Summary") or None
        for v in fmt.findall("Validation"):
            report.format_validations.append(_parse_validation(v))

    sip = root.find("Sip")
    if sip is not None:
        v = sip.find("Validation")
        if v is not None:
            report.sip_validation = _parse_validation(v)

    return report


# -----------------------------
# HTML Rendering (paper-like)
# -----------------------------

def _esc(s: str) -> str:
    return html.escape(s, quote=True)

def _file_name(p: str) -> str:
    return Path(p).name if p else ""

def _join_val_label(v: ValidationEntry) -> str:
    # Im PDF steht z.B.: "Validierung: PDFA-2U -> <pfad>"
    fmt = (v.format_vl or "").strip()
    return f"{v.val_type}{fmt}"

def _badge(status: str, warnings_count: int) -> str:
    if status == "valid":
        return '<span class="badge ok">valid</span>'
    if status == "accepted":
        return '<span class="badge ok">accepted</span>'
    if status == "invalid":
        return '<span class="badge bad">invalid</span>'
    if status == "warning":
        return f'<span class="badge warn">warning ({warnings_count})</span>'
    return '<span class="badge unk">unknown</span>'

def _render_messages(messages: List[str]) -> str:
    if not messages:
        return ""
    items = "".join(f"<li>{_esc(m)}</li>" for m in messages)
    return f"<ul class='msglist'>{items}</ul>"

def _render_entry_block(v: ValidationEntry, collapsible: bool, default_open: bool, with_details: bool) -> str:
    title = f"{_esc(_join_val_label(v))} <span class='arrow'>→</span> <span class='path'>{_esc(v.val_file)}</span>"
    status_html = _badge(v.status, v.warnings_count)

    # Nicht-collapsible (z.B. Valid): nur Kopfzeile, keine Details
    if not collapsible:
        return f"""
<div class="entry">
  <div class="entry-head">
    <div class="entry-title">{title}</div>
    <div class="entry-status">{status_html}</div>
  </div>
</div>
"""

    # Collapsible (Invalid/Warnung/Unknown) als <details>, default geschlossen
    open_attr = "open" if default_open else ""
    body_html = ""
    if with_details and v.errors:
        parts = ["<div class='entry-body'>"]
        for e in v.errors:
            mod = _esc(e.module) if e.module else "Fehler"
            parts.append(f"<div class='module'>{mod}</div>")
            parts.append(_render_messages(e.messages))
        parts.append("</div>")
        body_html = "\n".join(parts)

    return f"""
<details class="entry" {open_attr}>
  <summary>
    <div class="entry-title">{title}</div>
    <div class="entry-status">{status_html}</div>
  </summary>
  {body_html if body_html else "<div class='entry-body small'>Keine Detailmeldungen vorhanden.</div>"}
</details>
"""


CSS = r"""
:root{
  --bg: #0b0f14;
  --paper: #0f1622;
  --paper-border: rgba(255,255,255,.08);
  --text: #eaf2ff;
  --muted: rgba(234,242,255,.70);
  --rule: rgba(255,255,255,.10);

  --ok: #2fbf71;
  --warn: #ffb020;
  --bad: #ff4d4f;
  --unk: rgba(234,242,255,.55);

  --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  --sans: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
}

/* Light theme (nahe am PDF) */
html[data-theme="light"]{
  --bg: #f2f4f7;
  --paper: #ffffff;
  --paper-border: rgba(0,0,0,.10);
  --text: #111827;
  --muted: rgba(17,24,39,.70);
  --rule: rgba(0,0,0,.10);

  --ok: #0f7a3a;
  --warn: #b45309;
  --bad: #b91c1c;
  --unk: rgba(17,24,39,.60);
}

*{box-sizing:border-box}
body{
  margin:0;
  background:var(--bg);
  color:var(--text);
  font-family:var(--sans);
  font-size:16px;           
  line-height:1.65;            
}

.wrap{
  max-width: 980px;       
  margin: 0 auto;
  padding: 24px 18px 40px;
}

.paper{
  background: var(--paper);
  border: 1px solid var(--paper-border);
  border-radius: 14px;
  padding: 22px 22px 18px;
  box-shadow: 0 10px 35px rgba(0,0,0,.25);
}

.header{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:16px;
  margin-bottom: 10px;
}

h1{
  margin:0;
  font-size:22px;
  line-height:1.2;
}

.meta{
  margin-top:6px;
  font-size:13px;
  color:var(--muted);
}

.toolbar{
  display:flex;
  gap:10px;
  align-items:center;
  justify-content:flex-end;
}

button{
  border: 1px solid var(--paper-border);
  background: transparent;
  color: var(--text);
  padding: 8px 10px;
  border-radius: 10px;
  font-size:13px;
  cursor:pointer;
}
button:hover{ filter: brightness(1.08); }

hr{
  border:none;
  border-top:1px solid var(--rule);
  margin: 14px 0;
}

.section-title{
  font-weight:800;
  margin: 18px 0 8px;
  font-size:17px;
}

.kv{
  display:grid;
  grid-template-columns: 110px 1fr;
  gap: 10px 14px;
  font-size:14px;
}
.kv .k{ color:var(--muted); font-weight:700; }
.kv .v{ color:var(--text); }

.badge{
  display:inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  font-size:12px;
  font-weight:800;
  border: 1px solid var(--paper-border);
  white-space:nowrap;
}
.badge.ok{ color: var(--ok); background: color-mix(in srgb, var(--ok) 15%, transparent); }
.badge.warn{ color: var(--warn); background: color-mix(in srgb, var(--warn) 15%, transparent); }
.badge.bad{ color: var(--bad); background: color-mix(in srgb, var(--bad) 15%, transparent); }
.badge.unk{ color: var(--unk); background: rgba(127,127,127,.10); }

.toc{
  display:flex;
  flex-wrap:wrap;
  gap:10px;
  margin-top: 10px;
  font-size:13px;
}
.toc a{
  color: var(--text);
  text-decoration:none;
  border: 1px solid var(--paper-border);
  padding: 6px 10px;
  border-radius: 999px;
}
.toc a:hover{ filter: brightness(1.10); }

.entry{
  border-top: 1px solid var(--rule);
  padding: 12px 0;
}
.entry:first-child{ border-top:none; padding-top: 0; }
.entry-head{
  display:flex;
  gap:12px;
  align-items:flex-start;
  justify-content:space-between;
}
.entry-title{
  font-weight:800;
  font-size:15px;
}
.entry-title .arrow{ opacity:.55; padding: 0 4px; }
.path{
  font-family: var(--mono);
  font-weight: 600;
  font-size: 13px;
  color: var(--muted);
  word-break: break-all;
}
.entry-status{ margin-top: 2px; }

.entry-body{
  margin-top: 10px;
  padding-left: 10px;
}
.module{
  font-weight: 800;
  margin-top: 10px;
}
.msglist{
  margin: 6px 0 0 20px;
}
.msglist li{
  margin: 4px 0;
  color: var(--text);
}

.small{
  font-size:13px;
  color: var(--muted);
}

/* Farbige Streifen für Abschnittsüberschriften */
.band{
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid var(--paper-border);
  margin-top: 18px;
  margin-bottom: 8px;
}
.band.invalid{
  background: color-mix(in srgb, var(--bad) 18%, transparent);
}
.band.valid{
  background: color-mix(in srgb, var(--ok) 18%, transparent);
}
.band.warning{
  background: color-mix(in srgb, var(--warn) 18%, transparent);
}

/* Details als "auf/zu"-Container pro Eintrag */
details.entry{
  border-top: 1px solid var(--rule);
  padding: 10px 0;
}
details.entry:first-child{ border-top:none; padding-top: 0; }

details.entry > summary{
  list-style: none;
  cursor: pointer;
  display:flex;
  gap:12px;
  align-items:flex-start;
  justify-content:space-between;
}
details.entry > summary::-webkit-details-marker{ display:none; }

details.entry > summary .entry-title{
  font-weight:800;
  font-size:15px;
}
details.entry > summary .arrow{ opacity:.55; padding: 0 4px; }

details.entry[open] > summary{
  padding-bottom: 6px;
}


/* Print: sauber wie ein Report */
@media print {
  body{ background:#fff; }
  .wrap{ max-width: none; padding: 0; }
  .paper{ border: none; border-radius: 0; box-shadow: none; padding: 0; }
  .toolbar, .toc{ display:none !important; }
  .path{ color: #111 !important; }
}
"""

JS = r"""
(function(){
  const root = document.documentElement;
  const saved = localStorage.getItem("kostval-theme");
  if(saved){ root.setAttribute("data-theme", saved); }

  window.toggleTheme = function(){
    const cur = root.getAttribute("data-theme") || "dark";
    const next = (cur === "dark") ? "light" : "dark";
    root.setAttribute("data-theme", next);
    localStorage.setItem("kostval-theme", next);
  }
})();
"""

def render_html(report: KostValReport) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    src_name = Path(report.source_path).name
    title = f"KOST-Val Report – {src_name}"

    vals = report.format_validations[:]
    invalid = [v for v in vals if v.status == "invalid"]
    warning = [v for v in vals if v.status == "warning"]
    ok = [v for v in vals if v.status in ("valid", "accepted")]
    unk = [v for v in vals if v.status == "unknown"]

    sip_line = "—"
    sip_status_badge = '<span class="badge unk">unknown</span>'
    if report.sip_validation:
        sip_line = report.sip_validation.val_file or "—"
        sip_status_badge = _badge(report.sip_validation.status, report.sip_validation.warnings_count)

    summary_text = report.summary or "—"

    # Kopf / Summary 
    html_out = f"""<!doctype html>
<html lang="de" data-theme="dark">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{_esc(title)}</title>
  <style>{CSS}</style>
</head>
<body>
  <div class="wrap">
    <div class="paper">
      <div class="header">
        <div>
          <h1>{_esc(title)}</h1>
          <div class="meta">Generiert am {now} • Quelle: <span class="path">{_esc(report.source_path)}</span></div>
        </div>
        <div class="toolbar">
          <button onclick="toggleTheme()">Dark/Light</button>
          <button onclick="window.print()">Drucken / PDF</button>
        </div>
      </div>

      <div class="toc">
        <a href="#summary">Übersicht</a>
        <a href="#invalid">Invalid ({len(invalid)})</a>
        <a href="#warning">Warning ({len(warning)})</a>
        <a href="#valid">Valid ({len(ok)})</a>
        {("<a href='#unknown'>Unknown (" + str(len(unk)) + ")</a>") if unk else ""}
      </div>

      <hr/>

      <div id="summary" class="section-title">Übersicht (Summary)</div>
      <div class="kv">
        <div class="k">SIP</div><div class="v">{_esc(_file_name(sip_line))} <span class="small">({_esc(sip_line)})</span></div>
        <div class="k">SIP-Status</div><div class="v">{sip_status_badge}</div>

        <div class="k">Formatvalidierung</div><div class="v">{_esc(summary_text)}</div>

        <div class="k">Validierung</div><div class="v">{_esc(report.format_val_on or "—")}</div>
        <div class="k">Erkennung</div><div class="v">{_esc(report.format_rec_on or "—")}</div>

        <div class="k">Start</div><div class="v">{_esc(report.start or "—")}</div>
        <div class="k">Ende</div><div class="v">{_esc(report.end or "—")}</div>
      </div>
"""

    if report.info_text:
        html_out += f"<hr/><div class='small'>{_esc(report.info_text)}</div>"

    if report.configuration:
        html_out += (
            "<hr/>"
            "<details><summary><strong>Konfiguration (ausklappen)</strong></summary>"
            f"<pre style='white-space:pre-wrap;font-family:var(--mono);font-size:13px;color:var(--muted);margin:10px 0 0'>{_esc(report.configuration)}</pre>"
            "</details>"
        )

    html_out += "<hr/>"

    # Invalid (togglebar, default zu)
    html_out += f"""
      <div id="invalid" class="section-title band invalid">Invalid:</div>
      {("".join(_render_entry_block(v, collapsible=True, default_open=False, with_details=True) for v in invalid)
        if invalid else "<div class='small'>Keine invaliden Einträge.</div>")}
      <hr/>
"""

    # Warning (togglebar, default zu)
    html_out += f"""
      <div id="warning" class="section-title band warning">Warning:</div>
      {("".join(_render_entry_block(v, collapsible=True, default_open=False, with_details=True) for v in warning)
        if warning else "<div class='small'>Keine Warnungen.</div>")}
      <hr/>
"""

    # Valid (nicht togglebar, nur Zeilen)
    html_out += f"""
      <div id="valid" class="section-title band valid">Valid:</div>
      {("".join(_render_entry_block(v, collapsible=False, default_open=False, with_details=False) for v in ok)
        if ok else "<div class='small'>Keine validen Einträge.</div>")}
"""

    # Optional: Unknown (togglebar)
    if unk:
        html_out += f"""
      <hr/>
      <div id="unknown" class="section-title">Unknown:</div>
      {("".join(_render_entry_block(v, collapsible=True, default_open=False, with_details=True) for v in unk))}
"""

    # Footer 
    html_out += f"""
    </div>
  </div>

  <script>{JS}</script>
</body>
</html>
"""
    return html_out


# -----------------------------
# I/O
# -----------------------------

def write_report(xml_path: Path, out_dir: Path) -> Path:
    user_input = simpledialog.askstring("Dateiname", "Bitte den Dateinamen eingeben:")
    report = parse_kostval_log(xml_path)
    html_str = render_html(report)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (f"{user_input}.html")
    out_path.write_text(html_str, encoding="utf-8")
    return out_path

def create_report() -> int:
    # tkinter Root initialisieren (wird für FileDialog benötigt)
    root = tk.Tk()
    root.withdraw()

    # Datei auswählen
    xml_file = filedialog.askopenfilename(
        title="Wähle eine KOST-Val Log-Datei aus",
        filetypes=[("KOST-Val Log XML", "*.kost-val.log.xml"), ("Alle Dateien", "*.*")]
    )

    if not xml_file:
        print("Keine Datei ausgewählt. Abbruch.")
        return 1

    xml_path = Path(xml_file).resolve()
    out_dir = (Path.cwd().parent / "reports").resolve()

    generated: List[Path] = []

    try:
        generated.append(write_report(xml_path, out_dir))
    except Exception as ex:
        out_dir.mkdir(parents=True, exist_ok=True)
        err_path = out_dir / (xml_path.stem + ".ERROR.txt")
        err_path.write_text(f"Fehler beim Verarbeiten von {xml_path}:\n{ex}\n", encoding="utf-8")

    print(f"Fertig. Report erzeugt für: {xml_path.name}")
    print(f"Output-Ordner: {out_dir}")
    return 0