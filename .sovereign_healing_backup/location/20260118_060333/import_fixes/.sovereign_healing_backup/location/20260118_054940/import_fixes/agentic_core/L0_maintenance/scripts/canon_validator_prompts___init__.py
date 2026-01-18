
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, orchestrator, state, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations
"""
Canon Validator Prompts Package.
All few-shot prompting constants re-exported for backward compatibility.
"""
from agentic_core.L0_maintenance.P1_core.core import FEW_SHOT_GITOPS, FEW_SHOT_SHERLOCK, POSITIVE_INSTRUCTIONAL_CONTEXT
from agentic_core.Historian import FEW_SHOT_HISTORIAN
from agentic_core.refactoring import FEW_SHOT_GLOBAL_REFACTOR, FEW_SHOT_IMPORT_FIXES
from agentic_core.reflection import FEW_SHOT_REFLECTION_ENHANCED, FEW_SHOT_REFLECTION_STRATEGY, FEW_SHOT_STRATEGIC
from agentic_core.safety import FEW_SHOT_CONCURRENCY, FEW_SHOT_SAFETY
from agentic_core.style import FEW_SHOT_HYGIENE, FEW_SHOT_STYLE
from agentic_core.testing import FEW_SHOT_PROPERTY_TESTS, FEW_SHOT_TESTPILOT

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any
from agentic_core.L5_safety.validators.structure_blueprint_1 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

few_shot_prompts: Any = {'POSITIVE_INSTRUCTIONAL_CONTEXT': POSITIVE_INSTRUCTIONAL_CONTEXT, 'GLOBAL_REFACTOR': FEW_SHOT_GLOBAL_REFACTOR, 'IMPORT_FIXES': FEW_SHOT_IMPORT_FIXES, 'PROPERTY_TESTS': FEW_SHOT_PROPERTY_TESTS, 'REFLECTION_STRATEGY': FEW_SHOT_REFLECTION_STRATEGY, 'CONCURRENCY': FEW_SHOT_CONCURRENCY, 'SAFETY': FEW_SHOT_SAFETY, 'STYLE': FEW_SHOT_STYLE, 'HYGIENE': FEW_SHOT_HYGIENE, 'HISTORIAN': FEW_SHOT_HISTORIAN, 'TESTPILOT': FEW_SHOT_TESTPILOT, 'STRATEGIC': FEW_SHOT_STRATEGIC, 'REFLECTION_ENHANCED': FEW_SHOT_REFLECTION_ENHANCED, 'GITOPS': FEW_SHOT_GITOPS, 'SHERLOCK': FEW_SHOT_SHERLOCK}
__all__ = ['POSITIVE_INSTRUCTIONAL_CONTEXT', 'FEW_SHOT_GLOBAL_REFACTOR', 'FEW_SHOT_IMPORT_FIXES', 'FEW_SHOT_PROPERTY_TESTS', 'FEW_SHOT_REFLECTION_STRATEGY', 'FEW_SHOT_CONCURRENCY', 'FEW_SHOT_SAFETY', 'FEW_SHOT_STYLE', 'FEW_SHOT_HYGIENE', 'FEW_SHOT_HISTORIAN', 'FEW_SHOT_TESTPILOT', 'FEW_SHOT_STRATEGIC', 'FEW_SHOT_REFLECTION_ENHANCED', 'FEW_SHOT_GITOPS', 'FEW_SHOT_SHERLOCK', 'FEW_SHOT_PROMPTS']