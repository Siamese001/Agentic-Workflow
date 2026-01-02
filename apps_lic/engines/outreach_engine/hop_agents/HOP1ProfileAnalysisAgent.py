from __future__ import annotations
"""HOP-1: Profile Analysis Agent - Classify recipient Archetype."""

__version__ = "13.1"

from typing import Dict, Any

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L2_execution.ToolRegistry.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout

from apps_lic.domain.lic_models import OutreachMission
from apps_shared.utils.state_manager import StateManager


class HOP1ProfileAnalysisAgent(MCPHardenedMixin, HealerMixin, SubatomicTestingMixin):
    """
    v13.1: HOP-1 - Profile Analysis with state-based I/O (MCP Hardened)
    
    Single Responsibility: Classify recipient Archetype
    
    Input:  mission_input_LIC.json
    Output: state/1_profile_analysis.json
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize with externalized configuration
        
        Args:
            config: Loaded from config/agent_specs_LIC.json
        """
        super().__init__()  # MCPHardenedMixin init
        self.config = config["profile_analysis_agent"]
        self.archetype_indicators = self.config["archetype_indicators"]
        self.default_archetype = self.config["default_archetype"]
        self.manual_override_threshold = self.config["manual_override_threshold"]
    
    def execute(self, state_mgr: StateManager, mission: OutreachMission) -> str:
        """
        Execute HOP-1: Analyze profile and classify Archetype
        
        Args:
            state_mgr: State manager for this mission
            mission: Mission specification
        
        Returns:
            Path to output state file
        """
        print(f"\n{'='*80}")
        print("HOP-1: PROFILE ANALYSIS")
        print(f"{'='*80}\n")
        
        # Extract profile data
        title = mission.recipient_profile.get('title', '').lower()
        
        # Classify Archetype using config-based rules
        Archetype = None
        confidence = 0.0
        reasoning = ""
        key_indicators = []
        
        for arch_name, arch_config in self.archetype_indicators.items():
            for keyword in arch_config["keywords"]:
                if keyword in title:
                    Archetype = arch_name
                    confidence = arch_config["confidence"]
                    reasoning = f"Title '{title}' contains '{keyword}' indicator"
                    key_indicators = [keyword]
                    break
            
            if Archetype:
                break
        
        # Default if no match
        if not Archetype:
            Archetype = self.default_archetype
            confidence = self.config["default_confidence"]
            reasoning = f"Default classification - ambiguous title '{title}'"
            key_indicators = [title]
        
        needs_manual_override = confidence < self.manual_override_threshold
        
        # Prepare output state
        output_state = {
            "Archetype": Archetype,
            "confidence": confidence,
            "reasoning": reasoning,
            "key_indicators": key_indicators,
            "needs_manual_override": needs_manual_override,
            "recipient_title": title,
            "recipient_name": mission.recipient_profile.get('name', ''),
            "recipient_company": mission.recipient_profile.get('company', '')
        }
        
        # Write to state
        output_path = state_mgr.write_state("HOP-1", output_state)
        
        print(f"✓ Profile Analysis Complete")
        print(f"  Archetype: {Archetype}")
        print(f"  Confidence: {confidence:.2f}")
        print(f"  Reasoning: {reasoning}\n")
        
        return output_path

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: set = None) -> Dict[str, int]:
        """Operational agent - no repository healing required."""
        print(f"[{self.__class__.__name__}] Operational agent - no healing required")
        return {"skipped": 1}
