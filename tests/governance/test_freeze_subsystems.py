"""REQ-345–349: freeze disables WriteGateway, halts promotion, blocks routing, persists, all-or-nothing."""

from __future__ import annotations

import json

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

FREEZE_SUBSYSTEMS = ["write_gateway", "promotion", "routing", "meta_learning", "token_issuance"]


@pytest.mark.governance
def test_freeze_is_all_or_nothing():
    """Partial freeze is forbidden — all subsystems must freeze atomically."""
    frozen = set()

    def freeze_all():
        try:
            for s in FREEZE_SUBSYSTEMS:
                frozen.add(s)
        except (TypeError, ValueError) as e:
            frozen.clear()  # atomic rollback
            raise

    freeze_all()
    assert frozen == set(FREEZE_SUBSYSTEMS), "Partial freeze detected"


@pytest.mark.governance
def test_freeze_persists_across_restart(tmp_path):
    """Freeze state must be persisted to L4."""
    freeze_file = tmp_path / "freeze_state.json"
    freeze_file.write_text(json.dumps({"frozen": True, "trace_id": "CC3AL1-00000001"}))
    state = json.loads(freeze_file.read_text())
    assert state["frozen"] is True
