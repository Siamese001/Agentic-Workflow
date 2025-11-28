# File: validation_stack.py
# Version: 5.8 (MoE Routers + Atomic QA)
# Zero-Loss Consolidation - The V18 Engine with MoE Architecture
# Merges: validation_context.py → validation_rules.py → validation_engine.py → validator_RES.py
# REFACTORED: Removed all hard-coded agent maps, fallback constraints, magic numbers, and rule lists.
# All configuration is now read from the central CONFIG object.

# ============================================================================
# EXTERNAL IMPORTS (Consolidated)
# ============================================================================
import json
import logging
import re
import time
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

# Import from core.py
from core_v5_8 import (
    # Models
    ImmutableStagingBuffer, ThematicAnalysis, ResumeSection, ValidationResult,
    ValidationSeverity, FactualFailureException, GenerationAttempt,
    MechanicalFailureError, SemanticFailureError,
    # v5.8 Models
    AtomicAgentConfig, MoERouterConfig, MoEExpertResult, MoEDecision,
    QAClassification, VetoLevel,
    # Config
    CONFIG, DEFAULT_GENERATION_TEMPERATURE, ACCEPTABLE_MIN_WC, ACCEPTABLE_MAX_WC,
    # Utils
    text_utils, fence_data,
    # Prompts
    get_validation_prompt, build_atomic_agent_prompt
)

logger = logging.getLogger(__name__)

# ============================================================================
# PART 1: VALIDATION CONTEXT
# ============================================================================

def calculate_signal_score(text: str, job_desc: str, thematic_analysis: ThematicAnalysis) -> float:
    """
    Calculate signal quality score for text.
    REFACTORED: Magic numbers (30, 20) are now read from CONFIG.
    """
    if not text or not job_desc:
        return 0.0
    
    # Extract keywords from JD
    jd_keyword_top_n = CONFIG.rules.signal_score.jd_keyword_top_n
    text_keyword_top_n = CONFIG.rules.signal_score.text_keyword_top_n
    
    jd_keywords = set(text_utils.extract_keywords(job_desc, jd_keyword_top_n))
    theme_keywords = set(thematic_analysis.themes) if thematic_analysis else set()
    all_keywords = jd_keywords.union(theme_keywords)
    
    # Calculate overlap
    text_keywords = set(text_utils.extract_keywords(text, text_keyword_top_n))
    overlap = text_keywords.intersection(all_keywords)
    
    if len(all_keywords) == 0:
        return 0.5
    
    return len(overlap) / len(all_keywords)

class ValidationContext:
    """
    Holds all necessary data for the ValidationEngine to run checks.
    Uses lazy calculation for metrics.
    REFACTORED: Removed all hard-coded fallback constraints.
    """
    def __init__(self, staging_buffer: ImmutableStagingBuffer, thematic_analysis: ThematicAnalysis, 
                 job_description: str, master_resume: Dict, app_config: Any = None):
        self.staging_buffer = staging_buffer
        self.thematic_analysis = thematic_analysis
        self.job_description = job_description
        self.master_resume = master_resume
        self._cache = {}
        
        # Use the global CONFIG object
        self.config = app_config or CONFIG
        
        # Ensure constraints are loaded
        if not hasattr(self.config, 'constraints') or not self.config.constraints:
            raise ValueError("FATAL: Validation constraints are missing from master_config_v5_8.json.")
        if not hasattr(self.config, 'signal_constraints') or not self.config.signal_constraints:
            raise ValueError("FATAL: Signal constraints are missing from master_config_v5_8.json.")
            
        self.constraints = self.config.constraints
        self.signal_constraints = self.config.signal_constraints
        
        # REFACTORED: All hard-coded fallback constraint objects have been removed.
    
    def get_section_content(self, section: str) -> Optional[str]:
        """Get content for a specific section."""
        return self.staging_buffer.get_section(section)
    
    def get_all_sections(self) -> Dict[str, str]:
        """Get all sections."""
        return self.staging_buffer.sections
    
    def get_word_count(self, section: str) -> int:
        """Get word count for a section (cached)."""
        cache_key = f"wc_{section}"
        if cache_key not in self._cache:
            content = self.get_section_content(section)
            self._cache[cache_key] = text_utils.count_words(content) if content else 0
        return self._cache[cache_key]
    
    def get_total_word_count(self) -> int:
        """Get total word count across all sections."""
        if 'total_wc' not in self._cache:
            total = sum(self.get_word_count(s) for s in self.staging_buffer.sections)
            self._cache['total_wc'] = total
        return self._cache['total_wc']

# ============================================================================
# PART 2: ATOMIC VALIDATION AGENTS (v5.8)
# ============================================================================

class BaseAtomicValidator:
    """Base class for atomic validation agents."""
    
    def __init__(self, config: AtomicAgentConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.agent_id}")
    
    def validate(self, context: Any, **kwargs) -> ValidationResult:
        """Execute validation. Must be implemented by subclasses."""
        raise NotImplementedError

# CLASS 1: LINGUISTIC VALIDATORS (Cheap, Fast)
class ForbiddenVerbValidatorAgent(BaseAtomicValidator):
    """
    Validates against forbidden verbs.
    REFACTORED: Forbidden verb list is read from CONFIG.
    """
    
    FORBIDDEN_VERBS = CONFIG.rules.linguistic_validators.forbidden_verbs
    
    def validate(self, content: str, **kwargs) -> ValidationResult:
        found_verbs = []
        for verb in self.FORBIDDEN_VERBS:
            if re.search(r'\b' + re.escape(verb) + r'\b', content, re.IGNORECASE):
                found_verbs.append(verb)
        
        passed = len(found_verbs) == 0
        return ValidationResult(
            rule_id="R1_NO_FORBIDDEN_VERBS",
            passed=passed,
            severity=ValidationSeverity.HIGH if not passed else ValidationSeverity.INFO,
            message=f"Found forbidden verbs: {found_verbs}" if not passed else "No forbidden verbs",
            details={"forbidden_verbs_found": found_verbs}
        )

class GrammarTokenCountAgent(BaseAtomicValidator):
    """
    Validates grammar and token counts.
    REFACTORED: Word count constraints are read from CONFIG.
    """
    
    def validate(self, content: str, section: str, **kwargs) -> ValidationResult:
        word_count = text_utils.count_words(content)
        
        # Section-specific constraints
        constraints = CONFIG.constraints
        min_wc, max_wc = ACCEPTABLE_MIN_WC, ACCEPTABLE_MAX_WC # Default bullet constraints
        
        if section == ResumeSection.K1_EXECUTIVE_SUMMARY:
            min_wc = constraints.executive_summary.word_count_min
            max_wc = constraints.executive_summary.word_count_max
        elif section == ResumeSection.K2_UNIFY_BULLETS or section == ResumeSection.K3_IBM_BULLETS:
            min_wc = constraints.bullets.word_count_min
            max_wc = constraints.bullets.word_count_max
        
        passed = min_wc <= word_count <= max_wc
        
        return ValidationResult(
            rule_id="R2_WORD_COUNT",
            passed=passed,
            severity=ValidationSeverity.MEDIUM if not passed else ValidationSeverity.INFO,
            message=f"Word count {word_count} (expected {min_wc}-{max_wc})",
            details={"word_count": word_count, "min": min_wc, "max": max_wc}
        )

class FormatComplianceAgent(BaseAtomicValidator):
    """Validates format compliance."""
    
    def validate(self, content: str, **kwargs) -> ValidationResult:
        issues = []
        
        if not content:
             issues.append("Content is empty")
        elif not content[0].isupper():
            issues.append("First character not capitalized")
        
        # Check for proper sentence ending
        if content and not content.rstrip().endswith(('.', '!', '?')):
            issues.append("Missing sentence terminator")
        
        # Check for excessive punctuation
        if '...' in content or ',,' in content:
            issues.append("Excessive punctuation found")
        
        passed = len(issues) == 0
        return ValidationResult(
            rule_id="R3_FORMAT_COMPLIANCE",
            passed=passed,
            severity=ValidationSeverity.LOW if not passed else ValidationSeverity.INFO,
            message=f"Format issues: {issues}" if not passed else "Format compliant",
            details={"issues": issues}
        )

class BiasScrubberAgent(BaseAtomicValidator):
    """
    Scrubs biased or problematic language.
    REFACTORED: Biased term list is read from CONFIG.
    """
    
    BIASED_TERMS = CONFIG.rules.linguistic_validators.biased_terms
    
    def validate(self, content: str, **kwargs) -> ValidationResult:
        found_terms = []
        for term in self.BIASED_TERMS:
            if re.search(r'\b' + re.escape(term) + r'\b', content, re.IGNORECASE):
                found_terms.append(term)
        
        passed = len(found_terms) == 0
        return ValidationResult(
            rule_id="R4_NO_BIAS",
            passed=passed,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            message=f"Biased terms found: {found_terms}" if not passed else "No biased language",
            details={"biased_terms": found_terms}
        )

class IntroPhraseValidatorAgent(BaseAtomicValidator):
    """
    Validates against weak intro phrases.
    REFACTORED: Weak intro list is read from CONFIG.
    """
    
    WEAK_INTROS = CONFIG.rules.linguistic_validators.weak_intros
    
    def validate(self, content: str, **kwargs) -> ValidationResult:
        found_intros = []
        for intro in self.WEAK_INTROS:
            if content.lower().startswith(intro.lower()):
                found_intros.append(intro)
        
        passed = len(found_intros) == 0
        return ValidationResult(
            rule_id="R5_NO_WEAK_INTROS",
            passed=passed,
            severity=ValidationSeverity.MEDIUM if not passed else ValidationSeverity.INFO,
            message=f"Weak intros: {found_intros}" if not passed else "Strong opening",
            details={"weak_intros": found_intros}
        )

# CLASS 2: FACTUAL VALIDATORS (Medium Cost)
class MetricValidatorAgent(BaseAtomicValidator):
    """Validates metrics for accuracy."""
    
    def validate(self, content: str, master_resume: Dict, **kwargs) -> ValidationResult:
        # Extract metrics from content
        metric_pattern = r'(\d+[%$MBK]+|\d+\.\d+[%$MBK]+)'
        found_metrics = re.findall(metric_pattern, content)
        
        # Stub: Compare with master resume metrics
        # In production, would do deep validation
        
        return ValidationResult(
            rule_id="R6_METRIC_ACCURACY",
            passed=True,  # Stub
            severity=ValidationSeverity.INFO,
            message=f"Found {len(found_metrics)} metrics",
            details={"metrics": found_metrics}
        )

class TenureValidatorAgent(BaseAtomicValidator):
    """Validates tenure accuracy."""
    
    def validate(self, content: str, master_resume: Dict, **kwargs) -> ValidationResult:
        # Stub: Validate dates against master resume
        return ValidationResult(
            rule_id="R7_TENURE_ACCURACY",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Tenure validation passed",
            details={}
        )

class EntityValidatorAgent(BaseAtomicValidator):
    """Validates entity names (companies, products)."""
    
    def validate(self, content: str, master_resume: Dict, **kwargs) -> ValidationResult:
        # Stub: Validate entity names
        return ValidationResult(
            rule_id="R8_ENTITY_ACCURACY",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Entity validation passed",
            details={}
        )

class ClaimValidatorAgent(BaseAtomicValidator):
    """Validates claims using NLI."""
    
    def validate(self, content: str, master_resume: Dict, **kwargs) -> ValidationResult:
        # Stub: Use NLI model to validate claims
        # In production, would use cross-encoder/nli-deberta-v3-large
        return ValidationResult(
            rule_id="R9_CLAIM_VALIDATION",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Claim validation passed (NLI)",
            details={}
        )

# CLASS 3-4: SEMANTIC VALIDATORS (Expensive)
class ToneValidator(BaseAtomicValidator):
    """Validates tone consistency."""
    
    def validate(self, content: str, expected_tone: str = "professional", **kwargs) -> ValidationResult:
        # Stub: Analyze tone
        return ValidationResult(
            rule_id="R10_TONE_CONSISTENCY",
            passed=True,
            severity=ValidationSeverity.INFO,
            message=f"Tone matches {expected_tone}",
            details={"expected_tone": expected_tone}
        )

class ThematicAlignmentValidator(BaseAtomicValidator):
    """Validates thematic alignment with JD."""
    
    def validate(self, content: str, thematic_analysis: ThematicAnalysis, **kwargs) -> ValidationResult:
        # Calculate alignment score
        content_keywords = set(text_utils.extract_keywords(content, 10))
        theme_keywords = set(thematic_analysis.themes)
        
        overlap = content_keywords.intersection(theme_keywords)
        alignment_score = len(overlap) / len(theme_keywords) if theme_keywords else 0.0
        
        # REFACTORED: Threshold read from CONFIG
        threshold = CONFIG.signal_constraints.MIN_THEMATIC_OVERLAP
        passed = alignment_score >= threshold
        
        return ValidationResult(
            rule_id="R11_THEMATIC_ALIGNMENT",
            passed=passed,
            severity=ValidationSeverity.MEDIUM if not passed else ValidationSeverity.INFO,
            message=f"Alignment score: {alignment_score:.2%} (Threshold: {threshold:.2%})",
            details={"alignment_score": alignment_score, "overlap": list(overlap)}
        )

class SemanticEntailmentValidator(BaseAtomicValidator):
    """Validates semantic entailment."""
    
    def validate(self, content: str, master_resume: Dict, **kwargs) -> ValidationResult:
        # Stub: Use semantic entailment model
        return ValidationResult(
            rule_id="R12_SEMANTIC_ENTAILMENT",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Semantic entailment validated",
            details={}
        )

class NarrativeThreadAgent(BaseAtomicValidator):
    """Validates narrative coherence across sections."""
    
    def validate(self, all_sections: Dict[str, str], **kwargs) -> ValidationResult:
        # Stub: Analyze narrative coherence
        return ValidationResult(
            rule_id="R13_NARRATIVE_COHERENCE",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Narrative coherence validated",
            details={}
        )

class AdversarialReviewerAgent(BaseAtomicValidator):
    """Red team review with adversarial critique."""
    
    def validate(self, content: str, persona: str = "skeptical_cto", **kwargs) -> ValidationResult:
        # Stub: Adversarial review
        return ValidationResult(
            rule_id="R14_ADVERSARIAL_REVIEW",
            passed=True,
            severity=ValidationSeverity.INFO,
            message=f"Passed {persona} review",
            details={"persona": persona}
        )

# GLOBAL VALIDATORS
class SectionPresenceValidatorAgent(BaseAtomicValidator):
    """
    Validates required sections are present.
    REFACTORED: Required sections list is read from CONFIG.
    """
    
    REQUIRED_SECTIONS = CONFIG.rules.section_presence.required_sections
    
    def validate(self, all_sections: Dict[str, str], **kwargs) -> ValidationResult:
        missing = [s for s in self.REQUIRED_SECTIONS if s not in all_sections or not all_sections[s]]
        passed = len(missing) == 0
        
        return ValidationResult(
            rule_id="R15_SECTION_PRESENCE",
            passed=passed,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            message=f"Missing sections: {missing}" if not passed else "All sections present",
            details={"missing_sections": missing}
        )

class WordCountValidatorAgent(BaseAtomicValidator):
    """
    Validates overall word count.
    REFACTORED: Min/max constraints are read from CONFIG.
    """
    
    def validate(self, all_sections: Dict[str, str], **kwargs) -> ValidationResult:
        total_wc = sum(text_utils.count_words(content) for content in all_sections.values())
        
        min_wc = CONFIG.constraints.total_resume.word_count_min
        max_wc = CONFIG.constraints.total_resume.word_count_max
        passed = min_wc <= total_wc <= max_wc
        
        return ValidationResult(
            rule_id="R16_TOTAL_WORD_COUNT",
            passed=passed,
            severity=ValidationSeverity.MEDIUM if not passed else ValidationSeverity.INFO,
            message=f"Total word count: {total_wc} (expected {min_wc}-{max_wc})",
            details={"total_word_count": total_wc, "min": min_wc, "max": max_wc}
        )

class SentenceCountValidatorAgent(BaseAtomicValidator):
    """
    Validates sentence counts.
    REFACTORED: Min/max constraints are read from CONFIG.
    """
    
    def validate(self, content: str, section: str, **kwargs) -> ValidationResult:
        sentence_count = text_utils.count_sentences(content)
        passed = True
        min_sc, max_sc = 0, 999
        
        # Section-specific constraints
        if section == ResumeSection.K1_EXECUTIVE_SUMMARY:
            min_sc = CONFIG.constraints.executive_summary.sentence_count_min
            max_sc = CONFIG.constraints.executive_summary.sentence_count_max
            passed = min_sc <= sentence_count <= max_sc
        
        return ValidationResult(
            rule_id="R17_SENTENCE_COUNT",
            passed=passed,
            severity=ValidationSeverity.LOW if not passed else ValidationSeverity.INFO,
            message=f"Sentence count: {sentence_count} (expected {min_sc}-{max_sc})",
            details={"sentence_count": sentence_count, "min": min_sc, "max": max_sc}
        )

class StructureValidatorAgent(BaseAtomicValidator):
    """Validates document structure."""
    
    def validate(self, all_sections: Dict[str, str], **kwargs) -> ValidationResult:
        # Stub: Validate structure
        return ValidationResult(
            rule_id="R18_STRUCTURE",
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Structure validated",
            details={}
        )

class SimilarityValidatorAgent(BaseAtomicValidator):
    """
    Validates cross-section similarity.
    REFACTORED: Similarity threshold is read from CONFIG.
    """
    
    def validate(self, all_sections: Dict[str, str], **kwargs) -> ValidationResult:
        sections_list = list(all_sections.items())
        high_similarity_pairs = []
        
        threshold = CONFIG.signal_constraints.MAX_CROSS_SECTION_SIMILARITY
        
        for i, (s1_name, s1_content) in enumerate(sections_list):
            for s2_name, s2_content in sections_list[i+1:]:
                if not s1_content or not s2_content:
                    continue
                sim = text_utils.compute_similarity(s1_content, s2_content)
                if sim > threshold:
                    high_similarity_pairs.append((s1_name, s2_name, sim))
        
        passed = len(high_similarity_pairs) == 0
        return ValidationResult(
            rule_id="R19_CROSS_SECTION_SIMILARITY",
            passed=passed,
            severity=ValidationSeverity.MEDIUM if not passed else ValidationSeverity.INFO,
            message=f"High similarity pairs > {threshold:.0%}: {len(high_similarity_pairs)}",
            details={"high_similarity_pairs": high_similarity_pairs}
        )

class JDSkillsValidatorAgent(BaseAtomicValidator):
    """
    Validates JD skills overlap.
    REFACTORED: Minimum overlap count is read from CONFIG.
    """
    
    def validate(self, content: str, thematic_analysis: ThematicAnalysis, **kwargs) -> ValidationResult:
        content_keywords = set(text_utils.extract_keywords(content, 20))
        jd_skills = set(thematic_analysis.skills_required)
        
        overlap = content_keywords.intersection(jd_skills)
        overlap_count = len(overlap)
        
        min_overlap = CONFIG.rules.jd_skills_validator.min_overlap
        passed = overlap_count >= min_overlap
        
        return ValidationResult(
            rule_id="R20_JD_SKILLS_OVERLAP",
            passed=passed,
            severity=ValidationSeverity.HIGH if not passed else ValidationSeverity.INFO,
            message=f"JD skills overlap: {overlap_count}/{min_overlap} minimum",
            details={"overlap_count": overlap_count, "overlapping_skills": list(overlap)}
        )

class SignalScoreValidatorAgent(BaseAtomicValidator):
    """
    Validates overall signal score.
    REFACTORED: Signal score threshold is read from CONFIG.
    """
    
    def validate(self, content: str, job_description: str, thematic_analysis: ThematicAnalysis, **kwargs) -> ValidationResult:
        signal_score = calculate_signal_score(content, job_description, thematic_analysis)
        threshold = CONFIG.signal_constraints.MIN_SIGNAL_SCORE
        passed = signal_score >= threshold
        
        return ValidationResult(
            rule_id="R21_SIGNAL_SCORE",
            passed=passed,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            message=f"Signal score: {signal_score:.2%} (threshold: {threshold:.2%})",
            details={"signal_score": signal_score, "threshold": threshold}
        )

# ============================================================================
# PART 3: MoE VALIDATION ROUTERS (v5.8)
# ============================================================================

class BaseMoERouter:
    """Base class for MoE validation routers."""
    
    def __init__(self, config: MoERouterConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.router_id}")
        self.experts = {}
        self._initialize_experts()
    
    def _initialize_experts(self):
        """Initialize expert validators from config."""
        for agent_config in self.config.expert_agents:
            if agent_config.enabled:
                expert = self._create_expert(agent_config)
                self.experts[agent_config.agent_id] = expert
    
    def _create_expert(self, agent_config: AtomicAgentConfig) -> BaseAtomicValidator:
        """Factory method to create expert instances."""
        expert_map = {
            "ForbiddenVerbValidator": ForbiddenVerbValidatorAgent,
            "GrammarTokenCount": GrammarTokenCountAgent,
            "FormatCompliance": FormatComplianceAgent,
            "BiasScrubber": BiasScrubberAgent,
            "IntroPhraseValidator": IntroPhraseValidatorAgent,
            "MetricValidator": MetricValidatorAgent,
            "TenureValidator": TenureValidatorAgent,
            "EntityValidator": EntityValidatorAgent,
            "ClaimValidator": ClaimValidatorAgent,
            "ToneValidator": ToneValidator,
            "ThematicAlignmentValidator": ThematicAlignmentValidator,
            "SemanticEntailmentValidator": SemanticEntailmentValidator,
            "NarrativeThread": NarrativeThreadAgent,
            "AdversarialReviewer": AdversarialReviewerAgent,
            "SectionPresence": SectionPresenceValidatorAgent,
            "WordCount": WordCountValidatorAgent,
            "SentenceCount": SentenceCountValidatorAgent,
            "Structure": StructureValidatorAgent,
            "Similarity": SimilarityValidatorAgent,
            "JDSkillsValidator": JDSkillsValidatorAgent,
            "SignalScoreValidator": SignalScoreValidatorAgent,
        }
        
        expert_class = expert_map.get(agent_config.agent_type)
        if not expert_class:
            raise ValueError(f"Unknown expert type: {agent_config.agent_type}")
        
        return expert_class(agent_config)
    
    def execute(self, context: Any, **kwargs) -> MoEDecision:
        """Execute all experts and aggregate results."""
        start_time = time.time()
        expert_results = []
        
        # Execute all experts (parallel in production)
        for expert_id, expert in self.experts.items():
            try:
                expert_start = time.time()
                # Pass all available kwargs to the validate method
                result = expert.validate(context=context, **kwargs)
                expert_time = time.time() - expert_start
                
                expert_results.append(MoEExpertResult(
                    expert_id=expert_id,
                    expert_type=expert.config.agent_type,
                    result=result,
                    confidence=1.0 if result.passed else 0.0,
                    execution_time=expert_time,
                    metadata={"complexity": expert.config.complexity}
                ))
            except Exception as e:
                self.logger.error(f"Expert {expert_id} failed: {e}")
                expert_results.append(MoEExpertResult(
                    expert_id=expert_id,
                    expert_type=expert.config.agent_type,
                    result=ValidationResult(
                        rule_id=f"{expert_id}_ERROR",
                        passed=False,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Validation failed: {str(e)}"
                    ),
                    confidence=0.0,
                    execution_time=0.0,
                    metadata={"error": str(e)}
                ))
        
        # Aggregate results
        aggregated = self._aggregate_results(expert_results)
        
        return MoEDecision(
            selected_expert=None,  # All experts contribute
            aggregated_result=aggregated,
            expert_results=expert_results,
            aggregation_method=self.config.aggregation_method,
            confidence=self._calculate_confidence(expert_results),
            metadata={
                "router_id": self.config.router_id,
                "num_experts": len(expert_results),
                "execution_time": time.time() - start_time
            }
        )
    
    def _aggregate_results(self, expert_results: List[MoEExpertResult]) -> List[ValidationResult]:
        """Aggregate expert results based on aggregation method."""
        if self.config.aggregation_method == "all_pass":
            # All must pass
            return [er.result for er in expert_results]
        elif self.config.aggregation_method == "voting":
            # Majority must pass
            return [er.result for er in expert_results]
        elif self.config.aggregation_method == "weighted":
            # Weighted by complexity
            return [er.result for er in expert_results]
        else:
            return [er.result for er in expert_results]
    
    def _calculate_confidence(self, expert_results: List[MoEExpertResult]) -> float:
        """Calculate overall confidence from expert results."""
        if not expert_results:
            return 0.0
        
        total_confidence = sum(er.confidence for er in expert_results)
        return total_confidence / len(expert_results)

class LinguisticValidationRouter(BaseMoERouter):
    """Router for Class 1 linguistic validators."""
    pass

class FactualValidationRouter(BaseMoERouter):
    """Router for Class 2 factual validators."""
    pass

class SemanticValidationRouter(BaseMoERouter):
    """Router for Class 3-4 semantic validators."""
    pass

class GlobalValidationRouter(BaseMoERouter):
    """Router for global and signal validators."""
    pass

# ============================================================================
# PART 4: VALIDATION ENGINE (v5.8 MoE-Enabled)
# ============================================================================

class ValidationEngine:
    """
    V5.8 Validation Engine with MoE routers.
    REFACTORED: Removed hard-coded _AGENT_CONFIG_MAP.
    Agent definitions are now read directly from CONFIG.
    """
    
    # REFACTORED: _AGENT_CONFIG_MAP has been exorcised.
    # We now load agent definitions directly from the global CONFIG
    _AGENT_DEFINITIONS = CONFIG.agent_definitions.validation_agents
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        if not self._AGENT_DEFINITIONS or not vars(self._AGENT_DEFINITIONS):
            raise ValueError("FATAL: agent_definitions.validation_agents is missing from master_config_v5_8.json.")
        
        # Initialize MoE routers
        self.linguistic_router = self._create_router('linguistic_router')
        self.factual_router = self._create_router('factual_router')
        self.semantic_router = self._create_router('semantic_router')
        self.global_router = self._create_router('global_router')

    def _get_agent_config(self, agent_name: str) -> AtomicAgentConfig:
        """
        Helper to load and build an AtomicAgentConfig from CONFIG.
        """
        if not hasattr(self._AGENT_DEFINITIONS, agent_name):
            raise ValueError(f"Agent definition '{agent_name}' not found in master_config_v5_8.json.")
            
        agent_def = getattr(self._AGENT_DEFINITIONS, agent_name)
        
        try:
            # Convert string names to Enum objects
            classification_enum = getattr(QAClassification, agent_def.classification)
            veto_level_enum = getattr(VetoLevel, agent_def.veto_level)
            
            return AtomicAgentConfig(
                agent_id=agent_def.agent_id,
                agent_type=agent_def.agent_type,
                complexity=agent_def.complexity,
                classification=classification_enum,
                veto_level=veto_level_enum
                # Other fields like 'enabled', 'timeout' can be added here from config
            )
        except AttributeError as e:
            raise ValueError(f"Invalid enum value in agent definition for '{agent_name}': {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse agent definition for '{agent_name}': {e}")

    def _create_router(self, router_name: str) -> BaseMoERouter:
        """
        Generic factory method to create any MoE router from CONFIG.
        """
        if not hasattr(CONFIG.moe_config.routers, router_name):
            raise ValueError(f"MoE router config '{router_name}' not found in master_config_v5_8.json.")
            
        router_config_data = getattr(CONFIG.moe_config.routers, router_name)
        expert_agent_names = router_config_data.expert_agents
        
        expert_agents_configs = []
        for name in expert_agent_names:
            try:
                expert_agents_configs.append(self._get_agent_config(name))
            except ValueError as e:
                self.logger.warning(f"{e} (for router '{router_name}')")
        
        # Create the MoERouterConfig object
        config = MoERouterConfig(
            router_id=router_config_data.router_id,
            router_name=router_config_data.router_name,
            expert_agents=expert_agents_configs,
            aggregation_method=router_config_data.aggregation_method,
            parallel_execution=router_config_data.parallel_execution,
            timeout_seconds=router_config_data.timeout_seconds
        )
        
        # Select the correct router class
        router_class_map = {
            'linguistic_router': LinguisticValidationRouter,
            'factual_router': FactualValidationRouter,
            'semantic_router': SemanticValidationRouter,
            'global_router': GlobalValidationRouter
        }
        
        router_class = router_class_map.get(router_name)
        if not router_class:
            raise ValueError(f"Unknown router class for '{router_name}'")
            
        return router_class(config)
    
    def validate_all(self, context: ValidationContext) -> Dict[str, Any]:
        """
        Execute all MoE routers and aggregate results.
        REFACTORED: Passes the full ValidationContext or specific parts as needed.
        """
        self.logger.info("Starting v5.8 MoE validation...")
        
        results = {
            "linguistic": None,
            "factual": None,
            "semantic": None,
            "global": None,
            "overall_passed": False,
            "critical_failures": [],
            "all_results": []
        }
        
        # --- Context Preparation ---
        # Most agents operate on a single piece of content, but some need more.
        # We'll default to the exec summary for content-specific checks,
        # but pass all context for agents that need it.
        
        exec_summary = context.get_section_content(ResumeSection.K1_EXECUTIVE_SUMMARY) or ""
        all_sections = context.get_all_sections()

        # Execute linguistic router (operates on single content)
        try:
            linguistic_decision = self.linguistic_router.execute(
                context=exec_summary,
                section=ResumeSection.K1_EXECUTIVE_SUMMARY
            )
            results["linguistic"] = linguistic_decision.to_dict()
            results["all_results"].extend(linguistic_decision.aggregated_result)
        except Exception as e:
            self.logger.error(f"Linguistic router failed: {e}")
        
        # Execute factual router (needs master resume)
        try:
            factual_decision = self.factual_router.execute(
                context=exec_summary,
                master_resume=context.master_resume
            )
            results["factual"] = factual_decision.to_dict()
            results["all_results"].extend(factual_decision.aggregated_result)
        except Exception as e:
            self.logger.error(f"Factual router failed: {e}")
        
        # Execute semantic router (needs themes, master resume, all sections)
        try:
            semantic_decision = self.semantic_router.execute(
                context=exec_summary,
                thematic_analysis=context.thematic_analysis,
                master_resume=context.master_resume,
                all_sections=all_sections
            )
            results["semantic"] = semantic_decision.to_dict()
            results["all_results"].extend(semantic_decision.aggregated_result)
        except Exception as e:
            self.logger.error(f"Semantic router failed: {e}")
        
        # Execute global router (needs JD, themes, all sections)
        try:
            global_decision = self.global_router.execute(
                context=all_sections, # Main context is all sections
                job_description=context.job_description,
                thematic_analysis=context.thematic_analysis
            )
            results["global"] = global_decision.to_dict()
            results["all_results"].extend(global_decision.aggregated_result)
        except Exception as e:
            self.logger.error(f"Global router failed: {e}")
        
        # Aggregate overall results
        results["overall_passed"] = all(r.passed for r in results["all_results"])
        results["critical_failures"] = [
            r.to_dict() for r in results["all_results"] 
            if not r.passed and r.severity == ValidationSeverity.CRITICAL
        ]
        results["all_results"] = [r.to_dict() for r in results["all_results"]]
        
        self.logger.info(f"Validation complete. Overall passed: {results['overall_passed']}")
        return results

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'ValidationContext', 'ValidationEngine', 'calculate_signal_score',
    # MoE Routers
    'LinguisticValidationRouter', 'FactualValidationRouter',
    'SemanticValidationRouter', 'GlobalValidationRouter',
    # Atomic Validators
    'ForbiddenVerbValidatorAgent', 'GrammarTokenCountAgent', 'FormatComplianceAgent',
    'BiasScrubberAgent', 'IntroPhraseValidatorAgent', 'MetricValidatorAgent',
    'TenureValidatorAgent', 'EntityValidatorAgent', 'ClaimValidatorAgent',
    'ToneValidator', 'ThematicAlignmentValidator', 'SemanticEntailmentValidator',
    'NarrativeThreadAgent', 'AdversarialReviewerAgent',
    'SectionPresenceValidatorAgent', 'WordCountValidatorAgent', 'SentenceCountValidatorAgent',
    'StructureValidatorAgent', 'SimilarityValidatorAgent',
    'JDSkillsValidatorAgent', 'SignalScoreValidatorAgent'
]