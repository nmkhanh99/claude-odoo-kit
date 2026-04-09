# PRD Structure — Cấu trúc Feature Bắt Buộc

## Cấu trúc file
File: `prds/PRD-NEW-MAN-xx-[tên]-01.md`
Giới hạn: < 500 lines. Split `-01`, `-02`... nếu cần.

---

# PRD-NEW-MAN-xx: [Tên phân hệ/chức năng]

**Version:** 1.0
**Ngày:** YYYY-MM-DD
**Tham chiếu BRD:** BRD-NEW-MAN-xx-[tên].md

---

## Feature [F-xx]: [Tên tính năng]

### User Story
> As a [vai trò], I want to [hành động], so that [mục tiêu nghiệp vụ].

### Preconditions
> Điều kiện bắt buộc phải thỏa mãn trước khi thực hiện feature này.
- ...

### Flow chi tiết
> **Chỉ viết những bước đã được xác nhận** — không thêm bước, không thêm nhánh điều kiện nếu chưa có trong nguồn.

| Bước | Actor | Hành động | Kết quả |
|------|-------|----------|--------|
| 1 | | | |
| 2 | | | |

**Nhánh điều kiện (nếu có):**
- Nếu [điều kiện A] → [kết quả A]
- Nếu [điều kiện B] → [kết quả B]

### UI Description
> Mô tả màn hình/nút đã được xác nhận.
> Nếu chưa biết menu path → ghi **[CẦN XÁC NHẬN]** thay vì tự đoán.

- **Menu path:** [CẦN XÁC NHẬN] hoặc `Sản xuất → ...`
- **Màn hình chính:** ...
- **Các nút/action:** ...
- **Form fields hiển thị:** ...

### Business Rules
> **Bắt buộc có con số cụ thể** — không dùng "nhiều", "lớn", "nhanh", "sớm".

- BR-01: Khi [điều kiện] thì [hành động]. Ngưỡng: [số cụ thể].
- BR-02: Thời gian timeout phê duyệt: [X giờ]. Nếu quá hạn → [hành động cụ thể].

### Acceptance Criteria
> Phải **testable** — mô tả rõ: Input → Hành động → Kết quả mong đợi.

- [ ] **AC-01:** Given [trạng thái ban đầu], When [hành động], Then [kết quả mong đợi].
- [ ] **AC-02:** Given [...], When [...], Then [...].

---

## Open Questions

| # | Câu hỏi | Trạng thái | Blocking? | Trả lời |
|---|---------|------------|-----------|---------|
| | | | | |
