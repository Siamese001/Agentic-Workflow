"""Run inside pytest context to diagnose skips."""
import traceback


def test_heal_policy_types_imports():
    missing = []
    try:
        from agentic_core.L5_safety.types import heal_policy_types as m  # noqa: F401
        import inspect
        members = dir(m)
        wanted = [
            "ReasoningTier", "ScoreBand", "HealEscalationInputs",
            "LegacyHealEscalationInputs", "HealEscalationDecision",
            "classify_score", "classify_confidence", "decide_heal_escalation",
            "decide_reasoning_tier", "MAX_RETRIES", "DEFAULT_SLEEP", "THRESHOLD",
            "BUFFER_SIZE", "BATCH_SIZE", "MAX_DEPTH",
        ]
        for name in wanted:
            if name not in members:
                missing.append(name)
        print(f"\nPresent: {[x for x in wanted if x in members]}")
        print(f"Missing: {missing}")
        assert missing == [], f"Missing from heal_policy_types: {missing}"
    except ImportError as e:
        traceback.print_exc()
        raise AssertionError(f"ImportError: {e}")


def test_tiered_batch_util_imports():
    missing = []
    try:
        from agentic_core.L5_safety.utils import tiered_batch_util as m2  # noqa: F401
        wanted = [
            "TieredBatchProcessor", "MAX_RETRIES", "DEFAULT_SLEEP", "THRESHOLD",
            "BUFFER_SIZE", "BATCH_SIZE", "MAX_DEPTH",
        ]
        members = dir(m2)
        for name in wanted:
            if name not in members:
                missing.append(name)
        print(f"\nPresent: {[x for x in wanted if x in members]}")
        print(f"Missing: {missing}")
        assert missing == [], f"Missing from tiered_batch_util: {missing}"
    except ImportError as e:
        traceback.print_exc()
        raise AssertionError(f"ImportError: {e}")
