# So sánh Mermaid BRD vs Ảnh docx

## Quy trình

1. Đọc Mermaid từ BRD → liệt kê nodes + edges
2. Dùng `analyze-docx-flows` → đọc ảnh tương ứng → liệt kê bước từ ảnh
3. So sánh theo bảng:

| Chiều | Mermaid BRD | Ảnh docx | Delta |
|-------|------------|----------|-------|
| Actor bước N | Thủ kho | Trưởng phòng Kho | `Sửa vai trò` |
| Bước mới | — | Bước X mới | `Thêm mới` |
| Bước bị bỏ | Bước Y | — | `Bỏ` |
| Thứ tự | A → B → C | A → C → B | `Restructure` |

4. Với mỗi delta → áp dụng vào Chế độ 3: SỬA
