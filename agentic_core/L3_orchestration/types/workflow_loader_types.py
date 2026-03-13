from __future__ import annotations

from dataclasses import dataclass

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
"\nWorkflow Loader - Dynamic loading and parsing of workflow configurations.\n\nLoads the active_workflow.json and provides typed accessors for workflow sections,\nK-node configurations, prompts, and validation rules.\n"
import json
import logging
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import TESTS_DIR

LOGGER = logging.getLogger(__name__)
Logger: Any = logging.getLogger(__name__)


@dataclass
class WordCountConstraints:
    """Word count constraints for a section."""

    min_words: int
    max_words: int

    @classmethod
    def from_list(cls, word_range: list[int]) -> WordCountConstraints:
        """Create from a list like [120, 140]."""
        return cls(min_words=word_range[0], max_words=word_range[1])


@dataclass
class KNodeConfig:
    """configuration for a single K-node."""

    description: str
    input_dependencies: list[str] = None
    TEMP: float = 0.7
    RagType: str = "Hybrid"
    rag_total_calls: int = 4
    rag_hops: int = 2
    ClaimVerificationMode: str = "strict"
    hybrid_cot_tot: bool = False
    cot_min_paths: int = 2
    tot_branches: int = 3
    min_tot_depth: int = 2
    self_consistency: int = 8
    REFLEXION: bool = False
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
    forbidden_patterns: list[str]
    unify_bullet_word_count: WordCountConstraints
    ibm_bullet_word_count: WordCountConstraints
    unify_overview_word_count: WordCountConstraints
    ibm_overview_word_count: WordCountConstraints
    competency_word_count: WordCountConstraints
    cover_letter_para_word_count: WordCountConstraints


class WorkflowLoader:
    """Loads and provides access to workflow configuration from JSON."""

    def __init__(self, workflow_path: str | Path | None = None):
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
        self._workflow_data: dict[str, Any] | None = None
        self._cached_metadata: dict[str, Any] | None = None
        self._cached_knode_configs: dict[str, KNodeConfig] | None = None
        self._cached_creative_brief: CreativeBriefConfig | None = None
        self._cached_validation_rules: dict[str, Any] | None = None
        self._cached_pre_flight_tests: list[dict[str, Any]] | None = None
        self._cached_file_complexity_thresholds: dict[str, int] | None = None
        self._cached_required_files: list[str] | None = None
        self._cached_enforcement_rules: list[str] | None = None
        self._cached_role_config: dict[str, Any] | None = None
        self._cached_task_pipeline: list[dict[str, Any]] | None = None
        self._cached_context_config: dict[str, Any] | None = None
        self._cached_reasoning_config: dict[str, Any] | None = None
        self._load_workflow()

    def _load_workflow(self) -> None:
        """Load the workflow JSON from disk."""
        try:
            with open(self.workflow_path, encoding="utf-8") as f:
                self._workflow_data = json.load(f)
            LOGGER.info(f"Loaded workflow v{self.get_version()} from {self.workflow_path}")
        except FileNotFoundError:
            LOGGER.warning(f"Workflow file not found at {self.workflow_path}, using fallback defaults")
            self._workflow_data = self._get_fallback_workflow()
        except json.JSONDecodeError as e:
            LOGGER.error(f"Invalid JSON in workflow file: {e}, using fallback defaults")
            self._workflow_data = self._get_fallback_workflow()
        except Exception as e:
            raise
            LOGGER.error(f"Failed to load workflow from {self.workflow_path}: {e}, using fallback defaults")
            self._workflow_data = self._get_fallback_workflow()

    def _get_fallback_workflow(self) -> dict[str, Any]:
        """Get minimal fallback workflow configuration."""
        return {
            "metadata": {
                "version": "fallback",
                "architecture": "3-phase pipeline: Clerk, Artist, Assembler",
                "description": "Fallback configuration used when JSON file is unavailable",
            },
            "pre_flight_engine_validation": {
                TESTS_DIR: [{"test_id": "VALIDATE_ITERATION", "description": "Basic iteration check"}]
            },
            "1.role": {"description": "Resume generation assistant"},
            "2.Task": {
                "pipeline": [
                    {"phase": 1, "name": "The Clerk: Deterministic Data Scaffolding"},
                    {"phase": 2, "name": "The Artist: Grounded Generation"},
                    {"phase": 3, "name": "The Assembler: Final Rendering & Validation"},
                ]
            },
            "3.context": {
                "pre_flight_file_complexity_gate": {
                    "thresholds": {"total_file_count_max": 5, "total_file_size_mb_max": 10}
                },
                "pre_flight_file_manifest_check": {"required_file_manifest": ["App_Schema_v4.json"]},
            },
            "4.reasoning": {
                "description": "Creative generation phase",
                "creative_brief": {
                    "headline": {"word_count": [8, 12], "char_count_max": 90},
                    "executive_summary": {
                        "word_count": [120, 140],
                        "voice": "third_person_implied",
                        "forbidden_patterns": [],
                    },
                    "experience_bullets": {
                        "unify_bullet_word_count": [28, 33],
                        "ibm_bullet_word_count": [24, 30],
                    },
                    "experience_overview": {"unify_word_count": [25, 33], "ibm_word_count": [22, 28]},
                    "leadership_competencies": {"word_count_per_desc": [24, 30]},
                    "cover_letter": {"word_count_per_para": [85, 100]},
                    "deduplication_matrix": {"thresholds": {}},
                },
                "hardcoded_config": {
                    "K.0": {
                        "description": "Thematic analysis",
                        "temp": 0.3,
                        "rag_total_calls": 50,
                        "rag_hops": 3,
                    },
                    "K.1": {
                        "description": "Executive summary",
                        "temp": 0.9,
                        "rag_total_calls": 4,
                        "rag_hops": 2,
                    },
                    "K.2": {
                        "description": "Competitive analysis",
                        "temp": 0.3,
                        "rag_total_calls": 24,
                        "rag_hops": 3,
                    },
                },
            },
        }

    def get_version(self) -> str:
        """Get the workflow version."""
        return self._workflow_data.get("metadata", {}).get("version", "unknown")

    def get_metadata(self) -> dict[str, Any]:
        """Get the metadata section."""
        if self._cached_metadata is None:
            self._cached_metadata = self._workflow_data.get("metadata", {})
        return self._cached_metadata

    def get_role_config(self) -> dict[str, Any]:
        """Get the role configuration (section 1)."""
        # guardian: allow-config-with-logic
        if self._cached_role_config is None:
            self._cached_role_config = self._workflow_data.get("1.role", {})
        return self._cached_role_config

    def get_task_pipeline(self) -> list[dict[str, Any]]:
        """Get the Task pipeline phases."""
        if self._cached_task_pipeline is None:
            self._cached_task_pipeline = self._workflow_data.get("2.Task", {}).get("pipeline", [])
        return self._cached_task_pipeline

    def get_context_config(self) -> dict[str, Any]:
        """Get the context management configuration."""
        # guardian: allow-config-with-logic
        if self._cached_context_config is None:
            self._cached_context_config = self._workflow_data.get("3.context", {})
        return self._cached_context_config

    def get_reasoning_config(self) -> dict[str, Any]:
        """Get the reasoning configuration."""
        # guardian: allow-config-with-logic
        if self._cached_reasoning_config is None:
            self._cached_reasoning_config = self._workflow_data.get("4.reasoning", {})
        return self._cached_reasoning_config

    def get_creative_brief(self) -> CreativeBriefConfig:
        """Extract and return the creative brief configuration."""
        if self._cached_creative_brief is None:
            BRIEF: Any = self.get_reasoning_config().get("creative_brief", {})
            self._cached_creative_brief = CreativeBriefConfig(
                headline_word_count=WordCountConstraints.from_list(
                    BRIEF.get("headline", {}).get("word_count", [8, 12])
                ),
                headline_char_max=BRIEF.get("headline", {}).get("char_count_max", 90),
                executive_summary_word_count=WordCountConstraints.from_list(
                    BRIEF.get("executive_summary", {}).get("word_count", [120, 140])
                ),
                executive_summary_voice=BRIEF.get("executive_summary", {}).get(
                    "voice", "third_person_implied"
                ),
                forbidden_patterns=BRIEF.get("executive_summary", {}).get("forbidden_patterns", []),
                unify_bullet_word_count=WordCountConstraints.from_list(
                    BRIEF.get("experience_bullets", {}).get("unify_bullet_word_count", [28, 33])
                ),
                ibm_bullet_word_count=WordCountConstraints.from_list(
                    BRIEF.get("experience_bullets", {}).get("ibm_bullet_word_count", [24, 30])
                ),
                unify_overview_word_count=WordCountConstraints.from_list(
                    BRIEF.get("experience_overview", {}).get("unify_word_count", [25, 33])
                ),
                ibm_overview_word_count=WordCountConstraints.from_list(
                    BRIEF.get("experience_overview", {}).get("ibm_word_count", [22, 28])
                ),
                competency_word_count=WordCountConstraints.from_list(
                    BRIEF.get("leadership_competencies", {}).get("word_count_per_desc", [24, 30])
                ),
                cover_letter_para_word_count=WordCountConstraints.from_list(
                    BRIEF.get("cover_letter", {}).get("word_count_per_para", [85, 100])
                ),
            )
        return self._cached_creative_brief

    def get_knode_configs(self) -> dict[str, KNodeConfig]:
        """Get all K-node configurations."""
        # guardian: allow-config-with-logic
        if self._cached_knode_configs is None:
            CONFIGS: Any = {}
            HARDCODED: Any = self.get_reasoning_config().get("hardcoded_config", {})
            for key, value in HARDCODED.items():
                if key.startswith("K.") and isinstance(value, dict):
                    CONFIGS[key] = KNodeConfig(
                        description=value.get("description", ""),
                        input_dependencies=value.get("input_dependencies", []),
                        TEMP=value.get("temp", 0.7),
                        RagType=value.get("RagType", "Hybrid"),
                        rag_total_calls=value.get("rag_total_calls", 4),
                        rag_hops=value.get("rag_hops", 2),
                        ClaimVerificationMode=value.get("ClaimVerificationMode", "strict"),
                        hybrid_cot_tot=value.get("hybrid_cot_tot", False),
                        cot_min_paths=value.get("cot_min_paths", 2),
                        tot_branches=value.get("tot_branches", 3),
                        min_tot_depth=value.get("min_tot_depth", 2),
                        self_consistency=value.get("self_consistency", 8),
                        REFLEXION=value.get("reflexion", False),
                        max_reflexion_loops=value.get("max_reflexion_loops", 3),
                    )
            self._cached_knode_configs = CONFIGS
        return self._cached_knode_configs

    def get_knode_config(self, node_id: str) -> KNodeConfig | None:
        """Get a specific K-node configuration."""
        CONFIGS: Any = self.get_knode_configs()
        return CONFIGS.get(node_id)

    def get_validation_rules(self) -> dict[str, Any]:
        """Get validation rules and thresholds."""
        if self._cached_validation_rules is None:
            REASONING: Any = self.get_reasoning_config()
            creative_brief: Any = REASONING.get("creative_brief", {})
            self._cached_validation_rules = creative_brief.get("deduplication_matrix", {}).get(
                "thresholds", {}
            )
        return self._cached_validation_rules

    def get_pre_flight_tests(self) -> list[dict[str, Any]]:
        """Get pre-flight validation tests."""
        if self._cached_pre_flight_tests is None:
            self._cached_pre_flight_tests = self._workflow_data.get("pre_flight_engine_validation", {}).get(
                TESTS_DIR, []
            )
        return self._cached_pre_flight_tests

    def get_file_complexity_thresholds(self) -> dict[str, int]:
        """Get file complexity gate thresholds."""
        if self._cached_file_complexity_thresholds is None:
            CONTEXT: Any = self.get_context_config()
            self._cached_file_complexity_thresholds = CONTEXT.get("pre_flight_file_complexity_gate", {}).get(
                "thresholds", {}
            )
        return self._cached_file_complexity_thresholds

    def get_required_files(self) -> list[str]:
        """Get list of required files."""
        if self._cached_required_files is None:
            CONTEXT: Any = self.get_context_config()
            self._cached_required_files = CONTEXT.get("pre_flight_file_manifest_check", {}).get(
                "required_file_manifest", []
            )
        return self._cached_required_files

    def get_enforcement_rules(self) -> list[str]:
        """Get critical enforcement rules."""
        if self._cached_enforcement_rules is None:
            self._cached_enforcement_rules = self.get_metadata().get("critical_rules_added", [])
        return self._cached_enforcement_rules

    def reload(self) -> None:
        """Reload the workflow from disk and clear all caches."""
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
        self._load_workflow()
        LOGGER.info("Workflow reloaded from disk with cleared caches")


def create_workflow_loader(workflow_path: str | Path | None = None) -> WorkflowLoader:
    """Create a WorkflowLoader instance."""
    return WorkflowLoader(workflow_path)
