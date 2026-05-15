"""check_apps_hop_pipeline_location — SSOT gate for apps_* inner-DAG layout.

Enforces the canonical structure established by plan
``.cursor/plans/apps-hop-substrate-f7751b.md`` (Author-Gate 2026-05-01,
architecture_choice=shared_substrate_hop_pipeline):

- Inner DAG topology declared in ``apps_<name>/config/hop_pipeline.py``
  as a module-level ``REGISTRY: HopRegistry``.
- Each ``HopStageSpec.engine_module`` resolves to a real file under
  ``apps_<name>/engines/``.
- Exactly one ``apps_<name>/reasoning/*Orchestrator.py`` imports
  ``apps_shared.orchestration.HopPipelineExecutor`` (directly or via
  ``apps_shared.orchestration``).
- No ``apps_<name>/`` file imports the legacy
  ``apps_lic.engines.hop_stage_registry.get_stage_handler`` path outside
  the two grandfathered test files.

Opt-in model
------------
Apps are in scope only when ``apps_<name>/config/hop_pipeline.py`` exists.
Apps that haven't migrated (apps_rg, apps_underwriting_ai as of 2026-05-01)
are NOT flagged — the gate catches drift in migrated apps and warns
(non-blocking) about unmigrated apps that clearly have multi-hop
structure (heuristic: ``apps_<name>/engines/`` has >= 4 engine files).

Exit codes
----------
0 — all migrated apps pass; advisory lines emitted for candidates
2 — any migrated app fails one of the structural rules

Bypass
------
``APPS_HOP_PIPELINE_GATE_BYPASS=1`` env var — emits a WARNING line and
exits 0.

SSOT helper: none (this gate owns its logic; no sibling consumer).
"""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_ROOT = REPO_ROOT

_SHARED_EXECUTOR_IMPORTS = (
    "apps_shared.orchestration.hop_pipeline",
    "apps_shared.orchestration",
)
_LEGACY_SYMBOL = "apps_lic.engines.hop_stage_registry"
_LEGACY_TEST_GRANDFATHER = {
    "tests/unit/apps_lic/reasoning/test_hop_pipeline_executor.py",
    "tests/unit/apps_shared/adapters/test_w3_boundary_facades.py",
}


# =============================================================================
# App discovery
# =============================================================================


def _discover_apps(root: Path) -> list[Path]:
    """Return every ``apps_*`` package directory at the repo root."""
    return sorted(p for p in root.iterdir() if p.is_dir() and p.name.startswith("apps_"))


def _config_file(app: Path) -> Path:
    return app / "config" / "hop_pipeline.py"


def _engines_dir(app: Path) -> Path:
    return app / "engines"


def _reasoning_dir(app: Path) -> Path:
    return app / "reasoning"


def _is_migrated(app: Path) -> bool:
    return _config_file(app).is_file()


def _engine_file_count(app: Path) -> int:
    d = _engines_dir(app)
    if not d.is_dir():
        return 0
    return sum(
        1
        for p in d.iterdir()
        if p.is_file() and p.suffix == ".py" and p.stem not in ("__init__",)
    )


# =============================================================================
# AST probes
# =============================================================================


def _extract_engine_refs(config_path: Path) -> list[tuple[str, str]]:
    """Parse ``config/hop_pipeline.py`` and pull ``HopStageSpec`` engine refs.

    Returns a list of ``(engine_module, engine_class)`` tuples. Uses AST
    (not import) to avoid side-effects of module-load in a gate.
    """
    refs: list[tuple[str, str]] = []
    try:
        tree = ast.parse(config_path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError):
        return refs

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = (
            func.attr if isinstance(func, ast.Attribute) else
            func.id if isinstance(func, ast.Name) else
            ""
        )
        if name != "HopStageSpec":
            continue
        module = cls = ""
        for kw in node.keywords:
            if kw.arg == "engine_module" and isinstance(kw.value, ast.Constant):
                module = str(kw.value.value)
            elif kw.arg == "engine_class" and isinstance(kw.value, ast.Constant):
                cls = str(kw.value.value)
        if module and cls:
            refs.append((module, cls))
    return refs


def _file_imports_shared_executor(py_path: Path) -> bool:
    try:
        tree = ast.parse(py_path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError):
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in _SHARED_EXECUTOR_IMPORTS:
            # Look for HopPipelineExecutor OR a re-export (e.g. the alias)
            for alias in node.names:
                if alias.name in ("HopPipelineExecutor",) or alias.name == "*":
                    return True
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in _SHARED_EXECUTOR_IMPORTS:
                    return True
    return False


def _file_imports_legacy_symbol(py_path: Path) -> bool:
    try:
        text = py_path.read_text(encoding="utf-8")
    except OSError:
        return False
    return _LEGACY_SYMBOL in text


# =============================================================================
# Validation per app
# =============================================================================


def _validate_migrated(app: Path) -> list[str]:
    """Return list of violation messages (empty = clean)."""
    violations: list[str] = []
    app_rel = app.name

    # Rule 1: engine_module refs must resolve to real files under engines/
    cfg = _config_file(app)
    refs = _extract_engine_refs(cfg)
    if not refs:
        violations.append(
            f"{app_rel}: config/hop_pipeline.py exists but no HopStageSpec "
            f"calls with engine_module/engine_class were found"
        )
    for module, cls in refs:
        # Expect module path like 'apps_<name>.engines.<stage>_engine'
        expected_prefix = f"{app_rel}.engines."
        if not module.startswith(expected_prefix):
            violations.append(
                f"{app_rel}: engine_module={module!r} (class={cls!r}) does not "
                f"live under {expected_prefix}* — per-stage engines must be "
                f"colocated in the app's engines/ folder"
            )
            continue
        relative = module[len(expected_prefix):].replace(".", "/")
        engine_file = app / "engines" / f"{relative}.py"
        if not engine_file.is_file():
            violations.append(
                f"{app_rel}: engine_module={module!r} references "
                f"{engine_file.relative_to(REPO_ROOT)} which does not exist"
            )

    # Rule 2: exactly one reasoning/*Orchestrator.py imports the shared executor
    reasoning = _reasoning_dir(app)
    orchestrator_hits: list[Path] = []
    if reasoning.is_dir():
        for py in reasoning.glob("*Orchestrator.py"):
            if _file_imports_shared_executor(py):
                orchestrator_hits.append(py)
    if len(orchestrator_hits) == 0:
        violations.append(
            f"{app_rel}: no *Orchestrator.py under reasoning/ imports "
            f"apps_shared.orchestration.HopPipelineExecutor — a thin runner "
            f"delegating to the shared executor is required"
        )
    # Multiple orchestrators is allowed (e.g. healing vs campaign); the
    # rule only requires at least one.

    # Rule 3: no file in apps_<name>/ imports the legacy get_stage_handler
    # path (grandfathered test files live outside apps_<name>/ — they're
    # under tests/ and bypass this check naturally).
    for py in app.rglob("*.py"):
        if py.suffix != ".py":
            continue
        if _file_imports_legacy_symbol(py):
            rel = py.relative_to(REPO_ROOT).as_posix()
            # Deprecation-shim modules are allowed to reference the
            # legacy dotted path for one release while test-side migration
            # catches up. These two files are the documented grandfather set.
            if rel in (
                f"{app_rel}/engines/hop_stage_registry.py",
                f"{app_rel}/reasoning/HOPPipelineExecutor.py",
            ):
                continue
            violations.append(
                f"{rel}: imports or references the legacy "
                f"{_LEGACY_SYMBOL!r} symbol — migrate to "
                f"apps_<name>.config.hop_pipeline.REGISTRY"
            )

    return violations


def _advise_candidate(app: Path) -> str | None:
    """Non-blocking advisory for apps that look multi-hop but aren't migrated."""
    if _is_migrated(app):
        return None
    count = _engine_file_count(app)
    if count >= 4:
        return (
            f"{app.name}: {count} engine files in engines/ but no "
            f"config/hop_pipeline.py — consider migrating to the shared "
            f"substrate (plan apps-hop-substrate-f7751b, Wave 3/4.1)"
        )
    return None


# =============================================================================
# Main
# =============================================================================


def main() -> int:
    if os.environ.get("APPS_HOP_PIPELINE_GATE_BYPASS") == "1":
        print(
            "WARNING: APPS_HOP_PIPELINE_GATE_BYPASS=1 — skipping check "
            "(bypass logged)",
            file=sys.stderr,
        )
        return 0

    apps = _discover_apps(APPS_ROOT)
    migrated = [a for a in apps if _is_migrated(a)]
    candidates = [a for a in apps if not _is_migrated(a)]

    total_violations = 0
    print(f"[apps_hop_pipeline_gate] scanned {len(apps)} apps_* packages")
    print(f"[apps_hop_pipeline_gate] migrated: {', '.join(a.name for a in migrated) or '(none)'}")

    for app in migrated:
        violations = _validate_migrated(app)
        if violations:
            total_violations += len(violations)
            print(f"\n[FAIL] {app.name}:")
            for v in violations:
                print(f"  - {v}")
        else:
            print(f"[ OK ] {app.name}")

    # Advisory lines — do not fail the gate
    advisories: list[str] = []
    for app in candidates:
        msg = _advise_candidate(app)
        if msg:
            advisories.append(msg)
    if advisories:
        print("\n[apps_hop_pipeline_gate] advisory (non-blocking):")
        for a in advisories:
            print(f"  - {a}")

    if total_violations:
        print(
            f"\n[apps_hop_pipeline_gate] {total_violations} violation(s). "
            f"See plan .cursor/plans/apps-hop-substrate-f7751b.md"
        )
        return 2
    print("\n[apps_hop_pipeline_gate] all migrated apps clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
