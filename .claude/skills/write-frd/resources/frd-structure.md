# FRD Structure — Self-Contained Technical Spec

## Cấu trúc file
File: `frds/FRD-NEW-MAN-xx-[tên]-01.md`
Giới hạn: < 500 lines. Split `-01`, `-02`... nếu cần.

---

# FRD-NEW-MAN-xx: [Tên phân hệ/chức năng]

**Version:** 1.0
**Ngày:** YYYY-MM-DD
**Tham chiếu PRD:** PRD-NEW-MAN-xx-[tên]-01.md
**Type:** Custom / Native / Mixed

---

## 1. Models

### 1.1 [model.name] — [Mô tả ngắn]

> **100% native** — ghi "Không cần custom code" và mô tả config steps.
> **Custom** — phải có Python code đầy đủ dưới đây.

**Fields:**

| Field | Type | Required | Default | Stored | Tracking | Mô tả |
|-------|------|----------|---------|--------|----------|-------|
| `field_name` | Char/Many2one/... | True/False | ... | True/False | True/False | |

**Methods:**

#### `method_name(self, ...)`
- **Trigger:** [Khi nào được gọi — button, compute, onchange, action, ...]
- **Logic:**
  1. Bước 1: ...
  2. Bước 2: ...
- **Return:** [Kiểu trả về và ý nghĩa]
- **Raise:** [Điều kiện raise UserError/ValidationError và message]

```python
def method_name(self, param):
    self.ensure_one()
    # Python code hoàn chỉnh, copy-paste được
    ...
```

---

## 2. Views

### 2.1 [Tên view]

```xml
<record id="view_id" model="ir.ui.view">
    <field name="name">model.name.form.inherit</field>
    <field name="model">model.name</field>
    <field name="inherit_id" ref="module.original_view_xml_id"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='field_name']" position="after">
            <!-- Nội dung thêm vào -->
        </xpath>
    </field>
</record>
```

---

## 3. Security

### 3.1 Groups (`security/security.xml`)
```xml
<record id="group_name" model="res.groups">
    <field name="name">Group Display Name</field>
    <field name="category_id" ref="module.category_id"/>
</record>
```

### 3.2 ACL (`security/ir.model.access.csv`)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,model.name user,model_model_name,group_id,1,1,1,0
```

### 3.3 Record Rules (nếu có)
```xml
<record id="rule_id" model="ir.rule">
    <field name="name">Rule Name</field>
    <field name="model_id" ref="model_model_name"/>
    <field name="domain_force">[('company_id', '=', user.company_id.id)]</field>
    <field name="groups" eval="[(4, ref('group_id'))]"/>
</record>
```

---

## 4. Data files (`data/`)

| File | Nội dung | noupdate |
|------|---------|---------|
| `data/sequence.xml` | Sequences cho mã phiếu | 1 |

---

## 5. Open Questions

| # | Câu hỏi | Trạng thái | Blocking? | Trả lời |
|---|---------|------------|-----------|---------|
| | | | | |
