from __future__ import annotations
"""
Configuration Contracts - SSOT for all config dataclasses.
Modularized from core_contracts.py for DDD bounded context isolation.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set


@dataclass
class FilePathsConfig:
    """File paths for data files used by the workflow."""
    master_resume: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent.parent / 'config' / 'P1_core' / 'data' / 'master_resume.json')
    hyphenation_rules: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent.parent / 'config' / 'P1_core' / 'data' / 'hyphenation_rules.json')
    app_tracker_schema: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent.parent / 'config' / 'P1_core' / 'data' / 'app_tracker_schema.json')
    artist_specs: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent.parent / 'config' / 'P1_core' / 'data' / 'artist_specs.json')
    artist_constraints: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent.parent / 'config' / 'P1_core' / 'data' / 'artist_constraints.json')
    validator_rules: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent.parent / 'config' / 'P1_core' / 'data' / 'validator_rules.json')
    prompts: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent.parent / 'config' / 'P1_core' / 'data' / 'prompts.json')

# Backward compat alias


@dataclass
class ArtistConfig:
    """Configuration for the Artist Generator (resume content generation)."""
    provenance_split_targets: Dict = field(default_factory=dict)
    bullet_word_count_ranges: Dict = field(default_factory=dict)
    narrative_config: Dict = field(default_factory=dict)

# Backward compat alias


@dataclass
class ValidatorConfig:
    """Configuration for validation rules and constraints."""
    forbidden_verbs: List[str] = field(default_factory=list)
    required_sections: Set[str] = field(default_factory=set)
    bullet_word_count_sections_to_check: Set[str] = field(default_factory=set)
    provenance_split_targets: Dict = field(default_factory=dict)
    pipeline_status_enum: List[str] = field(default_factory=list)

# Backward compat alias


@dataclass
class PromptsConfig:
    """Configuration for all prompt templates."""
    prompts: Dict[str, Dict[str, str]] = field(default_factory=dict)
    
    def get_prompt(self, prompt_name: str, section: str='default') -> str:
        """Retrieve a prompt template by name and section."""
        if prompt_name not in self.prompts:
            raise KeyError(f"Prompt '{prompt_name}' not found in prompts.json")
        prompt_data = self.prompts[prompt_name]
        if section in prompt_data:
            return prompt_data[section]
        elif 'default' in prompt_data:
            return prompt_data['default']
        else:
            raise KeyError(f"Section '{section}' not found for prompt '{prompt_name}'")

# Backward compat alias


@dataclass
class WebRagConfig:
    """Configuration for Web RAG (Retrieval Augmented Generation)."""
    peers_by_industry: Dict = field(default_factory=lambda: {
        'Financial Technology': ['JPMorgan', 'Goldman Sachs', 'Morgan Stanley', 'Stripe', 'Square'],
        'Healthcare': ['UnitedHealth', 'CVS Health', 'Anthem', 'Cigna', 'Humana'],
        'Retail/E-Commerce': ['Amazon', 'Walmart', 'Target', 'Shopify', 'eBay'],
        'Software/SaaS': ['Salesforce', 'Oracle', 'SAP', 'Adobe', 'Workday'],
        'Technology': ['Google', 'Microsoft', 'Meta', 'Apple', 'Amazon']
    })

# Backward compat alias


@dataclass
class EnricherConfig:
    """Configuration for data enrichment."""
    canonical_verbs: Dict = field(default_factory=lambda: {
        'led': ['led', 'lead', 'leading'],
        'built': ['built', 'build', 'building'],
        'drove': ['drove', 'drive', 'driving'],
        'launched': ['launched', 'launch', 'launching'],
        'scaled': ['scaled', 'scale', 'scaling'],
        'delivered': ['delivered', 'deliver', 'delivering'],
        'achieved': ['achieved', 'achieve', 'achieving'],
        'established': ['established', 'establish', 'establishing'],
        'managed': ['managed', 'manage', 'managing'],
        'developed': ['developed', 'develop', 'developing']
    })

# Backward compat alias


@dataclass
class EnforcementRAGConfig:
    """Configuration for RAG system."""
    MODEL: str = 'gemini-2.5-pro'
    max_tokens: int = 8192
    TEMPERATURE: float = 0.7
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
    cache_ttl_days: int = 30
    telemetry_enabled: bool = True
    chroma_collection_name: str = 'rag_librarian_v1'
    source_weights: Dict[str, float] = field(default_factory=lambda: {
        'SOURCE_JD': 1.8,
        'SOURCE_COMPANY_BLOG': 1.5,
        'SOURCE_TARGET_EMPLOYEE': 1.4,
        'SOURCE_GARTNER_MQ': 1.2,
        'SOURCE_PEER_JD': 0.8,
        'SOURCE_GENERIC_PROFILE': 0.5,
        'LOCAL_NLP': 0.2
    })

# Backward compat alias


@dataclass
class EnforcementReasoningConfig:
    """Configuration for reasoning strategies."""
    cot_min_paths: int = 2
    tot_branches: int = 3
    min_tot_depth: int = 2
    self_consistency: int = 3
    REFLEXION: bool = True
    max_reflexion_loops: int = 3

# Backward compat alias


@dataclass
class ContentConstraintsConfig:
    """Content-level constraints for word counts, sentence counts, etc."""
    TOTAL_WORD_COUNT_MIN: int = 870
    TOTAL_WORD_COUNT_MAX: int = 1030
    MIN_JD_KEYWORDS: int = 7
    HEADLINE_WORD_COUNT_MIN: int = 8
    HEADLINE_WORD_COUNT_MAX: int = 12
    HEADLINE_COMPONENT_WORDS_MIN: int = 2
    HEADLINE_COMPONENT_WORDS_MAX: int = 4
    EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 6
    EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 9
    EXEC_SUMMARY_WORD_COUNT_MIN: int = 140
    EXEC_SUMMARY_WORD_COUNT_MAX: int = 170
    K1_MIN_DIFFERENTIATORS: int = 4
    SKILLS_COUNT_MIN: int = 8
    SKILLS_COUNT_MAX: int = 12
    SKILLS_WORD_COUNT_MIN: int = 1
    SKILLS_WORD_COUNT_MAX: int = 3
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
    COVER_LETTER_P1_WORD_COUNT_MIN: int = 80
    COVER_LETTER_P1_WORD_COUNT_MAX: int = 100
    COVER_LETTER_P2_WORD_COUNT_MIN: int = 90
    COVER_LETTER_P2_WORD_COUNT_MAX: int = 120
    COVER_LETTER_P3_WORD_COUNT_MIN: int = 80
    COVER_LETTER_P3_WORD_COUNT_MAX: int = 100
    COVER_LETTER_JD_RELEVANCE_THRESHOLD: float = 0.35

# Backward compat alias


@dataclass
class SignalControlConfig:
    """Signal control thresholds for quality and relevance."""
    K1_MAX_DIFFERENTIATORS: int = 4
    RESUME_MAX_JD_KEYWORDS: int = 16
    CL_MAX_JD_SIMILARITY: float = 0.65

# Backward compat alias


@dataclass
class PromptAddendumConfig:
    """Configuration for reasoning prompt addendums."""
    HEADER: str = '\n\n**REASONING IMPLEMENTATION DIRECTIVES (v16.40):**\n\n'
    FOOTER: str = '\nAll directives MUST be followed in the output.\n'

# Backward compat alias


@dataclass
class AppConfig:
    """Master application configuration containing all sub-configs."""
    paths: FilePathsConfig = field(default_factory=FilePathsConfig)
    content_constraints: ContentConstraintsConfig = field(default_factory=ContentConstraintsConfig)
    signal_constraints: SignalControlConfig = field(default_factory=SignalControlConfig)
    web_rag: WebRagConfig = field(default_factory=WebRagConfig)
    enricher: EnricherConfig = field(default_factory=EnricherConfig)

# Backward compat alias


# Public exports
__all__ = [
    # Snake case (canonical)
    "FilePathsConfig",
    "ArtistConfig",
    "ValidatorConfig",
    "PromptsConfig",
    "WebRagConfig",
    "EnricherConfig",
    "EnforcementRAGConfig",
    "EnforcementReasoningConfig",
    "ContentConstraintsConfig",
    "SignalControlConfig",
    "PromptAddendumConfig",
    "AppConfig",
    # PascalCase aliases (backward compat)
    "FilePathsConfig",
    "ArtistConfig",
    "ValidatorConfig",
    "PromptsConfig",
    "WebRagConfig",
    "EnricherConfig",
    "EnforcementRAGConfig",
    "EnforcementReasoningConfig",
    "ContentConstraintsConfig",
    "SignalControlConfig",
    "PromptAddendumConfig",
    "AppConfig",
]
