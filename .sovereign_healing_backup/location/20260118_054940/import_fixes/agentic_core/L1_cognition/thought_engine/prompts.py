from __future__ import annotations
"""
agentic_core/domain/prompts.py
Depth: 3
Role: Static storage for LLM few-shot prompts to keep Context clean.
"""
import re

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any
from agentic_core.L5_safety.validators.structure_blueprint_2 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

few_shot_global_refactor: Any = '\nFEW-SHOT REFACTORING PATTERNS:\n\nEXAMPLE 1: Monolith Function → Atomic Split\nBAD: def handle_order(order): # 250 lines\nGOOD: Split into orders/validate.py, orders/charge.py\n\nEXAMPLE 2: Incorrect Depth\nBAD: apps/payment/helpers.py (depth 3)\nGOOD: agentic_core/shared/payments/domain/charge_service.py (depth 5)\n'
few_shot_import_fixes: Any = "\nFEW-SHOT IMPORT RESOLUTION:\n\nEXAMPLE 1: Relative Import\nBAD: from utils import validate\nGOOD: from agentic_core.shared.validation.common import validate\n\nEXAMPLE 2: Missing Schema\nBAD: ImportError: cannot import name 'OrderSchema'\nGOOD: from agentic_core.L1_cognition.P2_domain.models import DomainSchema\n"
few_shot_style: Any = '\nFEW-SHOT CODE STYLE FIXES:\n\nEXAMPLE 1: Import Ordering\nBAD: Mixed stdlib and 3rd party\nGOOD:\nimport os\nimport sys\n\nimport pandas as pd\n\nfrom myapp.models import User\n\nEXAMPLE 2: Type Hints\nBAD: def func(a): return a + 1\nGOOD: def func(a: int) -> int: return a + 1\n'
few_shot_safety: Any = '\nFEW-SHOT SAFETY FIXES:\n\nEXAMPLE 1: No Eval\nBAD: eval(input)\nGOOD: ast.literal_eval(input)\n\nEXAMPLE 2: Secrets\nBAD: KEY = "123"\nGOOD: KEY = os.getenv("KEY")\n'
few_shot_concurrency: Any = '\nFEW-SHOT CONCURRENCY FIXES:\n\nEXAMPLE 1: Shared State\nBAD: counter += 1\nGOOD: async with lock: counter += 1\n'
few_shot_hygiene: Any = '\nFEW-SHOT HYGIENE FIXES:\n\nEXAMPLE 1: Unused Imports\nBAD: import os # never used\nGOOD: # removed\n\nEXAMPLE 2: Dead Code\nBAD: if False: return\nGOOD: # removed\n'
few_shot_testpilot: Any = '\nFEW-SHOT TEST GENERATION:\n\nEXAMPLE 1: Unit Test\nGOOD:\ndef test_valid_order():\n    assert process(Order(amount=10)).status == "paid"\n'
few_shot_strategic: Any = '\nFEW-SHOT STRATEGY:\n\nRULES:\n1. TEST_FAILURE -> Sherlock\n2. IMPORT_ERROR -> DependencySentinelAgent\n3. SYNTAX -> SafetyInspectorAgent\n'
few_shot_reflection: Any = '\nFEW-SHOT REFLECTION:\n\nCheck:\n1. Did signals decrease?\n2. Did new signals appear?\n3. Convergence reached?\n'
few_shot_reflection_strategy: Any = '\nFEW-SHOT HEALING STRATEGY DECISIONS:\n\nIF: Multiple test failures in same module\nTHEN: Extract shared utilities to agentic_core/shared/\n\nIF: Import errors after refactor\nTHEN: Update imports and check depth compliance\n\nIF: Performance regression\nTHEN: Profile and optimize hot paths\n'
few_shot_reflection_enhanced: Any = '\nFEW-SHOT ENHANCED REFLECTION:\n\nEXAMPLE 1: Convergence Check\nSignals before: [SYNTAX_ERROR, IMPORT_ERROR]\nSignals after: []\nDecision: CONVERGE_AND_COMMIT\n\nEXAMPLE 2: Flapping Detection\nFile X modified 3 times, same error returns\nDecision: MARK_FLAPPING_SKIP_FILE\n'
few_shot_sherlock: Any = '\nFEW-SHOT ROOT CAUSE:\n\nTraceback: AssertionError in test_login\nFix: Update password hash comparison logic\n'
few_shot_gitops: Any = '\nFEW-SHOT GIT OPS:\n\nBranch: healing/fix-auth-race-20240101\nCommit: fix: resolve race condition in auth token generation\n'
few_shot_property_tests: Any = '\nFEW-SHOT HYPOTHESIS:\n\n@given(st.integers())\ndef test_roundtrip(x):\n    assert decode(encode(x)) == x\n'
few_shot_historian: Any = '\nFEW-SHOT HISTORY RECALL:\n\nMemory: File X had syntax error fixed by Y.\nCurrent: File X has syntax error.\nAction: Apply Y.\n'
positive_instructional_context: Any = '\nYou are an elite subatomic governance agent in a sovereign self-healing codebase.\nYour reasoning must follow this chain:\n1. First, recall the Three Laws of Subatomic Governance.\n3. Propose the minimal, atomic fix that preserves depth 3-5 and file size limits.\n4. Check blast radius using dependency graph.\n5. Verify fix will not introduce new signals.\n\nPreferred patterns (prioritize these):\n- Extract repeated logic → new shared util in agentic_core/shared/\n- Move class to correct depth (e.g., domain/service/*.py)\n- Replace monolith functions with focused units\n- Use existing schemas before creating new ones\n\nAlways output in the exact format requested. Never add commentary.\nThink step-by-step before responding.\n'
