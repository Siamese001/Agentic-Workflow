# File: config.py
# Configuration module for Resume Workflow
# Contains all configuration dataclasses and their instantiations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List, Set, Tuple

# --- GEMINI API SETUP ---
# (Moved from monolithic file)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        logging.info("✓ Gemini API configured successfully in config.py")
    else:
        logging.warning("⚠️ GEMINI_API_KEY not found in environment. API calls will fail.")
        GEMINI_AVAILABLE = False

except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Warning: google-generativeai package not installed. API calls will fail.")
# --- END GEMINI API SETUP ---


# ============================================================================
# CONFIGURATION DATACLASSES
# ============================================================================

@dataclass
class FilePathsConfig:
    """File paths for data files used by the workflow."""
    master_resume: str = "master_resume.json"
    hyphenation_rules: str = "hyphenation_rules.json"
    app_tracker_schema: str = "app_tracker_schema.json"
    artist_specs: str = "artist_specs.json"


@dataclass
class ArtistConfig:
    """Configuration for the Artist Generator (resume content generation)."""
    provenance_split_targets: Dict = field(default_factory=lambda: {
        'K2_UNIFY_BULLETS': {'Verbatim': 2, 'Customized': 3, 'Synthetic': 2},
        'K3_IBM_BULLETS': {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        'K9_COMPETENCIES': {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
    })
    bullet_word_count_ranges: Dict = field(default_factory=lambda: {
        'K2_UNIFY_BULLETS': (25, 40),
        'K3_IBM_BULLETS': (25, 40),
        'K9_COMPETENCIES': (25, 40),
    })
    narrative_config: Dict = field(default_factory=lambda: {
        'K4_TRADERSENSE_NARRATIVE': {
            "min_wc_key": 'TRADERSENSE_NARRATIVE_WORD_COUNT_MIN',
            "max_wc_key": 'TRADERSENSE_NARRATIVE_WORD_COUNT_MAX',
            "rag_signals": ["high-frequency trading", "low-latency", "risk controls", "backtesting", "FIX protocol", "cloud infrastructure"],
            "focus": "Emphasize the early adoption of cloud, low-latency systems, HFT, risk management, and quantitative analysis, linking them to broader technical leadership and system design capabilities relevant today.",
            "k0_themes": []
        },
        'K5_EY_NARRATIVE': {
            "min_wc_key": 'EY_NARRATIVE_WORD_COUNT_MIN',
            "max_wc_key": 'EY_NARRATIVE_WORD_COUNT_MAX',
            "rag_signals": [],
            "focus": "Focus on transferable executive themes and how this consulting experience built foundational capabilities relevant to current target role requirements.",
            "k0_themes": ["Leadership", "Strategic Vision", "Executive Communication", "Risk Management", "Client Advisory"]
        },
        'K6_EARLY_CAREER_NARRATIVE': {
            "min_wc_key": 'EARLY_CAREER_NARRATIVE_WORD_COUNT_MIN',
            "max_wc_key": 'EARLY_CAREER_NARRATIVE_WORD_COUNT_MAX',
            "rag_signals": ["quantitative analysis", "modeling", "data-driven", "problem-solving", "analytical foundation"],
            "focus": "Emphasize how early quantitative and actuarial work built analytical foundations that enabled transition to technology career.",
            "k0_themes": []
        },
    })


@dataclass
class ValidatorConfig:
    """Configuration for validation rules and constraints."""
    forbidden_verbs: List[str] = field(default_factory=lambda: [
        "spearheaded", "leveraged", "utilized", "facilitated",
        "orchestrated", "championed", "pioneered", "revolutionized",
        "transformed", "optimized", "enhanced", "streamlined",
        "synergized", "enabled", "empowered", "drove"
    ])
    required_sections: Set[str] = field(default_factory=lambda: {
        'K0_NAME', 'K0_CONTACT', 'K0_HEADLINE', 'K1_EXECUTIVE_SUMMARY',
        'K2_UNIFY_BULLETS', 'K2_UNIFY_OVERVIEW', 'K3_IBM_BULLETS', 'K3_IBM_OVERVIEW',
        'K4_TRADERSENSE_NARRATIVE', 'K5_EY_NARRATIVE', 'K6_EARLY_CAREER_NARRATIVE',
        'K7_EDUCATION', 'K8_CERTIFICATIONS', 'K9_COMPETENCIES', 'K10_SKILLS', 'K11_COVER_LETTER'
    })
    bullet_word_count_sections_to_check: Set[str] = field(default_factory=lambda: {
        'K2_UNIFY_BULLETS', 'K3_IBM_BULLETS', 'K9_COMPETENCIES'
    })
    provenance_split_targets: Dict = field(default_factory=lambda: {
        'K2_UNIFY_BULLETS': {'Verbatim': 2, 'Customized': 3, 'Synthetic': 2},
        'K3_IBM_BULLETS': {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
        'K9_COMPETENCIES': {'Verbatim': 2, 'Customized': 2, 'Synthetic': 2},
    })
    pipeline_status_enum: List[str] = field(default_factory=lambda: [
        "Applied", "Follow-Up", "Interview", "Rejected", "Closed", "Waiting"
    ])


@dataclass
class WebRagConfig:
    """Configuration for Web RAG (Retrieval Augmented Generation)."""
    peers_by_industry: Dict = field(default_factory=lambda: {
        "Financial Technology": ["JPMorgan", "Goldman Sachs", "Morgan Stanley", "Stripe", "Square"],
        "Healthcare": ["UnitedHealth", "CVS Health", "Anthem", "Cigna", "Humana"],
        "Retail/E-Commerce": ["Amazon", "Walmart", "Target", "Shopify", "eBay"],
        "Software/SaaS": ["Salesforce", "Oracle", "SAP", "Adobe", "Workday"],
        "Technology": ["Google", "Microsoft", "Meta", "Apple", "Amazon"]
    })


@dataclass
class EnricherConfig:
    """Configuration for data enrichment."""
    canonical_verbs: Dict = field(default_factory=lambda: {
        "led": ["led", "lead", "leading"], 
        "built": ["built", "build", "building"],
        "drove": ["drove", "drive", "driving"], 
        "launched": ["launched", "launch", "launching"],
        "scaled": ["scaled", "scale", "scaling"], 
        "delivered": ["delivered", "deliver", "delivering"],
        "achieved": ["achieved", "achieve", "achieving"], 
        "established": ["established", "establish", "establishing"],
        "managed": ["managed", "manage", "managing"], 
        "developed": ["developed", "develop", "developing"]
    })


@dataclass
class RAGConfig:
    """Configuration for RAG (Retrieval Augmented Generation) system."""
    
    model: str = "gemini-2.5-pro"
    max_tokens: int = 30000
    temperature: float = 0.7

    api_max_retries: int = 7
    api_timeout_seconds: int = 120
    api_initial_backoff_seconds: float = 2.0
    api_max_backoff_seconds: float = 64.0
    api_backoff_multiplier: float = 2.0
    api_backoff_jitter: float = 0.1

    phase_max_retries: int = 3
    phase_timeout_seconds: int = 180

    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60

    cache_dir: str = "./rag_cache"
    cache_ttl_days: int = 30

    telemetry_enabled: bool = True
    telemetry_log_dir: str = "./rag_telemetry"

    source_weights: Dict[str, float] = field(default_factory=lambda: {
        "SOURCE_JD": 1.8,
        "SOURCE_COMPANY_BLOG": 1.5,
        "SOURCE_TARGET_EMPLOYEE": 1.4,
        "SOURCE_GARTNER_MQ": 1.2,
        "SOURCE_PEER_JD": 0.8,
        "SOURCE_GENERIC_PROFILE": 0.5,
        "LOCAL_NLP": 0.2
    })
    
    def __post_init__(self):
        """Ensure source_weights is a dict, not a field factory."""
        # Note: logging is imported at the top of this file now
        
        if not isinstance(self.source_weights, dict):
            logging.warning(f"RAGConfig.__post_init__: source_weights is {type(self.source_weights)}, attempting to fix...")
            
            if hasattr(self.source_weights, 'default_factory'):
                try:
                    self.source_weights = self.source_weights.default_factory()
                    logging.info("RAGConfig.__post_init__: Successfully fixed source_weights")
                except Exception as e:
                    logging.error(f"RAGConfig.__post_init__: Could not extract dict: {e}")
                    self.source_weights = {
                        "SOURCE_JD": 1.8,
                        "SOURCE_COMPANY_BLOG": 1.5,
                        "SOURCE_TARGET_EMPLOYEE": 1.4,
                        "SOURCE_GARTNER_MQ": 1.2,
                        "SOURCE_PEER_JD": 0.8,
                        "SOURCE_GENERIC_PROFILE": 0.5,
                        "LOCAL_NLP": 0.2
                    }
            else:
                logging.error(f"RAGConfig.__post_init__: Unexpected type for source_weights. Using defaults.")
                self.source_weights = {
                    "SOURCE_JD": 1.8,
                    "SOURCE_COMPANY_BLOG": 1.5,
                    "SOURCE_TARGET_EMPLOYEE": 1.4,
                    "SOURCE_GARTNER_MQ": 1.2,
                    "SOURCE_PEER_JD": 0.8,
                    "SOURCE_GENERIC_PROFILE": 0.5,
                    "LOCAL_NLP": 0.2
                }
        
        assert isinstance(self.source_weights, dict), \
            f"RAGConfig.__post_init__: source_weights must be dict, got {type(self.source_weights)}"


@dataclass
class ReasoningConfig:
    """Configuration for reasoning strategies (CoT, ToT, Self-Consistency, Reflexion)."""
    
    cot_min_paths: int = 2
    tot_branches: int = 3
    min_tot_depth: int = 2
    self_consistency: int = 4
    reflexion: bool = True
    max_reflexion_loops: int = 3

    # Class variables for specific section configurations
    DEFAULT: ClassVar['ReasoningConfig']
    K0_HEADLINE_CONFIG: ClassVar['ReasoningConfig']
    K1_EXECUTIVE_SUMMARY_CONFIG: ClassVar['ReasoningConfig']
    K2_UNIFY_BULLETS_CONFIG: ClassVar['ReasoningConfig']
    K2_UNIFY_OVERVIEW_CONFIG: ClassVar['ReasoningConfig']
    K3_IBM_BULLETS_CONFIG: ClassVar['ReasoningConfig']
    K3_IBM_OVERVIEW_CONFIG: ClassVar['ReasoningConfig']
    K4_TRADERSENSE_NARRATIVE_CONFIG: ClassVar['ReasoningConfig']
    K5_EY_NARRATIVE_CONFIG: ClassVar['ReasoningConfig']
    K6_EARLY_CAREER_NARRATIVE_CONFIG: ClassVar['ReasoningConfig']
    K9_COMPETENCIES_CONFIG: ClassVar['ReasoningConfig']
    K10_SKILLS_CONFIG: ClassVar['ReasoningConfig']
    K11_COVER_LETTER_CONFIG: ClassVar['ReasoningConfig']


@dataclass
class ContentConstraintsConfig:
    """Content-level constraints for word counts, sentence counts, etc."""
    
    TOTAL_WORD_COUNT_MIN: int = 870
    TOTAL_WORD_COUNT_MAX: int = 1030
    MIN_JD_KEYWORDS: int = 7

    HEADLINE_WORD_COUNT_MIN: int = 8
    HEADLINE_WORD_COUNT_MAX: int = 11
    HEADLINE_COMPONENT_WORDS_MIN: int = 2
    HEADLINE_COMPONENT_WORDS_MAX: int = 4

    EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 6
    EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 7
    EXEC_SUMMARY_WORD_COUNT_MIN: int = 140
    EXEC_SUMMARY_WORD_COUNT_MAX: int = 170
    K1_MIN_DIFFERENTIATORS: int = 4

    UNIFY_OVERVIEW_WORD_COUNT_MIN: int = 25
    UNIFY_OVERVIEW_WORD_COUNT_MAX: int = 40
    IBM_OVERVIEW_WORD_COUNT_MIN: int = 25
    IBM_OVERVIEW_WORD_COUNT_MAX: int = 35

    TRADERSENSE_NARRATIVE_WORD_COUNT_MIN: int = 40
    TRADERSENSE_NARRATIVE_WORD_COUNT_MAX: int = 60
    EY_NARRATIVE_WORD_COUNT_MIN: int = 40
    EY_NARRATIVE_WORD_COUNT_MAX: int = 60
    EARLY_CAREER_NARRATIVE_WORD_COUNT_MIN: int = 50
    EARLY_CAREER_NARRATIVE_WORD_COUNT_MAX: int = 70

    UNIFY_IBM_COMBINED_PERCENT_MIN: float = 35.0
    UNIFY_IBM_COMBINED_PERCENT_MAX: float = 45.0
    UNIFY_IBM_RATIO_MIN: float = 1.1
    UNIFY_IBM_RATIO_MAX: float = 1.3

    COVER_LETTER_P1_WORD_COUNT_MIN: int = 80
    COVER_LETTER_P1_WORD_COUNT_MAX: int = 100
    COVER_LETTER_P2_WORD_COUNT_MIN: int = 90
    COVER_LETTER_P2_WORD_COUNT_MAX: int = 120
    COVER_LETTER_P3_WORD_COUNT_MIN: int = 80
    COVER_LETTER_P3_WORD_COUNT_MAX: int = 100
    COVER_LETTER_JD_RELEVANCE_THRESHOLD: float = 0.35


@dataclass
class SignalControlConfig:
    """Signal control thresholds for quality and relevance."""
    
    K1_MAX_DIFFERENTIATORS: int = 4
    RESUME_MAX_JD_KEYWORDS: int = 16
    CL_MAX_JD_SIMILARITY: float = 0.65
    SECTION_SIGNAL_SCORE_MAX: float = 0.90


@dataclass
class PromptAddendumConfig:
    """Configuration for reasoning prompt addendums."""
    
    HEADER: str = "\n\n**REASONING IMPLEMENTATION DIRECTIVES (v5.71):**\n\n"
    FOOTER: str = "\nAll directives MUST be followed in the output.\n"

    COT_DIRECTIVES: List[Tuple[int, str]] = field(default_factory=lambda: [
        (5, "• MANDATORY: Explore at least {cot} distinct reasoning paths before reaching a conclusion.\n"),
        (4, "• Explore {cot} different reasoning paths; compare and synthesize insights.\n"),
        (0, "• Consider multiple reasoning approaches before concluding.\n")
    ])

    TOT_B_DIRECTIVES: List[Tuple[int, str]] = field(default_factory=lambda: [
        (5, "• MANDATORY: At each decision point, systematically evaluate {tot_b} different branches/alternatives.\n"),
        (4, "• Explore {tot_b} decision branches at critical junctures; document tradeoffs.\n"),
        (0, "• Consider multiple decision branches at key steps.\n")
    ])

    TOT_D_DIRECTIVES: List[Tuple[int, str]] = field(default_factory=lambda: [
        (5, "• MANDATORY: Reasoning depth must be {tot_d}+ levels deep with explicit layer separation.\n"),
        (4, "• Provide {tot_d}-level deep reasoning: foundation → intermediate → advanced → synthesis.\n"),
        (3, "• Provide {tot_d}-level reasoning with clear progression of thinking.\n"),
        (0, "• Structure reasoning with clear logical progression.\n")
    ])

    REFLEXION_DIRECTIVES: List[Tuple[int, str]] = field(default_factory=lambda: [
        (3, "• MANDATORY: Review your answer {max_loops} times, refining on each pass. Document improvements.\n"),
        (2, "• Review your answer {max_loops} times; improve if refinements are identified.\n"),
        (1, "• Review and refine your answer at least once.\n")
    ])


@dataclass
class AppConfig:
    """Master application configuration containing all sub-configs."""
    paths: FilePathsConfig = field(default_factory=FilePathsConfig)
    rag: RAGConfig = field(default_factory=lambda: RAGConfig())
    content_constraints: ContentConstraintsConfig = field(default_factory=lambda: ContentConstraintsConfig())
    signal_constraints: SignalControlConfig = field(default_factory=lambda: SignalControlConfig())
    artist: ArtistConfig = field(default_factory=ArtistConfig)
    validator: ValidatorConfig = field(default_factory=ValidatorConfig)
    web_rag: WebRagConfig = field(default_factory=WebRagConfig)
    enricher: EnricherConfig = field(default_factory=EnricherConfig)
    
    @property
    def reasoning_configs(self) -> Dict[str, 'ReasoningConfig']:
        """
        Convenience property for accessing all reasoning configs.
        Returns dictionary mapping section names to their ReasoningConfig.
        """
        return {
            'K0_HEADLINE': ReasoningConfig.K0_HEADLINE_CONFIG,
            'K1_EXECUTIVE_SUMMARY': ReasoningConfig.K1_EXECUTIVE_SUMMARY_CONFIG,
            'K2_UNIFY_BULLETS': ReasoningConfig.K2_UNIFY_BULLETS_CONFIG,
            'K2_UNIFY_OVERVIEW': ReasoningConfig.K2_UNIFY_OVERVIEW_CONFIG,
            'K3_IBM_BULLETS': ReasoningConfig.K3_IBM_BULLETS_CONFIG,
            'K3_IBM_OVERVIEW': ReasoningConfig.K3_IBM_OVERVIEW_CONFIG,
            'K4_TRADERSENSE_NARRATIVE': ReasoningConfig.K4_TRADERSENSE_NARRATIVE_CONFIG,
            'K5_EY_NARRATIVE': ReasoningConfig.K5_EY_NARRATIVE_CONFIG,
            'K6_EARLY_CAREER_NARRATIVE': ReasoningConfig.K6_EARLY_CAREER_NARRATIVE_CONFIG,
            'K9_COMPETENCIES': ReasoningConfig.K9_COMPETENCIES_CONFIG,
            'K10_SKILLS': ReasoningConfig.K10_SKILLS_CONFIG,
            'K11_COVER_LETTER': ReasoningConfig.K11_COVER_LETTER_CONFIG,
        }
    
    @property
    def rag_configs(self) -> Dict[str, 'RAGConfig']:
        """
        Convenience property for accessing RAG configs.
        Currently returns the main rag config in a dict.
        """
        return {
            'GLOBAL_JD_ANALYSIS': self.rag
        }
    
    @property
    def validator_config(self) -> 'ValidatorConfig':
        """
        Convenience property for accessing validator config.
        Alias for self.validator.
        """
        return self.validator


# ============================================================================
# REASONING CONFIG INSTANTIATIONS
# ============================================================================

ReasoningConfig.DEFAULT = ReasoningConfig()

ReasoningConfig.K0_HEADLINE_CONFIG = ReasoningConfig(cot_min_paths=4, tot_branches=2, min_tot_depth=2, self_consistency=5, reflexion=True)
ReasoningConfig.K1_EXECUTIVE_SUMMARY_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=8, reflexion=True, max_reflexion_loops=4)

ReasoningConfig.K2_UNIFY_BULLETS_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=3, min_tot_depth=2, self_consistency=6, reflexion=True)
ReasoningConfig.K2_UNIFY_OVERVIEW_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=4, reflexion=True)

ReasoningConfig.K3_IBM_BULLETS_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=3, min_tot_depth=2, self_consistency=5, reflexion=True)
ReasoningConfig.K3_IBM_OVERVIEW_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=4, reflexion=True)

ReasoningConfig.K4_TRADERSENSE_NARRATIVE_CONFIG = ReasoningConfig(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=False)

ReasoningConfig.K5_EY_NARRATIVE_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=2, min_tot_depth=3, self_consistency=4, reflexion=True)

ReasoningConfig.K6_EARLY_CAREER_NARRATIVE_CONFIG = ReasoningConfig(cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=False)

ReasoningConfig.K9_COMPETENCIES_CONFIG = ReasoningConfig(cot_min_paths=3, tot_branches=2, min_tot_depth=2, self_consistency=6, reflexion=True)

ReasoningConfig.K10_SKILLS_CONFIG = ReasoningConfig(cot_min_paths=1, tot_branches=2, min_tot_depth=1, self_consistency=1, reflexion=False)

ReasoningConfig.K11_COVER_LETTER_CONFIG = ReasoningConfig(cot_min_paths=4, tot_branches=3, min_tot_depth=3, self_consistency=6, reflexion=True, max_reflexion_loops=2)


# ============================================================================
# GLOBAL CONFIG INSTANTIATIONS
# ============================================================================

PROMPT_ADDENDUM_CONFIG = PromptAddendumConfig()

DEFAULT_GENERATION_TEMPERATURE = 0.9

# ============================================================================
# REASONING FUNCTIONS (Moved from monolithic resume_workflow_v16_20.py)
# ============================================================================

def reasoning_config_to_api_params(reasoning_config: ReasoningConfig) -> dict:
    """
    Converts a ReasoningConfig object into a dictionary of API parameters,
    including a GenerationConfig and a system prompt addendum.
    """
    logger = logging.getLogger(__name__)

    params = _get_normalized_reasoning_params(reasoning_config)

    temperature = DEFAULT_GENERATION_TEMPERATURE

    allocated_max_tokens = _allocate_tokens_from_depth(params['tot_d'], params['cot'], params['sc'])
    try:
         absolute_max_tokens = RAGConfig().max_tokens
    except NameError:
         logging.warning("RAGConfig not found, using default absolute max_tokens=30000.")
         absolute_max_tokens = 30000

    final_max_tokens = min(allocated_max_tokens, absolute_max_tokens)

    prompt_addendum = _build_reasoning_prompt_addendum(params)

    try:
        logger.debug(
            f"Reasoning Params for API: cot={params['cot']}, tot_b={params['tot_b']}, tot_d={params['tot_d']}, "
            f"sc={params['sc']}, reflexion={params['reflexion']}, max_loops={params['max_loops']}, "
            f"temp={temperature}, allocated_max_tokens={allocated_max_tokens}, final_max_tokens={final_max_tokens}"
        )
    except NameError:
        pass # Logging not fully initialized, skip debug log

    if not GEMINI_AVAILABLE:
        # Return a mock config if genai isn't available, to prevent crashes
        return {
            "generation_config": {"temperature": temperature, "max_output_tokens": final_max_tokens},
            "system_prompt_addendum": prompt_addendum,
            **params
        }

    return {
        "generation_config": genai.GenerationConfig(temperature=temperature, max_output_tokens=final_max_tokens),
        "system_prompt_addendum": prompt_addendum,
        **params
    }

def _get_normalized_reasoning_params(config: ReasoningConfig) -> Dict:
    """Normalizes and clamps reasoning parameters to sane values."""
    config = config or ReasoningConfig.DEFAULT
    tot_b = config.tot_branches if config.tot_branches is not None else 3
    tot_d = config.min_tot_depth if config.min_tot_depth is not None else 3
    sc = config.self_consistency if config.self_consistency is not None else 12
    reflexion = config.reflexion if config.reflexion is not None else True
    max_loops = config.max_reflexion_loops if config.max_reflexion_loops is not None else 2

    sc_clamped = max(1, min(sc, 8))

    return {
        "cot": max(2, min(config.cot_min_paths if config.cot_min_paths is not None else 3, 8)),
        "tot_b": max(2, min(tot_b, 6)),
        "tot_d": max(2, min(tot_d, 5)),
        "sc": sc_clamped,
        "reflexion": reflexion,
        "max_loops": max(1, min(max_loops, 5))
    }

def _allocate_tokens_from_depth(tot_d: int, cot: int, sc: int) -> int:
    """Allocates max_output_tokens based on reasoning complexity."""
    base_limit = 16384
    high_sc_limit = 24000
    mid_complex_limit = 26000
    high_complex_limit = 28000
    max_complex_limit = 30000

    if tot_d >= 4:
        max_tokens = max_complex_limit
    elif tot_d >= 3 and cot >= 5:
        max_tokens = high_complex_limit
    elif tot_d >= 3 or cot >= 5:
        max_tokens = mid_complex_limit
    elif sc >= 15:
        max_tokens = high_sc_limit
    else:
        max_tokens = base_limit

    rag_config_max = 30000
    return max(base_limit, min(max_tokens, rag_config_max))

def _build_reasoning_prompt_addendum(params: Dict) -> str:
    """Constructs the system prompt addendum from normalized parameters."""
    addendum = PROMPT_ADDENDUM_CONFIG.HEADER

    def find_directive(directives: List[Tuple[int, str]], value: int) -> str:
        for threshold, text in directives:
            if value >= threshold:
                return text
        return ""

    addendum += find_directive(PROMPT_ADDENDUM_CONFIG.COT_DIRECTIVES, params.get('cot', 0)).format(cot=params.get('cot'))
    addendum += find_directive(PROMPT_ADDENDUM_CONFIG.TOT_B_DIRECTIVES, params.get('tot_b', 0)).format(tot_b=params.get('tot_b'))
    addendum += find_directive(PROMPT_ADDENDUM_CONFIG.TOT_D_DIRECTIVES, params.get('tot_d', 0)).format(tot_d=params.get('tot_d'))

    if params.get('reflexion'):
        addendum += find_directive(PROMPT_ADDENDUM_CONFIG.REFLEXION_DIRECTIVES, params.get('max_loops', 0)).format(max_loops=params.get('max_loops'))

    addendum += PROMPT_ADDENDUM_CONFIG.FOOTER
    return addendum

def enhance_system_prompt_with_reasoning(
    base_system_prompt: str,
    reasoning_config: ReasoningConfig,
    section_id: str = "UNKNOWN"
) -> str:
    """
    Enhance a system prompt with reasoning configuration directives.

    Args:
        base_system_prompt: Original system prompt (e.g., "You are an expert...")
        reasoning_config: ReasoningConfig instance
        section_id: For logging (e.g., "K.1", "K.4")

    Returns:
        Enhanced system prompt with reasoning directives appended
    """
    api_params = reasoning_config_to_api_params(reasoning_config)
    enhanced = base_system_prompt + api_params["system_prompt_addendum"]
    return enhanced

# ============================================================================
# FINAL GLOBAL CONFIG INSTANCE
# ============================================================================

CONFIG = AppConfig(
    paths=FilePathsConfig(),
    rag=RAGConfig(),
    content_constraints=ContentConstraintsConfig(),
    signal_constraints=SignalControlConfig(),
    artist=ArtistConfig(),
    validator=ValidatorConfig(),
    web_rag=WebRagConfig(),
    enricher=EnricherConfig()
)