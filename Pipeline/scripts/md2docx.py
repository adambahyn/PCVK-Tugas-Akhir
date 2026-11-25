"""md2docx.py — konversi markdown sederhana ke .docx (headings, bullet, tabel, bold, code).

Dipakai untuk Laporan/Penjelasan_Santai_Pipeline.md.
Pemakaian: python Pipeline/scripts/md2docx.py <input.md> <output.docx>
"""

import re
import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`)")


def add_runs(par, text):
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            par.add_run(part[2:-2]).bold = True
        elif part.startswith("`") and part.endswith("`"):
            run = par.add_run(part[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(9.5)
        else:
            par.add_run(part)


def add_table(doc, rows):
    rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
    width = max(len(r) for r in rows)
    table = doc.add_table(rows=0, cols=width)
    table.style = "Light Grid Accent 1"
    for i, r in enumerate(rows):
        cells = table.add_row().cells
        for j in range(width):
            cells[j].text = ""
            add_runs(cells[j].paragraphs[0], r[j] if j < len(r) else "")
            if i == 0:
                for run in cells[j].paragraphs[0].runs:
                    run.bold = True
    doc.add_paragraph()


def convert(src: Path, dst: Path):
    lines = src.read_text(encoding="utf-8").splitlines()
    doc = Document()
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(11)
    for section in doc.sections:
        section.left_margin = section.right_margin = Cm(2.2)

    i, in_code, quote = 0, False, []
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            doc.add_paragraph(line, style="No Spacing").runs[0].font.name = "Consolas"
            i += 1
            continue
        if not stripped or stripped == "---":
            i += 1
            continue
        if stripped.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            add_table(doc, block)
            continue
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            doc.add_heading(stripped[level:].strip(), level=min(level, 4))
            i += 1
            continue
        if stripped.startswith(">"):
            quote.append(stripped.lstrip("> ").strip())
            if i + 1 == len(lines) or not lines[i + 1].strip().startswith(">"):
                for q in quote:
                    par = doc.add_paragraph(style="Intense Quote")
                    add_runs(par, q)
                quote = []
            i += 1
            continue
        if re.match(r"^([-*]|\d+\.)\s+", stripped):
            body = re.sub(r"^([-*]|\d+\.)\s+", "", stripped)
            par = doc.add_paragraph(style="List Bullet" if not stripped[0].isdigit() else "List Number")
            add_runs(par, body)
            i += 1
            continue

        par = doc.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_runs(par, stripped)
        i += 1

    dst.parent.mkdir(parents=True, exist_ok=True)
    doc.save(dst)
    return dst


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("pemakaian: python md2docx.py <input.md> <output.docx>")
    print(convert(Path(sys.argv[1]), Path(sys.argv[2])))
