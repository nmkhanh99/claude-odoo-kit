---
name: scaffold-odoo-code
description: Sinh boilerplate code Odoo 19 từ task list của brd-to-dev-tasks — tạo model, view, security group, record rule, ACL row, data file đúng chuẩn Odoo 19 (list không tree, invisible= không attrs, privilege_id không category_id). Kích hoạt khi user nói "scaffold", "tạo boilerplate", "sinh code", "generate model", "tạo view", "tạo file kho".
---

# Scaffold Odoo Code

## Goal
Nhận task entry từ `brd-to-dev-tasks` → sinh code Odoo 19 ready-to-paste, đúng pattern thực tế của dự án SPS.

**Input**: Task entry + context từ BRD (field list §2.3, states §2.1, groups §2.6)  
**Output**: File content hoàn chỉnh, viết thẳng vào file hoặc hiển thị để review

## When to use this skill
- "scaffold", "tạo boilerplate", "sinh code", "generate model/view"
- Sau khi `brd-to-dev-tasks` xuất task list có `[ADD]`/`[MODIFY]`
- "tạo file cho task Seq X", "viết code cho [ADD] models/X.py"

## Instructions

### Bước 1 — Xác định task và thu thập context

Từ task entry, xác định **scaffold type**:

| Task pattern | Scaffold type |
|---|---|
| `[ADD] models/<name>.py` | → `model-new` |
| `[MODIFY] models/<name>.py` — thêm field/method | → `model-extend` |
| `[ADD] views/<name>.xml` | → `view-full` |
| `[ADD] security/security.xml` — group | → `security-group` |
| `[ADD] security/security.xml` — ir.rule | → `security-rule` |
| `[MODIFY] security/ir.model.access.csv` | → `acl-row` |
| `[ADD] data/<name>.xml` — sequence | → `data-sequence` |

Thu thập context từ BRD (hỏi user nếu thiếu):
- **model-new**: tên model (`_name`), description, fields (từ §2.3), states (từ §2.1/§3.2), groups liên quan
- **view-full**: model name, key fields cần hiển thị, state field, action menu path
- **security-group**: tên group, privilege module, implied group, description
- **security-rule**: tên rule, model, domain_force, group áp dụng
- **acl-row**: model_id, group_id, r/w/c/d permissions

### Bước 2 — Chọn template và sinh code

Đọc template phù hợp, điền context:

| Scaffold type     | Template file                          |
|-------------------|----------------------------------------|
| `model-new`       | `templates/model-new.md`               |
| `model-extend`    | Không có template — dùng pattern inline từ `references/odoo19-patterns.md` |
| `view-full`       | `templates/view-full.md`               |
| `security-group`  | `templates/security-group.md`          |
| `security-rule`   | `templates/security-rule.md`           |
| `acl-row`         | `templates/acl-row.md`                 |
| `data-sequence`   | `templates/data-sequence.md`           |

→ Xem `references/odoo19-patterns.md` cho các pattern bắt buộc Odoo 19.

**Thứ tự sinh code trong 1 session** (khớp với Sequencing của brd-to-dev-tasks):
```
1. security group → 2. security rule → 3. ACL row → 4. model → 5. view → 6. data
```

### Bước 3 — Kiểm tra anti-patterns trước khi xuất

Tự kiểm tra code vừa sinh — REJECT nếu có:
```
❌ <tree ...>          → phải là <list ...>
❌ attrs="{'invisible'  → phải là invisible="..."
❌ def name_get(        → dùng _rec_name + display_name compute
❌ category_id ref=     → phải là privilege_id ref=
❌ self._cr.execute(    → phải dùng self.env.cr.execute() với SQL()
❌ api.multi            → deprecated, bỏ đi
❌ read_group(          → phải là _read_group(
```

→ Full list: `@references/odoo19-patterns.md`

### Bước 4 — Xuất code

Hỏi user: **"Ghi thẳng vào file hay hiển thị để review trước?"**

- **Ghi file**: dùng Write tool, sau đó in diff summary
- **Review trước**: in code block đầy đủ, hỏi xác nhận rồi mới ghi

Sau khi ghi file, nhắc nhở:
```
✅ Đã tạo: <file_path>
⚠️  Nhớ cập nhật __manifest__.py nếu đây là file mới (thêm vào 'data' list)
```

### Bước 5 — Cập nhật __manifest__.py (nếu file mới)

Với `[ADD]` file mới: đọc `__manifest__.py`, thêm đường dẫn vào đúng vị trí trong `data` list:
- `security/` → đầu danh sách (trước views)
- `data/` → sau security, trước views  
- `views/` → giữa
- `wizard/` → sau views

## Constraints
- **KHÔNG** dùng deprecated Odoo API — xem `@references/odoo19-patterns.md`
- **KHÔNG** ghi file nếu chưa hỏi user (Bước 4)
- **KHÔNG** tạo code mà không có context đủ — hỏi trước nếu thiếu field list / state list
- **PHẢI** dùng `_('string')` cho tất cả user-facing strings
- **PHẢI** có `company_id` và `mail.thread` mixin cho model nghiệp vụ chính
- **PHẢI** tuân thủ pattern từ `references/odoo19-patterns.md`

## Best practices
- Sinh security trước model → model trước view (đúng load order)
- `state` field: luôn có `tracking=True, index=True, copy=False`
- `name` field: `default='New', copy=False, readonly=True` + sequence trong `create()`
- Form view: đặt `<header>` với workflow buttons trước tiên
- Với `[MODIFY]`: chỉ sinh đoạn code cần thêm, kèm chỉ dẫn "thêm vào sau dòng X"
- Luôn có `_description` và `_order` trong mọi model mới
