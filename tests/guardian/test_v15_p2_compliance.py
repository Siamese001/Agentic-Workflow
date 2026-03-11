"""
V15 P2 Compliance Regression Tests — Determinism & Replayability.

Each test maps 1:1 to a P2 backlog item from p0_p1_remediation_backlog.md.
If any test fails, the corresponding P2 item has regressed.

17 P2 items: 3 FAIL, 14 MISSING → all must reach COMPLIANT.
"""

from __future__ import annotations

import hashlib
from dataclasses import fields

import pytest

from agentic_core.L0_routing.types.determinism_contracts_types import (
    EpisodicMemoryNotQueried,
    ForbiddenInputError,
    RollbackHashMismatch,
    ast_scan_wall_clock,
    canonical_ast_serialize,
    check_forbidden_input_type,
    check_velocity_threshold,
    create_boundary_snapshot,
    dedupe_check,
    dedupe_sha256,
    enforce_episodic_query_before_planning,
    knowledge_supervisor_check,
    validate_execution_input,
    validate_manifest_emission,
    verify_ast_determinism,
    verify_rollback_integrity,
)
from agentic_core.L0_routing.types.determinism_types import (
    FORBIDDEN_INPUT_PATTERNS,
    MEMORY_CONFIDENCE_THRESHOLD,
    TRACE_BUFFER_VELOCITY_THRESHOLD,
    WALL_CLOCK_FORBIDDEN_CALLABLES,
    BoundarySnapshotArtifact,
    EpisodicMemoryQueryResult,
    EpisodicSemanticLink,
    FixConstraint,
    ForensicTraceBuffer,
    KnowledgeSupervisorResult,
    MemoryHypostate,
    SemanticClock,
    StateCommitInvalid,
    SurgicalManifest,
    TrajectoryReuseConstraint,
)

# ---- helpers ----------------------------------------------------------------


def _make_manifest(**overrides) -> SurgicalManifest:
    snippet = overrides.pop("ast_snippet", "x = 1")
    defaults = {
        "schema_version": "1.0.0",
        "correlation_id": "00000000-0000-0000-0000-000000000000",
        "node_id": "module.Class.method",
        "target_layer": "L2",
        "ast_snippet": snippet,
        "serialization_canon": hashlib.sha256(snippet.encode()).hexdigest(),
        "fix_constraint": FixConstraint.STRICT,
        "manifest_hash": hashlib.sha256(snippet.encode()).hexdigest(),
        "change_history": ("initial",),
        "provenance_chain": ("art-001",),
    }
    defaults.update(overrides)
    return SurgicalManifest(**defaults)


# =============================================================================
# §1.1 — SurgicalManifest as exclusive execution input
# =============================================================================


class TestP2_1_1_SurgicalManifestExclusive:
    """§1.1: Only SurgicalManifest is a valid execution input."""

    def test_valid_manifest_accepted(self):
        m = _make_manifest()
        result = validate_execution_input(m)
        assert isinstance(result, SurgicalManifest)

    def test_raw_dict_rejected(self):
        with pytest.raises(ForbiddenInputError, match="dict"):
            validate_execution_input({"key": "value"})

    def test_string_rejected(self):
        with pytest.raises(ForbiddenInputError, match="str"):
            validate_execution_input("some/path.py")

    def test_none_rejected(self):
        with pytest.raises(ForbiddenInputError, match="NoneType"):
            validate_execution_input(None)


# =============================================================================
# §1.2 — Forbidden execution inputs
# =============================================================================


class TestP2_1_2_ForbiddenInputs:
    """§1.2: raw paths, regex, diffs, line numbers, free-form text forbidden."""

    def test_forbidden_set_has_eight_types(self):
        assert len(FORBIDDEN_INPUT_PATTERNS) == 8

    @pytest.mark.parametrize("input_type", sorted(FORBIDDEN_INPUT_PATTERNS))
    def test_each_forbidden_type_rejected(self, input_type: str):
        with pytest.raises(ForbiddenInputError):
            check_forbidden_input_type(input_type)

    def test_surgical_manifest_type_not_forbidden(self):
        check_forbidden_input_type("SurgicalManifest")
        assert True  # no-exception contract


# =============================================================================
# §1.3 — SurgicalManifest schema (10 required fields)
# =============================================================================


class TestP2_1_3_ManifestSchema:
    """§1.3: SurgicalManifest has exactly 10 required fields."""

    REQUIRED_FIELDS = {
        "schema_version",
        "correlation_id",
        "node_id",
        "target_layer",
        "ast_snippet",
        "serialization_canon",
        "fix_constraint",
        "manifest_hash",
        "change_history",
        "provenance_chain",
    }

    def test_exactly_ten_fields(self):
        actual = {f.name for f in fields(SurgicalManifest)}
        assert actual == self.REQUIRED_FIELDS
        assert len(actual) == 10

    def test_schema_version_must_be_semver(self):
        with pytest.raises(ValueError, match="semver"):
            _make_manifest(schema_version="not-semver")

    def test_target_layer_must_be_L0_L6(self):
        with pytest.raises(ValueError, match="L0-L6"):
            _make_manifest(target_layer="L9")

    def test_fix_constraint_enum(self):
        assert len(FixConstraint) == 2
        assert FixConstraint.STRICT.value == "STRICT"
        assert FixConstraint.RELAXED.value == "RELAXED"


# =============================================================================
# §1.4 — Deterministic AST serialization
# =============================================================================


class TestP2_1_4_DeterministicAST:
    """§1.4: AST serialization is deterministic; formatter-dependent output invalid."""

    def test_same_source_same_hash(self):
        assert verify_ast_determinism("x = 1\ny = 2\n")

    def test_canonical_result_has_required_fields(self):
        r = canonical_ast_serialize("x = 1")
        assert r.source_path == "<string>"
        assert r.canonical_hash == hashlib.sha256(r.canonical_form.encode()).hexdigest()
        assert r.verify()

    def test_different_formatting_same_ast(self):
        r1 = canonical_ast_serialize("x=1")
        r2 = canonical_ast_serialize("x =  1")
        assert r1.canonical_hash == r2.canonical_hash


# =============================================================================
# §2.1 — Validator emits SurgicalManifest (per-agent)
# =============================================================================


class TestP2_2_1_ValidatorEmitsManifest:
    """§2.1: Validator must emit SurgicalManifest, not raw data."""

    def test_valid_manifest_passes(self):
        m = _make_manifest()
        result = validate_manifest_emission(m)
        assert isinstance(result, SurgicalManifest)

    def test_non_manifest_rejected(self):
        with pytest.raises(TypeError, match="SurgicalManifest"):
            validate_manifest_emission({"raw": "data"})

    def test_invalid_hash_rejected(self):
        m = _make_manifest(manifest_hash="0000000000000000000000000000000000000000000000000000000000000000")
        with pytest.raises(ValueError, match="manifest_hash"):
            validate_manifest_emission(m)


# =============================================================================
# §5.1 — Dedupe uses SHA-256 (per-agent)
# =============================================================================


class TestP2_5_1_DedupeSHA256:
    """§5.1: Deduplication uses SHA-256 hashes."""

    def test_hash_is_sha256_hex(self):
        h = dedupe_sha256("test signal")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_same_input_same_hash(self):
        assert dedupe_sha256("signal") == dedupe_sha256("signal")

    def test_different_input_different_hash(self):
        assert dedupe_sha256("a") != dedupe_sha256("b")

    def test_dedupe_check_detects_duplicate(self):
        seen: set[str] = set()
        assert dedupe_check("sig1", seen) is False
        assert dedupe_check("sig1", seen) is True

    def test_dedupe_check_allows_new(self):
        seen: set[str] = set()
        assert dedupe_check("sig1", seen) is False
        assert dedupe_check("sig2", seen) is False


# =============================================================================
# §13.1 — Semantic Clock (Step ID + Vector Clock)
# =============================================================================


class TestP2_13_1_SemanticClock:
    """§13.1: Time via Step ID + Vector Clock, NOT wall-clock."""

    def test_initial_state(self):
        clock = SemanticClock()
        assert clock.step_id == 0
        assert clock.vector_clock == {}

    def test_tick_on_valid_commit(self):
        clock = SemanticClock()
        clock.prepare_commit("L2")
        tick = clock.tick("L2", state_commit_valid=True)
        assert tick == 1
        assert clock.vector_clock["L2"] == 1

    def test_multiple_ticks(self):
        clock = SemanticClock()
        clock.prepare_commit("L2")
        clock.tick("L2", state_commit_valid=True)
        clock.tick("L2", state_commit_valid=True)
        clock.tick("L5", state_commit_valid=True)
        assert clock.step_id == 3
        assert clock.vector_clock == {"L2": 2, "L5": 1}


# =============================================================================
# §13.1.1 — Semantic Clock advances only on valid StateCommit
# =============================================================================


class TestP2_13_1_1_StateCommitGated:
    """§13.1.1: Clock tick rejected on invalid StateCommit."""

    def test_invalid_commit_raises(self):
        clock = SemanticClock()
        clock.prepare_commit("L2")
        with pytest.raises(StateCommitInvalid, match="invalid"):
            clock.tick("L2", state_commit_valid=False)

    def test_step_id_unchanged_after_rejection(self):
        clock = SemanticClock()
        clock.prepare_commit("L2")
        try:
            clock.tick("L2", state_commit_valid=False)
        except StateCommitInvalid:  # guardian: allow-silent-swallower
            pass
        assert clock.step_id == 0


# =============================================================================
# §13.2 — No wall-clock in hashes/signatures/dedup
# =============================================================================


class TestP2_13_2_NoWallClock:
    """§13.2: AST scan detects wall-clock usage in hash/signature/dedup paths."""

    def test_wall_clock_forbidden_set(self):
        assert "datetime.utcnow" in WALL_CLOCK_FORBIDDEN_CALLABLES
        assert "datetime.now" in WALL_CLOCK_FORBIDDEN_CALLABLES
        assert "time.time" in WALL_CLOCK_FORBIDDEN_CALLABLES

    def test_clean_source_no_violations(self):
        source = "x = 1\ny = x + 2\n"
        assert ast_scan_wall_clock(source) == []

    def test_datetime_utcnow_detected(self):
        source = "import datetime\nt = datetime.utcnow()\n"
        violations = ast_scan_wall_clock(source, "test.py")
        assert len(violations) >= 1
        assert any("utcnow" in v.callable_name for v in violations)

    def test_time_time_detected(self):
        source = "import time\nt = time.time()\n"
        violations = ast_scan_wall_clock(source, "test.py")
        assert len(violations) >= 1


# =============================================================================
# §10.2 — Boundary Snapshot Artifact
# =============================================================================


class TestP2_10_2_BoundarySnapshot:
    """§10.2: BoundarySnapshotArtifact has all 5 required fields."""

    REQUIRED_FIELDS = {
        "trace_id",
        "filesystem_hash",
        "git_state_hash",
        "agent_memory_hash",
        "semantic_clock_tick",
    }

    def test_required_fields(self):
        actual = {f.name for f in fields(BoundarySnapshotArtifact)}
        assert actual == self.REQUIRED_FIELDS

    def test_create_boundary_snapshot(self):
        clock = SemanticClock()
        clock.tick("L2", state_commit_valid=True)
        snap = create_boundary_snapshot(
            trace_id="t1",
            filesystem_hash="fh1",
            git_state_hash="gh1",
            agent_memory_hash="mh1",
            semantic_clock=clock,
        )
        assert snap.semantic_clock_tick == 1


# =============================================================================
# §10.3 — Post-rollback hash matches pre-wave snapshot
# =============================================================================


class TestP2_10_3_RollbackHashMatch:
    """§10.3: Post-rollback state hash must match pre-wave snapshot exactly."""

    def test_matching_hashes_pass(self):
        snap = BoundarySnapshotArtifact(
            trace_id="t1",
            filesystem_hash="fh",
            git_state_hash="gh",
            agent_memory_hash="mh",
            semantic_clock_tick=1,
        )
        assert verify_rollback_integrity(snap, "fh", "gh", "mh") is True

    def test_fs_mismatch_raises(self):
        snap = BoundarySnapshotArtifact(
            trace_id="t1",
            filesystem_hash="fh",
            git_state_hash="gh",
            agent_memory_hash="mh",
            semantic_clock_tick=1,
        )
        with pytest.raises(RollbackHashMismatch, match="filesystem"):
            verify_rollback_integrity(snap, "WRONG", "gh", "mh")

    def test_git_mismatch_raises(self):
        snap = BoundarySnapshotArtifact(
            trace_id="t1",
            filesystem_hash="fh",
            git_state_hash="gh",
            agent_memory_hash="mh",
            semantic_clock_tick=1,
        )
        with pytest.raises(RollbackHashMismatch, match="git_state"):
            verify_rollback_integrity(snap, "fh", "WRONG", "mh")

    def test_memory_mismatch_raises(self):
        snap = BoundarySnapshotArtifact(
            trace_id="t1",
            filesystem_hash="fh",
            git_state_hash="gh",
            agent_memory_hash="mh",
            semantic_clock_tick=1,
        )
        with pytest.raises(RollbackHashMismatch, match="agent_memory"):
            verify_rollback_integrity(snap, "fh", "gh", "WRONG")


# =============================================================================
# §6.1 — Episodic memory queried before planning
# =============================================================================


class TestP2_6_1_EpisodicMemoryFirst:
    """§6.1: Episodic memory must be queried before planning."""

    def test_none_raises(self):
        with pytest.raises(EpisodicMemoryNotQueried):
            enforce_episodic_query_before_planning(None)

    def test_valid_result_passes(self):
        result = EpisodicMemoryQueryResult(
            trace_id="t1",
            query_hash="qh",
            results=("r1",),
            confidence_scores=(0.9,),
        )
        enforce_episodic_query_before_planning(result)
        assert True  # no-exception contract

    def test_query_result_fields(self):
        required = {"trace_id", "query_hash", "results", "confidence_scores"}
        actual = {f.name for f in fields(EpisodicMemoryQueryResult)}
        assert required == actual


# =============================================================================
# §6.2 — Trajectory reuse
# =============================================================================


class TestP2_6_2_TrajectoryReuse:
    """§6.2: Reuse requires similarity AND exact failure_reason match."""

    def test_reusable_when_both_match(self):
        c = TrajectoryReuseConstraint(
            trace_id="t1",
            similarity_score=0.95,
            similarity_threshold=THRESHOLD,
            failure_reason="ImportError",
            candidate_failure_reason="ImportError",
        )
        assert c.reusable is True

    def test_not_reusable_low_similarity(self):
        c = TrajectoryReuseConstraint(
            trace_id="t1",
            similarity_score=0.5,
            similarity_threshold=THRESHOLD,
            failure_reason="ImportError",
            candidate_failure_reason="ImportError",
        )
        assert c.reusable is False

    def test_not_reusable_different_reason(self):
        c = TrajectoryReuseConstraint(
            trace_id="t1",
            similarity_score=0.95,
            similarity_threshold=THRESHOLD,
            failure_reason="ImportError",
            candidate_failure_reason="SyntaxError",
        )
        assert c.reusable is False


# =============================================================================
# §6.6 — Knowledge Supervisor
# =============================================================================


class TestP2_6_6_KnowledgeSupervisor:
    """§6.6: Knowledge Supervisor audits low-confidence retrievals."""

    def test_default_threshold_is_0_7(self):
        assert MEMORY_CONFIDENCE_THRESHOLD == 0.7

    def test_low_confidence_triggers_retraining(self):
        r = KnowledgeSupervisorResult(trace_id="t1", confidence_score=0.5)
        assert r.requires_retraining is True

    def test_high_confidence_no_retraining(self):
        r = KnowledgeSupervisorResult(trace_id="t1", confidence_score=0.9)
        assert r.requires_retraining is False

    def test_check_function(self):
        assert knowledge_supervisor_check(0.5) is True
        assert knowledge_supervisor_check(0.9) is False


# =============================================================================
# §6.8 — Memory Hypostates
# =============================================================================


class TestP2_6_8_MemoryHypostates:
    """§6.8: Extended Trace Hypostate linked to Semantic Clock."""

    REQUIRED_FIELDS = {
        "trace_id",
        "semantic_clock_tick",
        "memory_snapshot_hash",
        "state_commit_id",
    }

    def test_required_fields(self):
        actual = {f.name for f in fields(MemoryHypostate)}
        assert actual == self.REQUIRED_FIELDS

    def test_instantiation(self):
        h = MemoryHypostate(
            trace_id="t1",
            semantic_clock_tick=5,
            memory_snapshot_hash="msh",
            state_commit_id="sc1",
        )
        assert h.semantic_clock_tick == 5


# =============================================================================
# §6.10 — Episodic ↔ Semantic Linking
# =============================================================================


class TestP2_6_10_EpisodicSemanticLinking:
    """§6.10: Episodic memory records outcome links used in reasoning."""

    REQUIRED_FIELDS = {
        "trace_id",
        "episodic_memory_id",
        "semantic_outcome_id",
        "reasoning_context_hash",
    }

    def test_required_fields(self):
        actual = {f.name for f in fields(EpisodicSemanticLink)}
        assert actual == self.REQUIRED_FIELDS

    def test_instantiation(self):
        link = EpisodicSemanticLink(
            trace_id="t1",
            episodic_memory_id="em1",
            semantic_outcome_id="so1",
            reasoning_context_hash="rch",
        )
        assert link.episodic_memory_id == "em1"


# =============================================================================
# §15.3 — Forensic Trace Buffer
# =============================================================================


class TestP2_15_3_ForensicTraceBuffer:
    """§15.3: Forensic Trace Buffer with velocity threshold."""

    def test_default_threshold_is_10(self):
        assert TRACE_BUFFER_VELOCITY_THRESHOLD == 10

    def test_ingest_and_count(self):
        buf = ForensicTraceBuffer(trace_id="t1", semantic_clock_tick=1)
        buf.ingest({"signal": "s1"})
        buf.ingest({"signal": "s2"})
        assert buf.signal_count == 2

    def test_velocity_not_exceeded_below_threshold(self):
        buf = ForensicTraceBuffer(trace_id="t1", semantic_clock_tick=1)
        for i in range(9):
            buf.ingest({"signal": f"s{i}"})
        assert buf.velocity_exceeded is False

    def test_velocity_exceeded_at_threshold(self):
        buf = ForensicTraceBuffer(trace_id="t1", semantic_clock_tick=1)
        for i in range(10):
            buf.ingest({"signal": f"s{i}"})
        assert buf.velocity_exceeded is True

    def test_flush_clears_buffer(self):
        buf = ForensicTraceBuffer(trace_id="t1", semantic_clock_tick=1)
        buf.ingest({"signal": "s1"})
        contents = buf.flush()
        assert len(contents) == 1
        assert buf.signal_count == 0

    def test_check_velocity_function(self):
        assert check_velocity_threshold(10) is True
        assert check_velocity_threshold(9) is False
