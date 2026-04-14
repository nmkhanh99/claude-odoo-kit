---
name: odoo-workflow
description: Thiết kế workflow và state machine Odoo — state transitions, multi-level approval, kanban stages, scheduled state changes. Kích hoạt khi user nói "workflow", "state machine", "luồng phê duyệt", "approval workflow", "trạng thái", "state transitions", "multi-level approval", "kanban stage".
---

# Odoo Workflow & State Machine Patterns

## Goal
Thiết kế và implement workflow với state machine cho module Odoo 19 — simple state, approval flow, stage-based Kanban, scheduled transitions.

**Input**: Mô tả luồng nghiệp vụ, các state và transition cần thiết  
**Output**: Code Python + View XML đầy đủ cho workflow

## When to use this skill
- "tạo workflow phê duyệt", "multi-level approval"
- "state machine", "luồng trạng thái"
- "kanban với stages", "task workflow"
- "cron job tự động chuyển state"

## Instructions

### Bước 1 — Basic State Machine

```python
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MyDocument(models.Model):
    _name = 'my.document'
    _description = 'My Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name: str = fields.Char(required=True, tracking=True)
    state: str = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', required=True,
       tracking=True, copy=False, index=True)

    # Transition methods — v19: type hints bắt buộc
    def action_confirm(self) -> None:
        """Draft → Confirmed."""
        for record in self:
            if record.state != 'draft':
                raise UserError(_("Only draft documents can be confirmed."))
        self.write({'state': 'confirmed'})

    def action_done(self) -> None:
        """Confirmed → Done."""
        for record in self:
            if record.state != 'confirmed':
                raise UserError(_("Only confirmed documents can be marked done."))
        self.write({'state': 'done'})

    def action_cancel(self) -> None:
        """Cancel (không được cancel khi đã Done)."""
        if any(r.state == 'done' for r in self):
            raise UserError(_("Cannot cancel completed documents."))
        self.write({'state': 'cancel'})

    def action_draft(self) -> None:
        """Cancel → Draft."""
        for record in self:
            if record.state != 'cancel':
                raise UserError(_("Only cancelled documents can be reset to draft."))
        self.write({'state': 'draft'})
```

**View với Statusbar (v17+ syntax):**
```xml
<form>
    <header>
        <button name="action_confirm" string="Confirm"
                type="object" class="btn-primary"
                invisible="state != 'draft'"/>
        <button name="action_done" string="Mark Done"
                type="object" class="btn-primary"
                invisible="state != 'confirmed'"/>
        <button name="action_cancel" string="Cancel"
                type="object"
                invisible="state in ('done', 'cancel')"/>
        <button name="action_draft" string="Reset to Draft"
                type="object"
                invisible="state != 'cancel'"/>
        <field name="state" widget="statusbar"
               statusbar_visible="draft,confirmed,done"/>
    </header>
    <sheet>
        <group>
            <!-- readonly dựa trên state — v17+ syntax -->
            <field name="name" readonly="state != 'draft'"/>
            <field name="partner_id" readonly="state != 'draft'"/>
        </group>
    </sheet>
</form>
```

### Bước 2 — Transition Validation Matrix

```python
class StateMachine(models.Model):
    _name = 'state.machine'
    _description = 'State Machine with Validation'

    # Map các transition hợp lệ
    TRANSITIONS: dict[str, list[str]] = {
        'draft': ['submitted', 'cancel'],
        'submitted': ['approved', 'rejected', 'cancel'],
        'approved': ['done', 'cancel'],
        'rejected': ['draft'],
        'done': [],        # Terminal state
        'cancel': ['draft'],
    }

    state: str = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], default='draft', tracking=True, index=True)

    def _transition_to(self, new_state: str) -> None:
        """Transition an toàn — validate trước khi chuyển."""
        for record in self:
            allowed = self.TRANSITIONS.get(record.state, [])
            if new_state not in allowed:
                raise UserError(_(
                    "Cannot transition from '%(from)s' to '%(to)s'. "
                    "Allowed: %(allowed)s",
                    from_=record.state,
                    to=new_state,
                    allowed=', '.join(allowed) or 'none',
                ))
            record.state = new_state

    def action_submit(self) -> None:
        self._transition_to('submitted')

    def action_approve(self) -> None:
        self._transition_to('approved')

    def action_reject(self) -> None:
        self._transition_to('rejected')

    def action_done(self) -> None:
        self._transition_to('done')

    def action_cancel(self) -> None:
        self._transition_to('cancel')

    def action_draft(self) -> None:
        self._transition_to('draft')
```

### Bước 3 — Multi-Level Approval Workflow

```python
class ApprovalDocument(models.Model):
    _name = 'approval.document'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name: str = fields.Char(required=True, tracking=True)
    amount: float = fields.Float(string='Amount')
    state: str = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('first_approval', 'First Approval'),
        ('second_approval', 'Second Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='draft', tracking=True, index=True)

    # Approval tracking
    submitted_by: int = fields.Many2one('res.users', readonly=True, copy=False)
    submitted_date: fields.Datetime = fields.Datetime(readonly=True, copy=False)
    first_approver_id: int = fields.Many2one('res.users', readonly=True, copy=False)
    first_approval_date: fields.Datetime = fields.Datetime(readonly=True, copy=False)
    second_approver_id: int = fields.Many2one('res.users', readonly=True, copy=False)
    second_approval_date: fields.Datetime = fields.Datetime(readonly=True, copy=False)
    rejection_reason: str = fields.Text(copy=False)

    # Thresholds
    MANAGER_LIMIT = 10000
    DIRECTOR_LIMIT = 50000

    def action_submit(self) -> None:
        """Submit for approval."""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Document must be in draft state."))
        self.write({
            'state': 'submitted',
            'submitted_by': self.env.uid,
            'submitted_date': fields.Datetime.now(),
        })
        self._notify_approvers()

    def action_first_approve(self) -> None:
        """First level approval."""
        self.ensure_one()
        if not self.env.user.has_group('my_module.group_first_approver'):
            from odoo.exceptions import AccessError
            raise AccessError(_("You don't have first approval rights."))
        self.write({
            'state': 'first_approval',
            'first_approver_id': self.env.uid,
            'first_approval_date': fields.Datetime.now(),
        })
        # Chuyển thẳng hoặc lên cấp 2
        if self.amount <= self.DIRECTOR_LIMIT:
            self._final_approve()
        else:
            self._notify_second_approvers()

    def action_second_approve(self) -> None:
        """Second level approval."""
        self.ensure_one()
        if not self.env.user.has_group('my_module.group_second_approver'):
            from odoo.exceptions import AccessError
            raise AccessError(_("You don't have second approval rights."))
        self.write({
            'state': 'second_approval',
            'second_approver_id': self.env.uid,
            'second_approval_date': fields.Datetime.now(),
        })
        self._final_approve()

    def _final_approve(self) -> None:
        self.write({'state': 'approved'})

    def action_reject(self) -> None:
        """Reject với lý do bắt buộc."""
        self.ensure_one()
        if not self.rejection_reason:
            raise UserError(_("Please provide a rejection reason."))
        self.write({'state': 'rejected'})
        self._notify_rejection()

    def _notify_approvers(self) -> None:
        """Notify approvers qua activity."""
        approvers = self.env.ref('my_module.group_first_approver').users
        for approver in approvers:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=approver.id,
                summary=_('Approval Required: %s', self.name),
                note=_('Please review and approve this document.'),
            )

    def _notify_second_approvers(self) -> None:
        approvers = self.env.ref('my_module.group_second_approver').users
        for approver in approvers:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=approver.id,
                summary=_('Final Approval Required: %s', self.name),
            )

    def _notify_rejection(self) -> None:
        if self.submitted_by:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=self.submitted_by.id,
                summary=_('Document Rejected: %s', self.name),
            )
```

**View cho Approval:**
```xml
<form>
    <header>
        <button name="action_submit" string="Submit for Approval"
                type="object" class="btn-primary"
                invisible="state != 'draft'"/>
        <button name="action_first_approve" string="Approve"
                type="object" class="btn-primary"
                invisible="state != 'submitted'"
                groups="my_module.group_first_approver"/>
        <button name="action_second_approve" string="Final Approve"
                type="object" class="btn-primary"
                invisible="state != 'first_approval'"
                groups="my_module.group_second_approver"/>
        <button name="action_reject" string="Reject"
                type="object"
                invisible="state not in ('submitted', 'first_approval')"/>
        <field name="state" widget="statusbar"
               statusbar_visible="draft,submitted,first_approval,approved"/>
    </header>
    <sheet>
        <group>
            <group>
                <field name="name" readonly="state != 'draft'"/>
                <field name="amount" readonly="state != 'draft'"/>
            </group>
            <group>
                <field name="submitted_by" invisible="not submitted_by"/>
                <field name="first_approver_id" invisible="not first_approver_id"/>
                <field name="second_approver_id" invisible="not second_approver_id"/>
            </group>
        </group>
        <group string="Rejection" invisible="state != 'rejected'">
            <field name="rejection_reason"/>
        </group>
    </sheet>
    <div class="oe_chatter">
        <field name="message_follower_ids"/>
        <field name="activity_ids"/>
        <field name="message_ids"/>
    </div>
</form>
```

### Bước 4 — Kanban Stage-Based Workflow

```python
class TaskStage(models.Model):
    _name = 'my.task.stage'
    _description = 'Task Stage'
    _order = 'sequence, id'

    name: str = fields.Char(required=True)
    sequence: int = fields.Integer(default=10)
    fold: bool = fields.Boolean(string='Folded in Kanban')
    state: str = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ], default='draft')
    is_closed: bool = fields.Boolean(string='Closing Stage')


class MyTask(models.Model):
    _name = 'my.task'
    _description = 'Task'

    name: str = fields.Char(required=True)
    stage_id: int = fields.Many2one(
        'my.task.stage',
        string='Stage',
        group_expand='_read_group_stage_ids',
        tracking=True,
        default=lambda self: self._get_default_stage(),
    )
    # State từ stage (stored cho performance)
    state: str = fields.Selection(related='stage_id.state', store=True, index=True)

    def _get_default_stage(self) -> 'TaskStage':
        return self.env['my.task.stage'].search([], limit=1)

    @api.model
    def _read_group_stage_ids(
        self,
        stages: 'TaskStage',
        domain: list,
        order: str,
    ) -> 'TaskStage':
        """Luôn hiển thị tất cả stages trong kanban."""
        return stages.search([])
```

### Bước 5 — Scheduled State Transitions

```python
class AutoCloseDocument(models.Model):
    _name = 'auto.close.document'
    _description = 'Auto Close Document'

    state: str = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
    ], default='active', index=True)
    expiry_date: fields.Date = fields.Date(index=True)

    @api.model
    def _cron_check_expiry(self) -> None:
        """Cron job tự động expire documents.
        
        Chạy hàng ngày — batch xử lý an toàn.
        """
        batch_size = 1000
        offset = 0

        while True:
            expired = self.search([
                ('state', '=', 'active'),
                ('expiry_date', '<', fields.Date.today()),
            ], limit=batch_size, offset=offset)

            if not expired:
                break

            expired.write({'state': 'expired'})
            for doc in expired:
                doc._notify_expiry()

            # Commit và clear cache sau mỗi batch
            self.env.cr.commit()
            self.env.invalidate_all()
            offset += batch_size
```

**Cron XML:**
```xml
<record id="ir_cron_check_document_expiry" model="ir.cron">
    <field name="name">Check Document Expiry</field>
    <field name="model_id" ref="model_auto_close_document"/>
    <field name="state">code</field>
    <field name="code">model._cron_check_expiry()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
    <field name="active" eval="True"/>
</record>
```

### Bước 6 — State Change Tracking

```python
class TrackedDocument(models.Model):
    _name = 'tracked.document'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state: str = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True)  # tracking=True log tự động

    def action_confirm(self) -> None:
        for record in self:
            record.write({'state': 'confirmed'})
            # Custom message nếu cần
            record.message_post(
                body=_("Document confirmed by %s.", self.env.user.name),
                subtype_xmlid='mail.mt_note',
            )
```

### Bước 7 — Workflow Checklist

```
□ state field có tracking=True và index=True
□ Mỗi transition method kiểm tra current state trước khi chuyển
□ Không cho xóa records không phải draft
□ Statusbar visible chỉ các states chính (không phải states phụ)
□ Buttons có invisible= phù hợp (không thấy khi không thể thực hiện)
□ Approval buttons có groups= restriction
□ Cron job: batch + commit + invalidate_all
□ Notify bằng activity hoặc message_post khi có action quan trọng
```

## Constraints
- **KHÔNG** thay đổi state trực tiếp mà không validate
- **PHẢI** check quyền trước khi thực hiện approval actions
- Cron jobs **bắt buộc** batch processing (tránh memory issue)
- **KHÔNG** dùng `@api.multi` (removed trong v15+)

## Best practices
- Dùng Selection state (không phải Many2one) cho state đơn giản
- Stage-based (Many2one) cho Kanban workflow phức tạp
- tracking=True + mail.thread để có chatter history đầy đủ
- TRANSITIONS dict pattern giúp validate và document rõ ràng
- Activity scheduling thay vì email trực tiếp để user quản lý tốt hơn
