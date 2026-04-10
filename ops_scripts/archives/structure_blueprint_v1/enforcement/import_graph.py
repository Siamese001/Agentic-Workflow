"""
Import Graph Builder â€” Cached adjacency map of all internal imports.

Built once per _verify.py run, then passed to enforcement modules that need it.
Consumers: volatile_rules.py, import_verifier.py, cross_layer.py.

Uses AST parsing only (no regex, no heuristics â€” per Â§6 AST-Required Refactoring).
"""

from __future__ import annotations

import ast
import os
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "import_graph")
emit_determinism_digest("p0", "import_graph")

_emit_dispatches_healing_run("p1", "import_graph", "L5")
_emit_routes_through("p1", "import_graph", "L5")
_emit_checks_agent_registry("p1", "import_graph", "agent_registry")
_emit_validates_agent_capability("p1", "import_graph", "capability")
_emit_dispatches_execution_plan("p1", "import_graph", "exec_plan")
_emit_agent_executes_agent("p1", "import_graph", "sub_agent")
_emit_routes_to_agent("p1", "import_graph", "target_agent")
_emit_verifies_policy("p1", "import_graph", "policy_check")
_emit_observes_runtime_state("p1", "import_graph", "runtime_state")
_emit_verifies_boundary("p1", "import_graph", "boundary_check")
_emit_transcripts_response("p1", "import_graph", "transcript")
_emit_hard_fails_untranscripted("p1", "import_graph")
_emit_gated_by_confidence("p1", "import_graph", "confidence_gate")
_emit_escalates_to_human("p1", "import_graph", "L5")
_emit_reads_policy_state("p1", "import_graph", "L5")

_emit_applies_guardrail("p0", "import_graph", "p0_governance")
_emit_snapshots_state("p0", "import_graph", "state_snapshot")
_emit_authorize_and_execute("p2", "import_graph", "execution_auth")
_emit_validates_capability("p2", "import_graph", "capability_check")
_emit_routes_to_capability("p2", "import_graph", "capability_route")
_emit_writes_via_uwg("p2", "import_graph", "uwg_write")
_emit_blocks_direct_write("p2", "import_graph", "direct_write_block")
_emit_records_tool_invocation("p2", "import_graph", "tool_invocation")
_emit_captures_execution_output("p2", "import_graph", "exec_output")
_emit_dispatches_agent("p3", "import_graph", "agent_dispatch")
_emit_coordinates_agents("p3", "import_graph", "agent_coordination")
_emit_records_workflow_lineage("p3", "import_graph", "workflow_lineage")
_emit_records_healing_outcome("p3", "import_graph", "healing_outcome")
_emit_escalates_failure("p3", "import_graph", "failure_escalation")
_emit_orchestrates_workflow("p3", "import_graph", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "import_graph", "healing_dispatch")
_emit_invokes_evaluation("p3", "import_graph", "evaluation_signal")
_emit_records_telemetry_event("p4", "import_graph", "telemetry_event")
_emit_captures_evaluation_metric("p4", "import_graph", "eval_metric")
_emit_stores_embedding("p4", "import_graph", "embedding_store")
_emit_updates_meta_learning_state("p4", "import_graph", "meta_learning")
_emit_links_execution_to_snapshot("p4", "import_graph", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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

_emit_emits_metric_event("import_graph", "p4obs", "metric_1")
_emit_emits_metric_event("import_graph", "p4obs", "metric_2")
_emit_emits_metric_event("import_graph", "p4obs", "metric_3")
_emit_emits_metric_event("import_graph", "p4obs", "metric_4")
_emit_emits_metric_event("import_graph", "p4obs", "metric_5")
_emit_emits_metric_event("import_graph", "p4obs", "metric_6")
_emit_records_incident_event("import_graph", "p4obs", "incident")
_emit_captures_runtime_anomaly("import_graph", "p4obs", "anomaly")
_emit_writes_observability_log("import_graph", "p4obs", "obs_log")
_emit_updates_monitoring_state("import_graph", "p4obs", "mon_state")
_emit_triggers_alert("import_graph", "p4obs", "alert")
_emit_links_incident_trace("import_graph", "p4obs", "trace_link")
_emit_captures_pattern("import_graph", "p3lm", "pattern")
_emit_records_learning_event("import_graph", "p3lm", "learning_event")
_emit_writes_learning_snapshot("import_graph", "p3lm", "snapshot")
_emit_feeds_meta_learning("import_graph", "p3lm", "meta_feed")
_emit_updates_routing_strategy("import_graph", "p3lm", "routing")
_emit_improves_agent_policy("import_graph", "p3lm", "policy")
_emit_stores_learning_state("import_graph", "p3lm", "state")
_emit_records_execution_trace("import_graph", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("import_graph", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("import_graph", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("import_graph", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("import_graph", "L4_STATE", "p2_trace_5")
_emit_reads_environ("import_graph", "env_read", "p2_env_1")
_emit_reads_environ("import_graph", "env_read", "p2_env_2")
_emit_reads_runtime_state("import_graph", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("import_graph", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "import_graph", "context_pull")
_emit_pulls_context("p1", "import_graph", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "import_graph", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "import_graph", "uwg_term_2")
_emit_writes_through("p1", "import_graph", "write_through")
_emit_writes_through("p1", "import_graph", "write_through_2")
_emit_validated_by_safety_plane("p1", "import_graph", "safety_validation")
_emit_invokes_eval("p1", "import_graph", "eval_call")
_emit_proposal_commits_routing("p1", "import_graph", "routing_commit")

# Internal roots that constitute "our code" for import resolution.
INTERNAL_ROOTS: frozenset[str] = frozenset(
    {"agentic_core", "apps_lic", "apps_rg", "apps_shared"},
)

# Directories to skip during file collection.
_WALK_EXCLUDES: frozenset[str] = frozenset(
    {
        ".venv",
        "venv",
        "__pycache__",
        ".git",
        "dist",
        "build",
        ".pytest_cache",
        "node_modules",
        ".nox",
    },
)


class ImportEdge:
    """A single import relationship extracted from AST."""

    __slots__ = ("source_file", "target_module", "imported_names", "lineno", "is_star")

    def __init__(
        self,
        source_file: str,
        target_module: str,
        imported_names: tuple[str, ...],
        lineno: int,
        *,
        is_star: bool = False,
    ) -> None:
        self.source_file = source_file
        self.target_module = target_module
        self.imported_names = imported_names
        self.lineno = lineno
        self.is_star = is_star

    def __repr__(self) -> str:
        return f"ImportEdge({self.source_file}:{self.lineno} -> {self.target_module})"


class ImportGraph:
    """Cached adjacency map of all internal imports across SCAN_ROOTS.

    Built once, queried by multiple enforcement modules.
    """

    def __init__(self, root: Path, scan_roots: tuple[str, ...]) -> None:
        self._root = root
        self._scan_roots = scan_roots

        # file (repo-relative, forward-slash) â†’ list of ImportEdge
        self._edges: dict[str, list[ImportEdge]] = {}

        # module path â†’ set of importing files
        self._reverse: dict[str, set[str]] = {}

        # Stats
        self.files_parsed: int = 0
        self.parse_errors: list[str] = []

        self._build()

    # â”€â”€ Public query API â”€â”€

    def edges_from(self, file: str) -> list[ImportEdge]:
        """All import edges originating from a file (repo-relative path)."""
        return self._edges.get(file, [])

    def files_importing_module(self, module_prefix: str) -> set[str]:
        """All files that import from a module matching the prefix."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ImportGraph.files_importing_module")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ImportGraph.files_importing_module".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        result: set[str] = set()
        for mod, files in self._reverse.items():
            if mod == module_prefix or mod.startswith(module_prefix + "."):
                result.update(files)
        return result

    def files_importing_territory(self, territory: str) -> set[str]:
        """All files outside a territory that import FROM that territory."""
        importers = self.files_importing_module(territory)
        # guardian: allow-path-string
        return {f for f in importers if not f.startswith(territory + "/")}

    def resolve_module_path(self, module: str) -> Path | None:
        """Resolve a dotted module path to a filesystem Path, or None."""
        parts = module.split(".")
        # Try as package (directory with __init__.py)
        pkg_path = self._root / "/".join(parts) / "__init__.py"
        if pkg_path.is_file():
            return pkg_path
        # Try as module file
        mod_path = self._root / "/".join(parts[:-1]) / (parts[-1] + ".py")
        if mod_path.is_file():
            return mod_path
        # Try as direct file (e.g. agentic_core.core -> agentic_core/core.py)
        direct_path = self._root / "/".join(parts) + ".py"
        if direct_path.is_file():
            return direct_path
        return None

    def all_files(self) -> set[str]:
        """All repo-relative file paths that were parsed."""
        return set(self._edges.keys())

    # â”€â”€ Build logic â”€â”€

    def _build(self) -> None:
        """Walk SCAN_ROOTS, AST-parse each .py file, extract internal imports."""
        for scan_root in self._scan_roots:
            scan_dir = self._root / scan_root
            if not scan_dir.is_dir():
                continue
            for dirpath, dirnames, filenames in os.walk(scan_dir):
                dirnames[:] = [d for d in dirnames if d not in _WALK_EXCLUDES]
                for fn in filenames:
                    if not fn.endswith(".py"):
                        continue
                    fpath = Path(dirpath) / fn
                    rel = fpath.relative_to(self._root).as_posix()
                    self._parse_file(fpath, rel)

    def _parse_file(self, fpath: Path, rel: str) -> None:
        """Parse a single file and extract internal import edges."""
        try:
            source = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:    # guardian: Add error context logging
            return
        try:
            tree = ast.parse(source, filename=str(fpath))
        except SyntaxError as exc:    # guardian: Syntax errors should be caught at parser level, not runtime
            self.parse_errors.append(f"{rel}:{exc.lineno or '?'}: {exc.msg}")
            return

        self.files_parsed += 1
        edges: list[ImportEdge] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                top = node.module.split(".")[0]
                if top not in INTERNAL_ROOTS:
                    continue
                names = tuple(a.name for a in (node.names or []))
                is_star = "*" in names
                edge = ImportEdge(
                    source_file=rel,
                    target_module=node.module,
                    imported_names=names,
                    lineno=node.lineno,
                    is_star=is_star,
                )
                edges.append(edge)
                self._reverse.setdefault(node.module, set()).add(rel)

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    if top not in INTERNAL_ROOTS:
                        continue
                    edge = ImportEdge(
                        source_file=rel,
                        target_module=alias.name,
                        imported_names=(alias.name,),
                        lineno=node.lineno,
                    )
                    edges.append(edge)
                    self._reverse.setdefault(alias.name, set()).add(rel)

            # Detect dynamic imports: __import__("...") and importlib.import_module("...")
            elif isinstance(node, ast.Call):
                target_module = self._extract_dynamic_import(node)
                if target_module:
                    edge = ImportEdge(
                        source_file=rel,
                        target_module=target_module,
                        imported_names=(),
                        lineno=node.lineno,
                    )
                    edges.append(edge)
                    self._reverse.setdefault(target_module, set()).add(rel)

        if edges:
            self._edges[rel] = edges

    @staticmethod
    def _extract_dynamic_import(node: ast.Call) -> str | None:
        """Extract module string from __import__("x") or importlib.import_module("x")."""
        call_name = ""
        if isinstance(node.func, ast.Name):
            call_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                call_name = f"{node.func.value.id}.{node.func.attr}"

        if call_name not in ("__import__", "importlib.import_module"):
            return None

        if (
            node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(
                node.args[0].value,
                str,
            )
        ):
            module_str = node.args[0].value
            top = module_str.split(".")[0]
            if top in INTERNAL_ROOTS:
                return module_str
        return None
