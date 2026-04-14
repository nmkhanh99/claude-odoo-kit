---
name: odoo-debug
description: Debug và troubleshoot lỗi Odoo — tra cứu nhanh nguyên nhân lỗi theo version, đề xuất fix cụ thể với code example. Kích hoạt khi user nói "lỗi", "error", "debug", "troubleshoot", "không chạy được", "crash", "AccessError", "ValidationError", "attrs", "check_company", "SQL deprecated", hoặc paste traceback Odoo.
---

# Odoo Debug & Troubleshoot

## Goal
Nhận mô tả lỗi hoặc traceback → xác định nguyên nhân theo version Odoo → đưa ra fix code cụ thể, sẵn sàng copy-paste.

**Input**: Error message, traceback, hoặc mô tả triệu chứng  
**Output**: Nguyên nhân + fix code + checklist kiểm tra

## When to use this skill
- User paste traceback hoặc error message
- "lỗi khi install module", "view không load", "access denied"
- "attrs error", "create() error", "check_company failed"
- "RecursionError", "MissingError", "KeyError field_name"
- "module không cài được", "field không hiện", "slow performance"

## Instructions

### Bước 1 — Xác định version và loại lỗi

Đọc error message, map vào bảng tra cứu nhanh:

| Error Pattern | Nguyên nhân | Version | Fix |
|---|---|---|---|
| `'api' has no attribute 'multi'` | Dùng @api.multi | v15+ | Xóa decorator |
| `attrs attribute is no longer supported` | Dùng attrs= | v17+ | Dùng `invisible=` |
| `create() takes 2 positional arguments` | Single create() | v17+ | Thêm `@api.model_create_multi` |
| `check_company failed` | Cross-company relation | v18+ | Thêm `check_company=True` |
| `SQL string query deprecated` | String SQL | v19 | Dùng `SQL()` builder |
| `groups_id` lỗi trong create() | groups_id bị cấm trong create | v19 | Tạo user trước, sau đó `.write({'groups_id': ...})` |
| `External ID not found` | XML reference sai | All | Kiểm tra thứ tự file trong manifest |
| `Access Denied` | Thiếu security rules | All | Thêm `ir.model.access.csv` |
| `KeyError: 'field_name'` | Field không có trong vals | All | Dùng `.get()` |
| `RecursionError` | Circular compute | All | Kiểm tra `@api.depends` |
| `MissingError` | Truy cập record đã xóa | All | Dùng `record.exists()` |
| `relation "table" does not exist` | Module chưa upgrade | All | `-u module_name` |
| `column "field" does not exist` | Field mới chưa upgrade | All | `-u module_name` |

### Bước 2 — Phân tích theo loại lỗi

#### Lỗi Version-Specific

**v17+ — attrs removed:**
```xml
<!-- SAI (v14-v16) -->
<field name="partner_id" attrs="{'invisible': [('state', '=', 'draft')]}"/>

<!-- ĐÚNG (v17+) -->
<field name="partner_id" invisible="state == 'draft'"/>
<field name="amount" readonly="state != 'draft'"/>
<field name="partner_id" required="state == 'confirmed'"/>
```

**v17+ — @api.model_create_multi bắt buộc:**
```python
# SAI (v14-v16)
@api.model
def create(self, vals):
    return super().create(vals)

# ĐÚNG (v17+)
@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)
```

**v18+ — check_company:**
```python
# SAI — thiếu company check
class MyModel(models.Model):
    _name = 'my.model'
    partner_id = fields.Many2one('res.partner')

# ĐÚNG (v18+)
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True
    company_id = fields.Many2one('res.company', required=True)
    partner_id = fields.Many2one('res.partner', check_company=True)
```

**v19 — SQL() builder bắt buộc:**
```python
# SAI (v14-v18)
self.env.cr.execute("""
    SELECT id FROM my_model WHERE state = %s
""", ('draft',))

# ĐÚNG (v19)
from odoo.tools import SQL
self.env.cr.execute(SQL(
    "SELECT id FROM my_model WHERE state = %s",
    'draft'
))
```

#### Lỗi XML/View

**External ID not found — sai thứ tự trong manifest:**
```python
# SAI — security load sau view
'data': [
    'views/my_views.xml',        # Tham chiếu group
    'security/security.xml',     # Group định nghĩa ở đây — MUỘN QUÁ!
]

# ĐÚNG — thứ tự chuẩn
'data': [
    'security/security.xml',          # 1. Groups
    'security/ir.model.access.csv',   # 2. ACL
    'data/sequences.xml',             # 3. Data
    'views/my_views.xml',             # 4. Views
    'views/menuitems.xml',            # 5. Menus
]
```

**XML Syntax Error — unescaped ký tự đặc biệt:**
```xml
<!-- SAI -->
<field name="domain">[('amount', '>', 100) & ('state', '=', 'draft')]</field>

<!-- ĐÚNG — dùng tuple thay & -->
<field name="domain">[('amount', '>', 100), ('state', '=', 'draft')]</field>
```

**View Inheritance — sai cú pháp:**
```xml
<!-- SAI -->
<field name="email" position="after">
    <field name="custom"/>
</field>

<!-- ĐÚNG — phải dùng xpath -->
<xpath expr="//field[@name='email']" position="after">
    <field name="custom"/>
</xpath>
```

#### Lỗi Security

**AccessError — thiếu ACL:**
```csv
# security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_mgr,my.model.manager,model_my_model,my_mod.group_manager,1,1,1,1
```

**Debug security issues:**
```python
# Check user groups
self.env.user.groups_id.mapped('full_name')

# Check record rules
rules = self.env['ir.rule'].search([('model_id.model', '=', 'my.model')])
for rule in rules:
    print(f"{rule.name}: {rule.domain_force}")

# Test với sudo để xác nhận là security issue
records = self.env['my.model'].sudo().search([])
```

#### Lỗi ORM

**KeyError trong create/write:**
```python
# SAI — crash nếu field không có trong vals
def create(self, vals_list):
    for vals in vals_list:
        if vals['state'] == 'draft':  # KeyError!
            vals['date'] = fields.Date.today()

# ĐÚNG
def create(self, vals_list):
    for vals in vals_list:
        if vals.get('state') == 'draft':  # Safe
            vals['date'] = fields.Date.today()
```

**RecursionError — circular dependency:**
```python
# SAI — depends on itself
total = fields.Float(compute='_compute_total', store=True)

@api.depends('total')  # CIRCULAR!
def _compute_total(self):
    pass

# SAI — write loop
def write(self, vals):
    res = super().write(vals)
    self.write({'date': fields.Date.today()})  # INFINITE LOOP!
    return res

# ĐÚNG
def write(self, vals):
    if 'date' not in vals:
        vals['date'] = fields.Date.today()
    return super().write(vals)
```

**MissingError — access after delete:**
```python
# SAI
for record in self:
    record.unlink()
    print(record.name)  # MissingError!

# ĐÚNG
for record in self:
    name = record.name  # Read trước
    record.unlink()

# Hoặc check exists
if record.exists():
    return record.name
```

#### Lỗi Performance (N+1)

```python
# SAI — N+1 queries
for order in orders:
    print(order.partner_id.name)  # Query per order

# ĐÚNG — prefetch
orders.mapped('partner_id')  # Prefetch tất cả
for order in orders:
    print(order.partner_id.name)  # Không có thêm query

# TỐT NHẤT — dùng search_read
data = self.env['sale.order'].search_read(
    [('state', '=', 'sale')],
    ['name', 'partner_id', 'amount_total'],
)
```

**v19 — groups_id KHÔNG được set trong res.users.create():**
```python
# SAI (v18 trở về)
user = self.env['res.users'].create({
    'name': 'Test',
    'login': 'test@test.com',
    'groups_id': [(6, 0, [group_id])],  # LỖI trong Odoo 19!
})

# ĐÚNG (v19) — tạo trước, set groups sau bằng write()
from odoo.fields import Command
user = self.env['res.users'].create({
    'name': 'Test',
    'login': 'test@test.com',
})
user.write({'groups_id': [Command.set([group_id])]})
```

**v19 — type hints + from __future__ import annotations:**
```python
# PHẢI có ở đầu file để dùng forward references
from __future__ import annotations

# Tất cả public methods PHẢI có return type
def action_confirm(self) -> bool: ...
def create(self, vals_list: list[dict]) -> 'MyModel': ...
def write(self, vals: dict) -> bool: ...
def _compute_total(self) -> None: ...
```

#### Lỗi OWL Components

**v19 OWL 3.x — hooks phải trong setup():**
```javascript
// SAI
class MyComponent extends Component {
    myState = useState({ value: 0 });  // Sai vị trí
}

// ĐÚNG
class MyComponent extends Component {
    setup() {
        this.state = useState({ value: 0 });
    }
}
```

### Bước 3 — Debug techniques

**Enable SQL logging:**
```ini
# odoo.conf
log_level = debug_sql
```

**Odoo Shell debugging:**
```bash
./odoo-bin shell -d mydb

# Trong shell
>>> record = env['my.model'].browse(1)
>>> record.read()
>>> env['ir.model.access'].search([('model_id.model', '=', 'my.model')])
```

**Python logging trong code:**
```python
import logging
_logger = logging.getLogger(__name__)

def my_method(self):
    _logger.info("Processing %s records", len(self))
    _logger.debug("Values: %s", self.read())
    _logger.warning("Potential issue: %s", detail)
    _logger.error("Error: %s", error)
```

**Validate syntax:**
```bash
# Kiểm tra Python syntax
python3 -m py_compile models/my_model.py

# Kiểm tra XML syntax
xmllint --noout views/my_views.xml
```

**Upgrade module:**
```bash
./odoo-bin -d mydb -u my_module --stop-after-init
```

### Bước 4 — Xuất kết quả debug

```
🐛 ODOO DEBUG REPORT

Lỗi phát hiện  : [loại lỗi]
Version liên quan: Odoo [version]
Nguyên nhân    : [mô tả ngắn gọn]

── FIX ──────────────────────────────────────────────

[Code fix cụ thể]

── CHECKLIST KIỂM TRA SAU KHI FIX ──────────────────

□ [Bước 1]
□ [Bước 2]
□ [Bước 3]
```

## Constraints
- **KHÔNG** tự sửa code nếu chưa được user xác nhận
- Luôn hỏi version Odoo nếu chưa rõ trước khi đề xuất fix
- Nếu lỗi không rõ ràng → yêu cầu user cung cấp full traceback

## Best practices
- Tra bảng Quick Lookup trước → tiết kiệm thời gian
- Với `AccessError`: luôn test với `sudo()` trước để confirm là security issue
- Với performance: enable `debug_sql` để đếm queries thực tế
- Với XML error: dùng `xmllint` để validate trước khi install
- Với v17+ attrs error: dùng regex `attrs=` để tìm toàn module, sửa hết một lần
