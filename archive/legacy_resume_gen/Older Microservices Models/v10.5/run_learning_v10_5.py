# File: run_learning_v10_5.py
# Version: 10.5 (Refactored)
#
# v10.5 REFACTOR CHANGES:
# - REMOVED: All duplicated Composition Root logic (61 lines).
# - ADDED: Call to core_v10_5.create_workflow_context() helper.
# - FIXED: Preserved the meta-learning-specific redis DB index (db + 10).
# - REMOVED: Unnecessary imports (redis, chromadb, service classes).
#
# v10.5 MAJOR CHANGES:
# - IMPLEMENTED (Fix #7): Added AsyncToolGeneratorAgent,
#   AsyncToolCritiqueAgent, and GeneratedToolWriterAgent.
# - IMPLEMENTED (Fix #7): Modified build_meta_learning_graph to include
#   a new branch for tool generation based on hypothesis type.
# - IMPLEMENTED (Fix #8, #13): run_meta_learning composition root
#   now instantiates and injects MetricsCollector and SemanticValidator.
# - FIXED: All v10_4 imports and class names updated to v10_5.
# - FIXED: State object 'MetaGraphState' (from core) now used.
# - FIXED (TEST): Removed redundant/conflicting conditional edges
#   from 'critique_proposal' node to pass test_meta_learning_graph_tool_gen_route.

import json
import logging
import os
import uuid
import asyncio
# import redis # v10.5 REFACTOR: Removed
# import chromadb # v10.5 REFACTOR: Removed
# from chromadb.utils import embedding_functions # v10.5 REFACTOR: Removed
from datetime import datetime
from typing import List, Dict, Any, Optional

# v10.5: Import from new core
from core_v10_5 import (
    ConfigV10_5, WorkflowContext, BaseAgent, MetaGraphState,
    FileIOError, WorkflowError,
    # v10.5: Import all services to be injected
    # CacheManager, CostTracker, FeedbackLogReader, ProposedRulesLoader, # v10.5 REFACTOR: Removed
    # PromptTemplateManager, ResponseValidator, ContextBudgetManager, # v10.5 REFACTOR: Removed
    # MetricsCollector, SemanticValidator, # v10.5 REFACTOR: Removed
    # v10.5 REFACTOR: Import new helper function
    create_workflow_context,
    PydanticSchemaError,
    track_metrics # v10.5 (Fix #8)
)
# v10.5: Import from new main
# from main_v10_5 import setup_logging # v10.5 REFACTOR: Removed (dead code)
from langgraph.graph import StateGraph, END
try:
    from langgraph.checkpoint.redis import RedisSaver
except ImportError:
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver as RedisSaver
    except ImportError:
        from langgraph.checkpoint.memory import MemorySaver as RedisSaver

# v10.5: Logger name updated
logger = logging.getLogger("meta_learner_v10_5")

# ============================================================================
# ROW 7: HOT-RELOAD RULE MANAGER (Preserved)
# ============================================================================

class HotReloadRuleManager:
    """ROW 7: Manages hot-reload of proposed rules"""
    
    def __init__(self, rules_path: str, auto_approve_threshold: float = 0.85):
        self.rules_path = rules_path
        self.auto_approve_threshold = auto_approve_threshold
    
    def write_proposed_rule(self, rule: Dict[str, Any], confidence: float) -> bool:
        try:
            status = "APPROVED" if confidence >= self.auto_approve_threshold else "PROPOSED"
            log_entry = {
                "timestamp": datetime.now().isoformat(), "status": status,
                "confidence": confidence, "pattern": rule,
            }
            os.makedirs(os.path.dirname(self.rules_path), exist_ok=True)
            with open(self.rules_path, 'a') as f:
                json.dump(log_entry, f)
                f.write('\n')
            logger.info(f"Rule written: {rule.get('type', 'unknown')} - Status: {status}")
            return True
        except Exception as e:
            logger.error(f"Failed to write rule: {e}")
            return False

# ============================================================================
# META-LEARNING AGENTS (v10.5: Added Tool Gen Agents)
# ============================================================================

class LogReaderAgent(BaseAgent):
    """Reads raw logs from disk"""
    @track_metrics('meta_read_logs') # v10.5 (Fix #8)
    def run(self) -> Dict[str, str]:
        self.log_info("Reading feedback and preference logs...")
        logs = {"feedback_log": "", "preference_log": ""}
        feedback_log_path = self.config.meta_loop_config.feedback_log_path
        preference_log_path = self.config.meta_loop_config.preference_log_path
        
        try:
            if os.path.exists(feedback_log_path):
                with open(feedback_log_path, 'r') as f:
                    logs["feedback_log"] = "\n".join(f.readlines()[-50:])
        except Exception: pass
        try:
            if os.path.exists(preference_log_path):
                with open(preference_log_path, 'r') as f:
                    logs["preference_log"] = "\n".join(f.readlines()[-50:])
        except Exception: pass
        
        return logs

class AsyncLogSummarizerAgent(BaseAgent):
    """Async LLM-based log summarizer"""
    @track_metrics('meta_summarize_logs') # v10.5 (Fix #8)
    async def run_async(self, raw_logs: Dict[str, str], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Summarizing logs with LLM (v10.5)...")
        client = self.get_model_client("qa_model")
        
        prompt_template = self.prompt_manager.get_template("meta_log_reader")
        prompt = prompt_template.format(
            feedback_log=raw_logs.get('feedback_log', 'No feedback log'),
            preference_log=raw_logs.get('preference_log', 'No preference log')
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], dict)
        if error:
            raise PydanticSchemaError(f"LogSummarizer failed validation: {error}")
        
        self.log_feedback(workflow_id, "log_summarization", "success", {})
        return validated_output

class AsyncPatternFinderAgent(BaseAgent):
    """Async pattern detection"""
    @track_metrics('meta_find_patterns') # v10.5 (Fix #8)
    async def run_async(self, log_summary: Dict[str, Any], workflow_id: str) -> List[Dict]:
        self.log_info("Finding patterns in logs (v10.5)...")
        client = self.get_model_client("strategy_model")
        
        prompt_template = self.prompt_manager.get_template("meta_pattern_finder")
        prompt = prompt_template.format(log_data=json.dumps(log_summary))
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], dict)
        if error:
            raise PydanticSchemaError(f"PatternFinder failed validation: {error}")
            
        patterns = validated_output.get("patterns", [])
        self.log_feedback(workflow_id, "pattern_finding", "success", {"patterns_found": len(patterns)})
        return patterns

class AsyncHypothesisGeneratorAgent(BaseAgent):
    """Async hypothesis generation"""
    @track_metrics('meta_gen_hypotheses') # v10.5 (Fix #8)
    async def run_async(self, patterns: List[Dict], previous_critique: Dict[str, Any], workflow_id: str) -> List[Dict]:
        self.log_info("Generating hypotheses (v10.5)...")
        client = self.get_model_client("strategy_model")
        
        prompt_template = self.prompt_manager.get_template("meta_hypothesis_generator")
        prompt = prompt_template.format(
            patterns=json.dumps(patterns),
            critique=json.dumps(previous_critique)
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5, response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], dict)
        if error:
            raise PydanticSchemaError(f"HypothesisGenerator failed validation: {error}")
            
        hypotheses = validated_output.get("hypotheses", [])
        self.log_feedback(workflow_id, "hypothesis_generation", "success", {"hypotheses_generated": len(hypotheses)})
        return hypotheses

class AsyncProposalDrafterAgent(BaseAgent):
    """Async proposal drafting"""
    @track_metrics('meta_draft_proposal') # v10.5 (Fix #8)
    async def run_async(self, hypothesis: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Drafting proposal for hypothesis (v10.5)...")
        client = self.get_model_client("prompt_engineer_model")
        
        prompt_template = self.prompt_manager.get_template("meta_proposal_drafter")
        prompt = prompt_template.format(hypothesis=json.dumps(hypothesis))
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4, response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], dict)
        if error:
            raise PydanticSchemaError(f"ProposalDrafter failed validation: {error}")
        
        validated_output["hypothesis_id"] = hypothesis.get("id", "unknown")
        validated_output["confidence"] = hypothesis.get("confidence", 0.5)
        # v10.5: Add hypothesis_type to route to tool gen
        validated_output["hypothesis_type"] = hypothesis.get("type", "rule_change")
        self.log_feedback(workflow_id, "proposal_drafting", "success", {})
        return validated_output

class AsyncProposalCritiqueAgent(BaseAgent):
    """Async proposal critique"""
    @track_metrics('meta_critique_proposal') # v10.5 (Fix #8)
    async def run_async(self, proposal: Dict[str, Any], patterns: List[Dict], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Critiquing proposal (v10.5)...")
        client = self.get_model_client("critique_model")
        
        prompt_template = self.prompt_manager.get_template("meta_proposal_critique")
        prompt = prompt_template.format(
            patterns=json.dumps(patterns),
            proposal=json.dumps(proposal)
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], dict)
        if error:
            raise PydanticSchemaError(f"ProposalCritique failed validation: {error}")
            
        self.log_feedback(workflow_id, "proposal_critique", "success" if validated_output.get("critique_passed") else "failure", {})
        return validated_output

# v10.5 (Fix #7): New Tool Generation Agents

class AsyncToolGeneratorAgent(BaseAgent):
    """Async LLM-based tool code generator."""
    @track_metrics('meta_generate_tool') # v10.5 (Fix #8)
    async def run_async(self, hypothesis: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Generating new tool code from hypothesis (v10.5)...")
        client = self.get_model_client("meta_tool_generator_model")
        
        prompt_template = self.prompt_manager.get_template("meta_tool_generator")
        prompt = prompt_template.format(hypothesis=json.dumps(hypothesis))
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4, response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], dict)
        if error:
            raise PydanticSchemaError(f"ToolGenerator failed validation: {error}")
            
        tool_code = validated_output.get("tool_code", "")
        tool_name = validated_output.get("tool_name", f"tool_{uuid.uuid4().hex[:6]}")
        
        self.log_feedback(workflow_id, "tool_generation", "success", {"tool_name": tool_name})
        return {"generated_tool_code": tool_code, "generated_tool_name": tool_name}

class AsyncToolCritiqueAgent(BaseAgent):
    """Async LLM-based tool code critique."""
    @track_metrics('meta_critique_tool') # v10.5 (Fix #8)
    async def run_async(self, tool_code: str, workflow_id: str) -> Dict[str, Any]:
        self.log_info("Critiquing generated tool code (v10.5)...")
        client = self.get_model_client("meta_tool_critique_model")
        
        prompt_template = self.prompt_manager.get_template("meta_tool_critique")
        prompt = prompt_template.format(generated_tool_code=tool_code)
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, response_format="json_object"
        )
        
        validated_output, error = self.validator.validate(response["content"], dict)
        if error:
            raise PydanticSchemaError(f"ToolCritique failed validation: {error}")
        
        self.log_feedback(workflow_id, "tool_critique", "success" if validated_output.get("critique_passed") else "failure", {})
        return validated_output

class GeneratedToolWriterAgent(BaseAgent):
    """Local agent to write generated tool code to disk."""
    @track_metrics('meta_write_tool') # v10.5 (Fix #8)
    def run(self, tool_name: str, tool_code: str, workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Writing generated tool '{tool_name}' to disk...")
        
        try:
            tools_dir = self.config.meta_loop_config.generated_tools_path
            os.makedirs(tools_dir, exist_ok=True)
            
            # Sanitize tool_name to be a valid filename
            safe_filename = f"{tool_name.lower().replace(' ', '_')}.py"
            file_path = os.path.join(tools_dir, safe_filename)
            
            with open(file_path, 'w') as f:
                f.write(f"# Generated by Meta-Learning Workflow ID: {workflow_id}\n")
                f.write(f"# Timestamp: {datetime.now().isoformat()}\n\n")
                f.write(tool_code)
                
            self.log_info(f"Successfully wrote new tool to {file_path}")
            return {"status": "success", "file_path": file_path}
        except Exception as e:
            self.log_error(f"Failed to write generated tool: {e}")
            return {"status": "error", "reason": str(e)}

# ============================================================================
# META-LEARNING CONDITIONAL EDGE FUNCTIONS (v10.5: Fix #7)
# ============================================================================

def check_proposal_type(state) -> str:
    """v10.5 (Fix #7): Routes to tool gen or rule gen branch."""
    # Handle both dict and MetaGraphState objects
    if hasattr(state, 'critique'):
        critique_dict = state.critique if isinstance(state.critique, dict) else getattr(state.critique, '__dict__', {})
    else:
        critique_dict = state.get("critique", {}) if isinstance(state, dict) else {}
    
    critique_passed = critique_dict.get("critique_passed", False) if critique_dict else False
    if not critique_passed:
        return "replan"
    
    if hasattr(state, 'proposal'):
        proposal_dict = state.proposal if isinstance(state.proposal, dict) else getattr(state.proposal, '__dict__', {})
    else:
        proposal_dict = state.get("proposal", {}) if isinstance(state, dict) else {}
    
    proposal_type = proposal_dict.get("hypothesis_type", "rule_change") if proposal_dict else "rule_change"
    if proposal_type == "tool_generation":
        logger.info("Proposal critique passed. Routing to TOOL generation.")
        return "generate_tool"
    else:
        logger.info("Proposal critique passed. Routing to RULE generation.")
        return "write_rules"

def check_tool_critique(state) -> str:
    """v10.5 (Fix #7): Checks if generated tool code passed critique."""
    if hasattr(state, 'critique'):
        critique_dict = state.critique if isinstance(state.critique, dict) else getattr(state.critique, '__dict__', {})
    else:
        critique_dict = state.get("critique", {}) if isinstance(state, dict) else {}
    
    critique_passed = critique_dict.get("critique_passed", False) if critique_dict else False
    if critique_passed:
        logger.info("Tool critique passed. Routing to write_tool.")
        return "write_tool"
    else:
        logger.info("Tool critique FAILED. Looping back to generate_tool.")
        return "replan"

def should_replan_hypothesis(state) -> str:
    """v10.5: This edge is now ONLY for hypothesis replanning."""
    if hasattr(state, 'replan_count'):
        replan_count = state.replan_count + 1
    else:
        replan_count = state.get("replan_count", 0) + 1
    
    max_replan = 3
    if replan_count < max_replan:
        logger.info(f"Replan attempt {replan_count}/{max_replan}. Routing to hypothesis_gen.")
        return "hypothesis_gen"
    else:
        logger.error(f"Max replan attempts ({max_replan}) reached. Exiting.")
        return "end"

# ============================================================================
# META-LEARNING GRAPH BUILDER (v10.5: Fix #7)
# ============================================================================

def build_meta_learning_graph(context: WorkflowContext, checkpointer: RedisSaver):
    """Build complete async meta-learning graph"""
    
    workflow = StateGraph(MetaGraphState) # v10.5: Use state class
    
    # --- Meta-Graph Nodes ---
    
    async def read_logs_node(state: MetaGraphState) -> MetaGraphState:
        log_reader = LogReaderAgent(context)
        state.raw_logs = log_reader.run()
        return state
    
    async def summarize_logs_node(state: MetaGraphState) -> MetaGraphState:
        summarizer = AsyncLogSummarizerAgent(context)
        state.log_summary = await summarizer.run_async(state.raw_logs, state.workflow_id)
        return state
    
    async def find_patterns_node(state: MetaGraphState) -> MetaGraphState:
        pattern_finder = AsyncPatternFinderAgent(context)
        state.patterns = await pattern_finder.run_async(state.log_summary, state.workflow_id)
        return state
    
    async def generate_hypotheses_node(state: MetaGraphState) -> MetaGraphState:
        hypothesis_gen = AsyncHypothesisGeneratorAgent(context)
        previous_critique = state.critique or {}
        state.hypotheses = await hypothesis_gen.run_async(state.patterns, previous_critique, state.workflow_id)
        return state
    
    async def draft_proposals_node(state: MetaGraphState) -> MetaGraphState:
        drafter = AsyncProposalDrafterAgent(context)
        hypotheses = state.hypotheses or []
        if not hypotheses: 
            state.proposal = {}
            return state
        
        proposal_tasks = [drafter.run_async(hyp, state.workflow_id) for hyp in hypotheses[:3]]
        proposals = await asyncio.gather(*proposal_tasks)
        best_proposal = max(proposals, key=lambda p: p.get("confidence", 0.0))
        state.proposal = best_proposal
        return state
    
    async def critique_proposal_node(state: MetaGraphState) -> MetaGraphState:
        critique_agent = AsyncProposalCritiqueAgent(context)
        state.critique = await critique_agent.run_async(state.proposal, state.patterns, state.workflow_id)
        return state
    
    async def write_rules_node(state: MetaGraphState) -> MetaGraphState:
        rule_manager = HotReloadRuleManager(
            rules_path=context.config.meta_loop_config.proposed_rules_path
        )
        critique = state.critique or {}
        proposal = state.proposal or {}
        
        if critique.get("critique_passed", False):
            confidence = proposal.get("confidence", 0.5)
            rule_manager.write_proposed_rule(proposal, confidence)
        else:
            logger.info("✗ Proposal (rule) did not pass critique, not writing rule")
        return state

    # v10.5 (Fix #7): New Tool Generation Nodes
    async def generate_tool_node(state: MetaGraphState) -> MetaGraphState:
        tool_gen = AsyncToolGeneratorAgent(context)
        # Use the *proposal* as the hypothesis for tool gen
        tool_gen_output = await tool_gen.run_async(state.proposal, state.workflow_id)
        state.generated_tool_code = tool_gen_output.get("generated_tool_code")
        state.proposal["generated_tool_name"] = tool_gen_output.get("generated_tool_name") # Save name
        return state

    async def critique_tool_node(state: MetaGraphState) -> MetaGraphState:
        tool_critique = AsyncToolCritiqueAgent(context)
        critique_output = await tool_critique.run_async(state.generated_tool_code, state.workflow_id)
        state.critique = critique_output # Overwrite 'critique' with tool critique
        return state

    async def write_tool_node(state: MetaGraphState) -> MetaGraphState:
        tool_writer = GeneratedToolWriterAgent(context)
        tool_writer.run(
            tool_name=state.proposal.get("generated_tool_name", "unknown_tool"),
            tool_code=state.generated_tool_code,
            workflow_id=state.workflow_id
        )
        return state

    # --- Conditional Edges ---
    
    def check_proposal_type(state: MetaGraphState) -> str:
        """vIndented block.5 (Fix #7): Routes to tool gen or rule gen branch."""
        critique_passed = state.critique.get("critique_passed", False)
        if not critique_passed:
            return "replan" # Critique failed, replan hypothesis
            
        proposal_type = state.proposal.get("hypothesis_type", "rule_change")
        if proposal_type == "tool_generation":
            logger.info("Proposal critique passed. Routing to TOOL generation.")
            return "generate_tool"
        else:
            logger.info("Proposal critique passed. Routing to RULE generation.")
            return "write_rules"

    def check_tool_critique(state: MetaGraphState) -> str:
        """v10.5 (Fix #7): Checks if generated tool code passed critique."""
        critique_passed = state.critique.get("critique_passed", False)
        if critique_passed:
            logger.info("Tool critique passed. Routing to write_tool.")
            return "write_tool"
        else:
            logger.info("Tool critique FAILED. Looping back to generate_tool.")
            # Future: Could add a retry limit here
            return "replan" # Replan (re-generate) the tool

    def should_replan_hypothesis(state: MetaGraphState) -> str:
        """v10.5: This edge is now ONLY for hypothesis replanning."""
        replan_count = state.replan_count + 1
        state.replan_count = replan_count
        
        max_replans = context.config.meta_loop_config.max_meta_replan_loops
        
        if replan_count < max_replans:
            logger.warning(f"Replanning hypothesis (Attempt {replan_count})...")
            return "replan"
        logger.error("Max hypothesis replans reached. Ending meta-loop.")
        return "end"
    
    # --- Build Graph ---
    workflow.add_node("read_logs", read_logs_node)
    workflow.add_node("summarize_logs", summarize_logs_node)
    workflow.add_node("find_patterns", find_patterns_node)
    workflow.add_node("generate_hypotheses", generate_hypotheses_node)
    workflow.add_node("draft_proposals", draft_proposals_node)
    workflow.add_node("critique_proposal", critique_proposal_node)
    
    workflow.add_node("write_rules", write_rules_node) # Rule branch
    
    # v10.5 (Fix #7): Tool branch
    workflow.add_node("generate_tool", generate_tool_node)
    workflow.add_node("critique_tool", critique_tool_node)
    workflow.add_node("write_tool", write_tool_node)
    
    workflow.set_entry_point("read_logs")
    workflow.add_edge("read_logs", "summarize_logs")
    workflow.add_edge("summarize_logs", "find_patterns")
    workflow.add_edge("find_patterns", "generate_hypotheses")
    workflow.add_edge("generate_hypotheses", "draft_proposals")
    workflow.add_edge("draft_proposals", "critique_proposal")
    
    # v10.5 (Fix #7): New conditional routing
    #
    # [DELETED] - This was the first conflicting edge
    #
    
    # v10.5 (Fix #7): Tool gen loop
    workflow.add_edge("generate_tool", "critique_tool")
    workflow.add_conditional_edges(
        "critique_tool",
        check_tool_critique,
        {
            "write_tool": "write_tool",
            "replan": "generate_tool" # Tool critique failed, re-generate tool
        }
    )
    
    # [DELETED] - This was the second conflicting edge
    #
    # [DELETED] - This was the buggy/redundant replan loop
    #

    workflow.add_edge("write_rules", END)
    workflow.add_edge("write_tool", END)
    
    # This is the correct, final conditional edge from 'critique_proposal'
    workflow.add_conditional_edges(
        "critique_proposal",
        check_proposal_type,
        {
            "replan": "generate_hypotheses", # If critique fails, go back to generate_hypotheses
            "generate_tool": "generate_tool", # If critique passes, route to tool gen
            "write_rules": "write_rules"      # If critique passes, route to rule gen
        }
    )

    return workflow.compile(checkpointer=checkpointer)

# ============================================================================
# MAIN META-LEARNING RUNNER (v10.5: Fix #8, #13)
# ============================================================================

async def run_meta_learning(config: ConfigV10_5): # v10.5
    """
    v10.5: Runs async meta-learning graph.
    """
    
    logger.info(f"===== Starting v10.5 Meta-Learning =====")
    
    if not config.meta_loop_config.enable_meta_learning:
        logger.info("Meta-learning disabled in config. Exiting.")
        return

    try:
        # --- v10.5: REFACTOR: COMPOSITION ROOT ---
        # Use the centralized helper from core_v10_5
        # Pass the meta-learning-specific DB index
        meta_db = config.redis_config.db + 10
        context = create_workflow_context(config, db=meta_db)
        logger.info("Initialized WorkflowContext for meta-learning (v10.5)")
        
        # v10.5: Conditionally instantiate checkpointer
        try:
            checkpointer = RedisSaver(
                host=config.redis_config.host, port=config.redis_config.port, db=meta_db
            )
        except TypeError:
            # MemorySaver doesn't take these parameters
            checkpointer = RedisSaver()
        # --- v10.5: REFACTOR END ---
        
        app = build_meta_learning_graph(context, checkpointer)
        
        workflow_id = str(uuid.uuid4())
        run_config = {"configurable": {"thread_id": workflow_id}}
        
        # v10.5: Use state class
        initial_state = MetaGraphState(workflow_id=workflow_id, replan_count=0)
        
        logger.info(f"Executing meta-learning graph (ID: {workflow_id})...")
        
        final_state = None
        async for s in app.astream(initial_state, run_config):
            node_name = list(s.keys())[0]
            logger.info(f"--- Meta-Node: {node_name} ---")
            final_state = s[node_name]
        
        if final_state is None:
             raise WorkflowError("Meta-learning graph did not return a final state.")

        patterns_found = len(final_state.patterns)
        critique_passed = final_state.critique.get("critique_passed", False)
        
        logger.info(f"META-LEARNING RESULTS (v10.5):")
        logger.info(f"  Patterns Found: {patterns_found}")
        logger.info(f"  Critique Passed: {critique_passed}")
        
        cost_summary = context.cost_tracker.get_cost_summary(workflow_id)
        logger.info(f"Meta-learning cost: ${cost_summary['total_workflow_cost']:.4f}")
        logger.info(f"===== v10.5 Meta-Learning Complete =====")
        
    except Exception as e:
        logger.error(f"Meta-Learning failed: {e}", exc_info=True)
        raise

# v10.5: This file is not a main entry point.
# ============================================================================
# END OF run_learning_v10_5.py
# ============================================================================