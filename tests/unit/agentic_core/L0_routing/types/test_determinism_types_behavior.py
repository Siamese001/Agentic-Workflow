"""Behavioral tests for agentic_core.L0_routing.types.determinism_types.

Covers the runtime contract logic that the existing `importorskip` smoke tests
do not exercise:
  - `SurgicalManifest` __post_init__ validation + verify_hash
  - `CanonicalASTResult.verify`
  - `SemanticClock` prepare_commit / tick / current_tick / StateCommitInvalid
  - `SemanticClockSnapshot` __post_init__, to_dict, from_clock
  - `validate_semantic_clock` None/type rejection
  - `TrajectoryReuseConstraint.reusable` predicate
  - `KnowledgeSupervisorResult.requires_retraining` post-init
  - `ForensicTraceBuffer` ingest / signal_count / velocity_exceeded / flush
  - `SemanticClockAdvancementArtifact` deterministic artifact_hash
  - `FORBIDDEN_INPUT_PATTERNS` / `WALL_CLOCK_FORBIDDEN_CALLABLES` constants

L0 is a ×2.0 criticality layer. This module ranked #2 (fan-in=34) in the
Stage 1 risk-weighted gap report
(`ops_scripts/verification/report_risk_weighted_test_gaps.py`).
"""

from __future__ import annotations

import hashlib

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def dt():
    return pytest.importorskip("agentic_core.L0_routing.types.determinism_types")


# --------------------------------------------------------------------------- #
# Constants                                                                   #
# --------------------------------------------------------------------------- #


class TestConstants:
    def test_forbidden_input_patterns_is_frozenset(self, dt):
        assert isinstance(dt.FORBIDDEN_INPUT_PATTERNS, frozenset)
        assert "raw_file_path" in dt.FORBIDDEN_INPUT_PATTERNS
        assert "free_form_text" in dt.FORBIDDEN_INPUT_PATTERNS

    def test_wall_clock_forbidden_callables_is_frozenset(self, dt):
        assert isinstance(dt.WALL_CLOCK_FORBIDDEN_CALLABLES, frozenset)
        assert "time.time" in dt.WALL_CLOCK_FORBIDDEN_CALLABLES
        assert "datetime.utcnow" in dt.WALL_CLOCK_FORBIDDEN_CALLABLES
        assert "datetime.now" in dt.WALL_CLOCK_FORBIDDEN_CALLABLES

    def test_memory_confidence_threshold_is_float(self, dt):
        assert isinstance(dt.MEMORY_CONFIDENCE_THRESHOLD, float)
        assert 0.0 < dt.MEMORY_CONFIDENCE_THRESHOLD < 1.0

    def test_trace_buffer_velocity_threshold_is_positive_int(self, dt):
        assert isinstance(dt.TRACE_BUFFER_VELOCITY_THRESHOLD, int)
        assert dt.TRACE_BUFFER_VELOCITY_THRESHOLD > 0


# --------------------------------------------------------------------------- #
# FixConstraint                                                               #
# --------------------------------------------------------------------------- #


class TestFixConstraint:
    def test_enum_members(self, dt):
        assert dt.FixConstraint.STRICT.value == "STRICT"
        assert dt.FixConstraint.RELAXED.value == "RELAXED"

    def test_is_str_enum(self, dt):
        assert dt.FixConstraint.STRICT == "STRICT"


# --------------------------------------------------------------------------- #
# SurgicalManifest                                                            #
# --------------------------------------------------------------------------- #


def _mk_manifest(dt, *, schema_version="1.0.0", target_layer="L0", ast_snippet="x=1", manifest_hash=None):
    """Build a SurgicalManifest with optional overrides; computes correct hash if None."""
    if manifest_hash is None:
        manifest_hash = hashlib.sha256(ast_snippet.encode("utf-8")).hexdigest()
    return dt.SurgicalManifest(
        schema_version=schema_version,
        correlation_id="corr-1",
        node_id="node-1",
        target_layer=target_layer,
        ast_snippet=ast_snippet,
        serialization_canon="canonical",
        fix_constraint=dt.FixConstraint.STRICT,
        manifest_hash=manifest_hash,
        change_history=(),
        provenance_chain=(),
    )


class TestSurgicalManifest:
    def test_valid_construction(self, dt):
        m = _mk_manifest(dt)
        assert m.schema_version == "1.0.0"
        assert m.target_layer == "L0"

    @pytest.mark.parametrize("bad", ["1.0", "v1.0.0", "1", "", "abc"])
    def test_invalid_semver_raises(self, dt, bad):
        with pytest.raises(ValueError, match="semver"):
            _mk_manifest(dt, schema_version=bad)

    @pytest.mark.parametrize("bad", ["L7", "L_APP", "routing", ""])
    def test_invalid_layer_raises(self, dt, bad):
        with pytest.raises(ValueError, match="target_layer"):
            _mk_manifest(dt, target_layer=bad)

    @pytest.mark.parametrize("ok", ["L0", "L1", "L2", "L3", "L4", "L5", "L6"])
    def test_all_valid_layers_accepted(self, dt, ok):
        m = _mk_manifest(dt, target_layer=ok)
        assert m.target_layer == ok

    def test_verify_hash_returns_true_when_match(self, dt):
        m = _mk_manifest(dt)
        assert m.verify_hash() is True

    def test_verify_hash_returns_false_when_mismatch(self, dt):
        m = _mk_manifest(dt, ast_snippet="x=1", manifest_hash="0" * 64)
        assert m.verify_hash() is False

    def test_is_frozen(self, dt):
        m = _mk_manifest(dt)
        with pytest.raises((AttributeError, Exception)):
            m.schema_version = "2.0.0"  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# CanonicalASTResult                                                          #
# --------------------------------------------------------------------------- #


class TestCanonicalASTResult:
    def test_verify_matches_sha256_of_canonical_form(self, dt):
        form = "def f(): return 1"
        r = dt.CanonicalASTResult(
            source_path="x.py",
            canonical_form=form,
            canonical_hash=hashlib.sha256(form.encode("utf-8")).hexdigest(),
        )
        assert r.verify() is True

    def test_verify_false_on_mismatch(self, dt):
        r = dt.CanonicalASTResult(
            source_path="x.py",
            canonical_form="content",
            canonical_hash="0" * 64,
        )
        assert r.verify() is False


# --------------------------------------------------------------------------- #
# SemanticClock / StateCommitInvalid                                          #
# --------------------------------------------------------------------------- #


class TestSemanticClock:
    def test_initial_state(self, dt):
        c = dt.SemanticClock()
        assert c.step_id == 0
        assert c.current_tick == 0
        assert c.vector_clock == {}

    def test_prepare_commit_registers_layer_at_zero(self, dt):
        c = dt.SemanticClock()
        c.prepare_commit("L2")
        assert c.vector_clock["L2"] == 0
        assert c.step_id == 0  # prepare does not advance

    def test_tick_valid_advances_step_and_layer(self, dt):
        c = dt.SemanticClock()
        c.prepare_commit("L2")
        new_step = c.tick("L2", state_commit_valid=True)
        assert new_step == 1
        assert c.step_id == 1
        assert c.vector_clock["L2"] == 1
        assert c.current_tick == 1

    def test_tick_invalid_raises_state_commit_invalid(self, dt):
        c = dt.SemanticClock()
        c.prepare_commit("L2")
        with pytest.raises(dt.StateCommitInvalid):
            c.tick("L2", state_commit_valid=False)
        # Clock must not advance
        assert c.step_id == 0

    def test_multiple_ticks_accumulate(self, dt):
        c = dt.SemanticClock()
        c.prepare_commit("L2")
        c.tick("L2", True)
        c.tick("L2", True)
        c.tick("L2", True)
        assert c.step_id == 3
        assert c.vector_clock["L2"] == 3

    def test_tick_without_prepare_still_initializes_layer(self, dt):
        # tick uses dict.get with default 0, so it works even without prepare
        c = dt.SemanticClock()
        c.tick("L3", True)
        assert c.vector_clock["L3"] == 1

    def test_state_commit_invalid_is_exception(self, dt):
        exc = dt.StateCommitInvalid("msg")
        assert isinstance(exc, Exception)


# --------------------------------------------------------------------------- #
# SemanticClockSnapshot                                                       #
# --------------------------------------------------------------------------- #


class TestSemanticClockSnapshot:
    def test_valid_construction(self, dt):
        s = dt.SemanticClockSnapshot(tick=5, vector_clock=(("L0", 1), ("L2", 4)))
        assert s.tick == 5

    def test_negative_tick_raises(self, dt):
        with pytest.raises(ValueError, match=">= 0"):
            dt.SemanticClockSnapshot(tick=-1)

    def test_zero_tick_allowed(self, dt):
        s = dt.SemanticClockSnapshot(tick=0)
        assert s.tick == 0

    def test_to_dict_sorts_vector_clock_keys(self, dt):
        s = dt.SemanticClockSnapshot(tick=3, vector_clock=(("L5", 2), ("L0", 1), ("L2", 3)))
        d = s.to_dict()
        assert d == {"tick": 3, "vector_clock": {"L0": 1, "L2": 3, "L5": 2}}
        # dict iteration order matches sorted keys
        assert list(d["vector_clock"].keys()) == ["L0", "L2", "L5"]

    def test_from_clock_captures_state(self, dt):
        c = dt.SemanticClock()
        c.tick("L2", True)
        c.tick("L5", True)
        snap = dt.SemanticClockSnapshot.from_clock(c)
        assert snap.tick == c.step_id
        assert dict(snap.vector_clock) == c.vector_clock

    def test_from_clock_result_is_sorted(self, dt):
        c = dt.SemanticClock()
        c.tick("L5", True)
        c.tick("L0", True)
        c.tick("L2", True)
        snap = dt.SemanticClockSnapshot.from_clock(c)
        keys = [k for k, _ in snap.vector_clock]
        assert keys == sorted(keys)


# --------------------------------------------------------------------------- #
# validate_semantic_clock                                                     #
# --------------------------------------------------------------------------- #


class TestValidateSemanticClock:
    def test_none_raises_value_error(self, dt):
        with pytest.raises(ValueError, match="required"):
            dt.validate_semantic_clock(None)

    def test_wrong_type_raises_type_error(self, dt):
        with pytest.raises(TypeError, match="SemanticClockSnapshot"):
            dt.validate_semantic_clock("not-a-snapshot")  # type: ignore[arg-type]

    def test_valid_snapshot_returns_snapshot(self, dt):
        s = dt.SemanticClockSnapshot(tick=1)
        assert dt.validate_semantic_clock(s) is s


# --------------------------------------------------------------------------- #
# TrajectoryReuseConstraint                                                   #
# --------------------------------------------------------------------------- #


class TestTrajectoryReuseConstraint:
    def test_reusable_when_above_threshold_and_reason_matches(self, dt):
        c = dt.TrajectoryReuseConstraint(
            trace_id="t",
            similarity_score=0.9,
            similarity_threshold=0.8,
            failure_reason="timeout",
            candidate_failure_reason="timeout",
        )
        assert c.reusable is True

    def test_not_reusable_when_below_threshold(self, dt):
        c = dt.TrajectoryReuseConstraint(
            trace_id="t",
            similarity_score=0.7,
            similarity_threshold=0.8,
            failure_reason="timeout",
            candidate_failure_reason="timeout",
        )
        assert c.reusable is False

    def test_not_reusable_when_reason_differs(self, dt):
        c = dt.TrajectoryReuseConstraint(
            trace_id="t",
            similarity_score=0.95,
            similarity_threshold=0.8,
            failure_reason="timeout",
            candidate_failure_reason="syntax_error",
        )
        assert c.reusable is False

    def test_reusable_at_exact_threshold(self, dt):
        c = dt.TrajectoryReuseConstraint(
            trace_id="t",
            similarity_score=0.8,
            similarity_threshold=0.8,
            failure_reason="x",
            candidate_failure_reason="x",
        )
        assert c.reusable is True  # >= not >


# --------------------------------------------------------------------------- #
# KnowledgeSupervisorResult                                                   #
# --------------------------------------------------------------------------- #


class TestKnowledgeSupervisorResult:
    def test_retraining_required_below_threshold(self, dt):
        r = dt.KnowledgeSupervisorResult(trace_id="t", confidence_score=0.5, threshold=0.7)
        assert r.requires_retraining is True

    def test_retraining_not_required_at_or_above_threshold(self, dt):
        r = dt.KnowledgeSupervisorResult(trace_id="t", confidence_score=0.7, threshold=0.7)
        assert r.requires_retraining is False

    def test_uses_default_threshold(self, dt):
        r = dt.KnowledgeSupervisorResult(trace_id="t", confidence_score=0.5)
        assert r.threshold == dt.MEMORY_CONFIDENCE_THRESHOLD


# --------------------------------------------------------------------------- #
# ForensicTraceBuffer                                                         #
# --------------------------------------------------------------------------- #


class TestForensicTraceBuffer:
    def test_empty_buffer_initial_state(self, dt):
        b = dt.ForensicTraceBuffer(trace_id="t", semantic_clock_tick=0)
        assert b.signal_count == 0
        assert b.velocity_exceeded is False

    def test_ingest_increments_signal_count(self, dt):
        b = dt.ForensicTraceBuffer(trace_id="t", semantic_clock_tick=0, velocity_threshold=3)
        b.ingest({"k": 1})
        b.ingest({"k": 2})
        assert b.signal_count == 2

    def test_velocity_exceeded_at_threshold(self, dt):
        b = dt.ForensicTraceBuffer(trace_id="t", semantic_clock_tick=0, velocity_threshold=3)
        for i in range(2):
            b.ingest({"i": i})
        assert b.velocity_exceeded is False
        b.ingest({"i": 2})
        assert b.velocity_exceeded is True

    def test_flush_returns_copy_and_clears(self, dt):
        b = dt.ForensicTraceBuffer(trace_id="t", semantic_clock_tick=0)
        b.ingest({"a": 1})
        b.ingest({"b": 2})
        contents = b.flush()
        assert contents == [{"a": 1}, {"b": 2}]
        assert b.signal_count == 0
        # Mutating returned list must not affect internal state
        contents.append({"c": 3})
        assert b.signal_count == 0

    def test_flush_empty_buffer_returns_empty_list(self, dt):
        b = dt.ForensicTraceBuffer(trace_id="t", semantic_clock_tick=0)
        assert b.flush() == []


# --------------------------------------------------------------------------- #
# SemanticClockAdvancementArtifact                                            #
# --------------------------------------------------------------------------- #


class TestSemanticClockAdvancementArtifact:
    def _mk(self, dt, **overrides):
        defaults = dict(
            advancement_id="adv-1",
            previous_tick=5,
            new_tick=6,
            advancement_reason="state_commit",
            l4_version_binding="v42",
            provider_id="prov-1",
            timestamp=1234567.0,
        )
        defaults.update(overrides)
        return dt.SemanticClockAdvancementArtifact(**defaults)

    def test_artifact_hash_auto_computed(self, dt):
        a = self._mk(dt)
        assert a.artifact_hash  # non-empty
        assert len(a.artifact_hash) == 64  # sha256 hex

    def test_artifact_hash_is_deterministic(self, dt):
        a1 = self._mk(dt)
        a2 = self._mk(dt)
        assert a1.artifact_hash == a2.artifact_hash

    def test_artifact_hash_changes_with_payload(self, dt):
        a = self._mk(dt, advancement_id="adv-1")
        b = self._mk(dt, advancement_id="adv-2")
        assert a.artifact_hash != b.artifact_hash

    def test_provided_hash_preserved(self, dt):
        a = self._mk(dt, artifact_hash="abc123")
        assert a.artifact_hash == "abc123"


# --------------------------------------------------------------------------- #
# Lightweight typed containers (construct-and-read)                           #
# --------------------------------------------------------------------------- #


class TestDataContainers:
    def test_boundary_snapshot_artifact_fields(self, dt):
        b = dt.BoundarySnapshotArtifact(
            trace_id="t",
            filesystem_hash="fs",
            git_state_hash="git",
            agent_memory_hash="mem",
            semantic_clock_tick=7,
        )
        assert b.semantic_clock_tick == 7

    def test_episodic_memory_query_result_fields(self, dt):
        e = dt.EpisodicMemoryQueryResult(
            trace_id="t",
            query_hash="qh",
            results=("a", "b"),
            confidence_scores=(0.9, 0.8),
        )
        assert e.results == ("a", "b")
        assert e.confidence_scores == (0.9, 0.8)

    def test_memory_hypostate_fields(self, dt):
        m = dt.MemoryHypostate(
            trace_id="t",
            semantic_clock_tick=3,
            memory_snapshot_hash="h",
            state_commit_id="cid",
        )
        assert m.semantic_clock_tick == 3

    def test_episodic_semantic_link_fields(self, dt):
        link = dt.EpisodicSemanticLink(
            trace_id="t",
            episodic_memory_id="em",
            semantic_outcome_id="so",
            reasoning_context_hash="rh",
        )
        assert link.episodic_memory_id == "em"
