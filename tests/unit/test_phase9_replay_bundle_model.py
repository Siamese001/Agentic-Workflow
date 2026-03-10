"""
Phase 9 — Wave 1 Tests: ReplayBundle model + deterministic validation.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.types.replay_bundle_types import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    ReplayBundle,
    build_replay_bundle,
)

pytestmark = pytest.mark.unit_min_deps

_MH = "m" * 64
_CONFIG = {"policy_hash": "ph1", "routing_hash": "rh1", "model_hash": "mh1", "budget_hash": "bh1"}


def _make_bundle(**overrides) -> ReplayBundle:
    defaults: dict = {
        "schema_version": 1,
        "mission_id": "mission-test",
        "execution_start_tick": 5,
        "execution_end_tick": 10,
        "manifest_hash": _MH,
        "active_config_hashes": dict(_CONFIG),
        "retrieval_used": False,
        "citation_hash": "",
        "prior_detection_signal_hash": "",
        "prior_violation_event_hashes": [],
        "tool_intent_hashes": [],
        "tool_result_hashes": [],
    }
    defaults.update(overrides)
    return ReplayBundle(**defaults)


class TestReplayBundleHashStable:
    def test_replay_bundle_hash_stable(self):
        """Same inputs produce the same replay_hash on repeated construction."""
        b1 = _make_bundle()
        b2 = _make_bundle()
        assert b1.replay_hash == b2.replay_hash
        assert len(b1.replay_hash) == 64

    def test_hash_changes_with_mission_id(self):
        b1 = _make_bundle(mission_id="mission-A")
        b2 = _make_bundle(mission_id="mission-B")
        assert b1.replay_hash != b2.replay_hash

    def test_hash_changes_with_manifest_hash(self):
        b1 = _make_bundle(manifest_hash="a" * 64)
        b2 = _make_bundle(manifest_hash="b" * 64)
        assert b1.replay_hash != b2.replay_hash

    def test_hash_changes_with_config_hashes(self):
        b1 = _make_bundle(active_config_hashes={"policy_hash": "aaa"})
        b2 = _make_bundle(active_config_hashes={"policy_hash": "bbb"})
        assert b1.replay_hash != b2.replay_hash

    def test_hash_changes_with_ticks(self):
        b1 = _make_bundle(execution_start_tick=5, execution_end_tick=10)
        b2 = _make_bundle(execution_start_tick=6, execution_end_tick=10)
        assert b1.replay_hash != b2.replay_hash

    def test_hash_changes_with_violation_hashes(self):
        b1 = _make_bundle(prior_violation_event_hashes=["vh-A"])
        b2 = _make_bundle(prior_violation_event_hashes=["vh-B"])
        assert b1.replay_hash != b2.replay_hash

    def test_replay_hash_excluded_from_canonical_bytes(self):
        b = _make_bundle()
        assert b"replay_hash" not in b.canonical_bytes()

    def test_canonical_bytes_deterministic(self):
        b1 = _make_bundle()
        b2 = _make_bundle()
        assert b1.canonical_bytes() == b2.canonical_bytes()

    def test_hash_with_retrieval_used_and_citation(self):
        b = _make_bundle(retrieval_used=True, citation_hash="c" * 64)
        assert len(b.replay_hash) == 64

    def test_hash_changes_with_citation_hash(self):
        b1 = _make_bundle(retrieval_used=True, citation_hash="c" * 64)
        b2 = _make_bundle(retrieval_used=True, citation_hash="d" * 64)
        assert b1.replay_hash != b2.replay_hash


class TestReplayBundleSortingDeterministic:
    def test_replay_bundle_sorting_deterministic(self):
        """
        Lists passed in any order produce the same replay_hash after sorting.
        """
        b1 = _make_bundle(
            prior_violation_event_hashes=["vh-Z", "vh-A", "vh-M"],
            tool_intent_hashes=["ih-Z", "ih-A"],
            tool_result_hashes=["rh-Z", "rh-A"],
        )
        b2 = _make_bundle(
            prior_violation_event_hashes=["vh-A", "vh-M", "vh-Z"],
            tool_intent_hashes=["ih-A", "ih-Z"],
            tool_result_hashes=["rh-A", "rh-Z"],
        )
        assert b1.replay_hash == b2.replay_hash

    def test_violation_hashes_stored_sorted(self):
        b = _make_bundle(prior_violation_event_hashes=["vh-Z", "vh-A", "vh-M"])
        assert b.prior_violation_event_hashes == sorted(b.prior_violation_event_hashes)

    def test_intent_hashes_stored_sorted(self):
        b = _make_bundle(tool_intent_hashes=["ih-Z", "ih-A"])
        assert b.tool_intent_hashes == sorted(b.tool_intent_hashes)

    def test_result_hashes_stored_sorted(self):
        b = _make_bundle(tool_result_hashes=["rh-Z", "rh-A"])
        assert b.tool_result_hashes == sorted(b.tool_result_hashes)

    def test_config_hashes_keys_sorted_in_canonical_bytes(self):
        b = _make_bundle(active_config_hashes={"z_hash": "zzz", "a_hash": "aaa", "m_hash": "mmm"})
        raw = b.canonical_bytes().decode()
        a_pos = raw.index("a_hash")
        m_pos = raw.index("m_hash")
        z_pos = raw.index("z_hash")
        assert a_pos < m_pos < z_pos

    def test_empty_lists_allowed(self):
        b = _make_bundle(
            prior_violation_event_hashes=[],
            tool_intent_hashes=[],
            tool_result_hashes=[],
        )
        assert b.prior_violation_event_hashes == []
        assert b.tool_intent_hashes == []
        assert b.tool_result_hashes == []
        assert len(b.replay_hash) == 64


class TestReplayBundleRequiresCitationHashWhenRetrievalUsed:
    def test_replay_bundle_requires_citation_hash_when_retrieval_used(self):
        """retrieval_used=True with empty citation_hash must raise ValueError."""
        with pytest.raises(ValueError, match="citation_hash"):
            _make_bundle(retrieval_used=True, citation_hash="")

    def test_retrieval_used_false_no_citation_hash_ok(self):
        b = _make_bundle(retrieval_used=False, citation_hash="")
        assert b.citation_hash == ""

    def test_retrieval_used_true_with_citation_hash_ok(self):
        b = _make_bundle(retrieval_used=True, citation_hash="c" * 64)
        assert b.citation_hash == "c" * 64

    def test_invalid_schema_version_raises(self):
        with pytest.raises(ValueError, match="schema_version"):
            _make_bundle(schema_version=99)

    def test_empty_mission_id_raises(self):
        with pytest.raises(ValueError, match="mission_id"):
            _make_bundle(mission_id="")

    def test_empty_manifest_hash_raises(self):
        with pytest.raises(ValueError, match="manifest_hash"):
            _make_bundle(manifest_hash="")

    def test_negative_start_tick_raises(self):
        with pytest.raises(ValueError, match="execution_start_tick"):
            _make_bundle(execution_start_tick=-1, execution_end_tick=0)

    def test_end_tick_before_start_tick_raises(self):
        with pytest.raises(ValueError, match="execution_end_tick"):
            _make_bundle(execution_start_tick=10, execution_end_tick=5)

    def test_non_dict_config_hashes_raises(self):
        with pytest.raises(TypeError, match="active_config_hashes"):
            _make_bundle(active_config_hashes="not-a-dict")  # type: ignore[arg-type]

    def test_non_list_violation_hashes_raises(self):
        with pytest.raises(TypeError, match="prior_violation_event_hashes"):
            _make_bundle(prior_violation_event_hashes="not-a-list")  # type: ignore[arg-type]


class TestBuildReplayBundleFactory:
    def test_factory_produces_valid_bundle(self):
        b = build_replay_bundle(
            mission_id="m1",
            execution_start_tick=5,
            execution_end_tick=10,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
        )
        assert isinstance(b, ReplayBundle)
        assert len(b.replay_hash) == 64

    def test_factory_defaults_no_retrieval(self):
        b = build_replay_bundle(
            mission_id="m1",
            execution_start_tick=5,
            execution_end_tick=10,
            manifest_hash=_MH,
            active_config_hashes=_CONFIG,
        )
        assert b.retrieval_used is False
        assert b.citation_hash == ""

    def test_to_dict_contains_all_fields(self):
        b = _make_bundle()
        d = b.to_dict()
        for key in (
            "schema_version",
            "mission_id",
            "execution_start_tick",
            "execution_end_tick",
            "manifest_hash",
            "active_config_hashes",
            "retrieval_used",
            "citation_hash",
            "prior_detection_signal_hash",
            "prior_violation_event_hashes",
            "tool_intent_hashes",
            "tool_result_hashes",
            "replay_hash",
        ):
            assert key in d
