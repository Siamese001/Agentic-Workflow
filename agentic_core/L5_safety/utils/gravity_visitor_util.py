from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "gravity_visitor_util", "L5")
_emit_routes_through("p1", "gravity_visitor_util", "L5")
_emit_escalates_to_human("p1", "gravity_visitor_util", "L5")
_emit_reads_policy_state("p1", "gravity_visitor_util", "L5")

_emit_applies_guardrail("p0", "gravity_visitor_util", "p0_governance")
_emit_snapshots_state("p0", "gravity_visitor_util", "state_snapshot")

'AST Engine - Centralized Architectural Parsing Logic.\n\n[Phase 5] Provides shared AST utilities for L5 agents.\nCentralizes import extraction and gravity violation detection.\n\nUsage:\n\n    imports = get_file_imports(Path("my_file.py"))\n    # Returns: [("module.name", line_number), ...]\n'
import ast
import logging
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)

Logger = logging.getLogger(__name__)


class GravityVisitor(ast.NodeVisitor):
    """
    Standardized AST visitor for architectural gravity enforcement.

    Extracts all import statements from a Python file for layer analysis.
    """

    def __init__(self, source_layer: str, file_path: Path) -> None:
        self.source_layer = source_layer
        self.file_path = file_path
        self.imports: list[tuple[str, int]] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Handle 'import x' statements."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "GravityVisitor.visit_Import")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:GravityVisitor.visit_Import".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        for alias in node.names:
            self.imports.append((alias.name, node.lineno))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Handle 'from x import y' statements."""
        if node.module:
            self.imports.append((node.module, node.lineno))
        self.generic_visit(node)


def get_file_imports(file_path: Path) -> list[tuple[str, int]]:
    """
    Centralized utility to extract imports from a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        List of (module_name, line_number) tuples
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        visitor = GravityVisitor("unknown", file_path)
        visitor.visit(tree)
        return visitor.imports
    except SyntaxError as e:
        Logger.debug(f"Syntax error in {file_path}: {e}")
        return []
    # guardian: allow-silent-swallow
    except Exception as e:
        Logger.debug(f"Could not parse {file_path}: {e}")
        return []


def extract_layer_from_path(file_path: Path) -> str | None:
    """
    Extract the layer (L0-L6, Apps) from a file path.

    Args:
        file_path: Path to analyze

    Returns:
        Layer string (e.g., "L3") or None if not determinable
    """
    path_str = str(file_path)
    for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        if f"/{layer}_" in path_str or f"\\{layer}_" in path_str:
            return layer
        if f"/{layer}/" in path_str or f"\\{layer}\\" in path_str:
            return layer
    if "/apps_" in path_str or "\\apps_" in path_str:
        return "Apps"
    if "/apps/" in path_str or "\\apps/" in path_str:
        return "Apps"
    if f"/{TESTS_DIR}/" in path_str or f"\\{TESTS_DIR}\\" in path_str:
        return TESTS_DIR
    return None


def extract_layer_from_import(import_path: str) -> str | None:
    """
    Extract the layer from an import path.

    Args:
        import_path: Import module path (e.g., "agentic_core.L5_safety.validators")

    Returns:
        Layer string (e.g., "L5") or None if not determinable
    """
    for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        if f".{layer}_" in import_path or f"{layer}_" in import_path:
            return layer
    if ".apps_" in import_path or "apps_" in import_path:
        return "Apps"
    return None


def check_gravity_violation(
    source_layer: str, target_layer: str, gravity_rules: dict[str, set[str]] | None = None
) -> bool:
    """
    Check if importing from target_layer violates gravity rules.

    Args:
        source_layer: Layer of the file doing the import
        target_layer: Layer being imported from
        gravity_rules: Optional custom gravity rules dict

    Returns:
        True if this is a violation, False if allowed
    """
    if gravity_rules is None:
        gravity_rules = {
            "L0": {"L0"},
            "L1": {"L0", "L1"},
            "L2": {"L0", "L1", "L2"},
            "L3": {"L0", "L1", "L2", "L3"},
            "L4": {"L0", "L1", "L2", "L3", "L4"},
            "L5": {"L0", "L1", "L2", "L3", "L4", "L5"},
            "L6": {"L0", "L1", "L2", "L3", "L4", "L5", "L6"},
            "Apps": {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "Apps"},
            "tests": {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "Apps", "tests"},
        }
    allowed_layers = gravity_rules.get(source_layer, set())
    return target_layer not in allowed_layers
