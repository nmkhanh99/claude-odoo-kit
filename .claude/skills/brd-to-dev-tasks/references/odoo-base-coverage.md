# Odoo Base Coverage (Stock / HR / Base)

## Những gì Odoo 19 base đã cung cấp sẵn — KHÔNG tạo lại

### stock module (Inventory)
| Feature | Model/Field | Ghi chú |
|---------|------------|---------|
| User groups | `stock.group_stock_user`, `stock.group_stock_manager` | 2 cấp cơ bản |
| Transfer states | `stock.picking.state`: draft/waiting/confirmed/assigned/done/cancel | Auto state machine |
| Audit fields | `write_uid`, `write_date`, `create_uid`, `create_date` | Auto trên mọi model |
| Multi-company picking | `company_id` trên `stock.picking` | Cần ir.rule nếu muốn restrict |
| Lot/Serial tracking | `stock.lot` | Bật theo product |
| FIFO/FEFO | `stock.quant` removal strategy | Cấu hình trên location |
| Warehouse | `stock.warehouse` | Multi-warehouse sẵn |
| Operation Type | `stock.picking.type` | Phân loại nhập/xuất/nội bộ |

### hr module (Employees)
| Feature | Model/Field | Ghi chú |
|---------|------------|---------|
| Employee record | `hr.employee` | name, department_id, work_location_id, parent_id |
| Department | `hr.department` | Hierarchy |
| Work Location | `hr.work.location` | Gắn địa điểm |
| Resource calendar | `resource.calendar` | Ca làm việc, giờ làm |
| Link user–employee | `hr.employee.user_id` | Many2one → res.users |

### base module
| Feature | Model/Field | Ghi chú |
|---------|------------|---------|
| Users | `res.users` | groups_id, company_ids |
| Groups | `res.groups` | implied_ids, users |
| Record Rules | `ir.rule` | domain_force, global/group |
| Multi-company | `res.company`, `company_ids` on user | |
| Mail/Chatter | `mail.thread` mixin | add_followers, message_post |
| Activity | `mail.activity.mixin` | Workflow tasks |

## Những gì KHÔNG có trong base — cần custom

| Yêu cầu BRD phổ biến | Không có trong base | Giải pháp custom |
|----------------------|---------------------|-----------------|
| Record Rule theo warehouse_id cụ thể | KHÔNG | Tạo `ir.rule` với domain theo warehouse |
| Approval workflow 4 cấp cho Inventory Adj | KHÔNG | Model `stock.inventory.approval` + state machine |
| Field `warehouse_ids` trên `res.users` | KHÔNG | Extend `res.users` thêm Many2many |
| Bắt buộc chọn Responsible trước Confirm | KHÔNG | Override `action_confirm` + constraint |
| Ca đêm chỉ Validate, không tạo Adjustment | KHÔNG | Override `_check_access` hoặc group restriction |

## Odoo 19 specific notes
- `name_get()` đã bị deprecated → dùng `_rec_name` + `display_name` compute
- `<tree>` → đổi thành `<list>` trong views
- `attrs` → dùng `invisible=`, `required=`, `readonly=` trực tiếp
- `read_group()` → `_read_group()` (new API)
- Groups dùng `privilege_id` thay vì `category_id` trong Odoo 19
