# Template: model-new
# Dùng khi: [ADD] models/<name>.py — tạo model mới hoàn toàn

## Context cần thu thập trước khi sinh
- `MODEL_NAME`      : technical name, vd `stock.inventory.approval`
- `CLASS_NAME`      : PascalCase, vd `StockInventoryApproval`
- `DESCRIPTION`     : mô tả ngắn bằng tiếng Anh
- `SEQUENCE_CODE`   : code sequence, vd `stock.inventory.approval`
- `FIELDS`          : list từ BRD §2.3 — [(field_name, type, string, required, tracking)]
- `STATES`          : list từ BRD §3.2 — [(value, label)]
- `HAS_LINES`       : True nếu có line_ids (One2many)
- `LINE_MODEL`      : nếu HAS_LINES, tên model line

## Generated output

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class {CLASS_NAME}(models.Model):
    _name = '{MODEL_NAME}'
    _description = _('{DESCRIPTION}')
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    # ── Identity ──────────────────────────────────────────────
    name = fields.Char(
        string=_('Reference'),
        default='New',
        copy=False,
        readonly=True,
        tracking=True,
    )

    # ── Core Fields (from BRD §2.3) ───────────────────────────
    # {FIELDS — sinh từng field theo type}

    # ── State Machine ─────────────────────────────────────────
    state = fields.Selection([
        # {STATES}
    ], string=_('Status'), default='{FIRST_STATE}',
       required=True, tracking=True, index=True, copy=False)

    # ── Relations ─────────────────────────────────────────────
    # {line_ids nếu HAS_LINES}

    # ── System Fields ─────────────────────────────────────────
    company_id = fields.Many2one(
        'res.company', string=_('Company'),
        default=lambda self: self.env.company,
        required=True, readonly=True,
    )
    requested_by = fields.Many2one(
        'res.users', string=_('Requested By'),
        default=lambda self: self.env.user,
        required=True, tracking=True,
    )

    # ── CRUD Override ─────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('{SEQUENCE_CODE}')
                    or 'New'
                )
        return super().create(vals_list)

    # ── Workflow Actions ──────────────────────────────────────
    def action_confirm(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Chỉ có thể xác nhận phiếu ở trạng thái Draft.'))
        self.write({'state': 'confirmed'})

    def action_cancel(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_('Không thể hủy phiếu đã hoàn thành.'))
            rec.write({'state': 'cancel'})
```

## Field type mappings (BRD → Odoo)

| BRD type | Odoo field |
|----------|-----------|
| VARCHAR | `fields.Char(string=_('...'), required=True)` |
| Many2one | `fields.Many2one('model.name', string=_('...'), required=True, tracking=True)` |
| Many2many | `fields.Many2many('model.name', 'rel_table', 'this_id', 'other_id', string=_('...'))` |
| SELECTION | `fields.Selection([('val','Label'),...], string=_('...'), required=True)` |
| FLOAT | `fields.Float(string=_('...'), digits='Product Unit of Measure')` |
| DATE | `fields.Date(string=_('...'), default=fields.Date.context_today, required=True)` |
| DATETIME | `fields.Datetime(string=_('...'), default=fields.Datetime.now)` |
| TEXT | `fields.Text(string=_('...'))` |
| Boolean | `fields.Boolean(string=_('...'), default=False)` |
| Binary | `fields.Binary(string=_('...'), attachment=True)` |
| Integer | `fields.Integer(string=_('...'))` |
