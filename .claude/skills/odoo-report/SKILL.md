---
name: odoo-report
description: Tạo báo cáo PDF Odoo — QWeb report template, report action, custom report model, paper format, report inheritance. Kích hoạt khi user nói "tạo báo cáo", "PDF report", "in phiếu", "QWeb report", "report template", "kế thừa báo cáo", "báo cáo PDF", "in hóa đơn".
---

# Odoo Report Patterns (QWeb PDF)

## Goal
Tạo báo cáo PDF Odoo đúng chuẩn — report action, QWeb template, custom report model, paper format, report inheritance.

**Input**: Tên model cần in, nội dung cần hiển thị  
**Output**: XML report action + QWeb template + Python report model (nếu cần)

## When to use this skill
- "tạo báo cáo PDF", "in phiếu"
- "QWeb template cho report"
- "custom paper format"
- "kế thừa báo cáo invoice"

## Instructions

### Bước 1 — Cấu trúc file

```
my_module/
├── report/
│   ├── __init__.py
│   ├── my_report.py           # Logic (optional)
│   └── my_report_templates.xml # QWeb templates
└── __manifest__.py
```

**Manifest:**
```python
'data': [
    'report/my_report_templates.xml',
],
```

### Bước 2 — Report Action + Template (XML)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Report Action -->
    <record id="report_my_model" model="ir.actions.report">
        <field name="name">My Report</field>
        <field name="model">my.module.my.model</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">my_module.report_my_model_document</field>
        <field name="report_file">my_module.report_my_model_document</field>
        <field name="print_report_name">'MyReport - %s' % object.name</field>
        <field name="binding_model_id" ref="my_module.model_my_module_my_model"/>
        <field name="binding_type">report</field>
        <field name="paperformat_id" ref="base.paperformat_euro"/>
    </record>

    <!-- QWeb Template -->
    <template id="report_my_model_document">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <!-- Dùng company letterhead -->
                <t t-call="web.external_layout">
                    <div class="page">
                        <!-- Tiêu đề -->
                        <h2>
                            <span t-field="doc.name"/>
                        </h2>

                        <!-- Header thông tin -->
                        <div class="row mt-4">
                            <div class="col-6">
                                <strong>Customer:</strong>
                                <span t-field="doc.partner_id.name"/>
                            </div>
                            <div class="col-6 text-end">
                                <strong>Date:</strong>
                                <span t-field="doc.date"/>
                            </div>
                        </div>

                        <!-- Table dòng -->
                        <table class="table table-sm mt-4">
                            <thead>
                                <tr>
                                    <th>Description</th>
                                    <th class="text-end">Quantity</th>
                                    <th class="text-end">Price</th>
                                    <th class="text-end">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                <t t-foreach="doc.line_ids" t-as="line">
                                    <tr>
                                        <td><span t-field="line.name"/></td>
                                        <td class="text-end">
                                            <span t-field="line.quantity"/>
                                        </td>
                                        <td class="text-end">
                                            <span t-field="line.price_unit"
                                                  t-options='{"widget": "monetary",
                                                              "display_currency": doc.currency_id}'/>
                                        </td>
                                        <td class="text-end">
                                            <span t-field="line.subtotal"
                                                  t-options='{"widget": "monetary",
                                                              "display_currency": doc.currency_id}'/>
                                        </td>
                                    </tr>
                                </t>
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td colspan="3" class="text-end">
                                        <strong>Total:</strong>
                                    </td>
                                    <td class="text-end">
                                        <strong>
                                            <span t-field="doc.amount_total"
                                                  t-options='{"widget": "monetary",
                                                              "display_currency": doc.currency_id}'/>
                                        </strong>
                                    </td>
                                </tr>
                            </tfoot>
                        </table>

                        <!-- Notes -->
                        <div t-if="doc.notes" class="mt-4">
                            <strong>Notes:</strong>
                            <p t-field="doc.notes"/>
                        </div>
                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

### Bước 3 — QWeb Directives Chính

```xml
<!-- Text output — dùng t-field trong reports, t-esc trong templates -->
<span t-field="doc.name"/>
<span t-esc="doc.description"/>

<!-- Field với formatting -->
<span t-field="doc.date"
      t-options='{"format": "dd/MM/yyyy"}'/>

<span t-field="doc.amount_total"
      t-options='{"widget": "monetary",
                  "display_currency": doc.currency_id}'/>

<span t-field="doc.quantity"
      t-options='{"precision": 2}'/>

<!-- Partner address block -->
<div t-field="doc.partner_id"
     t-options='{"widget": "contact",
                 "fields": ["address", "phone", "email"]}'/>

<!-- Conditional -->
<t t-if="doc.state == 'done'">
    <span class="badge bg-success">Completed</span>
</t>
<t t-elif="doc.state == 'cancel'">
    <span class="badge bg-danger">Cancelled</span>
</t>
<t t-else="">
    <span class="badge bg-secondary">In Progress</span>
</t>

<!-- Loop với index -->
<t t-foreach="doc.line_ids" t-as="line">
    <tr>
        <!-- line_index: 0-based, line_first, line_last, line_size -->
        <td><t t-esc="line_index + 1"/></td>
        <td><span t-field="line.name"/></td>
    </tr>
</t>

<!-- Variables -->
<t t-set="total" t-value="sum(doc.line_ids.mapped('amount'))"/>
<span t-esc="total"/>

<!-- Dynamic attribute -->
<tr t-att-class="'table-danger' if line.amount &lt; 0 else ''"/>
<div t-attf-class="alert alert-#{doc.state == 'done' and 'success' or 'warning'}"/>
```

### Bước 4 — Custom Report Model

```python
# report/my_report.py
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Optional
from odoo import api, models


class MyReport(models.AbstractModel):
    _name = 'report.my_module.report_my_model_document'
    _description = 'My Report'

    @api.model
    def _get_report_values(
        self,
        docids: list[int],
        data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Prepare report data."""
        docs = self.env['my.module.my.model'].browse(docids)

        # Tính totals
        totals = {
            'amount': sum(docs.mapped('amount_total')),
            'count': len(docs),
        }

        # Data phụ
        categories = docs.mapped('category_id')

        return {
            'doc_ids': docids,
            'doc_model': 'my.module.my.model',
            'docs': docs,
            'data': data,
            'totals': totals,
            'categories': categories,
            'company': self.env.company,
        }
```

**Dùng custom values trong template:**
```xml
<template id="report_my_model_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">
                <div class="page">
                    <p>Total Records: <t t-esc="totals['count']"/></p>
                    <p>Grand Total:
                        <span t-esc="totals['amount']"/>
                    </p>

                    <ul>
                        <t t-foreach="categories" t-as="cat">
                            <li t-esc="cat.name"/>
                        </t>
                    </ul>
                </div>
            </t>
        </t>
    </t>
</template>
```

### Bước 5 — Paper Format

```xml
<!-- Custom paper format -->
<record id="paperformat_my_module" model="report.paperformat">
    <field name="name">My Module Format</field>
    <field name="default" eval="False"/>
    <field name="format">A4</field>
    <field name="orientation">Portrait</field>
    <field name="margin_top">40</field>
    <field name="margin_bottom">20</field>
    <field name="margin_left">7</field>
    <field name="margin_right">7</field>
    <field name="header_line" eval="False"/>
    <field name="header_spacing">35</field>
    <field name="dpi">90</field>
</record>

<!-- Standard formats -->
<!-- base.paperformat_euro — A4 Portrait -->
<!-- base.paperformat_us  — Letter Portrait -->
```

### Bước 6 — Print từ Python

```python
# Single record
def action_print(self) -> dict[str, Any]:
    return self.env.ref('my_module.report_my_model').report_action(self)

# Multiple records
def action_print_selected(self) -> dict[str, Any]:
    return self.env.ref('my_module.report_my_model').report_action(self.ids)

# Với custom data
def action_print_with_data(self) -> dict[str, Any]:
    data = {
        'date_from': str(self.date_from),
        'date_to': str(self.date_to),
    }
    return self.env.ref('my_module.report_my_model').report_action(
        self, data=data
    )
```

### Bước 7 — Report Inheritance

```xml
<!-- Kế thừa báo cáo có sẵn (ví dụ: invoice) -->
<template id="report_invoice_document_inherit"
          inherit_id="account.report_invoice_document">
    <xpath expr="//div[@name='invoice_address']" position="after">
        <div class="col-6">
            <strong>Custom Field:</strong>
            <span t-field="o.x_custom_field"/>
        </div>
    </xpath>
</template>
```

### Bước 8 — CSS cho Report

```xml
<!-- Inline styles trong template -->
<style>
    .my-report-table {
        width: 100%;
        border-collapse: collapse;
    }
    .my-report-table th {
        background-color: #f5f5f5;
        border-bottom: 2px solid #333;
    }
    .page-break {
        page-break-after: always;
    }
</style>

<!-- Multi-page với page break -->
<t t-foreach="docs" t-as="doc">
    <div class="page">
        <!-- Content -->
    </div>
    <t t-if="not doc_last">
        <div class="page-break"/>
    </t>
</t>
```

**External stylesheet (manifest):**
```python
'assets': {
    'web.report_assets_common': [
        'my_module/static/src/scss/report.scss',
    ],
},
```

## Constraints
- **PHẢI** đặt `report_name` trùng với `template id`
- **PHẢI** khai báo report trong manifest data
- Report model `_name` **phải** có format: `report.{module}.{report_name}`
- `t-field` chỉ dùng trong reports/website — `t-esc` cho OWL templates

## Best practices
- Dùng `web.external_layout` cho tài liệu chuyên nghiệp (có company header)
- Test PDF render — wkhtmltopdf có thể render khác browser
- Dùng monetary widget + currency cho tất cả số tiền
- `t-esc` hoặc `t-field` cho user content (ngăn XSS)
- Kiểm tra `t-if` trước khi display field có thể null
- Group reports theo category với page break
