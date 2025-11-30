#!/usr/bin/env python3
"""
Prompt Governance Module
Section 3: Canonical Repository Tree - Prompt Governance
"""

from typing import Dict, Any
import logging

# Import prompt governance components that actually exist
try:
    from .builder import (
        PromptBuilder, PromptLayer, PromptComponent, PromptBuildResult,
        PromptDiff, PromptEvaluation, create_prompt_builder, build_simple_prompt
    )
except ImportError:
    logging.warning("builder module not available")
    PromptBuilder = None

try:
    from .injection_patterns import apply_injection, get_injection_prompt
except ImportError:
    logging.warning("injection_patterns module not available")
    apply_injection = None

logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__all__ = [
    # Core functions that exist
    "create_prompt_builder", "build_simple_prompt",
    
    # Core classes that exist
    "PromptBuilder", "PromptLayer", "PromptComponent", "PromptBuildResult",
    "PromptDiff", "PromptEvaluation",
    
    # Injection patterns if available
    "apply_injection", "get_injection_prompt",
]

def get_prompt_governance_info() -> Dict[str, Any]:
    """Get prompt governance module information"""
    return {
        "version": __version__,
        "components": {
            "manifests": "PromptManifest objects for structured prompt definitions",
            "prompt_acls": "Access control lists for prompt permissions",
            "definitions": "Core prompt definitions and templates",
            "metadata": "Prompt metadata and tagging system",
            "versions": "Version management for prompt evolution",
            "domains": "Domain-specific prompt specializations",
            "injection_policies": "Injection prevention and security policies"
        },
        "features": [
            "structured_prompt_management",
            "access_control",
            "version_control",
            "security_policies",
            "domain_specialization"
        ]
    }





