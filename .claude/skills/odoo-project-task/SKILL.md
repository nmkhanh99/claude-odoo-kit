---
name: odoo-project-task
description: Mở rộng Project/Task Odoo 19 — thêm field custom, stage-based workflow, task dependencies, checklist, automation theo stage, cron overdue alerts. Kích hoạt khi user nói "mở rộng project", "thêm field task", "task dependencies", "checklist task", "stage task", "project workflow", "overdue task".
---

# Project & Task Patterns (Odoo 19)

## Goal
Mở rộng module Project/Task Odoo 19 — custom fields, stages, dependencies, checklist, auto-assignment, notifications, scheduled alerts.

**Input**: Mô tả nhu cầu mở rộng project/task  
**Output**: Python models + View XML đầy đủ

## When to use this skill
- "thêm field tùy chỉnh vào project/task"
- "tạo stage workflow cho task"
- "task dependencies (phụ thuộc)"
- "checklist cho task"
- "tự động assign reviewer"
- "cảnh báo task quá hạn"

## Instructions

### Bước 1 — Manifest dependencies

```python
# __manifest__.py
{
    'name': 'My Project Module',
    'version': '19.0.1.0.0',
    'depends': [
        'project',          # Core bắt buộc
        # 'hr_timesheet',   # Nếu cần timesheet
        # 'sale_project',   # Nếu link với sale order
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_views.xml',
        'views/task_views.xml',
    ],
}
```

### Bước 2 — Mở rộng Project

```python
# -*- coding: utf-8 -*-
from __future__ import annotations

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProjectProject(models.Model):
    _inherit = 'project.project'

    x_project_code: str = fields.Char(string='Project Code')
    x_project_type: str = fields.Selection([
        ('internal', 'Internal'),
        ('client', 'Client'),
        ('rd', 'R&D'),
    ], string='Project Type', default='client')
    x_budget: float = fields.Monetary(
        string='Budget',
        currency_field='x_currency_id',
    )
    x_currency_id: int = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    x_start_date: fields.Date = fields.Date(string='Start Date')
    x_end_date: fields.Date = fields.Date(string='End Date')
    x_department_id: int = fields.Many2one('hr.department', string='Department')
    x_project_manager_id: int = fields.Many2one(
        'res.users',
        string='Project Manager',
        default=lambda self: self.env.user,
    )

    # Computed fields
    x_progress: float = fields.Float(
        string='Progress %',
        compute='_compute_progress',
        store=True,
    )
    x_total_hours: float = fields.Float(
        string='Total Hours',
        compute='_compute_hours',
    )
    x_remaining_budget: float = fields.Monetary(
        string='Remaining Budget',
        compute='_compute_remaining_budget',
        currency_field='x_currency_id',
    )

    @api.depends('task_ids.stage_id', 'task_ids.x_progress')
    def _compute_progress(self) -> None:
        for project in self:
            tasks = project.task_ids.filtered(lambda t: t.active)
            if tasks:
                project.x_progress = sum(tasks.mapped('x_progress')) / len(tasks)
            else:
                project.x_progress = 0.0

    def _compute_hours(self) -> None:
        for project in self:
            project.x_total_hours = sum(
                project.task_ids.mapped('effective_hours')
            )

    def _compute_remaining_budget(self) -> None:
        for project in self:
            spent = sum(project.task_ids.mapped('x_cost'))
            project.x_remaining_budget = project.x_budget - spent
```

### Bước 3 — Project Stages (Kanban)

```python
class ProjectProjectStage(models.Model):
    _name = 'project.project.stage'
    _description = 'Project Stage'
    _order = 'sequence, id'

    name: str = fields.Char(string='Stage Name', required=True)
    sequence: int = fields.Integer(default=10)
    fold: bool = fields.Boolean(string='Folded in Kanban')
    description: str = fields.Text(string='Description')


class ProjectProject(models.Model):
    _inherit = 'project.project'

    x_stage_id: int = fields.Many2one(
        'project.project.stage',
        string='Stage',
        tracking=True,
        group_expand='_read_group_stage_ids',
    )

    @api.model
    def _read_group_stage_ids(
        self,
        stages: 'project.project.stage',
        domain: list,
        order: str,
    ) -> 'project.project.stage':
        """Hiển thị tất cả stages trong kanban."""
        return stages.search([], order=order)
```

### Bước 4 — Mở rộng Task với custom fields

```python
class ProjectTask(models.Model):
    _inherit = 'project.task'

    x_task_type: str = fields.Selection([
        ('feature', 'Feature'),
        ('bug', 'Bug Fix'),
        ('improvement', 'Improvement'),
        ('support', 'Support'),
    ], string='Task Type', default='feature')

    x_priority_level: str = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Critical'),
    ], string='Priority Level', default='1')

    x_estimated_hours: float = fields.Float(string='Estimated Hours')
    x_reviewer_id: int = fields.Many2one('res.users', string='Reviewer')
    x_currency_id: int = fields.Many2one(
        related='project_id.x_currency_id',
    )

    x_progress: float = fields.Float(
        string='Progress %',
        compute='_compute_progress',
        store=True,
    )
    x_cost: float = fields.Monetary(
        string='Cost',
        compute='_compute_cost',
        currency_field='x_currency_id',
    )
    x_due_warning: bool = fields.Boolean(
        string='Due Warning',
        compute='_compute_due_warning',
    )

    @api.depends('effective_hours', 'x_estimated_hours')
    def _compute_progress(self) -> None:
        for task in self:
            if task.x_estimated_hours:
                progress = (task.effective_hours / task.x_estimated_hours) * 100
                task.x_progress = min(progress, 100)
            else:
                task.x_progress = 0.0

    def _compute_cost(self) -> None:
        for task in self:
            cost = sum(
                ts.unit_amount * ts.employee_id.hourly_cost
                for ts in task.timesheet_ids
            )
            task.x_cost = cost

    @api.depends('date_deadline')
    def _compute_due_warning(self) -> None:
        today = fields.Date.today()
        warning_days = 3
        for task in self:
            if task.date_deadline:
                days_until = (task.date_deadline - today).days
                task.x_due_warning = 0 <= days_until <= warning_days
            else:
                task.x_due_warning = False
```

### Bước 5 — Task Dependencies

```python
class ProjectTask(models.Model):
    _inherit = 'project.task'

    x_depends_on_ids: list = fields.Many2many(
        'project.task',
        'project_task_dependency_rel',
        'task_id',
        'depends_on_id',
        string='Depends On',
    )
    x_blocking_ids: list = fields.Many2many(
        'project.task',
        'project_task_dependency_rel',
        'depends_on_id',
        'task_id',
        string='Blocking',
    )
    x_is_blocked: bool = fields.Boolean(
        string='Is Blocked',
        compute='_compute_is_blocked',
    )

    @api.depends('x_depends_on_ids.stage_id')
    def _compute_is_blocked(self) -> None:
        """Task bị block nếu có dependency chưa xong."""
        done_stages = self.env['project.task.type'].search([
            ('fold', '=', True),
        ])
        for task in self:
            blocking = task.x_depends_on_ids.filtered(
                lambda t: t.stage_id not in done_stages
            )
            task.x_is_blocked = bool(blocking)

    @api.constrains('x_depends_on_ids')
    def _check_circular_dependency(self) -> None:
        """Kiểm tra circular dependency."""
        for task in self:
            if task in task._get_all_dependencies():
                raise ValidationError(
                    _("Circular dependency detected!")
                )

    def _get_all_dependencies(
        self,
        visited: set[int] | None = None,
    ) -> 'project.task':
        """Đệ quy lấy tất cả dependencies."""
        if visited is None:
            visited = set()
        dependencies = self.env['project.task']
        for dep in self.x_depends_on_ids:
            if dep.id not in visited:
                visited.add(dep.id)
                dependencies |= dep
                dependencies |= dep._get_all_dependencies(visited)
        return dependencies
```

### Bước 6 — Task Checklist

```python
class ProjectTaskChecklist(models.Model):
    _name = 'project.task.checklist'
    _description = 'Task Checklist Item'
    _order = 'sequence, id'

    task_id: int = fields.Many2one(
        'project.task',
        string='Task',
        required=True,
        ondelete='cascade',
    )
    name: str = fields.Char(string='Item', required=True)
    sequence: int = fields.Integer(default=10)
    is_done: bool = fields.Boolean(string='Done')
    done_date: fields.Datetime = fields.Datetime(string='Done Date')
    done_by: int = fields.Many2one('res.users', string='Done By')

    def action_toggle_done(self) -> None:
        """Toggle trạng thái done của checklist item."""
        for item in self:
            if item.is_done:
                item.write({
                    'is_done': False,
                    'done_date': False,
                    'done_by': False,
                })
            else:
                item.write({
                    'is_done': True,
                    'done_date': fields.Datetime.now(),
                    'done_by': self.env.uid,
                })


class ProjectTaskWithChecklist(models.Model):
    _inherit = 'project.task'

    x_checklist_ids: list = fields.One2many(
        'project.task.checklist',
        'task_id',
        string='Checklist',
    )
    x_checklist_progress: float = fields.Float(
        string='Checklist Progress',
        compute='_compute_checklist_progress',
    )

    @api.depends('x_checklist_ids.is_done')
    def _compute_checklist_progress(self) -> None:
        for task in self:
            total = len(task.x_checklist_ids)
            done = len(task.x_checklist_ids.filtered('is_done'))
            task.x_checklist_progress = (done / total * 100) if total else 0
```

### Bước 7 — Task Automation (Auto-assign + Stage Notifications)

```python
class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model_create_multi
    def create(self, vals_list: list[dict]) -> 'project.task':
        """Auto-assign khi tạo task không có assignee."""
        tasks = super().create(vals_list)
        for task in tasks:
            if not task.user_ids and task.project_id.x_project_manager_id:
                task.user_ids = task.project_id.x_project_manager_id
        return tasks

    def write(self, vals: dict) -> bool:
        """Notify khi task chuyển stage."""
        old_stages = {task.id: task.stage_id for task in self}
        result = super().write(vals)

        if 'stage_id' in vals:
            for task in self:
                old_stage = old_stages.get(task.id)
                if old_stage != task.stage_id:
                    task._notify_stage_change(old_stage)

                # Auto-assign reviewer khi vào review stage
                review_stage = self.env.ref(
                    'my_module.task_stage_review',
                    raise_if_not_found=False,
                )
                if (review_stage and task.stage_id == review_stage
                        and not task.x_reviewer_id):
                    task.x_reviewer_id = task.project_id.x_project_manager_id

        return result

    def _notify_stage_change(self, old_stage: 'project.task.type') -> None:
        """Gửi notification khi đổi stage."""
        self.message_post(
            body=_("Stage changed from '%(from)s' to '%(to)s'.",
                   from_=old_stage.name,
                   to=self.stage_id.name),
            message_type='notification',
        )
        # Notify assignees qua activity
        for user in self.user_ids:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_('Task moved to %s', self.stage_id.name),
                user_id=user.id,
            )
```

### Bước 8 — Cron: Cảnh báo task quá hạn

```python
class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def _cron_check_overdue_tasks(self) -> None:
        """Cảnh báo task quá hạn — chạy hàng ngày."""
        today = fields.Date.today()
        overdue_tasks = self.search([
            ('date_deadline', '<', today),
            ('stage_id.fold', '=', False),   # Chưa done
        ])

        for task in overdue_tasks:
            task.message_post(
                body=_("This task is overdue!"),
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
            )
            if task.project_id.x_project_manager_id:
                task.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_('Overdue task: %s', task.name),
                    user_id=task.project_id.x_project_manager_id.id,
                )
```

```xml
<!-- Cron XML -->
<record id="ir_cron_check_overdue_tasks" model="ir.cron">
    <field name="name">Check Overdue Tasks</field>
    <field name="model_id" ref="project.model_project_task"/>
    <field name="state">code</field>
    <field name="code">model._cron_check_overdue_tasks()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
    <field name="active" eval="True"/>
</record>
```

### Bước 9 — View XML kế thừa Project và Task

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Kế thừa Project Form -->
    <record id="view_project_form_inherit" model="ir.ui.view">
        <field name="name">project.project.form.inherit.my_module</field>
        <field name="model">project.project</field>
        <field name="inherit_id" ref="project.edit_project"/>
        <field name="arch" type="xml">
            <field name="partner_id" position="after">
                <field name="x_project_code"/>
                <field name="x_project_type"/>
            </field>

            <xpath expr="//page[@name='settings']" position="before">
                <page string="Planning" name="planning">
                    <group>
                        <group>
                            <field name="x_start_date"/>
                            <field name="x_end_date"/>
                            <field name="x_department_id"/>
                        </group>
                        <group>
                            <field name="x_budget"/>
                            <field name="x_remaining_budget"/>
                            <field name="x_progress" widget="progressbar"/>
                        </group>
                    </group>
                </page>
            </xpath>
        </field>
    </record>

    <!-- Kế thừa Task Form -->
    <record id="view_task_form_inherit" model="ir.ui.view">
        <field name="name">project.task.form.inherit.my_module</field>
        <field name="model">project.task</field>
        <field name="inherit_id" ref="project.view_task_form2"/>
        <field name="arch" type="xml">
            <field name="priority" position="after">
                <field name="x_task_type"/>
                <field name="x_priority_level"/>
            </field>

            <field name="user_ids" position="after">
                <field name="x_reviewer_id"/>
            </field>

            <xpath expr="//page[@name='description_page']" position="after">
                <page string="Planning" name="planning">
                    <group>
                        <group>
                            <field name="x_estimated_hours"/>
                            <field name="effective_hours"/>
                            <field name="x_progress" widget="progressbar"/>
                        </group>
                        <group>
                            <field name="x_depends_on_ids" widget="many2many_tags"/>
                            <field name="x_is_blocked"/>
                        </group>
                    </group>
                </page>

                <page string="Checklist" name="checklist">
                    <field name="x_checklist_ids">
                        <!-- v19: dùng <list> không phải <tree> -->
                        <list editable="bottom">
                            <field name="sequence" widget="handle"/>
                            <field name="name"/>
                            <field name="is_done"/>
                            <field name="done_by" readonly="1"/>
                            <field name="done_date" readonly="1"/>
                        </list>
                    </field>
                    <field name="x_checklist_progress" widget="progressbar"/>
                </page>
            </xpath>
        </field>
    </record>
</odoo>
```

### Bước 10 — ACL cho model tùy chỉnh

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_task_checklist_user,project.task.checklist.user,model_project_task_checklist,base.group_user,1,1,1,1
```

## Constraints
- **PHẢI** dùng `@api.model_create_multi` (không phải `create` đơn lẻ)
- `write()` kế thừa phải gọi `super().write(vals)` trước khi xử lý logic
- `_read_group_stage_ids` **phải** trả về recordset — không phải list
- `_get_all_dependencies` phải handle `visited` để tránh infinite loop
- **KHÔNG** dùng f-strings trong `_()` — dùng `%s` hoặc `%(name)s`

## Best practices
- Dùng `x_` prefix cho fields tùy chỉnh — tránh conflict với Odoo core
- Stage-based workflow thay vì custom state field cho flexibility
- `activity_schedule()` thay vì send email trực tiếp — user tự quản lý
- `effective_hours` là field chuẩn của project — không tự tính lại
- Cron overdue: search limit để batch, tránh memory issue
- Track dependencies để detect blocked tasks sớm
