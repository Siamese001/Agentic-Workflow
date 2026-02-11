"""One-shot discovery script to generate KNOWN_DEBT sets for all gates.

Run: python tests/contracts/_discover_debt.py
"""

import ast
import json
import sys

sys.path.insert(0, ".")  # guardian: allow-global_mutation

from tests.contracts._scanner import (
    AGENT_FILENAME_RE,
    AGENTIC_CORE,
    APPROVED_GUARD_DECORATORS,
    ARTIFACT_CALL_NAMES,
    ARTIFACT_CLASS_NAMES,
    FORBIDDEN_TEST_MODULES,
    FORBIDDEN_TEST_PREFIXES,
    KNOWN_SOVEREIGN_BASES,
    PROJECT_ROOT,
    ast_contains_call,
    ast_contains_name,
    collect_reasoning_agent_files,
    find_agent_class,
    find_method,
    get_all_imports,
    get_class_base_names,
    get_decorator_names,
    get_top_level_classes,
    is_stub_body,
    parse_file_ast,
    rel,
)

files = collect_reasoning_agent_files()
all_rels = sorted(rel(f) for f in files)


def emit_frozenset(name, paths):
    print(f"{name}: frozenset[str] = frozenset({{")
    for p in sorted(paths):
        print(f'    "{p}",')
    print("})")
    print()


# Phase 1
p1 = set()
for f in files:
    tree = parse_file_ast(f)
    if tree is None:
        continue
    stem = f.stem
    issues = []
    if not AGENT_FILENAME_RE.match(f.name):
        issues.append("fn")
    all_cls = get_top_level_classes(tree)
    pub = [c for c in all_cls if not c.name.startswith("_")]
    agents = [c for c in pub if c.name.endswith("Agent")]
    if len(agents) == 0:
        issues.append("no_agent")
    elif len(agents) > 1:
        issues.append("multi_agent")
    else:
        if agents[0].name != stem:
            issues.append("mismatch")
    non_agent = [c for c in pub if not c.name.endswith("Agent")]
    if non_agent:
        issues.append("extra_pub")
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.endswith("Agent"):
                    if isinstance(node.value, ast.Name):
                        issues.append("alias")
    if issues:
        p1.add(rel(f))
emit_frozenset("KNOWN_DEBT_P1", p1)

# Phase 2
p2 = set()
for f in files:
    tree = parse_file_ast(f)
    if tree is None:
        continue
    stem = f.stem
    agent_cls = find_agent_class(tree, stem)
    if agent_cls is None:
        all_cls = get_top_level_classes(tree)
        ac = [c for c in all_cls if c.name.endswith("Agent") and not c.name.startswith("_")]
        agent_cls = ac[0] if len(ac) == 1 else None
    if agent_cls is None:
        p2.add(rel(f))
        continue
    bases = get_class_base_names(agent_cls)
    has_sov = any(b in KNOWN_SOVEREIGN_BASES for b in bases)
    if not has_sov:
        p2.add(rel(f))
emit_frozenset("KNOWN_DEBT_P2", p2)

# Phase 3
p3 = set()
for f in files:
    tree = parse_file_ast(f)
    if tree is None:
        continue
    stem = f.stem
    agent_cls = find_agent_class(tree, stem)
    if agent_cls is None:
        all_cls = get_top_level_classes(tree)
        ac = [c for c in all_cls if c.name.endswith("Agent") and not c.name.startswith("_")]
        agent_cls = ac[0] if len(ac) == 1 else None
    if agent_cls is None:
        p3.add(rel(f))
        continue
    em = find_method(agent_cls, "execute")
    if em is None:
        p3.add(rel(f))
        continue
    args = em.args
    if args.kwarg is None and args.vararg is None and not args.kwonlyargs:
        p3.add(rel(f))
        continue
    if is_stub_body(em.body):
        p3.add(rel(f))
emit_frozenset("KNOWN_DEBT_P3", p3)

# Phase 4
p4 = set()
for f in files:
    tree = parse_file_ast(f)
    if tree is None:
        continue
    stem = f.stem
    agent_cls = find_agent_class(tree, stem)
    if agent_cls is None:
        all_cls = get_top_level_classes(tree)
        ac = [c for c in all_cls if c.name.endswith("Agent") and not c.name.startswith("_")]
        agent_cls = ac[0] if len(ac) == 1 else None
    if agent_cls is None:
        p4.add(rel(f))
        continue
    em = find_method(agent_cls, "execute")
    has_guard = False
    if em:
        ed = get_decorator_names(em)
        if any(d in APPROVED_GUARD_DECORATORS for d in ed):
            has_guard = True
    if not has_guard:
        cd = get_decorator_names(agent_cls)
        if any(d in APPROVED_GUARD_DECORATORS for d in cd):
            has_guard = True
    if not has_guard:
        p4.add(rel(f))
emit_frozenset("KNOWN_DEBT_P4", p4)

# Phase 5
p5 = set()
for f in files:
    tree = parse_file_ast(f)
    if tree is None:
        continue
    stem = f.stem
    agent_cls = find_agent_class(tree, stem)
    if agent_cls is None:
        all_cls = get_top_level_classes(tree)
        ac = [c for c in all_cls if c.name.endswith("Agent") and not c.name.startswith("_")]
        agent_cls = ac[0] if len(ac) == 1 else None
    if agent_cls is None:
        p5.add(rel(f))
        continue
    em = find_method(agent_cls, "execute")
    if em is None:
        p5.add(rel(f))
        continue
    has_art = ast_contains_call(em, ARTIFACT_CALL_NAMES)
    if not has_art:
        has_art = ast_contains_name(em, ARTIFACT_CLASS_NAMES)
    if not has_art:
        for child in ast.walk(em):
            if isinstance(child, ast.Dict):
                for key in child.keys:
                    if isinstance(key, ast.Constant) and isinstance(key.value, str):
                        if key.value in ("artifacts", "artifact", "results", "output"):
                            has_art = True
                            break
            if has_art:
                break
    if not has_art:
        p5.add(rel(f))
emit_frozenset("KNOWN_DEBT_P5", p5)

# Phase 6
prod_imports = set()
PROD_ROOTS = [
    AGENTIC_CORE,
    PROJECT_ROOT / "apps_rg",
    PROJECT_ROOT / "apps_lic",
    PROJECT_ROOT / "apps_shared",
    PROJECT_ROOT / "ops_scripts",
]
for root_dir in PROD_ROOTS:
    if not root_dir.exists():
        continue
    for py_file in root_dir.rglob("*.py"):
        try:
            src = py_file.read_text(encoding="utf-8")
            t = ast.parse(src)
        except Exception:  # guardian: allow-silent_swallower
            continue
        for n in ast.walk(t):
            if isinstance(n, ast.ImportFrom) and n.names:
                for a in n.names:
                    if a.name.endswith("Agent"):
                        prod_imports.add(a.name)
            elif isinstance(n, ast.Import):
                for a in n.names:
                    parts = a.name.split(".")
                    if parts[-1].endswith("Agent"):
                        prod_imports.add(parts[-1])

reg = set()
rp = PROJECT_ROOT / "agent_discovery_full.json"
if rp.exists():
    try:
        data = json.loads(rp.read_text(encoding="utf-8"))
        if isinstance(data, list):
            for e in data:
                cn = e.get("class_name", "")
                if cn:
                    reg.add(cn)
        elif isinstance(data, dict):
            for e in data.get("agents", data.get("entries", [])):
                cn = e.get("class_name", e.get("name", ""))
                if cn:
                    reg.add(cn)
    except Exception:  # guardian: allow-silent_swallower
        pass

p6 = set()
for f in files:
    tree = parse_file_ast(f)
    if tree is None:
        continue
    stem = f.stem
    if stem not in prod_imports and stem not in reg:
        p6.add(rel(f))
emit_frozenset("KNOWN_DEBT_P6", p6)

# Phase 7
p7 = set()
for f in files:
    tree = parse_file_ast(f)
    if tree is None:
        continue
    imports = get_all_imports(tree)
    has_forbidden = False
    for mod, ln in imports:
        top = mod.split(".")[0]
        if top in FORBIDDEN_TEST_MODULES:
            has_forbidden = True
            break
        for pfx in FORBIDDEN_TEST_PREFIXES:
            if mod.startswith(pfx):
                has_forbidden = True
                break
        if has_forbidden:
            break
    if has_forbidden:
        p7.add(rel(f))
emit_frozenset("KNOWN_DEBT_P7", p7)

# Summary
print("# Summary")
print(f"# Files scanned: {len(files)}")
print(f"# P1 (structural identity): {len(p1)}")
print(f"# P2 (inheritance):         {len(p2)}")
print(f"# P3 (execute contract):    {len(p3)}")
print(f"# P4 (guard integration):   {len(p4)}")
print(f"# P5 (artifact emission):   {len(p5)}")
print(f"# P6 (reachability):        {len(p6)}")
print(f"# P7 (prod hygiene):        {len(p7)}")
