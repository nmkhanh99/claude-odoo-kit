---
name: write-frd
description: Viết hoặc chỉnh sửa FRD (Functional Requirements Document) cho dự án Odoo. Kích hoạt khi user nói "viết FRD", "tạo FRD", "write FRD", "sửa FRD", hoặc yêu cầu đặc tả kỹ thuật chức năng đủ để code được.
---

# Write FRD

## Goal
Tạo FRD self-contained: đủ thông tin để code/configure mà không cần đọc source code. Mỗi field, method, view, security phải được document đầy đủ. Python code phải copy-paste được.

## When to use this skill
- "viết FRD", "tạo FRD", "write FRD", "create FRD"
- "sửa FRD", "update FRD", "cập nhật FRD"
- "viết FRD-STG", "tạo kiến trúc module"
- Yêu cầu đặc tả kỹ thuật đủ để developer code không cần hỏi thêm

## Instructions

1. **Đọc PROGRESS.md** trước tiên.
2. **Đọc PRD tương ứng** — xác nhận scope: custom hay native? Nếu mâu thuẫn → hỏi user.
3. **Đọc Knowledge Items (KI) trong `<appDataDir>/knowledge`** để tận dụng source code đã khám phá (tránh đọc lại từ đầu). Ưu tiên các KI Summaries.
4. **Đọc source code** nếu cần chi tiết hơn (ưu tiên: `scx_addons/` → `addons/`). Chỉ đọc, không sửa.
5. **Sau khi đọc source code mới** → cập nhật/tạo KI hoặc báo cáo `Antigravity_Research.md` ngay. Mọi UI Component Odoo 19 PHẢI chỉ định OWL, không được dùng Javascript Legacy.
6. **Liệt kê Open Questions** theo `resources/open-questions-process.md`.
7. **Viết FRD** theo cấu trúc trong `resources/frd-structure.md`.
8. **Cập nhật PROGRESS.md** sau khi hoàn thành.

## Constraints
- **KHÔNG** viết "xem source code chi tiết", "existing code xử lý", "tùy implementation".
- **KHÔNG** dùng pseudo-code — chỉ Python code hoàn chỉnh, copy-paste được vào `.py`.
- Mỗi **field** phải có: name, type, required, default, stored, tracking.
- Mỗi **method** phải có: trigger, logic step-by-step, return, raise conditions.
- Mỗi **view** phải có: inherit XML ID, xpath, position, attrs/invisible.
- **Security** phải có: groups (XML ID), ACL (csv format), record rules.
- **Phân biệt native vs custom** rõ ràng — "100% native" ghi config steps; "custom" phải có Python code.
- Mỗi file < 500 lines → split `-01`, `-02` nếu cần.
- **FRD-STG** phải được viết trước tất cả FRD khác (xem `resources/frd-stg-structure.md`).

## Best practices
- File naming: `frds/FRD-NEW-MAN-xx-[tên]-01.md` hoặc `frds/FRD-NEW-MAN-STG-Kiến trúc module-01.md`
- Coi như viết spec để build lại từ đầu — dù feature đã có code, vẫn document đầy đủ
- Report/Excel export: xem `resources/report-export-spec.md` cho cấu trúc bắt buộc
- Tham chiếu rõ nguồn khi dùng source code trong FRD
