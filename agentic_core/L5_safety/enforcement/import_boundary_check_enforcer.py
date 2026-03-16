"""
agentic_core/enforcement/import_boundary_check_enforcer.py

AST-based import boundary checker for the agentic_core package.

Enforces that no file inside agentic_core imports from downstream
apps_* packages (apps_lic, apps_rg, apps_shared).
Uses AST parsing — no regex.
"""

import ast
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "import_boundary_check_enforcer")
emit_determinism_digest("p0", "import_boundary_check_enforcer")

_emit_dispatches_healing_run("p1", "import_boundary_check_enforcer", "L5")
_emit_routes_through("p1", "import_boundary_check_enforcer", "L5")
_emit_escalates_to_human("p1", "import_boundary_check_enforcer", "L5")
_emit_reads_policy_state("p1", "import_boundary_check_enforcer", "L5")

_emit_applies_guardrail("p0", "import_boundary_check_enforcer", "p0_governance")
_emit_snapshots_state("p0", "import_boundary_check_enforcer", "state_snapshot")

_AGENTIC_CORE_ROOT = Path(__file__).parent.parent
FORBIDDEN_IMPORT_PREFIXES = frozenset({APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR})


class _ImportBoundaryVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.violations: list[str] = []

    def _check(self, module: str, lineno: int) -> None:
        if any(module.startswith(p) for p in FORBIDDEN_IMPORT_PREFIXES):
            self.violations.append(f"Line {lineno}: Forbidden import '{module}'")

    def visit_Import(self, node: ast.Import) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "_ImportBoundaryVisitor.visit_Import"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:_ImportBoundaryVisitor.visit_Import".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        for alias in node.names:
            self._check(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self._check(node.module, node.lineno)
        self.generic_visit(node)


def check_file_import_boundaries(file_path: Path) -> list[str]:
    """Return list of violation strings for a single file (empty = clean)."""
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return [f"SyntaxError: {exc}"]
    visitor = _ImportBoundaryVisitor()
    visitor.visit(tree)
    return visitor.violations


def check_agentic_core_boundaries() -> bool:
    """Check all agentic_core files for import boundary compliance.

    Prints violations and returns False if any found, True if clean.
    """
    all_violations: list[str] = []
    for py_file in _AGENTIC_CORE_ROOT.rglob("*.py"):
        file_violations = check_file_import_boundaries(py_file)
        if file_violations:
            for v in file_violations:
                all_violations.append(f"{py_file.relative_to(_AGENTIC_CORE_ROOT)}: {v}")
    if all_violations:
        print("agentic_core import boundary violations found:")
        for v in all_violations:
            print(f"  {v}")
        return False
    print("OK: All agentic_core files comply with import boundaries")
    return True


if __name__ == "__main__":
    import sys

    sys.exit(0 if check_agentic_core_boundaries() else 1)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)
