"""Diagnose why test_heal_policy_types and test_tiered_batch_util_adg skip."""
import traceback
import sys

print("=== heal_policy_types ===")
try:
    from agentic_core.L5_safety.types.heal_policy_types import (
        ReasoningTier, ScoreBand, HealEscalationInputs,
        LegacyHealEscalationInputs, HealEscalationDecision,
        classify_score, classify_confidence, decide_heal_escalation,
        decide_reasoning_tier, MAX_RETRIES, DEFAULT_SLEEP, THRESHOLD,
        BUFFER_SIZE, BATCH_SIZE, MAX_DEPTH,
    )
    print("ALL OK")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    traceback.print_exc()

print()
print("=== tiered_batch_util ===")
try:
    from agentic_core.L5_safety.utils.tiered_batch_util import (
        TieredBatchProcessor, MAX_RETRIES, DEFAULT_SLEEP, THRESHOLD,
        BUFFER_SIZE, BATCH_SIZE, MAX_DEPTH,
    )
    print("ALL OK")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    traceback.print_exc()

print()
print("=== what DOES exist in heal_policy_types ===")
try:
    import agentic_core.L5_safety.types.heal_policy_types as m
    print([x for x in dir(m) if not x.startswith('_')])
except Exception as e:
    print(f"Error: {e}")

print()
print("=== what DOES exist in tiered_batch_util ===")
try:
    import agentic_core.L5_safety.utils.tiered_batch_util as m2
    print([x for x in dir(m2) if not x.startswith('_')])
except Exception as e:
    print(f"Error: {e}")
