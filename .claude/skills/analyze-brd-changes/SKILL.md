---
name: analyze-brd-changes
description: Phân tích file phản hồi (.docx) so sánh với BRD/PRD/FRD gốc — đọc toàn bộ nội dung docx (comments, strikethrough, highlight, màu reviewer, cấu trúc heading/paragraph/table) để tạo bảng thay đổi chi tiết và xuất Excel. Kích hoạt khi user nói "phân tích phản hồi", "đọc docx phản hồi", "so sánh BRD", "phân tích thay đổi", "tạo báo cáo thay đổi".
---

# Analyze BRD Changes

## Goal
Đọc **toàn bộ** file `.docx` phản hồi — so sánh với BRD gốc trong `brds/` — tạo bảng "Nội dung hiện tại → Cần sửa thành" và xuất Excel.

**Nguồn thay đổi**: Comments · Strikethrough · Highlight · Màu chữ reviewer · Nội dung paragraph/table

## When to use this skill
- "phân tích phản hồi", "đọc docx phản hồi", "xem comment docx"
- "so sánh BRD", "phân tích thay đổi", "tạo báo cáo thay đổi"

## Instructions

### Bước 1 — Trích xuất markup từ docx
Dùng `extract-docx-comments` (6 nhóm: comments, strike, tracked changes, highlights, colored, comment map).  
Nên chạy `inspect-docx-markup` trước nếu là file mới lần đầu.

### Bước 2 — Đọc toàn bộ BRD gốc
File BRD trong `brds/` — **không skip section nào** (strike/highlight có thể nằm ở bất kỳ bảng nào).

### Bước 3 — Phân tích từng thay đổi
Xây cặp cho **mỗi** markup — không limit entries.

- **CROSS-SECTION CHECK** bắt buộc: grep toàn BRD tìm tất cả chỗ dùng thuật ngữ trước khi ghi "Cần sửa thành"
- **TERMINOLOGY CHECK** bắt buộc: xác định nghĩa trong ngữ cảnh → đề xuất từ không gây nhầm
- Chi tiết đầy đủ: `@references/terminology-guide.md`

### Bước 4 — Tạo bảng phân tích (3 sheets)
**CẦN SỬA** · **ĐÃ LÀM** · **OPEN QUESTIONS**

Quy tắc trích dẫn nguồn, format JSON, ví dụ đúng/sai: `@references/sheet-formats.md`

### Bước 5 — Hỏi về markup không rõ nghĩa
Highlight/strike không có comment → hỏi user trước khi phân loại. Không tự suy diễn.

### Bước 6 — Xuất Excel
```bash
python3 .agents/skills/export-excel/scripts/universal_builder.py docs/analysis_xyz.json
```

### Bước 7 — Cập nhật BRD
Sau khi user xác nhận Excel → apply thay đổi vào BRD. Grep lại toàn BRD trước mỗi edit.

## Constraints
- **Xác minh trước khi sửa**: khi user chỉ ra lỗi → grep + đọc lại nguồn trước, không sửa mù. Xem `@references/sheet-formats.md#quy-trình-khi-user-chỉ-ra-lỗi`
- **CẤM** limit/truncate entries ("top 30"…) — phải xử lý TOÀN BỘ
- **CẤM** ghi nguồn viết tắt (`S1`, `C0 partial`) trong mọi sheet — PHẢI trích dẫn nguyên văn
- **CẤM** pip install ngầm; dùng heredoc `python3 - << 'PYEOF'`
- **CẤM** tự suy diễn `~~từ_cũ~~` và `[HL:từ_mới]` cùng nghĩa khi chúng dùng danh từ khác nhau — phải chạy TERMINOLOGY CHECK (`@references/terminology-guide.md`) và hỏi user
- **CẤM** rút gọn hoặc bỏ nội dung trong `(...)` của cell bảng — đặc biệt là điều kiện nghiệp vụ, thời điểm áp dụng, ngoại lệ (xem CONTEXT NOTE RULE trong phần TABLE STRUCTURE DIFF)
- Mỗi session xử lý **một module** (INV-01, INV-02…)
- Bước 6 và 7 tách biệt — xin phép nghiệm thu Excel trước khi sửa BRD

## Best practices
- In tổng quan trước (`X comments | Y strike | Z highlight`) để user xác nhận
- `strike_text` + `colored_text` cùng đoạn = cặp thay thế rõ nhất — ưu tiên đọc trước
- Ưu tiên blocks có markup nhưng KHÔNG có comment — dễ bị bỏ sót nhất
- Chú ý bảng trong table cells (§1.2, §2.6, §3.x) — strikes trong cell dễ bị miss khi chỉ scan paragraphs
- Sau khi update BRD: chạy verify script để đảm bảo không miss entry nào

## Kiểm tra nhất quán xuyên section (CROSS-SECTION FIELD CONSISTENCY)

Khi thêm/sửa/xóa một **trường dữ liệu** (field) ở bất kỳ section nào của BRD, PHẢI kiểm tra tất cả các section liên quan có cần cập nhật đồng bộ không.

### Mapping bắt buộc (INV-01 pattern — áp dụng tương tự cho các module khác)

| Section nguồn | Section phải kiểm tra đồng bộ |
|---------------|-------------------------------|
| §2.3 Dữ liệu đầu vào | §3.1 User Access Configuration Record (template đầu vào) |
| §2.4 Dữ liệu đầu ra | §3.2, §3.3,... (template đầu ra tương ứng) |
| §2.x (thêm role/actor mới) | §2.6 Ma trận phân quyền (thêm hàng) |
| §1.2 Thuật ngữ | Toàn BRD (grep tất cả section) |

### Quy trình bắt buộc khi phát hiện field mới

1. **Grep toàn BRD** tìm field name để phát hiện tất cả section đã có field này
2. **Xác định section template** tương ứng theo mapping trên
3. Nếu field mới trong §2.x nhưng **không có** trong §3.x template tương ứng → **thêm vào §3.x** luôn trong cùng lần edit
4. Báo user danh sách sections đã cập nhật đồng bộ

### Ví dụ thực tế (INV-01, 2026-04-10)

- "Mã nhân viên" được thêm vào §2.3 (Dữ liệu đầu vào)
- → Phải kiểm tra §3.1 (User Access Configuration Record) — bảng template đầu vào
- → §3.1 chưa có "Mã nhân viên" → thêm vào STT 1, renumber các trường còn lại

### Cảnh báo thường gặp
- §3.x thường có **STT** cần renumber sau khi thêm dòng mới ở đầu/giữa bảng
- Field có thể xuất hiện ở §2.3 (nghiệp vụ) nhưng tên column ở §3.1 (kỹ thuật) có thể khác → dùng TERMINOLOGY CHECK để xác nhận cùng khái niệm
- Đừng bỏ sót: §3.x có thể có nhiều bảng con (User table, Role table, Warehouse table...) — kiểm tra TẤT CẢ

## Nhận biết thay đổi cấu trúc bảng (TABLE STRUCTURE DIFF)

Khi BRD có bảng, PHẢI chạy script so sánh cấu trúc trước khi edit — không chỉ so sánh nội dung cell.

### Bước bắt buộc: Extract table structure từ docx

```python
python3 - << 'PYEOF'
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

DOCX_PATH = "..."   # ← đường dẫn docx
TARGET_KEYWORD = "Cơ cấu nhân sự"   # ← từ khóa heading/paragraph trước bảng cần tìm

NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{NS_W}}}"

doc = Document(DOCX_PATH)

def get_cell_text_with_markup(cell):
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
            elif color == "EE0000":  # ← thay màu reviewer nếu cần
                parts.append(f"[NEW:{text}]")
            elif is_highlight:
                parts.append(f"[HL:{text}]")
            else:
                parts.append(text)
    return " ".join(parts) if parts else ""

def iter_doc_order():
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
                if val != prev:  # bỏ qua merged cell lặp
                    row_data.append(val)
                prev = val
            print(f"  Row {r_idx}: {' | '.join(row_data)}")
        found = False
PYEOF
```

### Quy trình so sánh bảng

1. **Đếm số cột** docx vs BRD — nếu khác nhau → **báo ngay cho user** trước khi tiếp tục
2. **Đọc header row** (row 0) từ docx → so sánh với header BRD để xác định cột mới/đổi tên/xóa
3. **Phân loại từng dòng**:
   - Dòng BRD không có trong docx → **xóa** (hoặc hỏi user)
   - Dòng docx không có trong BRD → **thêm mới**
   - Dòng có [HL:...] = nội dung mới được thêm vào cell hiện có
   - Dòng có ~~text~~ = nội dung bị xóa
   - Dòng có [NEW:...] = nội dung màu reviewer (cần xác nhận)
4. **TERMINOLOGY CHECK bắt buộc** — với mỗi cell có cả `~~struck~~` lẫn `[HL:new]`:
   - Đọc `@references/terminology-guide.md` để kiểm tra cặp từ
   - Nếu struck ≠ [HL] về **khái niệm** (vd: "kho vật lý" vs "danh mục kho") → **DỪNG, hỏi user** trước khi thay thế
   - Format hỏi bắt buộc:
     ```
     ⚠️ Thuật ngữ có thể khác nghĩa: cell "[tên cột]" dòng "[vai trò]"
        Struck: "~~[từ cũ]~~" → Highlight: "[từ mới]"
        Vấn đề: "[từ cũ]" có thể chỉ [khái niệm A], "[từ mới]" có thể chỉ [khái niệm B].
        Bạn muốn: (1) Thay thế hoàn toàn? (2) Giữ cả hai? (3) Dùng từ khác?
     ```
   - **CẤM** tự suy diễn chúng cùng nghĩa và thay trực tiếp
5. **Rebuild toàn bộ bảng** khi có cột mới — không chỉ edit từng cell

### Ký hiệu markup trong table cell

| Ký hiệu | Ý nghĩa |
|---------|---------|
| `~~text~~` | Bị gạch bỏ (xóa) |
| `[HL:text]` | Highlight vàng (thêm mới hoặc thay thế) |
| `[NEW:text]` | Chữ màu reviewer (nội dung mới reviewer bổ sung) |
| text thường | Nội dung giữ nguyên |

### Cảnh báo thường gặp
- python-docx **lặp cell** trong merged cells → dùng dedup (`if val != prev`) khi đọc
- Bảng có merged header (colspan) → số cell thực tế ≠ số cột logic
- Dòng [NEW:...] thường là dòng **hoàn toàn mới** do reviewer thêm, không có trong BRD gốc → cần thêm vào BRD

### Giữ nguyên chú thích ngữ cảnh trong cell (CONTEXT NOTE RULE)

**Không được rút gọn hoặc bỏ** bất kỳ đoạn nào trong ngoặc `(...)` hoặc ghi chú inline khi copy nội dung cell vào BRD — dù có vẻ "dài" hay "thừa".

**Lý do**: Những đoạn trong ngoặc thường là **điều kiện nghiệp vụ** (khi nào áp dụng, giới hạn phạm vi, ngoại lệ) — thiếu chúng làm BRD mất ngữ cảnh và gây hiểu sai khi implement.

**Dấu hiệu nhận biết context note**:
| Dạng | Ví dụ | Ý nghĩa |
|------|-------|---------|
| `(Từ thời điểm X...)` | "Từ thời điểm xuất ra khỏi kho Khuôn → thuộc SX quản lý" | Điều kiện chuyển giao trách nhiệm |
| `(chỉ khi X)` | "chỉ khi IQC Pass" | Điều kiện tiên quyết |
| `(không áp dụng X)` | "không áp dụng cho thành phẩm" | Ngoại lệ |
| `(vd: X, Y, Z)` | "vd: Giấy, Bìa, Sóng" | Ví dụ minh họa cần giữ |

**Quy tắc khi viết vào BRD**:
- Giữ nguyên toàn bộ nội dung trong `(...)` — không tóm tắt, không lược bỏ
- Nếu cell quá dài → dùng xuống dòng trong cell markdown, không cắt nội dung
- Nếu ngoặc chứa điều kiện nghiệp vụ → dùng format: `*(điều kiện: ...)*` để phân biệt với nội dung chính
