# File: agent_orchestration_v10_1.py
# Version: 10.1 (Design-Aligned Implementation)
#
# Description:
# Contains the "brain" of the operation: the ReAct Conductors
# and the final LangGraph builder (get_graph_app).
# Imports stacks from agent_stacks_v10_1.py and
# tools from agent_tools_v10_1.py.

import json
import logging
import asyncio
from typing import Dict, Any, List

# GAP 4 FIX: Removed global CONFIG import
from core_v10_1 import (
    WorkflowContext, BaseAgent
)
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis import RedisSaver
from langgraph.errors import GraphRecursionError

# Make HIL import conditional for environment compatibility
try:
    from langgraph.prebuilt import human_in_the_loop
    HIL_AVAILABLE = True
except ImportError:
    HIL_AVAILABLE = False
    human_in_the_loop = None # type: ignore
    import logging
    logging.getLogger(__name__).warning(
        "human_in_the_loop not available - HIL features will be disabled"
    )

# Import all agent stacks (nodes)
from agent_stacks_v10_1 import (
    PIISanitizerAgent,
    BiasDetectorAgent,
    ToTStrategistAgent,
    PromptEngineerAgent, # META-PROMPT GAP FIX: Import PromptEngineer
    RAG_SearchAgent,
    AsyncBulletGeneratorAgent,
    AsyncBulletCritiqueAgent,
    HILAmbiguityDetectorAgent,
    HILFeedbackRouterAgent
)

# Import all expert tools
from agent_tools_v10_1 import (
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

logger = logging.getLogger("agent_orchestration_v10_1")


# ============================================================================
# DRAFTING CONDUCTOR
# ============================================================================

class ReActConductorAgent(BaseAgent):
    """ROW 7: ReAct conductor with feedback-aware tuning and REAL tools"""
    
    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        super().__init__(context, debug_mode)
        # Design-Aligned: Instantiate REAL tools
        self.tools = {
            "review_draft_strategy": DraftingStrategistTool(context, debug_mode),
            "red_team_critique": DraftingRedTeamTool(context, debug_mode),
            "refine_section": DraftingRefinerTool(context, debug_mode),
            "add_metrics": DraftingMetricsTool(context, debug_mode)
        }
        self.tool_schemas = [t.get_schema() for t in self.tools.values()]

    async def run_async(self, task_context: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Running ReAct Drafting Conductor...")
        
        feedback_reader = self.context.feedback_reader
        react_failures = [f for f in feedback_reader.read_recent_feedback(max_entries=15) if f.agent_name == "ReActConductorAgent" and f.feedback_type == "failure"]
        
        # GAP 4 FIX: Use self.config
        max_steps = self.config.agent_stacks.conductor_max_steps
        temperature = self.config.agent_stacks.conductor_temperature
        
        if len(react_failures) > 3:
            max_steps = min(max_steps + 2, 15)
            temperature = max(0.3, temperature - 0.1)
            self.log_info(f"Adjusted ReAct: max_steps={max_steps}, temp={temperature}")
        
        # Design-Aligned: Use react_conductor_model (Gemini 2.5 Pro)
        client = self.get_model_client("react_conductor_model")
        
        messages = [{
            "role": "user",
            "content": f"""You are a ReAct drafting conductor. Your goal is to create a final resume draft.
Task Context: {json.dumps(task_context)}
Tools: {json.dumps(self.tool_schemas)}

Plan:
1.  Think about the task.
2.  Call `review_draft_strategy` to align.
3.  Call `add_metrics` to improve bullets.
4.  Call `red_team_critique` to find weaknesses.
5.  If weaknesses are found, call `refine_section` for them.
6.  Assemble the final draft.

Output thoughts and tool calls in JSON:
{{"thought": "Your reasoning", "tool_call": {{"name": "tool_name", "input": {{"arg": "value"}}}}}}
When finished, output:
{{"thought": "Draft complete", "final_draft": {{...}}}}
"""
        }]
        
        final_draft = {}
        
        for step in range(max_steps):
            response = await client.chat_completion_async(
                messages=messages,
                temperature=temperature,
                response_format="json_object"
            )
            
            step_data = response["content"]
            messages.append({"role": "assistant", "content": json.dumps(step_data)})
            
            if "final_draft" in step_data:
                final_draft = step_data["final_draft"]
                self.log_feedback(workflow_id, "react_conductor_draft", "success", {"steps_executed": step, "max_steps": max_steps})
                return {"final_output": final_draft, "steps": step}
            
            if "tool_call" in step_data:
                tool_name = step_data["tool_call"]["name"]
                tool_input = step_data["tool_call"]["input"]
                
                # Add context for tools
                tool_input["draft"] = task_context.get("bullets")
                tool_input["strategy"] = task_context.get("strategy")
                
                if tool_name in self.tools:
                    tool = self.tools[tool_name]
                    tool_result = await tool.run_async(tool_input, workflow_id)
                    messages.append({"role": "user", "content": f"Tool Result: {json.dumps(tool_result)}"})
                else:
                    messages.append({"role": "user", "content": f"Error: Tool '{tool_name}' not found."})

        self.log_feedback(workflow_id, "react_conductor_draft", "failure", {"reason": "Max steps reached", "steps_executed": max_steps})
        return {"final_output": {"error": "Max steps reached"}, "steps": max_steps}

# ============================================================================
# QA CONDUCTOR
# ============================================================================

class QAConductorAgent(BaseAgent):
    """ROW 7: ReAct Conductor for QA, using all 11 REAL expert tools"""
    
    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        super().__init__(context, debug_mode)
        # Design-Aligned: Instantiate REAL tools
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

    async def run_async(self, state: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Running ReAct QA Conductor with 11 tools...")
        
        feedback_reader = self.context.feedback_reader
        qa_failures = [f for f in feedback_reader.read_recent_feedback(max_entries=15) if f.agent_name == "QAConductorAgent" and f.feedback_type == "failure"]
        
        max_steps = 15 # QA needs more steps
        temperature = 0.4
        
        if len(qa_failures) > 3:
            temperature = max(0.2, temperature - 0.1)
            self.log_info(f"Adjusted QA ReAct: temp={temperature}")

        # Design-Aligned: Use react_conductor_model (Gemini 2.5 Pro)
        client = self.get_model_client("react_conductor_model")
        
        draft_text = json.dumps(state['draft']['sections'])
        
        messages = [{
            "role": "user",
            "content": f"""You are a ReAct QA conductor. Your goal is to validate the final resume draft.
Draft: {draft_text}
Tools: {json.dumps(self.tool_schemas)}

Plan:
1.  Run `validate_claims` and `validate_tenure` for factual accuracy.
2.  Run `validate_jd_skills` and `validate_thematic_alignment` for relevance.
3.  Run `validate_tone`, `validate_narrative_thread`, and `validate_signal_score` for quality.
4.  Run `validate_bias` for safety.
5.  Run `find_missed_opportunities` for gaps.
6.  Run `adversarial_review` as a final check.
7.  Compile all feedback into a final QA report.

Output thoughts and tool calls in JSON:
{{"thought": "Your reasoning", "tool_call": {{"name": "tool_name", "input": {{"arg": "value"}}}}}}
When finished, output:
{{"thought": "QA complete", "final_qa_report": {{"qa_passed": true/false, "issues": [...]}}}}
"""
        }]
        
        final_report = {}
        all_tool_results = []
        
        # Prepare context for tools
        tool_context = {
            "draft_text": draft_text,
            "master_resume": state['resume']['master_resume'],
            "job_description": state['job']['raw_jd'],
            "strategy": state['strategy']['strategy_plan']
        }
        
        for step in range(max_steps):
            response = await client.chat_completion_async(
                messages=messages,
                temperature=temperature,
                response_format="json_object"
            )
            
            step_data = response["content"]
            messages.append({"role": "assistant", "content": json.dumps(step_data)})
            
            if "final_qa_report" in step_data:
                final_report = step_data["final_qa_report"]
                final_report["all_tool_results"] = all_tool_results
                self.log_feedback(workflow_id, "react_conductor_qa", "success", {"steps_executed": step, "issues_found": len(final_report.get("issues", []))})
                return final_report
            
            if "tool_call" in step_data:
                tool_name = step_data["tool_call"]["name"]
                tool_input = step_data["tool_call"]["input"]
                
                # Inject the full context into the tool input
                tool_input.update(tool_context)
                
                if tool_name in self.tools:
                    tool = self.tools[tool_name]
                    tool_result = await tool.run_async(tool_input, workflow_id)
                    all_tool_results.append({tool_name: tool_result})
                    messages.append({"role": "user", "content": f"Tool Result: {json.dumps(tool_result)}"})
                else:
                    messages.append({"role": "user", "content": f"Error: Tool '{tool_name}' not found."})
        
        self.log_feedback(workflow_id, "react_conductor_qa", "failure", {"reason": "Max steps reached", "steps_executed": max_steps})
        return {"error": "Max steps reached", "steps": max_steps, "all_tool_results": all_tool_results, "qa_passed": False}

# ============================================================================
# LANGGRAPH WORKFLOW BUILDER (Design-Aligned v10.1)
# ============================================================================

def human_in_the_loop_node(state: dict) -> dict:
    """Wrapper for LangGraph's HIL"""
    if not HIL_AVAILABLE:
        logger.warning("HIL not available. Skipping pause.")
        return {}
    try:
        # Pause for 1 hour
        human_in_the_loop(timeout=3600) 
    except GraphRecursionError:
        # This will be raised if HIL is interrupted to resume
        logger.info("HIL pause interrupted by user feedback.")
    except Exception as e:
        logger.error(f"HIL node failed: {e}")
    return {}

def get_graph_app(checkpointer: RedisSaver, context: WorkflowContext, enable_hil: bool = True):
    """Build complete LangGraph workflow with all advanced agents"""
    
    workflow = StateGraph(dict)
    
    # --- NODE DEFINITIONS ---
    
    async def run_sanitize_pii(state: dict) -> dict:
        """Node 0: Sanitize PII"""
        pii_agent = PIISanitizerAgent(context)
        sanitized = pii_agent.run(state['resume']['master_resume'])
        
        # Also run initial bias check on JD
        bias_agent = BiasDetectorAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        bias_result = bias_agent.run(state['job']['raw_jd'], workflow_id)
        
        return {
            "resume": {"sanitized_resume": sanitized},
            "safety": {
                "pii_detected": False,
                "bias_detected": bias_result['bias_detected'],
                "safety_notes": [f"Initial JD bias check: {bias_result}"]
            }
        }
    
    async def run_tot_strategy(state: dict) -> dict:
        """Node 1: ToT strategy"""
        strategist = ToTStrategistAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        strategy_result = await strategist.run_async(
            {
                "job_title": state['job']['job_title'],
                "company": state['job']['company'],
                "raw_jd": state['job']['raw_jd']
            },
            workflow_id
        )
        return {"strategy": strategy_result}

    async def run_detect_ambiguity(state: dict) -> dict:
        """Node 2: Proactive HIL ambiguity check"""
        if not enable_hil:
            return {"hil": {"ambiguity_detected": False}}
            
        detector = HILAmbiguityDetectorAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        ambiguity_result = await detector.run_async(
            state['strategy']['strategy_plan'],
            workflow_id
        )
        
        # Only trigger HIL if ambiguity is high
        if ambiguity_result.get('confidence', 0) < context.config.agent_stacks.ambiguity_confidence_threshold:
             ambiguity_result["ambiguity_detected"] = False
        
        return {"hil": ambiguity_result}
    
    # META-PROMPT GAP FIX: Add new node for PromptEngineerAgent
    async def run_prompt_engineering(state: dict) -> dict:
        """Node 2.5: Generate dynamic prompts"""
        prompt_agent = PromptEngineerAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        prompts = await prompt_agent.run_async(
            state['strategy']['strategy_plan'],
            workflow_id
        )
        return {"prompts": {"prompts": prompts}}

    async def run_rag_stack(state: dict) -> dict:
        """Node 3: RAG with ReAct Search"""
        rag_agent = RAG_SearchAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        query = f"{state['job']['job_title']} at {state['job']['company']}"
        experience = state['resume']['sanitized_resume'].get('professional_experience', [])
        
        ranked_experience_sections = await rag_agent.run_async(query, experience, workflow_id)
        
        return {"resume": {"experience_bullets": ranked_experience_sections}}
    
    async def run_generate_bullets(state: dict) -> dict:
        """Node 4: Generate bullets (4-step)"""
        bullet_gen = AsyncBulletGeneratorAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        # META-PROMPT GAP FIX: Use generated prompt
        prompt = state['prompts']['prompts'].get('bullet_generation_prompt', 
             f"Generate achievement bullets for {state['job']['job_title']}")
        
        all_bullets = []
        # Process top N ranked experience sections
        for exp in state['resume']['experience_bullets'][:3]: 
            bullets = await bullet_gen.run_async(prompt, exp, workflow_id)
            all_bullets.extend([{"text": b, "experience": exp} for b in bullets])
        
        return {"bullets": {"generated_bullets": all_bullets}}
    
    async def run_critique_bullets(state: dict) -> dict:
        """Node 5: Critique bullets"""
        critique_agent = AsyncBulletCritiqueAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        # META-PROMPT GAP FIX: Use generated prompt
        critique_prompt = state['prompts']['prompts'].get('critique_prompt', 
             f"Critique these bullets against the strategy: {json.dumps(state['strategy']['strategy_plan'])}")
        
        bullets = state['bullets']['generated_bullets']
        
        critiques = await critique_agent.run_async(bullets, critique_prompt, workflow_id)
        
        return {"bullets": {"critiqued_bullets": critiques}}
    
    async def run_drafting(state: dict) -> dict:
        """Node 6: Draft assembly with ReAct Conductor"""
        conductor = ReActConductorAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        # Filter for high-scoring bullets
        good_bullets = [
            b for b in state['bullets']['critiqued_bullets']
            if b.get('critique', {}).get('score', 0) >= 7
        ]
        
        task_context = {
            "bullets": good_bullets,
            "strategy": state['strategy']['strategy_plan']
        }
        
        draft = await conductor.run_async(task_context, workflow_id)
        
        return {"draft": {"sections": draft.get("final_output", {})}}
    
    async def run_qa_validation(state: dict) -> dict:
        """Node 7: Final QA with ReAct Conductor"""
        qa_conductor = QAConductorAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        validation = await qa_conductor.run_async(state, workflow_id)
        
        return {
            "qa": {"validation_results": validation, "qa_passed": validation.get("qa_passed", False)},
            "artifacts": {
                "artifacts": {
                    "final_resume": state['draft']['sections'],
                    "qa_report": validation
                }
            }
        }
    
    # HIL Nodes (9, 10)
    async def run_feedback_router(state: dict) -> dict:
        """Node 10: HIL Feedback Router"""
        router = HILFeedbackRouterAgent(context)
        workflow_id = state.get('metadata', {}).get('workflow_id', '')
        
        last_human_message = ""
        try:
            # This logic reads feedback from LangGraph's checkpointing
            checkpoint = state.get("__checkpoint__")
            if checkpoint and checkpoint.get("channel_values"):
                human_messages = checkpoint["channel_values"].get("human", [])
                if human_messages:
                    last_human_message = human_messages[-1].content
        except Exception as e:
            logger.error(f"Error getting HIL feedback: {e}")
            last_human_message = "Default to drafting" # Fallback

        route = await router.run_async(last_human_message, workflow_id)
        return {"hil": {"next_step": route.get("next_step", "DRAFTING")}}
    
    # --- CONDITIONAL EDGES ---
    
    def check_ambiguity(state: dict) -> str:
        """Node 2 conditional: Route to HIL or continue"""
        if state.get("hil", {}).get("ambiguity_detected", False):
            return "pause_for_human"
        return "continue_workflow"

    def check_bullets_passed(state: dict) -> str:
        """Node 5 conditional: Check bullet quality and retries"""
        critiques = state.get('bullets', {}).get('critiqued_bullets', [])
        if not critiques:
            return "global_replanner" # Failed catastrophically
            
        avg_score = sum(b.get('critique', {}).get('score', 0) for b in critiques) / len(critiques)
        
        if avg_score >= 7.0:
            return "bullets_passed"
        
        # Bullets failed, check retries
        retries = state.get('metadata', {}).get('retries', {}).get('bullet_retries', 0)
        # GAP 4 FIX: Use context.config
        if retries < context.config.agent_stacks.max_local_retries:
            state['metadata']['retries']['bullet_retries'] = retries + 1
            logger.info(f"Bullets failed (score: {avg_score:.1f}). Retrying... ({retries+1}/{context.config.agent_stacks.max_local_retries})")
            return "retry_bullets"
        
        logger.error(f"Bullets failed after {retries} retries. Calling global replanner.")
        return "global_replanner"
        
    def check_qa_passed(state: dict) -> str:
        """Node 7 conditional: Check QA and retries"""
        if state.get('qa', {}).get('qa_passed', False):
            # GAP 5 HIL FIX: Route to HIL or END
            if enable_hil:
                return "pause_for_human" # Go to final review
            else:
                return "qa_passed" # End workflow
        
        retries = state.get('metadata', {}).get('retries', {}).get('qa_retries', 0)
        max_qa_retries = 1 # From design
        
        if retries < max_qa_retries:
            state['metadata']['retries']['qa_retries'] = retries + 1
            logger.info(f"QA failed. Retrying... ({retries+1}/{max_qa_retries})")
            return "retry_drafting"
            
        logger.error(f"QA failed after {retries} retries. Calling global replanner.")
        return "global_replanner"

    def route_feedback(state: dict) -> str:
        """Node 10 conditional: Route based on human feedback"""
        next_step = state.get("hil", {}).get("next_step", "DRAFTING")
        if next_step == "STRATEGY":
            return "to_strategy"
        if next_step == "BULLET_GENERATION":
            return "to_bullets"
        # Default or "DRAFTING"
        return "to_drafting"
        
    # --- BUILD GRAPH (Matches agentic_design_v10_1.md) ---
    
    workflow.add_node("run_sanitize_pii", run_sanitize_pii) # Node 0
    workflow.add_node("run_tot_strategy", run_tot_strategy) # Node 1
    workflow.add_node("run_detect_ambiguity", run_detect_ambiguity) # Node 2
    # META-PROMPT GAP FIX: Add Node 2.5
    workflow.add_node("run_prompt_engineering", run_prompt_engineering) 
    workflow.add_node("run_rag_stack", run_rag_stack) # Node 3
    workflow.add_node("run_generate_bullets", run_generate_bullets) # Node 4
    workflow.add_node("run_critique_bullets", run_critique_bullets) # Node 5
    workflow.add_node("run_drafting", run_drafting) # Node 6
    workflow.add_node("run_qa_validation", run_qa_validation) # Node 7
    # GAP 5 HIL FIX: Remove Node 8
    workflow.add_node("HIL_PAUSE", human_in_the_loop_node) # Node 9
    workflow.add_node("run_feedback_router", run_feedback_router) # Node 10
    
    # Global Replanner (simplified as an endpoint)
    workflow.add_node("GLOBAL_REPLANNER", END) # Node 🚨

    # --- CONNECT NODES ---
    
    workflow.set_entry_point("run_sanitize_pii")
    workflow.add_edge("run_sanitize_pii", "run_tot_strategy") # 0 -> 1
    workflow.add_edge("run_tot_strategy", "run_detect_ambiguity") # 1 -> 2
    
    # HIL Conditional Edge (Node 2)
    workflow.add_conditional_edges(
        "run_detect_ambiguity",
        check_ambiguity,
        {
            # GAP 5 HIL FIX: Proactive HIL routes to router
            "pause_for_human": "HIL_PAUSE", 
            # META-PROMPT GAP FIX: Continue to prompt engineering
            "continue_workflow": "run_prompt_engineering"
        }
    )
    
    # META-PROMPT GAP FIX: Add new edge
    workflow.add_edge("run_prompt_engineering", "run_rag_stack") # 2.5 -> 3
    
    # Main Workflow Path
    workflow.add_edge("run_rag_stack", "run_generate_bullets") # 3 -> 4
    workflow.add_edge("run_generate_bullets", "run_critique_bullets") # 4 -> 5
    
    # Bullet Critique Retry Loop (Node 5)
    workflow.add_conditional_edges(
        "run_critique_bullets",
        check_bullets_passed,
        {
            "bullets_passed": "run_drafting",
            "retry_bullets": "run_generate_bullets",
            "global_replanner": "GLOBAL_REPLANNER"
        }
    )
    
    workflow.add_edge("run_drafting", "run_qa_validation") # 6 -> 7
    
    # QA Validation -> HIL/End Loop (Node 7)
    workflow.add_conditional_edges(
        "run_qa_validation",
        check_qa_passed,
        {
            # GAP 5 HIL FIX: Route to final HIL pause or end
            "pause_for_human": "HIL_PAUSE",
            "qa_passed": END,
            "retry_drafting": "run_drafting",
            "global_replanner": "GLOBAL_REPLANNER"
        }
    )
    
    # HIL Feedback Loop (Node 9 -> 10)
    workflow.add_edge("HIL_PAUSE", "run_feedback_router") # 9 -> 10
    workflow.add_conditional_edges(
        "run_feedback_router",
        route_feedback,
        {
            "to_strategy": "run_tot_strategy",
            "to_bullets": "run_generate_bullets",
            "to_drafting": "run_drafting"
        }
    )
    
    return workflow.compile(checkpointer=checkpointer)

# ============================================================================
# END OF agent_orchestration_v10_1.py
# ============================================================================