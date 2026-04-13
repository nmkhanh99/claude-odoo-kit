---
name: scan-odoo-module
description: Quét hiện trạng module Odoo — trích xuất models/fields, security groups, record rules, access rights, views, menus, data files — phát hiện file rỗng/placeholder. Xuất báo cáo có cấu trúc để dùng làm input cho brd-to-dev-tasks. Kích hoạt khi user nói "xem hiện trạng module", "scan module", "module đang có gì", "kiểm tra code hiện tại", "hiện trạng code kho".
---

# Scan Odoo Module

## Goal
Quét toàn bộ module Odoo custom → xuất **Module State Report** có cấu trúc:
- Models & Fields (kèm flag: rỗng / đã có logic)
- Security Groups + Record Rules + Access Rights
- Views / Menus / Actions
- Data files
- Warnings: file rỗng, placeholder class, thiếu ACL

## When to use this skill
- "xem hiện trạng module", "scan module", "module đang có gì"
- "kiểm tra code hiện tại", "hiện trạng code kho"
- Trước khi chạy `brd-to-dev-tasks` để có dữ liệu "đã có"
- Khi muốn tìm file placeholder / class rỗng chưa implement

## Instructions

### Bước 1 — Xác định module path
Lấy từ argument hoặc hỏi user. Kiểm tra `__manifest__.py` tồn tại.

### Bước 2 — Chạy scan script

```bash
python3 - << 'PYEOF'
# paste toàn bộ nội dung scripts/scanner.py, thay MODULE_PATH
PYEOF
```

Copy boilerplate từ `scripts/scanner.py`, thay `MODULE_PATH`.

### Bước 3 — Trình bày Module State Report

In theo thứ tự:

```
📦 MODULE: <tên> v<version>
   Depends: [list]
   Data files: X files

🔐 SECURITY
   Groups    : X defined  → [tên group 1, tên group 2, ...]
   ir.rule   : X defined  → [tên rule + model]
   ACL rows  : X entries  → [model → group: r/w/c/d]

🗃️  MODELS
   <model_name> (_inherit / _name)  [EMPTY | OK | PARTIAL]
     Fields added : [field1 (type), field2 (type), ...]
     Methods      : [method1, method2, ...]
     Constraints  : [sql / api]

👁️  VIEWS
   <file.xml> → models: [x, y] | types: [form, list] | menus: N

📄 DATA FILES
   <file.xml/csv> → [sequences / cron / parameters]

⚠️  WARNINGS
   - models/res_users.py : class rỗng (_inherit only, no fields/methods)
   - security/security.xml : thiếu group cho role X (so với BRD §2.6)
   - ir.model.access.csv : model Y chưa có ACL entry
```

### Bước 4 — Tóm tắt cho brd-to-dev-tasks

Sau report, in bảng "Đã có / Chưa có" ngắn gọn:

```
## READY FOR brd-to-dev-tasks

ĐÃ CÓ (không cần tạo):
- Group: group_qc_user, group_scrap_manager, group_board_member
- Model: stock.disposal.proposal (đầy đủ)
- Rule: stock_disposal_proposal_company (multi-company)

PLACEHOLDER (có file nhưng chưa implement):
- models/res_users.py → chỉ có _inherit, chưa có field/method
- models/stock_picking.py → cần kiểm tra thêm

CHƯA CÓ (cần tạo mới):
- Group: group_warehouse_staff (NV kho thường) — BRD §2.6
- Rule: ir.rule giới hạn stock.picking theo warehouse_id
- Model: stock.inventory.approval (approval 4 cấp)
```

## Constraints
- **CẤM** tự sửa bất kỳ file nào — chỉ đọc và báo cáo
- **CẤM** pip install ngầm; dùng heredoc `python3 - << 'PYEOF'`
- Nếu path không tồn tại → báo lỗi rõ ràng, không đoán mò
- Phát hiện "class rỗng" = class chỉ có `_inherit`/`_name`, không có fields, methods, constraints

## Best practices
- Chạy scan trước `brd-to-dev-tasks` trong cùng session để tái sử dụng kết quả
- Highlight ⚠️ WARNINGS đặc biệt — đây thường là nơi dev nghĩ "đã làm" nhưng thực ra chưa
- Khi scan nhiều module: chạy từng module một, không gộp
- Với `_inherit` model: kiểm tra xem base model đã có field chưa trước khi đánh MISSING
