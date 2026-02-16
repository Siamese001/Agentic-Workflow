# Phase 4 — Controlled Model Escalation Evidence

## Wave 4.1 — Add Selection Hook (Pure + Default-Off)

### Diff

```diff
diff --git a/agentic_core/utils/decorators_util.py b/agentic_core/utils/decorators_util.py
index e2b0a38e0..3d10fa94d 100644
--- a/agentic_core/utils/decorators_util.py
+++ b/agentic_core/utils/decorators_util.py
@@ -20,6 +20,7 @@ from __future__ import annotations

 import functools
 import logging
+import os
 import time
 import traceback
 from collections.abc import Callable
@@ -49,6 +50,14 @@ HEAL_RESULT_SCHEMA = {
 }


+def _select_reasoning_tier_enabled() -> bool:
+    """Check if heal policy model escalation is enabled via env var.
+
+    Returns True iff HEAL_POLICY_MODEL_ESCALATION == "1", else False.
+    """
+    return os.environ.get("HEAL_POLICY_MODEL_ESCALATION") == "1"
+
+
 def _warn_non_canonical_keys(result: dict[str, Any], agent_name: str) -> None:
     """Emit warnings for non-canonical keys in heal_repository return values."""
     if not isinstance(result, dict):
@@ -190,6 +199,12 @@ def standard_heal(func: F) -> F:
                 f"[heal_policy] tier={policy_decision.tier.name} threshold={policy_decision.threshold_used}",
             )

+            # Phase 4: Escalation flag hook (default-off)
+            if _select_reasoning_tier_enabled():
+                Logger.debug(
+                    f"[heal_policy] escalation_enabled=1 selected_tier={policy_decision.tier.name}",
+                )
+
             result = func(
                 self,
                 *args,
```

### pytest -q

```text
===================== 122 passed in 20.32s =====================
```

Exit code: 0

**WAVE 4.1 ACCEPTANCE**: All tests pass. Escalation flag hook added (default-off).

---

## Wave 4.2 — Seam for Model Selection (No External Calls)

### Diff

```diff
diff --git a/agentic_core/utils/decorators_util.py b/agentic_core/utils/decorators_util.py
index 3d10fa94d..d6661844b 100644
--- a/agentic_core/utils/decorators_util.py
+++ b/agentic_core/utils/decorators_util.py
@@ -29,6 +29,7 @@ from typing import Any, TypeVar, cast
 from agentic_core.base_agents.timeout_decorator import TimeoutError, timeout
 from agentic_core.L5_safety.types.heal_policy_types import (
     HealEscalationInputs,
+    ReasoningTier,
     decide_reasoning_tier,
 )

@@ -58,6 +59,10 @@ def _select_reasoning_tier_enabled() -> bool:
     return os.environ.get("HEAL_POLICY_MODEL_ESCALATION") == "1"


+# Phase 4: Seam for tier observation (default None, no external calls)
+_HEAL_TIER_OBSERVER: Callable[[ReasoningTier], None] | None = None
+
+
 def _warn_non_canonical_keys(result: dict[str, Any], agent_name: str) -> None:
     """Emit warnings for non-canonical keys in heal_repository return values."""
     if not isinstance(result, dict):
@@ -204,6 +209,9 @@ def standard_heal(func: F) -> F:
                 Logger.debug(
                     f"[heal_policy] escalation_enabled=1 selected_tier={policy_decision.tier.name}",
                 )
+                # Invoke observer seam if set (for testing/monitoring)
+                if _HEAL_TIER_OBSERVER is not None:
+                    _HEAL_TIER_OBSERVER(policy_decision.tier)

             result = func(
                 self,
```

### pytest -q

```text
===================== 122 passed in 20.11s =====================
```

Exit code: 0

**WAVE 4.2 ACCEPTANCE**: All tests pass. Observer seam added (no external calls).

---

## Wave 4.3 — Governance Tests (Flag + Observer)

### Test File

`tests/governance/test_heal_policy_model_escalation_flag.py`

### Tests

**TestEscalationFlagDefaultOff**:
1. `test_no_escalation_log_when_disabled` — Without env var, no "escalation_enabled=1" log appears
2. `test_observer_not_invoked_when_disabled` — Without env var, observer is not invoked

**TestEscalationFlagEnabled**:
3. `test_escalation_log_when_enabled` — With env var set to "1", log contains escalation message
4. `test_observer_invoked_when_enabled` — With env var set to "1", observer is called exactly once

### pytest -q tests/governance/test_heal_policy_model_escalation_flag.py

```text
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagDefaultOff::test_no_escalation_log_when_disabled PASSED
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagDefaultOff::test_observer_not_invoked_when_disabled PASSED
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagEnabled::test_escalation_log_when_enabled PASSED
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagEnabled::test_observer_invoked_when_enabled PASSED
====================== 4 passed in 0.03s =======================
```

### pytest -q (full suite)

```text
===================== 126 passed in 20.51s =====================
```

Exit code: 0

**WAVE 4.3 ACCEPTANCE**: All tests pass. Flag + observer contract proven.
