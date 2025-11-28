# File: agent_orchestration_v10_4.py
# Version: 10.4 (CircuitBreaker Fix)
#
# Description:
# v10.4:
# - FIXED: Removed import of CircuitBreaker from run_batch.
# - FIXED: Imports CircuitBreaker from core_v10_4.
# - FIXED: All v10_3 imports and class names updated to v10_4.
# - FIX (Test Failure): Moved graph node functions (run_sanitize_pii, etc.)
#   and conditional edges (check_ambiguity, etc.) to the module level
#   to allow for proper test patching and import.
# - FIX (Test Failure): Modified ReActConductorAgent and QAConductorAgent
#   exception handling to NOT record a failure if the exception is
#   already a CircuitBreakerOpenError.
# - FIX (Test Failure): Updated run_generate_bullets to pass the strategy
#   to the bullet generator agent, satisfying new prompt requirements.
# - FIX (Type Error): Added Pydantic model reconstruction to all nodes
#   that access `strategy_plan` (e.g., run_detect_ambiguity, 
#   run_generate_bullets, run_drafting). This prevents TypeErrors when
#   LangGraph serializes the Pydantic model to a dict between steps.

import json
import logging
import asyncio
from typing import Dict, Any, List

# v10.4: Import from new core
from core_v10_4 import (
    WorkflowContext, BaseAgent, StrategyPlan, PydanticSchemaError,
    exponential_backoff_retry, CircuitBreakerOpenError,
    # v10.4: Import CircuitBreaker from core
    CircuitBreaker,
    ConfigV10_4 # Import config for context typing
)
from langgraph.graph import StateGraph, END
try:
    from langgraph.checkpoint.redis import RedisSaver
except ImportError:
    from langgraph.checkpoint.sqlite import SqliteSaver as RedisSaver
from langgraph.errors import GraphRecursionError

# v10.4: DELETED import from run_batch
# from run_batch_v10_3 import CircuitBreaker # GONE

# Make HIL import conditional for environment compatibility
try:
    from langgraph.prebuilt import human_in_the_loop
    HIL_AVAILABLE = True
except ImportError:
    HIL_AVAILABLE = False
    human_in_the_loop = None # type: ignore
    logging.getLogger(__name__).warning(
        "human_in_the_loop not available - HIL features will be disabled"
    )

# v10.4: Import from new stacks
from agent_stacks_v10_4 import (
    PIISanitizerAgent,
    BiasDetectorAgent,
    ToTStrategistAgent,
    PromptEngineerAgent,
    RAG_SearchAgent,
    AsyncBulletGeneratorAgent,
    AsyncBulletCritiqueAgent,
    HILAmbiguityDetectorAgent,
    HILFeedbackRouterAgent
)

# v10.4: Import from new tools file
from agent_tools_v10_4 import (
    DraftingStrategistTool,
    DraftingRedTeamTool,
    DraftingRefinerTool,
    DraftingMetricsTool,
    QAClaimValidatorTool,
    QAToneValidatorTool,
    QAThematicAlignmentTool,
    QASemanticEntailmentTool,
    QANarrativeThreadTool,
    QAAdversarialReviewerTool,
    QAJDSkillsValidatorTool,
    QASignalScoreValidatorTool,
    QABiasDetectorTool,
    QATenureValidatorTool,
    QAMissedOpportunityTool
)

# v10.4: Logger name updated
logger = logging.getLogger("agent_orchestration_v10_4")

# v10.4: Define context for module-level functions
# This is a module-level variable that will be SET by get_graph_app
# This is necessary for the node functions to access the config
# A bit of a hack, but required by the test patching design.
context: WorkflowContext = None # type: ignore

# ============================================================================
# DRAFTING CONDUCTOR (v10.4: Circuit Breaker Fix)
# ============================================================================

class ReActConductorAgent(BaseAgent):
    """v10.3: ReAct conductor with circuit breakers for tool calls."""
    
    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.tools = {
            "review_draft_strategy": DraftingStrategistTool(context, debug_mode),
            "red_team_critique": DraftingRedTeamTool(context, debug_mode),
            "refine_section": DraftingRefinerTool(context, debug_mode),
            "add_metrics": DraftingMetricsTool(context, debug_mode)
        }
        self.tool_schemas = [t.get_schema() for t in self.tools.values()]
        
        # v10.3: Mandate Circuit Breakers per tool
        # v10.4: CircuitBreaker class is imported from core_v10_4
        self.tool_breakers = {
            name: CircuitBreaker(
                failure_threshold=self.config.batch_config.circuit_breaker_failure_threshold
            ) for name in self.tools
        }
        self.style_guide = "Style: Professional, high-impact, and metrics-driven."

    async def run_async(self, task_context: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Running ReAct Drafting Conductor (v10.4)...")
        
        # Feedback-aware tuning can be re-implemented here
        # Example: Adjust conductor_temperature based on feedback
        
        client = self.get_model_client("react_conductor_model")
        
        # v10.3: Strategy is now a Pydantic model
        # v10.4: FIX - task_context['strategy'] may be a dict, ensure it's a Pydantic model
        strategy_plan = task_context.get('strategy')
        if isinstance(strategy_plan, dict):
            strategy_plan = StrategyPlan.model_validate(strategy_plan)
        
        strategy_json = strategy_plan.model_dump_json()
        
        messages = [{
            "role": "user",
            "content": f"""You are a ReAct drafting conductor.
Task Context: {json.dumps({"strategy": strategy_json})}
Tools: {json.dumps(self.tool_schemas)}
Plan:
1.  Call `review_draft_strategy`.
2.  Call `add_metrics`.
3.  Call `red_team_critique`.
4.  If weaknesses, call `refine_section`.
5.  Assemble final draft.

Output thoughts and tool calls in JSON:
{{"thought": "Your reasoning", "tool_call": {{"name": "tool_name", "input": {{"arg": "value"}}}}}}
When finished, output:
{{"thought": "Draft complete", "final_draft": {{...}}}}
"""
        }]
        
        final_draft = {}
        max_steps = self.config.agent_stacks.conductor_max_steps
        
        for step in range(max_steps):
            response = await client.chat_completion_async(
                messages=messages,
                temperature=self.config.agent_stacks.conductor_temperature,
                response_format="json_object"
            )
            
            # v10.4: Use validator for safer parsing
            step_data, error = self.validator.validate(response["content"], dict)
            if error:
                logger.warning(f"ReAct step {step} failed validation: {error}")
                messages.append({"role": "user", "content": f"Error: Invalid JSON response from LLM. {error}"})
                continue

            messages.append({"role": "assistant", "content": json.dumps(step_data)})
            
            if "final_draft" in step_data:
                final_draft = step_data["final_draft"]
                self.log_feedback(workflow_id, "react_conductor_draft", "success", {"steps_executed": step})
                return {"final_output": final_draft, "steps": step}
            
            if "tool_call" in step_data:
                tool_name = step_data["tool_call"].get("name")
                tool_input = step_data["tool_call"].get("input", {})
                
                if not tool_name:
                    messages.append({"role": "user", "content": f"Error: LLM tool_call missing 'name'."})
                    continue

                if tool_name not in self.tools:
                    messages.append({"role": "user", "content": f"Error: Tool '{tool_name}' not found."})
                    continue
                
                # Add context for tools
                tool_input["draft"] = task_context.get("bullets")
                tool_input["strategy"] = strategy_plan.model_dump() # Pass as dict
                tool_input["style_guide"] = self.style_guide
                
                try:
                    # v10.3: Check circuit breaker before tool call
                    breaker = self.tool_breakers[tool_name]
                    breaker.check()
                    
                    tool = self.tools[tool_name]
                    tool_result = await tool.run_async(tool_input, workflow_id)
                    
                    # v10.3: Record success
                    breaker.record_success()
                    messages.append({"role": "user", "content": f"Tool Result: {json.dumps(tool_result)}"})
                
                except (CircuitBreakerOpenError, PydanticSchemaError, Exception) as e:
                    # v10.4: TEST FIX - Only record failure if it's NOT a breaker error
                    self.log_error(f"Tool {tool_name} failed: {e}")
                    if not isinstance(e, CircuitBreakerOpenError):
                        if tool_name in self.tool_breakers:
                            self.tool_breakers[tool_name].record_failure()
                    
                    error_msg = f"Error: Tool '{tool_name}' failed. Reason: {str(e)}"
                    messages.append({"role": "user", "content": error_msg})

        self.log_feedback(workflow_id, "react_conductor_draft", "failure", {"reason": "Max steps reached"})
        return {"final_output": {"error": "Max steps reached"}, "steps": max_steps}

# ============================================================================
# QA CONDUCTOR (v10.4: Circuit Breaker Fix)
# ============================================================================

class QAConductorAgent(BaseAgent):
    """v10.3: ReAct QA Conductor with circuit breakers and context budgeting."""
    
    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.tools = {
            "validate_claims": QAClaimValidatorTool(context, debug_mode),
            "validate_tone": QAToneValidatorTool(context, debug_mode),
            "validate_thematic_alignment": QAThematicAlignmentTool(context, debug_mode),
            "validate_semantic_entailment": QASemanticEntailmentTool(context, debug_mode),
            "validate_narrative_thread": QANarrativeThreadTool(context, debug_mode),
            "adversarial_review": QAAdversarialReviewerTool(context, debug_mode),
            "validate_jd_skills": QAJDSkillsValidatorTool(context, debug_mode),
            "validate_signal_score": QASignalScoreValidatorTool(context, debug_mode),
            "validate_bias": QABiasDetectorTool(context, debug_mode),
            "validate_tenure": QATenureValidatorTool(context, debug_mode),
            "find_missed_opportunities": QAMissedOpportunityTool(context, debug_mode)
        }
        self.tool_schemas = [t.get_schema() for t in self.tools.values()]
        
        # v10.3: Mandate Circuit Breakers per tool
        # v10.4: CircuitBreaker class is imported from core_v10_4
        self.tool_breakers = {
            name: CircuitBreaker(
                failure_threshold=self.config.batch_config.circuit_breaker_failure_threshold
            ) for name in self.tools
        }
        self.style_guide = "Style: Ensure professional, clear, and unbiased language."

    async def run_async(self, state: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Running ReAct QA Conductor (v10.4)...")
        
        # Feedback-aware tuning can be re-implemented here
        # Example: Prioritize tools that failed in the past
        
        max_steps = 15
        
        client = self.get_model_client("react_conductor_model")
        
        # v10.3: Force Context Budgeting
        pruned_draft = self.budget_manager.prune(
            json.dumps(state['draft']['sections']), 4000
        )
        pruned_master_resume = self.budget_manager.prune(
            json.dumps(state['resume']['master_resume']), 4000
        )
        pruned_jd = self.budget_manager.prune(state['job']['raw_jd'], 2000)
        
        # v10.3: Strategy is now a Pydantic model
        # v10.4: FIX - strategy_plan is already reconstructed in the
        # run_qa_validation node, so state['strategy']['strategy_plan']
        # is a Pydantic model.
        strategy_plan = state['strategy']['strategy_plan']
        strategy_json = strategy_plan.model_dump_json()
        
        messages = [{
            "role": "user",
            "content": f"""You are a ReAct QA conductor. Your goal is to validate the draft.
Draft (Pruned): {pruned_draft}
Tools: {json.dumps(self.tool_schemas)}
Plan:
1.  Run `validate_claims` and `validate_tenure`.
2.  Run `validate_jd_skills` and `validate_thematic_alignment`.
3.  Run `validate_tone`, `validate_narrative_thread`, and `validate_signal_score`.
4.  Run `validate_bias`.
5.  Run `find_missed_opportunities`.
6.  Run `adversarial_review` as a final check.
7.  Compile all feedback into a final QA report.

Output thoughts/tool calls in JSON:
{{"thought": "Your reasoning", "tool_call": {{"name": "tool_name", "input": {{"arg": "value"}}}}}}
When finished, output:
{{"thought": "QA complete", "final_qa_report": {{"qa_passed": true/false, "issues": [...]}}}}
"""
        }]
        
        final_report = {}
        all_tool_results = []
        
        # Prepare budgeted context for tools
        tool_context = {
            "draft_text": pruned_draft,
            "master_resume": pruned_master_resume, # Pass pruned
            "job_description": pruned_jd,           # Pass pruned
            "strategy": strategy_plan.model_dump(), # Pass as dict
            "style_guide": self.style_guide
        }
        
        for step in range(max_steps):
            response = await client.chat_completion_async(
                messages=messages,
                temperature=0.4,
                response_format="json_object"
            )
            
            # v10.4: Use validator for safer parsing
            step_data, error = self.validator.validate(response["content"], dict)
            if error:
                logger.warning(f"QA step {step} failed validation: {error}")
                messages.append({"role": "user", "content": f"Error: Invalid JSON response from LLM. {error}"})
                continue
            
            messages.append({"role": "assistant", "content": json.dumps(step_data)})
            
            if "final_qa_report" in step_data:
                final_report = step_data["final_qa_report"]
                final_report["all_tool_results"] = all_tool_results
                self.log_feedback(workflow_id, "react_conductor_qa", "success", {"steps_executed": step})
                return final_report
            
            if "tool_call" in step_data:
                tool_name = step_data["tool_call"].get("name")
                tool_input = step_data["tool_call"].get("input", {})

                if not tool_name:
                    messages.append({"role": "user", "content": f"Error: LLM tool_call missing 'name'."})
                    continue

                if tool_name not in self.tools:
                    messages.append({"role": "user", "content": f"Error: Tool '{tool_name}' not found."})
                    continue
                
                # Inject the budgeted context
                tool_input.update(tool_context)
                
                try:
                    # v10.3: Check circuit breaker
                    breaker = self.tool_breakers[tool_name]
                    breaker.check()
                    
                    tool = self.tools[tool_name]
                    tool_result = await tool.run_async(tool_input, workflow_id)
                    
                    breaker.record_success()
                    all_tool_results.append({tool_name: tool_result})
                    messages.append({"role": "user", "content": f"Tool Result: {json.dumps(tool_result)}"})
                
                except (CircuitBreakerOpenError, PydanticSchemaError, Exception) as e:
                    # v10.4: TEST FIX - Only record failure if it's NOT a breaker error
                    self.log_error(f"QA Tool {tool_name} failed: {e}")
                    if not isinstance(e, CircuitBreakerOpenError):
                        if tool_name in self.tool_breakers:
                            self.tool_breakers[tool_name].record_failure()
                    
                    error_msg = f"Error: Tool '{tool_name}' failed. Reason: {str(e)}"
                    messages.append({"role": "user", "content": error_msg})
        
        self.log_feedback(workflow_id, "react_conductor_qa", "failure", {"reason": "Max steps reached"})
        return {"error": "Max steps reached", "steps": max_steps, "all_tool_results": all_tool_results, "qa_passed": False}

# ============================================================================
# LANGGRAPH NODE & EDGE FUNCTIONS (v10.4: Moved to module level)
# ============================================================================

# --- NODE DEFINITIONS (v10.4: Moved to module level) ---

@exponential_backoff_retry()
async def run_sanitize_pii(state: dict) -> dict:
    """Node 0: Sanitize PII"""
    # v10.4: Use module-level context
    pii_agent = PIISanitizerAgent(context)
    sanitized = pii_agent.run(state['resume']['master_resume'])
    
    bias_agent = BiasDetectorAgent(context)
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    bias_result = bias_agent.run(state['job']['raw_jd'], workflow_id)
    
    return {
        "resume": {"sanitized_resume": sanitized},
        "safety": {"bias_detected": bias_result['bias_detected']}
    }

@exponential_backoff_retry()
async def run_tot_strategy(state: dict) -> dict:
    """Node 1: ToT strategy"""
    # v10.4: Use module-level context
    strategist = ToTStrategistAgent(context)
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    strategy_result = await strategist.run_async(
        {
            "job_title": state['job']['job_title'], 
            "company": state['job']['company'],
            # v10.4: TEST FIX - Pass job_description
            "job_description": state['job']['raw_jd']
        },
        workflow_id
    )
    # v10.3: Return Pydantic model in state
    return {"strategy": strategy_result}

@exponential_backoff_retry()
async def run_detect_ambiguity(state: dict) -> dict:
    """Node 2: Proactive HIL ambiguity check"""
    # v10.4: Use module-level context
    if not context.config.agent_stacks.enable_hil_stack:
        return {"hil": {"ambiguity_report": {"ambiguity_detected": False, "confidence": 1.0, "reason": "HIL disabled", "question_for_human": ""}}}
        
    detector = HILAmbiguityDetectorAgent(context)
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    
    # v10.4: FIX - Reconstruct Pydantic model from state dict
    strategy_plan = state['strategy']['strategy_plan']
    if isinstance(strategy_plan, dict):
        strategy_plan = StrategyPlan.model_validate(strategy_plan)
    
    ambiguity_result = await detector.run_async(strategy_plan, workflow_id)
    
    # v10.3: Read from Pydantic model
    report = ambiguity_result.get("ambiguity_report")
    if report.confidence < context.config.agent_stacks.ambiguity_confidence_threshold:
            report.ambiguity_detected = False
    
    return {"hil": {"ambiguity_report": report.model_dump()}} # Store as dict

@exponential_backoff_retry()
async def run_prompt_engineering(state: dict) -> dict:
    """Node 2.5: Generate dynamic prompts"""
    # v10.4: Use module-level context
    prompt_agent = PromptEngineerAgent(context)
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    
    # v10.4: FIX - Reconstruct Pydantic model from state dict
    strategy_plan = state['strategy']['strategy_plan']
    if isinstance(strategy_plan, dict):
        strategy_plan = StrategyPlan.model_validate(strategy_plan)
    
    prompts_result = await prompt_agent.run_async(strategy_plan, workflow_id)
    
    return {"prompts": {"prompts": prompts_result.get("prompts").model_dump()}}

@exponential_backoff_retry()
async def run_rag_stack(state: dict) -> dict:
    """Node 3: RAG with Hybrid Search (v10.3)"""
    # v10.4: Use module-level context
    rag_agent = RAG_SearchAgent(context)
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    
    query = f"{state['job']['job_title']} at {state['job']['company']}"
    # v10.4: Use master_resume for RAG, not sanitized_resume
    experience = state['resume']['master_resume'].get('professional_experience', [])
    
    ranked_sections = await rag_agent.run_async(query, experience, workflow_id)
    
    return {"resume": {"experience_bullets": ranked_sections}}

@exponential_backoff_retry()
async def run_generate_bullets(state: dict) -> dict:
    """Node 4: Generate bullets (4-step)"""
    # v10.4: Use module-level context
    bullet_gen = AsyncBulletGeneratorAgent(context)
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    
    # v10.3: Prompts are dicts
    prompt = state['prompts']['prompts'].get('bullet_generation_prompt', "Generate bullets")
    
    # v10.4: FIX - Reconstruct Pydantic model from state dict
    strategy = state['strategy']['strategy_plan']
    if isinstance(strategy, dict):
        strategy = StrategyPlan.model_validate(strategy)
    
    all_bullets = []
    # v10.4: Use experience_bullets (RAG output), not master_resume
    for exp in state['resume']['experience_bullets'][:3]: 
        # v10.4: TEST FIX - Pass strategy
        bullets = await bullet_gen.run_async(prompt, exp, strategy, workflow_id)
        all_bullets.extend([{"text": b, "experience": exp} for b in bullets])
    
    return {"bullets": {"generated_bullets": all_bullets}}

@exponential_backoff_retry()
async def run_critique_bullets(state: dict) -> dict:
    """Node 5: Critique bullets"""
    # v10.4: Use module-level context
    critique_agent = AsyncBulletCritiqueAgent(context)
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    
    critique_prompt = state['prompts']['prompts'].get('critique_prompt', "Critique bullets")
    bullets = state['bullets']['generated_bullets']
    
    critiques = await critique_agent.run_async(bullets, critique_prompt, workflow_id)
    
    return {"bullets": {"critiqued_bullets": critiques}}

@exponential_backoff_retry()
async def run_drafting(state: dict) -> dict:
    """Node 6: Draft assembly with ReAct Conductor"""
    # v10.4: Use module-level context
    conductor = ReActConductorAgent(context)
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    
    good_bullets = [
        b for b in state['bullets']['critiqued_bullets']
        if b.get('critique', {}).get('score', 0) >= 7
    ]
    
    # v10.4: FIX - Reconstruct Pydantic model from state dict
    # Note: We pass the model itself, not a dict
    strategy_plan = state['strategy']['strategy_plan']
    if isinstance(strategy_plan, dict):
        strategy_plan = StrategyPlan.model_validate(strategy_plan)
    
    task_context = {
        "bullets": good_bullets,
        "strategy": strategy_plan # v10.4: Pass Pydantic model
    }
    
    draft = await conductor.run_async(task_context, workflow_id)
    return {"draft": {"sections": draft.get("final_output", {})}}

@exponential_backoff_retry()
async def run_qa_validation(state: dict) -> dict:
    """Node 7: Final QA with ReAct Conductor"""
    # v10.4: Use module-level context
    qa_conductor = QAConductorAgent(context)
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    
    # v10.4: We must reconstruct the StrategyPlan model from its dict form
    # as it gets serialized/deserialized by LangGraph
    if isinstance(state['strategy']['strategy_plan'], dict):
            state['strategy']['strategy_plan'] = StrategyPlan.model_validate(state['strategy']['strategy_plan'])
    
    validation = await qa_conductor.run_async(state, workflow_id)
    
    return {
        "qa": {"validation_results": validation, "qa_passed": validation.get("qa_passed", False)},
        "artifacts": {"artifacts": {"final_resume": state['draft']['sections'], "qa_report": validation}}
    }

# HIL Nodes (9, 10)
@exponential_backoff_retry()
async def run_feedback_router(state: dict) -> dict:
    """Node 10: HIL Feedback Router"""
    # v10.4: Use module-level context
    router = HILFeedbackRouterAgent(context)
    workflow_id = state.get('metadata', {}).get('workflow_id', '')
    
    last_human_message = "Default to drafting"
    # Logic to read actual human feedback would go here
    # For now, it uses the default

    route = await router.run_async(last_human_message, workflow_id)
    return {"hil": {"next_step": route.get("next_step", "DRAFTING")}}

def human_in_the_loop_node(state: dict) -> dict:
    if not HIL_AVAILABLE:
        logger.warning("HIL not available. Skipping pause.")
        return {}
    try:
        # This is the synchronous HIL pause
        human_in_the_loop(timeout=3600) 
    except GraphRecursionError:
        # This error is raised when feedback is submitted, interrupting the pause
        logger.info("HIL pause interrupted by user feedback.")
    except Exception as e:
        logger.error(f"HIL node failed: {e}")
    return {}

# --- CONDITIONAL EDGES (v10.4: Moved to module level) ---

def check_ambiguity(state: dict) -> str:
    """Node 2 conditional: Route to HIL or continue"""
    # v10.3: Read from dict-ified Pydantic model
    report = state.get("hil", {}).get("ambiguity_report", {})
    if report.get("ambiguity_detected", False):
        return "pause_for_human"
    return "continue_workflow"

def check_bullets_passed(state: dict) -> str:
    """Node 5 conditional: Check bullet quality and retries"""
    critiques = state.get('bullets', {}).get('critiqued_bullets', [])
    if not critiques:
        return "global_replanner"
        
    avg_score = sum(b.get('critique', {}).get('score', 0) for b in critiques) / len(critiques)
    
    if avg_score >= 7.0:
        return "bullets_passed"
    
    # v10.4: Use module-level context
    retries = state.get('metadata', {}).get('retries', {}).get('bullet_retries', 0)
    if retries < context.config.agent_stacks.max_local_retries:
        # NOTE: This state mutation is problematic in tests.
        if 'metadata' not in state: state['metadata'] = {}
        if 'retries' not in state['metadata']: state['metadata']['retries'] = {}
        state['metadata']['retries']['bullet_retries'] = retries + 1
        return "retry_bullets"
    
    return "global_replanner"
    
def check_qa_passed(state: dict) -> str:
    """Node 7 conditional: Check QA and retries"""
    # v10.4: Use module-level context
    if state.get('qa', {}).get('qa_passed', False):
        # v10.4: Check enable_hil from context
        return "pause_for_human" if HIL_AVAILABLE and context.config.agent_stacks.enable_hil_stack else "qa_passed"
    
    retries = state.get('metadata', {}).get('retries', {}).get('qa_retries', 0)
    if retries < 1: # Max 1 QA retry
        if 'metadata' not in state: state['metadata'] = {}
        if 'retries' not in state['metadata']: state['metadata']['retries'] = {}
        state['metadata']['retries']['qa_retries'] = retries + 1
        return "retry_drafting"
        
    return "global_replanner"

def route_feedback(state: dict) -> str:
    """Node 10 conditional: Route based on human feedback"""
    next_step = state.get("hil", {}).get("next_step", "DRAFTING")
    if next_step == "STRATEGY": return "to_strategy"
    if next_step == "BULLET_GENERATION": return "to_bullets"
    return "to_drafting"

# ============================================================================
# LANGGRAPH WORKFLOW BUILDER (Design-Aligned v10.4)
# ============================================================================

def get_graph_app(checkpointer: RedisSaver, workflow_context: WorkflowContext, enable_hil: bool = True):
    """Build complete LangGraph workflow with v10.4 resilience."""
    
    # v10.4: Set the module-level context
    global context
    context = workflow_context
    
    # v10.4: Override HIL enable based on both graph and global config
    global HIL_AVAILABLE
    HIL_AVAILABLE = HIL_AVAILABLE and enable_hil and context.config.agent_stacks.enable_hil_stack
    
    workflow = StateGraph(dict)
    
    # --- ADD NODES (v10.4: Reference module-level functions) ---
    
    workflow.add_node("run_sanitize_pii", run_sanitize_pii) # 0
    workflow.add_node("run_tot_strategy", run_tot_strategy) # 1
    workflow.add_node("run_detect_ambiguity", run_detect_ambiguity) # 2
    workflow.add_node("run_prompt_engineering", run_prompt_engineering) # 2.5
    workflow.add_node("run_rag_stack", run_rag_stack) # 3
    workflow.add_node("run_generate_bullets", run_generate_bullets) # 4
    workflow.add_node("run_critique_bullets", run_critique_bullets) # 5
    workflow.add_node("run_drafting", run_drafting) # 6
    workflow.add_node("run_qa_validation", run_qa_validation) # 7
    workflow.add_node("HIL_PAUSE", human_in_the_loop_node) # 9
    workflow.add_node("run_feedback_router", run_feedback_router) # 10
    workflow.add_node("GLOBAL_REPLANNER", END) # 🚨

    # --- CONNECT NODES ---
    
    workflow.set_entry_point("run_sanitize_pii")
    workflow.add_edge("run_sanitize_pii", "run_tot_strategy") # 0 -> 1
    workflow.add_edge("run_tot_strategy", "run_detect_ambiguity") # 1 -> 2
    
    workflow.add_conditional_edges(
        "run_detect_ambiguity", check_ambiguity,
        {"pause_for_human": "HIL_PAUSE", "continue_workflow": "run_prompt_engineering"}
    )
    
    workflow.add_edge("run_prompt_engineering", "run_rag_stack") # 2.5 -> 3
    workflow.add_edge("run_rag_stack", "run_generate_bullets") # 3 -> 4
    workflow.add_edge("run_generate_bullets", "run_critique_bullets") # 4 -> 5
    
    workflow.add_conditional_edges(
        "run_critique_bullets", check_bullets_passed,
        {"bullets_passed": "run_drafting", "retry_bullets": "run_generate_bullets", "global_replanner": "GLOBAL_REPLANNER"}
    )
    
    workflow.add_edge("run_drafting", "run_qa_validation") # 6 -> 7
    
    workflow.add_conditional_edges(
        "run_qa_validation", check_qa_passed,
        {"pause_for_human": "HIL_PAUSE", "qa_passed": END, "retry_drafting": "run_drafting", "global_replanner": "GLOBAL_REPLANNER"}
    )
    
    workflow.add_edge("HIL_PAUSE", "run_feedback_router") # 9 -> 10
    workflow.add_conditional_edges(
        "run_feedback_router", route_feedback,
        {"to_strategy": "run_tot_strategy", "to_bullets": "run_generate_bullets", "to_drafting": "run_drafting"}
    )
    
    return workflow.compile(checkpointer=checkpointer)

# ============================================================================
# END OF agent_orchestration_v10_4.py
# ============================================================================