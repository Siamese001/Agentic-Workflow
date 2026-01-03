"""L2 Execution Base Agents - Unified base classes for all L2 agents.

Phase 2 (Jan 03, 2026): Unified L2ExecutionBaseAgent replaces:
- ExecutionCanonBaseAgent (heavyweight with Gemini)
- SubAtomicAgent (lightweight validation)

Migration:
- Former CanonBaseAgent agents: use L2ExecutionBaseAgent(enable_gemini=True)
- Former SubAtomicAgent agents: use L2ExecutionBaseAgent(enable_gemini=False)
"""

from .L2ExecutionBaseAgent import L2ExecutionBaseAgent

__all__ = ['L2ExecutionBaseAgent']
