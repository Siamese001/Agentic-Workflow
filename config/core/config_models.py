"""Dataclass models for config."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class FilePathsConfig:
    """File paths for data files used by the workflow."""
    master_resume: Path = DATA_DIR / 'master_resume.json'
    hyphenation_rules: Path = DATA_DIR / 'hyphenation_rules.json'
    app_tracker_schema: Path = DATA_DIR / 'app_tracker_schema.json'
    artist_specs: Path = DATA_DIR / 'artist_specs.json'
    artist_constraints: Path = DATA_DIR / 'artist_constraints.json'
    validator_rules: Path = DATA_DIR / 'validator_rules.json'
    prompts: Path = DATA_DIR / 'prompts.json'

@dataclass
class ArtistConfig:
    """Configuration for the Artist Generator (resume content generation)."""
    provenance_split_targets: Dict = field(default_factory=dict)
    bullet_word_count_ranges: Dict = field(default_factory=dict)
    narrative_config: Dict = field(default_factory=dict)

    @classmethod
    def from_json(cls, json_path: Path=DATA_DIR / 'artist_constraints.json') -> 'ArtistConfig':
        """Load ArtistConfig from JSON file."""
        data = _load_json_config(str(json_path), 'Artist Constraints', required=False)
        bullet_ranges = {}
        for section, range_list in data.get('bullet_word_count_ranges', {}).items():
            if isinstance(range_list, list) and len(range_list) == 2:
                bullet_ranges[section] = tuple(range_list)
        return cls(provenance_split_targets=data.get('provenance_split_targets', {}), bullet_word_count_ranges=bullet_ranges, narrative_config=data.get('narrative_config', {}))

@dataclass
class ValidatorConfig:
    """Configuration for validation rules and constraints."""
    forbidden_verbs: List[str] = field(default_factory=list)
    required_sections: Set[str] = field(default_factory=set)
    bullet_word_count_sections_to_check: Set[str] = field(default_factory=set)
    provenance_split_targets: Dict = field(default_factory=dict)
    pipeline_status_enum: List[str] = field(default_factory=list)

    @classmethod
    def from_json(cls, json_path: Path=DATA_DIR / 'validator_rules.json') -> 'ValidatorConfig':
        """Load ValidatorConfig from JSON file."""
        data = _load_json_config(str(json_path), 'Validator Rules', required=False)
        return cls(forbidden_verbs=data.get('forbidden_verbs', []), required_sections=set(data.get('required_sections', [])), bullet_word_count_sections_to_check=set(data.get('bullet_word_count_sections_to_check', [])), provenance_split_targets=data.get('provenance_split_targets', {}), pipeline_status_enum=data.get('pipeline_status_enum', []))

@dataclass
class PromptsConfig:
    """Configuration for all prompt templates."""
    prompts: Dict[str, Dict[str, str]] = field(default_factory=dict)

    @classmethod
    def from_json(cls, json_path: Path=DATA_DIR / 'prompts.json') -> 'PromptsConfig':
        """Load PromptsConfig from JSON file."""
        data = _load_json_config(str(json_path), 'Prompts', required=True)
        return cls(prompts=data)

    def get_prompt(self, prompt_name: str, section: str='default') -> str:
        """
        Retrieve a prompt template by name and section.
        
        Args:
            prompt_name: Name of the prompt (e.g., "RAG_MISSION_EXTRACTION")
            section: Section key (e.g., "PHASE_1", "PHASE_2", "default")
            
        Returns:
            The prompt template string
            
        Raises:
            KeyError: If prompt or section doesn't exist
        """
        if prompt_name not in self.prompts:
            raise KeyError(f"Prompt '{prompt_name}' not found in prompts.json")
        prompt_data = self.prompts[prompt_name]
        if section in prompt_data:
            return prompt_data[section]
        elif 'default' in prompt_data:
            return prompt_data['default']
        else:
            raise KeyError(f"Section '{section}' not found for prompt '{prompt_name}'")

@dataclass
class WebRagConfig:
    """Configuration for Web RAG (Retrieval Augmented Generation)."""
    peers_by_industry: Dict = field(default_factory=lambda: {'Financial Technology': ['JPMorgan', 'Goldman Sachs', 'Morgan Stanley', 'Stripe', 'Square'], 'Healthcare': ['UnitedHealth', 'CVS Health', 'Anthem', 'Cigna', 'Humana'], 'Retail/E-Commerce': ['Amazon', 'Walmart', 'Target', 'Shopify', 'eBay'], 'Software/SaaS': ['Salesforce', 'Oracle', 'SAP', 'Adobe', 'Workday'], 'Technology': ['Google', 'Microsoft', 'Meta', 'Apple', 'Amazon']})

