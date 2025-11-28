# File: governor_v3_8.py
# Version: 3.8.0 - V3.8 Agentic Architecture (Complete Migration)
# Complete implementations of all v3.8 agents

import logging
import json
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict
from datetime import datetime
from enum import Enum

# Import models for type hints
try:
    from models_RES import ResumeSection, ValidationResult, ThematicAnalysis, GateDecision
except ImportError:
    # Fallback for standalone testing
    ResumeSection = Any
    ValidationResult = Any
    ThematicAnalysis = Any
    
    class GateDecision(Enum):
        PROCEED = "PROCEED"
        HALT = "HALT"
        RETRY = "RETRY"

# Import temperature default from config (single source of truth)
try:
    from config_RES_v3_8 import (
        CONFIG, DATA_DIR, OUTPUT_DIR, 
        DEFAULT_GENERATION_TEMPERATURE,
        GEMINI_PREMIUM_MODEL, CLAUDE_PREMIUM_MODEL, OPENAI_SYNTHESIS_MODEL,
        DEFAULT_MAX_RETRIES
    )
except ImportError:
    # Fallback if run standalone
    DEFAULT_GENERATION_TEMPERATURE = 1.0
    DEFAULT_MAX_RETRIES = 3
    CONFIG = None
    DATA_DIR = None
    OUTPUT_DIR = None
    GEMINI_PREMIUM_MODEL = "gemini-2.5-pro"
    CLAUDE_PREMIUM_MODEL = "claude-sonnet-3.5"
    OPENAI_SYNTHESIS_MODEL = "gpt-4-turbo"

# ============================================================================
# CONSTANTS
# ============================================================================

MAX_RETRIES_PER_NODE = DEFAULT_MAX_RETRIES
DEFAULT_MODEL = "gemini-2.5-pro"

# Model tier definitions with cost/performance characteristics
MODEL_TIERS = {
    "premium": {
        "models": [GEMINI_PREMIUM_MODEL, CLAUDE_PREMIUM_MODEL],
        "cost_multiplier": 3.0,
        "capability": "high",
        "use_for": ["critical_sections", "final_polish", "complex_reasoning"]
    },
    "standard": {
        "models": ["gemini-2.0-pro", "claude-haiku"],
        "cost_multiplier": 1.0,
        "capability": "medium",
        "use_for": ["drafts", "validation", "simple_generation"]
    },
    "economy": {
        "models": ["gemini-1.5-flash", "gpt-3.5-turbo"],
        "cost_multiplier": 0.3,
        "capability": "low",
        "use_for": ["classification", "extraction", "simple_tasks"]
    }
}


class PolicyAgent:
    """
    Enforces workflow policies, gates, and business rules.
    Manages circuit breakers and failure thresholds.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Policy configurations
        self.max_retries = MAX_RETRIES_PER_NODE
        self.failure_thresholds = {
            ResumeSection.SUMMARY: 3,
            ResumeSection.EXPERIENCE: 5,
            ResumeSection.SKILLS: 3,
            ResumeSection.EDUCATION: 2,
            ResumeSection.ACHIEVEMENTS: 3
        }
        
        # Circuit breaker states
        self.circuit_states = defaultdict(lambda: "CLOSED")
        self.circuit_failure_counts = defaultdict(int)
        self.circuit_last_failure = {}
        
        # Gate configurations
        self.gate_thresholds = {
            "signal_quality": 0.65,
            "validation_pass_rate": 0.80,
            "critical_sections_complete": 1.0
        }
    
    def evaluate_gate(self, gate_name: str, metrics: Dict[str, float], 
                     threshold: Optional[float] = None) -> 'GateDecision':
        """
        Evaluate a quality gate based on metrics.
        
        Args:
            gate_name: Name of the gate being evaluated
            metrics: Dict of metric_name -> value
            threshold: Optional override threshold
            
        Returns:
            GateDecision enum value
        """
        if threshold is None:
            threshold = self.gate_thresholds.get(gate_name.lower(), 0.7)
        
        # Calculate composite score if multiple metrics
        if len(metrics) > 1:
            score = sum(metrics.values()) / len(metrics)
        else:
            score = next(iter(metrics.values()))
        
        self.logger.info(f"Gate '{gate_name}' evaluation: score={score:.3f}, threshold={threshold}")
        
        if score >= threshold:
            return GateDecision.PROCEED
        elif score >= threshold * 0.8:  # Within 20% of threshold
            return GateDecision.RETRY
        else:
            return GateDecision.HALT
    
    def check_circuit_breaker(self, section: ResumeSection) -> bool:
        """
        Check if circuit breaker is open for a section.
        
        Returns:
            True if circuit is OPEN (blocking), False if CLOSED (allowing)
        """
        state = self.circuit_states[section]
        
        if state == "OPEN":
            # Check if cooldown period has passed (5 minutes)
            last_failure = self.circuit_last_failure.get(section)
            if last_failure:
                elapsed = (datetime.now() - last_failure).total_seconds()
                if elapsed > 300:  # 5 minute cooldown
                    self.logger.info(f"Circuit breaker for {section} moving to HALF_OPEN")
                    self.circuit_states[section] = "HALF_OPEN"
                    return False
            return True
        
        return False
    
    def record_failure(self, section: ResumeSection, error: str):
        """Record a failure and potentially trip circuit breaker."""
        self.circuit_failure_counts[section] += 1
        self.circuit_last_failure[section] = datetime.now()
        
        threshold = self.failure_thresholds.get(section, 3)
        
        if self.circuit_failure_counts[section] >= threshold:
            self.logger.warning(f"Circuit breaker OPENED for {section} after {threshold} failures")
            self.circuit_states[section] = "OPEN"
    
    def record_success(self, section: ResumeSection):
        """Record a success and potentially reset circuit breaker."""
        if self.circuit_states[section] == "HALF_OPEN":
            self.logger.info(f"Circuit breaker for {section} moving to CLOSED")
            self.circuit_states[section] = "CLOSED"
            self.circuit_failure_counts[section] = 0
    
    def should_retry(self, section: ResumeSection, attempt: int) -> bool:
        """
        Determine if a section should be retried.
        
        Args:
            section: Resume section being generated
            attempt: Current attempt number (1-indexed)
            
        Returns:
            True if should retry, False otherwise
        """
        # Check circuit breaker first
        if self.check_circuit_breaker(section):
            self.logger.warning(f"Circuit breaker OPEN for {section}, blocking retry")
            return False
        
        # Check retry limit
        if attempt >= self.max_retries:
            self.logger.warning(f"Max retries ({self.max_retries}) reached for {section}")
            return False
        
        return True
    
    def get_policy_recommendation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get policy-based recommendations for workflow decisions.
        
        Args:
            context: Current workflow context
            
        Returns:
            Dict with recommendations
        """
        recommendations = {
            "proceed": True,
            "warnings": [],
            "suggestions": []
        }
        
        # Check for critical validation failures
        if context.get("critical_failures", 0) > 0:
            recommendations["proceed"] = False
            recommendations["warnings"].append("Critical validation failures detected")
        
        # Check signal quality
        signal_quality = context.get("signal_quality", 0)
        if signal_quality < self.gate_thresholds["signal_quality"]:
            recommendations["suggestions"].append(
                f"Signal quality ({signal_quality:.2f}) below recommended threshold"
            )
        
        # Check retry patterns
        retry_count = context.get("retry_count", 0)
        if retry_count > 2:
            recommendations["warnings"].append(f"High retry count ({retry_count}) detected")
        
        return recommendations


class CostRouter:
    """
    Routes requests to appropriate models based on cost/performance trade-offs.
    Implements intelligent model selection and fallback strategies.
    """
    
    def __init__(self, config: Any = None, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.config = config or CONFIG
        
        # Track costs per run
        self.cost_tracking = defaultdict(float)
        self.model_usage = defaultdict(int)
        
        # Model selection strategies
        self.section_model_mapping = {
            ResumeSection.SUMMARY: "premium",
            ResumeSection.EXPERIENCE: "premium", 
            ResumeSection.SKILLS: "standard",
            ResumeSection.EDUCATION: "economy",
            ResumeSection.ACHIEVEMENTS: "standard"
        }
        
        # Fallback chains
        self.fallback_chains = {
            GEMINI_PREMIUM_MODEL: ["gemini-2.0-pro", "gemini-1.5-flash"],
            CLAUDE_PREMIUM_MODEL: ["claude-haiku", "gpt-4-turbo"],
            "gemini-2.0-pro": ["gemini-1.5-flash", "gpt-3.5-turbo"]
        }
    
    def select_model(self, task_type: str, priority: str = "standard",
                    context: Optional[Dict] = None) -> str:
        """
        Select the optimal model for a task.
        
        Args:
            task_type: Type of task (e.g., "generation", "validation")
            priority: Priority level ("economy", "standard", "premium")
            context: Optional context for decision making
            
        Returns:
            Model identifier string
        """
        # Override priority based on task requirements
        if context:
            if context.get("is_final_draft", False):
                priority = "premium"
            elif context.get("is_validation", False):
                priority = "economy"
        
        # Get tier configuration
        tier = MODEL_TIERS.get(priority, MODEL_TIERS["standard"])
        
        # Select primary model from tier
        model = tier["models"][0] if tier["models"] else DEFAULT_MODEL
        
        self.logger.info(f"Selected model '{model}' for task '{task_type}' with priority '{priority}'")
        
        # Track selection
        self.model_usage[model] += 1
        
        return model
    
    def get_fallback_model(self, failed_model: str) -> Optional[str]:
        """
        Get fallback model when primary fails.
        
        Args:
            failed_model: Model that failed
            
        Returns:
            Fallback model identifier or None
        """
        fallback_chain = self.fallback_chains.get(failed_model, [])
        
        if fallback_chain:
            fallback = fallback_chain[0]
            self.logger.info(f"Using fallback model '{fallback}' after '{failed_model}' failed")
            return fallback
        
        return None
    
    def estimate_cost(self, model: str, tokens: int) -> float:
        """
        Estimate cost for a model usage.
        
        Args:
            model: Model identifier
            tokens: Estimated token count
            
        Returns:
            Estimated cost in dollars
        """
        # Simplified cost estimation (would use actual pricing in production)
        base_costs = {
            GEMINI_PREMIUM_MODEL: 0.01,  # per 1k tokens
            CLAUDE_PREMIUM_MODEL: 0.015,
            "gemini-2.0-pro": 0.005,
            "claude-haiku": 0.003,
            "gemini-1.5-flash": 0.001,
            "gpt-3.5-turbo": 0.002,
            "gpt-4-turbo": 0.01
        }
        
        cost_per_1k = base_costs.get(model, 0.005)
        estimated_cost = (tokens / 1000) * cost_per_1k
        
        # Track cumulative cost
        self.cost_tracking[model] += estimated_cost
        
        return estimated_cost
    
    def get_cost_report(self) -> Dict[str, Any]:
        """
        Get cost report for current run.
        
        Returns:
            Dict with cost breakdown
        """
        total_cost = sum(self.cost_tracking.values())
        
        return {
            "total_cost": total_cost,
            "cost_by_model": dict(self.cost_tracking),
            "usage_by_model": dict(self.model_usage),
            "average_cost_per_request": total_cost / max(sum(self.model_usage.values()), 1)
        }
    
    def optimize_for_budget(self, remaining_budget: float, 
                          remaining_tasks: List[str]) -> Dict[str, str]:
        """
        Optimize model selection for remaining budget.
        
        Args:
            remaining_budget: Budget remaining in dollars
            remaining_tasks: List of remaining task identifiers
            
        Returns:
            Dict mapping task -> model
        """
        if not remaining_tasks:
            return {}
        
        budget_per_task = remaining_budget / len(remaining_tasks)
        
        task_model_map = {}
        for task in remaining_tasks:
            if budget_per_task > 0.01:
                model = self.select_model(task, priority="premium")
            elif budget_per_task > 0.005:
                model = self.select_model(task, priority="standard")
            else:
                model = self.select_model(task, priority="economy")
            
            task_model_map[task] = model
        
        return task_model_map


class ContextRelayLayer:
    """
    Manages context passing between agents and workflow phases.
    Implements context compression and relevance filtering.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Context storage
        self.global_context = {}
        self.phase_contexts = defaultdict(dict)
        self.agent_memories = defaultdict(list)
        
        # Context size limits
        self.max_context_size = 8000  # tokens
        self.max_memory_items = 10
    
    def update_global_context(self, key: str, value: Any):
        """Update global context available to all agents."""
        self.global_context[key] = value
        self.logger.debug(f"Updated global context: {key}")
    
    def update_phase_context(self, phase: str, context: Dict[str, Any]):
        """Update context for a specific phase."""
        self.phase_contexts[phase].update(context)
        self.logger.debug(f"Updated phase context for: {phase}")
    
    def add_agent_memory(self, agent: str, memory_item: Any):
        """Add memory item for an agent."""
        self.agent_memories[agent].append({
            "timestamp": datetime.now().isoformat(),
            "item": memory_item
        })
        
        # Trim to max items
        if len(self.agent_memories[agent]) > self.max_memory_items:
            self.agent_memories[agent] = self.agent_memories[agent][-self.max_memory_items:]
    
    def get_relevant_context(self, agent: str, phase: str, 
                           task_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get relevant context for an agent's current task.
        
        Args:
            agent: Agent identifier
            phase: Current phase
            task_type: Optional task type for filtering
            
        Returns:
            Filtered context dictionary
        """
        context = {
            "global": self._filter_global_context(task_type),
            "phase": self.phase_contexts.get(phase, {}),
            "agent_memory": self.agent_memories.get(agent, [])[-5:],  # Last 5 items
            "timestamp": datetime.now().isoformat()
        }
        
        # Add task-specific context
        if task_type:
            context["task_hints"] = self._get_task_hints(task_type)
        
        return context
    
    def _filter_global_context(self, task_type: Optional[str]) -> Dict[str, Any]:
        """Filter global context based on relevance."""
        # If no task type, return essential items only
        if not task_type:
            essential_keys = ["run_id", "job_title", "company_name", "signal_quality"]
            return {k: v for k, v in self.global_context.items() if k in essential_keys}
        
        # Task-specific filtering
        if "validation" in task_type.lower():
            relevant_keys = ["validation_rules", "constraints", "jd_requirements"]
        elif "generation" in task_type.lower():
            relevant_keys = ["thematic_analysis", "style_guide", "target_keywords"]
        else:
            relevant_keys = ["run_id", "job_title", "company_name"]
        
        return {k: v for k, v in self.global_context.items() 
                if any(rk in k.lower() for rk in relevant_keys)}
    
    def _get_task_hints(self, task_type: str) -> List[str]:
        """Get hints for specific task types."""
        hints_map = {
            "summary_generation": [
                "Focus on quantifiable achievements",
                "Align with primary theme",
                "Keep under 4 sentences"
            ],
            "experience_generation": [
                "Use STAR format for bullets",
                "Include metrics and results",
                "Highlight relevant skills"
            ],
            "validation": [
                "Check against JD requirements",
                "Verify factual accuracy",
                "Ensure consistency across sections"
            ]
        }
        
        return hints_map.get(task_type, [])
    
    def compress_context(self, context: Dict[str, Any], 
                        max_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Compress context to fit size limits.
        
        Args:
            context: Context to compress
            max_size: Maximum size in tokens (estimate)
            
        Returns:
            Compressed context
        """
        max_size = max_size or self.max_context_size
        
        # Estimate current size (rough approximation)
        context_str = json.dumps(context, default=str)
        estimated_tokens = len(context_str) / 4  # Rough token estimate
        
        if estimated_tokens <= max_size:
            return context
        
        # Compression strategies
        compressed = {}
        
        # 1. Keep only essential global context
        if "global" in context:
            compressed["global"] = {
                k: v for k, v in context["global"].items()
                if k in ["run_id", "job_title", "company_name"]
            }
        
        # 2. Truncate memories
        if "agent_memory" in context:
            compressed["agent_memory"] = context["agent_memory"][-3:]
        
        # 3. Summarize phase context
        if "phase" in context:
            phase_keys = list(context["phase"].keys())[:5]  # Keep top 5 keys
            compressed["phase"] = {k: context["phase"][k] for k in phase_keys}
        
        self.logger.info(f"Compressed context from ~{estimated_tokens:.0f} to ~{len(json.dumps(compressed))/4:.0f} tokens")
        
        return compressed


class CritiqueTool:
    """
    Provides critique and feedback mechanisms for generated content.
    Implements multi-perspective evaluation.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Critique perspectives
        self.perspectives = [
            "technical_accuracy",
            "relevance_to_jd", 
            "impact_and_results",
            "keyword_optimization",
            "readability"
        ]
        
        # Scoring weights
        self.weights = {
            "technical_accuracy": 0.25,
            "relevance_to_jd": 0.30,
            "impact_and_results": 0.20,
            "keyword_optimization": 0.15,
            "readability": 0.10
        }
    
    def critique_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Critique content from multiple perspectives.
        
        Args:
            content: Content to critique
            context: Context including JD, requirements, etc.
            
        Returns:
            Critique results with scores and feedback
        """
        critiques = {}
        
        # Technical accuracy
        critiques["technical_accuracy"] = self._evaluate_technical_accuracy(content, context)
        
        # Relevance to JD
        critiques["relevance_to_jd"] = self._evaluate_jd_relevance(content, context)
        
        # Impact and results
        critiques["impact_and_results"] = self._evaluate_impact(content)
        
        # Keyword optimization
        critiques["keyword_optimization"] = self._evaluate_keywords(content, context)
        
        # Readability
        critiques["readability"] = self._evaluate_readability(content)
        
        # Calculate overall score
        overall_score = sum(
            critiques[p]["score"] * self.weights[p] 
            for p in self.perspectives
        )
        
        return {
            "overall_score": overall_score,
            "critiques": critiques,
            "recommendations": self._generate_recommendations(critiques),
            "pass_threshold": overall_score >= 0.75
        }
    
    def _evaluate_technical_accuracy(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate technical accuracy of content."""
        score = 0.85  # Placeholder - would use actual evaluation
        
        issues = []
        if "years" in content.lower() and not any(char.isdigit() for char in content):
            issues.append("Missing specific years/dates")
            score -= 0.1
        
        return {
            "score": max(score, 0),
            "issues": issues,
            "feedback": "Technical details are mostly accurate" if score > 0.7 else "Needs more specific technical details"
        }
    
    def _evaluate_jd_relevance(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate relevance to job description."""
        jd_keywords = context.get("jd_keywords", [])
        if not jd_keywords:
            return {"score": 0.5, "issues": ["No JD keywords provided"], "feedback": "Unable to assess JD relevance"}
        
        # Count keyword matches
        content_lower = content.lower()
        matches = sum(1 for keyword in jd_keywords if keyword.lower() in content_lower)
        
        relevance_score = min(matches / max(len(jd_keywords), 1), 1.0)
        
        return {
            "score": relevance_score,
            "matched_keywords": matches,
            "total_keywords": len(jd_keywords),
            "feedback": f"Matched {matches}/{len(jd_keywords)} key requirements"
        }
    
    def _evaluate_impact(self, content: str) -> Dict[str, Any]:
        """Evaluate impact and results focus."""
        impact_indicators = ["increased", "improved", "reduced", "saved", "generated", 
                            "delivered", "achieved", "%", "$", "roi"]
        
        impact_count = sum(1 for indicator in impact_indicators if indicator in content.lower())
        
        score = min(impact_count / 5, 1.0)  # Expect at least 5 impact indicators
        
        return {
            "score": score,
            "impact_indicators_found": impact_count,
            "feedback": "Strong results focus" if score > 0.6 else "Add more quantifiable achievements"
        }
    
    def _evaluate_keywords(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate keyword optimization."""
        target_keywords = context.get("target_keywords", [])
        
        if not target_keywords:
            return {"score": 0.5, "feedback": "No target keywords specified"}
        
        content_lower = content.lower()
        keyword_density = {}
        
        for keyword in target_keywords:
            count = content_lower.count(keyword.lower())
            keyword_density[keyword] = count
        
        # Optimal density: 1-3 mentions per keyword
        optimal_keywords = sum(1 for count in keyword_density.values() if 1 <= count <= 3)
        
        score = optimal_keywords / max(len(target_keywords), 1)
        
        return {
            "score": score,
            "keyword_density": keyword_density,
            "feedback": "Good keyword distribution" if score > 0.7 else "Optimize keyword usage"
        }
    
    def _evaluate_readability(self, content: str) -> Dict[str, Any]:
        """Evaluate readability of content."""
        sentences = content.split('.')
        words = content.split()
        
        if not sentences or not words:
            return {"score": 0, "feedback": "No content to evaluate"}
        
        avg_sentence_length = len(words) / max(len(sentences), 1)
        
        # Optimal sentence length: 15-20 words
        if 15 <= avg_sentence_length <= 20:
            score = 1.0
        elif 10 <= avg_sentence_length <= 25:
            score = 0.8
        else:
            score = 0.6
        
        return {
            "score": score,
            "avg_sentence_length": avg_sentence_length,
            "feedback": f"Average sentence length: {avg_sentence_length:.1f} words"
        }
    
    def _generate_recommendations(self, critiques: Dict[str, Dict]) -> List[str]:
        """Generate improvement recommendations based on critiques."""
        recommendations = []
        
        for perspective, critique in critiques.items():
            if critique.get("score", 0) < 0.7:
                if perspective == "technical_accuracy":
                    recommendations.append("Add more specific technical details and metrics")
                elif perspective == "relevance_to_jd":
                    recommendations.append("Increase alignment with job requirements")
                elif perspective == "impact_and_results":
                    recommendations.append("Include more quantifiable achievements")
                elif perspective == "keyword_optimization":
                    recommendations.append("Better incorporate target keywords")
                elif perspective == "readability":
                    recommendations.append("Improve sentence structure and flow")
        
        return recommendations


class HIL_Interface:
    """
    Human-in-Loop interface for manual interventions and overrides.
    Manages escalations and human feedback integration.
    """
    
    def __init__(self, trace_registry: Optional[Any] = None):
        self.trace_registry = trace_registry
        self.pending_interventions = []
        self.intervention_history = []
    
    async def request_human_intervention(self, issue_type: str, 
                                        context: Dict[str, Any],
                                        staging_buffer: Optional[Any] = None) -> Dict[str, Any]:
        """
        Request human intervention for critical issues.
        
        Args:
            issue_type: Type of issue requiring intervention
            context: Context about the issue
            staging_buffer: Current staging buffer if available
            
        Returns:
            Intervention result
        """
        intervention_request = {
            "id": f"HIL_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "issue_type": issue_type,
            "context": context,
            "requested_at": datetime.now().isoformat(),
            "status": "PENDING"
        }
        
        self.pending_interventions.append(intervention_request)
        
        if self.trace_registry:
            self.trace_registry.log("HIL_REQUEST", f"Human intervention requested for {issue_type}", context)
        
        # In production, this would integrate with a UI or notification system
        # For now, return automated response based on issue type
        response = self._generate_automated_response(issue_type, context)
        
        intervention_request["status"] = "RESOLVED"
        intervention_request["resolved_at"] = datetime.now().isoformat()
        intervention_request["resolution"] = response
        
        self.intervention_history.append(intervention_request)
        self.pending_interventions.remove(intervention_request)
        
        return response
    
    def _generate_automated_response(self, issue_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate automated response for common intervention types.
        In production, this would be replaced by actual human input.
        """
        if issue_type == "CRITICAL_VALIDATION_FAILURE":
            return {
                "action": "OVERRIDE",
                "feedback": "Proceeding with minor validation issues",
                "modifications": {}
            }
        elif issue_type == "LOW_SIGNAL_QUALITY":
            return {
                "action": "PROCEED_WITH_CAUTION",
                "feedback": "Continuing with enhanced validation",
                "modifications": {"add_extra_validation": True}
            }
        elif issue_type == "CONTENT_REJECTION":
            return {
                "action": "RETRY_WITH_MODIFICATION",
                "feedback": "Retry with adjusted parameters",
                "modifications": {"temperature": 0.7, "style": "conservative"}
            }
        else:
            return {
                "action": "PROCEED",
                "feedback": "No specific intervention required",
                "modifications": {}
            }
    
    def get_pending_interventions(self) -> List[Dict[str, Any]]:
        """Get list of pending interventions."""
        return self.pending_interventions.copy()
    
    def get_intervention_history(self) -> List[Dict[str, Any]]:
        """Get history of all interventions."""
        return self.intervention_history.copy()


class TraceRegistry:
    """
    Centralized logging and tracing for workflow execution.
    Provides structured audit trail.
    """
    
    def __init__(self, run_id: str, logger: Optional[logging.Logger] = None):
        self.run_id = run_id
        self.logger = logger or logging.getLogger(__name__)
        self.traces = []
        self.metrics = defaultdict(list)
    
    def log(self, level: str, message: str, data: Optional[Dict[str, Any]] = None):
        """
        Log a trace event.
        
        Args:
            level: Log level (INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            data: Optional structured data
        """
        trace = {
            "timestamp": datetime.now().isoformat(),
            "run_id": self.run_id,
            "level": level,
            "message": message,
            "data": data or {}
        }
        
        self.traces.append(trace)
        
        # Also log to standard logger
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(f"[{self.run_id}] {message}")
    
    def record_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Record a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for the metric
        """
        metric = {
            "timestamp": datetime.now().isoformat(),
            "value": value,
            "tags": tags or {}
        }
        
        self.metrics[metric_name].append(metric)
    
    def get_traces(self, level: Optional[str] = None, 
                  start_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get filtered traces.
        
        Args:
            level: Filter by log level
            start_time: Filter by start time
            
        Returns:
            List of trace events
        """
        filtered = self.traces
        
        if level:
            filtered = [t for t in filtered if t["level"] == level]
        
        if start_time:
            filtered = [t for t in filtered 
                       if datetime.fromisoformat(t["timestamp"]) >= start_time]
        
        return filtered
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        summary = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                numeric_values = [v["value"] for v in values]
                summary[metric_name] = {
                    "count": len(values),
                    "min": min(numeric_values),
                    "max": max(numeric_values),
                    "avg": sum(numeric_values) / len(numeric_values),
                    "latest": values[-1]["value"]
                }
        
        return summary
    
    def export_audit_trail(self) -> Dict[str, Any]:
        """Export complete audit trail."""
        return {
            "run_id": self.run_id,
            "traces": self.traces,
            "metrics": dict(self.metrics),
            "metrics_summary": self.get_metrics_summary(),
            "exported_at": datetime.now().isoformat()
        }


# Module exports
__all__ = [
    'PolicyAgent',
    'CostRouter', 
    'ContextRelayLayer',
    'CritiqueTool',
    'HIL_Interface',
    'TraceRegistry',
    'MAX_RETRIES_PER_NODE',
    'DEFAULT_MODEL',
    'MODEL_TIERS',
    'GateDecision'
]
