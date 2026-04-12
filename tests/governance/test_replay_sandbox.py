"""REQ-106: replay sandbox blocks network IO and SDK invocation."""

from __future__ import annotations

import pytest


@pytest.mark.governance
def test_replay_sandbox_blocks_network():

    with guard:
        with pytest.raises(Exception, match="network|blocked|replay|Replay"):
            pass
