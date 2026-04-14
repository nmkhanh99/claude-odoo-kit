---
name: odoo-i18n
description: Đa ngôn ngữ và dịch thuật Odoo 19 — hàm _(), translate=True, file PO, with_context(lang=), gửi email theo ngôn ngữ partner, selection động có dịch. Kích hoạt khi user nói "đa ngôn ngữ", "dịch thuật", "translation", "i18n", "PO file", "ngôn ngữ", "locale", "_() function".
---

# Translation & i18n Patterns (Odoo 19)

## Goal
Implement đa ngôn ngữ đúng chuẩn cho module Odoo 19 — chuỗi dịch, field content, PO files, context lang, dynamic selection.

**Input**: Mô tả nhu cầu đa ngôn ngữ  
**Output**: Python + XML + PO file patterns đầy đủ

## When to use this skill
- "hỗ trợ đa ngôn ngữ", "dịch module"
- "tạo file PO", "export translations"
- "gửi email theo ngôn ngữ partner"
- "field có nội dung dịch theo ngôn ngữ"
- "selection label dịch được"

## Instructions

### Bước 1 — Chuỗi dịch trong Python

```python
# -*- coding: utf-8 -*-
from __future__ import annotations

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'  # Tự động dịch qua PO

    # Field label dịch tự động qua string=
    name: str = fields.Char(string='Name', required=True)

    # Help text cũng dịch được
    description: str = fields.Text(
        string='Description',
        help='Enter a detailed description',
    )

    # Selection labels dịch tự động
    state: str = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], string='Status', default='draft')

    def action_confirm(self) -> None:
        """Dùng _() cho mọi message user-facing."""
        for record in self:
            if not record.name:
                raise UserError(_("Name is required to confirm."))
            record.state = 'confirmed'
            record.message_post(body=_("Document confirmed."))
```

### Bước 2 — Patterns hàm _() đúng chuẩn

```python
from odoo import _

# ✅ ĐÚNG — simple translation
message = _("This is a translatable string")

# ✅ ĐÚNG — với %s formatting
name = "Test"
message = _("Record %s has been created") % name

# ✅ ĐÚNG — nhiều giá trị
message = _("Created %s records in %s seconds") % (count, time)

# ✅ ĐÚNG — named placeholders
message = _("Record %(name)s created by %(user)s") % {
    'name': record.name,
    'user': self.env.user.name,
}

# ❌ SAI — f-strings KHÔNG được extract bởi i18n tool
# _(f"Record {name} created")   # Sẽ không được dịch!

# ❌ SAI — concatenation tạo ra 2 chuỗi dịch rời
# _("Hello ") + name + _("!")

# ✅ ĐÚNG — chuỗi đơn với placeholder
_("Hello %s!") % name

# ❌ SAI — HTML trong translation khó dịch
# _("<b>Important:</b> Please confirm")

# ✅ ĐÚNG — tách HTML ra
"<b>%s</b>" % _("Important: Please confirm")

# Log messages KHÔNG cần dịch (giữ tiếng Anh)
import logging
_logger = logging.getLogger(__name__)
_logger.info("Record %s processed", record.id)  # Không dùng _()

# UI messages PHẢI dịch
record.message_post(body=_("Record processed."))
```

### Bước 3 — Field content dịch được (translate=True)

```python
class Product(models.Model):
    _name = 'product.product'
    _description = 'Product'

    # translate=True — nội dung field dịch theo từng ngôn ngữ
    name: str = fields.Char(string='Name', translate=True)
    description: str = fields.Text(string='Description', translate=True)
    website_description: str = fields.Html(
        string='Website Description',
        translate=True,
    )
```

### Bước 4 — Đọc/ghi field theo ngôn ngữ cụ thể

```python
def get_translated_name(self) -> dict[str, str]:
    """Lấy field value theo từng ngôn ngữ."""
    return {
        'current': self.name,
        'french': self.with_context(lang='fr_FR').name,
        'german': self.with_context(lang='de_DE').name,
    }

def set_translated_value(self, field: str, value: str, lang: str) -> None:
    """Ghi field value cho ngôn ngữ cụ thể."""
    self.with_context(lang=lang).write({field: value})
```

### Bước 5 — Selection động với dịch thuật

```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    # Static selection — labels tự động dịch
    priority: str = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], string='Priority', default='1')

    # Dynamic selection — dùng _() cho labels
    @api.model
    def _get_type_selection(self) -> list[tuple[str, str]]:
        return [
            ('type_a', _('Type A')),
            ('type_b', _('Type B')),
        ]

    type: str = fields.Selection(
        selection='_get_type_selection',
        string='Type',
    )

    def get_translated_status(self) -> str:
        """Lấy label Selection đã dịch của state hiện tại."""
        selection = self._fields['state'].selection
        if callable(selection):
            selection = selection(self)
        return dict(selection).get(self.state, self.state)
```

### Bước 6 — Gửi email theo ngôn ngữ partner

```python
def send_email_in_partner_language(self) -> None:
    """Gửi email theo ngôn ngữ của partner."""
    for record in self:
        partner = record.partner_id
        lang = partner.lang or 'en_US'

        # Render template trong ngôn ngữ partner
        template = self.env.ref('my_module.email_template')
        template.with_context(lang=lang).send_mail(record.id)

def process_in_language(self, lang_code: str) -> None:
    """Thực thi code trong ngữ cảnh ngôn ngữ cụ thể."""
    records_fr = self.with_context(lang=lang_code)
    name_in_lang = records_fr.name
```

### Bước 7 — QWeb report theo ngôn ngữ partner

```xml
<template id="report_my_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">
                <div class="page">
                    <!-- Text tĩnh trong XML tự động dịch qua PO -->
                    <h1>Order Confirmation</h1>

                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Quantity</th>
                                <th>Price</th>
                            </tr>
                        </thead>
                        <tbody>
                            <t t-foreach="doc.line_ids" t-as="line">
                                <tr>
                                    <!-- Tên sản phẩm trong ngôn ngữ document -->
                                    <td t-esc="line.product_id.with_context(lang=doc.partner_id.lang).name"/>
                                    <td t-esc="line.quantity"/>
                                    <td t-field="line.price_unit"/>
                                </tr>
                            </t>
                        </tbody>
                    </table>

                    <p>Thank you for your order!</p>
                </div>
            </t>
        </t>
    </t>
</template>
```

### Bước 8 — Cấu trúc file PO

```
my_module/
├── i18n/
│   ├── my_module.pot      # Template (source)
│   ├── fr.po              # Tiếng Pháp
│   ├── de.po              # Tiếng Đức
│   ├── vi.po              # Tiếng Việt
│   └── pt_BR.po           # Portuguese (Brazil)
```

**Định dạng file PO:**
```po
# Translation for Odoo module my_module
# Vietnamese translation
msgid ""
msgstr ""
"Project-Id-Version: Odoo 19.0\n"
"Language: vi\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

#. module: my_module
#: model:ir.model,name:my_module.model_my_model
msgid "My Model"
msgstr "Mô hình của tôi"

#. module: my_module
#: model:ir.model.fields,field_description:my_module.field_my_model__name
msgid "Name"
msgstr "Tên"

#. module: my_module
#: code:addons/my_module/models/my_model.py:0
#, python-format
msgid "Record %s has been created"
msgstr "Bản ghi %s đã được tạo"

#. module: my_module
#: model_terms:ir.ui.view,arch_db:my_module.my_model_view_form
msgid "Confirm"
msgstr "Xác nhận"
```

### Bước 9 — Export/Import translations

```bash
# Export POT template từ Odoo CLI
./odoo-bin -d mydb --i18n-export=/tmp/my_module.pot --modules=my_module

# Import PO file
./odoo-bin -d mydb --i18n-import=/tmp/vi.po --language=vi
```

```python
# Install ngôn ngữ từ code
def install_language(self, lang_code: str) -> 'res.lang':
    """Cài đặt ngôn ngữ và load translations."""
    lang = self.env['res.lang']._activate_lang(lang_code)
    if lang:
        self.env['ir.module.module']._load_module_terms(
            ['my_module'], [lang_code]
        )
    return lang

def get_user_language(self) -> str:
    """Lấy ngôn ngữ của user hiện tại."""
    return self.env.user.lang or self.env.context.get('lang', 'en_US')
```

### Bước 10 — Test translations

```python
def test_translation(self) -> None:
    """Test field translation hoạt động đúng."""
    record = self.env['my.model'].create({'name': 'English Name'})

    # Ghi translation tiếng Pháp
    record.with_context(lang='fr_FR').write({'name': 'Nom Français'})

    # Verify
    self.assertEqual(record.name, 'English Name')
    self.assertEqual(
        record.with_context(lang='fr_FR').name,
        'Nom Français',
    )
```

### Bước 11 — Bảng tóm tắt những gì dịch được

| Thành phần | Dịch được | Cách dịch |
|---|---|---|
| Field labels | Có | `string=` attribute |
| Field help text | Có | `help=` attribute |
| Selection labels | Có | Giá trị tuple |
| Nội dung field | Tuỳ chọn | `translate=True` |
| Error messages | Có | Hàm `_()` |
| Button labels | Có | `string=` trong XML |
| Menu names | Có | `name=` trong XML |
| Text trong report | Có | Text XML tĩnh |
| Log messages | **Không** | Giữ tiếng Anh |

## Constraints
- **KHÔNG** dùng f-strings trong `_()` — sẽ không được extract
- **KHÔNG** concatenate chuỗi dịch — tạo ra nhiều msgid rời
- **KHÔNG** dịch log messages — chỉ dùng `_()` cho UI/user messages
- `translate=True` tốn thêm query khi đọc — chỉ dùng khi thực sự cần

## Best practices
- Dùng `%s` hoặc `%(name)s` cho placeholders — không dùng `.format()` hay f-string
- Field `translate=True` cho name/description để admin có thể dịch từ UI
- Gửi email luôn theo `partner.lang` (không phải user.lang)
- Text trong QWeb report dịch tự động — không cần làm thêm gì
- Chú thích cho translator khi string có thể hiểu 2 nghĩa
