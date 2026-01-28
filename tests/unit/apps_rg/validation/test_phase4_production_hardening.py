import pytest
from apps_rg.core.sovereign_context import SovereignContext
from apps_rg.validation.regeneration_engine import RegenerationEngine


class TestPhase4ProductionHardening:
    """
    Validates Phase 4 components: Sovereign Context (Airlock) and Regeneration Engine.
    Mandatory 100% Pass Rate.
    """

    def test_airlock_security_isolation(self):
        """
        Critical Security Test: Verify that data in airlock is invisible
        to the main state until committed with a signature.
        """
        ctx = SovereignContext()
        key = "sensitive_resume_data"
        value = "CONFIDENTIAL"

        # 1. Write to Airlock
        ctx.write_to_airlock(key, value)

        # 2. Assert Isolation (Main state should be empty/None)
        assert ctx.get(key) is None, "SECURITY FAIL: Airlock leaked data before commit!"

        # 3. Attempt Commit without Signature (Should Fail)
        with pytest.raises(ValueError):
            ctx.commit_airlock("")

        # 4. Valid Commit
        ctx.commit_airlock("valid_hmac_signature_v1")
        assert ctx.get(key) == value, "Commit failed to promote data to master state."

    def test_airlock_rollback_mechanism(self):
        """
        Verify rollback discards staged changes completely.
        """
        ctx = SovereignContext()
        ctx.write_to_airlock("toxic_data", "MALFORMED_INPUT")

        # Execute Rollback
        ctx.rollback_airlock()

        # Commit (to prove nothing was left behind)
        ctx.commit_airlock("sig")

        assert ctx.get("toxic_data") is None, "Rollback failed to clear toxic data."

    def test_regeneration_expansion_strategy(self):
        """
        Verify ExpansionStrategy increases word count to meet requirements.
        """
        engine = RegenerationEngine()
        short_text = "Too short"
        min_required = 10

        regenerated = engine.regenerate(short_text, "UNDERFLOW", {"min_required": min_required})

        word_count = len(regenerated.split())
        assert word_count >= min_required, (
            f"Expansion failed. Got {word_count}, needed {min_required}"
        )
        assert "measurable strategic impact" in regenerated, "Heuristic expansion text missing."

    def test_regeneration_condensation_strategy(self):
        """
        Verify CondensationStrategy truncates content to limit.
        """
        engine = RegenerationEngine()
        long_text = "one " * 50  # 50 words
        max_allowed = 5

        regenerated = engine.regenerate(long_text, "OVERFLOW", {"max_allowed": max_allowed})

        word_count = len(regenerated.split())
        assert word_count == max_allowed, (
            f"Condensation failed. Got {word_count}, expected {max_allowed}"
        )
