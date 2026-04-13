# Template: data-sequence
# Dùng khi: [ADD] data/ir_sequence_data.xml — tạo sequence mới

## Pattern chuẩn

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="1">
    <record id="seq_{model_snake}" model="ir.sequence">
        <field name="name">{Model Description} Reference</field>
        <field name="code">{model.name}</field>
        <field name="prefix">{PREFIX}/%(year)s/</field>
        <field name="padding">5</field>
        <field name="company_id" eval="False"/>
    </record>
</odoo>
```

## Ví dụ thực tế

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="1">
    <!-- Sequence cho Phiếu xuất kho nội bộ -->
    <record id="seq_stock_disposal_proposal" model="ir.sequence">
        <field name="name">Disposal Proposal Reference</field>
        <field name="code">stock.disposal.proposal</field>
        <field name="prefix">DSP/%(year)s/</field>
        <field name="padding">5</field>
        <field name="company_id" eval="False"/>
    </record>
</odoo>
```

## Prefix patterns phổ biến

| Loại phiếu       | Prefix gợi ý         |
|------------------|----------------------|
| Xuất kho nội bộ  | `DSP/%(year)s/`      |
| Nhập kho         | `RCP/%(year)s/`      |
| Phiếu duyệt      | `APR/%(year)s/`      |
| Kiểm kê          | `INV/%(year)s/`      |
| Đề nghị xuất     | `SOQ/%(year)s/`      |

## Lưu ý

- `noupdate="1"` là bắt buộc — không bị xóa khi update module
- `company_id eval="False"` — sequence dùng cho tất cả company (multi-company)
- `code` phải khớp chính xác với `self.env['ir.sequence'].next_by_code('...')` trong model
- File đặt trong `data/` (không phải `demo/`)
- Thêm vào `__manifest__.py` trong `data` list, TRƯỚC views
