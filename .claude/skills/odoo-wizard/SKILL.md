---
name: odoo-wizard
description: Tạo Wizard (TransientModel) Odoo 19 — confirmation dialog, batch update, report wizard, import wizard, multi-step wizard. Kích hoạt khi user nói "tạo wizard", "dialog xác nhận", "batch action wizard", "popup form", "transient model", "multi-step form".
---

# Odoo Wizard Patterns (v19)

## Goal
Tạo wizards (TransientModel) đúng chuẩn Odoo 19 cho các use case phổ biến — confirmation, batch update, report params, import, multi-step.

**Input**: Mô tả wizard cần tạo, model target, actions cần thực hiện  
**Output**: TransientModel Python + View XML + ACL entry

## When to use this skill
- "tạo wizard xác nhận", "confirmation dialog"
- "batch update nhiều records", "wizard cho action"
- "tạo wizard nhập ngày cho báo cáo"
- "import CSV qua wizard", "multi-step form"

## Instructions

### Bước 1 — Cấu trúc Wizard (v19)

```python
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MyWizard(models.TransientModel):
    _name = 'my.module.wizard'
    _description = 'My Wizard'

    # Context-dependent fields
    model_id: int = fields.Many2one(
        comodel_name='my.model',
        string='Record',
        default=lambda self: self.env.context.get('active_id'),
    )
    model_ids: list = fields.Many2many(
        comodel_name='my.model',
        string='Records',
        default=lambda self: self.env.context.get('active_ids'),
    )

    # Wizard fields
    date: fields.Date = fields.Date(
        string='Date',
        default=fields.Date.today,
        required=True,
    )
    note: str = fields.Text(string='Notes')

    # v19: type hints bắt buộc
    def action_confirm(self) -> dict[str, Any]:
        """Execute wizard action."""
        self.ensure_one()
        if not self.model_id:
            raise UserError(_("No record selected."))
        self.model_id.write({
            'date': self.date,
            'notes': self.note,
        })
        return {'type': 'ir.actions.act_window_close'}
```

**View:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="my_wizard_view_form" model="ir.ui.view">
        <field name="name">my.module.wizard.form</field>
        <field name="model">my.module.wizard</field>
        <field name="arch" type="xml">
            <form string="My Wizard">
                <group>
                    <field name="model_id" readonly="1"
                           invisible="not model_id"/>
                    <field name="date"/>
                    <field name="note"/>
                </group>
                <footer>
                    <button name="action_confirm" string="Confirm"
                            type="object" class="btn-primary"/>
                    <button string="Cancel"
                            class="btn-secondary"
                            special="cancel"/>
                </footer>
            </form>
        </field>
    </record>

    <!-- Bind đến model (hiện trong Action menu) -->
    <record id="my_wizard_action" model="ir.actions.act_window">
        <field name="name">My Wizard</field>
        <field name="res_model">my.module.wizard</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
        <field name="binding_model_id" ref="my_module.model_my_module_my_model"/>
        <field name="binding_view_types">form,list</field>
    </record>
</odoo>
```

**ACL (ir.model.access.csv):**
```csv
access_my_wizard_user,my.module.wizard.user,model_my_module_wizard,base.group_user,1,1,1,1
```

### Bước 2 — Confirmation Dialog

```python
class ConfirmationWizard(models.TransientModel):
    _name = 'my.confirm.wizard'
    _description = 'Confirmation Dialog'

    message: str = fields.Text(
        string='Message',
        readonly=True,
        default=lambda self: self._default_message(),
    )

    @api.model
    def _default_message(self) -> str:
        active_ids = self.env.context.get('active_ids', [])
        count = len(active_ids)
        return _("Are you sure you want to process %s record(s)?", count)

    def action_confirm(self) -> dict[str, Any]:
        """Process confirmed action."""
        active_ids = self.env.context.get('active_ids', [])
        records = self.env['my.model'].browse(active_ids)
        for record in records:
            record.action_process()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Processed %s records.', len(records)),
                'type': 'success',
                'sticky': False,
            }
        }
```

```xml
<form string="Confirm">
    <group>
        <field name="message" nolabel="1"/>
    </group>
    <footer>
        <button name="action_confirm" string="Yes, Proceed"
                type="object" class="btn-primary"/>
        <button string="Cancel" class="btn-secondary" special="cancel"/>
    </footer>
</form>
```

### Bước 3 — Batch Update Wizard

```python
class BatchUpdateWizard(models.TransientModel):
    _name = 'my.batch.update.wizard'
    _description = 'Batch Update'

    record_ids: list = fields.Many2many(
        comodel_name='my.model',
        string='Records to Update',
        default=lambda self: self._default_records(),
    )
    new_state: str = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
        ],
        string='New Status',
        required=True,
    )
    update_date: bool = fields.Boolean(string='Update Date', default=False)
    date: fields.Date = fields.Date(string='New Date')

    @api.model
    def _default_records(self) -> 'my.model':
        active_ids = self.env.context.get('active_ids', [])
        return self.env['my.model'].browse(active_ids)

    def action_update(self) -> dict[str, Any]:
        """Apply batch update."""
        vals: dict[str, Any] = {'state': self.new_state}
        if self.update_date and self.date:
            vals['date'] = self.date
        self.record_ids.write(vals)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Updated %s records.', len(self.record_ids)),
                'type': 'success',
                'sticky': False,
            }
        }
```

### Bước 4 — Report Wizard (Date Range)

```python
class ReportWizard(models.TransientModel):
    _name = 'my.report.wizard'
    _description = 'Report Parameters'

    date_from: fields.Date = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1),
    )
    date_to: fields.Date = fields.Date(
        string='To Date',
        required=True,
        default=fields.Date.today,
    )
    partner_ids: list = fields.Many2many(
        comodel_name='res.partner',
        string='Partners',
        help='Leave empty for all partners',
    )
    output_format: str = fields.Selection(
        selection=[('pdf', 'PDF'), ('xlsx', 'Excel')],
        string='Format',
        default='pdf',
        required=True,
    )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self) -> None:
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise UserError(_("Start date must be before end date."))

    def action_print(self) -> dict[str, Any]:
        """Generate report."""
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        records = self.env['my.model'].search(domain)
        if self.output_format == 'pdf':
            return self.env.ref('my_module.report_my_model').report_action(records)
        else:
            return self._export_xlsx(records)

    def _export_xlsx(self, records: 'my.model') -> dict[str, Any]:
        """Export to Excel."""
        # TODO: implement xlsx export
        raise UserError(_("Excel export not implemented yet."))
```

### Bước 5 — Multi-Step Wizard

```python
class SelectionWizard(models.TransientModel):
    _name = 'my.selection.wizard'
    _description = 'Multi-Step Wizard'

    step: str = fields.Selection([
        ('select', 'Selection'),
        ('configure', 'Configuration'),
        ('confirm', 'Confirmation'),
    ], string='Step', default='select')

    # Step 1
    template_id: int = fields.Many2one('my.template', string='Template')

    # Step 2
    name: str = fields.Char(string='Name')
    date: fields.Date = fields.Date(string='Date')

    # Step 3 — Summary
    summary: str = fields.Text(
        string='Summary',
        compute='_compute_summary',
    )

    @api.depends('template_id', 'name', 'date')
    def _compute_summary(self) -> None:
        for wizard in self:
            wizard.summary = _(
                "Template: %(template)s\nName: %(name)s\nDate: %(date)s",
                template=wizard.template_id.name or _('None'),
                name=wizard.name or _('Not set'),
                date=wizard.date or _('Not set'),
            )

    def action_next(self) -> dict[str, Any]:
        """Next step."""
        self.ensure_one()
        if self.step == 'select':
            if not self.template_id:
                raise UserError(_("Please select a template."))
            self.step = 'configure'
        elif self.step == 'configure':
            if not self.name:
                raise UserError(_("Please enter a name."))
            self.step = 'confirm'
        return self._reopen()

    def action_previous(self) -> dict[str, Any]:
        """Previous step."""
        self.ensure_one()
        if self.step == 'configure':
            self.step = 'select'
        elif self.step == 'confirm':
            self.step = 'configure'
        return self._reopen()

    def action_create(self) -> dict[str, Any]:
        """Create record từ wizard."""
        self.ensure_one()
        record = self.env['my.model'].create({
            'template_id': self.template_id.id,
            'name': self.name,
            'date': self.date,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'my.model',
            'res_id': record.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _reopen(self) -> dict[str, Any]:
        """Reopen wizard."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
```

```xml
<!-- Multi-step view với invisible theo step -->
<form string="Setup Wizard">
    <!-- Step 1: Selection -->
    <group invisible="step != 'select'">
        <field name="template_id"/>
    </group>

    <!-- Step 2: Configuration -->
    <group invisible="step != 'configure'">
        <field name="name"/>
        <field name="date"/>
    </group>

    <!-- Step 3: Confirmation -->
    <group invisible="step != 'confirm'">
        <field name="summary" nolabel="1"/>
    </group>

    <field name="step" invisible="1"/>

    <footer>
        <button name="action_previous" string="Previous"
                type="object"
                invisible="step == 'select'"/>
        <button name="action_next" string="Next"
                type="object" class="btn-primary"
                invisible="step == 'confirm'"/>
        <button name="action_create" string="Create"
                type="object" class="btn-primary"
                invisible="step != 'confirm'"/>
        <button string="Cancel" special="cancel"/>
    </footer>
</form>
```

### Bước 6 — Wizard Return Types

```python
# Đóng wizard
return {'type': 'ir.actions.act_window_close'}

# Hiện notification
return {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'title': _('Success'),
        'message': _('Operation completed.'),
        'type': 'success',   # success, warning, danger, info
        'sticky': False,
    }
}

# Mở record
return {
    'type': 'ir.actions.act_window',
    'res_model': 'my.model',
    'res_id': record_id,
    'view_mode': 'form',
    'target': 'current',
}

# Mở list — v17+: view_mode dùng 'list' không phải 'tree'
return {
    'type': 'ir.actions.act_window',
    'name': _('Created Records'),
    'res_model': 'my.model',
    'view_mode': 'list,form',
    'domain': [('id', 'in', record_ids)],
}

# Reload trang
return {'type': 'ir.actions.client', 'tag': 'reload'}
```

### Bước 7 — Mở Wizard từ Python

```python
def action_open_wizard(self) -> dict[str, Any]:
    """Open wizard từ button."""
    return {
        'type': 'ir.actions.act_window',
        'name': _('My Wizard'),
        'res_model': 'my.module.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {
            'default_model_id': self.id,
            'default_model_ids': self.ids,
            'active_id': self.id,
            'active_ids': self.ids,
            'active_model': self._name,
        },
    }
```

## Constraints
- **PHẢI** khai báo ACL trong `ir.model.access.csv` — wizards cần ACL riêng
- **LUÔN** dùng `self.ensure_one()` trong action methods
- **KHÔNG** để wizard có logic phức tạp — delegate sang model
- Return type của action methods **phải** là `dict[str, Any]` (v19)

## Best practices
- Truyền active_id/active_ids qua context
- Validate input với `@api.constrains` hoặc trong action method
- Cung cấp feedback: notification hoặc mở result view
- Multi-step: dùng `invisible=` theo step thay vì nhiều views
- Wizard action return `list,form` (không phải `tree,form`) từ v17+
