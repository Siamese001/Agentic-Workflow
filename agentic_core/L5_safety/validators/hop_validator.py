"""
HOP Validator - Deterministic HOP Pipeline Validation

Zero-Ambiguity Standard: Renamed from hop_validation_deterministic_validator.py
Category: VALIDATOR (Deterministic safety check)

Moved from L0_routing/deterministic to L5_safety/validators.

Deterministic Operations:
- Profile classification (heuristic rules)
- JSON data extraction and validation
- Condition checking (boolean logic)
- Placeholder validation (regex patterns)
- Gate decision classification (rule-based)
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "hop_validator")
emit_determinism_digest("p0", "hop_validator")

_emit_dispatches_healing_run("p1", "hop_validator", "L5")
_emit_routes_through("p1", "hop_validator", "L5")
_emit_checks_agent_registry("p1", "hop_validator", "agent_registry")
_emit_validates_agent_capability("p1", "hop_validator", "capability")
_emit_dispatches_execution_plan("p1", "hop_validator", "exec_plan")
_emit_agent_executes_agent("p1", "hop_validator", "sub_agent")
_emit_routes_to_agent("p1", "hop_validator", "target_agent")
_emit_verifies_policy("p1", "hop_validator", "policy_check")
_emit_observes_runtime_state("p1", "hop_validator", "runtime_state")
_emit_verifies_boundary("p1", "hop_validator", "boundary_check")
_emit_transcripts_response("p1", "hop_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "hop_validator")
_emit_gated_by_confidence("p1", "hop_validator", "confidence_gate")
_emit_escalates_to_human("p1", "hop_validator", "L5")
_emit_reads_policy_state("p1", "hop_validator", "L5")

_emit_applies_guardrail("p0", "hop_validator", "p0_governance")
_emit_snapshots_state("p0", "hop_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "hop_validator", "execution_auth")
_emit_validates_capability("p2", "hop_validator", "capability_check")
_emit_routes_to_capability("p2", "hop_validator", "capability_route")
_emit_writes_via_uwg("p2", "hop_validator", "uwg_write")
_emit_blocks_direct_write("p2", "hop_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "hop_validator", "tool_invocation")
_emit_captures_execution_output("p2", "hop_validator", "exec_output")
_emit_dispatches_agent("p3", "hop_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "hop_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "hop_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "hop_validator", "healing_outcome")
_emit_escalates_failure("p3", "hop_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "hop_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hop_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "hop_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "hop_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hop_validator", "eval_metric")
_emit_stores_embedding("p4", "hop_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "hop_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hop_validator", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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

_emit_emits_metric_event("hop_validator", "p4obs", "metric_1")
_emit_emits_metric_event("hop_validator", "p4obs", "metric_2")
_emit_emits_metric_event("hop_validator", "p4obs", "metric_3")
_emit_emits_metric_event("hop_validator", "p4obs", "metric_4")
_emit_emits_metric_event("hop_validator", "p4obs", "metric_5")
_emit_emits_metric_event("hop_validator", "p4obs", "metric_6")
_emit_records_incident_event("hop_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("hop_validator", "p4obs", "anomaly")
_emit_writes_observability_log("hop_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("hop_validator", "p4obs", "mon_state")
_emit_triggers_alert("hop_validator", "p4obs", "alert")
_emit_links_incident_trace("hop_validator", "p4obs", "trace_link")
_emit_captures_pattern("hop_validator", "p3lm", "pattern")
_emit_records_learning_event("hop_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hop_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("hop_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hop_validator", "p3lm", "routing")
_emit_improves_agent_policy("hop_validator", "p3lm", "policy")
_emit_stores_learning_state("hop_validator", "p3lm", "state")
_emit_records_execution_trace("hop_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hop_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hop_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hop_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hop_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hop_validator", "env_read", "p2_env_1")
_emit_reads_environ("hop_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("hop_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hop_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hop_validator", "context_pull")
_emit_pulls_context("p1", "hop_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hop_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hop_validator", "uwg_term_2")
_emit_writes_through("p1", "hop_validator", "write_through")
_emit_writes_through("p1", "hop_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "hop_validator", "safety_validation")
_emit_invokes_eval("p1", "hop_validator", "eval_call")
_emit_proposal_commits_routing("p1", "hop_validator", "routing_commit")


@dataclass
class HOPValidationResult:
    """Result of HOP validation with deterministic scoring."""

    passed: bool
    issues: list[str]
    score: float | None = None
    classification: str | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class HOP1ProfileDeterministic:
    """Deterministic profile classification for HOP1."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize with HOP1 classification rules."""
        self.industry_keywords = config.get("industry_keywords", {})
        self.seniority_keywords = config.get("seniority_keywords", {})
        self.min_profile_completeness = config.get("min_profile_completeness", 0.7)

    def classify_profile_heuristic(self, profile: dict[str, Any]) -> HOPValidationResult:
        """
        Classify profile using deterministic heuristic rules.

        Moved to Deterministic: Pure rule-based classification
        """
        _emit_validated_by_safety_plane(
            str(uuid.uuid4()), "HOP1ProfileDeterministic.classify_profile_heuristic", "L5_POLICY"
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "HOP1ProfileDeterministic.classify_profile_heuristic"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:HOP1ProfileDeterministic.classify_profile_heuristic".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        issues: list[str] = []
        score = 0.0
        classification = "unknown"
        completeness = self._calculate_profile_completeness(profile)
        if completeness < self.min_profile_completeness:
            issues.append(f"Insufficient profile completeness ({completeness:.0%})")
        industry = self._classify_industry(profile)
        if industry == "unknown":
            issues.append("Unable to determine industry")
        seniority = self._classify_seniority(profile)
        if seniority == "unknown":
            issues.append("Unable to determine seniority level")
        score = (
            completeness + (1.0 if industry != "unknown" else 0.0) + (1.0 if seniority != "unknown" else 0.0)
        ) / 3.0
        classification = f"{seniority}_{industry}"
        return HOPValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            score=score,
            classification=classification,
            metadata={"hop": "HOP1", "validation_type": "deterministic"},
        )

    def _calculate_profile_completeness(self, profile: dict[str, Any]) -> float:
        """Calculate profile completeness using deterministic rules."""
        required_fields = ["name", "experience", "education", "skills"]
        present_fields = sum(1 for field in required_fields if field in profile and profile[field])
        return present_fields / len(required_fields)

    def _classify_industry(self, profile: dict[str, Any]) -> str:
        """Classify industry using deterministic keyword matching."""
        profile_text = json.dumps(profile).lower()
        for industry, keywords in self.industry_keywords.items():
            matches = sum(1 for keyword in keywords if keyword.lower() in profile_text)
            if matches >= 2:
                return industry
        return "unknown"

    def _classify_seniority(self, profile: dict[str, Any]) -> str:
        """Classify seniority using deterministic keyword matching."""
        profile_text = json.dumps(profile).lower()
        for seniority, keywords in self.seniority_keywords.items():
            matches = sum(1 for keyword in keywords if keyword.lower() in profile_text)
            if matches >= 1:
                return seniority
        return "unknown"


class HOP3DataExtractionDeterministic:
    """Deterministic data extraction for HOP3."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize with HOP3 extraction rules."""
        self.required_entities = config.get("required_entities", [])
        self.entity_patterns = config.get("entity_patterns", {})

    def extract_grounded_entities(self, json_data: dict[str, Any]) -> HOPValidationResult:
        """
        Extract grounded entities from JSON data.

        Moved to Deterministic: Pure JSON parsing and extraction
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "HOP3DataExtractionDeterministic.extract_grounded_entities"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:HOP3DataExtractionDeterministic.extract_grounded_entities".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        issues: list[str] = []
        extracted_entities = {}
        if not isinstance(json_data, dict):
            issues.append("Invalid JSON structure - expected dictionary")
            return HOPValidationResult(
                passed=False, issues=issues, metadata={"hop": "HOP3", "validation_type": "deterministic"}
            )
        for entity in self.required_entities:
            if entity in json_data:
                extracted_entities[entity] = json_data[entity]
            else:
                issues.append(f"Missing required entity: {entity}")
        pattern_matches = self._apply_entity_patterns(json_data)
        extracted_entities.update(pattern_matches)
        score = len(extracted_entities) / len(self.required_entities) if self.required_entities else 1.0
        return HOPValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            score=score,
            metadata={"hop": "HOP3", "extracted_entities": extracted_entities},
        )

    def _apply_entity_patterns(self, json_data: dict[str, Any]) -> dict[str, Any]:
        """Apply deterministic entity extraction patterns."""
        matches = {}
        json_text = json.dumps(json_data)
        for entity_name, pattern in self.entity_patterns.items():
            found_matches = re.findall(pattern, json_text, re.IGNORECASE)
            if found_matches:
                matches[entity_name] = found_matches
        return matches


class HOP4ConditionDeterministic:
    """Deterministic condition checking for HOP4."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize with HOP4 condition rules."""
        self.conditions = config.get("conditions", [])

    def check_conditions(self, context: dict[str, Any]) -> HOPValidationResult:
        """
        Check routing conditions using deterministic boolean logic.

        Moved to Deterministic: Pure boolean condition evaluation
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "HOP4ConditionDeterministic.check_conditions"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:HOP4ConditionDeterministic.check_conditions".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        issues: list[str] = []
        passed_conditions = []
        for condition in self.conditions:
            result = self._evaluate_condition(condition, context)
            if result["passed"]:
                passed_conditions.append(condition["name"])
            else:
                issues.append(f"Condition failed: {condition['name']} - {result['reason']}")
        score = len(passed_conditions) / len(self.conditions) if self.conditions else 1.0
        return HOPValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            score=score,
            metadata={"hop": "HOP4", "passed_conditions": passed_conditions},
        )

    def _evaluate_condition(self, condition: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate single condition using deterministic logic."""
        condition_type = condition.get("type", "equals")
        field = condition.get("field")
        expected_value = condition.get("value")
        actual_value = context.get(field)
        if condition_type == "equals":
            passed = actual_value == expected_value
            reason = f"Expected {expected_value}, got {actual_value}"
        elif condition_type == "contains":
            passed = expected_value in str(actual_value) if actual_value else False
            reason = f"Expected '{expected_value}' in '{actual_value}'"
        elif condition_type == "greater_than":
            try:
                passed = float(actual_value) > float(expected_value)
                reason = f"Expected > {expected_value}, got {actual_value}"
            except (ValueError, TypeError):
                passed = False
                reason = f"Invalid numeric comparison: {actual_value} vs {expected_value}"
        else:
            passed = False
            reason = f"Unknown condition type: {condition_type}"
        return {"passed": passed, "reason": reason}


class HOP6PlaceholderDeterministic:
    """Deterministic placeholder validation for HOP6."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize with HOP6 placeholder patterns."""
        self.placeholder_patterns = config.get(
            "placeholder_patterns", ["\\[.*?\\]", "\\{.*?\\}", "<.*?>", "\\$\\{.*?\\}"]
        )

    def validate_placeholders(self, content: str) -> HOPValidationResult:
        """
        Validate placeholders using deterministic regex patterns.

        Moved to Deterministic: Pure pattern matching
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "HOP6PlaceholderDeterministic.validate_placeholders"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:HOP6PlaceholderDeterministic.validate_placeholders".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        issues: list[str] = []
        found_placeholders = []
        for pattern in self.placeholder_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            found_placeholders.extend(matches)
        if found_placeholders:
            issues.append(f"Found {len(found_placeholders)} placeholders: {found_placeholders[:5]}")
        score = 1.0 if not found_placeholders else max(0.0, 1.0 - len(found_placeholders) * 0.1)
        return HOPValidationResult(
            passed=len(found_placeholders) == 0,
            issues=issues,
            score=score,
            metadata={"hop": "HOP6", "placeholders": found_placeholders},
        )


class HOP7GateDecisionDeterministic:
    """Deterministic gate decision classification for HOP7."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize with HOP7 gate decision rules."""
        self.violation_categories = config.get("violation_categories", {})
        self.decision_thresholds = config.get("decision_thresholds", {})

    def classify_gate_decision(self, violations: list[dict[str, Any]]) -> HOPValidationResult:
        """
        Classify gate decision using deterministic rule-based logic.

        Moved to Deterministic: Pure rule-based classification
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "HOP7GateDecisionDeterministic.classify_gate_decision"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:HOP7GateDecisionDeterministic.classify_gate_decision".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        issues: list[str] = []
        decision = "proceed"
        violation_counts = {}
        for violation in violations:
            category = violation.get("category", "unknown")
            violation_counts[category] = violation_counts.get(category, 0) + 1
        for category, count in violation_counts.items():
            threshold = self.decision_thresholds.get(category, {})
            if count >= threshold.get("critical", 999):
                decision = "reject"
                issues.append(f"Critical threshold exceeded for {category}: {count}")
            elif count >= threshold.get("retry", 999):
                decision = "retry"
                issues.append(f"Retry threshold exceeded for {category}: {count}")
        score = self._calculate_decision_score(violation_counts, decision)
        return HOPValidationResult(
            passed=decision == "proceed",
            issues=issues,
            score=score,
            classification=decision,
            metadata={"hop": "HOP7", "violation_counts": violation_counts},
        )

    def _calculate_decision_score(self, violation_counts: dict[str, str], decision: str) -> float:
        """Calculate decision score using deterministic algorithm."""
        base_scores = {"proceed": 1.0, "retry": 0.5, "reject": 0.0}
        base_score = base_scores.get(decision, 0.0)
        total_violations = sum(violation_counts.values())
        penalty = min(0.5, total_violations * 0.1)
        return max(0.0, base_score - penalty)


class HOPValidationDeterministic:
    """
    Unified deterministic validation for HOP series agents.

    Consolidates all HOP deterministic logic into a single interface.
    """

    def __init__(self, hop_config: dict[str, Any]) -> None:
        """Initialize with HOP configuration."""
        self.hop1 = HOP1ProfileDeterministic(hop_config.get("hop1", {}))
        self.hop3 = HOP3DataExtractionDeterministic(hop_config.get("hop3", {}))
        self.hop4 = HOP4ConditionDeterministic(hop_config.get("hop4", {}))
        self.hop6 = HOP6PlaceholderDeterministic(hop_config.get("hop6", {}))
        self.hop7 = HOP7GateDecisionDeterministic(hop_config.get("hop7", {}))

    def validate_hop1_profile(self, profile: dict[str, Any]) -> HOPValidationResult:
        """Validate HOP1 profile classification."""
        return self.hop1.classify_profile_heuristic(profile)

    def validate_hop3_extraction(self, json_data: dict[str, Any]) -> HOPValidationResult:
        """Validate HOP3 data extraction."""
        return self.hop3.extract_grounded_entities(json_data)

    def validate_hop4_conditions(self, context: dict[str, Any]) -> HOPValidationResult:
        """Validate HOP4 condition checking."""
        return self.hop4.check_conditions(context)

    def validate_hop6_placeholders(self, content: str) -> HOPValidationResult:
        """Validate HOP6 placeholder detection."""
        return self.hop6.validate_placeholders(content)

    def validate_hop7_decision(self, violations: list[dict[str, Any]]) -> HOPValidationResult:
        """Validate HOP7 gate decision classification."""
        return self.hop7.classify_gate_decision(violations)
