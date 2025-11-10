# File: run_learning_v10_3.py
# Version: 10.3 (Instructional Injection)
#
# v10.3 MAJOR CHANGES:
# - Enforced Strict Dependency Injection: This file no longer runs
#   as a standalone `if __name__ == "__main__"` script. It's now a module
#   imported by `run_batch_v10_3.py`.
# - Eliminated Service Locator Pattern: `run_meta_learning` now accepts
#   the `config: ConfigV10_3` object from the batch runner.
# - True Composition Root: `run_meta_learning` instantiates all
#   services (PromptManager, Validator, etc.) for the meta-learning
#   context.
# - Eradicated Hardcoded Prompts: All local `META_..._PROMPT` constants
#   are GONE. Agents now call `self.prompt_manager.get_template()`.
# - Mandated Schema Validation: All meta-learning agents now use
#   `self.validator.validate()` and Pydantic models (though simplified
#   for this stack, they still use the validator).

import json
import logging
import os
import uuid
import asyncio
import redis
import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime
from typing import List, Dict, Any, Optional

# v10.3: Import from new core
from core_v10_3 import (
    ConfigV10_3, WorkflowContext, BaseAgent, MetaGraphState,
    FileIOError,
    # v10.3: Import all services to be injected
    CacheManager, CostTracker, FeedbackLogReader, ProposedRulesLoader,
    PromptTemplateManager, ResponseValidator, ContextBudgetManager,
    PydanticSchemaError
)
# v10.3: Import from new main
from main_v10_3 import setup_logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis import RedisSaver

logger = logging.getLogger("meta_learner_v10_3")

# ============================================================================
# ROW 7: HOT-RELOAD RULE MANAGER (Preserved)
# ============================================================================

class HotReloadRuleManager:
    """ROW 7: Manages hot-reload of proposed rules"""
    
    def __init__(self, rules_path: str, auto_approve_threshold: float = 0.85):
        self.rules_path = rules_path
        self.auto_approve_threshold = auto_approve_threshold
    
    def write_proposed_rule(self, rule: Dict[str, Any], confidence: float) -> bool:
        """Write rule with auto-approval decision"""
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
# META-LEARNING AGENTS (v10.3: Validated, Prompts Centralized)
# ============================================================================

class LogReaderAgent(BaseAgent):
    """Reads raw logs from disk"""
    def run(self) -> Dict[str, str]:
        """Read feedback and preference logs"""
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
    async def run_async(self, raw_logs: Dict[str, str], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Summarizing logs with LLM (v10.3)...")
        client = self.get_model_client("qa_model")
        
        # v10.3: Get prompt from central manager
        prompt_template = self.prompt_manager.get_template("meta_log_reader")
        prompt = prompt_template.format(
            feedback_log=raw_logs.get('feedback_log', 'No feedback log'),
            preference_log=raw_logs.get('preference_log', 'No preference log')
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, response_format="json_object"
        )
        
        # v10.3: Validate output (simple dict validation)
        validated_output, error = self.validator.validate(response["content"], dict)
        if error:
            raise PydanticSchemaError(f"LogSummarizer failed validation: {error}")
        
        self.log_feedback(workflow_id, "log_summarization", "success", {})
        return validated_output

class AsyncPatternFinderAgent(BaseAgent):
    """Async pattern detection"""
    async def run_async(self, log_summary: Dict[str, Any], workflow_id: str) -> List[Dict]:
        self.log_info("Finding patterns in logs (v10.3)...")
        client = self.get_model_client("strategy_model")
        
        # v10.3: Get prompt from central manager
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
    async def run_async(self, patterns: List[Dict], previous_critique: Dict[str, Any], workflow_id: str) -> List[Dict]:
        self.log_info("Generating hypotheses (v10.3)...")
        client = self.get_model_client("strategy_model")
        
        # v10.3: Get prompt from central manager
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
    async def run_async(self, hypothesis: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        self.log_info(f"Drafting proposal for hypothesis (v10.3)...")
        client = self.get_model_client("prompt_engineer_model")
        
        # v10.3: Get prompt from central manager
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
        self.log_feedback(workflow_id, "proposal_drafting", "success", {})
        return validated_output

class AsyncProposalCritiqueAgent(BaseAgent):
    """Async proposal critique"""
    async def run_async(self, proposal: Dict[str, Any], patterns: List[Dict], workflow_id: str) -> Dict[str, Any]:
        self.log_info("Critiquing proposal (v10.3)...")
        client = self.get_model_client("critique_model")
        
        # v10.3: Get prompt from central manager
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

# ============================================================================
# META-LEARNING GRAPH BUILDER (v10.3)
# ============================================================================

def build_meta_learning_graph(context: WorkflowContext, checkpointer: RedisSaver):
    """Build complete async meta-learning graph"""
    
    workflow = StateGraph(dict)
    
    # --- Meta-Graph Nodes ---
    
    async def read_logs_node(state: dict) -> dict:
        log_reader = LogReaderAgent(context)
        return {"raw_logs": log_reader.run()}
    
    async def summarize_logs_node(state: dict) -> dict:
        summarizer = AsyncLogSummarizerAgent(context)
        workflow_id = state.get('workflow_id', '')
        return {"log_summary": await summarizer.run_async(state['raw_logs'], workflow_id)}
    
    async def find_patterns_node(state: dict) -> dict:
        pattern_finder = AsyncPatternFinderAgent(context)
        workflow_id = state.get('workflow_id', '')
        return {"patterns": await pattern_finder.run_async(state['log_summary'], workflow_id)}
    
    async def generate_hypotheses_node(state: dict) -> dict:
        hypothesis_gen = AsyncHypothesisGeneratorAgent(context)
        workflow_id = state.get('workflow_id', '')
        previous_critique = state.get('critique', {})
        return {"hypotheses": await hypothesis_gen.run_async(state['patterns'], previous_critique, workflow_id)}
    
    async def draft_proposals_node(state: dict) -> dict:
        drafter = AsyncProposalDrafterAgent(context)
        workflow_id = state.get('workflow_id', '')
        hypotheses = state.get('hypotheses', [])
        if not hypotheses: return {"proposal": {}}
        
        proposal_tasks = [drafter.run_async(hyp, workflow_id) for hyp in hypotheses[:3]]
        proposals = await asyncio.gather(*proposal_tasks)
        best_proposal = max(proposals, key=lambda p: p.get("confidence", 0.0))
        return {"proposal": best_proposal}
    
    async def critique_proposal_node(state: dict) -> dict:
        critique_agent = AsyncProposalCritiqueAgent(context)
        workflow_id = state.get('workflow_id', '')
        critique = await critique_agent.run_async(state['proposal'], state['patterns'], workflow_id)
        return {"critique": critique}
    
    async def write_rules_node(state: dict) -> dict:
        rule_manager = HotReloadRuleManager(
            rules_path=context.config.meta_loop_config.proposed_rules_path
        )
        critique = state.get('critique', {})
        proposal = state.get('proposal', {})
        
        if critique.get("critique_passed", False):
            confidence = proposal.get("confidence", 0.5)
            rule_manager.write_proposed_rule(proposal, confidence)
        else:
            logger.info("✗ Proposal did not pass critique, not writing rule")
        return {}
    
    def should_replan(state: dict) -> str:
        replan_count = state.get('replan_count', 0)
        critique_passed = state.get('critique', {}).get('critique_passed', False)
        max_replans = context.config.meta_loop_config.max_meta_replan_loops
        
        if critique_passed: return "write_rules"
        if replan_count < max_replans:
            state['replan_count'] = replan_count + 1
            return "replan"
        return "end"
    
    # --- Build Graph ---
    workflow.add_node("read_logs", read_logs_node)
    workflow.add_node("summarize_logs", summarize_logs_node)
    workflow.add_node("find_patterns", find_patterns_node)
    workflow.add_node("generate_hypotheses", generate_hypotheses_node)
    workflow.add_node("draft_proposals", draft_proposals_node)
    workflow.add_node("critique_proposal", critique_proposal_node)
    workflow.add_node("write_rules", write_rules_node)
    
    workflow.set_entry_point("read_logs")
    workflow.add_edge("read_logs", "summarize_logs")
    workflow.add_edge("summarize_logs", "find_patterns")
    workflow.add_edge("find_patterns", "generate_hypotheses")
    workflow.add_edge("generate_hypotheses", "draft_proposals")
    workflow.add_edge("draft_proposals", "critique_proposal")
    workflow.add_conditional_edges(
        "critique_proposal", should_replan,
        {"write_rules": "write_rules", "replan": "generate_hypotheses", "end": END}
    )
    workflow.add_edge("write_rules", END)
    
    return workflow.compile(checkpointer=checkpointer)

# ============================================================================
# MAIN META-LEARNING RUNNER (v10.3: True Composition Root)
# ============================================================================

async def run_meta_learning(config: ConfigV10_3):
    """
    v10.3: Runs async meta-learning graph.
    This function is now the "Composition Root" for meta-learning,
    accepting an injected config.
    """
    
    logger.info(f"===== Starting v10.3 Meta-Learning =====")
    
    if not config.meta_loop_config.enable_meta_learning:
        logger.info("Meta-learning disabled in config. Exiting.")
        return

    try:
        # --- v10.3: COMPOSITION ROOT START ---
        
        # 1. Create Core Services
        meta_db = config.redis_config.db + 10
        redis_client = redis.Redis(
            host=config.redis_config.host, port=config.redis_config.port, db=meta_db
        )
        
        if config.chromadb_config.use_http_client:
            chromadb_client = chromadb.HttpClient(
                host=config.chromadb_config.host, port=config.chromadb_config.port
            )
        else:
            chromadb_client = chromadb.PersistentClient(
                path=config.chromadb_config.persistent_path
            )
        
        cache_manager = CacheManager(
            redis_client, ttl_seconds=config.caching_config.cache_ttl_seconds
        )
        cost_tracker = CostTracker()
        feedback_reader = FeedbackLogReader(
            config.meta_loop_config.feedback_log_path
        )
        rules_loader = ProposedRulesLoader(
            config.meta_loop_config.proposed_rules_path
        )
        prompt_manager = PromptTemplateManager()
        response_validator = ResponseValidator()
        context_budget_manager = ContextBudgetManager(
            default_token_limit=config.performance_config.default_token_limit
        )
        
        # 2. Create and INJECT services into WorkflowContext
        context = WorkflowContext(
            config=config,
            redis_client=redis_client,
            chromadb_client=chromadb_client,
            cache_manager=cache_manager,
            cost_tracker=cost_tracker,
            feedback_reader=feedback_reader,
            rules_loader=rules_loader,
            prompt_manager=prompt_manager,
            response_validator=response_validator,
            context_budget_manager=context_budget_manager
        )
        logger.info("Initialized WorkflowContext for meta-learning (v10.3)")
        
        checkpointer = RedisSaver(
            host=config.redis_config.host, port=config.redis_config.port, db=meta_db
        )
        
        # --- v10.3: COMPOSITION ROOT END ---
        
        app = build_meta_learning_graph(context, checkpointer)
        
        workflow_id = str(uuid.uuid4())
        run_config = {"configurable": {"thread_id": workflow_id}}
        initial_state = {"workflow_id": workflow_id, "replan_count": 0}
        
        logger.info(f"Executing meta-learning graph (ID: {workflow_id})...")
        
        final_state = await asyncio.to_thread(
            app.invoke, initial_state, run_config
        )
        
        patterns_found = len(final_state.get('patterns', []))
        critique_passed = final_state.get('critique', {}).get('critique_passed', False)
        
        logger.info(f"META-LEARNING RESULTS (v10.3):")
        logger.info(f"  Patterns Found: {patterns_found}")
        logger.info(f"  Critique Passed: {critique_passed}")
        
        cost_summary = context.cost_tracker.get_cost_summary(workflow_id)
        logger.info(f"Meta-learning cost: ${cost_summary['total_workflow_cost']:.4f}")
        logger.info(f"===== v10.3 Meta-Learning Complete =====")
        
    except Exception as e:
        logger.error(f"Meta-Learning failed: {e}", exc_info=True)
        raise

# v10.3: Removed `if __name__ == "__main__"` block.
# This file is now only a module imported by run_batch_v10_3.py.

# ============================================================================
# END OF run_learning_v10_3.py
# ============================================================================