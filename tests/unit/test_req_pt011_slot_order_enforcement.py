"""REQ-PT-011: Negative control — tampered slot order must yield detection.

Production enforcement: validate_slot_order() in slot_contracts.py.
Wired into PromptAssembler.assemble() as fail-closed gate.

Positive tests: canonical order passes.
Negative tests: tampered/missing slots raise SlotOrderViolation.
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_req_pt011_slot_order_enforcement")
_emit_applies_guardrail("p0", "test_req_pt011_slot_order_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "test_req_pt011_slot_order_enforcement", "policy_binding")
_emit_snapshots_state("p0", "test_req_pt011_slot_order_enforcement", "state_snapshot")
emit_replay_key("p0", "test_req_pt011_slot_order_enforcement")
emit_determinism_digest("p0", "test_req_pt011_slot_order_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


# ---------------------------------------------------------------------------
# Positive: canonical slot order passes validation
# ---------------------------------------------------------------------------


def test_canonical_slot_order_passes():
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        validate_slot_order,
    )

    prompt = (
        "<SLOT_S0>system</SLOT_S0>\n"
        "<SLOT_D0>directives</SLOT_D0>\n"
        "<SLOT_I0>instructional</SLOT_I0>\n"
        "<SLOT_C0>context</SLOT_C0>\n"
        "<SLOT_U0>user</SLOT_U0>\n"
    )
    validate_slot_order(prompt)  # should not raise


def test_canonical_order_with_extra_content_passes():
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        validate_slot_order,
    )

    prompt = (
        "PREAMBLE\n"
        "<SLOT_S0>You are {role}.</SLOT_S0>\n"
        "--- separator ---\n"
        "<SLOT_D0>binding directives</SLOT_D0>\n"
        "<SLOT_I0>capability defs</SLOT_I0>\n"
        "<SLOT_C0>rag payload</SLOT_C0>\n"
        "<SLOT_U0>raw user intent</SLOT_U0>\n"
        "<OUTPUT_FORMAT>json</OUTPUT_FORMAT>\n"
    )
    validate_slot_order(prompt)  # should not raise


# ---------------------------------------------------------------------------
# Negative: tampered slot order raises SlotOrderViolation
# ---------------------------------------------------------------------------


def test_swapped_s0_d0_raises():
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        SlotOrderViolation,
        validate_slot_order,
    )

    prompt = (
        "<SLOT_D0>directives</SLOT_D0>\n"
        "<SLOT_S0>system</SLOT_S0>\n"
        "<SLOT_I0>instructional</SLOT_I0>\n"
        "<SLOT_C0>context</SLOT_C0>\n"
        "<SLOT_U0>user</SLOT_U0>\n"
    )
    with pytest.raises(SlotOrderViolation, match="SLOT_ORDER_VIOLATED"):
        validate_slot_order(prompt)


def test_u0_before_c0_raises():
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        SlotOrderViolation,
        validate_slot_order,
    )

    prompt = (
        "<SLOT_S0>system</SLOT_S0>\n"
        "<SLOT_D0>directives</SLOT_D0>\n"
        "<SLOT_I0>instructional</SLOT_I0>\n"
        "<SLOT_U0>user</SLOT_U0>\n"
        "<SLOT_C0>context</SLOT_C0>\n"
    )
    with pytest.raises(SlotOrderViolation, match="SLOT_ORDER_VIOLATED"):
        validate_slot_order(prompt)


def test_missing_slot_raises():
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        SlotOrderViolation,
        validate_slot_order,
    )

    prompt = (
        "<SLOT_S0>system</SLOT_S0>\n"
        "<SLOT_D0>directives</SLOT_D0>\n"
        "<SLOT_C0>context</SLOT_C0>\n"
        "<SLOT_U0>user</SLOT_U0>\n"
    )
    with pytest.raises(SlotOrderViolation, match="SLOT_MISSING.*I0"):
        validate_slot_order(prompt)


def test_empty_prompt_raises():
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        SlotOrderViolation,
        validate_slot_order,
    )

    with pytest.raises(SlotOrderViolation, match="SLOT_MISSING"):
        validate_slot_order("")


# ---------------------------------------------------------------------------
# SlotOrderViolation is a proper exception type
# ---------------------------------------------------------------------------


def test_slot_order_violation_is_exception():
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        SlotOrderViolation,
    )

    assert issubclass(SlotOrderViolation, Exception)


def test_slot_order_violation_carries_message():
    from agentic_core.prompt_governance.contracts.slot_contracts import (
        SlotOrderViolation,
    )

    err = SlotOrderViolation("tamper detected")
    assert "tamper detected" in str(err)
