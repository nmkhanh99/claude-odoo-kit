---
name: brd-to-dev-tasks
description: Đọc BRD Odoo, quét code module hiện tại và base Odoo, phân tích gap để xuất danh sách việc cần làm (ADD/MODIFY) với đường dẫn file cụ thể, lý do thay đổi, hiện trạng code, mong muốn sau thay đổi, và xuất file Excel báo cáo task list. Kích hoạt khi user nói "phân tích BRD để code", "tạo task từ BRD", "gap analysis BRD code", "BRD cần làm gì", "đọc BRD phân tích code".
---

# BRD to Dev Tasks

## Goal
Đọc BRD → quét code module custom + base Odoo → so sánh gap → xuất danh sách task có cấu trúc đầy đủ:

| Trường | Nội dung |
|--------|----------|
| `[ADD\|MODIFY\|CONFIG]` | Loại thay đổi |
| `<file_path>` | Đường dẫn file cụ thể |
| **Lý do thay đổi** | BRD section + rule number yêu cầu; tại sao cần thay đổi |
| **Hiện trạng** | Code hiện tại là gì (EMPTY / chưa có / đang làm X sai) |
| **Mong muốn** | Kết quả kỹ thuật cụ thể sau khi implement xong |

→ Xuất file Excel `.xlsx` lưu trong `<module>/.doc/features/<brd_id>/`

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

### Bước 3 — Phân tích gap và gắn 3 trường bắt buộc

So sánh 3 nguồn:
```
BRD yêu cầu  vs  Đã có (custom, từ Bước 0)  vs  Có trong Odoo base (Bước 2)
```

**Phân loại type:**
- `[ADD]`    — chưa tồn tại ở đâu, cần tạo mới
- `[MODIFY]` — file/class ĐÃ có (kể cả placeholder EMPTY), cần thêm nội dung
- `[CONFIG]` — không cần code, cấu hình trên Odoo UI

**Quan trọng — Placeholder EMPTY**:  
Nếu `scan-odoo-module` báo file là `⚠️ EMPTY` (class rỗng) → type = `[MODIFY]`, không phải `[ADD]`.

**Bắt buộc — Gắn 3 trường cho mỗi task:**

| Trường | Định nghĩa | Ví dụ |
|--------|-----------|-------|
| **Lý do thay đổi** | BRD section + rule nào yêu cầu; hậu quả nếu không làm | `§3.3 Rule 2 — Không có record rule → NV kho thao tác được toàn bộ kho, vi phạm Task Separation` |
| **Hiện trạng** | Kết quả scan thực tế: file rỗng / method chưa có / field thiếu / rule không tồn tại | `models/res_users.py tồn tại nhưng class ResUsers rỗng — chưa có field warehouse_ids` |
| **Mong muốn** | Trạng thái kỹ thuật cụ thể sau khi task hoàn thành (đủ để dev tự code không cần hỏi lại) | `Thêm warehouse_ids = fields.Many2many('stock.warehouse', 'res_users_warehouse_rel', 'user_id', 'warehouse_id', string='Kho được phân công')` |

**Nguyên tắc viết 3 trường:**
- **Lý do**: Trích trực tiếp từ BRD (§X.Y, Rule Z) + 1 câu giải thích nghiệp vụ. Không được viết chung chung "BRD yêu cầu".
- **Hiện trạng**: Phải có bằng chứng từ grep/scan — không được viết "chưa có" mà không kiểm tra.
- **Mong muốn**: Đủ cụ thể để developer code ngay — tên field, type, tên method, domain_force, hay màn hình UI path.

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

In bảng task list theo format đầy đủ **10 cột**:

```
| Seq | Type | File Path | Lý do thay đổi | Hiện trạng | Mong muốn | Layer | Priority | Phụ thuộc |
```

**Quy tắc hiển thị:**
- Mỗi task chiếm **1 dòng** trong bảng Markdown
- Cột **Lý do thay đổi**: `§X.Y Rule Z — <1 câu nghiệp vụ>`
- Cột **Hiện trạng**: trích dẫn kết quả scan thực tế (tên file, trạng thái EMPTY/missing/exists)
- Cột **Mong muốn**: đủ cụ thể để dev hiểu ngay không cần hỏi lại

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

Sau khi hiển thị xong → **tự động** thực hiện Bước 6 (xuất Excel) mà không cần hỏi user.

### Bước 6 — Xuất Excel task list (bắt buộc, tự động)

Sau khi hoàn thành Bước 5, **luôn** xuất file Excel mà không cần user yêu cầu.

**6.1 Xác định output path:**
```
<module_root>/.doc/features/<brd_id_lowercase>/tasks_<brd_id>_<tên_ngắn>.xlsx
```
Ví dụ: `addons-scx/scx_inventory/.doc/features/inv_01_warehouse_hr/tasks_INV-01_quan_ly_nhan_su_kho.xlsx`

Nếu thư mục chưa tồn tại → tạo thư mục trước khi ghi file.

**6.2 Tạo file `export_data.json`** tại cùng thư mục output, theo schema:
```json
{
  "output_path": "<đường dẫn tuyệt đối tới .xlsx>",
  "title": "TASK LIST – <BRD_ID>: <TÊN BRD IN HOA>",
  "subtitle": "Module: <module_name> | BRD: <brd_id> | Xuất: <YYYY-MM-DD>",
  "color_mapping": {
    "ADD":          "D9EAD3",
    "MODIFY":       "FFF2CC",
    "CONFIG":       "F3F3F3",
    "Blocking":     "F4CCCC",
    "Normal":       "FFFFFF",
    "Non-blocking": "D9EAD3"
  },
  "legend": [
    {"label": "ADD = Tạo mới file/model",          "color": "D9EAD3"},
    {"label": "MODIFY = Chỉnh sửa file đã có",     "color": "FFF2CC"},
    {"label": "CONFIG = Cấu hình trên Odoo UI",    "color": "F3F3F3"},
    {"label": "Blocking = Phải xong trước khi test","color": "F4CCCC"},
    {"label": "Non-blocking = Không chặn dev",     "color": "D9EAD3"}
  ],
  "summary_sheet": {
    "name": "TỔNG HỢP",
    "add_total_row": true,
    "headers": [
      {"label": "Layer",  "width": 22},
      {"label": "ADD",    "width": 8},
      {"label": "MODIFY", "width": 10},
      {"label": "CONFIG", "width": 10},
      {"label": "Tổng",   "width": 8}
    ],
    "rows": [ ... ]
  },
  "detail_sheets": [
    {
      "name": "Task List",
      "color_col_index": 1,
      "headers": [
        {"label": "Seq",              "width": 6},
        {"label": "Type",             "width": 10},
        {"label": "File Path",        "width": 45},
        {"label": "Mô tả",            "width": 45},
        {"label": "Lý do thay đổi",   "width": 50},
        {"label": "Hiện trạng",       "width": 45},
        {"label": "Mong muốn",        "width": 55},
        {"label": "Layer",            "width": 22},
        {"label": "Priority",         "width": 14},
        {"label": "Phụ thuộc",        "width": 14}
      ],
      "rows": [ ... ]
    }
  ]
}
```
- `color_col_index: 1` → tô màu theo cột **Type** (ADD/MODIFY/CONFIG)
- Summary rows: đếm ADD/MODIFY/CONFIG theo từng Layer
- Detail rows: mỗi task một dòng với đủ 10 cột; cột Phụ thuộc ghi "Seq X" hoặc "–"
- Cột **Lý do thay đổi**, **Hiện trạng**, **Mong muốn** phải có nội dung thực — không được để trống

**6.3 Chạy universal_builder:**
```bash
python3 /Users/khanhnm/Desktop/odoo-19.0/.claude/skills/export-excel/scripts/universal_builder.py \
  "<đường dẫn tuyệt đối tới export_data.json>"
```

**6.4 Xóa file JSON tạm** sau khi xuất thành công (file trung gian, không cần giữ lại).

**6.5 Thông báo kết quả:**
```
✅ Excel đã xuất: <output_path>
```

## Constraints
- **KHÔNG** tự implement (viết code) trong skill này — chỉ phân tích và liệt kê task
- **KHÔNG** bỏ sót yêu cầu BRD — phải cover toàn bộ sections (2.2, 2.3, 2.5, 2.6, 3.x)
- **KHÔNG** suggest reimplementing thứ Odoo base đã có sẵn
- **CẦN** grep code thực tế, không đoán mò — "đã có" phải có bằng chứng từ grep
- **CẦN** chỉ rõ file path cụ thể cho mỗi task (không ghi chung chung "trong models/")
- **CẦN** điền đủ 3 trường bắt buộc cho mỗi task — không được để trống hoặc viết chung chung:
  - **Lý do thay đổi**: phải trích dẫn đúng §section và Rule, kèm 1 câu nghiệp vụ cụ thể
  - **Hiện trạng**: phải dựa trên kết quả grep/scan thực tế — không được suy diễn
  - **Mong muốn**: phải đủ cụ thể để developer tự code không cần hỏi lại (tên field, method, domain, UI path)
- Mỗi BRD module xử lý trong một session riêng

## Best practices
- Đọc `__manifest__.py` trước để biết dependencies và version
- Ưu tiên quét `security/` trước — access rights thường là nguồn lỗi phổ biến nhất
- Với approval workflow: kiểm tra xem module `approvals` hay `mail.activity` đã được dùng chưa
- Multi-company requirement → luôn check domain_force có `company_id` chưa
- Khi BRD có bảng ma trận phân quyền (§2.6): map từng ô → group + operation_type + ir.rule
- `[CONFIG]` tasks nên liệt kê kèm hướng dẫn ngắn (menu path trên Odoo UI)
