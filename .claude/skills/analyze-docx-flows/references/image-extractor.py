"""
Boilerplate: Trích xuất ảnh từ .docx, map ảnh → section heading, lưu ra thư mục
Chạy qua: python3 - << 'PYEOF' ... PYEOF

Output:
  - Ảnh lưu tại OUTPUT_DIR/{module_prefix}/image{n}.png
  - In bảng mapping: image_path → section → module
"""
import zipfile, os
import xml.etree.ElementTree as ET
from docx import Document

DOCX_PATH     = "/path/to/file.docx"    # ← thay đường dẫn thực tế
OUTPUT_DIR    = "docs/extracted_images"  # ← thư mục lưu ảnh
MODULE_FILTER = None                     # None = tất cả | "INV-01" = chỉ lấy ảnh INV-01

NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

def w(tag): return f"{{{NS_W}}}{tag}"

# ─────────────────────────────────────────────────────────────────────────────
# 1. MAP rId → filename trong word/media/
# ─────────────────────────────────────────────────────────────────────────────
rid_to_media = {}

with zipfile.ZipFile(DOCX_PATH) as z:
    rels_root = ET.fromstring(z.read("word/_rels/document.xml.rels"))
    for rel in rels_root:
        rid    = rel.get("Id", "")
        target = rel.get("Target", "")
        if "media/" in target:
            rid_to_media[rid] = target.split("/")[-1]

# ─────────────────────────────────────────────────────────────────────────────
# 2. PARSE — dùng python-docx para_map để lấy style.name đúng
#    (XML lưu pStyle val="2" không phải "Heading2" — phải dùng python-docx)
# ─────────────────────────────────────────────────────────────────────────────
doc      = Document(DOCX_PATH)
para_map = {p._element: p for p in doc.paragraphs}   # {xml_el: Para object}

body = doc.element.body

current_module  = "【Đầu tài liệu】"
current_section = "【Đầu tài liệu】"
image_map = []

def heading_level_from_para(para):
    """Trả về int 1–9 nếu para là Heading, else None."""
    name = para.style.name  # "Heading 1", "Heading 2", ...
    if not name.lower().startswith("heading"):
        return None
    try:
        return int(name.lower().replace("heading", "").strip())
    except:
        return None

for child in body.iterchildren():
    tag = child.tag

    if tag == w("p"):
        para = para_map.get(child)
        if para:
            level = heading_level_from_para(para)
            text  = para.text.strip()
            if level is not None and text:
                current_section = text
                if level == 1:
                    current_module = text

        # Tìm drawing trong paragraph element
        for drawing in child.iter(w("drawing")):
            for elem in drawing.iter():
                embed = elem.get(f"{{{NS_R}}}embed")
                if embed and embed in rid_to_media:
                    image_map.append({
                        "rId":            embed,
                        "media_filename": rid_to_media[embed],
                        "module":         current_module,
                        "section":        current_section,
                    })

    elif tag == w("tbl"):
        # Ảnh đôi khi nằm trong table cell
        for para_el in child.iter(w("p")):
            for drawing in para_el.iter(w("drawing")):
                for elem in drawing.iter():
                    embed = elem.get(f"{{{NS_R}}}embed")
                    if embed and embed in rid_to_media:
                        image_map.append({
                            "rId":            embed,
                            "media_filename": rid_to_media[embed],
                            "module":         current_module,
                            "section":        current_section,
                        })

# ─────────────────────────────────────────────────────────────────────────────
# 3. EXTRACT ẢNH RA THƯ MỤC
# ─────────────────────────────────────────────────────────────────────────────
os.makedirs(OUTPUT_DIR, exist_ok=True)

extracted = []  # [{local_path, module, section, media_filename}]

with zipfile.ZipFile(DOCX_PATH) as z:
    for img in image_map:
        module = img["module"]
        section = img["section"]
        media_filename = img["media_filename"]

        # Lọc theo module nếu có filter
        if MODULE_FILTER and MODULE_FILTER.lower() not in module.lower():
            continue

        # Tạo prefix an toàn từ module name (lấy phần "INV-01")
        module_prefix = module.split("–")[0].strip().replace(" ", "_") if "–" in module else "misc"
        module_dir = os.path.join(OUTPUT_DIR, module_prefix)
        os.makedirs(module_dir, exist_ok=True)

        src_path   = f"word/media/{media_filename}"
        local_path = os.path.join(module_dir, media_filename)

        try:
            data = z.read(src_path)
            with open(local_path, "wb") as f:
                f.write(data)
            extracted.append({
                "local_path":     local_path,
                "module":         module,
                "section":        section,
                "media_filename": media_filename,
                "size_kb":        len(data) // 1024,
            })
        except KeyError:
            pass  # file không tồn tại trong zip, bỏ qua

# ─────────────────────────────────────────────────────────────────────────────
# 4. OUTPUT
# ─────────────────────────────────────────────────────────────────────────────
print(f"📷 Tổng ảnh trong docx: {len(image_map)} | Đã extract: {len(extracted)}")
print(f"📁 Output dir: {OUTPUT_DIR}")
print("=" * 80)
print()

for i, img in enumerate(extracted, 1):
    print(f"[IMG-{i:02d}] {img['local_path']}")
    print(f"  Module  : {img['module'][:70]}")
    print(f"  Section : {img['section'][:70]}")
    print(f"  Size    : {img['size_kb']} KB")
    print()

print("=" * 80)
print("\n✅ Dùng Read tool để xem từng ảnh theo đường dẫn local_path ở trên.")
print("   Claude có thể đọc ảnh PNG/JPG trực tiếp để phân tích luồng.")
