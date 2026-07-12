"""ADG Multi-Writer — produces all artifact tiers in one pass, zero redundancy.

Tier 1  adg_snapshot.json        CI-light, ~50 KB
    Metrics only: counts, digests, graph_plane_counts, violation summary,
    blind_spots, top-20 hotspots. No entities or edges.
    Used by: CI gate, drift detection, quick health checks.

Tier 2  adg_indexed.sqlite        Primary queryable store, ~38 MB
    SQLite database with three tables:
        nodes (id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path)
        edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
        meta  (key, value)
    Used by: all analysis, queries, layer-authority checks, mutation-path scans.
    NOTE: adg_full.json removed — SQLite is the canonical complete store.

Three non-overlapping split-plane sub-graphs (together = 100% edge coverage):
    adg_file_graph.json        imports, exports, dead_imports, covers, influences, in_cycle
    adg_symbol_graph.json      calls, implements, reads_from, writes_to, instantiates, ...
    adg_governance_graph.json  violates, antipattern, generates_prompt, ...
    NOTE: test_graph removed — covers edges live in file_graph.

Minimal ingestion set (non-redundant, 100% coverage):
    adg_LATEST.sqlite           ← primary: all 18 edge types, queryable
    adg_LATEST_snapshot.json    ← metrics / health summary only

Usage::

    from agentic_core.adg.artifact.multi_writer import write_all_artifacts

    paths = write_all_artifacts(artifact, out_dir=Path("artifacts/adg"), ts="20260311T154637Z")
    print(paths)
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

from agentic_core.adg.artifact.layer_splitter import split_artifact
from agentic_core.adg.artifact.normalizer import ArtifactNormalizer
from agentic_core.adg.artifact.sqlite_schema import DDL as _DDL
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
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

_emit_applies_guardrail("p0", "multi_writer", "p0_governance")
_emit_reads_policy_state("p0", "multi_writer", "policy_binding")
_emit_snapshots_state("p0", "multi_writer", "state_snapshot")
emit_replay_key("p0", "multi_writer")
emit_determinism_digest("p0", "multi_writer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "multi_writer", "execution_auth")
_emit_validates_capability("p2", "multi_writer", "capability_check")
_emit_routes_to_capability("p2", "multi_writer", "capability_route")
_emit_writes_via_uwg("p2", "multi_writer", "uwg_write")
_emit_blocks_direct_write("p2", "multi_writer", "direct_write_block")
_emit_records_tool_invocation("p2", "multi_writer", "tool_invocation")
_emit_captures_execution_output("p2", "multi_writer", "exec_output")
_emit_dispatches_agent("p3", "multi_writer", "agent_dispatch")
_emit_coordinates_agents("p3", "multi_writer", "agent_coordination")
_emit_records_workflow_lineage("p3", "multi_writer", "workflow_lineage")
_emit_records_healing_outcome("p3", "multi_writer", "healing_outcome")
_emit_escalates_failure("p3", "multi_writer", "failure_escalation")
_emit_orchestrates_workflow("p3", "multi_writer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "multi_writer", "healing_dispatch")
_emit_invokes_evaluation("p3", "multi_writer", "evaluation_signal")
_emit_records_telemetry_event("p4", "multi_writer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "multi_writer", "eval_metric")
_emit_stores_embedding("p4", "multi_writer", "embedding_store")
_emit_updates_meta_learning_state("p4", "multi_writer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "multi_writer", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.artifact.builder_types import ADGArtifact
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("multi_writer", "p4obs", "metric_1")
_emit_emits_metric_event("multi_writer", "p4obs", "metric_2")
_emit_emits_metric_event("multi_writer", "p4obs", "metric_3")
_emit_emits_metric_event("multi_writer", "p4obs", "metric_4")
_emit_emits_metric_event("multi_writer", "p4obs", "metric_5")
_emit_emits_metric_event("multi_writer", "p4obs", "metric_6")
_emit_records_incident_event("multi_writer", "p4obs", "incident")
_emit_captures_runtime_anomaly("multi_writer", "p4obs", "anomaly")
_emit_writes_observability_log("multi_writer", "p4obs", "obs_log")
_emit_updates_monitoring_state("multi_writer", "p4obs", "mon_state")
_emit_triggers_alert("multi_writer", "p4obs", "alert")
_emit_links_incident_trace("multi_writer", "p4obs", "trace_link")
_emit_captures_pattern("multi_writer", "p3lm", "pattern")
_emit_records_learning_event("multi_writer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("multi_writer", "p3lm", "snapshot")
_emit_feeds_meta_learning("multi_writer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("multi_writer", "p3lm", "routing")
_emit_improves_agent_policy("multi_writer", "p3lm", "policy")
_emit_stores_learning_state("multi_writer", "p3lm", "state")
_emit_records_execution_trace("multi_writer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("multi_writer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("multi_writer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("multi_writer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("multi_writer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("multi_writer", "env_read", "p2_env_1")
_emit_reads_environ("multi_writer", "env_read", "p2_env_2")
_emit_reads_runtime_state("multi_writer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("multi_writer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "multi_writer", "context_pull")
_emit_pulls_context("p1", "multi_writer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "multi_writer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "multi_writer", "uwg_term_2")
_emit_writes_through("p1", "multi_writer", "write_through")
_emit_writes_through("p1", "multi_writer", "write_through_2")
_emit_validated_by_safety_plane("p1", "multi_writer", "safety_validation")
_emit_invokes_eval("p1", "multi_writer", "eval_call")
_emit_proposal_commits_routing("p1", "multi_writer", "routing_commit")
_emit_escalates_to_human("p1", "multi_writer", "human_escalation")
_emit_routes_through("p1", "multi_writer", "route_through")
_emit_checks_agent_registry("p1", "multi_writer", "agent_registry")
_emit_validates_agent_capability("p1", "multi_writer", "capability")
_emit_dispatches_execution_plan("p1", "multi_writer", "exec_plan")
_emit_agent_executes_agent("p1", "multi_writer", "sub_agent")
_emit_routes_to_agent("p1", "multi_writer", "target_agent")
_emit_verifies_policy("p1", "multi_writer", "policy_check")
_emit_observes_runtime_state("p1", "multi_writer", "runtime_state")
_emit_verifies_boundary("p1", "multi_writer", "boundary_check")
_emit_transcripts_response("p1", "multi_writer", "transcript")
_emit_hard_fails_untranscripted("p1", "multi_writer")
_emit_gated_by_confidence("p1", "multi_writer", "confidence_gate")

# ---------------------------------------------------------------------------
# Snapshot (Tier 1)
# ---------------------------------------------------------------------------


def _build_snapshot(artifact: ADGArtifact) -> dict:
    """Build a lightweight CI snapshot dict — no entities or edges."""
    sm = artifact.structural_metrics.to_dict()
    bs = artifact.blind_spots.to_dict()

    # Relation-type distribution
    by_rel = sm.get("by_relation_type", {})

    # Top-20 fan-in hotspots (module names only, no full edge data)
    hotspots_in = sorted(sm.get("high_fan_in_modules", []), key=lambda x: -x.get("fan_in", 0))[:20]
    hotspots_out = sorted(sm.get("high_fan_out_modules", []), key=lambda x: -x.get("fan_out", 0))[:20]

    return {
        "schema_version": "snapshot-1.0",
        "commit_sha": artifact.commit_sha,
        "scanner_digest": artifact.scanner_digest,
        "artifact_digest": artifact.artifact_digest,
        "counts": {
            "total_entities": sm.get("total_entities", 0),
            "total_relations": sm.get("total_relations", 0),
            "module_count": sm.get("module_count", 0),
            "symbol_count": sm.get("symbol_count", 0),
            "external_count": sm.get("external_count", 0),
            "unresolved_count": sm.get("unresolved_count", 0),
            "orphan_module_count": sm.get("orphan_module_count", 0),
            "layer_violation_count": sm.get("layer_violation_count", 0),
        },
        "graph_plane_counts": {k: v for k, v in sorted(by_rel.items()) if v > 0},
        "by_layer": sm.get("by_layer", {}),
        "blind_spots": {
            "parse_failure_count": bs.get("parse_failure_count", 0),
            "dynamic_import_count": bs.get("dynamic_import_count", 0),
            "star_import_count": bs.get("star_import_count", 0),
        },
        "identity_health": artifact.identity_health,
        "top_fan_in_hotspots": hotspots_in,
        "top_fan_out_hotspots": hotspots_out,
    }


# ---------------------------------------------------------------------------
# SQLite index (Tier 3)
# ---------------------------------------------------------------------------

# Private compatibility alias imported from the canonical schema contract.


# STRICT MAP: one canonical token per edge_kind, PLUS a single documented
# semantic supersession: ``allow-broad-exception`` is the parent claim for
# ``except Exception``/``except BaseException`` and subsumes the swallow
# variants that a broad catch inherently exhibits (a broad catch always
# either swallows silently, logs-and-swallows, returns None, or re-raises).
# The swallow-specific tokens remain strictly scoped: they do NOT exempt
# each other or a broad catch.
_GUARDIAN_MAP: dict[str, tuple[str, ...]] = {
    "silent_exception_swallow": (
        "guardian: allow-silent-swallow",
        # W5.1 (2026-04-23): recognize author-vernacular variants documented in
        # tools/debug/_w5_token_inventory.py (≥2 occurrences, each with `--`
        # justification form). Variants describe the same semantic action —
        # silent swallow of a specific handler context:
        "guardian: allow-silent-swallower",  # 32 authored uses
        "guardian: allow-import-fail",  # 2 uses; ImportError-specific silent swallow
        "guardian: allow-rollback-failure",  # 2 uses; sqlite3 rollback best-effort
        "guardian: allow-specific",  # 19 uses; specific type but body still swallows
        "guardian: allow-specific-multi",  # 2 uses; tuple-form specific-type silent swallow
        "guardian: allow-broad-exception",
    ),
    "broad_exception_catch": (
        "guardian: allow-broad-exception",
        # W5.1 (2026-04-23): short/variant forms for broad catches:
        "guardian: allow-broad-except",  # 3 authored uses
        "guardian: allow-broad-catch",  # 2 uses
        "guardian: allow-broad",  # 2 uses; deliberate short form
        "guardian: allow-in-process-dispatcher",  # 2 uses; dispatcher-level broad isolation
    ),
    "log_and_swallow": (
        "guardian: allow-log-and-swallow",
        "guardian: allow-broad-exception",
    ),
    "return_none_swallow": (
        "guardian: allow-return-none-swallow",
        # W5.1 (2026-04-23): static scanner classifies
        #   `except X: Logger.debug(...)` as return_none_swallow when the
        # enclosing function returns None. Authors correctly annotate these as
        # log-and-swallow. Accept that alias here to close the scanner↔author
        # SSOT gap without touching the scanner itself (scheduled as W5.3).
        "guardian: allow-log-and-swallow",
        "guardian: allow-broad-exception",
    ),
    # Pattern C — dead code after raise. Strictly scoped: no supersession,
    # authors must justify each site individually (this is a bug, not a choice).
    "unreachable_after_raise": ("guardian: allow-unreachable-after-raise",),
    # Doc #8 — exception type erasure. Strictly scoped.
    "exception_type_erasure": ("guardian: allow-exception-type-erasure",),
    # Doc #9 — cleanup raises over original exception.
    "cleanup_raises_over_original": ("guardian: allow-cleanup-raises",),
    # Doc #10 — return in finally silently overrides try/except result.
    "return_in_finally": ("guardian: allow-finally-return",),
    # Blocking I/O inside an async function body (event-loop starvation).
    "blocking_call_in_async": ("guardian: allow-blocking-in-async",),
    # Retry loops without backoff (cost/latency amplification).
    "retry_without_backoff": ("guardian: allow-retry-without-backoff",),
    # Mutable default argument (shared state across calls).
    "mutable_default_arg": ("guardian: allow-mutable-default",),
    # Star import (namespace pollution, breaks static analysis).
    "star_import_use": ("guardian: allow-star-import",),
    "star_import": ("guardian: allow-star-import",),
    # Doc #7 — partial side effects: try-body writes, except swallows.
    "partial_side_effects": ("guardian: allow-partial-side-effects",),
    # Doc #11 — double logging: handler logs and re-raises.
    "double_logging": ("guardian: allow-double-logging",),
    # Bare 'except:' (catches SystemExit/KeyboardInterrupt/GeneratorExit).
    "bare_except": ("guardian: allow-bare-except",),
    # Doc #4 — default fallback masking: 'except: price = 0'.
    "default_fallback_masking": ("guardian: allow-default-fallback",),
    # Doc #12 — exception as normal control flow.
    "throw_for_normal_flow": ("guardian: allow-control-flow-exception",),
    # Hardcoded credentials in source code.
    "hardcoded_secret": ("guardian: allow-hardcoded-secret",),
    # Detector false-positive guard: 'getattr'/'setattr' flagged as hallucinated
    # tool names. getattr/setattr are Python stdlib builtins.
    "hallucinated_tool_name": ("guardian: allow-hallucinated-tool-name",),
    # Deliberate bypass of a chokepoint (e.g. direct HTTP/LLM call) with a
    # documented downstream fallback. Requires per-site justification.
    "chokepoint_bypass": ("guardian: allow-chokepoint-bypass",),
    # A3 — irreversible operation (unlink/rmtree/drop_table/etc.) without an
    # enclosing HITL checkpoint. Exempt only for rollback paths, cleanup-of-
    # cleanup, or documented reverse operations where HITL is structurally
    # incorrect. Requires per-site `-- <justification>` noting why the action
    # is reversal rather than a user-facing destructive primitive.
    "missing_hitl_on_irreversible": ("guardian: allow-missing-hitl-on-irreversible",),
}

_LAYER_VIOLATION_GUARDIANS = ("guardian: allow-layer-violation",)

_file_cache: dict[str, list[str]] = {}

_CANONICAL_GUARDIAN_TOKENS = frozenset(
    {
        "allow-silent-swallow",
        "allow-log-and-swallow",
        "allow-return-none-swallow",
        "allow-broad-exception",
        "allow-unreachable-after-raise",
        "allow-exception-type-erasure",
        "allow-cleanup-raises",
        "allow-finally-return",
        "allow-blocking-in-async",
        "allow-retry-without-backoff",
        "allow-mutable-default",
        "allow-star-import",
        "allow-partial-side-effects",
        "allow-double-logging",
        "allow-bare-except",
        "allow-default-fallback",
        "allow-control-flow-exception",
        "allow-hardcoded-secret",
        "allow-hallucinated-tool-name",
        "allow-chokepoint-bypass",
        "allow-missing-hitl-on-irreversible",
        # Layer-violation marker used by the layer-gravity filter path.
        # Without this entry, `_extract_guardian_tokens` silently drops the token
        # and `_has_guardian_comment` can never match layer-violation markers.
        "allow-layer-violation",
        # W5.1 (2026-04-23): author-vernacular exception-handling variants.
        # Each token is also listed in the relevant _GUARDIAN_MAP entry above
        # so `has_guardian_for_violation` will recognize them at the correct
        # edge_kind. Addition criterion: ≥2 occurrences in production source
        # with proper `-- <justification>` form (inventory at
        # tools/debug/_w5_token_inventory.py).
        "allow-silent-swallower",
        "allow-import-fail",
        "allow-rollback-failure",
        "allow-specific",
        "allow-specific-multi",
        "allow-broad-except",
        "allow-broad-catch",
        "allow-broad",
        "allow-in-process-dispatcher",
        # W17.b (2026-04-24): Author-Gate promotion of 4 high-volume tokens
        # (combined 1,076 organic call sites). Inventory baseline at
        # artifacts/guardian_lint/baseline_2026-04-24.txt. These suppress
        # non-exception-handling warnings (config/typing/mutation/path) and
        # therefore do NOT map to any existing _GUARDIAN_MAP edge_kind —
        # extending the edge_kind taxonomy is a separate ADG-scanner change
        # deferred to a follow-up wave. Until then, these tokens are
        # recognized as canonical (not flagged as non-canonical) but are not
        # wired into has_guardian_for_violation for any specific edge_kind.
        "allow-magic-config",  # 454 uses — hardcoded-literal-where-SSOT-expected
        "allow-type-erasure",  # 356 uses — runtime cast discarded
        "allow-global-mutation",  # 152 uses — intentional module-level mutation
        "allow-path-string",  # 114 uses — str where Path expected (API-compat)
    }
)


def _read_lines_cached(filepath: str) -> list[str]:
    """Read file lines with caching to avoid repeated I/O for hot files."""
    if filepath not in _file_cache:
        try:
            _file_cache[filepath] = (
                Path(filepath)
                .read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
                .splitlines()
            )
        except OSError:
            _file_cache[filepath] = []
    return _file_cache[filepath]


def _extract_guardian_tokens(line: str) -> set[str]:
    """Extract canonical guardian allow tokens from a single source line.

    STRICT: Requires a non-empty ``-- <justification>`` segment after the
    token. A bare ``# guardian: allow-X`` is rejected — every guardian must
    document *why* the swallow is justified.

    Multiple ``# guardian:`` comments on one physical line are all parsed
    (common after P2 burndown adds a second token beside an existing one).
    """
    if "guardian:" not in line:
        return set()
    tokens: set[str] = set()
    marker = "guardian:"
    start = 0
    while True:
        idx = line.find(marker, start)
        if idx < 0:
            break
        payload = line[idx + len(marker) :]
        parts = payload.split()
        if parts:
            head = parts[0].strip().strip(",;()[]{}")
            if head.startswith("allow-") and head in _CANONICAL_GUARDIAN_TOKENS:
                tail = " ".join(parts[1:])
                if "--" in tail:
                    after_dashes = tail.split("--", 1)[1].strip()
                    if len(after_dashes) >= 3:
                        tokens.add(head)
        start = idx + len(marker)
    return tokens


def _resolve_except_anchor_lines(lines: list[str], line_no: int) -> set[int]:
    """Resolve canonical anchor lines for an exception handler site.

    STRICT: Only two anchors are valid:
      1. The ``except ... :`` header line itself
      2. For multi-line except headers, the line containing the closing ``:``

    Pre-except orphan comments and generic ±6-line windows are rejected so
    guardians can no longer 'leak' between adjacent except blocks.
    """
    if line_no < 1 or not lines:
        return set()

    max_idx = len(lines) - 1
    idx = min(max(line_no - 1, 0), max_idx)
    start = idx

    # Walk back at most 6 lines to find the 'except' keyword that owns this site
    for probe in range(idx, max(-1, idx - 6), -1):
        stripped = lines[probe].lstrip()
        if stripped.startswith("except"):
            start = probe
            break

    # Walk forward to find the ':' that closes the except header (multi-line)
    end = start
    for probe in range(start, min(len(lines), start + 6)):
        end = probe
        if ":" in lines[probe]:
            break

    # STRICT: anchors are ONLY the except line and the closing-paren line.
    # No +/- 1-line fallback, no pre-except comment line.
    anchors = {start + 1, end + 1}
    return {ln for ln in anchors if 1 <= ln <= len(lines)}


_NON_EXCEPT_EDGE_KINDS = frozenset(
    {
        "hallucinated_tool_name",
        "chokepoint_bypass",
        "missing_hitl_on_irreversible",
        "hardcoded_secret",
        "star_import_use",
        "star_import",
        "mutable_default_arg",
        # Violation row is the for/while header (evidence for_retry|while_retry), not except.
        "retry_without_backoff",
    }
)


def _resolve_inline_anchor_lines(lines: list[str], line_no: int) -> set[int]:
    """Anchor resolver for non-exception antipatterns.

    Allows the guardian comment on the violation line itself or the line
    immediately above it (common pattern for call-site annotations).
    """
    if line_no < 1 or not lines:
        return set()
    max_line = len(lines)
    return {ln for ln in (line_no - 1, line_no) if 1 <= ln <= max_line}


def has_guardian_for_violation(source_file: str, line_no: int, edge_kind: str) -> bool:
    """Canonical guardian matcher used across write-time, phase2, and phase3."""
    guardians = _GUARDIAN_MAP.get(edge_kind)
    if not guardians:
        return False

    lines = _read_lines_cached(source_file)
    if not lines:
        return False

    valid_tokens = {g.split("guardian:", 1)[1].strip() for g in guardians if "guardian:" in g}
    if edge_kind in _NON_EXCEPT_EDGE_KINDS:
        anchor_lines = _resolve_inline_anchor_lines(lines, line_no)
    else:
        anchor_lines = _resolve_except_anchor_lines(lines, line_no)
    for anchor_line in anchor_lines:
        tokens = _extract_guardian_tokens(lines[anchor_line - 1])
        if any(token in valid_tokens for token in tokens):
            return True
    return False


def _has_guardian_comment(
    source_file: str,
    line_no: int,
    guardian_strings: tuple[str, ...],
) -> bool:
    """Check if source line (±1 line) contains a matching guardian comment.

    Used by the layer-violation filter path. These are `import` (or `calls`)
    edges — NOT exception handlers — so the except-header anchor resolver
    never matches. The inline resolver (line_no itself + line above) is the
    correct window, consistent with the multi-line-import marker window used
    by ``tools.adg.core.guardian_filter.is_layer_violation_exempted``.
    Also supports the common pattern where the marker is on the closing ``)``
    of a multi-line ``from X import (...)`` block up to 4 lines after line_no.
    """
    lines = _read_lines_cached(source_file)
    if not lines or line_no < 1:
        return False
    valid_tokens = {g.split("guardian:", 1)[1].strip() for g in guardian_strings if "guardian:" in g}
    # Window: line_no - 1 .. line_no + 4 (inclusive), clamped to file bounds.
    # Covers: (1) single-line import, (2) line-above marker, (3) closing ")" of
    # a multi-line from-import block.
    start = max(1, line_no - 1)
    end = min(len(lines), line_no + 4)
    for anchor_line in range(start, end + 1):
        tokens = _extract_guardian_tokens(lines[anchor_line - 1])
        if any(token in valid_tokens for token in tokens):
            return True
    return False


def _filter_guardian_exempted_violations(conn: sqlite3.Connection) -> int:
    """Remove violations that have valid guardian exemption comments in source.

    Queries all antipattern and layer-violation rows, reads the source file
    at the violation line, and DELETEs rows whose surrounding context contains
    the matching ``# guardian: allow-<type>`` comment.

    Returns the number of exempted (deleted) violations.
    """
    _file_cache.clear()

    # Collect antipattern violations with edge_kind
    rows = conn.execute(
        "SELECT v.id, e.edge_kind, v.file_path, v.line_no "
        "FROM violations v JOIN edges e ON v.edge_id = e.id "
        "WHERE v.category = 'antipattern'",
    ).fetchall()

    exempt_ids: list[int] = []
    for vid, edge_kind, fpath, lno in rows:
        if has_guardian_for_violation(fpath, lno, edge_kind):
            exempt_ids.append(vid)

    # Collect layer-violation violations
    lv_rows = conn.execute(
        "SELECT v.id, v.file_path, v.line_no "
        "FROM violations v JOIN edges e ON v.edge_id = e.id "
        "WHERE e.relation_type = 'violates'",
    ).fetchall()
    for vid, fpath, lno in lv_rows:
        if _has_guardian_comment(fpath, lno, _LAYER_VIOLATION_GUARDIANS):
            exempt_ids.append(vid)

    # Batch delete
    if exempt_ids:
        # SQLite max variable limit is 999; batch if needed
        for i in range(0, len(exempt_ids), 900):
            batch = exempt_ids[i : i + 900]
            placeholders = ",".join("?" for _ in batch)
            conn.execute(
                f"DELETE FROM violations WHERE id IN ({placeholders})",
                batch,
            )

    # Store exemption count in meta for transparency
    conn.execute(
        "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
        ("guardian_exemptions", str(len(exempt_ids))),
    )

    _file_cache.clear()
    return len(exempt_ids)


def _write_sqlite(ng_full, db_path: Path) -> Path:
    """Backward-compatible delegate to the sole canonical SQLite writer."""
    # Local import avoids the existing ArtifactPaths -> guardian helper cycle.
    from agentic_core.adg.artifact.ArtifactPaths import (
        _write_sqlite as _canonical_write_sqlite,
    )

    return _canonical_write_sqlite(ng_full, db_path)

def _create_latest_symlinks(
    out_dir: Path,
    sqlite_path: Path,
    snap_path: Path,
    file_graph_path: Path,
    symbol_graph_path: Path,
    governance_graph_path: Path,
) -> None:
    """Create LATEST symlinks pointing to the newest timestamped artifacts.

    On Windows, creates copies instead of symlinks if symlink creation fails.
    """
    import shutil

    # review: Multiple exceptions (OSError, NotImplementedError) need specific handling
    symlink_map = {
        "adg_LATEST.sqlite": sqlite_path,
        "adg_LATEST_snapshot.json": snap_path,
        "adg_LATEST_file_graph.json": file_graph_path,
        "adg_LATEST_symbol_graph.json": symbol_graph_path,
        "adg_LATEST_governance_graph.json": governance_graph_path,
    }

    for link_name, target_path in tqdm(symlink_map.items(), desc="Processing", unit="item"):
        if not target_path.exists():
            continue

        link_path = out_dir / link_name

        # Remove existing symlink/file
        if link_path.exists() or link_path.is_symlink():
            link_path.unlink()

        # Try to create symlink, fall back to copy on Windows
        try:
            link_path.symlink_to(target_path.name)
        except (
            OSError,
            NotImplementedError,
        ):  # guardian: allow-silent-swallow - acceptable exception handling
            # Windows without admin rights or filesystem doesn't support symlinks
            shutil.copy2(target_path, link_path)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


@dataclass
class ArtifactPaths:
    """Paths of all artifacts written by write_all_artifacts.

    Non-redundant output set (5 files, 100% edge coverage):
        snapshot          - Tier 1: metrics only (~50 KB)
        sqlite            - Tier 2: primary queryable store (~38 MB, all 18 edge types)
        file_graph        - imports, exports, dead_imports, covers, influences, in_cycle
        symbol_graph      - calls, implements, reads_from, writes_to, instantiates, ...
        governance_graph  - violates, antipattern, generates_prompt, ...
    """

    snapshot: Path
    sqlite: Path
    file_graph: Path
    symbol_graph: Path
    governance_graph: Path

    def size_report(self) -> dict[str, str]:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ArtifactPaths.size_report")

        result = {}
        for name, path in tqdm(
            (
                ("snapshot", self.snapshot),
                ("sqlite", self.sqlite),
                ("file_graph", self.file_graph),
                ("symbol_graph", self.symbol_graph),
                ("governance_graph", self.governance_graph),
            ),
            desc="Processing",
            unit="item",
        ):
            if path.exists():
                sz = path.stat().st_size
                result[name] = f"{sz / 1024:.0f} KB" if sz < 1_048_576 else f"{sz / 1_048_576:.1f} MB"
            else:
                result[name] = "missing"
        return result


def write_all_artifacts(
    artifact: ADGArtifact,
    out_dir: Path,
    *,
    ts: str = "",
    write_split_planes: bool = True,
    write_sqlite: bool = True,
    create_latest_symlinks: bool = False,
) -> ArtifactPaths:
    """Compatibility wrapper delegating to canonical ArtifactPaths writer."""
    from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts as _canonical_write_all_artifacts

    return cast(
        ArtifactPaths,
        _canonical_write_all_artifacts(
            artifact,
            out_dir=out_dir,
            ts=ts,
            write_split_planes=write_split_planes,
            write_sqlite=write_sqlite,
            create_latest_symlinks=create_latest_symlinks,
        ),
    )


__all__ = [
    "ArtifactPaths",
    "write_all_artifacts",
]
