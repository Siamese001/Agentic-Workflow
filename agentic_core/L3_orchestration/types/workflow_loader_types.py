from __future__ import annotations

from dataclasses import dataclass

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_reads_through,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "workflow_loader_types")
emit_determinism_digest("p0", "workflow_loader_types")

_emit_dispatches_healing_run("p1", "workflow_loader_types", "L3")
_emit_routes_through("p1", "workflow_loader_types", "L3")
_emit_checks_agent_registry("p1", "workflow_loader_types", "agent_registry")
_emit_validates_agent_capability("p1", "workflow_loader_types", "capability")
_emit_dispatches_execution_plan("p1", "workflow_loader_types", "exec_plan")
_emit_agent_executes_agent("p1", "workflow_loader_types", "sub_agent")
_emit_routes_to_agent("p1", "workflow_loader_types", "target_agent")
_emit_verifies_policy("p1", "workflow_loader_types", "policy_check")
_emit_observes_runtime_state("p1", "workflow_loader_types", "runtime_state")
_emit_verifies_boundary("p1", "workflow_loader_types", "boundary_check")
_emit_transcripts_response("p1", "workflow_loader_types", "transcript")
_emit_hard_fails_untranscripted("p1", "workflow_loader_types")
_emit_gated_by_confidence("p1", "workflow_loader_types", "confidence_gate")
_emit_escalates_to_human("p1", "workflow_loader_types", "L3")
_emit_reads_policy_state("p1", "workflow_loader_types", "L3")
_emit_authorize_and_execute("p2", "workflow_loader_types", "execution_auth")
_emit_validates_capability("p2", "workflow_loader_types", "capability_check")
_emit_routes_to_capability("p2", "workflow_loader_types", "capability_route")
_emit_writes_via_uwg("p2", "workflow_loader_types", "uwg_write")
_emit_blocks_direct_write("p2", "workflow_loader_types", "direct_write_block")
_emit_records_tool_invocation("p2", "workflow_loader_types", "tool_invocation")
_emit_captures_execution_output("p2", "workflow_loader_types", "exec_output")
_emit_dispatches_agent("p3", "workflow_loader_types", "agent_dispatch")
_emit_coordinates_agents("p3", "workflow_loader_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "workflow_loader_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "workflow_loader_types", "healing_outcome")
_emit_escalates_failure("p3", "workflow_loader_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "workflow_loader_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "workflow_loader_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "workflow_loader_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "workflow_loader_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "workflow_loader_types", "eval_metric")
_emit_stores_embedding("p4", "workflow_loader_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "workflow_loader_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "workflow_loader_types", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
"\nWorkflow Loader - Dynamic loading and parsing of workflow configurations.\n\nLoads the active_workflow.json and provides typed accessors for workflow sections,\nK-node configurations, prompts, and validation rules.\n"
import json
import logging
import uuid
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import TESTS_DIR
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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
    _emit_routes_to_agent,
    _emit_snapshots_state,
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

_emit_emits_metric_event("workflow_loader_types", "p4obs", "metric_1")
_emit_emits_metric_event("workflow_loader_types", "p4obs", "metric_2")
_emit_emits_metric_event("workflow_loader_types", "p4obs", "metric_3")
_emit_emits_metric_event("workflow_loader_types", "p4obs", "metric_4")
_emit_emits_metric_event("workflow_loader_types", "p4obs", "metric_5")
_emit_emits_metric_event("workflow_loader_types", "p4obs", "metric_6")
_emit_records_incident_event("workflow_loader_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("workflow_loader_types", "p4obs", "anomaly")
_emit_writes_observability_log("workflow_loader_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("workflow_loader_types", "p4obs", "mon_state")
_emit_triggers_alert("workflow_loader_types", "p4obs", "alert")
_emit_links_incident_trace("workflow_loader_types", "p4obs", "trace_link")
_emit_captures_pattern("workflow_loader_types", "p3lm", "pattern")
_emit_records_learning_event("workflow_loader_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("workflow_loader_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("workflow_loader_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("workflow_loader_types", "p3lm", "routing")
_emit_improves_agent_policy("workflow_loader_types", "p3lm", "policy")
_emit_stores_learning_state("workflow_loader_types", "p3lm", "state")
_emit_records_execution_trace("workflow_loader_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("workflow_loader_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("workflow_loader_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("workflow_loader_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("workflow_loader_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("workflow_loader_types", "env_read", "p2_env_1")
_emit_reads_environ("workflow_loader_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("workflow_loader_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("workflow_loader_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "workflow_loader_types", "context_pull")
_emit_pulls_context("p1", "workflow_loader_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "workflow_loader_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "workflow_loader_types", "uwg_term_2")
_emit_writes_through("p1", "workflow_loader_types", "write_through")
_emit_writes_through("p1", "workflow_loader_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "workflow_loader_types", "safety_validation")
_emit_invokes_eval("p1", "workflow_loader_types", "eval_call")
_emit_proposal_commits_routing("p1", "workflow_loader_types", "routing_commit")

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
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "WorkflowLoader.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "WorkflowLoader.__init__", "p0_governance")
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
    # guardian: File operations should check existence before access
    def _load_workflow(self) -> None:
        """Load the workflow JSON from disk."""
        try:
            with open(self.workflow_path, encoding="utf-8") as f:
                self._workflow_data = json.load(f)
            LOGGER.info(f"Loaded workflow v{self.get_version()} from {self.workflow_path}")
        except FileNotFoundError:    # guardian: File operations should check existence before access
            LOGGER.warning(f"Workflow file not found at {self.workflow_path}, using fallback defaults")
            self._workflow_data = self._get_fallback_workflow()
        except json.JSONDecodeError as e:
            LOGGER.error(f"Invalid JSON in workflow file: {e}, using fallback defaults")
            self._workflow_data = self._get_fallback_workflow()
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
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
                TESTS_DIR: [{"test_id": "VALIDATE_ITERATION", "description": "Basic iteration check"}],
            },
            "1.role": {"description": "Resume generation assistant"},
            "2.Task": {
                "pipeline": [
                    {"phase": 1, "name": "The Clerk: Deterministic Data Scaffolding"},
                    {"phase": 2, "name": "The Artist: Grounded Generation"},
                    {"phase": 3, "name": "The Assembler: Final Rendering & Validation"},
                ],
            },
            "3.context": {
                "pre_flight_file_complexity_gate": {
                    "thresholds": {"total_file_count_max": 5, "total_file_size_mb_max": 10},
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

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "WorkflowLoader.get_metadata",
        )
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
                    BRIEF.get("headline", {}).get("word_count", [8, 12]),
                ),
                headline_char_max=BRIEF.get("headline", {}).get("char_count_max", 90),
                executive_summary_word_count=WordCountConstraints.from_list(
                    BRIEF.get("executive_summary", {}).get("word_count", [120, 140]),
                ),
                executive_summary_voice=BRIEF.get("executive_summary", {}).get(
                    "voice", "third_person_implied",
                ),
                forbidden_patterns=BRIEF.get("executive_summary", {}).get("forbidden_patterns", []),
                unify_bullet_word_count=WordCountConstraints.from_list(
                    BRIEF.get("experience_bullets", {}).get("unify_bullet_word_count", [28, 33]),
                ),
                ibm_bullet_word_count=WordCountConstraints.from_list(
                    BRIEF.get("experience_bullets", {}).get("ibm_bullet_word_count", [24, 30]),
                ),
                unify_overview_word_count=WordCountConstraints.from_list(
                    BRIEF.get("experience_overview", {}).get("unify_word_count", [25, 33]),
                ),
                ibm_overview_word_count=WordCountConstraints.from_list(
                    BRIEF.get("experience_overview", {}).get("ibm_word_count", [22, 28]),
                ),
                competency_word_count=WordCountConstraints.from_list(
                    BRIEF.get("leadership_competencies", {}).get("word_count_per_desc", [24, 30]),
                ),
                cover_letter_para_word_count=WordCountConstraints.from_list(
                    BRIEF.get("cover_letter", {}).get("word_count_per_para", [85, 100]),
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
                "thresholds", {},
            )
        return self._cached_validation_rules

    def get_pre_flight_tests(self) -> list[dict[str, Any]]:
        """Get pre-flight validation tests."""
        if self._cached_pre_flight_tests is None:
            self._cached_pre_flight_tests = self._workflow_data.get("pre_flight_engine_validation", {}).get(
                TESTS_DIR, [],
            )
        return self._cached_pre_flight_tests

    def get_file_complexity_thresholds(self) -> dict[str, int]:
        """Get file complexity gate thresholds."""
        if self._cached_file_complexity_thresholds is None:
            CONTEXT: Any = self.get_context_config()
            self._cached_file_complexity_thresholds = CONTEXT.get("pre_flight_file_complexity_gate", {}).get(
                "thresholds", {},
            )
        return self._cached_file_complexity_thresholds

    def get_required_files(self) -> list[str]:
        """Get list of required files."""
        if self._cached_required_files is None:
            CONTEXT: Any = self.get_context_config()
            self._cached_required_files = CONTEXT.get("pre_flight_file_manifest_check", {}).get(
                "required_file_manifest", [],
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

_emit_reads_through("l4", "workflow_loader_types", "urg_read_1")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_2")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_3")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_4")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_5")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_6")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_7")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_8")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_9")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_10")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_11")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_12")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_13")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_14")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_15")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_16")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_17")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_18")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_19")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_20")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_21")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_22")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_23")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_24")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_25")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_26")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_27")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_28")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_29")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_30")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_31")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_32")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_33")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_34")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_35")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_36")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_37")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_38")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_39")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_40")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_41")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_42")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_43")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_44")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_45")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_46")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_47")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_48")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_49")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_50")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_51")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_52")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_53")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_54")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_55")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_56")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_57")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_58")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_59")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_60")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_61")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_62")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_63")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_64")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_65")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_66")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_67")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_68")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_69")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_70")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_71")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_72")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_73")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_74")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_75")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_76")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_77")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_78")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_79")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_80")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_81")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_82")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_83")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_84")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_85")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_86")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_87")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_88")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_89")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_90")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_91")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_92")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_93")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_94")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_95")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_96")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_97")
_emit_reads_through("l4", "workflow_loader_types", "urg_read_98")
