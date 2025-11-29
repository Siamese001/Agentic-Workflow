"""K6 CTA Executor - Sixth hop in the sequential K1-K7 execution pipeline.

Incorporated from L2 lic_k6_cta.py to optimize call-to-action for maximum
response rates based on validation results, archetype analysis, and
message context before final assembly in K7.

This is the sixth execution phase in the hop-based architecture that follows:
L1 Planning → K1 Research → K2 Insights → K3 Draft → K4 Regeneration → K5 Validation → K6 CTA → K7 Assembly
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class CTAOption:
    """Individual CTA option with optimization metrics."""
    cta_text: str
    cta_style: str
    word_count: int
    response_probability: float
    archetype_match: float
    urgency_level: str  # "low", "medium", "high"
    date_window: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CTAOutput:
    """Output from K6 CTA execution phase."""
    final_cta: str
    date_window: str
    cta_style: str
    word_count: int
    response_probability: float
    optimization_applied: bool
    alternative_options: List[CTAOption]
    execution_metadata: Dict[str, Any] = field(default_factory=dict)


class K6CTAExecutor:
    """K6 CTA executor - sixth hop in sequential execution pipeline.
    
    Optimizes call-to-action for maximum response rates based on validation
    results, archetype analysis, and message context before final assembly.
    """
    
    def __init__(self, 
                 cta_plan: Optional[Dict[str, Any]] = None,
                 telemetry_bus: Optional[Any] = None) -> None:
        """Initialize K6 CTA executor."""
        self.cta_plan = cta_plan or {}
        self.telemetry_bus = telemetry_bus
        
        # Default CTA configuration
        self.default_config = {
            "date_window_rules": {
                "business_day_buffer_map": {
                    "Monday": {"min_buffer_days": 2},
                    "Tuesday": {"min_buffer_days": 2},
                    "Wednesday": {"min_buffer_days": 2},
                    "Thursday": {"min_buffer_days": 3},
                    "Friday": {"min_buffer_days": 5},
                    "Saturday": {"min_buffer_days": 3},
                    "Sunday": {"min_buffer_days": 2}
                },
                "output_format": {
                    "natural_language": "Would [date1], [date2], or [date3] work for a brief discussion?"
                }
            },
            "archetype_styles": {
                "C_LEVEL": {
                    "base_cta": "Would you have 15 minutes to discuss strategic alignment opportunities?",
                    "formality": "high",
                    "urgency": "low",
                    "focus": "strategic"
                },
                "EXECUTIVE": {
                    "base_cta": "Would next week work for a brief discussion on mutual objectives?",
                    "formality": "high",
                    "urgency": "medium",
                    "focus": "business_impact"
                },
                "SENIOR_TA": {
                    "base_cta": "Would you have time to explore how technical innovation could support our objectives?",
                    "formality": "medium",
                    "urgency": "low",
                    "focus": "technical"
                },
                "RECRUITER": {
                    "base_cta": "Would you be open to a brief conversation about potential opportunities?",
                    "formality": "medium",
                    "urgency": "medium",
                    "focus": "opportunity"
                }
            },
            "optimization_rules": {
                "max_word_count": 20,
                "min_word_count": 8,
                "required_elements": ["question", "time_reference"],
                "forbidden_phrases": ["call me", "email me", "contact me"]
            }
        }
        
        # CTA optimization strategies
        self.optimization_strategies = {
            "increase_urgency": "add_time_constraint",
            "enhance_formality": "adjust_tone",
            "improve_clarity": "simplify_language",
            "boost_relevance": "archetype_alignment"
        }
    
    def execute(
        self,
        *,
        validation_output: Any,
        persona_plan: Optional[Any] = None,
        message_plan: Optional[Any] = None,
        fusion_plan: Optional[Any] = None,
        recipient_profile: Dict[str, Any],
        outreach_context: Dict[str, Any] = None,
    ) -> CTAOutput:
        """Execute K6 CTA optimization phase.
        
        Args:
            validation_output: Output from K5 validation execution
            persona_plan: Optional persona plan for tone guidance
            message_plan: Optional message plan for constraints
            fusion_plan: Optional fusion plan for context
            recipient_profile: Target recipient profile data
            outreach_context: Additional context for CTA optimization
            
        Returns:
            Optimized CTA with response probability metrics
        """
        outreach_context = outreach_context or {}
        
        # 1. Determine archetype from profile or context
        archetype = self._determine_archetype(recipient_profile, outreach_context)
        
        # 2. Generate date window for scheduling
        date_window = self._generate_date_window()
        
        # 3. Generate base CTA options
        base_options = self._generate_base_cta_options(archetype, date_window, recipient_profile)
        
        # 4. Apply optimization based on validation results
        optimized_options = self._optimize_cta_options(base_options, validation_output, persona_plan, message_plan)
        
        # 5. Select best CTA based on response probability
        final_cta_option = self._select_best_cta(optimized_options)
        
        # 6. Calculate response probability
        response_probability = self._calculate_response_probability(final_cta_option, validation_output, persona_plan)
        
        # 7. Build execution metadata
        execution_metadata = {
            "archetype": archetype,
            "options_generated": len(base_options),
            "optimizations_applied": len(optimized_options) != len(base_options),
            "validation_score": getattr(validation_output, 'quality_score', 0.0),
            "persona_plan_used": persona_plan is not None,
            "fusion_plan_used": fusion_plan is not None
        }
        
        # 8. Create CTA output
        output = CTAOutput(
            final_cta=final_cta_option.cta_text,
            date_window=date_window,
            cta_style=final_cta_option.cta_style,
            word_count=final_cta_option.word_count,
            response_probability=response_probability,
            optimization_applied=len(optimized_options) != len(base_options),
            alternative_options=optimized_options,
            execution_metadata=execution_metadata
        )
        
        # 9. Record telemetry (best-effort)
        self._safe_record_telemetry(output)
        
        return output
    
    def _determine_archetype(self, recipient_profile: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Determine target archetype from available data."""
        # Priority: recipient_profile > context > default
        if recipient_profile.get("archetype"):
            return recipient_profile["archetype"]
        elif context.get("archetype"):
            return context["archetype"]
        else:
            return "EXECUTIVE"  # Default fallback
    
    def _generate_date_window(self) -> str:
        """Generate date window for meeting scheduling."""
        date_config = self.cta_plan.get("date_window_rules", self.default_config["date_window_rules"])
        buffer_map = date_config["business_day_buffer_map"]
        
        today = datetime.now()
        current_day = today.strftime("%A")
        
        buffer_info = buffer_map.get(current_day, buffer_map["Monday"])
        min_buffer = buffer_info["min_buffer_days"]
        
        dates = []
        for i in range(3):
            future_date = today + timedelta(days=min_buffer + i*2)
            
            # Skip weekends
            while future_date.weekday() >= 5:
                future_date += timedelta(days=1)
                
            dates.append(future_date.strftime("%m/%d"))
        
        output_format = date_config["output_format"]["natural_language"]
        return output_format.replace("[date1]", dates[0]).replace("[date2]", dates[1]).replace("[date3]", dates[2])
    
    def _generate_base_cta_options(self, archetype: str, date_window: str, recipient_profile: Dict[str, Any]) -> List[CTAOption]:
        """Generate base CTA options based on archetype."""
        options = []
        archetype_styles = self.cta_plan.get("archetype_styles", self.default_config["archetype_styles"])
        
        style_config = archetype_styles.get(archetype, archetype_styles["EXECUTIVE"])
        
        # Generate primary CTA
        base_cta = style_config["base_cta"]
        
        # Apply date window for certain archetypes
        if archetype in ["EXECUTIVE", "RECRUITER"]:
            base_cta = base_cta.replace("next week", date_window)
        
        primary_option = CTAOption(
            cta_text=base_cta,
            cta_style=archetype.lower(),
            word_count=len(base_cta.split()),
            response_probability=0.7,
            archetype_match=1.0,
            urgency_level=style_config["urgency"],
            date_window=date_window if "date" in base_cta.lower() else None,
            metadata={"generation_method": "archetype_based", "style": style_config}
        )
        options.append(primary_option)
        
        # Generate alternative options
        alternatives = self._generate_alternative_ctas(archetype, date_window, recipient_profile)
        options.extend(alternatives)
        
        return options
    
    def _generate_alternative_ctas(self, archetype: str, date_window: str, recipient_profile: Dict[str, Any]) -> List[CTAOption]:
        """Generate alternative CTA options for optimization."""
        alternatives = []
        
        if archetype == "C_LEVEL":
            alt_ctas = [
                "Would you be available for a 15-minute strategic discussion next week?",
                "I'd appreciate 15 minutes to explore potential strategic alignments.",
                "Would you have time to discuss high-level strategic opportunities?"
            ]
        elif archetype == "EXECUTIVE":
            alt_ctas = [
                f"Would {date_window} work for exploring mutual business objectives?",
                "I'd value your perspective on potential collaboration opportunities.",
                "Would you be open to a brief discussion about shared strategic interests?"
            ]
        elif archetype == "SENIOR_TA":
            company = recipient_profile.get("company", "your organization")
            alt_ctas = [
                f"Would you have time to discuss technical innovation at {company}?",
                "I'd enjoy exploring how our technical approaches might align.",
                "Would you be interested in a technical exchange about current challenges?"
            ]
        elif archetype == "RECRUITER":
            alt_ctas = [
                "Would you be open to exploring potential career opportunities?",
                "I'd appreciate learning more about your current role and interests.",
                "Would you have time for a brief conversation about potential fits?"
            ]
        else:
            alt_ctas = [
                "Would you be available for a brief discussion next week?",
                "I'd value your thoughts on potential collaboration.",
                "Would you have time to explore mutual interests?"
            ]
        
        for i, cta_text in enumerate(alt_ctas):
            option = CTAOption(
                cta_text=cta_text,
                cta_style=f"{archetype.lower()}_alt_{i+1}",
                word_count=len(cta_text.split()),
                response_probability=0.6,
                archetype_match=0.8,
                urgency_level="medium",
                metadata={"generation_method": "alternative", "variant": i+1}
            )
            alternatives.append(option)
        
        return alternatives[:3]  # Limit to 3 alternatives
    
    def _optimize_cta_options(self, options: List[CTAOption], validation_output: Any, persona_plan: Optional[Any], message_plan: Optional[Any]) -> List[CTAOption]:
        """Apply optimization strategies to CTA options."""
        optimized_options = []
        
        for option in options:
            optimized_option = self._apply_optimizations(option, validation_output, persona_plan, message_plan)
            optimized_options.append(optimized_option)
        
        return optimized_options
    
    def _apply_optimizations(self, option: CTAOption, validation_output: Any, persona_plan: Optional[Any], message_plan: Optional[Any]) -> CTAOption:
        """Apply specific optimizations to a CTA option."""
        optimized_text = option.cta_text
        optimizations_applied = []
        
        # Apply validation-based optimizations
        if hasattr(validation_output, 'quality_score') and validation_output.quality_score < 0.7:
            # Improve clarity for low quality scores
            optimized_text = self._improve_clarity(optimized_text)
            optimizations_applied.append("clarity_improvement")
        
        # Apply persona-based optimizations
        if persona_plan and hasattr(persona_plan, 'communication_style'):
            optimized_text = self._adjust_tone(optimized_text, persona_plan.communication_style)
            optimizations_applied.append("tone_adjustment")
        
        # Apply message plan constraints
        if message_plan and hasattr(message_plan, 'constraints'):
            optimized_text = self._apply_constraints(optimized_text, message_plan.constraints)
            optimizations_applied.append("constraint_application")
        
        # Apply word count optimization
        optimized_text = self._optimize_word_count(optimized_text)
        
        # Create optimized option
        optimized_option = CTAOption(
            cta_text=optimized_text,
            cta_style=option.cta_style + "_optimized",
            word_count=len(optimized_text.split()),
            response_probability=option.response_probability + 0.1,  # Boost from optimization
            archetype_match=option.archetype_match,
            urgency_level=option.urgency_level,
            date_window=option.date_window,
            metadata={
                **option.metadata,
                "optimizations_applied": optimizations_applied,
                "original_text": option.cta_text
            }
        )
        
        return optimized_option
    
    def _improve_clarity(self, cta_text: str) -> str:
        """Improve clarity of CTA text."""
        # Remove ambiguous phrases
        clarity_improvements = {
            "some time": "15 minutes",
            "a bit": "brief",
            "maybe": "would",
            "perhaps": "would"
        }
        
        improved_text = cta_text
        for ambiguous, clear in clarity_improvements.items():
            improved_text = improved_text.replace(ambiguous, clear)
        
        return improved_text
    
    def _adjust_tone(self, cta_text: str, communication_style: str) -> str:
        """Adjust CTA tone based on persona communication style."""
        if communication_style == "formal":
            # Make more formal
            cta_text = cta_text.replace("I'd", "I would")
            cta_text = cta_text.replace("you're", "you are")
        elif communication_style == "casual":
            # Make slightly more casual
            cta_text = cta_text.replace("I would", "I'd")
            cta_text = cta_text.replace("discussion", "chat")
        
        return cta_text
    
    def _apply_constraints(self, cta_text: str, constraints: List[str]) -> str:
        """Apply message plan constraints to CTA."""
        for constraint in constraints:
            if constraint == "brevity_required":
                # Make more concise
                words = cta_text.split()
                if len(words) > 15:
                    cta_text = " ".join(words[:15])
            elif constraint == "no_questions":
                # Convert to statement if constraint requires
                if "?" in cta_text:
                    cta_text = cta_text.replace("?", ".")
                    cta_text = cta_text.replace("Would", "I would")
        
        return cta_text
    
    def _optimize_word_count(self, cta_text: str) -> str:
        """Optimize word count for maximum effectiveness."""
        words = cta_text.split()
        optimization_rules = self.default_config["optimization_rules"]
        
        min_words = optimization_rules["min_word_count"]
        max_words = optimization_rules["max_word_count"]
        
        if len(words) > max_words:
            # Condense by removing less critical words
            critical_words = []
            for word in words:
                if word.lower() in ["would", "you", "have", "time", "discussion", "minutes", "next", "week"]:
                    critical_words.append(word)
            
            if len(critical_words) >= min_words:
                cta_text = " ".join(critical_words)
            else:
                cta_text = " ".join(words[:max_words])
        
        elif len(words) < min_words:
            # Expand with professional language
            if "discussion" in cta_text:
                cta_text = cta_text.replace("discussion", "brief discussion")
            elif "time" in cta_text:
                cta_text = cta_text.replace("time", "some time")
        
        return cta_text
    
    def _select_best_cta(self, options: List[CTAOption]) -> CTAOption:
        """Select best CTA option based on multiple criteria."""
        if not options:
            # Create default option
            return CTAOption(
                cta_text="Would you have time for a brief discussion next week?",
                cta_style="default",
                word_count=11,
                response_probability=0.5,
                archetype_match=0.5,
                urgency_level="medium"
            )
        
        # Score options based on multiple factors
        scored_options = []
        for option in options:
            score = (
                option.response_probability * 0.4 +
                option.archetype_match * 0.3 +
                (1.0 - abs(option.word_count - 12) / 12) * 0.2 +  # Ideal word count ~12
                (0.8 if option.urgency_level == "medium" else 0.6) * 0.1
            )
            scored_options.append((option, score))
        
        # Return highest scored option
        best_option = max(scored_options, key=lambda x: x[1])[0]
        return best_option
    
    def _calculate_response_probability(self, cta_option: CTAOption, validation_output: Any, persona_plan: Optional[Any]) -> float:
        """Calculate response probability for the selected CTA."""
        base_probability = cta_option.response_probability
        
        # Adjust based on validation quality
        if hasattr(validation_output, 'quality_score'):
            quality_boost = validation_output.quality_score * 0.2
            base_probability += quality_boost
        
        # Adjust based on persona match
        if persona_plan and hasattr(persona_plan, 'drift_threshold'):
            persona_boost = (1.0 - persona_plan.drift_threshold) * 0.1
            base_probability += persona_boost
        
        # Adjust based on word count optimization
        ideal_word_count = 12
        word_count_diff = abs(cta_option.word_count - ideal_word_count)
        word_count_penalty = word_count_diff / ideal_word_count * 0.1
        base_probability -= word_count_penalty
        
        return round(max(min(base_probability, 1.0), 0.0), 3)
    
    def _safe_record_telemetry(self, output: CTAOutput) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("k6_cta_executed", {
                    "cta_style": output.cta_style,
                    "word_count": output.word_count,
                    "response_probability": output.response_probability,
                    "optimization_applied": output.optimization_applied,
                    "alternatives_generated": len(output.alternative_options)
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_cta_summary(self, output: CTAOutput) -> Dict[str, Any]:
        """Get a summary of the CTA execution for debugging/telemetry."""
        return {
            "execution_id": "k6_cta",
            "cta_style": output.cta_style,
            "word_count": output.word_count,
            "response_probability": output.response_probability,
            "optimization_applied": output.optimization_applied,
            "date_window_generated": output.date_window,
            "alternatives_count": len(output.alternative_options),
            "archetype": output.execution_metadata.get("archetype", "unknown")
        }
