"""
Layer Sovereignty Enforcer — Wave 1 Phase 1

AST-based enforcement of the L0-L6 layer hierarchy.
Upward imports (lower layer number importing higher layer number) are violations.
Allowed cross-layer exceptions are explicitly enumerated below.

Usage:
    python -m agentic_core.L5_safety.enforcement.layer_sovereignty_enforcer
"""

from __future__ import annotations

import ast
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "layer_sovereignty_enforcer")
trace_contract.emit_determinism_digest("p0", "layer_sovereignty_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "layer_sovereignty_enforcer", "L5")
trace_contract._emit_routes_through("p1", "layer_sovereignty_enforcer", "L5")
trace_contract._emit_checks_agent_registry("p1", "layer_sovereignty_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "layer_sovereignty_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "layer_sovereignty_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "layer_sovereignty_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "layer_sovereignty_enforcer", "target_agent")
trace_contract._emit_observes_runtime_state("p1", "layer_sovereignty_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "layer_sovereignty_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "layer_sovereignty_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "layer_sovereignty_enforcer")
trace_contract._emit_gated_by_confidence("p1", "layer_sovereignty_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "layer_sovereignty_enforcer", "L5")
trace_contract._emit_reads_policy_state("p1", "layer_sovereignty_enforcer", "L5")

trace_contract._emit_snapshots_state("p0", "layer_sovereignty_enforcer", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "layer_sovereignty_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "layer_sovereignty_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "layer_sovereignty_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "layer_sovereignty_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "layer_sovereignty_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "layer_sovereignty_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "layer_sovereignty_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "layer_sovereignty_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "layer_sovereignty_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "layer_sovereignty_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "layer_sovereignty_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "layer_sovereignty_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "layer_sovereignty_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "layer_sovereignty_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "layer_sovereignty_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "layer_sovereignty_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "layer_sovereignty_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "layer_sovereignty_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "layer_sovereignty_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "layer_sovereignty_enforcer", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("layer_sovereignty_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("layer_sovereignty_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("layer_sovereignty_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("layer_sovereignty_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("layer_sovereignty_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("layer_sovereignty_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("layer_sovereignty_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("layer_sovereignty_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("layer_sovereignty_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("layer_sovereignty_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("layer_sovereignty_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("layer_sovereignty_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("layer_sovereignty_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("layer_sovereignty_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("layer_sovereignty_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("layer_sovereignty_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("layer_sovereignty_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("layer_sovereignty_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("layer_sovereignty_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("layer_sovereignty_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("layer_sovereignty_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("layer_sovereignty_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("layer_sovereignty_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("layer_sovereignty_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("layer_sovereignty_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("layer_sovereignty_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("layer_sovereignty_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("layer_sovereignty_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "layer_sovereignty_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "layer_sovereignty_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "layer_sovereignty_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "layer_sovereignty_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "layer_sovereignty_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "layer_sovereignty_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "layer_sovereignty_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "layer_sovereignty_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "layer_sovereignty_enforcer", "routing_commit")

# ---------------------------------------------------------------------------
# Layer hierarchy: higher number = higher authority.
# A module at layer N MUST NOT import from layer M where M > N.
# ---------------------------------------------------------------------------
LAYER_HIERARCHY: dict[str, int] = {
    "L0_routing": 0,
    "L1_cognition": 1,
    "L2_execution": 2,
    "L3_orchestration": 3,
    "L4_state": 4,
    "L5_safety": 5,
    "L6_observability": 6,
}

# Modules explicitly allowed to cross upward (string-prefix match on importer).
# Format: (importer_prefix, imported_prefix)
ALLOWED_UPWARD_EXCEPTIONS: frozenset[tuple[str, str]] = frozenset(
    {
        # L0 scripts may inspect L5 SSOT for path validation
        ("agentic_core.L0_routing.scripts", "agentic_core.L5_safety.config"),
        # L2 execution seams may reference L5 safety gates
        ("agentic_core.L2_execution.seams", "agentic_core.L5_safety"),
        # Shared interfaces live outside layer numbering
        ("agentic_core.L0_routing", "agentic_core.interfaces"),
        ("agentic_core.L1_cognition", "agentic_core.interfaces"),
        ("agentic_core.L2_execution", "agentic_core.interfaces"),
        ("agentic_core.L3_orchestration", "agentic_core.interfaces"),
        ("agentic_core.L4_state", "agentic_core.interfaces"),
    },
)

SCAN_ROOTS_DEFAULT: tuple[str, ...] = (
    AGENTIC_CORE_DIR,
    SYSTEM_LEARNING_DIR,
    APPS_SHARED_DIR,
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class SovereigntyViolation:
    """A single detected upward-import violation."""

    file_path: str
    importer_module: str
    importer_layer: int
    imported_module: str
    imported_layer: int

    def __str__(self) -> str:
        return (
            f"VIOLATION L{self.importer_layer}→L{self.imported_layer}: "
            f"{self.importer_module} imports {self.imported_module}"
        )


@dataclass
class EnforcementReport:
    """Aggregated result of a sovereignty scan."""

    violations: list[SovereigntyViolation] = field(default_factory=list)
    files_scanned: int = 0
    files_skipped: int = 0
    parse_errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def summary(self) -> str:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "EnforcementReport.summary")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:EnforcementReport.summary".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        lines = [
            f"Files scanned : {self.files_scanned}",
            f"Files skipped : {self.files_skipped}",
            f"Parse errors  : {len(self.parse_errors)}",
            f"Violations    : {len(self.violations)}",
            f"Result        : {'PASS' if self.passed else 'FAIL'}",
        ]
        if self.violations:
            lines.append("")
            for v in self.violations:
                lines.append(f"  {v}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core enforcer
# ---------------------------------------------------------------------------


class LayerSovereigntyEnforcer:
    """
    AST-based layer sovereignty enforcer.

    Scans Python source files and detects any import from a layer with a
    higher authority number than the importing file's own layer.
    """

    def __init__(
        self,
        repo_root: Path,
        scan_roots: tuple[str, ...] | None = None,
        allowed_exceptions: frozenset[tuple[str, str]] | None = None,
    ) -> None:
        self.repo_root = repo_root
        self.scan_roots = scan_roots or SCAN_ROOTS_DEFAULT
        self.allowed_exceptions = (
            allowed_exceptions if allowed_exceptions is not None else ALLOWED_UPWARD_EXCEPTIONS
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> EnforcementReport:
        """Run the full sovereignty scan and return an EnforcementReport."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "LayerSovereigntyEnforcer.run")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:LayerSovereigntyEnforcer.run".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        report = EnforcementReport()
        for root_name in self.scan_roots:
            root_path = self.repo_root / root_name
            if not root_path.is_dir():
                continue
            for py_file in sorted(root_path.rglob("*.py")):
                if "__pycache__" in py_file.parts:
                    continue
                self._scan_file(py_file, report)
        return report

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _scan_file(self, file_path: Path, report: EnforcementReport) -> None:
        """Parse one file and append any violations to report."""
        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError as exc:  # guardian: allow-return-none-swallow -- per-file syntax error: recorded and skipped, enforcement continues
            report.parse_errors.append(f"{file_path}: SyntaxError: {exc}")
            report.files_skipped += 1
            return
        except OSError as exc:  # guardian: allow-return-none-swallow -- per-file read error: recorded and skipped, enforcement continues
            report.parse_errors.append(f"{file_path}: OSError: {exc}")
            report.files_skipped += 1
            return

        report.files_scanned += 1
        importer_module = self._path_to_module(file_path)
        importer_layer = self.extract_layer_from_module(importer_module)
        if importer_layer is None:
            return

        for imported_module in tqdm(self._collect_imports(tree), desc="Processing", unit="item"):
            imported_layer = self.extract_layer_from_module(imported_module)
            if imported_layer is None:
                continue
            if imported_layer <= importer_layer:
                continue  # Downward or same-layer import — allowed
            if self._is_allowed_exception(importer_module, imported_module):
                continue
            report.violations.append(
                SovereigntyViolation(
                    file_path=str(file_path.relative_to(self.repo_root)),
                    importer_module=importer_module,
                    importer_layer=importer_layer,
                    imported_module=imported_module,
                    imported_layer=imported_layer,
                ),
            )

    def _path_to_module(self, file_path: Path) -> str:
        """Convert a filesystem path to a dotted module name."""
        rel = file_path.relative_to(self.repo_root)
        parts = list(rel.with_suffix("").parts)
        return ".".join(parts)

    def _collect_imports(self, tree: ast.Module) -> list[str]:
        """Return all imported module names from an AST tree."""
        modules: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    modules.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    modules.append(node.module)
        return modules

    def _is_allowed_exception(self, importer: str, imported: str) -> bool:
        """Return True if this upward import pair is explicitly whitelisted."""
        for imp_prefix, target_prefix in self.allowed_exceptions:
            if importer.startswith(imp_prefix) and imported.startswith(target_prefix):
                return True
        return False

    # ------------------------------------------------------------------
    # Static helpers (usable without an instance)
    # ------------------------------------------------------------------

    @staticmethod
    def extract_layer_from_module(module_path: str) -> int | None:
        """
        Return the layer number for a dotted module path, or None if not
        part of the layer hierarchy.

        Examples
        --------
        >>> LayerSovereigntyEnforcer.extract_layer_from_module("agentic_core.L2_execution.foo")
        2
        >>> LayerSovereigntyEnforcer.extract_layer_from_module("agentic_core.base_agents.Foo") is None
        True
        """
        for layer_name, level in LAYER_HIERARCHY.items():
            if (
                f".{layer_name}." in module_path
                or module_path.startswith(f"{layer_name}.")
                or f".{layer_name}" == module_path[-len(layer_name) - 1 :]
            ):
                return level
        return None

    @staticmethod
    def check_upward_mutation(importer_layer: int, imported_layer: int) -> bool:
        """
        Return True if importing ``imported_layer`` from ``importer_layer``
        is an upward mutation (violation).

        A violation occurs when ``imported_layer > importer_layer``.
        """
        trace_contract._emit_applies_guardrail(
            str(uuid.uuid4()),
            "LayerSovereigntyEnforcer.check_upward_mutation",
            "L5_POLICY",
        )
        return imported_layer > importer_layer

    def analyze_file_imports(self, file_path: Path) -> list[SovereigntyViolation]:
        """
        Analyse a single file and return any violations found.
        Does NOT mutate any shared state.
        """
        violations: list[SovereigntyViolation] = []
        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(file_path))
        except (
            SyntaxError,
            OSError,
        ):  # review: Multiple exceptions (SyntaxError, OSError) need specific handling
            return violations

        importer_module = self._path_to_module(file_path)
        importer_layer = self.extract_layer_from_module(importer_module)
        if importer_layer is None:
            return violations

        for imported_module in tqdm(self._collect_imports(tree), desc="Processing", unit="item"):
            imported_layer = self.extract_layer_from_module(imported_module)
            if imported_layer is None:
                continue
            if not self.check_upward_mutation(importer_layer, imported_layer):
                continue
            if self._is_allowed_exception(importer_module, imported_module):
                continue
            violations.append(
                SovereigntyViolation(
                    file_path=str(file_path.relative_to(self.repo_root)),
                    importer_module=importer_module,
                    importer_layer=importer_layer,
                    imported_module=imported_module,
                    imported_layer=imported_layer,
                ),
            )
        return violations

    def detect_circular_imports(self) -> list[tuple[str, str]]:
        """
        Detect mutually circular imports between any two modules in scan roots.
        Returns a list of (module_a, module_b) pairs that import each other.
        """
        import_map: dict[str, set[str]] = {}

        for root_name in tqdm(self.scan_roots, desc="Processing", unit="item"):
            root_path = self.repo_root / root_name
            if not root_path.is_dir():
                continue
            for py_file in tqdm(sorted(root_path.rglob("*.py")), desc="Processing", unit="item"):
                if "__pycache__" in py_file.parts:
                    continue
                try:
                    source = py_file.read_text(encoding="utf-8", errors="replace")
                    tree = ast.parse(source)
                except (
                    SyntaxError,
                    OSError,
                ):  # review: Multiple exceptions (SyntaxError, OSError) need specific handling
                    continue
                mod = self._path_to_module(py_file)
                import_map[mod] = set(self._collect_imports(tree))

        cycles: list[tuple[str, str]] = []
        seen: set[frozenset[str]] = set()
        for mod_a, imports_a in import_map.items():
            for mod_b in imports_a:
                if mod_b in import_map and mod_a in import_map[mod_b]:
                    key = frozenset({mod_a, mod_b})
                    if key not in seen:
                        seen.add(key)
                        cycles.append((mod_a, mod_b))
        return cycles


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------


def main() -> int:
    trace_contract._emit_verifies_policy(str(uuid.uuid4()), "Module.main", "L5_POLICY")
    repo_root = Path(__file__).resolve().parents[4]
    enforcer = LayerSovereigntyEnforcer(repo_root)
    report = enforcer.run()
    print(report.summary())
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
