---
name: read-docx-tables
description: Trích xuất tất cả bảng từ file .docx — tách rõ struck/surviving/colored per cell, phân tích cấu trúc và thay đổi cột (tên cột, ý nghĩa cột), loại bỏ duplicate merged-cell rows, tóm tắt bảng cần so sánh với BRD. Dùng độc lập hoặc làm bước chuẩn bị cho analyze-brd-changes. Kích hoạt khi user nói "đọc bảng docx", "xem bảng trong file word", "lấy bảng từ docx", "so sánh bảng", "bảng nhân sự trong docx", "extract table".
---

# Read DOCX Tables

## Goal
Trích xuất **tất cả bảng** trong file `.docx` theo đúng thứ tự tài liệu, kèm:
- Cell-level markup tách rõ: `~~struck~~ surviving [+colored]`
- Phân tích cột: tên cột thay đổi, cột mới/bỏ, cột thay đổi ý nghĩa
- Phát hiện và bỏ duplicate rows (do merged cell trong Word)
- Tóm tắt cuối: bảng nào cần so sánh với BRD

## When to use
- "đọc bảng docx", "xem bảng trong file word", "lấy bảng từ docx"
- "bảng nhân sự trong docx", "bảng phân quyền trong word"
- "so sánh bảng docx vs BRD", "extract table", "phân tích cột"
- Trước khi chạy `analyze-brd-changes` để xem trước nội dung bảng

## Instructions

### Bước 1 — Xác định đường dẫn và filter
- Lấy `DOCX_PATH` từ user hoặc context
- Hỏi nếu user muốn lọc theo module (`BRD_SECTION_FILTER = "INV-01"` hoặc `None`)

### Bước 2 — Chạy script
Copy boilerplate từ `@references/table-extractor.py`, thay `DOCX_PATH` và `BRD_SECTION_FILTER`.

```bash
python3 - << 'PYEOF'
# ... (xem references/table-extractor.py)
PYEOF
```

**Lưu ý kỹ thuật:**

| Vấn đề | Cách xử lý |
|--------|-----------|
| Thứ tự paragraph + table | `body.iterchildren()` + pre-built `para_map`/`table_map` |
| Merged cell duplicate row | So sánh `row_key` với row trước, skip nếu giống |
| Comment trong table cell | Scan `commentRangeStart` trong `para._element.xml` |
| Bảng layout/chữ ký | Lọc: chỉ in bảng có ≥ 2 cột VÀ ≥ 2 row |
| Struck vs surviving | `segments = [(type, text)]` per run — không merge |

### Bước 3 — Đọc output (4 phần)

**Phần A** — Chi tiết từng bảng (section, rows, cells có markup, header, data rows)  
**Phần B** — Phân tích cột tổng hợp (chỉ bảng có thay đổi cấu trúc)  
**Phần C** — Tóm tắt BẢNG CẦN SO SÁNH VỚI BRD

### Bước 4 — Giải nghĩa markup per cell
Xem `@references/cell-markup-guide.md` cho bảng ký hiệu và quy tắc đọc cell mixed.

### Bước 5 — Phân tích thay đổi cột
Xem `@references/column-analysis-guide.md` cho 5 trường hợp: đổi tên · cột mới · thay đổi ý nghĩa · xóa cột · structural change.

### Bước 6 — Xuất kết quả (tuỳ chọn)
Ghi ra `docs/tables_{tên_file}_{ngày}.md`

## Constraints
- Dùng heredoc `python3 - << 'PYEOF' ... PYEOF` để tránh lỗi path có khoảng trắng
- **KHÔNG** tự suy diễn chiều thay đổi từ markup — chỉ trích xuất và báo cáo
- Khi cell có `~~struck~~ [HL:]` mà không có comment → hỏi user trước khi kết luận
- Bảng có duplicate row → bỏ qua row trùng, **không** báo lỗi

## Best practices
- Luôn in dòng tổng quan trước (số bảng, số cells có markup) để user xác nhận
- **Đọc Phần B (PHÂN TÍCH CỘT) trước** — nếu cột thay đổi cấu trúc thì không so sánh row-by-row được
- Bảng nhân sự/vai trò thường có merged cell → xem kỹ flag duplicate
- Bảng ma trận phân quyền: row bị struck = xóa vai trò; cell `✓` struck = thu hẹp quyền
- Khi output dài: hỏi user muốn xem section nào → đặt `BRD_SECTION_FILTER` thu hẹp
- Tham chiếu `@references/table-extractor.py` để copy boilerplate chính xác
