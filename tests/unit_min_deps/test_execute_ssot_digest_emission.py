"""Integration invariant: DeterminismDigestEmitter wired into execute_ssot.

Tests:
  1. _compute_pipeline_digest() exists and is callable.
  2. Two independent calls with identical targets produce identical 64-hex digest.
  3. Identical targets -> identical emitted DETERMINISM-DIGEST line.
  4. Different targets -> different digest (sensitivity check).
  5. Full emit path: DeterminismDigestEmitter.emit_once wraps _compute_pipeline_digest
     and produces exactly "DETERMINISM-DIGEST: <64-hex>".
  6. Two-run pipeline stdout simulation: capturing print() output from both runs
     shows exactly one DETERMINISM-DIGEST line per run, identical across runs.
  7. Tamper env (W_HARDEN_NEGCTRL_TAMPER=1) changes digest; clean run restores it.
"""

from __future__ import annotations

import io
import os
from contextlib import redirect_stdout
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.unit_min_deps


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_compute_fn():
    """Import _compute_pipeline_digest from execute_ssot."""
    from agentic_core.L0_routing.scripts.execute_ssot import _compute_pipeline_digest

    return _compute_pipeline_digest


def _emit_for_targets(targets: list[str]) -> str:
    """Run the full emit path: compute + emit_once. Return the printed line."""
    from agentic_core.L6_observability.engines.determinism_digest_emitter import (
        DeterminismDigestEmitter,
    )

    compute = _get_compute_fn()
    digest = compute(targets)
    return DeterminismDigestEmitter().emit_once(digest)


def _capture_emit(targets: list[str]) -> str:
    """Capture stdout from the emit path, return only DETERMINISM-DIGEST lines."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        line = _emit_for_targets(targets)
        print(line)
    captured = buf.getvalue()
    det_lines = [l for l in captured.splitlines() if l.startswith("DETERMINISM-DIGEST:")]
    return det_lines


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestComputePipelineDigestExists:
    @pytest.mark.unit_min_deps
    def test_function_is_importable(self):
        fn = _get_compute_fn()
        assert callable(fn)

    @pytest.mark.unit_min_deps
    def test_returns_64_hex_string(self):
        fn = _get_compute_fn()
        result = fn(["agentic_core"])
        assert isinstance(result, str)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)


class TestTwoRunIdenticalDigest:
    """Core closure proof: two independent runs produce identical digest."""

    _TARGETS = ["agentic_core", "system_learning", "apps_lic"]

    @pytest.mark.unit_min_deps
    def test_run1_equals_run2(self):
        fn = _get_compute_fn()
        run1 = fn(self._TARGETS)
        run2 = fn(self._TARGETS)
        assert run1 == run2, f"Two-run digest mismatch:\n  run1={run1}\n  run2={run2}"

    @pytest.mark.unit_min_deps
    def test_run1_equals_run2_single_target(self):
        fn = _get_compute_fn()
        run1 = fn(["L5_safety"])
        run2 = fn(["L5_safety"])
        assert run1 == run2

    @pytest.mark.unit_min_deps
    def test_run1_equals_run2_empty_targets(self):
        fn = _get_compute_fn()
        run1 = fn([])
        run2 = fn([])
        assert run1 == run2

    @pytest.mark.unit_min_deps
    def test_different_targets_different_digest(self):
        fn = _get_compute_fn()
        d1 = fn(["agentic_core"])
        d2 = fn(["system_learning"])
        assert d1 != d2, "Different targets must produce different digest"

    @pytest.mark.unit_min_deps
    def test_target_order_does_not_matter(self):
        """Digest uses sorted targets — order must not affect output."""
        fn = _get_compute_fn()
        d1 = fn(["agentic_core", "system_learning"])
        d2 = fn(["system_learning", "agentic_core"])
        assert d1 == d2, "Target order must not affect digest (sorted internally)"


class TestEmitLineFormat:
    """The emitted line must be DETERMINISM-DIGEST: <64-hex>."""

    @pytest.mark.unit_min_deps
    def test_emit_line_format(self):
        line = _emit_for_targets(["agentic_core"])
        assert line.startswith("DETERMINISM-DIGEST: "), f"Bad format: {line!r}"
        hex_part = line.split(": ", 1)[1]
        assert len(hex_part) == 64
        assert all(c in "0123456789abcdef" for c in hex_part)

    @pytest.mark.unit_min_deps
    def test_two_runs_emit_identical_line(self):
        line1 = _emit_for_targets(["agentic_core"])
        line2 = _emit_for_targets(["agentic_core"])
        assert line1 == line2, f"Emitted lines differ:\n  run1={line1!r}\n  run2={line2!r}"

    @pytest.mark.unit_min_deps
    def test_duplicate_emitter_raises(self):
        from agentic_core.L6_observability.engines.determinism_digest_emitter import (
            DeterminismDigestEmitter,
            DuplicateEmissionError,
        )

        fn = _get_compute_fn()
        emitter = DeterminismDigestEmitter()
        digest = fn(["agentic_core"])
        emitter.emit_once(digest)
        with pytest.raises(DuplicateEmissionError):
            emitter.emit_once(digest)


class TestTwoRunStdoutCapture:
    """Simulate the pipeline print() path: exactly one DETERMINISM-DIGEST line per run."""

    _TARGETS = ["agentic_core", "system_learning"]

    @pytest.mark.unit_min_deps
    def test_exactly_one_digest_line_per_run(self):
        lines_run1 = _capture_emit(self._TARGETS)
        lines_run2 = _capture_emit(self._TARGETS)
        assert len(lines_run1) == 1, (
            f"Expected exactly 1 DETERMINISM-DIGEST line in run1, got {len(lines_run1)}: {lines_run1}"
        )
        assert len(lines_run2) == 1, (
            f"Expected exactly 1 DETERMINISM-DIGEST line in run2, got {len(lines_run2)}: {lines_run2}"
        )

    @pytest.mark.unit_min_deps
    def test_two_runs_stdout_lines_identical(self):
        lines_run1 = _capture_emit(self._TARGETS)
        lines_run2 = _capture_emit(self._TARGETS)
        assert lines_run1[0] == lines_run2[0], (
            f"Captured digest lines differ:\n  run1={lines_run1[0]!r}\n  run2={lines_run2[0]!r}"
        )

    @pytest.mark.unit_min_deps
    def test_captured_line_is_correct_format(self):
        lines = _capture_emit(self._TARGETS)
        assert lines[0].startswith("DETERMINISM-DIGEST: ")
        hex_part = lines[0].split(": ", 1)[1]
        assert len(hex_part) == 64
        assert all(c in "0123456789abcdef" for c in hex_part)


class TestNegativeControlTwoRun:
    """Tamper env breaks digest; restoring it restores identical output."""

    _TARGETS = ["agentic_core"]

    @pytest.mark.unit_min_deps
    def test_tamper_changes_digest(self):
        fn = _get_compute_fn()
        with patch.dict(os.environ, {}, clear=False):
            if "W_HARDEN_NEGCTRL_TAMPER" in os.environ:
                del os.environ["W_HARDEN_NEGCTRL_TAMPER"]
            clean = fn(self._TARGETS)
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            tampered = fn(self._TARGETS)
        assert clean != tampered, "Negative control FAILED: W_HARDEN_NEGCTRL_TAMPER=1 did not change digest"

    @pytest.mark.unit_min_deps
    def test_restore_after_tamper_gives_clean_digest(self):
        fn = _get_compute_fn()
        with patch.dict(os.environ, {}, clear=False):
            if "W_HARDEN_NEGCTRL_TAMPER" in os.environ:
                del os.environ["W_HARDEN_NEGCTRL_TAMPER"]
            clean1 = fn(self._TARGETS)
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            _ = fn(self._TARGETS)
        with patch.dict(os.environ, {}, clear=False):
            if "W_HARDEN_NEGCTRL_TAMPER" in os.environ:
                del os.environ["W_HARDEN_NEGCTRL_TAMPER"]
            restored = fn(self._TARGETS)
        assert clean1 == restored, (
            f"Digest did not restore after tamper removal:\n  clean1={clean1}\n  restored={restored}"
        )
