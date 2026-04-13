# Template: view-full
# Dùng khi: [ADD] views/<name>_views.xml

## Generated output

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- ══ Search View ══════════════════════════════════════════ -->
    <record id="view_{model_snake}_search" model="ir.ui.view">
        <field name="name">{model.name}.search</field>
        <field name="model">{model.name}</field>
        <field name="arch" type="xml">
            <search string="{Description}">
                <field name="name"/>
                <!-- thêm field search từ BRD -->
                <filter string="My Records" name="my_records"
                        domain="[('requested_by','=',uid)]"/>
                <separator/>
                <filter string="Draft"     name="draft"
                        domain="[('state','=','draft')]"/>
                <filter string="Done"      name="done"
                        domain="[('state','=','done')]"/>
                <group>
                    <filter string="Trạng thái" name="group_state"
                            context="{'group_by':'state'}"/>
                    <filter string="Công ty" name="group_company"
                            context="{'group_by':'company_id'}"/>
                </group>
            </search>
        </field>
    </record>

    <!-- ══ List View ════════════════════════════════════════════ -->
    <record id="view_{model_snake}_list" model="ir.ui.view">
        <field name="name">{model.name}.list</field>
        <field name="model">{model.name}</field>
        <field name="arch" type="xml">
            <list string="{Description}"
                  decoration-info="state == 'draft'"
                  decoration-warning="state == 'confirmed'"
                  decoration-success="state == 'done'"
                  decoration-muted="state == 'cancel'">
                <field name="name"/>
                <!-- key fields từ BRD §2.3 -->
                <field name="state" widget="badge"
                       decoration-info="state == 'draft'"
                       decoration-success="state == 'done'"
                       decoration-muted="state == 'cancel'"/>
                <field name="requested_by" widget="many2one_avatar_user"/>
                <field name="company_id" groups="base.group_multi_company"/>
            </list>
        </field>
    </record>

    <!-- ══ Form View ════════════════════════════════════════════ -->
    <record id="view_{model_snake}_form" model="ir.ui.view">
        <field name="name">{model.name}.form</field>
        <field name="model">{model.name}</field>
        <field name="arch" type="xml">
            <form string="{Description}">
                <header>
                    <button name="action_confirm" string="Xác nhận"
                            type="object" class="oe_highlight"
                            invisible="state != 'draft'"
                            groups="stock.group_stock_user"/>
                    <button name="action_cancel" string="Hủy"
                            type="object"
                            invisible="state not in ('draft','confirmed')"/>
                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <h1><field name="name" readonly="1"/></h1>
                    </div>
                    <group>
                        <group>
                            <!-- left column: fields từ BRD -->
                        </group>
                        <group>
                            <!-- right column -->
                            <field name="requested_by" widget="many2one_avatar_user"/>
                            <field name="company_id" groups="base.group_multi_company"/>
                        </group>
                    </group>
                    <!-- line_ids nếu có One2many -->
                    <!-- <notebook>
                        <page string="Lines">
                            <field name="line_ids">
                                <list editable="bottom">
                                    ...
                                </list>
                            </field>
                        </page>
                    </notebook> -->
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>

    <!-- ══ Window Action ════════════════════════════════════════ -->
    <record id="action_{model_snake}" model="ir.actions.act_window">
        <field name="name">{Description}</field>
        <field name="res_model">{model.name}</field>
        <field name="view_mode">list,form</field>
        <field name="search_view_id" ref="view_{model_snake}_search"/>
        <field name="context">{}</field>
        <field name="domain">[]</field>
    </record>
</odoo>
```

## Menu item (thêm vào views/menu.xml hoặc file menu riêng)
```xml
<menuitem id="menu_{model_snake}"
          name="{Menu Label}"
          parent="{parent_menu_id}"
          action="action_{model_snake}"
          sequence="10"
          groups="{group_xml_id}"/>
```
