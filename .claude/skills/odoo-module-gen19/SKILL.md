---
name: odoo-module-gen19
description: Tạo scaffold module Odoo 19 chuẩn — manifest, model với type hints, views, security, OWL 3.x component. Kích hoạt khi user nói "tạo module", "scaffold module", "tạo model mới", "generate module", "tạo module odoo", "khởi tạo module".
---

# Odoo 19 Module Generator

## Goal
Sinh code scaffold cho module Odoo 19 hoàn chỉnh — manifest, model, views, security, OWL component — đúng chuẩn v19 bắt buộc.

**Input**: Tên module, tên model, danh sách fields cần thiết  
**Output**: Toàn bộ file scaffold sẵn sàng dùng

## When to use this skill
- "tạo module mới", "scaffold module odoo 19"
- "tạo model với view và security"
- "khởi tạo module từ đầu"
- Bắt đầu dự án Odoo 19 mới

## Instructions

### Bước 1 — Thu thập thông tin

Hỏi user nếu chưa rõ:
- Tên module (`my_module`)
- Tên model (`my.model`)
- Fields cần thiết
- Có cần OWL component không?
- Inherit module nào (`base`, `mail`, `sale`...)?

### Bước 2 — `__manifest__.py`

```python
# -*- coding: utf-8 -*-
{
    'name': '{Module Title}',
    'version': '19.0.1.0.0',
    'category': '{Category}',
    'summary': '{Short description}',
    'description': """
{Detailed description}
    """,
    'author': '{Author}',
    'website': '{Website}',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        # THỨ TỰ BẮT BUỘC
        'security/{module_name}_security.xml',     # 1. Groups trước
        'security/ir.model.access.csv',            # 2. ACL
        'views/{model_name}_views.xml',            # 3. Views
        'views/menuitems.xml',                     # 4. Menus sau cùng
    ],
    'assets': {
        'web.assets_backend': [
            '{module_name}/static/src/**/*.js',
            '{module_name}/static/src/**/*.xml',
            '{module_name}/static/src/**/*.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

### Bước 3 — Model (v19 — Type Hints bắt buộc)

```python
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Optional

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command
from odoo.tools import SQL


class {ModelName}(models.Model):
    _name = '{module_name}.{model_name}'
    _description = '{Model Description}'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _check_company_auto = True

    # === FIELDS CƠ BẢN === #
    name: str = fields.Char(
        string='Name',
        required=True,
        tracking=True,
    )
    active: bool = fields.Boolean(default=True)
    sequence: int = fields.Integer(default=10)
    description: str = fields.Text(string='Description')

    # === COMPANY + RELATIONAL === #
    company_id: int = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    partner_id: int = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        tracking=True,
        check_company=True,
    )
    user_id: int = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
        check_company=True,
    )
    line_ids: list = fields.One2many(
        comodel_name='{module_name}.{model_name}.line',
        inverse_name='parent_id',
        string='Lines',
        copy=True,
    )

    # === STATE === #
    state: str = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
        copy=False,
        index=True,
    )

    # === TIỀN TỆ === #
    currency_id: int = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    amount: float = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
    )

    # === COMPUTED === #
    total_amount: float = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True,
    )

    @api.depends('line_ids.amount')
    def _compute_total_amount(self) -> None:
        """Tính tổng từ các dòng."""
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))

    # === CONSTRAINTS === #
    @api.constrains('amount')
    def _check_amount(self) -> None:
        """Validate amount không âm."""
        for record in self:
            if record.amount < 0:
                raise ValidationError(_("Amount must be positive."))

    # v19: Dùng models.Constraint thay _sql_constraints (nếu cần)
    # _check_name_unique = models.Constraint(
    #     'UNIQUE(company_id, name)',
    #     'Name must be unique per company!',
    # )
    _sql_constraints = [
        ('name_company_uniq', 'unique(company_id, name)',
         'Name must be unique per company!'),
    ]

    # === CRUD (v19 — type hints bắt buộc) === #
    @api.model_create_multi
    def create(self, vals_list: list[dict[str, Any]]) -> '{ModelName}':
        """Tạo records với sequence."""
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    '{module_name}.{model_name}'
                ) or _('New')
        return super().create(vals_list)

    def write(self, vals: dict[str, Any]) -> bool:
        """Write với validation."""
        if 'state' in vals and vals['state'] == 'done':
            for record in self:
                if not record.line_ids:
                    raise UserError(_("Cannot complete without lines."))
        return super().write(vals)

    def unlink(self) -> bool:
        """Ngăn xóa records không phải draft."""
        if any(rec.state != 'draft' for rec in self):
            raise UserError(_("Cannot delete non-draft records."))
        return super().unlink()

    def copy(self, default: Optional[dict[str, Any]] = None) -> '{ModelName}':
        """Copy với suffix tên."""
        default = dict(default or {})
        default.setdefault('name', _("%s (Copy)", self.name))
        return super().copy(default)

    # === ACTION METHODS === #
    def action_confirm(self) -> None:
        """Confirm records."""
        self.write({'state': 'confirmed'})

    def action_done(self) -> None:
        """Mark as done."""
        self.write({'state': 'done'})

    def action_cancel(self) -> None:
        """Cancel records."""
        self.write({'state': 'cancelled'})

    def action_draft(self) -> None:
        """Reset to draft."""
        self.write({'state': 'draft'})

    # === SQL (v19 — SQL() bắt buộc) === #
    def _get_report_data(self) -> list[dict[str, Any]]:
        """Dùng SQL() builder cho raw SQL."""
        query = SQL(
            """
            SELECT
                m.id,
                m.name,
                m.state,
                COALESCE(SUM(l.amount), 0) as total
            FROM %s m
            LEFT JOIN %s l ON l.parent_id = m.id
            WHERE m.company_id IN %s
            GROUP BY m.id, m.name, m.state
            ORDER BY m.create_date DESC
            """,
            SQL.identifier(self._table),
            SQL.identifier('{module_name}_{model_name}_line'),
            tuple(self.env.companies.ids),
        )
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    # === ACTION MỞ VIEW === #
    def action_view_records(self) -> dict[str, Any]:
        """Mở list view của records liên quan."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'list,form',    # v17+: 'list' không phải 'tree'
            'domain': [('partner_id', '=', self.partner_id.id)],
            'context': {'default_partner_id': self.partner_id.id},
        }
```

### Bước 4 — View (v19 — `invisible=` không phải `attrs=`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- FORM VIEW -->
    <record id="{model_name}_view_form" model="ir.ui.view">
        <field name="name">{module_name}.{model_name}.form</field>
        <field name="model">{module_name}.{model_name}</field>
        <field name="arch" type="xml">
            <form string="{Model Title}">
                <header>
                    <!-- v17+: Direct Python expressions, không dùng attrs -->
                    <button name="action_confirm" string="Confirm"
                            type="object" class="btn-primary"
                            invisible="state != 'draft'"/>
                    <button name="action_done" string="Done"
                            type="object"
                            invisible="state != 'confirmed'"/>
                    <button name="action_cancel" string="Cancel"
                            type="object"
                            invisible="state in ('done', 'cancelled')"/>
                    <button name="action_draft" string="Reset"
                            type="object"
                            invisible="state != 'cancelled'"/>
                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box"/>
                    <widget name="web_ribbon" title="Archived"
                            bg_color="bg-danger"
                            invisible="active"/>
                    <div class="oe_title">
                        <h1>
                            <field name="name" placeholder="Name..."/>
                        </h1>
                    </div>
                    <group>
                        <group>
                            <field name="partner_id"/>
                            <field name="user_id"/>
                        </group>
                        <group>
                            <field name="company_id"
                                   groups="base.group_multi_company"/>
                            <field name="total_amount"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Lines" name="lines">
                            <field name="line_ids">
                                <list editable="bottom">
                                    <field name="sequence" widget="handle"/>
                                    <field name="name"/>
                                    <field name="quantity"/>
                                    <field name="price_unit"/>
                                    <field name="amount"/>
                                </list>
                            </field>
                        </page>
                    </notebook>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>

    <!-- LIST VIEW (v17+: <list> không phải <tree>) -->
    <record id="{model_name}_view_list" model="ir.ui.view">
        <field name="name">{module_name}.{model_name}.list</field>
        <field name="model">{module_name}.{model_name}</field>
        <field name="arch" type="xml">
            <list string="{Model Title}"
                  decoration-danger="state == 'cancelled'"
                  decoration-success="state == 'done'">
                <field name="name"/>
                <field name="partner_id"/>
                <field name="user_id"/>
                <field name="state" widget="badge"
                       decoration-success="state == 'done'"
                       decoration-warning="state == 'confirmed'"
                       decoration-info="state == 'draft'"/>
                <field name="amount" sum="Total"/>
            </list>
        </field>
    </record>

    <!-- ACTION -->
    <record id="{model_name}_action" model="ir.actions.act_window">
        <field name="name">{Model Title}</field>
        <field name="res_model">{module_name}.{model_name}</field>
        <field name="view_mode">list,form</field>
        <field name="context">{'search_default_my_records': 1}</field>
    </record>
</odoo>
```

### Bước 5 — Security

**`security/{module_name}_security.xml`**:
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="module_category_{module_name}" model="ir.module.category">
        <field name="name">{Module Name}</field>
        <field name="sequence">100</field>
    </record>

    <record id="group_{module_name}_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_{module_name}"/>
    </record>

    <record id="group_{module_name}_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_{module_name}"/>
        <field name="implied_ids" eval="[(4, ref('group_{module_name}_user'))]"/>
    </record>

    <!-- Multi-company rule (v18+: dùng allowed_company_ids) -->
    <record id="rule_{model_name}_company" model="ir.rule">
        <field name="name">{Model Name}: Multi-Company</field>
        <field name="model_id" ref="model_{module_name}_{model_name}"/>
        <field name="global" eval="True"/>
        <field name="domain_force">[
            '|',
            ('company_id', '=', False),
            ('company_id', 'in', allowed_company_ids)
        ]</field>
    </record>
</odoo>
```

**`security/ir.model.access.csv`**:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_{model_name}_user,{model_name}.user,model_{module_name}_{model_name},{module_name}.group_{module_name}_user,1,1,1,0
access_{model_name}_manager,{model_name}.manager,model_{module_name}_{model_name},{module_name}.group_{module_name}_manager,1,1,1,1
```

### Bước 6 — OWL 3.x Component (nếu cần)

```javascript
/** @odoo-module **/

import { Component, useState, useRef, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class {ComponentName} extends Component {
    static template = "{module_name}.{ComponentName}";
    static props = {
        recordId: { type: Number, optional: true },
        mode: { type: String, optional: true },
        onSelect: { type: Function, optional: true },
    };
    static defaultProps = { mode: "view" };

    setup() {
        // Services
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        // State — ALL hooks phải trong setup()
        this.state = useState({
            data: [],
            loading: true,
            error: null,
            selectedId: null,
        });

        this.containerRef = useRef("container");
        this._cleanup = null;

        onWillStart(async () => {
            await this.loadData();
        });

        onMounted(() => {
            this._setupEventListeners();
        });

        onWillUnmount(() => {
            this._cleanup?.();
        });
    }

    _setupEventListeners() {
        const handler = (e) => {
            if (e.key === "Escape") this.state.selectedId = null;
        };
        document.addEventListener("keydown", handler);
        this._cleanup = () => document.removeEventListener("keydown", handler);
    }

    async loadData() {
        this.state.loading = true;
        try {
            this.state.data = await this.orm.searchRead(
                "{module_name}.{model_name}",
                [],
                ["name", "state", "amount"],
                { limit: 100, order: "create_date DESC" }
            );
        } catch (error) {
            this.state.error = error.message;
            this.notification.add("Failed to load data", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    async onItemClick(item) {
        this.state.selectedId = item.id;
        if (this.props.onSelect) this.props.onSelect(item.id);
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "{module_name}.{model_name}",
            res_id: item.id,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("{module_name}.{component_name}", {ComponentName});
```

### Bước 7 — Cấu trúc thư mục chuẩn

```
{module_name}/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── {model_name}.py
├── views/
│   ├── {model_name}_views.xml
│   └── menuitems.xml
├── security/
│   ├── {module_name}_security.xml
│   └── ir.model.access.csv
├── data/
├── wizards/
├── controllers/
├── reports/
├── static/
│   ├── description/icon.png
│   └── src/
│       ├── js/
│       └── xml/
└── tests/
    ├── __init__.py
    └── test_{model_name}.py
```

### Bước 8 — v19 Checklist

```
□ from __future__ import annotations ở đầu mỗi file .py
□ Type hints trên TẤT CẢ method parameters và return types
□ SQL() builder cho TẤT CẢ raw SQL
□ _check_company_auto = True trên multi-company models
□ check_company=True trên relational fields
□ @api.model_create_multi cho create()
□ Command class cho x2many operations
□ invisible=/readonly=/required= (không dùng attrs=)
□ <list> không phải <tree>
□ allowed_company_ids trong record rules
□ OWL 3.x — hooks trong setup()
□ view_mode='list,form' (không phải 'tree,form')
```

## Constraints
- **PHẢI** xác nhận tên module và model trước khi generate
- **KHÔNG** dùng deprecated API: `name_get()`, `read_group()`, `attrs=`, `<tree>`
- **PHẢI** generate cả security file và ACL
- **KHÔNG** bỏ qua type hints

## Best practices
- Luôn kèm `__init__.py` cho mỗi thư mục Python
- Thứ tự data trong manifest: security.xml → ir.model.access.csv → data → views → menus
- Stored computed fields cho values thường đọc
- `tracking=True` trên fields quan trọng để có chatter history
