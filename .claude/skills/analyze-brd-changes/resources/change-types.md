# Phân loại Thay đổi – Báo cáo Phân tích BRD

## Bảng phân loại (dùng đúng tên để màu Excel khớp tự động)

| Loại thay đổi        | Màu Excel | Khi nào dùng |
| -------------------- | --------- | ------------ |
| `Sửa`                | Vàng nhạt `FFF2CC` | Chỉnh sửa nhỏ: từ ngữ, số liệu, tên gọi |
| `Sửa tên`            | Vàng nhạt `FFF2CC` | Đổi tên field, section, module |
| `Sửa từ`             | Vàng nhạt `FFF2CC` | Thay thế từ/cụm từ cụ thể |
| `Sửa số`             | Vàng nhạt `FFF2CC` | Thay đổi con số, ngưỡng, phần trăm |
| `Làm rõ`             | Vàng nhạt `FFF2CC` | Thêm diễn giải, ghi chú để rõ hơn |
| `Việt hóa`           | Xanh nhạt `E8F0FE` | Dịch thuật ngữ tiếng Anh → tiếng Việt |
| `Di chuyển`          | Xanh lá nhạt `E2EFDA` | Dời nội dung sang vị trí khác |
| `Đổi tên location`   | Vàng nhạt `FFF2CC` | Đổi tên kho/vị trí trong hệ thống |
| `Sửa quan trọng`     | Cam nhạt `FCE4D6` | Thay đổi logic nghiệp vụ, flow xử lý |
| `Sửa vai trò`        | Cam nhạt `FCE4D6` | Thay đổi phân quyền, vai trò người dùng |
| `Sửa phân quyền`     | Cam nhạt `FCE4D6` | Thay đổi quyền truy cập/thao tác |
| `Làm rõ quan trọng`  | Cam nhạt `FCE4D6` | Clarification có ảnh hưởng đến thiết kế |
| `Mở rộng scope`      | Cam nhạt `FCE4D6` | Mở rộng phạm vi so với ban đầu |
| `Bỏ`                 | Đỏ nhạt `F4CCCC` | Xóa hoàn toàn nội dung/tính năng |
| `Thêm mới`           | Xanh lá `D9EAD3` | Thêm nội dung hoàn toàn mới |
| `Bổ sung`            | Xanh lá `D9EAD3` | Bổ sung thêm vào nội dung đã có |
| `Restructure`        | Hồng nhạt `EAD1DC` | Cấu trúc lại toàn bộ section |
| `Thay thế`           | Hồng nhạt `EAD1DC` | Thay thế cách tiếp cận/giải pháp |
| `Open Question`      | Xám nhạt `F3F3F3` | Chưa có câu trả lời, cần xác nhận thêm |

## Quy tắc phân loại

1. **Ưu tiên loại cụ thể hơn loại chung**: `Sửa số` > `Sửa` > `Sửa quan trọng`
2. **Đánh giá impact để chọn mức độ**: nếu thay đổi ảnh hưởng đến flow/logic → dùng `*quan trọng`
3. **Open Question**: chỉ dùng sau khi đã hỏi user và user xác nhận chưa biết

## Cột "Lý do – Comment từ docx"

Format chuẩn:
```
C{id} – {Author} – {YYYY-MM-DD}: "{trích dẫn ngắn comment}"
```

Ví dụ:
```
C5 – PGĐ Nguyễn Thị Lựa – 2026-03-20: "Sửa 6 kho thành 14 kho theo cấu hình thực tế"
C12 – Thu Hoài Chu – 2026-03-24: "Bỏ phần này vì không còn áp dụng"
```

Nếu không có comment cụ thể (từ tracked change):
```
Tracked change (gạch bỏ) – không có comment kèm theo
```
