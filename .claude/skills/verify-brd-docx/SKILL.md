---
name: verify-brd-docx
description: Kiểm chứng BRD đã cập nhật đúng chưa — so sánh strike/comment trong .docx với BRD hiện tại, hỏi user và sửa ngay từng lệch, xuất Excel báo cáo tổng hợp (lệch, logic conflict, cần xác nhận). Kích hoạt khi user nói "kiểm chứng BRD", "verify BRD", "BRD còn lệch không", "check lại BRD", "xuất báo cáo lệch".
---

# Verify BRD vs DOCX

## Goal
Sau khi cập nhật BRD, phát hiện **3 loại vấn đề** và xử lý tương tác:
1. **❌ Lệch** — Struck text trong docx vẫn còn trong BRD (chưa xóa)
2. **⚡ Logic Conflict** — Comment reviewer mâu thuẫn với nội dung khác trong cùng BRD
3. **⚠️ Cần xác nhận** — Strike/highlight không có comment, không rõ nghĩa

## When to use this skill
- "kiểm chứng BRD", "verify BRD", "BRD còn lệch không"
- "check lại BRD sau khi cập nhật", "xuất báo cáo lệch"
- Sau Bước 7 của `analyze-brd-changes` để đảm bảo không miss

## Instructions

### Bước 1 — Hỏi user chế độ chạy

Trước khi làm bất cứ điều gì, hỏi:

```
Bạn muốn:
  [1] Sửa ngay từng lệch (tương tác)
  [2] Chỉ xuất báo cáo Excel, sửa sau
  [3] Cả hai — sửa những gì chắc chắn, phần còn lại vào báo cáo
```

Ghi nhớ lựa chọn và áp dụng xuyên suốt.

### Bước 2 — Chạy verify script

Paste nội dung `resources/verify-template.py`, thay `DOCX_PATH`, `BRD_PATH`, `MODULE_KEYWORDS`:

```bash
python3 - << 'PYEOF'
# ... resources/verify-template.py
PYEOF
```

Script xuất JSON kết quả sang `docs/verify_{module}_{date}.json`.

### Bước 3 — Xử lý theo chế độ đã chọn

**Chế độ [1] — Sửa ngay (tương tác):**

Với mỗi `❌ Lệch`, hiển thị và hỏi:
```
[L{n}] Struck: "{struck_text}"
  BRD hiện tại : {dòng BRD}
  Context docx : "{para.text}"
  → Sửa thành  : "{suggest_fix}"
Sửa ngay? (y = sửa / n = bỏ qua / r = vào báo cáo)
```
- **y** → Edit BRD ngay
- **n** → Bỏ qua hoàn toàn
- **r** → Ghi vào báo cáo Excel với trạng thái `🕐 Sửa sau`

**Chế độ [2] — Chỉ báo cáo:** Bỏ qua Bước 3, chuyển thẳng sang Bước 4.

**Chế độ [3] — Kết hợp:** Chỉ hỏi với `❌ Lệch` có `suggest_fix` rõ ràng; còn lại tự vào báo cáo.

> ⚠️ `⚡ Logic Conflict` và `⚠️ Cần xác nhận`: **KHÔNG tự sửa** dù ở chế độ nào — luôn vào báo cáo.

### Bước 4 — Detect Logic Conflict

Chạy cross-section check sau khi xử lý strikes:
- Grep BRD tìm mọi nơi dùng thuật ngữ vừa thay đổi
- Nếu section khác vẫn dùng giá trị cũ → `⚡ Logic Conflict`
- Ví dụ: đã sửa "4 cấp" → "3 cấp" ở §3.3, grep thấy §2.1 vẫn còn "4 cấp" → conflict

### Bước 5 — Xuất Excel báo cáo

Luôn xuất Excel bất kể chế độ nào. Script xuất JSON → `docs/verify_{module}_{date}.json` với 12 cột:

| Cột | Nội dung | Dùng để |
|-----|----------|---------|
| `#` | ID dòng | Tham chiếu |
| `Loại vấn đề` | ❌/⚡/⚠️/✅ | Màu sắc, ưu tiên |
| `BRD File` | Tên file BRD | Biết file nào |
| `Section (§)` | Heading BRD gần nhất | Tìm đúng chỗ |
| `Dòng BRD` | Số dòng | Mở file, Ctrl+G |
| `BRD Hiện tại (nguyên văn)` | Nội dung dòng BRD đang có | So sánh |
| `Nội dung cần xóa khỏi BRD` | Struck text từ docx | Biết cần xóa gì |
| `Context Docx` | Đoạn văn docx chứa struck | Kiểm chứng nguồn |
| `Lý do (Comment reviewer)` | Comment kèm theo (nếu có) | Giải thích tại sao |
| `BRD sau khi sửa (replace_new)` | BRD line sau khi xóa struck | Apply-skill dùng |
| `Quyết định` | User tự điền: ✅/🚫/🕐 | Input cho apply-skill |
| `Ghi chú` | Ghi tự do | Context thêm |

JSON cũng chứa `brd_path` (đường dẫn đầy đủ) và `replace_old`/`replace_new` trong mỗi row để skill `apply-verify-report` dùng trực tiếp.

Chạy export:
```bash
python3 .claude/skills/export-excel/scripts/universal_builder.py docs/verify_{module}_{date}.json
```

### Bước 6 — Chuyển sang apply-verify-report (tùy chọn)

Sau khi có JSON + Excel, hỏi:
```
Bạn muốn xử lý ngay các vấn đề trong báo cáo không?
→ Nếu có: dùng skill apply-verify-report để apply từng quyết định vào BRD
→ Nếu không: điền cột "Quyết định" trong Excel, sau đó dùng skill apply-verify-report
```

## Constraints
- **Chỉ báo lệch khi context khớp** — context match = ≥1 cụm từ ≥8 ký tự khớp với BRD
- **Không tự sửa** `⚡ Logic Conflict` và `⚠️ Cần xác nhận` — bắt buộc hỏi user
- **Không tự sửa** nếu struck text < 4 ký tự (tránh nhầm ký tự đơn như "✓", "✗")
- Chạy cho **một BRD file tại một thời điểm**

## Best practices
- Chạy lại verify sau mỗi lần sửa để xác nhận `❌ = 0`
- Khi BRD cell ngắn (< 10 ký tự), dùng heading section để xác định module trước khi báo lệch
- Xuất Excel ngay cả khi không có lệch — file Excel = biên bản kiểm chứng cho stakeholder
