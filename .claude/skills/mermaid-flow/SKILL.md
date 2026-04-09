---
name: mermaid-flow
description: Hiểu, vẽ mới và sửa Mermaid flowchart trong BRD/FRD Odoo — tuân thủ style guide màu sắc và pattern của dự án SPS (flowchart TD, 8 loại node màu, annotation transparent, multi-source diamond). Kích hoạt khi user nói "giải thích luồng", "vẽ mermaid", "sửa luồng", "thêm bước", "cập nhật flowchart", "mermaid bị lỗi", "so sánh luồng".
---

# Mermaid Flow Skill

## Goal
Xử lý Mermaid diagram trong BRD theo **3 chế độ**: HIỂU · VẼ · SỬA  
Tham chiếu `@references/style-guide.md` và `@references/patterns.md`.

## When to use
- "giải thích luồng mermaid", "đọc diagram", "luồng này có nghĩa gì"
- "vẽ luồng", "tạo mermaid", "diagram cho nghiệp vụ X"
- "sửa luồng", "thêm bước", "đổi actor", "cập nhật flowchart"
- "mermaid lỗi không render", "fix diagram"
- "so sánh luồng BRD với ảnh docx"

## Instructions

### Chế độ 1: HIỂU — Giải thích diagram

User hỏi "luồng này có nghĩa gì", paste diagram hoặc chỉ vào section BRD.

1. Đọc diagram (từ file BRD hoặc user paste)
2. Xác định loại pattern: linear / decision / multi-source / approval
3. Mô tả theo cấu trúc:

```
Loại luồng: [Linear / Multi-source / Approval / Decision]
Actor tham gia: [danh sách từ annotation nodes]
Các bước chính: 1. [Bước 1: mô tả + actor] ...
Điều kiện rẽ nhánh: Diamond "{text}" → Nếu [A] / Nếu [B]
Subprocess tham chiếu: [["..."]] → module nào
Ngoài ERP (dash border): [các bước xử lý thủ công]
```

4. Nếu cần so sánh với ảnh docx → gọi `analyze-docx-flows` + xem `@references/compare-guide.md`

---

### Chế độ 2: VẼ — Tạo diagram mới

User mô tả nghiệp vụ bằng lời → cần tạo Mermaid diagram.

**Bước 1 — Thu thập thông tin** (hỏi nếu thiếu): các bước theo thứ tự, actor, điều kiện rẽ nhánh, bước nào ngoài ERP, bước nào tham chiếu module khác.

**Bước 2 — Chọn pattern** từ `@references/patterns.md`: Linear · Decision · Multi-source · Approval · Subprocess

**Bước 3 — Viết diagram**: `flowchart TD` → Start → Main flow → Diamonds → End → Annotation block → Style block

**Bước 4 — Checklist trước khi xuất**:
- [ ] Mọi node ID duy nhất; label có ký tự đặc biệt → bọc `"..."`
- [ ] `linkStyle` index đúng (đếm từ 0); số note node = số step node
- [ ] Mọi End node có màu pink

**Bước 5 — Xuất vào BRD**: section `#### 2.2.1 Luồng tổng quát (Mermaid)`

---

### Chế độ 3: SỬA — Cập nhật diagram

Có thay đổi từ docx phản hồi → cần sửa diagram BRD hiện tại.

**Bước 1** — Đọc diagram hiện tại từ BRD

**Bước 2** — Xác định loại thay đổi:

| Loại thay đổi | Thao tác Mermaid |
|--------------|-----------------|
| Đổi tên actor | Sửa `note` node label + giữ style |
| Thêm bước | Thêm node + `-->` + style + note annotation |
| Bỏ bước | Xóa node + arrow + style + note; cập nhật `linkStyle` index |
| Thêm nhánh rẽ | Thêm diamond + `-->|label|` cho từng nhánh |
| Đổi in-ERP → ngoài ERP | Đổi style sang `#F5F5F5` + `stroke-dasharray:4` |
| Đổi step → subprocess | Đổi `["..."]` thành `[["..."]]` |

**Bước 3** — Cập nhật `linkStyle` index sau khi thêm/xóa node

**Bước 4** — Diff rõ ràng trước khi apply:
```
Thay đổi: note2 "Đối tượng: Thủ kho" → "Đối tượng: Trưởng phòng Kho"
Lý do: C0 – PGĐ – 2026-03-20
```

**Bước 5** — Apply vào BRD bằng Edit tool (chỉ sửa block mermaid)

## Constraints
- Luôn dùng `flowchart TD` — không dùng `LR`, `BT`
- **KHÔNG** tự bịa actor hay tên bước — hỏi user nếu thiếu
- Annotation transparent link **bắt buộc** khi có note nodes
- Theo `doc-no-inference`: nếu diagram docx và BRD mâu thuẫn → báo cáo, không tự chọn
- Khi sửa BRD: chỉ sửa block ` ```mermaid ... ``` `, không đụng text xung quanh

## Best practices
- Diagram > 15 nodes: hỏi user có muốn tách thành 2 sub-diagram không
- Luôn comment phân vùng `%% ── Nhánh X: tên ──` cho multi-source
- `note00` anchor node luôn cần, dù chỉ có 1 note
- Đọc lại 1 lần để check `linkStyle` index trước khi xuất
- Tham chiếu `@references/style-guide.md` cho màu sắc, `@references/patterns.md` cho boilerplate
