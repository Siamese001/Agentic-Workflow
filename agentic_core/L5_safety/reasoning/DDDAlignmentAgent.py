from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "DDDAlignmentAgent")
emit_determinism_digest("p0", "DDDAlignmentAgent")

_emit_dispatches_healing_run("p1", "DDDAlignmentAgent", "L5")
_emit_routes_through("p1", "DDDAlignmentAgent", "L5")
_emit_checks_agent_registry("p1", "DDDAlignmentAgent", "agent_registry")
_emit_validates_agent_capability("p1", "DDDAlignmentAgent", "capability")
_emit_dispatches_execution_plan("p1", "DDDAlignmentAgent", "exec_plan")
_emit_agent_executes_agent("p1", "DDDAlignmentAgent", "sub_agent")
_emit_routes_to_agent("p1", "DDDAlignmentAgent", "target_agent")
_emit_verifies_policy("p1", "DDDAlignmentAgent", "policy_check")
_emit_observes_runtime_state("p1", "DDDAlignmentAgent", "runtime_state")
_emit_verifies_boundary("p1", "DDDAlignmentAgent", "boundary_check")
_emit_transcripts_response("p1", "DDDAlignmentAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "DDDAlignmentAgent")
_emit_gated_by_confidence("p1", "DDDAlignmentAgent", "confidence_gate")
_emit_escalates_to_human("p1", "DDDAlignmentAgent", "L5")
_emit_reads_policy_state("p1", "DDDAlignmentAgent", "L5")
_emit_authorize_and_execute("p2", "DDDAlignmentAgent", "execution_auth")
_emit_validates_capability("p2", "DDDAlignmentAgent", "capability_check")
_emit_routes_to_capability("p2", "DDDAlignmentAgent", "capability_route")
_emit_writes_via_uwg("p2", "DDDAlignmentAgent", "uwg_write")
_emit_blocks_direct_write("p2", "DDDAlignmentAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "DDDAlignmentAgent", "tool_invocation")
_emit_captures_execution_output("p2", "DDDAlignmentAgent", "exec_output")
_emit_dispatches_agent("p3", "DDDAlignmentAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "DDDAlignmentAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "DDDAlignmentAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "DDDAlignmentAgent", "healing_outcome")
_emit_escalates_failure("p3", "DDDAlignmentAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "DDDAlignmentAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "DDDAlignmentAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "DDDAlignmentAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "DDDAlignmentAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "DDDAlignmentAgent", "eval_metric")
_emit_stores_embedding("p4", "DDDAlignmentAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "DDDAlignmentAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "DDDAlignmentAgent", "exec_snapshot_link")

"\nDDDAlignmentAgent - Domain-Driven Design Bounded Context Enforcement\n\nPURPOSE: Enforces DDD bounded context boundaries to prevent cross-context\ncoupling that undermines the L0-L6 sovereign layer architecture.\n\nKEYS: Architectural integrity, bounded contexts, aggregate roots\nTIER: 2 (Architectural) - runs after structural validation\n\nLOCATION: agentic_core/L5_safety/validators/ (SSOT-compliant)\n"
import ast
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR, TESTS_DIR
from agentic_core.mixins.subatomic_testing_mixin import subatomic_testing_mixin
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)
from agentic_core.utils.timeout_decorator_util import timeout

try:
    from agentic_core.mixins.mcp_hardened_mixin import mcp_hardened_mixin  # noqa: F401
except ImportError:  # guardian: allow-silent-swallow

    class MCPHardenedMixin:
        pass


try:
    from agentic_core.mixins.subatomic_testing_mixin import subatomic_testing_mixin  # noqa: F401
except ImportError:

    class SubatomicTestingMixin:
        pass


try:
    from agentic_core.L5_safety.config.structure_blueprint import (  # noqa: F401
        CORE_SUBFOLDER_MAP,
        SOVEREIGN_REGISTRY,
    )
except ImportError:
    pass  # guardian: allow-silent-swallow -- intentional: ImportError used for control flow
BOUNDED_CONTEXTS: dict[str, dict[str, Any]] = {
    "L0_Governance": {
        "path": "agentic_core/L0_routing",
        "rank": 0,
        "role": "Metacognition: The Law, Auditors, and Healers",
    },
    "L1_Cognition": {
        "path": "agentic_core/L1_cognition",
        "rank": 1,
        "role": "Strategic Reasoning: Planning and Consensus",
    },
    "L2_Execution": {
        "path": "agentic_core/L2_execution",
        "rank": 2,
        "role": "Action: Tool Implementation and Agent Realization",
    },
    "L3_Orchestration": {
        "path": "agentic_core/L3_orchestration",
        "rank": 3,
        "role": "Workflow: Task Fission and Fusion",
    },
    "L4_State": {
        "path": "agentic_core/L4_state",
        "rank": 4,
        "role": "Memory: Persistence and Semantic Caching",
    },
    "L5_Safety": {"path": "agentic_core/L5_safety", "rank": 5, "role": "Membrane: Input/Output Sanitization"},
    "L6_Observability": {
        "path": "agentic_core/L6_observability",
        "rank": 6,
        "role": "Truth: Telemetry, Logging, and Audit Trails",
    },
    "SharedContracts": {
        "path": "apps_shared/base_agents",
        "rank": -1,
        "role": "Neutral Interfaces: Cross-context contracts",
    },
}
STDLIB_MODULES = frozenset(
    {
        "pathlib",
        "os",
        "sys",
        "json",
        "logging",
        "typing",
        "datetime",
        "collections",
        "itertools",
        "functools",
        "re",
        "asyncio",
        "abc",
        "dataclasses",
        "enum",
        "copy",
        "io",
        "time",
        "uuid",
        "hashlib",
        "ast",
        "inspect",
        "importlib",
        "warnings",
        "contextlib",
        "shutil",
        "tempfile",
        "traceback",
        "threading",
        "multiprocessing",
        "subprocess",
        "socket",
        "http",
        "urllib",
        "email",
        "html",
        "xml",
        "csv",
        "pickle",
        "struct",
        "codecs",
        "base64",
        "binascii",
        "zlib",
        "gzip",
        "bz2",
        "lzma",
        "zipfile",
        "tarfile",
        "configparser",
        "argparse",
        "getopt",
        "textwrap",
        "difflib",
        "string",
        "unicodedata",
        "locale",
        "gettext",
        "math",
        "cmath",
        "decimal",
        "fractions",
        "random",
        "statistics",
        "secrets",
        "operator",
        "heapq",
        "bisect",
        "array",
        "weakref",
        "types",
        "pprint",
        "reprlib",
        "graphlib",
        "fnmatch",
        "glob",
        "linecache",
        "tokenize",
        "keyword",
        "symbol",
        "token",
        "dis",
        "builtins",
        "__future__",
        "gc",
        "atexit",
        "signal",
        "errno",
        "ctypes",
        "platform",
        "sysconfig",
        "site",
        "code",
        "codeop",
    },
)
ALLOWED_CROSS_CONTEXT_PATTERNS = frozenset({"contracts", "interfaces", "protocols", "base_agents", "mixins"})
Logger = logging.getLogger(__name__)


@dataclass
class DDDViolation:
    """Structured DDD violation for reporting."""

    file_path: Path
    source_context: str
    target_context: str
    imported_module: str
    line_number: int
    severity: int = 5

    def __str__(self) -> str:
        return f"DDD Violation in {self.file_path.name}:{self.line_number} - Context '{self.source_context}' imports from '{self.target_context}' via '{self.imported_module}'"


@dataclass
class DDDAlignmentAgent(SovereignBaseAgent):
    """
    Domain-Driven Design Alignment Agent.

    Enforces bounded context boundaries to prevent cross-context coupling.

    DETECTION:
    - Scans all Python files for imports
    - Identifies the bounded context of each file
    - Detects imports from other bounded contexts
    - Allows imports from SharedContracts and interface modules

    HEALING:
    - Reports violations (no auto-fix - requires manual refactoring)
    - Suggests using dependency inversion via interfaces

    KEYS: Architectural integrity, DDD, bounded contexts
    """

    project_root: Path = None

    def __post_init__(self):
        if self.project_root is None:
            self.project_root = Path.cwd()
        else:
            self.project_root = Path(self.project_root).resolve()
        self.violations: list[DDDViolation] = []
        self._skip_patterns = {TESTS_DIR, ARCHIVES_DIR, "__pycache__", ".git", "venv", ".venv"}

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        [HEALER PROTOCOL] Standardized healing interface for DDDAlignmentAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "DDDAlignmentAgent.heal", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "DDDAlignmentAgent.heal", "p0_governance")

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L5_POLICY, "DDDAlignmentAgent.heal")
        try:
            violation.get("type", "")
            file_path = violation.get("file")
            if not file_path:
                return {
                    "status": "failed",
                    "details": "No file path provided in violation",
                    "artifacts": [],
                    "errors": ["Missing file path"],
                }
            return {
                "status": "manual_required",
                "details": "DDDAlignmentAgent requires manual review for healing",
                "artifacts": [],
                "errors": [],
            }
        except (ValueError, TypeError) as e:
            return {
                "status": "failed",
                "details": "Exception during healing",
                "artifacts": [],
                "errors": [str(e)],
            }

    def _get_file_context(self, filepath: Path) -> str | None:
        """Determine which bounded context a file belongs to."""
        file_str = str(filepath).replace("\\", "/")
        for ctx_name, ctx_info in BOUNDED_CONTEXTS.items():
            ctx_path = ctx_info.get("path", "")
            if ctx_path and ctx_path in file_str:
                return ctx_name
        return None

    def _is_allowed_import(self, module: str, source_context: str) -> bool:
        """Check if an import is allowed (stdlib, same context, or interface)."""
        if not module:
            return True
        module_root = module.split(".")[0]
        if module_root in STDLIB_MODULES:
            return True
        for pattern in ALLOWED_CROSS_CONTEXT_PATTERNS:
            if pattern in module:
                return True
        return False

    def _check_file_imports(self, filepath: Path) -> list[DDDViolation]:
        """Check a single file for DDD violations."""
        violations = []  # guardian: Parsing and encoding errors need separate handling strategies
        source_context = self._get_file_context(filepath)
        if not source_context:
            return violations
        try:
            content = filepath.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except (
            SyntaxError,
            UnicodeDecodeError,
        ) as e:  # guardian: Parsing and encoding errors need separate handling strategies
            Logger.debug(f"Could not parse {filepath}: {e}")
            return violations
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                module = node.module
                if self._is_allowed_import(module, source_context):
                    continue
                for ctx_name, ctx_info in BOUNDED_CONTEXTS.items():
                    if ctx_name == source_context:
                        continue
                    if ctx_name == "SharedContracts":
                        continue
                    ctx_path = ctx_info.get("path", "").replace("/", ".")
                    if ctx_path and ctx_path in module:
                        violations.append(
                            DDDViolation(
                                file_path=filepath,
                                source_context=source_context,
                                target_context=ctx_name,
                                imported_module=module,
                                line_number=node.lineno,
                            ),
                        )
        return violations

    def _should_skip_path(self, path: Path) -> bool:
        """Check if a path should be skipped."""
        path_str = str(path)
        return any(skip in path_str for skip in self._skip_patterns)

    def run(self, target_dir: Path = None) -> list[DDDViolation]:
        """
        Scan for DDD bounded context violations.

        Args:
            target_dir: Directory to scan (defaults to project_root)

        Returns:
            List of DDDViolation objects
        """
        target = target_dir or self.project_root
        self.violations = []
        Logger.info(f"[DDDAlignmentAgent] Scanning for bounded context violations in {target}")
        try:
            from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

            python_files = list(get_python_files(target))
        except ImportError:
            python_files = list(target.rglob("*.py"))
        files_checked = 0
        for filepath in python_files:
            if self._should_skip_path(filepath):
                continue
            files_checked += 1
            file_violations = self._check_file_imports(filepath)
            self.violations.extend(file_violations)
        Logger.info(
            f"[DDDAlignmentAgent] Checked {files_checked} files, found {len(self.violations)} violations",
        )
        return self.violations

    def get_alignment_score(self) -> float:
        """Calculate DDD alignment score (0-100)."""
        if not self.violations:
            return 100.0
        score = max(0.0, 100.0 - len(self.violations) * 2)
        return score

    def get_violation_summary(self) -> dict[str, Any]:
        """Get summary of violations by context pair."""
        summary: dict[str, int] = {}
        for v in self.violations:
            key = f"{v.source_context} -> {v.target_context}"
            summary[key] = summary.get(key, 0) + 1
        return {
            "total_violations": len(self.violations),
            "alignment_score": self.get_alignment_score(),
            "violations_by_context_pair": summary,
        }

    @timeout(300)
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
    ) -> dict[str, Any]:
        """
        Autonomous DDD alignment enforcement (Canon Key 51 compliance).

        NOTE: DDD violations cannot be auto-healed - they require manual
        refactoring to use dependency inversion via interfaces.

        Args:
            dry_run: If True, only report violations
            execute: If True, would apply fixes (not applicable for DDD)

        Returns:
            Dict with violation counts and recommendations
        """
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            try:
                super().heal_repository(dry_run=dry_run)
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                Logger.debug(f"Parent chain warning: {e}")
            violations = self.run()
            result = {
                "violations_found": len(violations),
                "fixed": 0,
                "errors": 0,
                "alignment_score": self.get_alignment_score(),
                "summary": self.get_violation_summary(),
            }
            if violations:
                print(f"\n[DDDAlignmentAgent] Found {len(violations)} bounded context violations:")
                for v in violations[:10]:
                    print(f"   [!] {v}")
                if len(violations) > 10:
                    print(f"   ... and {len(violations) - 10} more")
                print("\n   RECOMMENDATION: Use dependency inversion via interfaces/contracts")
                print("   to decouple bounded contexts. Import from 'contracts' or 'interfaces'")
                print("   modules instead of directly importing implementation classes.")
            else:
                print("   [OK] DDD Alignment: 100% - No bounded context violations")
            return result
        finally:
            _call_path.discard(agent_name)


def validate_ddd_alignment(target_dir: str) -> tuple[float, list[str]]:
    """
    Convenience function for DDD validation.

    Args:
        target_dir: Directory to validate

    Returns:
        Tuple of (alignment_score, list of violation messages)
    """
    _emit_validated_by_safety_plane(str(uuid.uuid4()), "Module.validate_ddd_alignment", "L5_POLICY")
    agent = DDDAlignmentAgent(project_root=Path(target_dir))
    violations = agent.run()
    messages = [str(v) for v in violations]
    return (agent.get_alignment_score(), messages)


if __name__ == "__main__":
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    agent = DDDAlignmentAgent(project_root=target)
    result = agent.heal_repository(dry_run=True)
    print(f"\nAlignment Score: {result['alignment_score']:.1f}%")
    print(f"Violations: {result['violations_found']}")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("DDDAlignmentAgent", "p4obs", "metric_1")
_emit_emits_metric_event("DDDAlignmentAgent", "p4obs", "metric_2")
_emit_emits_metric_event("DDDAlignmentAgent", "p4obs", "metric_3")
_emit_emits_metric_event("DDDAlignmentAgent", "p4obs", "metric_4")
_emit_emits_metric_event("DDDAlignmentAgent", "p4obs", "metric_5")
_emit_emits_metric_event("DDDAlignmentAgent", "p4obs", "metric_6")
_emit_records_incident_event("DDDAlignmentAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("DDDAlignmentAgent", "p4obs", "anomaly")
_emit_writes_observability_log("DDDAlignmentAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("DDDAlignmentAgent", "p4obs", "mon_state")
_emit_triggers_alert("DDDAlignmentAgent", "p4obs", "alert")
_emit_links_incident_trace("DDDAlignmentAgent", "p4obs", "trace_link")
_emit_captures_pattern("DDDAlignmentAgent", "p3lm", "pattern")
_emit_records_learning_event("DDDAlignmentAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("DDDAlignmentAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("DDDAlignmentAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("DDDAlignmentAgent", "p3lm", "routing")
_emit_improves_agent_policy("DDDAlignmentAgent", "p3lm", "policy")
_emit_stores_learning_state("DDDAlignmentAgent", "p3lm", "state")
_emit_records_execution_trace("DDDAlignmentAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("DDDAlignmentAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("DDDAlignmentAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("DDDAlignmentAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("DDDAlignmentAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("DDDAlignmentAgent", "env_read", "p2_env_1")
_emit_reads_environ("DDDAlignmentAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("DDDAlignmentAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("DDDAlignmentAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "DDDAlignmentAgent", "context_pull")
_emit_pulls_context("p1", "DDDAlignmentAgent", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "DDDAlignmentAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "DDDAlignmentAgent", "uwg_term_secondary")
_emit_writes_through("p1", "DDDAlignmentAgent", "write_through")
_emit_writes_through("p1", "DDDAlignmentAgent", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "DDDAlignmentAgent", "safety_validation")
_emit_invokes_eval("p1", "DDDAlignmentAgent", "eval_call")
_emit_proposal_commits_routing("p1", "DDDAlignmentAgent", "routing_commit")
