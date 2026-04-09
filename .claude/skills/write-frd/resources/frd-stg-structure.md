# FRD-STG Structure — Kiến trúc Module

## Mục đích
FRD-STG được viết **trước tất cả FRD khác**. Mô tả nền tảng kỹ thuật chung áp dụng cho toàn bộ module.

## File
`frds/FRD-NEW-MAN-STG-Kiến trúc module-01.md` (tách `-02`, `-03` nếu vượt 500 lines)

---

## Phần 1 — `__manifest__.py` & Dependencies

```python
{
    'name': 'Module Name',
    'version': '19.0.x.x.x',
    'category': 'Manufacturing',
    'license': 'LGPL-3',
    'author': 'SPS',
    'website': '',
    'depends': [
        # Odoo core
        'mrp', 'stock', 'hr',
        # Odoo Enterprise
        'mrp_workorder',
        # SCX internal
        'scx_setting',
    ],
    'data': [
        # Thứ tự load quan trọng
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/...',
    ],
}
```

**Quy trình xác nhận depends:**
1. Đọc `scx_addons/<module>/__manifest__.py` để lấy danh sách thực tế
2. Đọc BRD/PRD đã duyệt để xác định module cần thiết
3. Đề xuất danh sách kèm lý do → **Hỏi user phê duyệt**
4. Chỉ viết vào FRD sau khi được phê duyệt

---

## Phần 2 — Strategy Pattern Architecture

### Registry trung tâm: `strategy.rule.config`

| Field | Type | Mô tả |
|-------|------|-------|
| `company_id` | Many2one | Công ty áp dụng |
| `res_model` | Char | Tên model gốc (ví dụ: `mrp.production`) |
| `strategy_model` | Char | Tên AbstractModel chứa logic |
| `active` | Boolean | Bật/tắt |

### Cấu trúc 3 lớp cho mỗi domain:
```
<domain>.strategy.base        (AbstractModel — default no-op)
  └── <domain>.strategy.sps   (AbstractModel — logic SPS)
  └── <domain>.config.strategy.sps  (AbstractModel — config mở rộng)
```

### Cách gọi strategy từ model chính:
```python
def _get_strategy(self):
    self.ensure_one()
    rule = self.env['strategy.rule.config'].search([
        ('company_id', '=', self.company_id.id),
        ('res_model', '=', self._name),
        ('active', '=', True),
    ], limit=1)
    if rule and rule.strategy_model:
        return self.env[rule.strategy_model]
    return self.env['<domain>.strategy.base']
```

### Cấu trúc thư mục strategy:
```
models/strategy/
├── __init__.py
├── strategy_<domain>/
│   ├── __init__.py
│   ├── <domain>_strategy_base.py
│   ├── <domain>_strategy_sps.py
│   └── <domain>_config_strategy_sps.py
```

---

## Phần 3 — Internationalization (i18n)

- **Ngôn ngữ bắt buộc:** `en` (English), `vi` (Vietnamese)
- **Thư mục:** `i18n/vi.po`
- **Quy tắc trong code:**
  - Tất cả string hiển thị cho user dùng `_()`
  - `field string=` và `help=` viết bằng tiếng Anh
  - Menu, label, thông báo lỗi đều translatable

**Nhóm string cần dịch:** field labels, menu items, error messages, wizard labels, report headers

---

## Phần 4 — Data files & Master data

| File | XML ID | Nội dung | noupdate |
|------|--------|---------|---------|
| `data/sequence.xml` | `seq_xxx` | Sequence mã phiếu | 1 |
| `data/workcenter.xml` | `wc_xxx` | Workcenter mặc định | 0 |
