# Odoo 19 — Patterns bắt buộc & Anti-patterns cấm

## Anti-patterns CẤM (sẽ gây lỗi hoặc deprecated warning)

| Cấm | Thay bằng | Lý do |
|-----|-----------|-------|
| `<tree ...>` | `<list ...>` | Odoo 17+ đổi tên |
| `attrs="{'invisible': [...]}"` | `invisible="state == 'draft'"` | New domain syntax |
| `attrs="{'required': [...]}"` | `required="field != False"` | New domain syntax |
| `attrs="{'readonly': [...]}"` | `readonly="state == 'done'"` | New domain syntax |
| `def name_get(self):` | `_rec_name = 'name'` hoặc `display_name` compute | Deprecated Odoo 17+ |
| `category_id ref="..."` trên group | `privilege_id ref="..."` | Odoo 17+ group structure |
| `@api.multi` | Bỏ decorator | Deprecated |
| `self._cr.execute(...)` | `self.env.cr.execute(SQL(...))` | Security: SQL injection |
| `.read_group(...)` | `._read_group(...)` | New API Odoo 17+ |
| `context={'active_test': False}` như positional | dùng `with_context(active_test=False)` | |
| `fields.datetime.now()` | `fields.Datetime.now()` | Case sensitive |
| `self.env.ref('...')` trong default lambda | `lambda self: self.env.ref('...')` | Lazy eval |

## Patterns bắt buộc

### Model class
```python
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model Description'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    _rec_name = 'name'

    name = fields.Char(
        string=_('Reference'),
        default='New',
        copy=False,
        readonly=True,
        tracking=True,
    )
    state = fields.Selection([
        ('draft',     _('Draft')),
        ('confirmed', _('Confirmed')),
        ('done',      _('Done')),
        ('cancel',    _('Cancelled')),
    ], string=_('Status'), default='draft',
       required=True, tracking=True, index=True, copy=False)

    company_id = fields.Many2one(
        'res.company', string=_('Company'),
        default=lambda self: self.env.company,
        required=True, readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('my.model') or 'New'
        return super().create(vals_list)
```

### State machine buttons (form header)
```xml
<header>
    <button name="action_confirm" string="Confirm" type="object"
            class="oe_highlight"
            invisible="state != 'draft'"
            groups="stock.group_stock_user"/>
    <button name="action_cancel" string="Cancel" type="object"
            invisible="state not in ('draft', 'confirmed')"/>
    <field name="state" widget="statusbar"
           statusbar_visible="draft,confirmed,done"/>
</header>
```

### List view (KHÔNG dùng tree)
```xml
<list string="My Model"
      decoration-info="state == 'draft'"
      decoration-success="state == 'done'"
      decoration-muted="state == 'cancel'">
    <field name="name"/>
    <field name="state" widget="badge"
           decoration-info="state == 'draft'"
           decoration-success="state == 'done'"/>
    <field name="company_id" groups="base.group_multi_company"/>
</list>
```

### Invisible / readonly / required (Odoo 17+ syntax)
```xml
<!-- ✅ Đúng -->
<field name="lot_id" invisible="product_tracking == 'none'"/>
<field name="note"   readonly="state == 'done'"/>
<field name="qty"    required="state == 'confirmed'"/>

<!-- ❌ Sai (deprecated) -->
<field name="lot_id" attrs="{'invisible': [('product_tracking', '=', 'none')]}"/>
```

### Security group (Odoo 17+)
```xml
<record id="group_warehouse_staff" model="res.groups">
    <field name="name">Warehouse Staff</field>
    <field name="privilege_id" ref="stock.res_groups_privilege_inventory"/>
    <field name="implied_ids" eval="[(4, ref('stock.group_stock_user'))]"/>
    <field name="comment">NV kho thường — tạo phiếu, không validate</field>
</record>
```

### Record Rule (multi-company + warehouse)
```xml
<record id="rule_my_model_company" model="ir.rule">
    <field name="name">My Model: Multi-Company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">['|', ('company_id','=',False), ('company_id','in',company_ids)]</field>
    <field name="global" eval="True"/>
</record>

<record id="rule_my_model_warehouse" model="ir.rule">
    <field name="name">My Model: Warehouse Access</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('warehouse_id','in',user.warehouse_ids.ids or [0])]</field>
    <field name="groups" eval="[(4, ref('scx_inventory.group_warehouse_staff'))]"/>
</record>
```

### ACL CSV row format
```
access_my_model_stock_user,my.model.stock.user,model_my_model,stock.group_stock_user,1,1,1,0
access_my_model_warehouse_staff,my.model.warehouse.staff,model_my_model,scx_inventory.group_warehouse_staff,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,stock.group_stock_manager,1,1,1,1
```

### Sequence data file
```xml
<odoo noupdate="1">
    <record id="seq_my_model" model="ir.sequence">
        <field name="name">My Model Reference</field>
        <field name="code">my.model</field>
        <field name="prefix">MYM/%(year)s/</field>
        <field name="padding">5</field>
        <field name="company_id" eval="False"/>
    </record>
</odoo>
```

### Computed field with store
```python
@api.depends('line_ids.quantity')
def _compute_total_quantity(self):
    for rec in self:
        rec.total_quantity = sum(rec.line_ids.mapped('quantity'))

total_quantity = fields.Float(
    string=_('Total Qty'),
    compute='_compute_total_quantity',
    store=True,
)
```

### Many2many field
```python
warehouse_ids = fields.Many2many(
    'stock.warehouse',
    'my_model_warehouse_rel',   # relation table name — PHẢI unique
    'model_id', 'warehouse_id',
    string=_('Warehouses'),
)
```

## __manifest__.py — thứ tự data files
```python
'data': [
    # 1. Security first
    'security/security.xml',
    'security/ir.model.access.csv',
    # 2. Data (sequences, config)
    'data/ir_sequence_data.xml',
    # 3. Views
    'views/my_model_views.xml',
    'views/menu.xml',
    # 4. Wizard views
    'wizard/my_wizard_views.xml',
    # 5. Reports (last)
    'reports/my_report.xml',
],
```
