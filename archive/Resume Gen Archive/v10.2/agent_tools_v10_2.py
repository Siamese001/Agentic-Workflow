# File: agent_tools_v10_2.py
# Version: 10.2 (ChromaDB Semantic RAG)
#
# Description:
# v10.2: Imports updated to v10.2. Tools preserved.
#
# Contains the 15 specialist "expert tools" for the Drafting and QA
# conductors. This file imports BaseTool and BiasDetectorAgent
# from agent_stacks_v10_2.py, creating a one-way dependency.

import json
import logging
from typing import Dict, Any

# v10.2: Import from new core
from core_v10_2 import WorkflowContext, BaseAgent
# v10.2: Import from new stacks
from agent_stacks_v10_2 import BaseTool, BiasDetectorAgent # Import from stacks

logger = logging.getLogger("agent_tools_v10_2")

# ============================================================================
# ROW 7: DRAFTING STACK (ReAct Conductor with REAL Tools)
# ============================================================================

# --- Drafting Tools (Design-Aligned, No Longer Mocked) ---

class DraftingStrategistTool(BaseTool):
    """(Gemini 2.5 Pro) Reviews the overall strategy and ensures the draft aligns."""
    tool_name = "review_draft_strategy"
    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Tool: Reviewing draft strategy (Gemini 2.5 Pro)...")
        client = self.get_model_client("drafting_strategist_model")
        
        prompt = f"""Review the draft against the strategy.
Strategy: {json.dumps(tool_input.get('strategy'))}
Draft: {json.dumps(tool_input.get('draft'))}
Output JSON: {{"status": "success", "feedback": "Your strategic feedback"}}"""
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.drafting_strategist_model.temperature,
            response_format="json_object"
        )
        return response["content"]

class DraftingRedTeamTool(BaseTool):
    """(Claude 4.1 Opus) Aggressively critiques the draft for weaknesses."""
    tool_name = "red_team_critique"
    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Tool: Red teaming draft (Claude 4.1 Opus)...")
        client = self.get_model_client("drafting_redteam_model")
        
        prompt = f"""You are a harsh red team agent. Find all weaknesses in this draft.
Draft: {json.dumps(tool_input.get('draft'))}
Output JSON: {{"status": "success", "weaknesses_found": ["weakness 1", "weakness 2"]}}"""
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.drafting_redteam_model.temperature,
            response_format="json_object"
        )
        return response["content"]

class DraftingRefinerTool(BaseTool):
    """(GPT-5) Refines and rewrites specific sections."""
    tool_name = "refine_section"
    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Tool: Refining section {tool_input.get('section')} (GPT-5)...")
        client = self.get_model_client("drafting_refiner_model")
        
        prompt = f"""Refine this section of the resume.
Section to refine: {json.dumps(tool_input.get('section_text'))}
Critique: {json.dumps(tool_input.get('critique'))}
Output JSON: {{"status": "success", "refined_text": "new refined text..."}}"""
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.drafting_refiner_model.temperature,
            response_format="json_object"
        )
        return response["content"]

class DraftingMetricsTool(BaseTool):
    """(Gemini 2.5 Flash) Finds opportunities to add metrics to bullets."""
    tool_name = "add_metrics"
    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Tool: Adding metrics (Gemini 2.5 Flash)...")
        client = self.get_model_client("drafting_metrics_model")
        
        prompt = f"""Review these bullets and suggest where to add metrics.
Bullets: {json.dumps(tool_input.get('bullets'))}
Output JSON: {{"status": "success", "suggestions": ["Add % to bullet 1", "Add $ to bullet 2"]}}"""
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.drafting_metrics_model.temperature,
            response_format="json_object"
        )
        return response["content"]

# ============================================================================
# ROW 7: QA STACK (ReAct Conductor with 11 REAL Tools)
# ============================================================================

# --- QA Tools (Design-Aligned, No Longer Mocked) ---
# All T2 tools use "qa_validator_model" (Gemini 2.5 Flash)
# The T1 tool uses "qa_adversarial_model" (Claude 4.1 Opus)

class QABaseValidatorTool(BaseTool):
    """Base class for the 10 T2 validator tools"""
    model_config_name = "qa_validator_model" # Gemini 2.5 Flash
    
    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Tool: Running {self.tool_name} (Gemini 2.5 Flash)...")
        client = self.get_model_client(self.model_config_name)
        
        prompt = self.get_prompt(tool_input)
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_validator_model.temperature,
            response_format="json_object"
        )
        return response["content"]
        
    def get_prompt(self, tool_input: Dict[str, Any]) -> str:
        """Subclasses must implement this"""
        raise NotImplementedError

class QAClaimValidatorTool(QABaseValidatorTool):
    """(NLI) Checks if claims in the draft are supported by the master resume."""
    tool_name = "validate_claims"
    def get_prompt(self, tool_input: Dict[str, Any]) -> str:
        return f"""Perform an NLI check. Are the claims in the draft entailed by the source resume?
Source: {json.dumps(tool_input.get('master_resume'))}
Draft: {json.dumps(tool_input.get('draft_text'))}
Output JSON: {{"status": "success", "unsupported_claims": 0, "feedback": "All claims appear supported."}}"""

class QAToneValidatorTool(QABaseValidatorTool):
    """Checks if the draft's tone matches the strategy (e.g., 'leadership')."""
    tool_name = "validate_tone"
    def get_prompt(self, tool_input: Dict[str, Any]) -> str:
        return f"""Check if the draft's tone matches the required tone.
Required Tone: {json.dumps(tool_input.get('strategy', {}).get('tone'))}
Draft: {json.dumps(tool_input.get('draft_text'))}
Output JSON: {{"status": "success", "tone_match": true, "current_tone": "professional"}}"""

class QAThematicAlignmentTool(QABaseValidatorTool):
    """Ensures all sections support the central strategy theme."""
    tool_name = "validate_thematic_alignment"
    def get_prompt(self, tool_input: Dict[str, Any]) -> str:
        return f"""Check if the draft aligns with the strategy's focus areas.
Strategy: {json.dumps(tool_input.get('strategy'))}
Draft: {json.dumps(tool_input.get('draft_text'))}
Output JSON: {{"status": "success", "alignment_score": 0.9, "feedback": "Strongly aligned."}}"""

class QASemanticEntailmentTool(QABaseValidatorTool):
    """Checks if bullets are semantically entailed by the job description."""
    tool_name = "validate_semantic_entailment"
    def get_prompt(self, tool_input: Dict[str, Any]) -> str:
        return f"""Check if the resume draft is semantically entailed by the job description.
Job Description: {json.dumps(tool_input.get('job_description'))}
Draft: {json.dumps(tool_input.get('draft_text'))}
Output JSON: {{"status": "success", "entailment_score": 0.85}}"""

class QANarrativeThreadTool(QABaseValidatorTool):
    """Checks for a consistent career story/narrative."""
    tool_name = "validate_narrative_thread"
    def get_prompt(self, tool_input: Dict[str, Any]) -> str:
        return f"""Check this draft for a clear and consistent career narrative.
Draft: {json.dumps(tool_input.get('draft_text'))}
Output JSON: {{"status": "success", "narrative_clear": true}}"""

class QAJDSkillsValidatorTool(QABaseValidatorTool):
    """Ensures keywords/skills from the JD are present in the draft."""
    tool_name = "validate_jd_skills"
    def get_prompt(self, tool_input: Dict[str, Any]) -> str:
        return f"""Check if keywords from the job description are in the draft.
Job Description: {json.dumps(tool_input.get('job_description'))}
Draft: {json.dumps(tool_input.get('draft_text'))}
Output JSON: {{"status": "success", "keyword_coverage": 0.9, "missing_keywords": ["kubernetes"]}}"""

class QASignalScoreValidatorTool(QABaseValidatorTool):
    """Rates the 'signal' (achievement) vs 'noise' (fluff) of each bullet."""
    tool_name = "validate_signal_score"
    def get_prompt(self, tool_input: Dict[str, Any]) -> str:
        return f"""Rate the 'signal-to-noise' ratio of these bullets (achievements vs. fluff).
Draft: {json.dumps(tool_input.get('draft_text'))}
Output JSON: {{"status": "success", "avg_signal_score": 8.5}}"""

class QATenureValidatorTool(QABaseValidatorTool):
    """Checks for consistency in dates and tenure."""
    tool_name = "validate_tenure"
    def get_prompt(self, tool_input: Dict[str, Any]) -> str:
        return f"""Check for date/tenure gaps or overlaps in this draft.
Draft: {json.dumps(tool_input.get('draft_text'))}
Output JSON: {{"status": "success", "gaps_found": 0, "overlaps_found": 0}}"""

class QAMissedOpportunityTool(QABaseValidatorTool):
    """Looks for experience in the master resume that was omitted but is relevant."""
    tool_name = "find_missed_opportunities"
    def get_prompt(self, tool_input: Dict[str, Any]) -> str:
        return f"""Find relevant experience from the master resume that was missed in the draft.
Master Resume: {json.dumps(tool_input.get('master_resume'))}
Draft: {json.dumps(tool_input.get('draft_text'))}
Output JSON: {{"status": "success", "opportunities_found": ["Add Python project from master."]}}"""

class QAAdversarialReviewerTool(BaseTool):
    """(Claude 4.1 Opus) Acts as a skeptical hiring manager to find flaws."""
    tool_name = "adversarial_review"
    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Tool: Running Adversarial Review (Claude 4.1 Opus)...")
        # Design-Aligned: Use qa_adversarial_model
        client = self.get_model_client("qa_adversarial_model")
        
        prompt = f"""You are a skeptical hiring manager. Find all red flags and flaws in this resume.
Draft: {json.dumps(tool_input.get('draft_text'))}
Output JSON: {{"status": "success", "red_flags": ["Slight job hop in 2022, but explained."]}}"""
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_adversarial_model.temperature,
            response_format="json_object"
        )
        return response["content"]

class QABiasDetectorTool(BaseTool):
    """Runs the local bias detector tool on the final draft."""
    tool_name = "validate_bias"
    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        # This tool imports BiasDetectorAgent from agent_stacks_v10_2.py
        bias_agent = BiasDetectorAgent(self.context)
        draft_text = json.dumps(tool_input.get("draft_text", ""))
        return bias_agent.run(draft_text, workflow_id)