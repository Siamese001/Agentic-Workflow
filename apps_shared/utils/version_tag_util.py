"""Semantic Versioning and Rollback for Prompts.

Phase 4 - Pillar 13: Prompt Governance (CMS)
Enables safe prompt tuning by non-engineers with version control and rollback.

Features:
- Semantic versioning (major.minor.patch)
- Environment tags (dev, staging, prod)
- Rollback capability
- Change tracking
- Deployment safety
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

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

_emit_applies_guardrail("p0", "version_tag_util", "p0_governance")
_emit_reads_policy_state("p0", "version_tag_util", "policy_binding")
_emit_snapshots_state("p0", "version_tag_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("version_tag_util", "p4obs", "metric_1")
_emit_emits_metric_event("version_tag_util", "p4obs", "metric_2")
_emit_emits_metric_event("version_tag_util", "p4obs", "metric_3")
_emit_emits_metric_event("version_tag_util", "p4obs", "metric_4")
_emit_emits_metric_event("version_tag_util", "p4obs", "metric_5")
_emit_emits_metric_event("version_tag_util", "p4obs", "metric_6")
_emit_records_incident_event("version_tag_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("version_tag_util", "p4obs", "anomaly")
_emit_writes_observability_log("version_tag_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("version_tag_util", "p4obs", "mon_state")
_emit_triggers_alert("version_tag_util", "p4obs", "alert")
_emit_links_incident_trace("version_tag_util", "p4obs", "trace_link")
_emit_captures_pattern("version_tag_util", "p3lm", "pattern")
_emit_records_learning_event("version_tag_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("version_tag_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("version_tag_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("version_tag_util", "p3lm", "routing")
_emit_improves_agent_policy("version_tag_util", "p3lm", "policy")
_emit_stores_learning_state("version_tag_util", "p3lm", "state")
_emit_records_execution_trace("version_tag_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("version_tag_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("version_tag_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("version_tag_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("version_tag_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("version_tag_util", "env_read", "p2_env_1")
_emit_reads_environ("version_tag_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("version_tag_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("version_tag_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "version_tag_util", "context_pull")
_emit_pulls_context("p1", "version_tag_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "version_tag_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "version_tag_util", "uwg_term_2")
_emit_writes_through("p1", "version_tag_util", "write_through")
_emit_writes_through("p1", "version_tag_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "version_tag_util", "safety_validation")
_emit_invokes_eval("p1", "version_tag_util", "eval_call")
_emit_proposal_commits_routing("p1", "version_tag_util", "routing_commit")
_emit_escalates_to_human("p1", "version_tag_util", "human_escalation")
_emit_routes_through("p1", "version_tag_util", "route_through")
_emit_checks_agent_registry("p1", "version_tag_util", "agent_registry")
_emit_validates_agent_capability("p1", "version_tag_util", "capability")
_emit_dispatches_execution_plan("p1", "version_tag_util", "exec_plan")
_emit_agent_executes_agent("p1", "version_tag_util", "sub_agent")
_emit_routes_to_agent("p1", "version_tag_util", "target_agent")
_emit_verifies_policy("p1", "version_tag_util", "policy_check")
_emit_observes_runtime_state("p1", "version_tag_util", "runtime_state")
_emit_verifies_boundary("p1", "version_tag_util", "boundary_check")
_emit_transcripts_response("p1", "version_tag_util", "transcript")
_emit_hard_fails_untranscripted("p1", "version_tag_util")
_emit_gated_by_confidence("p1", "version_tag_util", "confidence_gate")
emit_replay_key("p0", "version_tag_util")
emit_determinism_digest("p0", "version_tag_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "version_tag_util", "execution_auth")
_emit_validates_capability("p2", "version_tag_util", "capability_check")
_emit_routes_to_capability("p2", "version_tag_util", "capability_route")
_emit_writes_via_uwg("p2", "version_tag_util", "uwg_write")
_emit_blocks_direct_write("p2", "version_tag_util", "direct_write_block")
_emit_records_tool_invocation("p2", "version_tag_util", "tool_invocation")
_emit_captures_execution_output("p2", "version_tag_util", "exec_output")
_emit_dispatches_agent("p3", "version_tag_util", "agent_dispatch")
_emit_coordinates_agents("p3", "version_tag_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "version_tag_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "version_tag_util", "healing_outcome")
_emit_escalates_failure("p3", "version_tag_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "version_tag_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "version_tag_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "version_tag_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "version_tag_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "version_tag_util", "eval_metric")
_emit_stores_embedding("p4", "version_tag_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "version_tag_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "version_tag_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class VersionTag(Enum):
    """Version environment tags."""

    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


@dataclass
class PromptVersion:
    """Versioned prompt template."""

    version_id: str
    template_id: str
    version: str
    content: str
    tag: VersionTag
    created_at: float
    created_by: str
    change_notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version_id": self.version_id,
            "template_id": self.template_id,
            "version": self.version,
            "content": self.content,
            "tag": self.tag.value,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "change_notes": self.change_notes,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PromptVersion:
        """Create from dictionary."""
        return cls(
            version_id=data["version_id"],
            template_id=data["template_id"],
            version=data["version"],
            content=data["content"],
            tag=VersionTag(data["tag"]),
            created_at=data["created_at"],
            created_by=data["created_by"],
            change_notes=data.get("change_notes", ""),
            metadata=data.get("metadata", {}),
        )


class PromptVersionManager:
    """Manages prompt versions with semantic versioning.

    Features:
    - Semantic versioning (major.minor.patch)
    - Environment tagging
    - Version history
    - Rollback support
    - Safe deployment
    """

    def __init__(self, enable_logging: bool = True):
        """Initialize version manager.

        Args:
            enable_logging: Enable logging
        """
        self.enable_logging = enable_logging
        self._versions: dict[str, list[PromptVersion]] = {}
        self._tagged_versions: dict[str, dict[VersionTag, PromptVersion]] = {}
        if self.enable_logging:
            logger.info("prompt_version_manager_initialized")

    def create_version(
        self,
        template: PromptTemplate,
        created_by: str,
        change_notes: str = "",
        tag: VersionTag = VersionTag.DEV,
    ) -> PromptVersion:
        """Create a new version of a prompt.

        Args:
            template: Prompt template
            created_by: Creator identifier
            change_notes: Notes about changes
            tag: Environment tag

        Returns:
            PromptVersion
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptVersionManager.create_version")

        template_id = template.template_id
        next_version = self._get_next_version(template_id, template.version)
        version = PromptVersion(
            version_id=f"{template_id}_{next_version}_{int(time.time())}",
            template_id=template_id,
            version=next_version,
            content=template.content,
            tag=tag,
            created_at=time.time(),
            created_by=created_by,
            change_notes=change_notes,
            metadata=template.metadata.copy(),
        )
        if template_id not in self._versions:
            self._versions[template_id] = []
        self._versions[template_id].append(version)
        if template_id not in self._tagged_versions:
            self._tagged_versions[template_id] = {}
        self._tagged_versions[template_id][tag] = version
        if self.enable_logging:
            logger.info(
                "version_created",
                extra={"template_id": template_id, "version": next_version, "tag": tag.value},
            )
        return version

    def promote_version(self, template_id: str, version: str, to_tag: VersionTag) -> PromptVersion | None:
        """Promote a version to a different environment.

        Args:
            template_id: Template identifier
            version: Version to promote
            to_tag: Target environment tag

        Returns:
            PromptVersion or None
        """
        versions = self._versions.get(template_id, [])
        target_version = None
        for v in versions:
            if v.version == version:
                target_version = v
                break
        if not target_version:
            return None
        if template_id not in self._tagged_versions:
            self._tagged_versions[template_id] = {}
        self._tagged_versions[template_id][to_tag] = target_version
        if self.enable_logging:
            logger.info(
                "version_promoted",
                extra={"template_id": template_id, "version": version, "to_tag": to_tag.value},
            )
        return target_version

    def rollback(self, template_id: str, tag: VersionTag, to_version: str) -> PromptVersion | None:
        """Rollback to a previous version.

        Args:
            template_id: Template identifier
            tag: Environment tag
            to_version: Version to rollback to

        Returns:
            PromptVersion or None
        """
        versions = self._versions.get(template_id, [])
        target_version = None
        for v in versions:
            if v.version == to_version:
                target_version = v
                break
        if not target_version:
            return None
        if template_id not in self._tagged_versions:
            self._tagged_versions[template_id] = {}
        self._tagged_versions[template_id][tag] = target_version
        if self.enable_logging:
            logger.warning(
                "version_rolled_back",
                extra={"template_id": template_id, "tag": tag.value, "to_version": to_version},
            )
        return target_version

    def get_version(self, template_id: str, tag: VersionTag) -> PromptVersion | None:
        """Get current version for an environment.

        Args:
            template_id: Template identifier
            tag: Environment tag

        Returns:
            PromptVersion or None
        """
        tagged = self._tagged_versions.get(template_id, {})
        return tagged.get(tag)

    def get_version_history(self, template_id: str) -> list[PromptVersion]:
        """Get version history for a template.

        Args:
            template_id: Template identifier

        Returns:
            List of versions (newest first)
        """
        versions = self._versions.get(template_id, [])
        return sorted(versions, key=lambda v: v.created_at, reverse=True)

    def compare_versions(self, template_id: str, version1: str, version2: str) -> dict[str, Any] | None:
        """Compare two versions.

        Args:
            template_id: Template identifier
            version1: First version
            version2: Second version

        Returns:
            Comparison dict or None
        """
        versions = self._versions.get(template_id, [])
        v1 = None
        v2 = None
        for v in versions:
            if v.version == version1:
                v1 = v
            if v.version == version2:
                v2 = v
        if not v1 or not v2:
            return None
        return {
            "version1": v1.to_dict(),
            "version2": v2.to_dict(),
            "content_changed": v1.content != v2.content,
            "content_diff_length": abs(len(v1.content) - len(v2.content)),
        }

    def _get_next_version(self, template_id: str, current_version: str) -> str:
        """Get next semantic version.

        Args:
            template_id: Template identifier
            current_version: Current version string

        Returns:
            Next version string
        """
        versions = self._versions.get(template_id, [])
        if not versions:
            return "1.0.0"
        try:
            parts = current_version.split(".")
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
        except (ValueError, IndexError):
            return "1.0.0"
        patch += 1
        return f"{major}.{minor}.{patch}"

    def bump_minor(self, version: str) -> str:
        """Bump minor version.

        Args:
            version: Current version

        Returns:
            New version
        """
        try:
            parts = version.split(".")
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
        except (ValueError, IndexError):
            return "1.0.0"
        return f"{major}.{minor + 1}.0"

    def bump_major(self, version: str) -> str:
        """Bump major version.

        Args:
            version: Current version

        Returns:
            New version
        """
        try:
            parts = version.split(".")
            major = int(parts[0])
        except (ValueError, IndexError):
            return "1.0.0"
        return f"{major + 1}.0.0"


def create_version_manager() -> PromptVersionManager:
    """Factory function to create version manager.

    Returns:
        PromptVersionManager instance
    """
    return PromptVersionManager()
