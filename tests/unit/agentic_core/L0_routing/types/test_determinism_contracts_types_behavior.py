"""Behavioral tests for ``agentic_core.L0_routing.types.determinism_contracts_types``.

Covers V15 P2 runtime contracts:
- ForbiddenInputError raised for non-SurgicalManifest inputs; message carries input_type.
- check_forbidden_input_type rejects documented forbidden tokens and passes others.
- validate_manifest_emission enforces type + hash integrity.
- require_manifest_hash_ok raises on hash mismatch.
- canonical_ast_serialize is deterministic; produces canonical_form matching its hash.
- verify_ast_determinism returns True for valid Python sources.
- dedupe_sha256 is deterministic SHA-256 hex; dedupe_check flips on second sighting.
- WallClockViolation carries file/line/callable fields.
- ast_scan_wall_clock flags documented forbidden callables (datetime.utcnow, time.time, ...).
- create_boundary_snapshot assembles a BoundarySnapshotArtifact from a SemanticClock.
- verify_rollback_integrity passes on exact match; raises RollbackHashMismatch on any mismatch.
- enforce_episodic_query_before_planning raises on None; allows any other value.
- knowledge_supervisor_check / check_velocity_threshold boundary semantics.
"""

from __future__ import annotations

import hashlib

import pytest

from agentic_core.L0_routing.types.determinism_contracts_types import (
    EpisodicMemoryNotQueried,
    ForbiddenInputError,
    RollbackHashMismatch,
    WallClockViolation,
    ast_scan_wall_clock,
    canonical_ast_serialize,
    check_forbidden_input_type,
    check_velocity_threshold,
    create_boundary_snapshot,
    dedupe_check,
    dedupe_sha256,
    enforce_episodic_query_before_planning,
    knowledge_supervisor_check,
    require_manifest_hash_ok,
    validate_execution_input,
    validate_manifest_emission,
    verify_ast_determinism,
    verify_rollback_integrity,
)
from agentic_core.L0_routing.types.determinism_types import (
    FORBIDDEN_INPUT_PATTERNS,
    BoundarySnapshotArtifact,
    FixConstraint,
    SemanticClock,
    SurgicalManifest,
)


def _make_manifest(ast_snippet: str = "x = 1", *, bad_hash: bool = False) -> SurgicalManifest:
    correct = hashlib.sha256(ast_snippet.encode("utf-8")).hexdigest()
    return SurgicalManifest(
        schema_version="1.0.0",
        correlation_id="c1",
        node_id="n1",
        target_layer="L0",
        ast_snippet=ast_snippet,
        serialization_canon="canon",
        fix_constraint=FixConstraint.STRICT,
        manifest_hash="bad" if bad_hash else correct,
        change_history=(),
        provenance_chain=(),
    )


# ---- ForbiddenInputError / validate_execution_input ----------------------


class TestForbiddenInput:
    def test_validate_accepts_manifest(self) -> None:
        m = _make_manifest()
        assert validate_execution_input(m) is m

    @pytest.mark.parametrize("bad", ["plain string", 42, ["list"], {"d": 1}, None])
    def test_validate_rejects_non_manifest(self, bad: object) -> None:
        with pytest.raises(ForbiddenInputError) as exc:
            validate_execution_input(bad)
        assert exc.value.input_type == type(bad).__name__

    @pytest.mark.parametrize("pattern", sorted(FORBIDDEN_INPUT_PATTERNS))
    def test_check_forbidden_pattern_raises(self, pattern: str) -> None:
        with pytest.raises(ForbiddenInputError):
            check_forbidden_input_type(pattern)

    def test_check_allowed_type_passes(self) -> None:
        check_forbidden_input_type("surgical_manifest")  # no raise


# ---- validate_manifest_emission / require_manifest_hash_ok ---------------


class TestManifestEmission:
    def test_valid_manifest_passes(self) -> None:
        m = _make_manifest()
        assert validate_manifest_emission(m) is m

    def test_wrong_type_raises_typeerror(self) -> None:
        with pytest.raises(TypeError, match="SurgicalManifest"):
            validate_manifest_emission({"not": "a manifest"})

    def test_bad_hash_raises_valueerror(self) -> None:
        m = _make_manifest(bad_hash=True)
        with pytest.raises(ValueError, match="manifest_hash"):
            validate_manifest_emission(m)

    def test_require_manifest_hash_ok_pass(self) -> None:
        require_manifest_hash_ok(_make_manifest())  # no raise

    def test_require_manifest_hash_ok_fail(self) -> None:
        with pytest.raises(ValueError, match="integrity hash mismatch"):
            require_manifest_hash_ok(_make_manifest(bad_hash=True))


# ---- canonical_ast_serialize / verify_ast_determinism --------------------


class TestCanonicalAST:
    def test_returns_canonical_result(self) -> None:
        result = canonical_ast_serialize("x = 1", source_path="test.py")
        assert result.source_path == "test.py"
        assert result.canonical_form  # non-empty
        assert len(result.canonical_hash) == 64  # sha256 hex

    def test_hash_matches_canonical_form(self) -> None:
        result = canonical_ast_serialize("x = 1 + 2")
        expected = hashlib.sha256(result.canonical_form.encode("utf-8")).hexdigest()
        assert result.canonical_hash == expected

    def test_two_runs_produce_same_hash(self) -> None:
        r1 = canonical_ast_serialize("def f(): return 1")
        r2 = canonical_ast_serialize("def f(): return 1")
        assert r1.canonical_hash == r2.canonical_hash

    def test_different_sources_produce_different_hashes(self) -> None:
        r1 = canonical_ast_serialize("x = 1")
        r2 = canonical_ast_serialize("x = 2")
        assert r1.canonical_hash != r2.canonical_hash

    def test_verify_determinism_true(self) -> None:
        assert verify_ast_determinism("a = 1\nb = 2") is True


# ---- dedupe --------------------------------------------------------------


class TestDedupe:
    def test_sha256_is_deterministic(self) -> None:
        assert dedupe_sha256("signal") == dedupe_sha256("signal")

    def test_sha256_matches_hashlib(self) -> None:
        assert dedupe_sha256("x") == hashlib.sha256(b"x").hexdigest()

    def test_first_sighting_not_duplicate(self) -> None:
        seen: set[str] = set()
        assert dedupe_check("signal-1", seen) is False
        assert dedupe_sha256("signal-1") in seen

    def test_second_sighting_is_duplicate(self) -> None:
        seen: set[str] = set()
        dedupe_check("signal-1", seen)
        assert dedupe_check("signal-1", seen) is True

    def test_different_signals_independent(self) -> None:
        seen: set[str] = set()
        dedupe_check("a", seen)
        assert dedupe_check("b", seen) is False


# ---- WallClockViolation + ast_scan_wall_clock ----------------------------


class TestWallClockScan:
    def test_violation_carries_metadata(self) -> None:
        v = WallClockViolation("time.time", "f.py", 42)
        assert v.callable_name == "time.time"
        assert v.file_path == "f.py"
        assert v.line == 42

    def test_clean_source_has_no_violations(self) -> None:
        src = "x = 1 + 2\ndef f(): return x\n"
        assert ast_scan_wall_clock(src) == []

    @pytest.mark.parametrize(
        "snippet",
        [
            "import time\nx = time.time()\n",
            "import time\nx = time.monotonic()\n",
            "import time\nx = time.perf_counter()\n",
            "from datetime import datetime\nx = datetime.now()\n",
            "from datetime import datetime\nx = datetime.utcnow()\n",
        ],
    )
    def test_forbidden_callable_detected(self, snippet: str) -> None:
        violations = ast_scan_wall_clock(snippet, file_path="test.py")
        assert len(violations) >= 1
        assert all(v.file_path == "test.py" for v in violations)

    def test_syntax_error_returns_empty(self) -> None:
        # Guarded inside the implementation — returns [], does not crash
        assert ast_scan_wall_clock("def bad(:") == []


# ---- create_boundary_snapshot + verify_rollback_integrity ----------------


class TestBoundarySnapshot:
    def test_create_populates_fields(self) -> None:
        clock = SemanticClock()
        snap = create_boundary_snapshot(
            trace_id="t",
            filesystem_hash="fs",
            git_state_hash="git",
            agent_memory_hash="mem",
            semantic_clock=clock,
        )
        assert isinstance(snap, BoundarySnapshotArtifact)
        assert snap.trace_id == "t"
        assert snap.filesystem_hash == "fs"
        assert snap.semantic_clock_tick == clock.current_tick

    def test_rollback_integrity_matching(self) -> None:
        snap = BoundarySnapshotArtifact(
            trace_id="t",
            filesystem_hash="fs",
            git_state_hash="git",
            agent_memory_hash="mem",
            semantic_clock_tick=0,
        )
        assert verify_rollback_integrity(snap, "fs", "git", "mem") is True

    @pytest.mark.parametrize(
        ("fs", "git", "mem", "field"),
        [
            ("other", "git", "mem", "filesystem"),
            ("fs", "other", "mem", "git_state"),
            ("fs", "git", "other", "agent_memory"),
        ],
    )
    def test_rollback_integrity_mismatch(
        self,
        fs: str,
        git: str,
        mem: str,
        field: str,
    ) -> None:
        snap = BoundarySnapshotArtifact(
            trace_id="t",
            filesystem_hash="fs",
            git_state_hash="git",
            agent_memory_hash="mem",
            semantic_clock_tick=0,
        )
        with pytest.raises(RollbackHashMismatch) as exc:
            verify_rollback_integrity(snap, fs, git, mem)
        assert exc.value.field == field


# ---- Episodic memory gate ------------------------------------------------


class TestEpisodicGate:
    def test_none_raises(self) -> None:
        with pytest.raises(EpisodicMemoryNotQueried):
            enforce_episodic_query_before_planning(None)

    @pytest.mark.parametrize("val", [0, "", [], {}, "result"])
    def test_non_none_passes(self, val: object) -> None:
        enforce_episodic_query_before_planning(val)  # no raise


# ---- knowledge_supervisor_check / check_velocity_threshold --------------


class TestSupervisorThresholds:
    def test_ks_below_threshold_requires_retrain(self) -> None:
        assert knowledge_supervisor_check(confidence=0.5, threshold=0.7) is True

    def test_ks_at_threshold_ok(self) -> None:
        assert knowledge_supervisor_check(confidence=0.7, threshold=0.7) is False

    def test_ks_above_threshold_ok(self) -> None:
        assert knowledge_supervisor_check(confidence=0.9, threshold=0.7) is False

    def test_velocity_at_threshold_triggers(self) -> None:
        assert check_velocity_threshold(signal_count=10, threshold=10) is True

    def test_velocity_above_threshold_triggers(self) -> None:
        assert check_velocity_threshold(signal_count=100, threshold=10) is True

    def test_velocity_below_threshold_quiet(self) -> None:
        assert check_velocity_threshold(signal_count=9, threshold=10) is False
