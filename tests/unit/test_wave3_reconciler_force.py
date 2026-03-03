"""
Wave 3 Invariant: FilesystemSSOTReconcilerAgent.heal_repository() must accept
force=True kwarg to bypass the skip-gate and actually run detect_root_drift().
execute_ssot.py must pass force=True when healing is active.
"""

import ast
from pathlib import Path

RECONCILER_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "agentic_core"
    / "L5_safety"
    / "reasoning"
    / "FilesystemSSOTReconcilerAgent.py"
)
EXECUTE_SSOT_PATH = (
    Path(__file__).parent.parent.parent.parent / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot.py"
)


def _ast_func_args(path: Path, func_name: str, class_name: str | None = None) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    if class_name:
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == func_name:
                        return [a.arg for a in item.args.args] + [a.arg for a in item.args.kwonlyargs]
        return []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return [a.arg for a in node.args.args] + [a.arg for a in node.args.kwonlyargs]
    return []


def test_heal_repository_has_force_param():
    """Wave 3: FilesystemSSOTReconcilerAgent.heal_repository() must accept force kwarg."""
    args = _ast_func_args(RECONCILER_PATH, "heal_repository", "FilesystemSSOTReconcilerAgent")
    assert "force" in args, (
        "heal_repository() missing force kwarg on FilesystemSSOTReconcilerAgent — "
        "logs/ drift will always be skipped (returns {'skipped': 1})"
    )


def test_execute_ssot_passes_force_true():
    """Wave 3: execute_ssot.py must call heal_repository(force=True)."""
    src = EXECUTE_SSOT_PATH.read_text(encoding="utf-8", errors="replace")
    assert "heal_repository(force=True" in src, (
        "execute_ssot.py does not call heal_repository(force=True) — "
        "forbidden root folders like logs/ will never be reconciled"
    )


def test_detect_root_drift_still_exists():
    """Regression: detect_root_drift() must not be removed by Wave 3 edits."""
    args = _ast_func_args(RECONCILER_PATH, "detect_root_drift")
    # If returns empty, function may not exist — check via walk
    tree = ast.parse(RECONCILER_PATH.read_text(encoding="utf-8", errors="replace"))
    names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert "detect_root_drift" in names, "detect_root_drift() was removed"


def test_logs_in_forbidden_root_folders():
    """Wave 3: 'logs' must remain in FORBIDDEN_ROOT_FOLDERS."""
    src = RECONCILER_PATH.read_text(encoding="utf-8", errors="replace")
    assert '"logs"' in src or "'logs'" in src, (
        "logs not in FORBIDDEN_ROOT_FOLDERS — drift detection will miss it"
    )
