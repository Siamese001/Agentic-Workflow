"""
Full audit of P0-P3 completion status.
Checks:
  P0: frozenset type bugs (.get() on frozensets), DEPTH_RULES existence
  P1: SCAN_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS, GLOBAL_EXCLUDED_DIRS correctness
  P2: No live SOVEREIGN_TERRITORIES imports in app code (outside structure_blueprint + tests/structure_blueprint)
  P3: No direct sub-module imports (.ssot/.derived/._constants/.territories) outside allowlist
       interfaces/structure_config.py deleted
       no consumers of deleted file
"""
import ast
import re
import sys
from pathlib import Path

ROOT = Path("c:/Git/Agentic-Workflow")
sys.path.insert(0, str(ROOT))

SKIP_PARTS = {"archives", ".healing_backups", ".backup", "__pycache__", ".git"}


def _rglob_py(directory):
    p = ROOT / directory
    if not p.exists():
        return []
    results = []
    for f in p.rglob("*.py"):
        if any(part in SKIP_PARTS for part in f.parts):
            continue
        results.append(f)
    return results


# ─── P0 checks ───────────────────────────────────────────────────────────────
print("=" * 60)
print("P0: DEPTH_RULES existence and type")
try:
    from agentic_core.L5_safety.config.structure_blueprint import DEPTH_RULES
    assert isinstance(DEPTH_RULES, dict), f"DEPTH_RULES is {type(DEPTH_RULES)}"
    print(f"  [OK] DEPTH_RULES is dict with {len(DEPTH_RULES)} entries")
except Exception as e:
    print(f"  [FAIL] {e}")

print("P0: frozenset .get() bug scan")
frozenset_names = ["ENFORCED_TERRITORIES", "CODE_TERRITORIES", "VOLATILE_TERRITORIES",
                   "LAYER_PREFIX_EXEMPT_TERRITORIES", "ALLOW_ROOT_PY_TERRITORIES",
                   "PROJECT_ROOT_WHITELIST"]
pattern_get = re.compile(r'(' + '|'.join(frozenset_names) + r')\.get\(')
p0_hits = []
for f in _rglob_py("agentic_core") + _rglob_py("apps_lic") + _rglob_py("apps_rg") + _rglob_py("apps_shared"):
    src = f.read_text(encoding="utf-8", errors="ignore")
    if pattern_get.search(src):
        lines = [(i+1, l.strip()[:100]) for i, l in enumerate(src.splitlines())
                 if pattern_get.search(l) and not l.strip().startswith("#")]
        if lines:
            p0_hits.append((str(f.relative_to(ROOT)), lines))
if p0_hits:
    print(f"  [FAIL] frozenset .get() calls: {len(p0_hits)}")
    for fname, lines in p0_hits:
        print(f"    {fname}")
        for ln, l in lines[:2]:
            print(f"      L{ln}: {l}")
else:
    print("  [OK] Zero frozenset .get() calls")

# ─── P1 checks ───────────────────────────────────────────────────────────────
print("=" * 60)
print("P1: SCAN_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS, GLOBAL_EXCLUDED_DIRS")
try:
    from agentic_core.L5_safety.config.structure_blueprint import (
        GLOBAL_EXCLUDED_DIRS,
        SCAN_EXCLUDED_DIRS,
        SOVEREIGN_EXCLUDED_FOLDERS,
    )
    bad = {"data", "docs", "tests", "reports"}
    both = bad & (SOVEREIGN_EXCLUDED_FOLDERS | GLOBAL_EXCLUDED_DIRS)
    if both:
        print(f"  [FAIL] Real directories in exclusion sets: {both}")
    else:
        print("  [OK] No real dirs in exclusion sets")
    print(f"  [OK] SCAN_EXCLUDED_DIRS exists ({len(SCAN_EXCLUDED_DIRS)} entries)")
except Exception as e:
    print(f"  [FAIL] {e}")

# ─── P2 checks ───────────────────────────────────────────────────────────────
print("=" * 60)
print("P2: Live SOVEREIGN_TERRITORIES usage (imports only, non-comment)")

SKIP_P2 = SKIP_PARTS | {"structure_blueprint", "tests"}
st_import = re.compile(r'^(?!#).*(?:import|from)\s.*SOVEREIGN_TERRITORIES')

p2_hits = []
for f in ROOT.rglob("*.py"):
    if any(part in SKIP_P2 for part in f.parts):
        continue
    try:
        src = f.read_text(encoding="utf-8", errors="ignore")
    except (ValueError, TypeError, RuntimeError) as e:
        continue
    lines = []
    for i, line in enumerate(src.splitlines()):
        s = line.strip()
        if "SOVEREIGN_TERRITORIES" not in s:
            continue
        if s.startswith("#") or s.startswith('"""') or s.startswith("'''"):
            continue
        if "SOVEREIGN_TERRITORIES" in s and ("import" in s or "= SOVEREIGN" in s or "SOVEREIGN_TERRITORIES[" in s or "SOVEREIGN_TERRITORIES." in s or "SOVEREIGN_TERRITORIES)" in s):
            lines.append((i+1, s[:100]))
    if lines:
        p2_hits.append((str(f.relative_to(ROOT)), lines))

if p2_hits:
    print(f"  [FAIL] {len(p2_hits)} files with live SOVEREIGN_TERRITORIES usage:")
    for fname, lines in p2_hits:
        print(f"    {fname}")
        for ln, l in lines[:3]:
            print(f"      L{ln}: {l}")
else:
    print("  [OK] Zero live SOVEREIGN_TERRITORIES in app code")

# ─── P3 checks ───────────────────────────────────────────────────────────────
print("=" * 60)
print("P3a: interfaces/structure_config.py deleted")
f_sc = ROOT / "agentic_core/interfaces/structure_config.py"
print(f"  [{'OK' if not f_sc.exists() else 'FAIL'}] deleted={not f_sc.exists()}")

print("P3b: No consumers of interfaces.structure_config")
pattern_sc = re.compile(r"interfaces[./\\]structure_config|interfaces\.structure_config")
consumers = [str(f.relative_to(ROOT)) for f in ROOT.rglob("*.py")
             if not any(p in SKIP_PARTS for p in f.parts)
             and "structure_config.py" not in str(f)
             and pattern_sc.search(f.read_text(encoding="utf-8", errors="ignore"))]
print(f"  [{'OK' if not consumers else 'FAIL'}] consumers={consumers}")

print("P3c: Direct sub-module imports in production code")
FORBIDDEN_SUBMODULE_PREFIXES = [
    "agentic_core.L5_safety.config.structure_blueprint._constants",
    "agentic_core.L5_safety.config.structure_blueprint.territories",
    "agentic_core.L5_safety.config.structure_blueprint.ssot",
    "agentic_core.L5_safety.config.structure_blueprint.derived",
    "agentic_core.L5_safety.config.structure_blueprint.governance",
]
ALLOWED_DIRECT_PREFIXES = [
    "agentic_core/L5_safety/config/structure_blueprint",
    "agentic_core/L5_safety/enforcement",
    "agentic_core/L5_safety/reasoning",
    "agentic_core/L5_safety/validators",
    "agentic_core/L5_safety/governance",
    "agentic_core/L5_safety/utils",
    "agentic_core/L5_safety/types",
    "agentic_core/L0_routing/scripts",
    "agentic_core/L0_routing/utils",
    "agentic_core/L0_routing/reasoning",
    "agentic_core/L0_routing/types",
    "ops_scripts",
    "tools",
    "tests",
    "docs",
]

def is_allowed(rel):
    rel_norm = rel.replace("\\", "/")
    return any(rel_norm.startswith(p) for p in ALLOWED_DIRECT_PREFIXES)

p3c_hits = []
for f in ROOT.rglob("*.py"):
    if any(part in SKIP_PARTS for part in f.parts):
        continue
    rel = str(f.relative_to(ROOT))
    if is_allowed(rel):
        continue
    try:
        src = f.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(src)
    except (ValueError, TypeError, RuntimeError) as e:
        continue
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if any(mod.startswith(p) for p in FORBIDDEN_SUBMODULE_PREFIXES):
                bad.append(mod)
    if bad:
        p3c_hits.append((rel, bad))

if p3c_hits:
    print(f"  [FAIL] {len(p3c_hits)} files with direct sub-module imports:")
    for fname, mods in p3c_hits:
        print(f"    {fname}: {mods}")
else:
    print("  [OK] Zero direct sub-module imports in production code")

# ─── CI gate ─────────────────────────────────────────────────────────────────
print("=" * 60)
print("Running registry_config import test")
try:
    from agentic_core.config.registry_config import SOVEREIGN_REGISTRY
    print(f"  [OK] SOVEREIGN_REGISTRY: {len(SOVEREIGN_REGISTRY)} entries")
except Exception as e:
    print(f"  [FAIL] {e}")

print("Running syntax checks on all edited files")
edited_files = [
    "agentic_core/L5_safety/reasoning/hierarchy_healer.py",
    "agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py",
    "agentic_core/L5_safety/reasoning/location_validator.py",
    "agentic_core/config/core/registry_config.py",
    "ops_scripts/dev_tools/l0_scripts/generate_hooks_util.py",
    "agentic_core/L0_routing/scripts/populate_ssot_folders_util.py",
    "agentic_core/L0_routing/scripts/run_guardian_hierarchy_compliance.py",
    "agentic_core/L0_routing/config/__init__.py",
    "agentic_core/L5_safety/reasoning/SystemArchitectAgent.py",
    "agentic_core/L0_routing/scripts/execute_ssot.py",
    "agentic_core/L5_safety/config/structure_blueprint_config.py",
    "apps_lic/tools/clean_duplicates_enhanced.py",
    "apps_lic/tools/fix_duplicate_realagentdata.py",
    "apps_rg/config/void_compliance_config.py",
    "agentic_core/L0_routing/utils/complexity_visitor_util.py",
    "agentic_core/L3_orchestration/scripts/guardian_heal_orchestrator.py",
    "agentic_core/L6_observability/utils/integrity_report_generator_util.py",
    "tests/unit/agentic_core/L5_safety/config/test_structure_blueprint_config.py",
    "tests/unit_min_deps/test_ssot_single_entry_point.py",
]
syntax_fails = []
for rel in edited_files:
    f = ROOT / rel
    if not f.exists():
        syntax_fails.append(f"MISSING: {rel}")
        continue
    try:
        ast.parse(f.read_text(encoding="utf-8"))
    except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        syntax_fails.append(f"SYNTAX L{e.lineno} in {rel}: {e.msg}")

if syntax_fails:
    print(f"  [FAIL] {len(syntax_fails)} syntax issues:")
    for s in syntax_fails:
        print(f"    {s}")
else:
    print(f"  [OK] All {len(edited_files)} files syntax-valid")
