# Column Analysis Guide — Phân tích thay đổi cấu trúc cột

## 5.1 — Tên cột thay đổi
```
Header row: ~~Tên cũ~~ → Tên mới
→ Sửa tên cột trong BRD
```

## 5.2 — Cột mới hoàn toàn
- Dấu hiệu: header cell là `[HL:]` hoặc `[+]`, toàn bộ dữ liệu cột là `[HL:]`/`[+]`
- → Thêm cột vào BRD
- → Hỏi user: cột mới có ý nghĩa gì? Cần thêm ghi chú giải thích không?

## 5.3 — Cột thay đổi ý nghĩa (nhiều row highlight)
- Dấu hiệu: header giữ nguyên tên nhưng ≥ 2/3 rows trong cột có `[HL:]`
- Ví dụ: cột "Kho phân công" — 10/14 rows highlight → nội dung kho được tái phân công toàn bộ
- → Xem từng cell, không update hàng loạt mà không đọc từng dòng
- → Ghi: `Cập nhật nội dung cột` trong bảng phân tích

## 5.4 — Cột bị xóa
- Dấu hiệu: header bị `~~struck~~` toàn bộ, không có surviving text
- → Xóa cột khỏi bảng BRD

## 5.5 — Structural change (thêm cột phân nhóm)
- Ví dụ: BRD có 4 cột, docx có 5 cột (thêm "Vị trí" phân theo địa lý)
- → Đây là structural change — toàn bộ bảng cần được viết lại
- → Dùng loại thay đổi `Cập nhật bảng` trong `analyze-brd-changes`
