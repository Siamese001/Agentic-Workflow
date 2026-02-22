"""
Unit tests for apps_lic/engines/lic_spine_adapter.py

Proves:
  a) Adapter returns a cid string in the result.
  b) CID is created BEFORE the orchestrator execute() is invoked.
  c) GovernedPayload is constructed with the correct type and key fields.
  d) No randomness, no wall-clock, no network.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit_min_deps


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_adapter():
    from apps_lic.engines.lic_spine_adapter import LicSpineAdapter

    return LicSpineAdapter()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_adapter_returns_cid():
    """Adapter result must contain a non-empty 'cid' string."""
    adapter = _make_adapter()
    result = adapter.execute({"u0_user_prompt": "test intent"})
    assert "cid" in result
    assert isinstance(result["cid"], str)
    assert len(result["cid"]) > 0


def test_cid_has_lic_prefix():
    """CID must be derived deterministically and carry the 'lic-' prefix."""
    adapter = _make_adapter()
    result = adapter.execute({"u0_user_prompt": "test intent"})
    assert result["cid"].startswith("lic-")


def test_cid_is_deterministic():
    """Same input must always produce the same CID (no randomness)."""
    adapter = _make_adapter()
    intent = {"u0_user_prompt": "deterministic input", "s0_system": "sys"}
    r1 = adapter.execute(intent)
    r2 = adapter.execute(intent)
    assert r1["cid"] == r2["cid"]


def test_different_inputs_produce_different_cids():
    """Different payloads must produce different CIDs."""
    adapter = _make_adapter()
    r1 = adapter.execute({"u0_user_prompt": "input A"})
    r2 = adapter.execute({"u0_user_prompt": "input B"})
    assert r1["cid"] != r2["cid"]


def test_cid_registered_before_orchestrator_execute(monkeypatch):
    """CID must be registered in CIDRegistry before orchestrator.execute() is called."""
    from agentic_core.L2_execution.cid_registry import CIDRegistry
    from apps_lic.engines.lic_spine_adapter import LicSpineAdapter

    call_log: list[str] = []

    # Patch CIDRegistry.new_cycle to record when it is called.
    original_new_cycle = CIDRegistry.new_cycle

    def recording_new_cycle(self, cid: str):
        call_log.append(("new_cycle", cid))
        return original_new_cycle(self, cid)

    monkeypatch.setattr(CIDRegistry, "new_cycle", recording_new_cycle)

    # Patch ExecutionOrchestrator.execute to record when it is called.
    from agentic_core.L0_routing.engines.execution_orchestrator import ExecutionOrchestrator

    original_execute = ExecutionOrchestrator.execute

    def recording_execute(self, intent_input):
        call_log.append(("orchestrator_execute",))
        return original_execute(self, intent_input)

    monkeypatch.setattr(ExecutionOrchestrator, "execute", recording_execute)

    adapter = LicSpineAdapter()
    adapter.execute({"u0_user_prompt": "ordering test"})

    # new_cycle must appear before orchestrator_execute in the log.
    new_cycle_idx = next(i for i, e in enumerate(call_log) if e[0] == "new_cycle")
    orchestrator_idx = next(i for i, e in enumerate(call_log) if e[0] == "orchestrator_execute")
    assert new_cycle_idx < orchestrator_idx, (
        f"CID must be registered before orchestrator.execute(); "
        f"new_cycle at {new_cycle_idx}, orchestrator at {orchestrator_idx}"
    )


def test_cid_passed_to_orchestrator(monkeypatch):
    """The enriched intent_input passed to orchestrator must contain '_cid'."""
    from agentic_core.L0_routing.engines.execution_orchestrator import ExecutionOrchestrator
    from apps_lic.engines.lic_spine_adapter import LicSpineAdapter

    received_inputs: list[dict] = []

    original_execute = ExecutionOrchestrator.execute

    def capturing_execute(self, intent_input):
        received_inputs.append(dict(intent_input))
        return original_execute(self, intent_input)

    monkeypatch.setattr(ExecutionOrchestrator, "execute", capturing_execute)

    adapter = LicSpineAdapter()
    result = adapter.execute({"u0_user_prompt": "cid threading test"})

    assert len(received_inputs) == 1
    assert "_cid" in received_inputs[0]
    assert received_inputs[0]["_cid"] == result["cid"]


def test_governed_payload_constructed():
    """GovernedPayload must be constructed with the correct type and manifest_hash."""
    from agentic_core.L0_routing.engines.assembly_stage import GovernedPayload
    from apps_lic.engines.lic_spine_adapter import _LicAssemblerAdapter

    assembler = _LicAssemblerAdapter()
    payload = assembler.assemble(
        {
            "s0_system": "system",
            "i0_instructional": "instruct",
            "c0_context": "ctx",
            "u0_user_prompt": "user",
        }
    )
    assert isinstance(payload, GovernedPayload)
    assert payload.s0_system == "system"
    assert payload.i0_instructional == "instruct"
    assert payload.c0_context == "ctx"
    assert payload.u0_user_prompt == "user"
    assert len(payload.manifest_hash) == 64  # SHA-256 hex


def test_adapter_state_success_on_clean_input():
    """Adapter must return state='success' for a clean, non-blocked input."""
    adapter = _make_adapter()
    result = adapter.execute({"u0_user_prompt": "clean input"})
    assert result["state"] == "success"
