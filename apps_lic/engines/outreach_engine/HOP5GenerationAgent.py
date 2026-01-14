from __future__ import annotations
from dataclasses import dataclass
"""HOP-5: Generation Agent - N-candidate generation only."""

__version__ = "13.1"

import asyncio
import json
import logging
import os
from typing import Dict, List, Any

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin

from apps_shared.utils.state_manager import StateManager
from apps_lic.engines.outreach_engine.tools.code_interpreter import CodeInterpreterTool

Logger = logging.getLogger(__name__)


@dataclass
class HOP5GenerationAgent(MCPHardenedMixin, HealerMixin, SubatomicTestingMixin):
    """
    v13.1: Generation Agent - N-candidate generation only (MCP Hardened)
    
    Single Responsibility: Generate message candidates
    
    Input:  state/2_research_context.json, state/3_sender_grounding.json, state/4.5_scaffold.json
    Output: state/5_generated_drafts.json
    """
    
    def __init__(self, config: Dict[str, Any], llm_client: Any = None, tool: CodeInterpreterTool = None) -> None:
        super().__init__()
        self.config = config["generation_agent"]
        self.llm_client = llm_client
        self.tool = tool
        
        with open("config/prompts_LIC.json", 'r') as f:
            self.prompts = json.load(f)
    
    async def execute(self, state_mgr: StateManager, temperature: float = None) -> str:
        """Execute HOP-5: Generate message candidates"""
        print(f"\n{'='*80}")
        print("HOP-5: GENERATION AGENT")
        print(f"{'='*80}\n")
        
        research = state_mgr.read_state("HOP-2")
        grounding = state_mgr.read_state("HOP-3")
        scaffold = state_mgr.read_state("HOP-4.5")
        
        Archetype = scaffold["Archetype"]
        Route = scaffold["Route"]
        
        n_candidates = self.config["c_level_n_candidates"] if Archetype == "C_LEVEL" else 1
        
        if temperature is None:
            temperature = self._get_base_temperature(Archetype)
        
        print(f"Generating {n_candidates} candidate(s) at temperature {temperature:.2f}...")
        
        candidates = []
        for i in range(n_candidates):
            print(f"  Generating candidate {i+1}/{n_candidates}...")
            try:
                draft_text = await self._generate_single_draft(research, grounding, scaffold, temperature)
            except Exception as e:
                self.log(f"⚠️ LLM error: {e}")
                return None
            candidates.append({
                "candidate_id": i + 1,
                "text": draft_text,
                "word_count": len(draft_text.split()),
                "char_count": len(draft_text),
                "temperature": temperature
            })
        
        if n_candidates > 1:
            print(f"\nScoring {n_candidates} candidates (Fast Loop)...")
            scored = self._score_candidates_with_tool(candidates, research)
            selected_candidate = scored[0]
            print(f"  ✓ Selected candidate {selected_candidate['candidate_id']} (score: {selected_candidate['total_score']:.3f})")
        else:
            selected_candidate = candidates[0]
            scored = [selected_candidate]
        
        output_state = {
            "candidates": candidates,
            "scored_candidates": scored if n_candidates > 1 else None,
            "selected_draft": selected_candidate,
            "n_candidates": n_candidates,
            "generation_temperature": temperature,
            "generation_attempts": 1,
            "Archetype": Archetype,
            "Route": Route
        }
        
        output_path = state_mgr.write_state("HOP-5", output_state)
        
        print(f"\n✓ Generation Complete")
        print(f"  Selected draft: {selected_candidate['word_count']} words")
        print(f"  Temperature: {temperature:.2f}\n")
        
        return output_path
    
    async def _generate_single_draft(self, research: Dict[str, Any], grounding: Dict[str, Any], scaffold: Dict[str, Any], temperature: float) -> str:
        """Generate a single message draft"""
        template = self.prompts["strategic_alignment_prompt_template"]["template"]
        strategic_brief = research.get("strategic_brief", "")
        sender_summary = self._extract_sender_summary(grounding)
        recipient_summary = self._extract_recipient_summary(research, strategic_brief)
        voice = self._load_voice_profile()
        
        prompt = template.format(
            persona=voice.get("persona", "Strategic AI Leader"),
            principles="\n".join([f"- {p}" for p in voice.get("communication_principles", [])]),
            sender_summary=sender_summary,
            recipient_summary=recipient_summary,
            word_count_min=scaffold["constraints"]["word_range"][0],
            word_count_max=scaffold["constraints"]["word_range"][1],
            forbidden=", ".join(voice.get("forbidden_phrases", [])[:10]),
            Route=scaffold["Route"],
            Archetype=scaffold["Archetype"],
            adversarial_constraints=""
        )
        
        loop = asyncio.get_event_loop()
        draft_text = await loop.run_in_executor(None, self.llm_client.generate, prompt)
        return draft_text.strip()
    
    def _score_candidates_with_tool(self, candidates: List[Dict[str, Any]], research: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score candidates using CodeInterpreterTool (Fast Loop)"""
        strategic_brief = research.get("strategic_brief", "")
        scored = self.tool.execute(
            "run_scoring_competition",
            candidates=[c["text"] for c in candidates],
            strategic_brief=strategic_brief
        )
        
        for i, ScoreResult in enumerate(scored):
            ScoreResult["candidate_id"] = candidates[ScoreResult["candidate_index"]]["candidate_id"]
            ScoreResult["word_count"] = candidates[ScoreResult["candidate_index"]]["word_count"]
            ScoreResult["temperature"] = candidates[ScoreResult["candidate_index"]]["temperature"]
        
        return scored
    
    def _extract_sender_summary(self, grounding: Dict[str, Any]) -> str:
        """Extract top 5 sender capabilities"""
        sender_grounding = grounding.get("sender_grounding", {})
        achievements = sender_grounding.get("quantifiable_achievements", [])
        products = sender_grounding.get("products", [])
        
        summary_lines = []
        for achievement in achievements[:5]:
            summary_lines.append(f"- {achievement[:150]}")
        for product in products[:2]:
            summary_lines.append(f"- Product: {product}")
        
        return "\n".join(summary_lines) if summary_lines else "- Professional with relevant experience"
    
    def _extract_recipient_summary(self, research: Dict[str, Any], strategic_brief: str) -> str:
        """Extract top 5 recipient priorities"""
        summary_lines = []
        
        if strategic_brief:
            brief_lines = strategic_brief.split('\n')[:5]
            summary_lines.extend([f"- {line[:150]}" for line in brief_lines if line.strip()])
        
        if not summary_lines:
            insights = research.get("recipient_insights", [])
            summary_lines = [f"- {insight[:150]}" for insight in insights[:5]]
        
        return "\n".join(summary_lines) if summary_lines else "- Professional at target company"
    
    def _load_voice_profile(self) -> Dict[str, Any]:
        """Load sender voice profile"""
        if os.path.exists("sender_voice_profile.json"):
            with open("sender_voice_profile.json", 'r') as f:
                return json.load(f)
        return {}
    
    def _get_base_temperature(self, Archetype: str) -> float:
        """Get base temperature for Archetype from config"""
        temp_config = self.config.get("base_temperatures", {})
        return temp_config.get(Archetype, 0.50)

    def heal_repository(self) -> None:
        """Autonomy healing: Validate and auto-correct agent state/config for reliable message generation.

        - Chains super() for shared diagnostics/rollback
        - Lic-specific: LLM client availability, prompt config integrity, temperature bounds
        - MCP ensures safe operations (e.g., sanitized prompt loading)
        """
        super().heal_repository()

        self._heal_llm_client()
        self._heal_prompt_config()
        self._heal_temperature_bounds()
        self._run_generation_diagnostics()

    def _heal_llm_client(self) -> None:
        """Validate LLM client availability and gracefully degrade if needed."""
        try:
            if not self.llm_client:
                Logger.warning("LLM client missing — generation may fail")
                return
            if not hasattr(self.llm_client, 'generate'):
                Logger.error("LLM client missing generate method — disabling")
                self.llm_client = None
        except Exception as e:
            Logger.error(f"LLM client validation failed: {e}")

    def _heal_prompt_config(self) -> None:
        """Validate and reload prompt configuration if corrupted."""
        try:
            if not isinstance(self.prompts, dict):
                Logger.warning("Prompts config corrupted — reloading from file")
                if os.path.exists("config/prompts_LIC.json"):
                    with open("config/prompts_LIC.json", 'r') as f:
                        self.prompts = json.load(f)
                else:
                    Logger.error("Prompts file missing — using empty config")
                    self.prompts = {}
            required_keys = ["system", "user_template"]
            for key in required_keys:
                if key not in self.prompts:
                    Logger.warning(f"Missing prompt key {key} — using default")
                    if key == "system":
                        self.prompts[key] = "You are a professional message generator."
                    elif key == "user_template":
                        self.prompts[key] = "Generate a message for {recipient}."
        except Exception as e:
            Logger.error(f"Prompt config healing failed: {e}")

    def _heal_temperature_bounds(self) -> None:
        """Ensure temperature settings within safe bounds."""
        try:
            if not isinstance(self.config, dict):
                Logger.warning("Config corrupted — resetting to defaults")
                self.config = {"base_temperatures": {}}
            base_temps = self.config.get("base_temperatures", {})
            for archetype, temp in base_temps.items():
                if not isinstance(temp, (int, float)) or temp < 0 or temp > 2.0:
                    Logger.warning(f"Temperature {temp} for {archetype} out of bounds — resetting to 0.7")
                    base_temps[archetype] = 0.7
        except Exception as e:
            Logger.error(f"Temperature bounds check failed: {e}")

    def _run_generation_diagnostics(self) -> None:
        """Run generation-specific health checks (e.g., mock prompt rendering)."""
        try:
            if not self.prompts:
                Logger.error("Diagnostics failed — prompts unavailable")
                return
            test_prompt = self.prompts.get("user_template", "").format(recipient="Test Recipient")
            if not isinstance(test_prompt, str) or len(test_prompt) == 0:
                Logger.error("Diagnostics failed — invalid prompt rendering")
        except Exception as e:
            Logger.error(f"Generation diagnostics exception: {e}")
