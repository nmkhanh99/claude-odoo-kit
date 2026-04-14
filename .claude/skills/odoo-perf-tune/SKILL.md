---
name: odoo-perf-tune
description: Tối ưu hiệu năng module Odoo — phát hiện N+1 query, thiếu index, batch operation, memory issue và đề xuất fix cụ thể. Kích hoạt khi user nói "chậm", "slow", "timeout", "tối ưu", "performance", "N+1", "query nhiều", "memory", "tối ưu ORM", "batch", "cron chậm".
---

# Odoo Performance Tuning

## Goal
Phân tích code Odoo → phát hiện bottleneck hiệu năng → đề xuất fix cụ thể với code example sẵn sàng áp dụng.

**Input**: Code cần review hoặc mô tả vấn đề hiệu năng  
**Output**: Danh sách issues + fix code + checklist tối ưu

## When to use this skill
- "slow page load", "timeout", "server lag", "trang chạy chậm"
- "tối ưu query", "N+1 problem", "too many SQL queries"
- "memory error", "server crash", "cron job chậm"
- "tối ưu computed field", "batch processing"
- Review code trước khi deploy production

## Instructions

### Bước 1 — Xác định loại vấn đề hiệu năng

| Triệu chứng | Nguyên nhân thường gặp | Ưu tiên fix |
|---|---|---|
| Page load chậm | N+1 queries, thiếu prefetch | CRITICAL |
| Timeout khi search | Thiếu index, domain phức tạp | HIGH |
| Cron job treo | Không batch, không clear cache | HIGH |
| Memory error | Load quá nhiều records | HIGH |
| Computed field chậm | Query trong vòng lặp | MEDIUM |
| View kanban lag | Non-stored computed fields | MEDIUM |

### Bước 2 — Fix patterns theo từng loại

#### N+1 Query Problem

```python
# ❌ SAI — 1 query lấy orders + N queries lấy partner
for order in orders:
    print(order.partner_id.name)

# ✅ ĐÚNG — prefetch trước
orders.mapped('partner_id')  # 1 query lấy tất cả partners
for order in orders:
    print(order.partner_id.name)  # Không có thêm query

# ✅ TỐT NHẤT — dùng search_read khi chỉ cần 1 số field
data = self.env['sale.order'].search_read(
    [('state', '=', 'sale')],
    ['name', 'partner_id', 'amount_total'],
    limit=100,
)
```

#### Batch Operations

```python
# ❌ SAI — tạo từng record riêng lẻ
for data in data_list:
    self.env['my.model'].create(data)  # N queries

# ✅ ĐÚNG — batch create (v15+)
self.env['my.model'].create(data_list)  # 1 query

# ❌ SAI — write từng record
for record in records:
    record.write({'state': 'done'})  # N queries

# ✅ ĐÚNG — batch write
records.write({'state': 'done'})  # 1 query

# ❌ SAI — unlink từng record
for record in records:
    record.unlink()

# ✅ ĐÚNG
records.unlink()
```

#### Efficient Searching

```python
# ❌ SAI — search rồi count
count = len(self.env['my.model'].search([('state', '=', 'draft')]))

# ✅ ĐÚNG
count = self.env['my.model'].search_count([('state', '=', 'draft')])

# ❌ SAI — load all rồi filter Python
records = self.env['my.model'].search([])
draft_records = [r for r in records if r.state == 'draft']

# ✅ ĐÚNG — filter trong domain
draft_records = self.env['my.model'].search([('state', '=', 'draft')])

# ❌ SAI — 2 queries riêng
partners = self.env['res.partner'].search([('customer_rank', '>', 0)])
orders = self.env['sale.order'].search([('partner_id', 'in', partners.ids)])

# ✅ ĐÚNG — join trong 1 domain
orders = self.env['sale.order'].search([('partner_id.customer_rank', '>', 0)])
```

#### Field Indexing

```python
# Index cho fields thường dùng trong search/filter
state = fields.Selection([...], index=True)          # B-tree index
company_id = fields.Many2one('res.company', index=True)
date = fields.Date(index=True)

# Trigram index cho ILIKE search (v16+)
name = fields.Char(index='trigram')

# Index không NULL (v16+)
code = fields.Char(index='btree_not_null')
```

**Khi nào nên index:**

| Loại field | Khi nào index |
|---|---|
| Selection | Dùng trong filter/domain thường xuyên |
| Many2one | Dùng trong search hoặc record rules |
| Date/Datetime | Dùng trong date range queries |
| Char | Dùng với `=` operator |
| Char (pattern search) | Dùng `index='trigram'` cho ILIKE |

#### Computed Fields — Stored vs Non-Stored

```python
# STORED — tính 1 lần, cập nhật khi dependency thay đổi
# Dùng khi: đọc thường xuyên, ít thay đổi
total = fields.Float(compute='_compute_total', store=True)

@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))

# NON-STORED — tính mỗi lần đọc
# Dùng khi: thay đổi liên tục, ít khi hiển thị
days_left = fields.Integer(compute='_compute_days_left')

def _compute_days_left(self):
    today = fields.Date.today()
    for record in self:
        if record.deadline:
            record.days_left = (record.deadline - today).days
        else:
            record.days_left = 0
```

#### Computed Field — Tối ưu với read_group

```python
# ❌ SAI — query riêng cho từng record
@api.depends('partner_id')
def _compute_order_count(self):
    for record in self:
        record.order_count = self.env['sale.order'].search_count([
            ('partner_id', '=', record.partner_id.id)
        ])

# ✅ ĐÚNG — batch với read_group
@api.depends('partner_id')
def _compute_order_count(self):
    if not self:
        return
    partner_ids = self.mapped('partner_id').ids
    order_data = self.env['sale.order']._read_group(
        [('partner_id', 'in', partner_ids)],
        groupby=['partner_id'],
        aggregates=['__count'],
    )
    counts = {partner.id: count for partner, count in order_data}
    for record in self:
        record.order_count = counts.get(record.partner_id.id, 0)
```

#### SQL Tối ưu (Bulk Operations)

```python
# Dùng SQL khi cần update/delete hàng loạt
from odoo.tools import SQL

# Bulk update
self.env.cr.execute(SQL(
    """
    UPDATE my_model
    SET state = %s, write_date = NOW()
    WHERE state = %s AND company_id = %s
    """,
    'done', 'confirmed', self.env.company.id
))

# Sau SQL, invalidate ORM cache
self.browse(updated_ids).invalidate_recordset()
# Hoặc toàn bộ model
self.invalidate_model()

# Aggregation với SQL (thay vì load records)
self.env.cr.execute(SQL(
    """
    SELECT partner_id, COUNT(*) as cnt, SUM(amount_total) as total
    FROM sale_order
    WHERE state = %s AND company_id = %s
    GROUP BY partner_id
    """,
    'sale', self.env.company.id
))
results = self.env.cr.dictfetchall()
```

#### Prefetch Optimization

```python
def process_orders(self, orders):
    # Prefetch tất cả related data trước
    orders.mapped('partner_id')
    orders.mapped('order_line_ids')
    orders.mapped('order_line_ids.product_id')

    # Xử lý không có thêm query
    for order in orders:
        for line in order.order_line_ids:
            print(line.product_id.name)
```

#### ORM Tips

```python
# filtered() — in-memory, không phải DB query
# Tốt cho recordset nhỏ đã load
confirmed = orders.filtered(lambda o: o.state == 'sale')

# Với dataset lớn → dùng search()
confirmed = self.env['sale.order'].search([
    ('id', 'in', orders.ids),
    ('state', '=', 'sale'),
])

# mapped() — hiệu quả
partner_ids = orders.mapped('partner_id').ids
total = sum(orders.mapped('amount_total'))

# Tránh lặp env access
# ❌ SAI
for partner_id in partner_ids:
    partner = self.env['res.partner'].browse(partner_id)

# ✅ ĐÚNG
partners = self.env['res.partner'].browse(partner_ids)
```

#### Cron Job Optimization

```python
@api.model
def _cron_process_large_dataset(self) -> None:
    """Xử lý records theo batch, tránh memory issue (v19: cần return type)"""
    batch_size = 1000
    offset = 0

    while True:
        records = self.search(
            [('state', '=', 'pending')],
            limit=batch_size,
            offset=offset,
        )
        if not records:
            break

        for record in records:
            try:
                record._process_single()
            except Exception as e:
                _logger.error("Lỗi xử lý %s: %s", record.id, e)

        # Commit và clear cache sau mỗi batch
        self.env.cr.commit()
        self.env.invalidate_all()
        offset += batch_size
```

#### Memory Optimization

```python
# Generator pattern cho dataset lớn
def _iter_records(self, domain, batch_size=1000):
    offset = 0
    while True:
        records = self.search(domain, limit=batch_size, offset=offset)
        if not records:
            break
        yield from records
        offset += batch_size

# Dùng
for record in self._iter_records([('state', '=', 'pending')]):
    process(record)

# Clear cache định kỳ trong long operation
def process_many_records(self):
    count = 0
    for record in self:
        record._do_processing()
        count += 1
        if count % 500 == 0:
            self.env.invalidate_all()
```

### Bước 3 — Performance Monitoring

**Enable SQL logging:**
```ini
# odoo.conf
log_level = debug_sql
```

**Query count trong tests:**
```python
from odoo.tests.common import QueryCounter
with QueryCounter(self.env.cr) as qc:
    # Code cần test
    self.env['sale.order'].search([('state', '=', 'sale')])
print(f"Số queries: {qc.count}")
```

**Timing trong code:**
```python
import logging
import time

_logger = logging.getLogger(__name__)

def _performance_critical_method(self):
    start = time.time()
    # Code...
    elapsed = time.time() - start
    _logger.info("Method hoàn thành trong %.2f giây", elapsed)
    if elapsed > 5.0:
        _logger.warning("Slow operation: %.2f giây", elapsed)
```

**Odoo Profiler:**
```python
from odoo.tools.profiler import profile

@profile
def slow_method(self):
    # Log timing và query count tự động
    pass
```

### Bước 4 — Xuất báo cáo

```
⚡ PERFORMANCE ANALYSIS

Module : [tên module]
Issues : [số lượng] vấn đề phát hiện

── CRITICAL (ảnh hưởng nghiêm trọng) ───────────────

[PERF-001] models/my_model.py:45
  Vấn đề : N+1 query trong vòng lặp
  Tác động: ~N queries thay vì 1
  Fix     : [code fix]

── HIGH (nên fix sớm) ───────────────────────────────

[PERF-002] models/my_model.py:78
  Vấn đề : Thiếu index trên field state
  Tác động: Full table scan mỗi lần search
  Fix     : state = fields.Selection([...], index=True)

── CHECKLIST TỐI ƯU ─────────────────────────────────

□ Index tất cả fields dùng trong search domain
□ Stored computed fields cho values thường đọc
□ Batch operations (@api.model_create_multi)
□ Không có N+1 trong computed fields
□ Dùng search_count() thay len(search())
□ Prefetch related records trước loops
□ Cron job xử lý theo batch (1000/lần)
□ Clear cache trong long-running operations
```

## Constraints
- **KHÔNG** tự sửa code khi chưa được user xác nhận
- **KHÔNG** suggest raw SQL trừ khi ORM không đáp ứng được (bulk ops, phức tạp)
- Với Odoo 19: raw SQL **bắt buộc** dùng `SQL()` builder

## Best practices
- Enable `debug_sql` để đếm queries thực tế trước khi tối ưu
- Tối ưu theo thứ tự: N+1 → index → batch → SQL
- Stored computed field: tốt cho đọc, tệ cho write-heavy workloads
- Cron job: luôn batch + commit + invalidate_all
- Test performance với production-size data, không phải demo data
