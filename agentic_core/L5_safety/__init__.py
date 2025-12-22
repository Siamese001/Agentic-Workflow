"""L5 Safety Shield - Enterprise-grade security components for agentic systems.

This package provides comprehensive safety mechanisms:
- PII Vault: Holographic privacy protection with tokenized anonymization
- Constitutional Overseer: Rule-based content validation with configurable enforcement
- Canary Defense: Injection attack prevention with canary token detection
- Cost Governor: Financial circuit breaker with real-time cost tracking
"""
import re

import logging

LOGGER = logging.getLogger(__name__)

# Lazy imports to avoid hard dependency failures
try:
    from agentic_core.L5_safety.pii_vault import PIIVault
except Exception as e:
    LOGGER.debug(f"PIIVault not available: {e}")
    PIIVault = None

try:
    from agentic_core.L5_safety.overseer import ConstitutionalOverseer
except Exception as e:
    LOGGER.debug(f"ConstitutionalOverseer not available: {e}")
    ConstitutionalOverseer = None

try:
    from agentic_core.L5_safety.canary_defense import CanaryDefense, CanaryToken
except Exception as e:
    LOGGER.debug(f"CanaryDefense not available: {e}")
    CanaryDefense = None
    CanaryToken = None

try:
    from agentic_core.L5_safety.governor import CostGovernor
except Exception as e:
    LOGGER.debug(f"CostGovernor not available: {e}")
    CostGovernor = None

try:
    from agentic_core.L5_safety.safety_guardrail import SafetyGuardrail
except Exception as e:
    LOGGER.debug(f"SafetyGuardrail not available: {e}")
    SafetyGuardrail = None

try:
    from agentic_core.L5_safety.subatomic_engine import SubAtomicEngine
except Exception as e:
    LOGGER.debug(f"SubAtomicEngine not available: {e}")
    SubAtomicEngine = None

__all__ = [
    'PIIVault',
    'ConstitutionalOverseer',
    'CanaryDefense',
    'CostGovernor',
    'CanaryToken',
    'SafetyGuardrail',
    'SubAtomicEngine',
]

__version__ = '1.0.0'
__description__ = 'L5 Safety Shield - Enterprise-grade agentic security'
