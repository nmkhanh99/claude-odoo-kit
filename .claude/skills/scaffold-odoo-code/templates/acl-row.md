# Template: acl-row
# Dùng khi: [MODIFY] security/ir.model.access.csv — thêm ACL row

## Format CSV

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
```

## Pattern: Ma trận phân quyền điển hình

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_{model_snake}_stock_user,{model.name}.stock.user,model_{model_underscore},stock.group_stock_user,1,0,0,0
access_{model_snake}_warehouse_staff,{model.name}.warehouse.staff,model_{model_underscore},scx_inventory.group_warehouse_staff,1,1,1,0
access_{model_snake}_warehouse_manager,{model.name}.warehouse.manager,model_{model_underscore},scx_inventory.group_warehouse_manager,1,1,1,1
access_{model_snake}_manager,{model.name}.manager,model_{model_underscore},stock.group_stock_manager,1,1,1,1
```

## Giải thích cột perm

| Cột | Ý nghĩa | Odoo action |
|-----|---------|-------------|
| perm_read | Xem danh sách, mở form | `1` = được |
| perm_write | Sửa record | `1` = được |
| perm_create | Tạo record mới | `1` = được |
| perm_unlink | Xóa record | `1` = được |

## Quy tắc đặt tên model_id ref

- `stock.picking`         → `model_stock_picking`
- `my.custom.model`       → `model_my_custom_model`
- Công thức: `model_` + tên model thay `.` → `_`

## Ví dụ cho INV module

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_stock_disposal_proposal_user,stock.disposal.proposal.user,model_stock_disposal_proposal,stock.group_stock_user,1,0,0,0
access_stock_disposal_proposal_staff,stock.disposal.proposal.staff,model_stock_disposal_proposal,scx_inventory.group_warehouse_staff,1,1,1,0
access_stock_disposal_proposal_manager,stock.disposal.proposal.manager,model_stock_disposal_proposal,scx_inventory.group_warehouse_manager,1,1,1,1
```

## Lưu ý

- Dòng header `id,name,...` chỉ cần 1 lần ở đầu file
- Nếu file đã có header, chỉ paste các data rows
- Mỗi group từ BRD §2.6 cần 1 row riêng
- `id` phải unique trong toàn module — dùng prefix `access_` + model + group
