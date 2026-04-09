---
name: analyze-docx-flows
description: Trích xuất ảnh luồng (TO-BE, flowchart, sơ đồ) từ file .docx, map ảnh → section heading, lưu ra thư mục, đọc từng ảnh bằng vision để mô tả và phân tích luồng nghiệp vụ. Kích hoạt khi user nói "đọc ảnh luồng", "phân tích luồng TO-BE", "xem sơ đồ trong docx", "ảnh trong word", "flowchart docx", "describe flow image".
---

# Analyze DOCX Flows (Vision)

## Goal
Ảnh flowchart/luồng TO-BE trong `.docx` **không phải text** — không đọc được bằng python-docx thông thường. Skill này:
1. Extract ảnh từ `word/media/` ra thư mục local
2. Map mỗi ảnh → section heading (module INV-xx + sub-section)
3. Dùng **Read tool** để xem từng ảnh (Claude vision)
4. Mô tả luồng: các bước, actor, điều kiện rẽ nhánh, điểm bất thường

## When to use
- "đọc ảnh luồng trong docx", "phân tích luồng TO-BE"
- "xem sơ đồ", "flowchart trong word"
- "ảnh luồng INV-01/INV-03/..."
- Khi BRD có Mermaid diagram nhưng docx có ảnh → cần so sánh

## Instructions

### Bước 1 — Xác định đầu vào
- `DOCX_PATH`: đường dẫn file docx
- `MODULE_FILTER`: module cần xem (ví dụ: "INV-01") hoặc `None` để lấy tất cả
- `OUTPUT_DIR`: mặc định `docs/extracted_images` (tạo tự động)

### Bước 2 — Chạy script extract ảnh
Copy boilerplate từ `@references/image-extractor.py`, thay 3 biến trên.

```bash
python3 - << 'PYEOF'
# ... (xem references/image-extractor.py)
PYEOF
```

Script xuất ra danh sách:
```
[IMG-01] docs/extracted_images/INV-01/image2.png
  Module  : INV-01 – Quản lý Nhân viên Kho...
  Section : 2.2.1 Luồng tổng quát
  Size    : 150 KB
```

**Lưu ý kỹ thuật:**

| Vấn đề | Cách xử lý |
|--------|-----------|
| Heading detection | Đọc `w:pStyle[@w:val]` từ XML trực tiếp — không dùng `para.style.name` vì template khác nhau |
| Ảnh trong table cell | Script scan cả `w:tbl → w:p → w:drawing` |
| Module vs Section | Track riêng: `current_module` (Heading 1) và `current_section` (heading gần nhất) |
| Duplicate rId | Một ảnh có thể được reference nhiều lần — script giữ nguyên, chỉ extract 1 file |

### Bước 3 — Đọc và phân tích ảnh bằng vision

Với mỗi ảnh đã extract, dùng **Read tool** (không phải Bash cat):

```
Read file: docs/extracted_images/INV-01/image2.png
```

Sau khi đọc, mô tả theo cấu trúc:

```
### [IMG-01] INV-01 – 2.2.1 Luồng tổng quát

**Loại sơ đồ**: Flowchart / Swimlane / BPMN
**Actor**: [danh sách vai trò xuất hiện]

**Các bước chính**:
1. ...
2. ...

**Điều kiện rẽ nhánh**:
- Nếu [A] → ...
- Nếu [B] → ...

**Điểm chú ý / khác BRD**:
- ...
```

### Bước 4 — So sánh với BRD gốc (nếu được yêu cầu)

Sau khi mô tả ảnh, đọc section tương ứng trong BRD markdown (`brds/INV-xx.md`) và so sánh:

| Chiều so sánh | Câu hỏi | Loại thay đổi |
|--------------|---------|---------------|
| **Actor** | Ảnh docx có actor khác BRD không? | `Sửa vai trò` |
| **Bước** | Ảnh có bước mà BRD thiếu hoặc ngược lại? | `Thêm mới` / `Bỏ` |
| **Rẽ nhánh** | Điều kiện rẽ nhánh có khác không? | `Sửa quan trọng` |
| **Thứ tự** | Thứ tự bước có thay đổi? | `Restructure` |

Nếu BRD dùng Mermaid diagram → so sánh trực tiếp node/edge trong Mermaid với các bước trong ảnh.

### Bước 5 — Tóm tắt thay đổi (tuỳ chọn)
Sau khi phân tích toàn bộ ảnh trong 1 module, tạo bảng tổng hợp:

| IMG | Section | Mô tả ngắn luồng | Khác BRD? |
|-----|---------|-----------------|-----------|

## Constraints
- **KHÔNG** mô tả ảnh nếu chưa đọc bằng Read tool — không suy diễn từ tên file
- Nếu ảnh quá nhỏ/mờ → báo "Không đọc được rõ" thay vì đoán
- Xử lý **từng module một** — không đọc tất cả 17 ảnh cùng lúc
- Theo `doc-no-inference` rule: nếu luồng trong ảnh mâu thuẫn với BRD → **báo cáo mâu thuẫn**, không tự chọn phiên bản nào đúng

## Best practices
- Ưu tiên mô tả theo **swimlane/actor** nếu ảnh có phân làn
- Với ảnh Mermaid render (thường là flowchart dọc) → mô tả theo thứ tự node từ trên xuống
- Nếu ảnh chứa cả **text lẫn shape** → ưu tiên đọc text (chính xác hơn shape interpretation)
- Section heading là gợi ý tốt về ý nghĩa ảnh — dùng để định hướng mô tả
- Tham chiếu `@references/image-extractor.py` để copy boilerplate chính xác
