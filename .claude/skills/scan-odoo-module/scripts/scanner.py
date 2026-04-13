"""
scan-odoo-module scanner
Chạy qua: python3 - << 'PYEOF' ... PYEOF
Thay MODULE_PATH trước khi chạy.
"""
import os
import ast
import csv
import re
import xml.etree.ElementTree as ET

MODULE_PATH = "/path/to/module"   # ← thay đường dẫn thực tế

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def read_file(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def iter_xml_records(xml_path, model_filter=None):
    """Yield (id, model, fields_dict) từ XML data file."""
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

# ══════════════════════════════════════════════════════════════
# 1. MANIFEST
# ══════════════════════════════════════════════════════════════
manifest_path = os.path.join(MODULE_PATH, "__manifest__.py")
manifest_src  = read_file(manifest_path)
manifest = {}
try:
    manifest = ast.literal_eval(manifest_src)
except Exception:
    pass

mod_name    = manifest.get("name", os.path.basename(MODULE_PATH))
mod_version = manifest.get("version", "?")
mod_depends = manifest.get("depends", [])
data_files  = manifest.get("data", [])

# ══════════════════════════════════════════════════════════════
# 2. MODELS
# ══════════════════════════════════════════════════════════════
models_dir = os.path.join(MODULE_PATH, "models")
model_reports = []

for fname in sorted(os.listdir(models_dir)) if os.path.isdir(models_dir) else []:
    if not fname.endswith(".py") or fname.startswith("__"):
        continue
    fpath = os.path.join(models_dir, fname)
    src   = read_file(fpath)

    try:
        tree = ast.parse(src)
    except SyntaxError:
        model_reports.append({"file": fname, "status": "PARSE_ERROR", "classes": []})
        continue

    classes = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        # _name / _inherit
        model_name = None
        inherit    = None
        fields_added = []
        methods    = []
        sql_constr = False
        api_constr = False

        for item in node.body:
            if isinstance(item, ast.Assign):
                for t in item.targets:
                    if isinstance(t, ast.Name):
                        if t.id == "_name" and isinstance(item.value, ast.Constant):
                            model_name = item.value.value
                        elif t.id == "_inherit":
                            if isinstance(item.value, ast.Constant):
                                inherit = item.value.value
                            elif isinstance(item.value, ast.List):
                                inherit = [e.value for e in item.value.elts if isinstance(e, ast.Constant)]
                        elif t.id == "_sql_constraints":
                            sql_constr = True

            elif isinstance(item, ast.AnnAssign):
                pass  # fields declared with type annotation (rare in Odoo)

            elif isinstance(item, ast.Assign):
                pass

        # Detect Odoo fields (fields.Xxx(...))
        for node2 in ast.walk(node):
            if isinstance(node2, ast.Assign):
                for t in node2.targets:
                    if isinstance(t, ast.Name):
                        if isinstance(node2.value, ast.Call):
                            func = node2.value.func
                            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                                if func.value.id == "fields":
                                    fields_added.append(f"{t.id} ({func.attr})")
            elif isinstance(node2, ast.FunctionDef):
                if node2.name.startswith("_") or node2.name.startswith("action_") or node2.name.startswith("button_"):
                    # skip __init__ etc unless meaningful
                    if node2.name not in ("__init__",):
                        methods.append(node2.name)
                for deco in node2.decorator_list:
                    if isinstance(deco, ast.Attribute) and deco.attr == "constrains":
                        api_constr = True

        identifier = model_name or (inherit if isinstance(inherit, str) else str(inherit))
        is_empty   = (not fields_added and not methods and not sql_constr and not api_constr)
        status     = "EMPTY" if is_empty else "OK"

        classes.append({
            "class":    node.name,
            "model":    model_name,
            "inherit":  inherit,
            "fields":   fields_added,
            "methods":  [m for m in methods if m not in ("__init__",)][:15],  # cap at 15
            "sql_constr": sql_constr,
            "api_constr": api_constr,
            "status":   status,
        })

    model_reports.append({"file": fname, "classes": classes})

# ══════════════════════════════════════════════════════════════
# 3. SECURITY
# ══════════════════════════════════════════════════════════════
sec_dir  = os.path.join(MODULE_PATH, "security")
groups   = []
rules    = []
acl_rows = []

# security.xml
sec_xml = os.path.join(sec_dir, "security.xml")
for rid, model, fields in iter_xml_records(sec_xml, {"res.groups", "ir.rule"}):
    if model == "res.groups":
        groups.append({"id": rid, "name": fields.get("name", "?")})
    elif model == "ir.rule":
        rules.append({
            "id":     rid,
            "name":   fields.get("name", "?"),
            "model":  fields.get("model_id", "?"),
            "domain": fields.get("domain_force", "?")[:80],
        })

# ir.model.access.csv
acl_path = os.path.join(sec_dir, "ir.model.access.csv")
acl_src  = read_file(acl_path)
if acl_src:
    reader = csv.DictReader(acl_src.splitlines())
    for row in reader:
        acl_rows.append({
            "model":   row.get("model_id:id", "?"),
            "group":   row.get("group_id:id", "?"),
            "r": row.get("perm_read","0"),
            "w": row.get("perm_write","0"),
            "c": row.get("perm_create","0"),
            "d": row.get("perm_unlink","0"),
        })

# ══════════════════════════════════════════════════════════════
# 4. VIEWS
# ══════════════════════════════════════════════════════════════
views_dir = os.path.join(MODULE_PATH, "views")
view_reports = []

for fname in sorted(os.listdir(views_dir)) if os.path.isdir(views_dir) else []:
    if not fname.endswith(".xml"):
        continue
    fpath = os.path.join(views_dir, fname)
    content = read_file(fpath)
    models_ref  = set(re.findall(r'model="([a-z_.]+)"', content))
    view_types  = set(re.findall(r'<(?:form|list|tree|search|kanban|pivot|graph)\b', content))
    menu_count  = content.count('<menuitem')
    action_count = content.count('ir.actions')
    view_reports.append({
        "file":    fname,
        "models":  sorted(models_ref),
        "types":   sorted(t.lstrip("<") for t in view_types),
        "menus":   menu_count,
        "actions": action_count,
    })

# ══════════════════════════════════════════════════════════════
# 5. DATA FILES
# ══════════════════════════════════════════════════════════════
data_dir = os.path.join(MODULE_PATH, "data")
data_reports = []

for fname in sorted(os.listdir(data_dir)) if os.path.isdir(data_dir) else []:
    fpath = os.path.join(data_dir, fname)
    content = read_file(fpath)
    seqs    = len(re.findall(r'ir\.sequence', content))
    crons   = len(re.findall(r'ir\.cron', content))
    params  = len(re.findall(r'ir\.config_parameter', content))
    data_reports.append({"file": fname, "sequences": seqs, "crons": crons, "params": params})

# ══════════════════════════════════════════════════════════════
# 6. WARNINGS
# ══════════════════════════════════════════════════════════════
warnings = []

for mr in model_reports:
    for cls in mr.get("classes", []):
        if cls["status"] == "EMPTY":
            label = cls["model"] or (cls["inherit"] if isinstance(cls["inherit"], str) else str(cls["inherit"]))
            warnings.append(f"models/{mr['file']} — class `{cls['class']}` ({label}): rỗng (_inherit only, không có field/method)")

# Models in ACL but no xml record → just note
acl_models = {r["model"] for r in acl_rows}

# ══════════════════════════════════════════════════════════════
# 7. OUTPUT
# ══════════════════════════════════════════════════════════════
print(f"\n📦 MODULE: {mod_name}  v{mod_version}")
print(f"   Depends : {', '.join(mod_depends)}")
print(f"   Files   : {len(data_files)} data files registered in manifest")

print(f"\n{'='*65}")
print("🔐 SECURITY")
print(f"   Groups  : {len(groups)}")
for g in groups:
    print(f"     [{g['id']}] {g['name']}")
print(f"   Rules   : {len(rules)}")
for r in rules:
    print(f"     [{r['id']}] {r['name']}  model={r['model']}")
    print(f"       domain: {r['domain']}")
print(f"   ACL rows: {len(acl_rows)}")
for a in acl_rows:
    perms = f"r={a['r']} w={a['w']} c={a['c']} d={a['d']}"
    print(f"     {a['model']:<45} group={a['group']:<35} {perms}")

print(f"\n{'='*65}")
print("🗃️  MODELS")
for mr in model_reports:
    if not mr.get("classes"):
        continue
    for cls in mr["classes"]:
        ident = cls["model"] or (cls["inherit"] if isinstance(cls["inherit"], str) else str(cls["inherit"]))
        tag   = f"⚠️  {cls['status']}" if cls["status"] != "OK" else "✅ OK"
        print(f"\n  [{tag}] {ident}  (file: models/{mr['file']}, class: {cls['class']})")
        if cls["inherit"]:
            print(f"    _inherit : {cls['inherit']}")
        if cls["fields"]:
            print(f"    Fields   : {', '.join(cls['fields'])}")
        if cls["methods"]:
            print(f"    Methods  : {', '.join(cls['methods'])}")
        if cls["sql_constr"]:
            print(f"    _sql_constraints : YES")
        if cls["api_constr"]:
            print(f"    @api.constrains  : YES")

print(f"\n{'='*65}")
print("👁️  VIEWS")
for vr in view_reports:
    print(f"  {vr['file']}")
    print(f"    Models : {', '.join(vr['models']) or '(none)'}")
    print(f"    Types  : {', '.join(vr['types']) or '(none)'}  | Menus: {vr['menus']} | Actions: {vr['actions']}")

print(f"\n{'='*65}")
print("📄 DATA FILES")
for dr in data_reports:
    print(f"  {dr['file']}  sequences={dr['sequences']}  crons={dr['crons']}  params={dr['params']}")

if warnings:
    print(f"\n{'='*65}")
    print("⚠️  WARNINGS")
    for w in warnings:
        print(f"  • {w}")
else:
    print("\n✅ Không có warnings")
