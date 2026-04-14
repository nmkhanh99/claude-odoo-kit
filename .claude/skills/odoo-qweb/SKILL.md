---
name: odoo-qweb
description: Viết QWeb template Odoo — directives t-if/t-foreach/t-set/t-field/t-esc, dynamic attributes, template inheritance, report templates, kanban templates, website pages. Kích hoạt khi user nói "qweb", "template", "t-foreach", "t-if", "t-field", "t-call", "kanban template", "report template".
---

# QWeb Template Patterns (Odoo)

## Goal
Viết QWeb templates đúng chuẩn cho reports, kanban, website — directives, formatting, conditions, loops, inheritance.

**Input**: Mô tả cần hiển thị gì, context template nào  
**Output**: QWeb XML đầy đủ

## When to use this skill
- "viết QWeb template", "t-if t-foreach"
- "template cho kanban", "template báo cáo"
- "kế thừa template có sẵn"
- "website template", "portal template"

## Instructions

### Bước 1 — QWeb Directives Overview

| Directive | Purpose |
|---|---|
| `t-if` / `t-elif` / `t-else` | Conditional rendering |
| `t-foreach` / `t-as` | Loop iteration |
| `t-set` | Variable assignment |
| `t-esc` | Escaped output (text) |
| `t-out` | Output (escaped by default) |
| `t-raw` | Unescaped HTML (dùng cẩn thận) |
| `t-call` | Include another template |
| `t-field` | Field rendering với formatting |
| `t-options` | Field options |
| `t-att-{attr}` | Dynamic attribute value |
| `t-attf-{attr}` | Format string attribute |

### Bước 2 — Conditional Rendering

```xml
<!-- If/Elif/Else -->
<t t-if="record.state == 'draft'">
    <span class="badge bg-secondary">Draft</span>
</t>
<t t-elif="record.state == 'confirmed'">
    <span class="badge bg-primary">Confirmed</span>
</t>
<t t-elif="record.state == 'done'">
    <span class="badge bg-success">Done</span>
</t>
<t t-else="">
    <span class="badge bg-danger">Cancelled</span>
</t>

<!-- Conditional trên element -->
<div t-if="record.partner_id">
    Partner: <t t-esc="record.partner_id.name"/>
</div>

<!-- Multiple conditions -->
<t t-if="record.active and record.state == 'confirmed'">
    Active and confirmed
</t>

<t t-if="record.type in ['product', 'service']">
    Valid type
</t>

<t t-if="record.amount >= 1000 or record.is_priority">
    High value or priority
</t>
```

### Bước 3 — Loops và Iteration

```xml
<!-- Basic loop -->
<t t-foreach="records" t-as="record">
    <div class="record-item">
        <span t-esc="record.name"/>
    </div>
</t>

<!-- Loop với index (t-key bắt buộc trong OWL, recommended trong QWeb) -->
<t t-foreach="lines" t-as="line">
    <tr>
        <td t-esc="line_index + 1"/>  <!-- 0-based index -->
        <td t-esc="line.name"/>
        <td t-if="line_last">Last item</td>
    </tr>
</t>
```

**Loop Variables:**

| Variable | Mô tả |
|---|---|
| `{name}` | Current item |
| `{name}_index` | 0-based index |
| `{name}_size` | Total count |
| `{name}_first` | True nếu là first |
| `{name}_last` | True nếu là last |
| `{name}_odd` | True nếu odd index |
| `{name}_even` | True nếu even index |

```xml
<!-- Nested loops -->
<t t-foreach="orders" t-as="order">
    <div class="order">
        <h3 t-esc="order.name"/>
        <t t-foreach="order.line_ids" t-as="line">
            <div class="line">
                <span t-esc="line.product_id.name"/>
                <span t-esc="line.quantity"/>
            </div>
        </t>
    </div>
</t>

<!-- Striped table -->
<t t-foreach="items" t-as="item">
    <tr t-attf-class="#{item_odd and 'table-light' or ''}">
        <td t-esc="item.name"/>
    </tr>
</t>
```

### Bước 4 — Variables và Expressions

```xml
<!-- Simple assignment -->
<t t-set="total" t-value="0"/>

<!-- Expression -->
<t t-set="total" t-value="sum(line.amount for line in lines)"/>

<!-- Content assignment -->
<t t-set="greeting">
    Hello, <t t-esc="user.name"/>!
</t>

<!-- Calculations -->
<t t-set="subtotal" t-value="record.quantity * record.price"/>
<t t-set="tax" t-value="subtotal * 0.21"/>
<t t-set="total_with_tax" t-value="subtotal + tax"/>
```

### Bước 5 — Output và Escaping

```xml
<!-- t-esc — safe escaped output (dùng cho text thường) -->
<span t-esc="record.name"/>

<!-- t-field — render với formatting (dùng trong reports/website) -->
<span t-field="record.date"/>
<span t-field="record.amount"/>
<span t-field="record.partner_id"/>

<!-- t-field với options -->
<span t-field="record.amount"
      t-options='{"widget": "monetary", "display_currency": doc.currency_id}'/>

<span t-field="record.date"
      t-options='{"format": "dd/MM/yyyy"}'/>

<span t-field="record.duration"
      t-options='{"widget": "duration", "unit": "hour"}'/>

<div t-field="record.partner_id"
     t-options='{"widget": "contact", "fields": ["address", "phone", "email"]}'/>

<!-- t-raw — unescaped HTML (XSS risk — chỉ dùng với data tin cậy) -->
<div t-raw="record.html_content"/>
```

### Bước 6 — Dynamic Attributes

```xml
<!-- t-att: dynamic attribute value -->
<div t-att-class="record.state"/>
<input t-att-value="record.name"/>
<a t-att-href="record.url"/>

<!-- Conditional attribute -->
<div t-att-class="record.active and 'active' or 'inactive'"/>

<!-- t-attf: format string (interpolation với #{}) -->
<div t-attf-class="card state-#{record.state}"/>
<a t-attf-href="/web#id=#{record.id}&amp;model=my.model"/>

<!-- Class list theo conditions -->
<div t-attf-class="
    card
    #{record.state == 'done' and 'bg-success text-white' or ''}
    #{record.is_priority and 'border-warning' or ''}
"/>

<!-- Checkbox disabled -->
<input type="checkbox" t-att-checked="record.active and 'checked'"/>
<button t-att-disabled="not record.can_edit and 'disabled'"/>
```

### Bước 7 — Template Calls (t-call)

```xml
<!-- Define reusable template -->
<template id="address_block">
    <div class="address">
        <div t-esc="partner.name"/>
        <div t-esc="partner.street"/>
        <div><t t-esc="partner.city"/> <t t-esc="partner.zip"/></div>
        <div t-esc="partner.country_id.name"/>
    </div>
</template>

<!-- Call với parameters -->
<t t-call="my_module.address_block">
    <t t-set="partner" t-value="record.partner_id"/>
</t>

<!-- Template với parameters -->
<template id="price_display">
    <span t-attf-class="price #{highlight and 'text-success' or ''}">
        <t t-esc="amount"/> <t t-esc="currency"/>
    </span>
</template>

<t t-call="my_module.price_display">
    <t t-set="amount" t-value="record.amount_total"/>
    <t t-set="currency" t-value="record.currency_id.symbol"/>
    <t t-set="highlight" t-value="record.amount_total > 1000"/>
</t>
```

### Bước 8 — Report Templates

```xml
<!-- Standard report structure -->
<template id="report_my_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">
                <div class="page">
                    <h1 t-field="doc.name"/>
                    <!-- Content -->
                </div>
            </t>
        </t>
    </t>
</template>

<!-- Table với totals -->
<table class="table table-sm">
    <thead>
        <tr>
            <th>Product</th>
            <th class="text-end">Quantity</th>
            <th class="text-end">Price</th>
            <th class="text-end">Subtotal</th>
        </tr>
    </thead>
    <tbody>
        <t t-foreach="doc.line_ids" t-as="line">
            <tr>
                <td t-esc="line.product_id.name"/>
                <td class="text-end" t-esc="line.quantity"/>
                <td class="text-end" t-field="line.price_unit"
                    t-options='{"widget": "monetary",
                                "display_currency": doc.currency_id}'/>
                <td class="text-end" t-field="line.price_subtotal"
                    t-options='{"widget": "monetary",
                                "display_currency": doc.currency_id}'/>
            </tr>
        </t>
    </tbody>
    <tfoot>
        <tr>
            <td colspan="3" class="text-end"><strong>Total:</strong></td>
            <td class="text-end" t-field="doc.amount_total"
                t-options='{"widget": "monetary",
                            "display_currency": doc.currency_id}'/>
        </tr>
    </tfoot>
</table>
```

### Bước 9 — Kanban Templates

```xml
<kanban>
    <field name="name"/>
    <field name="state"/>
    <field name="color"/>
    <templates>
        <t t-name="kanban-box">
            <div t-attf-class="oe_kanban_card oe_kanban_global_click
                               #{kanban_color(record.color.raw_value)}">
                <div class="oe_kanban_content">
                    <div class="o_kanban_record_top">
                        <div class="o_kanban_record_headings">
                            <strong class="o_kanban_record_title">
                                <field name="name"/>
                            </strong>
                        </div>
                    </div>
                    <div class="o_kanban_record_body">
                        <field name="partner_id"/>
                    </div>
                    <div class="o_kanban_record_bottom">
                        <div class="oe_kanban_bottom_left">
                            <field name="priority" widget="priority"/>
                        </div>
                        <div class="oe_kanban_bottom_right">
                            <field name="user_id" widget="many2one_avatar_user"/>
                        </div>
                    </div>
                </div>
            </div>
        </t>
    </templates>
</kanban>
```

### Bước 10 — Website/Portal Templates

```xml
<!-- Website page -->
<template id="my_page" name="My Page">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure">
            <section class="container py-5">
                <h1>My Page Title</h1>
                <t t-foreach="records" t-as="record">
                    <div class="card mb-3">
                        <div class="card-body">
                            <h5 t-esc="record.name"/>
                            <p t-raw="record.description"/>
                        </div>
                    </div>
                </t>
            </section>
        </div>
    </t>
</template>

<!-- Portal template -->
<template id="portal_my_records" name="My Records">
    <t t-call="portal.portal_layout">
        <t t-set="breadcrumbs_searchbar" t-value="True"/>
        <t t-call="portal.portal_searchbar">
            <t t-set="title">My Records</t>
        </t>
        <t t-if="records">
            <t t-foreach="records" t-as="record">
                <div class="card mb-2">
                    <div class="card-body">
                        <a t-attf-href="/my/records/#{record.id}">
                            <t t-esc="record.name"/>
                        </a>
                    </div>
                </div>
            </t>
        </t>
        <t t-else="">
            <p>No records found.</p>
        </t>
    </t>
</template>
```

### Bước 11 — Useful Expressions

```xml
<!-- String operations -->
<t t-esc="record.name.upper()"/>
<t t-esc="record.name[:20] + '...' if len(record.name) > 20 else record.name"/>
<t t-esc="', '.join(record.tag_ids.mapped('name'))"/>
<t t-esc="record.name or 'No name'"/>

<!-- Number formatting -->
<t t-esc="'%.2f' % record.amount"/>
<t t-esc="'{:,.2f}'.format(record.amount)"/>

<!-- Date formatting (trong reports) -->
<t t-esc="format_date(env, record.date)"/>
<t t-esc="record.date.strftime('%d/%m/%Y') if record.date else ''"/>

<!-- List operations -->
<t t-esc="len(record.line_ids)"/>
<t t-esc="sum(record.line_ids.mapped('amount'))"/>
```

### Bước 12 — Template Inheritance

```xml
<!-- Extend existing template -->
<template id="my_inherit" inherit_id="web.layout">
    <xpath expr="//head" position="inside">
        <link rel="stylesheet" href="/my_module/static/src/css/custom.css"/>
    </xpath>
</template>

<!-- Extend report -->
<template id="report_invoice_inherit"
          inherit_id="account.report_invoice_document">
    <xpath expr="//div[@name='invoice_address']" position="after">
        <div class="col-6">
            <strong>Custom:</strong>
            <span t-field="o.x_custom_field"/>
        </div>
    </xpath>
</template>
```

## Constraints
- **KHÔNG** dùng `t-raw` với user data — XSS risk
- `t-field` chỉ dùng trong reports/website (không trong OWL templates)
- Trong OWL dùng `t-esc` hoặc `t-out`
- `t-key` bắt buộc trong OWL foreach, recommended trong QWeb

## Best practices
- `t-esc` cho safety — mặc định escape HTML
- `t-field` trong reports để formatting tự động (monetary, date...)
- `t-call` cho reusable blocks (DRY principle)
- Check null trước khi access field: `t-if="record.partner_id"`
- Dùng Bootstrap classes nhất quán với Odoo UI
