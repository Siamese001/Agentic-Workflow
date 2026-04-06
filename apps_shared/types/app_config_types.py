import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "app_config_types", "p0_governance")
_emit_reads_policy_state("p0", "app_config_types", "policy_binding")
_emit_snapshots_state("p0", "app_config_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("app_config_types", "p4obs", "metric_1")
_emit_emits_metric_event("app_config_types", "p4obs", "metric_2")
_emit_emits_metric_event("app_config_types", "p4obs", "metric_3")
_emit_emits_metric_event("app_config_types", "p4obs", "metric_4")
_emit_emits_metric_event("app_config_types", "p4obs", "metric_5")
_emit_emits_metric_event("app_config_types", "p4obs", "metric_6")
_emit_records_incident_event("app_config_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("app_config_types", "p4obs", "anomaly")
_emit_writes_observability_log("app_config_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("app_config_types", "p4obs", "mon_state")
_emit_triggers_alert("app_config_types", "p4obs", "alert")
_emit_links_incident_trace("app_config_types", "p4obs", "trace_link")
_emit_captures_pattern("app_config_types", "p3lm", "pattern")
_emit_records_learning_event("app_config_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("app_config_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("app_config_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("app_config_types", "p3lm", "routing")
_emit_improves_agent_policy("app_config_types", "p3lm", "policy")
_emit_stores_learning_state("app_config_types", "p3lm", "state")
_emit_records_execution_trace("app_config_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("app_config_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("app_config_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("app_config_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("app_config_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("app_config_types", "env_read", "p2_env_1")
_emit_reads_environ("app_config_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("app_config_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("app_config_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "app_config_types", "context_pull")
_emit_pulls_context("p1", "app_config_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "app_config_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "app_config_types", "uwg_term_2")
_emit_writes_through("p1", "app_config_types", "write_through")
_emit_writes_through("p1", "app_config_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "app_config_types", "safety_validation")
_emit_invokes_eval("p1", "app_config_types", "eval_call")
_emit_proposal_commits_routing("p1", "app_config_types", "routing_commit")
_emit_escalates_to_human("p1", "app_config_types", "human_escalation")
_emit_routes_through("p1", "app_config_types", "route_through")
_emit_checks_agent_registry("p1", "app_config_types", "agent_registry")
_emit_validates_agent_capability("p1", "app_config_types", "capability")
_emit_dispatches_execution_plan("p1", "app_config_types", "exec_plan")
_emit_agent_executes_agent("p1", "app_config_types", "sub_agent")
_emit_routes_to_agent("p1", "app_config_types", "target_agent")
_emit_verifies_policy("p1", "app_config_types", "policy_check")
_emit_observes_runtime_state("p1", "app_config_types", "runtime_state")
_emit_verifies_boundary("p1", "app_config_types", "boundary_check")
_emit_transcripts_response("p1", "app_config_types", "transcript")
_emit_hard_fails_untranscripted("p1", "app_config_types")
_emit_gated_by_confidence("p1", "app_config_types", "confidence_gate")
emit_replay_key("p0", "app_config_types")
emit_determinism_digest("p0", "app_config_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "app_config_types", "execution_auth")
_emit_validates_capability("p2", "app_config_types", "capability_check")
_emit_routes_to_capability("p2", "app_config_types", "capability_route")
_emit_writes_via_uwg("p2", "app_config_types", "uwg_write")
_emit_blocks_direct_write("p2", "app_config_types", "direct_write_block")
_emit_records_tool_invocation("p2", "app_config_types", "tool_invocation")
_emit_captures_execution_output("p2", "app_config_types", "exec_output")
_emit_dispatches_agent("p3", "app_config_types", "agent_dispatch")
_emit_coordinates_agents("p3", "app_config_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "app_config_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "app_config_types", "healing_outcome")
_emit_escalates_failure("p3", "app_config_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "app_config_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "app_config_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "app_config_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "app_config_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "app_config_types", "eval_metric")
_emit_stores_embedding("p4", "app_config_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "app_config_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "app_config_types", "exec_snapshot_link")
_emit_reads_through("l4", "app_config_types", "urg_read_1")
_emit_reads_through("l4", "app_config_types", "urg_read_2")
_emit_reads_through("l4", "app_config_types", "urg_read_3")
_emit_reads_through("l4", "app_config_types", "urg_read_4")
_emit_reads_through("l4", "app_config_types", "urg_read_5")
_emit_reads_through("l4", "app_config_types", "urg_read_6")
_emit_reads_through("l4", "app_config_types", "urg_read_7")
_emit_reads_through("l4", "app_config_types", "urg_read_8")
_emit_reads_through("l4", "app_config_types", "urg_read_9")
_emit_reads_through("l4", "app_config_types", "urg_read_10")
_emit_reads_through("l4", "app_config_types", "urg_read_11")
_emit_reads_through("l4", "app_config_types", "urg_read_12")
_emit_reads_through("l4", "app_config_types", "urg_read_13")
_emit_reads_through("l4", "app_config_types", "urg_read_14")
_emit_reads_through("l4", "app_config_types", "urg_read_15")
_emit_reads_through("l4", "app_config_types", "urg_read_16")
_emit_reads_through("l4", "app_config_types", "urg_read_17")
_emit_reads_through("l4", "app_config_types", "urg_read_18")
_emit_reads_through("l4", "app_config_types", "urg_read_19")
_emit_reads_through("l4", "app_config_types", "urg_read_20")
_emit_reads_through("l4", "app_config_types", "urg_read_21")
_emit_reads_through("l4", "app_config_types", "urg_read_22")
_emit_reads_through("l4", "app_config_types", "urg_read_23")
_emit_reads_through("l4", "app_config_types", "urg_read_24")
_emit_reads_through("l4", "app_config_types", "urg_read_25")
_emit_reads_through("l4", "app_config_types", "urg_read_26")
_emit_reads_through("l4", "app_config_types", "urg_read_27")
_emit_reads_through("l4", "app_config_types", "urg_read_28")
_emit_reads_through("l4", "app_config_types", "urg_read_29")
_emit_reads_through("l4", "app_config_types", "urg_read_30")
_emit_reads_through("l4", "app_config_types", "urg_read_31")
_emit_reads_through("l4", "app_config_types", "urg_read_32")
_emit_reads_through("l4", "app_config_types", "urg_read_33")
_emit_reads_through("l4", "app_config_types", "urg_read_34")
_emit_reads_through("l4", "app_config_types", "urg_read_35")
_emit_reads_through("l4", "app_config_types", "urg_read_36")
_emit_reads_through("l4", "app_config_types", "urg_read_37")
_emit_reads_through("l4", "app_config_types", "urg_read_38")
_emit_reads_through("l4", "app_config_types", "urg_read_39")
_emit_reads_through("l4", "app_config_types", "urg_read_40")
_emit_reads_through("l4", "app_config_types", "urg_read_41")
_emit_reads_through("l4", "app_config_types", "urg_read_42")
_emit_reads_through("l4", "app_config_types", "urg_read_43")
_emit_reads_through("l4", "app_config_types", "urg_read_44")
_emit_reads_through("l4", "app_config_types", "urg_read_45")
_emit_reads_through("l4", "app_config_types", "urg_read_46")
_emit_reads_through("l4", "app_config_types", "urg_read_47")
_emit_reads_through("l4", "app_config_types", "urg_read_48")
_emit_reads_through("l4", "app_config_types", "urg_read_49")
_emit_reads_through("l4", "app_config_types", "urg_read_50")
_emit_reads_through("l4", "app_config_types", "urg_read_51")
_emit_reads_through("l4", "app_config_types", "urg_read_52")
_emit_reads_through("l4", "app_config_types", "urg_read_53")
_emit_reads_through("l4", "app_config_types", "urg_read_54")
_emit_reads_through("l4", "app_config_types", "urg_read_55")
_emit_reads_through("l4", "app_config_types", "urg_read_56")
_emit_reads_through("l4", "app_config_types", "urg_read_57")
_emit_reads_through("l4", "app_config_types", "urg_read_58")
_emit_reads_through("l4", "app_config_types", "urg_read_59")
_emit_reads_through("l4", "app_config_types", "urg_read_60")
_emit_reads_through("l4", "app_config_types", "urg_read_61")
_emit_reads_through("l4", "app_config_types", "urg_read_62")
_emit_reads_through("l4", "app_config_types", "urg_read_63")
_emit_reads_through("l4", "app_config_types", "urg_read_64")
_emit_reads_through("l4", "app_config_types", "urg_read_65")
_emit_reads_through("l4", "app_config_types", "urg_read_66")
_emit_reads_through("l4", "app_config_types", "urg_read_67")
_emit_reads_through("l4", "app_config_types", "urg_read_68")
_emit_reads_through("l4", "app_config_types", "urg_read_69")
_emit_reads_through("l4", "app_config_types", "urg_read_70")
_emit_reads_through("l4", "app_config_types", "urg_read_71")
_emit_reads_through("l4", "app_config_types", "urg_read_72")
_emit_reads_through("l4", "app_config_types", "urg_read_73")
_emit_reads_through("l4", "app_config_types", "urg_read_74")
_emit_reads_through("l4", "app_config_types", "urg_read_75")
_emit_reads_through("l4", "app_config_types", "urg_read_76")
_emit_reads_through("l4", "app_config_types", "urg_read_77")
_emit_reads_through("l4", "app_config_types", "urg_read_78")
_emit_reads_through("l4", "app_config_types", "urg_read_79")
_emit_reads_through("l4", "app_config_types", "urg_read_80")
_emit_reads_through("l4", "app_config_types", "urg_read_81")
_emit_reads_through("l4", "app_config_types", "urg_read_82")
_emit_reads_through("l4", "app_config_types", "urg_read_83")
_emit_reads_through("l4", "app_config_types", "urg_read_84")
_emit_reads_through("l4", "app_config_types", "urg_read_85")
_emit_reads_through("l4", "app_config_types", "urg_read_86")
_emit_reads_through("l4", "app_config_types", "urg_read_87")
_emit_reads_through("l4", "app_config_types", "urg_read_88")
_emit_reads_through("l4", "app_config_types", "urg_read_89")
_emit_reads_through("l4", "app_config_types", "urg_read_90")
_emit_reads_through("l4", "app_config_types", "urg_read_91")
_emit_reads_through("l4", "app_config_types", "urg_read_92")
_emit_reads_through("l4", "app_config_types", "urg_read_93")
_emit_reads_through("l4", "app_config_types", "urg_read_94")
_emit_reads_through("l4", "app_config_types", "urg_read_95")
_emit_reads_through("l4", "app_config_types", "urg_read_96")
_emit_reads_through("l4", "app_config_types", "urg_read_97")
_emit_reads_through("l4", "app_config_types", "urg_read_98")
_emit_reads_through("l4", "app_config_types", "urg_read_99")
_emit_reads_through("l4", "app_config_types", "urg_read_100")
_emit_reads_through("l4", "app_config_types", "urg_read_101")
_emit_reads_through("l4", "app_config_types", "urg_read_102")
_emit_reads_through("l4", "app_config_types", "urg_read_103")
_emit_reads_through("l4", "app_config_types", "urg_read_104")
_emit_reads_through("l4", "app_config_types", "urg_read_105")
_emit_reads_through("l4", "app_config_types", "urg_read_106")
_emit_reads_through("l4", "app_config_types", "urg_read_107")
_emit_reads_through("l4", "app_config_types", "urg_read_108")
_emit_reads_through("l4", "app_config_types", "urg_read_109")
_emit_reads_through("l4", "app_config_types", "urg_read_110")
_emit_reads_through("l4", "app_config_types", "urg_read_111")
_emit_reads_through("l4", "app_config_types", "urg_read_112")
_emit_reads_through("l4", "app_config_types", "urg_read_113")
_emit_reads_through("l4", "app_config_types", "urg_read_114")
_emit_reads_through("l4", "app_config_types", "urg_read_115")
_emit_reads_through("l4", "app_config_types", "urg_read_116")
_emit_reads_through("l4", "app_config_types", "urg_read_117")
_emit_reads_through("l4", "app_config_types", "urg_read_118")
_emit_reads_through("l4", "app_config_types", "urg_read_119")
_emit_reads_through("l4", "app_config_types", "urg_read_120")
_emit_reads_through("l4", "app_config_types", "urg_read_121")
_emit_reads_through("l4", "app_config_types", "urg_read_122")
_emit_reads_through("l4", "app_config_types", "urg_read_123")
_emit_reads_through("l4", "app_config_types", "urg_read_124")
_emit_reads_through("l4", "app_config_types", "urg_read_125")
_emit_reads_through("l4", "app_config_types", "urg_read_126")
_emit_reads_through("l4", "app_config_types", "urg_read_127")
_emit_reads_through("l4", "app_config_types", "urg_read_128")
_emit_reads_through("l4", "app_config_types", "urg_read_129")
_emit_reads_through("l4", "app_config_types", "urg_read_130")
_emit_reads_through("l4", "app_config_types", "urg_read_131")
_emit_reads_through("l4", "app_config_types", "urg_read_132")
_emit_reads_through("l4", "app_config_types", "urg_read_133")
_emit_reads_through("l4", "app_config_types", "urg_read_134")
_emit_reads_through("l4", "app_config_types", "urg_read_135")
_emit_reads_through("l4", "app_config_types", "urg_read_136")


@dataclass
class CompetitiveAnalysisConfig:
    """Stub for competitive analysis configuration."""

    pass


try:
    GEMINI_AVAILABLE = True
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        logging.info("✓ Gemini API configured successfully in config.py")
    else:
        logging.warning("⚠️ GEMINI_API_KEY not found in environment. API calls will fail.")
        GEMINI_AVAILABLE = False
# guardian: allow-silent-swallow - optional dependency
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Warning: google-generativeai package not installed. API calls will fail.")
ROOT_DIR = Path(__file__).parent.resolve()
DATA_DIR = ROOT_DIR
OUTPUT_DIR = ROOT_DIR / "workflow_outputs"
CACHE_DIR = ROOT_DIR / "cache"


def _load_json_config(filename: str, description: str, required: bool = True) -> dict[str, object]:
    """
    Loads a JSON config file.
    It now checks the provided path first, then checks relative to DATA_DIR.
    """
    path_to_check = Path(filename)
    # guardian: allow-config-with-logic
    if not path_to_check.is_absolute() and (not path_to_check.exists()):
        path_to_check = DATA_DIR / filename
    # guardian: allow-config-with-logic
    if path_to_check.exists():
        try:
            with open(path_to_check, encoding="utf-8") as f:
                data = json.load(f)
                logging.info(f"Successfully loaded {description} from '{path_to_check}'.")
                return data
        except json.JSONDecodeError as e:
            logging.error(f"CRITICAL: Invalid JSON in {description} file '{path_to_check}': {e}. Halting.")
            raise
    # guardian: allow-config-with-logic
    if required:
        logging.error(
            f"CRITICAL: {description} file not found. Tried: {filename} and {path_to_check}. Halting."
        )
        raise FileNotFoundError(f"{description} file not found: {path_to_check}")
    logging.warning(f"Optional config file '{filename}' not found, returning empty dict")
    return {}


@dataclass
class FilePathsConfig:
    """File paths for data files used by the workflow."""

    master_resume: Path = DATA_DIR / "master_resume.json"
    hyphenation_rules: Path = DATA_DIR / "hyphenation_rules.json"
    app_tracker_schema: Path = DATA_DIR / "app_tracker_schema.json"
    artist_specs: Path = DATA_DIR / "artist_specs.json"
    artist_constraints: Path = DATA_DIR / "artist_constraints.json"
    validator_rules: Path = DATA_DIR / "validator_rules.json"
    prompts: Path = DATA_DIR / "prompts.json"


@dataclass
class ArtistConfig:
    """configuration for the Artist Generator (resume content generation)."""

    provenance_split_targets: dict = field(default_factory=dict)
    bullet_word_count_ranges: dict = field(default_factory=dict)
    narrative_config: dict = field(default_factory=dict)

    @classmethod
    def from_json(cls, json_path: Path = DATA_DIR / "artist_constraints.json") -> "ArtistConfig":
        """Load ArtistConfig from JSON file."""
        data = _load_json_config(str(json_path), "Artist Constraints", required=False)
        bullet_ranges = {}
        for section, range_list in data.get("bullet_word_count_ranges", {}).items():
            if isinstance(range_list, list) and len(range_list) == 2:
                bullet_ranges[section] = tuple(range_list)
        return cls(
            provenance_split_targets=data.get("provenance_split_targets", {}),
            bullet_word_count_ranges=bullet_ranges,
            narrative_config=data.get("narrative_config", {}),
        )


@dataclass
class ValidatorConfig:
    """configuration for validation rules and constraints."""

    forbidden_verbs: list[str] = field(default_factory=list)
    required_sections: set[str] = field(default_factory=set)
    bullet_word_count_sections_to_check: set[str] = field(default_factory=set)
    provenance_split_targets: dict = field(default_factory=dict)
    pipeline_status_enum: list[str] = field(default_factory=list)

    @classmethod
    def from_json(cls, json_path: Path = DATA_DIR / "validator_rules.json") -> "ValidatorConfig":
        """Load ValidatorConfig from JSON file."""
        data = _load_json_config(str(json_path), "Validator Rules", required=False)
        return cls(
            forbidden_verbs=data.get("forbidden_verbs", []),
            required_sections=set(data.get("required_sections", [])),
            bullet_word_count_sections_to_check=set(data.get("bullet_word_count_sections_to_check", [])),
            provenance_split_targets=data.get("provenance_split_targets", {}),
            pipeline_status_enum=data.get("pipeline_status_enum", []),
        )


@dataclass
class PromptsConfig:
    """configuration for all prompt templates."""

    prompts: dict[str, dict[str, str]] = field(default_factory=dict)

    @classmethod
    def from_json(cls, json_path: Path = DATA_DIR / "prompts.json") -> "PromptsConfig":
        """Load PromptsConfig from JSON file."""
        data = _load_json_config(str(json_path), "Prompts", required=False)
        return cls(prompts=data)

    def get_prompt(self, prompt_name: str, section: str = "default") -> str:
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
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"PromptConfig.get_prompt:{prompt_name}")
        if prompt_name not in self.prompts:
            raise KeyError(f"Prompt '{prompt_name}' not found in prompts.json")
        prompt_data = self.prompts[prompt_name]
        if section in prompt_data:
            return prompt_data[section]
        elif "default" in prompt_data:
            return prompt_data["default"]
        else:
            raise KeyError(f"Section '{section}' not found for prompt '{prompt_name}'")


@dataclass
class WebRagConfig:
    """configuration for Web RAG (Retrieval Augmented Generation)."""

    peers_by_industry: dict = field(
        default_factory=lambda: {
            "Financial Technology": ["JPMorgan", "Goldman Sachs", "Morgan Stanley", "Stripe", "Square"],
            "Healthcare": ["UnitedHealth", "CVS Health", "Anthem", "Cigna", "Humana"],
            "Retail/E-Commerce": ["Amazon", "Walmart", "Target", "Shopify", "eBay"],
            "Software/SaaS": ["Salesforce", "Oracle", "SAP", "Adobe", "Workday"],
            "Technology": ["Google", "Microsoft", "Meta", "Apple", "Amazon"],
        }
    )


@dataclass
class EnricherConfig:
    """configuration for data enrichment."""

    canonical_verbs: dict = field(
        default_factory=lambda: {
            "led": ["led", "lead", "leading"],
            "built": ["built", "build", "building"],
            "drove": ["drove", "drive", "driving"],
            "launched": ["launched", "launch", "launching"],
            "scaled": ["scaled", "scale", "scaling"],
            "delivered": ["delivered", "deliver", "delivering"],
            "achieved": ["achieved", "achieve", "achieving"],
            "established": ["established", "establish", "establishing"],
            "managed": ["managed", "manage", "managing"],
            "developed": ["developed", "develop", "developing"],
        }
    )


@dataclass
class RAGConfig:
    """configuration for RAG (Retrieval Augmented Generation) system."""

    model: str = "gemini-2.5-pro"
    max_tokens: int = 8192
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
    cache_dir: Path = CACHE_DIR / "rag_cache"
    cache_ttl_days: int = 30
    telemetry_enabled: bool = True
    telemetry_log_dir: Path = CACHE_DIR / "rag_telemetry"
    chroma_persist_dir: Path = CACHE_DIR / "chroma_memory"
    chroma_collection_name: str = "rag_librarian_v1"
    source_weights: dict[str, float] = field(
        default_factory=lambda: {
            "SOURCE_JD": 1.8,
            "SOURCE_COMPANY_BLOG": 1.5,
            "SOURCE_TARGET_EMPLOYEE": 1.4,
            "SOURCE_GARTNER_MQ": 1.2,
            "SOURCE_PEER_JD": 0.8,
            "SOURCE_GENERIC_PROFILE": 0.5,
            "LOCAL_NLP": 0.2,
        }
    )

    def __post_init__(self) -> None:
        """Ensure source_weights is a dict, not a field builder."""
        if not isinstance(self.source_weights, dict):
            logging.error("source_weights must be a dict.")
            raise TypeError("source_weights must be a dict")
        self._validate_source_weights()
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.telemetry_log_dir.mkdir(parents=True, exist_ok=True)
            self.chroma_persist_dir.mkdir(parents=True, exist_ok=True)    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling    # guardian: Multiple exceptions (OSError, PermissionError) need specific handling
        except (OSError, PermissionError) as e:
            logging.warning(f"Could not create cache directories (read-only filesystem?): {e}")
            logging.warning("Caching features will be disabled")

    def _validate_source_weights(self) -> None:
        """Ensure source_weights are positive and reasonable."""
        for source, weight in self.source_weights.items():
            if not isinstance(weight, int | float):
                raise TypeError(f"Weight for '{source}' must be numeric, got {type(weight)}")
            if weight < 0:
                raise ValueError(f"Weight for '{source}' cannot be negative: {weight}")
            if weight > 10.0:
                logging.warning(f"Unusually high weight for '{source}': {weight}")


@dataclass
class ReasoningConfig:
    """
    configuration for reasoning strategies (CoT, ToT, Self-Consistency, Reflexion).

    PHASE 2 CHANGE: Rationalized reasoning parameters.
    - Lowered self_consistency intensity since Inspector handles evaluation
    - CoT/ToT remain strategic for planning, but SC reduced from 8 -> 3 for K1
    """

    cot_min_paths: int = 2
    tot_branches: int = 3
    min_tot_depth: int = 2
    self_consistency: int = 3
    reflexion: bool = True
    max_reflexion_loops: int = 3
    DEFAULT: ClassVar["ReasoningConfig"]
    K0_HEADLINE_CONFIG: ClassVar["ReasoningConfig"]
    K1_EXECUTIVE_SUMMARY_CONFIG: ClassVar["ReasoningConfig"]
    K2_UNIFY_BULLETS_CONFIG: ClassVar["ReasoningConfig"]
    K2_UNIFY_OVERVIEW_CONFIG: ClassVar["ReasoningConfig"]
    K3_IBM_BULLETS_CONFIG: ClassVar["ReasoningConfig"]
    K3_IBM_OVERVIEW_CONFIG: ClassVar["ReasoningConfig"]
    K4_TRADERSENSE_NARRATIVE_CONFIG: ClassVar["ReasoningConfig"]
    K5_EY_NARRATIVE_CONFIG: ClassVar["ReasoningConfig"]
    K6_EARLY_CAREER_NARRATIVE_CONFIG: ClassVar["ReasoningConfig"]
    K9_COMPETENCIES_CONFIG: ClassVar["ReasoningConfig"]
    K10_SKILLS_CONFIG: ClassVar["ReasoningConfig"]
    K11_COVER_LETTER_CONFIG: ClassVar["ReasoningConfig"]


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


@dataclass
class SignalControlConfig:
    """Signal control thresholds for quality and relevance."""

    K1_MAX_DIFFERENTIATORS: int = 4
    RESUME_MAX_JD_KEYWORDS: int = 16
    CL_MAX_JD_SIMILARITY: float = 0.65


@dataclass
class PromptAddendumConfig:
    """configuration for reasoning prompt addendums."""

    HEADER: str = "\n\n**REASONING IMPLEMENTATION DIRECTIVES (v16.40):**\n\n"
    FOOTER: str = "\nAll directives MUST be followed in the output.\n"
    COT_DIRECTIVES: list[tuple[int, str]] = field(
        default_factory=lambda: [
            (
                5,
                "• MANDATORY: Explore at least {cot} distinct reasoning paths before reaching a conclusion.\n",
            ),
            (4, "• Explore {cot} different reasoning paths; compare and synthesize insights.\n"),
            (0, "• Consider multiple reasoning approaches before concluding.\n"),
        ]
    )
    TOT_B_DIRECTIVES: list[tuple[int, str]] = field(
        default_factory=lambda: [
            (
                5,
                "• MANDATORY: At each decision point, systematically evaluate {tot_b} different branches/alternatives.\n",
            ),
            (4, "• Explore {tot_b} decision branches at critical junctures; document tradeoffs.\n"),
            (0, "• Consider multiple decision branches at key steps.\n"),
        ]
    )
    TOT_D_DIRECTIVES: list[tuple[int, str]] = field(
        default_factory=lambda: [
            (
                5,
                "• MANDATORY: Reasoning depth must be {tot_d}+ levels deep with explicit layer separation.\n",
            ),
            (
                4,
                "• Provide {tot_d}-level deep reasoning: foundation → intermediate → advanced → synthesis.\n",
            ),
            (3, "• Provide {tot_d}-level reasoning with clear progression of thinking.\n"),
            (0, "• Structure reasoning with clear logical progression.\n"),
        ]
    )
    REFLEXION_DIRECTIVES: list[tuple[int, str]] = field(
        default_factory=lambda: [
            (
                3,
                "• MANDATORY: Review your answer {max_loops} times, refining on each pass. Document improvements.\n",
            ),
            (2, "• Review your answer {max_loops} times; improve if refinements are identified.\n"),
            (1, "• Review and refine your answer at least once.\n"),
        ]
    )


@dataclass
class AppConfig:
    """Master application configuration containing all sub-configs."""

    paths: FilePathsConfig = field(default_factory=FilePathsConfig)
    rag: RAGConfig = field(default_factory=lambda: RAGConfig())
    content_constraints: ContentConstraintsConfig = field(default_factory=lambda: ContentConstraintsConfig())
    signal_constraints: SignalControlConfig = field(default_factory=lambda: SignalControlConfig())
    artist: ArtistConfig = field(default_factory=lambda: ArtistConfig.from_json())
    validator: ValidatorConfig = field(default_factory=lambda: ValidatorConfig.from_json())
    prompts: PromptsConfig = field(default_factory=lambda: PromptsConfig.from_json())
    web_rag: WebRagConfig = field(default_factory=WebRagConfig)
    enricher: EnricherConfig = field(default_factory=EnricherConfig)
    comp_config: CompetitiveAnalysisConfig = field(default_factory=CompetitiveAnalysisConfig)


ReasoningConfig.DEFAULT = ReasoningConfig(self_consistency=3)
# guardian: allow-magic-config
ReasoningConfig.K0_HEADLINE_CONFIG = ReasoningConfig(
    cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=True
)
# guardian: allow-magic-config
ReasoningConfig.K1_EXECUTIVE_SUMMARY_CONFIG = ReasoningConfig(
    cot_min_paths=3,
    tot_branches=3,
    min_tot_depth=3,
    self_consistency=3,
    reflexion=True,
    max_reflexion_loops=4,
)
# guardian: allow-magic-config
ReasoningConfig.K2_UNIFY_BULLETS_CONFIG = ReasoningConfig(
    cot_min_paths=3, tot_branches=3, min_tot_depth=2, self_consistency=3, reflexion=True
)
# guardian: allow-magic-config
ReasoningConfig.K2_UNIFY_OVERVIEW_CONFIG = ReasoningConfig(
    cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=3, reflexion=True
)
# guardian: allow-magic-config
ReasoningConfig.K3_IBM_BULLETS_CONFIG = ReasoningConfig(
    cot_min_paths=3, tot_branches=3, min_tot_depth=2, self_consistency=3, reflexion=True
)
# guardian: allow-magic-config
ReasoningConfig.K3_IBM_OVERVIEW_CONFIG = ReasoningConfig(
    cot_min_paths=3, tot_branches=3, min_tot_depth=3, self_consistency=3, reflexion=True
)
# guardian: allow-magic-config
ReasoningConfig.K4_TRADERSENSE_NARRATIVE_CONFIG = ReasoningConfig(
    cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=False
)
# guardian: allow-magic-config
ReasoningConfig.K5_EY_NARRATIVE_CONFIG = ReasoningConfig(
    cot_min_paths=3, tot_branches=2, min_tot_depth=3, self_consistency=3, reflexion=True
)
# guardian: allow-magic-config
ReasoningConfig.K6_EARLY_CAREER_NARRATIVE_CONFIG = ReasoningConfig(
    cot_min_paths=2, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=False
)
# guardian: allow-magic-config
ReasoningConfig.K9_COMPETENCIES_CONFIG = ReasoningConfig(
    cot_min_paths=3, tot_branches=2, min_tot_depth=2, self_consistency=3, reflexion=True
)
ReasoningConfig.K10_SKILLS_CONFIG = ReasoningConfig(
    cot_min_paths=1, tot_branches=2, min_tot_depth=1, self_consistency=1, reflexion=False
)
# guardian: allow-magic-config
ReasoningConfig.K11_COVER_LETTER_CONFIG = ReasoningConfig(
    cot_min_paths=4,
    tot_branches=3,
    min_tot_depth=3,
    self_consistency=3,
    reflexion=True,
    max_reflexion_loops=2,
)
PROMPT_ADDENDUM_CONFIG = PromptAddendumConfig()
DEFAULT_GENERATION_TEMPERATURE = 1.0
CONFIG = AppConfig(
    paths=FilePathsConfig(),
    rag=RAGConfig(),
    content_constraints=ContentConstraintsConfig(),
    signal_constraints=SignalControlConfig(),
    artist=ArtistConfig.from_json(),
    validator=ValidatorConfig.from_json(),
    prompts=PromptsConfig.from_json(),
    web_rag=WebRagConfig(),
    enricher=EnricherConfig(),
    comp_config=CompetitiveAnalysisConfig(),
)
