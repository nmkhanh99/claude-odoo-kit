"""
scan-odoo-base: Quét source Odoo base modules để tìm models/fields/groups/rules.
Chạy qua: python3 - << 'PYEOF' ... PYEOF
Thay BASE_MODULES và QUERY_FIELDS trước khi chạy.
"""
import os
import ast
import re
import xml.etree.ElementTree as ET

# ── Cấu hình ──────────────────────────────────────────────────────────────────
BASE_MODULES = ["stock", "hr", "base"]   # ← thay danh sách module cần scan

# Query cụ thể (tuỳ chọn): kiểm tra field/model cụ thể có tồn tại không
# Format: [("model_name", "field_name"), ...] — bỏ trống nếu chỉ muốn report tổng quan
QUERY_FIELDS = [
    # ("res.users",    "warehouse_ids"),
    # ("stock.picking", "responsible_id"),
]

ADDON_PATHS = [
    "/Users/khanhnm/Desktop/odoo-19.0/addons",
    "/Users/khanhnm/Desktop/odoo-19.0/odoo/addons",
    "/Users/khanhnm/Desktop/odoo-19.0/addons-oca1",
]

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def find_module_path(module_name):
    for base in ADDON_PATHS:
        p = os.path.join(base, module_name)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "__manifest__.py")):
            return p
    return None

def read_file(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def iter_py_files(directory):
    if not os.path.isdir(directory):
        return
    for fname in sorted(os.listdir(directory)):
        if fname.endswith(".py") and not fname.startswith("__"):
            yield os.path.join(directory, fname), fname

def iter_xml_records(xml_path, model_filter=None):
    content = read_file(xml_path)
    if not content:
        return
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return
    for rec in root.iter("record"):
        model = rec.get("model", "")
        rid   = rec.get("id", "")
        if model_filter and model not in model_filter:
            continue
        fields = {f.get("name"): (f.text or "").strip() for f in rec.findall("field")}
        yield rid, model, fields

# ══════════════════════════════════════════════════════════════════════════════
# SCAN PYTHON — extract model + field inventory
# ══════════════════════════════════════════════════════════════════════════════

def scan_models(module_path):
    """
    Returns: dict { "model_name" : { "file": str, "fields": {fname: ftype}, "inherit": bool } }
    """
    models_dir = os.path.join(module_path, "models")
    result = {}

    dirs_to_scan = [models_dir]
    # Scan subfolders (strategy patterns, mixins, etc.)
    if os.path.isdir(models_dir):
        for entry in os.scandir(models_dir):
            if entry.is_dir() and not entry.name.startswith("__"):
                dirs_to_scan.append(entry.path)

    for scan_dir in dirs_to_scan:
        for fpath, fname in iter_py_files(scan_dir):
            src = read_file(fpath)
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue

                model_name = None
                inherit    = None
                fields     = {}

                for item in node.body:
                    if not isinstance(item, ast.Assign):
                        continue
                    for t in item.targets:
                        if not isinstance(t, ast.Name):
                            continue
                        if t.id == "_name" and isinstance(item.value, ast.Constant):
                            model_name = item.value.value
                        elif t.id == "_inherit":
                            if isinstance(item.value, ast.Constant):
                                inherit = item.value.value
                            elif isinstance(item.value, ast.List):
                                inherit = [e.value for e in item.value.elts
                                           if isinstance(e, ast.Constant)]

                # Extract fields
                for node2 in ast.walk(node):
                    if isinstance(node2, ast.Assign):
                        for t in node2.targets:
                            if isinstance(t, ast.Name) and isinstance(node2.value, ast.Call):
                                func = node2.value.func
                                if (isinstance(func, ast.Attribute)
                                        and isinstance(func.value, ast.Name)
                                        and func.value.id == "fields"):
                                    fields[t.id] = func.attr

                # Determine model key(s)
                keys = []
                if model_name:
                    keys.append(model_name)
                elif inherit:
                    keys = [inherit] if isinstance(inherit, str) else inherit

                for key in keys:
                    if key not in result:
                        result[key] = {"file": fpath, "fields": {}, "is_inherit": bool(inherit)}
                    result[key]["fields"].update(fields)
                    # keep first file path seen as canonical
                    if not result[key]["file"]:
                        result[key]["file"] = fpath

    return result

# ══════════════════════════════════════════════════════════════════════════════
# SCAN SECURITY
# ══════════════════════════════════════════════════════════════════════════════

def scan_security(module_path, module_name):
    groups = []
    rules  = []

    sec_dir = os.path.join(module_path, "security")
    if not os.path.isdir(sec_dir):
        return groups, rules

    for fname in os.listdir(sec_dir):
        if not fname.endswith(".xml"):
            continue
        fpath = os.path.join(sec_dir, fname)
        for rid, model, fields in iter_xml_records(fpath, {"res.groups", "ir.rule"}):
            if model == "res.groups":
                groups.append({
                    "id":   f"{module_name}.{rid}",
                    "name": fields.get("name", "?"),
                })
            elif model == "ir.rule":
                rules.append({
                    "id":     f"{module_name}.{rid}",
                    "name":   fields.get("name", "?"),
                    "domain": fields.get("domain_force", "?")[:80],
                })

    return groups, rules

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

all_model_index = {}   # model_name → {module, file, fields, is_inherit}

for module_name in BASE_MODULES:
    module_path = find_module_path(module_name)

    if not module_path:
        print(f"\n❌ Module '{module_name}' không tìm thấy trong addon paths.")
        continue

    print(f"\n{'='*65}")
    print(f"📦 BASE MODULE: {module_name}  ({module_path})")

    # Models
    models = scan_models(module_path)
    print(f"\n🗃️  MODELS ({len(models)} models defined/inherited)")

    for mname in sorted(models.keys()):
        info   = models[mname]
        tag    = "_inherit" if info["is_inherit"] else "_name  "
        fcount = len(info["fields"])
        rel_path = info["file"].replace(module_path + "/", "")
        print(f"  {tag} | {mname:<45} | {fcount:>3} fields | {rel_path}")
        # Build global index
        if mname not in all_model_index:
            all_model_index[mname] = {"module": module_name, "file": info["file"], "fields": {}}
        all_model_index[mname]["fields"].update(info["fields"])

    # Security
    groups, rules = scan_security(module_path, module_name)
    print(f"\n🔐 SECURITY GROUPS ({len(groups)})")
    for g in groups:
        print(f"  {g['id']:<50}  {g['name']}")
    if rules:
        print(f"\n🔒 RECORD RULES ({len(rules)})")
        for r in rules:
            print(f"  {r['id']}")
            print(f"    domain: {r['domain']}")

# ══════════════════════════════════════════════════════════════════════════════
# FIELD QUERIES
# ══════════════════════════════════════════════════════════════════════════════

if QUERY_FIELDS:
    print(f"\n{'='*65}")
    print("🔍 FIELD QUERY RESULTS")
    for (model, field) in QUERY_FIELDS:
        if model in all_model_index and field in all_model_index[model]["fields"]:
            ftype    = all_model_index[model]["fields"][field]
            rel_path = all_model_index[model]["file"]
            print(f"  ✅ FOUND    | {model}.{field:<35} | {ftype:<12} | {rel_path}")
        else:
            if model in all_model_index:
                print(f"  ❌ NOT FOUND| {model}.{field:<35} | – | model exists but field missing")
            else:
                print(f"  ❌ NOT FOUND| {model}.{field:<35} | – | model not in scanned modules")

# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY TABLE — for brd-to-dev-tasks handoff
# ══════════════════════════════════════════════════════════════════════════════

print(f"\n{'='*65}")
print("📋 MODEL INDEX (tất cả models từ tất cả modules đã scan)")
print(f"   Tổng: {len(all_model_index)} models")
for mname in sorted(all_model_index.keys()):
    info = all_model_index[mname]
    fields_preview = ", ".join(list(info["fields"].keys())[:6])
    if len(info["fields"]) > 6:
        fields_preview += f"... (+{len(info['fields'])-6} more)"
    print(f"  [{info['module']}] {mname}")
    if fields_preview:
        print(f"         fields: {fields_preview}")
