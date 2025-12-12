"""
Workflow Loader - Dynamic loading and parsing of workflow configurations.

Loads the active_workflow.json and provides typed accessors for workflow sections,
K-node configurations, prompts, and validation rules.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WordCountConstraints:
    """Word count constraints for a section."""
    min_words: int
    max_words: int
    
    @classmethod
    def from_list(cls, word_range: List[int]) -> "WordCountConstraints":
        """Create from a list like [120, 140]."""
        return cls(min_words=word_range[0], max_words=word_range[1])


@dataclass
class KNodeConfig:
    """Configuration for a single K-node."""
    description: str
    input_dependencies: List[str] = None
    temp: float = 0.7
    rag_type: str = "Hybrid"
    rag_total_calls: int = 4
    rag_hops: int = 2
    claim_verification_mode: str = "strict"
    hybrid_cot_tot: bool = False
    cot_min_paths: int = 2
    tot_branches: int = 3
    min_tot_depth: int = 2
    self_consistency: int = 8
    reflexion: bool = False
    max_reflexion_loops: int = 3
    
    def __post_init__(self) -> None:
        if self.input_dependencies is None:
            self.input_dependencies = []


@dataclass
class CreativeBriefConfig:
    """Creative brief configuration."""
    headline_word_count: WordCountConstraints
    headline_char_max: int
    executive_summary_word_count: WordCountConstraints
    executive_summary_voice: str
    forbidden_patterns: List[str]
    unify_bullet_word_count: WordCountConstraints
    ibm_bullet_word_count: WordCountConstraints
    unify_overview_word_count: WordCountConstraints
    ibm_overview_word_count: WordCountConstraints
    competency_word_count: WordCountConstraints
    cover_letter_para_word_count: WordCountConstraints


class WorkflowLoader:
    """Loads and provides access to workflow configuration from JSON."""
    
    def __init__(self, workflow_path: Optional[Union[str, Path]] = None):
        """
        Initialize WorkflowLoader.
        
        Args:
            workflow_path: Path to workflow JSON file. Defaults to active_workflow.json.
        """
        if workflow_path is None:
            workflow_path = Path(__file__).parent / "active_workflow.json"
        else:
            workflow_path = Path(workflow_path)
            
        self.workflow_path = workflow_path
        self._workflow_data: Optional[Dict[str, Any]] = None
        
        # Cache for parsed configurations
        self._cached_metadata: Optional[Dict[str, Any]] = None
        self._cached_knode_configs: Optional[Dict[str, KNodeConfig]] = None
        self._cached_creative_brief: Optional[CreativeBriefConfig] = None
        self._cached_validation_rules: Optional[Dict[str, Any]] = None
        self._cached_pre_flight_tests: Optional[List[Dict[str, Any]]] = None
        self._cached_file_complexity_thresholds: Optional[Dict[str, int]] = None
        self._cached_required_files: Optional[List[str]] = None
        self._cached_enforcement_rules: Optional[List[str]] = None
        self._cached_role_config: Optional[Dict[str, Any]] = None
        self._cached_task_pipeline: Optional[List[Dict[str, Any]]] = None
        self._cached_context_config: Optional[Dict[str, Any]] = None
        self._cached_reasoning_config: Optional[Dict[str, Any]] = None
        
        self._load_workflow()
    
    def _load_workflow(self) -> None:
        """Load the workflow JSON from disk."""
        try:
            with open(self.workflow_path, 'r', encoding='utf-8') as f:
                self._workflow_data = json.load(f)
            logger.info(f"Loaded workflow v{self.get_version()} from {self.workflow_path}")
        except FileNotFoundError:
            logger.warning(f"Workflow file not found at {self.workflow_path}, using fallback defaults")
            self._workflow_data = self._get_fallback_workflow()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in workflow file: {e}, using fallback defaults")
            self._workflow_data = self._get_fallback_workflow()
        except Exception as e:
            logger.error(f"Failed to load workflow from {self.workflow_path}: {e}, using fallback defaults")
            self._workflow_data = self._get_fallback_workflow()
    
    def _get_fallback_workflow(self) -> Dict[str, Any]:
        """Get minimal fallback workflow configuration."""
        return {
            "metadata": {
                "version": "fallback",
                "architecture": "3-phase pipeline: Clerk, Artist, Assembler",
                "description": "Fallback configuration used when JSON file is unavailable"
            },
            "pre_flight_engine_validation": {
                "tests": [
                    {"test_id": "VALIDATE_ITERATION", "description": "Basic iteration check"}
                ]
            },
            "1.role": {
                "description": "Resume generation assistant"
            },
            "2.task": {
                "pipeline": [
                    {"phase": 1, "name": "The Clerk: Deterministic Data Scaffolding"},
                    {"phase": 2, "name": "The Artist: Grounded Generation"},
                    {"phase": 3, "name": "The Assembler: Final Rendering & Validation"}
                ]
            },
            "3.context": {
                "pre_flight_file_complexity_gate": {
                    "thresholds": {
                        "total_file_count_max": 5,
                        "total_file_size_mb_max": 10
                    }
                },
                "pre_flight_file_manifest_check": {
                    "required_file_manifest": ["App_Schema_v4.json"]
                }
            },
            "4.reasoning": {
                "description": "Creative generation phase",
                "creative_brief": {
                    "headline": {"word_count": [8, 12], "char_count_max": 90},
                    "executive_summary": {"word_count": [120, 140], "voice": "third_person_implied", "forbidden_patterns": []},
                    "experience_bullets": {"unify_bullet_word_count": [28, 33], "ibm_bullet_word_count": [24, 30]},
                    "experience_overview": {"unify_word_count": [25, 33], "ibm_word_count": [22, 28]},
                    "leadership_competencies": {"word_count_per_desc": [24, 30]},
                    "cover_letter": {"word_count_per_para": [85, 100]},
                    "deduplication_matrix": {"thresholds": {}}
                },
                "hardcoded_config": {
                    "K.0": {"description": "Thematic analysis", "temp": 0.3, "rag_total_calls": 50, "rag_hops": 3},
                    "K.1": {"description": "Executive summary", "temp": 0.9, "rag_total_calls": 4, "rag_hops": 2},
                    "K.2": {"description": "Competitive analysis", "temp": 0.3, "rag_total_calls": 24, "rag_hops": 3}
                }
            }
        }
    
    def get_version(self) -> str:
        """Get the workflow version."""
        return self._workflow_data.get("metadata", {}).get("version", "unknown")
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get the metadata section."""
        if self._cached_metadata is None:
            self._cached_metadata = self._workflow_data.get("metadata", {})
        return self._cached_metadata
    
    def get_role_config(self) -> Dict[str, Any]:
        """Get the role configuration (section 1)."""
        if self._cached_role_config is None:
            self._cached_role_config = self._workflow_data.get("1.role", {})
        return self._cached_role_config
    
    def get_task_pipeline(self) -> List[Dict[str, Any]]:
        """Get the task pipeline phases."""
        if self._cached_task_pipeline is None:
            self._cached_task_pipeline = self._workflow_data.get("2.task", {}).get("pipeline", [])
        return self._cached_task_pipeline
    
    def get_context_config(self) -> Dict[str, Any]:
        """Get the context management configuration."""
        if self._cached_context_config is None:
            self._cached_context_config = self._workflow_data.get("3.context", {})
        return self._cached_context_config
    
    def get_reasoning_config(self) -> Dict[str, Any]:
        """Get the reasoning configuration."""
        if self._cached_reasoning_config is None:
            self._cached_reasoning_config = self._workflow_data.get("4.reasoning", {})
        return self._cached_reasoning_config
    
    def get_creative_brief(self) -> CreativeBriefConfig:
        """Extract and return the creative brief configuration."""
        if self._cached_creative_brief is None:
            brief = self.get_reasoning_config().get("creative_brief", {})
            
            self._cached_creative_brief = CreativeBriefConfig(
                headline_word_count=WordCountConstraints.from_list(
                    brief.get("headline", {}).get("word_count", [8, 12])
                ),
                headline_char_max=brief.get("headline", {}).get("char_count_max", 90),
                executive_summary_word_count=WordCountConstraints.from_list(
                    brief.get("executive_summary", {}).get("word_count", [120, 140])
                ),
                executive_summary_voice=brief.get("executive_summary", {}).get("voice", "third_person_implied"),
                forbidden_patterns=brief.get("executive_summary", {}).get("forbidden_patterns", []),
                unify_bullet_word_count=WordCountConstraints.from_list(
                    brief.get("experience_bullets", {}).get("unify_bullet_word_count", [28, 33])
                ),
                ibm_bullet_word_count=WordCountConstraints.from_list(
                    brief.get("experience_bullets", {}).get("ibm_bullet_word_count", [24, 30])
                ),
                unify_overview_word_count=WordCountConstraints.from_list(
                    brief.get("experience_overview", {}).get("unify_word_count", [25, 33])
                ),
                ibm_overview_word_count=WordCountConstraints.from_list(
                    brief.get("experience_overview", {}).get("ibm_word_count", [22, 28])
                ),
                competency_word_count=WordCountConstraints.from_list(
                    brief.get("leadership_competencies", {}).get("word_count_per_desc", [24, 30])
                ),
                cover_letter_para_word_count=WordCountConstraints.from_list(
                    brief.get("cover_letter", {}).get("word_count_per_para", [85, 100])
                )
            )
        return self._cached_creative_brief
    
    def get_knode_configs(self) -> Dict[str, KNodeConfig]:
        """Get all K-node configurations."""
        if self._cached_knode_configs is None:
            configs = {}
            hardcoded = self.get_reasoning_config().get("hardcoded_config", {})
            
            for key, value in hardcoded.items():
                if key.startswith("K.") and isinstance(value, dict):
                    configs[key] = KNodeConfig(
                        description=value.get("description", ""),
                        input_dependencies=value.get("input_dependencies", []),
                        temp=value.get("temp", 0.7),
                        rag_type=value.get("rag_type", "Hybrid"),
                        rag_total_calls=value.get("rag_total_calls", 4),
                        rag_hops=value.get("rag_hops", 2),
                        claim_verification_mode=value.get("claim_verification_mode", "strict"),
                        hybrid_cot_tot=value.get("hybrid_cot_tot", False),
                        cot_min_paths=value.get("cot_min_paths", 2),
                        tot_branches=value.get("tot_branches", 3),
                        min_tot_depth=value.get("min_tot_depth", 2),
                        self_consistency=value.get("self_consistency", 8),
                        reflexion=value.get("reflexion", False),
                        max_reflexion_loops=value.get("max_reflexion_loops", 3)
                    )
            
            self._cached_knode_configs = configs
        return self._cached_knode_configs
    
    def get_knode_config(self, node_id: str) -> Optional[KNodeConfig]:
        """Get a specific K-node configuration."""
        configs = self.get_knode_configs()
        return configs.get(node_id)
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules and thresholds."""
        if self._cached_validation_rules is None:
            reasoning = self.get_reasoning_config()
            # Check creative_brief first (where deduplication_matrix is located)
            creative_brief = reasoning.get("creative_brief", {})
            self._cached_validation_rules = creative_brief.get("deduplication_matrix", {}).get("thresholds", {})
        return self._cached_validation_rules
    
    def get_pre_flight_tests(self) -> List[Dict[str, Any]]:
        """Get pre-flight validation tests."""
        if self._cached_pre_flight_tests is None:
            self._cached_pre_flight_tests = self._workflow_data.get("pre_flight_engine_validation", {}).get("tests", [])
        return self._cached_pre_flight_tests
    
    def get_file_complexity_thresholds(self) -> Dict[str, int]:
        """Get file complexity gate thresholds."""
        if self._cached_file_complexity_thresholds is None:
            context = self.get_context_config()
            self._cached_file_complexity_thresholds = context.get("pre_flight_file_complexity_gate", {}).get("thresholds", {})
        return self._cached_file_complexity_thresholds
    
    def get_required_files(self) -> List[str]:
        """Get list of required files."""
        if self._cached_required_files is None:
            context = self.get_context_config()
            self._cached_required_files = context.get("pre_flight_file_manifest_check", {}).get("required_file_manifest", [])
        return self._cached_required_files
    
    def get_enforcement_rules(self) -> List[str]:
        """Get critical enforcement rules."""
        if self._cached_enforcement_rules is None:
            self._cached_enforcement_rules = self.get_metadata().get("critical_rules_added", [])
        return self._cached_enforcement_rules
    
    def reload(self) -> None:
        """Reload the workflow from disk and clear all caches."""
        # Clear all cached values
        self._cached_metadata = None
        self._cached_knode_configs = None
        self._cached_creative_brief = None
        self._cached_validation_rules = None
        self._cached_pre_flight_tests = None
        self._cached_file_complexity_thresholds = None
        self._cached_required_files = None
        self._cached_enforcement_rules = None
        self._cached_role_config = None
        self._cached_task_pipeline = None
        self._cached_context_config = None
        self._cached_reasoning_config = None
        
        # Reload from disk
        self._load_workflow()
        logger.info("Workflow reloaded from disk with cleared caches")


# Convenience function for creating a loader
def create_workflow_loader(workflow_path: Optional[Union[str, Path]] = None) -> WorkflowLoader:
    """Create a WorkflowLoader instance."""
    return WorkflowLoader(workflow_path)
