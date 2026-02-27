"""REQ-106: replay sandbox blocks network IO and SDK invocation."""

from __future__ import annotations

import pytest


@pytest.mark.governance
def test_replay_sandbox_blocks_network():
    from agentic_core.L2_execution.determinism.replay_guard import ReplayGuard

    guard = ReplayGuard()
    with guard:
        with pytest.raises(Exception, match="network|blocked|replay|Replay"):
            import urllib.request

            urllib.request.urlopen("http://example.com")
