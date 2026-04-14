---
name: odoo-owl19
description: Viết OWL 3.x component Odoo 19 — component structure, hooks, field widget, template, registry. Kích hoạt khi user nói "owl component", "viết component", "tạo widget", "OWL 3", "frontend odoo", "javascript odoo", "custom widget".
---

# Odoo OWL 3.x Component (v19)

## Goal
Tạo OWL 3.x components đúng chuẩn Odoo 19 — basic component, field widget, client action — với lifecycle hooks, JSDoc annotations và cleanup pattern.

**Input**: Mô tả component cần tạo  
**Output**: File JS + XML template + đăng ký manifest

## When to use this skill
- "tạo OWL component", "viết custom widget"
- "tạo client action với OWL"
- "tạo field widget tùy chỉnh"
- "OWL 3.x", "Owl frontend Odoo 19"

## Instructions

### Bước 1 — Quy tắc OWL 3.x bắt buộc

```
╔══════════════════════════════════════════════════════════════╗
║  OWL 3.x BẮT BUỘC:                                          ║
║  • Tất cả hooks (useState, useRef...) phải trong setup()     ║
║  • Dùng /** @odoo-module **/ directive                        ║
║  • JSDoc type annotations cho props và state                 ║
║  • Cleanup trong onWillUnmount                               ║
║  • Import từ "@odoo/owl" (không phải owljs)                  ║
╚══════════════════════════════════════════════════════════════╝
```

### Bước 2 — Basic Component

```javascript
/** @odoo-module **/

import {
    Component,
    useState,
    useRef,
    onWillStart,
    onMounted,
    onWillUnmount,
} from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

/**
 * @typedef {Object} MyComponentProps
 * @property {number} [recordId]
 * @property {string} [mode]
 * @property {Function} [onSelect]
 */

export class MyComponent extends Component {
    static template = "my_module.MyComponent";

    /** @type {MyComponentProps} */
    static props = {
        recordId: { type: Number, optional: true },
        mode: {
            type: String,
            optional: true,
            validate: (v) => ['view', 'edit'].includes(v),
        },
        onSelect: { type: Function, optional: true },
    };

    static defaultProps = { mode: "view" };

    setup() {
        // === SERVICES ===
        /** @type {import("@web/core/orm_service").ORM} */
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.user = useService("user");
        this.company = useService("company");

        // === STATE — phải trong setup() ===
        this.state = useState({
            /** @type {Array<Object>} */
            data: [],
            /** @type {boolean} */
            loading: true,
            /** @type {string|null} */
            error: null,
            /** @type {number|null} */
            selectedId: null,
            filters: {
                state: null,
                search: "",
            },
        });

        // === REFS ===
        this.containerRef = useRef("container");
        this.searchRef = useRef("search");

        // Cleanup functions
        this._cleanup = null;
        this._abortController = null;

        // === LIFECYCLE ===
        onWillStart(async () => {
            await this.loadData();
        });

        onMounted(() => {
            this._setupEventListeners();
            this.searchRef.el?.focus();
        });

        onWillUnmount(() => {
            this._cleanup?.();
            this._abortController?.abort();
        });
    }

    _setupEventListeners() {
        const handler = (e) => {
            if (e.key === "Escape") this.state.selectedId = null;
        };
        document.addEventListener("keydown", handler);
        this._cleanup = () => document.removeEventListener("keydown", handler);
    }

    /**
     * Load data từ server
     * @returns {Promise<void>}
     */
    async loadData() {
        this._abortController = new AbortController();
        this.state.loading = true;
        this.state.error = null;

        try {
            const domain = this._buildDomain();
            const data = await this.orm.searchRead(
                "my.model",
                domain,
                ["name", "state", "amount", "partner_id"],
                { order: "create_date DESC", limit: 100 }
            );
            this.state.data = data;
        } catch (error) {
            if (error.name !== 'AbortError') {
                this.state.error = error.message || "Failed to load data";
                this.notification.add(this.state.error, {
                    type: "danger",
                    sticky: true,
                });
            }
        } finally {
            this.state.loading = false;
        }
    }

    /**
     * Build search domain từ filters
     * @returns {Array}
     */
    _buildDomain() {
        const domain = [];
        if (this.state.filters.state) {
            domain.push(["state", "=", this.state.filters.state]);
        }
        if (this.state.filters.search) {
            domain.push(["name", "ilike", this.state.filters.search]);
        }
        return domain;
    }

    /**
     * @param {Object} item
     */
    onItemSelect(item) {
        this.state.selectedId = item.id;
        if (this.props.onSelect) this.props.onSelect(item.id);
    }

    /**
     * @param {number} id
     */
    async openRecord(id) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "my.model",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }

    /**
     * @param {Event} ev
     */
    onSearchInput(ev) {
        this.state.filters.search = ev.target.value;
        this.loadData();
    }

    /**
     * @param {string|null} state
     */
    onFilterChange(state) {
        this.state.filters.state = state;
        this.loadData();
    }

    async onRefresh() {
        await this.loadData();
        this.notification.add("Data refreshed", { type: "success" });
    }
}

// Đăng ký là client action
registry.category("actions").add("my_module.my_component", MyComponent);
```

### Bước 3 — XML Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent">
        <div t-ref="container" class="o_my_component d-flex flex-column h-100">
            <!-- Header với search và filters -->
            <div class="o_cp_top p-3 border-bottom bg-light">
                <div class="d-flex justify-content-between align-items-center">
                    <h4 class="mb-0">Records</h4>
                    <button class="btn btn-outline-secondary btn-sm"
                            t-on-click="onRefresh"
                            t-att-disabled="state.loading">
                        <i t-attf-class="fa fa-refresh {{ state.loading ? 'fa-spin' : '' }}"/>
                    </button>
                </div>

                <!-- Search -->
                <div class="d-flex gap-3 mt-3">
                    <div class="flex-grow-1">
                        <input t-ref="search"
                               type="search"
                               class="form-control form-control-sm"
                               placeholder="Search..."
                               t-att-value="state.filters.search"
                               t-on-input="onSearchInput"/>
                    </div>
                    <!-- Filters -->
                    <div class="btn-group btn-group-sm">
                        <button t-attf-class="btn {{ !state.filters.state ? 'btn-primary' : 'btn-outline-primary' }}"
                                t-on-click="() => this.onFilterChange(null)">All</button>
                        <button t-attf-class="btn {{ state.filters.state === 'draft' ? 'btn-primary' : 'btn-outline-primary' }}"
                                t-on-click="() => this.onFilterChange('draft')">Draft</button>
                        <button t-attf-class="btn {{ state.filters.state === 'confirmed' ? 'btn-primary' : 'btn-outline-primary' }}"
                                t-on-click="() => this.onFilterChange('confirmed')">Confirmed</button>
                    </div>
                </div>
            </div>

            <!-- Content -->
            <div class="flex-grow-1 overflow-auto p-3">
                <!-- Loading -->
                <t t-if="state.loading">
                    <div class="d-flex justify-content-center align-items-center h-100">
                        <div class="spinner-border text-primary" role="status"/>
                    </div>
                </t>

                <!-- Error -->
                <t t-elif="state.error">
                    <div class="alert alert-danger m-3">
                        <strong>Error loading data</strong>
                        <p class="mb-0 mt-1" t-esc="state.error"/>
                        <button class="btn btn-outline-danger btn-sm mt-3"
                                t-on-click="onRefresh">Try Again</button>
                    </div>
                </t>

                <!-- Data -->
                <t t-elif="state.data.length">
                    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">
                        <t t-foreach="state.data" t-as="item" t-key="item.id">
                            <div class="col">
                                <div t-attf-class="card h-100 {{ item.id === state.selectedId ? 'border-primary shadow' : '' }}"
                                     t-on-click="() => this.onItemSelect(item)"
                                     style="cursor: pointer;">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between align-items-start">
                                            <h5 class="card-title mb-1" t-esc="item.name"/>
                                            <span t-attf-class="badge bg-{{ item.state === 'done' ? 'success' : item.state === 'cancelled' ? 'danger' : 'secondary' }}">
                                                <t t-esc="item.state"/>
                                            </span>
                                        </div>
                                    </div>
                                    <div class="card-footer bg-transparent">
                                        <button class="btn btn-sm btn-outline-primary w-100"
                                                t-on-click.stop="() => this.openRecord(item.id)">
                                            <i class="fa fa-external-link me-1"/>
                                            Open
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </t>
                    </div>
                </t>

                <!-- Empty -->
                <t t-else="">
                    <div class="d-flex flex-column align-items-center justify-content-center h-100 text-muted">
                        <i class="fa fa-inbox fa-4x mb-3"/>
                        <h5>No Records Found</h5>
                    </div>
                </t>
            </div>
        </div>
    </t>
</templates>
```

### Bước 4 — Custom Field Widget

```javascript
/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class CustomFieldWidget extends Component {
    static template = "my_module.CustomFieldWidget";
    static props = {
        ...standardFieldProps,
        customOption: { type: String, optional: true },
    };

    /** @returns {string} */
    get formattedValue() {
        const value = this.props.record.data[this.props.name];
        if (!value) return "";
        return `★ ${value}`;
    }

    /** @returns {boolean} */
    get isReadonly() {
        return this.props.readonly || !this.props.record.isEditable;
    }

    /** @param {Event} ev */
    onChange(ev) {
        if (this.isReadonly) return;
        this.props.record.update({ [this.props.name]: ev.target.value });
    }
}

registry.category("fields").add("custom_widget", {
    component: CustomFieldWidget,
    supportedTypes: ["char", "text"],
    extractProps: ({ attrs }) => ({
        customOption: attrs.custom_option,
    }),
});
```

### Bước 5 — Manifest assets

```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/js/my_component.js',
        'my_module/static/src/xml/my_component.xml',
        'my_module/static/src/scss/my_component.scss',
    ],
},
```

### Bước 6 — OWL 3.x Checklist

```
□ /** @odoo-module **/ ở đầu file
□ Import từ "@odoo/owl"
□ JSDoc type annotations cho props và state
□ static props với type validation
□ static defaultProps cho optional props
□ Tất cả hooks trong setup() (useState, useRef, onMounted...)
□ Cleanup trong onWillUnmount (event listeners, abort controllers)
□ AbortController cho async operations
□ File được khai báo trong manifest assets
```

## Constraints
- **KHÔNG** đặt hooks ngoài `setup()` — sẽ crash trong OWL 3.x
- **KHÔNG** dùng OWL 2.x patterns
- **KHÔNG** import component mà không đăng ký trong `registry`

## Best practices
- Luôn cleanup event listeners trong `onWillUnmount`
- Dùng `AbortController` cho fetch/async để tránh memory leak
- `static props` validation giúp debug rõ ràng hơn
- `t-on-click.stop` để ngăn event propagation khi cần
- State Set/Map trong OWL 3.x có thể mutate trực tiếp (reactive)
