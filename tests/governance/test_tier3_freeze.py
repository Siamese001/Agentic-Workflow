"""REQ-091: Tier III freeze disables all 5 subsystems."""

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
def test_tier3_freeze_disables_write_gateway():
    from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway

    uwg = UniversalWriteGateway()
    uwg.freeze()
    with pytest.raises(Exception, match="frozen|freeze"):
        uwg.write(payload=b"x", signature="sig", store=None)


@pytest.mark.governance
def test_tier3_freeze_halts_token_issuance():
    from agentic_core.L2_execution.enforcement.capability_chokepoint import CapabilityChokepoint

    cp = CapabilityChokepoint()
    cp.freeze()
    with pytest.raises(Exception, match="frozen|freeze"):
        cp.issue_token(scope="read", trace_id="CC3AL1-00000001")
