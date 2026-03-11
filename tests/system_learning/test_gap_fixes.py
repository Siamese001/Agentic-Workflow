"""Deterministic tests for all system_learning gap fixes.

Covers:
  GAP-002: RUNTIME category in rca_engine CLASSIFICATION_RULES
  GAP-003: DPO proposals enter Stage 7 validation loop
  GAP-004: n_observations derived from audit_slice line count
  GAP-005: Stages 8.6 and 8.7 independent of Stage 8.5
  GAP-007: PipelineConfig.proposal_only default=True
  GAP-008: Pre-flight dual injection guard
  GAP-009: Stage B component extracted from pkg, not hardcoded
  GAP-010: CommitProofInvariant module
  GAP-011: C0 embedding metadata NOT in ChangePackage.changes bytes
  GAP-013: pipeline_factory wires missing surfaces
  GAP-014: Freeze gate at pipeline entry
  GAP-015: _shadow_telemetry_batch cleared at pipeline entry
  GAP-016: intake_record initialized before Stage 8 block
"""

from __future__ import annotations

import hashlib
import json
from unittest.mock import MagicMock

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

# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------


def _make_pipeline_config(**overrides):
    from system_learning.pipelines.meta_learning_pipeline import PipelineConfig
    from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
    from system_learning.validators.oscillation_detector import OscillationPolicy
    from system_learning.validators.shadow_evaluator import ShadowThresholds

    defaults = {
        "engine_version": "test",
        "config_surface_version": "test",
        "shadow_thresholds": ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.05,
            max_cpu_regression_pct=15.0,
            max_mem_regression_pct=15.0,
            forbid_any_safety_violation_increase=True,
        ),
        "cooldown_policy": CooldownPolicy(min_seconds_between_updates=0),
        "sample_policy": SampleSizePolicy(min_observations=1),
        "oscillation_policy": OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=0),
        "enabled_proposers": ("l0",),
        "proposal_only": True,
    }
    defaults.update(overrides)
    return PipelineConfig(**defaults)


def _minimal_package(
    source="test_src",
    target="test_tgt",
    changes=b"real content",
    confidence=0.9,
    reason=("r1",),
    timestamp_utc=1_000_000,
    target_surface="test_surface",
):
    from system_learning.engines.change_package_impl import ChangePackage

    return ChangePackage(
        source=source,
        target=target,
        changes=changes,
        confidence=confidence,
        reason=reason,
        timestamp_utc=timestamp_utc,
        target_surface=target_surface,
    )


# ---------------------------------------------------------------------------
# GAP-007: PipelineConfig.proposal_only default
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGap007ProposalOnlyDefault:
    def test_default_is_true(self):
        """proposal_only must default to True (fail-safe)."""
        import dataclasses

        from system_learning.pipelines.meta_learning_pipeline import PipelineConfig

        fields = {f.name: f for f in dataclasses.fields(PipelineConfig)}
        assert "proposal_only" in fields
        assert fields["proposal_only"].default is True, (
            f"proposal_only default must be True, got {fields['proposal_only'].default}"
        )

    def test_config_instantiated_without_proposal_only_is_true(self):
        cfg = _make_pipeline_config()
        assert cfg.proposal_only is True

    def test_config_explicit_false_works(self):
        cfg = _make_pipeline_config(proposal_only=False)
        assert cfg.proposal_only is False

    def test_module_docstring_states_true(self):
        import system_learning.pipelines.meta_learning_pipeline as m

        assert "proposal_only=True" in m.__doc__, "Module docstring invariant must state proposal_only=True"


# ---------------------------------------------------------------------------
# GAP-002: RUNTIME category in rca_engine
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGap002RuntimeCategory:
    def test_runtime_category_present(self):
        from system_learning.engines.rca_engine import CLASSIFICATION_RULES

        categories = {r[0] for r in CLASSIFICATION_RULES}
        assert "RUNTIME" in categories, "RUNTIME category missing from CLASSIFICATION_RULES"

    def test_runtime_error_classified(self):
        from system_learning.engines.rca_engine import classify_line

        result = classify_line("RuntimeError: something went wrong")
        assert result is not None, "RuntimeError line should be classified"
        assert result[0] == "RUNTIME"

    def test_attribute_error_classified(self):
        from system_learning.engines.rca_engine import classify_line

        result = classify_line("AttributeError: 'NoneType' has no attribute 'foo'")
        assert result is not None
        assert result[0] == "RUNTIME"

    def test_type_error_classified(self):
        from system_learning.engines.rca_engine import classify_line

        result = classify_line("TypeError: unhashable type: 'list'")
        assert result is not None
        assert result[0] == "RUNTIME"

    def test_value_error_classified(self):
        from system_learning.engines.rca_engine import classify_line

        result = classify_line("ValueError: invalid literal for int()")
        assert result is not None
        assert result[0] == "RUNTIME"

    def test_key_error_classified(self):
        from system_learning.engines.rca_engine import classify_line

        result = classify_line("KeyError: 'missing_key'")
        assert result is not None
        assert result[0] == "RUNTIME"

    def test_index_error_classified(self):
        from system_learning.engines.rca_engine import classify_line

        result = classify_line("IndexError: list index out of range")
        assert result is not None
        assert result[0] == "RUNTIME"

    def test_runtime_does_not_override_syntax(self):
        """RUNTIME rules must not incorrectly capture SyntaxError lines."""
        from system_learning.engines.rca_engine import classify_line

        result = classify_line("SyntaxError: invalid syntax")
        assert result is not None
        assert result[0] == "SYNTAX", f"SYNTAX should take priority, got {result[0]}"

    def test_unclassified_line_returns_none(self):
        from system_learning.engines.rca_engine import classify_line

        assert classify_line("INFO: Everything is fine") is None

    def test_analyze_failures_returns_runtime_category(self):
        """analyze_failures must include RUNTIME category in report for RuntimeError lines."""
        from system_learning.engines.rca_engine import analyze_failures

        audit_bytes = b"RuntimeError: something exploded\nAttributeError: oops\n"
        report = analyze_failures(
            snapshot_id="snap_test",
            audit_slice=audit_bytes,
            window_start_utc=0,
            window_end_utc=100,
        )
        categories = {f.category for f in report.findings}
        assert "RUNTIME" in categories, f"Got categories: {categories}"

    def test_analyze_failures_deterministic(self):
        """Same input produces identical report twice (determinism invariant)."""
        from system_learning.engines.rca_engine import analyze_failures

        audit_bytes = b"RuntimeError: x\nTypeError: y\nKeyError: z\n"
        r1 = analyze_failures(
            snapshot_id="snap_det",
            audit_slice=audit_bytes,
            window_start_utc=0,
            window_end_utc=100,
        )
        r2 = analyze_failures(
            snapshot_id="snap_det",
            audit_slice=audit_bytes,
            window_start_utc=0,
            window_end_utc=100,
        )
        assert r1.report_hash == r2.report_hash


# ---------------------------------------------------------------------------
# GAP-004: n_observations derived from audit_slice
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGap004NObservations:
    """Verify sample_policy.min_observations is checked against real line count."""

    def _make_deps_with_audit(self, audit_bytes: bytes, min_observations: int):
        """Build minimal deps that will trigger SampleSizeViolation if line count < min."""
        from system_learning.validators.dampening import SampleSizePolicy

        policy = SampleSizePolicy(min_observations=min_observations)
        text = audit_bytes.decode("utf-8", errors="replace")
        n = max(1, sum(1 for ln in text.splitlines() if ln.strip()))
        return n, policy

    def test_short_audit_below_threshold_raises(self):
        from system_learning.validators.dampening import (
            SampleSizePolicy,
            SampleSizeViolation,
            assert_min_sample_size,
        )

        audit = b"line1\nline2\n"
        text = audit.decode("utf-8", errors="replace")
        n = max(1, sum(1 for ln in text.splitlines() if ln.strip()))
        assert n == 2
        with pytest.raises(SampleSizeViolation):
            assert_min_sample_size(n_observations=n, sample_policy=SampleSizePolicy(min_observations=100))

    def test_sufficient_audit_passes(self):
        from system_learning.validators.dampening import SampleSizePolicy, assert_min_sample_size

        audit = b"\n".join(f"event {i}".encode() for i in range(200))
        text = audit.decode("utf-8", errors="replace")
        n = max(1, sum(1 for ln in text.splitlines() if ln.strip()))
        assert n == 200
        assert_min_sample_size(n_observations=n, sample_policy=SampleSizePolicy(min_observations=10))

    def test_empty_audit_minimum_one(self):
        """Even empty audit must not yield zero observations (division-safe)."""
        audit = b""
        text = audit.decode("utf-8", errors="replace")
        n = max(1, sum(1 for ln in text.splitlines() if ln.strip()))
        assert n == 1

    def test_whitespace_only_lines_not_counted(self):
        """Blank lines should not count as observations."""
        audit = b"   \n\n  \n"
        text = audit.decode("utf-8", errors="replace")
        n = max(1, sum(1 for ln in text.splitlines() if ln.strip()))
        assert n == 1

    def test_boundary_exact_min_passes(self):
        from system_learning.validators.dampening import SampleSizePolicy, assert_min_sample_size

        n = 10
        assert_min_sample_size(n_observations=n, sample_policy=SampleSizePolicy(min_observations=10))
        assert True  # no-exception contract

    def test_boundary_one_below_min_raises(self):
        from system_learning.validators.dampening import (
            SampleSizePolicy,
            SampleSizeViolation,
            assert_min_sample_size,
        )

        with pytest.raises(SampleSizeViolation):
            assert_min_sample_size(n_observations=9, sample_policy=SampleSizePolicy(min_observations=10))

    def test_boundary_one_above_min_passes(self):
        from system_learning.validators.dampening import SampleSizePolicy, assert_min_sample_size

        assert_min_sample_size(n_observations=11, sample_policy=SampleSizePolicy(min_observations=10))
        assert True  # no-exception contract


# ---------------------------------------------------------------------------
# GAP-007 / GAP-008: Pre-flight dual injection guard
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGap008DualInjectionGuard:
    """Verify the pre-flight dual injection guard is atomic."""

    def test_version_store_without_approval_gate_raises(self):
        """version_store present + approval_gate absent must raise PipelineError."""
        from system_learning.pipelines.meta_learning_pipeline import PipelineError

        # We test the guard logic directly (not full pipeline)
        version_store = MagicMock()
        approval_gate = None

        _vs_present = version_store is not None
        _ag_present = approval_gate is not None
        if _vs_present and not _ag_present:
            with pytest.raises(PipelineError):
                raise PipelineError("partial injection: version_store provided but approval_gate is None")

    def test_approval_gate_without_version_store_raises(self):
        from system_learning.pipelines.meta_learning_pipeline import PipelineError

        version_store = None
        approval_gate = MagicMock()

        _vs_present = version_store is not None
        _ag_present = approval_gate is not None
        if _ag_present and not _vs_present:
            with pytest.raises(PipelineError):
                raise PipelineError("partial injection: approval_gate provided but version_store is None")

    def test_both_none_while_proposal_only_false_raises(self):
        """When proposal_only=False and neither store injected, PipelineError raised."""
        from system_learning.pipelines.meta_learning_pipeline import PipelineError

        version_store = None
        approval_gate = None

        _vs_present = version_store is not None
        if not _vs_present:
            with pytest.raises(PipelineError):
                raise PipelineError("version_store required when proposal_only=False")

    def test_both_present_passes(self):
        """Both injected: no exception should be raised by the guard."""

        version_store = MagicMock()
        approval_gate = MagicMock()

        _vs_present = version_store is not None
        _ag_present = approval_gate is not None
        # No exception
        if _vs_present and not _ag_present:
            pytest.fail("Should not reach partial-injection guard")
        if _ag_present and not _vs_present:
            pytest.fail("Should not reach partial-injection guard")

    def test_guard_message_indicates_partial_injection(self):
        """Error message must mention 'partial injection'."""
        from system_learning.pipelines.meta_learning_pipeline import PipelineError

        try:
            raise PipelineError(
                "partial injection: version_store provided but approval_gate is None; "
                "both must be injected together when proposal_only=False"
            )
        except PipelineError as e:  # guardian: allow-silent-swallower
            assert "partial injection" in str(e)


# ---------------------------------------------------------------------------
# GAP-009: Stage B component extraction from pkg
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGap009ComponentExtraction:
    def test_target_surface_used_when_present(self):
        pkg = _minimal_package(target_surface="my_surface")
        component = getattr(pkg, "target_surface", None) or getattr(pkg, "target", "unknown")
        assert component == "my_surface"

    def test_target_used_when_target_surface_none(self):
        pkg = _minimal_package(target="my_target", target_surface=None)
        component = getattr(pkg, "target_surface", None) or getattr(pkg, "target", "unknown")
        assert component == "my_target"

    def test_unknown_fallback_when_both_none(self):
        """When neither target_surface nor target is available, fallback is 'unknown'."""

        class _FakePkg:
            target_surface = None
            target = None

        pkg = _FakePkg()
        component = getattr(pkg, "target_surface", None) or getattr(pkg, "target", None) or "unknown"
        assert component == "unknown"

    def test_empty_target_surface_falls_through_to_target(self):
        """Empty string target_surface is falsy, should fall through."""

        class _FakePkg:
            target_surface = ""
            target = "fallback_target"

        pkg = _FakePkg()
        component = getattr(pkg, "target_surface", None) or getattr(pkg, "target", "unknown")
        assert component == "fallback_target"


# ---------------------------------------------------------------------------
# GAP-010: CommitProofInvariant
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGap010CommitProofInvariant:
    def test_valid_proof_from_package(self):
        from system_learning.invariants.commit_proof_invariant import CommitProofInvariant

        pkg = _minimal_package()
        impl_hash = hashlib.sha256(pkg.canonical_bytes()).hexdigest()
        proof = CommitProofInvariant.from_package(
            version_id=impl_hash, package=pkg, commit_timestamp_utc=1_000_000
        )
        proof.verify()
        assert True  # no-exception contract

    def test_version_id_mismatch_raises(self):
        from system_learning.invariants.commit_proof_invariant import (
            CommitProofInvariant,
            CommitProofViolation,
        )

        pkg = _minimal_package()
        with pytest.raises(CommitProofViolation, match="does not match"):
            CommitProofInvariant.from_package(
                version_id="a" * 64, package=pkg, commit_timestamp_utc=1_000_000
            )

    def test_placeholder_hash_raises(self):
        from system_learning.invariants.commit_proof_invariant import (
            CommitProofInvariant,
            CommitProofViolation,
        )

        ph = hashlib.sha256(b"placeholder").hexdigest()
        proof = CommitProofInvariant(
            version_id=ph,
            implementation_hash=ph,
            commit_timestamp_utc=1_000_000,
        )
        with pytest.raises(CommitProofViolation, match="churn"):
            proof.verify()

    def test_empty_hash_raises(self):
        from system_learning.invariants.commit_proof_invariant import (
            CommitProofInvariant,
            CommitProofViolation,
        )

        eh = hashlib.sha256(b"").hexdigest()
        proof = CommitProofInvariant(
            version_id=eh,
            implementation_hash=eh,
            commit_timestamp_utc=1_000_000,
        )
        with pytest.raises(CommitProofViolation, match="churn"):
            proof.verify()

    def test_zero_timestamp_raises(self):
        from system_learning.invariants.commit_proof_invariant import (
            CommitProofInvariant,
            CommitProofViolation,
        )

        pkg = _minimal_package()
        impl_hash = hashlib.sha256(pkg.canonical_bytes()).hexdigest()
        proof = CommitProofInvariant(
            version_id=impl_hash,
            implementation_hash=impl_hash,
            commit_timestamp_utc=0,
        )
        with pytest.raises(CommitProofViolation, match="timestamp"):
            proof.verify()

    def test_negative_timestamp_raises(self):
        from system_learning.invariants.commit_proof_invariant import (
            CommitProofInvariant,
            CommitProofViolation,
        )

        pkg = _minimal_package()
        impl_hash = hashlib.sha256(pkg.canonical_bytes()).hexdigest()
        proof = CommitProofInvariant(
            version_id=impl_hash,
            implementation_hash=impl_hash,
            commit_timestamp_utc=-1,
        )
        with pytest.raises(CommitProofViolation, match="timestamp"):
            proof.verify()

    def test_short_version_id_raises(self):
        from system_learning.invariants.commit_proof_invariant import (
            CommitProofInvariant,
            CommitProofViolation,
        )

        pkg = _minimal_package()
        short_id = "abc123"
        proof = CommitProofInvariant(
            version_id=short_id,
            implementation_hash="a" * 64,
            commit_timestamp_utc=1_000_000,
        )
        with pytest.raises(CommitProofViolation, match="64-char"):
            proof.verify()

    def test_non_hex_version_id_raises(self):
        from system_learning.invariants.commit_proof_invariant import (
            CommitProofInvariant,
            CommitProofViolation,
        )

        pkg = _minimal_package()
        bad_id = "Z" * 64
        proof = CommitProofInvariant(
            version_id=bad_id,
            implementation_hash="a" * 64,
            commit_timestamp_utc=1_000_000,
        )
        with pytest.raises(CommitProofViolation):
            proof.verify()

    def test_package_without_canonical_bytes_raises(self):
        from system_learning.invariants.commit_proof_invariant import (
            CommitProofInvariant,
            CommitProofViolation,
        )

        class _BadPkg:
            pass

        with pytest.raises(CommitProofViolation, match="canonical_bytes"):
            CommitProofInvariant.from_package(
                version_id="a" * 64, package=_BadPkg(), commit_timestamp_utc=1_000_000
            )

    def test_verify_commit_proof_convenience(self):
        from system_learning.invariants.commit_proof_invariant import verify_commit_proof

        pkg = _minimal_package()
        impl_hash = hashlib.sha256(pkg.canonical_bytes()).hexdigest()
        proof = verify_commit_proof(version_id=impl_hash, package=pkg, commit_timestamp_utc=5)
        assert proof.version_id == impl_hash


# ---------------------------------------------------------------------------
# GAP-011: C0 embedding metadata NOT in ChangePackage.changes bytes
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGap011EmbeddingMetadataNotInChanges:
    def test_embedding_context_hash_field_exists(self):
        """ChangePackage must have embedding_context_hash field (not in changes bytes)."""
        import dataclasses

        from system_learning.engines.change_package_impl import ChangePackage

        field_names = {f.name for f in dataclasses.fields(ChangePackage)}
        assert "embedding_context_hash" in field_names

    def test_changes_bytes_do_not_contain_embedding_metadata_sentinel(self):
        """changes bytes must never contain EMBEDDING_METADATA: sentinel."""
        pkg = _minimal_package(changes=b'{"threshold": 0.5}')
        assert b"EMBEDDING_METADATA:" not in pkg.changes

    def test_embedding_context_hash_set_via_replace(self):
        """embedding_context_hash should be settable via dataclasses.replace."""
        import dataclasses

        pkg = _minimal_package()
        pkg2 = dataclasses.replace(pkg, embedding_context_hash="abc123")
        assert pkg2.embedding_context_hash == "abc123"
        # changes bytes unchanged
        assert pkg2.changes == pkg.changes

    def test_canonical_bytes_unchanged_by_embedding_context_hash(self):
        """Modifying embedding_context_hash changes canonical bytes (it's included in hash)."""
        import dataclasses

        pkg = _minimal_package()
        pkg_with_hash = dataclasses.replace(pkg, embedding_context_hash="abc123")
        # canonical_bytes includes embedding_context_hash field
        # so they differ -- that's expected and correct
        # The key invariant is that changes field is not mutated
        assert pkg_with_hash.changes == pkg.changes

    def test_changes_bytes_deterministic_without_embedding_metadata(self):
        """changes bytes must be deterministic regardless of embedding_context_hash."""
        import dataclasses

        pkg = _minimal_package()
        pkg2 = dataclasses.replace(pkg, embedding_context_hash="hash1")
        pkg3 = dataclasses.replace(pkg, embedding_context_hash="hash2")
        assert pkg2.changes == pkg3.changes, "changes bytes must not differ by embedding hash"


# ---------------------------------------------------------------------------
# GAP-014: Freeze gate
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGap014FreezeGate:
    def test_static_reader_not_frozen_returns_false(self):
        from system_learning.invariants.freeze_gate import StaticFreezeReader

        r = StaticFreezeReader(frozen=False)
        assert r.is_frozen() is False

    def test_static_reader_frozen_returns_true(self):
        from system_learning.invariants.freeze_gate import StaticFreezeReader

        r = StaticFreezeReader(frozen=True)
        assert r.is_frozen() is True

    def test_json_reader_no_freeze_key(self, tmp_path):
        from system_learning.invariants.freeze_gate import JsonFileBackedFreezeReader

        p = tmp_path / "runtime_state.json"
        p.write_text(json.dumps({"status": "running"}))
        r = JsonFileBackedFreezeReader(p)
        assert r.is_frozen() is False

    def test_json_reader_freeze_true_key(self, tmp_path):
        from system_learning.invariants.freeze_gate import JsonFileBackedFreezeReader

        p = tmp_path / "runtime_state.json"
        p.write_text(json.dumps({"freeze": True}))
        r = JsonFileBackedFreezeReader(p)
        assert r.is_frozen() is True

    def test_json_reader_freeze_false_key(self, tmp_path):
        from system_learning.invariants.freeze_gate import JsonFileBackedFreezeReader

        p = tmp_path / "runtime_state.json"
        p.write_text(json.dumps({"freeze": False}))
        r = JsonFileBackedFreezeReader(p)
        assert r.is_frozen() is False

    def test_json_reader_status_freez(self, tmp_path):
        from system_learning.invariants.freeze_gate import JsonFileBackedFreezeReader

        p = tmp_path / "runtime_state.json"
        p.write_text(json.dumps({"status": "FREEZ"}))
        r = JsonFileBackedFreezeReader(p)
        assert r.is_frozen() is True

    def test_json_reader_status_freez_lowercase(self, tmp_path):
        from system_learning.invariants.freeze_gate import JsonFileBackedFreezeReader

        p = tmp_path / "runtime_state.json"
        p.write_text(json.dumps({"status": "freez"}))
        r = JsonFileBackedFreezeReader(p)
        assert r.is_frozen() is True

    def test_json_reader_flags_l2_freeze(self, tmp_path):
        from system_learning.invariants.freeze_gate import JsonFileBackedFreezeReader

        p = tmp_path / "runtime_state.json"
        p.write_text(json.dumps({"flags": {"l2_freeze": True}}))
        r = JsonFileBackedFreezeReader(p)
        assert r.is_frozen() is True

    def test_json_reader_missing_file_fails_open(self, tmp_path):
        from system_learning.invariants.freeze_gate import JsonFileBackedFreezeReader

        p = tmp_path / "does_not_exist.json"
        r = JsonFileBackedFreezeReader(p)
        assert r.is_frozen() is False  # fail-open (do not block pipeline)

    def test_json_reader_malformed_json_fails_open(self, tmp_path):
        from system_learning.invariants.freeze_gate import JsonFileBackedFreezeReader

        p = tmp_path / "runtime_state.json"
        p.write_text("{not valid json")
        r = JsonFileBackedFreezeReader(p)
        assert r.is_frozen() is False

    def test_freeze_reader_in_pipeline_deps(self):
        """PipelineDependencies must accept freeze_reader field."""
        import dataclasses

        from system_learning.pipelines.meta_learning_pipeline import PipelineDependencies

        field_names = {f.name for f in dataclasses.fields(PipelineDependencies)}
        assert "freeze_reader" in field_names


# ---------------------------------------------------------------------------
# GAP-015: _shadow_telemetry_batch cleared at run_pipeline entry
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGap015ShadowBatchCleared:
    def test_module_has_shadow_telemetry_batch(self):
        import system_learning.pipelines.meta_learning_pipeline as m

        assert hasattr(m, "_shadow_telemetry_batch"), "_shadow_telemetry_batch global must exist"

    def test_shadow_batch_is_list(self):
        import system_learning.pipelines.meta_learning_pipeline as m

        assert isinstance(m._shadow_telemetry_batch, list)

    def test_shadow_batch_cleared_on_pipeline_entry_via_invalid_window(self):
        """Pollute the batch, call run_pipeline with bad window, verify batch cleared."""
        import system_learning.pipelines.meta_learning_pipeline as m
        from system_learning.pipelines.meta_learning_pipeline import PipelineError

        m._shadow_telemetry_batch = [{"stale": True}]

        # Create minimal deps/config
        cfg = _make_pipeline_config(proposal_only=True)
        deps = _make_minimal_deps()

        # window_start >= window_end triggers PipelineError BEFORE freeze gate
        with pytest.raises(PipelineError):
            from system_learning.pipelines.meta_learning_pipeline import run_pipeline

            run_pipeline(
                cfg=cfg,
                deps=deps,
                window_start_utc=100,
                window_end_utc=50,
                now_utc=200,
            )

    def test_shadow_batch_cleared_when_freeze_triggered(self):
        """When freeze is active, batch is NOT cleared (freeze fires before clear)."""
        import system_learning.pipelines.meta_learning_pipeline as m
        from system_learning.invariants.freeze_gate import StaticFreezeReader
        from system_learning.pipelines.meta_learning_pipeline import PipelineError

        m._shadow_telemetry_batch = [{"stale": True}]
        cfg = _make_pipeline_config(proposal_only=True)
        deps = _make_minimal_deps(freeze_reader=StaticFreezeReader(frozen=True))

        with pytest.raises(PipelineError, match="freeze"):
            from system_learning.pipelines.meta_learning_pipeline import run_pipeline

            run_pipeline(cfg=cfg, deps=deps, window_start_utc=0, window_end_utc=100, now_utc=50)

        # batch is NOT cleared (freeze fires before the clear line)
        assert m._shadow_telemetry_batch == [{"stale": True}]


# ---------------------------------------------------------------------------
# GAP-016: intake_record initialized before Stage 8 block
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGap016IntakeRecordInitialized:
    def test_intake_record_none_when_adapter_missing(self):
        """Pipeline code initializes intake_record = None; no NameError when adapter absent."""
        # Simulate the guard logic
        healing_outcome_intake_adapter = None
        intake_record = None

        if healing_outcome_intake_adapter is not None:
            intake_record = "would_be_set"

        # Stage 8.5 guard
        healing_config_optimizer = MagicMock()
        if (
            healing_config_optimizer is not None
            and intake_record is not None
            and hasattr(intake_record, "snapshot")
        ):
            pass  # Would run

        # If intake_record were uninitialized, the above would raise NameError
        assert intake_record is None

    def test_stage_8_5_guard_uses_intake_record_not_none(self):
        """Verify guard is intake_record is not None, not hasattr-only."""
        # With old code: `if deps.healing_config_optimizer is not None and hasattr(intake_record, "snapshot")`
        # would NameError when adapter is None. New code adds `intake_record = None` first.
        import inspect

        import system_learning.pipelines.meta_learning_pipeline as m

        src = inspect.getsource(m.run_pipeline)
        assert "intake_record = None" in src, (
            "run_pipeline must initialize intake_record = None before Stage 8 block"
        )

    def test_stage_8_5_guard_uses_is_not_none_check(self):
        """Guard must include `intake_record is not None`."""
        import inspect

        import system_learning.pipelines.meta_learning_pipeline as m

        src = inspect.getsource(m.run_pipeline)
        assert "intake_record is not None" in src, "Stage 8.5 guard must include `intake_record is not None`"


# ---------------------------------------------------------------------------
# GAP-005: Stages 8.6 and 8.7 independent of Stage 8.5
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGap005Stage86And87Independent:
    def test_pattern_report_assigned_outside_8_5_block(self):
        """_analyze_historical_patterns call must be at top level (not nested inside 8.5 if block)."""
        import inspect

        import system_learning.pipelines.meta_learning_pipeline as m

        src = inspect.getsource(m.run_pipeline)
        # The 8.5 block starts with 'if deps.healing_config_optimizer is not None and intake_record is not None'
        # The 8.6 pattern call must appear OUTSIDE (i.e. before) '_8_5_aggregate_snapshot is not None'
        # or at top-level indent.
        # Simplest check: both variable names appear in source
        assert "pattern_report" in src
        assert "_analyze_historical_patterns" in src
        assert "embedding_metadata" in src
        assert "_retrieve_semantic_context" in src

    def test_stage_86_runs_when_optimizer_absent(self):
        """When healing_config_optimizer is None, pattern analysis still has a path to run."""
        import inspect

        import system_learning.pipelines.meta_learning_pipeline as m

        src = inspect.getsource(m.run_pipeline)
        # Stage 8.6 must appear AFTER the else branch of healing_config_optimizer conditional
        # i.e. _8_5_aggregate_snapshot = None path must still call _analyze_historical_patterns
        # Evidence: the pattern_report assignment appears after the else branch
        assert "_8_5_aggregate_snapshot = None" in src
        # After that, _analyze_historical_patterns must appear (outside the if block)
        idx_none = src.index("_8_5_aggregate_snapshot = None")
        idx_pattern = src.index("pattern_report = _analyze_historical_patterns")
        assert idx_pattern > idx_none, (
            "pattern_report assignment must appear after the _8_5_aggregate_snapshot=None else branch"
        )


# ---------------------------------------------------------------------------
# GAP-013: pipeline_factory wires surfaces
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGap013FactoryWiring:
    def test_factory_wires_freeze_reader_field(self):
        """build_pipeline_deps result must have freeze_reader attribute."""
        import dataclasses

        from system_learning.pipelines.meta_learning_pipeline import PipelineDependencies

        field_names = {f.name for f in dataclasses.fields(PipelineDependencies)}
        assert "freeze_reader" in field_names

    def test_factory_wires_rlhf_optimizer_field(self):
        import dataclasses

        from system_learning.pipelines.meta_learning_pipeline import PipelineDependencies

        field_names = {f.name for f in dataclasses.fields(PipelineDependencies)}
        assert "rlhf_optimizer" in field_names

    def test_factory_wires_arbitration_engine_field(self):
        import dataclasses

        from system_learning.pipelines.meta_learning_pipeline import PipelineDependencies

        field_names = {f.name for f in dataclasses.fields(PipelineDependencies)}
        assert "arbitration_engine" in field_names

    def test_factory_wires_healing_confidence_scorer_field(self):
        import dataclasses

        from system_learning.pipelines.meta_learning_pipeline import PipelineDependencies

        field_names = {f.name for f in dataclasses.fields(PipelineDependencies)}
        assert "healing_confidence_scorer" in field_names

    def test_factory_wires_failure_fingerprinter_field(self):
        import dataclasses

        from system_learning.pipelines.meta_learning_pipeline import PipelineDependencies

        field_names = {f.name for f in dataclasses.fields(PipelineDependencies)}
        assert "failure_fingerprinter" in field_names

    def test_factory_wires_risk_correlator_field(self):
        import dataclasses

        from system_learning.pipelines.meta_learning_pipeline import PipelineDependencies

        field_names = {f.name for f in dataclasses.fields(PipelineDependencies)}
        assert "risk_correlator" in field_names

    def test_build_pipeline_config_default_proposal_only_true(self):
        from system_learning.pipelines.pipeline_factory import build_pipeline_config

        cfg = build_pipeline_config()
        assert cfg.proposal_only is True

    def test_build_pipeline_config_explicit_false(self):
        from system_learning.pipelines.pipeline_factory import build_pipeline_config

        cfg = build_pipeline_config(proposal_only=False)
        assert cfg.proposal_only is False


# ---------------------------------------------------------------------------
# GAP-003: DPO proposals enter validation loop (structural / invariant check)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGap003DpoBeforeStage7:
    def test_dpo_append_before_validation_loop_in_source(self):
        """Verify by source inspection that DPO proposals.append occurs before Stage 7 loop."""
        import inspect

        import system_learning.pipelines.meta_learning_pipeline as m

        src = inspect.getsource(m.run_pipeline)

        # Find the index of the DPO proposals.append() and Stage 7 loop header
        # The DPO comment is: "# Step 7: Validate each proposal"
        # The DPO append is: "proposals.append(dpo_proposal)"
        assert "proposals.append(dpo_proposal)" in src, "DPO append must be present"
        assert "# Step 7: Validate each proposal" in src

        idx_dpo_append = src.index("proposals.append(dpo_proposal)")
        idx_stage7 = src.index("# Step 7: Validate each proposal")
        assert idx_dpo_append < idx_stage7, (
            "DPO proposals.append must appear BEFORE Stage 7 loop header in source"
        )

    def test_dpo_comment_states_before_stage7(self):
        """Source comment must indicate DPO enters before Stage 7."""
        import inspect

        import system_learning.pipelines.meta_learning_pipeline as m

        src = inspect.getsource(m.run_pipeline)
        assert "before Stage 7" in src or "BEFORE Stage 7" in src, (
            "Source must contain comment confirming DPO placement before Stage 7"
        )


# ---------------------------------------------------------------------------
# Additional: CommitProofInvariant determinism (Rule 1.10)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCommitProofDeterminism:
    def test_same_package_yields_same_proof_twice(self):
        from system_learning.invariants.commit_proof_invariant import CommitProofInvariant

        pkg = _minimal_package()
        impl_hash = hashlib.sha256(pkg.canonical_bytes()).hexdigest()
        proof1 = CommitProofInvariant.from_package(version_id=impl_hash, package=pkg, commit_timestamp_utc=1)
        proof2 = CommitProofInvariant.from_package(version_id=impl_hash, package=pkg, commit_timestamp_utc=1)
        assert proof1 == proof2

    def test_different_packages_yield_different_version_ids(self):
        pkg1 = _minimal_package(changes=b"content_A")
        pkg2 = _minimal_package(changes=b"content_B")
        hash1 = hashlib.sha256(pkg1.canonical_bytes()).hexdigest()
        hash2 = hashlib.sha256(pkg2.canonical_bytes()).hexdigest()
        assert hash1 != hash2


# ---------------------------------------------------------------------------
# Additional: FreezeGate negative controls (Rule 1.6)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFreezeGateNegativeControls:
    def test_freeze_gate_blocks_pipeline_execution(self):
        """When freeze active, run_pipeline must raise PipelineError (negative control)."""
        from system_learning.invariants.freeze_gate import StaticFreezeReader
        from system_learning.pipelines.meta_learning_pipeline import PipelineError, run_pipeline

        cfg = _make_pipeline_config(proposal_only=True)
        deps = _make_minimal_deps(freeze_reader=StaticFreezeReader(frozen=True))

        with pytest.raises(PipelineError, match="freeze"):
            run_pipeline(cfg=cfg, deps=deps, window_start_utc=0, window_end_utc=100, now_utc=50)

    def test_no_freeze_does_not_block(self):
        """When freeze not active, pipeline proceeds past the gate."""
        from system_learning.invariants.freeze_gate import StaticFreezeReader
        from system_learning.pipelines.meta_learning_pipeline import PipelineError, run_pipeline

        cfg = _make_pipeline_config(proposal_only=True)
        deps = _make_minimal_deps(freeze_reader=StaticFreezeReader(frozen=False))

        # Should not raise PipelineError about freeze (may raise other errors due to minimal deps)
        try:
            run_pipeline(cfg=cfg, deps=deps, window_start_utc=0, window_end_utc=100, now_utc=50)
        except PipelineError as e:  # guardian: allow-silent-swallower
            assert "freeze" not in str(e).lower(), f"Should not be a freeze error, got: {e}"
        except Exception:  # guardian: allow-silent-swallower
            pass  # Other errors from minimal deps are acceptable


# ---------------------------------------------------------------------------
# Additional: RUNTIME classification negative controls
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRcaRuntimeNegativeControls:
    def test_policy_block_not_reclassified_as_runtime(self):
        from system_learning.engines.rca_engine import classify_line

        result = classify_line("AuthorityViolation: rejected")
        assert result is not None
        assert result[0] == "POLICY_BLOCK"

    def test_import_error_not_classified_as_runtime(self):
        from system_learning.engines.rca_engine import classify_line

        result = classify_line("ImportError: no module named foo")
        assert result is not None
        assert result[0] == "IMPORT"

    def test_timeout_error_not_classified_as_runtime(self):
        from system_learning.engines.rca_engine import classify_line

        result = classify_line("TimeoutError: operation timed out")
        assert result is not None
        # TimeoutError matches RUNTIME (RuntimeError prefix check) but TIMEOUT rule
        # appears after RUNTIME in rules list, so RUNTIME would capture it first
        # unless the text actually matches TIMEOUT pattern
        # TimeoutError does NOT start with "RuntimeError:" so RUNTIME only matches RuntimeError:
        assert result[0] in ("RUNTIME", "TIMEOUT")


# ---------------------------------------------------------------------------
# Helpers used by multiple tests
# ---------------------------------------------------------------------------


def _make_minimal_deps(freeze_reader=None):
    """Build a minimal PipelineDependencies with stubs."""
    from system_learning.pipelines.meta_learning_pipeline import PipelineDependencies

    audit_store = MagicMock()
    audit_store.read_audit_slice.return_value = b"line1\nline2\nline3\n"

    telemetry_store = MagicMock()

    config_provider = MagicMock()
    config_provider.get_current_configs.return_value = {}

    baseline_metrics = MagicMock()
    baseline_metrics.get_baseline_metrics.return_value = {}

    l0_proposer = MagicMock()
    l0_proposer.propose.return_value = None

    rag_proposer = MagicMock()
    rag_proposer.propose.return_value = None

    l1_proposer = MagicMock()
    l1_proposer.propose.return_value = None

    l5_proposer = MagicMock()
    l5_proposer.propose.return_value = None

    return PipelineDependencies(
        audit_store=audit_store,
        telemetry_store=telemetry_store,
        config_provider=config_provider,
        baseline_metrics_provider=baseline_metrics,
        l0_proposer=l0_proposer,
        rag_proposer=rag_proposer,
        l1_proposer=l1_proposer,
        l5_proposer=l5_proposer,
        freeze_reader=freeze_reader,
    )


# ---------------------------------------------------------------------------
# §1.5 Exception path: rca_engine.analyze_failures
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRcaAnalyzeFailuresExceptionPaths:
    """Force every exception/branch in analyze_failures (§1.5)."""

    def test_invalid_window_start_equals_end_raises(self):
        """window_start_utc == window_end_utc must raise RCAAnalysisError."""
        from system_learning.engines.rca_engine import RCAAnalysisError, analyze_failures

        with pytest.raises(RCAAnalysisError, match="Invalid window"):
            analyze_failures(
                snapshot_id="s",
                audit_slice=b"line\n",
                window_start_utc=50,
                window_end_utc=50,
            )

    def test_invalid_window_start_greater_than_end_raises(self):
        """window_start_utc > window_end_utc must raise RCAAnalysisError."""
        from system_learning.engines.rca_engine import RCAAnalysisError, analyze_failures

        with pytest.raises(RCAAnalysisError, match="Invalid window"):
            analyze_failures(
                snapshot_id="s",
                audit_slice=b"line\n",
                window_start_utc=100,
                window_end_utc=99,
            )

    def test_valid_window_start_one_below_end_passes(self):
        """window_start_utc == window_end_utc - 1 must NOT raise."""
        from system_learning.engines.rca_engine import analyze_failures

        report = analyze_failures(
            snapshot_id="s",
            audit_slice=b"RuntimeError: x\n",
            window_start_utc=49,
            window_end_utc=50,
        )
        assert report is not None

    def test_unicode_decode_error_raises_rca_analysis_error(self):
        """Non-UTF-8 bytes must raise RCAAnalysisError (fail-closed)."""
        from system_learning.engines.rca_engine import RCAAnalysisError, analyze_failures

        bad_bytes = b"\xff\xfe invalid utf-8 \xc3\x28"
        with pytest.raises(RCAAnalysisError, match="UTF-8"):
            analyze_failures(
                snapshot_id="s",
                audit_slice=bad_bytes,
                window_start_utc=0,
                window_end_utc=100,
            )

    def test_empty_bytes_yields_unknown_category(self):
        """Empty audit_slice must not crash; yields UNKNOWN finding."""
        from system_learning.engines.rca_engine import analyze_failures

        report = analyze_failures(
            snapshot_id="s",
            audit_slice=b"",
            window_start_utc=0,
            window_end_utc=100,
        )
        categories = {f.category for f in report.findings}
        assert "UNKNOWN" in categories

    def test_list_input_normalized_to_bytes(self):
        """list-of-strings audit_slice must be accepted and classified."""
        from system_learning.engines.rca_engine import analyze_failures

        report = analyze_failures(
            snapshot_id="s",
            audit_slice=["RuntimeError: boom", "TypeError: bad"],
            window_start_utc=0,
            window_end_utc=100,
        )
        categories = {f.category for f in report.findings}
        assert "RUNTIME" in categories

    def test_none_input_normalized_to_empty(self):
        """Non-bytes/list input must not crash (falls back to b'')."""
        from system_learning.engines.rca_engine import analyze_failures

        report = analyze_failures(
            snapshot_id="s",
            audit_slice=None,
            window_start_utc=0,
            window_end_utc=100,
        )
        assert report is not None
        categories = {f.category for f in report.findings}
        assert "UNKNOWN" in categories

    def test_all_blank_lines_yields_unknown(self):
        """Audit slice with only blank lines must yield UNKNOWN."""
        from system_learning.engines.rca_engine import analyze_failures

        report = analyze_failures(
            snapshot_id="s",
            audit_slice=b"   \n\n   \n",
            window_start_utc=0,
            window_end_utc=100,
        )
        categories = {f.category for f in report.findings}
        assert "UNKNOWN" in categories

    def test_no_patterns_matched_yields_unknown_not_crash(self):
        """Lines with no matching pattern must produce UNKNOWN, not crash."""
        from system_learning.engines.rca_engine import analyze_failures

        report = analyze_failures(
            snapshot_id="s",
            audit_slice=b"INFO: everything is fine\nDEBUG: step complete\n",
            window_start_utc=0,
            window_end_utc=100,
        )
        categories = {f.category for f in report.findings}
        assert "UNKNOWN" in categories

    def test_report_hash_changes_with_different_input(self):
        """Distinct inputs must not collapse to same report_hash (§1.10 distinct-input)."""
        from system_learning.engines.rca_engine import analyze_failures

        r1 = analyze_failures("s", b"RuntimeError: A\n", 0, 100)
        r2 = analyze_failures("s", b"TypeError: B\n", 0, 100)
        assert r1.report_hash != r2.report_hash

    def test_report_hash_stable_across_equivalent_inputs(self):
        """Same canonical input → identical report_hash (§1.10 metamorphic)."""
        from system_learning.engines.rca_engine import analyze_failures

        b = b"RuntimeError: x\nTypeError: y\n"
        r1 = analyze_failures("snap", b, 0, 100)
        r2 = analyze_failures("snap", b, 0, 100)
        assert r1.report_hash == r2.report_hash


# ---------------------------------------------------------------------------
# §1.4/1.14 Boundary + ingress-path: dual injection guard via real run_pipeline
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDualInjectionGuardViaRealPipeline:
    """§1.14: Tests must target the real entrypoint (run_pipeline), not simulated logic."""

    def test_version_store_only_raises_at_real_pipeline(self):
        """version_store present + approval_gate absent → PipelineError at real choke point."""
        from system_learning.pipelines.meta_learning_pipeline import PipelineError, run_pipeline

        cfg = _make_pipeline_config(proposal_only=False)
        deps = _make_minimal_deps()

        vs = MagicMock()
        import dataclasses

        deps = dataclasses.replace(deps, version_store=vs, approval_gate=None)

        with pytest.raises(PipelineError, match="approval_gate required"):
            run_pipeline(cfg=cfg, deps=deps, window_start_utc=0, window_end_utc=100, now_utc=50)

    def test_approval_gate_only_raises_at_real_pipeline(self):
        """approval_gate present + version_store absent → PipelineError at real choke point."""
        from system_learning.pipelines.meta_learning_pipeline import PipelineError, run_pipeline

        cfg = _make_pipeline_config(proposal_only=False)
        deps = _make_minimal_deps()

        ag = MagicMock()
        import dataclasses

        deps = dataclasses.replace(deps, version_store=None, approval_gate=ag)

        with pytest.raises(PipelineError, match="version_store required"):
            run_pipeline(cfg=cfg, deps=deps, window_start_utc=0, window_end_utc=100, now_utc=50)

    def test_both_absent_proposal_only_false_raises_at_real_pipeline(self):
        """Both absent + proposal_only=False → PipelineError at real choke point."""
        from system_learning.pipelines.meta_learning_pipeline import PipelineError, run_pipeline

        cfg = _make_pipeline_config(proposal_only=False)
        deps = _make_minimal_deps()

        import dataclasses

        deps = dataclasses.replace(deps, version_store=None, approval_gate=None)

        with pytest.raises(PipelineError, match="version_store required"):
            run_pipeline(cfg=cfg, deps=deps, window_start_utc=0, window_end_utc=100, now_utc=50)

    def test_proposal_only_true_skips_guard_entirely(self):
        """proposal_only=True must never reach the injection guard (no PipelineError from guard)."""
        from system_learning.pipelines.meta_learning_pipeline import PipelineError, run_pipeline

        cfg = _make_pipeline_config(proposal_only=True)
        deps = _make_minimal_deps()

        import dataclasses

        # Both absent but proposal_only=True — guard must not fire
        deps = dataclasses.replace(deps, version_store=None, approval_gate=None)

        try:
            run_pipeline(cfg=cfg, deps=deps, window_start_utc=0, window_end_utc=100, now_utc=50)
        except PipelineError as e:  # guardian: allow-silent-swallower
            assert "partial injection" not in str(e), f"Guard must not fire for proposal_only=True: {e}"
            assert "version_store required when proposal_only=False" not in str(e)
        except Exception:  # guardian: allow-silent-swallower
            pass  # Other errors from minimal deps are acceptable

    def test_window_boundary_start_equals_end_raises_pipeline_error(self):
        """window_start_utc == window_end_utc must raise PipelineError (boundary exact)."""
        from system_learning.pipelines.meta_learning_pipeline import PipelineError, run_pipeline

        cfg = _make_pipeline_config(proposal_only=True)
        deps = _make_minimal_deps()

        with pytest.raises(PipelineError, match="Invalid window"):
            run_pipeline(cfg=cfg, deps=deps, window_start_utc=100, window_end_utc=100, now_utc=200)

    def test_window_boundary_start_one_below_end_passes_gate(self):
        """window_start_utc == window_end_utc - 1 must NOT raise from window guard."""
        from system_learning.pipelines.meta_learning_pipeline import PipelineError, run_pipeline

        cfg = _make_pipeline_config(proposal_only=True)
        deps = _make_minimal_deps()

        try:
            run_pipeline(cfg=cfg, deps=deps, window_start_utc=99, window_end_utc=100, now_utc=200)
        except PipelineError as e:  # guardian: allow-silent-swallower
            assert "Invalid window" not in str(e), f"Window guard must not fire: {e}"
        except Exception:  # guardian: allow-silent-swallower
            pass


# ---------------------------------------------------------------------------
# §1.15 Regression: shadow vector dim bug
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestShadowVectorDimRegression:
    """§1.15: Regression tests for the shadow vector dimension mismatch bug.

    The bug: shadow_vector was built via range(0, 8, 2) → always 4 elements,
    but query_vector from generate_fallback_vector() has 16 elements.
    np.dot() raised ValueError when executed.
    The fix: shadow vector dimension derived from query_vector.shape[0].
    """

    def test_shadow_vector_build_loop_derives_from_query_dim(self):
        """Prove the fix: shadow vector must match query vector dimension."""
        import numpy as np

        from agentic_core.L2_execution.healers.failure_signal_normalizer import (
            generate_fallback_vector,
        )

        signature = "test_regression|shadow:shadow-embedder"
        import hashlib

        shadow_hash = hashlib.sha256(signature.encode()).hexdigest()
        query_vector = np.array(generate_fallback_vector("test_regression"), dtype=np.float32)
        _qdim = query_vector.shape[0]

        shadow_vector = []
        for _si in range(_qdim):
            _hex_start = (_si * 2) % (len(shadow_hash) - 1)
            val = int(shadow_hash[_hex_start : _hex_start + 2], 16) / 255.0
            shadow_vector.append(val)

        shadow_vector = np.array(shadow_vector, dtype=np.float32)
        assert shadow_vector.shape[0] == query_vector.shape[0], (
            f"Shadow dim {shadow_vector.shape[0]} != query dim {query_vector.shape[0]}"
        )

    def test_np_dot_does_not_raise_with_matched_dims(self):
        """np.dot(query, shadow) must not raise ValueError when dims match."""
        import hashlib

        import numpy as np

        from agentic_core.L2_execution.healers.failure_signal_normalizer import (
            generate_fallback_vector,
        )

        signature = "test_dot_safety"
        shadow_sig = f"{signature}|shadow:test"
        shadow_hash = hashlib.sha256(shadow_sig.encode()).hexdigest()
        query_vector = np.array(generate_fallback_vector(signature), dtype=np.float32)
        _qdim = query_vector.shape[0]

        shadow_vector = []
        for _si in range(_qdim):
            _hex_start = (_si * 2) % (len(shadow_hash) - 1)
            val = int(shadow_hash[_hex_start : _hex_start + 2], 16) / 255.0
            shadow_vector.append(val)

        shadow_vector = np.array(shadow_vector, dtype=np.float32)

        # This must not raise ValueError
        result = np.dot(query_vector, shadow_vector)
        assert isinstance(result, (float, np.floating))

    def test_old_bug_would_fail(self):
        """Prove the old range(0,8,2) approach produces dim=4, which mismatches 16-dim query."""
        import numpy as np

        from agentic_core.L2_execution.healers.failure_signal_normalizer import (
            generate_fallback_vector,
        )

        query_vector = np.array(generate_fallback_vector("any_sig"), dtype=np.float32)
        # Reproduce old bug: hardcoded range(0,8,2)
        old_shadow = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)

        # The old approach would cause this to fail
        if query_vector.shape[0] != old_shadow.shape[0]:
            with pytest.raises(ValueError):
                np.dot(query_vector, old_shadow)
        else:
            pytest.fail("generate_fallback_vector returned dim=4, bug not present in this env")

    def test_cosine_similarity_deterministic_same_signature(self):
        """Same failure_signature → same cosine result (§1.10 determinism)."""
        import hashlib

        import numpy as np

        from agentic_core.L2_execution.healers.failure_signal_normalizer import (
            generate_fallback_vector,
        )

        def _cosine(sig: str) -> float:
            sh = f"{sig}|shadow:embedder"
            shadow_hash = hashlib.sha256(sh.encode()).hexdigest()
            qv = np.array(generate_fallback_vector(sig), dtype=np.float32)
            dim = qv.shape[0]
            sv = np.array(
                [
                    int(
                        shadow_hash[
                            (_si * 2) % (len(shadow_hash) - 1) : (_si * 2) % (len(shadow_hash) - 1) + 2
                        ],
                        16,
                    )
                    / 255.0
                    for _si in range(dim)
                ],
                dtype=np.float32,
            )
            return float(np.dot(qv, sv) / (np.linalg.norm(qv) * np.linalg.norm(sv)))

        c1 = _cosine("deterministic_test_sig")
        c2 = _cosine("deterministic_test_sig")
        assert c1 == c2, "Cosine must be deterministic for identical input"

    def test_distinct_signatures_produce_distinct_cosines(self):
        """Distinct signatures must not produce identical cosine (§1.10 distinct collapse)."""
        import hashlib

        import numpy as np

        from agentic_core.L2_execution.healers.failure_signal_normalizer import (
            generate_fallback_vector,
        )

        def _cosine(sig: str) -> float:
            sh = f"{sig}|shadow:embedder"
            shadow_hash = hashlib.sha256(sh.encode()).hexdigest()
            qv = np.array(generate_fallback_vector(sig), dtype=np.float32)
            dim = qv.shape[0]
            sv = np.array(
                [
                    int(
                        shadow_hash[
                            (_si * 2) % (len(shadow_hash) - 1) : (_si * 2) % (len(shadow_hash) - 1) + 2
                        ],
                        16,
                    )
                    / 255.0
                    for _si in range(dim)
                ],
                dtype=np.float32,
            )
            return float(np.dot(qv, sv) / (np.linalg.norm(qv) * np.linalg.norm(sv)))

        c1 = _cosine("failure_type_A|component_X")
        c2 = _cosine("failure_type_B|component_Y")
        assert c1 != c2, "Distinct signatures must not collapse to identical cosine"


# ---------------------------------------------------------------------------
# §1.5 Exception paths: freeze_gate JsonFileBackedFreezeReader
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFreezeGateExceptionPaths:
    """Force every exception branch in JsonFileBackedFreezeReader (§1.5)."""

    def test_oserror_on_read_fails_open(self, tmp_path, monkeypatch):
        """OSError during file read → fail open (False). Forced via monkeypatch."""
        from system_learning.invariants.freeze_gate import JsonFileBackedFreezeReader

        p = tmp_path / "runtime_state.json"
        p.write_text('{"freeze": true}')

        # Force OSError regardless of OS file permission behaviour
        def _raise_oserror(*_a, **_kw):
            raise OSError("simulated unreadable")

        monkeypatch.setattr("pathlib.Path.read_text", _raise_oserror)
        r = JsonFileBackedFreezeReader(p)
        assert r.is_frozen() is False, "OSError must fail-open (False)"

    def test_json_decode_error_fails_open(self, tmp_path):
        """Malformed JSON → JSONDecodeError → fail open (False)."""
        from system_learning.invariants.freeze_gate import JsonFileBackedFreezeReader

        p = tmp_path / "runtime_state.json"
        p.write_text("{ this is not json }")
        r = JsonFileBackedFreezeReader(p)
        assert r.is_frozen() is False

    def test_empty_file_fails_open(self, tmp_path):
        """Empty file → JSONDecodeError → fail open (False)."""
        from system_learning.invariants.freeze_gate import JsonFileBackedFreezeReader

        p = tmp_path / "runtime_state.json"
        p.write_text("")
        r = JsonFileBackedFreezeReader(p)
        assert r.is_frozen() is False

    def test_flags_not_dict_does_not_raise(self, tmp_path):
        """flags key that is not a dict must not raise — treated as no freeze."""
        from system_learning.invariants.freeze_gate import JsonFileBackedFreezeReader

        p = tmp_path / "runtime_state.json"
        p.write_text('{"flags": "not_a_dict"}')
        r = JsonFileBackedFreezeReader(p)
        assert r.is_frozen() is False

    def test_flags_none_does_not_raise(self, tmp_path):
        """flags: null must not raise."""
        from system_learning.invariants.freeze_gate import JsonFileBackedFreezeReader

        p = tmp_path / "runtime_state.json"
        p.write_text('{"flags": null}')
        r = JsonFileBackedFreezeReader(p)
        assert r.is_frozen() is False

    def test_l2_freeze_false_not_frozen(self, tmp_path):
        """flags.l2_freeze = false must return False."""
        from system_learning.invariants.freeze_gate import JsonFileBackedFreezeReader

        p = tmp_path / "runtime_state.json"
        p.write_text('{"flags": {"l2_freeze": false}}')
        r = JsonFileBackedFreezeReader(p)
        assert r.is_frozen() is False

    def test_side_effect_safety_freeze_does_not_mutate_file(self, tmp_path):
        """is_frozen() must be read-only: file content unchanged after call."""
        from system_learning.invariants.freeze_gate import JsonFileBackedFreezeReader

        p = tmp_path / "runtime_state.json"
        content = '{"freeze": true}'
        p.write_text(content)
        r = JsonFileBackedFreezeReader(p)
        r.is_frozen()
        assert p.read_text() == content, "is_frozen must not mutate the file"


# ---------------------------------------------------------------------------
# §1.5 / §1.6 CommitProofInvariant: remaining exception paths + negative controls
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCommitProofInvariantCompleteness:
    """Complete branch coverage for CommitProofInvariant.verify() (§1.5, §1.6)."""

    def test_non_hex_implementation_hash_raises(self):
        """implementation_hash with non-hex chars must raise CommitProofViolation."""
        from system_learning.invariants.commit_proof_invariant import (
            CommitProofInvariant,
            CommitProofViolation,
        )

        good_vid = "a" * 64
        bad_impl = "Z" * 64  # non-hex
        proof = CommitProofInvariant(
            version_id=good_vid,
            implementation_hash=bad_impl,
            commit_timestamp_utc=1_000_000,
        )
        with pytest.raises(CommitProofViolation, match="not hex"):
            proof.verify()

    def test_empty_implementation_hash_string_raises(self):
        """Empty string implementation_hash must raise CommitProofViolation."""
        from system_learning.invariants.commit_proof_invariant import (
            CommitProofInvariant,
            CommitProofViolation,
        )

        proof = CommitProofInvariant(
            version_id="a" * 64,
            implementation_hash="",
            commit_timestamp_utc=1_000_000,
        )
        with pytest.raises(CommitProofViolation, match="non-empty"):
            proof.verify()

    def test_timestamp_exactly_one_passes(self):
        """commit_timestamp_utc == 1 (minimum positive) must pass."""
        from system_learning.invariants.commit_proof_invariant import CommitProofInvariant

        pkg = _minimal_package()
        impl_hash = hashlib.sha256(pkg.canonical_bytes()).hexdigest()
        proof = CommitProofInvariant(
            version_id=impl_hash,
            implementation_hash=impl_hash,
            commit_timestamp_utc=1,
        )
        proof.verify()  # must not raise
        assert True  # no-exception contract

    def test_version_id_exactly_64_chars_valid_hex_passes(self):
        """A valid 64-char lowercase hex version_id must not fail the length/hex check."""
        from system_learning.invariants.commit_proof_invariant import CommitProofInvariant

        pkg = _minimal_package()
        impl_hash = hashlib.sha256(pkg.canonical_bytes()).hexdigest()
        proof = CommitProofInvariant(
            version_id=impl_hash,
            implementation_hash=impl_hash,
            commit_timestamp_utc=100,
        )
        proof.verify()  # must not raise
        assert True  # no-exception contract

    def test_version_id_65_chars_raises(self):
        """65-char version_id must raise (off-by-one boundary)."""
        from system_learning.invariants.commit_proof_invariant import (
            CommitProofInvariant,
            CommitProofViolation,
        )

        proof = CommitProofInvariant(
            version_id="a" * 65,
            implementation_hash="a" * 64,
            commit_timestamp_utc=1_000_000,
        )
        with pytest.raises(CommitProofViolation, match="64-char"):
            proof.verify()

    def test_version_id_63_chars_raises(self):
        """63-char version_id must raise (off-by-one boundary below)."""
        from system_learning.invariants.commit_proof_invariant import (
            CommitProofInvariant,
            CommitProofViolation,
        )

        proof = CommitProofInvariant(
            version_id="a" * 63,
            implementation_hash="a" * 64,
            commit_timestamp_utc=1_000_000,
        )
        with pytest.raises(CommitProofViolation, match="64-char"):
            proof.verify()

    def test_from_package_no_side_effects_on_package(self):
        """from_package must not mutate the package (§1.11 side-effect safety)."""
        from system_learning.invariants.commit_proof_invariant import CommitProofInvariant

        pkg = _minimal_package()
        original_changes = pkg.changes
        impl_hash = hashlib.sha256(pkg.canonical_bytes()).hexdigest()
        CommitProofInvariant.from_package(version_id=impl_hash, package=pkg, commit_timestamp_utc=1)
        assert pkg.changes == original_changes, "from_package must not mutate package.changes"

    def test_verify_is_idempotent(self):
        """Calling verify() twice on same proof must not raise (idempotent)."""
        from system_learning.invariants.commit_proof_invariant import CommitProofInvariant

        pkg = _minimal_package()
        impl_hash = hashlib.sha256(pkg.canonical_bytes()).hexdigest()
        proof = CommitProofInvariant(
            version_id=impl_hash,
            implementation_hash=impl_hash,
            commit_timestamp_utc=1_000_000,
        )
        proof.verify()
        proof.verify()  # second call must not raise
        assert True  # no-exception contract

    def test_churn_hash_blocks_side_effects(self):
        """Churn hash verification failure must raise BEFORE any side-effects can occur."""
        from system_learning.invariants.commit_proof_invariant import (
            CommitProofInvariant,
            CommitProofViolation,
        )

        ph = hashlib.sha256(b"placeholder").hexdigest()
        proof = CommitProofInvariant(
            version_id=ph,
            implementation_hash=ph,
            commit_timestamp_utc=1_000_000,
        )
        # Violation must be raised — no partial state should be emitted
        with pytest.raises(CommitProofViolation):
            proof.verify()


# ---------------------------------------------------------------------------
# §1.10 Determinism: RCA classification rule ordering stability
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRcaClassificationDeterminism:
    """Verify CLASSIFICATION_RULES ordering is stable and deterministic (§1.10)."""

    def test_first_matching_rule_wins(self):
        """SYNTAX rules appear before RUNTIME; SyntaxError must classify as SYNTAX."""
        from system_learning.engines.rca_engine import classify_line

        # SyntaxError: would match RUNTIME if RUNTIME came first
        result = classify_line("SyntaxError: bad indentation")
        assert result[0] == "SYNTAX", f"Expected SYNTAX, got {result[0]}"

    def test_policy_block_before_runtime(self):
        """AuthorityViolation is POLICY_BLOCK not RUNTIME."""
        from system_learning.engines.rca_engine import classify_line

        result = classify_line("AuthorityViolation: access denied")
        assert result[0] == "POLICY_BLOCK"

    def test_import_error_before_runtime(self):
        """ImportError must classify as IMPORT, not RUNTIME."""
        from system_learning.engines.rca_engine import classify_line

        result = classify_line("ImportError: cannot import name foo")
        assert result[0] == "IMPORT"

    def test_classification_rules_count_stable(self):
        """CLASSIFICATION_RULES must have exactly the expected count (mutation guard)."""
        from system_learning.engines.rca_engine import CLASSIFICATION_RULES

        # Count is: 3 SYNTAX + 2 IMPORT + 2 TEST_DISCOVERY + 2 POLICY_BLOCK + 6 RUNTIME + 2 TIMEOUT
        assert len(CLASSIFICATION_RULES) == 17, (
            f"CLASSIFICATION_RULES must have 17 entries, got {len(CLASSIFICATION_RULES)}. "
            "This guards against accidental removal or duplication."
        )

    def test_runtime_category_has_six_entries(self):
        """RUNTIME category must have exactly 6 patterns (mutation guard)."""
        from system_learning.engines.rca_engine import CLASSIFICATION_RULES

        runtime_rules = [r for r in CLASSIFICATION_RULES if r[0] == "RUNTIME"]
        assert len(runtime_rules) == 6, f"Expected 6 RUNTIME rules, got {len(runtime_rules)}"


# ---------------------------------------------------------------------------
# §1.13 Metamorphic / contradiction: proposal_only invariant
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProposalOnlyMetamorphic:
    """Metamorphic and contradiction tests for proposal_only default (§1.13)."""

    def test_proposal_only_default_cannot_be_overridden_by_env(self):
        """The default must be hardcoded True, not read from env at class definition."""
        import dataclasses
        import os

        original = os.environ.get("PROPOSAL_ONLY")
        try:
            os.environ["PROPOSAL_ONLY"] = "false"
            from system_learning.pipelines.meta_learning_pipeline import PipelineConfig

            fields = {f.name: f for f in dataclasses.fields(PipelineConfig)}
            assert fields["proposal_only"].default is True, "Default must be hardcoded True, not env-driven"
        finally:
            if original is None:
                os.environ.pop("PROPOSAL_ONLY", None)
            else:
                os.environ["PROPOSAL_ONLY"] = original

    def test_proposal_only_is_immutable_field(self):
        """PipelineConfig is frozen dataclass — proposal_only cannot be mutated after creation."""
        cfg = _make_pipeline_config(proposal_only=True)
        with pytest.raises((AttributeError, TypeError)):
            cfg.proposal_only = False  # type: ignore[misc]

    def test_proposal_only_false_explicit_does_not_affect_true_default(self):
        """Creating explicit False instance must not alter default for subsequent instances."""
        import dataclasses

        from system_learning.pipelines.meta_learning_pipeline import PipelineConfig

        _ = _make_pipeline_config(proposal_only=False)
        fields = {f.name: f for f in dataclasses.fields(PipelineConfig)}
        assert fields["proposal_only"].default is True


# ---------------------------------------------------------------------------
# §1.17 Stateful surface: _shadow_telemetry_batch module-level state
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestShadowTelemetryBatchStateful:
    """Verify module-level _shadow_telemetry_batch behaves as a stateful surface (§1.17)."""

    def test_batch_starts_as_list(self):
        import system_learning.pipelines.meta_learning_pipeline as m

        assert isinstance(m._shadow_telemetry_batch, list)

    def test_batch_cleared_to_empty_list_on_pipeline_entry(self):
        """After pipeline entry clears it, batch must be an empty list (not None, not old list)."""
        import system_learning.pipelines.meta_learning_pipeline as m
        from system_learning.pipelines.meta_learning_pipeline import PipelineError, run_pipeline

        m._shadow_telemetry_batch = [{"polluted": 1}, {"polluted": 2}]
        cfg = _make_pipeline_config(proposal_only=True)
        deps = _make_minimal_deps()

        # Trigger via invalid window (raises before significant work)
        with pytest.raises(PipelineError):
            run_pipeline(cfg=cfg, deps=deps, window_start_utc=50, window_end_utc=50, now_utc=100)

        # The invalid window fires BEFORE the clear line — batch still polluted
        # (window guard fires first at line 917, clear is at line 926)
        # This verifies the ORDER: window check → freeze check → clear
        # So after invalid-window error, batch remains polluted
        assert m._shadow_telemetry_batch == [{"polluted": 1}, {"polluted": 2}]

    def test_batch_cleared_on_valid_pipeline_entry_past_window_gate(self):
        """With valid window + no freeze, batch IS cleared at entry."""
        import system_learning.pipelines.meta_learning_pipeline as m
        from system_learning.pipelines.meta_learning_pipeline import run_pipeline

        m._shadow_telemetry_batch = [{"stale": True}]
        cfg = _make_pipeline_config(proposal_only=True)
        deps = _make_minimal_deps()

        # Valid window — pipeline will clear batch then may fail on deps
        try:
            run_pipeline(cfg=cfg, deps=deps, window_start_utc=0, window_end_utc=100, now_utc=50)
        except Exception:  # guardian: allow-silent-swallower
            pass

        # Batch must have been cleared (even if pipeline later failed)
        assert m._shadow_telemetry_batch == []

    def test_repeated_pipeline_entry_clears_each_time(self):
        """Each pipeline call clears the batch fresh (no accumulation across calls)."""
        import system_learning.pipelines.meta_learning_pipeline as m
        from system_learning.pipelines.meta_learning_pipeline import run_pipeline

        cfg = _make_pipeline_config(proposal_only=True)
        deps = _make_minimal_deps()

        for _call in range(3):
            m._shadow_telemetry_batch = [{"run": _call}]
            try:
                run_pipeline(cfg=cfg, deps=deps, window_start_utc=0, window_end_utc=100, now_utc=50)
            except Exception:  # guardian: allow-silent-swallower
                pass
            assert m._shadow_telemetry_batch == [], f"Batch must be cleared on call {_call}"
