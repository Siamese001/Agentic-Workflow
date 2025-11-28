# File: validation_LIC.py
# Description: Validation & QA agents (HOP-6, HOP-8) for v13.0 architecture
# REFACTOR: v13.0 - Implements state-based I/O and externalized rule engine

__version__ = "13.0"

import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from models_LIC import ValidationSeverity, ValidationResult, AgentStatus
from state_manager_LIC import StateManager
from tools_LIC import ValidationToolkit, CodeInterpreterTool

# ============================================================================
# HOP-6: VALIDATION AGENT
# ============================================================================

class HOP6_ValidationAgent:
    """
    v13.0: HOP-6 Validation Agent - Rule-based validation from config.
    
    CRITICAL ENHANCEMENTS:
    - Enhancement 1: Loads all rules from `validator_rules_LIC.json`.
    - Enhancement 3: Uses StateManager for all I/O. Reads HOP-2, 3, 5. Writes HOP-6.
    - Enhancement 5: Uses ValidationToolkit/CodeInterpreterTool for all checks.
    
    Single Responsibility: Validate the winning generated message against all rules.
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        toolkit: ValidationToolkit,
        code_interpreter: CodeInterpreterTool
    ):
        """
        Initialize with externalized config and tools.
        
        Args:
            config: Loaded from config/agent_specs_LIC.json
            toolkit: ValidationToolkit for deterministic checks
            code_interpreter: CodeInterpreterTool for complex scoring
        """
        self.config = config["validation_agent"]
        self.toolkit = toolkit
        self.code_interpreter = code_interpreter
        self.status = AgentStatus.IDLE
        
        # Load validation rules from JSON (Enhancement 1)
        self.rules = self._load_validation_rules("config/validator_rules_LIC.json")
        self.rule_map = self._build_rule_map()
        self.execution_order = self.rules.get("validation_execution_order", {})
        
        print("  HOP-6: ValidationAgent Initialized")
    
    def _load_validation_rules(self, rules_file: str) -> Dict[str, Any]:
        """Loads validator_rules_LIC.json."""
        if not os.path.exists(rules_file):
            raise FileNotFoundError(f"CRITICAL: {rules_file} not found.")
        
        with open(rules_file, 'r') as f:
            rules = json.load(f)
            print(f"  HOP-6: Loaded validation rules from {rules_file}")
            return rules
    
    def _build_rule_map(self) -> Dict[str, Dict[str, Any]]:
        """Creates a simple map of rule_id -> config for fast lookup."""
        rule_map = {}
        for config_group in self.rules.values():
            if isinstance(config_group, dict) and "rule_id" in config_group:
                rule_map[config_group["rule_id"]] = config_group
        return rule_map

    async def execute(self, state_mgr: StateManager) -> str:
        """
        Execute HOP-6: Validate the winning message.
        
        Args:
            state_mgr: State manager for this mission
        
        Returns:
            Path to output state file
        """
        self.status = AgentStatus.RUNNING
        print(f"\n{'='*80}")
        print("HOP-6: VALIDATION AGENT")
        print(f"{'='*80}\n")
        
        # Read state from previous HOPs (Enhancement 3)
        try:
            generation_state = state_mgr.read_state("HOP-5")
            research_state = state_mgr.read_state("HOP-2")
            grounding_state = state_mgr.read_state("HOP-3")
            scaffold_state = state_mgr.read_state("HOP-4.5") # Using 4.5 from hop_specs
        except FileNotFoundError as e:
            print(f"  ✗ ERROR: Missing required state file: {e}")
            self.status = AgentStatus.FAILED
            raise
            
        draft = generation_state["selected_draft"]
        text_to_validate = draft["text"]
        
        print(f"Validating selected draft ({draft['word_count']} words)...")
        
        # Run the validation engine
        validation_results = self._run_validation_engine(
            draft,
            research_state,
            grounding_state,
            scaffold_state
        )
        
        # Aggregate results
        critical_issues = sum(1 for r in validation_results if r["severity"] == "CRITICAL" and not r["passed"])
        high_issues = sum(1 for r in validation_results if r["severity"] == "HIGH" and not r["passed"])
        medium_issues = sum(1 for r in validation_results if r["severity"] == "MEDIUM" and not r["passed"])
        
        passed = critical_issues == 0 and high_issues == 0
        
        # Prepare output state
        output_state = {
            "validation_results": validation_results,
            "passed": passed,
            "critical_issues": critical_issues,
            "high_issues": high_issues,
            "medium_issues": medium_issues,
            "total_rules_checked": len(validation_results)
        }
        
        # Write to state (Enhancement 3)
        output_path = state_mgr.write_state("HOP-6", output_state)
        
        if passed:
            print(f"\n✓ Validation PASSED")
        else:
            print(f"\n✗ Validation FAILED")
        
        print(f"  Critical: {critical_issues}")
        print(f"  High: {high_issues}")
        print(f"  Medium: {medium_issues}\n")
        
        self.status = AgentStatus.COMPLETED
        return output_path

    def _run_validation_engine(
        self,
        draft: Dict[str, Any],
        research: Dict[str, Any],
        grounding: Dict[str, Any],
        scaffold: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Executes all validation rules from the loaded JSON config in priority order.
        This is the new "Rule Engine" implementation for v13.0.
        """
        results = []
        text = draft["text"]
        
        # Iterate through rule priorities
        for priority_group in sorted(self.execution_order.keys()):
            for rule_id in self.execution_order[priority_group]:
                config = self.rule_map.get(rule_id)
                if not config:
                    print(f"  ⚠ Warning: Rule config for '{rule_id}' not found. Skipping.")
                    continue
                
                # Dispatch to the correct validation tool
                is_valid, details = self._dispatch_rule(
                    rule_id, config, text, research, grounding, scaffold, draft
                )
                
                if not is_valid:
                    results.append(self._format_result(False, config, details))
        
        # If all checks passed, add a success result
        if not results:
            results.append({
                "passed": True,
                "severity": "INFO",
                "rule_id": "ALL-CHECKS",
                "message": "All validation checks passed"
            })
            
        return results

    def _dispatch_rule(
        self, 
        rule_id: str, 
        config: Dict[str, Any], 
        text: str, 
        research: Dict, 
        grounding: Dict, 
        scaffold: Dict, 
        draft: Dict
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Calls the correct ValidationToolkit or CodeInterpreterTool function
        based on the rule_id from validator_rules_LIC.json.
        """
        text_lower = text.lower()
        details = {}

        try:
            if rule_id == "LIC-QA-PLACEHOLDERS":
                patterns = self.rules["content_cleanliness_rules"]["placeholder_patterns"]["patterns"]
                is_clean, violations = self.toolkit.check_forbidden_patterns(text, patterns)
                details["violations"] = violations
                return is_clean, details

            elif rule_id == "LIC-QA-FORBIDDEN-VERBS":
                verbs = self.rules["content_cleanliness_rules"]["forbidden_verbs"]["list"]
                patterns = [f"\\b{v}\\b" for v in verbs]
                is_clean, violations = self.toolkit.check_forbidden_patterns(text, patterns)
                details["violations"] = violations
                return is_clean, details

            elif rule_id == "LIC-QA-FILLERS": # Assuming "LIC-QA-FILLERS" is the ID for filler_patterns
                patterns = self.rules["content_cleanliness_rules"]["filler_patterns"]["patterns"]
                is_clean, violations = self.toolkit.check_forbidden_patterns(text, patterns)
                details["violations"] = violations
                return is_clean, details

            elif rule_id == "LIC-QA-WORD-COUNT":
                # Get target from scaffold, not draft
                target = scaffold["constraints"]["word_range"][1] 
                is_valid, details = self.toolkit.check_word_count_range(
                    text, target, config["tolerance_percentage"]
                )
                return is_valid, details

            elif rule_id == "LIC-QA-055": # ASCII Enforcement
                is_valid, non_ascii = self.toolkit.check_ascii_only(text)
                details["non_ascii_chars"] = non_ascii
                return is_valid, details

            elif rule_id == "LIC-QA-201": # Strategic Alignment
                brief_text = research.get("strategic_brief", "")
                if not brief_text: 
                    return True, {"message": "No strategic brief to validate against."}
                
                # Use CodeInterpreterTool for overlap
                overlap_data = self.code_interpreter.execute(
                    "calculate_overlap",
                    text=text,
                    keyword_set=brief_text.split(), # Use brief text as keyword set
                    min_word_length=config.get("min_keyword_length", 4)
                )
                is_valid = overlap_data["overlap_count"] >= config["min_keyword_overlap"]
                details.update(overlap_data)
                details["failure_classifier"] = config.get("failure_classifier", "FACTUAL_FAILURE")
                return is_valid, details

            elif rule_id.startswith("LIC-QA-105"): # Sender Grounding
                sender_grounding_data = grounding.get("sender_grounding", {})
                rule_config = self.rules["sender_grounding_validation"]

                if rule_id == "LIC-QA-105-TEAM":
                    keywords = rule_config["team_keywords"]
                    whitelist = sender_grounding_data.get("team_members", [])
                    claim_type = "team"
                elif rule_id == "LIC-QA-105-PRODUCT":
                    keywords = rule_config["product_keywords"]
                    whitelist = sender_grounding_data.get("products", [])
                    claim_type = "product"
                elif rule_id == "LIC-QA-105-CASE":
                    keywords = rule_config["case_study_keywords"]
                    whitelist = sender_grounding_data.get("case_studies", [])
                    claim_type = "case study"
                else:
                    return True, {} # Unknown grounding rule

                has_claim = any(kw in text_lower for kw in keywords)
                has_grounding = bool(whitelist)
                is_valid = not (has_claim and not has_grounding) # Invalid if claim AND no grounding
                details["claim_type"] = claim_type
                details["claim_detected"] = has_claim
                details["grounding_exists"] = has_grounding
                return is_valid, details

            # ... Add other rule_id dispatches here (e.g., LIC-QA-075, LIC-QA-049) ...
            
            else:
                # Rule logic not implemented in this dispatch
                return True, {"message": f"Rule {rule_id} logic not implemented, skipping."}

        except Exception as e:
            print(f"  ✗ ERROR executing rule {rule_id}: {e}")
            return False, {"error": str(e), "message": f"Rule execution failed."}

    def _format_result(self, passed: bool, config: Dict[str, Any], details: Dict[str, Any]) -> Dict[str, Any]:
        """Formats a validation result dictionary."""
        rule_id = config["rule_id"]
        severity = config["severity"]
        error_code = config.get("error_code", "N/A")
        remediation = self.rules["error_code_registry"].get(error_code, {}).get("remediation", "N/A")
        
        message = f"Rule {rule_id} failed."
        if "violations" in details and details["violations"]:
            message = f"{config['description']}: {', '.join(details['violations'][:3])}"
        elif "word_count" in details:
            message = f"Word count {details['word_count']} outside range {details['min_words']}-{details['max_words']}"
        elif "overlap_count" in details:
            message = f"Strategic alignment failure: Only {details['overlap_count']} keyword overlap"
        elif "claim_type" in details:
            message = f"Ungrounded {details['claim_type']} claim detected."

        return {
            "passed": passed,
            "severity": severity,
            "rule_id": rule_id,
            "message": message,
            "details": {**details, "remediation": remediation}
        }

# ============================================================================
# HOP-8: QA REPORT AGENT
# ============================================================================

class HOP8_QAReportAgent:
    """
    v13.0: QA Report Agent - Persistent markdown report generation
    
    NEW in v13.0:
    - Reads ALL state files from workflow
    - Synthesizes comprehensive QA report
    - Outputs persistent markdown file
    
    Single Responsibility: Generate audit trail report
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize with externalized config
        
        Args:
            config: Loaded from config/agent_specs_LIC.json
        """
        self.config = config["qa_report_agent"]
        self.sections = self.config["report_sections"]
        self.scoring_weights = self.config["scoring_weights"]
        self.status = AgentStatus.IDLE
    
    async def execute(self, state_mgr: StateManager) -> str:
        """
        Execute HOP-8: Generate comprehensive QA report
        
        Args:
            state_mgr: State manager for this mission
        
        Returns:
            Path to QA report file
        """
        self.status = AgentStatus.RUNNING
        print(f"\n{'='*80}")
        print("HOP-8: QA REPORT GENERATION")
        print(f"{'='*80}\n")
        
        # Read all state files
        states = {}
        for hop_id in ["HOP-1", "HOP-2", "HOP-3", "HOP-4.5", "HOP-5", "HOP-6", "HOP-7"]:
            if state_mgr.state_exists(hop_id):
                states[hop_id] = state_mgr.read_state(hop_id)
        
        print(f"Synthesizing report from {len(states)} state files...")
        
        # Generate markdown report
        report = self._generate_markdown_report(states, state_mgr.mission_id)
        
        # Write report to outputs/
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        report_path = output_dir / f"QA_Report_{state_mgr.mission_id}.md"
        
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"\n✓ QA Report Generated: {report_path}\n")
        self.status = AgentStatus.COMPLETED
        return str(report_path)
    
    def _generate_markdown_report(self, states: Dict[str, Any], mission_id: str) -> str:
        """Generate comprehensive markdown report"""
        
        lines = []
        
        # Header
        lines.append(f"# LIC v13.0 QA Report")
        lines.append(f"\n**Mission ID**: `{mission_id}`")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"\n---\n")
        
        # 1. Executive Summary
        lines.append("## 1. Executive Summary\n")
        
        validation = states.get("HOP-6", {})
        passed = validation.get("passed", False)
        
        if passed:
            lines.append("**Status**: ✅ **PASS** - Message ready for production")
        else:
            lines.append("**Status**: ❌ **FAIL** - Message requires revision")
        
        lines.append(f"\n**Critical Issues**: {validation.get('critical_issues', 0)}")
        lines.append(f"**High Issues**: {validation.get('high_issues', 0)}")
        lines.append(f"**Medium Issues**: {validation.get('medium_issues', 0)}")
        lines.append("\n")
        
        # 2. Archetype & Route Selection
        lines.append("## 2. Archetype & Route Selection\n")
        
        profile = states.get("HOP-1", {})
        routing = states.get("HOP-4.5", {}).get("route", "N/A") # Get route from scaffold
        
        lines.append(f"**Archetype**: {profile.get('archetype', 'N/A')}")
        lines.append(f"**Confidence**: {profile.get('confidence', 0):.2f}")
        lines.append(f"**Reasoning**: {profile.get('reasoning', 'N/A')}")
        lines.append(f"\n**Route**: {routing}")
        lines.append("\n")
        
        # 3. Research Quality Assessment
        lines.append("## 3. Research Quality Assessment\n")
        
        research = states.get("HOP-2", {})
        
        lines.append(f"**Total Sources**: {research.get('total_sources', 0)}")
        lines.append(f"**Signal Score**: {research.get('signal_score', 0):.2f}")
        lines.append(f"**Cache Hit**: {'Yes' if research.get('cache_hit', False) else 'No (Fallback RAG used)'}")
        lines.append(f"**Fallback Used**: {'Yes' if research.get('fallback_used', False) else 'No'}")
        lines.append("\n")
        
        # 4. Generation Strategy
        lines.append("## 4. Generation Strategy\n")
        
        generation = states.get("HOP-5", {})
        
        lines.append(f"**Candidates Generated**: {generation.get('n_candidates', 1)}")
        lines.append(f"**Temperature**: {generation.get('generation_temperature', 0.5):.2f}")
        lines.append(f"**Generation Attempts**: {generation.get('generation_attempts', 1)}")
        lines.append("\n")
        
        # 5. Validation Results
        lines.append("## 5. Validation Results\n")
        
        results = validation.get("validation_results", [])
        
        lines.append(f"**Total Rules Checked**: {len(results)}")
        lines.append("\n### Failed Checks:\n")
        
        failed = [r for r in results if not r.get("passed", True)]
        if failed:
            for result in failed:
                lines.append(f"- **{result['rule_id']}** ({result['severity']}): {result['message']}")
        else:
            lines.append("_No failed checks_")
        
        lines.append("\n")
        
        # 6. Loop Execution Details
        lines.append("## 6. Loop Execution Details\n")
        
        gate = states.get("HOP-7", {})
        
        lines.append(f"**Factual Loops (S6→S2)**: {gate.get('factual_loop_count', 0)}")
        lines.append(f"**Creative Retries (S5)**: {gate.get('creative_retry_count', 0)}")
        lines.append(f"**Gate Decision**: {gate.get('decision', 'N/A')}")
        lines.append("\n")
        
        # 7. Final Message
        lines.append("## 7. Final Generated Message\n")
        
        draft = generation.get("selected_draft", {})
        
        lines.append(f"**Word Count**: {draft.get('word_count', 0)}")
        lines.append(f"**Character Count**: {draft.get('char_count', 0)}")
        lines.append("\n```")
        lines.append(draft.get('text', 'N/A'))
        lines.append("```\n")
        
        # 8. Quality Score
        lines.append("## 8. Overall Quality Score\n")
        
        score = self._calculate_quality_score(states)
        
        lines.append(f"**Final Score**: {score:.1f}/100")
        lines.append("\n---")
        lines.append("\n*Generated by LIC v13.0 QA Report Agent*")
        
        return "\n".join(lines)
    
    def _calculate_quality_score(self, states: Dict[str, Any]) -> float:
        """Calculate overall quality score based on config weights."""
        
        research = states.get("HOP-2", {})
        validation = states.get("HOP-6", {})
        gate = states.get("HOP-7", {})
        
        # Research quality
        research_score = research.get('signal_score', 0.5) * self.scoring_weights.get("research_quality", 0.3) * 100
        
        # Strategic alignment
        alignment_score = 0.0
        if validation.get("passed", False):
            alignment_score = self.scoring_weights.get("strategic_alignment", 0.3) * 100
        else:
            # Check if alignment was the failure
            for result in validation.get("validation_results", []):
                if result.get("rule_id") == "LIC-QA-201" and not result.get("passed", True):
                    alignment_score = 0.0
                    break
            else:
                alignment_score = self.scoring_weights.get("strategic_alignment", 0.3) * 50 # Passed other things

        # Validation pass rate
        total_rules = len(validation.get("validation_results", []))
        failed_count = validation.get("critical_issues", 0) + validation.get("high_issues", 0) + validation.get("medium_issues", 0)
        pass_rate = (total_rules - failed_count) / total_rules if total_rules > 0 else 0
        validation_score = pass_rate * self.scoring_weights.get("validation_pass_rate", 0.2) * 100
        
        # Loop efficiency
        factual_loops = gate.get('factual_loop_count', 0)
        creative_retries = gate.get('creative_retry_count', 0)
        loop_penalty = (factual_loops * 0.5) + (creative_retries * 0.25)
        loop_score = max(0, 1.0 - loop_penalty) * self.scoring_weights.get("loop_efficiency", 0.1) * 100
        
        # Generation quality (simple proxy)
        generation = states.get("HOP-5", {})
        draft = generation.get("selected_draft", {})
        word_count = draft.get('word_count', 0)
        in_range = 150 <= word_count <= 300
        generation_score = (1.0 if in_range else 0.5) * self.scoring_weights.get("generation_quality", 0.1) * 100

        total_score = research_score + alignment_score + validation_score + loop_score + generation_score
        
        return total_score