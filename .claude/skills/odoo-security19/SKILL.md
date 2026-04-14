---
name: odoo-security19
description: Thiết lập security Odoo 19 đúng chuẩn — groups, ACL, record rules, multi-company, field visibility, SQL injection prevention. Kích hoạt khi user nói "thiết lập security", "tạo groups", "access rights", "record rules", "multi-company security", "phân quyền", "ir.model.access".
---

# Odoo Security Guide (v19)

## Goal
Tạo security đầy đủ cho module Odoo 19 — security groups, ACL, record rules, multi-company, view security — đúng chuẩn v19.

**Input**: Tên model, yêu cầu phân quyền  
**Output**: security.xml, ir.model.access.csv, model security patterns

## When to use this skill
- "tạo security groups", "tạo phân quyền"
- "tạo record rules multi-company"
- "field visibility theo group"
- "SQL injection prevention"
- Review security module trước deploy

## Instructions

### Bước 1 — Security Groups (security.xml)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Module Category -->
    <record id="module_category_my_module" model="ir.module.category">
        <field name="name">My Module</field>
        <field name="sequence">100</field>
    </record>

    <!-- User Group -->
    <record id="group_my_module_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_my_module"/>
        <!-- Implied từ base user (tùy chọn) -->
        <!-- <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/> -->
    </record>

    <!-- Manager Group — inherits User -->
    <record id="group_my_module_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_my_module"/>
        <field name="implied_ids" eval="[(4, ref('group_my_module_user'))]"/>
    </record>

    <!-- Multi-Company Record Rule (v18+: dùng allowed_company_ids) -->
    <record id="rule_my_model_company" model="ir.rule">
        <field name="name">My Model: Multi-Company</field>
        <field name="model_id" ref="model_my_module_my_model"/>
        <field name="global" eval="True"/>
        <field name="domain_force">[
            '|',
            ('company_id', '=', False),
            ('company_id', 'in', allowed_company_ids)
        ]</field>
    </record>

    <!-- Own Records Rule (tùy chọn) -->
    <record id="rule_my_model_own" model="ir.rule">
        <field name="name">My Model: Own Records</field>
        <field name="model_id" ref="model_my_module_my_model"/>
        <field name="groups" eval="[(4, ref('group_my_module_user'))]"/>
        <field name="domain_force">[
            ('user_id', '=', user.id)
        ]</field>
        <field name="perm_read" eval="True"/>
        <field name="perm_write" eval="True"/>
        <field name="perm_create" eval="True"/>
        <field name="perm_unlink" eval="False"/>
    </record>
</odoo>
```

### Bước 2 — Access Rights (ir.model.access.csv)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_module_my_model,my_module.group_my_module_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_module_my_model,my_module.group_my_module_manager,1,1,1,1
access_my_model_line_user,my.model.line.user,model_my_module_my_model_line,my_module.group_my_module_user,1,1,1,0
access_my_model_line_manager,my.model.line.manager,model_my_module_my_model_line,my_module.group_my_module_manager,1,1,1,1
```

**Quy tắc đặt `model_id`**: `model_` + tên model thay `.` bằng `_`
- `my.module.my.model` → `model_my_module_my_model`

### Bước 3 — Model Security Patterns (v19)

```python
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import SQL


class SecureModel(models.Model):
    _name = 'my.module.my.model'
    _description = 'Secure Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True    # v18+: bắt buộc cho multi-company

    # v19: type annotations trên tất cả fields
    name: str = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        index='btree',
    )
    active: bool = fields.Boolean(default=True)
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
        check_company=True,    # v18+: validate partner thuộc đúng company
        index=True,
    )
    user_id: int = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
        check_company=True,
    )
    # Field nhạy cảm — chỉ manager mới thấy
    internal_notes: str = fields.Text(
        string='Internal Notes',
        groups='my_module.group_my_module_manager',
    )
    state: str = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
        ],
        string='Status',
        default='draft',
        tracking=True,
        copy=False,
        index=True,
    )

    # v19: type hints bắt buộc trên mọi method
    @api.model_create_multi
    def create(self, vals_list: list[dict[str, Any]]) -> 'SecureModel':
        return super().create(vals_list)

    def write(self, vals: dict[str, Any]) -> bool:
        return super().write(vals)

    def action_sensitive_operation(self) -> None:
        """Method cần kiểm tra quyền thủ công."""
        # Kiểm tra group
        if not self.env.user.has_group('my_module.group_my_module_manager'):
            raise AccessError(_("Only managers can perform this action."))
        # Kiểm tra access rights
        self.check_access_rights('write')
        self.check_access_rule('write')
        self._execute_sensitive_operation()

    def _execute_sensitive_operation(self) -> None:
        """Internal method."""
        pass
```

### Bước 4 — SQL Security (v19 — SQL() bắt buộc)

```python
from odoo.tools import SQL

# ❌ SAI — SQL injection risk
# self.env.cr.execute(f"SELECT * FROM {self._table} WHERE name = '{name}'")
# self.env.cr.execute("SELECT * FROM " + table)

# ✅ ĐÚNG — SQL() builder ngăn injection
def _get_secure_data(self) -> list[dict[str, Any]]:
    """v19: SQL() builder là bắt buộc."""
    query = SQL(
        """
        SELECT id, name, amount
        FROM %(table)s
        WHERE company_id = %(company_id)s
          AND active = %(active)s
          AND create_uid = %(user_id)s
        ORDER BY %(order)s
        """,
        table=SQL.identifier(self._table),
        company_id=self.env.company.id,
        active=True,
        user_id=self.env.user.id,
        order=SQL.identifier('create_date') + SQL(' DESC'),
    )
    self.env.cr.execute(query)
    return self.env.cr.dictfetchall()

def _execute_complex_query(self) -> list[dict[str, Any]]:
    """Complex query với JOIN."""
    query = SQL(
        """
        SELECT
            m.id,
            m.name,
            p.name AS partner_name,
            COALESCE(SUM(l.amount), 0) AS total_amount
        FROM %(main_table)s m
        LEFT JOIN %(partner_table)s p ON m.partner_id = p.id
        LEFT JOIN %(line_table)s l ON l.parent_id = m.id
        WHERE m.company_id IN %(company_ids)s
          AND m.state = %(state)s
        GROUP BY m.id, m.name, p.name
        HAVING COALESCE(SUM(l.amount), 0) > %(min_amount)s
        """,
        main_table=SQL.identifier(self._table),
        partner_table=SQL.identifier('res_partner'),
        line_table=SQL.identifier('my_module_my_model_line'),
        company_ids=tuple(self.env.companies.ids),
        state='confirmed',
        min_amount=0,
    )
    self.env.cr.execute(query)
    return self.env.cr.dictfetchall()
```

### Bước 5 — View Security (v17+ syntax)

```xml
<form>
    <sheet>
        <group>
            <field name="name"/>

            <!-- v17+: Direct invisible expression -->
            <field name="internal_notes"
                   invisible="not user_has_groups('my_module.group_my_module_manager')"/>

            <!-- Kết hợp state và group -->
            <field name="secret_field"
                   invisible="state == 'draft' or not user_has_groups('my_module.group_my_module_manager')"/>

            <!-- Readonly dựa trên state -->
            <field name="amount"
                   readonly="state != 'draft'"
                   required="state == 'confirmed'"/>
        </group>
    </sheet>
</form>

<!-- Button với group restriction -->
<button name="action_approve"
        string="Approve"
        type="object"
        groups="my_module.group_my_module_manager"
        invisible="state != 'pending'"
        class="btn-primary"/>

<!-- Button không cần group nhưng dùng invisible -->
<button name="action_admin"
        string="Admin Action"
        type="object"
        invisible="not user_has_groups('base.group_system')"/>
```

### Bước 6 — Audit Log Pattern

```python
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from typing import Any
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AuditLog(models.Model):
    _name = 'my.module.audit.log'
    _description = 'Audit Log'
    _order = 'create_date desc'

    model: str = fields.Char(required=True, index=True)
    res_id: int = fields.Integer(required=True, index=True)
    action: str = fields.Selection([
        ('create', 'Created'),
        ('write', 'Updated'),
        ('unlink', 'Deleted'),
        ('access', 'Accessed'),
        ('export', 'Exported'),
    ], required=True, index=True)
    user_id: int = fields.Many2one('res.users', required=True, index=True)
    timestamp: fields.Datetime = fields.Datetime(
        default=fields.Datetime.now,
        required=True,
        index=True,
    )
    old_values: str = fields.Text()
    new_values: str = fields.Text()

    @api.model_create_multi
    def create(self, vals_list: list[dict[str, Any]]) -> 'AuditLog':
        return super().create(vals_list)

    def write(self, vals: dict[str, Any]) -> bool:
        raise UserError(_("Audit logs cannot be modified."))

    def unlink(self) -> bool:
        raise UserError(_("Audit logs cannot be deleted."))
```

### Bước 7 — Security Checklist (v19)

```
□ TẤT CẢ models có ir.model.access.csv entries
□ _check_company_auto = True cho multi-company models
□ check_company=True trên relational fields (partner_id, user_id...)
□ allowed_company_ids trong record rules (không phải company_ids)
□ Type annotations trên tất cả fields
□ Type annotations trên tất cả method signatures
□ SQL() builder cho tất cả raw SQL — KHÔNG dùng string SQL
□ Views dùng invisible= (không phải attrs=)
□ KHÔNG dùng sudo() bừa bãi
□ KHÔNG hardcode IDs (luôn dùng ref())
□ Field nhạy cảm có groups= attribute
```

## Constraints
- **KHÔNG** dùng raw string SQL — luôn dùng `SQL()` builder
- **KHÔNG** bỏ qua ACL cho model mới
- **KHÔNG** dùng `company_ids` trong record rules (v18+: `allowed_company_ids`)
- Luôn test với `sudo()` để xác nhận là security issue khi có AccessError

## Best practices
- Thứ tự phân quyền: Users (read/write/create) → Managers (+ unlink)
- Record rules nên có domain rõ ràng, tránh quá phức tạp
- Kiểm tra `has_group()` trước khi thực hiện sensitive operations
- Audit log là immutable — không cho phép write/unlink
- Dùng `check_access_rights()` + `check_access_rule()` khi cần kiểm tra thủ công
