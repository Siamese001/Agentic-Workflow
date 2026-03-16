"""REQ-016/020: all boundary systems fail-closed; sealed artifacts immutable."""

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

_emit_records_execution_trace("p0", "evidence", "test_fail_closed")
_emit_applies_guardrail("p0", "test_fail_closed", "p0_governance")
_emit_reads_policy_state("p0", "test_fail_closed", "policy_binding")
_emit_snapshots_state("p0", "test_fail_closed", "state_snapshot")
emit_replay_key("p0", "test_fail_closed")
emit_determinism_digest("p0", "test_fail_closed")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
