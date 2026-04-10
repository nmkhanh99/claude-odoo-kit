"""
Table Extractor — Extract table structure from .docx with markup annotations.
Usage: Set DOCX_PATH and TARGET_KEYWORD, then run.
"""
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

DOCX_PATH = "..."            # ← đường dẫn file docx
TARGET_KEYWORD = "Cơ cấu nhân sự"  # ← từ khóa heading/paragraph trước bảng cần tìm
REVIEWER_COLOR = "EE0000"    # ← màu chữ reviewer (hex, không có #)

NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{NS_W}}}"

doc = Document(DOCX_PATH)


def get_cell_text_with_markup(cell):
    """Return cell text with ~~strike~~, [HL:highlight], [NEW:colored] annotations."""
    parts = []
    for para in cell.paragraphs:
        for run in para.runs:
            text = run.text.strip()
            if not text:
                continue
            is_strike = run.font.strike
            rpr = run._element.find(f"{W}rPr")
            color = None
            if rpr is not None:
                col_el = rpr.find(f"{W}color")
                if col_el is not None:
                    val = col_el.get(f"{W}val", "").upper()
                    if val and val not in {"000000", "AUTO"}:
                        color = val
            is_highlight = run.font.highlight_color is not None
            if is_strike:
                parts.append(f"~~{text}~~")
            elif color == REVIEWER_COLOR.upper():
                parts.append(f"[NEW:{text}]")
            elif is_highlight:
                parts.append(f"[HL:{text}]")
            else:
                parts.append(text)
    return " ".join(parts) if parts else ""


def iter_doc_order():
    """Yield (kind, obj) in document order — preserves table/paragraph interleaving."""
    body = doc.element.body
    for child in body.iterchildren():
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag == "p":
            yield "para", Paragraph(child, doc)
        elif tag == "tbl":
            yield "table", Table(child, doc)


found = False
for kind, obj in iter_doc_order():
    if kind == "para" and TARGET_KEYWORD in obj.text:
        found = True
        print(f">>> Section: {obj.text[:80]}")
    elif kind == "table" and found:
        print(f"\n=== Số cột: {len(obj.columns)} | Số dòng: {len(obj.rows)} ===")
        for r_idx, row in enumerate(obj.rows):
            row_data = []
            prev = None
            for cell in row.cells:
                val = get_cell_text_with_markup(cell)
                if val != prev:   # skip duplicate merged cells
                    row_data.append(val)
                prev = val
            print(f"  Row {r_idx}: {' | '.join(row_data)}")
        found = False
