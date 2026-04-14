---
name: odoo-uom
description: Unit of Measure (UoM) Odoo 19 — tạo danh mục và đơn vị đo, chuyển đổi số lượng/giá, UoM trên sản phẩm, stock moves, float_compare/float_round, view pattern với groups="uom.group_uom". Kích hoạt khi user nói "đơn vị đo", "UoM", "unit of measure", "chuyển đổi đơn vị", "_compute_quantity", "float_compare".
---

# Unit of Measure (UoM) Patterns (Odoo 19)

## Goal
Implement UoM đúng chuẩn Odoo 19 — tạo category/unit, chuyển đổi số lượng và giá, tích hợp vào model tùy chỉnh, view pattern ẩn/hiện theo group.

**Input**: Mô tả nhu cầu UoM, model target  
**Output**: Python + XML + Data file đầy đủ

## When to use this skill
- "thêm UoM vào model", "chuyển đổi đơn vị đo"
- "tạo danh mục UoM tùy chỉnh"
- "tính giá theo UoM mua/bán"
- "stock move với UoM khác nhau"
- "float_compare precision"

## Instructions

### Bước 1 — UoM Category và cấu trúc

```
UoM Category: Weight (Khối lượng)
├── kg (reference unit, factor = 1.0)
├── g  (factor = 0.001)
├── lb (factor = 0.453592)
└── oz (factor = 0.0283495)

UoM Category: Unit (Cái/Chiếc)
├── Unit(s) (reference)
├── Dozen (factor = 12)
└── Hundred (factor = 100)
```

### Bước 2 — Tạo UoM Category và Unit

```python
# -*- coding: utf-8 -*-
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError

# Tạo category (ví dụ: Volume)
category = self.env['uom.category'].create({'name': 'Volume'})

# Reference unit (factor = 1)
liter = self.env['uom.uom'].create({
    'name': 'Liter',
    'category_id': category.id,
    'uom_type': 'reference',   # Đơn vị cơ sở
    'rounding': 0.001,
})

# Smaller unit — factor_inv: bao nhiêu ml = 1 L
milliliter = self.env['uom.uom'].create({
    'name': 'Milliliter',
    'category_id': category.id,
    'uom_type': 'smaller',
    'factor_inv': 1000,        # 1000 ml = 1 L
    'rounding': 1,
})

# Bigger unit — factor: 1 gallon = bao nhiêu L
gallon = self.env['uom.uom'].create({
    'name': 'Gallon',
    'category_id': category.id,
    'uom_type': 'bigger',
    'factor': 3.78541,         # 1 gallon = 3.78541 L
    'rounding': 0.01,
})
```

### Bước 3 — Chuyển đổi số lượng

```python
from odoo.exceptions import UserError

def convert_uom(
    self,
    qty: float,
    from_uom: 'uom.uom',
    to_uom: 'uom.uom',
) -> float:
    """Chuyển đổi số lượng giữa các UoM.
    
    Lưu ý: Chỉ chuyển được trong cùng category.
    """
    if from_uom.category_id != to_uom.category_id:
        raise UserError(
            "Cannot convert between different UoM categories."
        )
    return from_uom._compute_quantity(qty, to_uom)

# Ví dụ: 2 tá → đơn vị lẻ
from_uom = self.env.ref('uom.product_uom_dozen')
to_uom = self.env.ref('uom.product_uom_unit')
units = from_uom._compute_quantity(2, to_uom)  # = 24

# Với rounding method
units_rounded = from_uom._compute_quantity(
    2.5,
    to_uom,
    round=True,
    rounding_method='HALF-UP',  # Default
)

# Luôn làm tròn lên
units_up = from_uom._compute_quantity(
    10.3,
    to_uom,
    round=True,
    rounding_method='UP',
)
```

### Bước 4 — Chuyển đổi giá

```python
def convert_price(
    self,
    price: float,
    from_uom: 'uom.uom',
    to_uom: 'uom.uom',
) -> float:
    """Chuyển đổi đơn giá giữa các UoM."""
    return from_uom._compute_price(price, to_uom)

# Ví dụ: Sản phẩm giá $10/gallon → giá/liter?
price_per_liter = gallon._compute_price(10, liter)  # ≈ $2.64
```

### Bước 5 — Float comparison đúng chuẩn

```python
from odoo.tools import float_compare, float_round

# So sánh số lượng với precision của UoM
result = float_compare(
    qty1,
    qty2,
    precision_rounding=uom.rounding,
)
# Returns: -1 (nhỏ hơn), 0 (bằng nhau), 1 (lớn hơn)

# Làm tròn theo UoM precision
rounded_qty = float_round(qty, precision_rounding=uom.rounding)

# Pattern kiểm tra bằng nhau
if float_compare(qty, 0, precision_rounding=uom.rounding) == 0:
    # qty == 0
    pass

# KHÔNG dùng == trực tiếp cho float
# if qty == 0:  # SAI — lỗi floating point
```

### Bước 6 — Model tùy chỉnh với UoM

```python
class InventoryAdjustment(models.Model):
    _name = 'inventory.adjustment'
    _description = 'Inventory Adjustment'

    product_id: int = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    quantity: float = fields.Float(
        string='Quantity',
        digits='Product Unit of Measure',
    )
    product_uom_id: int = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    # Helper field để filter domain
    product_uom_category_id: int = fields.Many2one(
        related='product_id.uom_id.category_id',
        string='UoM Category',
    )
    # Số lượng quy đổi về UoM cơ sở của sản phẩm
    product_qty: float = fields.Float(
        string='Quantity (Base UoM)',
        compute='_compute_product_qty',
        store=True,
    )

    @api.depends('quantity', 'product_uom_id', 'product_id')
    def _compute_product_qty(self) -> None:
        for record in self:
            if record.product_uom_id and record.product_id:
                record.product_qty = record.product_uom_id._compute_quantity(
                    record.quantity,
                    record.product_id.uom_id,
                )
            else:
                record.product_qty = record.quantity

    @api.onchange('product_id')
    def _onchange_product_id(self) -> None:
        """Set UoM mặc định từ sản phẩm."""
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
```

### Bước 7 — UoM trên Sale/Purchase Order Line

```python
class SaleOrderLineExtend(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom')
    def _onchange_product_uom(self) -> None:
        """Tính lại giá khi đổi UoM."""
        if self.product_id and self.product_uom:
            base_price = self.product_id.lst_price
            self.price_unit = self.product_id.uom_id._compute_price(
                base_price, self.product_uom
            )
```

### Bước 8 — Stock Move với UoM

```python
def create_stock_move(
    self,
    product: 'product.product',
    qty: float,
    uom: 'uom.uom',
    location_src: 'stock.location',
    location_dest: 'stock.location',
) -> 'stock.move':
    """Tạo stock move với UoM chỉ định."""
    move = self.env['stock.move'].create({
        'name': product.name,
        'product_id': product.id,
        'product_uom_qty': qty,    # Số lượng theo UoM của move
        'product_uom': uom.id,
        'location_id': location_src.id,
        'location_dest_id': location_dest.id,
    })
    return move

def get_stock_in_uom(
    self,
    product: 'product.product',
    uom: 'uom.uom',
    location: 'stock.location | None' = None,
) -> float:
    """Lấy tồn kho quy đổi theo UoM chỉ định."""
    if location:
        qty = product.with_context(location=location.id).qty_available
    else:
        qty = product.qty_available
    return product.uom_id._compute_quantity(qty, uom)
```

### Bước 9 — View XML với UoM (v19 syntax)

```xml
<!-- Form view — dùng <list> không phải <tree> -->
<form>
    <group>
        <field name="product_id"/>
        <label for="quantity"/>
        <div class="o_row">
            <!-- quantity và UoM cùng hàng -->
            <field name="quantity" class="oe_inline"/>
            <field name="product_uom_id" class="oe_inline"
                   options="{'no_create': True}"
                   groups="uom.group_uom"/>
            <!-- groups="uom.group_uom" — ẩn khi chưa bật Multi-UoM -->
        </div>
        <field name="product_uom_category_id" invisible="1"/>
    </group>
</form>

<!-- List view — v19: dùng <list> không phải <tree> -->
<list>
    <field name="product_id"/>
    <field name="quantity"/>
    <!-- Ẩn nếu chưa bật tính năng Multi-UoM -->
    <field name="product_uom_id" groups="uom.group_uom"/>
    <field name="product_qty" string="Qty (Base)"/>
</list>
```

### Bước 10 — Data XML định nghĩa UoM

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="1">
    <!-- UoM Category -->
    <record id="uom_categ_length" model="uom.category">
        <field name="name">Length</field>
    </record>

    <!-- Reference unit -->
    <record id="uom_meter" model="uom.uom">
        <field name="name">Meter</field>
        <field name="category_id" ref="uom_categ_length"/>
        <field name="uom_type">reference</field>
        <field name="rounding">0.01</field>
    </record>

    <!-- Smaller unit: 1m = 100cm -->
    <record id="uom_centimeter" model="uom.uom">
        <field name="name">Centimeter</field>
        <field name="category_id" ref="uom_categ_length"/>
        <field name="uom_type">smaller</field>
        <field name="factor_inv">100</field>
        <field name="rounding">1</field>
    </record>

    <!-- Bigger unit: 1km = 1000m -->
    <record id="uom_kilometer" model="uom.uom">
        <field name="name">Kilometer</field>
        <field name="category_id" ref="uom_categ_length"/>
        <field name="uom_type">bigger</field>
        <field name="factor">1000</field>
        <field name="rounding">0.001</field>
    </record>
</odoo>
```

### Bước 11 — UoM chuẩn Odoo (external IDs)

```python
# Nhóm Unit (Cái)
unit   = self.env.ref('uom.product_uom_unit')
dozen  = self.env.ref('uom.product_uom_dozen')

# Nhóm Weight (Khối lượng)
kg     = self.env.ref('uom.product_uom_kgm')
gram   = self.env.ref('uom.product_uom_gram')
lb     = self.env.ref('uom.product_uom_lb')
oz     = self.env.ref('uom.product_uom_oz')

# Nhóm Time (Thời gian)
hour   = self.env.ref('uom.product_uom_hour')
day    = self.env.ref('uom.product_uom_day')

# Nhóm Volume (Thể tích — nếu đã cài)
litre  = self.env.ref('uom.product_uom_litre')
```

## Constraints
- **Chỉ** chuyển đổi trong cùng UoM category — khác category sẽ lỗi
- **PHẢI** dùng `float_compare` — không dùng `==` cho float
- `product_uom_category_id` là computed field — dùng làm domain filter, không store
- View UoM fields **phải** có `groups="uom.group_uom"` để ẩn khi chưa bật

## Best practices
- Set `rounding` phù hợp: kg → 0.001, cái → 1.0, giờ → 0.25
- Dùng `digits='Product Unit of Measure'` cho Float field quantity
- Khi tạo product: `uom_id` = đơn vị bán, `uom_po_id` = đơn vị mua
- Stock luôn tính theo UoM cơ sở của sản phẩm — convert khi cần hiển thị
- `noupdate="1"` trong data XML để không override khi upgrade module
