# Comment Classification Guide

## 3 loại phân loại

| Loại | Ký hiệu | Khi nào dùng |
|------|---------|--------------|
| Cần sửa BRD | `[A]` | Comment chỉ rõ nội dung sai/thiếu → cần edit text BRD |
| Open Question | `[B]` | Comment đặt câu hỏi / chưa có câu trả lời / cần xác nhận thêm |
| Ghi chú | `[C]` | Comment là giải thích ngữ cảnh, không thay đổi nội dung BRD |

## Quy trình bắt buộc

1. **Đọc toàn bộ text comment** — KHÔNG được đọc qua 80/100/150 ký tự rồi phân loại.
2. Với mỗi comment, xác định: Loại `[A]/[B]/[C]` · Section BRD · Hành động cụ thể.
3. In bảng phân loại và **hỏi user xác nhận** trước khi tiếp tục Bước 2.
4. Comment `[B]` → chuyển thẳng vào sheet OPEN QUESTIONS, không phân tích Bước 3.

### Format bảng phân loại

```
| Comment | Loại | Section | Comment về (anchored text) | Nội dung đầy đủ | Hành động |
|---------|------|---------|---------------------------|-----------------|-----------|
| C5      | [A]  | §2.6    | "Trưởng phòng Kho"        | "Trưởng phòng không phải người duyệt, mà là Thủ kho" | Sửa cột "Phê duyệt" §2.6 |
| C14     | [B]  | §3.2    | "vị trí gia công"         | "Gia công đặt ở đâu?" | Hỏi user về location gia công |
| C20     | [A]  | §2.6    | "Nhân viên kho"           | "Nhân viên kho phải có quyền tạo / Thủ kho phê duyệt" | Sửa quyền §2.6 |
```

Cột **"Comment về"** = anchored text từ `extract-docx-comments`. Nếu trống → dùng 50 ký tự đầu paragraph context.

---

## Quy trình đặc biệt — Comment trên Highlight paragraph

Khi comment nằm trên đoạn văn ĐÃ có highlight (Hx), thực hiện 3 bước:

```
1. Đọc TOÀN BỘ nội dung đoạn Hx (không chỉ đọc comment)
2. So sánh Hx với BRD — ghi nhận chi tiết nào có trong Hx nhưng THIẾU trong BRD
3. Xác định vai trò comment:
   - Thay thế hoàn toàn → dùng comment làm "Cần sửa thành"
   - Làm rõ/bổ sung Hx   → dùng (Hx + áp dụng comment) làm "Cần sửa thành"
```

### Nhận biết "comment làm rõ/bổ sung" (KHÔNG thay thế hoàn toàn)

- Comment ngắn hơn Hx nhưng Hx có thêm chi tiết ngữ nghĩa
- Comment dùng từ: "làm rõ", "bổ sung", "chỉnh sửa thành", "ghi chú thêm"
- Comment chỉ đề cập một phần của Hx (ví dụ chỉ 1 trong 2 trường hợp)
- Hx có điều kiện/ngoại lệ/ví dụ mà comment không đề cập

### Lỗi phổ biến — "False Đã Làm"

> thấy `comment text ≈ BRD text` → kết luận "Đã làm" → **BỎ SÓT** chi tiết từ Hx

**Ví dụ thực tế (INV-03, C13):**
- BRD có: "nếu NCC xuất HĐ → nhập kho; không HĐ → theo dõi ngoài" *(rút gọn)*
- Hx có thêm: "liên kết lên hệ thống kế toán" + "xuất ra sản xuất/R&D kiểm tra chất lượng mẫu"
- → Phải phân loại **[A]**, không phải "Đã làm"

---

## Constraints

- **CẤM** bỏ sót comment — phải có mọi comment trong bảng
- **CẤM** đánh `[C]` khi chưa đọc hết text (dễ miss actionable content)
- **CẤM** dùng text bị cắt (`...`) để phân loại — sửa template nếu còn cắt
- **CẤM** phân loại "Đã làm" nếu chưa so sánh đầy đủ Hx với BRD
- **Comment trên Highlight = guidance, không phải nội dung thay thế** — nội dung Hx gốc phải được giữ
