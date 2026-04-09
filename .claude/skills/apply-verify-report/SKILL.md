---
name: apply-verify-report
description: Đọc báo cáo verify JSON (docs/verify_*.json), hiển thị từng vấn đề pending, hỏi quyết định (Sửa/Bỏ/Defer), áp dụng edit trực tiếp vào BRD và re-verify. Kích hoạt khi user nói "áp dụng báo cáo", "apply verify", "cập nhật BRD từ báo cáo", "xử lý báo cáo verify".
---

# Apply Verify Report → BRD

## Goal
Đọc file `docs/verify_*.json` (xuất từ skill `verify-brd-docx`) — hiển thị các vấn đề chưa có quyết định, hỏi user từng cái, áp dụng sửa vào BRD, sau đó re-verify để xác nhận `❌ = 0`.

Skill này được thiết kế để dùng **sau khi context cũ đã mất** — mọi thông tin cần thiết đều đọc từ JSON, không cần nhớ conversation trước.

## When to use this skill
- "áp dụng báo cáo verify", "apply verify report", "cập nhật BRD từ báo cáo"
- "xử lý verify JSON", "quyết định từng vấn đề trong báo cáo"
- Khi user mở lại báo cáo verify sau nhiều ngày và muốn apply

## Instructions

### Bước 1 — Tìm và đọc JSON báo cáo

Hỏi user path nếu chưa rõ, hoặc tự tìm file mới nhất:

```bash
ls -t docs/verify_*.json | head -5
```

Đọc JSON: lấy `sheets[0].rows` và `summary`.

### Bước 2 — Hiển thị tóm tắt trạng thái

In bảng tóm tắt:
```
Module: {module} | Ngày verify: {date}
──────────────────────────────────────
❌ Lệch:          {lenh} dòng
⚡ Logic Conflict: {conflict} dòng  
⚠️ Cần xác nhận:  {uncertain} dòng
✅ Đã sửa:        {fixed} dòng

Chưa có quyết định: {pending} dòng cần xử lý
```

### Bước 3 — Xử lý từng vấn đề pending

Với mỗi row có `Quyết định = ""` và `Loại vấn đề ∈ {❌ Lệch, ⚡ Logic Conflict}`:

Hiển thị đầy đủ:
```
[#{id}] {Loại vấn đề} — {Section (§)} | Dòng BRD: {Dòng BRD}
────────────────────────────────────────────────────────────────
BRD File     : {BRD File}
BRD hiện tại : {BRD Hiện tại (nguyên văn)}
Cần xóa      : "{Nội dung cần xóa khỏi BRD}"
BRD sau sửa  : "{BRD sau khi sửa (replace_new)}"
Lý do        : {Lý do (Comment reviewer)}
Context Docx : {Context Docx}
────────────────────────────────────────────────────────────────
Quyết định? (✅ = sửa ngay / 🚫 = bỏ qua / 🕐 = sửa sau / ? = giải thích thêm)
```

**Xử lý theo quyết định:**
- **✅ Sửa ngay**: Dùng Edit tool — `replace_old` → `replace_new` trong file `brd_path`
- **🚫 Bỏ qua**: Ghi lý do vào `Ghi chú`, không chỉnh BRD
- **🕐 Sửa sau**: Đánh dấu để báo cáo lại cuối session
- **?**: Đọc thêm context BRD quanh `dong_brd` rồi giải thích

> ⚠️ `⚠️ Cần xác nhận`: Không tự áp dụng dù user bảo. Phải hỏi: "Bạn muốn sửa thành gì?"

### Bước 4 — Áp dụng edit vào BRD

Khi user chọn ✅ cho một row:

1. **Đọc file BRD** (để xác nhận `replace_old` vẫn còn tồn tại — file có thể đã bị edit từ lần verify)
2. **Tìm chính xác** chuỗi `replace_old` trong file
   - Nếu tìm thấy → dùng Edit tool thay bằng `replace_new`
   - Nếu không tìm thấy → báo "Dòng đã thay đổi kể từ lần verify. BRD hiện tại gần nhất:" + grep xung quanh `dong_brd` → hỏi user xử lý thủ công
3. **Xác nhận** sau edit: grep lại để confirm `replace_old` không còn tồn tại

### Bước 5 — Tóm tắt sau khi xử lý

In bảng quyết định cuối session:
```
Đã sửa  : N dòng  →  {list id}
Bỏ qua  : N dòng  →  {list id + lý do}
Sửa sau : N dòng  →  {list id}
```

### Bước 6 — Re-verify (nếu có ≥1 sửa)

Hỏi: "Chạy lại verify để xác nhận không còn ❌?"

Nếu đồng ý → chạy lại verify script (xem `verify-brd-docx` skill) với cùng `DOCX_PATH` và `BRD_PATH`.

Mục tiêu: `❌ Lệch = 0` sau khi apply tất cả quyết định ✅.

## Constraints
- **Chỉ edit** khi `replace_old` khớp chính xác với nội dung BRD hiện tại
- **Không tự sửa** `⚠️ Cần xác nhận` — luôn hỏi user muốn sửa thành gì
- **Không tự sửa** `⚡ Logic Conflict` mà không hỏi — conflict có thể valid (e.g., "Thủ kho" và "Quản lý kho tương ứng" là 2 vai trò khác nhau)
- Mỗi lần chỉ xử lý **một BRD file** — nếu JSON chứa nhiều `brd_path` khác nhau, hỏi user bắt đầu từ file nào
- **Luôn đọc lại BRD** trước khi edit — tránh dùng nội dung cached từ JSON (file có thể đã thay đổi)

## Best practices
- Với row có `Lý do = "(không có comment — suy luận từ strike)"` + context docx từ module khác → gợi ý "Có thể là false positive cross-module. Bỏ qua?"
- Khi `replace_new = "(xóa dòng này)"` → xác nhận rõ với user trước khi xóa hẳn dòng khỏi BRD
- Sau khi apply, grep lại `replace_old` để đảm bảo không còn duplicate
- Nếu JSON cũ (> 7 ngày so với today) → cảnh báo "Báo cáo này đã {N} ngày. Nên chạy lại verify trước khi apply"
