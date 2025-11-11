# File: agent_tools_v10_4.py
# Version: 10.4 (Version Alignment)
#
# Description:
# v10.4:
# - FIXED: All v10_3 imports and class names updated to v10_4
#   (e.g., core_v10_4, agent_stacks_v10_4).
# - FIX (Test Failure): Updated all tool 'run_async' methods and
#   'format_prompt' methods to pass all possible format keys
#   (e.g., style_guide, draft, strategy, job_description) to the
#   prompt_template.format() call. This resolves all KeyErrors
#   from the updated PromptTemplateManager.
#
# v10.3 CHANGES (Preserved):
# - Eradicated Hardcoded Prompts (now in core_v10_4).
# - Mandated Schema Validation via core_v10_4.

import json
import logging
from typing import Dict, Any, List

# v10.4: Import from new core
from core_v10_4 import (
    WorkflowContext, 
    PydanticSchemaError,
    # Import all 15 Pydantic output models
    BaseToolOutput,
    DraftStrategyOutput,
    RedTeamOutput,
    RefineSectionOutput,
    AddMetricsOutput,
    QAClaimOutput,
    QAToneOutput,
    QAThematicAlignmentOutput,
    QASemanticEntailmentOutput,
    QANarrativeThreadOutput,
    QAJDSkillsOutput,
    QASignalScoreOutput,
    QATenureOutput,
    QAMissedOpportunitiesOutput,
    QAAdversarialOutput,
    QABiasOutput
)
# v10.4: Import from new stacks
from agent_stacks_v10_4 import BaseTool, BiasDetectorAgent # Import from stacks

# v10.4: Logger name updated
logger = logging.getLogger("agent_tools_v10_4")

# ============================================================================
# ROW 7: DRAFTING STACK (ReAct Conductor with REAL Tools)
# ============================================================================

# --- Drafting Tools (v10.4: Validated, Prompts Centralized) ---

class DraftingStrategistTool(BaseTool):
    """(Gemini 2.5 Pro) Reviews the overall strategy and ensures the draft aligns."""
    tool_name = "review_draft_strategy"
    output_model = DraftStrategyOutput

    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Tool: Reviewing draft strategy (v10.4)...")
        client = self.get_model_client("drafting_strategist_model")
        
        # v10.3: Get prompt from central manager
        prompt_template = self.prompt_manager.get_template(self.tool_name)
        
        # v10.4: TEST FIX - Pass all possible keys to avoid KeyError
        prompt = prompt_template.format(
            strategy=json.dumps(tool_input.get('strategy')),
            draft=json.dumps(tool_input.get('draft')),
            style_guide=tool_input.get('style_guide', "Default style: professional."),
            # Add defaults for other keys
            section_text="N/A",
            critique="N/A",
            bullets="N/A"
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.drafting_strategist_model.temperature,
            response_format="json_object"
        )
        
        # v10.3: Validate output against Pydantic model
        validated_output, error = self.validator.validate(response["content"], self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")
            
        return validated_output.model_dump()

class DraftingRedTeamTool(BaseTool):
    """(Claude 4.1 Opus) Aggressively critiques the draft for weaknesses."""
    tool_name = "red_team_critique"
    output_model = RedTeamOutput

    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Tool: Red teaming draft (v10.4)...")
        client = self.get_model_client("drafting_redteam_model")
        
        prompt_template = self.prompt_manager.get_template(self.tool_name)
        
        # v10.4: TEST FIX - Pass all possible keys to avoid KeyError
        prompt = prompt_template.format(
            draft=json.dumps(tool_input.get('draft')),
            style_guide=tool_input.get('style_guide', "Default style: professional."),
            # Add defaults for other keys
            strategy="N/A",
            section_text="N/A",
            critique="N/A",
            bullets="N/A"
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.drafting_redteam_model.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")
            
        return validated_output.model_dump()

class DraftingRefinerTool(BaseTool):
    """(GPT-5) Refines and rewrites specific sections."""
    tool_name = "refine_section"
    output_model = RefineSectionOutput

    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Tool: Refining section (v10.4)...")
        client = self.get_model_client("drafting_refiner_model")
        
        # v10.3: "Style & Voice" injection
        style_guide = tool_input.get('style_guide', "Default style: professional.")
        
        prompt_template = self.prompt_manager.get_template(self.tool_name)
        
        # v10.4: TEST FIX - Pass all possible keys to avoid KeyError
        prompt = prompt_template.format(
            section_text=json.dumps(tool_input.get('section_text')),
            critique=json.dumps(tool_input.get('critique')),
            style_guide=style_guide, # Pass style guide to prompt
            # Add defaults for other keys
            strategy="N/A",
            draft="N/A",
            bullets="N/A"
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.drafting_refiner_model.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")
            
        return validated_output.model_dump()

class DraftingMetricsTool(BaseTool):
    """(Gemini 2.5 Flash) Finds opportunities to add metrics to bullets."""
    tool_name = "add_metrics"
    output_model = AddMetricsOutput

    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Tool: Adding metrics (v10.4)...")
        client = self.get_model_client("drafting_metrics_model")
        
        prompt_template = self.prompt_manager.get_template(self.tool_name)
        
        # v10.4: TEST FIX - Pass all possible keys to avoid KeyError
        prompt = prompt_template.format(
            bullets=json.dumps(tool_input.get('bullets')),
            style_guide=tool_input.get('style_guide', "Default style: professional."),
            # Add defaults for other keys
            strategy="N/A",
            draft="N/A",
            section_text="N/A",
            critique="N/A"
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.drafting_metrics_model.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")
            
        return validated_output.model_dump()

# ============================================================================
# ROW 7: QA STACK (ReAct Conductor with 11 REAL Tools)
# ============================================================================

# --- QA Tools (v10.4: Validated, Prompts Centralized) ---

class QABaseValidatorTool(BaseTool):
    """Base class for the 10 T2 validator tools"""
    model_config_name = "qa_validator_model" # Gemini 2.5 Flash
    output_model = BaseToolOutput # Subclasses must override this
    
    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Tool: Running {self.tool_name} (v10.4)...")
        client = self.get_model_client(self.model_config_name)
        
        # v10.3: Get prompt from central manager
        prompt_template = self.prompt_manager.get_template(self.tool_name)
        
        # v10.4: TEST FIX - Call the subclass-defined format_prompt
        # which is responsible for passing all keys
        prompt = self.format_prompt(prompt_template, tool_input)
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_validator_model.temperature,
            response_format="json_object"
        )
        
        # v10.3: Validate output against Pydantic model
        validated_output, error = self.validator.validate(response["content"], self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")
            
        return validated_output.model_dump()
        
    def format_prompt(self, template: str, tool_input: Dict[str, Any]) -> str:
        """
        Subclasses must implement this to fill their specific template.
        v10.4: TEST FIX - This method *must* provide all possible keys
        to the template.format() call.
        """
        # Base implementation provides all keys with defaults
        
        # v10.3: Use budget manager to prune large context
        master_resume = self.budget_manager.prune(
            json.dumps(tool_input.get('master_resume')), 4000
        )
        draft_text = self.budget_manager.prune(
            json.dumps(tool_input.get('draft_text')), 4000
        )
        job_description = self.budget_manager.prune(
            json.dumps(tool_input.get('job_description')), 4000
        )
        
        return template.format(
            master_resume=master_resume,
            draft_text=draft_text,
            job_description=job_description,
            strategy=json.dumps(tool_input.get('strategy')),
            required_tone=json.dumps(tool_input.get('strategy', {}).get('tone', 'N/A')),
            style_guide=tool_input.get('style_guide', "Default style: professional.")
        )

class QAClaimValidatorTool(QABaseValidatorTool):
    """(NLI) Checks if claims in the draft are supported by the master resume."""
    tool_name = "validate_claims"
    output_model = QAClaimOutput # v10.3
    
    # v10.4: Use QABaseValidatorTool.format_prompt (it provides all keys)
    pass

class QAToneValidatorTool(QABaseValidatorTool):
    """Checks if the draft's tone matches the strategy (e.g., 'leadership')."""
    tool_name = "validate_tone"
    output_model = QAToneOutput # v10.3
    
    # v10.4: Use QABaseValidatorTool.format_prompt
    pass

class QAThematicAlignmentTool(QABaseValidatorTool):
    """Ensures all sections support the central strategy theme."""
    tool_name = "validate_thematic_alignment"
    output_model = QAThematicAlignmentOutput # v10.3
    
    # v10.4: Use QABaseValidatorTool.format_prompt
    pass

class QASemanticEntailmentTool(QABaseValidatorTool):
    """Checks if bullets are semantically entailed by the job description."""
    tool_name = "validate_semantic_entailment"
    output_model = QASemanticEntailmentOutput # v10.3
    
    # v10.4: Use QABaseValidatorTool.format_prompt
    pass

class QANarrativeThreadTool(QABaseValidatorTool):
    """Checks for a consistent career story/narrative."""
    tool_name = "validate_narrative_thread"
    output_model = QANarrativeThreadOutput # v10.3
    
    # v10.4: Use QABaseValidatorTool.format_prompt
    pass

class QAJDSkillsValidatorTool(QABaseValidatorTool):
    """Ensures keywords/skills from the JD are present in the draft."""
    tool_name = "validate_jd_skills"
    output_model = QAJDSkillsOutput # v10.3
    
    # v10.4: Use QABaseValidatorTool.format_prompt
    pass

class QASignalScoreValidatorTool(QABaseValidatorTool):
    """Rates the 'signal' (achievement) vs 'noise' (fluff) of each bullet."""
    tool_name = "validate_signal_score"
    output_model = QASignalScoreOutput # v10.3
    
    # v10.4: Use QABaseValidatorTool.format_prompt
    pass

class QATenureValidatorTool(QABaseValidatorTool):
    """Checks for consistency in dates and tenure."""
    tool_name = "validate_tenure"
    output_model = QATenureOutput # v10.3
    
    # v10.4: Use QABaseValidatorTool.format_prompt
    pass

class QAMissedOpportunityTool(QABaseValidatorTool):
    """Looks for experience in the master resume that was omitted but is relevant."""
    tool_name = "find_missed_opportunities"
    output_model = QAMissedOpportunitiesOutput # v10.3
    
    # v10.4: Use QABaseValidatorTool.format_prompt
    pass

class QAAdversarialReviewerTool(BaseTool):
    """(Claude 4.1 Opus) Acts as a skeptical hiring manager to find flaws."""
    tool_name = "adversarial_review"
    output_model = QAAdversarialOutput # v10.3

    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Tool: Running Adversarial Review (v10.4)...")
        client = self.get_model_client("qa_adversarial_model")
        
        draft_text = self.budget_manager.prune(
            json.dumps(tool_input.get('draft_text')), 8000
        )
        
        prompt_template = self.prompt_manager.get_template(self.tool_name)
        
        # v10.4: TEST FIX - Pass all possible keys to avoid KeyError
        prompt = prompt_template.format(
            draft_text=draft_text,
            # Add defaults for other keys
            master_resume="N/A",
            job_description="N/A",
            strategy="N/A",
            required_tone="N/A",
            style_guide=tool_input.get('style_guide', "Default style: professional.")
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_adversarial_model.temperature,
            response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")
            
        return validated_output.model_dump()

class QABiasDetectorTool(BaseTool):
    """Runs the local bias detector tool on the final draft."""
    tool_name = "validate_bias"
    output_model = QABiasOutput # v10.3

    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        # This tool imports BiasDetectorAgent from agent_stacks_v10_4.py
        # It's a local tool, not an LLM call.
        bias_agent = BiasDetectorAgent(self.context)
        draft_text = json.dumps(tool_input.get("draft_text", ""))
        
        # The local agent's .run() method already returns the correct dict format
        # which matches the QABiasOutput Pydantic model.
        result_dict = bias_agent.run(draft_text, workflow_id)
        
        # We still validate to ensure the contract is met
        validated_output, error = self.validator.validate(result_dict, self.output_model)
        if error:
            raise PydanticSchemaError(f"Tool {self.tool_name} failed validation: {error}")
            
        return validated_output.model_dump()