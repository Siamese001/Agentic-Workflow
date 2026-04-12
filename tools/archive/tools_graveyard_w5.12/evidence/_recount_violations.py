"""Recount current fan_in>=3 violations after skeleton generation."""

from __future__ import annotations

import ast
import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through

_emit_reads_through("l4", "_recount_violations", "urg_read_1")
_emit_reads_through("l4", "_recount_violations", "urg_read_2")
_emit_reads_through("l4", "_recount_violations", "urg_read_3")
_emit_reads_through("l4", "_recount_violations", "urg_read_4")
_emit_reads_through("l4", "_recount_violations", "urg_read_5")
_emit_reads_through("l4", "_recount_violations", "urg_read_6")
_emit_reads_through("l4", "_recount_violations", "urg_read_7")
_emit_reads_through("l4", "_recount_violations", "urg_read_8")
_emit_reads_through("l4", "_recount_violations", "urg_read_9")
_emit_reads_through("l4", "_recount_violations", "urg_read_10")
_emit_reads_through("l4", "_recount_violations", "urg_read_11")
_emit_reads_through("l4", "_recount_violations", "urg_read_12")
_emit_reads_through("l4", "_recount_violations", "urg_read_13")
_emit_reads_through("l4", "_recount_violations", "urg_read_14")
_emit_reads_through("l4", "_recount_violations", "urg_read_15")
ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_INTERNAL_PREFIXES = (
    "agentic_core",
    "apps_rg",
    "apps_lic",
    "apps_shared",
    "system_learning",
    "ops_scripts",
)
FAN_IN_THRESHOLD = 3
FOUNDATIONAL_DEPTH_MIN = 1


def _is_prod(path: str) -> bool:
    p = path.replace("\\", "/")
    return (
        not p.startswith("tests/")
        and not p.startswith("tools/")
        and "ops_scripts" not in p
        and "__pycache__" not in p
        and p.endswith(".py")
    )


def _collect_prod() -> list[str]:
    modules = []
    for pkg in _INTERNAL_PREFIXES:
        d = ROOT / pkg
        if not d.exists():
            continue
        for f in d.rglob("*.py"):
            if "__pycache__" in f.parts:
                continue
            rel = str(f.relative_to(ROOT)).replace("\\", "/")
            if _is_prod(rel):
                modules.append(rel)
    return sorted(modules)


def _build_fan_in(prod: list[str]) -> dict[str, int]:
    dotted = {m.removesuffix(".py").replace("/", "."): m for m in prod}
    fan_in: dict[str, int] = defaultdict(int)
    for m in prod:
        try:
            tree = ast.parse((ROOT / m).read_text(encoding="utf-8", errors="replace"))
        # guardian: allow-silent-swallow
        except Exception:
            continue
        for node in ast.walk(tree):
            targets = []
            if isinstance(node, ast.Import):
                for a in node.names:
                    targets.append(a.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    targets.append(node.module)
                    parent = ".".join(node.module.rsplit(".", 1)[:-1])
                    if parent:
                        targets.append(parent)
            for t in targets:
                if t in dotted:
                    fan_in[dotted[t]] += 1
                p = ".".join(t.rsplit(".", 1)[:-1])
                if p in dotted:
                    fan_in[dotted[p]] += 1
    return dict(fan_in)


def _count_asserts(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    # guardian: allow-silent-swallow
    except Exception:
        return 0
    n = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            n += 1
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "raises":
                n += 1
    return n


def _has_foundational(module_path: str) -> bool:
    parts = Path(module_path).parts
    stem = Path(parts[-1]).stem
    test_dir = ROOT / "tests" / "unit" / Path(*parts[:-1])
    if test_dir.exists():
        for f in test_dir.iterdir():
            if (
                f.name.startswith(f"test_{stem}")
                and f.suffix == ".py"
                and not f.name.endswith("_adg.py")
                and _count_asserts(f) >= FOUNDATIONAL_DEPTH_MIN
            ):
                return True
    # also check unit_min_deps
    for f in (ROOT / "tests" / "unit_min_deps").glob(f"test_{stem}*.py"):
        if not f.name.endswith("_adg.py") and _count_asserts(f) >= FOUNDATIONAL_DEPTH_MIN:
            return True
    return False


prod = _collect_prod()
fi = _build_fan_in(prod)

violations = [
    {"module": m, "fan_in": fi.get(m, 0)}
    for m in prod
    if fi.get(m, 0) >= FAN_IN_THRESHOLD and not _has_foundational(m)
]
violations.sort(key=lambda x: -x["fan_in"])

above = [m for m in prod if fi.get(m, 0) >= FAN_IN_THRESHOLD]
print(f"Production modules:              {len(prod)}")
print(f"Above fan_in>={FAN_IN_THRESHOLD} threshold:       {len(above)}")
print(f"Current violations:              {len(violations)}")
print(f"Resolved since snapshot (133):   {133 - len(violations)}")
print()
print(f"{'fan_in':>8}  module")
for v in violations:
    print(f"  {v['fan_in']:>6}  {v['module']}")
