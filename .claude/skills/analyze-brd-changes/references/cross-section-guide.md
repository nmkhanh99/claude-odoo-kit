# Cross-Section Field Consistency Guide

Khi thêm/sửa/xóa một **trường dữ liệu** ở bất kỳ section nào của BRD, PHẢI kiểm tra tất cả section liên quan có cần cập nhật đồng bộ không.

## Mapping bắt buộc (INV pattern)

| Section nguồn | Section phải kiểm tra đồng bộ |
|---------------|-------------------------------|
| §2.3 Dữ liệu đầu vào | §3.1 template đầu vào tương ứng |
| §2.4 Dữ liệu đầu ra | §3.2, §3.3,... template đầu ra |
| §2.x (thêm role/actor mới) | §2.6 Ma trận phân quyền (thêm hàng) |
| §1.2 Thuật ngữ | Toàn BRD (grep tất cả section) |

## Quy trình

1. **Grep toàn BRD** tìm field name — phát hiện tất cả section đã dùng field này
2. **Xác định section template** tương ứng theo mapping trên
3. Nếu field mới trong §2.x nhưng **không có** trong §3.x → **thêm ngay** trong cùng lần edit
4. Báo user danh sách sections đã cập nhật đồng bộ

## Ví dụ thực tế (INV-01, 2026-04-10)

- "Mã nhân viên" thêm vào §2.3 (Dữ liệu đầu vào)
- → Kiểm tra §3.1 (User Access Configuration Record) — bảng template đầu vào
- → §3.1 chưa có → thêm vào STT 1, renumber các trường còn lại

## Cảnh báo thường gặp

- §3.x thường có **STT** cần renumber sau khi thêm dòng đầu/giữa bảng
- Field có thể dùng tên khác nhau ở §2.x (nghiệp vụ) vs §3.x (kỹ thuật) → dùng TERMINOLOGY CHECK
- §3.x có thể có nhiều bảng con (User, Role, Warehouse...) — kiểm tra TẤT CẢ
