---
name: inspect-docx-markup
description: Khảo sát nhanh toàn bộ loại markup có trong file .docx (comments, strike, highlight, tracked changes, màu chữ, shading) và gợi ý cấu hình REVIEWER_COLORS/HIGHLIGHT_FILTER trước khi chạy extract-docx-comments. Kích hoạt khi user nói "khảo sát file docx", "file này có gì", "check markup", "xem cấu trúc docx", "trước khi đọc comment", hoặc khi extract-docx-comments cho kết quả bất thường.
---

# Inspect DOCX Markup

## Goal
Chạy **trước** `extract-docx-comments` để trả lời câu hỏi:
> "File này có những loại markup nào? Cần cấu hình gì để extract đúng?"

Output trả về:
1. **Bảng tổng hợp** – loại markup → số lượng → có hay không
2. **Danh sách reviewer** – ai comment, bao nhiêu lần
3. **Màu chữ & highlight** – bảng màu xuất hiện + sample text
4. **Shading** – màu nền (để phân biệt branding vs reviewer markup)
5. **Gợi ý cấu hình** – `REVIEWER_COLORS`, `HIGHLIGHT_FILTER`, có Tracked Changes không

## When to use this skill
- Trước lần đầu chạy `extract-docx-comments` trên file mới
- Khi `extract-docx-comments` cho kết quả lạ (số lượng bất thường, màu reviewer sai)
- Khi user hỏi "file này có gì?", "kiểm tra markup", "check docx"
- Khi cần biết reviewer dùng Track Changes hay strike thủ công

## Instructions

### Bước 1 — Xác định đường dẫn file
Hỏi user nếu chưa rõ. Nếu đã có trong context thì dùng luôn.

### Bước 2 — Chạy script khảo sát
```bash
python3 - << 'PYEOF'
# ... (xem resources/inspector-template.py)
PYEOF
```

Copy boilerplate từ `resources/inspector-template.py`, thay `DOCX_PATH`.

### Bước 3 — Đọc và trình bày kết quả
Trình bày theo thứ tự:

```
📂 THÀNH PHẦN FILE
  comments.xml  : ✅ / ❌
  people.xml    : ✅ / ❌

📊 TỔNG HỢP MARKUP
  💬 Comments           : X   ✅/❌
  🔗 Comment refs map   : X
  ✂️  Strikethrough      : X
  🔄 Tracked INSERT/DEL : X / X
  🟡 Highlights         : X
  🎨 Colored text runs  : X  (Y màu khác nhau)
  🟦 Shading            : X

👥 REVIEWER  (danh sách tên + số comment)

🎨 TEXT COLORS  (bảng màu non-black + sample)

💡 GỢI Ý CẤU HÌNH
  REVIEWER_COLORS = {...}
  HIGHLIGHT_FILTER = ...
  Có/Không Tracked Changes
```

### Bước 4 — Kết luận và đề xuất
Sau khi in kết quả, tóm tắt ngắn:
- Reviewer dùng **cơ chế nào** để đánh dấu thay đổi (Track Changes, strike thủ công, hay màu chữ)
- Có cần điều chỉnh `REVIEWER_COLORS` trong `extract-docx-comments` không
- Đề xuất chạy `extract-docx-comments` tiếp theo với config đã xác định

## Constraints
- **CẤM** tự động chạy lệnh `pip install` hoặc bất kỳ package nào ngầm. Nếu script báo lỗi thiếu thư viện, hãy dừng lại, báo cho User và yêu cầu User tự copy/paste lệnh cài đặt.
- **Chỉ đọc, không sửa** file docx
- Dùng heredoc `python3 - << 'PYEOF' ... PYEOF` để tránh lỗi path có khoảng trắng
- Phân biệt **branding color** (xuất hiện > 100 lần, thường là màu header/bảng) vs **reviewer color** (ít lần hơn, tone đỏ/cam/tím)
- Không gọi `extract-docx-comments` tự động — để user quyết định sau khi xem kết quả

## Best practices
- Chỉ cần chạy 1 lần per file (kết quả ổn định trừ khi file bị sửa)
- Nếu `strike_count > 0` và `del_count == 0` → báo rõ: reviewer dùng strike thủ công, **không** dùng Word Track Changes
- Nếu `ins_count > 0` hoặc `del_count > 0` → `extract-docx-comments` sẽ tự pick up, không cần config thêm
- Highlight thường là `yellow` (WD_COLOR_INDEX 7) — nếu khác thì note rõ để user confirm
- Màu branding phổ biến trong Odoo docs: `0F9ED5` (xanh SPS), `FFFFFF` (trắng header), `B7B7B7` (xám) — bỏ qua khi xác định REVIEWER_COLORS
- Tham chiếu `resources/inspector-template.py` để copy boilerplate chính xác
