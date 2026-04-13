# BRD Extract Guide

## Cách đọc từng section BRD để trích xuất yêu cầu kỹ thuật

### §1.1 Mô tả chung
- Trích: số lượng entity (nhân sự, kho, công ty)
- Tìm: multi-company flag, audit trail requirement, workflow requirement
- Dấu hiệu: "phân quyền", "ghi nhận", "phê duyệt", "24 nhân sự", "14 kho"

### §2.1 TO-BE (numbered list)
- Mỗi bước = 1 nghiệp vụ cần implement
- Map bước → model + method:
  - "ERP tự động sinh" → computed field hoặc `_onchange` / `_compute`
  - "Phê duyệt X cấp" → approval workflow (state machine + `action_*` method)
  - "Ghi nhận audit" → `write_uid`, `write_date` (auto) hoặc chatter message
  - "Record Rules giới hạn" → `ir.rule` với domain_force

### §2.2.2 Bảng bước chi tiết
- Cột "Chức năng / Module" → xác định module Odoo (`stock`, `hr`, `base`, custom)
- Cột "Đối tượng" → xác định group thực hiện
- Cột "Mô tả chi tiết" → field/method cụ thể

### §2.3 Dữ liệu đầu vào (Input fields)
- Mỗi row = 1 field
- Loại dữ liệu → `fields.TYPE` trong Odoo:
  - VARCHAR → `fields.Char`
  - Many2one → `fields.Many2one`
  - Many2many → `fields.Many2many`
  - SELECTION → `fields.Selection`
  - FLOAT → `fields.Float`
  - Binary → `fields.Binary`
- Cột "Bắt buộc ✓" → `required=True`
- Cột "Ghi chú đặc thù" → constraint hoặc `_sql_constraints`

### §2.5 Module hệ thống ERP liên quan
- Cột "Module" → dependency trong `__manifest__.py`
- Nếu `hr` → cần `depends: ['hr']`
- Nếu `approvals` → kiểm tra có trong Odoo 19 không

### §2.6 Ma trận phân quyền
- Mỗi role → 1 `res.groups`
- Mỗi ô `✓` / `✗` → entry trong `ir.model.access.csv`
- Record Rules cần thiết khi: user chỉ được thao tác subset dữ liệu (theo kho, công ty)

### §3.x Template dữ liệu / Quy tắc nghiệp vụ
- §3.1, §3.2 → data file hoặc seed data (CSV/XML trong `data/`)
- §3.3 Quy tắc & Validation → `@api.constrains` hoặc `write()` override

## Pattern nhận biết "cần code custom" vs "Odoo base đủ"

| BRD nói | Odoo base | Cần custom? |
|---------|-----------|-------------|
| "ghi nhận write_uid, write_date" | Auto trong tất cả model | Không — chỉ config chatter |
| "phân quyền Inventory/User" | `stock.group_stock_user` | Không — dùng group sẵn |
| "Record Rule theo warehouse" | KHÔNG có sẵn | CÓ — cần tạo ir.rule |
| "Approval 4 cấp cho Adj" | Không đủ | CÓ — cần model/workflow |
| "Audit log chatter" | `mail.thread` mixin | Chỉ thêm mixin nếu chưa có |
| "Ca làm việc" | `resource.calendar` | Không — chỉ cấu hình |
