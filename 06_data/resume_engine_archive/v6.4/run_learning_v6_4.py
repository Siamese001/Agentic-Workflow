# File: run_learning_v6_4.py
# NEW: Asynchronous Meta-Learning Loop (v6.4) - UN-STUBBED
# This script is run *after* a batch to analyze feedback and update rules.
# 1. Reads feedback_log.jsonl (created by FeedbackLoggerAgent)
# 2. Activates PatternFinderAgent to find recurring failures
# 3. Activates MetaPlannerAgent to update rules_registry.json

import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict

# Imports from its *own* versioned files
# We need to import the agents, but also core_v6_4 for config and logging
from core_v6_4 import CONFIG, setup_logging # Assuming setup_logging is in core
# We need the agent definitions, which are in agent_swarm
# We'll use stubbed agents for this file as they are not defined yet
# from agent_swarm_v6_4 import PatternFinderAgent, MetaPlannerAgent, FeedbackLoggerAgent

logger = logging.getLogger("meta_learner_v6_4")

# --- UN-STUBBED AGENTS ---
# These agents now perform real logic instead of returning hard-coded data.

class PatternFinderAgent:
    """Agent to find recurring failure patterns in feedback logs."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("PatternFinderAgent")
    
    def find_patterns(self, feedback_log_path: str) -> List[Dict[str, Any]]:
        self.logger.info(f"Analyzing feedback log: {feedback_log_path}")
        
        if not os.path.exists(feedback_log_path):
            self.logger.warning("Feedback log not found. No patterns to find.")
            return []

        # --- UN-STUBBED LOGIC ---
        # We will read the log and find actual patterns.
        rule_failures = defaultdict(lambda: defaultdict(int))
        rule_totals = defaultdict(int)

        try:
            with open(feedback_log_path, 'r') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line)
                        all_results = log_entry.get("all_results", [])
                        
                        for result in all_results:
                            rule_id = result.get("rule_id")
                            passed = result.get("passed")
                            
                            if not rule_id:
                                continue
                                
                            # We can also key by context, e.g., job_title
                            # For simplicity, we'll aggregate by rule_id only.
                            context_key = "all_contexts" 
                            
                            rule_totals[rule_id] += 1
                            if not passed:
                                rule_failures[rule_id][context_key] += 1
                                
                    except json.JSONDecodeError:
                        self.logger.warning(f"Skipping corrupt log line: {line}")
        
        except Exception as e:
            self.logger.error(f"Failed to read feedback log: {e}")
            return []

        # Now, analyze the aggregates to find patterns
        found_patterns = []
        min_samples = self.config.min_samples_for_learning
        failure_threshold = self.config.pattern_confidence_threshold

        for rule_id, totals in rule_totals.items():
            if totals < min_samples:
                continue # Not enough data to learn from
            
            for context_key, fail_count in rule_failures[rule_id].items():
                failure_rate = fail_count / totals
                
                if failure_rate >= failure_threshold:
                    pattern = {
                        "rule_id": rule_id,
                        "failure_rate": failure_rate,
                        "context": context_key,
                        "samples": totals
                    }
                    self.logger.info(f"Found pattern: {rule_id} failing {failure_rate:.0%} of the time.")
                    found_patterns.append(pattern)
        
        return found_patterns

class MetaPlannerAgent:
    """Agent to update the rules registry based on found patterns."""
    
    def __init__(self):
        self.logger = logging.getLogger("MetaPlannerAgent")

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
        
        # --- UN-STUBBED LOGIC ---
        # Apply intelligent changes based on *found* patterns.
        
        changes_made = False
        for pattern in patterns:
            rule_id = pattern.get("rule_id")
            
            # This is where the "intelligence" goes.
            # We define how to react to specific patterns.
            
            if rule_id == 'R21_SIGNAL_SCORE':
                # PATTERN: The signal score is consistently too strict.
                # ACTION: Loosen the MIN_SIGNAL_SCORE threshold.
                current_threshold = registry.get('MIN_SIGNAL_SCORE', 0.75) # Get current or default
                
                # Loosen threshold by 10% (e.g., 0.75 -> 0.675)
                # We apply a relative change, which is safer than a hard-coded value.
                new_threshold = current_threshold * 0.9 
                
                # Add a safety floor
                new_threshold = max(0.50, new_threshold) # Don't let it drop below 0.50
                
                if new_threshold < current_threshold:
                    registry['MIN_SIGNAL_SCORE'] = round(new_threshold, 3)
                    self.logger.info(f"MetaPlanner: Loosening MIN_SIGNAL_SCORE from {current_threshold} to {registry['MIN_SIGNAL_SCORE']} due to {pattern['failure_rate']:.0%} failure rate.")
                    changes_made = True
            
            # Add more "if" blocks here for other rules
            # if rule_id == 'R2_WORD_COUNT':
            #   ...

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

# --- End Un-stubbed Agents ---


def run_meta_learning():
    """
    Runs the asynchronous meta-learning loop (v6.4).
    This should be run *after* a batch is complete.
    """
    # Use the v6.4 logging setup
    setup_logging(debug_mode=False) 
    logger.info(f"===== Starting v6.4 Meta-Learning Loop ({datetime.now().isoformat()}) =====")
    
    if not CONFIG.meta_loop_config.enable_meta_learning:
        logger.info("Meta-learning is disabled in master_config_v6_4.json. Exiting.")
        return

    feedback_log_path = CONFIG.meta_loop_config.feedback_log_path
    rules_registry_path = CONFIG.meta_loop_config.rules_registry_path

    # 1. Activate PatternFinder
    # Pass the relevant config section to the agent
    pattern_finder = PatternFinderAgent(config=CONFIG.meta_loop_config)
    patterns = pattern_finder.find_patterns(feedback_log_path)
    
    if not patterns:
        logger.info("No significant patterns found. No updates made.")
        logger.info("===== v6.4 Meta-Learning Loop Complete =====")
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
    
    logger.info("===== v6.4 Meta-Learning Loop Complete =====")

if __name__ == "__main__":
    run_meta_learning()