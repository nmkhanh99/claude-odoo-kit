---
name: odoo-review-module
description: Review toàn diện module Odoo — kiểm tra code quality, security, performance, version compliance và đưa ra báo cáo có điểm số. Kích hoạt khi user nói "review module", "audit module", "kiểm tra code", "check security", "review code quality", "phân tích module", "code review odoo".
---

# Odoo Module Review

## Goal
Review module Odoo theo checklist hệ thống → chấm điểm từng hạng mục → xuất báo cáo có ưu tiên fix rõ ràng.

**Input**: Đường dẫn module hoặc module đang làm việc  
**Output**: Báo cáo review với điểm số, critical issues, warnings và suggestions

## When to use this skill
- "review module", "audit code", "kiểm tra module trước khi deploy"
- "check security holes", "tìm lỗi performance"
- "code có đúng chuẩn Odoo 19 không"
- Trước khi submit PR / deploy production
- Sau khi nhận module từ vendor/OCA

## Instructions

### Bước 1 — Xác định module và version

1. Tìm `__manifest__.py` trong module path
2. Đọc version: format `'19.0.x.x.x'` → Odoo version = số đầu
3. Nếu không rõ version → hỏi user trước khi review

```python
# Đọc manifest để lấy version
# 'version': '19.0.1.0.0' → Odoo 19
```

### Bước 2 — Scan toàn bộ files

Dùng Glob để tìm tất cả files:
```
*.py      → Python models, controllers, wizards
*.xml     → Views, data, security
*.csv     → Access rights
*.js      → OWL components
```

### Bước 3 — Review theo 6 hạng mục

#### Hạng mục 1: Manifest Review (max 10 điểm)

Checklist:
- [ ] Version format đúng (`19.0.x.x.x`)
- [ ] Tất cả dependencies được khai báo
- [ ] Data files liệt kê đầy đủ và đúng thứ tự
- [ ] Assets khai báo đúng chuẩn (v15+)
- [ ] License phù hợp (LGPL-3 cho OCA)
- [ ] `summary`, `description`, `author` đầy đủ

**Thứ tự đúng trong `data`:**
```python
'data': [
    'security/security.xml',          # Groups TRƯỚC
    'security/ir.model.access.csv',   # ACL
    'data/*.xml',                      # Data
    'views/*.xml',                     # Views
    'views/menuitems.xml',            # Menus SAU CÙNG
]
```

#### Hạng mục 2: Security Review (max 20 điểm)

Checklist:
- [ ] `ir.model.access.csv` có cho TẤT CẢ models
- [ ] Record rules cho multi-company (`allowed_company_ids` với v18+)
- [ ] Không dùng `sudo()` bừa bãi
- [ ] Không có hardcoded IDs
- [ ] Field-level security (`groups=` attribute) cho fields nhạy cảm
- [ ] Không có SQL injection (dùng ORM hoặc `SQL()` builder)
- [ ] Input validation cho user-facing endpoints

**Patterns nguy hiểm cần tìm:**
```python
# SQL Injection
self.env.cr.execute(f"SELECT * FROM {table}")  # CRITICAL
self.env.cr.execute("SELECT * FROM " + table)  # CRITICAL

# sudo() lạm dụng
def action_confirm(self):
    self.sudo().write({'state': 'confirmed'})  # WHY SUDO?

# Hardcoded ID
group_id = 42  # NEVER hardcode
```

**Multi-company pattern (v18+):**
```python
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True)
    partner_id = fields.Many2one('res.partner', check_company=True)

# Record rule v18+
# domain_force: [('company_id', 'in', allowed_company_ids)]
```

#### Hạng mục 3: Code Quality Review (max 20 điểm)

Checklist:
- [ ] Không dùng deprecated API (xem version matrix bên dưới)
- [ ] Decorators đúng cho version (`@api.model_create_multi` v17+)
- [ ] Method signatures chuẩn
- [ ] Inheritance patterns đúng
- [ ] Type hints (required v19, recommended v18)
- [ ] Logging thay vì print()
- [ ] Strings dùng `_()` translation wrapper

**Deprecated/Removed API theo version:**
```python
# v17+ — REMOVED (crash ngay lập tức)
attrs="{'invisible': [...]}"   # → invisible="..."
def name_get(self)             # → _rec_name hoặc _compute_display_name
<tree ...>                     # → <list ...>
read_group(...)                # → _read_group(groupby=[], aggregates=[])

# v17+ — Mandatory
@api.model_create_multi        # Thay @api.model cho create()

# v19 — REQUIRED (ERROR nếu thiếu)
SQL()                          # Cho tất cả raw SQL — KHÔNG dùng string SQL
type hints                     # Trên public methods và fields
from __future__ import annotations  # Đầu file để dùng forward references

# v19 — FORBIDDEN
res.users.create({'groups_id': [...]})  # groups_id KHÔNG được set trong create()
```

**Odoo 19 type hints — bắt buộc (ERROR nếu thiếu):**
```python
# ĐÚNG cho v19 — type hints trên mọi public method
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
state: str = fields.Selection([...], default='draft')
```

**groups_id trong res.users — bắt buộc tách 2 bước (v19):**
```python
# SAI (v19) — groups_id KHÔNG cho phép trong create()
user = self.env['res.users'].create({
    'name': 'Test User',
    'login': 'test@test.com',
    'groups_id': [(6, 0, [group_id])],  # ERROR trong Odoo 19!
})

# ĐÚNG (v19) — tạo trước, set groups sau
from odoo.fields import Command
user = self.env['res.users'].create({
    'name': 'Test User',
    'login': 'test@test.com',
})
user.write({'groups_id': [Command.set([group_id])]})
```

#### Hạng mục 4: Performance Review (max 20 điểm)

Checklist:
- [ ] Index trên fields thường search
- [ ] Stored computed fields cho values hay đọc
- [ ] Không có N+1 queries trong computed fields
- [ ] Batch operations (`records.write()` thay vì loop)
- [ ] Cron jobs xử lý theo batch

**N+1 patterns cần tìm:**
```python
# ❌ NGUY HIỂM — N queries trong loop
for record in self:
    # Bất kỳ search/browse nào trong loop không có prefetch trước
    partner = self.env['res.partner'].search([...])

# ✅ Đúng
partner_ids = self.mapped('partner_id').ids
partners = self.env['res.partner'].browse(partner_ids)
```

#### Hạng mục 5: View Review (max 15 điểm)

Checklist:
- [ ] Dùng `<list>` (không phải `<tree>`) từ v17+
- [ ] Visibility syntax đúng cho version
- [ ] Group restrictions trên views/buttons nhạy cảm
- [ ] Xpath expressions đúng cú pháp
- [ ] Không duplicate view IDs

**View syntax theo version:**
```xml
<!-- v17+ -->
<field name="x" invisible="state != 'draft'"/>
<field name="y" readonly="is_locked"/>
<button invisible="state == 'draft'" .../>
<list string="...">  <!-- KHÔNG phải <tree> -->
```

#### Hạng mục 6: Test Coverage (max 15 điểm)

Checklist:
- [ ] Test files tồn tại trong `tests/`
- [ ] `tests/__init__.py` import đúng
- [ ] Tests có `@tagged` decorator
- [ ] Covers: CRUD, workflow transitions, constraints
- [ ] Security tests (`with_user()`, `assertRaises(AccessError)`)
- [ ] setUpClass() với `tracking_disable=True`

**Test structure chuẩn Odoo 19:**
```python
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import AccessError, ValidationError

@tagged('post_install', '-at_install')
class TestMyModel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Setup test data

    def test_create_basic(self):
        """Test tạo record cơ bản"""
        record = self.env['my.model'].create({'name': 'Test'})
        self.assertTrue(record.id)

    def test_workflow(self):
        """Test workflow transitions"""
        record = self.env['my.model'].create({'name': 'Test'})
        self.assertEqual(record.state, 'draft')
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')
```

### Bước 4 — Tính điểm và xuất báo cáo

```
╔══════════════════════════════════════════════════════════════╗
║  CODE REVIEW: [module_name]
║  Version    : Odoo [X.0]
║  Reviewed   : [date]
╚══════════════════════════════════════════════════════════════╝

ĐIỂM TỔNG: [tổng]/100

┌─────────────────────────────┬──────┬────────┐
│ Hạng mục                    │ Điểm │ Tối đa │
├─────────────────────────────┼──────┼────────┤
│ 1. Manifest                 │  X   │   10   │
│ 2. Security                 │  X   │   20   │
│ 3. Code Quality             │  X   │   20   │
│ 4. Performance              │  X   │   20   │
│ 5. Views                    │  X   │   15   │
│ 6. Tests                    │  X   │   15   │
└─────────────────────────────┴──────┴────────┘

── CRITICAL (phải fix ngay) ─────────────────────────────────

[SECURITY] models/my_model.py:45
  Vấn đề: SQL injection vulnerability
  Code  : self.env.cr.execute(f"SELECT * FROM {table}")
  Fix   : Dùng ORM hoặc SQL() builder

── WARNINGS (nên fix) ───────────────────────────────────────

[DEPRECATED] views/my_views.xml:23
  Vấn đề: Dùng <tree> tag (removed v17+)
  Fix   : Đổi thành <list>

[PERFORMANCE] models/my_model.py:78
  Vấn đề: N+1 query pattern trong computed field
  Fix   : [code fix cụ thể]

── SUGGESTIONS (nice to have) ───────────────────────────────

[QUALITY] models/my_model.py:100
  Gợi ý: Thiếu `from __future__ import annotations` ở đầu file

── FILES REVIEWED ───────────────────────────────────────────

│ File                              │ Issues │
│ __manifest__.py                   │   0    │
│ models/my_model.py                │   3    │
│ views/my_views.xml                │   2    │
│ security/ir.model.access.csv      │   1    │

── ĐIỂM MẠNH ────────────────────────────────────────────────

✓ [Ghi nhận những gì code đang làm tốt]
```

## Constraints
- **CẤM** tự sửa code — chỉ báo cáo, đề xuất
- **PHẢI** xác định version trước khi review
- Nếu không tìm thấy `__manifest__.py` → báo lỗi, dừng
- Scan **toàn bộ** files — không skip subfolder

## Best practices
- Sắp xếp issues: Critical → Warning → Suggestion
- Trong cùng severity: sắp xếp theo file path
- Luôn ghi nhận điểm tốt (dễ chấp nhận feedback hơn)
- Với security issues: ưu tiên cao nhất, luôn đứng đầu báo cáo
- Refer `check-odoo19-compat` để scan deprecated API chi tiết hơn
