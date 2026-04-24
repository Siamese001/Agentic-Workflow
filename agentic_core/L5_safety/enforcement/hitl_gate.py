"""HitlGate — Human-In-The-Loop enforcement for destructive healing operations.

SSOT for all HITL decisions across the healing pipeline.

Core contract (non-negotiable)
-------------------------------
HITL is MANDATORY.  Every destructive operation — archive, delete, move —
must stop and wait for an explicit human choice before proceeding.

There is no "non-interactive bypass", no "CI skip", no silent auto-approve
for destructive ops.  If there is no TTY, the operation raises
HitlRequiredError and the healing run aborts.  The human is always present.

Rules
-----
1. Any destructive op (protected OR non-protected):
   - Interactive TTY → prompt with labelled options [Y/N/S/A]
   - No TTY          → raise HitlRequiredError (hard abort)
2. SOVEREIGN_AUTO_APPROVE / ARCHIVE_BATCH_ACCEPT are IGNORED entirely.
   They exist in the environment for other subsystems; this gate does not
   honour them.  The human must type a choice.
3. Prompt always shows: agent, operation, territory, reason, full file list.
4. Options always shown: [Y] Yes / [N] No / [S] Skip / [A] Abort
   — never a bare y/n.
"""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Sequence

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

emit_replay_key("p0", "hitl_gate")
emit_determinism_digest("p0", "hitl_gate")

_emit_dispatches_healing_run("p1", "hitl_gate", "L5")
_emit_routes_through("p1", "hitl_gate", "L5")
_emit_checks_agent_registry("p1", "hitl_gate", "agent_registry")
_emit_validates_agent_capability("p1", "hitl_gate", "capability")
_emit_dispatches_execution_plan("p1", "hitl_gate", "exec_plan")
_emit_agent_executes_agent("p1", "hitl_gate", "sub_agent")
_emit_routes_to_agent("p1", "hitl_gate", "target_agent")
_emit_verifies_policy("p1", "hitl_gate", "policy_check")
_emit_observes_runtime_state("p1", "hitl_gate", "runtime_state")
_emit_verifies_boundary("p1", "hitl_gate", "boundary_check")
_emit_transcripts_response("p1", "hitl_gate", "transcript")
_emit_hard_fails_untranscripted("p1", "hitl_gate")
_emit_gated_by_confidence("p1", "hitl_gate", "confidence_gate")
_emit_escalates_to_human("p1", "hitl_gate", "L5")
_emit_reads_policy_state("p1", "hitl_gate", "L5")

_emit_applies_guardrail("p0", "hitl_gate", "p0_governance")
_emit_snapshots_state("p0", "hitl_gate", "state_snapshot")
_emit_authorize_and_execute("p2", "hitl_gate", "execution_auth")
_emit_validates_capability("p2", "hitl_gate", "capability_check")
_emit_routes_to_capability("p2", "hitl_gate", "capability_route")
_emit_writes_via_uwg("p2", "hitl_gate", "uwg_write")
_emit_blocks_direct_write("p2", "hitl_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "hitl_gate", "tool_invocation")
_emit_captures_execution_output("p2", "hitl_gate", "exec_output")
_emit_dispatches_agent("p3", "hitl_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "hitl_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "hitl_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "hitl_gate", "healing_outcome")
_emit_escalates_failure("p3", "hitl_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "hitl_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hitl_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "hitl_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "hitl_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hitl_gate", "eval_metric")
_emit_stores_embedding("p4", "hitl_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "hitl_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hitl_gate", "exec_snapshot_link")
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

_emit_emits_metric_event("hitl_gate", "p4obs", "metric_1")
_emit_emits_metric_event("hitl_gate", "p4obs", "metric_2")
_emit_emits_metric_event("hitl_gate", "p4obs", "metric_3")
_emit_emits_metric_event("hitl_gate", "p4obs", "metric_4")
_emit_emits_metric_event("hitl_gate", "p4obs", "metric_5")
_emit_emits_metric_event("hitl_gate", "p4obs", "metric_6")
_emit_records_incident_event("hitl_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("hitl_gate", "p4obs", "anomaly")
_emit_writes_observability_log("hitl_gate", "p4obs", "obs_log")
_emit_updates_monitoring_state("hitl_gate", "p4obs", "mon_state")
_emit_triggers_alert("hitl_gate", "p4obs", "alert")
_emit_links_incident_trace("hitl_gate", "p4obs", "trace_link")
_emit_captures_pattern("hitl_gate", "p3lm", "pattern")
_emit_records_learning_event("hitl_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hitl_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("hitl_gate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hitl_gate", "p3lm", "routing")
_emit_improves_agent_policy("hitl_gate", "p3lm", "policy")
_emit_stores_learning_state("hitl_gate", "p3lm", "state")
_emit_records_execution_trace("hitl_gate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hitl_gate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hitl_gate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hitl_gate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hitl_gate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hitl_gate", "env_read", "p2_env_1")
_emit_reads_environ("hitl_gate", "env_read", "p2_env_2")
_emit_reads_runtime_state("hitl_gate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hitl_gate", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hitl_gate", "context_pull")
_emit_pulls_context("p1", "hitl_gate", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hitl_gate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hitl_gate", "uwg_term_2")
_emit_writes_through("p1", "hitl_gate", "write_through")
_emit_writes_through("p1", "hitl_gate", "write_through_2")
_emit_validated_by_safety_plane("p1", "hitl_gate", "safety_validation")
_emit_invokes_eval("p1", "hitl_gate", "eval_call")
_emit_proposal_commits_routing("p1", "hitl_gate", "routing_commit")

Logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# HITL_PROTECTED_PATHS
# Directories whose files MUST NOT be destroyed without explicit user consent.
# Checked against the *first component* of a file's path relative to repo root.
# ---------------------------------------------------------------------------
HITL_PROTECTED_PATHS: frozenset[str] = frozenset(
    {
        "agentic_core",
        "scripts",
        "mixins",
        "runtime",
        "ops_scripts",
        "apps_rg",
        "apps_lic",
        "apps_shared",
        "tests",
        "system_learning",
    },
)

_BORDER = "=" * 64


class HitlChoice(str, Enum):
    YES = "Y"  # approve this batch
    NO = "N"  # deny this batch, abort the operation
    SKIP = "S"  # skip this item (no changes made)
    ABORT = "A"  # abort entire healing run


@dataclass
class HitlDecision:
    choice: HitlChoice
    reason: str
    protected: bool = False
    batch_count: int = 0


@dataclass
class HitlRequest:
    agent: str
    operation: str  # e.g. "ARCHIVE", "DELETE", "MOVE"
    affected_paths: Sequence[Path]
    reason: str
    territory: str = ""
    extra_context: str = ""


class HitlRequiredError(RuntimeError):
    """Raised when a destructive operation is attempted with no TTY available.

    This is a hard abort.  The healing run must stop.  The human must be
    present to approve destructive operations — there is no automated bypass.
    """


def _is_protected(paths: Sequence[Path], repo_root: Path) -> bool:
    """Return True if any path's first component is in HITL_PROTECTED_PATHS."""
    for p in paths:
        try:
            rel = p.relative_to(repo_root)
            if rel.parts and rel.parts[0] in HITL_PROTECTED_PATHS:
                return True
        except ValueError:  # guardian: allow-silent-swallow -- relative_to ValueError: non-fatal, path excluded
            pass
    return False


# guardian: allow-magic-config
def _format_paths(paths: Sequence[Path], limit: int = 20) -> str:
    shown = list(paths)[:limit]
    lines = [f"  • {p}" for p in shown]
    if len(paths) > limit:
        lines.append(f"  ... and {len(paths) - limit} more")
    return "\n".join(lines)


class HitlGate:
    """Central HITL gate.  Use HitlGate.request() for all destructive ops.

    Injection point for tests: pass ``input_fn`` to override stdin reading.
    Set ``_tty_override=True`` in tests to simulate an interactive terminal.
    """

    def __init__(
        self,
        repo_root: Path,
        *,
        input_fn: Callable[[str], str] | None = None,
        _tty_override: bool = False,
    ) -> None:
        self._repo_root = repo_root
        self._input_fn: Callable[[str], str] = input_fn or input
        self._tty_override = _tty_override

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def request(self, req: HitlRequest) -> HitlDecision:
        """Evaluate a destructive operation request and return a decision.

        HITL is mandatory — always prompts when a TTY is present.
        Raises HitlRequiredError when no TTY is available (no silent skip).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "HitlGate.request")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HitlGate.request".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        protected = _is_protected(req.affected_paths, self._repo_root)
        interactive = self._tty_override or sys.stdin.isatty()

        if not interactive:
            msg = (
                f"[HitlGate] HITL REQUIRED — cannot proceed without human approval.\n"
                f"  Agent    : {req.agent}\n"
                f"  Operation: {req.operation}\n"
                f"  Reason   : {req.reason}\n"
                f"  Paths    : {len(req.affected_paths)} file(s)\n"
                f"  Protected: {protected}\n"
                f"No TTY detected.  Run this command interactively so you can "
                f"approve or deny the operation."
            )
            Logger.error(
                "[HitlGate] No TTY — raising HitlRequiredError for %s / %s",
                req.agent,
                req.operation,
            )
            raise HitlRequiredError(msg)

        return self._prompt(req, protected=protected)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _prompt(self, req: HitlRequest, *, protected: bool) -> HitlDecision:
        label = "⚠  PROTECTED PATH" if protected else "ℹ  STANDARD PATH"
        print(f"\n{_BORDER}")
        print(f"  HITL GATE  [{req.operation}]  {label}")
        print(_BORDER)
        print(f"  Agent     : {req.agent}")
        if req.territory:
            print(f"  Territory : {req.territory}")
        print(f"  Reason    : {req.reason[:120]}")
        if req.extra_context:
            print(f"  Context   : {req.extra_context[:120]}")
        print(f"\n  Files affected ({len(req.affected_paths)}):")
        print(_format_paths(req.affected_paths))
        print(_BORDER)
        print("  [Y] Yes   — approve this batch")
        print("  [N] No    — deny and abort this operation")
        print("  [S] Skip  — skip (no changes made)")
        print("  [A] Abort — abort entire healing run")
        print(_BORDER)
        try:
            raw = self._input_fn("  Choice [Y/N/S/A]: ").strip().upper()
        except (
            EOFError,
            KeyboardInterrupt,
        ):  # review: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling
            raw = "N"

        choice_map = {
            "Y": HitlChoice.YES,
            "N": HitlChoice.NO,
            "S": HitlChoice.SKIP,
            "A": HitlChoice.ABORT,
        }
        choice = choice_map.get(raw, HitlChoice.NO)
        reason = f"User chose {choice.value} for {req.operation} on {len(req.affected_paths)} path(s)"
        Logger.info("[HitlGate] %s | agent=%s protected=%s", reason, req.agent, protected)
        return HitlDecision(
            choice=choice,
            reason=reason,
            protected=protected,
            batch_count=len(req.affected_paths),
        )


# ---------------------------------------------------------------------------
# Module-level convenience singleton (lazy, per repo_root)
# ---------------------------------------------------------------------------
_gates: dict[Path, HitlGate] = {}


def get_hitl_gate(
    repo_root: Path,
    *,
    input_fn: Callable[[str], str] | None = None,
    _tty_override: bool = False,
) -> HitlGate:
    """Return a cached HitlGate for repo_root (or build a new one)."""
    if repo_root not in _gates:
        _gates[repo_root] = HitlGate(
            repo_root,
            input_fn=input_fn,
            _tty_override=_tty_override,
        )
    return _gates[repo_root]


def clear_gate_cache() -> None:
    """Clear singleton cache (for tests)."""
    _gates.clear()


def prompt_for_hitl(
    operation: str,
    agent: str,
    affected_paths: Sequence[Path],
    reason: str,
    territory: str = "",
    extra_context: str = "",
    *,
    input_fn: Callable[[str], str] | None = None,
) -> HitlDecision:
    """Convenience function for HITL prompt (module-level API).

    Args:
        operation: Operation type (e.g., "ARCHIVE", "DELETE", "MOVE")
        agent: Agent name requesting HITL
        affected_paths: List of paths affected by operation
        reason: Reason for the operation
        territory: Optional territory context
        extra_context: Optional extra context
        input_fn: Optional input function override (for testing)

    Returns:
        HitlDecision with user's choice
    """
    from pathlib import Path

    repo_root = Path.cwd()
    gate = get_hitl_gate(repo_root, input_fn=input_fn)
    req = HitlRequest(
        agent=agent,
        operation=operation,
        affected_paths=affected_paths,
        reason=reason,
        territory=territory,
        extra_context=extra_context,
    )
    return gate.request(req)
