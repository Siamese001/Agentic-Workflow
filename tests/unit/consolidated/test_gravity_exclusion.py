"""
Wave 2 Invariant: GravityLeakRepairAgent must exclude ops_scripts/ and scripts/
from gravity scan, and apply_fix() must accept privileged_mutation_context kwarg.
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""

import ast
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, OPS_SCRIPTS_DIR

GRAVITY_PATH = (
    Path(__file__).parent.parent.parent
    / AGENTIC_CORE_DIR
    / "L5_safety"
    / "reasoning"
    / "GravityLeakRepairAgent.py"
)
STRUCTURE_PATH = (
    Path(__file__).parent.parent.parent
    / AGENTIC_CORE_DIR
    / "L5_safety"
    / "reasoning"
    / "StructuralValidatorAgent.py"
)


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8", errors="replace"))


def test_structure_config_has_excluded_paths():
    """Wave 2: StructureConfig must have excluded_paths field."""

    tree = _parse(STRUCTURE_PATH)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "StructureConfig":
            for item in ast.walk(node):
                if isinstance(item, ast.AnnAssign):
                    if isinstance(item.target, ast.Name) and item.target.id == "excluded_paths":
                        return
    raise AssertionError(
        "excluded_paths field not found in StructureConfig — "
        "GravityLeakRepairAgent cannot exclude ops_scripts/ and scripts/"
    )


def test_apply_fix_has_privileged_mutation_context_param():
    """Wave 2: apply_fix() must accept privileged_mutation_context kwarg."""
    tree = _parse(GRAVITY_PATH)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "apply_fix":
            arg_names = [a.arg for a in node.args.args] + [a.arg for a in node.args.kwonlyargs]
            assert "privileged_mutation_context" in arg_names, (
                "apply_fix() missing privileged_mutation_context kwarg — "
                "ops_scripts/ and scripts/ fixes will always be plan_only"
            )
            return
    raise AssertionError("apply_fix() not found in GravityLeakRepairAgent")


def test_heal_repository_excludes_ops_scripts():
    """Wave 2: heal_repository must reference ops_scripts exclusion."""
    src = GRAVITY_PATH.read_text(encoding="utf-8", errors="replace")
    assert OPS_SCRIPTS_DIR in src, (
        "ops_scripts not excluded in GravityLeakRepairAgent.heal_repository() — "
        "violations in that directory will always block as plan_only"
    )


def test_heal_repository_excludes_scripts():
    """Wave 2: heal_repository must reference scripts exclusion."""
    src = GRAVITY_PATH.read_text(encoding="utf-8", errors="replace")
    # Must appear in context of excluded_paths or similar
    assert '"scripts"' in src or "'scripts'" in src, (
        "scripts not excluded in GravityLeakRepairAgent — "
        "violations in that directory will always block as plan_only"
    )
