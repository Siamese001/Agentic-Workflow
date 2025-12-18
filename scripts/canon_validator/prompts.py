"""
Few-shot prompting constants for Canon Validator agents.
All FEW_SHOT_* constants are defined here to keep types.py clean.
"""

# L5+ Positive Instructional Context (TRUSTED - never from user input)
POSITIVE_INSTRUCTIONAL_CONTEXT = """
You are an elite subatomic governance agent in a sovereign self-healing codebase.
Your reasoning must follow this chain:
1. First, recall the Three Laws of Subatomic Governance.
2. Identify the root cause pattern from memory (use Pinecone recall if available).
3. Propose the minimal, atomic fix that preserves depth 3-5 and file size limits.
4. Check blast radius using dependency graph.
5. Verify fix will not introduce new signals.

Preferred patterns (prioritize these):
- Extract repeated logic → new shared util in apps_shared/
- Move class to correct depth (e.g., domain/service/*.py)
- Replace monolith functions with focused units
- Use existing schemas before creating new ones

Always output in the exact format requested. Never add commentary.
Think step-by-step before responding.
"""

FEW_SHOT_GLOBAL_REFACTOR = """
FEW-SHOT REFACTORING PATTERNS (Follow exactly for subatomic compliance):

EXAMPLE 1: Monolith Function → Atomic Split
BAD (violates Atomicity Law):
def handle_order(order):
    # 250 lines: validate, charge, inventory, email...

GOOD (compliant):
# Split into:
# apps_rg/orders/validate.py
# apps_rg/orders/charge.py  
# apps_rg/orders/notify.py
# Each file <180 lines, single responsibility

EXAMPLE 2: Incorrect Depth → Correct Depth
BAD: apps/payment/helpers.py (depth 3)
GOOD: Move to apps_shared/payments/domain/charge_service.py (depth 5)

EXAMPLE 3: Duplicated Validation Logic
BAD: Same Pydantic model in lic.py and rg.py
GOOD: Single source in schemas/payment.py, imported with:
from schemas.payment import PaymentSchema

EXAMPLE 4: Root Directory Noise
BAD: debug_tool.py in root
GOOD: Move to scripts/debug_tool.py or delete

Prioritize minimal changes. Always preserve behavior.
"""

FEW_SHOT_IMPORT_FIXES = """
FEW-SHOT IMPORT RESOLUTION (DependencySentinel):

EXAMPLE 1: Relative Import Wrong Depth
BAD: from utils.validation import validate
GOOD: from apps_shared.validation.common import validate

EXAMPLE 2: Missing Schema
BAD: ImportError: cannot import name 'OrderSchema'
GOOD: from schemas.order import OrderSchema

EXAMPLE 3: Circular Dependency
BAD: orders/service.py imports payments/utils.py
      payments/utils.py imports orders/models.py
GOOD: Extract shared types to schemas/shared.py
      Both import from schemas/shared.py

EXAMPLE 4: Unused Import
GOOD: Remove line entirely — do not replace
"""

FEW_SHOT_PROPERTY_TESTS = """
FEW-SHOT HYPOTHESIS PROPERTY TESTS (Valid syntax only):

EXAMPLE 1: List reversal idempotency
from hypothesis import given, strategies as st
@given(st.lists(st.integers()))
def test_reverse_twice(lst):
    assert lst[::-1][::-1] == lst

EXAMPLE 2: JSON serialization roundtrip
@given(st.dictionaries(st.text(), st.integers()))
def test_json_roundtrip(data):
    assert json.loads(json.dumps(data)) == data

EXAMPLE 3: Sorting is idempotent
@given(st.lists(st.integers()))
def test_sorted_idempotent(numbers):
    assert sorted(sorted(numbers)) == sorted(numbers)
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

FEW_SHOT_CONCURRENCY = """
FEW-SHOT CONCURRENCY FIXES (ConcurrencyGuardian — Follow exactly):

EXAMPLE 1: Shared Mutable Dict Without Lock
BAD (race condition):
shared_cache = {}
def update_cache(key, value):
    shared_cache[key] = value  # Not thread-safe

GOOD (safe):
from threading import Lock
shared_cache = {}
cache_lock = Lock()

def update_cache(key, value):
    with cache_lock:
        shared_cache[key] = value

EXAMPLE 2: Compound Assignment (+=) on Shared State
BAD:
    total += amount  # Reads, modifies, writes — race!

GOOD:
    with total_lock:
        total += amount

EXAMPLE 3: Async Shared State Without AsyncLock
BAD:
shared_counter = 0
async def increment():
    shared_counter += 1  # Not safe in asyncio

GOOD:
from asyncio import Lock
shared_counter = 0
counter_lock = Lock()

async def increment():
    async with counter_lock:
        shared_counter += 1

Prioritize context managers. Never use time.sleep() for synchronization.
"""

FEW_SHOT_SAFETY = """
FEW-SHOT SAFETY FIXES (SafetyInspector — Follow exactly):

EXAMPLE 1: Dangerous eval/exec
BAD:
value = eval(user_input)

GOOD:
import ast
try:
    value = ast.literal_eval(user_input)
except (ValueError, SyntaxError):
    raise ValueError("Invalid literal")

EXAMPLE 2: subprocess Without Restrictions
BAD:
subprocess.run(command)
subprocess.Popen(user_command, shell=True)

GOOD:
subprocess.run(["git", "pull"], check=True, cwd="/repo")

EXAMPLE 3: Hardcoded Secrets
BAD:
API_KEY = "sk-1234567890abcdef"

GOOD:
import os
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable required")

Never introduce eval/exec/subprocess/shell=True.
Always require env vars for secrets.
"""

FEW_SHOT_STYLE = """
FEW-SHOT CODE STYLE FIXES (CodeStyleGuardian — Follow exactly):

EXAMPLE 1: Import Ordering (isort)
BAD:
import os
import pandas as pd
from pathlib import Path

GOOD (isort sections):
import os

from pathlib import Path

import pandas as pd

EXAMPLE 2: Type Hints (Modern Python)
BAD:
def process(data):
    return data.upper()

GOOD:
def process(data: str) -> str:
    return data.upper()

Always follow black formatting.
Always use type hints.
Always use f-strings.
"""

FEW_SHOT_HYGIENE = """
FEW-SHOT HYGIENE FIXES (HygieneGuardian — Follow exactly):

EXAMPLE 1: Unused Import
BAD:
import pandas as pd
# pandas never used

GOOD:
# Remove line entirely

EXAMPLE 2: Unused Variable
BAD:
temp = setup()
# temp never read

GOOD:
setup()  # Or remove if side-effect free

Rules:
- Remove unused imports ALWAYS
- Remove unused variables ONLY if not in loop/setup
- Never remove __all__, abstract methods, dunder
"""

FEW_SHOT_HISTORIAN = """
FEW-SHOT MEMORY RECALL USAGE (Historian):

EXAMPLE 1: Past Fix Recall
MEMORY: File apps/utils.py had SYNTAX_ERROR fixed by adding missing colon
Current: Same file, same error
GOOD: Apply exact same fix — do not reinvent

EXAMPLE 2: Failed Strategy
MEMORY: Inline extraction caused TEST_FAILURE → rolled back
Current: Similar monolith
GOOD: Try split-into-files instead

Always check recalled memories first.
"""

FEW_SHOT_TESTPILOT = """
FEW-SHOT TEST GENERATION (TestPilot):

EXAMPLE 1: Unit Test Structure
GOOD:
def test_process_valid_order():
    order = OrderFactory(status="pending")
    result = process_order(order)
    assert result.status == "processed"

Use pytest style.
Cover happy path + one error case.
Never use real external calls.
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

FEW_SHOT_GITOPS = """
FEW-SHOT GIT OPERATIONS (GitAgent — Follow exactly):

BRANCH NAMING CONVENTION:
healing/<category>-<short-description>-YYYYMMDD

EXAMPLE: healing/fix-import-cycle-20251217

COMMIT MESSAGE CONVENTION (Conventional Commits):
<type>: <short description>

Types: fix, refactor, security, style, test, chore

Never commit secrets, large files, or .env
Always create new healing branch per session
"""

FEW_SHOT_SHERLOCK = """
FEW-SHOT ROOT CAUSE ANALYSIS (Sherlock — Follow exactly):

EXAMPLE 1: Test Failure Traceback
Traceback: AssertionError in test_order_process
Modified: orders/service.py
GOOD:
Root cause: status check uses == "processed" instead of "completed"
Fix: change string literal

METHOD:
1. Read traceback bottom-up
2. Find modified file in stack
3. Compare old vs new behavior
4. Propose one-line fix if possible

Always minimal. Output unified diff.
"""

# Aggregate all prompts for easy access
FEW_SHOT_PROMPTS = {
    "POSITIVE_INSTRUCTIONAL_CONTEXT": POSITIVE_INSTRUCTIONAL_CONTEXT,
    "GLOBAL_REFACTOR": FEW_SHOT_GLOBAL_REFACTOR,
    "IMPORT_FIXES": FEW_SHOT_IMPORT_FIXES,
    "PROPERTY_TESTS": FEW_SHOT_PROPERTY_TESTS,
    "REFLECTION_STRATEGY": FEW_SHOT_REFLECTION_STRATEGY,
    "CONCURRENCY": FEW_SHOT_CONCURRENCY,
    "SAFETY": FEW_SHOT_SAFETY,
    "STYLE": FEW_SHOT_STYLE,
    "HYGIENE": FEW_SHOT_HYGIENE,
    "HISTORIAN": FEW_SHOT_HISTORIAN,
    "TESTPILOT": FEW_SHOT_TESTPILOT,
    "STRATEGIC": FEW_SHOT_STRATEGIC,
    "REFLECTION_ENHANCED": FEW_SHOT_REFLECTION_ENHANCED,
    "GITOPS": FEW_SHOT_GITOPS,
    "SHERLOCK": FEW_SHOT_SHERLOCK,
}
