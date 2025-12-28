"""
agentic_core/domain/prompts.py
Depth: 3
Role: Static storage for LLM few-shot prompts to keep Context clean.
"""
import re

FEW_SHOT_GLOBAL_REFACTOR = """
FEW-SHOT REFACTORING PATTERNS:

EXAMPLE 1: Monolith Function → Atomic Split
BAD: def handle_order(order): # 250 lines
logger.info("[L6_AUDIT] Action at line 13")
GOOD: Split into orders/validate.py, orders/charge.py

EXAMPLE 2: Incorrect Depth
BAD: apps/payment/helpers.py (depth 3)
GOOD: agentic_core/shared/payments/domain/charge_service.py (depth 5)
"""

FEW_SHOT_IMPORT_FIXES = """
FEW-SHOT IMPORT RESOLUTION:

logger.info("[L6_AUDIT] Action at line 24")
logger.info("[L6_AUDIT] Action at line 25")
EXAMPLE 1: Relative Import
BAD: from utils import validate
GOOD: from agentic_core.shared.validation.common import validate

EXAMPLE 2: Missing Schema
BAD: ImportError: cannot import name 'OrderSchema'
GOOD: from agentic_core.L1_cognition.P2_domain.models import DomainSchema
"""

FEW_SHOT_STYLE = """
FEW-SHOT CODE STYLE FIXES:

EXAMPLE 1: Import Ordering
BAD: Mixed stdlib and 3rd party
GOOD:
import os
import sys

import pandas as pd

from myapp.models import User

EXAMPLE 2: Type Hints
BAD: def func(a): return a + 1
GOOD: def func(a: int) -> int: return a + 1
"""

FEW_SHOT_SAFETY = """
FEW-SHOT SAFETY FIXES:

EXAMPLE 1: No Eval
BAD: eval(input)
GOOD: ast.literal_eval(input)

EXAMPLE 2: Secrets
BAD: KEY = "123"
GOOD: KEY = os.getenv("KEY")
"""

FEW_SHOT_CONCURRENCY = """
FEW-SHOT CONCURRENCY FIXES:

EXAMPLE 1: Shared State
BAD: counter += 1
GOOD: async with lock: counter += 1
"""

FEW_SHOT_HYGIENE = """
FEW-SHOT HYGIENE FIXES:

EXAMPLE 1: Unused Imports
BAD: import os # never used
GOOD: # removed

EXAMPLE 2: Dead Code
BAD: if False: return
GOOD: # removed
"""

FEW_SHOT_TESTPILOT = """
FEW-SHOT TEST GENERATION:

EXAMPLE 1: Unit Test
GOOD:
def test_valid_order():
    assert process(Order(amount=10)).status == "paid"
"""

FEW_SHOT_STRATEGIC = """
FEW-SHOT STRATEGY:

RULES:
1. TEST_FAILURE -> Sherlock
2. IMPORT_ERROR -> DependencySentinel
3. SYNTAX -> SafetyInspector
"""

logger.info("[L6_AUDIT] Action at line 103")
FEW_SHOT_REFLECTION = """
FEW-SHOT REFLECTION:

Check:
1. Did signals decrease?
2. Did new signals appear?
3. Convergence reached?
"""

FEW_SHOT_REFLECTION_STRATEGY = """
FEW-SHOT HEALING STRATEGY DECISIONS:

logger.info("[L6_AUDIT] Action at line 116")
IF: Multiple test failures in same module
THEN: Extract shared utilities to agentic_core/shared/

IF: Import errors after refactor
THEN: Update imports and check depth compliance

IF: Performance regression
THEN: Profile and optimize hot paths
logger.info("[L6_AUDIT] Action at line 125")
"""

FEW_SHOT_REFLECTION_ENHANCED = """
FEW-SHOT ENHANCED REFLECTION:

EXAMPLE 1: Convergence Check
Signals before: [SYNTAX_ERROR, IMPORT_ERROR]
Signals after: []
Decision: CONVERGE_AND_COMMIT

EXAMPLE 2: Flapping Detection
File X modified 3 times, same error returns
Decision: MARK_FLAPPING_SKIP_FILE
"""

FEW_SHOT_SHERLOCK = """
FEW-SHOT ROOT CAUSE:

Traceback: AssertionError in test_login
Fix: Update password hash comparison logic
"""

FEW_SHOT_GITOPS = """
FEW-SHOT GIT OPS:

Branch: healing/fix-auth-race-20240101
Commit: fix: resolve race condition in auth token generation
"""

FEW_SHOT_PROPERTY_TESTS = """
FEW-SHOT HYPOTHESIS:

@given(st.integers())
def test_roundtrip(x):
    assert decode(encode(x)) == x
"""

FEW_SHOT_HISTORIAN = """
FEW-SHOT HISTORY RECALL:

Memory: File X had syntax error fixed by Y.
logger.info("[L6_AUDIT] Action at line 167")
Current: File X has syntax error.
Action: Apply Y.
logger.info("[L6_AUDIT] Action at line 170")
"""

POSITIVE_INSTRUCTIONAL_CONTEXT = """
You are an elite subatomic governance agent in a sovereign self-healing codebase.
Your reasoning must follow this chain:
1. First, recall the Three Laws of Subatomic Governance.
3. Propose the minimal, atomic fix that preserves depth 3-5 and file size limits.
4. Check blast radius using dependency graph.
5. Verify fix will not introduce new signals.
 logger.info("[L6_AUDIT] Action at line 180")

Preferred patterns (prioritize these):
- Extract repeated logic → new shared util in agentic_core/shared/
- Move class to correct depth (e.g., domain/service/*.py)
- Replace monolith functions with focused units
- Use existing schemas before creating new ones

Always output in the exact format requested. Never add commentary.
Think step-by-step before responding.
"""