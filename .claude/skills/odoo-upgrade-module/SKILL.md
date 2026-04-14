---
name: odoo-upgrade-module
description: Phân tích tương thích và lập kế hoạch upgrade module Odoo sang version mới — phát hiện breaking changes, deprecations, tạo migration script. Kích hoạt khi user nói "upgrade module", "migrate sang odoo", "nâng cấp module", "compatibility check", "migration plan", "porting odoo", "chuyển sang version".
---

# Odoo Module Upgrade Planner

## Goal
Phân tích module Odoo → phát hiện tất cả breaking changes và deprecations theo version jump → tạo kế hoạch migration chi tiết với code examples.

**Input**: Module path + version nguồn + version đích  
**Output**: Báo cáo migration với breaking changes, code fixes và migration scripts

## When to use this skill
- "upgrade module từ v16 sang v19", "migrate sang Odoo 18"
- "module cũ có chạy được trên Odoo 19 không"
- "nâng cấp module vendor từ v15"
- "porting module OCA sang version mới"
- Trước khi upgrade production server

## Instructions

### Bước 1 — Xác định versions

1. Đọc `__manifest__.py` → lấy version hiện tại
2. Hỏi user: version đích cần upgrade lên
3. Tính migration path (có thể nhiều bước)

```
Ví dụ: 16.0 → 19.0 = 3 bước (16→17, 17→18, 18→19)
```

### Bước 2 — Ma trận Breaking Changes

#### v14 → v15 (Breaking Changes)

| API cũ | Thay đổi | Fix |
|---|---|---|
| `@api.multi` | REMOVED | Xóa decorator |
| `track_visibility='onchange'` | REMOVED | Dùng `tracking=True` |
| `fields.Datetime.now()` | Deprecated | Dùng `fields.Datetime.now` |

```python
# v14 → v15 fix examples:

# @api.multi removed
# SAI (v14)
@api.multi
def action_confirm(self):
    for record in self:
        record.state = 'confirmed'

# ĐÚNG (v15+)
def action_confirm(self):
    for record in self:
        record.state = 'confirmed'

# track_visibility removed
# SAI
name = fields.Char(track_visibility='onchange')
# ĐÚNG
name = fields.Char(tracking=True)
```

#### v15 → v16 (Breaking Changes)

| API cũ | Thay đổi | Fix |
|---|---|---|
| `(0,0,{})` syntax | Deprecated | Dùng `Command.create({})` |
| `(6,0,[])` syntax | Deprecated | Dùng `Command.set([])` |
| Asset XML (old format) | REMOVED | Dùng asset bundles mới |

```python
# Command class (v16+)
from odoo.fields import Command

# SAI (v14-v15)
record.write({'line_ids': [(0, 0, {'name': 'New'})]})

# ĐÚNG (v16+)
record.write({'line_ids': [Command.create({'name': 'New'})]})

# Các Command commands
Command.create(vals)     # (0, 0, vals)
Command.update(id, vals) # (1, id, vals)
Command.delete(id)       # (2, id)
Command.unlink(id)       # (3, id)
Command.link(id)         # (4, id)
Command.clear()          # (5,)
Command.set(ids)         # (6, 0, ids)
```

```xml
<!-- Assets v16+ format -->
<!-- SAI (v14-v15 assets in manifest) -->
'web.assets_backend': [
    'my_module/static/src/js/my_widget.js',
]

<!-- ĐÚNG (v16+) — trong ir_module_data.xml hoặc assets.xml -->
<record id="assets_backend" model="ir.asset">
    ...
</record>
<!-- Hoặc trong manifest (v16 syntax) -->
'assets': {
    'web.assets_backend': [
        'my_module/static/src/js/my_widget.js',
        'my_module/static/src/css/my_style.css',
    ],
},
```

#### v16 → v17 (MAJOR Breaking Changes)

| API cũ | Thay đổi | Fix |
|---|---|---|
| `attrs=` trong XML | **REMOVED** | Dùng `invisible=`, `readonly=`, `required=` |
| `<tree ...>` tag | **REMOVED** | Dùng `<list ...>` |
| `name_get()` method | **REMOVED** | Dùng `_rec_name` hoặc `_compute_display_name` |
| `@api.model` cho create | Changed | Dùng `@api.model_create_multi` |
| `read_group()` | Deprecated | Dùng `_read_group()` |

```xml
<!-- attrs REMOVED (v17) -->

<!-- SAI (v14-v16) -->
<field name="partner_id" attrs="{'invisible': [('state', '=', 'draft')], 'required': [('type', '=', 'customer')]}"/>
<button attrs="{'invisible': [('state', '!=', 'draft')]}" .../>

<!-- ĐÚNG (v17+) -->
<field name="partner_id"
       invisible="state == 'draft'"
       required="type == 'customer'"/>
<button invisible="state != 'draft'" .../>

<!-- <tree> REMOVED (v17) -->
<!-- SAI -->
<tree string="My Records" decoration-danger="state=='cancelled'">
<!-- ĐÚNG -->
<list string="My Records" decoration-danger="state=='cancelled'">
```

```python
# name_get() REMOVED (v17)

# SAI (v14-v16)
def name_get(self):
    result = []
    for record in self:
        result.append((record.id, f"[{record.code}] {record.name}"))
    return result

# ĐÚNG (v17+)
_rec_name = 'display_name'

@api.depends('code', 'name')
def _compute_display_name(self):
    for record in self:
        record.display_name = f"[{record.code}] {record.name}"

# @api.model_create_multi (v17 mandatory)
# SAI
@api.model
def create(self, vals):
    return super().create(vals)

# ĐÚNG
@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)

# read_group → _read_group (v17)
# SAI
data = self.env['my.model'].read_group(
    [('state', '=', 'draft')],
    ['partner_id', 'amount:sum'],
    ['partner_id'],
)

# ĐÚNG (v17+)
data = self.env['my.model']._read_group(
    [('state', '=', 'draft')],
    groupby=['partner_id'],
    aggregates=['amount:sum'],
)
```

#### v17 → v18 (Breaking Changes)

| API cũ | Thay đổi | Fix |
|---|---|---|
| `company_ids` trong record rules | Changed | Dùng `allowed_company_ids` |
| String SQL | Deprecated | Dùng `SQL()` builder (required v19) |
| No type hints | Warning | Thêm type hints (required v19) |

```python
# Multi-company (v18+)

# SAI (v14-v17 record rules)
# domain_force: [('company_id', 'in', company_ids)]

# ĐÚNG (v18+)
# domain_force: [('company_id', 'in', allowed_company_ids)]

# Model v18+
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True  # Thêm mới v18

    company_id = fields.Many2one('res.company', required=True)
    partner_id = fields.Many2one('res.partner', check_company=True)  # Thêm mới

# SQL builder (recommended v18, required v19)
from odoo.tools import SQL

self.env.cr.execute(SQL(
    "SELECT id FROM my_model WHERE state = %s",
    'draft'
))
```

#### v18 → v19 (Breaking Changes)

| API cũ | Thay đổi | Fix |
|---|---|---|
| String SQL | **REQUIRED** SQL() | Phải dùng `SQL()` |
| No type hints | **REQUIRED** | Thêm type hints trên public methods và fields |
| `from __future__` missing | **REQUIRED** | Thêm `from __future__ import annotations` |
| OWL 2.x patterns | OWL 3.x | Cập nhật components |
| `groups_id` trong `create()` | **FORBIDDEN** | Tạo user trước, set groups sau bằng `write()` |

```python
# Type hints bắt buộc v19 — thêm from __future__ import annotations
from __future__ import annotations

def action_confirm(self) -> bool:
    self.filtered(lambda r: r.state == 'draft').write({'state': 'confirmed'})
    return True

@api.model_create_multi
def create(self, vals_list: list[dict]) -> 'MyModel':
    return super().create(vals_list)

def write(self, vals: dict) -> bool:
    return super().write(vals)

@api.depends('line_ids.amount')
def _compute_total(self) -> None:
    for record in self:
        record.total_amount = sum(record.line_ids.mapped('amount'))

# Field type annotations
name: str = fields.Char(required=True)
amount: float = fields.Float(default=0.0)
state: str = fields.Selection([('draft', 'Draft')], default='draft')

# SQL() builder bắt buộc v19
from odoo.tools import SQL

# SAI (v14-v18)
self.env.cr.execute("""
    UPDATE my_model SET state = %s WHERE id IN %s
""", ('done', tuple(ids)))

# ĐÚNG (v19)
self.env.cr.execute(SQL(
    "UPDATE my_model SET state = %s WHERE id IN %s",
    'done', tuple(ids)
))

# groups_id KHÔNG được set trong res.users.create() v19
# SAI (v18 trở về trước)
user = self.env['res.users'].create({
    'name': 'John',
    'login': 'john@test.com',
    'groups_id': [(6, 0, [group_id])],  # BỊ CẤM trong v19!
})

# ĐÚNG (v19)
from odoo.fields import Command
user = self.env['res.users'].create({
    'name': 'John',
    'login': 'john@test.com',
})
user.write({'groups_id': [Command.set([group_id])]})
```

```javascript
// OWL 3.x changes (v19)

// SAI (OWL 2.x)
import { Component, useState } from "@odoo/owl";

// ĐÚNG (OWL 3.x v19)
import { Component } from "@odoo/owl";
import { useState } from "@odoo/owl";

// Hooks PHẢI trong setup()
class MyComponent extends Component {
    setup() {
        this.state = useState({ value: 0 });  // ĐÚNG
    }
}
```

### Bước 3 — Scan module để tìm issues

Dùng Grep để tìm patterns cần fix:

```bash
# attrs= trong XML
grep -rn 'attrs=' --include="*.xml" .

# <tree trong XML
grep -rn '<tree' --include="*.xml" .

# name_get method
grep -rn 'def name_get' --include="*.py" .

# @api.multi
grep -rn '@api.multi' --include="*.py" .

# @api.model create (không phải create_multi)
grep -rn '@api.model' --include="*.py" .

# String SQL (có thể false positive)
grep -rn 'cr.execute(' --include="*.py" .

# track_visibility
grep -rn 'track_visibility' --include="*.py" .
```

### Bước 4 — Xuất Migration Report

```
╔══════════════════════════════════════════════════════════════╗
║  UPGRADE ANALYSIS: [module_name]
║  Migration: [from_version] → [to_version]
╚══════════════════════════════════════════════════════════════╝

Độ phức tạp : LOW / MEDIUM / HIGH
Breaking    : X items → phải sửa trước khi chạy
Deprecations: Y items → nên sửa sau
Files bị ảnh: Z files

── BREAKING CHANGES (phải fix) ──────────────────────────────

[BC-001] views/my_views.xml (23 chỗ)
  Vấn đề : attrs= removed từ v17
  Files   : views/form.xml:12, views/list.xml:8, ...
  Trước   : attrs="{'invisible': [('state', '=', 'draft')]}"
  Sau     : invisible="state == 'draft'"

[BC-002] models/my_model.py:45
  Vấn đề : name_get() removed từ v17
  Trước   : def name_get(self): ...
  Sau     : _rec_name = 'display_name' + _compute_display_name

── DEPRECATIONS (nên fix) ────────────────────────────────────

[DEP-001] models/my_model.py:67
  Vấn đề : String SQL deprecated (required SQL() trong v19)
  Fix     : from odoo.tools import SQL + SQL(...) wrapper

── MIGRATION CHECKLIST ───────────────────────────────────────

□ Cập nhật version trong __manifest__.py
□ Fix breaking change 1: attrs → inline expressions
□ Fix breaking change 2: <tree> → <list>
□ Fix breaking change 3: name_get() → _compute_display_name
□ Fix breaking change 4: read_group() → _read_group()
□ Thêm @api.model_create_multi cho create()
□ Cập nhật record rules: company_ids → allowed_company_ids
□ Thêm _check_company_auto + check_company=True
□ Migrate SQL sang SQL() builder (required v19)
□ Thêm `from __future__ import annotations` ở đầu mỗi .py
□ Thêm type hints trên public methods và fields (required v19)
□ Fix groups_id trong res.users.create() → tách thành write() (v19)
□ Chạy tests sau upgrade
□ Test trên staging environment

── MIGRATION SCRIPTS ─────────────────────────────────────────

[Nếu cần data migration — migration scripts chạy ở level db cursor]

# migrations/19.0.1.0.0/pre-migration.py
from odoo.tools import SQL

def migrate(cr, version):
    """Pre-migration: chạy trước khi ORM update schema"""
    if not version:
        return

    # Ví dụ: rename column (DDL - dùng string SQL vì SQL() không hỗ trợ DDL)
    cr.execute("ALTER TABLE my_model RENAME COLUMN old_field TO new_field")

# migrations/19.0.1.0.0/post-migration.py
from odoo.tools import SQL

def migrate(cr, version):
    """Post-migration: chạy sau khi ORM update schema"""
    if not version:
        return

    # Ví dụ: backfill data (DML - dùng SQL() builder)
    cr.execute(SQL(
        """
        UPDATE my_model
        SET new_computed_field = old_source_field
        WHERE new_computed_field IS NULL
        """
    ))
```

## Constraints
- **PHẢI** xác định cả version nguồn và version đích trước khi bắt đầu
- Với multi-version jump (16→19): phải check tất cả intermediate changes
- **KHÔNG** sửa code mà không được user xác nhận
- Nếu không tìm thấy `__manifest__.py` → báo lỗi và dừng

## Best practices
- Migration từ nhiều versions cũ → khuyên upgrade từng bước (không nhảy quá 2 versions)
- Luôn backup database và code trước khi upgrade
- Test trên staging environment trước production
- Với `attrs=` nhiều chỗ → dùng regex replace hàng loạt, không sửa tay từng chỗ
- Sau upgrade: chạy `check-odoo19-compat` để verify không còn deprecated patterns
- Migration scripts trong folder `migrations/{version}/` được Odoo tự chạy khi upgrade
