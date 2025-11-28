"""LIC Message Executor - L2 Execution Layer

Implements HOP-4 message generation execution from legacy LIC system.
Executes personalized message generation with hooks, value props, CTA.
Consumes L1 fusion plans - no embedded reasoning.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from l1.lic_fusion_planner import (
    ResumeFusionPlan, FusionStrategy, MessageComponent
)
from l1.lic_grounding_planner import SenderGroundingPlan
from l1.lic_profile_planner import ProfileAnalysisPlan
from l2.interfaces import ExecutorResult


logger = logging.getLogger(__name__)


@dataclass
class MessageExecutionContext:
    """Message generation execution context"""
    fusion_plan: ResumeFusionPlan
    grounding_plan: SenderGroundingPlan
    profile_plan: ProfileAnalysisPlan
    execution_start_time: datetime


@dataclass
class MessageComponent:
    """Individual message component with fusion data"""
    component_type: str
    content: str
    fusion_sources: List[str]
    confidence: float
    persona_aligned: bool


@dataclass
class GeneratedMessage:
    """Complete generated message with components"""
    message_id: str
    hook: str
    value_prop: str
    evidence: str
    cta: str
    closing: str
    
    # Fusion tracking
    fusion_applied: Dict[str, List[str]]
    persona_consistency_score: float
    personalization_score: float
    
    # Quality metrics
    overall_quality: float
    length_appropriate: bool
    tone_aligned: bool


@dataclass
class MessageExecutionResult:
    """Complete message execution result"""
    # Execution metadata
    plan_id: str
    execution_time_ms: int
    archetype: str
    
    # Generated messages
    primary_message: GeneratedMessage
    alternative_messages: List[GeneratedMessage]
    
    # Execution details
    fusion_strategies_applied: List[str]
    personalization_elements: Dict[str, Any]
    quality_metrics: Dict[str, float]
    
    # Validation results
    persona_validation: Dict[str, bool]
    content_validation: Dict[str, bool]
    overall_success: bool


class LICMessageExecutor:
    """
    L2 Executor for LIC HOP-4 Message Generation
    
    Executes message generation plans with resume fusion, personalization,
    and archetype-specific content strategies. Pure execution - no planning logic.
    """
    
    def __init__(
        self,
        llm_client: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize message executor
        
        Args:
            llm_client: LLM client for content generation
            config: Optional execution configuration
        """
        self.llm_client = llm_client
        self.config = config or self._get_default_config()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default execution configuration"""
        return {
            "execution": {
                "max_alternatives": 3,
                "generation_timeout_ms": 30000,
                "min_quality_threshold": 0.7,
                "max_message_length": 500,
                "enable_fusion": True,
                "enable_persona_validation": True
            },
            "archetype_configs": {
                "executive": {
                    "tone": "formal",
                    "focus": "strategic",
                    "length_preference": "concise",
                    "key_elements": ["business_value", "strategic_impact"]
                },
                "hiring_manager": {
                    "tone": "professional",
                    "focus": "team",
                    "length_preference": "balanced",
                    "key_elements": ["team_value", "leadership", "culture"]
                },
                "technical_lead": {
                    "tone": "technical",
                    "focus": "solutions",
                    "length_preference": "detailed",
                    "key_elements": ["technical_value", "innovation", "problem_solving"]
                },
                "recruiter": {
                    "tone": "friendly",
                    "focus": "candidate",
                    "length_preference": "balanced",
                    "key_elements": ["qualifications", "fit", "opportunity"]
                }
            }
        }
    
    async def execute_message_generation(
        self,
        fusion_plan: ResumeFusionPlan,
        grounding_plan: SenderGroundingPlan,
        profile_plan: ProfileAnalysisPlan
    ) -> ExecutorResult[MessageExecutionResult]:
        """
        Execute message generation plan
        
        Args:
            fusion_plan: Resume→message fusion plan from L1
            grounding_plan: Sender grounding plan from L1
            profile_plan: Profile analysis plan from L1
            
        Returns:
            Complete message execution result
        """
        execution_start = datetime.now()
        
        try:
            # Create execution context
            context = MessageExecutionContext(
                fusion_plan=fusion_plan,
                grounding_plan=grounding_plan,
                profile_plan=profile_plan,
                execution_start_time=execution_start
            )
            
            logger.info(f"Executing message generation for {profile_plan.archetype.value}")
            
            # Step 1: Generate primary message
            primary_message = await self._generate_primary_message(context)
            
            # Step 2: Generate alternative messages
            alternative_messages = await self._generate_alternative_messages(context)
            
            # Step 3: Apply fusion strategies
            fused_messages = await self._apply_fusion_strategies(context, primary_message, alternative_messages)
            
            # Step 4: Validate persona consistency
            validated_messages = await self._validate_persona_consistency(context, fused_messages)
            
            # Step 5: Quality assessment and selection
            final_result = await self._assess_and_select_final(context, validated_messages)
            
            # Calculate execution time
            execution_time = int((datetime.now() - execution_start).total_seconds() * 1000)
            
            # Create execution result
            result = MessageExecutionResult(
                plan_id=fusion_plan.plan_id,
                execution_time_ms=execution_time,
                archetype=profile_plan.archetype.value,
                primary_message=final_result.primary_message,
                alternative_messages=final_result.alternative_messages,
                fusion_strategies_applied=[mapping.fusion_strategy.value for mapping in fusion_plan.fusion_mappings],
                personalization_elements=final_result.personalization_elements,
                quality_metrics=final_result.quality_metrics,
                persona_validation=final_result.persona_validation,
                content_validation=final_result.content_validation,
                overall_success=final_result.overall_success
            )
            
            logger.info(f"Message generation completed in {execution_time}ms with quality score {result.primary_message.overall_quality:.2f}")
            
            return ExecutorResult(
                success=True,
                data=result,
                message=f"Message generated successfully with quality score {result.primary_message.overall_quality:.2f}"
            )
            
        except Exception as e:
            execution_time = int((datetime.now() - execution_start).total_seconds() * 1000)
            logger.error(f"Message generation failed after {execution_time}ms: {str(e)}")
            
            return ExecutorResult(
                success=False,
                data=None,
                message=f"Message generation failed: {str(e)}",
                error_code="MESSAGE_GENERATION_ERROR"
            )
    
    async def _generate_primary_message(self, context: MessageExecutionContext) -> GeneratedMessage:
        """Generate primary message based on plans"""
        archetype = context.profile_plan.archetype.value
        archetype_config = self.config["execution"]["archetype_configs"].get(archetype, {})
        
        # Generate each message component
        hook = await self._generate_hook(context, archetype_config)
        value_prop = await self._generate_value_prop(context, archetype_config)
        evidence = await self._generate_evidence(context, archetype_config)
        cta = await self._generate_cta(context, archetype_config)
        closing = await self._generate_closing(context, archetype_config)
        
        # Create message
        message = GeneratedMessage(
            message_id=f"{context.fusion_plan.plan_id}_primary",
            hook=hook,
            value_prop=value_prop,
            evidence=evidence,
            cta=cta,
            closing=closing,
            fusion_applied={},  # Will be filled during fusion
            persona_consistency_score=0.0,  # Will be calculated
            personalization_score=0.0,  # Will be calculated
            overall_quality=0.0,  # Will be calculated
            length_appropriate=False,  # Will be validated
            tone_aligned=False  # Will be validated
        )
        
        return message
    
    async def _generate_alternative_messages(self, context: MessageExecutionContext) -> List[GeneratedMessage]:
        """Generate alternative message variations"""
        max_alternatives = self.config["execution"]["max_alternatives"]
        alternatives = []
        
        for i in range(max_alternatives):
            try:
                # Generate variation with different focus
                alternative = await self._generate_message_variation(context, i)
                alternatives.append(alternative)
            except Exception as e:
                logger.warning(f"Failed to generate alternative message {i}: {str(e)}")
        
        return alternatives
    
    async def _generate_message_variation(
        self,
        context: MessageExecutionContext,
        variation_index: int
    ) -> GeneratedMessage:
        """Generate a specific message variation"""
        archetype = context.profile_plan.archetype.value
        archetype_config = self.config["execution"]["archetype_configs"].get(archetype, {})
        
        # Apply variation strategy based on index
        variation_strategies = ["focus_different_skill", "alternate_tone", "different_evidence"]
        strategy = variation_strategies[variation_index % len(variation_strategies)]
        
        # Generate components with variation
        hook = await self._generate_hook_variation(context, archetype_config, strategy)
        value_prop = await self._generate_value_prop_variation(context, archetype_config, strategy)
        evidence = await self._generate_evidence_variation(context, archetype_config, strategy)
        cta = await self._generate_cta(context, archetype_config)  # CTA usually stays consistent
        closing = await self._generate_closing(context, archetype_config)
        
        return GeneratedMessage(
            message_id=f"{context.fusion_plan.plan_id}_alt_{variation_index}",
            hook=hook,
            value_prop=value_prop,
            evidence=evidence,
            cta=cta,
            closing=closing,
            fusion_applied={},
            persona_consistency_score=0.0,
            personalization_score=0.0,
            overall_quality=0.0,
            length_appropriate=False,
            tone_aligned=False
        )
    
    async def _apply_fusion_strategies(
        self,
        context: MessageExecutionContext,
        primary_message: GeneratedMessage,
        alternative_messages: List[GeneratedMessage]
    ) -> Tuple[GeneratedMessage, List[GeneratedMessage]]:
        """Apply resume fusion strategies to messages"""
        if not self.config["execution"]["enable_fusion"]:
            return primary_message, alternative_messages
        
        # Apply fusion to primary message
        fused_primary = await self._apply_fusion_to_message(context, primary_message)
        
        # Apply fusion to alternatives
        fused_alternatives = []
        for alt_message in alternative_messages:
            fused_alt = await self._apply_fusion_to_message(context, alt_message)
            fused_alternatives.append(fused_alt)
        
        return fused_primary, fused_alternatives
    
    async def _apply_fusion_to_message(
        self,
        context: MessageExecutionContext,
        message: GeneratedMessage
    ) -> GeneratedMessage:
        """Apply fusion strategies to a single message"""
        fusion_plan = context.fusion_plan
        grounding_plan = context.grounding_plan
        
        fusion_applied = {}
        
        # Apply each fusion mapping
        for mapping in fusion_plan.fusion_mappings:
            component_type = mapping.message_component.value
            fusion_content = await self._extract_fusion_content(context, mapping)
            
            # Apply fusion to appropriate component
            if component_type == "hook" and fusion_content:
                message.hook = self._integrate_fusion_content(message.hook, fusion_content, mapping.content_template)
                fusion_applied["hook"] = [mapping.resume_source]
            elif component_type == "value_prop" and fusion_content:
                message.value_prop = self._integrate_fusion_content(message.value_prop, fusion_content, mapping.content_template)
                fusion_applied["value_prop"] = [mapping.resume_source]
            elif component_type == "evidence" and fusion_content:
                message.evidence = self._integrate_fusion_content(message.evidence, fusion_content, mapping.content_template)
                fusion_applied["evidence"] = [mapping.resume_source]
            elif component_type == "cta" and fusion_content:
                message.cta = self._integrate_fusion_content(message.cta, fusion_content, mapping.content_template)
                fusion_applied["cta"] = [mapping.resume_source]
        
        message.fusion_applied = fusion_applied
        return message
    
    async def _extract_fusion_content(self, context: MessageExecutionContext, mapping) -> str:
        """Extract relevant content from resume for fusion"""
        resume_source = mapping.resume_source
        
        if resume_source == "technical_skills":
            skills = context.grounding_plan.technical_capabilities[:3]  # Top 3 skills
            return ", ".join(skills)
        elif resume_source == "achievements":
            achievements = context.grounding_plan.achievement_highlights[:2]  # Top 2 achievements
            return " and ".join(achievements)
        elif resume_source == "leadership_experience":
            leadership = context.grounding_plan.leadership_qualifications[:2]
            return ", ".join(leadership)
        elif resume_source == "domain_expertise":
            domains = context.grounding_plan.domain_expertise_areas[:2]
            return ", ".join(domains)
        else:
            return ""
    
    def _integrate_fusion_content(self, original_content: str, fusion_content: str, template: str) -> str:
        """Integrate fusion content into message component using template"""
        if not fusion_content:
            return original_content
        
        # Simple template substitution
        try:
            integrated = template.format(
                capability=fusion_content,
                skill=fusion_content,
                achievement=fusion_content,
                experience=fusion_content,
                value=fusion_content
            )
            return integrated
        except (KeyError, ValueError):
            # Fallback: prepend fusion content
            return f"{fusion_content} - {original_content}"
    
    async def _validate_persona_consistency(
        self,
        context: MessageExecutionContext,
        messages: Tuple[GeneratedMessage, List[GeneratedMessage]]
    ) -> Tuple[GeneratedMessage, List[GeneratedMessage]]:
        """Validate persona consistency across messages"""
        if not self.config["execution"]["enable_persona_validation"]:
            return messages
        
        primary_message, alternative_messages = messages
        
        # Validate primary message
        validated_primary = await self._validate_message_persona(context, primary_message)
        
        # Validate alternatives
        validated_alternatives = []
        for alt_message in alternative_messages:
            validated_alt = await self._validate_message_persona(context, alt_message)
            validated_alternatives.append(validated_alt)
        
        return validated_primary, validated_alternatives
    
    async def _validate_message_persona(
        self,
        context: MessageExecutionContext,
        message: GeneratedMessage
    ) -> GeneratedMessage:
        """Validate persona consistency for a single message"""
        archetype = context.profile_plan.archetype.value
        archetype_config = self.config["execution"]["archetype_configs"].get(archetype, {})
        
        # Calculate persona consistency score
        persona_score = self._calculate_persona_score(message, archetype_config)
        message.persona_consistency_score = persona_score
        
        # Calculate personalization score
        personalization_score = self._calculate_personalization_score(message, context)
        message.personalization_score = personalization_score
        
        # Validate length
        total_length = len(message.hook) + len(message.value_prop) + len(message.evidence) + len(message.cta) + len(message.closing)
        max_length = self.config["execution"]["max_message_length"]
        message.length_appropriate = total_length <= max_length
        
        # Validate tone alignment
        expected_tone = archetype_config.get("tone", "professional")
        message.tone_aligned = self._validate_tone_alignment(message, expected_tone)
        
        # Calculate overall quality
        message.overall_quality = self._calculate_overall_quality(message)
        
        return message
    
    def _calculate_persona_score(self, message: GeneratedMessage, archetype_config: Dict[str, Any]) -> float:
        """Calculate persona consistency score"""
        # Simple scoring based on tone and focus alignment
        tone_score = 0.8 if message.tone_aligned else 0.5
        length_score = 0.9 if message.length_appropriate else 0.6
        
        # Content relevance scoring (simplified)
        content_score = 0.7  # Base score
        
        # Weighted average
        persona_score = (tone_score * 0.4) + (length_score * 0.3) + (content_score * 0.3)
        
        return min(persona_score, 1.0)
    
    def _calculate_personalization_score(self, message: GeneratedMessage, context: MessageExecutionContext) -> float:
        """Calculate personalization score based on fusion applied"""
        fusion_count = len(message.fusion_applied)
        max_fusion = len(context.fusion_plan.fusion_mappings)
        
        if max_fusion == 0:
            return 0.0
        
        # Score based on fusion coverage
        fusion_score = fusion_count / max_fusion
        
        # Quality of fusion content
        quality_score = 0.8 if fusion_count > 0 else 0.0
        
        # Combined score
        personalization_score = (fusion_score * 0.6) + (quality_score * 0.4)
        
        return min(personalization_score, 1.0)
    
    def _validate_tone_alignment(self, message: GeneratedMessage, expected_tone: str) -> bool:
        """Validate tone alignment with archetype expectations"""
        # Simple tone validation based on keywords
        all_content = f"{message.hook} {message.value_prop} {message.evidence} {message.cta} {message.closing}"
        content_lower = all_content.lower()
        
        tone_indicators = {
            "formal": ["strategic", "business", "professional", "executive"],
            "professional": ["experience", "expertise", "qualified", "skilled"],
            "technical": ["technical", "solution", "architecture", "engineering"],
            "friendly": ["collaborate", "discuss", "opportunity", "excited"]
        }
        
        expected_indicators = tone_indicators.get(expected_tone, [])
        
        # Check if any expected indicators are present
        has_expected_tone = any(indicator in content_lower for indicator in expected_indicators)
        
        return has_expected_tone
    
    def _calculate_overall_quality(self, message: GeneratedMessage) -> float:
        """Calculate overall message quality score"""
        # Weighted components
        persona_weight = 0.3
        personalization_weight = 0.3
        length_weight = 0.2
        tone_weight = 0.2
        
        persona_score = message.persona_consistency_score
        personalization_score = message.personalization_score
        length_score = 0.9 if message.length_appropriate else 0.5
        tone_score = 0.9 if message.tone_aligned else 0.6
        
        overall_quality = (
            persona_score * persona_weight +
            personalization_score * personalization_weight +
            length_score * length_weight +
            tone_score * tone_weight
        )
        
        return min(overall_quality, 1.0)
    
    async def _assess_and_select_final(
        self,
        context: MessageExecutionContext,
        messages: Tuple[GeneratedMessage, List[GeneratedMessage]]
    ) -> Any:
        """Assess quality and select final messages"""
        primary_message, alternative_messages = messages
        
        # Quality threshold check
        min_quality = self.config["execution"]["min_quality_threshold"]
        
        # If primary doesn't meet threshold, try to find better alternative
        if primary_message.overall_quality < min_quality and alternative_messages:
            best_alternative = max(alternative_messages, key=lambda m: m.overall_quality)
            if best_alternative.overall_quality > primary_message.overall_quality:
                primary_message, best_alternative = best_alternative, primary_message
                alternative_messages[0] = primary_message  # Swap back
        
        # Prepare final result data
        personalization_elements = {
            "fusion_applied": primary_message.fusion_applied,
            "key_capabilities": context.grounding_plan.technical_capabilities,
            "achievements_highlighted": context.grounding_plan.achievement_highlights,
            "archetype_adaptation": context.profile_plan.archetype.value
        }
        
        quality_metrics = {
            "overall_quality": primary_message.overall_quality,
            "persona_consistency": primary_message.persona_consistency_score,
            "personalization_score": primary_message.personalization_score,
            "length_appropriate": primary_message.length_appropriate,
            "tone_aligned": primary_message.tone_aligned
        }
        
        persona_validation = {
            "tone_aligned": primary_message.tone_aligned,
            "length_appropriate": primary_message.length_appropriate,
            "quality_threshold_met": primary_message.overall_quality >= min_quality
        }
        
        content_validation = {
            "has_hook": len(primary_message.hook.strip()) > 0,
            "has_value_prop": len(primary_message.value_prop.strip()) > 0,
            "has_evidence": len(primary_message.evidence.strip()) > 0,
            "has_cta": len(primary_message.cta.strip()) > 0,
            "has_closing": len(primary_message.closing.strip()) > 0
        }
        
        overall_success = (
            primary_message.overall_quality >= min_quality and
            all(content_validation.values()) and
            primary_message.tone_aligned
        )
        
        # Create final result object
        class FinalResult:
            def __init__(self):
                self.primary_message = primary_message
                self.alternative_messages = alternative_messages
                self.personalization_elements = personalization_elements
                self.quality_metrics = quality_metrics
                self.persona_validation = persona_validation
                self.content_validation = content_validation
                self.overall_success = overall_success
        
        return FinalResult()
    
    # Component generation methods (simplified implementations)
    async def _generate_hook(self, context: MessageExecutionContext, archetype_config: Dict[str, Any]) -> str:
        """Generate message hook"""
        archetype = context.profile_plan.archetype.value
        company = context.profile_plan.recipient_company
        
        hooks = {
            "executive": f"Driving strategic growth at {company} through executive leadership and innovation",
            "hiring_manager": f"Building high-performing teams at {company} through collaborative leadership",
            "technical_lead": f"Solving complex technical challenges at {company} through innovative engineering",
            "recruiter": f"Excited about the opportunity to contribute to {company}'s success"
        }
        
        return hooks.get(archetype, f"Interested in contributing to {company}'s success")
    
    async def _generate_value_prop(self, context: MessageExecutionContext, archetype_config: Dict[str, Any]) -> str:
        """Generate value proposition"""
        skills = context.grounding_plan.technical_capabilities[:2]
        return f"Leveraging expertise in {', '.join(skills)} to deliver exceptional results"
    
    async def _generate_evidence(self, context: MessageExecutionContext, archetype_config: Dict[str, Any]) -> str:
        """Generate evidence section"""
        achievements = context.grounding_plan.achievement_highlights[:1]
        if achievements:
            return f"Proven track record with achievements including {achievements[0]}"
        return "Consistent track record of delivering high-impact results"
    
    async def _generate_cta(self, context: MessageExecutionContext, archetype_config: Dict[str, Any]) -> str:
        """Generate call to action"""
        archetype = context.profile_plan.archetype.value
        
        ctas = {
            "executive": "I'd welcome the opportunity to discuss how my strategic leadership can benefit your organization.",
            "hiring_manager": "I'd like to explore how my team-building experience can support your hiring goals.",
            "technical_lead": "Let's discuss how my technical expertise can help solve your engineering challenges.",
            "recruiter": "I'm excited to learn more about this opportunity and discuss my qualifications."
        }
        
        return ctas.get(archetype, "I look forward to discussing this opportunity further.")
    
    async def _generate_closing(self, context: MessageExecutionContext, archetype_config: Dict[str, Any]) -> str:
        """Generate message closing"""
        return "Best regards"
    
    # Variation generation methods
    async def _generate_hook_variation(self, context: MessageExecutionContext, archetype_config: Dict[str, Any], strategy: str) -> str:
        """Generate hook variation based on strategy"""
        base_hook = await self._generate_hook(context, archetype_config)
        
        if strategy == "focus_different_skill":
            skills = context.grounding_plan.technical_capabilities
            if len(skills) > 2:
                alternative_skills = skills[2:4]
                return f"Applying {' and '.join(alternative_skills)} expertise to drive innovation at {context.profile_plan.recipient_company}"
        
        return base_hook
    
    async def _generate_value_prop_variation(self, context: MessageExecutionContext, archetype_config: Dict[str, Any], strategy: str) -> str:
        """Generate value proposition variation"""
        base_value_prop = await self._generate_value_prop(context, archetype_config)
        
        if strategy == "focus_different_skill":
            skills = context.grounding_plan.technical_capabilities
            if len(skills) > 2:
                alternative_skills = skills[2:4]
                return f"Utilizing {' and '.join(alternative_skills)} to create measurable business impact"
        
        return base_value_prop
    
    async def _generate_evidence_variation(self, context: MessageExecutionContext, archetype_config: Dict[str, Any], strategy: str) -> str:
        """Generate evidence variation"""
        base_evidence = await self._generate_evidence(context, archetype_config)
        
        if strategy == "different_evidence":
            achievements = context.grounding_plan.achievement_highlights
            if len(achievements) > 1:
                return f"Demonstrated success with key achievements including {achievements[1]}"
        
        return base_evidence
