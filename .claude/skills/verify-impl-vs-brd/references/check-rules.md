# Check Rules — verify-impl-vs-brd
# Quy tắc gán [DONE] / [PARTIAL] / [MISSING] theo loại yêu cầu

## Nguyên tắc chung

| Status    | Điều kiện |
|-----------|-----------|
| `[DONE]`    | Tìm thấy trong code VÀ đủ thuộc tính BRD yêu cầu |
| `[PARTIAL]` | Tìm thấy trong code NHƯNG thiếu ≥ 1 thuộc tính quan trọng |
| `[MISSING]` | Không tìm thấy trong source code |

---

## 1. security-group

**DONE khi:**
- `grep id="group_<name>"` tìm thấy trong `security/security.xml`
- Có `privilege_id` (Odoo 17+) — không dùng `category_id`
- `implied_ids` đúng hierarchy (nếu BRD quy định)

**PARTIAL khi:**
- Tìm thấy group nhưng dùng `category_id` thay `privilege_id` → deprecated
- Tìm thấy group nhưng `implied_ids` sai / thiếu
- Group tồn tại nhưng chưa có ACL row tương ứng trong CSV

**MISSING khi:**
- Không grep được `id="group_<name>"` trong bất kỳ XML nào trong module

---

## 2. model-field

**DONE khi:**
- `grep "field_name = fields\."` tìm thấy trong `models/`
- Đúng field type (Many2one / Char / Selection / Float…)
- Có `required=True` nếu BRD nói bắt buộc
- Có `tracking=True` nếu BRD nói cần audit trail

**PARTIAL khi:**
- Field tồn tại nhưng sai type (vd BRD: Float, code: Integer)
- Field có nhưng thiếu `required=True` khi BRD ghi "bắt buộc"
- Field có nhưng thiếu `tracking=True` khi BRD ghi "ghi nhật ký"
- Field trên class EMPTY (class không có gì khác ngoài `_inherit`)

**MISSING khi:**
- Không grep được `field_name = fields.` trong models/ của module

---

## 3. ir-rule (Record Rule)

**DONE khi:**
- `grep id="rule_<name>"` tìm thấy trong `security/security.xml`
- `domain_force` đúng điều kiện BRD (company_ids, warehouse_ids…)
- `groups` đúng group áp dụng (nếu không phải global)
- `perm_read/write/create/unlink` đúng BRD

**PARTIAL khi:**
- Rule tồn tại nhưng `domain_force` quá rộng (ví dụ: chỉ company, thiếu warehouse)
- Rule có nhưng `groups` sai (áp dụng nhầm group)
- Rule global khi BRD chỉ yêu cầu group-specific (hoặc ngược lại)

**MISSING khi:**
- Không grep được rule XML record với model đó trong security/

---

## 4. acl-row (Access Control)

**DONE khi:**
- Grep `model_<model_underscore>` trong `security/ir.model.access.csv`
- Có đủ rows cho tất cả groups BRD yêu cầu
- Permissions (r/w/c/d) đúng với BRD §2.6

**PARTIAL khi:**
- Có ACL nhưng thiếu 1+ group trong ma trận §2.6
- Permission sai (vd unlink=1 khi BRD chỉ cho r/w/c)

**MISSING khi:**
- Không có dòng nào trong CSV chứa `model_<model_underscore>`

---

## 5. state-machine

**DONE khi:**
- `grep "state.*Selection"` tìm thấy trong models/
- Đủ values (`draft`, `confirmed`, `done`, `cancel`…) theo BRD §2.1
- Có `def action_confirm`, `def action_cancel`… tương ứng transition

**PARTIAL khi:**
- Có Selection nhưng thiếu 1+ state BRD yêu cầu
- Có state nhưng không có `action_*` method tương ứng
- `default` sai trạng thái khởi đầu

**MISSING khi:**
- Không có `state = fields.Selection` trong model

---

## 6. workflow-action (Button Method)

**DONE khi:**
- `grep "def action_<name>"` tìm thấy trong models/
- Method có `ensure_one()` hoặc `for rec in self:` (không phải empty pass)
- Logic state transition đúng BRD

**PARTIAL khi:**
- Method tồn tại nhưng chỉ có `pass` hoặc `return True` (stub)
- Method không có validation (raise UserError) khi BRD yêu cầu

**MISSING khi:**
- Không grep được `def action_<name>` trong module

---

## 7. view-form / view-list / view-search

**DONE khi:**
- `grep 'res_model.*<model.name>\|model.*<model.name>'` tìm thấy trong views/
- Có `ir.actions.act_window` record cho model
- View type (form/list/search) tương ứng BRD §2.2.2

**PARTIAL khi:**
- Có view nhưng dùng `<tree>` thay `<list>` (deprecated)
- Có form view nhưng thiếu `<header>` state machine button
- Thiếu search view hoặc list view

**MISSING khi:**
- Không tìm thấy view XML cho model trong views/

---

## 8. menu-item

**DONE khi:**
- `grep 'menuitem.*action_<model>'` tìm thấy
- Parent menu đúng theo BRD §2.2.2
- `groups` attribute đúng access control

**PARTIAL khi:**
- Menuitem có nhưng parent sai / thiếu groups
- Sequence sai gây menu lộn thứ tự

**MISSING khi:**
- Không grep được menuitem liên kết đến action của model

---

## 9. data-sequence

**DONE khi:**
- `grep "ir.sequence"` trong `data/` tìm thấy
- `code` đúng với sequence code trong `create()` method
- `prefix` và `padding` hợp lý theo BRD

**PARTIAL khi:**
- Sequence XML có nhưng `code` sai (không khớp với `next_by_code()`)
- Sequence có nhưng `noupdate="1"` thiếu (sẽ bị override khi update module)

**MISSING khi:**
- Model dùng sequence trong `create()` nhưng không có file data XML

---

## Cách ghi bằng chứng

Mọi kết luận phải kèm:
```
Found: <file_path> line <N>   ← bắt buộc khi DONE hoặc PARTIAL
Issue: <mô tả ngắn vấn đề>    ← bắt buộc khi PARTIAL
```

Với MISSING: ghi "KHÔNG TÌM THẤY" và gợi ý file cần tạo.
