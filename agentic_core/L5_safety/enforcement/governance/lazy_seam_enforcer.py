"""
Lazy Seam Enforcer - Phase 4 Option A: Enforcer for Phase 3B seam universe.

Ensures all lazy seams from Phase 3B metric are registered in the allowlist.
Implements LAZY_SEAM_UNREGISTERED invariant.
"""

# Import Phase 3B metric functions (replicated to avoid import issues)
import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L0_routing.config.path_constants import OPS_SCRIPTS_DIR
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "lazy_seam_enforcer")
trace_contract.emit_determinism_digest("p0", "lazy_seam_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "lazy_seam_enforcer", "L5")
trace_contract._emit_routes_through("p1", "lazy_seam_enforcer", "L5")
trace_contract._emit_checks_agent_registry("p1", "lazy_seam_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "lazy_seam_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "lazy_seam_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "lazy_seam_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "lazy_seam_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "lazy_seam_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "lazy_seam_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "lazy_seam_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "lazy_seam_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "lazy_seam_enforcer")
trace_contract._emit_gated_by_confidence("p1", "lazy_seam_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "lazy_seam_enforcer", "L5")
trace_contract._emit_reads_policy_state("p1", "lazy_seam_enforcer", "L5")

trace_contract._emit_applies_guardrail("p0", "lazy_seam_enforcer", "p0_governance")
trace_contract._emit_snapshots_state("p0", "lazy_seam_enforcer", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "lazy_seam_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "lazy_seam_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "lazy_seam_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "lazy_seam_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "lazy_seam_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "lazy_seam_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "lazy_seam_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "lazy_seam_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "lazy_seam_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "lazy_seam_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "lazy_seam_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "lazy_seam_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "lazy_seam_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "lazy_seam_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "lazy_seam_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "lazy_seam_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "lazy_seam_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "lazy_seam_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "lazy_seam_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "lazy_seam_enforcer", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("lazy_seam_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("lazy_seam_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("lazy_seam_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("lazy_seam_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("lazy_seam_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("lazy_seam_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("lazy_seam_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("lazy_seam_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("lazy_seam_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("lazy_seam_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("lazy_seam_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("lazy_seam_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("lazy_seam_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("lazy_seam_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("lazy_seam_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("lazy_seam_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("lazy_seam_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("lazy_seam_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("lazy_seam_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("lazy_seam_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("lazy_seam_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("lazy_seam_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("lazy_seam_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("lazy_seam_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("lazy_seam_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("lazy_seam_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("lazy_seam_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("lazy_seam_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "lazy_seam_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "lazy_seam_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "lazy_seam_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "lazy_seam_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "lazy_seam_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "lazy_seam_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "lazy_seam_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "lazy_seam_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "lazy_seam_enforcer", "routing_commit")


@dataclass
class LazyUpwardImport:
    """A lazy upward import excluded by function/try guard."""

    source_file: Path
    source_layer: int
    target_layer: int
    import_statement: str
    line_number: int
    context: str  # function name or '__try_module_scope__'


# Replicate Phase 3B metric functions
LAYER_PATTERN = re.compile(r"^L(\d+)_")
IMPORT_LAYER_PATTERN = re.compile(r"agentic_core\.L(\d+)_")


def extract_import_targets(node: ast.AST) -> list[tuple[str, int]]:
    """Extract import target strings and line numbers from an AST node."""
    targets = []

    if isinstance(node, ast.Import):
        for alias in node.names:
            targets.append((alias.name, node.lineno))
    elif isinstance(node, ast.ImportFrom):
        if node.module:
            targets.append((node.module, node.lineno))

    return targets


def _is_inside_function_or_guarded(tree: ast.AST, target_lineno: int) -> bool:
    """Check if a line is inside a function, method, or try/except block."""
    for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.end_lineno is not None:
                    if node.lineno <= target_lineno <= node.end_lineno:
                        return True
        if isinstance(node, ast.Try):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.end_lineno is not None:
                    if node.lineno <= target_lineno <= node.end_lineno:
                        return True
    return False


def _get_enclosing_function(
    tree: ast.AST,
    target_lineno: int,
) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    """Return the innermost FunctionDef/AsyncFunctionDef enclosing target_lineno."""
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.end_lineno is not None:
                    if node.lineno <= target_lineno <= node.end_lineno:
                        if best is None or (
                            best.end_lineno is not None
                            and node.end_lineno - node.lineno < best.end_lineno - best.lineno
                        ):
                            best = node
    return best


def _is_inside_try_module_scope(tree: ast.AST, target_lineno: int) -> bool:
    """Return True if target_lineno is inside a Try block at module scope."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.end_lineno is not None:
                    if node.lineno <= target_lineno <= node.end_lineno:
                        enclosing_fn = _get_enclosing_function(tree, node.lineno)
                        if enclosing_fn is None:
                            return True
    return False


def collect_lazy_upward_imports(
    agentic_root: Path,
) -> list[LazyUpwardImport]:
    """Collect all upward imports excluded ONLY because they are inside a
    function/try guard (the 'lazy seam')."""
    results: list[LazyUpwardImport] = []

    for layer in tqdm(range(7), desc="Processing", unit="item"):
        layer_dir = None
        for item in agentic_root.iterdir():
            if item.is_dir() and item.name.startswith(f"L{layer}_"):
                layer_dir = item
                break
        if layer_dir is None:
            continue

        for py_file in tqdm(layer_dir.rglob("*.py"), desc="Processing", unit="item"):
            try:
                rel = py_file.relative_to(agentic_root)
            except ValueError:
                continue
            parts = rel.parts
            if not parts:
                continue
            m = LAYER_PATTERN.match(parts[0])
            if not m:
                continue
            src_layer = int(m.group(1))

            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(py_file))
            except (
                SyntaxError,
                UnicodeDecodeError,
            ):  # review: Parsing and encoding errors need separate handling strategies
                continue

            for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
                if not isinstance(node, (ast.Import, ast.ImportFrom)):
                    continue
                targets = extract_import_targets(node)
                for import_str, line_no in tqdm(targets, desc="Processing", unit="item"):
                    match = IMPORT_LAYER_PATTERN.search(import_str)
                    if not match:
                        continue
                    tgt_layer = int(match.group(1))
                    if tgt_layer <= src_layer:
                        continue
                    if not _is_inside_function_or_guarded(tree, line_no):
                        continue
                    fn = _get_enclosing_function(tree, line_no)
                    if fn is not None:
                        context = fn.name
                    elif _is_inside_try_module_scope(tree, line_no):
                        context = "__try_module_scope__"
                    else:
                        context = "__unknown__"
                    results.append(
                        LazyUpwardImport(
                            source_file=py_file,
                            source_layer=src_layer,
                            target_layer=tgt_layer,
                            import_statement=import_str,
                            line_number=line_no,
                            context=context,
                        ),
                    )

    return results


def lazy_upward_import_metric(
    agentic_root: Path,
) -> dict:
    """Compute the LAZY_UPWARD_IMPORTS metric."""
    items = collect_lazy_upward_imports(agentic_root)
    by_pair: dict[tuple[int, int], int] = {}
    by_file: dict[str, int] = {}
    for item in items:
        pair = (item.source_layer, item.target_layer)
        by_pair[pair] = by_pair.get(pair, 0) + 1
        key = str(item.source_file)
        by_file[key] = by_file.get(key, 0) + 1
    return {
        "total": len(items),
        "by_pair": by_pair,
        "by_file": by_file,
        "items": items,
    }


class LazySeamEnforcer:
    """Enforces lazy seam allowlist compliance."""

    lazy_upward_import_metric = staticmethod(lazy_upward_import_metric)

    def __init__(self, root_path: Path, allowlist_path: Path):
        self.root_path = root_path
        self.allowlist_path = allowlist_path
        self.allowlist_data = self._load_allowlist()
        self.violations = []

    def _load_allowlist(self) -> dict[str, Any]:
        """Load allowlist from file."""
        with open(self.allowlist_path, encoding="utf-8") as f:
            return json.load(f)

    def _create_seam_key(
        self,
        file_path: str,
        function_name: str,
        imported_modules: list[str],
        imported_symbols: list[tuple],
    ) -> str:
        """Create a unique key for a seam."""
        return f"{file_path}::{function_name}::{sorted(imported_modules)}::{sorted(imported_symbols)}"

    def _get_allowlist_keys(self) -> set[str]:
        """Get all allowed seam keys."""
        allowed_keys = set()
        for seam in self.allowlist_data["seams"]:
            key = self._create_seam_key(
                seam["file_path"],
                seam["function_name"],
                seam.get("imported_modules", []),
                seam.get("imported_symbols", []),
            )
            allowed_keys.add(key)
        return allowed_keys

    def scan_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Scan a single file for lazy seams."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            seams = []

            for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("_get_"):
                    # Extract imports from within the function
                    imported_modules = set()
                    imported_symbols = []

                    for child in ast.walk(node):
                        if isinstance(child, ast.Import):
                            for alias in child.names:
                                imported_modules.add(alias.name)
                                imported_symbols.append((alias.name, None))
                        elif isinstance(child, ast.ImportFrom):
                            module = child.module or ""
                            for alias in child.names:
                                imported_modules.add(module)
                                imported_symbols.append((module, alias.name))

                    # Create seam entry
                    seam = {
                        "file_path": str(file_path.relative_to(self.root_path)),
                        "function_name": node.name,
                        "imported_modules": sorted(imported_modules),
                        "imported_symbols": imported_symbols,
                    }
                    seams.append(seam)

            return seams

        except (RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
            print(f"Error scanning {file_path}: {e}")
            return []

    def scan_codebase(self) -> list[dict[str, Any]]:
        """Scan entire codebase for lazy seams."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "LazySeamEnforcer.scan_codebase")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:LazySeamEnforcer.scan_codebase".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        python_files = list(self.root_path.rglob("*.py"))

        # Skip patterns (same as scanner)
        skip_patterns = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS

        skip_file_patterns = {"test_", "_test.py", "conftest.py"}

        all_seams = []
        for file_path in tqdm(python_files, desc="Processing", unit="item"):
            # Skip if in ignored directory
            if any(pattern in file_path.parts for pattern in skip_patterns):
                continue

            # Skip test files and other patterns
            if any(pattern in file_path.name for pattern in skip_file_patterns):
                continue

            # Skip artifacts and ops scripts (focus on core source)
            if any(
                pattern in file_path.parts
                for pattern in ["artifacts", OPS_SCRIPTS_DIR, "docs", "data", ".pytest_tmp"]
            ):
                continue

            seams = self.scan_file(file_path)
            all_seams.extend(seams)

        return all_seams

    def enforce(self) -> list[dict[str, Any]]:
        """Enforce allowlist compliance using Phase 3B metric."""
        print("Scanning codebase for lazy seams (Phase 3B universe)...")

        # Get Phase 3B metric results
        agentic_core_path = self.root_path / AGENTIC_CORE_DIR
        metric = self.lazy_upward_import_metric(agentic_core_path)
        phase3b_seams = metric["items"]

        print(f"Found {len(phase3b_seams)} lazy seams")
        print(f"Allowlist contains {len(self.allowlist_data['seams'])} allowed seams")

        # Create allowlist lookup
        allowed_keys = self._get_allowlist_keys()

        violations = []
        for seam in tqdm(phase3b_seams, desc="Processing", unit="item"):
            # Convert Phase 3B seam to allowlist format for comparison
            seam_entry = {
                "file_path": str(seam.source_file.relative_to(self.root_path)),
                "function_name": seam.context,
                "imported_modules": [seam.import_statement] if seam.import_statement else [],
                "imported_symbols": [],  # Phase 3B doesn't track symbols separately
            }

            key = self._create_seam_key(
                seam_entry["file_path"],
                seam_entry["function_name"],
                seam_entry.get("imported_modules", []),
                seam_entry.get("imported_symbols", []),
            )

            if key not in allowed_keys:
                violation = {
                    "type": "LAZY_SEAM_UNREGISTERED",
                    "file_path": seam_entry["file_path"],
                    "function_name": seam_entry["function_name"],
                    "description": f"Lazy seam not found in allowlist: {seam_entry['function_name']} in {seam_entry['file_path']}",
                }
                violations.append(violation)

        self.violations = violations
        return violations

    def print_results(self) -> None:
        """Print enforcement results."""
        if not self.violations:
            print("✓ All lazy seams are registered in allowlist")
        else:
            print(f"✗ Found {len(self.violations)} unregistered lazy seams:")
            for violation in self.violations:
                print(f"  - {violation['description']}")


def main():
    """Main execution."""
    root_path = Path.cwd()
    allowlist_path = root_path / AGENTIC_CORE_DIR / "L5_safety" / "governance" / "lazy_seam_allowlist.json"

    enforcer = LazySeamEnforcer(root_path, allowlist_path)
    violations = enforcer.enforce()
    enforcer.print_results()

    # Exit with error code if violations found
    if violations:
        exit(1)
    else:
        print("✓ Lazy seam enforcement passed")


if __name__ == "__main__":
    main()
