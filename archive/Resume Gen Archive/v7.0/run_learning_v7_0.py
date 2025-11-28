# File: run_learning_v7.0.py
# Overwrites: run_learning_v6_4.py
# NEW: Asynchronous Meta-Learning Loop (v7.0)
#
# v7.0 (Based on v7.0 Architecture) CHANGES:
# - Updated all imports from v6_4 to v7_0.
# - 'PatternFinderAgent' updated to parse the new feedback log format,
#   which uses 'agent_name' or 'check_name' instead of 'rule_id'.
# - 'MetaPlannerAgent' logic updated to look for new agent names
#   (e.g., 'SignalScoreValidatorAgent') as pattern keys.
# - Assumes that some agent (even if not yet implemented) will
#   read the 'rules_registry.json' to close the loop.

import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict

# Imports from its *own* versioned files (v7.0)
# We need core_v7_0 for config and logging
from core_v7_0 import CONFIG, setup_logging

logger = logging.getLogger("meta_learner_v7_0")

# --- AGENTS (Preserved from v6.4 structure) ---

class PatternFinderAgent:
    """Agent to find recurring failure patterns in feedback logs."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.PatternFinderAgent")
    
    def find_patterns(self, feedback_log_path: str) -> List[Dict[str, Any]]:
        self.logger.info(f"Analyzing feedback log: {feedback_log_path}")
        
        if not os.path.exists(feedback_log_path):
            self.logger.warning("Feedback log not found. No patterns to find.")
            return []

        # --- v7.0: UN-STUBBED LOGIC (Updated) ---
        # We read the log and find actual patterns based on agent_name/check_name
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
                continue # Not enough data to learn from
            
            for context_key, fail_count in check_failures[check_id].items():
                failure_rate = fail_count / totals
                
                if failure_rate >= failure_threshold:
                    pattern = {
                        "check_id": check_id, # v7.0: Renamed from rule_id
                        "failure_rate": failure_rate,
                        "context": context_key,
                        "samples": totals
                    }
                    self.logger.info(f"Found pattern: {check_id} failing {failure_rate:.0%} of the time.")
                    found_patterns.append(pattern)
        
        return found_patterns

class MetaPlannerAgent:
    """Agent to update the rules registry based on found patterns."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.MetaPlannerAgent")

    def update_rules(self, patterns: List[Dict[str, Any]], rules_registry_path: str) -> bool:
        self.logger.info(f"Updating rules registry: {rules_registry_path}")
        
        registry = {}
        if os.path.exists(rules_registry_path):
            try:
                with open(rules_registry_path, 'r') as f:
                    registry = json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not parse rules registry {rules_registry_path}. Starting new one. Error: {e}")
                registry = {}
        
        # --- v7.0: UN-STUBBED LOGIC (Updated) ---
        changes_made = False
        for pattern in patterns:
            # v7.0: Use check_id
            check_id = pattern.get("check_id")
            
            # This is where the "intelligence" goes.
            # We define how to react to specific patterns.
            
            # v7.0: Update rule name from R21_SIGNAL_SCORE
            if check_id == 'SignalScoreValidatorAgent':
                # PATTERN: The signal score is consistently too strict.
                # ACTION: Loosen the MIN_SIGNAL_SCORE threshold.
                current_threshold = registry.get('MIN_SIGNAL_SCORE', 0.75) # Get current or default
                
                # Loosen threshold by 10% (e.g., 0.75 -> 0.675)
                new_threshold = current_threshold * 0.9 
                new_threshold = max(0.50, new_threshold) # Add a safety floor
                
                if new_threshold < current_threshold:
                    registry['MIN_SIGNAL_SCORE'] = round(new_threshold, 3)
                    self.logger.info(f"MetaPlanner: Loosening MIN_SIGNAL_SCORE from {current_threshold} to {registry['MIN_SIGNAL_SCORE']} due to {pattern['failure_rate']:.0%} failure rate.")
                    changes_made = True
            
            # v7.0: Example for a logic check
            if check_id == 'word_count':
                 # PATTERN: Word count logic check fails often.
                 # ACTION: Widen the acceptable range.
                 current_min = registry.get('LOGIC_WC_MIN', 50)
                 new_min = max(25, current_min * 0.8) # Widen, but not below 25
                 if new_min < current_min:
                    registry['LOGIC_WC_MIN'] = int(new_min)
                    self.logger.info(f"MetaPlanner: Loosening LOGIC_WC_MIN to {registry['LOGIC_WC_MIN']}")
                    changes_made = True

        if not changes_made:
            self.logger.info("No actionable patterns found. Rules registry remains unchanged.")
            return True # Successful, but no changes

        # Write the updated registry back
        try:
            with open(rules_registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
            self.logger.info("Rules registry updated successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write to rules registry: {e}")
            return False

# --- End Agents ---


def run_meta_learning():
    """
    Runs the asynchronous meta-learning loop (v7.0).
    This should be run *after* a batch is complete.
    """
    # Use the v7.0 logging setup
    try:
        setup_logging(debug_mode=False) 
    except Exception as e:
        print(f"Warning: setup_logging failed: {e}")
        logging.basicConfig(level=logging.INFO)

    logger.info(f"===== Starting v7.0 Meta-Learning Loop ({datetime.now().isoformat()}) =====")
    
    if not CONFIG.meta_loop_config.enable_meta_learning:
        logger.info("Meta-learning is disabled in master_config_v7_0.json. Exiting.")
        return

    feedback_log_path = CONFIG.meta_loop_config.feedback_log_path
    rules_registry_path = CONFIG.meta_loop_config.rules_registry_path

    # 1. Activate PatternFinder
    # Pass the relevant config section to the agent
    pattern_finder = PatternFinderAgent(config=CONFIG.meta_loop_config)
    patterns = pattern_finder.find_patterns(feedback_log_path)
    
    if not patterns:
        logger.info("No significant patterns found. No updates made.")
        logger.info("===== v7.0 Meta-Learning Loop Complete =====")
        return

    logger.info(f"Found {len(patterns)} patterns. Engaging MetaPlanner...")
    
    # 2. Activate MetaPlanner
    meta_planner = MetaPlannerAgent()
    update_success = meta_planner.update_rules(
        patterns, 
        rules_registry_path
    )
    
    if update_success:
        logger.info("Meta-Planner successfully updated the rules registry.")
    else:
        logger.error("Meta-Planner failed to update rules.")
    
    logger.info("===== v7.0 Meta-Learning Loop Complete =====")

if __name__ == "__main__":
    run_meta_learning()