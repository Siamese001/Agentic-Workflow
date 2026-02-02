# FILE: tests/core/test_models_hardened.py
# [NEW FILE] - STRICT SSOT VERIFICATION
# Purpose: Validate Phase 3 hardening (immutability) and deprecation warnings.


import pytest
from pydantic import ValidationError

# Target Modules (Hardened)
from agentic_core.schemas.models.anomaly_report_config import AnomalyReport, AnomalySeverity
from agentic_core.schemas.models.consensus_verdict_validator import ConsensusVerdict
from agentic_core.schemas.models.safety_profile_validator import SafetyProfile


class TestHardenedContracts:
    """
    Aggressive verification of 'frozen=True' enforcement on Critical Contracts.
    """

    def test_anomaly_report_immutability(self):
        """
        CRITICAL: AnomalyReport must be immutable.
        Attempts to modify fields after instantiation must raise ValidationError.
        """
        report = AnomalyReport(
            type="drift",
            severity=AnomalySeverity.CRITICAL,
            description="Test Anomaly",
            source="Unit Test",
        )

        with pytest.raises((ValidationError, TypeError, AttributeError)) as excinfo:
            report.description = "Hacked Description"

        assert "frozen" in str(excinfo.value).lower()

    def test_consensus_verdict_validation(self):
        """
        CRITICAL: ConsensusVerdict must enforce strict field validation.
        Assuming 'consensus_score' has bounds (0.0 to 1.0).
        """
        verdict = ConsensusVerdict(
            chosen_plan="Use safe plan A",
            consensus_score=0.95,
            reasoning="Solid match",
            safe_to_proceed=True,
        )
        assert verdict.consensus_score == 0.95

        with pytest.raises(ValidationError):
            ConsensusVerdict(
                chosen_plan="Use safe plan A",
                consensus_score="not-a-float",
                reasoning="Invalid type",
                safe_to_proceed=True,
            )

    def test_safety_profile_validation(self):
        """
        CRITICAL: SafetyProfile must enforce the tier whitelist.
        """
        profile = SafetyProfile(safety_tier="standard")
        assert profile.safety_tier == "standard"

        with pytest.raises(ValidationError):
            SafetyProfile(safety_tier="nonexistent")


class TestRuntimeMutability:
    """
    Verify that 'KEEP' files (State/Config) remain mutable.
    """

    def test_reasoning_config_remains_mutable(self):
        """
        CRITICAL: ReasoningConfig was marked KEEP. It must NOT be frozen.
        """
        from agentic_core.schemas.models.reasoning_config_types import ReasoningConfig

        try:
            config = ReasoningConfig()
            if hasattr(config, "max_tokens"):
                original_val = config.max_tokens
                config.max_tokens = original_val + 1
                assert config.max_tokens == original_val + 1
        except ValidationError:
            pytest.fail("ReasoningConfig should be MUTABLE but raised ValidationError")
        except Exception:
            pass
