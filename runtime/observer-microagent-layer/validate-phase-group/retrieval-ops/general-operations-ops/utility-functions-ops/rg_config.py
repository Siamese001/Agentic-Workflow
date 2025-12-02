#!/usr/bin/env python3
"""
Resume Engine Configuration
Configuration dataclasses for all L1-L5 components
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class FilePathsConfig:
    """File path configuration"""
    master_resume_path: str
    job_description_path: str
    output_dir: str
    config_dir: str = "config"


@dataclass
class ArtistConfig:
    """Artist generation configuration"""
    temperature: float = 0.9
    max_tokens: int = 2048
    model: str = "gemini-pro"


@dataclass
class ValidatorConfig:
    """Validation configuration with forbidden verbs and constraints"""
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
    """Web RAG configuration with industry peer mapping"""
    peers_by_industry: Dict = field(default_factory=lambda: {
        "Financial Technology": ["JPMorgan", "Goldman Sachs", "Morgan Stanley", "Stripe", "Square"],
        "Healthcare": ["UnitedHealth", "CVS Health", "Anthem", "Cigna", "Humana"],
        "Retail/E-Commerce": ["Amazon", "Walmart", "Target", "Shopify", "eBay"],
        "Software/SaaS": ["Salesforce", "Oracle", "SAP", "Adobe", "Workday"],
        "Technology": ["Google", "Microsoft", "Meta", "Apple", "Amazon"]
    })
    enabled: bool = True
    max_search_results: int = 10
    confidence_threshold: float = 0.7


@dataclass
class EnricherConfig:
    """Data enrichment configuration with canonical verb mapping"""
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
    enable_verb_canonicalization: bool = True
    enable_skill_mapping: bool = True
    duplicate_threshold: float = 0.9


@dataclass
class ContentConstraintsConfig:
    """Content constraints for word counts and structure"""
    
    # Total resume constraints
    TOTAL_WORD_COUNT_MIN: int = 870
    TOTAL_WORD_COUNT_MAX: int = 1030
    MIN_JD_KEYWORDS: int = 7

    # Headline constraints
    HEADLINE_WORD_COUNT_MIN: int = 8
    HEADLINE_WORD_COUNT_MAX: int = 11
    HEADLINE_COMPONENT_WORDS_MIN: int = 2
    HEADLINE_COMPONENT_WORDS_MAX: int = 4

    # Executive summary constraints
    EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 6
    EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 7
    EXEC_SUMMARY_WORD_COUNT_MIN: int = 140
    EXEC_SUMMARY_WORD_COUNT_MAX: int = 170
    K1_MIN_DIFFERENTIATORS: int = 4

    # Section overview constraints
    UNIFY_OVERVIEW_WORD_COUNT_MIN: int = 25
    UNIFY_OVERVIEW_WORD_COUNT_MAX: int = 40
    IBM_OVERVIEW_WORD_COUNT_MIN: int = 25
    IBM_OVERVIEW_WORD_COUNT_MAX: int = 35

    # Narrative constraints
    TRADERSENSE_NARRATIVE_WORD_COUNT_MIN: int = 40
    TRADERSENSE_NARRATIVE_WORD_COUNT_MAX: int = 60
    EY_NARRATIVE_WORD_COUNT_MIN: int = 40
    EY_NARRATIVE_WORD_COUNT_MAX: int = 60
    EARLY_CAREER_NARRATIVE_WORD_COUNT_MIN: int = 50
    EARLY_CAREER_NARRATIVE_WORD_COUNT_MAX: int = 70

    # Combined section constraints
    UNIFY_IBM_COMBINED_PERCENT_MIN: float = 35.0
    UNIFY_IBM_COMBINED_PERCENT_MAX: float = 45.0
    UNIFY_IBM_RATIO_MIN: float = 1.1
    UNIFY_IBM_RATIO_MAX: float = 1.3

    # Cover letter constraints
    COVER_LETTER_P1_WORD_COUNT_MIN: int = 80
    COVER_LETTER_P1_WORD_COUNT_MAX: int = 100
    COVER_LETTER_P2_WORD_COUNT_MIN: int = 90
    COVER_LETTER_P2_WORD_COUNT_MAX: int = 120
    COVER_LETTER_P3_WORD_COUNT_MIN: int = 80
    COVER_LETTER_P3_WORD_COUNT_MAX: int = 100
    COVER_LETTER_JD_RELEVANCE_THRESHOLD: float = 0.35


@dataclass
class SignalControlConfig:
    """Signal control configuration for content generation"""
    K1_MAX_DIFFERENTIATORS: int = 4
    RESUME_MAX_JD_KEYWORDS: int = 16
    CL_MAX_JD_SIMILARITY: float = 0.65


@dataclass
class AppConfig:
    """Application configuration aggregating all sub-configs"""
    file_paths: FilePathsConfig
    artist: ArtistConfig
    validator: ValidatorConfig
    web_rag: WebRagConfig
    enricher: EnricherConfig
    content_constraints: ContentConstraintsConfig
    signal_control: SignalControlConfig
    test_mode: bool = False
