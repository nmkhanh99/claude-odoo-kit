---
name: export-excel
description: Kỹ năng "Universal JSON Builder" xuất mọi dữ liệu phân tích, list lỗi, bảng tổng hợp ra file Excel chuyên nghiệp với số lượng cột và màu sắc tuỳ biến. Kích hoạt khi user nói "xuất excel", "tính năng báo cáo", "export excel", "xuất array ra excel".
---

# Export Excel (Universal Builder)

## Goal
Tạo file `.xlsx` chuyên nghiệp dựa trên file cấu hình JSON được định nghĩa động (Dynamic Columns, Dynamic Colors, Totals, Freeze pane). 
Kỹ năng này hoạt động đóng vai trò như một **System Utility** — các kỹ năng khác (như `analyze-brd-changes`, PRD, bug reports...) đều có thể gọi kỹ năng này để render mảng dữ liệu ra Excel.

## When to use this skill
- "xuất excel", "export excel", "tạo báo cáo excel", "lưu excel"
- Khi người dùng muốn xem kết quả dưới dạng bảng biểu / tracker (log lỗi, lịch sử thay đổi, task list...).
- Được các kỹ năng phân tích khác gọi vào lưới xử lý.

## Instructions

### 1. Chuẩn bị file JSON (`export_data.json`)
Thay vì phải code Python script trực tiếp, Hãy tạo ra 1 file `docs/export_data.json` tuân theo cấu trúc Schema dưới đây. **Bạn có quyền tuỳ chỉnh số lượng CỘT tuỳ ý**.

```json
{
  "output_path": "docs/Bao_cao_XYZ.xlsx",
  "title": "TIÊU ĐỀ LỚN NHẤT CỦA FILE",
  "subtitle": "Ngày xuất / Nguồn trích dẫn (Dòng itallic nhỏ dưới Title)",
  "color_mapping": {
    "Sửa": "FFF2CC",
    "Thêm mới": "D9EAD3",
    "Cảnh báo": "FCE4D6",
    "Lỗi": "F4CCCC",
    "Open Question": "F3F3F3",
    "Bỏ": "EAD1DC"
  },
  "legend": [
    {"label": "Đỏ = Xóa/Lỗi", "color": "F4CCCC"},
    {"label": "Vàng = Chỉnh sửa", "color": "FFF2CC"},
    {"label": "Xanh = Thêm mới/Passed", "color": "D9EAD3"}
  ],
  "summary_sheet": {
    "name": "TỔNG HỢP",
    "add_total_row": true,
    "headers": [
      {"label": "Module / Tên Sheet", "width": 20},
      {"label": "Lỗi/Vấn đề", "width": 15},
      {"label": "Thành công", "width": 15}
    ],
    "rows": [
      ["Frontend OWL", 10, 5],
      ["Backend Controller", 2, 20]
    ]
  },
  "detail_sheets": [
    {
      "name": "Frontend OWL",
      "color_col_index": 2,
      "headers": [
        {"label": "STT", "width": 5},
        {"label": "Mô tả Issue", "width": 45},
        {"label": "Loại", "width": 15},
        {"label": "Assignee", "width": 20}
      ],
      "rows": [
        [1, "Lỗi UI Component A", "Lỗi", "User1"],
        [2, "Missing Docs", "Cảnh báo", "User2"]
      ]
    }
  ]
}
```

> **Lưu ý `color_col_index`**: Là chỉ số cột (index BẮT ĐẦU TỪ 0) chứa đoạn Text sẽ dùng làm key tra cứu vào `color_mapping` để tô màu nguyên cành row đó. (Ví dụ: cột "Loại" ở vị trí số mảng `[2]` là `"Lỗi"` -> Tô màu đỏ). Nếu không muốn tô màu theo dòng thì đừng truyền trường này.

### 2. Thực thi Script Universal Builder
Sau khi có JSON file, chạy script sau qua Bash:
```bash
python3 .agents/skills/export-excel/scripts/universal_builder.py docs/export_data.json
```

### 3. Báo cáo hoàn tất
Trình bày URL output_path của file Excel vừa được tạo ra cho Khách Hàng.

## Helper Functions Reference

Các function có sẵn trong `universal_builder.py` (tự động xử lý, không cần gọi thủ công):

| Function | Dùng khi |
|----------|---------|
| `make_title(ws, text, ncols, row)` | Tiêu đề merge toàn hàng, nền navy |
| `make_subtitle(ws, text, ncols, row)` | Dòng nguồn/ngày, nền xám nhạt |
| `make_header(ws, row, cols)` | Header row theo `cols = [(label, width), ...]` |
| `make_data(ws, row, values, loai, alt)` | Ghi 1 dòng, tự tô màu theo `loai` |
| `make_total_row(ws, row, values, ncols)` | Dòng TỔNG nền xanh đậm |
| `make_legend(ws, start_row, ncols)` | Khối chú giải màu cuối sheet |
| `make_detail_sheet(wb, name, title, data)` | Tạo sheet chi tiết 1 module (theo cột chuẩn) |
| `make_summary_sheet(wb, title, subtitle, data, cols)` | Tạo sheet TỔNG HỢP hoàn chỉnh |
| `row_height(values)` | Tính chiều cao dòng tự động |
| `hfill(hex)` | PatternFill từ hex string |
| `tborder()` | Border mỏng màu BDD7EE |

## Constraints
- **Luôn dùng `python3 universal_builder.py`** — KHÔNG sinh array code python thủ công vào heredoc/`Bash` tool nữa.
- `color_mapping`: Luôn bỏ tiền tố `#` ở mã HEX (Ví dụ dùng `F4CCCC`, không dùng `#F4CCCC`).
- Cột có Text dài nên để `width` từ 40-50 để tự ngắt dòng wrap_text đẹp nhất.
- Module này **CHỈ** phụ trách chức năng xuất file thuần túy.
- Luôn dùng **openpyxl** — KHÔNG dùng `pandas`, `xlwt`, `xlrd`.

## Best practices
- Nếu không có Sheet tổng hợp, hãy truyền `summary_sheet: null`.
- File output thường lưu tại thư mục `docs/`.
- **Freeze pane** `A3` cho tất cả detail sheets (title + header cố định khi scroll).
- **Auto-filter** trên header row của mọi sheet.
- **Màu phân loại** theo `color_mapping` trong JSON — nhất quán giữa các file.
- Row height tự động — không hardcode.
- Xem `resources/color-palette.md` cho bảng màu đầy đủ.
