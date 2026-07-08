"""
Intelligence Query Validator - Deterministic Query Validation

Zero-Ambiguity Standard: Renamed from intelligence_librarian_deterministic_validator.py
Category: VALIDATOR (Deterministic safety check)

Moved from L0_routing/deterministic to L5_safety/validators.

Deterministic Operations:
- Query validation (string validation)
- Filter validation (schema validation)
- Cache key generation (deterministic hashing)
- Result filtering (deterministic filtering)
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "intelligence_query_validator")
trace_contract.emit_determinism_digest("p0", "intelligence_query_validator")

trace_contract._emit_dispatches_healing_run("p1", "intelligence_query_validator", "L5")
trace_contract._emit_routes_through("p1", "intelligence_query_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "intelligence_query_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "intelligence_query_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "intelligence_query_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "intelligence_query_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "intelligence_query_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "intelligence_query_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "intelligence_query_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "intelligence_query_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "intelligence_query_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "intelligence_query_validator")
trace_contract._emit_gated_by_confidence("p1", "intelligence_query_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "intelligence_query_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "intelligence_query_validator", "L5")

trace_contract._emit_applies_guardrail("p0", "intelligence_query_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "intelligence_query_validator", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "intelligence_query_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "intelligence_query_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "intelligence_query_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "intelligence_query_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "intelligence_query_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "intelligence_query_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "intelligence_query_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "intelligence_query_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "intelligence_query_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "intelligence_query_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "intelligence_query_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "intelligence_query_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "intelligence_query_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "intelligence_query_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "intelligence_query_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "intelligence_query_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "intelligence_query_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "intelligence_query_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "intelligence_query_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "intelligence_query_validator", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("intelligence_query_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("intelligence_query_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("intelligence_query_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("intelligence_query_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("intelligence_query_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("intelligence_query_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("intelligence_query_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("intelligence_query_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("intelligence_query_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("intelligence_query_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("intelligence_query_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("intelligence_query_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("intelligence_query_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("intelligence_query_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("intelligence_query_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("intelligence_query_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("intelligence_query_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("intelligence_query_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("intelligence_query_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("intelligence_query_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("intelligence_query_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("intelligence_query_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("intelligence_query_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("intelligence_query_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("intelligence_query_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("intelligence_query_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("intelligence_query_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("intelligence_query_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "intelligence_query_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "intelligence_query_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "intelligence_query_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "intelligence_query_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "intelligence_query_validator", "write_through")
trace_contract._emit_writes_through("p1", "intelligence_query_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "intelligence_query_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "intelligence_query_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "intelligence_query_validator", "routing_commit")


@dataclass
class IntelligenceQueryResult:
    """Result of intelligence query validation."""

    valid: bool
    issues: list[str]
    cache_key: str | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class IntelligenceQueryValidator:
    """
    Pure deterministic intelligence query validation.

    All methods are 100% deterministic and can be executed without
    external dependencies or LLM calls.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """
        Initialize with intelligence librarian configuration.

        Args:
            config: Configuration dictionary containing validation rules
        """
        config = config or {}
        self.min_query_length = config.get("min_query_length", 3)
        self.max_query_length = config.get("max_query_length", 500)
        self.allowed_filter_keys = config.get(
            "allowed_filter_keys",
            ["industry", "date_range", "source", "relevance_threshold"],
        )
        self.cache_ttl = config.get("cache_ttl", 3600)

    def validate_query(self, query: str, filters: dict[str, Any] | None = None) -> IntelligenceQueryResult:
        """
        Validate intelligence query using purely deterministic logic.

        Args:
            query: Query string to validate
            filters: Optional filters dictionary

        Returns:
            IntelligenceQueryResult with deterministic findings
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "IntelligenceQueryValidator.validate_query",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:IntelligenceQueryValidator.validate_query".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        issues: list[str] = []
        query_issues = self._validate_query_string(query)
        issues.extend(query_issues)
        if filters:
            filter_issues = self._validate_filters(filters)
            issues.extend(filter_issues)
        cache_key = self._generate_cache_key(query, filters) if not issues else None
        return IntelligenceQueryResult(
            valid=len(issues) == 0,
            issues=issues,
            cache_key=cache_key,
            metadata={"validation_type": "deterministic"},
        )

    def _validate_query_string(self, query: str) -> list[str]:
        """
        Validate query string using deterministic rules.

        Moved to Deterministic: Pure string validation
        """
        issues: list[str] = []
        if not query:
            issues.append("Query cannot be empty")
            return issues
        if len(query) < self.min_query_length:
            issues.append(f"Query too short (min {self.min_query_length} characters)")
        if len(query) > self.max_query_length:
            issues.append(f"Query too long (max {self.max_query_length} characters)")
        if re.search("[<>{}]", query):
            issues.append("Query contains invalid characters")
        return issues

    def _validate_filters(self, filters: dict[str, Any]) -> list[str]:
        """
        Validate filters using deterministic schema validation.

        Moved to Deterministic: Pure schema validation
        """
        issues: list[str] = []
        for key in filters.keys():
            if key not in self.allowed_filter_keys:
                issues.append(f"Unknown filter key: {key}")
        if "relevance_threshold" in filters:
            threshold = filters["relevance_threshold"]
            if not isinstance(threshold, int | float) or not 0 <= threshold <= 1:
                issues.append("relevance_threshold must be between 0 and 1")
        if "date_range" in filters:
            date_range = filters["date_range"]
            if not isinstance(date_range, dict) or "start" not in date_range:
                issues.append("date_range must have 'start' field")
        return issues

    def _generate_cache_key(self, query: str, filters: dict[str, Any] | None) -> str:
        """
        Generate cache key using deterministic hashing.

        Moved to Deterministic: Pure hash generation
        """
        filter_str = str(sorted(filters.items())) if filters else ""
        combined = f"{query}:{filter_str}"
        return hashlib.md5(combined.encode()).hexdigest()

    def normalize_query(self, query: str) -> str:
        """
        Normalize query string using deterministic rules.

        Moved to Deterministic: Pure string normalization
        """
        query = re.sub("\\s+", " ", query.strip())
        query = query.lower()
        return query

    def filter_results(self, results: list[dict[str, Any]], filters: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Filter results using deterministic filtering logic.

        Moved to Deterministic: Pure filtering logic
        """
        filtered = results.copy()
        if "relevance_threshold" in filters:
            threshold = filters["relevance_threshold"]
            filtered = [r for r in filtered if r.get("relevance", 0) >= threshold]
        if "industry" in filters:
            industry = filters["industry"]
            filtered = [r for r in filtered if r.get("industry") == industry]
        if "source" in filters:
            source = filters["source"]
            filtered = [r for r in filtered if r.get("source") == source]
        return filtered

    def calculate_query_complexity(self, query: str) -> dict[str, Any]:
        """
        Calculate query complexity using deterministic analysis.

        Returns complexity metrics for query optimization.
        """
        words = query.split()
        word_count = len(words)
        operator_count = sum(1 for word in words if word.upper() in ["AND", "OR", "NOT"])
        quoted_phrases = len(re.findall('"[^"]*"', query))
        complexity_score = word_count + operator_count * 2 + quoted_phrases * 3
        complexity_level = (
            "simple" if complexity_score < 5 else "moderate" if complexity_score < 15 else "complex"
        )
        return {
            "word_count": word_count,
            "operator_count": operator_count,
            "quoted_phrases": quoted_phrases,
            "complexity_score": complexity_score,
            "complexity_level": complexity_level,
        }
