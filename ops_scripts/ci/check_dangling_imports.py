#!/usr/bin/env python3
"""Gate G-DANGLING-IMPORT — broken import-target detector.

Walks the production source tree and flags ``from <pkg>.<mod> import <name>``
or ``import <pkg>.<mod>`` whose target does NOT resolve to a real ``.py`` file
or package (``__init__.py``) on disk.

Also flags ``importlib.import_module(literal)``, ``__import__(literal)``,
``importlib.util.find_spec(literal)`` patterns whose constant string argument
does not resolve. This catches the dynamic-string seam case that the AST
visitor in ``tools/generate/generate_static_adg.py`` cannot see (it captures
the call target ``importlib.import_module`` but never the literal arg).

Tier: B (blocking). On a fresh repo, count MUST be zero. Any new dangling
import is a hard failure — wrong-path imports always indicate either a typo
or a stale reference to a moved/renamed module.

Bypass: ``DANGLING_IMPORT_BYPASS=1`` in env.

Origin: RCA on 2026-04-28 ``full_agent_discovery`` module-load failure
(`agentic_core.L5_safety.core_kernel.classification_kernel` typo) that
existed at HEAD ``8beda0a4`` for 6+ files but no existing CI gate detected
it. See ``docs/reports/plans/`` for the full RCA.
"""

from __future__ import annotations

# W4 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md
# §6 + agentic_core/adg/artifact/consumer_mode.py).
# Dangling imports surface UNRESOLVED_STATIC edges — risk signal, not verdict.
__adg_consumer_mode__ = "risk"

import ast
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Production package roots — anything imported from one of these MUST resolve.
# stdlib + third-party imports are passed through unchanged.
PRODUCTION_PACKAGE_ROOTS = (
    "agentic_core",
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_research",
    "apps_rfp",
    "apps_rg",
    "apps_shared",
    "apps_underwriting_ai",
    "system_learning",
    "ops_scripts",
    "tools",
    "infrastructure",
    "scripts",
)

# Directories the scanner walks for source files.
SCAN_ROOTS = PRODUCTION_PACKAGE_ROOTS

# Dynamic-import call-name patterns to inspect. Each entry is the dotted
# attribute path of the call target as seen by ast.unparse(node.func).
DYNAMIC_IMPORT_CALLS = frozenset(
    {
        "importlib.import_module",
        "import_module",  # bare alias after `from importlib import import_module`
        "__import__",
        "importlib.util.find_spec",
        "find_spec",
    }
)

LOG_DIR = REPO_ROOT / "artifacts" / "windsurf"
LOG_FILE = LOG_DIR / "dangling_import_violations.jsonl"


@dataclass
class DanglingImport:
    source_file: str
    line_no: int
    target_module: str
    kind: str  # "from_import" | "import" | "dynamic_import"
    detail: str = ""


@dataclass
class GateOutcome:
    violations: list[DanglingImport] = field(default_factory=list)
    files_scanned: int = 0
    bypassed: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def build_module_resolver(repo_root: Path) -> set[str]:
    """Scan repo for every ``.py`` file and ``__init__.py`` package; return
    a set of resolvable dotted module paths (e.g. ``agentic_core.L0_routing``,
    ``agentic_core.L0_routing.config.path_constants``).
    """
    resolvable: set[str] = set()
    for root_name in PRODUCTION_PACKAGE_ROOTS:
        # progress_bar: bounded — PRODUCTION_PACKAGE_ROOTS ≤ O(10) entries.
        root = repo_root / root_name
        if not root.is_dir():
            continue
        # Add the package root itself.
        resolvable.add(root_name)
        for path in root.rglob("*.py"):
            # progress_bar: bounded per-iteration (each step is constant-time).
            # rglob is consumed only at module-resolver build time — once per gate run.
            try:
                rel = path.relative_to(repo_root)
            except ValueError:
                continue
            parts = list(rel.with_suffix("").parts)
            # Skip __pycache__ etc.
            if any(p == "__pycache__" or p.startswith(".") for p in parts):
                continue
            if parts[-1] == "__init__":
                parts = parts[:-1]
            if not parts:
                continue
            dotted = ".".join(parts)
            resolvable.add(dotted)
            # Also add every prefix so namespace-style traversal works.
            for i in range(1, len(parts)):
                resolvable.add(".".join(parts[:i]))
    return resolvable


def is_internal_module(module: str) -> bool:
    return any(module == root or module.startswith(root + ".") for root in PRODUCTION_PACKAGE_ROOTS)


def _attr_path(node: ast.expr) -> str | None:
    """Render a Name/Attribute chain as a dotted string; return None for
    anything else (Subscript, Call, etc.)."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _attr_path(node.value)
        if base is None:
            return None
        return f"{base}.{node.attr}"
    return None


def _scan_file(
    path: Path,
    repo_root: Path,
    resolvable: set[str],
) -> list[DanglingImport]:
    rel = str(path.relative_to(repo_root)).replace("\\", "/")
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except (SyntaxError, OSError, ValueError):
        # Unparseable files are out of scope; other gates (parse-error gates)
        # handle that signal. Silently skip.
        return []

    violations: list[DanglingImport] = []

    for node in ast.walk(tree):
        # progress_bar: bounded AST walk over a single parsed file
        # (typically <O(1000) nodes). Per-file cost is sub-millisecond;
        # outer file iterator in run_gate carries the multi-file progress bar.
        # 1. `from <module> import <name>` — only relative-level=0 (absolute imports).
        if isinstance(node, ast.ImportFrom) and node.level == 0:
            module = node.module or ""
            if module and is_internal_module(module) and module not in resolvable:
                # The full module path itself doesn't resolve. But a `from X.Y import Z`
                # might be importing a submodule Z that becomes X.Y.Z — also check that.
                names = [a.name for a in node.names]
                # If ANY of the (module + "." + name) variants resolve, treat as OK
                # (covers `from importlib import import_module` style).
                joined = [f"{module}.{n}" for n in names]
                if not any(j in resolvable for j in joined):
                    violations.append(
                        DanglingImport(
                            source_file=rel,
                            line_no=node.lineno,
                            target_module=module,
                            kind="from_import",
                            detail=f"names={names}",
                        )
                    )

        # 2. `import <module>` / `import <module> as alias` — absolute imports.
        elif isinstance(node, ast.Import):
            for alias in node.names:
                # progress_bar: bounded — node.names is the comma-separated import list (≤O(10)).
                module = alias.name
                if is_internal_module(module) and module not in resolvable:
                    violations.append(
                        DanglingImport(
                            source_file=rel,
                            line_no=node.lineno,
                            target_module=module,
                            kind="import",
                            detail=f"asname={alias.asname or '-'}",
                        )
                    )

        # 3. Dynamic import: `importlib.import_module("literal")` etc.
        elif isinstance(node, ast.Call):
            target = _attr_path(node.func)
            if target not in DYNAMIC_IMPORT_CALLS:
                continue
            if not node.args:
                continue
            first_arg = node.args[0]
            if not isinstance(first_arg, ast.Constant) or not isinstance(first_arg.value, str):
                continue  # only literals are statically checkable
            module = first_arg.value
            if is_internal_module(module) and module not in resolvable:
                violations.append(
                    DanglingImport(
                        source_file=rel,
                        line_no=node.lineno,
                        target_module=module,
                        kind="dynamic_import",
                        detail=f"call={target}",
                    )
                )

    return violations


def _iter_python_files(repo_root: Path) -> Iterable[Path]:
    # Use the canonical exclusion SSOT — see check_hardcoded_exclusions.py.
    from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS

    skip_dirs = set(GLOBAL_EXCLUDED_DIRS) | {"_archived_obsolete", "tools_graveyard"}
    for root_name in SCAN_ROOTS:
        # progress_bar: this generator is consumed by run_gate which wraps it
        # with tqdm. The skip-set check below is constant-time per file.
        root = repo_root / root_name
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            if any(skip in path.parts for skip in skip_dirs):
                continue
            # Skip archived directories anywhere in the path
            if any(p.startswith("archive") or "graveyard" in p for p in path.parts):
                continue
            yield path


def run_gate(repo_root: Path | None = None) -> GateOutcome:
    repo_root = repo_root or REPO_ROOT
    outcome = GateOutcome()

    if os.environ.get("DANGLING_IMPORT_BYPASS", "").strip() == "1":
        outcome.bypassed = True
        return outcome

    resolvable = build_module_resolver(repo_root)
    files = list(_iter_python_files(repo_root))
    outcome.files_scanned = len(files)
    for path in files:
        for v in _scan_file(path, repo_root, resolvable):
            outcome.violations.append(v)
    return outcome


def _emit_log(outcome: GateOutcome) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "gate": "G-DANGLING-IMPORT",
        "timestamp": outcome.timestamp,
        "files_scanned": outcome.files_scanned,
        "violation_count": len(outcome.violations),
        "bypassed": outcome.bypassed,
        "violations": [
            {
                "source_file": v.source_file,
                "line_no": v.line_no,
                "target_module": v.target_module,
                "kind": v.kind,
                "detail": v.detail,
            }
            for v in outcome.violations[:200]  # cap for log hygiene
        ],
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def main() -> int:
    outcome = run_gate()
    if outcome.bypassed:
        print("[G-DANGLING-IMPORT] BYPASSED via DANGLING_IMPORT_BYPASS=1")
        _emit_log(outcome)
        return 0

    print(
        f"[G-DANGLING-IMPORT] scanned {outcome.files_scanned} files, "
        f"{len(outcome.violations)} dangling imports"
    )
    if outcome.violations:
        # Group by kind for readability
        by_kind: dict[str, list[DanglingImport]] = {}
        for v in outcome.violations:
            by_kind.setdefault(v.kind, []).append(v)
        for kind, items in sorted(by_kind.items()):
            print(f"  {kind}: {len(items)}")
            for v in items[:25]:
                print(f"    {v.source_file}:{v.line_no} -> {v.target_module}  ({v.detail})")
            if len(items) > 25:
                print(f"    ... ({len(items) - 25} more)")
    _emit_log(outcome)
    return 1 if outcome.violations else 0


if __name__ == "__main__":
    sys.exit(main())
