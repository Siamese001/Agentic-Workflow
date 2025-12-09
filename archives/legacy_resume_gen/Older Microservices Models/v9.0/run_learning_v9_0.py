# File: run_learning_v9_0.py
# Overwrites: run_learning_v9_0.py
# Version: 9.0 (Agentic Loops)
#
# v9.0 (Agentic Loops) CHANGES:
# - Imports from core_v9_0.

# - PatternFinderAgent now also reads 'preference_log.jsonl'.
# - MetaPlannerAgent can now propose 'prompt_adjustment' rules.
import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict

# Imports from its *own* versioned files (v9.0)
from core_v9_0 import CONFIG, setup_logging

logger = logging.getLogger("meta_learner_v9_0")

# --- AGENTS (Preserved from v6.4 structure) ---

class PatternFinderAgent:
    """Agent to find recurring failure patterns in feedback logs."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.PatternFinderAgent")
    
    def find_failure_patterns(self, feedback_log_path: str) -> List[Dict[str, Any]]:
        self.logger.info(f"Analyzing feedback log: {feedback_log_path}")
        
        if not os.path.exists(feedback_log_path):
            self.logger.warning("Feedback log not found. No patterns to find.")
            return []

        # --- v7.0: UN-STUBBED LOGIC (Updated) ---
        check_failures = defaultdict(lambda: defaultdict(int))
        check_totals = defaultdict(int)

        try:
            with open(feedback_log_path, 'r') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line)
                        # v7.0: The new log format has 'all_results'
                        all_results = log_entry.get("all_results", [])
                        
                        for result in all_results:
                            # v7.0: Check for 'agent_name' or 'check_name'
                            check_id = result.get("agent_name") or result.get("check_name")
                            passed = result.get("passed")
                            
                            if not check_id:
                                continue
                                
                            context_key = "all_contexts" 
                            
                            check_totals[check_id] += 1
                            if not passed:
                                check_failures[check_id][context_key] += 1
                                
                    except json.JSONDecodeError:
                        self.logger.warning(f"Skipping corrupt log line: {line}")
        
        except Exception as e:
            self.logger.error(f"Failed to read feedback log: {e}")
            return []

        # Now, analyze the aggregates to find patterns
        found_patterns = []
        min_samples = self.config.min_samples_for_learning
        failure_threshold = self.config.pattern_confidence_threshold

        for check_id, totals in check_totals.items():
            if totals < min_samples:
                continue
            
            for context_key, fail_count in check_failures[check_id].items():
                failure_rate = fail_count / totals
                
                if failure_rate >= failure_threshold:
                    pattern = {
                        "check_id": check_id,
                        "failure_rate": failure_rate,
                        "context": context_key,
                        "samples": totals
                    }
                    self.logger.info(f"Found pattern: {check_id} failing {failure_rate:.0%} of the time.")
                    found_patterns.append(pattern)
        
        return found_patterns

    def find_preference_patterns(self, preference_log_path: str) -> List[Dict[str, Any]]:
        self.logger.info(f"Analyzing preference log: {preference_log_path}")
        if not os.path.exists(preference_log_path):
            self.logger.warning("Preference log not found. No patterns to find.")
            return []

        found_patterns = []
        metric_additions = 0
        tone_softening = 0
        total_logs = 0

        try:
            with open(preference_log_path, 'r') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line)
                        total_logs += 1
                        summary = log_entry.get("preference_summary", "").lower()
                        if "metric" in summary or "quantify" in summary or "number" in summary:
                            metric_additions += 1
                        if "tone" in summary or "soften" in summary or "professional" in summary:
                            tone_softening += 1
                    except json.JSONDecodeError:
                        self.logger.warning(f"Skipping corrupt preference log line: {line}")
        except Exception as e:
            self.logger.error(f"Failed to read preference log: {e}")
            return []

        if total_logs < self.config.min_samples_for_learning:
            return []

        # Analyze preference aggregates
        if metric_additions / total_logs >= self.config.pattern_confidence_threshold:
            found_patterns.append({
                "type": "preference",
                "pattern_id": "user_adds_metrics",
                "reason": f"User adds metrics in {metric_additions/total_logs:.0%} of edits."
            })
        
        return found_patterns

class MetaPlannerAgent:
    """
    Agent to *propose* updates to the rules registry based on patterns.
    v7.5: This agent no longer has write access to the live rules.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.MetaPlannerAgent")

    def propose_updates(self, patterns: List[Dict[str, Any]], proposed_rules_path: str) -> bool:
        self.logger.info(f"Analyzing patterns to create proposals...")
        
        proposals = []
        for pattern in patterns:
            check_id = pattern.get("check_id")
            
            if check_id == 'SignalScoreValidatorAgent':
                # PATTERN: The signal score is consistently too strict.
                # ACTION: Propose loosening the MIN_SIGNAL_SCORE threshold.
                proposal = {
                    "type": "threshold_adjustment",
                    "check_id": check_id,
                    "proposed_change": {
                        "key": "MIN_SIGNAL_SCORE",
                        "action": "multiply",
                        "value": 0.9,
                        "reason": f"Failing {pattern['failure_rate']:.0%} of the time."
                    }
                }
                proposals.append(proposal)

            if check_id == 'word_count':
                proposal = {
                    "type": "threshold_adjustment",
                    "check_id": check_id,
                    "proposed_change": {
                        "key": "LOGIC_WC_MIN",
                        "action": "multiply",
                        "value": 0.8,
                        "reason": f"Failing {pattern['failure_rate']:.0%} of the time."
                    }
                }
                proposals.append(proposal)

            # v9.0: Handle preference patterns
            if pattern.get("type") == "preference":
                if pattern.get("pattern_id") == "user_adds_metrics":
                    proposal = {
                        "type": "prompt_adjustment",
                        "check_id": "MetricsSpecialistAgent",
                        "proposed_change": {
                            "key": "DRAFTING_METRICS_SYSTEM_PROMPT",
                            "action": "append",
                            "value": "\n\nCRITICAL: Ensure all bullets are quantified with metrics where possible. The user consistently adds metrics manually.",
                            "reason": pattern["reason"]
                        }
                    }
                    proposals.append(proposal)

        if not proposals:
            self.logger.info("No actionable patterns found. No new proposals created.")
            return True

        # Write the new proposals to the proposal log
        try:
            with open(proposed_rules_path, 'a') as f:
                for prop in proposals:
                    log_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "status": "PROPOSED",
                        "pattern": prop,
                    }
                    json.dump(log_entry, f)
                    f.write('\n')
            
            self.logger.info(f"Successfully proposed {len(proposals)} new rules to {proposed_rules_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write proposals to {proposed_rules_path}: {e}")
            return False

# --- End Agents ---


def run_meta_learning():
    """
    Runs the asynchronous meta-learning loop (v9.0).
    """
    try:
        setup_logging(debug_mode=False) 
    except Exception as e:
        print(f"Warning: setup_logging failed: {e}")
        logging.basicConfig(level=logging.INFO)

    logger.info(f"===== Starting v9.0 Meta-Learning Loop ({datetime.now().isoformat()}) =====")
    
    if not CONFIG.meta_loop_config.enable_meta_learning:
        logger.info("Meta-learning is disabled in master_config_v9_0.json. Exiting.")
        return

    feedback_log_path = CONFIG.meta_loop_config.feedback_log_path
    preference_log_path = CONFIG.meta_loop_config.preference_log_path
    proposed_rules_path = CONFIG.meta_loop_config.proposed_rules_path

    # 1. Activate PatternFinder
    pattern_finder = PatternFinderAgent(config=CONFIG.meta_loop_config)
    failure_patterns = pattern_finder.find_failure_patterns(feedback_log_path)
    preference_patterns = pattern_finder.find_preference_patterns(preference_log_path)
    patterns = failure_patterns + preference_patterns
    
    if not patterns:
        logger.info("No significant patterns found. No updates proposed.")
        logger.info("===== v9.0 Meta-Learning Loop Complete =====")
        return

    logger.info(f"Found {len(patterns)} patterns. Engaging MetaPlanner to create proposals...")
    
    # 2. Activate MetaPlanner
    meta_planner = MetaPlannerAgent()
    update_success = meta_planner.propose_updates(
        patterns, 
        proposed_rules_path
    )
    
    if update_success:
        logger.info("Meta-Planner successfully proposed new rules.")
    else:
        logger.error("Meta-Planner failed to write proposals.")
    
    logger.info("===== v9.0 Meta-Learning Loop Complete =====")
    logger.info(f"Next Step: Review {proposed_rules_path} and approve changes.")

if __name__ == "__main__":
    run_meta_learning()
