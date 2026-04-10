---
name: extract-docx-comments
description: Trích xuất comments, tracked changes (w:ins/w:del), strikethrough, highlights (bôi màu), colored text và map comment → đoạn văn từ file .docx. Dùng độc lập hoặc làm Bước 1 của analyze-brd-changes. Kích hoạt khi user nói "trích xuất comment", "đọc comment docx", "lấy comment từ word", "extract comment", "xem comment file word", "xem tracked changes", "bôi màu", "gạch bỏ".
---

# Extract DOCX Comments

## Goal
Đọc file `.docx` và trả về **7 nhóm dữ liệu** có cấu trúc:
1. **Comments** – toàn bộ comment của reviewer (id, author, date, text)
2. **Strikethrough** – text bị gạch bỏ (trong paragraph VÀ table cell)
3. **Tracked changes** – w:ins (thêm mới) và w:del (xóa) do Word revision tracking
4. **Highlights** – text bôi màu (mặc định yellow, nhóm theo paragraph)
5. **Colored text** – text màu đặc biệt của reviewer (vd: đỏ EE0000)
6. **Comment anchor** – text cụ thể bị comment (đoạn reviewer bôi/chọn trong Word, khác với cả paragraph)
7. **Comment map** – gắn mỗi comment vào đoạn văn/ô bảng tương ứng

## When to use this skill
- "trích xuất comment", "lấy comment từ word/docx"
- "đọc comment file word", "xem tracked changes"
- "extract comment docx", "list comments"
- "xem phần bôi màu", "xem gạch bỏ", "phần thay thế"
- Khi cần làm Bước 1 trước khi phân tích BRD (`analyze-brd-changes`)

## Instructions

### Bước 1 — Xác định đường dẫn file
Hỏi user nếu chưa rõ đường dẫn file `.docx`. Nếu đã có trong context thì dùng luôn.

### Bước 2 — Chạy script trích xuất
Dùng heredoc bash để chạy Python. Copy **toàn bộ** nội dung từ `resources/extractor-template.py`, thay `DOCX_PATH` và `REVIEWER_COLORS` trước khi chạy.

```bash
python3 - << 'PYEOF'
# paste toàn bộ nội dung resources/extractor-template.py vào đây
PYEOF
```

**Lưu ý kỹ thuật quan trọng:**

| Loại markup | Cách đọc đúng | Lỗi thường gặp |
|-------------|--------------|----------------|
| Comments | `zipfile` đọc `word/comments.xml` trực tiếp | Dùng relationship API của python-docx → lỗi |
| Strike | `r.font.strike` **+ kèm `para.text` làm ngữ cảnh** | Chỉ lưu `text` mà không lưu `context` → không biết nằm ở section nào |
| Tracked changes (w:ins/w:del) | `zipfile` đọc `word/document.xml`; `w:del` → `w:delText` | Nhầm dùng `w:t` cho `w:del` → mất toàn bộ nội dung xóa |
| Highlight | `r.font.highlight_color is not None` + `para.text` làm context | Chỉ scan `doc.paragraphs` → bỏ sót highlight trong table cell |
| Colored text | `rPr > w:color[@w:val]` qua `run._element` + lọc `REVIEWER_COLORS` | Không lọc màu đen/auto → output nhiễu |
| Comment anchor | Walk `document.xml` từ `commentRangeStart` → `commentRangeEnd`, thu `w:t`, bỏ `w:delText` | Chỉ lưu paragraph text → không biết comment nói về đoạn text nào |
| Comment map | `commentRangeStart` trong XML của paragraph → paragraph context | Dùng regex trên `para._element.xml` |

> ⚠️ **CRITICAL – thứ tự duyệt**: PHẢI dùng helper `_iter_all_paragraphs()` (dựa trên `body.iterchildren()`) cho **tất cả** các bước scan (strike, highlight, colored, comment map). Không được dùng `doc.paragraphs` + `doc.tables` riêng lẻ — làm riêng sẽ mất thứ tự xen kẽ và mất mapping section cho table cells.

> ℹ️ **Comment anchor dùng cơ chế khác**: `_extract_anchored_text()` walk trực tiếp XML tree (`root.iter()`) thay vì dùng `_iter_all_paragraphs()` — vì cần track state liên tục qua `commentRangeStart`/`commentRangeEnd` vốn không nằm trong cùng một paragraph. Đây là ngoại lệ có chủ đích, không phải lỗi.

**Namespace:** `w:` = `http://schemas.openxmlformats.org/wordprocessingml/2006/main`

### Bước 3 — Hiển thị kết quả
In dòng tổng quan trước:
```
📋 X comments | ✂️ Y đoạn gạch bỏ | 🔄 Z tracked changes | 🟡 W đoạn highlight | 🔴 V colored runs | 🔗 U comment đã map
```

Sau đó in chi tiết theo từng nhóm:

```
[C{id}] {author} – {YYYY-MM-DD}
  Comment về: "{text cụ thể bị comment trong Word}"   ← anchored text (nếu có)
  Trong đoạn ({paragraph|table}): "{đoạn văn tối đa 200 ký tự}"
  Nội dung: {toàn bộ text comment — KHÔNG cắt}

[S{n}] ({source}) Gạch bỏ: "{text gạch bỏ}"
  Ngữ cảnh: "{đoạn văn chứa phần gạch bỏ}"

[TC{n}] INSERT|DELETE | {author} – {date}
  Text: "{text được thêm/xóa}"

[H{n}] ({source}) [{color}] {text highlight}
  Ngữ cảnh: "{đoạn văn}"

[CR{n}] #{COLOR_HEX} ({source}): "{text màu đặc biệt}"
  Ngữ cảnh: "{đoạn văn}"
```

### Bước 4 — Xuất ra file (tuỳ chọn)
Nếu user muốn lưu, ghi ra `docs/comments_{tên_file}_{ngày}.md` theo cấu trúc trên.

## Constraints
- **CẤM** tự động chạy lệnh `pip install python-docx` hoặc bất kỳ package nào ngầm. Nếu script báo lỗi thiếu thư viện, hãy dừng lại, báo cho User và yêu cầu User tự copy/paste lệnh cài đặt.
- **KHÔNG** tự suy diễn nội dung markup – chỉ trích xuất nguyên văn
- Dùng `python3 - << 'PYEOF' ... PYEOF` (heredoc) để tránh lỗi ký tự đặc biệt trong path
- Nếu `word/comments.xml` không tồn tại → báo "File không có comment" và dừng phần comment, **vẫn tiếp tục** các phần khác
- Không đọc `commentsExtended.xml` (chỉ chứa metadata thread, không có text)
- Đối với `REVIEWER_COLORS`: mặc định là các tone đỏ `{EE0000, FF0000, C00000}`. Hỏi user nếu màu reviewer khác
- **CẤM** truncate/limit output ("top 30 strikes", "first 50 entries"…). PHẢI xuất **TOÀN BỘ** entries để đảm bảo không miss thay đổi. Nếu output quá dài, chia làm nhiều lần chạy hoặc ghi ra file
- **CẤM** cắt ngắn (`[:N]`) trường `Nội dung:` của bất kỳ comment nào — phải in **toàn bộ** text comment, dù dài bao nhiêu. Cắt context location (Vị trí) là chấp nhận được, cắt body comment là **không được**.

## Best practices
- Luôn in dòng tổng quan trước để user xác nhận số lượng
- Sort comment theo `int(comment_id)` để giữ thứ tự tự nhiên
- Trường `Nội dung:` — in **TOÀN BỘ**, không cắt. Trường `Trong đoạn:` — có thể cắt tối đa 200 ký tự.
- Với comment trống (text = ""), ghi rõ `[trống – có thể là placeholder]`
- **Highlight**: nhóm theo paragraph (1 paragraph → 1 entry) thay vì run-by-run để dễ đọc
- **Strike**: luôn kèm ngữ cảnh (đoạn văn chứa gạch bỏ) để biết phần nào bị xóa
- Tham chiếu `resources/extractor-template.py` để copy boilerplate chính xác
- Nên chạy `inspect-docx-markup` trước lần đầu để xác định cấu hình đúng
