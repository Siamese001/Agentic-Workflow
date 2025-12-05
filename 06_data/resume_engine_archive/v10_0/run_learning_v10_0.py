# File: run_learning_v10_0.py
# Version: 10.0 (Modularity, Caching, Async Performance)
#
# v10.0 MAJOR CHANGES:
# ROW 4: Uses WorkflowContext for dependency injection
# ROW 5: Meta-learning agents use caching
# ROW 6: Async meta-learning execution

import json
import logging
import os
import uuid
import asyncio
import redis
from datetime import datetime
from typing import List, Dict, Any, Optional

from core_v10_0 import (
    CONFIG, WorkflowContext, BaseAgent, MetaGraphState,
    META_LOG_READER_SYSTEM_PROMPT,
    META_PATTERN_FINDER_SYSTEM_PROMPT,
    META_HYPOTHESIS_GENERATOR_SYSTEM_PROMPT,
    META_PROPOSAL_DRAFTER_SYSTEM_PROMPT,
    META_PROPOSAL_CRITIQUE_SYSTEM_PROMPT,
    FileIOError
)
from main_v10_0 import setup_logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis import RedisSaver

logger = logging.getLogger("meta_learner_v10_0")

# ============================================================================
# META-LEARNING AGENTS (With dependency injection)
# ============================================================================

class LogReaderAgent(BaseAgent):
    """Reads raw logs from disk"""
    
    def __init__(self, context: WorkflowContext, debug_mode: bool = False):
        super().__init__(context, debug_mode)

    def run(self) -> Dict[str, str]:
        self.log_info("Reading feedback and preference logs...")
        logs = {"feedback_log": "", "preference_log": ""}
        
        try:
            with open(CONFIG.meta_loop_config.feedback_log_path, 'r') as f:
                logs["feedback_log"] = "\n".join(f.readlines()[-50:])
        except FileIOError as e:
            self.log_warning(f"Could not read feedback_log.jsonl: {e}")
        
        try:
            with open(CONFIG.meta_loop_config.preference_log_path, 'r') as f:
                logs["preference_log"] = "\n".join(f.readlines()[-50:])
        except FileIOError as e:
            self.log_warning(f"Could not read preference_log.jsonl: {e}")
        
        return logs

class AsyncPatternFinderAgent(BaseAgent):
    """Finds recurring failure patterns (async)"""
    
    def __init__(self, context: WorkflowContext, debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.client = context.get_model_client("google", "gemini-2.0-flash-exp")
    
    async def run_async(self, raw_logs: Dict[str, str]) -> List[Dict[str, Any]]:
        self.log_info("Analyzing logs for patterns (ASYNC)...")
        
        if not raw_logs["feedback_log"] and not raw_logs["preference_log"]:
            self.log_warning("No log data found.")
            return []

        try:
            prompt = META_PATTERN_FINDER_SYSTEM_PROMPT.format(log_data=json.dumps(raw_logs))
            messages = [{"role": "user", "content": prompt}]
            
            response = await self.client.chat_completion_async(
                messages=messages,
                response_format="json_object"
            )
            
            patterns = response.get("content", {}).get("patterns", [])
            self.log_info(f"Found {len(patterns)} patterns.")
            return patterns
            
        except Exception as e:
            self.log_error(f"PatternFinderAgent failed: {e}")
            return []

class AsyncHypothesisGeneratorAgent(BaseAgent):
    """Generates root causes (async)"""
    
    def __init__(self, context: WorkflowContext, debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.client = context.get_model_client("google", "gemini-2.0-flash-exp")

    async def run_async(self, patterns: List[Dict], critique: Optional[Dict] = None) -> List[Dict]:
        self.log_info(f"Generating hypotheses for {len(patterns)} patterns (ASYNC)...")
        
        try:
            prompt = META_HYPOTHESIS_GENERATOR_SYSTEM_PROMPT.format(
                patterns=json.dumps(patterns),
                critique=json.dumps(critique) if critique else "None"
            )
            messages = [{"role": "user", "content": prompt}]
            
            response = await self.client.chat_completion_async(
                messages=messages,
                response_format="json_object"
            )
            
            hypotheses = response.get("content", {}).get("hypotheses", [])
            self.log_info(f"Generated {len(hypotheses)} hypotheses.")
            return hypotheses
            
        except Exception as e:
            self.log_error(f"HypothesisGeneratorAgent failed: {e}")
            return []

class AsyncProposalDrafterAgent(BaseAgent):
    """Drafts change proposal (async)"""
    
    def __init__(self, context: WorkflowContext, debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.client = context.get_model_client("google", "gemini-2.0-flash-exp")

    async def run_async(self, hypothesis: Dict) -> Dict:
        self.log_info(f"Drafting proposal for: {hypothesis.get('id')} (ASYNC)...")
        
        try:
            prompt = META_PROPOSAL_DRAFTER_SYSTEM_PROMPT.format(hypothesis=json.dumps(hypothesis))
            messages = [{"role": "user", "content": prompt}]
            
            response = await self.client.chat_completion_async(
                messages=messages,
                response_format="json_object"
            )
            
            proposal = response.get("content", {})
            self.log_info(f"Proposal drafted: {proposal.get('type')}")
            return proposal
            
        except Exception as e:
            self.log_error(f"ProposalDrafterAgent failed: {e}")
            return {}

class MetaPlannerAgent:
    """Writes approved proposal to disk"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.MetaPlannerAgent")

    def run(self, proposal: Dict, proposed_rules_path: str) -> bool:
        self.logger.info(f"Writing approved proposal to {proposed_rules_path}...")
        
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "status": "PROPOSED",
                "pattern": proposal,
            }
            with open(proposed_rules_path, 'a') as f:
                json.dump(log_entry, f)
                f.write('\n')
            self.logger.info("Successfully proposed new rule.")
            return True
            
        except FileIOError as e:
            self.logger.error(f"Failed to write to {proposed_rules_path}: {e}")
            return False

class AsyncProposalCritiqueAgent(BaseAgent):
    """Reviews proposal (async)"""
    
    def __init__(self, context: WorkflowContext, debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.client = context.get_model_client("google", "gemini-2.0-flash-exp")

    async def run_async(self, proposal: Dict, patterns: List[Dict]) -> Dict:
        self.log_info(f"Critiquing proposal: {proposal.get('type')} (ASYNC)...")
        
        try:
            prompt = META_PROPOSAL_CRITIQUE_SYSTEM_PROMPT.format(
                patterns=json.dumps(patterns),
                proposal=json.dumps(proposal)
            )
            messages = [{"role": "user", "content": prompt}]
            
            response = await self.client.chat_completion_async(
                messages=messages,
                response_format="json_object"
            )
            
            content = response.get("content", {})
            if not content.get("critique_passed", False):
                self.log_warning(f"Critique FAILED: {content.get('reason')}")
            return content
            
        except Exception as e:
            self.log_error(f"ProposalCritiqueAgent failed: {e}")
            return {"critique_passed": False, "reason": str(e)}

# ============================================================================
# LANGGRAPH NODES (Async)
# ============================================================================

async def run_read_logs(state: MetaGraphState, context: WorkflowContext) -> Dict:
    """Read logs node"""
    agent = LogReaderAgent(context, debug_mode=True)
    logs = agent.run()
    return {"raw_logs": logs}

async def run_find_patterns(state: MetaGraphState, context: WorkflowContext) -> Dict:
    """Find patterns node (async)"""
    agent = AsyncPatternFinderAgent(context, debug_mode=True)
    patterns = await agent.run_async(state["raw_logs"])
    
    if not patterns:
        logger.info("No patterns found. No updates proposed.")
        return {"patterns": []}
    
    return {"patterns": patterns}

async def run_generate_hypothesis(state: MetaGraphState, context: WorkflowContext) -> Dict:
    """Generate hypothesis node (async)"""
    agent = AsyncHypothesisGeneratorAgent(context, debug_mode=True)
    hypotheses = await agent.run_async(state["patterns"], state.get("critique"))
    return {"hypotheses": hypotheses, "replan_count": state["replan_count"] + 1}

async def run_draft_proposal(state: MetaGraphState, context: WorkflowContext) -> Dict:
    """Draft proposal node (async)"""
    hypotheses = state["hypotheses"]
    
    if not hypotheses:
        logger.error("No hypotheses to test. Halting.")
        return {"proposal": {}, "hypotheses": []}
    
    hypothesis_to_test = hypotheses.pop(0)
    agent = AsyncProposalDrafterAgent(context, debug_mode=True)
    proposal = await agent.run_async(hypothesis_to_test)
    
    return {"proposal": proposal, "hypotheses": hypotheses}

async def run_critique_proposal(state: MetaGraphState, context: WorkflowContext) -> Dict:
    """Critique proposal node (async)"""
    agent = AsyncProposalCritiqueAgent(context, debug_mode=True)
    critique = await agent.run_async(state["proposal"], state["patterns"])
    return {"critique": critique}

async def run_write_proposal(state: MetaGraphState, context: WorkflowContext) -> Dict:
    """Write proposal node"""
    agent = MetaPlannerAgent()
    agent.run(state["proposal"], CONFIG.meta_loop_config.proposed_rules_path)
    return {}

# ============================================================================
# ROUTING
# ============================================================================

def check_patterns(state: MetaGraphState) -> str:
    if not state["patterns"]:
        return "END"
    return "GENERATE_HYPOTHESIS"

def check_proposal_critique(state: MetaGraphState) -> str:
    critique = state.get("critique", {})
    
    if critique.get("critique_passed", False):
        return "WRITE_PROPOSAL"
    
    if state["replan_count"] >= CONFIG.meta_loop_config.max_meta_replan_loops:
        logger.error("Max replan loops reached.")
        return "END"
    
    if state["hypotheses"]:
        return "DRAFT_PROPOSAL"
    
    return "GENERATE_HYPOTHESIS"

# ============================================================================
# GRAPH BUILDER (with context injection)
# ============================================================================

def get_meta_learning_graph_app(checkpointer: RedisSaver, context: WorkflowContext):
    """Build meta-learning graph with injected context"""
    workflow = StateGraph(MetaGraphState)
    
    # Add nodes with context injection
    workflow.add_node("READ_LOGS", lambda s: run_read_logs(s, context))
    workflow.add_node("FIND_PATTERNS", lambda s: run_find_patterns(s, context))
    workflow.add_node("GENERATE_HYPOTHESIS", lambda s: run_generate_hypothesis(s, context))
    workflow.add_node("DRAFT_PROPOSAL", lambda s: run_draft_proposal(s, context))
    workflow.add_node("CRITIQUE_PROPOSAL", lambda s: run_critique_proposal(s, context))
    workflow.add_node("WRITE_PROPOSAL", lambda s: run_write_proposal(s, context))
    
    # Build flow
    workflow.set_entry_point("READ_LOGS")
    workflow.add_edge("READ_LOGS", "FIND_PATTERNS")
    workflow.add_conditional_edges("FIND_PATTERNS", check_patterns, {
        "GENERATE_HYPOTHESIS": "GENERATE_HYPOTHESIS",
        "END": END
    })
    workflow.add_edge("GENERATE_HYPOTHESIS", "DRAFT_PROPOSAL")
    workflow.add_edge("DRAFT_PROPOSAL", "CRITIQUE_PROPOSAL")
    workflow.add_conditional_edges("CRITIQUE_PROPOSAL", check_proposal_critique, {
        "WRITE_PROPOSAL": "WRITE_PROPOSAL",
        "DRAFT_PROPOSAL": "DRAFT_PROPOSAL",
        "GENERATE_HYPOTHESIS": "GENERATE_HYPOTHESIS",
        "END": END
    })
    workflow.add_edge("WRITE_PROPOSAL", END)
    
    return workflow.compile(checkpointer=checkpointer)

# ============================================================================
# MAIN ASYNC EXECUTION
# ============================================================================

async def run_meta_learning():
    """Runs v10.0 async meta-learning graph"""
    try:
        setup_logging(debug_mode=False)
    except Exception as e:
        print(f"Warning: setup_logging failed: {e}")
        logging.basicConfig(level=logging.INFO)

    logger.info(f"===== Starting v10.0 Async Meta-Learning Graph ({datetime.now().isoformat()}) =====")
    
    if not CONFIG.meta_loop_config.enable_meta_learning:
        logger.info("Meta-learning disabled. Exiting.")
        return

    try:
        # Row 4: Initialize context
        meta_db = CONFIG.redis_config.db + 10
        redis_client = redis.Redis(
            host=CONFIG.redis_config.host,
            port=CONFIG.redis_config.port,
            db=meta_db
        )
        
        context = WorkflowContext(CONFIG, redis_client)
        logger.info("Initialized WorkflowContext for meta-learning")
        
        # Initialize checkpointer
        checkpointer = RedisSaver(
            host=CONFIG.redis_config.host,
            port=CONFIG.redis_config.port,
            db=meta_db
        )
        logger.info(f"Meta-Graph connected to DB {meta_db}")
        
        # Build graph
        app = get_meta_learning_graph_app(checkpointer, context)
        
        # Execute
        workflow_id = f"meta-loop-{uuid.uuid4()}"
        run_config = {"configurable": {"thread_id": workflow_id}}
        
        inputs = {
            "raw_logs": {}, "log_summary": {}, "patterns": [],
            "hypotheses": [], "proposal": {}, "critique": {},
            "replan_count": 0, "workflow_id": workflow_id
        }
        
        # Row 6: Async execution
        await asyncio.to_thread(app.invoke, inputs, run_config)
        
        # Row 5: Cache stats
        cache_stats = context.cache_manager.get_stats()
        logger.info(f"Meta-learning cache performance: {cache_stats}")
        
        logger.info(f"===== v10.0 Meta-Learning Complete ({workflow_id}) =====")
        logger.info(f"Next Step: Review {CONFIG.meta_loop_config.proposed_rules_path}")
        
    except Exception as e:
        logger.error(f"Meta-Learning Graph failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(run_meta_learning())

# ============================================================================
# END OF run_learning_v10_0.py
# ============================================================================