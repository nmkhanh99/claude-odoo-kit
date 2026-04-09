---
name: write-brd
description: Viết hoặc chỉnh sửa BRD (Business Requirements Document) cho dự án Odoo. Kích hoạt khi user nói "viết BRD", "tạo BRD", "write BRD", "sửa BRD", hoặc yêu cầu tạo tài liệu yêu cầu nghiệp vụ.
---

# Write BRD

## Goal
Tạo hoặc chỉnh sửa BRD đúng chuẩn: ngôn ngữ business-only, có số liệu cụ thể, không suy diễn, đúng 10 sections.

## When to use this skill
- "viết BRD", "tạo BRD", "write BRD", "create BRD"
- "sửa BRD", "update BRD", "cập nhật BRD"
- Yêu cầu tài liệu yêu cầu nghiệp vụ cho một module/phân hệ

## Instructions

1. **Đọc PROGRESS.md** trước tiên để biết trạng thái hiện tại.
2. **Đọc file nguồn** trong `sources/MAN-xx – *.md` tương ứng.
3. **Liệt kê Open Questions** theo `resources/open-questions-process.md` — hỏi người dùng, chờ trả lời.
4. **Viết BRD** theo đúng cấu trúc 10 sections trong `resources/brd-template.md`.
5. **Cập nhật PROGRESS.md** sau khi tạo/sửa file.

## Constraints
- **KHÔNG** dùng tên Odoo model, field, module, group kỹ thuật (ví dụ: `mrp.production`, `stock_picking`).
- **KHÔNG** tự điền thông tin không có trong file nguồn hoặc chưa được xác nhận.
- **KHÔNG** bắt đầu viết nếu còn Open Questions blocking chưa giải quyết.
- Mỗi file < 500 lines. Nếu cần nhiều hơn → split `-01`, `-02`.
- Pain points phải có **số liệu cụ thể** ("chênh lệch 10–15%", không dùng "nhiều", "lớn").

## Best practices
- File naming: `brds/BRD-NEW-MAN-xx-[tên].md`
- Ngôn ngữ: business-only, viết cho người không biết Odoo đọc được
- Mỗi pain point liên kết với business objective cụ thể
- Tham chiếu `resources/brd-template.md` cho cấu trúc 10 sections đầy đủ
