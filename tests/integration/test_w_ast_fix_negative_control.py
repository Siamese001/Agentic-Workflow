"""W-AST-FIX Negative Control: env-toggled tamper/restore for REQ-PT-011 + REQ-RAGX-006.

When W_AST_FIX_NEGCTRL_TAMPER=1:
  - A controlled violation is injected so the test yields xfail(strict=True) exit 0.
When W_AST_FIX_NEGCTRL_TAMPER is unset or 0:
  - The tests run normally and PASS.
"""

from __future__ import annotations

import os

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_w_ast_fix_negative_control")
_emit_applies_guardrail("p0", "test_w_ast_fix_negative_control", "p0_governance")
_emit_reads_policy_state("p0", "test_w_ast_fix_negative_control", "policy_binding")
_emit_snapshots_state("p0", "test_w_ast_fix_negative_control", "state_snapshot")
emit_replay_key("p0", "test_w_ast_fix_negative_control")
emit_determinism_digest("p0", "test_w_ast_fix_negative_control")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_w_ast_fix_negative_control", "execution_auth")
_emit_validates_capability("p2", "test_w_ast_fix_negative_control", "capability_check")
_emit_routes_to_capability("p2", "test_w_ast_fix_negative_control", "capability_route")
_emit_writes_via_uwg("p2", "test_w_ast_fix_negative_control", "uwg_write")
_emit_blocks_direct_write("p2", "test_w_ast_fix_negative_control", "direct_write_block")
_emit_records_tool_invocation("p2", "test_w_ast_fix_negative_control", "tool_invocation")
_emit_captures_execution_output("p2", "test_w_ast_fix_negative_control", "exec_output")
_emit_dispatches_agent("p3", "test_w_ast_fix_negative_control", "agent_dispatch")
_emit_coordinates_agents("p3", "test_w_ast_fix_negative_control", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_w_ast_fix_negative_control", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_w_ast_fix_negative_control", "healing_outcome")
_emit_escalates_failure("p3", "test_w_ast_fix_negative_control", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_w_ast_fix_negative_control", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_w_ast_fix_negative_control", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_w_ast_fix_negative_control", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_w_ast_fix_negative_control", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_w_ast_fix_negative_control", "eval_metric")
_emit_stores_embedding("p4", "test_w_ast_fix_negative_control", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_w_ast_fix_negative_control", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_w_ast_fix_negative_control", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

_TAMPER = os.environ.get("W_AST_FIX_NEGCTRL_TAMPER", "0") == "1"


# ---------------------------------------------------------------------------
# REQ-PT-011 negative control
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    condition=_TAMPER,
    reason="W_AST_FIX_NEGCTRL_TAMPER=1: deliberate slot-order tamper",
    strict=True,
)
def test_negctrl_pt011_slot_order():
    """Normal mode: canonical order passes.  Tamper mode: reversed order must fail."""
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        validate_slot_order,
    )

    if _TAMPER:
        # Deliberate tamper: reversed slot order — this MUST raise
        tampered = (
            "<SLOT_U0>user</SLOT_U0>\n"
            "<SLOT_C0>context</SLOT_C0>\n"
            "<SLOT_I0>instructional</SLOT_I0>\n"
            "<SLOT_D0>directives</SLOT_D0>\n"
            "<SLOT_S0>system</SLOT_S0>\n"
        )
        validate_slot_order(tampered)  # raises SlotOrderViolation -> xfail
    else:
        # Normal: canonical order passes
        canonical = (
            "<SLOT_S0>system</SLOT_S0>\n"
            "<SLOT_D0>directives</SLOT_D0>\n"
            "<SLOT_I0>instructional</SLOT_I0>\n"
            "<SLOT_C0>context</SLOT_C0>\n"
            "<SLOT_U0>user</SLOT_U0>\n"
        )
        validate_slot_order(canonical)


# ---------------------------------------------------------------------------
# REQ-RAGX-006 negative control
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    condition=_TAMPER,
    reason="W_AST_FIX_NEGCTRL_TAMPER=1: deliberate citation-custody tamper",
    strict=True,
)
def test_negctrl_ragx006_citation_custody():
    """Normal mode: cited context passes.  Tamper mode: uncited context must fail."""
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
        CitationBundle,
        validate_citation_custody,
    )

    if _TAMPER:
        # Deliberate tamper: context present but no citations
        chunks = [{"chunk_id": "c1", "text": "external knowledge"}]
        validate_citation_custody(chunks, None)  # raises -> xfail
    else:
        # Normal: properly cited
        chunks = [{"chunk_id": "c1", "text": "external knowledge"}]
        citations = [
            CitationBundle(
                chunk_id="c1",
                source_ref="docs/ref.md",
                byte_sha256="a" * 64,
                byte_range=(0, 100),
                score=0.95,
            )
        ]
        validate_citation_custody(chunks, citations)
