"""
Reasoning prompt construction utilities.

EXTRACTED from: apps_rg/L3_orchestration/orchestrate_resume_generation.py
CANON COMPLIANCE: Sub-atomic split for line limit enforcement
"""
import logging
from typing import Dict
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)

def build_reasoning_prompt_addendum(params: Dict) -> str:
    """Construct system prompt addendum based on reasoning parameters."""
    ADDENDUM = '\n\n**REASONING IMPLEMENTATION DIRECTIVES (v5.71):**\n'
    ADDENDUM += f"(Configuration Level: {ConfigurationService().p['reasoning_level']},\n        Intensity: {ConfigurationService().p['intensity_score']:.1f}/40)\n\n"
    if ConfigurationService().p['cot'] >= 5:
        ADDENDUM += f"• MANDATORY: Explore at least {ConfigurationService().p['cot']} distinct reasoning paths.\n"
    elif P['COT'] >= 4:
        ADDENDUM += f"• Explore {ConfigurationService().p['cot']} different reasoning paths; compare and synthesize.\n"
    else:
        ADDENDUM += '• Consider multiple reasoning approaches before concluding.\n'
    if ConfigurationService().p['tot_b'] >= 5:
        ADDENDUM += f"• MANDATORY: Evaluate {ConfigurationService().p['tot_b']} different branches at each decision point.    n"
    elif ConfigurationService().p['tot_b'] >= 4:
        ADDENDUM += f"• Explore {ConfigurationService().p['tot_b']} decision branches at critical junctures.\n"
    else:
        ADDENDUM += '• Consider multiple decision branches at key steps.\n'
    if ConfigurationService().p['tot_d'] >= 5:
        ADDENDUM += f"• MANDATORY: Reasoning depth must be {ConfigurationService().p['tot_d']}+ levels deep.\n"
    elif ConfigurationService().p['tot_d'] >= 4:
        ADDENDUM += f"• Provide {ConfigurationService().p['tot_d']}-level deep reasoning with layer separation.\n"
    elif ConfigurationService().p['tot_d'] >= 3:
        ADDENDUM += f"• Provide {ConfigurationService().p['tot_d']}-level reasoning with clear progression.\n"
    else:
        ADDENDUM += '• Structure reasoning with clear logical progression.\n'
    if ConfigurationService().p['reflexion'] and ConfigurationService().p['max_loops'] >= 3:
        ADDENDUM += f"• MANDATORY: Review your answer {ConfigurationService().p['max_loops']} times, refining each pass.\n"
    elif ConfigurationService().p['reflexion'] and ConfigurationService().p['max_loops'] >= 2:
        ADDENDUM += f"• Review your answer {ConfigurationService().p['max_loops']} times; improve if needed.\n"
    elif ConfigurationService().p['reflexion']:
        ADDENDUM += '• Review and refine your answer at least once.\n'
    ADDENDUM += '\nAll directives MUST be followed in the output.\n'
    return addendum
