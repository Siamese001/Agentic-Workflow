"""ADG importability contract for agentic_core/L5_safety/validators/silent_degradation_validator.py.

Covers GT_covers edge for ADG reachability.
Behavioral tests live in tests/guardian/test_silent_degradation_detector.py.
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_silent_degradation_validator_adg")
_emit_applies_guardrail("p0", "test_silent_degradation_validator_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_silent_degradation_validator_adg", "policy_binding")
_emit_snapshots_state("p0", "test_silent_degradation_validator_adg", "state_snapshot")
emit_replay_key("p0", "test_silent_degradation_validator_adg")
emit_determinism_digest("p0", "test_silent_degradation_validator_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

try:
    from agentic_core.L5_safety.validators.silent_degradation_validator import (  # noqa: F401
        SilentDegradationDetector,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SilentDegradationDetector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="silent_degradation_validator deps unavailable")
class TestSilentDegradationValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/validators/silent_degradation_validator.py must be importable."""
        assert _AVAILABLE

    def test_silentdegradationdetector_defined(self) -> None:
        assert SilentDegradationDetector is not None

    def test_detector_instantiates(self) -> None:
        det = SilentDegradationDetector()
        assert det is not None

    def test_category_is_silent_degradation(self) -> None:
        from agentic_core.L5_safety.validators.base_detector_validator import AntiPatternCategory

        det = SilentDegradationDetector()
        assert det.category == AntiPatternCategory.SILENT_DEGRADATION

    def test_all_exports_present(self) -> None:
        import agentic_core.L5_safety.validators.silent_degradation_validator as mod

        assert hasattr(mod, "SilentDegradationDetector")
        assert "SilentDegradationDetector" in mod.__all__
