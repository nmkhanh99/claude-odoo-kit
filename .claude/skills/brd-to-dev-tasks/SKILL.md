---
name: brd-to-dev-tasks
description: Đọc BRD Odoo, quét code module hiện tại và base Odoo, phân tích gap để xuất danh sách việc cần làm (ADD/MODIFY) với đường dẫn file cụ thể. Kích hoạt khi user nói "phân tích BRD để code", "tạo task từ BRD", "gap analysis BRD code", "BRD cần làm gì", "đọc BRD phân tích code".
---

# BRD to Dev Tasks

## Goal
Đọc BRD → quét code module custom + base Odoo → so sánh gap → xuất danh sách task có cấu trúc:
**`[ADD|MODIFY] <file_path> — <mô tả ngắn>`**

## When to use this skill
- "phân tích BRD để code", "tạo task từ BRD", "BRD cần làm gì"
- "gap analysis BRD", "đọc BRD phân tích code", "triển khai BRD"
- Sau khi BRD đã được duyệt và cần chuyển sang giai đoạn dev

## Instructions

### Bước 0 — Nạp hiện trạng module (tái sử dụng hoặc chạy mới)

**Kiểm tra trước**: Trong session hiện tại, đã có kết quả từ `scan-odoo-module` chưa?

- **Đã có** → tái sử dụng trực tiếp, **KHÔNG** chạy lại scan. Ghi chú: "Dùng kết quả scan từ [tên module]."
- **Chưa có** → yêu cầu user chạy `scan-odoo-module` trước, hoặc chạy script scan inline:

```bash
python3 /Users/khanhnm/Desktop/odoo-19.0/.claude/skills/scan-odoo-module/scripts/scanner.py
# (thay MODULE_PATH trong file trước khi chạy)
```

Từ kết quả scan, lập **bảng hiện trạng**:
```
| Loại         | Đã có trong custom module         | Placeholder (EMPTY) |
|--------------|-----------------------------------|---------------------|
| Groups       | group_qc_user, group_scrap_manager | –                  |
| ir.rule      | rule_disposal_company             | –                   |
| Models (OK)  | stock.disposal.proposal, ...      | –                   |
| Models (⚠️)  | –                                 | res.users, stock.location |
| Views        | stock_disposal_proposal_views.xml | –                   |
```

### Bước 1 — Đọc BRD, trích xuất yêu cầu kỹ thuật

Đọc toàn bộ BRD (không skip section). Trích xuất vào bảng trung gian:

```
| Loại yêu cầu   | Nội dung cụ thể từ BRD                          | Section BRD |
|----------------|--------------------------------------------------|-------------|
| Model / Field  | model name, field name, field type, constraint   | §2.3        |
| Security Group | tên group, quyền (read/write/create/unlink)      | §2.6        |
| Record Rule    | domain_force, model, group áp dụng              | §3.3        |
| View           | form/list/search/action, menu item               | §2.2.2      |
| Workflow/State | trạng thái, transition, điều kiện               | §2.1        |
| Data file      | dữ liệu mặc định (sequence, parameter…)         | §3.x        |
| Wizard/Report  | tên wizard, input/output                         | –           |
```

→ Xem `@references/brd-extract-guide.md` để biết cách đọc từng section BRD.

### Bước 2 — Đối chiếu Odoo base (tránh reimplement)

Với từng yêu cầu trong bảng Bước 1, kiểm tra Odoo base đã cung cấp chưa:

```bash
# Tìm field/group/model trong Odoo source (chỉ khi cần xác minh cụ thể)
grep -r "<tên cần tìm>" /Users/khanhnm/Desktop/odoo-19.0/odoo/addons/<module>/
```

→ Tham chiếu `@references/odoo-base-coverage.md` cho các trường hợp phổ biến.

**Nguyên tắc**: Không tạo lại thứ Odoo base đã có. Chỉ `_inherit` khi cần thêm field/logic.

> ⚠️ `odoo-base-coverage.md` là tài liệu tĩnh — khi không chắc, grep source thực tế.

### Bước 3 — Phân tích gap

So sánh 3 nguồn:
```
BRD yêu cầu  vs  Đã có (custom, từ Bước 0)  vs  Có trong Odoo base (Bước 2)
```

Phân loại mỗi gap:
- `[ADD]`    — chưa tồn tại ở đâu, cần tạo mới
- `[MODIFY]` — file/class ĐÃ có (kể cả placeholder EMPTY), cần thêm nội dung
- `[CONFIG]` — không cần code, cấu hình trên Odoo UI

**Quan trọng — Placeholder EMPTY**:  
Nếu `scan-odoo-module` báo file là `⚠️ EMPTY` (class rỗng) → type = `[MODIFY]`, không phải `[ADD]`.

Format output → xem `@references/task-output-format.md`

### Bước 4 — Sắp xếp theo thứ tự thực thi (Task Sequencing)

Sau khi có danh sách gap, **sắp xếp theo 6 layer** bắt buộc:

```
Layer 1 — Security     : groups, record rules, ACL   (phải có trước khi chạy bất kỳ thứ gì)
Layer 2 — Models       : _name/_inherit, fields, constraints
Layer 3 — Data         : sequences, default data, seed groups
Layer 4 — Views        : form, list, search, action
Layer 5 — Menus        : menuitem (phụ thuộc action ở Layer 4)
Layer 6 — Config       : hướng dẫn cấu hình UI (không có dependency code)
```

Gắn `Seq` cho mỗi task (1, 2, 3...) theo thứ tự layer. Task trong cùng layer thì thứ tự tự do.

**Dependency đặc biệt** — ghi rõ khi task B phụ thuộc task A:
```
Seq 5 | [ADD] views/approval_views.xml | phụ thuộc: Seq 2 (model phải có trước)
```

### Bước 5 — Hiển thị, xác nhận và handoff

In bảng task list đầy đủ theo format trong `@references/task-output-format.md`.

Sau bảng, in **tóm tắt handoff**:
```
## TỔNG KẾT
  Tổng tasks : XX  (ADD: X | MODIFY: X | CONFIG: X)
  Blocking 🔴: X tasks — phải xong trước khi test chạy được
  Layer thứ tự: Security (X) → Models (X) → Data (X) → Views (X) → Menus (X) → Config (X)

## BƯỚC TIẾP THEO
  → Implement theo Seq 1..N
  → Sau khi code xong: chạy scan-odoo-module lại để verify không còn EMPTY
  → Dùng verify-impl-vs-brd (khi có) để đối chiếu code với BRD
```

Hỏi user xác nhận trước khi chuyển sang implement.

## Constraints
- **KHÔNG** tự implement (viết code) trong skill này — chỉ phân tích và liệt kê task
- **KHÔNG** bỏ sót yêu cầu BRD — phải cover toàn bộ sections (2.2, 2.3, 2.5, 2.6, 3.x)
- **KHÔNG** suggest reimplementing thứ Odoo base đã có sẵn
- **CẦN** grep code thực tế, không đoán mò — "đã có" phải có bằng chứng từ grep
- **CẦN** chỉ rõ file path cụ thể cho mỗi task (không ghi chung chung "trong models/")
- Mỗi BRD module xử lý trong một session riêng

## Best practices
- Đọc `__manifest__.py` trước để biết dependencies và version
- Ưu tiên quét `security/` trước — access rights thường là nguồn lỗi phổ biến nhất
- Với approval workflow: kiểm tra xem module `approvals` hay `mail.activity` đã được dùng chưa
- Multi-company requirement → luôn check domain_force có `company_id` chưa
- Khi BRD có bảng ma trận phân quyền (§2.6): map từng ô → group + operation_type + ir.rule
- `[CONFIG]` tasks nên liệt kê kèm hướng dẫn ngắn (menu path trên Odoo UI)
