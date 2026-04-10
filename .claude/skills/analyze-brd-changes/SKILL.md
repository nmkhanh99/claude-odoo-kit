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

### Bước 1b — Phân loại comment
Phân loại **từng comment** theo 3 loại `[A]`/`[B]`/`[C]` trước khi tiếp tục.  
→ Quy trình đầy đủ, format bảng, anti-pattern "False Đã Làm", xử lý comment trên Highlight: **`@references/comment-classification.md`**

### Bước 2 — Đọc toàn bộ BRD gốc
File BRD trong `brds/` — **không skip section nào** (strike/highlight có thể nằm ở bất kỳ bảng nào).

### Bước 3 — Phân tích từng thay đổi
Xây cặp cho **mỗi** markup — không limit entries.

- **CROSS-SECTION CHECK** bắt buộc: grep toàn BRD tìm tất cả chỗ dùng thuật ngữ → xem `@references/cross-section-guide.md`
- **TERMINOLOGY CHECK** bắt buộc: xác định nghĩa trong ngữ cảnh → xem `@references/terminology-guide.md`
- **TABLE STRUCTURE DIFF** bắt buộc khi BRD có bảng: extract cấu trúc → so sánh cột/dòng → xem `@references/table-structure-diff.md`

### Bước 4 — Tạo bảng phân tích (3 sheets)
**CẦN SỬA** · **ĐÃ LÀM** · **OPEN QUESTIONS**  
→ Quy tắc trích dẫn nguồn, format JSON, ví dụ đúng/sai: `@references/sheet-formats.md`

### Bước 5 — Hỏi về markup không rõ nghĩa
Highlight/strike không có comment → hỏi user trước khi phân loại. Không tự suy diễn.

### Bước 6 — Xuất Excel
```bash
python3 .agents/skills/export-excel/scripts/universal_builder.py docs/analysis_xyz.json
```

### Bước 7 — Cập nhật BRD
Sau khi user xác nhận Excel → apply thay đổi vào BRD. Grep lại toàn BRD trước mỗi edit.

**Sau mỗi lần thêm/xóa mục trong numbered list** (`**1.**`, `**2.**`, `**3.**`…): đọc lại toàn bộ danh sách đó và renumber để không có số bị trùng hoặc bị nhảy.

## Constraints
- **Xác minh trước khi sửa**: khi user chỉ ra lỗi → grep + đọc lại nguồn trước, không sửa mù
- **CẤM** limit/truncate entries ("top 30"…) — phải xử lý TOÀN BỘ
- **CẤM** ghi nguồn viết tắt (`S1`, `C0 partial`) — PHẢI trích dẫn nguyên văn
- **CẤM** pip install ngầm; dùng heredoc `python3 - << 'PYEOF'`
- **CẤM** tự suy diễn `~~từ_cũ~~` và `[HL:từ_mới]` cùng nghĩa — phải TERMINOLOGY CHECK
- **CẤM** rút gọn nội dung trong `(...)` của cell bảng — xem CONTEXT NOTE RULE trong `@references/table-structure-diff.md`
- Mỗi session xử lý **một module** (INV-01, INV-02…)
- Bước 6 và 7 tách biệt — xin phép nghiệm thu Excel trước khi sửa BRD

## Best practices
- In tổng quan trước (`X comments | Y strike | Z highlight`) để user xác nhận
- `strike_text` + `colored_text` cùng đoạn = cặp thay thế rõ nhất — ưu tiên đọc trước
- Ưu tiên blocks có markup nhưng KHÔNG có comment — dễ bị bỏ sót nhất
- Chú ý bảng trong table cells (§1.2, §2.6, §3.x) — strikes trong cell dễ bị miss
- Sau khi update BRD: chạy verify script để đảm bảo không miss entry nào
