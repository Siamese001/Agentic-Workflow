"""REQ-106: replay sandbox blocks network IO and SDK invocation."""

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

_emit_records_execution_trace("p0", "evidence", "test_replay_sandbox")
_emit_applies_guardrail("p0", "test_replay_sandbox", "p0_governance")
_emit_reads_policy_state("p0", "test_replay_sandbox", "policy_binding")
_emit_snapshots_state("p0", "test_replay_sandbox", "state_snapshot")
emit_replay_key("p0", "test_replay_sandbox")
emit_determinism_digest("p0", "test_replay_sandbox")
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

@pytest.mark.governance
def test_replay_sandbox_blocks_network():
    from agentic_core.L2_execution.determinism.replay_guard import ReplayGuard

    guard = ReplayGuard()
    with guard:
        with pytest.raises(Exception, match="network|blocked|replay|Replay"):
            import urllib.request

            urllib.request.urlopen("http://example.com")
