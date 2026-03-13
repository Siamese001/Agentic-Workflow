"""LicReflectionAgent — LIC domain reflection agent.

Originally from: LeadQualityAgent.py (Surgical Extraction 2026-01-06)
Refactored: 2026-03-11 (P2-A) — now subclasses BaseReflectionAgent.
"""

from dataclasses import dataclass

from apps_shared.reasoning.BaseReflectionAgent import BaseReflectionAgent


@dataclass
class LicReflectionAgent(BaseReflectionAgent):
    """Reflects on LIC campaign execution and suggests improvements.

    Inherits execute() and heal() from BaseReflectionAgent.
    Domain-specific post-reflection logic may be added via _post_reflect().
    """
