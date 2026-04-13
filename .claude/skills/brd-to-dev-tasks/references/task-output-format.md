# Task Output Format

## Format chuẩn mỗi task

```
[TYPE] <relative_file_path> — <mô tả ngắn gọn>
  BRD ref: §X.X | Nguồn: <tên yêu cầu cụ thể>
  Chi tiết: <1-2 câu mô tả kỹ thuật>
```

### TYPE values
- `[ADD]`    — tạo mới file hoặc record chưa có
- `[MODIFY]` — file đã tồn tại, cần thêm/sửa
- `[CONFIG]` — không cần code, thực hiện trên Odoo UI

## Template bảng tổng hợp (với Seq + Depends + Priority)

```markdown
## Layer 1 — Security & Access Rights  🔴 (phải xong trước mọi thứ)
| Seq | Type     | File                          | Mô tả                                              | BRD ref | Priority | Depends |
|-----|----------|-------------------------------|----------------------------------------------------|---------|----------|---------|
|  1  | [ADD]    | security/security.xml         | Group `group_warehouse_staff` (NV kho)             | §2.6    | 🔴       | –       |
|  2  | [MODIFY] | security/security.xml         | Group `group_board_member`: thêm implied NV kho    | §2.6    | 🟡       | Seq 1   |
|  3  | [MODIFY] | security/ir.model.access.csv  | Access stock.picking, stock.move cho group NV kho  | §2.6    | 🔴       | Seq 1   |
|  4  | [ADD]    | security/security.xml         | ir.rule: stock.picking theo warehouse_id           | §3.3/R2 | 🔴       | Seq 1   |

## Layer 2 — Models
| Seq | Type     | File                               | Mô tả                                           | BRD ref | Priority | Depends |
|-----|----------|------------------------------------|--------------------------------------------------|---------|----------|---------|
|  5  | [MODIFY] | models/res_users.py                | Thêm `warehouse_ids` Many2many (stock.warehouse)| §3.1/F9 | 🔴       | Seq 1   |
|  6  | [ADD]    | models/stock_inventory_approval.py | Model + state machine approval 4 cấp            | §2.1/B5 | 🟡       | –       |

## Layer 3 — Data
| Seq | Type  | File                      | Mô tả                              | BRD ref | Priority | Depends |
|-----|-------|---------------------------|------------------------------------|---------|----------|---------|
|  7  | [ADD] | data/res_groups_data.xml  | Seed groups: Thủ kho, NV kho, QC  | §2.6    | 🔴       | Seq 1   |

## Layer 4 — Views
| Seq | Type  | File                                     | Mô tả                                                  | BRD ref | Priority | Depends |
|-----|-------|------------------------------------------|--------------------------------------------------------|---------|----------|---------|
|  8  | [ADD] | views/res_users_views.xml                | Tab "Kho phân công" (warehouse_ids many2many_tags)     | §2.3    | 🟡       | Seq 5   |
|  9  | [ADD] | views/stock_inventory_approval_views.xml | Form + list view approval request                      | §2.2.2  | 🟡       | Seq 6   |

## Layer 5 — Menus
| Seq | Type  | File         | Mô tả                            | BRD ref | Priority | Depends |
|-----|-------|--------------|----------------------------------|---------|----------|---------|
| 10  | [ADD] | views/menu.xml | Menu "Phê duyệt điều chỉnh tồn" | §2.5    | 🟡       | Seq 9   |

## Layer 6 — Config (không cần code)
| Seq | Hướng dẫn UI                                          | BRD ref | Priority |
|-----|-------------------------------------------------------|---------|----------|
| 11  | Employees > Work Locations: tạo "Tiên Sơn", "Đại Đồng" | §3.1/F4 | 🟢      |
| 12  | Settings > Inventory: bật Multi-Warehouses            | §2.5    | 🟢       |
```

## Priority labels

- 🔴 **Blocking** — không có thì module không load / nghiệp vụ không chạy được
- 🟡 **Important** — cần cho nghiệp vụ core, thiếu thì tính năng không đủ
- 🟢 **Nice to have** — UX, config, enhancement, có thể làm sau

## Sequencing rules

| Layer | Nội dung              | Lý do phải làm trước                            |
|-------|-----------------------|-------------------------------------------------|
| 1     | Security / Groups / Rules / ACL | Odoo load module cần ACL; ir.rule cần group |
| 2     | Models                | View cần model tồn tại; ACL reference model    |
| 3     | Data                  | Seed data cần model + group đã có              |
| 4     | Views (form/list)     | Cần model + field đã có                        |
| 5     | Menus                 | Cần action (từ view) đã có                     |
| 6     | Config                | Không phụ thuộc code, làm sau cùng             |

## Tóm tắt handoff

```
## TỔNG KẾT
  Tổng tasks : 12  (ADD: 7 | MODIFY: 3 | CONFIG: 2)
  Blocking 🔴: 6 tasks
  Thứ tự    : Security (4) → Models (2) → Data (1) → Views (2) → Menus (1) → Config (2)

## BƯỚC TIẾP THEO
  → Implement theo Seq 1 → 12
  → Sau khi code xong: chạy scan-odoo-module lại (EMPTY phải = 0)
  → Dùng verify-impl-vs-brd để đối chiếu code với BRD
```
