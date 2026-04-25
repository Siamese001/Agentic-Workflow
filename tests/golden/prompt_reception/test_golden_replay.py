"""Golden-replay harness for prompt-reception fixtures (phase RH5B.2).

Plan: prompt-reception-followups-a7b3c4.

Walks every ``fixtures/*.json`` file and asserts that the current
``PromptMessages`` projection still matches the recorded expectations.

Missing-fixture case (empty directory) is a warning, not a failure, so
this harness can be merged before every app has a recorded fixture.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L4_state.cache.replay_key import (
    SLOT_DIGEST_PREFIX,
    compute_slot_digest_key,
)
from tests.golden.prompt_reception._recorder import (
    FIXTURE_SCHEMA_VERSION,
    _build_artifact_and_slots,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _discover_fixtures() -> list[Path]:
    if not FIXTURES_DIR.exists():
        return []
    return sorted(FIXTURES_DIR.glob("*.json"))


@pytest.mark.parametrize(
    "fixture_path",
    _discover_fixtures(),
    ids=lambda p: p.stem if isinstance(p, Path) else str(p),
)
def test_golden_fixture_matches_current_projection(fixture_path: Path) -> None:
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert payload["fixture_schema_version"] == FIXTURE_SCHEMA_VERSION, (
        f"{fixture_path.name} has stale schema version; re-record via _recorder.record_fixture"
    )

    inputs = payload["inputs"]
    expected = payload["expected"]

    slots = {code: text for code, text in inputs["slots"]}
    artifact, slot_objs = _build_artifact_and_slots(slots)
    ir = artifact.to_prompt_messages(slots=slot_objs)

    assert list(artifact.slots_used) == expected["slots_used"]
    assert dict(ir.slot_map) == expected["slot_map"]
    assert list(ir.ordered_slots) == expected["ordered_slots"]

    replay_key = compute_slot_digest_key(ir)
    assert replay_key.startswith(expected["replay_key_prefix"])
    assert len(replay_key) - len(SLOT_DIGEST_PREFIX) == expected["replay_key_digest_length"]


def test_harness_imports_cleanly_without_fixtures() -> None:
    """Smoke: the harness must not crash on collection with zero fixtures.

    The parametrize decorator handles the empty-list case. This test
    simply verifies that every helper the harness depends on is
    importable. Guards against future refactors that accidentally break
    the recorder or replay_key modules.
    """
    assert FIXTURE_SCHEMA_VERSION == 1
    # A round-trip smoke through the helper with no I/O.
    artifact, slot_objs = _build_artifact_and_slots({"S0": "x", "U0": "y"})
    ir = artifact.to_prompt_messages(slots=slot_objs)
    assert "S0" in ir.slot_map
    assert "U0" in ir.slot_map
    key = compute_slot_digest_key(ir)
    assert key.startswith(SLOT_DIGEST_PREFIX)
