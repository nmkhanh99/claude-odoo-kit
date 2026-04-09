# Cell Markup Guide — Quy tắc đọc markup trong cell

## Ký hiệu output

| Ký hiệu | Nghĩa | Hành động BRD |
|---------|-------|--------------|
| `~~text~~` | Bị gạch bỏ = nội dung CŨ cần XÓA | Xóa khỏi BRD |
| `text` (không flag) | Text bình thường = nội dung CÒN LẠI | Giữ nguyên |
| `[HL:text]` | Highlighted = nội dung cần chú ý / nội dung MỚI | Xác nhận với user |
| `[+text]` | Colored text = reviewer TỰ THÊM MỚI | Thêm vào BRD |
| `💬C{id}:text` | Comment của reviewer | Đọc đầy đủ, áp dụng theo hướng dẫn |

## Quy tắc đọc cell mixed

| Pattern | Diễn giải | Hành động BRD |
|---------|-----------|--------------|
| `~~A~~ [HL:B]` | A bị xóa, B là text thay thế | Sửa: A → B |
| `~~A~~` (không có gì sau) | A bị xóa, không có replacement | Bỏ A |
| `[HL:A]` (không có struck) | A được highlight để chú ý | Xác nhận A còn hiệu lực |
| `[+A]` | Reviewer thêm A hoàn toàn mới | Thêm A vào BRD |
| `~~A~~ B` (B không highlight) | A bị xóa, B là text bình thường còn lại | Sửa: A → B |

## Ví dụ đã xác nhận

```
~~Trưởng phòng Kho~~ [HL:Thủ kho]   →  Sửa "Trưởng phòng Kho" → "Thủ kho"
[+BP. Sản xuất] | [+Kho Khuôn vật lý] →  Thêm dòng mới vào BRD
~~✓~~ (toàn row struck)              →  Xóa toàn bộ row khỏi BRD
```

## Khi nào phải hỏi user

Cell có struck + HL nhưng không rõ struck là text cũ hay annotation, hoặc struck và HL ở hai đoạn tách biệt không liên quan — hỏi user xác nhận trước khi kết luận.
