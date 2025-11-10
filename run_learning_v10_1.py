# File: run_learning_v10_1.py
# Version: 10.1 (Feedback-Driven Adaptation)

import json
import logging
import os
import uuid
import asyncio
import redis
from datetime import datetime
from typing import List, Dict, Any, Optional

from core_v10_1 import (
    CONFIG, WorkflowContext, BaseAgent, MetaGraphState,
    FileIOError, META_LOG_READER_SYSTEM_PROMPT,
    META_PATTERN_FINDER_SYSTEM_PROMPT, META_HYPOTHESIS_GENERATOR_SYSTEM_PROMPT,
    META_PROPOSAL_DRAFTER_SYSTEM_PROMPT, META_PROPOSAL_CRITIQUE_SYSTEM_PROMPT
)
from main_v10_1 import setup_logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis import RedisSaver

logger = logging.getLogger("meta_learner_v10_1")

# ============================================================================
# ROW 7: HOT-RELOAD RULE MANAGER
# ============================================================================

class HotReloadRuleManager:
    """ROW 7: Manages hot-reload of proposed rules"""
    
    def __init__(self, rules_path: Optional[str] = None):
        self.rules_path = rules_path or CONFIG.meta_loop_config.proposed_rules_path
        self.auto_approve_threshold = 0.85
    
    def write_proposed_rule(self, rule: Dict[str, Any], confidence: float) -> bool:
        """Write rule with auto-approval decision"""
        try:
            if confidence >= self.auto_approve_threshold:
                status = "APPROVED"
                logger.info(f"Auto-approving rule with confidence {confidence:.2%}")
            else:
                status = "PROPOSED"
                logger.info(f"Proposing rule for human review (confidence: {confidence:.2%})")
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "confidence": confidence,
                "pattern": rule,
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
# META-LEARNING AGENTS
# ============================================================================

class LogReaderAgent(BaseAgent):
    """Reads raw logs from disk"""
    
    def __init__(self, context: WorkflowContext, debug_mode: bool = False):
        super().__init__(context, debug_mode)

    def run(self) -> Dict[str, str]:
        """Read feedback and preference logs"""
        self.log_info("Reading feedback and preference logs...")
        logs = {"feedback_log": "", "preference_log": ""}
        
        try:
            if os.path.exists(CONFIG.meta_loop_config.feedback_log_path):
                with open(CONFIG.meta_loop_config.feedback_log_path, 'r') as f:
                    logs["feedback_log"] = "\n".join(f.readlines()[-50:])
            else:
                self.log_warning(f"Feedback log not found: {CONFIG.meta_loop_config.feedback_log_path}")
        except Exception as e:
            self.log_warning(f"Could not read feedback_log.jsonl: {e}")
        
        try:
            if os.path.exists(CONFIG.meta_loop_config.preference_log_path):
                with open(CONFIG.meta_loop_config.preference_log_path, 'r') as f:
                    logs["preference_log"] = "\n".join(f.readlines()[-50:])
            else:
                self.log_warning(f"Preference log not found: {CONFIG.meta_loop_config.preference_log_path}")
        except Exception as e:
            self.log_warning(f"Could not read preference_log.jsonl: {e}")
        
        return logs

class AsyncLogSummarizerAgent(BaseAgent):
    """Async LLM-based log summarizer"""
    
    async def run_async(self, raw_logs: Dict[str, str], workflow_id: str) -> Dict[str, Any]:
        """Summarize logs"""
        self.log_info("Summarizing logs with LLM...")
        
        model_config = CONFIG.model_config.qa_model  # Reuse QA model
        client = self.context.get_model_client(model_config.provider, model_config.model_name)
        
        prompt = f"""{META_LOG_READER_SYSTEM_PROMPT}

Feedback Log (last 50 lines):
{raw_logs.get('feedback_log', 'No feedback log')}

Preference Log (last 50 lines):
{raw_logs.get('preference_log', 'No preference log')}

Output JSON summary."""
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format="json_object"
        )
        
        summary = response["content"]
        
        self.log_feedback(
            workflow_id,
            "log_summarization",
            "success",
            {"total_workflows": summary.get("total_workflows", 0)}
        )
        
        return summary

class AsyncPatternFinderAgent(BaseAgent):
    """Async pattern detection"""
    
    async def run_async(self, log_summary: Dict[str, Any], workflow_id: str) -> List[Dict]:
        """Find recurring patterns"""
        self.log_info("Finding patterns in logs...")
        
        model_config = CONFIG.model_config.strategy_model
        client = self.context.get_model_client(model_config.provider, model_config.model_name)
        
        prompt = META_PATTERN_FINDER_SYSTEM_PROMPT.format(log_data=json.dumps(log_summary))
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format="json_object"
        )
        
        patterns = response["content"].get("patterns", [])
        
        self.log_feedback(
            workflow_id,
            "pattern_finding",
            "success",
            {"patterns_found": len(patterns)}
        )
        
        return patterns

class AsyncHypothesisGeneratorAgent(BaseAgent):
    """Async hypothesis generation"""
    
    async def run_async(self, patterns: List[Dict], previous_critique: Dict[str, Any], workflow_id: str) -> List[Dict]:
        """Generate hypotheses for patterns"""
        self.log_info("Generating hypotheses...")
        
        model_config = CONFIG.model_config.strategy_model
        client = self.context.get_model_client(model_config.provider, model_config.model_name)
        
        prompt = META_HYPOTHESIS_GENERATOR_SYSTEM_PROMPT.format(
            patterns=json.dumps(patterns),
            critique=json.dumps(previous_critique)
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format="json_object"
        )
        
        hypotheses = response["content"].get("hypotheses", [])
        
        self.log_feedback(
            workflow_id,
            "hypothesis_generation",
            "success",
            {"hypotheses_generated": len(hypotheses)}
        )
        
        return hypotheses

class AsyncProposalDrafterAgent(BaseAgent):
    """Async proposal drafting"""
    
    async def run_async(self, hypothesis: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Draft change proposal"""
        self.log_info(f"Drafting proposal for hypothesis: {hypothesis.get('id', 'unknown')}")
        
        model_config = CONFIG.model_config.prompt_engineer_model
        client = self.context.get_model_client(model_config.provider, model_config.model_name)
        
        prompt = META_PROPOSAL_DRAFTER_SYSTEM_PROMPT.format(hypothesis=json.dumps(hypothesis))
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            response_format="json_object"
        )
        
        proposal = response["content"]
        proposal["hypothesis_id"] = hypothesis.get("id", "unknown")
        proposal["confidence"] = hypothesis.get("confidence", 0.5)
        
        self.log_feedback(
            workflow_id,
            "proposal_drafting",
            "success",
            {"hypothesis_id": hypothesis.get("id"), "proposal_type": proposal.get("type")}
        )
        
        return proposal

class AsyncProposalCritiqueAgent(BaseAgent):
    """Async proposal critique"""
    
    async def run_async(self, proposal: Dict[str, Any], patterns: List[Dict], workflow_id: str) -> Dict[str, Any]:
        """Critique proposal"""
        self.log_info("Critiquing proposal...")
        
        model_config = CONFIG.model_config.critique_model
        client = self.context.get_model_client(model_config.provider, model_config.model_name)
        
        prompt = META_PROPOSAL_CRITIQUE_SYSTEM_PROMPT.format(
            patterns=json.dumps(patterns),
            proposal=json.dumps(proposal)
        )
        
        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format="json_object"
        )
        
        critique = response["content"]
        
        self.log_feedback(
            workflow_id,
            "proposal_critique",
            "success" if critique.get("critique_passed", False) else "failure",
            {"passed": critique.get("critique_passed", False)}
        )
        
        return critique

# ============================================================================
# META-LEARNING GRAPH BUILDER
# ============================================================================

def build_meta_learning_graph(context: WorkflowContext, checkpointer: RedisSaver):
    """Build complete async meta-learning graph"""
    
    workflow = StateGraph(dict)
    
    # Node 1: Read logs
    async def read_logs_node(state: dict) -> dict:
        """Read raw logs"""
        log_reader = LogReaderAgent(context)
        raw_logs = log_reader.run()
        return {"raw_logs": raw_logs}
    
    # Node 2: Summarize logs
    async def summarize_logs_node(state: dict) -> dict:
        """Summarize logs with LLM"""
        summarizer = AsyncLogSummarizerAgent(context)
        workflow_id = state.get('workflow_id', '')
        
        log_summary = await summarizer.run_async(state['raw_logs'], workflow_id)
        return {"log_summary": log_summary}
    
    # Node 3: Find patterns
    async def find_patterns_node(state: dict) -> dict:
        """Find recurring patterns"""
        pattern_finder = AsyncPatternFinderAgent(context)
        workflow_id = state.get('workflow_id', '')
        
        patterns = await pattern_finder.run_async(state['log_summary'], workflow_id)
        return {"patterns": patterns}
    
    # Node 4: Generate hypotheses
    async def generate_hypotheses_node(state: dict) -> dict:
        """Generate hypotheses"""
        hypothesis_gen = AsyncHypothesisGeneratorAgent(context)
        workflow_id = state.get('workflow_id', '')
        
        previous_critique = state.get('critique', {})
        hypotheses = await hypothesis_gen.run_async(state['patterns'], previous_critique, workflow_id)
        return {"hypotheses": hypotheses}
    
    # Node 5: Draft proposals (parallel for all hypotheses)
    async def draft_proposals_node(state: dict) -> dict:
        """Draft proposals for all hypotheses"""
        drafter = AsyncProposalDrafterAgent(context)
        workflow_id = state.get('workflow_id', '')
        
        hypotheses = state.get('hypotheses', [])
        
        if not hypotheses:
            logger.warning("No hypotheses to draft proposals for")
            return {"proposal": {}}
        
        # Draft proposals in parallel
        proposal_tasks = [
            drafter.run_async(hyp, workflow_id)
            for hyp in hypotheses[:3]  # Limit to top 3
        ]
        
        proposals = await asyncio.gather(*proposal_tasks)
        
        # Select best proposal (highest confidence)
        best_proposal = max(proposals, key=lambda p: p.get("confidence", 0.0))
        
        return {"proposal": best_proposal}
    
    # Node 6: Critique proposal
    async def critique_proposal_node(state: dict) -> dict:
        """Critique proposal"""
        critique_agent = AsyncProposalCritiqueAgent(context)
        workflow_id = state.get('workflow_id', '')
        
        critique = await critique_agent.run_async(
            state['proposal'],
            state['patterns'],
            workflow_id
        )
        
        return {"critique": critique}
    
    # Node 7: Write approved rules
    async def write_rules_node(state: dict) -> dict:
        """Write rules if critique passed"""
        rule_manager = HotReloadRuleManager()
        
        critique = state.get('critique', {})
        proposal = state.get('proposal', {})
        
        if critique.get("critique_passed", False):
            confidence = proposal.get("confidence", 0.5)
            success = rule_manager.write_proposed_rule(proposal, confidence)
            
            if success:
                logger.info(f"✓ Rule written successfully with confidence {confidence:.2%}")
            else:
                logger.error("✗ Failed to write rule")
        else:
            logger.info("✗ Proposal did not pass critique, not writing rule")
            reason = critique.get("reason", "No reason provided")
            logger.info(f"   Critique reason: {reason}")
        
        return {}
    
    # Node 8: Replan check
    def should_replan(state: dict) -> str:
        """Decide if we should replan"""
        replan_count = state.get('replan_count', 0)
        critique_passed = state.get('critique', {}).get('critique_passed', False)
        
        max_replans = CONFIG.meta_loop_config.max_meta_replan_loops
        
        if critique_passed:
            return "write_rules"
        elif replan_count < max_replans:
            return "replan"
        else:
            return "end"
    
    # Build graph
    workflow.add_node("read_logs", read_logs_node)
    workflow.add_node("summarize_logs", summarize_logs_node)
    workflow.add_node("find_patterns", find_patterns_node)
    workflow.add_node("generate_hypotheses", generate_hypotheses_node)
    workflow.add_node("draft_proposals", draft_proposals_node)
    workflow.add_node("critique_proposal", critique_proposal_node)
    workflow.add_node("write_rules", write_rules_node)
    
    # Connect nodes
    workflow.set_entry_point("read_logs")
    workflow.add_edge("read_logs", "summarize_logs")
    workflow.add_edge("summarize_logs", "find_patterns")
    workflow.add_edge("find_patterns", "generate_hypotheses")
    workflow.add_edge("generate_hypotheses", "draft_proposals")
    workflow.add_edge("draft_proposals", "critique_proposal")
    
    # Conditional edge after critique
    workflow.add_conditional_edges(
        "critique_proposal",
        should_replan,
        {
            "write_rules": "write_rules",
            "replan": "generate_hypotheses",
            "end": END
        }
    )
    
    workflow.add_edge("write_rules", END)
    
    return workflow.compile(checkpointer=checkpointer)

# ============================================================================
# MAIN META-LEARNING RUNNER
# ============================================================================

async def run_meta_learning():
    """Runs v10.1 async meta-learning graph with hot-reload"""
    try:
        setup_logging(debug_mode=False)
    except Exception as e:
        print(f"Warning: setup_logging failed: {e}")
        logging.basicConfig(level=logging.INFO)

    logger.info(f"===== Starting v10.1 Meta-Learning ({datetime.now().isoformat()}) =====")
    
    if not CONFIG.meta_loop_config.enable_meta_learning:
        logger.info("Meta-learning disabled in config. Exiting.")
        return

    try:
        # Initialize Redis (separate DB for meta-learning)
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
        
        # Build graph
        app = build_meta_learning_graph(context, checkpointer)
        logger.info("Built meta-learning graph with 8 nodes")
        
        # Initialize rule manager
        rule_manager = HotReloadRuleManager()
        logger.info("✓ Rules with high confidence (≥85%) are automatically approved")
        
        # Run meta-learning
        workflow_id = str(uuid.uuid4())
        run_config = {"configurable": {"thread_id": workflow_id}}
        
        initial_state = {
            "workflow_id": workflow_id,
            "raw_logs": {},
            "log_summary": {},
            "patterns": [],
            "hypotheses": [],
            "proposal": {},
            "critique": {},
            "replan_count": 0
        }
        
        logger.info(f"Meta-learning workflow ID: {workflow_id}")
        logger.info("Executing meta-learning graph...")
        
        final_state = await asyncio.to_thread(
            app.invoke,
            initial_state,
            run_config
        )
        
        # Report results
        patterns_found = len(final_state.get('patterns', []))
        hypotheses_generated = len(final_state.get('hypotheses', []))
        critique_passed = final_state.get('critique', {}).get('critique_passed', False)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"META-LEARNING RESULTS:")
        logger.info(f"  Patterns Found: {patterns_found}")
        logger.info(f"  Hypotheses Generated: {hypotheses_generated}")
        logger.info(f"  Critique Passed: {critique_passed}")
        logger.info(f"  Replans Used: {final_state.get('replan_count', 0)}/{CONFIG.meta_loop_config.max_meta_replan_loops}")
        
        if critique_passed:
            proposal = final_state.get('proposal', {})
            logger.info(f"  ✓ Approved Rule: {proposal.get('type', 'unknown')}")
            logger.info(f"  ✓ Confidence: {proposal.get('confidence', 0.0):.2%}")
        else:
            logger.info(f"  ✗ No rule approved this run")
        
        logger.info(f"{'='*80}\n")
        
        # Cache stats
        cache_stats = context.cache_manager.get_stats()
        logger.info(f"Cache performance: {cache_stats}")
        
        # Cost tracking
        cost_summary = context.cost_tracker.get_cost_summary(workflow_id)
        logger.info(f"Meta-learning cost: ${cost_summary['total_workflow_cost']:.4f}")
        
        logger.info(f"===== v10.1 Meta-Learning Complete =====")
        
    except Exception as e:
        logger.error(f"Meta-Learning failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(run_meta_learning())

# ============================================================================
# END OF run_learning_v10_1.py
# ============================================================================
