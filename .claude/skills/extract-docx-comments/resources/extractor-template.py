"""
Boilerplate: Trích xuất Comments + Strikethrough (kèm ngữ cảnh) +
             Tracked Changes (w:ins/w:del) + Highlights + Colored Text +
             Comment Map từ file .docx
Chạy qua: python3 - << 'PYEOF' ... PYEOF
"""
import zipfile
import xml.etree.ElementTree as ET
from docx import Document
import re

DOCX_PATH = "/path/to/file.docx"          # ← thay đường dẫn thực tế
REVIEWER_COLORS = {"EE0000", "FF0000", "C00000"}  # ← màu chữ reviewer, điều chỉnh nếu cần

NS  = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W   = f'{{{NS["w"]}}}'          # shorthand: {http://...main}


# ══════════════════════════════════════════════════════════════════════════════
# 1. COMMENTS  (đọc trực tiếp word/comments.xml qua zipfile)
# ══════════════════════════════════════════════════════════════════════════════
comments = {}
tracked_changes = []   # sẽ fill ở bước 2

with zipfile.ZipFile(DOCX_PATH) as z:
    namelist = z.namelist()

    # -- 1a. Comments ----------------------------------------------------------
    if "word/comments.xml" not in namelist:
        print("ℹ️  File không có word/comments.xml – bỏ qua phần comment.")
    else:
        root = ET.fromstring(z.read("word/comments.xml"))
        for c in root.findall("w:comment", NS):
            cid    = c.get(f"{W}id")
            author = c.get(f"{W}author", "")
            date   = c.get(f"{W}date", "")[:10]        # YYYY-MM-DD
            texts  = [r.text or "" for r in c.iter(f"{W}t")]
            comments[cid] = {
                "author": author,
                "date":   date,
                "text":   " ".join(texts).strip(),
            }

    # -- 1b. Tracked Changes: w:ins / w:del (đọc word/document.xml) -----------
    # QUAN TRỌNG: w:del dùng thẻ w:delText, KHÔNG phải w:t
    if "word/document.xml" in namelist:
        doc_xml = ET.fromstring(z.read("word/document.xml"))

        for ins in doc_xml.iter(f"{W}ins"):
            author = ins.get(f"{W}author", "")
            date   = ins.get(f"{W}date", "")[:10]
            text   = "".join(t.text or "" for t in ins.iter(f"{W}t")).strip()
            if text:
                tracked_changes.append({
                    "type": "INSERT", "author": author,
                    "date": date,     "text": text,
                })

        for dele in doc_xml.iter(f"{W}del"):
            author = dele.get(f"{W}author", "")
            date   = dele.get(f"{W}date", "")[:10]
            # w:del → w:delText  (khác w:t !)
            text   = "".join(t.text or "" for t in dele.iter(f"{W}delText")).strip()
            if text:
                tracked_changes.append({
                    "type": "DELETE", "author": author,
                    "date": date,     "text": text,
                })


# ══════════════════════════════════════════════════════════════════════════════
# Helpers dùng chung
# ══════════════════════════════════════════════════════════════════════════════
doc = Document(DOCX_PATH)


def _get_run_color(run) -> str | None:
    """Trả về hex color (uppercase) của run, hoặc None nếu không có / là màu đen."""
    rPr = run._element.find(f"{W}rPr")
    if rPr is None:
        return None
    color_el = rPr.find(f"{W}color")
    if color_el is None:
        return None
    val = color_el.get(f"{W}val", "").upper()
    return val if val and val not in {"000000", "AUTO", ""} else None


def _iter_all_paragraphs():
    """
    Yield (para, source_label) theo đúng thứ tự xuất hiện trong tài liệu,
    bao gồm cả paragraph trong table cell.
    Dùng body.iterchildren() để giữ thứ tự xen kẽ paragraph/table.
    """
    body = doc.element.body
    for child in body.iterchildren():
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag == "p":
            from docx.text.paragraph import Paragraph
            yield Paragraph(child, doc), "paragraph"
        elif tag == "tbl":
            from docx.table import Table
            tbl = Table(child, doc)
            for row in tbl.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        yield para, "table"


# ══════════════════════════════════════════════════════════════════════════════
# 2. STRIKETHROUGH  (kèm ngữ cảnh đoạn văn)
# ══════════════════════════════════════════════════════════════════════════════
strikes = []

for para, source in _iter_all_paragraphs():
    struck = [r.text for r in para.runs if r.font.strike and r.text.strip()]
    if struck:
        strikes.append({
            "source":  source,
            "text":    " ".join(struck),
            "context": para.text,          # ← toàn bộ đoạn văn chứa phần gạch bỏ
        })


# ══════════════════════════════════════════════════════════════════════════════
# 3. HIGHLIGHTS  (bôi màu, nhóm theo paragraph)
# ══════════════════════════════════════════════════════════════════════════════
highlights = []

for para, source in _iter_all_paragraphs():
    hl_runs = [r for r in para.runs if r.font.highlight_color is not None and r.text.strip()]
    if not hl_runs:
        continue
    color = str(hl_runs[0].font.highlight_color)       # tên màu (vd: "YELLOW")
    highlights.append({
        "source":  source,
        "color":   color,
        "text":    " ".join(r.text for r in hl_runs),
        "context": para.text,
    })


# ══════════════════════════════════════════════════════════════════════════════
# 4. COLORED TEXT  (màu chữ của reviewer)
# ══════════════════════════════════════════════════════════════════════════════
colored_runs = []

for para, source in _iter_all_paragraphs():
    for run in para.runs:
        if not run.text.strip():
            continue
        color = _get_run_color(run)
        if color and color in REVIEWER_COLORS:
            colored_runs.append({
                "source":  source,
                "color":   color,
                "text":    run.text,
                "context": para.text,
            })


# ══════════════════════════════════════════════════════════════════════════════
# 5. COMMENT MAP + ANCHORED TEXT
# ══════════════════════════════════════════════════════════════════════════════
# comment_map: cid → (source_type, paragraph_text)
# comment_anchor: cid → text bị comment (phần được chọn trong Word)

comment_map = {}
comment_anchor = {}  # ← MỚI: text cụ thể bị comment, không phải cả đoạn văn

for para, source in _iter_all_paragraphs():
    xml_str = para._element.xml
    if "commentRangeStart" not in xml_str:
        continue
    ids = re.findall(r'commentRangeStart[^>]+w:id="(\d+)"', xml_str)
    for cid in ids:
        comment_map[cid] = (source, para.text)


def _extract_anchored_text(doc_xml_bytes: bytes) -> dict:
    """
    Trả về dict: comment_id (str) → text được anchor (phần văn bản bị comment).
    Dùng commentRangeStart / commentRangeEnd để xác định phạm vi chính xác.
    Bỏ qua w:delText để không lẫn text bị xóa vào anchor.
    """
    root = ET.fromstring(doc_xml_bytes)
    W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    W_TAG = f"{{{W_NS}}}"
    collecting: dict[str, list[str]] = {}
    anchors: dict[str, str] = {}

    def _walk(elem, in_del: bool = False):
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        if tag == "commentRangeStart":
            cid = elem.get(f"{W_TAG}id")
            if cid:
                collecting[cid] = []
        elif tag == "commentRangeEnd":
            cid = elem.get(f"{W_TAG}id")
            if cid in collecting:
                anchors[cid] = "".join(collecting.pop(cid)).strip()
        elif tag == "del":
            # Các con của w:del là w:delText — bỏ qua để không lẫn text xóa
            for child in elem:
                _walk(child, in_del=True)
            return
        elif tag == "t" and not in_del:
            text = elem.text or ""
            for cid in list(collecting.keys()):
                collecting[cid].append(text)
        for child in elem:
            _walk(child, in_del)

    _walk(root)
    return anchors


with zipfile.ZipFile(DOCX_PATH) as z:
    if "word/document.xml" in z.namelist():
        comment_anchor = _extract_anchored_text(z.read("word/document.xml"))


# ══════════════════════════════════════════════════════════════════════════════
# 6. OUTPUT
# ══════════════════════════════════════════════════════════════════════════════
print(
    f"📋 {len(comments)} comments | "
    f"✂️  {len(strikes)} đoạn gạch bỏ | "
    f"🔄 {len(tracked_changes)} tracked changes | "
    f"🟡 {len(highlights)} đoạn highlight | "
    f"🔴 {len(colored_runs)} colored runs | "
    f"🔗 {len(comment_map)} comment đã map"
)
print("=" * 70)

# ── Comments ──────────────────────────────────────────────────────────────────
if comments:
    print("\n### COMMENTS\n")
    for cid in sorted(comments.keys(), key=lambda x: int(x)):
        info = comments[cid]
        loc  = comment_map.get(cid)
        loc_type = loc[0] if loc else "?"
        # Anchored text: đúng đoạn text bị comment (ưu tiên hơn paragraph text)
        anchor = comment_anchor.get(cid, "")
        # Paragraph context: cắt tối đa 200 ký tự là chấp nhận được
        loc_text = (loc[1][:200] + "…") if loc and len(loc[1]) > 200 else (loc[1] if loc else "(không map được)")
        # QUAN TRỌNG: body comment KHÔNG được cắt — phải in toàn bộ
        body = info["text"] or "[trống – có thể là placeholder]"
        print(f"[C{cid}] {info['author']} – {info['date']}")
        if anchor:
            print(f"  Comment về: \"{anchor}\"")       # ← text cụ thể bị comment
        print(f"  Trong đoạn ({loc_type}): \"{loc_text}\"")
        print(f"  Nội dung: {body}")  # ← toàn bộ text, không cắt
        print()

# ── Strikethrough ─────────────────────────────────────────────────────────────
if strikes:
    print("\n### GẠCH BỎ (Strikethrough)\n")
    for i, s in enumerate(strikes, 1):
        print(f"[S{i}] ({s['source']}) Gạch bỏ: \"{s['text']}\"")
        print(f"  Ngữ cảnh: \"{s['context']}\"")
        print()

# ── Tracked Changes ───────────────────────────────────────────────────────────
if tracked_changes:
    print("\n### TRACKED CHANGES (w:ins / w:del)\n")
    for i, tc in enumerate(tracked_changes, 1):
        print(f"[TC{i}] {tc['type']} | {tc['author']} – {tc['date']}")
        print(f"  Text: \"{tc['text']}\"")
        print()

# ── Highlights ────────────────────────────────────────────────────────────────
if highlights:
    print("\n### HIGHLIGHTS (bôi màu)\n")
    for i, h in enumerate(highlights, 1):
        print(f"[H{i}] ({h['source']}) [{h['color']}] {h['text']}")
        print(f"  Ngữ cảnh: \"{h['context']}\"")
        print()

# ── Colored Text ──────────────────────────────────────────────────────────────
if colored_runs:
    print("\n### COLORED TEXT (màu reviewer)\n")
    for i, cr in enumerate(colored_runs, 1):
        print(f"[CR{i}] #{cr['color']} ({cr['source']}): \"{cr['text']}\"")
        print(f"  Ngữ cảnh: \"{cr['context']}\"")
        print()
