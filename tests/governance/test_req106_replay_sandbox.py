"""REQ-106: replay sandbox blocks network IO and SDK invocation."""

from __future__ import annotations

import pytest


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
