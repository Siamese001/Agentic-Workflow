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
