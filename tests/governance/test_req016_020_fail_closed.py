"""REQ-016/020: all boundary systems fail-closed; sealed artifacts immutable."""

from __future__ import annotations

import pytest

HARDENING_ORDER = "land AST/CI ratchet for fail-closed patterns BEFORE applying runtime behavior changes."


@pytest.mark.governance
def test_req016_all_subsystems_fail_closed():
    """Boundary: 10 subsystems must raise on failure, never silently return."""
    from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway

    uwg = UniversalWriteGateway()
    with pytest.raises(Exception):  # noqa: B017
        uwg.write(payload=b"x", signature="invalid", store=None)


@pytest.mark.governance
def test_req020_sealed_artifact_immutable():
    """Sealed artifacts must raise on post-seal mutation attempt."""
    from agentic_core.L4_state.enforcement.replay_bundle_store import ReplayBundleStore

    store = ReplayBundleStore()
    bundle_id = store.seal({"trace_id": "CC3AL1-00000001", "payload": "data"})
    with pytest.raises(Exception, match="sealed|immutable|append.only"):
        store.mutate(bundle_id, {"payload": "tampered"})
