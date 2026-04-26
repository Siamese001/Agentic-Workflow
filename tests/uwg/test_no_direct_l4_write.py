"""UWG anti-bypass / no-direct-l4-write tests.

Doctrine: ``docs/reference/00_L4_State_and_UWG/00.8_*`` §PHASE 3 anti-bypass matrix.

This suite enforces the constitutional invariant that EVERY non-UWG surface
attempting a direct L4 mutation is recorded as a blocked attempt with a
receipt and an ``l4.direct_write_attempt.blocked`` span.

Surfaces tested (per parent doctrine §"Hard Write Law"):
- L0, L1, L2, L3, L5, L6
- C0, PromptAssembly
- HITL
- Tool, Model, Connector
- PTC_Sandbox
- BackgroundEvaluator, AdHocScript
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.otel.spans import get_emitted_spans
from agentic_core.L4_state.uwg.durable_write_gateway import (
    NON_AUTHORIZED_SOURCES,
    DurableWriteGateway,
)


@pytest.mark.parametrize(
    "surface",
    sorted(NON_AUTHORIZED_SOURCES),
)
def test_direct_write_from_non_authorized_surface_blocked(surface: str) -> None:
    """Per 00.8 §PHASE 3: every non-UWG surface direct write must produce a block receipt."""
    gateway = DurableWriteGateway()
    receipt = gateway.reject_direct_write(
        attempting_surface=surface,
        target_surface="memory",
        reason=f"direct_write_attempt_from_{surface}",
        request_id="req:1",
        run_id="run:1",
    )
    assert receipt.no_mutation_assertion == "NO_MUTATION_APPLIED"
    assert "non_uwg_surface_blocked" in receipt.blocked_reason_codes
    assert "UWG_AUTHORITY_REQUIRED" in receipt.failed_rule_ids
    assert receipt.audit_append_receipt_ref


def test_blocked_attempts_recorded_in_audit_ledger() -> None:
    gateway = DurableWriteGateway()
    gateway.reject_direct_write(
        attempting_surface="L6",
        target_surface="memory",
        reason="L6_attempted_direct_memory_write",
    )
    records = gateway.audit_ledger.read()
    assert len(records) == 1
    assert records[0].event_type == "direct_write_attempt_blocked"
    assert records[0].actor_surface == "L6"


def test_blocked_attempts_emit_blocked_span() -> None:
    gateway = DurableWriteGateway()
    gateway.reject_direct_write(
        attempting_surface="PTC_Sandbox",
        target_surface="cache",
        reason="PTC_attempted_direct_cache_promotion",
    )
    spans = get_emitted_spans(name_prefix="l4.direct_write_attempt")
    assert any(s.name == "l4.direct_write_attempt.blocked" for s in spans)
    blocked = [s for s in spans if s.name == "l4.direct_write_attempt.blocked"][0]
    assert blocked.attributes["source_surface"] == "PTC_Sandbox"
    assert blocked.attributes["state_surface"] == "cache"


def test_list_direct_write_blocks_aggregates_history() -> None:
    gateway = DurableWriteGateway()
    for surface in ("L2", "L6", "HITL"):
        gateway.reject_direct_write(
            attempting_surface=surface,
            target_surface="memory",
            reason=f"{surface}_test",
        )
    history = gateway.list_direct_write_blocks()
    assert len(history) == 3
    actors_in_audit = {r.actor_surface for r in gateway.audit_ledger.read()}
    assert {"L2", "L6", "HITL"} <= actors_in_audit


def test_non_authorized_sources_includes_all_required_surfaces() -> None:
    """The constitutional surface list must include every surface listed in 00_*."""
    must_include = {
        "L0",
        "L1",
        "L2",
        "L3",
        "L5",
        "L6",
        "C0",
        "PromptAssembly",
        "HITL",
        "Tool",
        "Model",
        "Connector",
        "PTC_Sandbox",
        "BackgroundEvaluator",
        "AdHocScript",
    }
    assert must_include <= NON_AUTHORIZED_SOURCES
    assert "Exit" not in NON_AUTHORIZED_SOURCES  # Exit is the SOLE authorized commit source
    assert "UWG" not in NON_AUTHORIZED_SOURCES  # UWG is the SOLE authorized writer
