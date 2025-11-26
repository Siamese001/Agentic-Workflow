"""
Self-Correction Injection for resume generation quality improvement.

Provides self-correction loops and mechanisms for continuous
resume enhancement and error recovery.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

from l1.instructional_injection_v6 import InstructionalExtension, ExtensionContent


class CorrectionType(str, Enum):
    """
    Types of self-correction mechanisms for resume improvement.

    Defines correction approaches for enhanced resume quality.
    """
    
    PROMPT_REFINEMENT = "prompt_refinement"
    OUTPUT_VALIDATION = "output_validation"
    STRATEGY_ADJUSTMENT = "strategy_adjustment"
    ERROR_RECOVERY = "error_recovery"
    QUALITY_IMPROVEMENT = "quality_improvement"


@dataclass
class CorrectionRule:
    """
    Rule for triggering self-correction in resume generation.

    Ensures automated quality improvement for resume content.
    """
    
    rule_id: str
    correction_type: CorrectionType
    trigger_condition: str
    correction_action: str
    confidence_threshold: float = 0.7
    max_attempts: int = 3


@dataclass
class CorrectionAttempt:
    """
    Record of a correction attempt for resume improvement.

    Tracks quality enhancement progress for resume content optimization.
    """
    
    attempt_id: str
    original_output: str
    correction_type: CorrectionType
    correction_applied: str
    improved_output: str
    quality_score_before: float
    quality_score_after: float
    timestamp: str


class SelfCorrectionEngine:
    """Engine for applying self-correction mechanisms."""
    
    # Default correction rules
    DEFAULT_RULES = [
        CorrectionRule(
            rule_id="prompt_clarity",
            correction_type=CorrectionType.PROMPT_REFINEMENT,
            trigger_condition="output_length < 50 or contains_generic_phrases",
            correction_action="add_specific_examples_and_details",
            confidence_threshold=0.6
        ),
        CorrectionRule(
            rule_id="output_validation",
            correction_type=CorrectionType.OUTPUT_VALIDATION,
            trigger_condition="missing_required_fields or invalid_format",
            correction_action="reformat_and_add_missing_fields",
            confidence_threshold=0.8
        ),
        CorrectionRule(
            rule_id="strategy_optimization",
            correction_type=CorrectionType.STRATEGY_ADJUSTMENT,
            trigger_condition="low_relevance_score or poor_evidence_alignment",
            correction_action="adjust_strategy_based_on_evidence",
            confidence_threshold=0.7
        ),
        CorrectionRule(
            rule_id="error_recovery",
            correction_type=CorrectionType.ERROR_RECOVERY,
            trigger_condition="execution_failed or timeout_occurred",
            correction_action="fallback_to_simpler_approach",
            confidence_threshold=0.9
        ),
    ]
    
    def __init__(self, rules: Optional[List[CorrectionRule]] = None) -> None:
        """Initialize the self-correction engine."""
        self.rules = rules or self.DEFAULT_RULES
        self.correction_history: List[CorrectionAttempt] = []
        self.logger = logging.getLogger(__name__)
    
    def should_correct(
        self,
        output: str,
        context: Dict[str, Any],
        quality_score: float = 0.5
    ) -> List[CorrectionRule]:
        """
        Determine if correction should be applied based on rules.
        
        Args:
            output: Current output to evaluate
            context: Execution context
            quality_score: Quality score of the output
            
        Returns:
            List of applicable correction rules
        """
        applicable_rules = []
        
        for rule in self.rules:
            if self._evaluate_trigger(rule.trigger_condition, output, context):
                if quality_score < rule.confidence_threshold:
                    applicable_rules.append(rule)
        
        return applicable_rules
    
    def apply_correction(
        self,
        rule: CorrectionRule,
        output: str,
        context: Dict[str, Any]
    ) -> Tuple[str, float]:
        """
        Apply a correction rule to improve output.
        
        Args:
            rule: Correction rule to apply
            output: Current output
            context: Execution context
            
        Returns:
            Tuple of (improved_output, new_quality_score)
        """
        try:
            if rule.correction_type == CorrectionType.PROMPT_REFINEMENT:
                improved_output = self._refine_prompt_output(output, context)
            elif rule.correction_type == CorrectionType.OUTPUT_VALIDATION:
                improved_output = self._validate_and_fix_output(output, context)
            elif rule.correction_type == CorrectionType.STRATEGY_ADJUSTMENT:
                improved_output = self._adjust_strategy_output(output, context)
            elif rule.correction_type == CorrectionType.ERROR_RECOVERY:
                improved_output = self._recover_from_error(output, context)
            else:
                improved_output = output
            
            new_quality_score = self._calculate_quality_score(improved_output, context)
            
            # Record the correction attempt
            attempt = CorrectionAttempt(
                attempt_id=f"corr_{len(self.correction_history)}",
                original_output=output,
                correction_type=rule.correction_type,
                correction_applied=rule.correction_action,
                improved_output=improved_output,
                quality_score_before=self._calculate_quality_score(output, context),
                quality_score_after=new_quality_score,
                timestamp=str(datetime.now(UTC))
            )
            self.correction_history.append(attempt)
            
            return improved_output, new_quality_score
            
        except Exception as e:
            self.logger.error(f"Correction failed: {e}")
            return output, 0.0
    
    def _evaluate_trigger(self, condition: str, output: str, context: Dict[str, Any]) -> bool:
        """Evaluate if a trigger condition is met."""
        # Simple condition evaluation - in production would be more sophisticated
        if "output_length < 50" in condition and len(output) < 50:
            return True
        elif "missing_required_fields" in condition:
            # Check if JSON output has required fields
            try:
                parsed = json.loads(output)
                required_fields = context.get("required_fields", [])
                return not all(field in parsed for field in required_fields)
            except json.JSONDecodeError:
                return True
        elif "low_relevance_score" in condition:
            return context.get("relevance_score", 1.0) < 0.5
        elif "execution_failed" in condition:
            return context.get("execution_failed", False)
        
        return False
    
    def _refine_prompt_output(self, output: str, context: Dict[str, Any]) -> str:
        """Refine output for better prompt clarity."""
        if len(output) < 50:
            # Add more detail to short outputs
            return f"{output}\n\nAdditional details and specific examples should be included to strengthen this response."
        return output
    
    def _validate_and_fix_output(self, output: str, context: Dict[str, Any]) -> str:
        """Validate and fix output format."""
        try:
            parsed = json.loads(output)
            # Ensure required fields are present
            required_fields = context.get("required_fields", [])
            for field in required_fields:
                if field not in parsed:
                    parsed[field] = "placeholder_value"
            return json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            # Try to fix JSON formatting
            try:
                # Simple JSON fix attempt
                fixed = output.replace("'", '"')
                json.loads(fixed)
                return fixed
            except json.JSONDecodeError:
                # Return a valid JSON structure as fallback
                return json.dumps({"error": "Invalid JSON format", "original": output})
    
    def _adjust_strategy_output(self, output: str, context: Dict[str, Any]) -> str:
        """Adjust strategy based on evidence and context."""
        # Simple strategy adjustment
        if "strategy" in output.lower():
            return f"{output}\n\nStrategy refined based on available evidence and job requirements."
        return output
    
    def _recover_from_error(self, output: str, context: Dict[str, Any]) -> str:
        """Recover from execution errors."""
        return json.dumps({
            "error_recovery": True,
            "fallback_strategy": "Use simplified approach",
            "original_error": output
        })
    
    def _calculate_quality_score(self, output: str, context: Dict[str, Any]) -> float:
        """Calculate quality score for output."""
        score = 0.5  # Base score
        
        # Length scoring
        if 50 <= len(output) <= 1000:
            score += 0.2
        
        # Format scoring
        try:
            json.loads(output)
            score += 0.2
        except json.JSONDecodeError:
            pass
        
        # Content scoring
        if any(keyword in output.lower() for keyword in ["strategy", "analysis", "recommendation"]):
            score += 0.1
        
        return min(score, 1.0)


class SelfCorrectionInjectionProvider:
    """Provides self-correction injection for V6 prompts."""
    
    def __init__(self, engine: Optional[SelfCorrectionEngine] = None) -> None:
        """Initialize the self-correction injection provider."""
        self.engine = engine or SelfCorrectionEngine()
    
    def add_self_correction_extension(
        self,
        prompt_extensions: Dict[InstructionalExtension, ExtensionContent],
        agent_type: str,
        context: Dict[str, Any]
    ) -> Dict[InstructionalExtension, ExtensionContent]:
        """
        Add self-correction instructions as a V6 extension.
        
        Args:
            prompt_extensions: Existing prompt extensions
            agent_type: Type of agent (strategy, rag, drafting, etc.)
            context: Execution context
            
        Returns:
            Updated extensions with self-correction instructions
        """
        correction_content = self._build_correction_instructions(agent_type, context)
        
        if correction_content:
            correction_extension = ExtensionContent(
                extension=InstructionalExtension.SELF_CORRECTION,
                content=correction_content
            )
            prompt_extensions[InstructionalExtension.SELF_CORRECTION] = correction_extension
        
        return prompt_extensions
    
    def _build_correction_instructions(self, agent_type: str, context: Dict[str, Any]) -> str:
        """Build self-correction instructions for the agent type."""
        instructions = [
            "## SELF-CORRECTION INSTRUCTIONS",
            "",
            "After generating your initial output, review and improve it using these criteria:",
            ""
        ]
        
        if agent_type == "strategy":
            instructions.extend([
                "1. **Strategy Clarity**: Is the strategy specific and actionable?",
                "2. **Evidence Alignment**: Does the strategy align with available evidence?",
                "3. **Job Relevance**: Is the strategy tailored to the specific job requirements?",
                ""
            ])
        elif agent_type == "drafting":
            instructions.extend([
                "1. **Content Quality**: Is the content professional and well-written?",
                "2. **Keyword Optimization**: Are relevant keywords naturally included?",
                "3. **Achievement Quantification**: Are achievements quantified where possible?",
                ""
            ])
        elif agent_type == "qa":
            instructions.extend([
                "1. **Completeness**: Are all aspects of the content reviewed?",
                "2. **Accuracy**: Are the findings accurate and well-justified?",
                "3. **Actionability**: Are the recommendations actionable?",
                ""
            ])
        
        instructions.extend([
            "If the output doesn't meet these criteria, revise and improve it before finalizing.",
            "Focus on continuous improvement and quality enhancement."
        ])
        
        return "\n".join(instructions)
    
    def apply_corrections_if_needed(
        self,
        output: str,
        agent_type: str,
        context: Dict[str, Any]
    ) -> Tuple[str, List[CorrectionAttempt]]:
        """
        Apply self-corrections if needed based on output quality.
        
        Args:
            output: Current output
            agent_type: Type of agent
            context: Execution context
            
        Returns:
            Tuple of (improved_output, correction_attempts)
        """
        quality_score = self.engine._calculate_quality_score(output, context)
        applicable_rules = self.engine.should_correct(output, context, quality_score)
        
        correction_attempts = []
        improved_output = output
        
        for rule in applicable_rules[:2]:  # Limit to 2 corrections to avoid loops
            improved_output, new_score = self.engine.apply_correction(rule, improved_output, context)
            # Get the last correction attempt
            if self.engine.correction_history:
                correction_attempts.append(self.engine.correction_history[-1])
        
        return improved_output, correction_attempts


def create_self_correction_provider() -> SelfCorrectionInjectionProvider:
    """Create a self-correction injection provider."""
    return SelfCorrectionInjectionProvider()


# Import datetime for timestamp generation
from datetime import datetime, UTC

__all__ = [
    'CorrectionType',
    'CorrectionRule',
    'CorrectionAttempt',
    'SelfCorrectionEngine',
    'SelfCorrectionInjectionProvider',
    'create_self_correction_provider',
]



