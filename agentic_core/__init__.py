"""
Agentic Core - Phase 1 Foundation
Configuration, Domain Entities, Exceptions, and Logging
"""

__version__ = "0.1.0"

# Bootstrap secure secrets before any SDK initialization
from agentic_core.security.secure_secrets import inject_into_env

inject_into_env()

# REQ-417: install runtime mutation guards (idempotent)
from agentic_core.L5_safety.enforcement.runtime_mutation_guard import install_guards as _install_guards

_install_guards()
