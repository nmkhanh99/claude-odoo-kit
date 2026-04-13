---
name: check-odoo19-compat
description: Quét module Odoo tìm deprecated API và pattern không tương thích Odoo 17+/19 — báo cáo ERROR/WARN với file:line và hướng dẫn fix. Kích hoạt khi user nói "check compat", "kiểm tra deprecated", "odoo 19 compat", "tìm api cũ", "scan deprecated", "upgrade check", "code cũ".
---

# Check Odoo 19 Compatibility

## Goal
Quét toàn bộ source code module → phát hiện **deprecated API, removed syntax, anti-pattern** so với Odoo 17+/19 → báo cáo từng vị trí cụ thể với severity + hướng dẫn fix.

Severity:
- `[ERROR]` — sẽ crash hoặc raise exception khi chạy trên Odoo 17+
- `[WARN]`  — deprecated warning, vẫn chạy được nhưng cần sửa trước khi upgrade tiếp
- `[INFO]`  — style issue, không ảnh hưởng runtime nhưng không đúng chuẩn mới

## When to use this skill
- "check compat", "kiểm tra deprecated", "odoo 19 compat", "tìm api cũ"
- "scan deprecated", "upgrade check", "code cũ", "migrate sang 17/19"
- Trước khi submit PR / deploy lên production
- Sau khi nhận module từ bên ngoài (OCA, vendor)

## Instructions

### Bước 1 — Xác định module path
Lấy từ argument hoặc hỏi user. Kiểm tra `__manifest__.py` tồn tại.

### Bước 2 — Chạy compatibility scanner

```bash
python3 - << 'PYEOF'
# paste toàn bộ nội dung scripts/compat_scanner.py, thay MODULE_PATH
PYEOF
```

Copy boilerplate từ `scripts/compat_scanner.py`, thay `MODULE_PATH`.

Script scan:
- `*.py` — Python deprecated patterns
- `*.xml` — XML deprecated syntax
- `*.csv` — không scan (không có deprecated patterns)

### Bước 3 — Hiển thị báo cáo

```
🔍 ODOO 19 COMPAT REPORT: <module_name>
   Scanned: X .py files | Y .xml files
   Found  : A errors | B warnings | C info

── ERRORS (sẽ crash) ────────────────────────────────────────────

[ERROR] models/stock_picking.py:42
  Pattern : def name_get(self):
  Problem : name_get() bị remove trong Odoo 17+
  Fix     : Dùng _rec_name = 'name' hoặc compute display_name

[ERROR] views/stock_views.xml:18
  Pattern : <tree string="...">
  Problem : <tree> tag không còn tồn tại trong Odoo 17+
  Fix     : Đổi thành <list string="...">

── WARNINGS (deprecated, vẫn chạy) ─────────────────────────────

[WARN] models/approval.py:67
  Pattern : @api.multi
  Problem : @api.multi bị remove từ Odoo 14
  Fix     : Bỏ decorator — Odoo tự hiểu recordset method

[WARN] views/form.xml:34
  Pattern : attrs="{'invisible': [('state', '=', 'draft')]}"
  Problem : attrs= deprecated từ Odoo 17
  Fix     : Dùng invisible="state == 'draft'"

── INFO (style) ─────────────────────────────────────────────────

[INFO] models/base.py:12
  Pattern : self._cr.execute(...)
  Problem : _cr shortcut deprecated — dùng self.env.cr
  Fix     : Đổi thành self.env.cr.execute(SQL(...))

── TÓM TẮT ──────────────────────────────────────────────────────

Files có vấn đề : X / Y tổng files
ERROR           : A issues  → PHẢI sửa trước khi chạy Odoo 17+
WARN            : B issues  → Nên sửa trước khi upgrade tiếp
INFO            : C issues  → Có thể defer

Top files nhiều lỗi nhất:
  1. models/stock_picking.py  — 5 issues
  2. views/stock_views.xml    — 3 issues
```

### Bước 4 — Tạo fix task list (tùy chọn)

Hỏi user: "Muốn tôi tạo fix task list không?"
- Nếu có → xuất bảng patch tasks theo format `brd-to-dev-tasks`, nhóm theo file
- Ưu tiên ERROR trước WARN

```
| Seq | File                      | Line | Fix cần làm                    | Severity |
|-----|---------------------------|------|--------------------------------|----------|
| 1   | views/stock_views.xml     | 18   | <tree> → <list>                | ERROR    |
| 2   | models/stock_picking.py   | 42   | name_get() → _rec_name         | ERROR    |
| 3   | models/approval.py        | 67   | bỏ @api.multi                  | WARN     |
```

## Constraints
- **CẤM** tự sửa code — chỉ báo cáo
- **KHÔNG** báo false positive cho import `from odoo import` (đây là đúng)
- **CẤM** pip install ngầm; dùng heredoc
- Nếu module path không tồn tại → báo lỗi rõ, dừng lại
- Scan toàn bộ files — **không skip** subfolder nào

## Best practices
- Sắp xếp theo severity: ERROR trước WARN trước INFO
- Trong cùng severity, sắp xếp theo file path (dễ fix theo file)
- Với `attrs=` trong XML: script regex đã đủ — không cần grep thêm
- Với `name_get` báo ERROR: nếu class đã có `_rec_name` hoặc `_compute_display_name` → là false positive, safe to ignore
- Chạy sau `scan-odoo-module` để có context module trước
- Refer `@references/compat-patterns.md` cho full danh sách patterns + fix guide
