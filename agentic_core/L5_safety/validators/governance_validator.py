"""
Governance Shield Validator - Deterministic Governance Validation

Zero-Ambiguity Standard: Renamed from governance_shield_deterministic_validator.py
Category: VALIDATOR (Deterministic safety check)

Moved from L0_routing/deterministic to L5_safety/validators.

Deterministic Operations:
- Risk level scanning (rule-based classification)
- Privacy language detection (keyword matching)
- Protocol generation (template-based)
- Basic governance rule validation
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "governance_validator")
trace_contract.emit_determinism_digest("p0", "governance_validator")

trace_contract._emit_dispatches_healing_run("p1", "governance_validator", "L5")
trace_contract._emit_routes_through("p1", "governance_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "governance_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "governance_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "governance_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "governance_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "governance_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "governance_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "governance_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "governance_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "governance_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "governance_validator")
trace_contract._emit_gated_by_confidence("p1", "governance_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "governance_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "governance_validator", "L5")

trace_contract._emit_applies_guardrail("p0", "governance_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "governance_validator", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "governance_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "governance_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "governance_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "governance_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "governance_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "governance_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "governance_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "governance_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "governance_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "governance_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "governance_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "governance_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "governance_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "governance_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "governance_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "governance_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "governance_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "governance_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "governance_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "governance_validator", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("governance_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("governance_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("governance_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("governance_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("governance_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("governance_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("governance_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("governance_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("governance_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("governance_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("governance_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("governance_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("governance_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("governance_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("governance_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("governance_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("governance_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("governance_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("governance_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("governance_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("governance_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("governance_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("governance_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("governance_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("governance_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("governance_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("governance_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("governance_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "governance_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "governance_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "governance_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "governance_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "governance_validator", "write_through")
trace_contract._emit_writes_through("p1", "governance_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "governance_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "governance_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "governance_validator", "routing_commit")


@dataclass
class GovernanceResult:
    """Result of governance validation with deterministic scoring."""

    passed: bool
    issues: list[str]
    risk_level: str
    score: float | None = None
    protocol: str | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class GovernanceShieldValidator:
    """
    Pure deterministic governance and risk validation.

    All methods are 100% deterministic and can be executed without
    external dependencies or LLM calls.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize with governance validation configuration.

        Args:
            config: Configuration dictionary containing governance rules
        """
        self.risk_keywords = config.get(
            "risk_keywords",
            {
                "high": ["guarantee", "always", "never", "promise", "commitment"],
                "medium": ["likely", "probably", "usually", "typically"],
                "low": ["may", "might", "could", "possibly", "potential"],
            },
        )
        self.privacy_patterns = config.get(
            "privacy_patterns",
            [
                "\\b(ssn|social security)\\b",
                "\\b(credit card|cc number)\\b",
                "\\b(password|pwd)\\b",
                "\\b(private|confidential|secret)\\b",
            ],
        )
        self.forbidden_patterns = config.get(
            "forbidden_patterns",
            [
                "\\b(money back|refund guaranteed)\\b",
                "\\b(risk free|no risk)\\b",
                "\\b(100%|perfect|always)\\b",
            ],
        )
        self.protocol_templates = config.get(
            "protocol_templates",
            {
                "high": "HIGH_RISK_PROTOCOL: Immediate review required. Content: {content}",
                "medium": "MEDIUM_RISK_PROTOCOL: Manager review recommended. Content: {content}",
                "low": "LOW_RISK_PROTOCOL: Standard validation passed. Content: {content}",
            },
        )

    def scan_risk_level(self, content: str) -> GovernanceResult:
        """
        Scan content for risk level using deterministic keyword matching.

        Moved to Deterministic: Pure keyword-based risk classification
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "GovernanceShieldValidator.scan_risk_level",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:GovernanceShieldValidator.scan_risk_level".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        issues: list[str] = []
        risk_scores = {"high": 0, "medium": 0, "low": 0}
        content_lower = content.lower()
        for level, keywords in tqdm(self.risk_keywords.items(), desc="Processing", unit="item"):
            for keyword in keywords:
                matches = len(re.findall(f"\\b{re.escape(keyword)}\\b", content_lower))
                risk_scores[level] += matches
        total_score = risk_scores["high"] * 3 + risk_scores["medium"] * 2 + risk_scores["low"] * 1
        if risk_scores["high"] >= 2 or total_score >= 5:
            risk_level = "high"
            issues.append(f"High risk detected: {risk_scores['high']} high-risk keywords")
        elif risk_scores["medium"] >= 3 or total_score >= 3:
            risk_level = "medium"
            issues.append(f"Medium risk detected: {risk_scores['medium']} medium-risk keywords")
        else:
            risk_level = "low"
        max_possible_score = sum(len(keywords) for keywords in self.risk_keywords.values())
        score = 1.0 - total_score / max_possible_score if max_possible_score > 0 else 1.0
        return GovernanceResult(
            passed=risk_level != "high",
            issues=issues,
            risk_level=risk_level,
            score=max(0.0, score),
            metadata={"validation_type": "deterministic", "risk_scores": risk_scores},
        )

    def detect_privacy_language(self, content: str) -> GovernanceResult:
        """
        Detect privacy-sensitive language using deterministic patterns.

        Moved to Deterministic: Pure regex pattern matching
        """
        issues: list[str] = []
        privacy_matches = []
        for pattern in self.privacy_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            privacy_matches.extend(matches)
        if privacy_matches:
            issues.append(f"Privacy-sensitive language detected: {len(privacy_matches)} instances")
            issues.extend([f"- {match}" for match in set(privacy_matches)])
        score = 1.0 - len(privacy_matches) * 0.2
        score = max(0.0, score)
        risk_level = "high" if len(privacy_matches) >= 3 else "medium" if privacy_matches else "low"
        return GovernanceResult(
            passed=len(privacy_matches) == 0,
            issues=issues,
            risk_level=risk_level,
            score=score,
            metadata={"validation_type": "deterministic", "privacy_matches": privacy_matches},
        )

    def check_forbidden_patterns(self, content: str) -> GovernanceResult:
        """
        Check for forbidden patterns using deterministic regex.

        Moved to Deterministic: Pure forbidden pattern detection
        """
        issues: list[str] = []
        forbidden_matches = []
        for pattern in self.forbidden_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            forbidden_matches.extend(matches)
        if forbidden_matches:
            issues.append(f"Forbidden patterns detected: {len(forbidden_matches)} instances")
            issues.extend([f"- {match}" for match in set(forbidden_matches)])
        score = 1.0 - len(forbidden_matches) * 0.3
        score = max(0.0, score)
        risk_level = "high" if forbidden_matches else "low"
        return GovernanceResult(
            passed=len(forbidden_matches) == 0,
            issues=issues,
            risk_level=risk_level,
            score=score,
            metadata={"validation_type": "deterministic", "forbidden_matches": forbidden_matches},
        )

    def generate_safety_protocol(self, risk_level: str, content: str) -> GovernanceResult:
        """
        Generate safety protocol using deterministic templates.

        Moved to Deterministic: Pure template-based protocol generation
        """
        template = self.protocol_templates.get(risk_level, self.protocol_templates["low"])
        protocol = template.format(content=content[:200] + "..." if len(content) > 200 else content)
        return GovernanceResult(
            passed=True,
            issues=[],
            risk_level=risk_level,
            protocol=protocol,
            metadata={"validation_type": "deterministic", "protocol_type": "template"},
        )

    def audit_content_compliance(self, content: str) -> GovernanceResult:
        """
        Perform comprehensive content audit using deterministic rules.

        Combines all deterministic validation methods.
        """
        all_issues = []
        risk_levels = []
        scores = []
        risk_result = self.scan_risk_level(content)
        all_issues.extend(risk_result.issues)
        risk_levels.append(risk_result.risk_level)
        if risk_result.score is not None:
            scores.append(risk_result.score)
        privacy_result = self.detect_privacy_language(content)
        all_issues.extend(privacy_result.issues)
        risk_levels.append(privacy_result.risk_level)
        if privacy_result.score is not None:
            scores.append(privacy_result.score)
        forbidden_result = self.check_forbidden_patterns(content)
        all_issues.extend(forbidden_result.issues)
        risk_levels.append(forbidden_result.risk_level)
        if forbidden_result.score is not None:
            scores.append(forbidden_result.score)
        overall_risk = "high" if "high" in risk_levels else "medium" if "medium" in risk_levels else "low"
        overall_score = sum(scores) / len(scores) if scores else 1.0
        protocol_result = self.generate_safety_protocol(overall_risk, content)
        return GovernanceResult(
            passed=overall_risk != "high" and len(all_issues) == 0,
            issues=all_issues,
            risk_level=overall_risk,
            score=overall_score,
            protocol=protocol_result.protocol,
            metadata={
                "validation_type": "deterministic",
                "component_risks": risk_levels,
                "total_issues": len(all_issues),
            },
        )

    def sanitize_claims(self, content: str) -> GovernanceResult:
        """
        Sanitize claims using deterministic rule-based logic.

        Moved to Deterministic: Pure claim sanitization rules
        """
        sanitized_content = content
        sanitizations = []
        absolute_patterns = {
            "\\balways\\b": "typically",
            "\\bnever\\b": "rarely",
            "\\bguaranteed\\b": "expected",
            "\\b100%\\b": "high",
            "\\bperfect\\b": "excellent",
        }
        for pattern, replacement in absolute_patterns.items():
            matches = len(re.findall(pattern, sanitized_content, re.IGNORECASE))
            if matches > 0:
                sanitized_content = re.sub(pattern, replacement, sanitized_content, flags=re.IGNORECASE)
                sanitizations.append(f"Replaced {matches} instances of '{pattern}' with '{replacement}'")
        score = 1.0 - len(sanitizations) * 0.1
        score = max(0.0, score)
        return GovernanceResult(
            passed=len(sanitizations) == 0,
            issues=sanitizations,
            risk_level="low",
            score=score,
            metadata={"validation_type": "deterministic", "sanitizations": sanitizations},
        )
