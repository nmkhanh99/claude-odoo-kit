"""
Verify BRD vs DOCX — Báo cáo đầy đủ 10 cột để ra quyết định không cần mở file gốc
Xuất: docs/verify_{MODULE}_{date}.json  →  dùng export-excel tạo .xlsx
"""
import zipfile, xml.etree.ElementTree as ET, re, json
from datetime import date
from docx import Document

DOCX_PATH       = "/path/to/phan-hoi.docx"     # ← file phản hồi
BRD_PATH        = "/path/to/INV-XX.md"          # ← BRD cần verify
MODULE_NAME     = "INV-01"                       # ← tên module
OUTPUT_JSON     = f"docs/verify_{MODULE_NAME}_{date.today()}.json"

# Từ khoá đặc trưng của module — lọc strikes thuộc module này
MODULE_KEYWORDS = ["Thủ kho", "NV kho", "Validate", "Nhân viên kho", "Confirmed",
                   "phê duyệt", "Inventory", "kho"]

# Cặp thuật ngữ để detect logic conflict: (mới, cũ)
TERM_PAIRS = [
    ("3 cấp",   "4 cấp"),
    ("Thủ kho", "Trưởng phòng Kho"),
    ("Quản lý kho tương ứng", "Thủ kho"),
]

# ─────────────────────────────────────────────────────────────────────────────

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W  = f'{{{NS["w"]}}}'

with open(BRD_PATH, encoding="utf-8") as f:
    brd_lines = f.readlines()
brd_text = "".join(brd_lines)

# ── Trích section headings từ BRD ─────────────────────────────────────────────
def get_brd_section(line_no: int) -> str:
    """Tìm heading gần nhất phía trên dòng line_no trong BRD."""
    for i in range(line_no - 2, -1, -1):
        ln = brd_lines[i].strip()
        if ln.startswith("#"):
            return ln.lstrip("#").strip()
    return "(đầu file)"

def find_struck_in_brd(struck: str):
    """(found, line_no, full_line, section)"""
    if len(struck) < 4:
        return False, 0, "", ""
    for i, line in enumerate(brd_lines, 1):
        if struck in line:
            return True, i, line.strip(), get_brd_section(i)
    return False, 0, "", ""

def context_in_brd(context: str, min_chunk: int = 8):
    """(matched, line_no, full_line, section)"""
    words = re.split(r'[\s\-\|→:;,]+', context)
    chunks = []
    for i in range(len(words)):
        for j in range(i + 1, len(words) + 1):
            chunk = " ".join(words[i:j])
            if len(chunk) >= min_chunk:
                chunks.append(chunk)
    for i, line in enumerate(brd_lines, 1):
        for chunk in chunks:
            if chunk in line:
                return True, i, line.strip(), get_brd_section(i)
    return False, 0, "", ""

def suggest_fix(struck: str, context: str) -> str:
    fixed = re.sub(re.escape(struck), "", context).strip()
    fixed = re.sub(r'\s{2,}', ' ', fixed)
    return fixed if fixed and fixed != context.strip() else "(xóa đoạn/ô này)"

def brd_replace_pair(struck: str, brd_line: str) -> tuple[str, str]:
    """Trả về (replace_old, replace_new) — cặp thay thế chính xác trong BRD.
    replace_old = brd_line hiện tại (nguyên văn, bao gồm leading whitespace)
    replace_new = brd_line sau khi xóa struck text
    """
    new_line = re.sub(re.escape(struck), "", brd_line)
    new_line = re.sub(r'\s{2,}', ' ', new_line).strip()
    return brd_line.strip(), new_line if new_line and new_line != brd_line.strip() else "(xóa dòng này)"

# ── Đọc docx ──────────────────────────────────────────────────────────────────
doc = Document(DOCX_PATH)

with zipfile.ZipFile(DOCX_PATH) as z:
    comment_db = {}
    if "word/comments.xml" in z.namelist():
        root = ET.fromstring(z.read("word/comments.xml"))
        for c in root.findall("w:comment", NS):
            cid    = c.get(f"{W}id")
            author = c.get(f"{W}author", "").split("-")[0].strip()  # tên ngắn
            date_  = c.get(f"{W}date", "")[:10]
            texts  = [r.text or "" for r in c.iter(f"{W}t")]
            comment_db[cid] = {
                "author": author,
                "date":   date_,
                "text":   " ".join(texts).strip(),
            }

def _iter_all_paragraphs():
    from docx.text.paragraph import Paragraph
    from docx.table import Table
    for child in doc.element.body.iterchildren():
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag == "p":
            yield Paragraph(child, doc), "paragraph"
        elif tag == "tbl":
            tbl = Table(child, doc)
            for row in tbl.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        yield para, "table"

def get_comments_for_para(para) -> list[dict]:
    xml_str = para._element.xml
    cids    = re.findall(r'commentRangeStart[^>]+w:id="(\d+)"', xml_str)
    result  = []
    for c in cids:
        if c in comment_db:
            cd = comment_db[c]
            result.append({
                "ref":  f"C{c}",
                "who":  f"{cd['author']} – {cd['date']}",
                "text": cd["text"],
            })
    return result

# ── Thu thập strikes ──────────────────────────────────────────────────────────
results = []
issue_id = 1

for para, source in _iter_all_paragraphs():
    struck_runs = [r.text for r in para.runs if r.font.strike and r.text.strip()]
    if not struck_runs:
        continue
    struck_text = " ".join(struck_runs).strip()
    if len(struck_text) < 4:
        continue

    relevant = any(kw.lower() in para.text.lower() for kw in MODULE_KEYWORDS)
    if not relevant:
        continue

    para_comments = get_comments_for_para(para)
    comment_str   = "; ".join(
        f"{c['ref']} ({c['who']}): \"{c['text'][:120]}\""
        for c in para_comments
    ) or "(không có comment — suy luận từ strike)"

    struck_found, s_line, s_brd_full, s_section = find_struck_in_brd(struck_text)
    ctx_found,    c_line, c_brd_full, c_section  = context_in_brd(para.text)

    if not struck_found:
        status     = "✅ Đã sửa"
        issue_type = "✅ Đã sửa"
        brd_line_no, brd_full, section = 0, "(không còn trong BRD)", ""
    elif ctx_found:
        status     = "❌ Lệch"
        issue_type = "❌ Lệch"
        brd_line_no, brd_full, section = s_line, s_brd_full, s_section
    else:
        status     = "⚠️ Cần xác nhận"
        issue_type = "⚠️ Cần xác nhận"
        brd_line_no, brd_full, section = s_line, s_brd_full, s_section

    _brd_line = brd_full or c_brd_full
    _r_old, _r_new = brd_replace_pair(struck_text, _brd_line) if issue_type == "❌ Lệch" else ("", "")

    results.append({
        "id":              issue_id,
        "issue_type":      issue_type,
        "brd_file":        BRD_PATH.split("/")[-1],
        "brd_path":        BRD_PATH,           # đường dẫn đầy đủ cho apply-skill
        "section":         section or c_section,
        "dong_brd":        brd_line_no or c_line,
        "brd_hien_tai":    _brd_line,
        "noi_dung_thay":   struck_text,
        "context_docx":    para.text.strip()[:200],
        "ly_do":           comment_str,
        "replace_old":     _r_old,             # chuỗi cần tìm trong BRD để thay
        "replace_new":     _r_new,             # chuỗi thay thế vào BRD
        "de_xuat_sua":     suggest_fix(struck_text, para.text) if issue_type == "❌ Lệch" else "",
        "quyet_dinh":      "",   # người dùng tự điền: ✅ Sửa / 🚫 Bỏ qua / 🕐 Sửa sau
        "ghi_chu":         "",
        "status":          status,
        "source":          source,
    })
    issue_id += 1

# ── Logic Conflict ─────────────────────────────────────────────────────────────
for new_term, old_term in TERM_PAIRS:
    if new_term not in brd_text or old_term not in brd_text:
        continue
    old_occurrences = [
        (i + 1, brd_lines[i].strip(), get_brd_section(i + 1))
        for i in range(len(brd_lines))
        if old_term in brd_lines[i]
    ]
    if not old_occurrences:
        continue
    for ln, full, sec in old_occurrences[:5]:   # tối đa 5 dòng conflict
        results.append({
            "id":           issue_id,
            "issue_type":   "⚡ Logic Conflict",
            "brd_file":     BRD_PATH.split("/")[-1],
            "section":      sec,
            "dong_brd":     ln,
            "brd_hien_tai": full,
            "noi_dung_thay": old_term,
            "context_docx": f"BRD đã dùng '{new_term}' ở chỗ khác nhưng đây vẫn còn '{old_term}'",
            "ly_do":        f"Cross-section conflict: '{new_term}' ↔ '{old_term}'",
            "de_xuat_sua":  full.replace(old_term, new_term),
            "quyet_dinh":   "",
            "ghi_chu":      "",
            "status":       "⚡ Logic Conflict",
            "source":       "cross-section",
        })
        issue_id += 1

# ── In tóm tắt ───────────────────────────────────────────────────────────────
lenh      = [r for r in results if r["issue_type"] == "❌ Lệch"]
conflicts = [r for r in results if r["issue_type"] == "⚡ Logic Conflict"]
uncertain = [r for r in results if r["issue_type"] == "⚠️ Cần xác nhận"]
fixed     = [r for r in results if r["issue_type"] == "✅ Đã sửa"]

print(f"❌ Lệch: {len(lenh)} | ⚡ Conflict: {len(conflicts)} | ⚠️ Xác nhận: {len(uncertain)} | ✅ Đã sửa: {len(fixed)}")
print("=" * 80)

for r in lenh:
    print(f"\n[L{r['id']}] ❌ {r['section']} — dòng {r['dong_brd']}")
    print(f"  BRD hiện tại : {r['brd_hien_tai'][:100]}")
    print(f"  Struck       : \"{r['noi_dung_thay']}\"")
    print(f"  Đề xuất      : \"{r['de_xuat_sua'][:100]}\"")
    print(f"  Lý do        : {r['ly_do'][:120]}")

for r in conflicts:
    print(f"\n[C{r['id']}] ⚡ Conflict — {r['section']} dòng {r['dong_brd']}")
    print(f"  {r['context_docx']}")
    print(f"  → {r['de_xuat_sua'][:100]}")

for r in uncertain:
    print(f"\n[U{r['id']}] ⚠️ {r['section']} dòng {r['dong_brd']}")
    print(f"  Struck: \"{r['noi_dung_thay']}\" | Context: \"{r['context_docx'][:80]}\"")

# ── Xuất JSON cho export-excel ────────────────────────────────────────────────
COLUMN_LABELS = [
    "#", "Loại vấn đề", "BRD File", "Section (§)", "Dòng BRD",
    "BRD Hiện tại (nguyên văn)", "Nội dung cần xóa khỏi BRD", "Context Docx",
    "Lý do (Comment reviewer)", "BRD sau khi sửa (replace_new)",
    "Quyết định", "Ghi chú"
]

excel_rows = []
for r in sorted(results, key=lambda x: (
    {"❌ Lệch": 0, "⚡ Logic Conflict": 1, "⚠️ Cần xác nhận": 2, "✅ Đã sửa": 3}.get(r["issue_type"], 9)
)):
    excel_rows.append({
        "#":                              r["id"],
        "Loại vấn đề":                   r["issue_type"],
        "BRD File":                       r["brd_file"],
        "Section (§)":                    r["section"],
        "Dòng BRD":                       r["dong_brd"],
        "BRD Hiện tại (nguyên văn)":      r["brd_hien_tai"],
        "Nội dung cần xóa khỏi BRD":      r["noi_dung_thay"],
        "Context Docx":                   r["context_docx"],
        "Lý do (Comment reviewer)":       r["ly_do"],
        "BRD sau khi sửa (replace_new)":  r.get("replace_new", ""),
        "Quyết định":                     r["quyet_dinh"],
        "Ghi chú":                        r["ghi_chu"],
    })

export_payload = {
    "filename": OUTPUT_JSON.replace(".json", ".xlsx"),
    "sheets": [{
        "name": f"Verify {MODULE_NAME}",
        "columns": COLUMN_LABELS,
        "rows": excel_rows,
        "color_column": "Loại vấn đề",
        "color_mapping": {
            "❌ Lệch":            "FFB3B3",
            "⚡ Logic Conflict":  "FFD9B3",
            "⚠️ Cần xác nhận":   "FFF9C4",
            "✅ Đã sửa":          "C8E6C9",
            "🕐 Sửa sau":         "E3F2FD",
            "🚫 Bỏ qua":          "E0E0E0",
        }
    }],
    "summary": {
        "module":      MODULE_NAME,
        "date":        str(date.today()),
        "total":       len(results),
        "lenh":        len(lenh),
        "conflict":    len(conflicts),
        "uncertain":   len(uncertain),
        "fixed":       len(fixed),
    }
}

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(export_payload, f, ensure_ascii=False, indent=2)

print(f"\n📄 JSON: {OUTPUT_JSON}  →  chạy export-excel để tạo .xlsx")
print(f"   Tổng: {len(results)} | ❌ {len(lenh)} | ⚡ {len(conflicts)} | ⚠️ {len(uncertain)} | ✅ {len(fixed)}")
