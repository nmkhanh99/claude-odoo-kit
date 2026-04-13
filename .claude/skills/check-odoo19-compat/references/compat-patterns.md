# Odoo 19 Compatibility Patterns
# Danh sách đầy đủ deprecated/removed patterns + cách fix

## Severity legend
- `ERROR` — sẽ crash / raise AttributeError / không load được module
- `WARN`  — DeprecationWarning, vẫn chạy nhưng sẽ break ở version tiếp theo
- `INFO`  — style/best-practice, không ảnh hưởng runtime

---

## Python Patterns

### P01 — name_get() removed
```
Severity : ERROR
Pattern  : def name_get(self):
Since    : Odoo 17 (removed in 17, deprecated từ 16)
Fix      : _rec_name = 'field_name'
           hoặc: display_name = fields.Char(compute='_compute_display_name')
Note     : Nếu cần format phức tạp hơn field đơn → dùng _compute_display_name
```

### P02 — @api.multi removed
```
Severity : WARN
Pattern  : @api.multi
Since    : Odoo 14
Fix      : Bỏ hoàn toàn decorator — tất cả method mặc định là recordset
```

### P03 — @api.one removed
```
Severity : ERROR
Pattern  : @api.one
Since    : Odoo 14
Fix      : Bỏ decorator, thêm `for rec in self:` loop trong body nếu cần
```

### P04 — @api.returns removed
```
Severity : WARN
Pattern  : @api.returns
Since    : Odoo 14
Fix      : Bỏ decorator
```

### P05 — read_group() → _read_group()
```
Severity : ERROR
Pattern  : \.read_group\(
Since    : Odoo 17 (API hoàn toàn thay đổi)
Fix      : ._read_group() — signature khác, cần đọc docs mới
           Old: model.read_group(domain, fields, groupby)
           New: model._read_group(domain, groupby, aggregates)
Note     : Return type cũng khác — không chỉ rename
```

### P06 — self._cr / self._uid / self._context deprecated
```
Severity : INFO
Pattern  : self\._cr\b | self\._uid\b | self\._context\b
Since    : Odoo 10+
Fix      : self.env.cr | self.env.uid | self.env.context
```

### P07 — Raw SQL without SQL() wrapper
```
Severity : WARN
Pattern  : self\.env\.cr\.execute\(['"f]  (non-SQL() call)
Since    : Odoo 17
Fix      : from odoo.tools import SQL
           self.env.cr.execute(SQL("SELECT %s", (val,)))
Note     : Cần để tránh SQL injection — Odoo 17+ enforce
```

### P08 — fields.datetime.now() wrong case
```
Severity : ERROR
Pattern  : fields\.datetime\.now\(\)
Since    : Always wrong
Fix      : fields.Datetime.now()  (chữ hoa D)
```

### P09 — .sudo(uid) deprecated
```
Severity : WARN
Pattern  : \.sudo\(\w+\)  (sudo với argument)
Since    : Odoo 10
Fix      : .with_user(uid).sudo()  hoặc  .with_user(uid)
```

### P10 — openerp import
```
Severity : ERROR
Pattern  : from openerp | import openerp
Since    : Odoo 10
Fix      : from odoo | import odoo
```

### P11 — @api.cr / @api.uid / @api.model_cr legacy
```
Severity : ERROR
Pattern  : @api\.cr\b | @api\.uid\b | @api\.model_cr\b
Since    : Odoo 13
Fix      : Bỏ decorator, dùng self.env.cr / self.env.uid
```

### P12 — SUPERUSER_ID import
```
Severity : WARN
Pattern  : from odoo import.*SUPERUSER_ID | SUPERUSER_ID
Since    : Odoo 14 (deprecated)
Fix      : self.env['model'].sudo() — không cần SUPERUSER_ID literal
```

### P13 — .search() with old domain syntax
```
Severity : INFO
Pattern  : \.search\(\[.*'active_test'
Since    : Odoo 16
Fix      : .with_context(active_test=False).search(...)
```

### P14 — _columns class attribute
```
Severity : ERROR
Pattern  : _columns\s*=\s*\{
Since    : Odoo 10 (Old API removed)
Fix      : Dùng fields.FieldType() trực tiếp trong class body
```

### P15 — fields.related() old syntax
```
Severity : ERROR
Pattern  : fields\.related\(.*type=
Since    : Odoo 10
Fix      : fields.Many2one(..., related='field.subfield')
```

---

## XML Patterns

### X01 — <tree> tag
```
Severity : ERROR
Pattern  : <tree[\s>]
Since    : Odoo 17 (renamed to <list>)
Fix      : <list ...>
Note     : Áp dụng cho cả opening và closing tag
```

### X02 — attrs= deprecated
```
Severity : WARN
Pattern  : \battrs=
Since    : Odoo 17
Fix      : invisible="expr" | readonly="expr" | required="expr"
           Old: attrs="{'invisible': [('state', '=', 'draft')]}"
           New: invisible="state == 'draft'"
Note     : Inline domain expression — không phải Python list syntax
```

### X03 — states= attribute on button/field
```
Severity : WARN
Pattern  : \bstates=["'][^"']+["']  (trong field/button tag)
Since    : Odoo 17
Fix      : invisible="state not in ('draft', 'confirmed')"
```

### X04 — category_id on res.groups
```
Severity : ERROR
Pattern  : name="category_id"  (trong res.groups record)
Since    : Odoo 17 (groups structure changed)
Fix      : <field name="privilege_id" ref="module.res_groups_privilege_xxx"/>
```

### X05 — old Many2many rel syntax in view
```
Severity : INFO
Pattern  : widget="many2many_tags"  (still works but check)
Since    : Odoo 16+
Note     : many2many_tags vẫn OK, nhưng many2many_checkboxes có thể cần review
```

### X06 — <field widget="statusbar"> without statusbar_visible
```
Severity : INFO
Pattern  : widget="statusbar"(?!.*statusbar_visible)
Since    : Always best practice
Fix      : Thêm statusbar_visible="draft,confirmed,done" để UX tốt hơn
```

### X07 — groups string trong action/view
```
Severity : WARN
Pattern  : <field name="groups_id"  (trong ir.actions)
Since    : Odoo 17
Fix      : Dùng groups= attribute trực tiếp trên menuitem hoặc field
```

---

## False Positive Exclusions
Các pattern trông giống deprecated nhưng KHÔNG phải:

| Pattern | Lý do bỏ qua |
|---------|--------------|
| `from odoo import` | Đúng, không phải openerp |
| `self.env.cr.execute(SQL(...))` | Đúng format mới |
| `fields.Datetime.now()` | Đúng (chữ hoa) |
| `_rec_name = 'name'` | Đúng cách replace name_get |
| `invisible="state == 'draft'"` | Đúng syntax mới |
| `<list string=` | Đúng (không phải tree) |
| `def _compute_display_name` | Đúng cách mới |

---

## Quick Reference Summary

| # | Pattern | Severity | Fix |
|---|---------|----------|-----|
| P01 | `def name_get` | ERROR | `_rec_name` |
| P02 | `@api.multi` | WARN | bỏ decorator |
| P03 | `@api.one` | ERROR | bỏ + for loop |
| P04 | `read_group(` | ERROR | `_read_group(` |
| P05 | `self._cr` | INFO | `self.env.cr` |
| P06 | `self._uid` | INFO | `self.env.uid` |
| P07 | raw SQL execute | WARN | `SQL()` wrapper |
| P08 | `fields.datetime.now()` | ERROR | `fields.Datetime.now()` |
| P09 | `.sudo(uid)` | WARN | `.with_user(uid)` |
| P10 | `from openerp` | ERROR | `from odoo` |
| P11 | `@api.cr/@api.uid` | ERROR | bỏ decorator |
| P12 | `SUPERUSER_ID` | WARN | `.sudo()` |
| P13 | `_columns = {` | ERROR | field declarations |
| X01 | `<tree>` | ERROR | `<list>` |
| X02 | `attrs=` | WARN | `invisible=`/`readonly=` |
| X03 | `states=` on tag | WARN | `invisible=` |
| X04 | `category_id` on group | ERROR | `privilege_id` |
