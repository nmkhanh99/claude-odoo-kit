---
name: odoo-xml-views
description: Viết XML views Odoo 17+/19 đúng chuẩn — form, list, kanban, search, kế thừa view (inheritance), visibility syntax, actions, menus. Kích hoạt khi user nói "viết view", "tạo form view", "list view", "kanban view", "kế thừa view", "view inheritance", "xml view", "tạo menu".
---

# Odoo XML View Patterns

## Goal
Tạo XML views Odoo 19 đúng chuẩn — form, list (không phải tree), kanban, search, view inheritance — với visibility syntax v17+.

**Input**: Tên model, loại view cần tạo, fields hiển thị  
**Output**: XML views đầy đủ, sẵn sàng dùng

## When to use this skill
- "tạo form view", "tạo list view", "tạo kanban"
- "kế thừa view Odoo", "thêm field vào view"
- "tạo search view", "tạo action, menu"
- "chuyển attrs sang invisible="

## Instructions

### Bước 1 — Quy tắc v17+ bắt buộc

| Tính năng | ❌ v14-v16 (REMOVED) | ✅ v17+ (REQUIRED) |
|---|---|---|
| Visibility | `attrs="{'invisible': [...]}"` | `invisible="expr"` |
| Readonly | `attrs="{'readonly': [...]}"` | `readonly="expr"` |
| Required | `attrs="{'required': [...]}"` | `required="expr"` |
| List view | `<tree ...>` | `<list ...>` |
| view_mode | `'tree,form'` | `'list,form'` |

### Bước 2 — Form View

```xml
<record id="my_model_view_form" model="ir.ui.view">
    <field name="name">my.module.my.model.form</field>
    <field name="model">my.module.my.model</field>
    <field name="arch" type="xml">
        <form string="My Model">
            <header>
                <!-- v17+: Direct Python expressions -->
                <button name="action_confirm" string="Confirm"
                        type="object" class="btn-primary"
                        invisible="state != 'draft'"/>
                <button name="action_cancel" string="Cancel"
                        type="object"
                        invisible="state not in ('draft', 'confirmed')"/>
                <button name="action_draft" string="Reset"
                        type="object"
                        invisible="state != 'cancelled'"/>
                <field name="state" widget="statusbar"
                       statusbar_visible="draft,confirmed,done"/>
            </header>
            <sheet>
                <!-- Stat Buttons -->
                <div class="oe_button_box" name="button_box">
                    <button name="action_view_invoices"
                            type="object"
                            class="oe_stat_button"
                            icon="fa-pencil-square-o">
                        <field name="invoice_count" widget="statinfo"
                               string="Invoices"/>
                    </button>
                </div>
                <!-- Archived ribbon -->
                <widget name="web_ribbon" title="Archived"
                        bg_color="bg-danger"
                        invisible="active"/>
                <!-- Title -->
                <div class="oe_title">
                    <h1>
                        <field name="name" placeholder="Name..."/>
                    </h1>
                </div>
                <!-- Main Groups -->
                <group>
                    <group string="General">
                        <field name="partner_id"/>
                        <field name="date"/>
                        <field name="user_id"/>
                    </group>
                    <group string="Details">
                        <field name="company_id"
                               groups="base.group_multi_company"/>
                        <field name="currency_id" invisible="1"/>
                        <field name="amount"/>
                    </group>
                </group>
                <!-- Notebook -->
                <notebook>
                    <page string="Lines" name="lines">
                        <field name="line_ids">
                            <list editable="bottom">
                                <field name="sequence" widget="handle"/>
                                <field name="name"/>
                                <field name="quantity"/>
                                <field name="price_unit"/>
                                <field name="subtotal" readonly="1"/>
                            </list>
                        </field>
                    </page>
                    <page string="Notes" name="notes">
                        <field name="notes" placeholder="Internal notes..."/>
                    </page>
                </notebook>
            </sheet>
            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="activity_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

### Bước 3 — List View (v17+: `<list>` không phải `<tree>`)

```xml
<record id="my_model_view_list" model="ir.ui.view">
    <field name="name">my.module.my.model.list</field>
    <field name="model">my.module.my.model</field>
    <field name="arch" type="xml">
        <!-- v17+: <list> không phải <tree> -->
        <list string="My Models"
              decoration-danger="state == 'cancelled'"
              decoration-warning="state == 'draft'"
              decoration-success="state == 'done'"
              default_order="date desc">
            <field name="sequence" widget="handle"/>
            <field name="name"/>
            <field name="partner_id"/>
            <field name="date"/>
            <field name="state" widget="badge"
                   decoration-success="state == 'done'"
                   decoration-info="state == 'confirmed'"
                   decoration-warning="state == 'draft'"/>
            <field name="amount" sum="Total"/>
            <!-- Ẩn hoàn toàn column -->
            <field name="company_id" column_invisible="True"/>
            <!-- Column tùy chọn (user có thể show/hide) -->
            <field name="internal_notes" optional="hide"/>
        </list>
    </field>
</record>
```

### Bước 4 — Visibility Conversion (attrs → expressions)

```xml
<!-- ❌ v14-v16 (REMOVED trong v17) -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')],
               'readonly': [('state', '!=', 'draft')],
               'required': [('type', '=', 'customer')]}"/>

<!-- ✅ v17+ -->
<field name="partner_id"
       invisible="state == 'draft'"
       readonly="state != 'draft'"
       required="type == 'customer'"/>
```

**Bảng chuyển đổi attrs → expressions:**

| attrs Domain | v17+ Expression |
|---|---|
| `[('field', '=', 'value')]` | `field == 'value'` |
| `[('field', '!=', 'value')]` | `field != 'value'` |
| `[('field', '=', True)]` | `field` |
| `[('field', '=', False)]` | `not field` |
| `[('field', 'in', ['a','b'])]` | `field in ('a', 'b')` |
| `[('field', '>', 0)]` | `field > 0` |
| `['&', A, B]` | `A and B` |
| `['|', A, B]` | `A or B` |

**Biểu thức phức hợp:**
```xml
<!-- AND -->
<field name="x" invisible="state == 'draft' and not is_manager"/>

<!-- OR -->
<field name="x" invisible="state == 'done' or state == 'cancel'"/>

<!-- Nested -->
<field name="x" invisible="state == 'draft' or (type == 'service' and qty == 0)"/>

<!-- Truy cập parent trong One2many -->
<field name="x" invisible="parent.state != 'draft'"/>

<!-- Context -->
<field name="x" invisible="context.get('hide_field')"/>

<!-- Group check -->
<field name="x" invisible="not user_has_groups('my_module.group_manager')"/>
```

### Bước 5 — Search View

```xml
<record id="my_model_view_search" model="ir.ui.view">
    <field name="name">my.module.my.model.search</field>
    <field name="model">my.module.my.model</field>
    <field name="arch" type="xml">
        <search string="Search My Model">
            <!-- Search fields -->
            <field name="name"/>
            <field name="partner_id"/>
            <field name="user_id"/>

            <!-- Filters -->
            <separator/>
            <filter name="draft" string="Draft"
                    domain="[('state', '=', 'draft')]"/>
            <filter name="confirmed" string="Confirmed"
                    domain="[('state', '=', 'confirmed')]"/>
            <separator/>
            <filter name="my_records" string="My Records"
                    domain="[('user_id', '=', uid)]"/>
            <separator/>
            <filter name="today" string="Today"
                    domain="[('date', '=', context_today().strftime('%Y-%m-%d'))]"/>

            <!-- Group By -->
            <group expand="0" string="Group By">
                <filter name="group_state" string="Status"
                        context="{'group_by': 'state'}"/>
                <filter name="group_partner" string="Partner"
                        context="{'group_by': 'partner_id'}"/>
                <filter name="group_date" string="Date"
                        context="{'group_by': 'date:month'}"/>
            </group>

            <!-- Search Panel (sidebar) -->
            <searchpanel>
                <field name="state" icon="fa-filter" enable_counters="1"/>
                <field name="category_id" icon="fa-folder" enable_counters="1"/>
            </searchpanel>
        </search>
    </field>
</record>
```

### Bước 6 — Kanban View

```xml
<record id="my_model_view_kanban" model="ir.ui.view">
    <field name="name">my.module.my.model.kanban</field>
    <field name="model">my.module.my.model</field>
    <field name="arch" type="xml">
        <kanban default_group_by="state" class="o_kanban_small_column">
            <field name="id"/>
            <field name="name"/>
            <field name="partner_id"/>
            <field name="state"/>
            <field name="color"/>
            <templates>
                <t t-name="kanban-box">
                    <div t-attf-class="oe_kanban_card oe_kanban_global_click #{kanban_color(record.color.raw_value)}">
                        <div class="oe_kanban_content">
                            <div class="o_kanban_record_top">
                                <div class="o_kanban_record_headings">
                                    <strong class="o_kanban_record_title">
                                        <field name="name"/>
                                    </strong>
                                </div>
                                <div class="o_dropdown_kanban dropdown">
                                    <a role="button" class="dropdown-toggle o-no-caret btn"
                                       data-bs-toggle="dropdown" href="#">
                                        <span class="fa fa-ellipsis-v"/>
                                    </a>
                                    <div class="dropdown-menu" role="menu">
                                        <a t-if="widget.editable" role="menuitem"
                                           type="edit" class="dropdown-item">Edit</a>
                                        <a t-if="widget.deletable" role="menuitem"
                                           type="delete" class="dropdown-item">Delete</a>
                                    </div>
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
    </field>
</record>
```

### Bước 7 — View Inheritance

```xml
<record id="view_partner_form_inherit_my_module" model="ir.ui.view">
    <field name="name">res.partner.form.inherit.my_module</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <!-- Thêm field sau field hiện có -->
        <xpath expr="//field[@name='email']" position="after">
            <field name="x_custom_field"/>
        </xpath>

        <!-- Thêm trước -->
        <xpath expr="//field[@name='phone']" position="before">
            <field name="x_another_field"/>
        </xpath>

        <!-- Replace field -->
        <xpath expr="//field[@name='website']" position="replace">
            <field name="website" widget="url"/>
        </xpath>

        <!-- Thêm attributes -->
        <xpath expr="//field[@name='name']" position="attributes">
            <attribute name="required">1</attribute>
        </xpath>

        <!-- Thêm page vào notebook -->
        <xpath expr="//notebook" position="inside">
            <page string="Custom" name="custom">
                <group>
                    <field name="x_custom_field"/>
                </group>
            </page>
        </xpath>
    </field>
</record>
```

**QUAN TRỌNG — Luôn đọc parent view trước khi viết xpath:**
```python
# ✅ Đúng workflow
# 1. Đọc parent view để hiểu cấu trúc thực tế
# 2. Sau đó viết xpath dựa trên cấu trúc thực

# ❌ Sai — tự đoán cấu trúc mà không đọc
```

**XPath Expressions:**

| Expression | Match |
|---|---|
| `//field[@name='x']` | Field name='x' |
| `//group[@name='x']` | Group name='x' |
| `//page[@name='x']` | Page name='x' |
| `//button[@name='x']` | Button name='x' |
| `//notebook` | First notebook |
| `//sheet` | Sheet element |

### Bước 8 — Actions và Menus

```xml
<!-- Window Action — v17+: view_mode dùng 'list' không phải 'tree' -->
<record id="my_model_action" model="ir.actions.act_window">
    <field name="name">My Models</field>
    <field name="res_model">my.module.my.model</field>
    <field name="view_mode">list,form,kanban</field>
    <field name="domain">[('active', '=', True)]</field>
    <field name="context">{'search_default_my_records': 1}</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">
            Create your first record
        </p>
    </field>
</record>

<!-- Root menu -->
<menuitem id="my_module_menu_root"
          name="My Module"
          sequence="10"
          web_icon="my_module,static/description/icon.png"/>

<!-- Submenu -->
<menuitem id="my_module_menu_main"
          name="Main Menu"
          parent="my_module_menu_root"
          sequence="10"/>

<!-- Action menu item -->
<menuitem id="my_model_menu"
          name="My Models"
          parent="my_module_menu_main"
          action="my_model_action"
          sequence="10"/>
```

### Bước 9 — Common Widgets

| Widget | Field Types | Purpose |
|---|---|---|
| `statusbar` | Selection | Status bar display |
| `badge` | Selection | Colored badge |
| `priority` | Selection | Star rating |
| `many2one_avatar_user` | Many2one | User avatar |
| `many2many_tags` | Many2many | Tag chips |
| `monetary` | Float/Monetary | Currency display |
| `handle` | Integer | Drag handle |
| `boolean_toggle` | Boolean | Toggle switch |
| `progressbar` | Float/Integer | Progress bar |
| `html` | Html | Rich text editor |
| `url` | Char | Clickable URL |
| `email` | Char | Mailto link |
| `statinfo` | Integer | Stat button counter |

## Constraints
- **KHÔNG** dùng `<tree>` — phải dùng `<list>`
- **KHÔNG** dùng `attrs=` — phải dùng `invisible=`, `readonly=`, `required=`
- **KHÔNG** dùng `view_mode='tree,form'` — phải dùng `'list,form'`
- **PHẢI** đọc parent view trước khi viết view inheritance

## Best practices
- Form header: buttons + statusbar
- Groups theo 2 cột: general info bên trái, details bên phải
- Notebook cho One2many lines và notes
- Chatter (`oe_chatter`) chỉ khi model kế thừa `mail.thread`
- Dùng `column_invisible="True"` thay `invisible="1"` cho columns trong list
