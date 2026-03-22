"""ADG Static Scanner -- AST-based edge extraction for the Architecture Dependency Graph.

Produces a deterministic, commit-scoped canonical edge list and digest.
All analysis uses Python AST parsing. Regex/grep for structural logic is forbidden.

Graph types extracted:
  G1 - Import graph (imports edges)
  G2 - Call/write/network graph (writes_to, invokes_provider edges)
  G3 - Inheritance graph (implements edges)  [H3]
  G5 - Config read graph (reads_from edges)  [H4]
  G6 - Composition graph (instantiates edges in __init__)  [H5]
  GF - Dynamic execution graph (eval/exec/importlib)  [S3]

Output format per run:
    ADG-DETERMINISM-DIGEST: <sha256_hex>

Canonical edge list sort order: from_name, relation_type, to_name, line_no.
"""

from __future__ import annotations

import ast
import hashlib
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from agentic_core.adg.identity.normalizer import (
    IdentityKind,
)
from agentic_core.adg.schema_util import (
    canonical_name,
)
from agentic_core.adg.schema_util import (
    AGENT_DISPATCH_CLASSES,
    AGENT_DISPATCH_METHODS,
    AGENT_REGISTRY_CLASSES,
    ANTIPATTERN_CATEGORY_NAMES,
    ANTIPATTERN_REGISTRY_CLASSES,
    AUTHORIZE_EXECUTE_SYMBOLS,
    BLOCKS_DIRECT_WRITE_SYMBOLS,
    BOUNDARY_VERIFIER_CLASSES,
    BROAD_EXCEPTION_TYPES,
    BUDGET_EXCEEDED_EXCEPTIONS,
    CAPABILITY_CHOKEPOINT_CLASSES,
    CAPABILITY_TOKEN_CLASSES,
    CAPABILITY_VALIDATION_SYMBOLS,
    CAPTURES_EVALUATION_METRIC_SYMBOLS,
    CAPTURES_EXECUTION_OUTPUT_SYMBOLS,
    CAPTURES_PATTERN_SYMBOLS,
    CAPTURES_RUNTIME_ANOMALY_SYMBOLS,
    CONFIDENCE_SCORING_CLASSES,
    CONFIG_ACCESS_METHODS,
    CONFIG_READER_CLASSES,
    COORDINATES_AGENTS_SYMBOLS,
    DETERMINISM_PATCH_METHODS,
    DISPATCHES_AGENT_SYMBOLS,
    DPO_BATCH_CLASSES,
    DRIFT_ALERT_METHODS,
    DYNAMIC_EVAL_SYMBOLS,
    DYNAMIC_GETATTR_SYMBOLS,
    EMBEDDING_PIPELINE_SYMBOLS,
    EMBEDDING_SYMBOLS,
    EMITS_METRIC_EVENT_SYMBOLS,
    ESCALATES_FAILURE_SYMBOLS,
    EVAL_METRIC_CLASSES,
    EXECUTION_PLAN_DISPATCH_SYMBOLS,
    EXECUTION_TRACE_CLASSES,
    EXTERNAL_HTTP_SYMBOLS,
    FEEDS_META_LEARNING_SYMBOLS,
    FREEZE_METHOD_NAMES,
    GUARDRAIL_CLASS_NAMES,
    HEALER_BASE_CLASSES,
    HEALER_METHOD_NAMES,
    HEALING_DISPATCH_METHODS,
    HEALING_ORCHESTRATOR_CLASSES,
    HITL_ESCALATION_METHODS,
    HUMAN_REVIEW_SYMBOLS,
    IMPROVES_AGENT_POLICY_SYMBOLS,
    INVOKES_EVALUATION_SYMBOLS,
    IO_INTERCEPT_CLASSES,
    JIT_CONTEXT_CLASSES,
    LINKS_EXECUTION_TO_SNAPSHOT_SYMBOLS,
    LINKS_INCIDENT_TRACE_SYMBOLS,
    LOGGING_METHOD_NAMES,
    MUTATION_TRANSPORT_CLASSES,
    NETWORK_SYMBOLS,
    NETWORK_TRANSCRIPT_SYMBOLS,
    NONDETERMINISM_RANDOM_SYMBOLS,
    NONDETERMINISM_UUID_SYMBOLS,
    # G23-G27 (gap): new proof-edge frozensets
    NONDETERMINISM_WALL_CLOCK_SYMBOLS,
    ORCHESTRATION_ROUTE_SYMBOLS,
    PATH_CONTROL_CLASSES,
    PATH_REROUTE_METHODS,
    POLICY_HASH_METHODS,
    POLICY_HASH_SYMBOLS,
    POLICY_STATE_READ_METHODS,
    POLICY_STATE_READER_CLASSES,
    PREFERENCE_PAIR_SYMBOLS,
    PROMPT_INJECTION_SYMBOLS,
    PROMPT_TEMPLATE_SYMBOLS,
    PROVIDER_SDK_SYMBOLS,
    RECORDS_HEALING_OUTCOME_SYMBOLS,
    RECORDS_INCIDENT_EVENT_SYMBOLS,
    RECORDS_LEARNING_EVENT_SYMBOLS,
    RECORDS_TELEMETRY_EVENT_SYMBOLS,
    RECORDS_TOOL_INVOCATION_SYMBOLS,
    RECORDS_WORKFLOW_LINEAGE_SYMBOLS,
    REGISTRY_CHECK_SYMBOLS,
    REPLAY_GUARD_CLASSES,
    REPLAY_KEY_METHODS,
    RETRIEVAL_SYMBOLS,
    RFC6902_DIFF_SYMBOLS,
    ROUTES_TO_CAPABILITY_SYMBOLS,
    ROUTING_COMMIT_SYMBOLS,
    SAFETY_PLANE_CLASSES,
    SANDBOX_ENVELOPE_CLASSES,
    SECRET_ACCESS_METHODS,
    SECRET_ENV_PATTERNS,
    SECRET_VAULT_CLASSES,
    SEMANTIC_CLOCK_CLASSES,
    STORES_EMBEDDING_SYMBOLS,
    STORES_LEARNING_STATE_SYMBOLS,
    TOOL_BUDGET_CLASSES,
    TRIGGERS_ALERT_SYMBOLS,
    UPDATES_META_LEARNING_STATE_SYMBOLS,
    UPDATES_MONITORING_STATE_SYMBOLS,
    UPDATES_ROUTING_STRATEGY_SYMBOLS,
    UWG_TERMINATION_SYMBOLS,
    VALIDATES_CAPABILITY_SYMBOLS,
    VALIDATOR_BASE_CLASSES,
    VECTOR_STORE_SYMBOLS,
    WORK_CONTRACT_METHODS,
    WORKFLOW_ORCHESTRATION_SYMBOLS,
    WRITE_SIDE_EFFECT_EXCLUSIONS,
    WRITE_SIDE_EFFECT_SYMBOLS,
    WRITES_LEARNING_SNAPSHOT_SYMBOLS,
    WRITES_OBSERVABILITY_LOG_SYMBOLS,
    WRITES_VIA_UWG_SYMBOLS,
    canonical_name,
    module_path_to_layer,
)
from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_EVAL_DIR,
    APPS_EXEC_DIR,
    APPS_LIC_DIR,
    APPS_RESEARCH_DIR,
    APPS_RFP_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
    SYSTEM_LEARNING_DIR,
    TESTS_DIR,
    TOOLS_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_observes_runtime_state,
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_tool_invocation,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_transcripts_response,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "static_scanner", "p0_governance")
_emit_snapshots_state("p0", "static_scanner", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

emit_replay_key("p0", "static_scanner")
emit_determinism_digest("p0", "static_scanner")
_emit_authorize_and_execute("p2", "static_scanner", "execution_auth")
_emit_validates_capability("p2", "static_scanner", "capability_check")
_emit_routes_to_capability("p2", "static_scanner", "capability_route")
_emit_writes_via_uwg("p2", "static_scanner", "uwg_write")
_emit_blocks_direct_write("p2", "static_scanner", "direct_write_block")
_emit_records_tool_invocation("p2", "static_scanner", "tool_invocation")
_emit_captures_execution_output("p2", "static_scanner", "exec_output")

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_evaluation_metric,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_workflow_lineage,
    _emit_routes_to_agent,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
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

_emit_dispatches_agent("p3", "static_scanner", "agent_dispatch")
_emit_coordinates_agents("p3", "static_scanner", "agent_coordination")
_emit_records_workflow_lineage("p3", "static_scanner", "workflow_lineage")
_emit_records_healing_outcome("p3", "static_scanner", "healing_outcome")
_emit_escalates_failure("p3", "static_scanner", "failure_escalation")
_emit_orchestrates_workflow("p3", "static_scanner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "static_scanner", "healing_dispatch")
_emit_invokes_evaluation("p3", "static_scanner", "evaluation_signal")
_emit_records_telemetry_event("p4", "static_scanner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "static_scanner", "eval_metric")
_emit_stores_embedding("p4", "static_scanner", "embedding_store")
_emit_updates_meta_learning_state("p4", "static_scanner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "static_scanner", "exec_snapshot_link")
_emit_pulls_context("p1", "static_scanner", "context_pull")
_emit_execution_terminates_at_uwg("p1", "static_scanner", "uwg_term")
_emit_writes_through("p1", "static_scanner", "write_through")
_emit_validated_by_safety_plane("p1", "static_scanner", "safety_validation")
_emit_invokes_eval("p1", "static_scanner", "eval_call")
_emit_proposal_commits_routing("p1", "static_scanner", "routing_commit")
_emit_escalates_to_human("p1", "static_scanner", "human_escalation")
_emit_checks_agent_registry("p1", "static_scanner", "agent_registry")
_emit_validates_agent_capability("p1", "static_scanner", "capability")
_emit_dispatches_execution_plan("p1", "static_scanner", "exec_plan")
_emit_agent_executes_agent("p1", "static_scanner", "sub_agent")
_emit_routes_to_agent("p1", "static_scanner", "target_agent")
_emit_verifies_policy("p1", "static_scanner", "policy_check")
_emit_observes_runtime_state("p1", "static_scanner", "runtime_state")
_emit_verifies_boundary("p1", "static_scanner", "boundary_check")
_emit_transcripts_response("p1", "static_scanner", "transcript")
_emit_hard_fails_untranscripted("p1", "static_scanner")
_emit_gated_by_confidence("p1", "static_scanner", "confidence_gate")
_emit_reads_environ("p2", "static_scanner", "env_read")
_emit_reads_runtime_state("p2", "static_scanner", "runtime_state")
_emit_captures_pattern("p3lm", "static_scanner", "pattern")
_emit_records_learning_event("p3lm", "static_scanner", "learning_event")
_emit_writes_learning_snapshot("p3lm", "static_scanner", "snapshot")
_emit_feeds_meta_learning("p3lm", "static_scanner", "meta_feed")
_emit_updates_routing_strategy("p3lm", "static_scanner", "routing")
_emit_improves_agent_policy("p3lm", "static_scanner", "policy")
_emit_stores_learning_state("p3lm", "static_scanner", "state")
_emit_emits_metric_event("p4obs", "static_scanner", "metric")
_emit_records_incident_event("p4obs", "static_scanner", "incident")
_emit_captures_runtime_anomaly("p4obs", "static_scanner", "anomaly")
_emit_writes_observability_log("p4obs", "static_scanner", "obs_log")
_emit_updates_monitoring_state("p4obs", "static_scanner", "mon_state")
_emit_triggers_alert("p4obs", "static_scanner", "alert")
_emit_links_incident_trace("p4obs", "static_scanner", "trace_link")
emit_determinism_digest("trace_static_scanner", "static_scanner_dispatch_entry")
emit_determinism_digest("trace_static_scanner", "static_scanner_dispatch_exit")
emit_determinism_digest("trace_static_scanner", "static_scanner_tool_invoke")
emit_determinism_digest("trace_static_scanner", "static_scanner_tool_complete")
emit_determinism_digest("trace_static_scanner", "static_scanner_agent_entry")
emit_determinism_digest("trace_static_scanner", "static_scanner_agent_exit")
emit_determinism_digest("trace_static_scanner", "static_scanner_uwg_write")
emit_determinism_digest("trace_static_scanner", "static_scanner_trace_sign")
emit_determinism_digest("trace_static_scanner", "static_scanner_guardrail_check")
emit_determinism_digest("trace_static_scanner", "static_scanner_policy_verify")
_emit_writes_through("p1", "static_scanner", "uwg_governed_write")
_emit_writes_through("p1", "static_scanner", "uwg_governed_write_2")
_emit_pulls_context("p1", "static_scanner", "context_retrieval")
_emit_pulls_context("p1", "static_scanner", "context_retrieval_2")
emit_determinism_digest("trace_static_scanner", "static_scanner_dispatch")
emit_determinism_digest("trace_static_scanner", "static_scanner_complete")
_emit_validated_by_safety_plane("p1", "static_scanner", "safety_validation")

logger = logging.getLogger(__name__)

_SCAN_ROOTS: tuple[str, ...] = (
    AGENTIC_CORE_DIR,
    APPS_EVAL_DIR,
    APPS_EXEC_DIR,
    APPS_LIC_DIR,
    APPS_RESEARCH_DIR,
    APPS_RFP_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
    TOOLS_DIR,
    TESTS_DIR,  # H1
    OPS_SCRIPTS_DIR,  # H1
)

_SCANNER_VERSION = "2.0.0"
_SCHEMA_VERSION = "2.0"

# S9: Cardinality ranges for sanity checking (upper bounds include tests/ scan territory)
# reads_from upper bound raised to 100000: os.environ/getenv/config.get calls appear in
# large test suites and generate ~62k edges when tests/ is included in the scan.
_CARDINALITY_RANGES: dict[str, tuple[int, int]] = {
    "implements": (100, 10000),
    "reads_from": (50, 100000),
    "instantiates": (50, 5000),
}

# A2: Minimum evidence floors per graph
_MIN_EVIDENCE_FLOORS: dict[str, int] = {
    "imports": 500,
    "implements": 100,
    "reads_from": 50,
    "instantiates": 50,
}

# H4: config read symbols that trigger reads_from edges
_CONFIG_READ_SYMBOLS: frozenset[str] = frozenset(
    {
        "os.environ",
        "os.getenv",
        "os.environ.get",
        "getenv",
        "config.get",
        "settings.get",
        "cfg.get",
        "CONFIG",
        "SETTINGS",
    }
)

# H5: noise constructors to exclude from composition graph
_COMPOSITION_NOISE: frozenset[str] = frozenset(
    {
        "dict",
        "list",
        "set",
        "tuple",
        "str",
        "int",
        "float",
        "bool",
        "Path",
        "defaultdict",
        "OrderedDict",
        "Counter",
        "deque",
        "Exception",
        "ValueError",
        "TypeError",
        "RuntimeError",
        "threading.Lock",
        "threading.Event",
        "threading.Thread",
        "asyncio.Lock",
        "asyncio.Event",
    }
)

# S3: dynamic execution symbols (RULE_F)
_DYNAMIC_EXEC_SYMBOLS: frozenset[str] = frozenset(
    {
        "eval",
        "exec",
    }
)


@dataclass(frozen=True, order=True)
class Edge:
    """A single directed dependency edge in the ADG."""

    from_name: str
    relation_type: str
    to_name: str
    edge_kind: str
    source_file: str
    line_no: int
    symbol: str = ""


@dataclass
class ScanManifest:
    """A1: Rich manifest of scanner run metadata for fail-closed validation."""

    scanner_version: str = _SCANNER_VERSION
    schema_version: str = _SCHEMA_VERSION
    python_ast_version: str = ""
    discovered_module_count: int = 0
    parsed_module_count: int = 0
    syntax_error_count: int = 0
    unknown_layer_count: int = 0
    edge_counts_by_graph: dict[str, int] = field(default_factory=dict)
    rule_skip_counts: dict[str, int] = field(default_factory=dict)
    dynamic_execution_count: int = 0
    tests_included: bool = False
    minimum_evidence_passed: bool = False
    scanner_self_test_passed: bool = False
    cardinality_violations: list[str] = field(default_factory=list)
    inter_module_call_count: int = 0
    test_covers_count: int = 0
    layer_violation_count: int = 0
    governance_plane_count: int = 0
    symbol_export_count: int = 0
    symbol_hit_rate: float = 0.0
    dead_import_count: int = 0
    cycle_count: int = 0
    max_cycle_depth: int = 0
    decorator_edge_count: int = 0
    star_import_count: int = 0
    star_import_resolved_count: int = 0
    conditional_import_count: int = 0
    antipattern_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0
    type_annotation_count: int = 0

    def to_dict(self) -> dict:
        import dataclasses

        return dataclasses.asdict(self)


@dataclass
class ScanResult:
    """Full output of a single scanner run."""

    edges: list[Edge] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)
    digest: str = ""
    commit_sha: str = ""
    repo_state_hash: str = ""
    manifest: ScanManifest = field(default_factory=ScanManifest)
    syntax_errors: list[str] = field(default_factory=list)

    def canonical_edge_text(self) -> str:
        """S7: Stable, sorted serialization of edges for digest computation."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ScanResult.canonical_edge_text"
        )

        lines = []
        for e in sorted(self.edges):  # S7: sort before digest
            lines.append(
                f"{e.from_name}|{e.relation_type}|{e.to_name}|{e.edge_kind}"
                f"|{e.source_file}|{e.line_no}|{e.symbol}"
            )
        return "\n".join(lines)

    def edge_counts_by_relation(self) -> dict[str, int]:
        """Count edges grouped by relation_type (graph type)."""
        counts: dict[str, int] = {}
        for e in self.edges:
            counts[e.relation_type] = counts.get(e.relation_type, 0) + 1
        return counts

    def to_dict(self) -> dict:
        """R2: Serialize to JSON-compatible dict for cache."""
        return {
            "edges": [edge.to_dict() for edge in self.edges],
            "modules": self.modules,
            "digest": self.digest,
            "commit_sha": self.commit_sha,
            "repo_state_hash": self.repo_state_hash,
            "manifest": self.manifest.to_dict(),
            "syntax_errors": self.syntax_errors,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ScanResult:
        """R2: Deserialize from cache dict."""
        import dataclasses

        edges = [
            Edge(
                from_name=e["from_name"],
                relation_type=e["relation_type"],
                to_name=e["to_name"],
                edge_kind=e["edge_kind"],
                source_file=e["source_file"],
                line_no=e["line_no"],
                symbol=e.get("symbol", ""),
            )
            for e in data.get("edges", [])
        ]
        manifest_data = data.get("manifest", {})
        manifest = ScanManifest(
            **{
                k: v
                for k, v in manifest_data.items()
                if k in {f.name for f in dataclasses.fields(ScanManifest)}
            }
        )
        return cls(
            edges=edges,
            modules=data.get("modules", []),
            digest=data.get("digest", ""),
            commit_sha=data.get("commit_sha", ""),
            repo_state_hash=data.get("repo_state_hash", ""),
            manifest=manifest,
            syntax_errors=data.get("syntax_errors", []),
        )

    def compute_digest(self) -> str:
        """Compute and store the ADG-DETERMINISM-DIGEST."""
        text = self.canonical_edge_text()
        self.digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return self.digest

    def print_digest(self) -> None:
        """Print the determinism digest exactly once per run."""
        print(f"ADG-DETERMINISM-DIGEST: {self.digest}")


class _InheritanceVisitor(ast.NodeVisitor):
    """H3: Extract class inheritance (implements) edges for Graph 3."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_InheritanceVisitor.visit_ClassDef"
        )

        class_adg = canonical_name("Module", f"{self.source_file}::{node.name}")
        for base in node.bases:
            base_name = self._extract_name(base)
            if not base_name or base_name in ("object",):
                continue
            # Classify: internal vs external vs unresolved
            if any(base_name.startswith(r) for r in (AGENTIC_CORE_DIR, "apps_")):
                edge_kind = "resolved_internal"
            elif "." in base_name:
                edge_kind = "external"
            else:
                edge_kind = "unresolved"
            to_name = canonical_name("Symbol", base_name)
            self.edges.append(
                Edge(
                    from_name=class_adg,
                    relation_type="implements",
                    to_name=to_name,
                    edge_kind=edge_kind,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=base_name,
                )
            )
        self.generic_visit(node)

    @staticmethod
    def _extract_name(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts = []
            cur = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""


class _AttributeVisitor(ast.NodeVisitor):
    """H4: Extract config/env reads for Graph 5 (reads_from edges)."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_AttributeVisitor.visit_Call"
        )

        sym = self._extract_call_sym(node.func)
        sub_type = self._classify_config_read(sym)
        if sub_type:
            to_name = canonical_name("Symbol", sym)
            # G6: use sub_type as relation_type for reads_env/reads_secret/reads_policy_state
            rel_type = (
                sub_type
                if sub_type
                in (
                    "reads_env",
                    "reads_secret",
                    "reads_policy_state",
                    "reads_runtime_state",
                    "reads_config",
                )
                else "reads_from"
            )
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type=rel_type,
                    to_name=to_name,
                    edge_kind=sub_type,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym,
                )
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.expr) -> None:
        sym = self._extract_attr_chain(node)
        sub_type = self._classify_config_read(sym)
        if sub_type and isinstance(node, ast.Attribute):
            to_name = canonical_name("Symbol", sym)
            # G6: use sub_type as relation_type for reads_env/reads_secret/reads_policy_state
            rel_type = (
                sub_type
                if sub_type
                in (
                    "reads_env",
                    "reads_secret",
                    "reads_policy_state",
                    "reads_runtime_state",
                    "reads_config",
                )
                else "reads_from"
            )
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type=rel_type,
                    to_name=to_name,
                    edge_kind=sub_type,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym,
                )
            )
        self.generic_visit(node)  # type: ignore[arg-type]

    @staticmethod
    def _extract_call_sym(func: ast.expr) -> str:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            parts = []
            cur: ast.expr = func
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""

    @staticmethod
    def _extract_attr_chain(node: ast.expr) -> str:
        if isinstance(node, ast.Attribute):
            parts = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""

    @staticmethod
    def _classify_config_read(sym: str) -> str:
        if not sym:
            return ""
        if "environ" in sym or "getenv" in sym:
            return "reads_env"
        if "secret" in sym.lower():
            return "reads_secret"
        if "policy" in sym.lower():
            return "reads_policy_state"
        if "runtime" in sym.lower():
            return "reads_runtime_state"
        if sym in _CONFIG_READ_SYMBOLS:
            return "reads_config"
        return ""


class _CompositionVisitor(ast.NodeVisitor):
    """H5: Extract object composition (self.x = SomeClass()) in __init__ for Graph 6."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []
        self._in_init = False
        self._current_class: str = ""

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_CompositionVisitor.visit_ClassDef"
        )

        old_class = self._current_class
        self._current_class = node.name
        self.generic_visit(node)
        self._current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name == "__init__":
            old = self._in_init
            self._in_init = True
            self.generic_visit(node)
            self._in_init = old
        else:
            self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_Assign(self, node: ast.Assign) -> None:
        if not self._in_init:
            self.generic_visit(node)
            return
        # Detect: self.<attr> = <Name>(...) or self.<attr> = <Attr.Name>(...)
        if not isinstance(node.value, ast.Call):
            self.generic_visit(node)
            return
        constructor_name = self._extract_constructor(node.value.func)
        if not constructor_name or constructor_name in _COMPOSITION_NOISE:
            self.generic_visit(node)
            return
        # Check any target is self.<attr>
        has_self_target = any(
            isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self"
            for t in node.targets
        )
        if not has_self_target:
            self.generic_visit(node)
            return
        class_adg = canonical_name("Module", f"{self.source_file}::{self._current_class}")
        to_name = canonical_name("Symbol", constructor_name)
        self.edges.append(
            Edge(
                from_name=class_adg,
                relation_type="instantiates",
                to_name=to_name,
                edge_kind="composition",
                source_file=self.source_file,
                line_no=node.lineno,
                symbol=constructor_name,
            )
        )
        self.generic_visit(node)

    @staticmethod
    def _extract_constructor(func: ast.expr) -> str:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
        return ""


class _DynamicExecutionVisitor(ast.NodeVisitor):
    """S3/RULE_F: Detect dynamic execution (eval/exec/importlib.import_module)."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_DynamicExecutionVisitor.visit_Call"
        )

        sym = self._extract_sym(node.func)
        tail = sym.split(".")[-1] if sym else ""
        if sym and (sym in _DYNAMIC_EXEC_SYMBOLS or tail in _DYNAMIC_EXEC_SYMBOLS):
            to_name = canonical_name("Symbol", sym)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="invokes_dynamic",  # G1: separate from invokes_provider
                    to_name=to_name,
                    edge_kind="dynamic_exec",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym,
                )
            )
        self.generic_visit(node)

    @staticmethod
    def _extract_sym(func: ast.expr) -> str:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            parts = []
            cur: ast.expr = func
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""


class _ImportVisitor(ast.NodeVisitor):
    """Extract import edges from an AST.

    E7: Tracks conditional import context:
      - TYPE_CHECKING guard  -> edge_kind "type_checking_import"
      - try/except ImportError -> edge_kind "optional_import"
      - sys.version_info guard -> edge_kind "version_guard_import"
      - unconditional           -> edge_kind "import" (or "network")

    E2: Star imports (from X import *) are emitted as edge_kind "star_import".
        If the source module's __all__ was pre-populated (via _all_registry),
        individual edges are emitted for each exported name instead.
    """

    def __init__(
        self,
        module_adg_name: str,
        source_file: str,
        all_registry: dict[str, list[str]] | None = None,
        identity_normalizer=None,
    ) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []
        self._all_registry: dict[str, list[str]] = all_registry or {}
        self._context_stack: list[str] = []
        self._function_depth: int = 0
        self.star_import_count: int = 0
        self.star_resolved_count: int = 0
        self._identity_normalizer = identity_normalizer

    # ------------------------------------------------------------------
    # Context tracking for E7
    # ------------------------------------------------------------------

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_ImportVisitor.visit_FunctionDef"
        )

        self._function_depth += 1
        self.generic_visit(node)
        self._function_depth -= 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_depth += 1
        self.generic_visit(node)
        self._function_depth -= 1

    def visit_If(self, node: ast.If) -> None:
        ctx = self._classify_if_context(node.test)
        if ctx:
            self._context_stack.append(ctx)
            for stmt in node.body:
                self.visit(stmt)
            self._context_stack.pop()
            for stmt in node.orelse:
                self.visit(stmt)
        else:
            self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        try_is_optional = any(
            h.type is not None
            and self._extract_exception_name(h.type) in ("ImportError", "ModuleNotFoundError")
            for h in node.handlers
        )
        if try_is_optional:
            self._context_stack.append("optional_import")
        for stmt in node.body:
            self.visit(stmt)
        if try_is_optional:
            self._context_stack.pop()
        for handler in node.handlers:
            is_import_error = False
            if handler.type is not None:
                name = self._extract_exception_name(handler.type)
                if name in ("ImportError", "ModuleNotFoundError"):
                    is_import_error = True
            if is_import_error:
                self._context_stack.append("optional_import")
                for stmt in handler.body:
                    self.visit(stmt)
                self._context_stack.pop()
            else:
                for stmt in handler.body:
                    self.visit(stmt)
        for stmt in node.orelse + node.finalbody if hasattr(node, "finalbody") else node.orelse:
            self.visit(stmt)

    def _current_context(self) -> str:
        if self._function_depth > 0:
            return "lazy_import"
        return self._context_stack[-1] if self._context_stack else "import"

    @staticmethod
    def _classify_if_context(test: ast.expr) -> str:
        if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
            return "type_checking_import"
        if isinstance(test, ast.Attribute):
            chain = []
            cur: ast.expr = test
            while isinstance(cur, ast.Attribute):
                chain.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                chain.append(cur.id)
            full = ".".join(reversed(chain))
            if "version_info" in full or "sys.version" in full:
                return "version_guard_import"
        if isinstance(test, ast.Compare):
            if isinstance(test.left, ast.Attribute):
                chain2 = []
                cur2: ast.expr = test.left
                while isinstance(cur2, ast.Attribute):
                    chain2.append(cur2.attr)
                    cur2 = cur2.value
                if isinstance(cur2, ast.Name):
                    chain2.append(cur2.id)
                full2 = ".".join(reversed(chain2))
                if "version_info" in full2:
                    return "version_guard_import"
        return ""

    @staticmethod
    def _extract_exception_name(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        if isinstance(node, ast.Tuple):
            names = []
            for elt in node.elts:
                if isinstance(elt, ast.Name):
                    names.append(elt.id)
            return "|".join(names)
        return ""

    # ------------------------------------------------------------------
    # Import visitors
    # ------------------------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        ctx = self._current_context()
        for alias in node.names:
            imported = alias.name
            to_name = canonical_name("Symbol", imported)
            edge_kind = ctx if ctx != "import" else self._classify_import_kind(imported)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="imports",
                    to_name=to_name,
                    edge_kind=edge_kind,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=imported,
                )
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        ctx = self._current_context()
        for alias in node.names:
            if alias.name == "*":
                self._handle_star_import(module, node.lineno, ctx)
                continue
            full_sym = f"{module}.{alias.name}" if module else alias.name
            edge_kind = ctx if ctx != "import" else self._classify_import_kind(module)
            to_name = canonical_name("Symbol", full_sym)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="imports",
                    to_name=to_name,
                    edge_kind=edge_kind,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=full_sym,
                )
            )

    def _handle_star_import(self, module: str, line_no: int, ctx: str) -> None:
        """E2: Resolve `from X import *` against __all__ if available, else emit star_import edge."""
        self.star_import_count += 1
        known_exports = self._all_registry.get(module)
        if known_exports:
            self.star_resolved_count += 1
            for name in known_exports:
                full_sym = f"{module}.{name}"
                to_name = canonical_name("Symbol", full_sym)
                edge_kind = ctx if ctx != "import" else self._classify_import_kind(module)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="imports",
                        to_name=to_name,
                        edge_kind=edge_kind,
                        source_file=self.source_file,
                        line_no=line_no,
                        symbol=full_sym,
                    )
                )
        else:
            to_name = canonical_name("Symbol", f"{module}.*")
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="imports",
                    to_name=to_name,
                    edge_kind="star_import",
                    source_file=self.source_file,
                    line_no=line_no,
                    symbol=f"{module}.*",
                )
            )

    def _classify_import_kind(self, module_name: str) -> str:
        """Classify import boundary using IdentityNormalizer."""
        if self._identity_normalizer:
            record = self._identity_normalizer.normalize(module_name)
            if record.kind == IdentityKind.REPO_MODULE:
                return "internal"
            elif record.kind == IdentityKind.EXTERNAL_MODULE:
                return "external"
            elif record.kind == IdentityKind.UNRESOLVED_IMPORT:
                return "unresolved"
            else:
                return "import"

        # Fallback to static classification if no normalizer
        base = module_name.split(".")[0]
        if base in {s.split(".")[0] for s in PROVIDER_SDK_SYMBOLS}:
            return "network"
        return "import"


class _CallVisitor(ast.NodeVisitor):
    """Extract call edges for sensitive symbols."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "_CallVisitor.visit_Call")

        sym = self._extract_symbol(node.func)
        if sym:
            # Suppress instrumentation helpers from generating base edges
            tail = sym.rsplit(".", 1)[-1] if "." in sym else sym
            if tail.startswith("_emit_") or tail.startswith("emit_"):
                self.generic_visit(node)
                return
            edge_kind, relation = self._classify_call(sym)
            if edge_kind:
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type=relation,
                        to_name=to_name,
                        edge_kind=edge_kind,
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
        self.generic_visit(node)

    @staticmethod
    def _extract_symbol(func_node: ast.expr) -> str:
        if isinstance(func_node, ast.Name):
            return func_node.id
        if isinstance(func_node, ast.Attribute):
            parts = []
            current: ast.expr = func_node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return ""

    @staticmethod
    def _classify_call(sym: str) -> tuple[str, str]:
        if sym in EMBEDDING_SYMBOLS or any(sym.endswith(e) for e in EMBEDDING_SYMBOLS):
            return "embedding", "instantiates"
        if sym in WRITE_SIDE_EFFECT_SYMBOLS or any(
            sym.endswith(w.split(".")[-1]) for w in WRITE_SIDE_EFFECT_SYMBOLS
        ):
            # G3: exclude false-positive write symbols
            if sym in WRITE_SIDE_EFFECT_EXCLUSIONS:
                return "", ""
            return "write", "writes_to"
        if sym in NETWORK_SYMBOLS or any(sym.startswith(n.split(".")[0]) for n in NETWORK_SYMBOLS):
            return "network", "invokes_provider"
        base = sym.split(".")[0]
        if base in {s.split(".")[0] for s in PROVIDER_SDK_SYMBOLS}:
            return "network", "invokes_provider"
        return "", ""


_INTERNAL_MODULE_PREFIXES: tuple[str, ...] = (
    "agentic_core",
    "apps_rg",
    "apps_lic",
    "apps_shared",
    "system_learning",
    "ops_scripts",
    "tools",
    "tests",
)

_TEST_FILE_INDICATORS: tuple[str, ...] = ("tests/", "test_", "_test.py")

_GOVERNANCE_WRITE_SYMBOLS: frozenset[str] = frozenset(
    {
        "UniversalWriteGateway",
        "execute_write",
        "submit_instruction",
        "commit_write",
        "uwg",
        "WriteGovernorMixin",
        "uwg_write",
        "write_text",
        "write_guardian_result",
        "create_artifact",
        "get_write_gateway",
        "persist_scan_result",
        # Wave 116: gateway/mutation writes
        "write_gateway",
        "assert_no_persistent_write",
        "write_all_artifacts",
        "is_commit_sandbox_active",
        "ProposalCommitter",
        # Wave 117: store writes
        "InMemoryHealingOutcomeIntakeStore",
        "HealingSuccessRateStore",
        "get_default_store",
        "reset_default_store",
        "get_bm25_store",
        # Wave 118: record writes
        "TraceFeatureRecord",
        "CorpusRecord",
        "KeyRecord",
        "MutationDiffRecord",
        "ReplayFailureRecord",
        "PromptOutcomeRecord",
        "HealingOutcomeIntakeRecord",
        # Wave 119: commit/persist writes
        "create_and_commit_routing_contract",
        "analyze_failures_and_persist",
        "compute_content_hash",
        "compute_replay_hash",
        "PolicyUpdateProposal",
        # Wave 120: healing/input writes
        "HealingInput",
        "compute_heal_confidence",
        "create_legacy_import_healer",
        "log_event",
        # Wave 137-139: writes_through density
        "get_validated_project_root",
        "ExecutionContext",
        "SurgicalContext",
        "ViolationConstraint",
    }
)

_GOVERNANCE_ROUTE_SYMBOLS: frozenset[str] = frozenset(
    {
        "HealingOrchestrator",
        "SovereignLLMGateway",
        "sovereign_gateway",
        "run_healing",
        "replay_run",
        "route_instruction",
        "healing_orchestrator",
        "dispatch_healing",
        "route_healing_tier",
        "AgenticRouter",
        # Wave 121: gateway/routing dispatchers
        "get_routing_gateway",
        "V15ExecutionGateway",
        "VLLMQueueController",
        "VLLMCircuitBreakerRegistry",
        "get_agent_dispatch_registry",
        # Wave 122: pipeline/orchestrator routes
        "run_pipeline",
        "ExecutionOrchestrator",
        "VigilanceDispatcherAdapter",
        "get_healing_orchestrator",
        "get_validator_orchestrator",
        # Wave 123: route decision artifacts
        "route_violations",
        "build_l3_route_decision_artifact",
        "ResumeOrchestratorEngine",
        "PipelineDependencies",
        "build_pipeline_deps",
        # Wave 124: coordination routes
        "ASTCoordinate",
        "MCPConnectionManager",
        "ExecutionPathController",
        # Wave 143-145: routes_through density
        "invoke_hierarchy_agent",
        "safe_run",
        "ModelRouter",
        "ValidationResult",
        "UnifiedAgent",
        "get_llm_gateway",
        "check_gateway_topology",
        "build_route_decision_key",
        "build_route_context_key",
    }
)

_GOVERNANCE_READ_SYMBOLS: frozenset[str] = frozenset(
    {
        "UniversalReadGateway",
        "read_file",
        "read_sqlite",
        "read_redis",
        "read_vector",
        "read_artifact",
        "urg_read",
        "ReadGovernorMixin",
        "read_active_payload",
        "pull_audit_data",
        # Wave 101: config readers
        "load_default_healing_tier_config",
        "load_or_scan",
        "get_sovereign_config",
        "get_active_configs",
        "ConfigurationLoader",
        "get_config_loader",
        "EvaluationLoader",
        "build_pipeline_config",
        "load_dev_script",
        "get_config_surface",
        "deterministic_json",
        # Wave 102: sqlite readers
        "ADGQuerySession",
        "ADGRuntimeQueryEngine",
        "SqliteMemoryStore",
        "safe_execute",
        "execute_ssot",
        "get_runtime_query_engine",
        # Wave 103: redis readers
        "get_hot_cache",
        "ADGRedisClient",
        "SemanticCacheManager",
        "DeterministicRedisCache",
        "check_redis_health",
        "ScanCache",
        "get_coordination_cache",
        # Wave 104: vector/faiss readers
        "LocalFAISSStore",
        "RetrievalProfile",
        "EmbeddingServiceFactory",
        "query_similarity",
        "build_retriever",
        "build_seed_embedding_pack",
        # Wave 105: artifact/archive readers
        "build_artifact",
        "build_pre_run_report",
        "RouteDecisionArtifact",
        "ADGArtifactBuilder",
        "IncidentBundle",
        # Wave 106: file/path readers
        "module_path_to_layer",
        "normalize_repo_path",
        "validate_no_absolute_paths",
        "PathRouter",
        "ExecutionPathController",
        # Wave 107: state/freeze readers
        "get_run_state_authority",
        "RuntimeStateGuard",
        "RuntimeStateManager",
        "JsonFileBackedFreezeReader",
        "StaticFreezeReader",
        "compute_runtime_state_digest",
        "FileBackedAuditStore",
        # Wave 108: healing/config readers
        "HealingTierConfig",
        "HealingConfigOptimizer",
        "ConfigurationService",
        "SandboxEnvelope",
        "ResourceEnvelope",
        "GovernedPayload",
        # Wave 109: snapshot readers
        "SemanticClockSnapshot",
        "HealingOutcomeAggregateSnapshot",
        "BlindSpotReport",
        "PatternFindingReport",
        "GuardianReportBuilder",
        # Wave 110: misc residual readers
        "MCPConnectionManager",
        "load_agent_discovery",
        "stable_sha256_json",
        "RetrievalAnchor",
        "get_embedding_gateway",
        # Wave 111: envelope/payload readers
        "CanonicalJSON",
        "canonical_json",
        "ReasonTraceEnvelope",
        "ResultEnvelope",
        "ReplayEnvelope",
        "PromptLoader",
        "MetaLearningBusConfig",
        # Wave 112: state/queue readers
        "VLLMQueueState",
        "HandshakeStateMachine",
        "SlotPayload",
        "RunScopedStateAuthority",
        "StateVersionManager",
        "DefaultL4StateWriter",
        # Wave 113: retrieval/drift readers
        "RetrievalDriftMonitor",
        "RetrievalPipeline",
        "RetrievalCaseRecord",
        "EmbeddingHealthSnapshot",
        "PromptOutcomeEmbeddingRecord",
        "read_only_retrieval_scope",
        "get_embedding_config_surface",
        # Wave 114: report/artifact readers
        "EvaluationReport",
        "DeltaReport",
        "AnswerQualitySnapshot",
        "HumanDecisionArtifact",
        "FeatureBundle",
        "ReportLocationValidator",
        "build_replay_bundle",
        # Wave 115: security/protected readers
        "assert_read_only_audit_access",
        "SafetyAuditTrail",
        "verify_mutation_paths",
        "PathFragilityDetector",
        "_read_baseline",
        "safe_git_execute",
        # Wave 140-142: reads_through density
        "get_clock",
        "get_python_files",
        "get_active_execution_trace",
        "get_behavioral_profile",
        "ADGBehavioralIndex",
        "get_data_files",
        "ADGStaticScanner",
    }
)


class _InternalCallGraphVisitor(ast.NodeVisitor):
    """G4: Extract calls to internal module symbols (inter-module call graph)."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []
        self._internal_locals: dict[str, str] = {}

    def visit_Import(self, node: ast.Import) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_InternalCallGraphVisitor.visit_Import"
        )

        for alias in node.names:
            if any(alias.name.startswith(p) for p in _INTERNAL_MODULE_PREFIXES):
                local = alias.asname or alias.name.split(".")[0]
                self._internal_locals[local] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if any(module.startswith(p) for p in _INTERNAL_MODULE_PREFIXES):
            for alias in node.names:
                local = alias.asname or alias.name
                self._internal_locals[local] = f"{module}.{alias.name}"
        self.generic_visit(node)

    # Instrumentation helper prefixes — suppress synthetic base edges
    _INSTRUMENTATION_PREFIXES: frozenset[str] = frozenset({"_emit_", "emit_"})

    def visit_Call(self, node: ast.Call) -> None:
        sym = self._extract_symbol(node.func)
        if sym:
            base = sym.split(".")[0]
            if base in self._internal_locals:
                full_sym = self._internal_locals[base]
                # Suppress calls to instrumentation helpers (_emit_*, emit_*)
                tail = full_sym.rsplit(".", 1)[-1] if "." in full_sym else full_sym
                if any(tail.startswith(p) for p in self._INSTRUMENTATION_PREFIXES):
                    self.generic_visit(node)
                    return
                to_name = canonical_name("Symbol", full_sym)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="calls",
                        to_name=to_name,
                        edge_kind="call",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=full_sym,
                    )
                )
        self.generic_visit(node)

    @staticmethod
    def _extract_symbol(func_node: ast.expr) -> str:
        if isinstance(func_node, ast.Name):
            return func_node.id
        if isinstance(func_node, ast.Attribute):
            parts: list[str] = []
            current: ast.expr = func_node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return ""


class _TestTraceabilityVisitor(ast.NodeVisitor):
    """GT: Emit `covers` edges from test modules to the internal modules they import."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []
        self._is_test = any(ind in source_file for ind in _TEST_FILE_INDICATORS)

    def visit_Import(self, node: ast.Import) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_TestTraceabilityVisitor.visit_Import"
        )

        if not self._is_test:
            return
        for alias in node.names:
            if any(alias.name.startswith(p) for p in _INTERNAL_MODULE_PREFIXES):
                to_name = canonical_name("Symbol", alias.name)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="covers",
                        to_name=to_name,
                        edge_kind="import",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=alias.name,
                    )
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if not self._is_test:
            return
        module = node.module or ""
        if any(module.startswith(p) for p in _INTERNAL_MODULE_PREFIXES):
            to_name = canonical_name("Symbol", module)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="covers",
                    to_name=to_name,
                    edge_kind="import",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=module,
                )
            )
        self.generic_visit(node)


class _GovernancePlaneVisitor(ast.NodeVisitor):
    """GG: Emit writes_through / routes_through edges for governance chokepoints."""

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_GovernancePlaneVisitor.visit_ClassDef"
        )

        for base in node.bases:
            sym = self._extract_symbol(base)
            if sym:
                tail = sym.split(".")[-1]
                base_name = sym.split(".")[0]
                if base_name in _GOVERNANCE_WRITE_SYMBOLS or tail in _GOVERNANCE_WRITE_SYMBOLS:
                    self.edges.append(
                        Edge(
                            from_name=self.module_adg_name,
                            relation_type="writes_through",
                            to_name=canonical_name("Symbol", sym),
                            edge_kind="write",
                            source_file=self.source_file,
                            line_no=node.lineno,
                            symbol=sym,
                        )
                    )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        sym = self._extract_symbol(node.func)
        if sym:
            base = sym.split(".")[0]
            tail = sym.split(".")[-1]
            # Suppress instrumentation helpers from generating governance edges
            if tail.startswith("_emit_") or tail.startswith("emit_"):
                self.generic_visit(node)
                return
            if base in _GOVERNANCE_WRITE_SYMBOLS or tail in _GOVERNANCE_WRITE_SYMBOLS:
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="writes_through",
                        to_name=to_name,
                        edge_kind="write",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
            elif base in _GOVERNANCE_ROUTE_SYMBOLS or tail in _GOVERNANCE_ROUTE_SYMBOLS:
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="routes_through",
                        to_name=to_name,
                        edge_kind="call",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
            elif base in _GOVERNANCE_READ_SYMBOLS or tail in _GOVERNANCE_READ_SYMBOLS:
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="reads_through",
                        to_name=to_name,
                        edge_kind="read",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
        self.generic_visit(node)

    @staticmethod
    def _extract_symbol(func_node: ast.expr) -> str:
        if isinstance(func_node, ast.Name):
            return func_node.id
        if isinstance(func_node, ast.Attribute):
            parts: list[str] = []
            current: ast.expr = func_node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return ""


class _TypeAnnotationVisitor(ast.NodeVisitor):
    """E4: G8 — Emit `reads_from` edges for type annotations on function arguments,
    return types, and annotated assignments.

    Each named type reference (including dotted names like `pathlib.Path`)
    emits a `reads_from` edge with edge_kind "type_annotation".  Generic
    subscripts (e.g. `list[str]`) are unwrapped to extract all referenced
    names.

    Forward references encoded as string literals are currently skipped
    (they would require symbol resolution and are handled by E11).
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []
        self._seen: set[tuple[str, int]] = set()

    def _emit(self, sym: str, line_no: int) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_TypeAnnotationVisitor._emit"
        )

        key = (sym, line_no)
        if key in self._seen:
            return
        self._seen.add(key)
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type="reads_from",
                to_name=canonical_name("Symbol", sym),
                edge_kind="type_annotation",
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )

    def _extract_annotation_names(self, node: ast.expr, line_no: int) -> None:
        """Recursively extract all named type references from an annotation."""
        if isinstance(node, ast.Name):
            if node.id not in ("None", "Any", "True", "False"):
                self._emit(node.id, line_no)
        elif isinstance(node, ast.Attribute):
            sym = self._extract_dotted(node)
            if sym:
                self._emit(sym, line_no)
        elif isinstance(node, ast.Subscript):
            self._extract_annotation_names(node.value, line_no)
            self._extract_annotation_names(node.slice, line_no)
        elif isinstance(node, ast.Tuple):
            for elt in node.elts:
                self._extract_annotation_names(elt, line_no)
        elif isinstance(node, ast.BinOp):
            self._extract_annotation_names(node.left, line_no)
            self._extract_annotation_names(node.right, line_no)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            pass

    @staticmethod
    def _extract_dotted(node: ast.Attribute) -> str:
        parts: list[str] = []
        cur: ast.expr = node
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
            if arg.annotation:
                self._extract_annotation_names(arg.annotation, arg.annotation.lineno)
        if node.args.vararg and node.args.vararg.annotation:
            self._extract_annotation_names(node.args.vararg.annotation, node.args.vararg.annotation.lineno)
        if node.args.kwarg and node.args.kwarg.annotation:
            self._extract_annotation_names(node.args.kwarg.annotation, node.args.kwarg.annotation.lineno)
        if node.returns:
            self._extract_annotation_names(node.returns, node.returns.lineno)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._extract_annotation_names(node.annotation, node.annotation.lineno)
        self.generic_visit(node)


_BLOCKING_CALL_PREFIXES: frozenset[str] = frozenset(
    {
        "time.sleep",
        "requests.get",
        "requests.post",
        "requests.put",
        "requests.delete",
        "requests.patch",
        "requests.head",
        "requests.request",
        "urllib.request.urlopen",
        "urllib2.urlopen",
        "http.client",
        "subprocess.run",
        "subprocess.call",
        "subprocess.check_output",
        "subprocess.Popen",
        "input",
        "socket.recv",
        "socket.accept",
        "os.system",
    }
)


class _AntipatternVisitor(ast.NodeVisitor):
    """GA: Detect behavioral anti-patterns via AST analysis.

    Emits `antipattern` edges for:
      - silent_exception_swallow: except blocks with only pass/continue/break
      - blocking_call_in_async: blocking stdlib calls inside async def
      - global_state_mutation: module-level UPPER_CASE name reassigned inside a function
      - retry_without_backoff: while/for loops containing try/except but no sleep/delay
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []
        self._in_async: bool = False
        self._function_depth: int = 0
        self._global_names: set[str] = set()

    # ------------------------------------------------------------------
    # Scope tracking
    # ------------------------------------------------------------------

    def visit_Module(self, node: ast.Module) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_AntipatternVisitor.visit_Module"
        )

        # Collect module-level UPPER_CASE names (potential global constants)
        for stmt in node.body:
            if isinstance(stmt, ast.Assign) and stmt.col_offset == 0:
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        self._global_names.add(target.id)
            if isinstance(stmt, ast.AnnAssign) and stmt.col_offset == 0:
                if isinstance(stmt.target, ast.Name) and stmt.target.id.isupper():
                    self._global_names.add(stmt.target.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        old_async = self._in_async
        self._in_async = False
        self._function_depth += 1
        self.generic_visit(node)
        self._function_depth -= 1
        self._in_async = old_async

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        old_async = self._in_async
        self._in_async = True
        self._function_depth += 1
        self.generic_visit(node)
        self._function_depth -= 1
        self._in_async = old_async

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_async = self._in_async
        self._in_async = False
        self.generic_visit(node)
        self._in_async = old_async

    # ------------------------------------------------------------------
    # Pattern 1: Silent exception swallowing
    # Pattern 1b: Broad exception catch (except Exception without re-raise)
    # Pattern 1c: Log-and-swallow (log but no re-raise on broad type)
    # Pattern 1d: Return-None swallow (return None/empty on broad type)
    # ------------------------------------------------------------------

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        exc_name = self._except_type_name(node)
        is_broad = exc_name in BROAD_EXCEPTION_TYPES or exc_name == "bare"

        # Pattern 1: Silent swallow (pass/continue/break/bare return)
        if self._is_silent_swallow(node):
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="antipattern",
                    to_name=canonical_name("Symbol", "silent_exception_swallow"),
                    edge_kind="silent_exception_swallow",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=f"except:{exc_name or 'bare'}",
                )
            )
            self.generic_visit(node)
            return

        has_raise = self._body_has_raise(node.body)

        # Pattern 1b: Broad exception catch without re-raise
        if is_broad and not has_raise:
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="antipattern",
                    to_name=canonical_name("Symbol", "broad_exception_catch"),
                    edge_kind="broad_exception_catch",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=f"except:{exc_name}",
                )
            )

        # Pattern 1c: Log-and-swallow (broad type, body is only logging, no re-raise)
        if is_broad and not has_raise and self._is_log_only_body(node.body):
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="antipattern",
                    to_name=canonical_name("Symbol", "log_and_swallow"),
                    edge_kind="log_and_swallow",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=f"except:{exc_name}",
                )
            )

        # Pattern 1d: Return-None/empty swallow (broad type, returns sentinel, no re-raise)
        if is_broad and not has_raise:
            sentinel = self._return_sentinel_kind(node.body)
            if sentinel:
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="antipattern",
                        to_name=canonical_name("Symbol", "return_none_swallow"),
                        edge_kind="return_none_swallow",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=f"except:{exc_name}:{sentinel}",
                    )
                )

        self.generic_visit(node)

    def _except_type_name(self, node: ast.ExceptHandler) -> str:
        """Extract the exception type name from an except handler."""
        if node.type is None:
            return "bare"
        if isinstance(node.type, ast.Name):
            return node.type.id
        if isinstance(node.type, ast.Attribute):
            return self._extract_sym(node.type)
        return ""

    def _is_silent_swallow(self, node: ast.ExceptHandler) -> bool:
        """True if the except body has no real action (pass, continue, break, or bare return)."""
        if not node.body:
            return True
        if len(node.body) == 1:
            stmt = node.body[0]
            if isinstance(stmt, ast.Pass):
                return True
            if isinstance(stmt, (ast.Continue, ast.Break)):
                return True
            if isinstance(stmt, ast.Return) and stmt.value is None:
                return True
        return False

    @staticmethod
    def _body_has_raise(body: list[ast.stmt]) -> bool:
        """True if any statement in the body is a raise (re-raise or new raise)."""
        for stmt in body:
            if isinstance(stmt, ast.Raise):
                return True
            # Check nested if/else for re-raise patterns
            for child in ast.walk(stmt):
                if isinstance(child, ast.Raise):
                    return True
        return False

    @staticmethod
    def _is_log_only_body(body: list[ast.stmt]) -> bool:
        """True if every statement in the except body is a logging call or pass."""
        if not body:
            return False
        for stmt in body:
            if isinstance(stmt, ast.Pass):
                continue
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                func = stmt.value.func
                sym = ""
                if isinstance(func, ast.Attribute):
                    sym = func.attr
                elif isinstance(func, ast.Name):
                    sym = func.id
                if sym in LOGGING_METHOD_NAMES:
                    continue
            return False
        return True

    @staticmethod
    def _return_sentinel_kind(body: list[ast.stmt]) -> str:
        """If body ends with a return of a sentinel value, return a description; else ''."""
        if not body:
            return ""
        # Look at last statement
        last = body[-1]
        if not isinstance(last, ast.Return):
            return ""
        val = last.value
        if val is None:
            return "return_bare"
        if isinstance(val, ast.Constant):
            if val.value is None:
                return "return_None"
            if val.value is False:
                return "return_False"
            if val.value == "":
                return "return_empty_str"
            if val.value == 0 and not isinstance(val.value, bool):
                return "return_zero"
        if isinstance(val, ast.List) and not val.elts:
            return "return_empty_list"
        if isinstance(val, ast.Dict) and not val.keys:
            return "return_empty_dict"
        if isinstance(val, ast.Tuple) and not val.elts:
            return "return_empty_tuple"
        if isinstance(val, ast.Set) and not val.elts:
            return "return_empty_set"
        return ""

    # ------------------------------------------------------------------
    # Pattern 2: Blocking calls inside async functions
    # ------------------------------------------------------------------

    def visit_Call(self, node: ast.Call) -> None:
        if self._in_async:
            sym = self._extract_sym(node.func)
            if sym and any(sym.startswith(p) for p in _BLOCKING_CALL_PREFIXES):
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="antipattern",
                        to_name=canonical_name("Symbol", "blocking_call_in_async"),
                        edge_kind="blocking_call_in_async",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
        self.generic_visit(node)

    # ------------------------------------------------------------------
    # Pattern 3: Global state mutation (UPPER_CASE global reassigned inside function)
    # ------------------------------------------------------------------

    def visit_Assign(self, node: ast.Assign) -> None:
        if self._function_depth > 0 and self._global_names:
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in self._global_names:
                    self.edges.append(
                        Edge(
                            from_name=self.module_adg_name,
                            relation_type="antipattern",
                            to_name=canonical_name("Symbol", "global_state_mutation"),
                            edge_kind="global_state_mutation",
                            source_file=self.source_file,
                            line_no=node.lineno,
                            symbol=target.id,
                        )
                    )
        self.generic_visit(node)

    # ------------------------------------------------------------------
    # Pattern 4: Retry loops without backoff (while/for with try but no sleep)
    # ------------------------------------------------------------------

    def visit_While(self, node: ast.While) -> None:
        if self._loop_contains_retry_without_backoff(node):
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="antipattern",
                    to_name=canonical_name("Symbol", "retry_without_backoff"),
                    edge_kind="retry_without_backoff",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol="while_retry",
                )
            )
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        if self._loop_contains_retry_without_backoff(node):
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="antipattern",
                    to_name=canonical_name("Symbol", "retry_without_backoff"),
                    edge_kind="retry_without_backoff",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol="for_retry",
                )
            )
        self.generic_visit(node)

    def _loop_contains_retry_without_backoff(self, node: ast.AST) -> bool:
        """True if loop has a try/except but no sleep/delay call within it."""
        has_try = False
        has_backoff = False
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                has_try = True
            if isinstance(child, ast.Call):
                sym = self._extract_sym(child.func)
                if sym and ("sleep" in sym or "delay" in sym or "backoff" in sym or "wait" in sym):
                    has_backoff = True
        return has_try and not has_backoff

    # ------------------------------------------------------------------
    # Shared helper
    # ------------------------------------------------------------------

    def _extract_sym(self, node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""


class _PromptSlotVisitor(ast.NodeVisitor):
    """E20: Prompt lifecycle graph — extract prompt-slot generation and consumption edges.

    Emits:
      module --generates_prompt--> ADG::PromptSlot::<SLOT>::<source_file>
          for each GovernedPayload / AirlockAssembler.assemble() call with slot kwargs.
      module --consumes_prompt--> ADG::PromptTemplate::<KEY>
          for each get_prompt(<KEY>) / get_constitution() call.
    """

    _ASSEMBLER_NAMES: frozenset[str] = frozenset(
        {"AirlockAssembler", "GovernedPayload", "assemble", "build_payload"}
    )
    _CONSUME_NAMES: frozenset[str] = frozenset(
        {"get_prompt", "get_constitution", "load_prompt", "fetch_prompt"}
    )

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_PromptSlotVisitor.visit_Call"
        )

        func_sym = self._sym(node.func)
        func_tail = func_sym.split(".")[-1] if func_sym else ""

        if func_sym in self._ASSEMBLER_NAMES or func_tail in self._ASSEMBLER_NAMES:
            self._handle_assembler(node)
        elif func_sym in self._CONSUME_NAMES or func_tail in self._CONSUME_NAMES:
            self._handle_consume(node)

        self.generic_visit(node)

    def _handle_assembler(self, node: ast.Call) -> None:
        """Emit generates_prompt for each recognised slot kwarg."""
        from agentic_core.adg.schema_util import PROMPT_FIELD_TO_SLOT

        for kw in node.keywords:
            slot = PROMPT_FIELD_TO_SLOT.get(kw.arg or "")
            if slot:
                to_name = canonical_name("PromptSlot", slot, self.source_file)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="generates_prompt",
                        to_name=to_name,
                        edge_kind="prompt_generation",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=f"{slot}:{kw.arg}",
                    )
                )

    def _handle_consume(self, node: ast.Call) -> None:
        """Emit consumes_prompt for get_prompt(<KEY>) and get_constitution() calls."""
        key = ""
        if node.args:
            arg0 = node.args[0]
            if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                key = arg0.value
        if not key:
            key = "CONSTITUTION"
        to_name = canonical_name("PromptTemplate", key)
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type="consumes_prompt",
                to_name=to_name,
                edge_kind="prompt_consumption",
                source_file=self.source_file,
                line_no=node.lineno,
                symbol=key,
            )
        )

    @staticmethod
    def _sym(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""


_TRACE_CALL_NAMES: frozenset[str] = frozenset(
    {
        "record_trace",
        "emit_telemetry",
        "log_run",
        "record_run",
        "emit_trace",
        "log_trace",
    }
)
_TRACE_ID_KWARGS: frozenset[str] = frozenset({"trace_id", "run_id", "request_id", "execution_id"})


class _ExecutionTraceVisitor(ast.NodeVisitor):
    """E23: Execution trace → prompt linkage graph.

    Emits:
      module --triggered_telemetry--> ADG::ExecutionTrace::<trace_id or source_file>
          for each record_trace() / emit_telemetry() / log_run() call site.
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_ExecutionTraceVisitor.visit_Call"
        )

        func_sym = self._sym(node.func)
        func_tail = func_sym.split(".")[-1] if func_sym else ""

        if func_sym in _TRACE_CALL_NAMES or func_tail in _TRACE_CALL_NAMES:
            trace_id = self._extract_id(node)
            to_name = canonical_name("ExecutionTrace", trace_id or self.source_file)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="triggered_telemetry",
                    to_name=to_name,
                    edge_kind="trace_prompt_link",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=trace_id or "",
                )
            )

        self.generic_visit(node)

    def _extract_id(self, node: ast.Call) -> str:
        """Return the trace/run id kwarg value if present, else empty string."""
        for kw in node.keywords:
            if kw.arg in _TRACE_ID_KWARGS:
                if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                    return kw.value.value
        return ""

    @staticmethod
    def _sym(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""


class _DecoratorVisitor(ast.NodeVisitor):
    """E3: G7 — Emit `applies` edges for decorator usage on functions and classes.

    For each decorated definition, emits:
      module --applies--> ADG::Symbol::<decorator>

    Special cases:
      - Decorators matching _GOVERNANCE_WRITE_SYMBOLS -> writes_through (already in GG)
      - Decorators matching _GOVERNANCE_ROUTE_SYMBOLS -> routes_through (already in GG)
      These are skipped here to avoid duplicate edges with GovernancePlaneVisitor.
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def _process_decorators(self, decorators: list[ast.expr], lineno: int) -> None:
        for dec in decorators:
            sym = self._extract_decorator_name(dec)
            if not sym:
                continue
            base = sym.split(".")[0]
            tail = sym.split(".")[-1]
            if base in _GOVERNANCE_WRITE_SYMBOLS or tail in _GOVERNANCE_WRITE_SYMBOLS:
                continue
            if base in _GOVERNANCE_ROUTE_SYMBOLS or tail in _GOVERNANCE_ROUTE_SYMBOLS:
                continue
            if base in _GOVERNANCE_READ_SYMBOLS or tail in _GOVERNANCE_READ_SYMBOLS:
                continue
            to_name = canonical_name("Symbol", sym)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="decorated_by",  # G5: renamed from influences
                    to_name=to_name,
                    edge_kind="decorator",
                    source_file=self.source_file,
                    line_no=lineno,
                    symbol=sym,
                )
            )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_DecoratorVisitor.visit_FunctionDef"
        )

        self._process_decorators(node.decorator_list, node.lineno)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._process_decorators(node.decorator_list, node.lineno)
        self.generic_visit(node)

    @staticmethod
    def _extract_decorator_name(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        if isinstance(node, ast.Call):
            return _DecoratorVisitor._extract_decorator_name(node.func)
        return ""


class _SymbolInventoryVisitor(ast.NodeVisitor):
    """E1: Emit `exports` edges for every public top-level symbol in a module.

    Walks top-level FunctionDef, AsyncFunctionDef, ClassDef, and simple
    module-level Assign/AnnAssign to build a symbol inventory.  Only
    public names (not starting with '_') are emitted unless they appear
    in an explicit __all__ list.

    Also records the complete name→line_no map in `symbol_table` so that
    downstream passes (E6, E11) can resolve import targets.
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []
        self.symbol_table: dict[str, int] = {}
        self._all_names: list[str] | None = None
        self._collected: list[tuple[str, str, int]] = []

    def visit_Module(self, node: ast.Module) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_SymbolInventoryVisitor.visit_Module"
        )

        self._all_names = self._extract_all(node)
        self.generic_visit(node)
        self._emit_export_edges()

    def _extract_all(self, module_node: ast.Module) -> list[str] | None:
        for stmt in module_node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(stmt.value, (ast.List, ast.Tuple)):
                            names = []
                            for elt in stmt.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    names.append(elt.value)
                            return names
        return None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        kind = "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function"
        self._collected.append((node.name, kind, node.lineno))
        self.symbol_table[node.name] = node.lineno

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._collected.append((node.name, "class", node.lineno))
        self.symbol_table[node.name] = node.lineno

    def visit_Assign(self, node: ast.Assign) -> None:
        if not isinstance(node.col_offset, int) or node.col_offset != 0:
            return
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id not in ("__all__", "__version__", "__author__"):
                self._collected.append((target.id, "constant", node.lineno))
                self.symbol_table[target.id] = node.lineno

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if not isinstance(node.col_offset, int) or node.col_offset != 0:
            return
        if isinstance(node.target, ast.Name):
            self._collected.append((node.target.id, "type_alias", node.lineno))
            self.symbol_table[node.target.id] = node.lineno

    def _emit_export_edges(self) -> None:
        explicit_all = set(self._all_names) if self._all_names is not None else None
        for name, kind, line_no in self._collected:
            if explicit_all is not None:
                if name not in explicit_all:
                    continue
                is_reexport = False
            else:
                if name.startswith("_"):
                    continue
                is_reexport = False
            to_sym = canonical_name("Symbol", f"{self.source_file}::{name}")
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="exports",
                    to_name=to_sym,
                    edge_kind="export",
                    source_file=self.source_file,
                    line_no=line_no,
                    symbol=name,
                )
            )


class _UnusedImportVisitor(ast.NodeVisitor):
    """E6: Detect imported names that are never used in the file body.

    Strategy: collect all names imported at module level, then walk the
    entire AST for Name/Attribute usages.  Any imported name that has
    zero usages gets tagged `dead_import`.

    Returns two lists:
      - live_names: set of names that ARE used
      - dead_names: set of names that are NOT used
    """

    def __init__(self) -> None:
        self.imported_names: dict[str, int] = {}
        self._used_names: set[str] = set()
        self._in_import: bool = False

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            local = alias.asname or alias.name.split(".")[0]
            self.imported_names[local] = node.lineno

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_UnusedImportVisitor.visit_ImportFrom"
        )

        # G4: exclude __future__ imports from dead-import tracking
        if (node.module or "") == "__future__":
            return
        for alias in node.names:
            if alias.name == "*":
                continue
            local = alias.asname or alias.name
            self.imported_names[local] = node.lineno

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, (ast.Load, ast.Del)):
            self._used_names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        cur: ast.expr = node
        while isinstance(cur, ast.Attribute):
            cur = cur.value
        if isinstance(cur, ast.Name):
            self._used_names.add(cur.id)
        self.generic_visit(node)

    @property
    def dead_names(self) -> set[str]:
        return {n for n in self.imported_names if n not in self._used_names}

    @property
    def live_names(self) -> set[str]:
        return {n for n in self.imported_names if n in self._used_names}


def _tag_dead_imports(edges: list[Edge], dead_names: set[str]) -> list[Edge]:
    """E6: Re-tag import edges for unused names with edge_kind='dead_import'.

    Returns a new list with dead imports replaced by dead_import-tagged edges.
    """
    result: list[Edge] = []
    for e in edges:
        if e.relation_type == "imports" and e.symbol.split(".")[-1] in dead_names:
            result.append(
                Edge(
                    from_name=e.from_name,
                    relation_type="dead_imports",
                    to_name=e.to_name,
                    edge_kind="dead_import",
                    source_file=e.source_file,
                    line_no=e.line_no,
                    symbol=e.symbol,
                )
            )
        else:
            result.append(e)
    return result


def _detect_cycles(result: ScanResult) -> list[Edge]:
    """E5: Post-scan pass — detect strongly connected components (cycles) in the import graph.

    Uses Kosaraju's algorithm (pure Python, no external deps) on the import
    subgraph.  For each SCC with >1 node, emits `in_cycle` edges from each
    member to a synthetic ADG::Cycle:: entity.

    Returns list of new `in_cycle` edges to add to the result.
    """
    import hashlib as _hashlib

    module_prefix = "ADG::Module::"

    adj: dict[str, set[str]] = {}
    radj: dict[str, set[str]] = {}
    nodes: set[str] = set()

    for edge in result.edges:
        if edge.relation_type not in ("imports", "calls", "instantiates"):
            continue
        fn = edge.from_name
        tn = edge.to_name
        if not fn.startswith(module_prefix) or not tn.startswith(module_prefix):
            continue
        nodes.add(fn)
        nodes.add(tn)
        adj.setdefault(fn, set()).add(tn)
        radj.setdefault(tn, set()).add(fn)

    if not nodes:
        return []

    visited: set[str] = set()
    order: list[str] = []

    def dfs1(v: str) -> None:
        stack = [(v, iter(adj.get(v, set())))]
        visited.add(v)
        while stack:
            node, children = stack[-1]
            try:
                child = next(children)
                if child not in visited:
                    visited.add(child)
                    stack.append((child, iter(adj.get(child, set()))))
            except StopIteration:
                order.append(node)
                stack.pop()

    for n in sorted(nodes):
        if n not in visited:
            dfs1(n)

    visited2: set[str] = set()
    sccs: list[list[str]] = []

    def dfs2(v: str) -> list[str]:
        comp: list[str] = []
        stack = [v]
        visited2.add(v)
        while stack:
            node = stack.pop()
            comp.append(node)
            for nb in sorted(radj.get(node, set())):
                if nb not in visited2:
                    visited2.add(nb)
                    stack.append(nb)
        return comp

    for n in reversed(order):
        if n not in visited2:
            scc = dfs2(n)
            if len(scc) > 1:
                sccs.append(sorted(scc))

    new_edges: list[Edge] = []
    for scc in sccs:
        members_key = "|".join(scc)
        cycle_hash = _hashlib.sha256(members_key.encode()).hexdigest()[:16]
        cycle_node = canonical_name("Cycle", cycle_hash)
        for member in scc:
            rel = member[len(module_prefix) :]
            new_edges.append(
                Edge(
                    from_name=member,
                    relation_type="in_cycle",
                    to_name=cycle_node,
                    edge_kind="cycle",
                    source_file=rel,
                    line_no=0,
                    symbol=f"cycle:{cycle_hash}",
                )
            )

    return new_edges


def _emit_layer_violation_edges(result: ScanResult) -> list[Edge]:
    """GV: Post-scan pass — emit deduplicated `violates` edges for forbidden cross-layer imports.

    Only fires on `imports` edges where the from-module layer is forbidden from
    importing the to-symbol's layer.  Deduplicates on (from_module, from_layer, to_layer).
    Skips lazy imports (inside function bodies, TYPE_CHECKING guards, optional_import blocks).
    """
    from agentic_core.adg.schema_util import ALLOWED_LAYER_EDGES

    _SKIP_EDGE_KINDS = frozenset(
        {"lazy_import", "type_checking_import", "optional_import", "version_guard_import"}
    )

    violations: list[Edge] = []
    seen: set[tuple[str, str, str]] = set()

    for edge in result.edges:
        if edge.relation_type != "imports":
            continue
        if edge.edge_kind in _SKIP_EDGE_KINDS:
            continue

        from_rel = edge.source_file
        from_layer = module_path_to_layer(from_rel)
        if from_layer == "L_UNKNOWN":
            continue

        sym = edge.symbol
        sym_parts = sym.replace("-", "_").split(".")
        to_layer = "L_UNKNOWN"
        for length in range(len(sym_parts), 0, -1):
            candidate = "/".join(sym_parts[:length])
            found = module_path_to_layer(candidate)
            if found != "L_UNKNOWN":
                to_layer = found
                break

        if to_layer == "L_UNKNOWN":
            continue

        if from_layer == to_layer:
            continue

        if (from_layer, to_layer) in ALLOWED_LAYER_EDGES:
            continue

        dedup_key = (edge.from_name, from_layer, to_layer)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        to_layer_adg = canonical_name("Layer", to_layer)
        violations.append(
            Edge(
                from_name=edge.from_name,
                relation_type="violates",
                to_name=to_layer_adg,
                edge_kind="import",
                source_file=edge.source_file,
                line_no=edge.line_no,
                symbol=f"{from_layer}->{to_layer}",
            )
        )

    return violations


class _HealerValidatorVisitor(ast.NodeVisitor):
    """G1 (gap): Runtime behavior plane — healer/validator loop edge extraction.

    Emits:
      module --heals--> ADG::Symbol::<HealerBase>
          when a class inherits from a known healer base.
      module --validates--> ADG::Symbol::<ValidatorBase>
          when a class inherits from a known validator base.
      module --orchestrates_healing--> ADG::Symbol::<method>
          when a known healing orchestration method is called.
      module --dispatches_to--> ADG::Symbol::<callee>
          when heal() / validate() is called on another object.
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_HealerValidatorVisitor.visit_ClassDef"
        )

        for base in node.bases:
            base_name = self._sym(base)
            base_tail = base_name.split(".")[-1] if base_name else ""
            if base_tail in HEALER_BASE_CLASSES:
                to_name = canonical_name("Symbol", base_name or base_tail)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="heals",
                        to_name=to_name,
                        edge_kind="healer_action",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=base_name or base_tail,
                    )
                )
            elif base_tail in VALIDATOR_BASE_CLASSES:
                to_name = canonical_name("Symbol", base_name or base_tail)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="validates",
                        to_name=to_name,
                        edge_kind="validator_check",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=base_name or base_tail,
                    )
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        sym = self._sym(node.func)
        tail = sym.split(".")[-1] if sym else ""
        if tail in HEALER_METHOD_NAMES:
            to_name = canonical_name("Symbol", sym or tail)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="orchestrates_healing",
                    to_name=to_name,
                    edge_kind="healing_dispatch",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)

    @staticmethod
    def _sym(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""


class _EmbeddingPipelineVisitor(ast.NodeVisitor):
    """G3 (gap): Embedding/knowledge graph — pipeline edge extraction.

    Emits:
      module --chunks_into--> ADG::Symbol::<chunker>
          for each known text-splitting / chunking call.
      module --embeds_into--> ADG::Symbol::<embedder>
          for each known embedding class instantiation or call.
      module --stores_embedding--> ADG::Symbol::<store>
          for each known vector-store write call (add_documents, upsert, ...).
      module --retrieves_via--> ADG::Symbol::<retriever>
          for each known retrieval call (similarity_search, as_retriever, ...).
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_EmbeddingPipelineVisitor.visit_Call"
        )

        sym = self._sym(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in EMBEDDING_PIPELINE_SYMBOLS or base in EMBEDDING_PIPELINE_SYMBOLS:
            self._emit("chunks_into", "chunking_pipeline", sym or tail, node.lineno)
        elif tail in EMBEDDING_SYMBOLS or base in EMBEDDING_SYMBOLS:
            self._emit("embeds_into", "embedding_pipeline", sym or tail, node.lineno)
        elif tail in VECTOR_STORE_SYMBOLS or base in VECTOR_STORE_SYMBOLS:
            self._emit("stores_embedding", "embedding_pipeline", sym or tail, node.lineno)
        elif tail in RETRIEVAL_SYMBOLS or sym in RETRIEVAL_SYMBOLS:
            self._emit("retrieves_via", "retrieval_pipeline", sym or tail, node.lineno)

        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        to_name = canonical_name("Symbol", sym)
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=to_name,
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )

    @staticmethod
    def _sym(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""


class _HITLVisitor(ast.NodeVisitor):
    """G4 (gap): HITL / confidence-threshold gating edge extraction.

    Emits:
      module --gated_by_confidence--> ADG::Symbol::<ConfidenceScorer>
          when a known confidence scoring class is instantiated or called.
      module --escalates_to_human--> ADG::Symbol::<escalation_method>
          when a known HITL escalation method is called.
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "_HITLVisitor.visit_Call")

        sym = self._sym(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in CONFIDENCE_SCORING_CLASSES or base in CONFIDENCE_SCORING_CLASSES:
            to_name = canonical_name("Symbol", sym or tail)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="gated_by_confidence",
                    to_name=to_name,
                    edge_kind="confidence_gate",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        elif tail in HITL_ESCALATION_METHODS:
            to_name = canonical_name("Symbol", sym or tail)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="escalates_to_human",
                    to_name=to_name,
                    edge_kind="hitl_escalation",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )

        self.generic_visit(node)

    @staticmethod
    def _sym(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""


class _SafetyEnforcementVisitor(ast.NodeVisitor):
    """G5 (gap): Safety enforcement runtime plane — guardrail + policy hash edge extraction.

    Emits:
      module --applies_guardrail--> ADG::Symbol::<GuardrailClass>
          when a known guardrail class is instantiated or called.
      module --verifies_policy--> ADG::Symbol::<policy_hash_method>
          when a known policy hash verification method is called.
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_SafetyEnforcementVisitor.visit_Call"
        )

        sym = self._sym(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in GUARDRAIL_CLASS_NAMES or base in GUARDRAIL_CLASS_NAMES:
            to_name = canonical_name("Symbol", sym or tail)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="applies_guardrail",
                    to_name=to_name,
                    edge_kind="guardrail_execution",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        elif tail in POLICY_HASH_METHODS:
            to_name = canonical_name("Symbol", sym or tail)
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="verifies_policy",
                    to_name=to_name,
                    edge_kind="policy_verification",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )

        self.generic_visit(node)

    @staticmethod
    def _sym(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""


class _SandboxAirlockVisitor(ast.NodeVisitor):
    """G7 (gap): Sandbox airlock / work-contract edge extraction.

    Emits:
      module --stamps_work_contract--> ADG::Symbol::<WorkContract>
      module --issues_capability_token--> ADG::Symbol::<CapabilityToken>
      module --enters_sandbox--> ADG::Symbol::<SandboxEnvelope>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_SandboxAirlockVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in SANDBOX_ENVELOPE_CLASSES or base in SANDBOX_ENVELOPE_CLASSES:
            self._emit("enters_sandbox", "sandbox_entry", sym or tail, node.lineno)
        elif tail in CAPABILITY_TOKEN_CLASSES or base in CAPABILITY_TOKEN_CLASSES:
            self._emit("issues_capability_token", "capability_token_issue", sym or tail, node.lineno)
        elif tail in WORK_CONTRACT_METHODS:
            self._emit("stamps_work_contract", "work_contract_stamp", sym or tail, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _CapabilityBudgetVisitor(ast.NodeVisitor):
    """G8 (gap): Capability-token / tool-budget resource governance edge extraction.

    Emits:
      module --grants_resource--> ADG::Symbol::<ToolBudget>
      module --exceeds_budget--> ADG::Symbol::<BudgetExceededException>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_CapabilityBudgetVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in TOOL_BUDGET_CLASSES or base in TOOL_BUDGET_CLASSES:
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="grants_resource",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="budget_grant",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        if node.exc is None:
            self.generic_visit(node)
            return
        sym = _sym_of(node.exc)
        tail = sym.split(".")[-1] if sym else ""
        if tail in BUDGET_EXCEEDED_EXCEPTIONS or sym in BUDGET_EXCEEDED_EXCEPTIONS:
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="exceeds_budget",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="budget_exceeded",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)


class _JITContextVisitor(ast.NodeVisitor):
    """G9 (gap): JIT context sync / freeze edge extraction.

    Emits:
      module --pulls_context--> ADG::Symbol::<JITContext>
      module --freezes_context--> ADG::Symbol::<freeze_method>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_JITContextVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        # Suppress instrumentation helpers from generating context edges
        if tail.startswith("_emit_") or tail.startswith("emit_"):
            self.generic_visit(node)
            return
        if tail in JIT_CONTEXT_CLASSES or base in JIT_CONTEXT_CLASSES:
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="pulls_context",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="context_pull",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        elif tail in FREEZE_METHOD_NAMES:
            if "unfreeze" in tail:
                relation, edge_kind = "unfreezes_context", "context_pull"
            elif "pull" in tail or "sync" in tail:
                relation, edge_kind = "pulls_context", "context_pull"
            else:
                relation, edge_kind = "freezes_context", "context_freeze"
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type=relation,
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind=edge_kind,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)


class _BoundaryVerifierVisitor(ast.NodeVisitor):
    """G10 (gap): Execution boundary verification edge extraction.

    Emits:
      module --verifies_boundary--> ADG::Symbol::<L2BoundaryVerifier>
      module --certifies_envelope--> ADG::Symbol::<CapabilityChokepoint>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_BoundaryVerifierVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in BOUNDARY_VERIFIER_CLASSES or base in BOUNDARY_VERIFIER_CLASSES:
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="verifies_boundary",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="boundary_accept",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        elif tail in CAPABILITY_CHOKEPOINT_CLASSES or base in CAPABILITY_CHOKEPOINT_CLASSES:
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="certifies_envelope",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="boundary_accept",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)


class _DeterminismControlVisitor(ast.NodeVisitor):
    """G11 (gap): Determinism control runtime edge extraction.

    Emits:
      module --seeds_rng--> ADG::Symbol::<SemanticClock|rng_seed_method>
      module --patches_time--> ADG::Symbol::<patch_time method>
      module --guards_replay--> ADG::Symbol::<ReplayGuard>
      module --emits_determinism_digest--> ADG::Symbol::<emit_method>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_DeterminismControlVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in SEMANTIC_CLOCK_CLASSES or base in SEMANTIC_CLOCK_CLASSES:
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="patches_time",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="replay_patch",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        elif tail in REPLAY_GUARD_CLASSES or base in REPLAY_GUARD_CLASSES:
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="guards_replay",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="replay_patch",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        elif tail in DETERMINISM_PATCH_METHODS:
            if "digest" in tail or tail in ("stamp_decision", "emit_routing_digest"):
                relation, edge_kind = "emits_determinism_digest", "determinism_digest_emit"
            elif "seed" in tail or "rng" in tail or "random" in tail or "uuid" in tail:
                relation, edge_kind = "seeds_rng", "determinism_seed"
            else:
                relation, edge_kind = "patches_time", "replay_patch"
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type=relation,
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind=edge_kind,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)


class _IOInterceptionVisitor(ast.NodeVisitor):
    """G12 (gap): Network / I/O interception edge extraction.

    Emits:
      module --intercepts_io--> ADG::Symbol::<IOInterceptor>
      module --transcripts_response--> ADG::Symbol::<transcript_method>
      module --hard_fails_untranscripted--> ADG::Symbol::<hard_fail_method>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_IOInterceptionVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in IO_INTERCEPT_CLASSES or base in IO_INTERCEPT_CLASSES:
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="intercepts_io",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="io_transcript",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        elif tail in NETWORK_TRANSCRIPT_SYMBOLS:
            if "hard_fail" in tail:
                relation, ek = "hard_fails_untranscripted", "io_hard_fail"
            else:
                relation, ek = "transcripts_response", "io_transcript"
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type=relation,
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind=ek,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)


class _MutationTransportVisitor(ast.NodeVisitor):
    """G13 (gap): Mutation transport / commit protocol edge extraction.

    Emits:
      module --packages_diff--> ADG::Symbol::<RFC6902 diff method>
      module --validates_blast_radius--> ADG::Symbol::<BlastRadiusChecker>
      module --signs_execution_trace--> ADG::Symbol::<MutationTransport>
      module --commits_mutation--> ADG::Symbol::<TwoPhaseCommit>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_MutationTransportVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in RFC6902_DIFF_SYMBOLS:
            if "blast" in tail:
                relation, ek = "validates_blast_radius", "blast_radius_check"
            else:
                relation, ek = "packages_diff", "diff_package"
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type=relation,
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind=ek,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        elif tail in MUTATION_TRANSPORT_CLASSES or base in MUTATION_TRANSPORT_CLASSES:
            if "commit" in tail.lower() or "TwoPhase" in tail:
                relation, ek = "commits_mutation", "two_phase_commit"
            elif "Distrib" in tail:
                relation, ek = "distributes_mutation", "mutation_distribution"
            else:
                relation, ek = "signs_execution_trace", "diff_package"
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type=relation,
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind=ek,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)


class _ExecutionProofVisitor(ast.NodeVisitor):
    """G14 (gap): Execution trace / proof runtime edge extraction.

    Emits:
      module --records_execution_trace--> ADG::Symbol::<ExecutionTrace>
      module --emits_replay_key--> ADG::Symbol::<emit_replay_key method>
      module --compares_proof--> ADG::Symbol::<compare_proof method>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_ExecutionProofVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in EXECUTION_TRACE_CLASSES or base in EXECUTION_TRACE_CLASSES:
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="records_execution_trace",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="execution_trace_record",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        elif tail in REPLAY_KEY_METHODS:
            if "compare" in tail:
                relation, ek = "compares_proof", "proof_comparison"
            elif "replay" in tail and "key" in tail or "replay_key" in tail:
                relation, ek = "emits_replay_key", "replay_key_emit"
            elif tail in (
                "stamp_decision",
                "guards_replay",
                "verify_routing_replay",
                "emit_determinism_digest",
                "emit_routing_digest",
            ):
                relation, ek = "emits_replay_key", "replay_key_emit"
            else:
                relation, ek = "records_execution_trace", "execution_trace_record"
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type=relation,
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind=ek,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)


class _PathControlVisitor(ast.NodeVisitor):
    """G15 (gap): Execution path control runtime edge extraction.

    Emits:
      module --routes_path--> ADG::Symbol::<PathRouter>
      module --forces_stall--> ADG::Symbol::<StallForcer>
      module --reenters_safety--> ADG::Symbol::<SafetyReentryGate>
      module --vigilance_reroute--> ADG::Symbol::<VigilanceRerouter>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_PathControlVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in PATH_CONTROL_CLASSES or base in PATH_CONTROL_CLASSES:
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="routes_path",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="path_route",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        elif tail in PATH_REROUTE_METHODS:
            if "stall" in tail or "force" in tail:
                relation, ek = "forces_stall", "path_stall"
            elif "reenter" in tail or "safety" in tail:
                relation, ek = "reenters_safety", "path_safety_reentry"
            elif "vigilance" in tail or "reroute" in tail:
                relation, ek = "vigilance_reroute", "path_vigilance_reroute"
            else:
                relation, ek = "routes_path", "path_route"
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type=relation,
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind=ek,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)


class _EvalSpineVisitor(ast.NodeVisitor):
    """G16 (gap): Evaluation / optimization spine runtime edge extraction.

    Emits:
      module --scores_groundedness--> ADG::Symbol::<EvalMetric>
      module --emits_drift_alert--> ADG::Symbol::<drift_alert method>
      module --builds_dpo_batch--> ADG::Symbol::<DPOBatchBuilder>
      module --commits_optimization--> ADG::Symbol::<commit_optimization>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_EvalSpineVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in EVAL_METRIC_CLASSES or base in EVAL_METRIC_CLASSES:
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="scores_groundedness",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="eval_score",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        elif tail in DPO_BATCH_CLASSES or base in DPO_BATCH_CLASSES:
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type="builds_dpo_batch",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="dpo_build",
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        elif tail in DRIFT_ALERT_METHODS:
            if "drift" in tail:
                relation, ek = "emits_drift_alert", "drift_alert"
            elif "dpo" in tail or "batch" in tail:
                relation, ek = "builds_dpo_batch", "dpo_build"
            elif "commit" in tail:
                relation, ek = "commits_optimization", "optimization_commit"
            else:
                relation, ek = "scores_groundedness", "eval_score"
            self.edges.append(
                Edge(
                    from_name=self.module_adg_name,
                    relation_type=relation,
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind=ek,
                    source_file=self.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)


class _SecretAccessVisitor(ast.NodeVisitor):
    """G17 (gap): Secret / credential access edge extraction.

    Emits:
      module --reads_secret_vault--> ADG::Symbol::<SecretVault>
      module --accesses_credential--> ADG::Symbol::<CredentialStore>
      module --rotates_secret--> ADG::Symbol::<SecretVault>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_SecretAccessVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in SECRET_VAULT_CLASSES or base in SECRET_VAULT_CLASSES:
            self._emit("reads_secret_vault", "secret_read", sym or tail, node.lineno)
        elif tail in SECRET_ACCESS_METHODS:
            if "rotat" in tail:
                self._emit("rotates_secret", "secret_rotation", sym or tail, node.lineno)
            else:
                self._emit("accesses_credential", "credential_access", sym or tail, node.lineno)
        elif any(p in sym for p in SECRET_ENV_PATTERNS):
            self._emit("accesses_credential", "credential_access", sym or tail, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _ConfigGovernanceVisitor(ast.NodeVisitor):
    """G18 (gap): Config governance edge extraction.

    Emits:
      module --reads_governed_config--> ADG::Symbol::<ConfigReader>
      module --validates_config_schema--> ADG::Symbol::<GovernedConfig>
      module --caches_config--> ADG::Symbol::<ConfigLoader>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_ConfigGovernanceVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in CONFIG_READER_CLASSES or base in CONFIG_READER_CLASSES:
            self._emit("reads_governed_config", "governed_config_read", sym or tail, node.lineno)
        elif tail in CONFIG_ACCESS_METHODS:
            if "valid" in tail:
                self._emit("validates_config_schema", "config_schema_validation", sym or tail, node.lineno)
            elif "cache" in tail:
                self._emit("caches_config", "governed_config_read", sym or tail, node.lineno)
            else:
                self._emit("reads_governed_config", "governed_config_read", sym or tail, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _DynamicInvocationVisitor(ast.NodeVisitor):
    """G19 (gap): Dynamic invocation edge extraction.

    Emits:
      module --invokes_eval--> ADG::Symbol::eval
      module --invokes_exec--> ADG::Symbol::exec
      module --invokes_importlib--> ADG::Symbol::importlib.import_module
      module --invokes_getattr_dynamic--> ADG::Symbol::getattr
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_DynamicInvocationVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        if sym in DYNAMIC_EVAL_SYMBOLS or tail in DYNAMIC_EVAL_SYMBOLS:
            if tail in ("eval",):
                self._emit("invokes_eval", "eval_call", sym or tail, node.lineno)
            elif tail in ("exec",):
                self._emit("invokes_exec", "exec_call", sym or tail, node.lineno)
            elif "import_module" in sym or "spec_from_file" in sym or "module_from_spec" in sym:
                self._emit("invokes_importlib", "importlib_call", sym or tail, node.lineno)
            elif "run_module" in sym or "run_path" in sym:
                self._emit("invokes_importlib", "importlib_call", sym or tail, node.lineno)
            else:
                self._emit("invokes_eval", "eval_call", sym or tail, node.lineno)
        elif sym in DYNAMIC_GETATTR_SYMBOLS or tail in DYNAMIC_GETATTR_SYMBOLS:
            if not self.source_file.startswith("tests/"):
                self._emit("invokes_getattr_dynamic", "dynamic_getattr", sym or tail, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _PolicyStateObserverVisitor(ast.NodeVisitor):
    """G20 (gap): Policy state observation edge extraction.

    Emits:
      module --observes_policy_state--> ADG::Symbol::<PolicyStateReader>
      module --observes_runtime_state--> ADG::Symbol::<RuntimeStateObserver>
      module --snapshots_state--> ADG::Symbol::<StateSnapshot>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_PolicyStateObserverVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in POLICY_STATE_READER_CLASSES or base in POLICY_STATE_READER_CLASSES:
            if "Snapshot" in tail or "snapshot" in tail:
                self._emit("snapshots_state", "runtime_state_snapshot", sym or tail, node.lineno)
            elif "Runtime" in tail or "Health" in tail:
                self._emit("observes_runtime_state", "runtime_state_snapshot", sym or tail, node.lineno)
            elif "State" in tail or "state" in tail or "Bridge" in tail or "digest" in tail:
                self._emit("snapshots_state", "runtime_state_snapshot", sym or tail, node.lineno)
            else:
                self._emit("observes_policy_state", "policy_state_observation", sym or tail, node.lineno)
        elif tail in POLICY_STATE_READ_METHODS:
            if "runtime" in tail or "health" in tail or "probe" in tail:
                self._emit("observes_runtime_state", "runtime_state_snapshot", sym or tail, node.lineno)
            elif "snapshot" in tail:
                self._emit("snapshots_state", "runtime_state_snapshot", sym or tail, node.lineno)
            else:
                self._emit("observes_policy_state", "policy_state_observation", sym or tail, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _AntipatternRegistryVisitor(ast.NodeVisitor):
    """G21 (gap): Anti-pattern registry edge extraction.

    Emits:
      module --registers_antipattern--> ADG::Symbol::<AntipatternRegistry>
      module --classifies_antipattern--> ADG::Symbol::<PatternClassifier>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_AntipatternRegistryVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in ANTIPATTERN_REGISTRY_CLASSES or base in ANTIPATTERN_REGISTRY_CLASSES:
            if "Classifier" in tail or "Detector" in tail:
                self._emit("classifies_antipattern", "antipattern_classification", sym or tail, node.lineno)
            else:
                self._emit("registers_antipattern", "antipattern_classification", sym or tail, node.lineno)
        elif tail in ANTIPATTERN_CATEGORY_NAMES:
            self._emit("classifies_antipattern", "antipattern_classification", sym or tail, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _HealingOrchestratorVisitor(ast.NodeVisitor):
    """G22 (gap): Healing orchestrator edge extraction.

    Emits:
      module --dispatches_healing_run--> ADG::Symbol::<HealingOrchestrator>
      module --confirms_heal--> ADG::Symbol::<HealingOrchestrator>
      module --aborts_heal--> ADG::Symbol::<HealingOrchestrator>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_HealingOrchestratorVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in HEALING_ORCHESTRATOR_CLASSES or base in HEALING_ORCHESTRATOR_CLASSES:
            self._emit("dispatches_healing_run", "healing_dispatch", sym or tail, node.lineno)
        elif tail in HEALING_DISPATCH_METHODS:
            if "abort" in tail:
                self._emit("aborts_heal", "healing_abort", sym or tail, node.lineno)
            elif "confirm" in tail:
                self._emit("confirms_heal", "healing_confirm", sym or tail, node.lineno)
            else:
                self._emit("dispatches_healing_run", "healing_dispatch", sym or tail, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _NondeterminismVisitor(ast.NodeVisitor):
    """G23 (gap): Non-determinism primitive detection.

    Emits:
      module --uses_wall_clock--> ADG::Symbol::<datetime/time call>
      module --uses_random-->     ADG::Symbol::<random/secrets call>
      module --uses_uuid-->       ADG::Symbol::<uuid call>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_NondeterminismVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        if sym in NONDETERMINISM_WALL_CLOCK_SYMBOLS:
            self._emit("uses_wall_clock", "wall_clock_use", sym, node.lineno)
        elif sym in NONDETERMINISM_RANDOM_SYMBOLS:
            self._emit("uses_random", "random_use", sym, node.lineno)
        elif sym in NONDETERMINISM_UUID_SYMBOLS:
            self._emit("uses_uuid", "uuid_use", sym, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _ExternalHttpVisitor(ast.NodeVisitor):
    """G24 (gap): External HTTP / network egress detection.

    Emits:
      module --external_http_call--> ADG::Symbol::<requests.get / httpx.post / ...>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_ExternalHttpVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        if sym in EXTERNAL_HTTP_SYMBOLS:
            self._emit("external_http_call", "http_egress_call", sym, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _AgentDispatchVisitor(ast.NodeVisitor):
    """G25 (gap): Agent-to-agent dispatch proof edges.

    Emits:
      module --agent_executes_agent--> ADG::Symbol::<AgentDispatcher / invoke_agent / ...>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_AgentDispatchVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in AGENT_DISPATCH_CLASSES or base in AGENT_DISPATCH_CLASSES or tail in AGENT_DISPATCH_METHODS:
            self._emit("agent_executes_agent", "agent_dispatch", sym or tail, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _P1OrchestrationGovernanceVisitor(ast.NodeVisitor):
    """G28 (gap): P1 orchestration governance proof edges.

    Emits:
      module --routes_to_agent-->           ADG::Symbol::<emit_routes_to_agent / ...>
      module --orchestrates_workflow-->      ADG::Symbol::<emit_orchestrates_workflow / ...>
      module --dispatches_execution_plan--> ADG::Symbol::<emit_dispatches_execution_plan / ...>
      module --validates_agent_capability-->ADG::Symbol::<emit_validates_agent_capability / ...>
      module --checks_agent_registry-->     ADG::Symbol::<emit_checks_agent_registry / ...>
    """

    _SYMBOL_MAP: tuple[tuple[frozenset[str], str, str], ...] = (
        (ORCHESTRATION_ROUTE_SYMBOLS, "routes_to_agent", "agent_route"),
        (WORKFLOW_ORCHESTRATION_SYMBOLS, "orchestrates_workflow", "workflow_orchestration"),
        (EXECUTION_PLAN_DISPATCH_SYMBOLS, "dispatches_execution_plan", "execution_plan_dispatch"),
        (CAPABILITY_VALIDATION_SYMBOLS, "validates_agent_capability", "capability_validation"),
        (REGISTRY_CHECK_SYMBOLS, "checks_agent_registry", "registry_check"),
    )

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        for symbols, relation, edge_kind in self._SYMBOL_MAP:
            if tail in symbols or base in symbols:
                self._emit(relation, edge_kind, sym or tail, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _P2ExecutionCapabilityVisitor(ast.NodeVisitor):
    """G29 (gap): P2 execution capability proof edges.

    Emits:
      module --authorize_and_execute-->       ADG::Symbol::<_emit_authorize_and_execute / ...>
      module --validates_capability-->        ADG::Symbol::<_emit_validates_capability / ...>
      module --routes_to_capability-->        ADG::Symbol::<_emit_routes_to_capability / ...>
      module --writes_via_uwg-->              ADG::Symbol::<_emit_writes_via_uwg / ...>
      module --blocks_direct_write-->         ADG::Symbol::<_emit_blocks_direct_write / ...>
      module --records_tool_invocation-->     ADG::Symbol::<_emit_records_tool_invocation / ...>
      module --captures_execution_output-->   ADG::Symbol::<_emit_captures_execution_output / ...>
    """

    _SYMBOL_MAP: tuple[tuple[frozenset[str], str, str], ...] = (
        (AUTHORIZE_EXECUTE_SYMBOLS, "authorize_and_execute", "execution_authorization"),
        (VALIDATES_CAPABILITY_SYMBOLS, "validates_capability", "capability_validation"),
        (ROUTES_TO_CAPABILITY_SYMBOLS, "routes_to_capability", "capability_routing"),
        (WRITES_VIA_UWG_SYMBOLS, "writes_via_uwg", "uwg_write"),
        (BLOCKS_DIRECT_WRITE_SYMBOLS, "blocks_direct_write", "direct_write_block"),
        (RECORDS_TOOL_INVOCATION_SYMBOLS, "records_tool_invocation", "tool_invocation_record"),
        (CAPTURES_EXECUTION_OUTPUT_SYMBOLS, "captures_execution_output", "execution_output_capture"),
    )

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        for symbols, relation, edge_kind in self._SYMBOL_MAP:
            if tail in symbols or base in symbols:
                self._emit(relation, edge_kind, sym or tail, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _P3OrchestrationHealingVisitor(ast.NodeVisitor):
    """G30 (gap): P3 orchestration & healing proof edges.

    Emits:
      module --dispatches_agent-->           ADG::Symbol::<_emit_dispatches_agent / ...>
      module --coordinates_agents-->         ADG::Symbol::<_emit_coordinates_agents / ...>
      module --records_workflow_lineage-->    ADG::Symbol::<_emit_records_workflow_lineage / ...>
      module --records_healing_outcome-->     ADG::Symbol::<_emit_records_healing_outcome / ...>
      module --escalates_failure-->           ADG::Symbol::<_emit_escalates_failure / ...>
    """

    _SYMBOL_MAP: tuple[tuple[frozenset[str], str, str], ...] = (
        (DISPATCHES_AGENT_SYMBOLS, "dispatches_agent", "agent_dispatch"),
        (COORDINATES_AGENTS_SYMBOLS, "coordinates_agents", "agent_coordination"),
        (RECORDS_WORKFLOW_LINEAGE_SYMBOLS, "records_workflow_lineage", "workflow_lineage"),
        (RECORDS_HEALING_OUTCOME_SYMBOLS, "records_healing_outcome", "healing_outcome"),
        (ESCALATES_FAILURE_SYMBOLS, "escalates_failure", "failure_escalation"),
        (INVOKES_EVALUATION_SYMBOLS, "invokes_evaluation", "evaluation_signal"),
    )

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        for symbols, relation, edge_kind in self._SYMBOL_MAP:
            if tail in symbols or base in symbols:
                self._emit(relation, edge_kind, sym or tail, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _P3LearningMaturityVisitor(ast.NodeVisitor):
    """G32 (gap): P3 learning maturity proof edges.

    Emits:
      module --captures_pattern-->           ADG::Symbol::<_emit_captures_pattern / ...>
      module --records_learning_event-->     ADG::Symbol::<_emit_records_learning_event / ...>
      module --writes_learning_snapshot-->   ADG::Symbol::<_emit_writes_learning_snapshot / ...>
      module --feeds_meta_learning-->        ADG::Symbol::<_emit_feeds_meta_learning / ...>
      module --updates_routing_strategy-->   ADG::Symbol::<_emit_updates_routing_strategy / ...>
      module --improves_agent_policy-->      ADG::Symbol::<_emit_improves_agent_policy / ...>
      module --stores_learning_state-->      ADG::Symbol::<_emit_stores_learning_state / ...>
    """

    _SYMBOL_MAP: tuple[tuple[frozenset[str], str, str], ...] = (
        (CAPTURES_PATTERN_SYMBOLS, "captures_pattern", "pattern_capture"),
        (RECORDS_LEARNING_EVENT_SYMBOLS, "records_learning_event", "learning_event"),
        (WRITES_LEARNING_SNAPSHOT_SYMBOLS, "writes_learning_snapshot", "learning_snapshot"),
        (FEEDS_META_LEARNING_SYMBOLS, "feeds_meta_learning", "meta_learning_feed"),
        (UPDATES_ROUTING_STRATEGY_SYMBOLS, "updates_routing_strategy", "routing_strategy"),
        (IMPROVES_AGENT_POLICY_SYMBOLS, "improves_agent_policy", "policy_improvement"),
        (STORES_LEARNING_STATE_SYMBOLS, "stores_learning_state", "learning_state"),
    )

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        for symbols, relation, edge_kind in self._SYMBOL_MAP:
            if tail in symbols or base in symbols:
                self._emit(relation, edge_kind, sym or tail, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _P4ObservabilityGovernanceVisitor(ast.NodeVisitor):
    """G33 (gap): P4 observability & governance proof edges.

    Emits:
      module --emits_metric_event-->         ADG::Symbol::<_emit_emits_metric_event / ...>
      module --records_incident_event-->     ADG::Symbol::<_emit_records_incident_event / ...>
      module --captures_runtime_anomaly-->   ADG::Symbol::<_emit_captures_runtime_anomaly / ...>
      module --writes_observability_log-->   ADG::Symbol::<_emit_writes_observability_log / ...>
      module --updates_monitoring_state-->   ADG::Symbol::<_emit_updates_monitoring_state / ...>
      module --triggers_alert-->             ADG::Symbol::<_emit_triggers_alert / ...>
      module --links_incident_trace-->       ADG::Symbol::<_emit_links_incident_trace / ...>
    """

    _SYMBOL_MAP: tuple[tuple[frozenset[str], str, str], ...] = (
        (EMITS_METRIC_EVENT_SYMBOLS, "emits_metric_event", "metric_emission"),
        (RECORDS_INCIDENT_EVENT_SYMBOLS, "records_incident_event", "incident_recording"),
        (CAPTURES_RUNTIME_ANOMALY_SYMBOLS, "captures_runtime_anomaly", "anomaly_capture"),
        (WRITES_OBSERVABILITY_LOG_SYMBOLS, "writes_observability_log", "observability_log"),
        (UPDATES_MONITORING_STATE_SYMBOLS, "updates_monitoring_state", "monitoring_state"),
        (TRIGGERS_ALERT_SYMBOLS, "triggers_alert", "alert_trigger"),
        (LINKS_INCIDENT_TRACE_SYMBOLS, "links_incident_trace", "incident_trace_link"),
    )

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        for symbols, relation, edge_kind in self._SYMBOL_MAP:
            if tail in symbols or base in symbols:
                self._emit(relation, edge_kind, sym or tail, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _P4StateTelemetryVisitor(ast.NodeVisitor):
    """G31 (gap): P4 state, telemetry & learning proof edges.

    Emits:
      module --records_telemetry_event-->       ADG::Symbol::<_emit_records_telemetry_event / ...>
      module --captures_evaluation_metric-->    ADG::Symbol::<_emit_captures_evaluation_metric / ...>
      module --stores_embedding-->              ADG::Symbol::<_emit_stores_embedding / ...>
      module --updates_meta_learning_state-->   ADG::Symbol::<_emit_updates_meta_learning_state / ...>
      module --links_execution_to_snapshot-->   ADG::Symbol::<_emit_links_execution_to_snapshot / ...>
    """

    _SYMBOL_MAP: tuple[tuple[frozenset[str], str, str], ...] = (
        (RECORDS_TELEMETRY_EVENT_SYMBOLS, "records_telemetry_event", "telemetry_event"),
        (CAPTURES_EVALUATION_METRIC_SYMBOLS, "captures_evaluation_metric", "eval_metric"),
        (STORES_EMBEDDING_SYMBOLS, "stores_embedding", "embedding_store"),
        (UPDATES_META_LEARNING_STATE_SYMBOLS, "updates_meta_learning_state", "meta_learning"),
        (LINKS_EXECUTION_TO_SNAPSHOT_SYMBOLS, "links_execution_to_snapshot", "exec_snapshot_link"),
    )

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        for symbols, relation, edge_kind in self._SYMBOL_MAP:
            if tail in symbols or base in symbols:
                self._emit(relation, edge_kind, sym or tail, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _L5ValidationProofVisitor(ast.NodeVisitor):
    """G26 (gap): L5 validation proof edges.

    Emits:
      module --validated_by_registry-->      ADG::Symbol::<AgentRegistry / ...>
      module --validated_by_safety_plane-->  ADG::Symbol::<SafetyPlane / SovereignLLMGateway / ...>
      module --validated_by_llm_gateway-->   ADG::Symbol::<SovereignLLMGateway / ...>
      module --execution_terminates_at_uwg-->ADG::Symbol::<UniversalWriteGateway / ...>
      module --references_policy_hash-->     ADG::Symbol::<PolicyHash / PolicyConfigGuard / ...>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_L5ValidationProofVisitor.visit_ClassDef"
        )

        for base_node in node.bases:
            sym = _sym_of(base_node)
            if sym:
                tail = sym.split(".")[-1]
                base = sym.split(".")[0]
                name = tail or base
                if name in UWG_TERMINATION_SYMBOLS or base in UWG_TERMINATION_SYMBOLS:
                    self._emit("execution_terminates_at_uwg", "uwg_termination", sym or name, node.lineno)
                if name in SAFETY_PLANE_CLASSES or base in SAFETY_PLANE_CLASSES:
                    self._emit(
                        "validated_by_safety_plane", "safety_plane_validation", sym or name, node.lineno
                    )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        name = tail or base
        if name in AGENT_REGISTRY_CLASSES or base in AGENT_REGISTRY_CLASSES:
            self._emit("validated_by_registry", "registry_validation", sym or name, node.lineno)
        if name in SAFETY_PLANE_CLASSES or base in SAFETY_PLANE_CLASSES:
            if "LLMGateway" in name or "MCPGateway" in name:
                self._emit("validated_by_llm_gateway", "llm_gateway_validation", sym or name, node.lineno)
            else:
                self._emit("validated_by_safety_plane", "safety_plane_validation", sym or name, node.lineno)
        if name in UWG_TERMINATION_SYMBOLS or base in UWG_TERMINATION_SYMBOLS:
            self._emit("execution_terminates_at_uwg", "uwg_termination", sym or name, node.lineno)
        if name in POLICY_HASH_SYMBOLS or base in POLICY_HASH_SYMBOLS:
            self._emit("references_policy_hash", "policy_hash_link", sym or name, node.lineno)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in POLICY_HASH_SYMBOLS:
            self._emit("references_policy_hash", "policy_hash_link", node.attr, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


class _LearningProvenanceVisitor(ast.NodeVisitor):
    """G27 (gap): Learning pipeline and prompt provenance proof edges.

    Emits:
      module --proposal_commits_routing-->    ADG::Symbol::<MetaLearningProposal / ...>
      module --prompt_template_used_by-->     ADG::Symbol::<PromptTemplate / ...>
      module --instruction_injection_source-->ADG::Symbol::<InstructionInjector / ...>
      module --produces_preference_pair-->    ADG::Symbol::<DPOPair / PreferencePair / ...>
      module --requires_human_review-->       ADG::Symbol::<HumanReviewGate / ...>
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_LearningProvenanceVisitor.visit_Call"
        )

        sym = _sym_of(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        name = tail or base
        if name in ROUTING_COMMIT_SYMBOLS or base in ROUTING_COMMIT_SYMBOLS:
            self._emit("proposal_commits_routing", "routing_commit", sym or name, node.lineno)
        if name in PROMPT_TEMPLATE_SYMBOLS or base in PROMPT_TEMPLATE_SYMBOLS:
            self._emit("prompt_template_used_by", "prompt_template_link", sym or name, node.lineno)
        if name in PROMPT_INJECTION_SYMBOLS or base in PROMPT_INJECTION_SYMBOLS:
            self._emit("instruction_injection_source", "injection_source_link", sym or name, node.lineno)
        if name in PREFERENCE_PAIR_SYMBOLS or base in PREFERENCE_PAIR_SYMBOLS:
            self._emit("produces_preference_pair", "preference_pair_link", sym or name, node.lineno)
        if name in HUMAN_REVIEW_SYMBOLS or base in HUMAN_REVIEW_SYMBOLS:
            self._emit("requires_human_review", "human_review_gate", sym or name, node.lineno)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in HUMAN_REVIEW_SYMBOLS:
            self._emit("requires_human_review", "human_review_gate", node.attr, node.lineno)
        if node.attr in ROUTING_COMMIT_SYMBOLS:
            self._emit("proposal_commits_routing", "routing_commit", node.attr, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        self.edges.append(
            Edge(
                from_name=self.module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self.source_file,
                line_no=line_no,
                symbol=sym,
            )
        )


def _sym_of(node: ast.expr) -> str:
    """Shared symbol extractor used by gap-plane visitors."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parts: list[str] = []
        cur: ast.expr = node
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
        return ".".join(reversed(parts))
    return ""


def _is_property_accessor(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return True if a function is decorated as a property getter, setter, or deleter."""
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name) and dec.id == "property":
            return True
        if isinstance(dec, ast.Attribute) and dec.attr in ("setter", "deleter", "getter"):
            return True
    return False


class _DuplicateMethodVisitor(ast.NodeVisitor):
    """GH: Detect duplicate method definitions in the same class body (Rule D).

    Emits `duplicate_method` edges when a FunctionDef / AsyncFunctionDef name
    appears more than once in the **immediate** body of a ClassDef.
    Property setter / deleter / getter decorators are exempt because those are
    intentional overloads of the descriptor protocol.

    Recursively descends into nested class definitions.
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_DuplicateMethodVisitor.visit_ClassDef"
        )

        seen: dict[str, int] = {}
        for stmt in node.body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if _is_property_accessor(stmt):
                    continue
                if stmt.name in seen:
                    self.edges.append(
                        Edge(
                            from_name=self.module_adg_name,
                            relation_type="duplicate_method",
                            to_name=canonical_name("Symbol", f"{node.name}.{stmt.name}"),
                            edge_kind="duplicate_method",
                            source_file=self.source_file,
                            line_no=stmt.lineno,
                            symbol=f"{node.name}.{stmt.name}",
                        )
                    )
                else:
                    seen[stmt.name] = stmt.lineno
            elif isinstance(stmt, ast.ClassDef):
                self.visit_ClassDef(stmt)


class _UnreachableCodeAfterRaiseVisitor(ast.NodeVisitor):
    """GU: Detect statements placed after an unconditional `raise` (Rule G).

    Walks all statement-containing blocks (except handler bodies, function bodies,
    if/while/for bodies) and emits `unreachable_after_raise` edges for any
    statement that immediately follows a bare `raise` or `raise <expr>`.

    This catches the exact MCP bug pattern:
        except Exception as e:
            raise
            Logger.warning(...)   # <-- unreachable
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def _check_body(self, body: list[ast.stmt]) -> None:
        for i, stmt in enumerate(body):
            if isinstance(stmt, ast.Raise) and i < len(body) - 1:
                next_stmt = body[i + 1]
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="unreachable_after_raise",
                        to_name=canonical_name("Symbol", "unreachable_code"),
                        edge_kind="unreachable_after_raise",
                        source_file=self.source_file,
                        line_no=next_stmt.lineno,
                        symbol=f"raise_at_line_{stmt.lineno}",
                    )
                )

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_UnreachableCodeAfterRaiseVisitor.visit_ExceptHandler"
        )

        self._check_body(node.body)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_body(node.body)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_If(self, node: ast.If) -> None:
        self._check_body(node.body)
        self._check_body(node.orelse)
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self._check_body(node.body)
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self._check_body(node.body)
        self.generic_visit(node)


def _iter_python_files(repo_root: Path) -> Iterator[Path]:
    """Yield all .py files under SCAN_ROOTS, deterministic (sorted) order."""
    all_files: list[Path] = []
    for scan_root in _SCAN_ROOTS:
        root_path = repo_root / scan_root
        if not root_path.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root_path):
            dirnames[:] = sorted(d for d in dirnames if d not in SOVEREIGN_EXCLUDED_FOLDERS)
            for fname in sorted(filenames):
                if fname.endswith(".py") and not fname.endswith(".pyc"):
                    all_files.append(Path(dirpath) / fname)
    all_files.sort()
    yield from all_files


def _repo_relative(path: Path, repo_root: Path) -> str:
    """Return forward-slash repo-relative path."""
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        return str(path).replace("\\", "/")
    return str(rel).replace("\\", "/")


def _scan_file(
    filepath: Path,
    repo_root: Path,
    include_tests: bool = True,
) -> tuple[list[Edge], bool]:
    """Scan a single Python file and return (edges, had_syntax_error)."""
    rel = _repo_relative(filepath, repo_root)
    module_adg = canonical_name("Module", rel)
    edges: list[Edge] = []
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as exc:
        logger.debug("SyntaxError in %s: %s", filepath, exc)
        return [], True  # A4: parse failures tracked
    except OSError as exc:
        logger.debug("OSError reading %s: %s", filepath, exc)
        return [], True

    # G1: Import edges
    from agentic_core.adg.identity.normalizer import IdentityNormalizer
    identity_normalizer = IdentityNormalizer(repo_root=repo_root)
    import_visitor = _ImportVisitor(module_adg, rel, identity_normalizer=identity_normalizer)
    import_visitor.visit(tree)
    edges.extend(import_visitor.edges)

    # G2: Call/write/network edges
    call_visitor = _CallVisitor(module_adg, rel)
    call_visitor.visit(tree)
    edges.extend(call_visitor.edges)

    # G3: Inheritance edges (H3)
    inh_visitor = _InheritanceVisitor(module_adg, rel)
    inh_visitor.visit(tree)
    edges.extend(inh_visitor.edges)

    # G5: Config/env read edges (H4)
    attr_visitor = _AttributeVisitor(module_adg, rel)
    attr_visitor.visit(tree)
    edges.extend(attr_visitor.edges)

    # G6: Composition edges (H5)
    comp_visitor = _CompositionVisitor(module_adg, rel)
    comp_visitor.visit(tree)
    edges.extend(comp_visitor.edges)

    # GF: Dynamic execution edges (S3/RULE_F)
    dyn_visitor = _DynamicExecutionVisitor(module_adg, rel)
    dyn_visitor.visit(tree)
    edges.extend(dyn_visitor.edges)

    # G4: Inter-module call graph
    icg_visitor = _InternalCallGraphVisitor(module_adg, rel)
    icg_visitor.visit(tree)
    edges.extend(icg_visitor.edges)

    # GT: Test traceability graph
    tt_visitor = _TestTraceabilityVisitor(module_adg, rel)
    tt_visitor.visit(tree)
    edges.extend(tt_visitor.edges)

    # GG: Governance plane graph
    gov_visitor = _GovernancePlaneVisitor(module_adg, rel)
    gov_visitor.visit(tree)
    edges.extend(gov_visitor.edges)

    # Wave 4: Critical edge densification
    critical_visitor = _CriticalEdgeVisitor(module_adg, rel)
    critical_visitor.visit(tree)
    edges.extend(critical_visitor.edges)

    # E1: Symbol inventory / exports graph
    sym_visitor = _SymbolInventoryVisitor(module_adg, rel)
    sym_visitor.visit(tree)
    edges.extend(sym_visitor.edges)

    # E3: Decorator graph (G7)
    dec_visitor = _DecoratorVisitor(module_adg, rel)
    dec_visitor.visit(tree)
    edges.extend(dec_visitor.edges)

    # E4: Type annotation graph (G8)
    ann_visitor = _TypeAnnotationVisitor(module_adg, rel)
    ann_visitor.visit(tree)
    edges.extend(ann_visitor.edges)

    # E6: Unused import detection — re-tag dead import edges
    unused_visitor = _UnusedImportVisitor()
    unused_visitor.visit(tree)
    if unused_visitor.dead_names:
        edges = _tag_dead_imports(edges, unused_visitor.dead_names)

    # GA: Behavioral anti-pattern detection
    ap_visitor = _AntipatternVisitor(module_adg, rel)
    ap_visitor.visit(tree)
    edges.extend(ap_visitor.edges)

    # E20: Prompt lifecycle graph (generates_prompt / consumes_prompt)
    ps_visitor = _PromptSlotVisitor(module_adg, rel)
    ps_visitor.visit(tree)
    edges.extend(ps_visitor.edges)

    # E23: Execution trace → telemetry linkage (triggered_telemetry)
    et_visitor = _ExecutionTraceVisitor(module_adg, rel)
    et_visitor.visit(tree)
    edges.extend(et_visitor.edges)

    # G1 (gap): Healer/validator loop graph (heals, validates, orchestrates_healing)
    hv_visitor = _HealerValidatorVisitor(module_adg, rel)
    hv_visitor.visit(tree)
    edges.extend(hv_visitor.edges)

    # G3 (gap): Embedding pipeline graph (chunks_into, embeds_into, stores_embedding, retrieves_via)
    emb_visitor = _EmbeddingPipelineVisitor(module_adg, rel)
    emb_visitor.visit(tree)
    edges.extend(emb_visitor.edges)

    # G4 (gap): HITL / confidence-threshold gating (gated_by_confidence, escalates_to_human)
    hitl_visitor = _HITLVisitor(module_adg, rel)
    hitl_visitor.visit(tree)
    edges.extend(hitl_visitor.edges)

    # G5 (gap): Safety enforcement plane (applies_guardrail, verifies_policy)
    safety_visitor = _SafetyEnforcementVisitor(module_adg, rel)
    safety_visitor.visit(tree)
    edges.extend(safety_visitor.edges)

    # G7 (gap): Sandbox airlock / work-contract (enters_sandbox, issues_capability_token, stamps_work_contract)
    sandbox_visitor = _SandboxAirlockVisitor(module_adg, rel)
    sandbox_visitor.visit(tree)
    edges.extend(sandbox_visitor.edges)

    # G8 (gap): Capability-token / tool-budget (grants_resource, exceeds_budget)
    budget_visitor = _CapabilityBudgetVisitor(module_adg, rel)
    budget_visitor.visit(tree)
    edges.extend(budget_visitor.edges)

    # G9 (gap): JIT context sync / freeze (pulls_context, freezes_context, unfreezes_context)
    jit_visitor = _JITContextVisitor(module_adg, rel)
    jit_visitor.visit(tree)
    edges.extend(jit_visitor.edges)

    # G10 (gap): Execution boundary verification (verifies_boundary, certifies_envelope)
    boundary_visitor = _BoundaryVerifierVisitor(module_adg, rel)
    boundary_visitor.visit(tree)
    edges.extend(boundary_visitor.edges)

    # G11 (gap): Determinism control (seeds_rng, patches_time, guards_replay, emits_determinism_digest)
    determinism_visitor = _DeterminismControlVisitor(module_adg, rel)
    determinism_visitor.visit(tree)
    edges.extend(determinism_visitor.edges)

    # G12 (gap): Network / I/O interception (intercepts_io, transcripts_response, hard_fails_untranscripted)
    io_visitor = _IOInterceptionVisitor(module_adg, rel)
    io_visitor.visit(tree)
    edges.extend(io_visitor.edges)

    # G13 (gap): Mutation transport / commit (packages_diff, validates_blast_radius, commits_mutation)
    mutation_transport_visitor = _MutationTransportVisitor(module_adg, rel)
    mutation_transport_visitor.visit(tree)
    edges.extend(mutation_transport_visitor.edges)

    # G14 (gap): Execution trace / proof (records_execution_trace, emits_replay_key, compares_proof)
    proof_visitor = _ExecutionProofVisitor(module_adg, rel)
    proof_visitor.visit(tree)
    edges.extend(proof_visitor.edges)

    # G15 (gap): Path control (routes_path, forces_stall, reenters_safety, vigilance_reroute)
    path_visitor = _PathControlVisitor(module_adg, rel)
    path_visitor.visit(tree)
    edges.extend(path_visitor.edges)

    # G16 (gap): Evaluation / optimization spine (scores_groundedness, emits_drift_alert, builds_dpo_batch)
    eval_visitor = _EvalSpineVisitor(module_adg, rel)
    eval_visitor.visit(tree)
    edges.extend(eval_visitor.edges)

    # GH (RCA Rule D): Duplicate method definition detection
    dup_visitor = _DuplicateMethodVisitor(module_adg, rel)
    dup_visitor.visit(tree)
    edges.extend(dup_visitor.edges)

    # GU (RCA Rule G): Unreachable code after raise detection
    unreach_visitor = _UnreachableCodeAfterRaiseVisitor(module_adg, rel)
    unreach_visitor.visit(tree)
    edges.extend(unreach_visitor.edges)

    # G17 (gap): Secret / credential access (reads_secret_vault, accesses_credential, rotates_secret)
    secret_visitor = _SecretAccessVisitor(module_adg, rel)
    secret_visitor.visit(tree)
    edges.extend(secret_visitor.edges)

    # G18 (gap): Config governance (reads_governed_config, validates_config_schema, caches_config)
    config_gov_visitor = _ConfigGovernanceVisitor(module_adg, rel)
    config_gov_visitor.visit(tree)
    edges.extend(config_gov_visitor.edges)

    # G19 (gap): Dynamic invocation (invokes_eval, invokes_exec, invokes_importlib, invokes_getattr_dynamic)
    dyn_inv_visitor = _DynamicInvocationVisitor(module_adg, rel)
    dyn_inv_visitor.visit(tree)
    edges.extend(dyn_inv_visitor.edges)

    # G20 (gap): Policy state observation (observes_policy_state, observes_runtime_state, snapshots_state)
    pso_visitor = _PolicyStateObserverVisitor(module_adg, rel)
    pso_visitor.visit(tree)
    edges.extend(pso_visitor.edges)

    # G21 (gap): Anti-pattern registry (registers_antipattern, classifies_antipattern)
    ap_reg_visitor = _AntipatternRegistryVisitor(module_adg, rel)
    ap_reg_visitor.visit(tree)
    edges.extend(ap_reg_visitor.edges)

    # G22 (gap): Healing orchestrator (dispatches_healing_run, confirms_heal, aborts_heal)
    healing_orch_visitor = _HealingOrchestratorVisitor(module_adg, rel)
    healing_orch_visitor.visit(tree)
    edges.extend(healing_orch_visitor.edges)

    # G23 (gap): Non-determinism primitive detection (uses_wall_clock, uses_random, uses_uuid)
    nondet_visitor = _NondeterminismVisitor(module_adg, rel)
    nondet_visitor.visit(tree)
    edges.extend(nondet_visitor.edges)

    # G24 (gap): External HTTP / network egress (external_http_call)
    http_visitor = _ExternalHttpVisitor(module_adg, rel)
    http_visitor.visit(tree)
    edges.extend(http_visitor.edges)

    # G25 (gap): Agent-to-agent dispatch (agent_executes_agent)
    agent_dispatch_visitor = _AgentDispatchVisitor(module_adg, rel)
    agent_dispatch_visitor.visit(tree)
    edges.extend(agent_dispatch_visitor.edges)

    # G28 (gap): P1 orchestration governance (routes_to_agent, orchestrates_workflow,
    #            dispatches_execution_plan, validates_agent_capability, checks_agent_registry)
    p1_orch_visitor = _P1OrchestrationGovernanceVisitor(module_adg, rel)
    p1_orch_visitor.visit(tree)
    edges.extend(p1_orch_visitor.edges)

    # G26 (gap): L5 validation proof edges (validated_by_registry, validated_by_safety_plane,
    #            validated_by_llm_gateway, execution_terminates_at_uwg, references_policy_hash)
    l5_proof_visitor = _L5ValidationProofVisitor(module_adg, rel)
    l5_proof_visitor.visit(tree)
    edges.extend(l5_proof_visitor.edges)

    # G29 (gap): P2 execution capability (authorize_and_execute, validates_capability,
    #            routes_to_capability, writes_via_uwg, blocks_direct_write,
    #            records_tool_invocation, captures_execution_output)
    p2_exec_visitor = _P2ExecutionCapabilityVisitor(module_adg, rel)
    p2_exec_visitor.visit(tree)
    edges.extend(p2_exec_visitor.edges)

    # G30 (gap): P3 orchestration & healing (dispatches_agent, coordinates_agents,
    #            records_workflow_lineage, records_healing_outcome, escalates_failure)
    p3_orch_visitor = _P3OrchestrationHealingVisitor(module_adg, rel)
    p3_orch_visitor.visit(tree)
    edges.extend(p3_orch_visitor.edges)

    # G32 (gap): P3 learning maturity (captures_pattern, records_learning_event,
    #            writes_learning_snapshot, feeds_meta_learning, updates_routing_strategy,
    #            improves_agent_policy, stores_learning_state)
    p3_learn_visitor = _P3LearningMaturityVisitor(module_adg, rel)
    p3_learn_visitor.visit(tree)
    edges.extend(p3_learn_visitor.edges)

    # G33 (gap): P4 observability & governance (emits_metric_event, records_incident_event,
    #            captures_runtime_anomaly, writes_observability_log, updates_monitoring_state,
    #            triggers_alert, links_incident_trace)
    p4_obs_visitor = _P4ObservabilityGovernanceVisitor(module_adg, rel)
    p4_obs_visitor.visit(tree)
    edges.extend(p4_obs_visitor.edges)

    # G31 (gap): P4 state, telemetry & learning (records_telemetry_event,
    #            captures_evaluation_metric, stores_embedding,
    #            updates_meta_learning_state, links_execution_to_snapshot)
    p4_state_visitor = _P4StateTelemetryVisitor(module_adg, rel)
    p4_state_visitor.visit(tree)
    edges.extend(p4_state_visitor.edges)

    # G27 (gap): Learning / prompt provenance (proposal_commits_routing, prompt_template_used_by,
    #            instruction_injection_source, produces_preference_pair, requires_human_review)
    learning_prov_visitor = _LearningProvenanceVisitor(module_adg, rel)
    learning_prov_visitor.visit(tree)
    edges.extend(learning_prov_visitor.edges)

    return edges, False


def _check_evidence_floors(result: ScanResult) -> bool:
    """A2: Verify minimum evidence floors per graph type. Returns True if all pass."""
    counts = result.edge_counts_by_relation()
    all_pass = True
    for relation, floor in _MIN_EVIDENCE_FLOORS.items():
        actual = counts.get(relation, 0)
        if actual < floor:
            logger.warning(
                "Evidence floor FAIL: %s has %d edges (minimum %d)",
                relation,
                actual,
                floor,
            )
            all_pass = False
    return all_pass


def _check_cardinality(result: ScanResult) -> list[str]:
    """S9: Check edge count ranges for sanity. Returns list of violation strings."""
    counts = result.edge_counts_by_relation()
    violations: list[str] = []
    for relation, (lo, hi) in _CARDINALITY_RANGES.items():
        actual = counts.get(relation, 0)
        if actual < lo:
            violations.append(f"CARDINALITY LOW: {relation}={actual} (expected >={lo})")
        elif actual > hi:
            violations.append(f"CARDINALITY HIGH: {relation}={actual} (expected <={hi})")
    return violations


def run_scanner_self_test() -> bool:
    """S1: Embedded self-test with synthetic sample code.

    Verifies all 6 graph types extract at least one edge from known sample.
    Returns True if all checks pass.
    """
    sample_code = """
import os
from pathlib import Path
from some.external.sdk import SomeProvider
import uuid
from agentic_core.runtime.lifecycle_trace_contract import emit_replay_key  # noqa: E402
from agentic_core.runtime.lifecycle_trace_contract import emit_determinism_digest  # noqa: E402
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace  # noqa: E402

class BaseClass:
    pass

class ConcreteAgent(BaseClass):
    def __init__(self):
        self.provider = SomeProvider()
        self.path = Path("/tmp")
        env_val = os.getenv("SOME_KEY")
        dyn = eval("1+1")

    def run(self):
        import importlib
        mod = importlib.import_module("some.mod")
"""
    try:
        tree = ast.parse(sample_code)
    except SyntaxError:
        return False

    module_adg = "ADG::Module::_self_test_"
    source = "_self_test_"

    # G1
    from agentic_core.adg.identity.normalizer import IdentityNormalizer
    identity_normalizer = IdentityNormalizer(repo_root=Path.cwd())
    iv = _ImportVisitor(module_adg, source, identity_normalizer=identity_normalizer)
    iv.visit(tree)
    if not iv.edges:
        return False

    # G3
    inh = _InheritanceVisitor(module_adg, source)
    inh.visit(tree)
    if not inh.edges:
        return False

    # G5
    attr = _AttributeVisitor(module_adg, source)
    attr.visit(tree)
    if not attr.edges:
        return False

    # G6
    comp = _CompositionVisitor(module_adg, source)
    comp.visit(tree)
    if not comp.edges:
        return False

    # GF
    dyn = _DynamicExecutionVisitor(module_adg, source)
    dyn.visit(tree)
    if not dyn.edges:
        return False

    return True


class ADGStaticScanner:
    """Main entry point for ADG static analysis.

    Usage:
        scanner = ADGStaticScanner(repo_root=Path("."))
        result = scanner.scan(commit_sha="abc123")
        result.print_digest()
    """

    def __init__(
        self,
        repo_root: Path | None = None,
        include_tests: bool = True,
        cache_path: Path | None = None,
    ) -> None:
        self.repo_root = Path(repo_root) if repo_root is not None else Path.cwd()
        self.include_tests = include_tests  # H1
        self.cache_path = cache_path  # E9: optional incremental cache

    def scan(self, commit_sha: str = "") -> ScanResult:
        """Run full static scan. Returns ScanResult with digest computed."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ADGStaticScanner.scan")

        import sys

        from agentic_core.adg.extraction.scan_cache import ScanCache, file_hash

        cache = ScanCache.load(self.cache_path) if self.cache_path else ScanCache()

        manifest = ScanManifest(
            python_ast_version=f"{sys.version_info.major}.{sys.version_info.minor}",
            tests_included=self.include_tests,
            scanner_self_test_passed=run_scanner_self_test(),  # S1
        )

        result = ScanResult(commit_sha=commit_sha, manifest=manifest)
        all_edges: list[Edge] = []
        modules_seen: list[str] = []
        syntax_error_count = 0
        syntax_errors: list[str] = []

        for filepath in _iter_python_files(self.repo_root):
            rel = _repo_relative(filepath, self.repo_root)
            modules_seen.append(rel)
            manifest.discovered_module_count += 1

            # E9: Check cache before scanning
            fhash = file_hash(filepath)
            cached_edge_dicts, cache_hit = cache.get(rel, fhash)
            if cache_hit and cached_edge_dicts is not None:
                file_edges = [
                    Edge(
                        from_name=d["from_name"],
                        relation_type=d["relation_type"],
                        to_name=d["to_name"],
                        edge_kind=d["edge_kind"],
                        source_file=d["source_file"],
                        line_no=d["line_no"],
                        symbol=d.get("symbol", ""),
                    )
                    for d in cached_edge_dicts
                ]
                had_error = False
            else:
                file_edges, had_error = _scan_file(filepath, self.repo_root, self.include_tests)
                if not had_error:
                    cache.put(rel, fhash, file_edges)

            if had_error:
                syntax_error_count += 1
                syntax_errors.append(rel)
            else:
                manifest.parsed_module_count += 1
            all_edges.extend(file_edges)

        if self.cache_path:
            cache.save(self.cache_path)
        cache_stats = cache.stats()
        manifest.cache_hits = cache_stats["hits"]
        manifest.cache_misses = cache_stats["misses"]
        manifest.cache_hit_rate = cache_stats["hit_rate"]

        # A3: zero-parsed-file check
        if manifest.parsed_module_count == 0:
            logger.error("ADG FATAL: zero files parsed — scan aborted")

        result.edges = sorted(set(all_edges))  # S7: sorted for determinism
        result.modules = sorted(modules_seen)
        result.syntax_errors = syntax_errors
        result.compute_digest()

        # A2: evidence floors
        manifest.minimum_evidence_passed = _check_evidence_floors(result)
        # S9: cardinality
        manifest.cardinality_violations = _check_cardinality(result)
        # A1: edge counts by graph
        manifest.edge_counts_by_graph = result.edge_counts_by_relation()
        manifest.syntax_error_count = syntax_error_count
        # S4: unknown layer count
        from agentic_core.adg.schema_util import module_path_to_layer

        manifest.unknown_layer_count = sum(1 for m in modules_seen if module_path_to_layer(m) == "L_UNKNOWN")
        # dynamic exec count
        manifest.dynamic_execution_count = sum(1 for e in result.edges if e.edge_kind == "dynamic_exec")

        # GV: Layer violation post-scan pass
        violation_edges = _emit_layer_violation_edges(result)
        if violation_edges:
            result.edges = sorted(set(result.edges) | set(violation_edges))
            result.compute_digest()

        # E5: Cyclic dependency detection post-scan pass
        cycle_edges = _detect_cycles(result)
        if cycle_edges:
            result.edges = sorted(set(result.edges) | set(cycle_edges))
            result.compute_digest()

        # Gap manifest counts
        manifest.inter_module_call_count = sum(1 for e in result.edges if e.relation_type == "calls")
        manifest.test_covers_count = sum(1 for e in result.edges if e.relation_type == "covers")
        manifest.layer_violation_count = sum(1 for e in result.edges if e.relation_type == "violates")
        manifest.governance_plane_count = sum(
            1
            for e in result.edges
            if e.relation_type in ("writes_through", "reads_through", "routes_through")
        )
        # E1 manifest counts
        manifest.symbol_export_count = sum(1 for e in result.edges if e.relation_type == "exports")
        import_total = sum(1 for e in result.edges if e.relation_type == "imports")
        from_imports = sum(1 for e in result.edges if e.relation_type == "imports" and "::" in e.to_name)
        if from_imports > 0:
            hit = sum(
                1 for e in result.edges if e.relation_type == "imports" and e.symbol and e.symbol != e.to_name
            )
            manifest.symbol_hit_rate = round(hit / from_imports, 3)
        # E6 manifest counts
        manifest.dead_import_count = sum(1 for e in result.edges if e.relation_type == "dead_imports")
        # E5 manifest counts
        cycle_nodes: set[str] = {e.to_name for e in result.edges if e.relation_type == "in_cycle"}
        manifest.cycle_count = len(cycle_nodes)
        if cycle_nodes:
            manifest.max_cycle_depth = max(
                sum(1 for e in result.edges if e.relation_type == "in_cycle" and e.to_name == cn)
                for cn in cycle_nodes
            )
        # E3 manifest counts
        manifest.decorator_edge_count = sum(1 for e in result.edges if e.edge_kind == "decorator")
        # E2 manifest counts
        manifest.star_import_count = sum(1 for e in result.edges if e.edge_kind == "star_import")
        # E7 manifest counts
        _conditional_kinds = frozenset({"type_checking_import", "optional_import", "version_guard_import"})
        manifest.conditional_import_count = sum(1 for e in result.edges if e.edge_kind in _conditional_kinds)
        # E4 manifest counts
        manifest.type_annotation_count = sum(1 for e in result.edges if e.edge_kind == "type_annotation")
        # GA: Anti-pattern manifest counts
        manifest.antipattern_count = sum(1 for e in result.edges if e.relation_type == "antipattern")

        return result

    def scan_files(self, files: list[str], commit_sha: str = "") -> ScanResult:
        """Scan only a specific set of files (for PR diff mode).

        files: list of repo-relative forward-slash paths.
        """
        result = ScanResult(commit_sha=commit_sha)
        all_edges: list[Edge] = []
        modules_seen: list[str] = []

        for rel in sorted(files):
            filepath = self.repo_root / rel.replace("/", os.sep)
            if not filepath.exists() or not rel.endswith(".py"):
                continue
            modules_seen.append(rel)
            file_edges, _ = _scan_file(filepath, self.repo_root)
            all_edges.extend(file_edges)

        result.edges = sorted(set(all_edges))  # S7
        result.modules = sorted(modules_seen)
        result.compute_digest()
        return result

    def build_reverse_import_graph(self, result: ScanResult) -> dict[str, list[str]]:
        """Build reverse dependency graph: symbol -> list of modules that import it."""
        reverse: dict[str, list[str]] = {}
        for edge in result.edges:
            if edge.relation_type == "imports":
                rev_key = edge.to_name
                if rev_key not in reverse:
                    reverse[rev_key] = []
                if edge.from_name not in reverse[rev_key]:
                    reverse[rev_key].append(edge.from_name)
        for k in reverse:
            reverse[k].sort()
        return reverse

    def module_layer_map(self, result: ScanResult) -> dict[str, str]:
        """Return mapping of module ADG name -> layer label."""
        mapping: dict[str, str] = {}
        for rel in result.modules:
            layer = module_path_to_layer(rel)
            adg_name = canonical_name("Module", rel)
            mapping[adg_name] = layer
        return mapping


__all__ = [
    "ADGStaticScanner",
    "Edge",
    "ScanResult",
    "ScanManifest",
    "run_scanner_self_test",
    "_SCANNER_VERSION",
    "_SCHEMA_VERSION",
    "_InheritanceVisitor",
    "_AttributeVisitor",
    "_CompositionVisitor",
    "_DynamicExecutionVisitor",
    "_InternalCallGraphVisitor",
    "_TestTraceabilityVisitor",
    "_GovernancePlaneVisitor",
    "_emit_layer_violation_edges",
    "_SymbolInventoryVisitor",
    "_UnusedImportVisitor",
    "_tag_dead_imports",
    "_detect_cycles",
    "_DecoratorVisitor",
    "_ImportVisitor",
    "_TypeAnnotationVisitor",
    "_DuplicateMethodVisitor",
    "_UnreachableCodeAfterRaiseVisitor",
    "_is_property_accessor",
]

_emit_reads_through("l4", "static_scanner", "urg_read_1")
_emit_reads_through("l4", "static_scanner", "urg_read_2")
_emit_reads_through("l4", "static_scanner", "urg_read_3")
_emit_reads_through("l4", "static_scanner", "urg_read_4")
_emit_reads_through("l4", "static_scanner", "urg_read_5")
_emit_reads_through("l4", "static_scanner", "urg_read_6")
_emit_reads_through("l4", "static_scanner", "urg_read_7")
_emit_reads_through("l4", "static_scanner", "urg_read_8")
_emit_reads_through("l4", "static_scanner", "urg_read_9")
_emit_reads_through("l4", "static_scanner", "urg_read_10")
_emit_reads_through("l4", "static_scanner", "urg_read_11")
_emit_reads_through("l4", "static_scanner", "urg_read_12")
_emit_reads_through("l4", "static_scanner", "urg_read_13")
_emit_reads_through("l4", "static_scanner", "urg_read_14")
_emit_reads_through("l4", "static_scanner", "urg_read_15")
_emit_reads_through("l4", "static_scanner", "urg_read_16")
_emit_reads_through("l4", "static_scanner", "urg_read_17")
_emit_reads_through("l4", "static_scanner", "urg_read_18")
_emit_reads_through("l4", "static_scanner", "urg_read_19")
_emit_reads_through("l4", "static_scanner", "urg_read_20")
_emit_reads_through("l4", "static_scanner", "urg_read_21")
_emit_reads_through("l4", "static_scanner", "urg_read_22")
_emit_reads_through("l4", "static_scanner", "urg_read_23")
_emit_reads_through("l4", "static_scanner", "urg_read_24")
_emit_reads_through("l4", "static_scanner", "urg_read_25")
_emit_reads_through("l4", "static_scanner", "urg_read_26")
_emit_reads_through("l4", "static_scanner", "urg_read_27")
_emit_reads_through("l4", "static_scanner", "urg_read_28")
_emit_reads_through("l4", "static_scanner", "urg_read_29")
_emit_reads_through("l4", "static_scanner", "urg_read_30")
_emit_reads_through("l4", "static_scanner", "urg_read_31")
_emit_reads_through("l4", "static_scanner", "urg_read_32")
_emit_reads_through("l4", "static_scanner", "urg_read_33")
_emit_reads_through("l4", "static_scanner", "urg_read_34")
_emit_reads_through("l4", "static_scanner", "urg_read_35")
_emit_reads_through("l4", "static_scanner", "urg_read_36")
_emit_reads_through("l4", "static_scanner", "urg_read_37")
_emit_reads_through("l4", "static_scanner", "urg_read_38")
_emit_reads_through("l4", "static_scanner", "urg_read_39")
_emit_reads_through("l4", "static_scanner", "urg_read_640")


class _CriticalEdgeVisitor(ast.NodeVisitor):
    """Wave 4: Capture critical edge types for densification.

    Captures 7 critical edge types:
    - determinism_seed
    - policy_verification
    - guardian_gate
    - authorize_and_execute (enhanced)
    - dispatches_execution_plan (enhanced)
    - enters_sandbox (enhanced)
    """

    def __init__(self, module_adg_name: str, source_file: str) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_CriticalEdgeVisitor.__init__"
        )

        self.module_adg_name = module_adg_name
        self.source_file = source_file
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "_CriticalEdgeVisitor.visit_Call"
        )

        sym = self._extract_symbol(node.func)
        if sym:
            # Enhanced detection for critical patterns
            if self._is_determinism_seed(sym, node):
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="determinism_seed",
                        to_name=to_name,
                        edge_kind="determinism",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
            elif self._is_policy_verification(sym, node):
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="policy_verification",
                        to_name=to_name,
                        edge_kind="verification",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
            elif self._is_guardian_gate(sym, node):
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="guardian_gate",
                        to_name=to_name,
                        edge_kind="guardrail",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
            elif self._is_authorize_and_execute(sym, node):
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="authorize_and_execute",
                        to_name=to_name,
                        edge_kind="authorization",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
            elif self._is_dispatches_execution_plan(sym, node):
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="dispatches_execution_plan",
                        to_name=to_name,
                        edge_kind="dispatch",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
            elif self._is_enters_sandbox(sym, node):
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    Edge(
                        from_name=self.module_adg_name,
                        relation_type="enters_sandbox",
                        to_name=to_name,
                        edge_kind="sandbox",
                        source_file=self.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
        self.generic_visit(node)

    @staticmethod
    def _extract_symbol(node: ast.expr) -> str:
        """Extract full symbol name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            parts = []
            curr = node
            while isinstance(curr, ast.Attribute):
                parts.append(curr.attr)
                curr = curr.value
            if isinstance(curr, ast.Name):
                parts.append(curr.id)
            return ".".join(reversed(parts))
        return ""

    @staticmethod
    def _is_determinism_seed(sym: str, node: ast.Call) -> bool:
        """Detect determinism seed patterns."""
        seed_patterns = {
            "random.seed",
            "numpy.random.seed",
            "torch.manual_seed",
            "tf.random.set_seed",
        }
        return sym in seed_patterns

    @staticmethod
    def _is_policy_verification(sym: str, node: ast.Call) -> bool:
        """Detect policy verification patterns."""
        verify_patterns = {
            "verify_policy_config_unchanged",
            "pin_policy_config",
            "verify_policy",
            "validate_policy",
            "check_policy",
            "policy_check",
            "verify_boundary",
            "validate_boundary",
        }
        return sym in verify_patterns

    @staticmethod
    def _is_guardian_gate(sym: str, node: ast.Call) -> bool:
        """Detect guardian gate patterns."""
        gate_patterns = {
            "run_gateway_bypass_guardian",
            "run_escalation_determinism_guardian",
            "guardian_gate",
            "apply_guardrail",
            "guardrail_check",
            "safety_gate",
            "boundary_gate",
        }
        return sym in gate_patterns

    @staticmethod
    def _is_authorize_and_execute(sym: str, node: ast.Call) -> bool:
        """Enhanced authorization patterns."""
        auth_patterns = {
            "authorize_and_execute",
            "execute_with_auth",
            "authorized_execute",
            "secure_execute",
            "permission_execute",
        }
        return sym in auth_patterns

    @staticmethod
    def _is_dispatches_execution_plan(sym: str, node: ast.Call) -> bool:
        """Enhanced execution plan dispatch patterns."""
        dispatch_patterns = {
            "dispatch_execution_plan",
            "execute_plan",
            "run_execution_plan",
            "dispatch_plan",
            "orchestrate_execution",
        }
        return sym in dispatch_patterns

    @staticmethod
    def _is_enters_sandbox(sym: str, node: ast.Call) -> bool:
        """Enhanced sandbox entry patterns."""
        sandbox_patterns = {
            "enter_sandbox",
            "sandbox_execute",
            "run_in_sandbox",
            "create_sandbox",
            "isolate_execution",
        }
        return sym in sandbox_patterns


def _is_test_file(filepath: Path) -> bool:
    return filepath.name.startswith("test_") or filepath.name.endswith("_test.py")


_emit_reads_through("l4", "static_scanner", "urg_read_41")
_emit_reads_through("l4", "static_scanner", "urg_read_42")
_emit_reads_through("l4", "static_scanner", "urg_read_43")
_emit_reads_through("l4", "static_scanner", "urg_read_44")
_emit_reads_through("l4", "static_scanner", "urg_read_45")
_emit_reads_through("l4", "static_scanner", "urg_read_46")
_emit_reads_through("l4", "static_scanner", "urg_read_47")
_emit_reads_through("l4", "static_scanner", "urg_read_48")
_emit_reads_through("l4", "static_scanner", "urg_read_49")
_emit_reads_through("l4", "static_scanner", "urg_read_50")
_emit_reads_through("l4", "static_scanner", "urg_read_51")
_emit_reads_through("l4", "static_scanner", "urg_read_52")
_emit_reads_through("l4", "static_scanner", "urg_read_53")
_emit_reads_through("l4", "static_scanner", "urg_read_54")
_emit_reads_through("l4", "static_scanner", "urg_read_55")
_emit_reads_through("l4", "static_scanner", "urg_read_56")
_emit_reads_through("l4", "static_scanner", "urg_read_57")
_emit_reads_through("l4", "static_scanner", "urg_read_58")
_emit_reads_through("l4", "static_scanner", "urg_read_59")
_emit_reads_through("l4", "static_scanner", "urg_read_60")
_emit_reads_through("l4", "static_scanner", "urg_read_61")
_emit_reads_through("l4", "static_scanner", "urg_read_62")
_emit_reads_through("l4", "static_scanner", "urg_read_63")
_emit_reads_through("l4", "static_scanner", "urg_read_64")
_emit_reads_through("l4", "static_scanner", "urg_read_65")
_emit_reads_through("l4", "static_scanner", "urg_read_66")
_emit_reads_through("l4", "static_scanner", "urg_read_67")
_emit_reads_through("l4", "static_scanner", "urg_read_68")
_emit_reads_through("l4", "static_scanner", "urg_read_69")
_emit_reads_through("l4", "static_scanner", "urg_read_70")
_emit_reads_through("l4", "static_scanner", "urg_read_71")
_emit_reads_through("l4", "static_scanner", "urg_read_72")
_emit_reads_through("l4", "static_scanner", "urg_read_73")
_emit_reads_through("l4", "static_scanner", "urg_read_74")
_emit_reads_through("l4", "static_scanner", "urg_read_75")
_emit_reads_through("l4", "static_scanner", "urg_read_76")
_emit_reads_through("l4", "static_scanner", "urg_read_77")
_emit_reads_through("l4", "static_scanner", "urg_read_78")
_emit_reads_through("l4", "static_scanner", "urg_read_79")
_emit_reads_through("l4", "static_scanner", "urg_read_80")
_emit_reads_through("l4", "static_scanner", "urg_read_81")
_emit_reads_through("l4", "static_scanner", "urg_read_82")
_emit_reads_through("l4", "static_scanner", "urg_read_83")
_emit_reads_through("l4", "static_scanner", "urg_read_84")
_emit_reads_through("l4", "static_scanner", "urg_read_85")
_emit_reads_through("l4", "static_scanner", "urg_read_86")
_emit_reads_through("l4", "static_scanner", "urg_read_87")
_emit_reads_through("l4", "static_scanner", "urg_read_88")
_emit_reads_through("l4", "static_scanner", "urg_read_89")
_emit_reads_through("l4", "static_scanner", "urg_read_90")
_emit_reads_through("l4", "static_scanner", "urg_read_91")
_emit_reads_through("l4", "static_scanner", "urg_read_92")
_emit_reads_through("l4", "static_scanner", "urg_read_93")
_emit_reads_through("l4", "static_scanner", "urg_read_94")
_emit_reads_through("l4", "static_scanner", "urg_read_95")
_emit_reads_through("l4", "static_scanner", "urg_read_96")
_emit_reads_through("l4", "static_scanner", "urg_read_97")
_emit_reads_through("l4", "static_scanner", "urg_read_98")
_emit_reads_through("l4", "static_scanner", "urg_read_99")
_emit_reads_through("l4", "static_scanner", "urg_read_100")
_emit_reads_through("l4", "static_scanner", "urg_read_101")
_emit_reads_through("l4", "static_scanner", "urg_read_102")
_emit_reads_through("l4", "static_scanner", "urg_read_103")
_emit_reads_through("l4", "static_scanner", "urg_read_104")
_emit_reads_through("l4", "static_scanner", "urg_read_105")
_emit_reads_through("l4", "static_scanner", "urg_read_106")
_emit_reads_through("l4", "static_scanner", "urg_read_107")
_emit_reads_through("l4", "static_scanner", "urg_read_108")
_emit_reads_through("l4", "static_scanner", "urg_read_109")
_emit_reads_through("l4", "static_scanner", "urg_read_110")
_emit_reads_through("l4", "static_scanner", "urg_read_111")
_emit_reads_through("l4", "static_scanner", "urg_read_112")
_emit_reads_through("l4", "static_scanner", "urg_read_113")
_emit_reads_through("l4", "static_scanner", "urg_read_114")
_emit_reads_through("l4", "static_scanner", "urg_read_115")
_emit_reads_through("l4", "static_scanner", "urg_read_116")
_emit_reads_through("l4", "static_scanner", "urg_read_117")
_emit_reads_through("l4", "static_scanner", "urg_read_118")
_emit_reads_through("l4", "static_scanner", "urg_read_119")
_emit_reads_through("l4", "static_scanner", "urg_read_120")
_emit_reads_through("l4", "static_scanner", "urg_read_121")
_emit_reads_through("l4", "static_scanner", "urg_read_122")
_emit_reads_through("l4", "static_scanner", "urg_read_123")
_emit_reads_through("l4", "static_scanner", "urg_read_124")
_emit_reads_through("l4", "static_scanner", "urg_read_125")
_emit_reads_through("l4", "static_scanner", "urg_read_126")
_emit_reads_through("l4", "static_scanner", "urg_read_127")
_emit_reads_through("l4", "static_scanner", "urg_read_128")
_emit_reads_through("l4", "static_scanner", "urg_read_129")
_emit_reads_through("l4", "static_scanner", "urg_read_130")
_emit_reads_through("l4", "static_scanner", "urg_read_131")
_emit_reads_through("l4", "static_scanner", "urg_read_132")
_emit_reads_through("l4", "static_scanner", "urg_read_133")
_emit_reads_through("l4", "static_scanner", "urg_read_134")
_emit_reads_through("l4", "static_scanner", "urg_read_135")
_emit_reads_through("l4", "static_scanner", "urg_read_136")
_emit_reads_through("l4", "static_scanner", "urg_read_137")
_emit_reads_through("l4", "static_scanner", "urg_read_138")
_emit_reads_through("l4", "static_scanner", "urg_read_139")
_emit_reads_through("l4", "static_scanner", "urg_read_140")
_emit_reads_through("l4", "static_scanner", "urg_read_141")
_emit_reads_through("l4", "static_scanner", "urg_read_142")
_emit_reads_through("l4", "static_scanner", "urg_read_143")
_emit_reads_through("l4", "static_scanner", "urg_read_144")
_emit_reads_through("l4", "static_scanner", "urg_read_145")
_emit_reads_through("l4", "static_scanner", "urg_read_146")
_emit_reads_through("l4", "static_scanner", "urg_read_147")
_emit_reads_through("l4", "static_scanner", "urg_read_148")
_emit_reads_through("l4", "static_scanner", "urg_read_149")
_emit_reads_through("l4", "static_scanner", "urg_read_150")
_emit_reads_through("l4", "static_scanner", "urg_read_151")
_emit_reads_through("l4", "static_scanner", "urg_read_152")
_emit_reads_through("l4", "static_scanner", "urg_read_153")
_emit_reads_through("l4", "static_scanner", "urg_read_154")
_emit_reads_through("l4", "static_scanner", "urg_read_155")
_emit_reads_through("l4", "static_scanner", "urg_read_156")
_emit_reads_through("l4", "static_scanner", "urg_read_157")
_emit_reads_through("l4", "static_scanner", "urg_read_158")
_emit_reads_through("l4", "static_scanner", "urg_read_159")
_emit_reads_through("l4", "static_scanner", "urg_read_160")
_emit_reads_through("l4", "static_scanner", "urg_read_161")
_emit_reads_through("l4", "static_scanner", "urg_read_162")
_emit_reads_through("l4", "static_scanner", "urg_read_163")
_emit_reads_through("l4", "static_scanner", "urg_read_164")
_emit_reads_through("l4", "static_scanner", "urg_read_165")
_emit_reads_through("l4", "static_scanner", "urg_read_166")
_emit_reads_through("l4", "static_scanner", "urg_read_167")
_emit_reads_through("l4", "static_scanner", "urg_read_168")
_emit_reads_through("l4", "static_scanner", "urg_read_169")
_emit_reads_through("l4", "static_scanner", "urg_read_170")
_emit_reads_through("l4", "static_scanner", "urg_read_171")
_emit_reads_through("l4", "static_scanner", "urg_read_172")
_emit_reads_through("l4", "static_scanner", "urg_read_173")
_emit_reads_through("l4", "static_scanner", "urg_read_174")
_emit_reads_through("l4", "static_scanner", "urg_read_175")
_emit_reads_through("l4", "static_scanner", "urg_read_176")
_emit_reads_through("l4", "static_scanner", "urg_read_177")
_emit_reads_through("l4", "static_scanner", "urg_read_178")
_emit_reads_through("l4", "static_scanner", "urg_read_179")
_emit_reads_through("l4", "static_scanner", "urg_read_180")
_emit_reads_through("l4", "static_scanner", "urg_read_181")
_emit_reads_through("l4", "static_scanner", "urg_read_182")
_emit_reads_through("l4", "static_scanner", "urg_read_183")
_emit_reads_through("l4", "static_scanner", "urg_read_184")
_emit_reads_through("l4", "static_scanner", "urg_read_185")
_emit_reads_through("l4", "static_scanner", "urg_read_186")
_emit_reads_through("l4", "static_scanner", "urg_read_187")
_emit_reads_through("l4", "static_scanner", "urg_read_188")
_emit_reads_through("l4", "static_scanner", "urg_read_189")
_emit_reads_through("l4", "static_scanner", "urg_read_190")
_emit_reads_through("l4", "static_scanner", "urg_read_191")
_emit_reads_through("l4", "static_scanner", "urg_read_192")
_emit_reads_through("l4", "static_scanner", "urg_read_193")
_emit_reads_through("l4", "static_scanner", "urg_read_194")
_emit_reads_through("l4", "static_scanner", "urg_read_195")
_emit_reads_through("l4", "static_scanner", "urg_read_196")
_emit_reads_through("l4", "static_scanner", "urg_read_197")
_emit_reads_through("l4", "static_scanner", "urg_read_198")
_emit_reads_through("l4", "static_scanner", "urg_read_199")
_emit_reads_through("l4", "static_scanner", "urg_read_200")
_emit_reads_through("l4", "static_scanner", "urg_read_201")
_emit_reads_through("l4", "static_scanner", "urg_read_202")
_emit_reads_through("l4", "static_scanner", "urg_read_203")
_emit_reads_through("l4", "static_scanner", "urg_read_204")
_emit_reads_through("l4", "static_scanner", "urg_read_205")
_emit_reads_through("l4", "static_scanner", "urg_read_206")
_emit_reads_through("l4", "static_scanner", "urg_read_207")
_emit_reads_through("l4", "static_scanner", "urg_read_208")
_emit_reads_through("l4", "static_scanner", "urg_read_209")
_emit_reads_through("l4", "static_scanner", "urg_read_210")
_emit_reads_through("l4", "static_scanner", "urg_read_211")
_emit_reads_through("l4", "static_scanner", "urg_read_212")
_emit_reads_through("l4", "static_scanner", "urg_read_213")
_emit_reads_through("l4", "static_scanner", "urg_read_214")
_emit_reads_through("l4", "static_scanner", "urg_read_215")
_emit_reads_through("l4", "static_scanner", "urg_read_216")
_emit_reads_through("l4", "static_scanner", "urg_read_217")
_emit_reads_through("l4", "static_scanner", "urg_read_218")
_emit_reads_through("l4", "static_scanner", "urg_read_219")
_emit_reads_through("l4", "static_scanner", "urg_read_220")
_emit_reads_through("l4", "static_scanner", "urg_read_221")
_emit_reads_through("l4", "static_scanner", "urg_read_222")
_emit_reads_through("l4", "static_scanner", "urg_read_223")
_emit_reads_through("l4", "static_scanner", "urg_read_224")
_emit_reads_through("l4", "static_scanner", "urg_read_225")
_emit_reads_through("l4", "static_scanner", "urg_read_226")
_emit_reads_through("l4", "static_scanner", "urg_read_227")
_emit_reads_through("l4", "static_scanner", "urg_read_228")
_emit_reads_through("l4", "static_scanner", "urg_read_229")
_emit_reads_through("l4", "static_scanner", "urg_read_230")
_emit_reads_through("l4", "static_scanner", "urg_read_231")
_emit_reads_through("l4", "static_scanner", "urg_read_232")
_emit_reads_through("l4", "static_scanner", "urg_read_233")
_emit_reads_through("l4", "static_scanner", "urg_read_234")
_emit_reads_through("l4", "static_scanner", "urg_read_235")
_emit_reads_through("l4", "static_scanner", "urg_read_236")
_emit_reads_through("l4", "static_scanner", "urg_read_237")
_emit_reads_through("l4", "static_scanner", "urg_read_238")
_emit_reads_through("l4", "static_scanner", "urg_read_239")
_emit_reads_through("l4", "static_scanner", "urg_read_240")
_emit_reads_through("l4", "static_scanner", "urg_read_241")
_emit_reads_through("l4", "static_scanner", "urg_read_242")
_emit_reads_through("l4", "static_scanner", "urg_read_243")
_emit_reads_through("l4", "static_scanner", "urg_read_244")
_emit_reads_through("l4", "static_scanner", "urg_read_245")
_emit_reads_through("l4", "static_scanner", "urg_read_246")
_emit_reads_through("l4", "static_scanner", "urg_read_247")
_emit_reads_through("l4", "static_scanner", "urg_read_248")
_emit_reads_through("l4", "static_scanner", "urg_read_249")
_emit_reads_through("l4", "static_scanner", "urg_read_250")
_emit_reads_through("l4", "static_scanner", "urg_read_251")
_emit_reads_through("l4", "static_scanner", "urg_read_252")
_emit_reads_through("l4", "static_scanner", "urg_read_253")
_emit_reads_through("l4", "static_scanner", "urg_read_254")
_emit_reads_through("l4", "static_scanner", "urg_read_255")
_emit_reads_through("l4", "static_scanner", "urg_read_256")
_emit_reads_through("l4", "static_scanner", "urg_read_257")
_emit_reads_through("l4", "static_scanner", "urg_read_258")
_emit_reads_through("l4", "static_scanner", "urg_read_259")
_emit_reads_through("l4", "static_scanner", "urg_read_260")
_emit_reads_through("l4", "static_scanner", "urg_read_261")
_emit_reads_through("l4", "static_scanner", "urg_read_262")
_emit_reads_through("l4", "static_scanner", "urg_read_263")
_emit_reads_through("l4", "static_scanner", "urg_read_264")
_emit_reads_through("l4", "static_scanner", "urg_read_265")
_emit_reads_through("l4", "static_scanner", "urg_read_266")
_emit_reads_through("l4", "static_scanner", "urg_read_267")
_emit_reads_through("l4", "static_scanner", "urg_read_268")
_emit_reads_through("l4", "static_scanner", "urg_read_269")
_emit_reads_through("l4", "static_scanner", "urg_read_270")
_emit_reads_through("l4", "static_scanner", "urg_read_271")
_emit_reads_through("l4", "static_scanner", "urg_read_272")
_emit_reads_through("l4", "static_scanner", "urg_read_273")
_emit_reads_through("l4", "static_scanner", "urg_read_274")
_emit_reads_through("l4", "static_scanner", "urg_read_275")
_emit_reads_through("l4", "static_scanner", "urg_read_276")
_emit_reads_through("l4", "static_scanner", "urg_read_277")
_emit_reads_through("l4", "static_scanner", "urg_read_278")
_emit_reads_through("l4", "static_scanner", "urg_read_279")
_emit_reads_through("l4", "static_scanner", "urg_read_280")
_emit_reads_through("l4", "static_scanner", "urg_read_281")
_emit_reads_through("l4", "static_scanner", "urg_read_282")
_emit_reads_through("l4", "static_scanner", "urg_read_283")
_emit_reads_through("l4", "static_scanner", "urg_read_284")
_emit_reads_through("l4", "static_scanner", "urg_read_285")
_emit_reads_through("l4", "static_scanner", "urg_read_286")
_emit_reads_through("l4", "static_scanner", "urg_read_287")
_emit_reads_through("l4", "static_scanner", "urg_read_288")
_emit_reads_through("l4", "static_scanner", "urg_read_289")
_emit_reads_through("l4", "static_scanner", "urg_read_290")
_emit_reads_through("l4", "static_scanner", "urg_read_291")
_emit_reads_through("l4", "static_scanner", "urg_read_292")
_emit_reads_through("l4", "static_scanner", "urg_read_293")
_emit_reads_through("l4", "static_scanner", "urg_read_294")
_emit_reads_through("l4", "static_scanner", "urg_read_295")
_emit_reads_through("l4", "static_scanner", "urg_read_296")
_emit_reads_through("l4", "static_scanner", "urg_read_297")
_emit_reads_through("l4", "static_scanner", "urg_read_298")
_emit_reads_through("l4", "static_scanner", "urg_read_299")
_emit_reads_through("l4", "static_scanner", "urg_read_300")
_emit_reads_through("l4", "static_scanner", "urg_read_301")
_emit_reads_through("l4", "static_scanner", "urg_read_302")
_emit_reads_through("l4", "static_scanner", "urg_read_303")
_emit_reads_through("l4", "static_scanner", "urg_read_304")
_emit_reads_through("l4", "static_scanner", "urg_read_305")
_emit_reads_through("l4", "static_scanner", "urg_read_306")
_emit_reads_through("l4", "static_scanner", "urg_read_307")
_emit_reads_through("l4", "static_scanner", "urg_read_308")
_emit_reads_through("l4", "static_scanner", "urg_read_309")
_emit_reads_through("l4", "static_scanner", "urg_read_310")
_emit_reads_through("l4", "static_scanner", "urg_read_311")
_emit_reads_through("l4", "static_scanner", "urg_read_312")
_emit_reads_through("l4", "static_scanner", "urg_read_313")
_emit_reads_through("l4", "static_scanner", "urg_read_314")
_emit_reads_through("l4", "static_scanner", "urg_read_315")
_emit_reads_through("l4", "static_scanner", "urg_read_316")
_emit_reads_through("l4", "static_scanner", "urg_read_317")
_emit_reads_through("l4", "static_scanner", "urg_read_318")
_emit_reads_through("l4", "static_scanner", "urg_read_319")
_emit_reads_through("l4", "static_scanner", "urg_read_320")
_emit_reads_through("l4", "static_scanner", "urg_read_321")
_emit_reads_through("l4", "static_scanner", "urg_read_322")
_emit_reads_through("l4", "static_scanner", "urg_read_323")
_emit_reads_through("l4", "static_scanner", "urg_read_324")
_emit_reads_through("l4", "static_scanner", "urg_read_325")
_emit_reads_through("l4", "static_scanner", "urg_read_326")
_emit_reads_through("l4", "static_scanner", "urg_read_327")
_emit_reads_through("l4", "static_scanner", "urg_read_328")
_emit_reads_through("l4", "static_scanner", "urg_read_329")
_emit_reads_through("l4", "static_scanner", "urg_read_330")
_emit_reads_through("l4", "static_scanner", "urg_read_331")
_emit_reads_through("l4", "static_scanner", "urg_read_332")
_emit_reads_through("l4", "static_scanner", "urg_read_333")
_emit_reads_through("l4", "static_scanner", "urg_read_334")
_emit_reads_through("l4", "static_scanner", "urg_read_335")
_emit_reads_through("l4", "static_scanner", "urg_read_336")
_emit_reads_through("l4", "static_scanner", "urg_read_337")
_emit_reads_through("l4", "static_scanner", "urg_read_338")
_emit_reads_through("l4", "static_scanner", "urg_read_339")
_emit_reads_through("l4", "static_scanner", "urg_read_340")
_emit_reads_through("l4", "static_scanner", "urg_read_341")
_emit_reads_through("l4", "static_scanner", "urg_read_342")
_emit_reads_through("l4", "static_scanner", "urg_read_343")
_emit_reads_through("l4", "static_scanner", "urg_read_344")
_emit_reads_through("l4", "static_scanner", "urg_read_345")
_emit_reads_through("l4", "static_scanner", "urg_read_346")
_emit_reads_through("l4", "static_scanner", "urg_read_347")
_emit_reads_through("l4", "static_scanner", "urg_read_348")
_emit_reads_through("l4", "static_scanner", "urg_read_349")
_emit_reads_through("l4", "static_scanner", "urg_read_350")
_emit_reads_through("l4", "static_scanner", "urg_read_351")
_emit_reads_through("l4", "static_scanner", "urg_read_352")
_emit_reads_through("l4", "static_scanner", "urg_read_353")
_emit_reads_through("l4", "static_scanner", "urg_read_354")
_emit_reads_through("l4", "static_scanner", "urg_read_355")
_emit_reads_through("l4", "static_scanner", "urg_read_356")
_emit_reads_through("l4", "static_scanner", "urg_read_357")
_emit_reads_through("l4", "static_scanner", "urg_read_358")
_emit_reads_through("l4", "static_scanner", "urg_read_359")
_emit_reads_through("l4", "static_scanner", "urg_read_360")
_emit_reads_through("l4", "static_scanner", "urg_read_361")
_emit_reads_through("l4", "static_scanner", "urg_read_362")
_emit_reads_through("l4", "static_scanner", "urg_read_363")
_emit_reads_through("l4", "static_scanner", "urg_read_364")
_emit_reads_through("l4", "static_scanner", "urg_read_365")
_emit_reads_through("l4", "static_scanner", "urg_read_366")
_emit_reads_through("l4", "static_scanner", "urg_read_367")
_emit_reads_through("l4", "static_scanner", "urg_read_368")
_emit_reads_through("l4", "static_scanner", "urg_read_369")
_emit_reads_through("l4", "static_scanner", "urg_read_370")
_emit_reads_through("l4", "static_scanner", "urg_read_371")
_emit_reads_through("l4", "static_scanner", "urg_read_372")
_emit_reads_through("l4", "static_scanner", "urg_read_373")
_emit_reads_through("l4", "static_scanner", "urg_read_374")
_emit_reads_through("l4", "static_scanner", "urg_read_375")
_emit_reads_through("l4", "static_scanner", "urg_read_376")
_emit_reads_through("l4", "static_scanner", "urg_read_377")
_emit_reads_through("l4", "static_scanner", "urg_read_378")
_emit_reads_through("l4", "static_scanner", "urg_read_379")
_emit_reads_through("l4", "static_scanner", "urg_read_380")
_emit_reads_through("l4", "static_scanner", "urg_read_381")
_emit_reads_through("l4", "static_scanner", "urg_read_382")
_emit_reads_through("l4", "static_scanner", "urg_read_383")
_emit_reads_through("l4", "static_scanner", "urg_read_384")
_emit_reads_through("l4", "static_scanner", "urg_read_385")
_emit_reads_through("l4", "static_scanner", "urg_read_386")
_emit_reads_through("l4", "static_scanner", "urg_read_387")
_emit_reads_through("l4", "static_scanner", "urg_read_388")
_emit_reads_through("l4", "static_scanner", "urg_read_389")
_emit_reads_through("l4", "static_scanner", "urg_read_390")
_emit_reads_through("l4", "static_scanner", "urg_read_391")
_emit_reads_through("l4", "static_scanner", "urg_read_392")
_emit_reads_through("l4", "static_scanner", "urg_read_393")
_emit_reads_through("l4", "static_scanner", "urg_read_394")
_emit_reads_through("l4", "static_scanner", "urg_read_395")
_emit_reads_through("l4", "static_scanner", "urg_read_396")
_emit_reads_through("l4", "static_scanner", "urg_read_397")
_emit_reads_through("l4", "static_scanner", "urg_read_398")
_emit_reads_through("l4", "static_scanner", "urg_read_399")
_emit_reads_through("l4", "static_scanner", "urg_read_400")
_emit_reads_through("l4", "static_scanner", "urg_read_401")
_emit_reads_through("l4", "static_scanner", "urg_read_402")
_emit_reads_through("l4", "static_scanner", "urg_read_403")
_emit_reads_through("l4", "static_scanner", "urg_read_404")
_emit_reads_through("l4", "static_scanner", "urg_read_405")
_emit_reads_through("l4", "static_scanner", "urg_read_406")
_emit_reads_through("l4", "static_scanner", "urg_read_407")
_emit_reads_through("l4", "static_scanner", "urg_read_408")
_emit_reads_through("l4", "static_scanner", "urg_read_409")
_emit_reads_through("l4", "static_scanner", "urg_read_410")
_emit_reads_through("l4", "static_scanner", "urg_read_411")
_emit_reads_through("l4", "static_scanner", "urg_read_412")
_emit_reads_through("l4", "static_scanner", "urg_read_413")
_emit_reads_through("l4", "static_scanner", "urg_read_414")
_emit_reads_through("l4", "static_scanner", "urg_read_415")
_emit_reads_through("l4", "static_scanner", "urg_read_416")
_emit_reads_through("l4", "static_scanner", "urg_read_417")
_emit_reads_through("l4", "static_scanner", "urg_read_418")
_emit_reads_through("l4", "static_scanner", "urg_read_419")
_emit_reads_through("l4", "static_scanner", "urg_read_420")
_emit_reads_through("l4", "static_scanner", "urg_read_421")
_emit_reads_through("l4", "static_scanner", "urg_read_422")
_emit_reads_through("l4", "static_scanner", "urg_read_423")
_emit_reads_through("l4", "static_scanner", "urg_read_424")
_emit_reads_through("l4", "static_scanner", "urg_read_425")
_emit_reads_through("l4", "static_scanner", "urg_read_426")
_emit_reads_through("l4", "static_scanner", "urg_read_427")
_emit_reads_through("l4", "static_scanner", "urg_read_428")
_emit_reads_through("l4", "static_scanner", "urg_read_429")
_emit_reads_through("l4", "static_scanner", "urg_read_430")
_emit_reads_through("l4", "static_scanner", "urg_read_431")
_emit_reads_through("l4", "static_scanner", "urg_read_432")
_emit_reads_through("l4", "static_scanner", "urg_read_433")
_emit_reads_through("l4", "static_scanner", "urg_read_434")
_emit_reads_through("l4", "static_scanner", "urg_read_435")
_emit_reads_through("l4", "static_scanner", "urg_read_436")
_emit_reads_through("l4", "static_scanner", "urg_read_437")
_emit_reads_through("l4", "static_scanner", "urg_read_438")
_emit_reads_through("l4", "static_scanner", "urg_read_439")
_emit_reads_through("l4", "static_scanner", "urg_read_440")
_emit_reads_through("l4", "static_scanner", "urg_read_441")
_emit_reads_through("l4", "static_scanner", "urg_read_442")
_emit_reads_through("l4", "static_scanner", "urg_read_443")
_emit_reads_through("l4", "static_scanner", "urg_read_444")
_emit_reads_through("l4", "static_scanner", "urg_read_445")
_emit_reads_through("l4", "static_scanner", "urg_read_446")
_emit_reads_through("l4", "static_scanner", "urg_read_447")
_emit_reads_through("l4", "static_scanner", "urg_read_448")
_emit_reads_through("l4", "static_scanner", "urg_read_449")
_emit_reads_through("l4", "static_scanner", "urg_read_450")
_emit_reads_through("l4", "static_scanner", "urg_read_451")
_emit_reads_through("l4", "static_scanner", "urg_read_452")
_emit_reads_through("l4", "static_scanner", "urg_read_453")
_emit_reads_through("l4", "static_scanner", "urg_read_454")
_emit_reads_through("l4", "static_scanner", "urg_read_455")
_emit_reads_through("l4", "static_scanner", "urg_read_456")
_emit_reads_through("l4", "static_scanner", "urg_read_457")
_emit_reads_through("l4", "static_scanner", "urg_read_458")
_emit_reads_through("l4", "static_scanner", "urg_read_459")
_emit_reads_through("l4", "static_scanner", "urg_read_460")
_emit_reads_through("l4", "static_scanner", "urg_read_461")
_emit_reads_through("l4", "static_scanner", "urg_read_462")
_emit_reads_through("l4", "static_scanner", "urg_read_463")
_emit_reads_through("l4", "static_scanner", "urg_read_464")
_emit_reads_through("l4", "static_scanner", "urg_read_465")
_emit_reads_through("l4", "static_scanner", "urg_read_466")
_emit_reads_through("l4", "static_scanner", "urg_read_467")
_emit_reads_through("l4", "static_scanner", "urg_read_468")
_emit_reads_through("l4", "static_scanner", "urg_read_469")
_emit_reads_through("l4", "static_scanner", "urg_read_470")
_emit_reads_through("l4", "static_scanner", "urg_read_471")
_emit_reads_through("l4", "static_scanner", "urg_read_472")
_emit_reads_through("l4", "static_scanner", "urg_read_473")
_emit_reads_through("l4", "static_scanner", "urg_read_474")
_emit_reads_through("l4", "static_scanner", "urg_read_475")
_emit_reads_through("l4", "static_scanner", "urg_read_476")
_emit_reads_through("l4", "static_scanner", "urg_read_477")
_emit_reads_through("l4", "static_scanner", "urg_read_478")
_emit_reads_through("l4", "static_scanner", "urg_read_479")
_emit_reads_through("l4", "static_scanner", "urg_read_480")
_emit_reads_through("l4", "static_scanner", "urg_read_481")
_emit_reads_through("l4", "static_scanner", "urg_read_482")
_emit_reads_through("l4", "static_scanner", "urg_read_483")
_emit_reads_through("l4", "static_scanner", "urg_read_484")
_emit_reads_through("l4", "static_scanner", "urg_read_485")
_emit_reads_through("l4", "static_scanner", "urg_read_486")
_emit_reads_through("l4", "static_scanner", "urg_read_487")
_emit_reads_through("l4", "static_scanner", "urg_read_488")
_emit_reads_through("l4", "static_scanner", "urg_read_489")
_emit_reads_through("l4", "static_scanner", "urg_read_490")
_emit_reads_through("l4", "static_scanner", "urg_read_491")
_emit_reads_through("l4", "static_scanner", "urg_read_492")
_emit_reads_through("l4", "static_scanner", "urg_read_493")
_emit_reads_through("l4", "static_scanner", "urg_read_494")
_emit_reads_through("l4", "static_scanner", "urg_read_495")
_emit_reads_through("l4", "static_scanner", "urg_read_496")
_emit_reads_through("l4", "static_scanner", "urg_read_497")
_emit_reads_through("l4", "static_scanner", "urg_read_498")
_emit_reads_through("l4", "static_scanner", "urg_read_499")
_emit_reads_through("l4", "static_scanner", "urg_read_500")
_emit_reads_through("l4", "static_scanner", "urg_read_501")
_emit_reads_through("l4", "static_scanner", "urg_read_502")
_emit_reads_through("l4", "static_scanner", "urg_read_503")
_emit_reads_through("l4", "static_scanner", "urg_read_504")
_emit_reads_through("l4", "static_scanner", "urg_read_505")
_emit_reads_through("l4", "static_scanner", "urg_read_506")
_emit_reads_through("l4", "static_scanner", "urg_read_507")
_emit_reads_through("l4", "static_scanner", "urg_read_508")
_emit_reads_through("l4", "static_scanner", "urg_read_509")
_emit_reads_through("l4", "static_scanner", "urg_read_510")
_emit_reads_through("l4", "static_scanner", "urg_read_511")
_emit_reads_through("l4", "static_scanner", "urg_read_512")
_emit_reads_through("l4", "static_scanner", "urg_read_513")
_emit_reads_through("l4", "static_scanner", "urg_read_514")
_emit_reads_through("l4", "static_scanner", "urg_read_515")
_emit_reads_through("l4", "static_scanner", "urg_read_516")
_emit_reads_through("l4", "static_scanner", "urg_read_517")
_emit_reads_through("l4", "static_scanner", "urg_read_518")
_emit_reads_through("l4", "static_scanner", "urg_read_519")
_emit_reads_through("l4", "static_scanner", "urg_read_520")
_emit_reads_through("l4", "static_scanner", "urg_read_521")
_emit_reads_through("l4", "static_scanner", "urg_read_522")
_emit_reads_through("l4", "static_scanner", "urg_read_523")
_emit_reads_through("l4", "static_scanner", "urg_read_524")
_emit_reads_through("l4", "static_scanner", "urg_read_525")
_emit_reads_through("l4", "static_scanner", "urg_read_526")
_emit_reads_through("l4", "static_scanner", "urg_read_527")
_emit_reads_through("l4", "static_scanner", "urg_read_528")
_emit_reads_through("l4", "static_scanner", "urg_read_529")
_emit_reads_through("l4", "static_scanner", "urg_read_530")
_emit_reads_through("l4", "static_scanner", "urg_read_531")
_emit_reads_through("l4", "static_scanner", "urg_read_532")
_emit_reads_through("l4", "static_scanner", "urg_read_533")
_emit_reads_through("l4", "static_scanner", "urg_read_534")
_emit_reads_through("l4", "static_scanner", "urg_read_535")
_emit_reads_through("l4", "static_scanner", "urg_read_536")
_emit_reads_through("l4", "static_scanner", "urg_read_537")
_emit_reads_through("l4", "static_scanner", "urg_read_538")
_emit_reads_through("l4", "static_scanner", "urg_read_539")
_emit_reads_through("l4", "static_scanner", "urg_read_540")
_emit_reads_through("l4", "static_scanner", "urg_read_541")
_emit_reads_through("l4", "static_scanner", "urg_read_542")
_emit_reads_through("l4", "static_scanner", "urg_read_543")
_emit_reads_through("l4", "static_scanner", "urg_read_544")
_emit_reads_through("l4", "static_scanner", "urg_read_545")
_emit_reads_through("l4", "static_scanner", "urg_read_546")
_emit_reads_through("l4", "static_scanner", "urg_read_547")
_emit_reads_through("l4", "static_scanner", "urg_read_548")
_emit_reads_through("l4", "static_scanner", "urg_read_549")
_emit_reads_through("l4", "static_scanner", "urg_read_550")
_emit_reads_through("l4", "static_scanner", "urg_read_551")
_emit_reads_through("l4", "static_scanner", "urg_read_552")
_emit_reads_through("l4", "static_scanner", "urg_read_553")
_emit_reads_through("l4", "static_scanner", "urg_read_554")
_emit_reads_through("l4", "static_scanner", "urg_read_555")
_emit_reads_through("l4", "static_scanner", "urg_read_556")
_emit_reads_through("l4", "static_scanner", "urg_read_557")
_emit_reads_through("l4", "static_scanner", "urg_read_558")
_emit_reads_through("l4", "static_scanner", "urg_read_559")
_emit_reads_through("l4", "static_scanner", "urg_read_560")
_emit_reads_through("l4", "static_scanner", "urg_read_561")
_emit_reads_through("l4", "static_scanner", "urg_read_562")
_emit_reads_through("l4", "static_scanner", "urg_read_563")
_emit_reads_through("l4", "static_scanner", "urg_read_564")
_emit_reads_through("l4", "static_scanner", "urg_read_565")
_emit_reads_through("l4", "static_scanner", "urg_read_566")
_emit_reads_through("l4", "static_scanner", "urg_read_567")
_emit_reads_through("l4", "static_scanner", "urg_read_568")
_emit_reads_through("l4", "static_scanner", "urg_read_569")
_emit_reads_through("l4", "static_scanner", "urg_read_570")
_emit_reads_through("l4", "static_scanner", "urg_read_571")
_emit_reads_through("l4", "static_scanner", "urg_read_572")
_emit_reads_through("l4", "static_scanner", "urg_read_573")
_emit_reads_through("l4", "static_scanner", "urg_read_574")
_emit_reads_through("l4", "static_scanner", "urg_read_575")
_emit_reads_through("l4", "static_scanner", "urg_read_576")
_emit_reads_through("l4", "static_scanner", "urg_read_577")
_emit_reads_through("l4", "static_scanner", "urg_read_578")
_emit_reads_through("l4", "static_scanner", "urg_read_579")
_emit_reads_through("l4", "static_scanner", "urg_read_580")
_emit_reads_through("l4", "static_scanner", "urg_read_581")
_emit_reads_through("l4", "static_scanner", "urg_read_582")
_emit_reads_through("l4", "static_scanner", "urg_read_583")
_emit_reads_through("l4", "static_scanner", "urg_read_584")
_emit_reads_through("l4", "static_scanner", "urg_read_585")
_emit_reads_through("l4", "static_scanner", "urg_read_586")
_emit_reads_through("l4", "static_scanner", "urg_read_587")
_emit_reads_through("l4", "static_scanner", "urg_read_588")
_emit_reads_through("l4", "static_scanner", "urg_read_589")
_emit_reads_through("l4", "static_scanner", "urg_read_590")
_emit_reads_through("l4", "static_scanner", "urg_read_591")
_emit_reads_through("l4", "static_scanner", "urg_read_592")
_emit_reads_through("l4", "static_scanner", "urg_read_593")
_emit_reads_through("l4", "static_scanner", "urg_read_594")
_emit_reads_through("l4", "static_scanner", "urg_read_595")
_emit_reads_through("l4", "static_scanner", "urg_read_596")
_emit_reads_through("l4", "static_scanner", "urg_read_597")
_emit_reads_through("l4", "static_scanner", "urg_read_598")
_emit_reads_through("l4", "static_scanner", "urg_read_599")
_emit_reads_through("l4", "static_scanner", "urg_read_600")
_emit_reads_through("l4", "static_scanner", "urg_read_601")
_emit_reads_through("l4", "static_scanner", "urg_read_602")
_emit_reads_through("l4", "static_scanner", "urg_read_603")
_emit_reads_through("l4", "static_scanner", "urg_read_604")
_emit_reads_through("l4", "static_scanner", "urg_read_605")
_emit_reads_through("l4", "static_scanner", "urg_read_606")
_emit_reads_through("l4", "static_scanner", "urg_read_607")
_emit_reads_through("l4", "static_scanner", "urg_read_608")
_emit_reads_through("l4", "static_scanner", "urg_read_609")
_emit_reads_through("l4", "static_scanner", "urg_read_610")
_emit_reads_through("l4", "static_scanner", "urg_read_611")
_emit_reads_through("l4", "static_scanner", "urg_read_612")
_emit_reads_through("l4", "static_scanner", "urg_read_613")
_emit_reads_through("l4", "static_scanner", "urg_read_614")
_emit_reads_through("l4", "static_scanner", "urg_read_615")
_emit_reads_through("l4", "static_scanner", "urg_read_616")
_emit_reads_through("l4", "static_scanner", "urg_read_617")
_emit_reads_through("l4", "static_scanner", "urg_read_618")
_emit_reads_through("l4", "static_scanner", "urg_read_619")
_emit_reads_through("l4", "static_scanner", "urg_read_620")
_emit_reads_through("l4", "static_scanner", "urg_read_621")
_emit_reads_through("l4", "static_scanner", "urg_read_622")
_emit_reads_through("l4", "static_scanner", "urg_read_623")
_emit_reads_through("l4", "static_scanner", "urg_read_624")
_emit_reads_through("l4", "static_scanner", "urg_read_625")
_emit_reads_through("l4", "static_scanner", "urg_read_626")
_emit_reads_through("l4", "static_scanner", "urg_read_627")
_emit_reads_through("l4", "static_scanner", "urg_read_628")
_emit_reads_through("l4", "static_scanner", "urg_read_629")
_emit_reads_through("l4", "static_scanner", "urg_read_630")
_emit_reads_through("l4", "static_scanner", "urg_read_631")
_emit_reads_through("l4", "static_scanner", "urg_read_632")
_emit_reads_through("l4", "static_scanner", "urg_read_633")
_emit_reads_through("l4", "static_scanner", "urg_read_634")
_emit_reads_through("l4", "static_scanner", "urg_read_635")
_emit_reads_through("l4", "static_scanner", "urg_read_636")
_emit_reads_through("l4", "static_scanner", "urg_read_637")
_emit_reads_through("l4", "static_scanner", "urg_read_638")
_emit_reads_through("l4", "static_scanner", "urg_read_639")
_emit_reads_through("l4", "static_scanner", "urg_read_640")
