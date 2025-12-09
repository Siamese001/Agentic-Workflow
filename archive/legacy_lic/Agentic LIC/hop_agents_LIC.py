# File: hop_agents_LIC.py
# Description: Refactored HOP agents for v13.0 pure agentic architecture
# Demonstrates state-based I/O, single responsibility, and tool augmentation

__version__ = "13.0"

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from models_LIC import (
    OutreachMission, ProfileAnalysis, ResearchContext, MessageScaffold,
    Route, Archetype, ValidationResult, ValidationSeverity, RAGResult,
    SenderGroundingWhitelists, FactualGapError, FailureClassifier
)
from state_manager_LIC import StateManager
from memory_LIC import VectorMemoryStore
from llm_clients import GeminiLLMClient
from retrieval_clients import GoogleSearchClient
from utils_LIC import CircuitBreaker
from tools_LIC import CodeInterpreterTool, ValidationToolkit


# ============================================================================
# HOP-1: PROFILE ANALYSIS AGENT
# ============================================================================

class HOP1_ProfileAnalysisAgent:
    """
    v13.0: HOP-1 - Profile Analysis with state-based I/O
    
    Single Responsibility: Classify recipient archetype
    
    Input:  mission_input_LIC.json
    Output: state/1_profile_analysis.json
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize with externalized configuration
        
        Args:
            config: Loaded from config/agent_specs_LIC.json
        """
        self.config = config["profile_analysis_agent"]
        self.archetype_indicators = self.config["archetype_indicators"]
        self.default_archetype = self.config["default_archetype"]
        self.manual_override_threshold = self.config["manual_override_threshold"]
    
    def execute(self, state_mgr: StateManager, mission: OutreachMission) -> str:
        """
        Execute HOP-1: Analyze profile and classify archetype
        
        Args:
            state_mgr: State manager for this mission
            mission: Mission specification
        
        Returns:
            Path to output state file
        """
        print(f"\n{'='*80}")
        print("HOP-1: PROFILE ANALYSIS")
        print(f"{'='*80}\n")
        
        # Extract profile data
        title = mission.recipient_profile.get('title', '').lower()
        
        # Classify archetype using config-based rules
        archetype = None
        confidence = 0.0
        reasoning = ""
        key_indicators = []
        
        for arch_name, arch_config in self.archetype_indicators.items():
            for keyword in arch_config["keywords"]:
                if keyword in title:
                    archetype = arch_name
                    confidence = arch_config["confidence"]
                    reasoning = f"Title '{title}' contains '{keyword}' indicator"
                    key_indicators = [keyword]
                    break
            
            if archetype:
                break
        
        # Default if no match
        if not archetype:
            archetype = self.default_archetype
            confidence = self.config["default_confidence"]
            reasoning = f"Default classification - ambiguous title '{title}'"
            key_indicators = [title]
        
        needs_manual_override = confidence < self.manual_override_threshold
        
        # Prepare output state
        output_state = {
            "archetype": archetype,
            "confidence": confidence,
            "reasoning": reasoning,
            "key_indicators": key_indicators,
            "needs_manual_override": needs_manual_override,
            "recipient_title": title,
            "recipient_name": mission.recipient_profile.get('name', ''),
            "recipient_company": mission.recipient_profile.get('company', '')
        }
        
        # Write to state
        output_path = state_mgr.write_state("HOP-1", output_state)
        
        print(f"✓ Profile Analysis Complete")
        print(f"  Archetype: {archetype}")
        print(f"  Confidence: {confidence:.2f}")
        print(f"  Reasoning: {reasoning}\n")
        
        return output_path


# ============================================================================
# HOP-3: SENDER GROUNDING AGENT
# ============================================================================

class HOP3_SenderGroundingAgent:
    """
    v13.0: HOP-3 - Sender Grounding Extraction (NEW - decomposed from S2)
    
    Single Responsibility: Extract sender capabilities from knowledge base
    
    Input:  master_resume.json, sender_knowledge_base.json
    Output: state/3_sender_grounding.json
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize with externalized configuration
        
        Args:
            config: Loaded from config/agent_specs_LIC.json
        """
        self.config = config["sender_grounding_agent"]
        self.source_files = self.config["source_files"]
        self.extraction_targets = self.config["extraction_targets"]
    
    def execute(self, state_mgr: StateManager) -> str:
        """
        Execute HOP-3: Extract sender grounding from knowledge base
        
        Args:
            state_mgr: State manager for this mission
        
        Returns:
            Path to output state file
        """
        print(f"\n{'='*80}")
        print("HOP-3: SENDER GROUNDING EXTRACTION")
        print(f"{'='*80}\n")
        
        grounding = {
            "team_members": [],
            "products": [],
            "case_studies": [],
            "quantifiable_achievements": [],
            "raw_evidence": {}
        }
        
        # Load sender knowledge base
        for source_file in self.source_files:
            if not os.path.exists(source_file):
                print(f"  ⚠ Warning: {source_file} not found, skipping")
                continue
            
            print(f"  Loading: {source_file}")
            
            with open(source_file, 'r') as f:
                data = json.load(f)
            
            # Extract based on file type
            if "sender_knowledge_base" in source_file:
                # Extract from sender_knowledge_base.json
                if "whitelisted_team_members" in data:
                    grounding["team_members"] = [
                        member["name"] for member in data["whitelisted_team_members"]
                    ]
                
                if "whitelisted_products" in data:
                    grounding["products"] = [
                        product["name"] for product in data["whitelisted_products"]
                    ]
                
                if "whitelisted_case_studies" in data:
                    grounding["case_studies"] = [
                        case["client"] for case in data["whitelisted_case_studies"]
                    ]
                
                if "quantifiable_achievements" in data:
                    grounding["quantifiable_achievements"] = data["quantifiable_achievements"]
            
            elif "master_resume" in source_file:
                # Extract from master_resume.json
                if "professional_experience" in data:
                    for exp in data["professional_experience"]:
                        company = exp.get("company", "")
                        grounding["raw_evidence"].setdefault("companies", []).append(company)
                        
                        # Extract bullet achievements
                        if "bullet_pool" in exp:
                            grounding["raw_evidence"].setdefault("achievements", []).extend(
                                exp["bullet_pool"][:3]  # Top 3 per company
                            )
        
        # Write to state
        output_state = {
            "sender_grounding": grounding,
            "source_files_loaded": [f for f in self.source_files if os.path.exists(f)]
        }
        
        output_path = state_mgr.write_state("HOP-3", output_state)
        
        print(f"✓ Sender Grounding Complete")
        print(f"  Team members: {len(grounding['team_members'])}")
        print(f"  Products: {len(grounding['products'])}")
        print(f"  Case studies: {len(grounding['case_studies'])}")
        print(f"  Achievements: {len(grounding['quantifiable_achievements'])}\n")
        
        return output_path


# ============================================================================
# HOP-4: ROUTING AGENT
# ============================================================================

class HOP4_RoutingAgent:
    """
    v13.0: HOP-4 - Routing Decision with state-based I/O
    
    Single Responsibility: Determine optimal message route
    
    Input:  state/1_profile_analysis.json, mission_input_LIC.json
    Output: state/4_routing_decision.json
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize with externalized configuration
        
        Args:
            config: Loaded from config/agent_specs_LIC.json
        """
        self.config = config["routing_agent"]
        self.routing_rules = self.config["routing_rules"]
    
    def execute(self, state_mgr: StateManager, mission: OutreachMission) -> str:
        """
        Execute HOP-4: Determine message route
        
        Args:
            state_mgr: State manager for this mission
            mission: Mission specification
        
        Returns:
            Path to output state file
        """
        print(f"\n{'='*80}")
        print("HOP-4: ROUTING DECISION")
        print(f"{'='*80}\n")
        
        # Read HOP-1 state
        profile_state = state_mgr.read_state("HOP-1")
        archetype = profile_state["archetype"]
        
        # Extract mission context
        connection_status = mission.connection_status
        prior_message_count = mission.prior_message_count
        
        # Apply routing rules from config
        selected_route = None
        reasoning = []
        
        for route_name, route_config in self.routing_rules.items():
            conditions = route_config["conditions"]
            
            # Check all conditions
            matches = True
            
            if "connection_status" in conditions:
                if connection_status != conditions["connection_status"]:
                    matches = False
            
            if "prior_message_count" in conditions:
                if prior_message_count != conditions["prior_message_count"]:
                    matches = False
            
            if "prior_message_count_gte" in conditions:
                if prior_message_count < conditions["prior_message_count_gte"]:
                    matches = False
            
            if "prior_message_count_gt" in conditions:
                if prior_message_count <= conditions["prior_message_count_gt"]:
                    matches = False
            
            if matches:
                selected_route = route_name
                reasoning.append(f"Route {route_name} selected:")
                reasoning.append(f"  - Connection status: {connection_status}")
                reasoning.append(f"  - Prior messages: {prior_message_count}")
                break
        
        # Default to INMAIL if no match
        if not selected_route:
            selected_route = "INMAIL"
            reasoning.append("Default route: INMAIL")
        
        # Get constraints for this route
        constraints = self.routing_rules[selected_route]["constraints"]
        
        # Prepare output state
        output_state = {
            "route": selected_route,
            "archetype": archetype,
            "constraints": constraints,
            "reasoning": "\n".join(reasoning),
            "connection_status": connection_status,
            "prior_message_count": prior_message_count
        }
        
        # Write to state
        output_path = state_mgr.write_state("HOP-4", output_state)
        
        print(f"✓ Routing Decision Complete")
        print(f"  Route: {selected_route}")
        print(f"  Archetype: {archetype}")
        print(f"  Word range: {constraints['word_range']}")
        print(f"  Char limit: {constraints['char_limit']}\n")
        
        return output_path


# ============================================================================
# HOP-7: GATE DECISION AGENT
# ============================================================================

class HOP7_GateDecisionAgent:
    """
    v13.0: HOP-7 - Gate Decision Agent (NEW - extracted from GenerationOrchestrator)
    
    Single Responsibility: Make the "Slow Loop" decision
    
    Input:  state/6_validation_report.json
    Output: state/7_gate_decision.json
    
    Decision Logic:
    - FACTUAL_FAILURE: raise FactualGapError → trigger S6->S2 meta-loop
    - CREATIVE_FAILURE: raise CreativeFailureError → HALT workflow
    - PASS: return True → proceed to output
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize with externalized configuration
        
        Args:
            config: Loaded from config/agent_specs_LIC.json
        """
        self.config = config["gate_decision_agent"]
        self.factual_failure_rules = set(self.config["factual_failure_rules"])
        self.max_factual_loops = self.config["max_factual_loops"]
        self.max_creative_retries = self.config["max_creative_retries"]
        
        # Track loop counts
        self.factual_loop_count = 0
        self.creative_retry_count = 0
    
    def execute(self, state_mgr: StateManager) -> str:
        """
        Execute HOP-7: Make gate decision based on validation results
        
        Args:
            state_mgr: State manager for this mission
        
        Returns:
            Path to output state file
        
        Raises:
            FactualGapError: If factual failure detected (triggers S6->S2 loop)
            ValueError: If creative failure detected (halts workflow)
        """
        print(f"\n{'='*80}")
        print("HOP-7: GATE DECISION")
        print(f"{'='*80}\n")
        
        # Read HOP-6 validation results
        validation_state = state_mgr.read_state("HOP-6")
        
        validation_results = validation_state.get("validation_results", [])
        passed = validation_state.get("passed", False)
        
        # If validation passed, proceed
        if passed:
            decision = "PASS"
            reasoning = "All validation checks passed"
            
            output_state = {
                "decision": decision,
                "reasoning": reasoning,
                "factual_loop_count": self.factual_loop_count,
                "creative_retry_count": self.creative_retry_count
            }
            
            output_path = state_mgr.write_state("HOP-7", output_state)
            
            print(f"✓ Gate Decision: PASS")
            print(f"  All validations passed\n")
            
            return output_path
        
        # Validation failed - classify failures
        critical_failures = [
            r for r in validation_results
            if r.get("severity") in ["CRITICAL", "HIGH"] and not r.get("passed", True)
        ]
        
        if not critical_failures:
            # No critical failures, allow proceed
            decision = "PASS"
            reasoning = "No critical failures detected"
            
            output_state = {
                "decision": decision,
                "reasoning": reasoning,
                "factual_loop_count": self.factual_loop_count,
                "creative_retry_count": self.creative_retry_count
            }
            
            output_path = state_mgr.write_state("HOP-7", output_state)
            
            print(f"✓ Gate Decision: PASS (non-critical issues only)")
            return output_path
        
        # Classify failure type
        failure_type, failure_message = self._classify_failure(critical_failures)
        
        print(f"  Failure Type: {failure_type}")
        print(f"  Reason: {failure_message}\n")
        
        # Make decision based on failure type
        if failure_type == FailureClassifier.FACTUAL_FAILURE:
            # Check loop limit
            if self.factual_loop_count >= self.max_factual_loops:
                print(f"  ✗ Max factual loops ({self.max_factual_loops}) reached - HALTING")
                
                decision = "HALT_MAX_FACTUAL_LOOPS"
                reasoning = f"Exceeded max factual loops ({self.max_factual_loops})"
                
                output_state = {
                    "decision": decision,
                    "reasoning": reasoning,
                    "factual_loop_count": self.factual_loop_count,
                    "failure_message": failure_message
                }
                
                output_path = state_mgr.write_state("HOP-7", output_state)
                
                raise ValueError(f"Max factual loops exceeded: {failure_message}")
            
            # Trigger S6->S2 meta-loop
            self.factual_loop_count += 1
            
            decision = "FACTUAL_FAILURE"
            reasoning = f"Factual failure detected - triggering S6->S2 meta-loop (attempt {self.factual_loop_count}/{self.max_factual_loops})"
            
            output_state = {
                "decision": decision,
                "reasoning": reasoning,
                "factual_loop_count": self.factual_loop_count,
                "failure_message": failure_message,
                "action": "LOOP_TO_HOP2"
            }
            
            output_path = state_mgr.write_state("HOP-7", output_state)
            
            print(f"  → Triggering S6->S2 meta-loop (attempt {self.factual_loop_count})")
            
            raise FactualGapError(failure_message)
        
        else:  # CREATIVE_FAILURE
            # Check retry limit
            if self.creative_retry_count >= self.max_creative_retries:
                print(f"  ✗ Max creative retries ({self.max_creative_retries}) reached - HALTING")
                
                decision = "HALT_MAX_CREATIVE_RETRIES"
                reasoning = f"Exceeded max creative retries ({self.max_creative_retries})"
                
                output_state = {
                    "decision": decision,
                    "reasoning": reasoning,
                    "creative_retry_count": self.creative_retry_count,
                    "failure_message": failure_message
                }
                
                output_path = state_mgr.write_state("HOP-7", output_state)
                
                raise ValueError(f"Max creative retries exceeded: {failure_message}")
            
            # Trigger S5 creative retry
            self.creative_retry_count += 1
            
            decision = "CREATIVE_FAILURE"
            reasoning = f"Creative failure detected - triggering S5 retry with escalated temperature (attempt {self.creative_retry_count}/{self.max_creative_retries})"
            
            output_state = {
                "decision": decision,
                "reasoning": reasoning,
                "creative_retry_count": self.creative_retry_count,
                "failure_message": failure_message,
                "action": "RETRY_HOP5"
            }
            
            output_path = state_mgr.write_state("HOP-7", output_state)
            
            print(f"  → Triggering S5 creative retry (attempt {self.creative_retry_count})")
            
            # Return path - orchestrator will handle retry
            return output_path
    
    def _classify_failure(
        self,
        failures: List[Dict[str, Any]]
    ) -> Tuple[FailureClassifier, str]:
        """
        Classify failure type to determine retry strategy
        
        Args:
            failures: List of validation failures
        
        Returns:
            (failure_classifier, failure_message)
        """
        for failure in failures:
            rule_id = failure.get("rule_id", "")
            
            # Check if this is a factual failure rule
            if rule_id in self.factual_failure_rules:
                return FailureClassifier.FACTUAL_FAILURE, f"({rule_id}) {failure.get('message', '')}"
            
            # Check details for override
            details = failure.get("details", {})
            if details.get("failure_classifier") == "FACTUAL_FAILURE":
                return FailureClassifier.FACTUAL_FAILURE, f"({rule_id}) {failure.get('message', '')}"
        
        # Default to creative failure
        return FailureClassifier.CREATIVE_FAILURE, f"({failures[0].get('rule_id', '')}) {failures[0].get('message', '')}"


# ============================================================================
# HOP ORCHESTRATOR EXAMPLE
# ============================================================================

class HOPOrchestrator:
    """
    v13.0: Example orchestrator showing HOP execution pattern
    
    This demonstrates the "Foreman" pattern - iterate through HOPs,
    each reading from and writing to state/ directory
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize orchestrator with configuration
        
        Args:
            config: Full configuration from config/agent_specs_LIC.json
        """
        self.config = config
        self.hop_execution_order = config["hop_execution_order"]["hops"]
        
        # Initialize agents
        self.agents = {
            "HOP-1": HOP1_ProfileAnalysisAgent(config),
            "HOP-3": HOP3_SenderGroundingAgent(config),
            "HOP-4": HOP4_RoutingAgent(config),
            "HOP-7": HOP7_GateDecisionAgent(config)
        }
    
    def execute_workflow(self, mission: OutreachMission) -> Dict[str, Any]:
        """
        Execute workflow by iterating through HOPs
        
        Args:
            mission: Mission specification
        
        Returns:
            Workflow result dictionary
        """
        print(f"\n{'='*80}")
        print(f"HOP WORKFLOW ORCHESTRATOR v13.0")
        print(f"Mission ID: {mission.mission_id}")
        print(f"{'='*80}")
        
        # Initialize state manager
        state_mgr = StateManager(mission_id=mission.mission_id)
        
        # Execute each HOP in sequence
        for hop_spec in self.hop_execution_order:
            hop_id = hop_spec["hop_id"]
            agent_name = hop_spec["agent"]
            
            # Check if agent is implemented
            if hop_id not in self.agents:
                print(f"\n⚠ {hop_id} ({agent_name}) - Not yet implemented, skipping")
                continue
            
            # Execute agent
            agent = self.agents[hop_id]
            
            try:
                if hop_id == "HOP-1":
                    agent.execute(state_mgr, mission)
                elif hop_id == "HOP-3":
                    agent.execute(state_mgr)
                elif hop_id == "HOP-4":
                    agent.execute(state_mgr, mission)
                elif hop_id == "HOP-7":
                    agent.execute(state_mgr)
                else:
                    agent.execute(state_mgr, mission)
            
            except FactualGapError as e:
                print(f"\n⚠ Factual gap detected: {e}")
                print("  → Would trigger S6->S2 meta-loop (not implemented in this demo)")
                break
            
            except Exception as e:
                print(f"\n✗ Error in {hop_id}: {e}")
                break
        
        # Get workflow progress
        progress = state_mgr.get_workflow_progress()
        
        print(f"\n{'='*80}")
        print(f"WORKFLOW COMPLETE")
        print(f"Completed HOPs: {', '.join(progress['completed_hops'])}")
        print(f"{'='*80}\n")
        
        return {
            "mission_id": mission.mission_id,
            "status": "partial_demo",
            "completed_hops": progress['completed_hops'],
            "state_files": progress['state_files']
        }


def test_hop_agents():
    """
    Test the HOP agents with a sample mission
    """
    print("\n=== Testing HOP Agents ===\n")
    
    # Load configuration
    with open("config/agent_specs_LIC.json", 'r') as f:
        config = json.load(f)
    
    # Create sample mission
    mission = OutreachMission(
        mission_id="test_hop_001",
        sender_profile={
            "name": "Amit Ayer",
            "title": "Chief AI Officer",
            "company": "Unify Consulting"
        },
        recipient_profile={
            "name": "Sarah Johnson",
            "title": "VP of Engineering",
            "company": "Tech Giants Corp"
        },
        job_description={
            "title": "Head of AI Platform",
            "company": "Tech Giants Corp"
        },
        connection_status="not_connected",
        prior_message_count=0
    )
    
    # Execute workflow
    orchestrator = HOPOrchestrator(config)
    result = orchestrator.execute_workflow(mission)
    
    print(f"\nTest complete. State files created: {len(result['state_files'])}")


if __name__ == "__main__":
    """
    Test the HOP agents
    
    Usage:
        python hop_agents_LIC.py
    """
    test_hop_agents()
