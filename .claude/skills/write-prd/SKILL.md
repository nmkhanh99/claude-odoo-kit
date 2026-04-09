---
name: write-prd
description: Viết hoặc chỉnh sửa PRD (Product Requirements Document) cho dự án Odoo. Kích hoạt khi user nói "viết PRD", "tạo PRD", "write PRD", "sửa PRD", hoặc yêu cầu đặc tả sản phẩm/tính năng.
---

# Write PRD

## Goal
Tạo hoặc chỉnh sửa PRD đúng chuẩn: mỗi feature đủ 6 thành phần bắt buộc, flow chỉ viết những gì đã xác nhận, Business Rules có con số cụ thể, Acceptance Criteria testable.

## When to use this skill
- "viết PRD", "tạo PRD", "write PRD", "create PRD"
- "sửa PRD", "update PRD", "cập nhật PRD"
- Yêu cầu đặc tả sản phẩm / feature spec cho một chức năng

## Instructions

1. **Đọc PROGRESS.md** trước tiên để biết trạng thái hiện tại.
2. **Đọc BRD tương ứng** trong `brds/BRD-NEW-MAN-xx-*.md` — PRD phải align với BRD.
3. **Đọc file nguồn** trong `sources/MAN-xx – *.md` tương ứng.
4. **Liệt kê Open Questions** theo `resources/open-questions-process.md` — đặc biệt hỏi về menu path, timeout, ngưỡng số lượng.
5. **Viết PRD** theo cấu trúc trong `resources/prd-structure.md`.
6. **Cập nhật PROGRESS.md** sau khi tạo/sửa file.

## Constraints
- Mỗi feature phải có đủ **6 thành phần**: User Story + Preconditions + Flow chi tiết + UI Description + Business Rules + Acceptance Criteria.
- **Flow chi tiết**: chỉ viết những bước đã được xác nhận — không thêm bước, không thêm nhánh điều kiện chưa có nguồn.
- **UI Description**: nếu chưa biết menu path → **để trống và ghi [CẦN XÁC NHẬN]**.
- **Business Rules**: phải có con số cụ thể — không dùng "nhiều", "lớn", "nhanh", "sớm".
- **Acceptance Criteria**: phải testable — mô tả rõ input → hành động → kết quả mong đợi.
- Mỗi file < 500 lines. Nếu cần nhiều hơn → split `-01`, `-02`.

## Best practices
- File naming: `prds/PRD-NEW-MAN-xx-[tên]-01.md`
- Verify BRD trước: PRD phải align scope với BRD đã duyệt
- Tham chiếu `resources/prd-structure.md` cho cấu trúc đầy đủ
- Không được mở rộng/thu hẹp scope BRD trong PRD mà không xác nhận với user
