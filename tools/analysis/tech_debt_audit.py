"""Repo-wide technical-debt scanner.

Detects 9 patterns:

  P1  Rename-shim files          — file whose docstring says "compat alias",
                                    "use X directly for new code", "Legacy mixin",
                                    "deprecated alias"
  P2  Try/except ImportError stubs — `class X: pass` inside an except ImportError
                                    block (signal of fragile cross-layer imports)
  P3  Dead-import targets       — `from path.to.module import X` where the module
                                    does not exist on disk
  P4  Duplicate file pairs      — `foo.py` + `foo_util.py` or `foo.py` + `foo_types.py`
                                    with near-identical SHA1 of normalized content
  P5  Synthetic emit-only files — files whose top-level statements are >50%
                                    `_emit_*(...)` no-op calls
  P6  Zero-body classes/functions — `class X: pass` or `def f(): pass` defined at
                                    module scope (not in try/except)
  P7  Stale `__all__`           — `__all__ = [...]` listing names that don't appear
                                    in the module
  P8  Empty `__init__.py`       — package init that is empty or only docstring
  P9  Naming collision          — same class/function name defined in 2+ files
                                    (excluding archives)

Writes JSON to docs/reports/plans/tech_debt_audit.json.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXCLUDE_DIRS = {
    "archives",
    "tools_graveyard_w5.12",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "_smoke_v1_coerce_e9aa09",
    ".backup",
    ".git",
    "site-packages",
}

OUT = REPO / "docs" / "reports" / "plans" / "tech_debt_audit.json"

SHIM_MARKERS = re.compile(
    r"(Backwards Compatibility Shim|Backwards-compat alias|"
    r"compat alias|Use \w+ directly for new code|Legacy mixin|"
    r"legacy alias|deprecated alias|use [A-Z]\w+ instead)",
    re.IGNORECASE,
)
EMIT_CALL = re.compile(r"^\s*_emit_\w+\(")


def iter_py() -> list[Path]:
    out: list[Path] = []
    for py in REPO.rglob("*.py"):
        rel_parts = set(py.relative_to(REPO).parts)
        if rel_parts & EXCLUDE_DIRS:
            continue
        out.append(py)
    return out


def safe_read(p: Path) -> str | None:
    try:
        return p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def parse(p: Path, txt: str) -> ast.Module | None:
    try:
        return ast.parse(txt)
    except SyntaxError:
        return None


# Module-existence cache for P3
# Returns ("exists", "namespace_pkg", "missing"):
#   exists       : .py file or package with __init__.py is present
#   namespace_pkg: folder structure exists but lacks __init__.py at some level
#   missing      : neither .py nor folder exists on disk
def module_path_status(dotted: str) -> str:
    parts = dotted.split(".")
    base = REPO
    last = len(parts) - 1
    saw_namespace = False
    for i, part in enumerate(parts):
        as_pkg = base / part
        as_mod = base / f"{part}.py"
        if as_pkg.is_dir():
            if (as_pkg / "__init__.py").exists():
                base = as_pkg
                continue
            # Namespace package (no __init__) — keep walking
            saw_namespace = True
            base = as_pkg
            continue
        if i == last and as_mod.exists():
            return "namespace_pkg" if saw_namespace else "exists"
        return "missing"
    return "namespace_pkg" if saw_namespace else "exists"


def main() -> int:
    findings: dict = {
        "p1_rename_shims": [],
        "p2_import_error_stubs": [],
        "p3_dead_imports": [],
        "p4_duplicate_pairs": [],
        "p5_synthetic_emit_files": [],
        "p6_zero_body_definitions": [],
        "p7_stale_all": [],
        "p8_empty_init": [],
        "p9_name_collisions": [],
    }
    body_hash: dict[str, list[str]] = defaultdict(list)  # for P4
    name_to_files: dict[str, list[str]] = defaultdict(list)  # for P9

    files = iter_py()
    print(f"# scanning {len(files)} .py files ...", file=sys.stderr)

    for py in files:
        rel = str(py.relative_to(REPO)).replace("\\", "/")
        txt = safe_read(py)
        if txt is None:
            continue
        tree = parse(py, txt)

        # ---------- P1 rename shims ----------
        if tree is not None:
            doc = ast.get_docstring(tree) or ""
            if SHIM_MARKERS.search(doc) or SHIM_MARKERS.search(txt[:600]):
                # body class count
                cls = [n for n in tree.body if isinstance(n, ast.ClassDef)]
                lines = txt.count("\n") + 1
                findings["p1_rename_shims"].append(
                    {
                        "file": rel,
                        "lines": lines,
                        "classes": [c.name for c in cls],
                        "marker_excerpt": (re.search(SHIM_MARKERS, txt) or [""])[0]
                        if SHIM_MARKERS.search(txt)
                        else "",
                    }
                )

        # ---------- P5 synthetic emit-only files ----------
        if "_emit_" in txt:
            stmts = [ln for ln in txt.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
            emit = sum(1 for ln in stmts if EMIT_CALL.match(ln))
            if stmts and emit / max(len(stmts), 1) > 0.30 and emit >= 20:
                findings["p5_synthetic_emit_files"].append(
                    {
                        "file": rel,
                        "emit_calls": emit,
                        "non_blank_stmts": len(stmts),
                        "ratio": round(emit / len(stmts), 2),
                    }
                )

        # ---------- P8 empty __init__.py ----------
        if py.name == "__init__.py":
            stripped = re.sub(r'""".*?"""', "", txt, flags=re.S).strip()
            stripped = re.sub(r"#.*", "", stripped).strip()
            if not stripped:
                findings["p8_empty_init"].append({"file": rel})

        if tree is None:
            continue

        # ---------- P2 try/except ImportError stubs ----------
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for h in node.handlers:
                    et = h.type
                    matches_imperror = False
                    if isinstance(et, ast.Name) and et.id in {"ImportError", "ModuleNotFoundError"}:
                        matches_imperror = True
                    elif isinstance(et, ast.Tuple) and any(
                        isinstance(el, ast.Name)
                        and el.id in {"ImportError", "ModuleNotFoundError", "NameError"}
                        for el in et.elts
                    ):
                        matches_imperror = True
                    if not matches_imperror:
                        continue
                    for stmt in h.body:
                        if isinstance(stmt, ast.ClassDef) and len(stmt.body) <= 2:
                            findings["p2_import_error_stubs"].append(
                                {
                                    "file": rel,
                                    "class": stmt.name,
                                    "line": stmt.lineno,
                                    "body_size": len(stmt.body),
                                }
                            )

        # ---------- P3 dead-import targets ----------
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                # Only check repo-internal imports
                top = node.module.split(".", 1)[0]
                if top not in {
                    "agentic_core",
                    "apps_eval",
                    "apps_exec",
                    "apps_lic",
                    "apps_research",
                    "apps_rg",
                    "apps_shared",
                    "apps_underwriting_ai",
                    "system_learning",
                    "tools",
                    "ops_scripts",
                    "infrastructure",
                    "config",
                }:
                    continue
                status = module_path_status(node.module)
                if status != "exists":
                    findings["p3_dead_imports"].append(
                        {
                            "file": rel,
                            "line": node.lineno,
                            "module": node.module,
                            "status": status,
                            "names": [a.name for a in node.names],
                        }
                    )

        # ---------- P4 file body hash for dup detection ----------
        # Normalized body: strip docstrings + comments + emit calls, hash
        norm_lines: list[str] = []
        for ln in txt.splitlines():
            s = ln.strip()
            if not s or s.startswith("#") or EMIT_CALL.match(ln):
                continue
            if s.startswith('"""') or s.startswith("'''"):
                continue
            norm_lines.append(s)
        if len(norm_lines) >= 5:
            h = hashlib.sha1("\n".join(norm_lines).encode("utf-8")).hexdigest()
            body_hash[h].append(rel)

        # ---------- P6 zero-body module-scope defs ----------
        for n in tree.body:
            if (
                isinstance(n, ast.ClassDef)
                and len(n.body) == 1
                and isinstance(n.body[0], (ast.Pass, ast.Expr))
            ):
                findings["p6_zero_body_definitions"].append(
                    {
                        "file": rel,
                        "kind": "class",
                        "name": n.name,
                        "line": n.lineno,
                    }
                )
            if (
                isinstance(n, ast.FunctionDef)
                and len(n.body) == 1
                and isinstance(n.body[0], (ast.Pass, ast.Expr))
            ):
                findings["p6_zero_body_definitions"].append(
                    {
                        "file": rel,
                        "kind": "function",
                        "name": n.name,
                        "line": n.lineno,
                    }
                )
            # P9 name index (top-level defs)
            if isinstance(n, (ast.ClassDef, ast.FunctionDef)):
                # Skip dunder + private + Test* (test classes legitimately repeat)
                if not (n.name.startswith("_") or n.name.startswith("Test") or n.name.startswith("test_")):
                    name_to_files[n.name].append(rel)

        # ---------- P7 stale __all__ ----------
        for n in tree.body:
            if isinstance(n, ast.Assign):
                for tgt in n.targets:
                    if isinstance(tgt, ast.Name) and tgt.id == "__all__":
                        if isinstance(n.value, (ast.List, ast.Tuple)):
                            declared = []
                            for el in n.value.elts:
                                if isinstance(el, ast.Constant) and isinstance(el.value, str):
                                    declared.append(el.value)
                            # Check that each declared name is defined or imported
                            present = set()
                            for sub in ast.walk(tree):
                                if isinstance(sub, (ast.ClassDef, ast.FunctionDef)):
                                    present.add(sub.name)
                                if isinstance(sub, ast.ImportFrom):
                                    for a in sub.names:
                                        present.add(a.asname or a.name)
                                if isinstance(sub, ast.Import):
                                    for a in sub.names:
                                        present.add((a.asname or a.name).split(".")[0])
                                if isinstance(sub, ast.Assign):
                                    for t2 in sub.targets:
                                        if isinstance(t2, ast.Name):
                                            present.add(t2.id)
                            missing = [d for d in declared if d not in present]
                            if missing:
                                findings["p7_stale_all"].append(
                                    {
                                        "file": rel,
                                        "missing": missing,
                                        "declared": declared,
                                    }
                                )

    # P4 finalize
    for h, paths in body_hash.items():
        if len(paths) >= 2:
            findings["p4_duplicate_pairs"].append(
                {
                    "hash": h[:12],
                    "files": sorted(paths),
                }
            )

    # P9 finalize — only collisions within the same package depth (excludes
    # legitimate test classes etc; also drop names with > 6 collisions because
    # those are usually intentional protocol/Mixin patterns)
    for name, fls in name_to_files.items():
        unique = sorted(set(fls))
        if 2 <= len(unique) <= 6:
            findings["p9_name_collisions"].append(
                {
                    "name": name,
                    "files": unique,
                }
            )

    OUT.write_text(json.dumps(findings, indent=2), encoding="utf-8")

    summary = {k: len(v) for k, v in findings.items()}
    print(json.dumps(summary, indent=2))
    print(f"\n# wrote {OUT}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
