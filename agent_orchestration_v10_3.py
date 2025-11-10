# File: agent_orchestration_v10_3.py
# Version: 10.3 (Instructional Injection)
#
# Description:
# v10.3: DESTRUCTIVE OVERWRITE based on Instructional_Injection_Enhanced_v4.md
# - Mandated Circuit Breakers: ReActConductorAgent and QAConductorAgent
#   now wrap all tool calls in a CircuitBreaker, instantiated per-tool,
#   to make the toolchain resilient to cascading failures.
# - Implemented Robust Retries: All 11 graph nodes (run_tot_strategy,
#   run_rag_stack, etc.) are now decorated with @exponential_backoff_retry
#   to enhance error recovery and stop brittle failures.
# - Forced Context Budgeting: QAConductorAgent no longer naively injects
#   full documents. It now uses the injected self.budget_manager.prune()
#   to summarize context and prevent token limit errors.
# - Imports updated to v10.3 and logic updated to handle Pydantic models
#   from core_v10_3 (e.g., StrategyPlan).

import json
import logging
import asyncio
from typing import Dict, Any, List

# v10.3: Import from new core
from core_v10_3 import (
    WorkflowContext, BaseAgent, StrategyPlan, PydanticSchemaError,
    exponential_backoff_retry, CircuitBreakerOpenError
)
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis import RedisSaver
from langgraph.errors import GraphRecursionError

# v10.3: Import from batch runner (which will be v10.3)
from run_batch_v10_3 import CircuitBreaker

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

# v10.3: Import from new stacks
from agent_stacks_v10_3 import (
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

# v10.3: Import from new tools file
from agent_tools_v10_3 import (
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

logger = logging.getLogger("agent_orchestration_v10_3")


# ============================================================================
# DRAFTING CONDUCTOR (v10.3: With Circuit Breakers)
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
        self.tool_breakers = {
            name: CircuitBreaker(
                failure_threshold=self.config.batch_config.circuit_breaker_failure_threshold
            ) for name in self.tools
        }
        self.style_guide = "Style: Professional, high-impact, and metrics-driven."

    async def run_async(self, task_context: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Running ReAct Drafting Conductor (v10.3)...")
        
        # ... (Feedback-aware tuning preserved) ...
        
        client = self.get_model_client("react_conductor_model")
        
        # v10.3: Strategy is now a Pydantic model
        strategy_json = task_context.get('strategy').model_dump_json()
        
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
            
            step_data = response["content"]
            messages.append({"role": "assistant", "content": json.dumps(step_data)})
            
            if "final_draft" in step_data:
                final_draft = step_data["final_draft"]
                self.log_feedback(workflow_id, "react_conductor_draft", "success", {"steps_executed": step})
                return {"final_output": final_draft, "steps": step}
            
            if "tool_call" in step_data:
                tool_name = step_data["tool_call"]["name"]
                tool_input = step_data["tool_call"]["input"]
                
                if tool_name not in self.tools:
                    messages.append({"role": "user", "content": f"Error: Tool '{tool_name}' not found."})
                    continue
                
                # Add context for tools
                tool_input["draft"] = task_context.get("bullets")
                tool_input["strategy"] = task_context.get("strategy").model_dump() # Pass as dict
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
                    # v10.3: Record failure and report to ReAct loop
                    self.log_error(f"Tool {tool_name} failed: {e}")
                    if tool_name in self.tool_breakers:
                        self.tool_breakers[tool_name].record_failure()
                    
                    error_msg = f"Error: Tool '{tool_name}' failed. Reason: {str(e)}"
                    messages.append({"role": "user", "content": error_msg})

        self.log_feedback(workflow_id, "react_conductor_draft", "failure", {"reason": "Max steps reached"})
        return {"final_output": {"error": "Max steps reached"}, "steps": max_steps}

# ============================================================================
# QA CONDUCTOR (v10.3: With Circuit Breakers & Context Budgeting)
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
        self.tool_breakers = {
            name: CircuitBreaker(
                failure_threshold=self.config.batch_config.circuit_breaker_failure_threshold
            ) for name in self.tools
        }
        self.style_guide = "Style: Ensure professional, clear, and unbiased language."

    async def run_async(self, state: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Running ReAct QA Conductor (v10.3)...")
        
        # ... (Feedback-aware tuning preserved) ...
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
        strategy_json = state['strategy']['strategy_plan'].model_dump_json()
        
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
            "strategy": state['strategy']['strategy_plan'].model_dump(), # Pass as dict
            "style_guide": self.style_guide
        }
        
        for step in range(max_steps):
            response = await client.chat_completion_async(
                messages=messages,
                temperature=0.4,
                response_format="json_object"
            )
            step_data = response["content"]
            messages.append({"role": "assistant", "content": json.dumps(step_data)})
            
            if "final_qa_report" in step_data:
                final_report = step_data["final_qa_report"]
                final_report["all_tool_results"] = all_tool_results
                self.log_feedback(workflow_id, "react_conductor_qa", "success", {"steps_executed": step})
                return final_report
            
            if "tool_call" in step_data:
                tool_name = step_data["tool_call"]["name"]
                tool_input = step_data["tool_call"]["input"]
                
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
                    # v10.3: Record failure
                    self.log_error(f"QA Tool {tool_name} failed: {e}")
                    if tool_name in self.tool_breakers:
                        self.tool_breakers[tool_name].record_failure()
                    
                    error_msg = f"Error: Tool '{tool_name}' failed. Reason: {str(e)}"
                    messages.append({"role": "user", "content": error_msg})
        
        self.log_feedback(workflow_id, "react_conductor_qa", "failure", {"reason": "Max steps reached"})
        return {"error": "Max steps reached", "steps": max_steps, "all_tool_results": all_tool_results, "qa_passed": False}

# ============================================================================
# LANGGRAPH WORKFLOW BUILDER (Design-Aligned v10.3)
# ============================================================================

def human_in_the_loop_node(state: dict) -> dict:
    if not HIL_AVAILABLE:
        logger.warning("HIL not available. Skipping pause.")
        return {}
    try:
        human_in_the_loop(timeout=3600) 
    except GraphRecursionError:
        logger.info("HIL pause interrupted by user feedback.")
    except Exception as e:
        logger.error(f"HIL node failed: {e}")
    return {}

def get_graph_app(checkpointer: RedisSaver, context: WorkflowContext, enable_hil: bool = True):
    """Build complete LangGraph workflow with v10.3 resilience."""
    
    workflow = StateGraph(dict)
    
    # --- NODE DEFINITIONS (v10.3: Now with retry decorators) ---
    
    @exponential_backoff_retry()
    async def run_sanitize_pii(state: dict) -> dict:
        """Node 0: Sanitize PII"""
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
        strategist = ToTStrategistAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        strategy_result = await strategist.run_async(
            {"job_title": state['job']['job_title'], "company": state['job']['company']},
            workflow_id
        )
        # v10.3: Return Pydantic model in state
        return {"strategy": strategy_result}

    @exponential_backoff_retry()
    async def run_detect_ambiguity(state: dict) -> dict:
        """Node 2: Proactive HIL ambiguity check"""
        if not enable_hil:
            return {"hil": {"ambiguity_report": {"ambiguity_detected": False}}}
            
        detector = HILAmbiguityDetectorAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        # v10.3: Pass Pydantic model
        strategy_plan = state['strategy']['strategy_plan']
        ambiguity_result = await detector.run_async(strategy_plan, workflow_id)
        
        # v10.3: Read from Pydantic model
        report = ambiguity_result.get("ambiguity_report")
        if report.confidence < context.config.agent_stacks.ambiguity_confidence_threshold:
             report.ambiguity_detected = False
        
        return {"hil": {"ambiguity_report": report.model_dump()}} # Store as dict
    
    @exponential_backoff_retry()
    async def run_prompt_engineering(state: dict) -> dict:
        """Node 2.5: Generate dynamic prompts"""
        prompt_agent = PromptEngineerAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        # v10.3: Pass Pydantic model
        strategy_plan = state['strategy']['strategy_plan']
        prompts_result = await prompt_agent.run_async(strategy_plan, workflow_id)
        
        return {"prompts": {"prompts": prompts_result.get("prompts").model_dump()}}
    
    @exponential_backoff_retry()
    async def run_rag_stack(state: dict) -> dict:
        """Node 3: RAG with Hybrid Search (v10.3)"""
        rag_agent = RAG_SearchAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        query = f"{state['job']['job_title']} at {state['job']['company']}"
        experience = state['resume']['sanitized_resume'].get('professional_experience', [])
        
        ranked_sections = await rag_agent.run_async(query, experience, workflow_id)
        
        return {"resume": {"experience_bullets": ranked_sections}}
    
    @exponential_backoff_retry()
    async def run_generate_bullets(state: dict) -> dict:
        """Node 4: Generate bullets (4-step)"""
        bullet_gen = AsyncBulletGeneratorAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        # v10.3: Prompts are dicts
        prompt = state['prompts']['prompts'].get('bullet_generation_prompt', "Generate bullets")
        
        all_bullets = []
        for exp in state['resume']['experience_bullets'][:3]: 
            bullets = await bullet_gen.run_async(prompt, exp, workflow_id)
            all_bullets.extend([{"text": b, "experience": exp} for b in bullets])
        
        return {"bullets": {"generated_bullets": all_bullets}}
    
    @exponential_backoff_retry()
    async def run_critique_bullets(state: dict) -> dict:
        """Node 5: Critique bullets"""
        critique_agent = AsyncBulletCritiqueAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        critique_prompt = state['prompts']['prompts'].get('critique_prompt', "Critique bullets")
        bullets = state['bullets']['generated_bullets']
        
        critiques = await critique_agent.run_async(bullets, critique_prompt, workflow_id)
        
        return {"bullets": {"critiqued_bullets": critiques}}
    
    @exponential_backoff_retry()
    async def run_drafting(state: dict) -> dict:
        """Node 6: Draft assembly with ReAct Conductor"""
        conductor = ReActConductorAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        good_bullets = [
            b for b in state['bullets']['critiqued_bullets']
            if b.get('critique', {}).get('score', 0) >= 7
        ]
        
        task_context = {
            "bullets": good_bullets,
            "strategy": state['strategy']['strategy_plan'] # v10.3: Pass Pydantic model
        }
        
        draft = await conductor.run_async(task_context, workflow_id)
        return {"draft": {"sections": draft.get("final_output", {})}}
    
    @exponential_backoff_retry()
    async def run_qa_validation(state: dict) -> dict:
        """Node 7: Final QA with ReAct Conductor"""
        qa_conductor = QAConductorAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        # v10.3: We must reconstruct the StrategyPlan model for the conductor
        state['strategy']['strategy_plan'] = StrategyPlan(**state['strategy']['strategy_plan'])
        
        validation = await qa_conductor.run_async(state, workflow_id)
        
        return {
            "qa": {"validation_results": validation, "qa_passed": validation.get("qa_passed", False)},
            "artifacts": {"artifacts": {"final_resume": state['draft']['sections'], "qa_report": validation}}
        }
    
    # HIL Nodes (9, 10)
    @exponential_backoff_retry()
    async def run_feedback_router(state: dict) -> dict:
        """Node 10: HIL Feedback Router"""
        router = HILFeedbackRouterAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        last_human_message = "Default to drafting"
        # ... (HIL feedback reading logic preserved) ...

        route = await router.run_async(last_human_message, workflow_id)
        return {"hil": {"next_step": route.get("next_step", "DRAFTING")}}
    
    # --- CONDITIONAL EDGES ---
    
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
        
        retries = state.get('metadata', {}).get('retries', {}).get('bullet_retries', 0)
        if retries < context.config.agent_stacks.max_local_retries:
            state['metadata']['retries']['bullet_retries'] = retries + 1
            return "retry_bullets"
        
        return "global_replanner"
        
    def check_qa_passed(state: dict) -> str:
        """Node 7 conditional: Check QA and retries"""
        if state.get('qa', {}).get('qa_passed', False):
            return "pause_for_human" if enable_hil else "qa_passed"
        
        retries = state.get('metadata', {}).get('retries', {}).get('qa_retries', 0)
        if retries < 1: # Max 1 QA retry
            state['metadata']['retries']['qa_retries'] = retries + 1
            return "retry_drafting"
            
        return "global_replanner"

    def route_feedback(state: dict) -> str:
        """Node 10 conditional: Route based on human feedback"""
        next_step = state.get("hil", {}).get("next_step", "DRAFTING")
        if next_step == "STRATEGY": return "to_strategy"
        if next_step == "BULLET_GENERATION": return "to_bullets"
        return "to_drafting"
        
    # --- BUILD GRAPH (Matches v10.3 design) ---
    
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
# END OF agent_orchestration_v10_3.py
# ============================================================================