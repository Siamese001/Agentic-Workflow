from __future__ import annotations

"""
Bias Auditor - Import from canonical L5 implementation
Consolidated 2026-01-06: Removed stub, now imports from L5_safety/validators
"""

from agentic_core.L5_safety.validators.bias_auditor import (
    BiasAuditorAgent,
    BiasMatch,
    BiasResult,
    BiasType,
    audit_bias,
)


# Factory function for compatibility
def create_bias_auditor() -> BiasAuditorAgent:
    """Factory function to create bias auditor."""
    return BiasAuditorAgent()

__all__ = ['BiasType', 'BiasMatch', 'BiasResult', 'BiasAuditorAgent', 'audit_bias', 'create_bias_auditor']
