"""Per-name reference check for the 18 'unused' mixins.

For each name, count references outside its own definition file by category:
  - imports (`import X`, `from .. import X`)
  - isinstance / issubclass usage
  - direct instantiation `X(`
  - test files (`tests/`)
  - re-exports in __init__.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
NAMES = [
    "ASTEnforcementMixin",
    "AppsTracingMixin",
    "CognitiveRecoveryMixin",
    "FeatureFlaggedAgentMixin",
    "HealerAgentMixin",
    "HealingMixin",
    "HygieneMixin",
    "L2SelfTestingMixin",
    "ReplayGuardMixin",
    "SafetyAnalysisMixin",
    "SecretsManagementMixin",
    "StateAnalysisMixin",
    "TestGetBundledMixin",
    "TestGetI0Mixin",
    "TestIsBundledMixin",
    "_EmbeddingMixin",
    "_MissingDependencyMixin",
    "_SemanticCacheMixin",
]
EXCLUDE_DIRS = {
    "archives",
    "tools_graveyard_w5.12",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "_smoke_v1_coerce_e9aa09",
}


def own_def_files(name: str) -> set[str]:
    """Files that contain `class <name>(...)` or `class <name>:`."""
    pat = re.compile(rf"^\s*class\s+{re.escape(name)}\b", re.MULTILINE)
    out = set()
    for py in REPO.rglob("*.py"):
        if set(py.relative_to(REPO).parts) & EXCLUDE_DIRS:
            continue
        try:
            txt = py.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if pat.search(txt):
            out.add(str(py.relative_to(REPO)).replace("\\", "/"))
    return out


def find_refs(name: str, own_defs: set[str]) -> dict:
    word = re.compile(rf"\b{re.escape(name)}\b")
    isinst = re.compile(rf"\b(isinstance|issubclass)\s*\([^)]*\b{re.escape(name)}\b")
    instant = re.compile(rf"\b{re.escape(name)}\s*\(")
    imp = re.compile(
        rf"\bimport\s+[\w.,\s]*\b{re.escape(name)}\b|\bfrom\s+[\w.]+\s+import\s+[\w.,\s]*\b{re.escape(name)}\b"
    )
    cats: dict[str, list[str]] = {
        "test_files": [],
        "imports": [],
        "isinstance": [],
        "instantiations": [],
        "init_reexports": [],
        "other": [],
    }
    for py in REPO.rglob("*.py"):
        rel = str(py.relative_to(REPO)).replace("\\", "/")
        if set(py.relative_to(REPO).parts) & EXCLUDE_DIRS:
            continue
        if rel in own_defs:
            continue
        try:
            txt = py.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if not word.search(txt):
            continue
        is_test = rel.startswith("tests/") or "/test_" in rel or rel.endswith("_test.py")
        is_init = py.name == "__init__.py"
        if is_test:
            cats["test_files"].append(rel)
        if is_init:
            cats["init_reexports"].append(rel)
        if imp.search(txt):
            cats["imports"].append(rel)
        if isinst.search(txt):
            cats["isinstance"].append(rel)
        if instant.search(txt):
            cats["instantiations"].append(rel)
        if not (is_test or is_init or imp.search(txt) or isinst.search(txt) or instant.search(txt)):
            cats["other"].append(rel)
    return {k: sorted(set(v)) for k, v in cats.items()}


report: dict[str, dict] = {}
for name in NAMES:
    defs = own_def_files(name)
    refs = find_refs(name, defs)
    total = sum(len(v) for v in refs.values())
    report[name] = {"defined_in": sorted(defs), "total_external_refs": total, "refs": refs}

out = REPO / "docs" / "reports" / "plans" / "mixin_unused_verification.json"
out.write_text(json.dumps(report, indent=2), encoding="utf-8")

# Print summary
print(f"{'NAME':40s}  {'DEFS':>4s}  {'EXT':>4s}  STATUS")
for name in NAMES:
    r = report[name]
    n_defs = len(r["defined_in"])
    n_ext = r["total_external_refs"]
    if n_ext == 0:
        status = "TRULY UNUSED — safe to delete"
    elif r["refs"]["test_files"] and not (r["refs"]["imports"] or r["refs"]["instantiations"]):
        status = "test-only (delete test + def)"
    elif r["refs"]["init_reexports"]:
        status = "re-exported in __init__ (audit needed)"
    elif r["refs"]["instantiations"] or r["refs"]["isinstance"]:
        status = "ACTIVELY USED (do not delete)"
    elif r["refs"]["imports"]:
        status = "imported but no class-base (still in use)"
    else:
        status = "referenced (other)"
    print(f"{name:40s}  {n_defs:4d}  {n_ext:4d}  {status}")
print(f"\n# Full report: {out}")
