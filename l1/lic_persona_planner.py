"""LIC Persona Consistency Planning - L1 Planning Layer

Implements persona drift control planning from legacy LIC system.
Plans persona consistency validation and drift detection strategies.
Pure planning - no execution, IO, or LLM calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum


class PersonaDimension(Enum):
    """Dimensions of persona consistency to monitor"""
    COMMUNICATION_STYLE = "communication_style"
    TONE_AND_VOICE = "tone_and_voice"
    PROFESSIONAL_LEVEL = "professional_level"
    EXPERTISE_DOMAIN = "expertise_domain"
    LEADERSHIP_APPROACH = "leadership_approach"
    COLLABORATION_STYLE = "collaboration_style"


class DriftSeverity(Enum):
    """Severity levels for persona drift"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationTrigger(Enum):
    """Triggers for persona validation"""
    PRE_EXECUTION = "pre_execution"
    POST_GENERATION = "post_generation"
    ARCHETYPE_CHANGE = "archetype_change"
    CONTEXT_SHIFT = "context_shift"
    MANUAL_REQUEST = "manual_request"


@dataclass
class PersonaBaseline:
    """Baseline persona characteristics for comparison"""
    dimension: PersonaDimension
    baseline_characteristics: List[str]
    tolerance_threshold: float
    weight: float
    validation_methods: List[str]


@dataclass
class DriftIndicator:
    """Specific indicator of potential persona drift"""
    dimension: PersonaDimension
    indicator_type: str
    detection_method: str
    threshold_value: float
    severity_weight: float


@dataclass
class PersonaConsistencyPlan:
    """Complete persona consistency validation plan"""
    # Core planning data
    mission_context: str
    recipient_archetype: str
    sender_persona_profile: Dict[str, Any]
    
    # Persona baselines
    persona_baselines: List[PersonaBaseline]
    
    # Drift detection configuration
    drift_indicators: List[DriftIndicator]
    validation_triggers: List[ValidationTrigger]
    
    # Validation strategy
    pre_execution_checks: List[str]
    post_generation_validations: List[str]
    drift_correction_strategies: Dict[str, str]
    
    # Monitoring configuration
    monitoring_frequency: str
    alert_thresholds: Dict[str, float]
    escalation_criteria: List[str]
    
    # Planning metadata
    plan_id: str
    created_at: str
    validation_priority_order: List[str]
    expected_consistency_score: float
    
    # Compliance requirements
    required_dimensions: List[PersonaDimension]
    optional_dimensions: List[PersonaDimension]


class LICPersonaPlanner:
    """
    L1 Planner for LIC Persona Consistency and Drift Control
    
    Creates plans for maintaining persona consistency across message
    generation and detecting/correcting persona drift.
    Pure deterministic planning - no external execution.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize persona planner with configuration
        
        Args:
            config: Optional configuration for persona validation
        """
        self.config = config or self._get_default_config()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default persona configuration"""
        return {
            "persona_agent": {
                "persona_dimensions": {
                    "communication_style": {
                        "baseline_characteristics": ["professional", "clear", "concise"],
                        "tolerance_threshold": 0.8,
                        "weight": 0.3,
                        "validation_methods": ["tone_analysis", "formality_check", "clarity_score"]
                    },
                    "tone_and_voice": {
                        "baseline_characteristics": ["confident", "authoritative", "respectful"],
                        "tolerance_threshold": 0.7,
                        "weight": 0.25,
                        "validation_methods": ["sentiment_analysis", "voice_consistency", "confidence_score"]
                    },
                    "professional_level": {
                        "baseline_characteristics": ["executive", "strategic", "business_focused"],
                        "tolerance_threshold": 0.9,
                        "weight": 0.2,
                        "validation_methods": ["professionalism_score", "business_acumen_check", "strategic_alignment"]
                    },
                    "expertise_domain": {
                        "baseline_characteristics": ["technical", "innovative", "solution_oriented"],
                        "tolerance_threshold": 0.8,
                        "weight": 0.15,
                        "validation_methods": ["domain_consistency", "technical_accuracy", "innovation_focus"]
                    },
                    "leadership_approach": {
                        "baseline_characteristics": ["collaborative", "empowering", "visionary"],
                        "tolerance_threshold": 0.7,
                        "weight": 0.1,
                        "validation_methods": ["leadership_style_check", "collaboration_indicators", "vision_language"]
                    }
                },
                "drift_detection": {
                    "monitoring_frequency": "continuous",
                    "alert_thresholds": {
                        "overall_consistency": 0.7,
                        "dimension_drift": 0.3,
                        "critical_drift": 0.5
                    },
                    "escalation_criteria": [
                        "multiple_dimensions_drift",
                        "critical_dimension_drift",
                        "repeated_drift_patterns"
                    ]
                }
            }
        }
    
    def plan_persona_consistency(
        self,
        mission_context: str,
        recipient_archetype: str,
        sender_persona_profile: Dict[str, Any],
        plan_id: Optional[str] = None
    ) -> PersonaConsistencyPlan:
        """
        Create persona consistency validation plan
        
        Args:
            mission_context: Context of the outreach mission
            recipient_archetype: Target recipient's archetype
            sender_persona_profile: Sender's persona characteristics
            plan_id: Optional plan identifier
            
        Returns:
            Complete persona consistency plan
        """
        # Generate plan ID if not provided
        if plan_id is None:
            import hashlib
            id_string = f"{mission_context}_{recipient_archetype}_persona"
            plan_id = hashlib.md5(id_string.encode()).hexdigest()[:12]
        
        # Create persona baselines
        persona_baselines = self._create_persona_baselines(sender_persona_profile)
        
        # Create drift indicators
        drift_indicators = self._create_drift_indicators(recipient_archetype)
        
        # Define validation triggers
        validation_triggers = self._define_validation_triggers(recipient_archetype)
        
        # Create validation strategies
        pre_execution_checks = self._define_pre_execution_checks(recipient_archetype)
        post_generation_validations = self._define_post_generation_validations(recipient_archetype)
        drift_correction_strategies = self._define_drift_correction_strategies(recipient_archetype)
        
        # Configure monitoring
        monitoring_config = self.config["persona_agent"]["drift_detection"]
        monitoring_frequency = monitoring_config["monitoring_frequency"]
        alert_thresholds = monitoring_config["alert_thresholds"]
        escalation_criteria = monitoring_config["escalation_criteria"]
        
        # Determine validation priority order
        validation_priority_order = self._prioritize_validations(recipient_archetype)
        
        # Calculate expected consistency score
        expected_consistency_score = self._calculate_consistency_score(
            sender_persona_profile, recipient_archetype
        )
        
        # Define dimension requirements
        required_dimensions, optional_dimensions = self._define_dimension_requirements(recipient_archetype)
        
        # Get timestamp
        from datetime import datetime
        created_at = datetime.now().isoformat()
        
        return PersonaConsistencyPlan(
            mission_context=mission_context,
            recipient_archetype=recipient_archetype,
            sender_persona_profile=sender_persona_profile,
            persona_baselines=persona_baselines,
            drift_indicators=drift_indicators,
            validation_triggers=validation_triggers,
            pre_execution_checks=pre_execution_checks,
            post_generation_validations=post_generation_validations,
            drift_correction_strategies=drift_correction_strategies,
            monitoring_frequency=monitoring_frequency,
            alert_thresholds=alert_thresholds,
            escalation_criteria=escalation_criteria,
            plan_id=plan_id,
            created_at=created_at,
            validation_priority_order=validation_priority_order,
            expected_consistency_score=expected_consistency_score,
            required_dimensions=required_dimensions,
            optional_dimensions=optional_dimensions
        )
    
    def _create_persona_baselines(self, persona_profile: Dict[str, Any]) -> List[PersonaBaseline]:
        """Create persona baselines from profile and configuration"""
        baselines = []
        dimension_configs = self.config["persona_agent"]["persona_dimensions"]
        
        for dimension_name, config in dimension_configs.items():
            try:
                dimension = PersonaDimension(dimension_name)
            except ValueError:
                continue
            
            # Use profile-specific characteristics if available, otherwise use defaults
            profile_characteristics = persona_profile.get(dimension_name, config["baseline_characteristics"])
            
            baseline = PersonaBaseline(
                dimension=dimension,
                baseline_characteristics=profile_characteristics,
                tolerance_threshold=config["tolerance_threshold"],
                weight=config["weight"],
                validation_methods=config["validation_methods"]
            )
            baselines.append(baseline)
        
        return baselines
    
    def _create_drift_indicators(self, archetype: str) -> List[DriftIndicator]:
        """Create drift indicators based on recipient archetype"""
        indicators = []
        
        # Base indicators for all archetypes
        base_indicators = [
            DriftIndicator(
                dimension=PersonaDimension.COMMUNICATION_STYLE,
                indicator_type="formality_shift",
                detection_method="formality_analysis",
                threshold_value=0.3,
                severity_weight=0.3
            ),
            DriftIndicator(
                dimension=PersonaDimension.TONE_AND_VOICE,
                indicator_type="sentiment_drift",
                detection_method="sentiment_analysis",
                threshold_value=0.25,
                severity_weight=0.25
            ),
            DriftIndicator(
                dimension=PersonaDimension.PROFESSIONAL_LEVEL,
                indicator_type="professionalism_variance",
                detection_method="professionalism_scoring",
                threshold_value=0.2,
                severity_weight=0.2
            )
        ]
        
        indicators.extend(base_indicators)
        
        # Add archetype-specific indicators
        if archetype == "executive":
            indicators.extend([
                DriftIndicator(
                    dimension=PersonaDimension.LEADERSHIP_APPROACH,
                    indicator_type="strategic_language_drift",
                    detection_method="strategic_language_analysis",
                    threshold_value=0.15,
                    severity_weight=0.15
                ),
                DriftIndicator(
                    dimension=PersonaDimension.EXPERTISE_DOMAIN,
                    indicator_type="business_focus_variance",
                    detection_method="business_focus_analysis",
                    threshold_value=0.2,
                    severity_weight=0.1
                )
            ])
        elif archetype == "technical_lead":
            indicators.extend([
                DriftIndicator(
                    dimension=PersonaDimension.EXPERTISE_DOMAIN,
                    indicator_type="technical_language_drift",
                    detection_method="technical_language_analysis",
                    threshold_value=0.15,
                    severity_weight=0.2
                ),
                DriftIndicator(
                    dimension=PersonaDimension.COMMUNICATION_STYLE,
                    indicator_type="technical_clarity_variance",
                    detection_method="technical_clarity_scoring",
                    threshold_value=0.25,
                    severity_weight=0.15
                )
            ])
        elif archetype == "hiring_manager":
            indicators.extend([
                DriftIndicator(
                    dimension=PersonaDimension.COLLABORATION_STYLE,
                    indicator_type="team_language_drift",
                    detection_method="team_language_analysis",
                    threshold_value=0.2,
                    severity_weight=0.15
                ),
                DriftIndicator(
                    dimension=PersonaDimension.LEADERSHIP_APPROACH,
                    indicator_type="mentoring_focus_variance",
                    detection_method="mentoring_focus_analysis",
                    threshold_value=0.25,
                    severity_weight=0.1
                )
            ])
        
        return indicators
    
    def _define_validation_triggers(self, archetype: str) -> List[ValidationTrigger]:
        """Define validation triggers based on archetype"""
        base_triggers = [
            ValidationTrigger.PRE_EXECUTION,
            ValidationTrigger.POST_GENERATION,
            ValidationTrigger.MANUAL_REQUEST
        ]
        
        # Add archetype-specific triggers
        if archetype == "executive":
            base_triggers.append(ValidationTrigger.ARCHETYPE_CHANGE)
        elif archetype == "technical_lead":
            base_triggers.append(ValidationTrigger.CONTEXT_SHIFT)
        
        return base_triggers
    
    def _define_pre_execution_checks(self, archetype: str) -> List[str]:
        """Define pre-execution persona checks"""
        base_checks = [
            "communication_style_validation",
            "tone_consistency_check",
            "professional_level_verification",
            "expertise_domain_alignment"
        ]
        
        # Add archetype-specific checks
        if archetype == "executive":
            base_checks.extend([
                "strategic_language_validation",
                "business_focus_verification",
                "executive_presence_check"
            ])
        elif archetype == "technical_lead":
            base_checks.extend([
                "technical_language_validation",
                "innovation_focus_check",
                "solution_orientation_verification"
            ])
        elif archetype == "hiring_manager":
            base_checks.extend([
                "team_language_validation",
                "collaboration_style_check",
                "mentoring_approach_verification"
            ])
        
        return base_checks
    
    def _define_post_generation_validations(self, archetype: str) -> List[str]:
        """Define post-generation persona validations"""
        base_validations = [
            "overall_consistency_score",
            "dimension_drift_analysis",
            "language_pattern_verification",
            "tone_drift_detection"
        ]
        
        # Add archetype-specific validations
        if archetype == "executive":
            base_validations.extend([
                "strategic_consistency_check",
                "business_message_alignment",
                "leadership_voice_maintenance"
            ])
        elif archetype == "technical_lead":
            base_validations.extend([
                "technical_consistency_verification",
                "innovation_language_maintenance",
                "solution_clarity_validation"
            ])
        elif archetype == "hiring_manager":
            base_validations.extend([
                "team_consistency_check",
                "collaboration_language_maintenance",
                "mentoring_tone_validation"
            ])
        
        return base_validations
    
    def _define_drift_correction_strategies(self, archetype: str) -> Dict[str, str]:
        """Define drift correction strategies"""
        base_strategies = {
            "low_drift": "gentle_realignment",
            "medium_drift": "targeted_correction",
            "high_drift": "comprehensive_reset",
            "critical_drift": "emergency_intervention"
        }
        
        # Add archetype-specific strategies
        if archetype == "executive":
            base_strategies.update({
                "strategic_drift": "executive_voice_reinforcement",
                "business_focus_drift": "business_language_recentering"
            })
        elif archetype == "technical_lead":
            base_strategies.update({
                "technical_drift": "technical_voice_recalibration",
                "innovation_drift": "innovation_language_reinforcement"
            })
        elif archetype == "hiring_manager":
            base_strategies.update({
                "team_drift": "collaborative_voice_recentering",
                "mentoring_drift": "mentoring_language_reinforcement"
            })
        
        return base_strategies
    
    def _prioritize_validations(self, archetype: str) -> List[str]:
        """Prioritize validation checks based on archetype"""
        base_priority = [
            "communication_style_validation",
            "tone_consistency_check",
            "professional_level_verification",
            "expertise_domain_alignment",
            "leadership_approach_validation",
            "collaboration_style_check"
        ]
        
        # Adjust priority based on archetype
        if archetype == "executive":
            base_priority = [
                "professional_level_verification",
                "leadership_approach_validation",
                "communication_style_validation",
                "tone_consistency_check",
                "expertise_domain_alignment",
                "collaboration_style_check"
            ]
        elif archetype == "technical_lead":
            base_priority = [
                "expertise_domain_alignment",
                "communication_style_validation",
                "tone_consistency_check",
                "professional_level_verification",
                "leadership_approach_validation",
                "collaboration_style_check"
            ]
        elif archetype == "hiring_manager":
            base_priority = [
                "collaboration_style_check",
                "leadership_approach_validation",
                "communication_style_validation",
                "tone_consistency_check",
                "professional_level_verification",
                "expertise_domain_alignment"
            ]
        
        return base_priority
    
    def _calculate_consistency_score(
        self,
        persona_profile: Dict[str, Any],
        archetype: str
    ) -> float:
        """Calculate expected persona consistency score"""
        # Base consistency scores by archetype
        base_scores = {
            "executive": 0.85,
            "hiring_manager": 0.80,
            "technical_lead": 0.80,
            "recruiter": 0.75,
            "influencer": 0.70,
            "peer": 0.70
        }
        
        base_score = base_scores.get(archetype, 0.70)
        
        # Adjust based on persona profile completeness
        profile_dimensions = len(persona_profile.keys())
        total_dimensions = len(PersonaDimension)
        completeness_factor = profile_dimensions / total_dimensions
        
        # Adjust based on profile specificity
        specificity_factor = 0.0
        for dimension, characteristics in persona_profile.items():
            if isinstance(characteristics, list) and len(characteristics) > 2:
                specificity_factor += 0.1
        
        specificity_factor = min(specificity_factor, 0.2)
        
        # Calculate final score
        final_score = base_score * (0.8 + 0.15 * completeness_factor + 0.05 * specificity_factor)
        
        return min(final_score, 1.0)
    
    def _define_dimension_requirements(self, archetype: str) -> Tuple[List[PersonaDimension], List[PersonaDimension]]:
        """Define required and optional persona dimensions based on archetype"""
        required = [
            PersonaDimension.COMMUNICATION_STYLE,
            PersonaDimension.TONE_AND_VOICE,
            PersonaDimension.PROFESSIONAL_LEVEL
        ]
        
        optional = [
            PersonaDimension.EXPERTISE_DOMAIN,
            PersonaDimension.LEADERSHIP_APPROACH,
            PersonaDimension.COLLABORATION_STYLE
        ]
        
        # Adjust based on archetype
        if archetype == "executive":
            required.append(PersonaDimension.LEADERSHIP_APPROACH)
            required.append(PersonaDimension.EXPERTISE_DOMAIN)
        elif archetype == "technical_lead":
            required.append(PersonaDimension.EXPERTISE_DOMAIN)
        elif archetype == "hiring_manager":
            required.append(PersonaDimension.COLLABORATION_STYLE)
            required.append(PersonaDimension.LEADERSHIP_APPROACH)
        
        return required, optional
    
    def validate_plan(self, plan: PersonaConsistencyPlan) -> List[str]:
        """
        Validate persona consistency plan for completeness and correctness
        
        Args:
            plan: Persona consistency plan to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not plan.mission_context:
            errors.append("mission_context is required")
        
        if not plan.recipient_archetype:
            errors.append("recipient_archetype is required")
        
        if not plan.sender_persona_profile:
            errors.append("sender_persona_profile is required")
        
        if not plan.persona_baselines:
            errors.append("persona_baselines cannot be empty")
        
        if not plan.drift_indicators:
            errors.append("drift_indicators cannot be empty")
        
        if not plan.plan_id:
            errors.append("plan_id is required")
        
        if plan.expected_consistency_score < 0.0 or plan.expected_consistency_score > 1.0:
            errors.append("expected_consistency_score must be between 0.0 and 1.0")
        
        if not plan.pre_execution_checks:
            errors.append("pre_execution_checks cannot be empty")
        
        if not plan.post_generation_validations:
            errors.append("post_generation_validations cannot be empty")
        
        return errors
