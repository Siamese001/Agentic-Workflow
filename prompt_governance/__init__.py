#!/usr/bin/env python3
"""
Prompt Governance Module
Section 3: Canonical Repository Tree - Prompt Governance
"""

from typing import Dict, Any
import logging

# Import prompt governance components
from .manifests import create_prompt_manifest, PromptManifest
from .PromptACLs import create_prompt_acl, PromptACL
from .PromptDefinitions import (
    create_prompt_definition, PromptDefinition,
    get_system_prompt, initialize_system_prompts, update_system_template,
    get_developer_prompt, list_developer_templates, create_custom_prompt,
    get_user_prompt, format_user_query, generate_response_template
)
from .governance_metadata import create_prompt_metadata, PromptMetadata
from .PromptVersions import create_prompt_version, PromptVersion
from .Domains import create_prompt_domain, PromptDomain
from .InjectionPolicies import (
    create_injection_policy, InjectionPolicy,
    get_injection_prompt, apply_injection, list_injection_types,
    ContextBundle, FramingBundle, L1PlanningBundle,
    L2ExecutionBundle, L3OrchestrationBundle, L4MemoryBundle,
    L5SafetyBundle, OutputBundle, ReasoningBundle,
    SafetyBundle, ToolingBundle
)
from .builder import (
    PromptBuilder, PromptLayer, PromptComponent, PromptBuildResult,
    PromptDiff, PromptEvaluation, create_prompt_builder, build_simple_prompt
)

logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__all__ = [
    # Core factory functions
    "create_prompt_manifest",
    "create_prompt_acl", 
    "create_prompt_definition",
    "create_prompt_metadata",
    "create_prompt_version",
    "create_prompt_domain",
    "create_injection_policy",
    
    # Core classes
    "PromptManifest",
    "PromptACL", 
    "PromptDefinition",
    "PromptMetadata",
    "PromptVersion",
    "PromptDomain",
    "InjectionPolicy",
    
    # System prompts
    "get_system_prompt", "initialize_system_prompts", "update_system_template",
    
    # Developer prompts
    "get_developer_prompt", "list_developer_templates", "create_custom_prompt",
    
    # User prompts
    "get_user_prompt", "format_user_query", "generate_response_template",
    
    # Injection templates
    "get_injection_prompt", "apply_injection", "list_injection_types",
    
    # Layered Injection Bundles
    "ContextBundle", "FramingBundle", "L1PlanningBundle",
    "L2ExecutionBundle", "L3OrchestrationBundle", "L4MemoryBundle",
    "L5SafetyBundle", "OutputBundle", "ReasoningBundle",
    "SafetyBundle", "ToolingBundle",
    
    # Prompt Builder (Section 11)
    "PromptBuilder", "PromptLayer", "PromptComponent", "PromptBuildResult",
    "PromptDiff", "PromptEvaluation", "create_prompt_builder", "build_simple_prompt"
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
