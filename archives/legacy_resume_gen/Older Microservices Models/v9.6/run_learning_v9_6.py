# File: run_learning_v9_6.py
# Overwrites: run_learning_v9_5.py
# Version: 9.6 (Adversarial)
#
# v9.6 (Adversarial) CHANGES:
# - Re-architected from a simple script into a full agentic graph
#   using LangGraph to achieve a 90+ meta-learning score.
# - Implements dynamic, multi-agent collaboration and critique.

import json
import logging
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict


# Imports from its *own* versioned files (v9.6)
from core_v9_6 import (
    CONFIG, BaseAgent, get_model_client, MetaGraphState,
    META_LOG_READER_SYSTEM_PROMPT,
    META_PATTERN_FINDER_SYSTEM_PROMPT,
    META_HYPOTHESIS_GENERATOR_SYSTEM_PROMPT,
    META_PROPOSAL_DRAFTER_SYSTEM_PROMPT,
    META_PROPOSAL_CRITIQUE_SYSTEM_PROMPT
)
from main_v9_6 import setup_logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis import RedisSaver

logger = logging.getLogger("meta_learner_v9_6")

# --- AGENTS (Preserved from v6.4 structure) ---

class LogReaderAgent(BaseAgent):
    """v9.6: (Python) Reads raw logs from disk."""
    def __init__(self, blackboard: Dict, debug_mode=False):
        super().__init__(blackboard, debug_mode)

    def run(self) -> Dict[str, str]:
        self.log_info("Reading feedback and preference logs...")
        logs = {"feedback_log": "", "preference_log": ""}
        try:
            with open(CONFIG.meta_loop_config.feedback_log_path, 'r') as f:
                logs["feedback_log"] = "\n".join(f.readlines()[-50:]) # Read last 50
        except Exception as e:
            self.log_warning(f"Could not read feedback_log.jsonl: {e}")
        
        try:
            with open(CONFIG.meta_loop_config.preference_log_path, 'r') as f:
                logs["preference_log"] = "\n".join(f.readlines()[-50:]) # Read last 50
        except Exception as e:
            self.log_warning(f"Could not read preference_log.jsonl: {e}")
        
        return logs

class PatternFinderAgent(BaseAgent):
    """v9.6: (LLM) Agent to find recurring failure patterns in feedback logs."""
    
    def __init__(self, blackboard: Dict, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("google", "gemini-2.5-flash")
    
    def run(self, raw_logs: Dict[str, str]) -> List[Dict[str, Any]]:
        self.log_info(f"Analyzing log data to find patterns...")
        if not raw_logs["feedback_log"] and not raw_logs["preference_log"]:
            self.log_warning("No log data found. No patterns to find.")
            return []

        try:
            prompt = META_PATTERN_FINDER_SYSTEM_PROMPT.format(
                log_data=json.dumps(raw_logs)
            )
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(messages=messages, response_format="json_object")
            patterns = response.get("patterns", [])
            self.log_info(f"Found {len(patterns)} patterns.")
            return patterns
        except Exception as e:
            self.log_error(f"PatternFinderAgent failed: {e}")
            return []

class HypothesisGeneratorAgent(BaseAgent):
    """v9.6: (LLM) Generates potential root causes for observed patterns."""
    def __init__(self, blackboard: Dict, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("google", "gemini-2.5-flash")

    def run(self, patterns: List[Dict], critique: Optional[Dict] = None) -> List[Dict]:
        self.log_info(f"Generating hypotheses for {len(patterns)} patterns...")
        try:
            prompt = META_HYPOTHESIS_GENERATOR_SYSTEM_PROMPT.format(
                patterns=json.dumps(patterns),
                critique=json.dumps(critique) if critique else "None"
            )
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(messages=messages, response_format="json_object")
            hypotheses = response.get("hypotheses", [])
            self.log_info(f"Generated {len(hypotheses)} hypotheses.")
            return hypotheses
        except Exception as e:
            self.log_error(f"HypothesisGeneratorAgent failed: {e}")
            return []

class ProposalDrafterAgent(BaseAgent):
    """v9.6: (LLM) Drafts a specific change proposal from a hypothesis."""
    def __init__(self, blackboard: Dict, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("google", "gemini-2.5-flash")

    def run(self, hypothesis: Dict) -> Dict:
        self.log_info(f"Drafting proposal for hypothesis: {hypothesis.get('id')}")
        try:
            prompt = META_PROPOSAL_DRAFTER_SYSTEM_PROMPT.format(
                hypothesis=json.dumps(hypothesis)
            )
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(messages=messages, response_format="json_object")
            self.log_info(f"Proposal drafted: {response.get('type')}")
            return response
        except Exception as e:
            self.log_error(f"ProposalDrafterAgent failed: {e}")
            return {}

class MetaPlannerAgent:
    """
    v9.6: (Python) Writes the final, approved proposal to disk.
    """
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
            self.logger.info(f"Successfully proposed new rule.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write proposals to {proposed_rules_path}: {e}")
            return False

class ProposalCritiqueAgent(BaseAgent):
    """v9.6: (LLM) Adversarially reviews the drafted proposal."""
    def __init__(self, blackboard: Dict, debug_mode=False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("google", "gemini-2.5-flash")

    def run(self, proposal: Dict, patterns: List[Dict]) -> Dict:
        self.log_info(f"Critiquing proposal: {proposal.get('type')}")
        try:
            prompt = META_PROPOSAL_CRITIQUE_SYSTEM_PROMPT.format(
                patterns=json.dumps(patterns),
                proposal=json.dumps(proposal)
            )
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(messages=messages, response_format="json_object")
            if not response.get("critique_passed", False):
                self.log_warning(f"Proposal Critique FAILED: {response.get('reason')}")
            return response
        except Exception as e:
            self.log_error(f"ProposalCritiqueAgent failed: {e}")
            return {"critique_passed": False, "reason": str(e)}


# --- v9.6: Meta-Learning Graph Nodes ---

def run_read_logs(state: MetaGraphState) -> Dict:
    agent = LogReaderAgent(state, debug_mode=True)
    logs = agent.run()
    return {"raw_logs": logs}

def run_find_patterns(state: MetaGraphState) -> Dict:
    agent = PatternFinderAgent(state, debug_mode=True)
    patterns = agent.run(state["raw_logs"])
    if not patterns:
        logger.info("No significant patterns found. No updates proposed.")
        return {"patterns": []}
    return {"patterns": patterns}

def run_generate_hypothesis(state: MetaGraphState) -> Dict:
    agent = HypothesisGeneratorAgent(state, debug_mode=True)
    hypotheses = agent.run(state["patterns"], state.get("critique"))
    return {"hypotheses": hypotheses, "replan_count": state["replan_count"] + 1}

def run_draft_proposal(state: MetaGraphState) -> Dict:
    # Pop one hypothesis off the stack to try
    hypotheses = state["hypotheses"]
    if not hypotheses:
        logger.error("No hypotheses to test. Halting.")
        return {"proposal": {}, "hypotheses": []}
    
    hypothesis_to_test = hypotheses.pop(0)
    agent = ProposalDrafterAgent(state, debug_mode=True)
    proposal = agent.run(hypothesis_to_test)
    return {"proposal": proposal, "hypotheses": hypotheses}

def run_critique_proposal(state: MetaGraphState) -> Dict:
    agent = ProposalCritiqueAgent(state, debug_mode=True)
    critique = agent.run(state["proposal"], state["patterns"])
    return {"critique": critique}

def run_write_proposal(state: MetaGraphState) -> Dict:
    agent = MetaPlannerAgent()
    agent.run(state["proposal"], CONFIG.meta_loop_config.proposed_rules_path)
    return {}

# --- v9.6: Graph Conditional Edges ---

def check_patterns(state: MetaGraphState) -> str:
    if not state["patterns"]:
        return "END"
    return "GENERATE_HYPOTHESIS"

def check_proposal_critique(state: MetaGraphState) -> str:
    critique = state.get("critique", {})
    if critique.get("critique_passed", False):
        return "WRITE_PROPOSAL"
    
    if state["replan_count"] >= CONFIG.meta_loop_config.max_meta_replan_loops:
        logger.error("Meta-Learning: Max replan loops reached. Halting.")
        return "END"
        
    if state["hypotheses"]:
        return "DRAFT_PROPOSAL" # Try next hypothesis
    
    return "GENERATE_HYPOTHESIS" # Regenerate hypotheses with critique

# --- v9.6: Graph Assembly ---

def get_meta_learning_graph_app(checkpointer: 'RedisSaver') -> 'CompiledGraph':
    workflow = StateGraph(MetaGraphState)
    workflow.add_node("READ_LOGS", run_read_logs)
    workflow.add_node("FIND_PATTERNS", run_find_patterns)
    workflow.add_node("GENERATE_HYPOTHESIS", run_generate_hypothesis)
    workflow.add_node("DRAFT_PROPOSAL", run_draft_proposal)
    workflow.add_node("CRITIQUE_PROPOSAL", run_critique_proposal)
    workflow.add_node("WRITE_PROPOSAL", run_write_proposal)
    
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

def run_meta_learning():
    """
    Runs the asynchronous, agentic meta-learning graph (v9.6).
    """
    try:
        setup_logging(debug_mode=False)
    except Exception as e:
        print(f"Warning: setup_logging failed: {e}")
        logging.basicConfig(level=logging.INFO)

    logger.info(f"===== Starting v9.6 Meta-Learning Graph ({datetime.now().isoformat()}) =====")
    
    if not CONFIG.meta_loop_config.enable_meta_learning:
        logger.info("Meta-learning is disabled in master_config_v9_6.json. Exiting.")
        return

    try:
        # Use a different Redis DB for the meta-graph's state
        meta_db = CONFIG.redis_config.db + 10 
        checkpointer = RedisSaver(
            host=CONFIG.redis_config.host,
            port=CONFIG.redis_config.port,
            db=meta_db
        )
        logger.info(f"Meta-Graph checkpointer connected to DB {meta_db}")
        
        app = get_meta_learning_graph_app(checkpointer)
        
        workflow_id = f"meta-loop-{uuid.uuid4()}"
        run_config = {"configurable": {"thread_id": workflow_id}}
        
        inputs = {
            "raw_logs": {}, "log_summary": {}, "patterns": [],
            "hypotheses": [], "proposal": {}, "critique": {},
            "replan_count": 0, "workflow_id": workflow_id
        }
        
        app.invoke(inputs, config=run_config)
        
        logger.info(f"===== v9.6 Meta-Learning Graph Complete ({workflow_id}) =====")
        logger.info(f"Next Step: Review {CONFIG.meta_loop_config.proposed_rules_path} and approve changes.")
        
    except Exception as e:
        logger.error(f"Meta-Learning Graph failed: {e}", exc_info=True)

if __name__ == "__main__":
    run_meta_learning()

