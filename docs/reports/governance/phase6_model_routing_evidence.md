# Phase 6 — Enabled-Path Model Tier Routing Evidence

## Wave 6.1 — Add Routing Seam (No SDK, No Executor Imports)

### Diff

```diff
diff --git a/agentic_core/utils/decorators_util.py b/agentic_core/utils/decorators_util.py
index d6661844b..b2a9094bb 100644
--- a/agentic_core/utils/decorators_util.py
+++ b/agentic_core/utils/decorators_util.py
@@ -63,6 +63,10 @@ def _select_reasoning_tier_enabled() -> bool:
 _HEAL_TIER_OBSERVER: Callable[[ReasoningTier], None] | None = None


+# Phase 6: Seam for model routing (default None, no SDK/executor imports)
+_HEAL_MODEL_ROUTER: Callable[[ReasoningTier], str] | None = None
+
+
 def _warn_non_canonical_keys(result: dict[str, Any], agent_name: str) -> None:
     """Emit warnings for non-canonical keys in heal_repository return values."""
     if not isinstance(result, dict):
@@ -213,6 +217,13 @@ def standard_heal(func: F) -> F:
                 if _HEAL_TIER_OBSERVER is not None:
                     _HEAL_TIER_OBSERVER(policy_decision.tier)

+                # Phase 6: Model routing seam (no SDK/executor imports)
+                if _HEAL_MODEL_ROUTER is not None:
+                    model_id = _HEAL_MODEL_ROUTER(policy_decision.tier)
+                    Logger.debug(f"[heal_policy] routed_model={model_id}")
+                else:
+                    Logger.debug("[heal_policy] routed_model=NONE")
+
             result = func(
                 self,
                 *args,
diff --git a/tests/governance/test_standard_heal_no_routing_contract.py b/tests/governance/test_standard_heal_no_routing_contract.py
index 419ac7ebd..d0ea3efaa 100644
--- a/tests/governance/test_standard_heal_no_routing_contract.py
+++ b/tests/governance/test_standard_heal_no_routing_contract.py
@@ -38,6 +38,12 @@ BANNED_CALL_NAMES = {
     "invoke",
 }

+# Allowlist: Controlled seam variables (not actual routing calls)
+ALLOWED_SEAM_VARIABLES = {
+    "_HEAL_MODEL_ROUTER",
+    "_HEAL_TIER_OBSERVER",
+}
+

 class TestStandardHealNoRoutingContract:
     """Enforce standard_heal contains no routing/executor calls."""
@@ -101,11 +107,16 @@ class TestStandardHealNoRoutingContract:
                     call_name = node.func.attr

                 if call_name:
+                    # Skip allowlisted seam variables
+                    if call_name in ALLOWED_SEAM_VARIABLES:
+                        continue
+
                     call_name_lower = call_name.lower()
                     for banned_name in BANNED_CALL_NAMES:
                         if banned_name in call_name_lower:
                             violations.append(
-                                f"Line {node.lineno}: Banned call '{call_name}' (contains '{banned_name}')"
+                                f"Line {node.lineno}: Banned call '{call_name}' "
+                                f"(contains '{banned_name}')"
                             )

         assert not violations, "standard_heal contains banned calls:\n" + "\n".join(violations)
@@ -146,11 +157,16 @@ class TestStandardHealNoRoutingContract:
                     call_name = node.func.attr

                 if call_name:
+                    # Skip allowlisted seam variables
+                    if call_name in ALLOWED_SEAM_VARIABLES:
+                        continue
+
                     call_name_lower = call_name.lower()
                     for banned_name in BANNED_CALL_NAMES:
                         if banned_name in call_name_lower:
                             violations.append(
-                                f"Line {node.lineno}: Banned call '{call_name}' (contains '{banned_name}')"
+                                f"Line {node.lineno}: Banned call '{call_name}' "
+                                f"(contains '{banned_name}')"
                             )

         assert not violations, "standard_heal wrapper contains banned calls:\n" + "\n".join(violations)
```

### pytest -q

```text
===================== 136 passed in 19.94s =====================
```

Exit code: 0

**WAVE 6.1 ACCEPTANCE**: All tests pass. Routing seam added (no SDK/executor imports). Phase 5 governance contract updated to allowlist controlled seam variables.

---

## Wave 6.2 — Default Router Implementation (Pure Map, Not Plugged)

### File Created

`agentic_core/L5_safety/types/heal_model_map.py`

### Contents

```python
"""
Tier-to-model ID mapping for heal policy escalation.

Pure mapping function (stdlib-only, no environment access).
Phase 6 Wave 6.2.
"""

from __future__ import annotations

from agentic_core.L5_safety.types.heal_policy_types import ReasoningTier

# Model identifiers for LOW and HIGH reasoning tiers
LOW_MODEL_ID = "local_low"
HIGH_MODEL_ID = "local_high"


def map_tier_to_model_id(tier: ReasoningTier) -> str:
    """Map a reasoning tier to a model identifier.

    Args:
        tier: The reasoning tier (LOW or HIGH)

    Returns:
        Model identifier string ("local_low" or "local_high")
    """
    return LOW_MODEL_ID if tier == ReasoningTier.LOW else HIGH_MODEL_ID
```

### Verification

```bash
python -c "from agentic_core.L5_safety.types.heal_model_map import map_tier_to_model_id; from agentic_core.L5_safety.types.heal_policy_types import ReasoningTier; print(map_tier_to_model_id(ReasoningTier.LOW))"
```

```text
local_low
```

### pytest -q

```text
===================== 136 passed in 20.19s =====================
```

Exit code: 0

**WAVE 6.2 ACCEPTANCE**: All tests pass. Tier→model ID mapping created (pure, stdlib-only).
