"""ADG importability contract for agentic_core/L5_safety/validators/test_skip_detector_validator.py.

Behavioral tests live in tests/guardian/test_test_silent_skip_detector.py.
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

_emit_records_execution_trace("p0", "evidence", "test_test_skip_detector_validator_adg")
_emit_applies_guardrail("p0", "test_test_skip_detector_validator_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_test_skip_detector_validator_adg", "policy_binding")
_emit_snapshots_state("p0", "test_test_skip_detector_validator_adg", "state_snapshot")
emit_replay_key("p0", "test_test_skip_detector_validator_adg")
emit_determinism_digest("p0", "test_test_skip_detector_validator_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

try:
    from agentic_core.L5_safety.validators.test_skip_detector_validator import (  # noqa: F401
        TestSilentSkipDetector,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    TestSilentSkipDetector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="test_skip_detector_validator deps unavailable")
class TestTestSkipDetectorValidatorImportability:
    def test_module_importable(self) -> None:
        assert _AVAILABLE

    def test_class_defined(self) -> None:
        assert TestSilentSkipDetector is not None

    def test_instantiates(self) -> None:
        det = TestSilentSkipDetector()
        assert det is not None

    def test_category_is_test_silent_skip(self) -> None:
        from agentic_core.L5_safety.validators.base_detector_validator import AntiPatternCategory

        det = TestSilentSkipDetector()
        assert det.category == AntiPatternCategory.TEST_SILENT_SKIP

    def test_all_exports_present(self) -> None:
        import agentic_core.L5_safety.validators.test_skip_detector_validator as mod

        assert hasattr(mod, "TestSilentSkipDetector")
        assert "TestSilentSkipDetector" in mod.__all__
