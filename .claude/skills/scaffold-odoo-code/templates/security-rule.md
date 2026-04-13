# Template: security-rule
# Dùng khi: [ADD] security/security.xml — thêm ir.rule record

## Pattern 1: Multi-company rule (global — áp dụng tất cả user)
```xml
<record id="rule_{model_snake}_company" model="ir.rule">
    <field name="name">{Model}: Multi-Company</field>
    <field name="model_id" ref="model_{model_underscore}"/>
    <field name="domain_force">
        ['|', ('company_id','=',False), ('company_id','in',company_ids)]
    </field>
    <field name="global" eval="True"/>
</record>
```

## Pattern 2: Warehouse restriction (chỉ áp dụng 1 group)
```xml
<record id="rule_{model_snake}_warehouse" model="ir.rule">
    <field name="name">{Model}: Warehouse Access</field>
    <field name="model_id" ref="model_{model_underscore}"/>
    <field name="domain_force">
        [('warehouse_id','in',user.warehouse_ids.ids or [0])]
    </field>
    <field name="groups" eval="[(4, ref('scx_inventory.group_warehouse_staff'))]"/>
    <field name="perm_read"   eval="True"/>
    <field name="perm_write"  eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

## Pattern 3: Owner rule (chỉ xem record của mình)
```xml
<record id="rule_{model_snake}_own" model="ir.rule">
    <field name="name">{Model}: Own Records Only</field>
    <field name="model_id" ref="model_{model_underscore}"/>
    <field name="domain_force">[('requested_by','=',user.id)]</field>
    <field name="groups" eval="[(4, ref('scx_inventory.group_warehouse_staff'))]"/>
</record>
```

## Lưu ý tên model_id ref
- `stock.picking`         → `model_stock_picking`
- `stock.inventory`       → `model_stock_inventory`
- `my.custom.model`       → `model_my_custom_model` (replace dot → underscore)
