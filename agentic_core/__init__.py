"""
AGENTIC CORE: THE BRAIN (Key 40)
================================
The sovereign domain for domain-agnostic agentic reasoning.
This package contains the 5 Atomic Layers of the architecture.

STRUCTURE:
- L1_cognition/       : Strategy, Planning, Reflection
- L2_execution/       : Tools, Engines, IO
- L3_orchestration/   : Workflows, Fission, Delegation
- L4_state/           : Context, Memory, Persistence
- L5_safety/          : Guardrails, Security, PII

COMPLIANCE:
- This package is SOVEREIGN. It must NOT import from 'apps_*'.
- Domain-specific logic (e.g., 'BulletNarrative') belongs in 'apps_rg'.
"""

import logging

# ==============================================================================
# 1. SOVEREIGN CONFIGURATION
# ==============================================================================

__version__ = "2.8.0"
__author__ = "Architecture Governor"

# Configure centralized logger for The Brain
_logger = logging.getLogger("agentic_core")
_logger.setLevel(logging.INFO) # Can be overridden by Key 0 (Global Config)

# ==============================================================================
# 2. LAYER EXPOSURE
# ==============================================================================

# We explicitly do NOT import all agents here to prevent:
# 1. Circular Dependencies (The "Mega-Init" anti-pattern)
# 2. Premature loading of heavy ML libraries
# 3. Violation of Fission (Agents should be imported only when needed)

# Agents should be discovered via 'canon_validator' or imported specifically:
# from agentic_core.L5_safety import PIISanitizerAgent

# ==============================================================================
# 3. RUNTIME BRIDGE (The Janitor)
# ==============================================================================

# Expose compliance tools for external validators (Key 46/47)
try:
    from .runtime import compliance
except ImportError:
    # Allow partial initialization during bootstrapping/migration
    _logger.warning("agentic_core.runtime.compliance not found. Skipping bridge.")
    compliance = None

__all__ = [
    "__version__",
    "compliance",
]