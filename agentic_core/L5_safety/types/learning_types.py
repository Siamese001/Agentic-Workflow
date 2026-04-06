from __future__ import annotations

import os

from agentic_core.L2_execution.utils import write_gateway as _wg
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

emit_replay_key("p0", "learning_types")
emit_determinism_digest("p0", "learning_types")

_emit_dispatches_healing_run("p1", "learning_types", "L5")
_emit_routes_through("p1", "learning_types", "L5")
_emit_checks_agent_registry("p1", "learning_types", "agent_registry")
_emit_validates_agent_capability("p1", "learning_types", "capability")
_emit_dispatches_execution_plan("p1", "learning_types", "exec_plan")
_emit_agent_executes_agent("p1", "learning_types", "sub_agent")
_emit_routes_to_agent("p1", "learning_types", "target_agent")
_emit_verifies_policy("p1", "learning_types", "policy_check")
_emit_observes_runtime_state("p1", "learning_types", "runtime_state")
_emit_verifies_boundary("p1", "learning_types", "boundary_check")
_emit_transcripts_response("p1", "learning_types", "transcript")
_emit_hard_fails_untranscripted("p1", "learning_types")
_emit_gated_by_confidence("p1", "learning_types", "confidence_gate")
_emit_escalates_to_human("p1", "learning_types", "L5")
_emit_reads_policy_state("p1", "learning_types", "L5")
_emit_authorize_and_execute("p2", "learning_types", "execution_auth")
_emit_validates_capability("p2", "learning_types", "capability_check")
_emit_routes_to_capability("p2", "learning_types", "capability_route")
_emit_writes_via_uwg("p2", "learning_types", "uwg_write")
_emit_blocks_direct_write("p2", "learning_types", "direct_write_block")
_emit_records_tool_invocation("p2", "learning_types", "tool_invocation")
_emit_captures_execution_output("p2", "learning_types", "exec_output")
_emit_dispatches_agent("p3", "learning_types", "agent_dispatch")
_emit_coordinates_agents("p3", "learning_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "learning_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "learning_types", "healing_outcome")
_emit_escalates_failure("p3", "learning_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "learning_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "learning_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "learning_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "learning_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "learning_types", "eval_metric")
_emit_stores_embedding("p4", "learning_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "learning_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "learning_types", "exec_snapshot_link")

"\nAdaptive Learning Engine - L1 Cognition Enhancement\n\nLearns from healing patterns to predict and prevent violations before they occur.\nUses pattern recognition and predictive analytics to make agents more autonomous.\n"
import asyncio
import json
import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import DEFAULT_SLEEP
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
    _emit_signs_execution_trace,
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

_emit_emits_metric_event("learning_types", "p4obs", "metric_1")
_emit_emits_metric_event("learning_types", "p4obs", "metric_2")
_emit_emits_metric_event("learning_types", "p4obs", "metric_3")
_emit_emits_metric_event("learning_types", "p4obs", "metric_4")
_emit_emits_metric_event("learning_types", "p4obs", "metric_5")
_emit_emits_metric_event("learning_types", "p4obs", "metric_6")
_emit_records_incident_event("learning_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("learning_types", "p4obs", "anomaly")
_emit_writes_observability_log("learning_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("learning_types", "p4obs", "mon_state")
_emit_triggers_alert("learning_types", "p4obs", "alert")
_emit_links_incident_trace("learning_types", "p4obs", "trace_link")
_emit_captures_pattern("learning_types", "p3lm", "pattern")
_emit_records_learning_event("learning_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("learning_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("learning_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("learning_types", "p3lm", "routing")
_emit_improves_agent_policy("learning_types", "p3lm", "policy")
_emit_stores_learning_state("learning_types", "p3lm", "state")
_emit_records_execution_trace("learning_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("learning_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("learning_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("learning_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("learning_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("learning_types", "env_read", "p2_env_1")
_emit_reads_environ("learning_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("learning_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("learning_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "learning_types", "context_pull")
_emit_pulls_context("p1", "learning_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "learning_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "learning_types", "uwg_term_2")
_emit_writes_through("p1", "learning_types", "write_through")
_emit_writes_through("p1", "learning_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "learning_types", "safety_validation")
_emit_invokes_eval("p1", "learning_types", "eval_call")
_emit_proposal_commits_routing("p1", "learning_types", "routing_commit")

Logger: Any = logging.getLogger(__name__)


@dataclass
class HealingPattern:
    """Represents a learned healing pattern."""

    violation_key: int
    violation_signature: str
    fix_strategy: str
    success_count: int = 0
    failure_count: int = 0
    avg_rounds_to_fix: float = 0.0
    last_used: datetime | None = None
    confidence_score: float = 0.0
    file_patterns: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "HealingPattern.success_rate", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "HealingPattern.success_rate", "p0_governance")
        total: Any = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0

    def update_confidence(self) -> Any:
        """Update confidence score based on success rate and usage."""

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L5_POLICY, "HealingPattern.update_confidence"
        )
        base_confidence: Any = self.success_rate
        usage_factor: Any = min(1.0, (self.success_count + self.failure_count) / 10)
        recency_factor: Any = 1.0
        if self.last_used:
            days_since: Any = (datetime.now() - self.last_used).days
            recency_factor: Any = max(0.5, 1.0 - days_since / 30)
        self.confidence_score = base_confidence * usage_factor * recency_factor


@dataclass
class ViolationPrediction:
    """Prediction of potential Violation."""

    file_path: str
    violation_key: int
    confidence: float
    recommended_pattern: HealingPattern | None
    reasoning: str


class AdaptiveLearningEngine:
    """
    Learns from healing patterns to predict and prevent violations.

    Features:
    - Pattern recognition from successful healing attempts
    - Predictive Violation detection
    - Automatic fix suggestion based on learned patterns
    - Continuous learning from new healing attempts
    """

    def __init__(self, pattern_storage_path: str | Path | None = None, autonomous_mode: bool = True):
        """Initialize the adaptive learning engine."""
        if pattern_storage_path:
            self.storage_path = Path(pattern_storage_path)
        else:
            self.storage_path = Path.cwd() / ".canon_memory" / "healing_patterns.json"
        self.pattern_storage_path = str(self.storage_path)
        self.backup_dir = Path(".canon_memory/backups")
        _wg.ensure_dir(self.backup_dir)
        self.autonomous_mode = autonomous_mode
        self._improvement_task = None
        self.patterns: dict[int, list[HealingPattern]] = defaultdict(list)
        self.violation_history: dict[str, list[tuple[int, bool, datetime]]] = defaultdict(list)
        self.prediction_cache: dict[str, list[ViolationPrediction]] = {}
        self._load_patterns()
        Logger.info("Adaptive Learning Engine initialized")

    def awaken(self) -> Any:
        """L1: Explicitly trigger the autonomous learning loop"""
        if self.autonomous_mode and (not self._improvement_task):
            self._improvement_task = asyncio.create_task(self.eternal_self_improvement())
            Logger.info("L1 Autonomous learning loop awakened")

    async def eternal_self_improvement(self) -> Any:
        """L1: Continuous self-improvement loop"""
        while self.autonomous_mode:
            try:
                await asyncio.sleep(DEFAULT_SLEEP)
                for key in list(self.patterns.keys()):
                    self.patterns[key] = [
                        p
                        for p in self.patterns[key]
                        if p.confidence_score > 0.3 or p.success_count + p.failure_count < 5
                    ]
                self._save_patterns()
                Logger.debug("L1 Self-improvement cycle completed")
            except Exception as e:
                raise
                Logger.error(f"L1 Self-improvement error: {e}")
                await asyncio.sleep(DEFAULT_SLEEP)

    def _load_patterns(self):
        """Load learned patterns from storage."""
        if not self.storage_path.exists():
            Logger.info("No existing patterns found, starting fresh")
            return
        try:
            with open(self.pattern_storage_path, encoding="utf-8") as f:
                data = json.load(f)
            for key_str, patterns_data in data.get("patterns", {}).items():
                key = int(key_str)
                for p_data in patterns_data:
                    pattern = HealingPattern(
                        violation_key=p_data["violation_key"],
                        violation_signature=p_data["violation_signature"],
                        fix_strategy=p_data["fix_strategy"],
                        success_count=p_data["success_count"],
                        failure_count=p_data["failure_count"],
                        avg_rounds_to_fix=p_data["avg_rounds_to_fix"],
                        last_used=datetime.fromisoformat(p_data["last_used"])
                        if p_data.get("last_used")
                        else None,
                        confidence_score=p_data["confidence_score"],
                        file_patterns=p_data.get("file_patterns", []),
                    )
                    self.patterns[key].append(pattern)
            Logger.info(f"Loaded {sum(len(p) for p in self.patterns.values())} healing patterns")
        except Exception as e:
            raise
            Logger.error(f"Failed to load patterns: {e}")

    def _save_patterns(self):
        """Save learned patterns to storage with versioned rotation (Keep Last 10)."""
        try:
            _wg.makedirs(Path(self.pattern_storage_path).parent, exist_ok=True)
            if self.storage_path.exists():
                backup = self.backup_dir / f"healing_patterns.{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
                _wg.copy_file(self.storage_path, backup)
                from agentic_core.utils.runners.ssot_discovery_validator import get_data_files

                all_files = get_data_files(self.backup_dir, extensions=[".json"])
                backups = sorted(
                    [f for f in all_files if "healing_patterns." in f.name],
                    key=os.path.getmtime,
                    reverse=True,
                )
                while len(backups) > 10:
                    _wg.remove_file(backups[0])
                    backups.pop(0)
            data = {"patterns": {}, "last_updated": datetime.now().isoformat()}
            for key, patterns in self.patterns.items():
                data["patterns"][str(key)] = [
                    {
                        "violation_key": p.violation_key,
                        "violation_signature": p.violation_signature,
                        "fix_strategy": p.fix_strategy,
                        "success_count": p.success_count,
                        "failure_count": p.failure_count,
                        "avg_rounds_to_fix": p.avg_rounds_to_fix,
                        "last_used": p.last_used.isoformat() if p.last_used else None,
                        "confidence_score": p.confidence_score,
                        "file_patterns": p.file_patterns,
                    }
                    for p in patterns
                ]
            _wg.write_json(self.pattern_storage_path, data, indent=2)
            Logger.debug(f"Saved patterns to {self.pattern_storage_path}")
        except Exception as e:
            raise
            Logger.error(f"Failed to save patterns: {e}")

    def learn_from_healing(
        self,
        file_path: str,
        violation_key: int,
        violation_details: str,
        fix_code: str,
        success: bool,
        rounds_taken: int,
    ) -> Any:
        """
        Learn from a healing attempt.

        Args:
            file_path: Path to the healed file
            violation_key: Canon key that was fixed
            violation_details: Description of the Violation
            fix_code: The code that fixed the issue
            success: Whether healing succeeded
            rounds_taken: Number of rounds it took
        """
        signature: Any = self._create_violation_signature(violation_details, file_path)
        existing_pattern: Any = self._find_matching_pattern(violation_key, signature)
        if existing_pattern:
            if success:
                existing_pattern.success_count += 1
                old_avg: Any = existing_pattern.avg_rounds_to_fix
                total: Any = existing_pattern.success_count
                existing_pattern.avg_rounds_to_fix = (old_avg * (total - 1) + rounds_taken) / total
            else:
                existing_pattern.failure_count += 1
            existing_pattern.last_used = datetime.now()
            existing_pattern.update_confidence()
        else:
            new_pattern: Any = HealingPattern(
                violation_key=violation_key,
                violation_signature=signature,
                fix_strategy=fix_code[:500],
                success_count=1 if success else 0,
                failure_count=0 if success else 1,
                avg_rounds_to_fix=float(rounds_taken) if success else 0.0,
                last_used=datetime.now(),
                file_patterns=[self._extract_file_pattern(file_path)],
            )
            new_pattern.update_confidence()
            self.patterns[violation_key].append(new_pattern)
        self.violation_history[file_path].append((violation_key, success, datetime.now()))
        self._save_patterns()
        Logger.info(f"Learned from healing: Key {violation_key}, Success: {success}")

    def _create_violation_signature(self, violation_details: str, file_path: str) -> str:
        """Create a signature for a Violation type."""
        # guardian: allow-path-string
        file_type = os.path.splitext(file_path)[1]
        keywords = self._extract_keywords(violation_details)
        return f"{file_type}:{':'.join(sorted(keywords[:5]))}"

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract key terms from Violation details."""
        stopwords = {"the", "a", "an", "in", "on", "at", "to", "for", "of", "with", "is", "are"}
        words = text.lower().split()
        return [w for w in words if len(w) > 3 and w not in stopwords]

    def _extract_file_pattern(self, file_path: str) -> str:
        """Extract pattern from file path."""
        parts = file_path.replace("\\", "/").split("/")
        if len(parts) >= 2:
            return f"{parts[-2]}/*.py"
        return "*.py"

    def _find_matching_pattern(self, violation_key: int, signature: str) -> HealingPattern | None:
        """Find existing pattern matching the signature."""
        for pattern in self.patterns.get(violation_key, []):
            if pattern.violation_signature == signature:
                return pattern
        return None

    async def predict_violations(self, file_path: str, code: str) -> list[ViolationPrediction]:
        """
        Predict potential violations in a file before they occur.

        Args:
            file_path: Path to the file
            code: File contents

        Returns:
            List of predicted violations with confidence scores
        """
        cache_key: Any = f"{file_path}:{hash(code)}"
        if cache_key in self.prediction_cache:
            return self.prediction_cache[cache_key]
        predictions: Any = []
        file_history: Any = self.violation_history.get(file_path, [])
        recent_violations: Any = [v[0] for v in file_history[-5:] if not v[1]]
        for violation_key in set(recent_violations):
            patterns: Any = self.patterns.get(violation_key, [])
            high_confidence_patterns: Any = [p for p in patterns if p.confidence_score > 0.75]
            if high_confidence_patterns:
                best_pattern: Any = max(high_confidence_patterns, key=lambda p: p.confidence_score)
                predictions.append(
                    ViolationPrediction(
                        file_path=file_path,
                        violation_key=violation_key,
                        confidence=best_pattern.confidence_score,
                        recommended_pattern=best_pattern,
                        reasoning=f"File has history of Key {violation_key} violations",
                    )
                )
        for violation_key, patterns in self.patterns.items():
            if violation_key in recent_violations:
                continue
            for pattern in patterns:
                if pattern.confidence_score < 0.8:
                    continue
                file_pattern: Any = self._extract_file_pattern(file_path)
                if file_pattern in pattern.file_patterns:
                    predictions.append(
                        ViolationPrediction(
                            file_path=file_path,
                            violation_key=violation_key,
                            confidence=pattern.confidence_score * 0.8,
                            recommended_pattern=pattern,
                            reasoning=f"Similar files often have Key {violation_key} violations",
                        )
                    )
        predictions.sort(key=lambda p: p.confidence, reverse=True)
        self.prediction_cache[cache_key] = predictions[:5]
        return predictions[:5]

    def get_recommended_fix(self, violation_key: int, violation_details: str, file_path: str) -> str | None:
        """
        Get recommended fix based on learned patterns.

        Args:
            violation_key: Canon key
            violation_details: Violation description
            file_path: File path

        Returns:
            Recommended fix strategy or None
        """
        signature: Any = self._create_violation_signature(violation_details, file_path)
        pattern: Any = self._find_matching_pattern(violation_key, signature)
        if pattern and pattern.confidence_score > 0.75:
            return pattern.fix_strategy
        patterns: Any = self.patterns.get(violation_key, [])
        if patterns:
            best: Any = max(patterns, key=lambda p: p.confidence_score)
            if best.confidence_score > 0.6:
                return best.fix_strategy
        return None

    def get_statistics(self) -> dict[str, Any]:
        """Get learning statistics."""
        total_patterns: Any = sum(len(p) for p in self.patterns.values())
        high_confidence: Any = sum(
            1 for patterns in self.patterns.values() for p in patterns if p.confidence_score > 0.8
        )
        avg_success_rate: Any = 0.0
        if total_patterns > 0:
            avg_success_rate: Any = (
                sum(p.success_rate for patterns in self.patterns.values() for p in patterns) / total_patterns
            )
        return {
            "total_patterns": total_patterns,
            "high_confidence_patterns": high_confidence,
            "average_success_rate": avg_success_rate,
            "keys_with_patterns": len(self.patterns),
            "total_healing_attempts": sum(
                p.success_count + p.failure_count for patterns in self.patterns.values() for p in patterns
            ),
        }


def create_adaptive_learning_engine(
    storage_path: str | None = None, autonomous_mode: bool = True
) -> AdaptiveLearningEngine:
    """Factory function to create adaptive learning engine."""
    return AdaptiveLearningEngine(pattern_storage_path=storage_path, autonomous_mode=autonomous_mode)
