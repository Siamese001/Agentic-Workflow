"""
Reflection and strategic planning few-shot patterns.
Used by ReflectionAgent, StrategicPlanner.
"""

FEW_SHOT_REFLECTION_STRATEGY = """
FEW-SHOT HEALING STRATEGY DECISIONS:

CASE 1: Signals dropped from 18 → 4, no new failures
→ RECOMMEND: CONVERGE_AND_COMMIT

CASE 2: Same SYNTAX_ERROR in file for 3+ cycles
→ RECOMMEND: MARK_FLAPPING_SKIP_FILE

CASE 3: New TEST_FAILURE after modification
→ RECOMMEND: ROLLBACK_LAST_CHANGE_AND_RETRY

CASE 4: >15 files modified or budget near limit
→ RECOMMEND: ESCALATE_TO_HUMAN_WITH_REPORT
"""

FEW_SHOT_STRATEGIC = """
FEW-SHOT AGENDA PLANNING (StrategicPlanner):

PRIORITY RULES:
1. TEST_FAILURE → Sherlock + TestPilot
2. IMPORT_ERROR → DependencySentinel first
3. SYNTAX_ERROR → SafetyInspector
4. Many modified files → Safety + Style recheck
5. Flapping file → Skip or escalate
6. Convergence → Stop

Output ordered list of agents to run.
"""

FEW_SHOT_REFLECTION_ENHANCED = """
FEW-SHOT SELF-REFLECTION (ReflectionAgent):

SUCCESS CRITERIA:
- Signals → 0
- No new signals introduced
- All files subatomic and correct depth
- Tests pass
- Budget under limit

Always ask:
1. Are we closer to zero signals?
2. Any regression?
3. What worked/didn't?
"""
