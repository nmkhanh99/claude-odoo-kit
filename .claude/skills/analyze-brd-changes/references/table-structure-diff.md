# Table Structure Diff Guide

Khi BRD có bảng, PHẢI so sánh cấu trúc trước khi edit — không chỉ so sánh nội dung cell.

## Bước 1 — Extract table structure từ docx

Chạy script `references/scripts/table-extractor.py` (thay `DOCX_PATH` và `TARGET_KEYWORD`):

```bash
python3 - << 'PYEOF'
# paste nội dung scripts/table-extractor.py vào đây, thay 2 biến:
# DOCX_PATH = "..."
# TARGET_KEYWORD = "tên heading/paragraph trước bảng cần tìm"
PYEOF
```

## Bước 2 — Quy trình so sánh bảng

1. **Đếm số cột** docx vs BRD — nếu khác → **báo ngay cho user** trước khi tiếp tục
2. **Đọc header row** (row 0) từ docx → so sánh header BRD để xác định cột mới/đổi tên/xóa
3. **Phân loại từng dòng**:

| Trường hợp | Hành động |
|-----------|-----------|
| Dòng BRD không có trong docx | Xóa (hoặc hỏi user) |
| Dòng docx không có trong BRD | Thêm mới |
| Cell có `[HL:...]` | Nội dung mới được thêm/thay thế trong cell |
| Cell có `~~text~~` | Nội dung bị xóa |
| Cell có `[NEW:...]` | Chữ màu reviewer — cần xác nhận |

4. **TERMINOLOGY CHECK** với mỗi cell có cả `~~struck~~` lẫn `[HL:new]`:

```
⚠️ Thuật ngữ có thể khác nghĩa: cell "[tên cột]" dòng "[vai trò]"
   Struck: "~~[từ cũ]~~" → Highlight: "[từ mới]"
   Vấn đề: "[từ cũ]" có thể chỉ [khái niệm A], "[từ mới]" có thể chỉ [khái niệm B].
   Bạn muốn: (1) Thay thế hoàn toàn? (2) Giữ cả hai? (3) Dùng từ khác?
```

5. **Rebuild toàn bộ bảng** khi có cột mới — không chỉ edit từng cell

## Ký hiệu markup trong table cell

| Ký hiệu | Ý nghĩa |
|---------|---------|
| `~~text~~` | Bị gạch bỏ (xóa) |
| `[HL:text]` | Highlight vàng (thêm mới hoặc thay thế) |
| `[NEW:text]` | Chữ màu reviewer (nội dung mới) |
| text thường | Giữ nguyên |

## Cảnh báo thường gặp

- python-docx **lặp cell** trong merged cells → dùng dedup (`if val != prev`)
- Bảng có merged header (colspan) → số cell thực tế ≠ số cột logic
- Dòng `[NEW:...]` thường là dòng **hoàn toàn mới** → thêm vào BRD

## CONTEXT NOTE RULE — Giữ nguyên nội dung trong `(...)`

**Không được rút gọn hoặc bỏ** bất kỳ đoạn trong ngoặc `(...)` — thường là điều kiện nghiệp vụ, ngoại lệ, ví dụ.

| Dạng | Ví dụ | Ý nghĩa |
|------|-------|---------|
| `(Từ thời điểm X...)` | "Từ thời điểm xuất khỏi kho Khuôn → thuộc SX" | Điều kiện chuyển giao |
| `(chỉ khi X)` | "chỉ khi IQC Pass" | Điều kiện tiên quyết |
| `(không áp dụng X)` | "không áp dụng cho thành phẩm" | Ngoại lệ |
| `(vd: X, Y, Z)` | "vd: Giấy, Bìa, Sóng" | Ví dụ minh họa |

- Nếu cell quá dài → dùng xuống dòng trong cell markdown, **không cắt nội dung**
- Ngoặc chứa điều kiện nghiệp vụ → dùng format `*(điều kiện: ...)*`
