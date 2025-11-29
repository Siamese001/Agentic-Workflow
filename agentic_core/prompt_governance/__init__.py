#!/usr/bin/env python3
"""
Prompt Governance Module
Section 3: Canonical Repository Tree - Prompt Governance
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Import prompt governance components
from .manifests import create_prompt_manifest, PromptManifest
from .PromptACLs import create_prompt_acl, PromptACL
from .definitions import create_prompt_definition, PromptDefinition
from .metadata import create_prompt_metadata, PromptMetadata
from .versions import create_prompt_version, PromptVersion
from .domains import create_prompt_domain, PromptDomain
from .injection_policies import create_injection_policy, InjectionPolicy

__version__ = "1.0.0"
__all__ = [
    # Core components
    "create_prompt_manifest",
    "create_prompt_acl", 
    "create_prompt_definition",
    "create_prompt_metadata",
    "create_prompt_version",
    "create_prompt_domain",
    "create_injection_policy",
    
    # Class exports for direct usage
    "PromptManifest",
    "PromptACL", 
    "PromptDefinition",
    "PromptMetadata",
    "PromptVersion",
    "PromptDomain",
    "InjectionPolicy"
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
