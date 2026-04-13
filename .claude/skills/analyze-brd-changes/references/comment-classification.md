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

## Quy trình đặc biệt — Comment anchor là Heading

Khi `anchored text` = **tiêu đề section** (heading `##`, `###`, `####` hoặc text dạng `"2.2.1 Sơ đồ..."`, `"3.1 Bảng..."`), comment KHÔNG chỉ là sửa tiêu đề — mà là **chỉ thị viết lại toàn bộ nội dung section đó**.

**Cách nhận biết comment trên heading:**
- Anchored text khớp hoàn toàn hoặc gần hoàn toàn với tiêu đề section
- Comment nói: "Sửa sơ đồ...", "Điều chỉnh XX theo...", "Mô tả lại chi tiết...", "Viết lại..."
- Paragraph context = tiêu đề (không có nội dung body)

**Hành động bắt buộc khi phát hiện:**
```
1. Đánh loại [A] — section rewrite
2. Cột "Hành động": ghi "⚠️ SECTION REWRITE: viết lại toàn bộ §X.X dựa trên [nguồn]"
3. Tìm "nguồn" = comment khác cùng author/cùng chủ đề cung cấp nội dung mới
4. Nhóm các comment cùng nguồn lại, xử lý cùng lúc
```

**Ví dụ thực tế (INV-02, C5/C7):**
- C5: anchor = `"2.2.1 Sơ đồ tổng quan 6 kho"` → "Sửa sơ đồ kho thành 14 kho **như đã nêu ở trên**"
- C7: anchor = `"3.1 Warehouse Record – Bảng chi tiết 6 kho"` → "Điều chỉnh 14 kho **như đã nêu**"
- Nguồn = C2 (cùng module, cùng author Thu Hoài Chu, cung cấp danh sách 14 kho đầy đủ)
- Hành động: Rewrite §2.2.1 + §3.1 dựa trên C2

---

## Quy trình đặc biệt — "Bổ sung đầy đủ theo To-be"

Khi comment trên heading §2.2.x nói `"Bổ sung đầy đủ theo To-be"` (hoặc `"Sửa theo To-be"`, `"Cập nhật theo To-be"`):

```
1. Đọc TOÀN BỘ §2.1 → Quy trình mong muốn (TO-BE) của CÙNG module
2. Liệt kê tất cả bước / điểm trong TO-BE
3. So sánh từng điểm với diagram/table hiện tại của §2.2.x
4. Ghi rõ: điểm nào ĐÃ có, điểm nào THIẾU
5. Bổ sung điểm THIẾU vào §2.2.x
```

**Ví dụ thực tế (INV-04, C29/C30):**
- C29: anchor = heading `§2.2.1 Luồng tổng quát` → "Bổ sung đầy đủ theo To-be"
- §2.1 TO-BE có: *(1)* SO → phiếu đề nghị; *(2)* **lot giờ** → tạo SO lot giờ → phiếu xuất; *(3)* lấy từ Vị trí Thành phẩm → Chờ xuất; *(4)* OQC; *(5)* Validate; *(6)* Phiếu giao Logistic
- Mermaid cũ: thiếu *(2)* lot giờ sub-flow + *(3)* tên vị trí cụ thể
- → Thêm node `LotGio` + `LotGioSO` + cập nhật label Bước 2

**Cảnh báo:**
- "To-be" không phải file khác — luôn là §2.1 của cùng module
- Cần đọc TOÀN BỘ §2.1 (không chỉ đoạn đầu) vì to-be thường có nhiều case

---

## Quy trình đặc biệt — Cross-reference comment ("như đã nêu")

Khi comment chứa cụm **tham chiếu** như: `"như đã nêu ở trên"`, `"theo điều chỉnh ở trên"`, `"như phân tích trên"`, `"xem trên"`:

```
1. DỪNG — không thể xác định "Cần sửa thành" mà không có nguồn
2. Tìm comment TRƯỚC ĐÓ cùng author/cùng module có nội dung chi tiết
3. Ghi vào bảng: Hành động = "Áp dụng [Cx] – [tóm tắt Cx]"
4. Nếu không tìm thấy nguồn → đánh [B], hỏi user
```

**Cảnh báo**: Comment tham chiếu thường đi theo nhóm — một comment có nội dung gốc (C2), các comment còn lại tham chiếu về nó (C5, C6, C7, C8). Phải xử lý C2 trước, các comment tham chiếu sau.

---

---

## Anti-pattern: Partial Application — "Áp dụng một phần"

> Comment có nhiều điểm → chỉ áp dụng điểm đầu → **BỎ SÓT** các điểm còn lại → kết luận "Đã làm" sai.

**Nhận biết comment có nhiều điểm:**
- Nhiều câu cách nhau bằng `. ` hoặc `\n`
- Có số thứ tự: `1,`, `2,`, `3,`
- Có dấu hiệu liệt kê: `Đối với X... Đối với Y...`
- Mỗi câu nói về một đối tượng / trường hợp khác nhau

**Quy trình bắt buộc với multi-point comment:**
```
1. Tách comment thành N điểm riêng biệt
2. Với MỖI điểm: kiểm tra BRD có đủ nội dung không
3. Chỉ đánh "Đã làm" khi ALL N điểm đều có trong BRD
4. Nếu chỉ một số điểm có → đánh "⚠️ Áp dụng một phần"
   → Ghi rõ điểm nào đã làm, điểm nào chưa
```

**Ví dụ thực tế (INV-04, C26):**
- Comment có 3 điểm:
  1. "CCDC: áp dụng" → BRD có: ✓
  2. "TP NG tại OQC → trả SX, không phải INV-08" → BRD: ❌ thiếu
  3. "NVL SX NG → INV-03, không liên quan INV-08" → BRD: ❌ thiếu
- → Phải phân loại **⚠️ Áp dụng một phần**, không phải "Đã làm"

**Cảnh báo thường gặp:**
- Comment bắt đầu bằng điểm chính → điểm phụ ở cuối dễ bị bỏ
- "Đối với X..." ở giữa comment dễ bị đọc lướt qua
- Multi-point comment trong table cell: mỗi điểm có thể cần apply vào ROW khác nhau

## Constraints

- **CẤM** bỏ sót comment — phải có mọi comment trong bảng
- **CẤM** đánh `[C]` khi chưa đọc hết text (dễ miss actionable content)
- **CẤM** dùng text bị cắt (`...`) để phân loại — sửa template nếu còn cắt
- **CẤM** phân loại "Đã làm" nếu chưa so sánh đầy đủ Hx với BRD
- **Comment trên Highlight = guidance, không phải nội dung thay thế** — nội dung Hx gốc phải được giữ
