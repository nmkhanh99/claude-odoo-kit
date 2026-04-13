# Template: model-extend
# Dùng khi: [MODIFY] models/<name>.py — thêm field/method vào model đã có (_inherit)

## Pattern 1: Thêm field vào model base (res.users, stock.picking, …)

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class {CLASS_NAME}(models.Model):
    _inherit = '{BASE_MODEL}'

    # ── New Fields ────────────────────────────────────────────────
    {field_name} = fields.{FieldType}(
        '{relation_model_if_any}',          # bỏ dòng này nếu không phải relational
        string=_('{Label}'),
        {required=True,}                    # tuỳ BRD
        {tracking=True,}                    # nếu BRD yêu cầu audit trail
    )

    # ── New Methods (nếu có) ──────────────────────────────────────
    # def action_xxx(self): ...
```

## Pattern 2: Thêm computed field có store

```python
class {CLASS_NAME}(models.Model):
    _inherit = '{BASE_MODEL}'

    {computed_field} = fields.{Type}(
        string=_('{Label}'),
        compute='_compute_{computed_field}',
        store=True,
    )

    @api.depends('{depends_field}')
    def _compute_{computed_field}(self):
        for rec in self:
            rec.{computed_field} = ...
```

## Pattern 3: Override create / write

```python
class {CLASS_NAME}(models.Model):
    _inherit = '{BASE_MODEL}'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # custom logic trước khi create
            pass
        return super().create(vals_list)

    def write(self, vals):
        # custom logic trước khi write
        return super().write(vals)
```

## Lưu ý

- Chỉ paste đoạn code cần thêm, kèm hướng dẫn "thêm vào sau dòng X trong class"
- `_inherit` không cần `_name` (trừ khi tạo model mới từ base)
- Nhiều `_inherit` trong cùng module: mỗi file một class, không gộp
- Đừng khai báo lại field đã có trong base model — chỉ `_inherit` để thêm mới
