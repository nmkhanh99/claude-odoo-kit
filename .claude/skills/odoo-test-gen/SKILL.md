---
name: odoo-test-gen
description: Sinh test cases Odoo tự động từ model/business logic — tạo unit test, integration test, security test đúng chuẩn Odoo 19. Kích hoạt khi user nói "viết test", "sinh test", "tạo test cases", "generate tests", "unit test", "write tests odoo", "test cho model".
---

# Odoo Test Generator

## Goal
Phân tích module/model Odoo → sinh test cases đầy đủ, đúng chuẩn Odoo 19 (setUpClass, tagged, TransactionCase).

**Input**: Đường dẫn module hoặc model cụ thể, loại test cần tạo  
**Output**: File test hoàn chỉnh, sẵn sàng chạy với `./odoo-bin --test-enable`

## When to use this skill
- "viết test cho model X", "tạo unit test cho module Y"
- "tạo security test", "tạo integration test"
- "generate test cases từ BRD"
- Sau khi `scaffold-odoo-code` tạo xong model/workflow

## Instructions

### Bước 1 — Xác định scope và loại test

Hỏi user nếu chưa rõ:

| Loại test | Khi nào dùng | Tag |
|---|---|---|
| Unit test | CRUD operations, computed fields, constraints | `post_install` |
| Integration test | Workflow multi-step, cross-model operations | `post_install` |
| Security test | Access rights, record rules, multi-company | `post_install`, `security` |

### Bước 2 — Đọc model để hiểu structure

Scan model file để lấy:
- `_name`, `_inherit`, fields list
- States/workflow methods
- Constraints (`_sql_constraints`, `@api.constrains`)
- Computed fields và dependencies
- Custom CRUD overrides (`create`, `write`, `unlink`)

### Bước 3 — Sinh test structure

#### Template cơ bản (Odoo 19 chuẩn)

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import AccessError, ValidationError, UserError
from odoo.fields import Command

@tagged('post_install', '-at_install')
class Test{ModelName}(TransactionCase):
    """Test suite cho model {model_name}"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Tắt mail tracking để test nhanh hơn
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Setup data dùng chung cho toàn bộ test class
        cls.company = cls.env.company
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'company_type': 'company',
        })

    def _create_record(self, **kwargs):
        """Helper tạo record với default values"""
        vals = {
            'name': 'Test Record',
            **kwargs,
        }
        return self.env['{model_name}'].create(vals)
```

#### Test CRUD Operations

```python
    def test_create_basic(self):
        """Tạo record với thông tin cơ bản"""
        record = self._create_record(name='Test Basic')
        self.assertTrue(record.id, "Record phải có ID sau khi tạo")
        self.assertEqual(record.name, 'Test Basic')
        self.assertEqual(record.state, 'draft', "State mặc định phải là draft")

    def test_create_required_fields(self):
        """Không thể tạo khi thiếu required fields"""
        with self.assertRaises((ValidationError, Exception)):
            self.env['{model_name}'].create({})  # Thiếu required fields

    def test_write_basic(self):
        """Cập nhật record"""
        record = self._create_record()
        record.write({'name': 'Updated Name'})
        self.assertEqual(record.name, 'Updated Name')

    def test_unlink_basic(self):
        """Xóa record"""
        record = self._create_record()
        record_id = record.id
        record.unlink()
        self.assertFalse(self.env['{model_name}'].browse(record_id).exists())
```

#### Test Computed Fields

```python
    def test_computed_total(self):
        """Kiểm tra computed field tổng tiền"""
        record = self._create_record()
        record.write({
            'line_ids': [
                (0, 0, {'name': 'Line 1', 'amount': 100.0}),
                (0, 0, {'name': 'Line 2', 'amount': 200.0}),
            ]
        })
        self.assertAlmostEqual(record.total_amount, 300.0, places=2)

    def test_computed_recompute(self):
        """Computed field phải tái tính khi dependency thay đổi"""
        record = self._create_record()
        record.write({'line_ids': [(0, 0, {'name': 'L1', 'amount': 100.0})]})
        self.assertAlmostEqual(record.total_amount, 100.0, places=2)

        # Thay đổi dependency → computed phải cập nhật
        record.line_ids[0].amount = 150.0
        self.assertAlmostEqual(record.total_amount, 150.0, places=2)
```

#### Test Workflow/State Machine

```python
    def test_workflow_confirm(self):
        """Workflow: draft → confirmed"""
        record = self._create_record()
        self.assertEqual(record.state, 'draft')

        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')

    def test_workflow_complete(self):
        """Workflow: confirmed → done"""
        record = self._create_record()
        record.action_confirm()
        record.action_done()
        self.assertEqual(record.state, 'done')

    def test_workflow_cancel(self):
        """Workflow: confirmed → cancelled"""
        record = self._create_record()
        record.action_confirm()
        record.action_cancel()
        self.assertEqual(record.state, 'cancelled')

    def test_workflow_invalid_transition(self):
        """Không thể chuyển state không hợp lệ"""
        record = self._create_record()
        record.action_confirm()
        record.action_done()
        # Từ done không thể confirm lại
        with self.assertRaises((UserError, ValidationError)):
            record.action_confirm()
```

#### Test Constraints

```python
    def test_constraint_negative_amount(self):
        """Amount không được âm"""
        with self.assertRaises(ValidationError):
            self._create_record(amount=-100.0)

    def test_constraint_unique_code(self):
        """Code phải unique"""
        self._create_record(code='UNIQUE001')
        with self.assertRaises(Exception):  # IntegrityError hoặc ValidationError
            self._create_record(code='UNIQUE001')

    def test_constraint_date_range(self):
        """Start date phải trước end date"""
        from datetime import date
        with self.assertRaises(ValidationError):
            self._create_record(
                date_start=date(2024, 12, 31),
                date_end=date(2024, 1, 1),
            )
```

#### Template Security Test

```python
@tagged('post_install', '-at_install', 'security')
class Test{ModelName}Security(TransactionCase):
    """Security tests cho model {model_name}"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # ⚠️ ODOO 19: groups_id KHÔNG được set trong res.users.create()
        # Phải tạo user trước, sau đó set groups_id bằng write()
        cls.user_basic = cls.env['res.users'].create({
            'name': 'Basic User',
            'login': 'test_basic_{model_name}',
            'email': 'basic@test.com',
        })
        cls.user_basic.write({
            'groups_id': [Command.set([
                cls.env.ref('{module_name}.group_user').id
            ])]
        })

        cls.user_manager = cls.env['res.users'].create({
            'name': 'Manager User',
            'login': 'test_mgr_{model_name}',
            'email': 'mgr@test.com',
        })
        cls.user_manager.write({
            'groups_id': [Command.set([
                cls.env.ref('{module_name}.group_manager').id
            ])]
        })

    def _create_record(self, user=None):
        env = self.env if not user else self.env.with_user(user)
        return env['{model_name}'].create({'name': 'Test'})

    def test_basic_user_can_read(self):
        """Basic user có quyền đọc"""
        record = self._create_record()
        # Không raise exception
        record_as_user = record.with_user(self.user_basic)
        self.assertEqual(record_as_user.name, 'Test')

    def test_basic_user_cannot_delete(self):
        """Basic user không có quyền xóa"""
        record = self._create_record()
        with self.assertRaises(AccessError):
            record.with_user(self.user_basic).unlink()

    def test_manager_can_delete(self):
        """Manager có quyền xóa"""
        record = self._create_record()
        # Không raise exception
        record.with_user(self.user_manager).unlink()

    def test_multi_company_isolation(self):
        """Record của company khác phải bị ẩn"""
        company_2 = self.env['res.company'].create({'name': 'Company 2'})
        record = self.env['{model_name}'].create({
            'name': 'Company 2 Record',
            'company_id': company_2.id,
        })
        # User thuộc company 1 không thấy record của company 2
        records = self.env['{model_name}'].with_user(self.user_basic).search([])
        self.assertNotIn(record.id, records.ids)
```

#### Template Integration Test

```python
@tagged('post_install', '-at_install')
class Test{ModelName}Integration(TransactionCase):
    """Integration tests — luồng nghiệp vụ đầu cuối"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    def test_full_workflow(self):
        """Test toàn bộ vòng đời record: tạo → confirm → done"""
        # Tạo
        record = self.env['{model_name}'].create({
            'name': 'Full Workflow Test',
            'partner_id': self.env['res.partner'].create({'name': 'P'}).id,
            'line_ids': [(0, 0, {'name': 'L1', 'amount': 500.0})],
        })
        self.assertEqual(record.state, 'draft')
        self.assertAlmostEqual(record.total_amount, 500.0)

        # Confirm
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')

        # Done
        record.action_done()
        self.assertEqual(record.state, 'done')

        # Verify related records updated
        # [Thêm assertions cho side effects]
```

### Bước 4 — Tạo `tests/__init__.py`

```python
# -*- coding: utf-8 -*-
from . import test_{model_name}
from . import test_{model_name}_security
```

### Bước 5 — Xuất files và hướng dẫn chạy

```
✅ Files sinh ra:
   tests/__init__.py
   tests/test_{model_name}.py          (unit + integration)
   tests/test_{model_name}_security.py (security)

📋 Cách chạy:
   # Chạy tất cả tests của module
   ./odoo-bin -d testdb --test-enable -i {module_name} --stop-after-init

   # Chạy theo test class
   ./odoo-bin -d testdb --test-enable --test-tags=Test{ModelName}

   # Chạy chỉ security tests
   ./odoo-bin -d testdb --test-enable --test-tags=security

⚠️  Lưu ý:
   - Dùng database riêng cho test (testdb)
   - setUpClass() chạy một lần per class → nhanh hơn setUp()
   - tracking_disable=True → tắt mail tracking → test nhanh hơn 3-5x
```

## Constraints
- **KHÔNG** dùng `setUp()` thay `setUpClass()` nếu không cần reset state
- Test users: login phải unique, thêm `{model_name}` suffix
- **PHẢI** dùng `@tagged('post_install', '-at_install')`
- **KHÔNG** hardcode IDs trong test
- Test phải độc lập — không phụ thuộc thứ tự chạy

## Best practices
- Đặt tên test method rõ ràng: `test_[kịch bản]_[kết quả mong đợi]`
- 1 test = 1 kịch bản — dễ debug khi fail
- Dùng helper methods (`_create_record`) để tránh duplicate setup code
- Security tests: luôn test cả "được phép" và "không được phép"
- Workflow tests: test cả happy path và error cases
- Với `assertRaises`: specify exception type cụ thể (`ValidationError`, `AccessError`, `UserError`)
