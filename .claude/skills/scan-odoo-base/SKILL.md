---
name: scan-odoo-base
description: Quét động source code Odoo base (addons/stock, hr, base, approvals...) để kiểm tra model/field/group/rule đã có sẵn — tránh reimplementing trong custom module. Bổ trợ cho brd-to-dev-tasks Bước 2. Kích hoạt khi user nói "odoo base có gì", "kiểm tra field trong base", "stock module có field X không", "base đã có group Y chưa", "scan odoo base".
---

# Scan Odoo Base

## Goal
Quét **source thực tế** của Odoo base modules → trả lời chính xác:
- Model X có field Y không? (thay vì đoán theo tài liệu tĩnh)
- Module Z định nghĩa groups/rules nào?
- Nên `_inherit` + thêm gì, hay tạo mới hoàn toàn?

## When to use this skill
- "odoo base có gì", "kiểm tra field trong base", "scan odoo base"
- "stock module có field X không", "base đã có group Y chưa"
- Trước khi viết task `[ADD]` / `[MODIFY]` trong `brd-to-dev-tasks`
- Khi `odoo-base-coverage.md` (tài liệu tĩnh) không đủ chi tiết

## Instructions

### Bước 1 — Xác định module cần scan

Lấy tên module từ argument. Một lần scan có thể nhận nhiều module:
```
scan-odoo-base: stock, hr, base
```

Các addon paths được kiểm tra theo thứ tự:
```
1. /Users/khanhnm/Desktop/odoo-19.0/addons/<module>/
2. /Users/khanhnm/Desktop/odoo-19.0/odoo/addons/<module>/
3. /Users/khanhnm/Desktop/odoo-19.0/addons-oca1/<module>/
```

### Bước 2 — Chạy scan script

```bash
python3 - << 'PYEOF'
# paste toàn bộ scripts/base_scanner.py, thay BASE_MODULES
PYEOF
```

Copy boilerplate từ `scripts/base_scanner.py`, thay `BASE_MODULES`.

### Bước 3 — Trả lời query (nếu có)

Nếu user hỏi câu cụ thể (e.g. "res.users có warehouse_ids không?"), scan xong trả lời trực tiếp:

```
✅ FOUND   | res.users.warehouse_ids   | Many2many | stock/models/res_users.py:L42
❌ NOT FOUND | res.users.allowed_warehouse_ids | – | (không tồn tại trong base)
```

### Bước 4 — Trình bày Base Coverage Report

```
📦 BASE MODULE: stock  (addons/stock)
   Models scan: XX models

🔐 SECURITY GROUPS  (stock/security/stock_security.xml)
   stock.group_stock_user       — Stock / User
   stock.group_stock_manager    — Stock / Administrator
   stock.group_adv_location     — Stock / Multi-Step Routes
   stock.group_lot_on_delivery  — Stock / Lots & Serial Numbers

🗃️  MODEL COVERAGE
   res.users (_inherit)
     warehouse_ids       : ❌ (không có trong stock, chỉ có trong stock_location)
     property_warehouse_id: ❌
   stock.picking (_name)
     responsible_id      : ✅ Many2one (res.users)  [stock_picking.py:L89]
     company_id          : ✅ Many2one (res.company)
   stock.warehouse (_name)
     lot_stock_id        : ✅ Many2one (stock.location)
     ...

📋 FIELD QUERY RESULTS  (nếu user hỏi cụ thể)
   Q: res.users.warehouse_ids ?
   A: ❌ Không có trong base stock/hr/base — cần ADD vào custom module
```

### Bước 5 — Kết luận cho brd-to-dev-tasks

Sau report, in mapping trực tiếp dùng được:

```
## KẾT LUẬN CHO brd-to-dev-tasks

ĐÃ CÓ TRONG BASE (→ chỉ [MODIFY] nếu cần thêm field):
  stock.picking.responsible_id    ✅ → BRD §3.3/R1: "phải có người phụ trách" — ĐÃ CÓ
  stock.picking.company_id        ✅ → multi-company tự động

KHÔNG CÓ TRONG BASE (→ [ADD] hoặc [MODIFY] class rỗng):
  res.users.warehouse_ids         ❌ → BRD §3.1/F9: cần thêm vào models/res_users.py
  stock.inventory.approval.*      ❌ → BRD §2.1/B5: cần tạo model mới

DÙNG BASE GROUP TRỰC TIẾP (không cần tạo group mới):
  stock.group_stock_user          ✅ → dùng cho role "NV kho thường"
  stock.group_stock_manager       ✅ → dùng cho role "Thủ kho"
```

## Constraints
- **KHÔNG** sửa bất kỳ file Odoo base nào — chỉ đọc
- **KHÔNG** scan `__pycache__` hay `.pyc`
- Nếu module không tìm thấy trong cả 3 addon paths → báo rõ, không đoán
- Với query field cụ thể: grep kết quả phải có file path + line number thực tế
- Dùng heredoc `python3 - << 'PYEOF'` để tránh lỗi path có khoảng trắng

## Best practices
- Scan `stock` + `hr` + `base` làm bộ mặc định cho dự án SPS (cover ~80% yêu cầu INV)
- Khi BRD có approval workflow → scan thêm `approvals` và `mail`
- Field kết quả `✅` nhưng có `_inherit` → kiểm tra xem field đó ở base model hay ở inherited model nào
- Chạy một lần per session rồi cache kết quả — Odoo base không đổi trong development
- Kết hợp luôn: `scan-odoo-module` (custom) + `scan-odoo-base` (base) → đưa cả 2 vào `brd-to-dev-tasks` Bước 0+2
