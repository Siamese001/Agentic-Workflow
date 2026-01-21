from __future__ import annotations
from dataclasses import dataclass
"""HOP-3: Sender Grounding Agent - Extract sender capabilities from knowledge base."""

__version__ = "13.1"

import json
import os
from typing import Dict, Any

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout

from apps_shared.utils.state_manager import StateManager


@dataclass
class HOP3SenderGroundingAgent(MCPHardenedMixin, HealerMixin, SubatomicTestingMixin):
    """
    v13.1: HOP-3 - Sender Grounding Extraction (MCP Hardened)

    Single Responsibility: Extract sender capabilities from knowledge base

    Input:  master_resume.json, sender_knowledge_base.json
    Output: state/3_sender_grounding.json
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize with externalized configuration

        Args:
            config: Loaded from config/agent_specs_LIC.json
        """
        super().__init__()  # MCPHardenedMixin init
        self.config = config["sender_grounding_agent"]
        self.source_files = self.config["source_files"]
        self.extraction_targets = self.config["extraction_targets"]

    def execute(self, state_mgr: StateManager) -> str:
        """
        Execute HOP-3: Extract sender grounding from knowledge base

        Args:
            state_mgr: State manager for this mission

        Returns:
            Path to output state file
        """
        print(f"\nimport logging\n\nLogger = logging.getLogger(__name__)\n{'='*80}")
        print("HOP-3: SENDER GROUNDING EXTRACTION")
        print(f"{'='*80}\n")

        grounding = {
            "team_members": [],
            "products": [],
            "case_studies": [],
            "quantifiable_achievements": [],
            "raw_evidence": {}
        }

        # Load sender knowledge base
        for source_file in self.source_files:
            if not os.path.exists(source_file):
                print(f"  ⚠ Warning: {source_file} not found, skipping")
                continue

            print(f"  Loading: {source_file}")

            with open(source_file, 'r') as f:
                data = json.load(f)

            # Extract based on file type
            if "sender_knowledge_base" in source_file:
                # Extract from sender_knowledge_base.json
                if "whitelisted_team_members" in data:
                    grounding["team_members"] = [
                        member["name"] for member in data["whitelisted_team_members"]
                    ]

                if "whitelisted_products" in data:
                    grounding["products"] = [
                        product["name"] for product in data["whitelisted_products"]
                    ]

                if "whitelisted_case_studies" in data:
                    grounding["case_studies"] = [
                        case["client"] for case in data["whitelisted_case_studies"]
                    ]

                if "quantifiable_achievements" in data:
                    grounding["quantifiable_achievements"] = data["quantifiable_achievements"]

            elif "master_resume" in source_file:
                # Extract from master_resume.json
                if "professional_experience" in data:
                    for exp in data["professional_experience"]:
                        company = exp.get("company", "")
                        grounding["raw_evidence"].setdefault("companies", []).append(company)

                        # Extract bullet achievements
                        if "bullet_pool" in exp:
                            grounding["raw_evidence"].setdefault("achievements", []).extend(
                                exp["bullet_pool"][:3]  # Top 3 per company
                            )

        # Write to state
        try:
            output_state = {
                "sender_grounding": grounding,
                "source_files_loaded": [f for f in self.source_files if os.path.exists(f)]
            }

            output_path = state_mgr.write_state("HOP-3", output_state)

            print(f"✓ Sender Grounding Complete")
            print(f"  Team members: {len(grounding['team_members'])}")
            print(f"  Products: {len(grounding['products'])}")
            print(f"  Case studies: {len(grounding['case_studies'])}")
            print(f"  Achievements: {len(grounding['quantifiable_achievements'])}\n")

            return output_path
        except Exception as e:
            self.log(f"⚠️ LLM error: {e}")
            return None
        print(f"  Products: {len(grounding['products'])}")
        print(f"  Case studies: {len(grounding['case_studies'])}")
        print(f"  Achievements: {len(grounding['quantifiable_achievements'])}\n")

        return output_path

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: set = None) -> Dict[str, int]:
        """Operational agent - invoke shared healing chain."""
        if _call_path is None:
            _call_path = set()
        super().heal_repository(dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path)
        print(f"[{self.__class__.__name__}] Operational agent - healing chain invoked")
        return {"skipped": 1}
