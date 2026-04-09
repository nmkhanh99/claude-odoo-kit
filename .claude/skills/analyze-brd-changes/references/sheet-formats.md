# Sheet Formats & Citation Rules

## Sheet CẦN SỬA — Quy tắc trích dẫn nguồn

| Trường hợp | Cách ghi cột "Chi tiết lý do" |
|-----------|-------------------------------|
| **(a) Có comment** | `C{id} – {author}: "{trích dẫn comment nguyên văn}"` |
| **(b) Strike không có comment** | `Strike S{n}: bỏ "{strike_text}" — ngữ cảnh: "{đoạn văn chứa strike}"` |
| **(c) Highlight không có comment** | `Highlight H{n}: đánh dấu "{highlight_text}" — ngữ cảnh: "{đoạn văn}"` |

---

## Sheet OPEN QUESTIONS — 3 phần bắt buộc

Mỗi OQ PHẢI có đủ 3 phần — thiếu 1 là không hợp lệ:

| Cột | Nội dung bắt buộc | Ví dụ đúng | Ví dụ sai |
|-----|-------------------|-----------|-----------|
| **Vấn đề** | Câu hỏi cụ thể | "Với 14 kho, có 1 hay nhiều Thủ kho?" | "Câu hỏi về Thủ kho" |
| **Bằng chứng từ docx** | Trích dẫn nguyên văn + `C{id}` hoặc `S{n}`/`H{n}` | `C3 – PGĐ SPS: "kho khuôn do Kho quản lý & kho Khuôn vật lý do SX quản lý là khác nhau"` | `S11 context` |
| **Tại sao chưa có câu trả lời** | BRD nói gì, docx nói gì, chỗ nào mâu thuẫn | "BRD §3.1 field 9 liệt kê 'Kho Khuôn vật lý' là SELECTION nhưng C3 xác nhận do SX quản lý riêng" | "Cần xác nhận thêm" |

**Format JSON:**
```json
{
  "name": "OPEN QUESTIONS",
  "headers": [
    {"label": "#", "width": 5},
    {"label": "Section (BRD)", "width": 25},
    {"label": "Vấn đề cần xác nhận", "width": 50},
    {"label": "Loại", "width": 18},
    {"label": "Bằng chứng từ docx (trích dẫn)", "width": 55},
    {"label": "Tại sao chưa có câu trả lời", "width": 50},
    {"label": "Người cần trả lời", "width": 20}
  ]
}
```

---

## Sheet ĐÃ LÀM — Quy tắc trích dẫn nguồn

Áp dụng cùng quy tắc với CẦN SỬA. Cấm viết tắt:

| Cột | Ví dụ SAI | Ví dụ ĐÚNG |
|-----|-----------|------------|
| Chi tiết nguồn | `S2 + H2` | `Strike S2: bỏ "Validate Receipt" — ngữ cảnh: "Nhân viên kho thực hiện Validate Receipt..." · Highlight H2: reviewer xác nhận giữ lại "xác nhận nhập kho"` |
| Chi tiết nguồn | `C0 (partial)` | `C0 – PGĐ SPS – 2026-03-20: "Quy trình đúng phải là: Nhân viên phụ trách tạo, Thủ kho kiểm tra xác nhận" → áp dụng phần note §2.6` |

**Format JSON:**
```json
{
  "name": "ĐÃ LÀM",
  "headers": [
    {"label": "#", "width": 5},
    {"label": "Section (BRD)", "width": 30},
    {"label": "Thay đổi đã áp dụng", "width": 50},
    {"label": "Trạng thái", "width": 12},
    {"label": "Chi tiết nguồn (trích dẫn)", "width": 60}
  ]
}
```

---

## Quy tắc xây cặp "Hiện tại → Đề xuất"

| Trường hợp | "Nội dung hiện tại" | "Cần sửa thành" |
|-----------|---------------------|-----------------|
| Comment trên đoạn text | `full_text` của đoạn | Text từ comment |
| Strike có comment | `strike_text` | Phần giữ lại + hướng dẫn từ comment |
| Strike không có comment | `full_text` chứa strike | `full_text` sau khi bỏ `strike_text` |
| Highlight + comment | Text được highlight | Hướng dẫn từ comment |
| Colored text | — (thêm mới) | `colored_text` = nội dung reviewer muốn thêm |
| Markup không có comment | Ghi rõ loại markup + text | "(cần xác nhận với reviewer)" |

---

## Cross-section check — bắt buộc trước khi ghi "Cần sửa thành"

Với mỗi thuật ngữ sắp thay đổi, grep toàn BRD tìm tất cả nơi xuất hiện.  
Nếu section khác dùng thuật ngữ đó với nghĩa nhất quán với giá trị cũ → KHÔNG tự sửa.  
Ghi vào "Chi tiết lý do": `⚠️ Mâu thuẫn với §X.Y: "{trích dẫn}"` và hỏi user.

**Ví dụ lỗi thực tế**: §2.6 NV kho "Validate" sửa thành "Create" do đọc C0/C20, nhưng §1.1 ghi "Thủ kho/NV kho chỉ Validate phần việc được giao" → §1.1 này nói về Record Rules scope, không phải Create/Validate distinction → không nhầm lẫn.

---

## Quy trình khi user chỉ ra lỗi (3 bước)

1. **Xác minh** — grep BRD + đọc lại đoạn docx liên quan trước khi sửa
2. **Nếu user đúng** → sửa + ghi ngắn hành động (không lặp lại giải thích)
3. **Nếu claim có vấn đề** → trình bày bằng chứng ngắn + hỏi xác nhận
