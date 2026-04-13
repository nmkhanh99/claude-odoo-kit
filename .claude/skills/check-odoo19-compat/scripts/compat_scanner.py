#!/usr/bin/env python3
"""
compat_scanner.py — check-odoo19-compat skill
Scan Odoo module for deprecated API patterns (Odoo 17+/19).

Usage: Set MODULE_PATH below, then run.
"""
import re
import sys
from pathlib import Path

# ── CONFIGURE ─────────────────────────────────────────────────────────────────
MODULE_PATH = "/Users/khanhnm/Desktop/odoo-19.0/addons-scx/scx_inventory"
# ──────────────────────────────────────────────────────────────────────────────


# ── Pattern definitions ────────────────────────────────────────────────────────
# (pattern_id, severity, regex, description, fix_hint, file_type, exclude_regex)
PATTERNS = [
    # Python patterns
    ("P01", "ERROR", r"\bdef name_get\s*\(self\)",
     "name_get() removed in Odoo 17+",
     "Use _rec_name = 'field' or compute _compute_display_name",
     "py", None),

    ("P02", "WARN", r"@api\.multi\b",
     "@api.multi removed (Odoo 14+)",
     "Remove decorator — all methods are recordset by default",
     "py", None),

    ("P03", "ERROR", r"@api\.one\b",
     "@api.one removed (Odoo 14+)",
     "Remove decorator, add 'for rec in self:' loop if needed",
     "py", None),

    ("P04", "WARN", r"@api\.returns\b",
     "@api.returns removed (Odoo 14+)",
     "Remove decorator",
     "py", None),

    ("P05", "ERROR", r"\.read_group\s*\(",
     "read_group() API changed to _read_group() in Odoo 17+",
     "Use ._read_group(domain, groupby, aggregates) — new signature",
     "py", r"\._read_group\("),  # exclude already-correct _read_group

    ("P06", "INFO", r"\bself\._cr\b",
     "self._cr deprecated — use self.env.cr",
     "Replace with self.env.cr",
     "py", None),

    ("P07", "INFO", r"\bself\._uid\b",
     "self._uid deprecated — use self.env.uid",
     "Replace with self.env.uid",
     "py", None),

    ("P08", "INFO", r"\bself\._context\b",
     "self._context deprecated — use self.env.context",
     "Replace with self.env.context",
     "py", None),

    ("P09", "ERROR", r"\bfields\.datetime\.now\(\)",
     "fields.datetime.now() — wrong case (lowercase d)",
     "Use fields.Datetime.now() (capital D)",
     "py", None),

    ("P10", "WARN", r"\.sudo\(\s*\w+\s*\)",
     ".sudo(uid) deprecated — sudo no longer accepts uid argument",
     "Use .with_user(uid) or .with_user(uid).sudo()",
     "py", r"\.sudo\(\s*\)"),  # exclude empty sudo()

    ("P11", "ERROR", r"\bfrom\s+openerp\b|\bimport\s+openerp\b",
     "openerp import — use 'odoo' instead",
     "Replace 'from openerp' with 'from odoo'",
     "py", None),

    ("P12", "ERROR", r"@api\.(cr|uid|model_cr)\b",
     "@api.cr / @api.uid / @api.model_cr removed",
     "Remove decorator, use self.env.cr / self.env.uid",
     "py", None),

    ("P13", "WARN", r"\bSUPERUSER_ID\b",
     "SUPERUSER_ID deprecated in Odoo 14+",
     "Use .sudo() on recordset instead",
     "py", None),

    ("P14", "ERROR", r"\b_columns\s*=\s*\{",
     "_columns dict (Old API) removed in Odoo 10+",
     "Use fields.FieldType() declarations in class body",
     "py", None),

    ("P15", "ERROR", r"\bfields\.related\s*\([^)]*\btype\s*=",
     "fields.related() old syntax removed",
     "Use fields.Many2one/Char with related='field.subfield'",
     "py", None),

    ("P16", "WARN", r"self\.env\.cr\.execute\s*\(\s*['\"]",
     "Raw SQL string without SQL() wrapper — SQL injection risk",
     "Use: from odoo.tools import SQL; self.env.cr.execute(SQL(...))",
     "py", None),

    # XML patterns
    ("X01", "ERROR", r"<tree[\s>/]",
     "<tree> tag removed in Odoo 17+ — renamed to <list>",
     "Replace <tree ...> with <list ...> (and </tree> with </list>)",
     "xml", None),

    ("X02", "WARN", r'\battrs\s*=\s*["\']',
     "attrs= deprecated in Odoo 17+",
     "Use: invisible=\"expr\" | readonly=\"expr\" | required=\"expr\"",
     "xml", None),

    ("X03", "WARN", r'\bstates\s*=\s*["\'][^"\']+["\']',
     "states= attribute deprecated in Odoo 17+",
     "Use: invisible=\"state not in ('draft','confirmed')\"",
     "xml", r'<(record|field|menuitem|template)'),  # only on UI tags

    ("X04", "ERROR", r'<field\s+name=["\']category_id["\']',
     "category_id on res.groups removed in Odoo 17+",
     "Use: <field name=\"privilege_id\" ref=\"module.res_groups_privilege_xxx\"/>",
     "xml", None),

    ("X05", "INFO", r'</tree>',
     "</tree> closing tag — should be </list>",
     "Replace </tree> with </list>",
     "xml", None),
]

SEVERITY_ORDER = {"ERROR": 0, "WARN": 1, "INFO": 2}
SEVERITY_ICON  = {"ERROR": "❌", "WARN": "⚠️ ", "INFO": "ℹ️ "}


def scan_file(filepath: Path, file_type: str) -> list:
    """Return list of findings for a single file."""
    findings = []
    try:
        lines = filepath.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception as e:
        return []

    for pattern_id, severity, pattern, description, fix_hint, ftype, exclude in PATTERNS:
        if ftype != file_type:
            continue
        regex = re.compile(pattern)
        excl  = re.compile(exclude) if exclude else None

        for line_no, line in enumerate(lines, 1):
            if regex.search(line):
                # Skip if matches exclusion pattern
                if excl and excl.search(line):
                    continue
                findings.append({
                    "pattern_id": pattern_id,
                    "severity":   severity,
                    "line_no":    line_no,
                    "line":       line.strip()[:120],
                    "description": description,
                    "fix_hint":   fix_hint,
                })
    return findings


def main():
    base = Path(MODULE_PATH)
    if not base.exists():
        print(f"❌ Module not found: {MODULE_PATH}")
        sys.exit(1)

    py_files  = sorted(base.rglob("*.py"))
    xml_files = sorted(base.rglob("*.xml"))

    # Skip __pycache__ and .pyc
    py_files = [f for f in py_files if "__pycache__" not in str(f)]

    all_findings = []  # (filepath, finding)

    for f in py_files:
        for finding in scan_file(f, "py"):
            all_findings.append((f.relative_to(base), finding))

    for f in xml_files:
        for finding in scan_file(f, "xml"):
            all_findings.append((f.relative_to(base), finding))

    # Sort by severity then file
    all_findings.sort(key=lambda x: (SEVERITY_ORDER[x[1]["severity"]], str(x[0]), x[1]["line_no"]))

    error_count = sum(1 for _, f in all_findings if f["severity"] == "ERROR")
    warn_count  = sum(1 for _, f in all_findings if f["severity"] == "WARN")
    info_count  = sum(1 for _, f in all_findings if f["severity"] == "INFO")

    files_with_issues = len(set(str(fp) for fp, _ in all_findings))
    total_files = len(py_files) + len(xml_files)

    print(f"\n🔍 ODOO 19 COMPAT REPORT: {base.name}")
    print(f"   Module  : {MODULE_PATH}")
    print(f"   Scanned : {len(py_files)} .py files | {len(xml_files)} .xml files")
    print(f"   Found   : {error_count} errors | {warn_count} warnings | {info_count} info\n")

    if not all_findings:
        print("✅ No deprecated patterns found — module is Odoo 19 compatible!")
        return

    current_severity = None
    for filepath, finding in all_findings:
        sev = finding["severity"]
        if sev != current_severity:
            current_severity = sev
            labels = {"ERROR": "ERRORS (sẽ crash)", "WARN": "WARNINGS (deprecated)", "INFO": "INFO (style)"}
            icon = SEVERITY_ICON[sev]
            print(f"── {icon} {labels[sev]} {'─' * 40}\n")

        print(f"[{sev}] {filepath}:{finding['line_no']}")
        print(f"  Pattern : {finding['line']}")
        print(f"  Problem : [{finding['pattern_id']}] {finding['description']}")
        print(f"  Fix     : {finding['fix_hint']}")
        print()

    # Summary by file
    from collections import defaultdict
    file_counts = defaultdict(lambda: {"ERROR": 0, "WARN": 0, "INFO": 0})
    for fp, finding in all_findings:
        file_counts[str(fp)][finding["severity"]] += 1

    top_files = sorted(file_counts.items(), key=lambda x: -(x[1]["ERROR"] * 100 + x[1]["WARN"] * 10 + x[1]["INFO"]))[:5]

    print(f"── TỔNG KẾT {'─' * 50}\n")
    print(f"Files có vấn đề : {files_with_issues} / {total_files}")
    print(f"❌ ERROR         : {error_count}  → PHẢI sửa trước khi chạy Odoo 17+")
    print(f"⚠️  WARN          : {warn_count}  → Nên sửa trước khi upgrade tiếp")
    print(f"ℹ️  INFO           : {info_count}  → Có thể defer\n")

    if top_files:
        print("Top files nhiều lỗi:")
        for fp, counts in top_files:
            parts = []
            if counts["ERROR"]: parts.append(f"{counts['ERROR']} error")
            if counts["WARN"]:  parts.append(f"{counts['WARN']} warn")
            if counts["INFO"]:  parts.append(f"{counts['INFO']} info")
            print(f"  {fp}  —  {', '.join(parts)}")


if __name__ == "__main__":
    main()
