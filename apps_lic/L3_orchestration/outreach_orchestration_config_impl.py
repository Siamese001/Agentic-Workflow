"""Implementation for outreach_orchestration_config."""

from typing import Any, Dict, List, Optional
from .outreach_orchestration_config_types import *

def get_route_config(route: Route) -> Optional[RouteConfig]:
    """Get route configuration.
    
    Args:
        route: Message route
        
    Returns:
        RouteConfig or None if not defined
    """
    return ROUTE_CONFIGS.get(route)

def get_archetype_config(archetype: Archetype) -> Optional[ArchetypeConfig]:
    """Get archetype configuration.
    
    Args:
        archetype: Recipient archetype
        
    Returns:
        ArchetypeConfig or None if not defined
    """
    return ARCHETYPE_CONFIGS.get(archetype)

def classify_archetype(title: str, about: str='') -> Archetype:
    """Classify recipient archetype based on title and about.
    
    Args:
        title: Recipient job title
        about: Recipient about section
        
    Returns:
        Classified archetype
    """
    combined_text = f'{title} {about}'.upper()
    for token in CXO_PRECEDENCE_TOKENS:
        if token.upper() in combined_text:
            return Archetype.C_LEVEL
    for token in ARCHETYPE_TOKENS['C_LEVEL']:
        if token.upper() in combined_text:
            return Archetype.C_LEVEL
    for token in ARCHETYPE_TOKENS['EXECUTIVE']:
        if token.upper() in combined_text:
            return Archetype.EXECUTIVE
    for token in ARCHETYPE_TOKENS['SENIOR_TA']:
        if token.upper() in combined_text:
            return Archetype.SENIOR_TA
    for token in ARCHETYPE_TOKENS['RECRUITER']:
        if token.upper() in combined_text:
            return Archetype.RECRUITER
    return Archetype.EXECUTIVE

def get_validation_rules(phase: str) -> List[ValidationRule]:
    """Get validation rules for a specific phase.
    
    Args:
        phase: Execution phase
        
    Returns:
        List of validation rules
    """
    return [rule for rule in VALIDATION_RULES if rule.phase == phase]

