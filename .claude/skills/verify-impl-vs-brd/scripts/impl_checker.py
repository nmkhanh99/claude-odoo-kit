#!/usr/bin/env python3
"""
impl_checker.py — verify-impl-vs-brd skill
Scan module source code and verify each BRD requirement.

Usage: Set MODULE_PATH and REQUIREMENTS below, then run.
"""
import ast
import os
import csv
import re
from pathlib import Path
from xml.etree import ElementTree as ET

# ── CONFIGURE BEFORE RUNNING ──────────────────────────────────────────────────
MODULE_PATH = "/Users/khanhnm/Desktop/odoo-19.0/addons-scx/scx_inventory"

# List of requirements to verify — generated from brd-to-dev-tasks output
# Format: (req_id, req_type, identifier, description, brd_section)
# req_type options: security-group, model-field, ir-rule, acl-row,
#                   state-machine, workflow-action, view-form, menu-item, data-sequence
REQUIREMENTS = [
    # Examples — replace with actual BRD requirements:
    # ("REQ-01", "security-group", "group_warehouse_staff",    "NV kho thường",            "§2.6"),
    # ("REQ-02", "model-field",    "res.users:warehouse_ids",  "M2M warehouse per user",   "§2.3"),
    # ("REQ-03", "ir-rule",        "rule_picking_warehouse",   "Restrict picking by WH",   "§3.3"),
    # ("REQ-04", "acl-row",        "stock.picking",            "ACL for warehouse staff",  "§2.6"),
    # ("REQ-05", "state-machine",  "stock.disposal.proposal",  "draft/confirmed/done",     "§2.1"),
    # ("REQ-06", "workflow-action","action_confirm",           "Confirm button method",    "§2.1"),
    # ("REQ-07", "view-form",      "stock.disposal.proposal",  "Form + list views",        "§2.2.2"),
    # ("REQ-08", "data-sequence",  "stock.disposal.proposal",  "Sequence DSP/YYYY/NNNNN",  "§3.1"),
]
# ──────────────────────────────────────────────────────────────────────────────


def find_files(base: Path, pattern: str) -> list:
    return list(base.rglob(pattern))


def grep_in_file(filepath: Path, pattern: str) -> list:
    """Return list of (line_no, line_content) matching pattern."""
    results = []
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(pattern, line):
                results.append((i, line.strip()))
    except Exception:
        pass
    return results


def grep_in_dir(base: Path, subdir: str, pattern: str, ext: str = "*") -> list:
    """Search pattern across all files matching ext in subdir."""
    results = []
    target = base / subdir
    if not target.exists():
        return results
    for f in target.rglob(f"*.{ext}"):
        hits = grep_in_file(f, pattern)
        for line_no, line in hits:
            results.append((str(f.relative_to(base)), line_no, line))
    return results


def check_security_group(base: Path, identifier: str) -> dict:
    """Check if security group exists in security/security.xml."""
    results = grep_in_dir(base, "security", rf'id="{identifier}"', "xml")
    if not results:
        return {"status": "MISSING", "evidence": None, "issue": "Not found in security/*.xml"}

    filepath, line_no, line = results[0]
    # Check for privilege_id (Odoo 17+) vs deprecated category_id
    sec_file = base / filepath
    full_text = sec_file.read_text(encoding="utf-8", errors="ignore")
    has_privilege = "privilege_id" in full_text
    has_category = "category_id" in full_text and "privilege_id" not in full_text

    if has_category:
        return {
            "status": "PARTIAL",
            "evidence": f"{filepath}:{line_no}",
            "issue": "Uses deprecated category_id — should use privilege_id (Odoo 17+)"
        }
    return {
        "status": "DONE",
        "evidence": f"{filepath}:{line_no}",
        "issue": None
    }


def check_model_field(base: Path, identifier: str) -> dict:
    """Check model.name:field_name exists with correct type."""
    if ":" not in identifier:
        return {"status": "MISSING", "evidence": None, "issue": "Bad format — use 'model.name:field_name'"}

    model_name, field_name = identifier.split(":", 1)
    model_snake = model_name.replace(".", "_")

    # Try to find in models/
    results = grep_in_dir(base, "models", rf"{field_name}\s*=\s*fields\.", "py")
    if not results:
        return {"status": "MISSING", "evidence": None, "issue": f"Field '{field_name}' not found in models/"}

    filepath, line_no, line = results[0]
    # Check if it's in an EMPTY class (no other fields/methods nearby)
    full_path = base / filepath
    try:
        tree = ast.parse(full_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_field = any(
                    isinstance(stmt, ast.Assign) and
                    any(t.id == field_name for t in stmt.targets if isinstance(t, ast.Name))
                    for stmt in ast.walk(node)
                )
                if has_field:
                    non_trivial = [
                        s for s in node.body
                        if not (isinstance(s, ast.Assign) and
                                any(t.id in ("_name", "_inherit", "_description", "_order", "_rec_name")
                                    for t in s.targets if isinstance(t, ast.Name)))
                        and not isinstance(s, ast.Pass)
                        and not isinstance(s, ast.Expr)
                    ]
                    if len(non_trivial) <= 1:  # Only the field itself
                        return {
                            "status": "PARTIAL",
                            "evidence": f"{filepath}:{line_no}",
                            "issue": "Field in EMPTY class (no other logic) — class may be a stub"
                        }
    except Exception:
        pass

    return {"status": "DONE", "evidence": f"{filepath}:{line_no}", "issue": None}


def check_ir_rule(base: Path, identifier: str) -> dict:
    """Check if ir.rule record exists."""
    results = grep_in_dir(base, "security", rf'id="{identifier}"', "xml")
    if not results:
        return {"status": "MISSING", "evidence": None, "issue": "ir.rule not found in security/*.xml"}

    filepath, line_no, _ = results[0]
    # Check domain_force exists
    domain_results = grep_in_dir(base, "security", r"domain_force", "xml")
    if not domain_results:
        return {
            "status": "PARTIAL",
            "evidence": f"{filepath}:{line_no}",
            "issue": "Rule found but no domain_force defined"
        }
    return {"status": "DONE", "evidence": f"{filepath}:{line_no}", "issue": None}


def check_acl_row(base: Path, identifier: str) -> dict:
    """Check ACL entry for model in ir.model.access.csv."""
    model_name = identifier  # e.g., "stock.picking"
    model_ref = "model_" + model_name.replace(".", "_")

    csv_files = find_files(base / "security", "ir.model.access.csv")
    if not csv_files:
        return {"status": "MISSING", "evidence": None, "issue": "No ir.model.access.csv found"}

    found_rows = []
    for csv_file in csv_files:
        try:
            with open(csv_file, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader, 1):
                    if len(row) >= 3 and model_ref in row[2]:
                        found_rows.append((str(csv_file.relative_to(base)), i, row))
        except Exception:
            pass

    if not found_rows:
        return {"status": "MISSING", "evidence": None, "issue": f"No ACL row for '{model_name}' ({model_ref})"}

    rel_path, line_no, _ = found_rows[0]
    return {
        "status": "DONE",
        "evidence": f"{rel_path}:{line_no} ({len(found_rows)} rows)",
        "issue": None
    }


def check_state_machine(base: Path, identifier: str) -> dict:
    """Check state Selection field on model."""
    model_name = identifier
    results = grep_in_dir(base, "models", r"state\s*=\s*fields\.Selection", "py")
    if not results:
        return {"status": "MISSING", "evidence": None, "issue": "No 'state = fields.Selection' found in models/"}

    filepath, line_no, line = results[0]
    # Check for action methods
    action_results = grep_in_dir(base, "models", r"def action_(confirm|cancel|validate|done)", "py")
    if not action_results:
        return {
            "status": "PARTIAL",
            "evidence": f"{filepath}:{line_no}",
            "issue": "State field found but no action_* transition methods"
        }
    return {"status": "DONE", "evidence": f"{filepath}:{line_no}", "issue": None}


def check_workflow_action(base: Path, identifier: str) -> dict:
    """Check workflow action method exists."""
    results = grep_in_dir(base, "models", rf"def {identifier}\s*\(", "py")
    if not results:
        return {"status": "MISSING", "evidence": None, "issue": f"def {identifier}() not found in models/"}

    filepath, line_no, _ = results[0]
    # Check not a stub (just pass / return True)
    full_path = base / filepath
    try:
        lines = full_path.read_text(encoding="utf-8").splitlines()
        body_lines = []
        in_method = False
        indent_level = None
        for i, l in enumerate(lines[line_no:line_no + 10], line_no + 1):
            stripped = l.strip()
            if not stripped:
                continue
            indent = len(l) - len(l.lstrip())
            if indent_level is None and stripped.startswith("def "):
                indent_level = indent
                continue
            if indent_level is not None and indent <= indent_level and stripped:
                break
            body_lines.append(stripped)

        if body_lines and all(l in ("pass", "return True", "return") for l in body_lines[:3]):
            return {
                "status": "PARTIAL",
                "evidence": f"{filepath}:{line_no}",
                "issue": "Method exists but appears to be a stub (only pass/return)"
            }
    except Exception:
        pass

    return {"status": "DONE", "evidence": f"{filepath}:{line_no}", "issue": None}


def check_view_form(base: Path, identifier: str) -> dict:
    """Check if form/list view exists for model."""
    model_name = identifier
    results = grep_in_dir(base, "views", re.escape(model_name), "xml")
    if not results:
        return {"status": "MISSING", "evidence": None, "issue": f"No view XML referencing '{model_name}'"}

    filepath, line_no, _ = results[0]
    # Check for list (not tree)
    tree_results = grep_in_dir(base, "views", r"<tree", "xml")
    if tree_results:
        return {
            "status": "PARTIAL",
            "evidence": f"{filepath}:{line_no}",
            "issue": "Uses deprecated <tree> tag — should use <list> (Odoo 17+)"
        }
    return {"status": "DONE", "evidence": f"{filepath}:{line_no}", "issue": None}


def check_data_sequence(base: Path, identifier: str) -> dict:
    """Check sequence data file exists for model."""
    results = grep_in_dir(base, "data", r"ir\.sequence", "xml")
    if not results:
        return {"status": "MISSING", "evidence": None, "issue": "No ir.sequence in data/ directory"}

    model_snake = identifier.replace(".", "_")
    model_results = grep_in_dir(base, "data", re.escape(identifier), "xml")
    if not model_results:
        return {
            "status": "PARTIAL",
            "evidence": results[0][0],
            "issue": f"ir.sequence found but no sequence for '{identifier}'"
        }

    filepath, line_no, _ = model_results[0]
    # Check noupdate="1"
    full_path = base / filepath
    content = full_path.read_text(encoding="utf-8", errors="ignore")
    if 'noupdate="1"' not in content:
        return {
            "status": "PARTIAL",
            "evidence": f"{filepath}:{line_no}",
            "issue": "Sequence found but missing noupdate=\"1\" — will be overwritten on module update"
        }
    return {"status": "DONE", "evidence": f"{filepath}:{line_no}", "issue": None}


# ── Main ──────────────────────────────────────────────────────────────────────

CHECKERS = {
    "security-group":  check_security_group,
    "model-field":     check_model_field,
    "ir-rule":         check_ir_rule,
    "acl-row":         check_acl_row,
    "state-machine":   check_state_machine,
    "workflow-action": check_workflow_action,
    "view-form":       check_view_form,
    "data-sequence":   check_data_sequence,
}

STATUS_ICON = {"DONE": "✅", "PARTIAL": "⚠️ ", "MISSING": "❌"}


def main():
    base = Path(MODULE_PATH)
    if not base.exists():
        print(f"❌ Module path not found: {MODULE_PATH}")
        return

    if not REQUIREMENTS:
        print("⚠️  No requirements configured. Edit REQUIREMENTS list in this script.")
        print("   Format: (req_id, req_type, identifier, description, brd_section)")
        return

    results = []
    for req_id, req_type, identifier, description, brd_section in REQUIREMENTS:
        checker = CHECKERS.get(req_type)
        if not checker:
            results.append({
                "id": req_id, "type": req_type, "identifier": identifier,
                "description": description, "section": brd_section,
                "status": "MISSING", "evidence": None,
                "issue": f"Unknown req_type: {req_type}"
            })
            continue

        result = checker(base, identifier)
        results.append({
            "id": req_id, "type": req_type, "identifier": identifier,
            "description": description, "section": brd_section,
            **result
        })

    # ── Print Report ──
    done_count    = sum(1 for r in results if r["status"] == "DONE")
    partial_count = sum(1 for r in results if r["status"] == "PARTIAL")
    missing_count = sum(1 for r in results if r["status"] == "MISSING")
    total = len(results)
    pct = int(done_count / total * 100) if total else 0

    print(f"\n📋 VERIFICATION REPORT: {base.name}")
    print(f"   Module : {MODULE_PATH}")
    print(f"   Total  : {total} requirements\n")
    print(f"✅ DONE    : {done_count} / {total}  ({pct}%)")
    print(f"⚠️  PARTIAL : {partial_count} / {total}")
    print(f"❌ MISSING : {missing_count} / {total}")
    print("\n── DETAILS ─────────────────────────────────────────────────────\n")

    for r in results:
        icon = STATUS_ICON[r["status"]]
        print(f"[{r['status']}] {icon} {r['id']} | {r['type']} | {r['identifier']}")
        print(f"  Description : {r['description']}  (BRD {r['section']})")
        if r["evidence"]:
            print(f"  Found       : {r['evidence']}")
        if r["issue"]:
            print(f"  Issue       : {r['issue']}")
        print()

    # ── Action Summary ──
    partials = [r for r in results if r["status"] == "PARTIAL"]
    missings = [r for r in results if r["status"] == "MISSING"]

    if partials or missings:
        print("── ACTION SUMMARY ───────────────────────────────────────────────\n")
        if partials:
            print("⚠️  CẦN FIX (PARTIAL):")
            for r in partials:
                print(f"  {r['id']} | {r['evidence']} → {r['issue']}")
        if missings:
            print("\n❌ CẦN LÀM (MISSING):")
            for r in missings:
                print(f"  {r['id']} | {r['identifier']} — {r['description']}")
    else:
        print("🎉 All requirements verified — DONE!")


if __name__ == "__main__":
    main()
