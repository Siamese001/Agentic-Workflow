"""
Reflection and strategic planning few-shot patterns.
Used by ReflectionAgent, StrategicPlanner.
"""
from typing import Any, Dict, List, Optional, Protocol
few_shot_reflection_strategy: Any = '\nFEW-SHOT HEALING STRATEGY DECISIONS:\n\nCASE 1: Signals dropped from 18 → 4, no new failures\n→ RECOMMEND: CONVERGE_AND_COMMIT\n\nCASE 2: Same SYNTAX_ERROR in file for 3+ cycles\n→ RECOMMEND: MARK_FLAPPING_SKIP_FILE\n\nCASE 3: New TEST_FAILURE after modification\n→ RECOMMEND: ROLLBACK_LAST_CHANGE_AND_RETRY\n\nCASE 4: >15 files modified or budget near limit\n→ RECOMMEND: ESCALATE_TO_HUMAN_WITH_REPORT\n'
few_shot_strategic: Any = '\nFEW-SHOT AGENDA PLANNING (StrategicPlanner):\n\nPRIORITY RULES:\n1. TEST_FAILURE → Sherlock + TestPilot\n2. IMPORT_ERROR → DependencySentinel first\n3. SYNTAX_ERROR → SafetyInspector\n4. Many modified files → Safety + Style recheck\n5. Flapping file → Skip or escalate\n6. Convergence → Stop\n\nOutput ordered list of agents to run.\n'
few_shot_reflection_enhanced: Any = "\nFEW-SHOT SELF-REFLECTION (ReflectionAgent):\n\nSUCCESS CRITERIA:\n- Signals → 0\n- No new signals introduced\n- All files subatomic and correct depth\n- Tests pass\n- Budget under limit\n\nAlways ask:\n1. Are we closer to zero signals?\n2. Any regression?\n3. What worked/didn't?\n"
