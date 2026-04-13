---
name: verify-impl-vs-brd
description: Kiểm chứng code đã implement đúng và đủ BRD chưa — so sánh từng yêu cầu BRD với source code module, gán trạng thái [DONE]/[PARTIAL]/[MISSING], xuất báo cáo. Kích hoạt khi user nói "verify impl", "kiểm tra code vs BRD", "code đã đủ BRD chưa", "check impl", "đối chiếu BRD code", "còn thiếu gì so với BRD".
---

# Verify Implementation vs BRD

## Goal
Đọc BRD + quét source code module → đối chiếu từng yêu cầu → gán status:
- `[DONE]`    — đã implement đầy đủ, tìm thấy trong code
- `[PARTIAL]` — có trong code nhưng thiếu thuộc tính/logic so với BRD
- `[MISSING]` — không tìm thấy trong code, chưa làm

## When to use this skill
- "verify impl", "kiểm tra code vs BRD", "code đã đủ BRD chưa"
- "check impl", "đối chiếu BRD code", "còn thiếu gì so với BRD"
- Sau khi implement xong một batch task (từ `brd-to-dev-tasks`)
- Trước khi demo / UAT để đảm bảo không miss requirement

## Instructions

### Bước 0 — Nạp task list (tái sử dụng nếu có)

**Kiểm tra session**: Đã có output từ `brd-to-dev-tasks` chưa?
- **Đã có** → tái sử dụng trực tiếp làm checklist, ghi chú: "Dùng task list từ session."
- **Chưa có** → đọc BRD trực tiếp và tự extract checklist theo `@references/check-rules.md`

Checklist có cấu trúc:
```
| # | Loại          | Yêu cầu cụ thể                      | Section BRD |
|---|---------------|--------------------------------------|-------------|
| 1 | security-group| group_warehouse_staff (NV kho)       | §2.6        |
| 2 | model-field   | res.users.warehouse_ids (Many2many)  | §2.3        |
| 3 | ir-rule       | rule warehouse per user              | §3.3        |
| 4 | acl-row       | stock.picking / group_warehouse_staff| §2.6        |
| 5 | state-machine | draft→confirmed→done (3 states)      | §2.1        |
```

### Bước 1 — Chạy scan để lấy hiện trạng code

Tái sử dụng kết quả `scan-odoo-module` nếu có trong session.  
Nếu chưa, chạy `scan-odoo-module` skill trước, hoặc chạy script verify trực tiếp:

```bash
python3 - << 'PYEOF'
# paste toàn bộ nội dung scripts/impl_checker.py, thay MODULE_PATH + REQUIREMENTS
PYEOF
```

### Bước 2 — Đối chiếu từng yêu cầu

Với mỗi item trong checklist, áp dụng **check rule** từ `@references/check-rules.md`:

| Loại yêu cầu    | Kiểm tra cụ thể |
|-----------------|-----------------|
| `security-group`| grep `id="group_X"` trong security/security.xml |
| `model-field`   | grep `field_name = fields.` trong models/ |
| `ir-rule`       | grep `domain_force` + model ref trong security/ |
| `acl-row`       | grep model name trong ir.model.access.csv |
| `state-machine` | grep `state.*Selection` + kiểm tra đủ values |
| `workflow-action`| grep `def action_X` trong models/ |
| `view-form`     | grep `res_model.*model.name` trong views/ |
| `menu-item`     | grep `menuitem.*action_X` trong views/ |
| `data-sequence` | grep `ir.sequence` + code trong data/ |

Quy tắc gán status → xem `@references/check-rules.md`

### Bước 3 — Xuất Verification Report

```
📋 VERIFICATION REPORT: <BRD Module> vs <Module Path>
   Ngày verify: <date>

✅ DONE    : X / Y  (XX%)
⚠️ PARTIAL : X / Y
❌ MISSING : X / Y

── DETAILS ──────────────────────────────────────────

[DONE] #1 | security-group | group_warehouse_staff
  Found : security/security.xml line 12
  Match : privilege_id, implied_ids ✅

[PARTIAL] #2 | model-field | res.users.warehouse_ids
  Found : models/res_users.py line 8
  Issue : tracking=True thiếu (BRD §2.3 yêu cầu audit trail)
  Fix   : thêm `tracking=True` vào field definition

[MISSING] #5 | ir-rule | warehouse per user restriction
  Found : KHÔNG TÌM THẤY trong security/security.xml
  BRD   : §3.3 — NV kho chỉ thấy picking trong warehouse được phân công
  Action: [ADD] security/security.xml — thêm ir.rule domain_force warehouse_ids

── TÓM TẮT ACTION ────────────────────────────────────

⚠️ CẦN FIX (PARTIAL):
  1. models/res_users.py → thêm tracking=True vào warehouse_ids

❌ CẦN LÀM (MISSING):
  1. security/security.xml → ir.rule warehouse restriction

📊 STATUS: X DONE | Y PARTIAL (cần patch) | Z MISSING (cần implement)
```

### Bước 4 — Tạo patch task list (tùy chọn)

Nếu có PARTIAL hoặc MISSING, hỏi user:
> "Muốn tôi tạo patch task list (PARTIAL + MISSING) để implement không?"

Nếu có → xuất bảng patch tasks theo format `brd-to-dev-tasks`:
```
| Seq | Type     | File path                    | Mô tả              | Priority |
|-----|----------|------------------------------|--------------------|----------|
| 1   | [MODIFY] | models/res_users.py          | thêm tracking=True | 🔴 High  |
| 2   | [ADD]    | security/security.xml        | ir.rule warehouse  | 🔴 High  |
```

## Constraints
- **CẤM** tự sửa code trong skill này — chỉ báo cáo và gợi ý
- **KHÔNG** đánh DONE nếu chưa grep xác minh — mọi kết luận phải có file path bằng chứng
- **CẤM** bỏ sót requirement — phải verify TẤT CẢ items trong checklist
- **CẤM** đánh DONE cho EMPTY class (class chỉ có `_inherit`, không có field/method)
- Mỗi BRD module verify trong một session riêng

## Best practices
- Reuse `scan-odoo-module` + `brd-to-dev-tasks` output từ cùng session — tránh scan trùng
- PARTIAL thường nguy hiểm hơn MISSING vì dev nghĩ "đã làm xong"
- Kiểm tra `__manifest__.py` dependencies — missing dependency = runtime error dù code đúng
- Với approval workflow: xác minh cả `mail.activity` type và `approval.request` model
- In % completion cuối report để user thấy tổng quan nhanh
