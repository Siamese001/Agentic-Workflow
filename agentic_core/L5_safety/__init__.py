from __future__ import annotations
"""Sovereign Layer: L5_safety"""

# Temporarily disabled due to cascading import errors
# from agentic_core.P1_red_team.adversarial_red_teamer import VulnerabilityTest, RedTeamResult, AdversarialRedTeamer
# from agentic_core.P4_security.security_utilities import SecurityStatus, SecurityResult, PromptFirewall, FactChecker

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'SafetyGuardrail':
        from agentic_core.L5_safety.guardrails.SafetyGuardrail import SafetyGuardrail
        return SafetyGuardrail
    elif name == 'SubAtomicEngine':
        from agentic_core.L5_safety.guardrails.subatomic_engine import SubAtomicEngine
        return SubAtomicEngine
    elif name == 'sub_atomic_engine':
        from agentic_core.L5_safety.guardrails.subatomic_engine import SubAtomicEngine
        return SubAtomicEngine
    elif name == 'healer_mixin':
        from agentic_core.L5_safety.guardrails import healer_mixin
        return healer_mixin
    elif name == 'HealerMixin':
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
        return HealerMixin
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ['SafetyGuardrail', 'SubAtomicEngine', 'sub_atomic_engine']
