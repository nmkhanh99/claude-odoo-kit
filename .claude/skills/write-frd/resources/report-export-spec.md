# Report & Excel Export Spec

## Bắt buộc cho mỗi report/export

Mỗi report export (Excel, PDF) phải có đủ các phần sau:

### 1. Worksheet & Filename
- **Worksheet name:** [tên tab trong Excel]
- **Filename format:** `[prefix]_YYYYMMDD_HHMMSS.xlsx`

### 2. Column Table
| STT | Header Text | Column Width | Data Source (field/formula) |
|-----|------------|-------------|---------------------------|
| 1 | | | |

### 3. Header Layout
- **Số header rows:** [N]
- **Merge ranges:** [ví dụ: A1:D1, E1:G1]
- **Multi-level structure:** [mô tả nếu có]

### 4. Data Row Pattern
- **Pattern:** 1-row-per-record / multi-row
- **Min rows:** [N rows tối thiểu]

### 5. Footer Layout
- **Footer sections:** [nội dung từng phần footer]

### 6. Helper Methods (Python code)
```python
def _get_report_data(self, domain=None):
    """Query data cho report"""
    domain = domain or []
    records = self.env['model.name'].search(domain)
    return records

def _compute_report_value(self, record):
    """Compute formula cho một ô"""
    return ...
```

### 7. Stage/Filter
- **Stage name hoặc domain:** `[('state', 'in', ['confirmed', 'done'])]`
