"""
Agentic Core - Phase 1 Foundation
Configuration, Domain Entities, Exceptions, and Logging
"""

__version__ = "0.1.0"

# Bootstrap secure secrets before any SDK initialization
from agentic_core.security.secure_secrets import inject_into_env

inject_into_env()
