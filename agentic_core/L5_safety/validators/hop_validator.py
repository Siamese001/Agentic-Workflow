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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_validated_by_safety_plane,
)

_emit_dispatches_healing_run("p1", "hop_validator", "L5")
_emit_routes_through("p1", "hop_validator", "L5")
_emit_escalates_to_human("p1", "hop_validator", "L5")
_emit_reads_policy_state("p1", "hop_validator", "L5")

_emit_applies_guardrail("p0", "hop_validator", "p0_governance")
_emit_snapshots_state("p0", "hop_validator", "state_snapshot")


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
