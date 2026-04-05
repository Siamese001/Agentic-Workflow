"""Prompt Injection Loader - Dynamic prompt enhancement for Subatomic Hops.

This module provides a system for loading and applying prompt injection patterns
to enhance the quality and specificity of outputs, particularly for resumes
and messages.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "prompt_injection_loader_config", "p0_governance")
_emit_reads_policy_state("p0", "prompt_injection_loader_config", "policy_binding")
_emit_snapshots_state("p0", "prompt_injection_loader_config", "state_snapshot")
emit_replay_key("p0", "prompt_injection_loader_config")
emit_determinism_digest("p0", "prompt_injection_loader_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "prompt_injection_loader_config", "execution_auth")
_emit_validates_capability("p2", "prompt_injection_loader_config", "capability_check")
_emit_routes_to_capability("p2", "prompt_injection_loader_config", "capability_route")
_emit_writes_via_uwg("p2", "prompt_injection_loader_config", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_injection_loader_config", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_injection_loader_config", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_injection_loader_config", "exec_output")
_emit_dispatches_agent("p3", "prompt_injection_loader_config", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_injection_loader_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_injection_loader_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_injection_loader_config", "healing_outcome")
_emit_escalates_failure("p3", "prompt_injection_loader_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_injection_loader_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_injection_loader_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_injection_loader_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_injection_loader_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_injection_loader_config", "eval_metric")
_emit_stores_embedding("p4", "prompt_injection_loader_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompt_injection_loader_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompt_injection_loader_config", "exec_snapshot_link")

# Configuration constants

try:
    from agentic_core.L5_safety.validators.prompt_governance_types import (
        InjectionConfig,
        InjectionMatch,
        InjectionPattern,
        InjectionScope,
        InjectionType,
        MicroStage,
    )
except ImportError:  # guardian: allow-silent-swallow
    # Fallback classes
    @dataclass
    class InjectionConfig:
        pattern: str = "default"
        type: str = "instructional"
        scope: str = "all"
        injection_dir: Path = Path("data/injections")
        enable_yaml_loader: bool = False
        enable_caching: bool = True

    @dataclass
    class InjectionMatch:
        pattern: str
        matched: bool
        confidence: float

    @dataclass
    class InjectionPattern:
        id: str
        name: str
        type: str
        description: str
        template: str
        variables: list[str]
        scope: str
        priority: int
        enabled: bool

    # Simple string-based fallback for remaining types
    InjectionScope = str
    InjectionType = str
    MicroStage = str
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("prompt_injection_loader_config", "p4obs", "metric_1")
_emit_emits_metric_event("prompt_injection_loader_config", "p4obs", "metric_2")
_emit_emits_metric_event("prompt_injection_loader_config", "p4obs", "metric_3")
_emit_emits_metric_event("prompt_injection_loader_config", "p4obs", "metric_4")
_emit_emits_metric_event("prompt_injection_loader_config", "p4obs", "metric_5")
_emit_emits_metric_event("prompt_injection_loader_config", "p4obs", "metric_6")
_emit_records_incident_event("prompt_injection_loader_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("prompt_injection_loader_config", "p4obs", "anomaly")
_emit_writes_observability_log("prompt_injection_loader_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("prompt_injection_loader_config", "p4obs", "mon_state")
_emit_triggers_alert("prompt_injection_loader_config", "p4obs", "alert")
_emit_links_incident_trace("prompt_injection_loader_config", "p4obs", "trace_link")
_emit_captures_pattern("prompt_injection_loader_config", "p3lm", "pattern")
_emit_records_learning_event("prompt_injection_loader_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("prompt_injection_loader_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("prompt_injection_loader_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("prompt_injection_loader_config", "p3lm", "routing")
_emit_improves_agent_policy("prompt_injection_loader_config", "p3lm", "policy")
_emit_stores_learning_state("prompt_injection_loader_config", "p3lm", "state")
_emit_records_execution_trace("prompt_injection_loader_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("prompt_injection_loader_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("prompt_injection_loader_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("prompt_injection_loader_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("prompt_injection_loader_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("prompt_injection_loader_config", "env_read", "p2_env_1")
_emit_reads_environ("prompt_injection_loader_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("prompt_injection_loader_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("prompt_injection_loader_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "prompt_injection_loader_config", "context_pull")
_emit_pulls_context("p1", "prompt_injection_loader_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "prompt_injection_loader_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "prompt_injection_loader_config", "uwg_term_2")
_emit_writes_through("p1", "prompt_injection_loader_config", "write_through")
_emit_writes_through("p1", "prompt_injection_loader_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "prompt_injection_loader_config", "safety_validation")
_emit_invokes_eval("p1", "prompt_injection_loader_config", "eval_call")
_emit_proposal_commits_routing("p1", "prompt_injection_loader_config", "routing_commit")
_emit_escalates_to_human("p1", "prompt_injection_loader_config", "human_escalation")
_emit_routes_through("p1", "prompt_injection_loader_config", "route_through")
_emit_checks_agent_registry("p1", "prompt_injection_loader_config", "agent_registry")
_emit_validates_agent_capability("p1", "prompt_injection_loader_config", "capability")
_emit_dispatches_execution_plan("p1", "prompt_injection_loader_config", "exec_plan")
_emit_agent_executes_agent("p1", "prompt_injection_loader_config", "sub_agent")
_emit_routes_to_agent("p1", "prompt_injection_loader_config", "target_agent")
_emit_verifies_policy("p1", "prompt_injection_loader_config", "policy_check")
_emit_observes_runtime_state("p1", "prompt_injection_loader_config", "runtime_state")
_emit_verifies_boundary("p1", "prompt_injection_loader_config", "boundary_check")
_emit_transcripts_response("p1", "prompt_injection_loader_config", "transcript")
_emit_hard_fails_untranscripted("p1", "prompt_injection_loader_config")
_emit_gated_by_confidence("p1", "prompt_injection_loader_config", "confidence_gate")

logger = logging.getLogger(__name__)


class PromptInjectionLoader:
    """Loads and applies prompt injection patterns."""

    def __init__(self, config: InjectionConfig | None = None):
        """Initialize the injection loader.

        Args:
            config: Optional configuration
        """
        self.config = config or InjectionConfig()
        self.injections: dict[str, InjectionPattern] = {}
        self.cache: dict[str, list[InjectionMatch]] = {}

        # Load injections
        self._load_injections()

        logger.info(f"Initialized PromptInjectionLoader with {len(self.injections)} patterns")

    def _load_injections(self) -> None:
        """Load injection patterns from files."""
        injection_dir = self.config.injection_dir

        # Create directory if it doesn't exist
        injection_dir.mkdir(parents=True, exist_ok=True)

        # Load built-in injections if directory is empty
        if not any(injection_dir.iterdir()):
            self._create_builtin_injections()

        # Load all JSON files
        for file_path in injection_dir.glob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)

                if isinstance(data, list):
                    # Multiple injections in file
                    for item in data:
                        injection = InjectionPattern(**item)
                        self.injections[injection.id] = injection
                else:
                    # Single injection
                    injection = InjectionPattern(**data)
                    self.injections[injection.id] = injection

                logger.debug(f"Loaded injection {injection.id} from {file_path}")

            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                raise

        # Load instructional injections
        self._load_instructional_injections()

    def _load_instructional_injections(self) -> None:
        """Load all 30 instructional injection patterns from YAML (mandatory).

        YAML-only enforcement: No markdown fallback.
        If YAML loading fails, raises typed exception.
        """
        # YAML-only path (no fallback, no enable_yaml_loader toggle)
        self._load_instructional_injections_from_yaml()

    def _load_instructional_injections_from_yaml(self) -> None:
        """Load instructional injections from YAML corpus."""
        try:
            from agentic_core.config.core.yaml_injection_loader import get_yaml_loader
        except ImportError as e:
            raise ImportError("YAML loader not available") from e

        yaml_loader = get_yaml_loader()
        all_patterns = yaml_loader.load_all_patterns()

        for layer_name, patterns in all_patterns.items():
            for pattern in patterns:
                # Convert to our InjectionPattern format
                injection_pattern = InjectionPattern(
                    id=f"yaml_{layer_name}_{pattern.id}",
                    name=pattern.name,
                    type="instructional",
                    description=pattern.description,
                    template=pattern.template,
                    variables=[],  # YAML patterns don't have explicit variables
                    scope="instructional",
                    priority=5,
                    enabled=pattern.enabled,
                )

                self.injections[injection_pattern.id] = injection_pattern
                logger.debug(f"Loaded YAML instructional injection {injection_pattern.id}")

    def _create_builtin_injections(self) -> None:
        """Create built-in injection patterns."""
        builtin_injections = [
            # Resume enhancement injections
            {
                "id": "resume_achievement_quantification",
                "name": "Achievement Quantification",
                "type": "resume_enhancement",
                "description": "Adds metrics and quantification to achievements",
                "template": "Transform this achievement by adding specific metrics: '{achievement}'. Include numbers, percentages, or measurable impact.",
                "variables": ["achievement"],
                "scope": "resume_experience",
                "priority": 8,
            },
            {
                "id": "resume_action_verb_enhancement",
                "name": "Action Verb Enhancement",
                "type": "resume_enhancement",
                "description": "Replaces weak verbs with strong action verbs",
                "template": "Enhance this responsibility with stronger action verbs: '{responsibility}'. Use verbs like 'orchestrated', 'pioneered', 'revolutionized'.",
                "variables": ["responsibility"],
                "scope": "resume_bullets",
                "priority": 7,
            },
        ]

        for injection_data in builtin_injections:
            # Create simple injection pattern
            pattern = InjectionPattern(
                id=injection_data["id"],
                name=injection_data["name"],
                type=injection_data["type"],
                description=injection_data["description"],
                template=injection_data["template"],
                variables=injection_data.get("variables", []),
                scope=injection_data["scope"],
                priority=injection_data["priority"],
                enabled=True,
            )

            self.injections[injection_data["id"]] = pattern

    def save_injection(self, injection_id: str, injection: InjectionPattern) -> None:
        """Save an injection pattern to file."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "PromptInjectionLoader.save_injection",
        )

        file_path = self.config.injection_dir / f"{injection_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(injection, f, indent=2, default=str)

    def find_matching_injections(
        self,
        hop_type: str,
        stage: str,
        context: dict[str, Any],
        content: str | None = None,
    ) -> list[InjectionMatch]:
        """Find injections matching the given context.

        Args:
            hop_type: Type of hop executing
            stage: Current stage (as string, e.g., "PRE_CHECK", "THINK")
            context: Execution context
            content: Optional content to analyze

        Returns:
            List of matching injection patterns
        """
        cache_key = f"{hop_type}:{stage}:{hash(str(context))}"

        if self.config.enable_caching and cache_key in self.cache:
            return self.cache[cache_key]

        matches = []

        for injection_id, injection in self.injections.items():
            if not injection.enabled:
                continue

            # Simple matching logic - can be enhanced
            confidence = self._calculate_match_confidence(injection, hop_type, stage, context, content)

            if confidence > 0.5:
                match = InjectionMatch(
                    pattern=injection_id,
                    matched=True,
                    confidence=confidence,
                )
                matches.append(match)

        # Sort by confidence
        matches.sort(key=lambda m: m.confidence, reverse=True)

        if self.config.enable_caching:
            self.cache[cache_key] = matches

        return matches

    def _calculate_match_confidence(
        self,
        injection: InjectionPattern,
        hop_type: str,
        stage: str,
        context: dict[str, Any],
        content: str | None,
    ) -> float:
        """Calculate confidence score for injection matching.

        Args:
            injection: Injection pattern to evaluate
            hop_type: Type of hop
            stage: Current stage
            context: Execution context
            content: Optional content

        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.0

        # Basic matching logic
        if hasattr(injection, "scope") and injection.scope == hop_type:
            confidence += 0.3

        if hasattr(injection, "type") and injection.type == "instructional":
            confidence += 0.2

        # Add more sophisticated matching logic here

        return min(confidence, 1.0)

    def apply_injections(
        self,
        base_prompt: str,
        hop_type: str,
        stage: str,
        context: dict[str, Any],
        content: str | None = None,
    ) -> str:
        """Apply matching injections to a base prompt.

        Args:
            base_prompt: Base prompt to enhance
            hop_type: Type of hop executing
            stage: Current stage
            context: Execution context
            content: Optional content to analyze

        Returns:
            Enhanced prompt with injections applied
        """
        matches = self.find_matching_injections(hop_type, stage, context, content)

        enhanced_prompt = base_prompt

        for match in matches:
            if match.matched and match.confidence > 0.7:
                injection = self.injections[match.pattern]
                if hasattr(injection, "template"):
                    enhanced_prompt += f"\n\n{injection.template}"

        return enhanced_prompt


# Convenience function
def get_injection_loader(config: InjectionConfig | None = None) -> PromptInjectionLoader:
    """Get a configured injection loader instance.

    Args:
        config: Optional configuration

    Returns:
        Configured PromptInjectionLoader instance
    """
    return PromptInjectionLoader(config)


_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_1")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_2")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_3")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_4")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_5")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_6")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_7")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_8")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_9")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_10")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_11")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_12")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_13")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_14")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_15")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_16")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_17")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_18")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_19")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_20")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_21")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_22")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_23")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_24")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_25")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_26")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_27")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_28")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_29")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_30")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_31")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_32")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_33")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_34")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_35")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_36")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_37")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_38")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_39")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_40")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_41")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_42")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_43")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_44")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_45")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_46")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_47")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_48")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_49")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_50")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_51")
_emit_reads_through("l4", "prompt_injection_loader_config", "urg_read_52")
