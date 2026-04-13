# Template: security-group
# Dùng khi: [ADD] security/security.xml — thêm res.groups record

## Odoo 19 pattern (dùng privilege_id, KHÔNG dùng category_id)

```xml
<!-- Group: NV kho thường (tạo phiếu, không validate) -->
<record id="group_warehouse_staff" model="res.groups">
    <field name="name">Warehouse Staff</field>
    <field name="privilege_id" ref="stock.res_groups_privilege_inventory"/>
    <field name="implied_ids" eval="[(4, ref('stock.group_stock_user'))]"/>
    <field name="comment">Nhân viên kho — tạo phiếu xuất/nhập, không Validate</field>
</record>

<!-- Group: Thủ kho (full quyền kho được phân công) -->
<record id="group_warehouse_manager" model="res.groups">
    <field name="name">Warehouse Manager</field>
    <field name="privilege_id" ref="stock.res_groups_privilege_inventory"/>
    <field name="implied_ids" eval="[(4, ref('group_warehouse_staff'))]"/>
    <field name="comment">Thủ kho — Validate, Adjust, full quyền kho phân công</field>
</record>
```

## Hierarchy implied_ids thường gặp

| Group mới       | implied từ                            |
|-----------------|---------------------------------------|
| NV kho thường   | `stock.group_stock_user`             |
| Thủ kho         | group NV kho thường (cascade)        |
| QC User         | `stock.group_stock_user`             |
| Kế toán kho     | `base.group_user`                    |
| Ban lãnh đạo    | group Thủ kho (hoặc không implied)   |

## privilege_id references phổ biến
- `stock.res_groups_privilege_inventory`  — cho group thuộc Inventory
- `base.res_groups_privilege_user`        — cho group thuộc Settings/Users
- `hr.res_groups_privilege_hr`            — cho group thuộc HR
