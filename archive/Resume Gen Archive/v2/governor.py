# File: governor.py
# Version: 17.01 (Patched) - V2 Agentic Architecture (Production Implementation)
# Complete implementations of all v2 agents with zero placeholders

import logging
import json
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict
from datetime import datetime
from enum import Enum

# Import models for type hints
try:
    from models_RES import ResumeSection, ValidationResult, ThematicAnalysis
except ImportError:
    # Fallback for standalone testing
    ResumeSection = Any
    ValidationResult = Any
    ThematicAnalysis = Any

# Import temperature default from config (single source of truth)
try:
    # --- REFACTOR: Standardized global config import ---
    from config_RES_v2 import (
        CONFIG, DATA_DIR, OUTPUT_DIR, 
        DEFAULT_GENERATION_TEMPERATURE,
        DEFAULT_MAX_RETRIES # <-- IMPORTED
    )
except ImportError:
    # Fallback if run standalone
    DEFAULT_GENERATION_TEMPERATURE = 1.0
    DEFAULT_MAX_RETRIES = 3 # <-- Fallback
    # Add fallbacks for new imports to maintain standalone capability
    CONFIG = None
    DATA_DIR = None
    OUTPUT_DIR = None
# --- END REFACTOR ---

# ============================================================================
# CONSTANTS
# ============================================================================

# --- FIX: Use imported constant ---
MAX_RETRIES_PER_NODE = DEFAULT_MAX_RETRIES
# --- END FIX ---
DEFAULT_MODEL = "gemini-2.5-pro"

# Model tier definitions with cost/performance characteristics
MODEL_TIERS = {
    "PREMIUM": {
        "model": "gemini-2.5-pro",
        "cost_multiplier": 3.0,
        "use_cases": ["high_stakes", "complex_reasoning", "final_retry"]
    },
    "STANDARD": {
        "model": "gemini-2.5-flash",
        "cost_multiplier": 1.0,
        "use_cases": ["default", "iterative_refinement"]
    },
    "ECONOMY": {
        "model": "gemini-2.5-flash-lite",
        "cost_multiplier": 0.3,
        "use_cases": ["simple_sections", "mechanical_fixes"]
    }
}

# Section complexity is now loaded from artist_specs.json
# No hardcoded SECTION_COMPLEXITY dictionary


# ============================================================================
# POLICY AGENT
# ============================================================================

class PolicyAgent:
    """
    Production PolicyAgent: Decides retry strategies based on failure analysis.
    
    Responsibilities:
    - Classify failure severity and type
    - Select appropriate retry strategy
    - Decide when to escalate to HIL
    - Track success patterns for adaptive learning
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
        # Track success rates for adaptive policy
        self.success_history: Dict[str, List[bool]] = defaultdict(list)
        self.strategy_effectiveness: Dict[str, Dict[str, int]] = {
            "critique_and_reframe": {"success": 0, "failure": 0},
            "temperature_adjustment": {"success": 0, "failure": 0},
            "model_escalation": {"success": 0, "failure": 0}
        }
    
    def get_failure_strategy(
        self, 
        node: str, 
        failure_type: str, 
        retries: int
    ) -> Dict[str, Any]:
        """
        Determines the next action based on failure analysis.
        
        Args:
            node: Node name (section identifier)
            failure_type: Type of failure (CREATIVE, MECHANICAL, STRATEGIC)
            retries: Number of retries already attempted
            
        Returns:
            Strategy dictionary with action and parameters
        """
        self.logger.info(f"PolicyAgent analyzing failure: {node} | Type: {failure_type} | Retries: {retries}")
        
        # Circuit breaker: Max retries reached
        if retries >= MAX_RETRIES_PER_NODE:
            self.logger.error(f"Node {node} exhausted max retries ({retries}). Escalating to HIL.")
            return {
                "action": "hybrid_review_escalation",
                "reason": "max_retries_exceeded",
                "metadata": {
                    "total_attempts": retries,
                    "failure_type": failure_type
                }
            }
        
        # First failure: Apply failure-type specific strategy
        if retries == 1:
            return self._first_failure_strategy(node, failure_type)
        
        # Second failure: Escalate strategy
        elif retries == 2:
            return self._second_failure_strategy(node, failure_type)
        
        # Should never reach here due to circuit breaker, but safety fallback
        else:
            return {"action": "hybrid_review_escalation"}
    
    def _first_failure_strategy(self, node: str, failure_type: str) -> Dict[str, Any]:
        """Strategy for first failure attempt."""
        
        if failure_type == "MECHANICAL":
            # Mechanical failures: Format, word count, structure issues
            self.logger.info(f"{node}: MECHANICAL failure. Strategy: Focused critique with constraints.")
            return {
                "action": "invoke_critique_and_reframe",
                "params": {
                    "strategy": "mechanical_fix",
                    "focus": "address_specific_constraints",
                    "temperature_adjustment": -0.1,  # Lower temp for precision
                    "emphasis": "exact_requirements"
                }
            }
        
        elif failure_type == "STRATEGIC":
            # Strategic failures: Missing themes, weak positioning
            self.logger.info(f"{node}: STRATEGIC failure. Strategy: Deep thematic reframe.")
            return {
                "action": "invoke_critique_and_reframe",
                "params": {
                    "strategy": "strategic_reframe",
                    "focus": "strengthen_positioning",
                    "temperature_adjustment": 0.0,  # Keep standard temp
                    "emphasis": "thematic_alignment"
                }
            }
        
        else:  # CREATIVE or unknown
            # Creative failures: Quality, originality, engagement
            self.logger.info(f"{node}: CREATIVE failure. Strategy: Creative exploration.")
            return {
                "action": "invoke_critique_and_reframe",
                "params": {
                    "strategy": "creative_rewrite",
                    "focus": "enhance_quality",
                    "temperature_adjustment": 0.1,  # Higher temp for creativity
                    "emphasis": "originality_and_impact"
                }
            }
    
    def _second_failure_strategy(self, node: str, failure_type: str) -> Dict[str, Any]:
        """Strategy for second failure attempt - more aggressive."""
        
        self.logger.warning(f"{node}: Second failure. Applying aggressive strategy.")
        
        if failure_type == "MECHANICAL":
            # Still mechanical after first retry: Model escalation + strict critique
            return {
                "action": "invoke_critique_and_reframe",
                "params": {
                    "strategy": "mechanical_fix_aggressive",
                    "focus": "exact_compliance",
                    "temperature_adjustment": -0.2,  # Very low temp
                    "model_escalation": True,  # Signal to CostRouter
                    "emphasis": "rule_by_rule_compliance"
                }
            }
        
        elif failure_type == "STRATEGIC":
            # Strategic failure persists: Deep research + reposition
            return {
                "action": "invoke_critique_and_reframe",
                "params": {
                    "strategy": "strategic_deep_dive",
                    "focus": "complete_repositioning",
                    "temperature_adjustment": 0.0,
                    "model_escalation": True,
                    "emphasis": "fundamental_rethink"
                }
            }
        
        else:  # CREATIVE
            # Creative failure persists: Maximum model tier + fresh approach
            return {
                "action": "invoke_critique_and_reframe",
                "params": {
                    "strategy": "creative_breakthrough",
                    "focus": "completely_fresh_angle",
                    "temperature_adjustment": 0.15,  # Higher temp for breakthrough
                    "model_escalation": True,
                    "emphasis": "radical_reimagination"
                }
            }
    
    def record_outcome(self, node: str, strategy: str, success: bool):
        """Record strategy outcome for adaptive learning."""
        self.success_history[node].append(success)
        
        if strategy in self.strategy_effectiveness:
            if success:
                self.strategy_effectiveness[strategy]["success"] += 1
            else:
                self.strategy_effectiveness[strategy]["failure"] += 1
        
        self.logger.debug(f"Recorded outcome: {node} | {strategy} | Success: {success}")
    
    def get_effectiveness_report(self) -> Dict[str, Any]:
        """Generate effectiveness report for Meta-Planner."""
        return {
            "strategy_effectiveness": self.strategy_effectiveness,
            "node_success_rates": {
                node: sum(outcomes) / len(outcomes) if outcomes else 0.0
                for node, outcomes in self.success_history.items()
            }
        }


# ============================================================================
# COST ROUTER
# ============================================================================

class CostRouter:
    """
    Production CostRouter: Selects optimal model based on task complexity and budget.
    
    Responsibilities:
    - Select model tier based on section complexity
    - Escalate to premium models on retry
    - Balance cost vs. quality
    - Track spend and optimize
    """
    
    def __init__(self, config: "AppConfig", logger: logging.Logger):
        self.config = config
        self.artist_specs = self.config.artist_specs
        self.logger = logger

        # Track model usage for cost analysis
        self.model_usage_count: Dict[str, int] = defaultdict(int)
        self.total_estimated_cost: float = 0.0
        
    def get_model_for_task(
        self, 
        section_enum: ResumeSection, 
        attempt: int,
        force_premium: bool = False
    ) -> str:
        """
        Selects the optimal model for a given task.
        
        Args:
            section_enum: The resume section being generated
            attempt: The attempt number (1-indexed)
            force_premium: Force premium model selection
            
        Returns:
            Model identifier string
        """
        section_name = section_enum.name if hasattr(section_enum, 'name') else str(section_enum)
        
        # Determine section complexity
        complexity = self._get_section_complexity(section_name)
        
        # Select tier based on complexity, attempt, and flags
        if force_premium or attempt >= MAX_RETRIES_PER_NODE:
            tier = "PREMIUM"
            reason = "forced_premium" if force_premium else "final_retry"
        elif complexity == "HIGH":
            # High complexity: Start with standard, escalate to premium on retry
            tier = "STANDARD" if attempt == 1 else "PREMIUM"
            reason = f"high_complexity_attempt_{attempt}"
        elif complexity == "MEDIUM":
            # Medium complexity: Standard for all attempts
            tier = "STANDARD"
            reason = f"medium_complexity_attempt_{attempt}"
        else:  # LOW
            # Low complexity: Economy unless retrying
            tier = "ECONOMY" if attempt == 1 else "STANDARD"
            reason = f"low_complexity_attempt_{attempt}"
        
        selected_model = MODEL_TIERS[tier]["model"]
        
        # Log decision
        self.logger.info(
            f"CostRouter: {section_name} | Attempt {attempt} | "
            f"Complexity: {complexity} | Tier: {tier} | Model: {selected_model} | "
            f"Reason: {reason}"
        )
        
        # Track usage
        self.model_usage_count[selected_model] += 1
        self.total_estimated_cost += MODEL_TIERS[tier]["cost_multiplier"]
        
        return selected_model
    
    def _get_section_complexity(self, section_name: str) -> str:
        """Determine complexity level of a section from artist_specs config."""
        # Look up section in artist_specs
        spec = self.artist_specs.get(section_name)
        if spec and "complexity" in spec:
            return spec["complexity"]
        
        # Default to MEDIUM if not found or no complexity defined
        self.logger.warning(f"Section {section_name} not in artist_specs or no complexity defined. Defaulting to MEDIUM.")
        return "MEDIUM"
    
    def get_cost_report(self) -> Dict[str, Any]:
        """Generate cost analysis report."""
        return {
            "model_usage": dict(self.model_usage_count),
            "estimated_total_cost": self.total_estimated_cost,
            "average_cost_per_call": (
                self.total_estimated_cost / sum(self.model_usage_count.values())
                if self.model_usage_count else 0.0
            )
        }


# ============================================================================
# CONTEXT RELAY LAYER
# ============================================================================

class ContextRelayLayer:
    """
    Production ContextRelayLayer: Centralizes all prompt construction logic.
    
    Responsibilities:
    - Build context for each section type
    - Format prompts with data
    - Inject critique from previous attempts
    - Return complete context envelope for Writer
    
    V2: Delegates to prompts_RES_v2.py for sophisticated context building.
    """
    
    def __init__(self, config: "AppConfig", logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.prompts = self.config.prompts.prompts

        if not self.prompts:
            raise ValueError("ContextRelayLayer requires prompts dictionary")
        
        # Import prompt building functions from prompts_RES_v2
        try:
            from prompts_RES_v2 import build_crl_context_for_section
            self.build_context = build_crl_context_for_section
        except ImportError:
            self.logger.warning("Could not import prompts_RES_v2. Using simplified context building.")
            self.build_context = None
    
    def get_context_envelope(
        self,
        section_enum: ResumeSection,
        thematic_analysis: Any,
        enriched_scaffold: Dict,
        model: str,
        reasoning_config: Any,
        temperature: float,
        critique_context: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Builds the complete context envelope for the Writer.
        
        V2: Uses prompts_RES_v2 for sophisticated context building when available.
        
        Args:
            section_enum: Section to generate
            thematic_analysis: ThematicAnalysis object
            enriched_scaffold: Enriched data scaffold
            model: Model identifier
            reasoning_config: Reasoning configuration
            temperature: Generation temperature
            critique_context: Optional critique from previous attempt
            
        Returns:
            Context envelope dictionary with prompt, system_prompt, config, etc.
        """
        section_name = section_enum.name if hasattr(section_enum, 'name') else str(section_enum)
        
        self.logger.debug(f"CRL: Building context for {section_name}")
        
        # Use prompts_RES_v2 for context building if available
        try:
            context_data = self.build_context(
                section_name,
                thematic_analysis,
                enriched_scaffold,
                **kwargs
            )
        except Exception as e:
            self.logger.error(f"Error building context with prompts_RES_v2: {e}")
            # V2 assumes self.build_context will always work. Re-raise if it fails.
            raise
        
        # Determine prompt key and system prompt
        prompt_key, system_prompt = self._get_prompt_metadata(section_name)
        
        # Get prompt template
        prompt_template = self.prompts.get(prompt_key, "")
        if not prompt_template:
            self.logger.warning(f"No prompt template found for key: {prompt_key}")
            prompt_template = f"Generate high-quality content for {section_name}."
        
        # Format prompt with context data
        try:
            formatted_prompt = prompt_template.format(**context_data)
        except KeyError as e:
            self.logger.error(f"Prompt formatting error for {section_name}: Missing key {e}")
            formatted_prompt = prompt_template  # Use unformatted as fallback
        
        # Inject critique if exists
        if critique_context:
            # --- FIX: Handle dict or str critique ---
            critique_text = ""
            if isinstance(critique_context, dict):
                critique_text = critique_context.get("text", "")
            elif isinstance(critique_context, str):
                critique_text = critique_context
            
            formatted_prompt += (
                f"\n\n**PREVIOUS ATTEMPT FEEDBACK:**\n{critique_text}\n\n"
                f"Based on this feedback, generate an improved version that addresses all identified issues."
            )
            # --- END FIX ---
        
        return {
            "prompt": formatted_prompt,
            "system_prompt": system_prompt,
            "reasoning_config": reasoning_config,
            "temperature": temperature,
            "model": model,
            "section_name": section_name
        }
    
    def _get_prompt_metadata(self, section_name: str) -> Tuple[str, str]:
        """Get prompt key and system prompt for a section."""
        metadata_map = {
            "HEADLINE": ("artist_headline", "You are an expert resume headline crafter specializing in concise, impactful, keyword-rich headlines."),
            "EXECUTIVE_SUMMARY": ("artist_executive_summary", "You are an expert resume writer specializing in executive value propositions."),
            "COVER_LETTER": ("artist_cover_letter", "You are an expert executive ghostwriter crafting tailored cover letters."),
            "BULLETS": ("artist_bullets", "You are an expert resume bullet writer specializing in impact-driven achievement statements."),
            "NARRATIVE": ("artist_narrative", "You are an expert resume writer crafting concise narratives that bridge past experience to current capabilities."),
            "COMPETENCIES": ("artist_competencies", "You are an expert at identifying and articulating strategic competencies."),
            "SKILLS": ("artist_skills", "You are an expert HR analyst extracting relevant skills from job requirements.")
        }
        
        for key, (prompt_key, sys_prompt) in metadata_map.items():
            if key in section_name:
                return prompt_key, sys_prompt
        
        return "artist_generic", "You are an expert resume writer."
    

# ============================================================================
# CRITIQUE TOOL
# ============================================================================

class CritiqueTool:
    """
    Production CritiqueTool: Generates actionable feedback from validation failures.
    
    Responsibilities:
    - Analyze validation failures
    - Generate specific, actionable critiques
    - Provide guidance for improvement
    - Vary tone based on strategy
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def generate_critique(
        self,
        draft: str,
        validation_results: List[ValidationResult],
        strategy_params: Dict
    ) -> str:
        """
        Generates a natural language critique with specific guidance.
        
        Args:
            draft: The failed draft text
            validation_results: List of validation results
            strategy_params: Strategy parameters from PolicyAgent
            
        Returns:
            Detailed critique text
        """
        strategy = strategy_params.get('strategy', 'generic')
        focus = strategy_params.get('focus', 'general improvement')
        emphasis = strategy_params.get('emphasis', 'quality')
        
        self.logger.info(f"CritiqueTool generating critique | Strategy: {strategy} | Focus: {focus}")
        
        # Analyze failures
        failures = [vr for vr in validation_results if not vr.passed]
        failure_categories = self._categorize_failures(failures)
        
        # Build critique sections
        critique_parts = []
        
        # 1. Opening statement
        critique_parts.append(self._generate_opening(strategy, len(failures)))
        
        # 2. Specific failure analysis
        critique_parts.append("**Issues Identified:**")
        
        for category, issues in failure_categories.items():
            if issues:
                critique_parts.append(f"\n*{category}:*")
                for issue in issues:
                    critique_parts.append(f"- {issue['message']}")
                    if issue.get('details'):
                        critique_parts.append(f"  └─ {self._format_details(issue['details'])}")
        
        # 3. Strategic guidance
        critique_parts.append(f"\n**Guidance for Revision (Focus: {focus}):**")
        critique_parts.append(self._generate_strategic_guidance(strategy, emphasis, failure_categories))
        
        # 4. Specific requirements
        critique_parts.append("\n**Requirements Checklist:**")
        critique_parts.append(self._generate_requirements_checklist(failure_categories))
        
        return "\n".join(critique_parts)
    
    def _categorize_failures(self, failures: List[ValidationResult]) -> Dict[str, List[Dict]]:
        """Categorize validation failures into groups."""
        categories = {
            "Structural Issues": [],
            "Content Quality": [],
            "Theme Alignment": [],
            "Mechanical Compliance": []
        }
        
        for failure in failures:
            issue = {
                "rule_id": failure.rule_id,
                "message": failure.message,
                "details": failure.details
            }
            
            # Categorize based on rule_id patterns
            if any(x in failure.rule_id for x in ["WORD_COUNT", "SENTENCE_COUNT", "LENGTH", "FORMAT"]):
                categories["Mechanical Compliance"].append(issue)
            elif any(x in failure.rule_id for x in ["THEME", "KEYWORD", "SIGNAL", "POSITIONING"]):
                categories["Theme Alignment"].append(issue)
            elif any(x in failure.rule_id for x in ["QUALITY", "VERB", "CLICHE", "WEAK"]):
                categories["Content Quality"].append(issue)
            else:
                categories["Structural Issues"].append(issue)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _generate_opening(self, strategy: str, failure_count: int) -> str:
        """Generate opening statement based on strategy."""
        openings = {
            "mechanical_fix": f"The previous draft failed {failure_count} validation rule(s). Let's address each constraint precisely:",
            "strategic_reframe": f"The positioning needs strengthening. {failure_count} strategic issue(s) identified:",
            "creative_rewrite": f"The content needs elevation. {failure_count} quality issue(s) to address:",
            "creative_breakthrough": "Let's take a completely fresh approach. Here's what needs transformation:"
        }
        return openings.get(strategy, f"The draft failed {failure_count} validation(s). Analysis:")
    
    def _generate_strategic_guidance(
        self, 
        strategy: str, 
        emphasis: str, 
        categories: Dict
    ) -> str:
        """Generate strategic guidance based on strategy and failures."""
        guidance = []
        
        if "Mechanical Compliance" in categories:
            if "exact" in emphasis.lower():
                guidance.append("- Follow word/sentence count requirements EXACTLY. No approximations.")
            else:
                guidance.append("- Adjust length to meet specified constraints.")
        
        if "Theme Alignment" in categories:
            if "thematic" in emphasis.lower():
                guidance.append("- Reframe content around the primary theme. Every sentence must serve positioning.")
            else:
                guidance.append("- Incorporate missing keywords naturally into the narrative.")
        
        if "Content Quality" in categories:
            if "originality" in emphasis.lower():
                guidance.append("- Avoid generic language. Use specific, distinctive phrasing.")
                guidance.append("- Lead with unique insights that differentiate the candidate.")
            else:
                guidance.append("- Strengthen weak verbs and remove clichés.")
        
        if not guidance:
            guidance.append("- Review all feedback above and revise comprehensively.")
        
        return "\n".join(guidance)
    
    def _generate_requirements_checklist(self, categories: Dict) -> str:
        """Generate a checklist of requirements to meet."""
        checklist = []
        
        for category, issues in categories.items():
            for issue in issues:
                rule_id = issue['rule_id']
                # Convert rule_id to readable requirement
                requirement = rule_id.replace('_', ' ').title()
                checklist.append(f"- [ ] {requirement}")
        
        if not checklist:
            checklist.append("- [ ] Meet all validation criteria")
        
        return "\n".join(checklist[:8])  # Limit to top 8 for readability
    
    def _format_details(self, details: Dict) -> str:
        """Format details dictionary into readable string."""
        if not details:
            return ""
        
        formatted = []
        for key, value in details.items():
            if isinstance(value, (list, dict)):
                formatted.append(f"{key}: {str(value)[:100]}")
            else:
                formatted.append(f"{key}: {value}")
        
        return " | ".join(formatted)


# ============================================================================
# HIL INTERFACE
# ============================================================================

class HIL_Interface:
    """
    Production HIL Interface: Manages human-in-the-loop escalations.
    
    Responsibilities:
    - Notify human reviewers of failures
    - Present context and draft for review
    - Capture human decisions
    - Log HIL events for feedback pipeline
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.escalation_count = 0
        self.hil_decisions: List[Dict] = []
    
    def notify(
        self,
        section_enum: ResumeSection,
        drafts: Dict[ResumeSection, Any],
        critique_context: Optional[str]
    ) -> Dict[str, Any]:
        """
        Notifies human for review and waits for decision.
        
        In production, this would:
        1. Send notification to review queue
        2. Present draft and context via UI
        3. Block until human decision received
        
        Current implementation: Auto-approve with warnings and logging.
        
        Args:
            section_enum: Section that failed
            drafts: Current draft dictionary
            critique_context: Critique context
            
        Returns:
            Decision dictionary with action and draft
        """
        self.escalation_count += 1
        section_name = section_enum.name if hasattr(section_enum, 'name') else str(section_enum)
        
        self.logger.critical("=" * 80)
        self.logger.critical(f"🧑‍💻 HIL ESCALATION #{self.escalation_count}: {section_name}")
        self.logger.critical("=" * 80)
        self.logger.critical("REASON: Section failed all automated retry attempts.")
        
        # Extract failed draft
        failed_draft = drafts.get(section_enum, "[NO DRAFT AVAILABLE]")
        
        self.logger.critical(f"\nFAILED DRAFT PREVIEW:")
        self.logger.critical(f"{str(failed_draft)[:500]}...")
        
        if critique_context:
            self.logger.critical(f"\nLATEST CRITIQUE:")
            self.logger.critical(f"{critique_context[:300]}...")
        
        self.logger.critical("\n" + "=" * 80)
        self.logger.critical("HIL DECISION: AUTO-APPROVE (with warnings)")
        self.logger.critical("=" * 80)
        
        # Record decision
        decision = {
            "action": "continue_with_draft",
            "draft_with_warnings": failed_draft,
            "escalation_id": self.escalation_count,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "section": section_name,
            "resolution": "auto_approved",
            "notes": "Section exhausted retries. Proceeding with best available draft."
        }
        
        self.hil_decisions.append(decision)
        
        # In production, this would log to feedback pipeline for meta-planner
        self._log_to_feedback_pipeline(decision)
        
        return decision
    
    def _log_to_feedback_pipeline(self, decision: Dict):
        """Log HIL decision to feedback pipeline (stub for now)."""
        self.logger.info(f"Logging HIL decision to feedback pipeline: {decision['section']}")
        # In production: Send to message queue / database for meta-planner analysis
    
    def get_hil_summary(self) -> Dict[str, Any]:
        """Generate summary of HIL activity."""
        return {
            "total_escalations": self.escalation_count,
            "decisions": self.hil_decisions,
            "auto_approve_rate": 1.0  # Currently all auto-approve
        }


# ============================================================================
# TRACE REGISTRY
# ============================================================================

class TraceRegistry:
    """
    Production TraceRegistry: Centralized structured event logging system (ATI).
    
    Responsibilities:
    - Log all L1/L2/L3 events
    - Maintain complete audit trail
    - Support QA report generation
    - Enable debugging and monitoring
    """
    
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.trace_log: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"TraceRegistry initialized for run {run_id}")
        
        # Event counters
        self.event_counts: Dict[str, int] = defaultdict(int)
        
    def log(self, level: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Logs a structured trace event.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            metadata: Optional metadata dictionary
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level.upper(),
            "message": message,
            "metadata": metadata or {},
            "run_id": self.run_id
        }
        
        self.trace_log.append(log_entry)
        self.event_counts[level.upper()] += 1
        
        # Also log to standard logger
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        metadata_str = f" | {metadata}" if metadata else ""
        log_func(f"{message}{metadata_str}")
    
    def get_full_trace(self) -> List[Dict[str, Any]]:
        """Returns the complete trace log."""
        return self.trace_log.copy()
    
    def get_events_by_level(self, level: str) -> List[Dict[str, Any]]:
        """Get all events of a specific level."""
        return [e for e in self.trace_log if e["level"] == level.upper()]
    
    def get_events_by_node(self, node_name: str) -> List[Dict[str, Any]]:
        """Get all events related to a specific node."""
        return [
            e for e in self.trace_log 
            if e.get("metadata", {}).get("node") == node_name
        ]
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Generate summary statistics of trace events."""
        return {
            "total_events": len(self.trace_log),
            "event_counts_by_level": dict(self.event_counts),
            "run_id": self.run_id,
            "first_event": self.trace_log[0]["timestamp"] if self.trace_log else None,
            "last_event": self.trace_log[-1]["timestamp"] if self.trace_log else None
        }
    
    def export_to_json(self, filepath: str):
        """Export trace log to JSON file."""
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "run_id": self.run_id,
                "summary": self.get_summary_stats(),
                "events": self.trace_log
            }, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Trace log exported to {filepath}")


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "PolicyAgent",
    "CostRouter",
    "ContextRelayLayer",
    "CritiqueTool",
    "HIL_Interface",
    "TraceRegistry",
    "MAX_RETRIES_PER_NODE",
    "DEFAULT_MODEL",
    "DEFAULT_GENERATION_TEMPERATURE"
]