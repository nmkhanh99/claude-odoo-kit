# Terminology Conflict Check & Resolution Guide

## Quy trình 4 bước bắt buộc

### Bước 1 — Nhận diện từ có nguy cơ gây nhầm

| Dấu hiệu nguy cơ | Ví dụ | Hành động |
|-----------------|-------|-----------|
| Con số không kèm đơn vị rõ ràng | "6 kho", "3 cấp", "14 loại" | Đọc toàn đoạn xác định đơn vị |
| Danh từ mơ hồ | "kho NVL" có thể là 1 kho hoặc danh mục | Kiểm tra context docx + BRD |
| Docx dùng từ khác BRD cho cùng khái niệm | docx: "danh mục", BRD: "chức năng" | Phải thống nhất 1 từ |
| Từ kỹ thuật Odoo bị dịch sai hoặc dùng lẫn | "Validate" / "Xác nhận" / "Phê duyệt" | Xác định đúng action trên UI |

### Bước 2 — Phân tích nghĩa trong ngữ cảnh

Đọc toàn bộ đoạn văn xung quanh trong docx. Xác định:
- Từ này chỉ **loại/nhóm/category** (tập hợp trừu tượng) hay **instance/bản thể cụ thể**?
- Số đếm đi kèm có khớp không? (category thường số nhỏ; instance thường số lớn hơn)

### Bước 3 — Đề xuất từ chính xác và giải thích

Khi phát hiện conflict, PHẢI làm đủ 3 việc:
1. Giải thích vì sao từ hiện tại gây nhầm (2 nghĩa cụ thể)
2. Xác định nghĩa thực tế trong ngữ cảnh này
3. Đề xuất từ thay thế kèm lý do

**Format tư vấn khi trình bày với user:**
```
⚠️ Thuật ngữ mơ hồ: "[từ hiện tại]"
   Vấn đề: Có thể hiểu là [nghĩa A] hoặc [nghĩa B] — hai khái niệm khác nhau.
   Ngữ cảnh docx: "[đoạn văn hoặc comment xác nhận nghĩa thực tế]"
   → Đề xuất thay bằng: "[từ rõ ràng hơn]" — vì [lý do cụ thể]
```

### Bước 4 — Kiểm tra nhất quán toàn BRD

Sau khi thống nhất từ → grep toàn BRD tìm tất cả chỗ dùng từ cũ → sửa đồng loạt.

---

## Bộ từ dễ gây nhầm (tham chiếu nhanh)

| Từ mơ hồ | Nghĩa A | Nghĩa B | Từ nên dùng |
|----------|---------|---------|-------------|
| "X kho" (không chú thích) | X danh mục kho (category) | X kho vật lý (instance) | Ghi rõ: "X danh mục kho" hoặc "X kho vật lý" |
| "kho chức năng" | Kho có chức năng riêng (vague) | — | "kho vật lý" (instance) hoặc "danh mục kho" |
| "Validate" | Nút bấm trên Odoo UI | Khái niệm phê duyệt chung | Giữ "Validate" cho action Odoo; "phê duyệt" cho approval workflow |
| "phê duyệt" | Approval workflow (BGĐ ký) | Validate phiếu trên hệ thống | Phân biệt rõ trong §2.6: "Validate phiếu" vs "Phê duyệt (approval)" |
| "nhóm quyền" / "role" | Loại vai trò (category) | Một user được gán vai trò | "nhóm quyền" cho category; "vai trò của [tên]" cho instance |

**Ví dụ lỗi thực tế**: docx §2.1 Thủ kho ghi "06 danh mục kho" — nếu replace thành "14 kho chức năng" → sai nghĩa. Docx đang nói về 6 loại kho, không phải 14 kho vật lý.
