#!/usr/bin/env python3
"""Graph-native ADG watchlist builder - Prompt 5.

Builds high-signal graph intelligence watchlist from:
- mv_graph_reverse_dependency_hotspots
- mv_graph_chokepoint_bridges
- mv_graph_scc_clusters
- mv_graph_critical_path_blast_radius

Focus: graph-native architectural intelligence not covered by regular ADG CI.
Emits compact JSON artifact and terminal summary.
Non-blocking intelligence layer.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from tqdm import tqdm


@dataclass
class RemediationGuide:
    """Remediation guidance for a graph hotspot."""

    recommended_fix_pattern: str
    remediation_priority: str  # high, medium, low
    gate_severity: str  # warn, fail
    gate_decision: str  # WARN, FAIL, INFO
    operator_note: str
    dry_run_patch: str | None = None  # Prompt 8: Generated patch for human review
    auto_apply_eligible: bool = False  # Prompt 8: Whether auto-apply is permitted


@dataclass
class GraphWatchlistItem:
    """Single graph-native watchlist entry."""

    rank: int
    file: str
    layer: str
    graph_anomaly_type: str
    score: float
    reverse_dep_score: float
    bridge_score: float
    scc_cluster_size: int
    blast_radius: float
    why_it_matters: str
    remediation: RemediationGuide | None = None


@dataclass
class DeltaClassification:
    """Prompt 9: Delta classification for graph hotspot transitions."""

    delta_type: str  # NEW_HOTSPOT, WORSENED, IMPROVED, STABLE, RESOLVED
    score_delta: float  # Current - Baseline
    gate_delta: str  # worsened, improved, stable
    baseline_score: float | None
    current_score: float
    baseline_gate: str | None
    current_gate: str
    is_regression: bool  # True if this represents negative change


@dataclass
class ProposalPacket:
    """Prompt 10: Shadow learning proposal for offline improvement.

    Shadow-only: No live runtime mutation. Promotion gated.
    """

    proposal_id: str
    category: str  # threshold_tuning, policy_refinement, wording_refinement, etc.
    trigger_evidence: list[dict]  # List of triggering events/patterns
    affected_signals: list[str]  # Which graph signals affected
    affected_layers: list[str]  # Which layers affected
    affected_files: list[str]  # Specific files involved
    suggested_change: str  # Proposed change description
    expected_benefit: str  # Expected outcome
    risk_assessment: str  # Risk of change
    confidence_score: float  # 0.0-1.0 confidence
    occurrence_count: int  # How many times pattern seen
    learning_window_runs: int  # Number of runs analyzed
    requires_human_review: bool = True  # Always true for shadow mode
    promotion_status: str = "shadow_only"  # Never auto-promoted


@dataclass
class PromotionQueueEntry:
    """Prompt 11: Queue entry for shadow proposal review.

    Tracks proposal through review workflow.
    """

    queue_id: str
    proposal_id: str
    original_proposal: ProposalPacket
    decision_state: (
        str  # shadow_only, queued_for_review, approved, rejected, modified_then_approved, rolled_back
    )
    reviewer: str | None  # Who made the decision
    rationale: str | None  # Why decision was made
    timestamp_queued: str
    timestamp_decided: str | None
    affected_targets: list[str]  # What would be changed
    rollback_token: str | None  # Token for reverting this promotion


@dataclass
class PromotionAction:
    """Prompt 11: Record of applied promotion.

    Attributed, reversible change to live config/reporting.
    """

    action_id: str
    source_proposal_id: str
    source_queue_id: str
    reviewer: str
    target_type: str  # threshold, reporting_priority, remediation_wording, caveat, policy_metadata
    target_path: str  # What was changed
    old_value: Any
    new_value: Any
    timestamp: str
    rationale: str
    rollback_token: str
    reversible: bool = True


@dataclass
class RollbackAction:
    """Prompt 11: Record of promotion rollback.

    Reverts a previously applied promotion.
    """

    rollback_id: str
    source_action_id: str
    source_proposal_id: str
    reviewer: str
    target_type: str
    target_path: str
    restored_value: Any
    timestamp: str
    rationale: str


@dataclass
class AcceptedBaseline:
    """Prompt 12: Explicitly accepted baseline for governance-grade delta tracking.

    Replaces "most recent artifact" heuristic with explicit governance.
    """

    baseline_id: str
    source_run_artifact: str  # Path to the source watchlist artifact
    accepted_by: str  # Who accepted this baseline
    accepted_at: str  # ISO timestamp
    rationale: str  # Why this baseline was accepted
    active: bool  # Only one baseline active at a time
    metadata: dict[str, Any]  # Additional context


@dataclass
class PromotionApplication:
    """Prompt 12: Record of approved promotion being applied to live state.

    Explicit, attributable, reversible application of promotion to config/reporting.
    """

    application_id: str
    source_promotion_action_id: str  # Links to PromotionAction from Prompt 11
    target_type: str  # threshold_config, reporting_priority, etc.
    target_path: str
    old_value: Any
    new_value: Any
    applied_by: str  # Who applied this promotion
    applied_at: str  # ISO timestamp
    rationale: str
    rollback_token: str
    active: bool  # Can be rolled back


@dataclass
class ActiveState:
    """Prompt 12: Current active state pointer.

    Single source of truth for which baseline and promotions are live.
    """

    active_baseline_id: str | None
    active_promotion_set_id: str | None  # ID of currently applied promotion set
    applied_promotion_ids: list[str]  # All currently active promotion applications
    last_applied_at: str | None
    last_updated_by: str | None


class ADGGraphWatchlistBuilder:
    """Build high-signal graph-native ADG watchlist."""

    # High-signal thresholds (graph-native)
    TOP_PERCENTILE = 90  # Top 10% by graph metrics
    CRITICAL_LAYERS = {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "L_APP", "L_SHARED", "L_RUNTIME"}

    # Signal-to-fix-pattern mapping (Prompt 7 remediation guidance)
    FIX_PATTERNS: dict[str, dict[str, str]] = {
        "reverse_dependency_hotspot": {
            "pattern": "reduce_inbound_surface",
            "actions": "split_responsibilities, introduce_stable_facade",
            "note": "Module has high inbound dependency surface; consider facade or responsibility split",
        },
        "chokepoint_bridge": {
            "pattern": "extract_interface_boundary",
            "actions": "break_hub_module, separate_coordination_from_execution",
            "note": "Module acts as structural bridge; extract interfaces to reduce coupling",
        },
        "risky_scc_cluster": {
            "pattern": "break_cycle_with_contract_extraction",
            "actions": "invert_dependency_direction, move_shared_types_to_neutral_layer",
            "note": "Module in cyclic dependency cluster; break cycle with contract extraction",
        },
        "critical_path_blast_radius": {
            "pattern": "isolate_change_surface",
            "actions": "narrow_shared_config, stabilize_adapter_boundary",
            "note": "Module has large downstream impact; isolate change surface",
        },
        "multi_signal_graph_hotspot": {
            "pattern": "comprehensive_refactor_needed",
            "actions": "combine_all_single_signal_fixes",
            "note": "Multiple structural risks detected; comprehensive review required",
        },
    }

    # CI Gate thresholds (Prompt 7)
    GATE_WARN_THRESHOLD = 50.0  # Score above this triggers WARN
    GATE_FAIL_THRESHOLD = 75.0  # Score above this in protected layer triggers FAIL
    BLAST_RADIUS_WARN_THRESHOLD = 100.0  # Blast radius above this triggers WARN
    BLAST_RADIUS_FAIL_THRESHOLD = 200.0  # Blast radius above this in protected layer triggers FAIL

    # Prompt 8: Auto-remediation safety policy
    # EXPLICIT DENYLIST - Never auto-remediate these
    AUTO_REMEDIATION_DENYLIST = {
        "layers": {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "L_APP", "L_SHARED", "L_RUNTIME"},
        "signals": {"multi_signal_graph_hotspot"},  # Multi-signal too complex
        "conditions": {"scc_cluster_size > 0"},  # SCC cases require architecture review
    }

    # CONDITIONAL ALLOWLIST - Dry-run OK, auto-apply requires human approval
    AUTO_REMEDIATION_ALLOWLIST = {
        "patterns": {"extract_interface_boundary"},  # Only __all__ exports (Class B)
        "layers": {"L_TOOLS", "L_UNKNOWN", "L_TEST", "L_SL"},  # Non-protected only
        "max_blast_radius": 100.0,  # Low impact only
    }

    # Prompt 9: Delta tracking and regression governance
    DELTA_IMPROVEMENT_THRESHOLD = -5.0  # Score decrease of 5+ is improvement
    DELTA_WORSENING_THRESHOLD = 5.0  # Score increase of 5+ is worsening
    PROTECTED_LAYER_REGRESSION_BAND = 10.0  # Protected layer score increase of 10+ is regression

    # Prompt 10: Shadow learning / meta-learning configuration
    LEARNING_WINDOW_RUNS = 5  # Analyze last 5 runs for pattern detection
    MIN_PATTERN_OCCURRENCES = 3  # Pattern must appear 3+ times to qualify
    HIGH_CONFIDENCE_THRESHOLD = 0.75  # Confidence >= 0.75 is high-confidence
    PROPOSAL_ID_PREFIX = "SL"  # Shadow Learning proposal ID prefix

    # Eligible learning signals for shadow proposals
    ELIGIBLE_LEARNING_SIGNALS = {
        "NEW_HOTSPOT",
        "WORSENED",
    }

    # Shadow proposal categories (all are advisory-only)
    PROPOSAL_CATEGORIES = {
        "threshold_tuning",
        "policy_refinement",
        "wording_refinement",
        "reporting_prioritization",
        "hotspot_clustering",
        "future_scope_recommendation",
        "no_change_recommended",
    }

    def __init__(self, sqlite_path: Path):
        self.sqlite_path = sqlite_path
        self.conn = sqlite3.connect(str(sqlite_path))
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.conn.close()

    def _get_threshold(self, table: str, column: str) -> float:
        """Get threshold for top percentile."""
        self.cur.execute(
            f"SELECT {column} FROM {table} ORDER BY {column} DESC "
            f"LIMIT 1 OFFSET (SELECT COUNT(*) FROM {table}) * {self.TOP_PERCENTILE} / 100"
        )
        row = self.cur.fetchone()
        return row[0] if row else 0.0

    def _get_reverse_dep_hotspots(self, threshold: float) -> list[dict[str, Any]]:
        """Get reverse dependency hotspots above threshold."""
        self.cur.execute(
            "SELECT file_path, layer, reverse_dependency_score, layer_criticality_weight "
            "FROM mv_graph_reverse_dependency_hotspots "
            "WHERE reverse_dependency_score >= ? "
            "ORDER BY reverse_dependency_score * layer_criticality_weight DESC",
            (threshold,),
        )
        return [dict(r) for r in self.cur.fetchall()]

    def _get_chokepoint_bridges(self, threshold: float) -> list[dict[str, Any]]:
        """Get chokepoint/bridge modules above threshold."""
        self.cur.execute(
            "SELECT file_path, layer, bridge_score, bridge_type, fan_in, fan_out "
            "FROM mv_graph_chokepoint_bridges "
            "WHERE bridge_score >= ? AND bridge_type IN ('high_impact_bridge', 'bridge_candidate') "
            "ORDER BY bridge_score DESC",
            (threshold,),
        )
        return [dict(r) for r in self.cur.fetchall()]

    def _get_scc_clusters(self, threshold: int) -> list[dict[str, Any]]:
        """Get SCC clusters above threshold."""
        self.cur.execute(
            "SELECT file_path, layer, scc_risk_score, cluster_size, cluster_type "
            "FROM mv_graph_scc_clusters "
            "WHERE scc_risk_score >= ? AND cluster_type IN ('large_tight_cluster', 'medium_tight_cluster') "
            "ORDER BY scc_risk_score DESC",
            (threshold,),
        )
        return [dict(r) for r in self.cur.fetchall()]

    def _get_blast_radius(self, threshold: float) -> list[dict[str, Any]]:
        """Get critical path blast radius modules above threshold."""
        self.cur.execute(
            "SELECT file_path, layer, weighted_blast_radius, blast_radius_type, critical_downstream_count "
            "FROM mv_graph_critical_path_blast_radius "
            "WHERE weighted_blast_radius >= ? AND blast_radius_type IN ('high_impact_hub', 'moderate_impact_hub') "
            "ORDER BY weighted_blast_radius DESC",
            (threshold,),
        )
        return [dict(r) for r in self.cur.fetchall()]

    def _compute_graph_composite_score(
        self,
        reverse_dep: float,
        bridge: float,
        scc_risk: int,
        blast_radius: float,
        layer: str,
    ) -> float:
        """Compute bounded graph-native composite score."""
        # Base weights (graph-native metrics)
        rev_weight = min(reverse_dep / 100 * 25, 25)  # Cap at 25
        bridge_weight = min(bridge / 50 * 20, 20)  # Cap at 20
        scc_weight = min(scc_risk / 100 * 20, 20)  # Cap at 20
        blast_weight = min(blast_radius / 100 * 25, 25)  # Cap at 25

        # Critical layer multiplier
        layer_multiplier = 1.25 if layer in self.CRITICAL_LAYERS else 1.0

        return (rev_weight + bridge_weight + scc_weight + blast_weight) * layer_multiplier

    def _classify_graph_anomaly(
        self,
        high_reverse_dep: bool,
        high_bridge: bool,
        high_scc: bool,
        high_blast: bool,
    ) -> str:
        """Classify graph-native anomaly type."""
        signals = []
        if high_reverse_dep:
            signals.append("reverse_dep")
        if high_bridge:
            signals.append("bridge")
        if high_scc:
            signals.append("scc")
        if high_blast:
            signals.append("blast")

        # Multi-signal requires 2 or more live non-zero graph dimensions
        if len(signals) >= 2:
            if len(signals) >= 3:
                return "multi_signal_graph_hotspot"
            # Exactly 2 signals
            return f"{signals[0]}_{signals[1]}_combined"
        if high_reverse_dep and high_blast:
            return "reverse_dependency_hotspot"  # High inbound + high downstream impact
        if high_bridge:
            return "chokepoint_bridge"
        if high_scc:
            return "risky_scc_cluster"
        if high_blast:
            return "critical_path_blast_radius"
        if high_reverse_dep:
            return "reverse_dependency_hotspot"
        return "low_signal_graph"

    def _explain_graph_why(
        self,
        reverse_dep: float,
        bridge: float,
        scc_size: int,
        blast_radius: float,
        layer: str,
    ) -> str:
        """One-line explanation of why this graph-native finding matters."""
        parts = []
        if reverse_dep > 200:
            parts.append(f"high inbound dep surface ({int(reverse_dep)})")
        elif reverse_dep > 50:
            parts.append(f"significant inbound deps ({int(reverse_dep)})")

        if bridge > 100:
            parts.append("structural chokepoint")
        elif bridge > 50:
            parts.append("bridge-like connectivity")

        if scc_size > 15:
            parts.append(f"large tight cluster ({scc_size} modules)")
        elif scc_size > 8:
            parts.append(f"tight coupling cluster ({scc_size} modules)")

        if blast_radius > 200:
            parts.append(f"massive blast radius ({int(blast_radius)})")
        elif blast_radius > 100:
            parts.append(f"high change impact ({int(blast_radius)})")

        if layer in self.CRITICAL_LAYERS:
            parts.append(f"{layer} critical layer")

        return ", ".join(parts[:3]) if parts else "graph-structural anomaly"

    def _get_remediation_guide(
        self,
        anomaly_type: str,
        score: float,
        blast_radius: float,
        layer: str,
    ) -> RemediationGuide:
        """Compute remediation guidance and gate decision for a graph hotspot.

        Prompt 7: Implements CI gate policy:
        - WARN on new high-score hotspot in non-protected layers
        - FAIL on new multi-signal hotspot in protected layers
        - FAIL on SCC emergence in protected layers
        - WARN/FAIL on blast radius increase above threshold for protected modules
        """
        # Get fix pattern for this anomaly type
        fix_info = self.FIX_PATTERNS.get(
            anomaly_type,
            {
                "pattern": "review_required",
                "actions": "manual_analysis",
                "note": "Graph anomaly detected; manual review required",
            },
        )

        # Determine if in protected layer
        is_protected = layer in self.CRITICAL_LAYERS

        # Determine gate decision based on score and layer
        if anomaly_type == "risky_scc_cluster" and is_protected:
            # SCC in protected layer is always FAIL
            gate_decision = "FAIL"
            gate_severity = "fail"
            priority = "high"
        elif score >= self.GATE_FAIL_THRESHOLD and is_protected:
            # High score in protected layer = FAIL
            gate_decision = "FAIL"
            gate_severity = "fail"
            priority = "high"
        elif blast_radius >= self.BLAST_RADIUS_FAIL_THRESHOLD and is_protected:
            # High blast radius in protected layer = FAIL
            gate_decision = "FAIL"
            gate_severity = "fail"
            priority = "high"
        elif score >= self.GATE_WARN_THRESHOLD:
            # High score anywhere = WARN
            gate_decision = "WARN"
            gate_severity = "warn"
            priority = "medium"
        elif blast_radius >= self.BLAST_RADIUS_WARN_THRESHOLD:
            # High blast radius anywhere = WARN
            gate_decision = "WARN"
            gate_severity = "warn"
            priority = "medium"
        else:
            # Below thresholds = INFO only
            gate_decision = "INFO"
            gate_severity = "info"
            priority = "low"

        # Build operator note
        note = fix_info["note"]
        if gate_decision in ("WARN", "FAIL"):
            note += f" [{gate_decision}: {priority} priority in {layer}]"

        # Determine auto-remediation eligibility (Prompt 8)
        auto_apply_eligible = self._is_auto_remediation_eligible(anomaly_type, score, blast_radius, layer)

        # Generate dry-run patch if applicable (Prompt 8)
        dry_run_patch = None
        if anomaly_type == "chokepoint_bridge" or auto_apply_eligible:
            dry_run_patch = self._generate_dry_run_patch(anomaly_type, fix_info["pattern"])

        return RemediationGuide(
            recommended_fix_pattern=fix_info["pattern"],
            remediation_priority=priority,
            gate_severity=gate_severity,
            gate_decision=gate_decision,
            operator_note=note,
            dry_run_patch=dry_run_patch,
            auto_apply_eligible=auto_apply_eligible,
        )

    def _is_auto_remediation_eligible(
        self, anomaly_type: str, score: float, blast_radius: float, layer: str
    ) -> bool:
        """Check if auto-remediation is eligible under Prompt 8 safety policy."""
        # Check denylist layers
        if layer in self.AUTO_REMEDIATION_DENYLIST["layers"]:
            return False
        # Check denylist signals (multi-signal too complex)
        if anomaly_type in self.AUTO_REMEDIATION_DENYLIST["signals"]:
            return False
        # Check blast radius threshold
        if blast_radius > self.AUTO_REMEDIATION_ALLOWLIST["max_blast_radius"]:
            return False
        # Check allowlist patterns
        fix_pattern = self.FIX_PATTERNS.get(anomaly_type, {}).get("pattern", "")
        if fix_pattern not in self.AUTO_REMEDIATION_ALLOWLIST["patterns"]:
            return False
        # Check allowlist layers
        if layer not in self.AUTO_REMEDIATION_ALLOWLIST["layers"]:
            return False
        # All checks passed - eligible for dry-run (NOT auto-apply)
        return True

    def _generate_dry_run_patch(self, anomaly_type: str, fix_pattern: str) -> str | None:
        """Generate a dry-run patch for human review (Prompt 8 bounded pilot)."""
        if fix_pattern == "extract_interface_boundary":
            # Generate __all__ export patch template
            lines = [
                "# AUTO-GENERATED PATCH - HUMAN REVIEW REQUIRED",
                f"# Pattern: Add __all__ to reduce module export surface",
                f"# Anomaly: {anomaly_type}",
                "# Safety: Dry-run only - apply manually after review",
                "",
                "--- a/{file}",
                "+++ b/{file}",
                "@@ -1,5 +1,15 @@",
                ' """Module docstring."""',
                "",
                "+# Prompt 8: Reduced export surface to address chokepoint bridge",
                "+__all__ = [",
                "+    # Add explicit exports here based on actual API surface",
                '+    # Example: "public_function",',
                '+    # Example: "PublicClass",',
                "+]",
                "",
                " # ... rest of module ...",
                "",
                "+# NOTE: Verify all legitimate consumers use explicit imports",
                "+# before applying this patch.",
            ]
            return "\n".join(lines)
        return None

    # Prompt 9: Delta tracking and baseline comparison methods
    def _load_baseline(self, output_dir: Path) -> dict[str, dict] | None:
        """Load most recent baseline watchlist artifact for comparison.

        Returns:
            Dict mapping file_path to baseline item data, or None if no baseline exists.
        """
        # Find most recent graph watchlist artifact
        artifacts = sorted(output_dir.glob("adg_graph_watchlist_*.json"))
        if not artifacts:
            return None  # No baseline exists (first run)

        # Use the most recent artifact as baseline
        baseline_path = artifacts[-1]
        try:
            with open(baseline_path, encoding="utf-8") as f:
                baseline_data = json.load(f)
            # Create lookup by file path
            return {item["file"]: item for item in baseline_data.get("watchlist", [])}
        except (json.JSONDecodeError, KeyError, OSError):
            return None  # Graceful fallback if baseline is corrupted

    def _classify_delta(
        self,
        file_path: str,
        current_item: GraphWatchlistItem | None,
        baseline_item: dict | None,
    ) -> DeltaClassification:
        """Classify the delta between current and baseline for a single item."""
        # Extract baseline values
        baseline_score = baseline_item.get("score") if baseline_item else None
        baseline_gate = None
        if baseline_item and baseline_item.get("remediation"):
            baseline_gate = baseline_item["remediation"].get("gate_decision")

        # Extract current values
        current_score = current_item.score if current_item else 0.0
        current_gate = (
            current_item.remediation.gate_decision if current_item and current_item.remediation else "INFO"
        )

        # Calculate score delta
        score_delta = current_score - (baseline_score or 0.0)

        # Determine delta type
        if baseline_item is None and current_item is not None:
            delta_type = "NEW_HOTSPOT"
        elif baseline_item is not None and current_item is None:
            delta_type = "RESOLVED"
        elif score_delta >= self.DELTA_WORSENING_THRESHOLD:
            delta_type = "WORSENED"
        elif score_delta <= self.DELTA_IMPROVEMENT_THRESHOLD:
            delta_type = "IMPROVED"
        else:
            delta_type = "STABLE"

        # Determine gate delta
        gate_priority = {"FAIL": 3, "WARN": 2, "INFO": 1}
        current_priority = gate_priority.get(current_gate, 0)
        baseline_priority = gate_priority.get(baseline_gate, 0) if baseline_gate else 0

        if current_priority > baseline_priority:
            gate_delta = "worsened"
        elif current_priority < baseline_priority:
            gate_delta = "improved"
        else:
            gate_delta = "stable"

        # Determine if this is a regression (negative change)
        is_regression = delta_type in ("NEW_HOTSPOT", "WORSENED") or gate_delta == "worsened"

        return DeltaClassification(
            delta_type=delta_type,
            score_delta=score_delta,
            gate_delta=gate_delta,
            baseline_score=baseline_score,
            current_score=current_score,
            baseline_gate=baseline_gate,
            current_gate=current_gate,
            is_regression=is_regression,
        )

    def _is_regression(self, delta: DeltaClassification, layer: str) -> bool:
        """Determine if a delta constitutes a regression requiring CI action."""
        if not delta.is_regression:
            return False

        # Protected layer regressions are more serious
        is_protected = layer in self.CRITICAL_LAYERS

        # New protected-layer multi-signal hotspot above fail threshold = regression
        if delta.delta_type == "NEW_HOTSPOT" and is_protected and delta.current_gate == "FAIL":
            return True

        # Protected layer score worsening beyond band = regression
        if is_protected and delta.score_delta >= self.PROTECTED_LAYER_REGRESSION_BAND:
            return True

        # Gate worsening in protected layer = regression
        if is_protected and delta.gate_delta == "worsened":
            return True

        return False

    def _compute_deltas(
        self,
        current_watchlist: list[GraphWatchlistItem],
        output_dir: Path,
    ) -> dict:
        """Compute deltas between current watchlist and baseline.

        Prompt 12: Uses accepted baseline for governance-grade delta tracking.
        Falls back to most-recent only if no accepted baseline exists.

        Returns dict with delta_summary and per-item classifications.
        """
        # Load accepted baseline (governance-grade)
        baseline = self._load_baseline_accepted(output_dir)

        # First run - no baseline
        if baseline is None:
            return {
                "has_baseline": False,
                "delta_summary": {
                    "new": 0,
                    "worsened": 0,
                    "improved": 0,
                    "stable": 0,
                    "resolved": 0,
                },
                "items": [],
                "regressions": [],
            }

        # Track all files from both current and baseline
        all_files = set(item.file for item in current_watchlist) | set(baseline.keys())

        delta_items = []
        regressions = []
        summary = {"new": 0, "worsened": 0, "improved": 0, "stable": 0, "resolved": 0}

        for file_path in tqdm(all_files, desc="Processing", unit="item"):
            current_item = next((i for i in current_watchlist if i.file == file_path), None)
            baseline_item = baseline.get(file_path)

            delta = self._classify_delta(file_path, current_item, baseline_item)

            delta_items.append(
                {
                    "file": file_path,
                    "delta_type": delta.delta_type,
                    "score_delta": round(delta.score_delta, 2),
                    "gate_delta": delta.gate_delta,
                    "is_regression": delta.is_regression,
                }
            )

            summary[delta.delta_type.lower().replace("_hotspot", "")] += 1

            if self._is_regression(delta, current_item.layer if current_item else ""):
                regressions.append(
                    {
                        "file": file_path,
                        "layer": current_item.layer if current_item else baseline_item.get("layer", ""),
                        "delta_type": delta.delta_type,
                        "score_delta": round(delta.score_delta, 2),
                    }
                )

        return {
            "has_baseline": True,
            "baseline_artifact": str(sorted(output_dir.glob("adg_graph_watchlist_*.json"))[-1])
            if list(output_dir.glob("adg_graph_watchlist_*.json"))
            else None,
            "delta_summary": summary,
            "items": delta_items,
            "regressions": regressions,
        }

    # Prompt 12: Accepted baseline delta tracking
    def _load_baseline_accepted(self, output_dir: Path) -> dict[str, dict] | None:
        """Load accepted baseline for governance-grade delta tracking.

        Prompt 12: Replaces heuristic with explicit accepted baseline.
        Falls back to most-recent only if no accepted baseline exists.
        """
        # Try accepted baseline first (governance-grade)
        baseline_manager = AcceptedBaselineManager(output_dir)
        accepted_path = baseline_manager.get_accepted_baseline_artifact_path()

        if accepted_path:
            try:
                with open(accepted_path, encoding="utf-8") as f:
                    baseline_data = json.load(f)
                # Create lookup by file path
                return {item["file"]: item for item in baseline_data.get("watchlist", [])}
            except (json.JSONDecodeError, KeyError, OSError):
                pass  # Fall through to legacy behavior

        # Fallback: most recent artifact (legacy behavior for first-run)
        return self._load_baseline_legacy(output_dir)

    def _load_baseline_legacy(self, output_dir: Path) -> dict[str, dict] | None:
        """Legacy baseline loading - most recent artifact."""
        artifacts = sorted(output_dir.glob("adg_graph_watchlist_*.json"))
        if not artifacts:
            return None  # No baseline exists (first run)

        # Use the most recent artifact as baseline
        baseline_path = artifacts[-1]
        try:
            with open(baseline_path, encoding="utf-8") as f:
                baseline_data = json.load(f)
            # Create lookup by file path
            return {item["file"]: item for item in baseline_data.get("watchlist", [])}
        except (json.JSONDecodeError, KeyError, OSError):
            return None  # Graceful fallback if baseline is corrupted

    # Prompt 10: Shadow learning / meta-learning methods
    def _load_learning_window(self, output_dir: Path) -> list[dict]:
        """Load last N runs for pattern analysis.

        Returns list of artifact data from learning window.
        """
        artifacts = sorted(output_dir.glob("adg_graph_watchlist_*.json"))
        if not artifacts:
            return []

        # Take last LEARNING_WINDOW_RUNS artifacts
        window_artifacts = artifacts[-self.LEARNING_WINDOW_RUNS :]

        window_data = []
        for artifact_path in window_artifacts:
            try:
                with open(artifact_path, encoding="utf-8") as f:
                    data = json.load(f)
                    data["_artifact_path"] = str(artifact_path)
                    window_data.append(data)
            except (json.JSONDecodeError, OSError):
                continue  # Skip corrupted artifacts

        return window_data

    def _aggregate_patterns(self, window_data: list[dict]) -> dict:
        """Aggregate repeated patterns across learning window.

        Returns pattern summary with occurrence counts.
        """
        patterns = {
            "file_repeat_offenders": {},
            "layer_repeat_offenders": {},
            "signal_repeat_offenders": {},
            "gate_fail_repeat": {},
            "new_hotspot_repeat": {},
            "worsened_repeat": {},
        }

        for run_data in tqdm(window_data, desc="Processing", unit="item"):
            watchlist = run_data.get("watchlist", [])
            delta_tracking = run_data.get("delta_tracking", {})

            # Track file occurrences
            for item in tqdm(watchlist, desc="Processing", unit="item"):
                file_path = item.get("file", "")
                layer = item.get("layer", "")
                signal = item.get("graph_anomaly_type", "")
                remediation = item.get("remediation", {})
                gate = remediation.get("gate_decision", "INFO")

                # File patterns
                if file_path:
                    patterns["file_repeat_offenders"][file_path] = (
                        patterns["file_repeat_offenders"].get(file_path, 0) + 1
                    )

                # Layer patterns
                if layer:
                    patterns["layer_repeat_offenders"][layer] = (
                        patterns["layer_repeat_offenders"].get(layer, 0) + 1
                    )

                # Signal patterns
                if signal:
                    patterns["signal_repeat_offenders"][signal] = (
                        patterns["signal_repeat_offenders"].get(signal, 0) + 1
                    )

                # Gate FAIL patterns
                if gate == "FAIL":
                    patterns["gate_fail_repeat"][file_path] = (
                        patterns["gate_fail_repeat"].get(file_path, 0) + 1
                    )

            # Delta patterns
            delta_items = delta_tracking.get("items", [])
            for delta_item in delta_items:
                delta_type = delta_item.get("delta_type", "")
                file_path = delta_item.get("file", "")

                if delta_type == "NEW_HOTSPOT":
                    patterns["new_hotspot_repeat"][file_path] = (
                        patterns["new_hotspot_repeat"].get(file_path, 0) + 1
                    )
                elif delta_type == "WORSENED":
                    patterns["worsened_repeat"][file_path] = patterns["worsened_repeat"].get(file_path, 0) + 1

        return patterns

    def _compute_confidence(self, occurrence_count: int, window_runs: int) -> float:
        """Compute proposal confidence score.

        Formula: min(occurrence_count / MIN_PATTERN_OCCURRENCES, 1.0) * (window_runs / LEARNING_WINDOW_RUNS)
        """
        if window_runs == 0:
            return 0.0

        # Occurrence ratio (capped at 1.0)
        occurrence_ratio = min(occurrence_count / self.MIN_PATTERN_OCCURRENCES, 1.0)

        # Window completeness ratio
        window_ratio = min(window_runs / self.LEARNING_WINDOW_RUNS, 1.0)

        # Combined confidence
        confidence = occurrence_ratio * window_ratio

        return round(confidence, 2)

    def _generate_shadow_proposals(self, patterns: dict, window_data: list[dict]) -> list[ProposalPacket]:
        """Generate shadow learning proposals from aggregated patterns.

        All proposals are shadow-only (no live mutation).
        """
        proposals = []
        window_runs = len(window_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if window_runs < 2:
            # Insufficient data - recommend no change
            proposals.append(
                ProposalPacket(
                    proposal_id=f"{self.PROPOSAL_ID_PREFIX}_{timestamp}_001",
                    category="no_change_recommended",
                    trigger_evidence=[
                        {"reason": "insufficient_historical_data", "runs_available": window_runs}
                    ],
                    affected_signals=[],
                    affected_layers=[],
                    affected_files=[],
                    suggested_change="Continue monitoring; insufficient data for confident proposal",
                    expected_benefit="Avoid premature threshold changes",
                    risk_assessment="Low - no change proposed",
                    confidence_score=1.0,  # High confidence that we should NOT change yet
                    occurrence_count=window_runs,
                    learning_window_runs=window_runs,
                )
            )
            return proposals

        proposal_counter = 1

        # Proposal 1: Repeat offender files
        repeat_offenders = {
            f: c for f, c in patterns["file_repeat_offenders"].items() if c >= self.MIN_PATTERN_OCCURRENCES
        }
        if repeat_offenders:
            top_offender = max(repeat_offenders.items(), key=lambda x: x[1])
            confidence = self._compute_confidence(top_offender[1], window_runs)

            proposals.append(
                ProposalPacket(
                    proposal_id=f"{self.PROPOSAL_ID_PREFIX}_{timestamp}_{proposal_counter:03d}",
                    category="hotspot_clustering",
                    trigger_evidence=[
                        {
                            "pattern": "file_repeat_offender",
                            "file": top_offender[0],
                            "occurrences": top_offender[1],
                        }
                    ],
                    affected_signals=["multi_signal_graph_hotspot"],
                    affected_layers=[],
                    affected_files=[top_offender[0]],
                    suggested_change=f"Consider dedicated review of {top_offender[0]} - appears in {top_offender[1]}/{window_runs} runs",
                    expected_benefit="Targeted attention on persistent hotspot",
                    risk_assessment="Low - advisory only",
                    confidence_score=confidence,
                    occurrence_count=top_offender[1],
                    learning_window_runs=window_runs,
                )
            )
            proposal_counter += 1

        # Proposal 2: Protected layer repeat offenders
        protected_offenders = {
            layer: count
            for layer, count in patterns["layer_repeat_offenders"].items()
            if layer in self.CRITICAL_LAYERS and count >= self.MIN_PATTERN_OCCURRENCES
        }
        if protected_offenders:
            top_layer = max(protected_offenders.items(), key=lambda x: x[1])
            confidence = self._compute_confidence(top_layer[1], window_runs)

            proposals.append(
                ProposalPacket(
                    proposal_id=f"{self.PROPOSAL_ID_PREFIX}_{timestamp}_{proposal_counter:03d}",
                    category="policy_refinement",
                    trigger_evidence=[
                        {
                            "pattern": "protected_layer_repeat",
                            "layer": top_layer[0],
                            "occurrences": top_layer[1],
                        }
                    ],
                    affected_signals=[],
                    affected_layers=[top_layer[0]],
                    affected_files=[],
                    suggested_change=f"Review gate thresholds for {top_layer[0]} - persistent protected-layer hotspot",
                    expected_benefit="More appropriate severity assignment",
                    risk_assessment="Medium - threshold changes affect CI behavior",
                    confidence_score=confidence,
                    occurrence_count=top_layer[1],
                    learning_window_runs=window_runs,
                )
            )
            proposal_counter += 1

        # Proposal 3: Repeated NEW_HOTSPOT pattern
        new_hotspots = patterns.get("new_hotspot_repeat", {})
        if new_hotspots:
            top_new = max(new_hotspots.items(), key=lambda x: x[1])
            if top_new[1] >= self.MIN_PATTERN_OCCURRENCES:
                confidence = self._compute_confidence(top_new[1], window_runs)

                proposals.append(
                    ProposalPacket(
                        proposal_id=f"{self.PROPOSAL_ID_PREFIX}_{timestamp}_{proposal_counter:03d}",
                        category="threshold_tuning",
                        trigger_evidence=[
                            {"pattern": "repeated_new_hotspot", "file": top_new[0], "occurrences": top_new[1]}
                        ],
                        affected_signals=["NEW_HOTSPOT"],
                        affected_layers=[],
                        affected_files=[top_new[0]],
                        suggested_change=f"Investigate why {top_new[0]} appears as NEW in multiple runs - may indicate flaky threshold",
                        expected_benefit="More stable hotspot detection",
                        risk_assessment="Low - advisory review",
                        confidence_score=confidence,
                        occurrence_count=top_new[1],
                        learning_window_runs=window_runs,
                    )
                )
                proposal_counter += 1

        # Proposal 4: Repeated WORSENED pattern
        worsened = patterns.get("worsened_repeat", {})
        if worsened:
            top_worsened = max(worsened.items(), key=lambda x: x[1])
            if top_worsened[1] >= self.MIN_PATTERN_OCCURRENCES:
                confidence = self._compute_confidence(top_worsened[1], window_runs)

                proposals.append(
                    ProposalPacket(
                        proposal_id=f"{self.PROPOSAL_ID_PREFIX}_{timestamp}_{proposal_counter:03d}",
                        category="reporting_prioritization",
                        trigger_evidence=[
                            {
                                "pattern": "repeated_worsening",
                                "file": top_worsened[0],
                                "occurrences": top_worsened[1],
                            }
                        ],
                        affected_signals=["WORSENED"],
                        affected_layers=[],
                        affected_files=[top_worsened[0]],
                        suggested_change=f"Prioritize investigation of {top_worsened[0]} - consistently worsening across runs",
                        expected_benefit="Early intervention on degrading module",
                        risk_assessment="Low - reporting change only",
                        confidence_score=confidence,
                        occurrence_count=top_worsened[1],
                        learning_window_runs=window_runs,
                    )
                )
                proposal_counter += 1

        return proposals

    def emit_shadow_learning_artifact(
        self,
        proposals: list[ProposalPacket],
        patterns: dict,
        window_data: list[dict],
        output_dir: Path,
    ) -> Path | None:
        """Emit shadow learning artifact with proposals.

        Shadow-only: Does not mutate live runtime behavior.
        """
        if not proposals:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifact_path = output_dir / f"adg_shadow_learning_{timestamp}.json"

        # Count high-confidence proposals
        high_confidence_count = sum(
            1 for p in proposals if p.confidence_score >= self.HIGH_CONFIDENCE_THRESHOLD
        )

        artifact = {
            "timestamp": timestamp,
            "shadow_mode": True,
            "live_mutation": False,  # Explicit: no live changes
            "learning_window": {
                "runs_analyzed": len(window_data),
                "max_runs_configured": self.LEARNING_WINDOW_RUNS,
            },
            "pattern_summary": {
                "total_files_seen": len(patterns.get("file_repeat_offenders", {})),
                "repeat_offenders": len(
                    [
                        f
                        for f, c in patterns.get("file_repeat_offenders", {}).items()
                        if c >= self.MIN_PATTERN_OCCURRENCES
                    ]
                ),
                "protected_layer_offenders": len(
                    [
                        l
                        for l, c in patterns.get("layer_repeat_offenders", {}).items()
                        if l in self.CRITICAL_LAYERS and c >= self.MIN_PATTERN_OCCURRENCES
                    ]
                ),
            },
            "proposal_summary": {
                "total_proposals": len(proposals),
                "high_confidence_proposals": high_confidence_count,
                "categories": list(set(p.category for p in proposals)),
            },
            "proposals": [
                {
                    "proposal_id": p.proposal_id,
                    "category": p.category,
                    "suggested_change": p.suggested_change,
                    "confidence_score": p.confidence_score,
                    "occurrence_count": p.occurrence_count,
                    "requires_human_review": p.requires_human_review,
                    "promotion_status": p.promotion_status,
                }
                for p in proposals[:10]
            ],  # Cap at 10 proposals
            "top_proposals": [
                {
                    "proposal_id": p.proposal_id,
                    "category": p.category,
                    "suggested_change": p.suggested_change[:100] + "..."
                    if len(p.suggested_change) > 100
                    else p.suggested_change,
                    "confidence_score": p.confidence_score,
                }
                for p in sorted(proposals, key=lambda x: x.confidence_score, reverse=True)[:3]
            ],
        }

        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2)

        return artifact_path

    def build_graph_watchlist(self) -> list[GraphWatchlistItem]:
        """Build ranked graph-native watchlist."""
        # Get thresholds for top percentile filtering
        rev_threshold = self._get_threshold(
            "mv_graph_reverse_dependency_hotspots", "reverse_dependency_score"
        )
        bridge_threshold = self._get_threshold("mv_graph_chokepoint_bridges", "bridge_score")
        scc_threshold = self._get_threshold("mv_graph_scc_clusters", "scc_risk_score")
        blast_threshold = self._get_threshold("mv_graph_critical_path_blast_radius", "weighted_blast_radius")

        # Get high-signal items from each graph view
        rev_hotspots = {r["file_path"]: r for r in self._get_reverse_dep_hotspots(rev_threshold)}
        bridges = {b["file_path"]: b for b in self._get_chokepoint_bridges(bridge_threshold)}
        scc_clusters = {s["file_path"]: s for s in self._get_scc_clusters(int(scc_threshold))}
        blast_modules = {b["file_path"]: b for b in self._get_blast_radius(blast_threshold)}

        # Combine all files of interest
        all_files = (
            set(rev_hotspots.keys())
            | set(bridges.keys())
            | set(scc_clusters.keys())
            | set(blast_modules.keys())
        )

        # Get max values for normalization
        max_rev = max((r["reverse_dependency_score"] for r in rev_hotspots.values()), default=1.0)
        max_bridge = max((b["bridge_score"] for b in bridges.values()), default=1.0)
        max_scc = max((s["scc_risk_score"] for s in scc_clusters.values()), default=1)
        max_blast = max((b["weighted_blast_radius"] for b in blast_modules.values()), default=1.0)

        # Build watchlist items
        items: list[tuple[float, GraphWatchlistItem]] = []

        for file_path in tqdm(all_files, desc="Processing", unit="item"):
            rev = rev_hotspots.get(file_path, {})
            bridge = bridges.get(file_path, {})
            scc = scc_clusters.get(file_path, {})
            blast = blast_modules.get(file_path, {})

            reverse_dep_score = rev.get("reverse_dependency_score", 0.0)
            bridge_score = bridge.get("bridge_score", 0.0)
            scc_size = scc.get("cluster_size", 0)
            blast_radius = blast.get("weighted_blast_radius", 0.0)
            layer = rev.get("layer") or bridge.get("layer") or scc.get("layer") or blast.get("layer") or ""

            # Skip low-signal items
            if reverse_dep_score < 30 and bridge_score < 30 and scc_size < 5 and blast_radius < 30:
                continue

            high_rev = reverse_dep_score >= rev_threshold
            high_bridge = bridge_score >= bridge_threshold
            high_scc = scc_size >= scc_threshold
            high_blast = blast_radius >= blast_threshold

            score = self._compute_graph_composite_score(
                reverse_dep_score, bridge_score, scc_size, blast_radius, layer
            )

            graph_anomaly_type = self._classify_graph_anomaly(high_rev, high_bridge, high_scc, high_blast)

            # Compute remediation guide (Prompt 7)
            remediation = self._get_remediation_guide(graph_anomaly_type, score, blast_radius, layer)

            item = GraphWatchlistItem(
                rank=0,  # Set after sorting
                file=file_path,
                layer=layer,
                graph_anomaly_type=graph_anomaly_type,
                score=round(score, 2),
                reverse_dep_score=round(reverse_dep_score, 2),
                bridge_score=round(bridge_score, 2),
                scc_cluster_size=scc_size,
                blast_radius=round(blast_radius, 2),
                why_it_matters=self._explain_graph_why(
                    reverse_dep_score, bridge_score, scc_size, blast_radius, layer
                ),
                remediation=remediation,
            )
            items.append((score, item))

        # Sort by score descending and assign ranks
        items.sort(key=lambda x: x[0], reverse=True)
        result = []
        for i, (_, item) in enumerate(items, 1):
            item.rank = i
            result.append(item)

        return result

    def emit_artifact(self, watchlist: list[GraphWatchlistItem], output_dir: Path) -> Path:
        """Emit graph watchlist JSON artifact."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifact_path = output_dir / f"adg_graph_watchlist_{timestamp}.json"

        # Promotion classification for each signal type
        promotion_status = {
            "reverse_dependency": "promote_now",
            "chokepoint_bridge": "promote_now",
            "blast_radius": "promote_now",
            "scc_cluster": "surface_with_caveat",  # Semantic proof not fully closed
        }

        # Caveat for SCC: codebase may be acyclic (positive signal)
        scc_caveat = (
            "SCC detection returned 0 clusters - codebase may have no import cycles. "
            "This is architecturally positive. Full semantic toy-graph proof deferred."
        )

        # Compute gate summary for artifact (Prompt 7)
        gate_summary = {
            "total_fail": sum(
                1 for i in watchlist if i.remediation and i.remediation.gate_decision == "FAIL"
            ),
            "total_warn": sum(
                1 for i in watchlist if i.remediation and i.remediation.gate_decision == "WARN"
            ),
            "total_info": sum(
                1 for i in watchlist if i.remediation and i.remediation.gate_decision == "INFO"
            ),
        }

        # Prompt 9: Delta tracking - compare against baseline if available
        delta_result = self._compute_deltas(watchlist, output_dir)

        artifact = {
            "timestamp": timestamp,
            "sqlite_source": self.sqlite_path.name,
            "total_items": len(watchlist),
            "threshold": {
                "graph_top_percentile": self.TOP_PERCENTILE,
                "gate_warn_threshold": self.GATE_WARN_THRESHOLD,
                "gate_fail_threshold": self.GATE_FAIL_THRESHOLD,
            },
            "promotion_status": promotion_status,
            "gate_summary": gate_summary,
            "caveats": {
                "scc_detection": scc_caveat
                if len(watchlist) > 0 and all(i.scc_cluster_size == 0 for i in watchlist)
                else None,
            },
            "delta_tracking": {
                "has_baseline": delta_result["has_baseline"],
                "baseline_artifact": delta_result.get("baseline_artifact"),
                "delta_summary": delta_result["delta_summary"],
                "regression_count": len(delta_result.get("regressions", [])),
                "per_item_deltas": delta_result.get("items", [])[:50],  # Cap at 50
            },
            "watchlist": [asdict(item) for item in watchlist[:30]],  # Cap at 30
        }

        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2)

        return artifact_path

    def emit_terminal_summary(self, watchlist: list[GraphWatchlistItem], top_n: int = 10) -> str:
        """Emit compact terminal summary for graph-native SQL analytics."""
        lines = [
            "",
            "╔══════════════════════════════════════════════════════════════╗",
            "║     ADG GRAPH-NATIVE SQL ANALYTICS WATCHLIST               ║",
            "╚══════════════════════════════════════════════════════════════╝",
            "",
            f"Total graph items: {len(watchlist)} | Top {min(top_n, len(watchlist))} shown",
            "",
            f"{'Rank':<6}{'Score':<8}{'Graph Type':<28}{'Layer':<8}{'File':<40}",
            "-" * 90,
        ]

        for item in watchlist[:top_n]:
            file_short = item.file[:39] if len(item.file) <= 39 else item.file[:36] + "..."
            type_short = item.graph_anomaly_type[:27]
            layer_short = item.layer[:7] if item.layer else ""
            lines.append(f"{item.rank:<6}{item.score:<8.1f}{type_short:<28}{layer_short:<8}{file_short}")

        # Add caveat note for SCC if relevant
        has_scc_items = any(i.scc_cluster_size > 0 for i in watchlist[:top_n])
        scc_note = ""
        if not has_scc_items:
            scc_note = "[Note: SCC=0 - codebase appears acyclic, which is architecturally positive]"

        # Add remediation guidance for top 3 items (Prompt 7)
        lines.append("")
        lines.append("Remediation guidance (top 3):")
        for item in watchlist[:3]:
            if item.remediation:
                fix_short = item.remediation.recommended_fix_pattern[:35]
                gate = item.remediation.gate_decision
                lines.append(f"  G{item.rank}: {fix_short:<35} [{gate}]")

        lines.extend(
            [
                "",
                "Graph-native SQL signals: RevDep=reverse-dep, Bridge=chokepoint,",
                "                         SCC=tight-cluster, Blast=downstream-impact",
                f"{scc_note}",
                "Multi-signal items = highest structural risk.",
                "",
            ]
        )

        return "\n".join(lines)


def build_and_emit_graph_watchlist(
    sqlite_path: Path,
    output_dir: Path,
    print_summary: bool = True,
    enable_shadow_learning: bool = True,  # Prompt 10
) -> Path:
    """Main entry: build graph watchlist, emit artifact, optionally print summary.

    Args:
        sqlite_path: Path to ADG SQLite snapshot
        output_dir: Directory for watchlist artifact
        print_summary: Whether to print terminal summary
        enable_shadow_learning: Whether to generate shadow learning proposals (Prompt 10)

    Returns:
        Path to emitted JSON artifact
    """
    with ADGGraphWatchlistBuilder(sqlite_path) as builder:
        watchlist = builder.build_graph_watchlist()
        artifact_path = builder.emit_artifact(watchlist, output_dir)

        # Prompt 10: Shadow learning - generate offline proposals
        shadow_artifact_path = None
        if enable_shadow_learning:
            window_data = builder._load_learning_window(output_dir)
            patterns = builder._aggregate_patterns(window_data)
            proposals = builder._generate_shadow_proposals(patterns, window_data)
            shadow_artifact_path = builder.emit_shadow_learning_artifact(
                proposals, patterns, window_data, output_dir
            )

        if print_summary:
            summary = builder.emit_terminal_summary(watchlist, top_n=10)
            print(summary)

            # Prompt 10: Show shadow learning summary
            if shadow_artifact_path:
                print(f"\n[ADG] Shadow learning: proposals generated (no live changes)")
                print(f"      Artifact: {shadow_artifact_path.name}")

        return artifact_path


class ADGProposalPromotionManager:
    """Prompt 11: Human-reviewed promotion workflow for shadow learning proposals.

    Manages queue, review decisions, promotion application, and rollback.
    Core principle: No live mutation without explicit human approval.
    """

    # Prompt 11: Valid state transitions
    VALID_TRANSITIONS = {
        "shadow_only": ["queued_for_review"],
        "queued_for_review": ["approved_for_promotion", "rejected", "modified_then_approved"],
        "approved_for_promotion": ["rolled_back"],
        "modified_then_approved": ["rolled_back"],
        "rejected": [],  # Terminal state
        "rolled_back": [],  # Terminal state
    }

    # Allowed promotion targets
    ALLOWED_TARGETS = {
        "threshold_config",
        "reporting_priority",
        "remediation_wording",
        "caveat_wording",
        "policy_metadata",
    }

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.queue: list[PromotionQueueEntry] = []
        self.promotions: list[PromotionAction] = []
        self.rollbacks: list[RollbackAction] = []
        self._load_existing_queue()

    def _load_existing_queue(self) -> None:
        """Load existing queue from promotion artifact if exists."""
        queue_artifacts = sorted(self.output_dir.glob("adg_promotion_queue_*.json"))
        if queue_artifacts:
            try:
                with open(queue_artifacts[-1], encoding="utf-8") as f:
                    data = json.load(f)
                    # Reconstruct queue entries from saved data
                    for entry_data in tqdm(data.get("entries", []), desc="Processing", unit="item"):
                        # Create minimal proposal for reconstruction
                        proposal = ProposalPacket(
                            proposal_id=entry_data.get("proposal_id", "unknown"),
                            category="unknown",
                            trigger_evidence=[],
                            affected_signals=[],
                            affected_layers=[],
                            affected_files=[],
                            suggested_change="",
                            expected_benefit="",
                            risk_assessment="",
                            confidence_score=0.0,
                            occurrence_count=0,
                            learning_window_runs=0,
                        )
                        entry = PromotionQueueEntry(
                            queue_id=entry_data.get("queue_id", ""),
                            proposal_id=entry_data.get("proposal_id", ""),
                            original_proposal=proposal,
                            decision_state=entry_data.get("decision_state", "queued_for_review"),
                            reviewer=entry_data.get("reviewer"),
                            rationale=None,
                            timestamp_queued=entry_data.get(
                                "queued_at", datetime.now().strftime("%Y%m%d_%H%M%S")
                            ),
                            timestamp_decided=None,
                            affected_targets=entry_data.get("affected_targets", []),
                            rollback_token=entry_data.get("rollback_token"),
                        )
                        self.queue.append(entry)
            except (json.JSONDecodeError, OSError, KeyError):
                pass  # Start with empty queue

    def queue_proposal(self, proposal: ProposalPacket) -> PromotionQueueEntry:
        """Add shadow proposal to review queue.

        Default state: shadow_only -> queued_for_review
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        queue_id = f"QP_{timestamp}_{proposal.proposal_id}"

        # Determine affected targets from proposal category
        affected_targets = self._determine_affected_targets(proposal)

        entry = PromotionQueueEntry(
            queue_id=queue_id,
            proposal_id=proposal.proposal_id,
            original_proposal=proposal,
            decision_state="queued_for_review",
            reviewer=None,
            rationale=None,
            timestamp_queued=timestamp,
            timestamp_decided=None,
            affected_targets=affected_targets,
            rollback_token=None,
        )

        self.queue.append(entry)
        return entry

    def _determine_affected_targets(self, proposal: ProposalPacket) -> list[str]:
        """Determine what would be affected by this proposal."""
        targets = []

        if proposal.category == "threshold_tuning":
            targets.append("threshold_config")
        elif proposal.category == "reporting_prioritization":
            targets.append("reporting_priority")
        elif proposal.category == "wording_refinement":
            targets.append("remediation_wording")
        elif proposal.category == "hotspot_clustering":
            targets.append("reporting_priority")
        elif proposal.category == "policy_refinement":
            targets.append("policy_metadata")

        return targets

    def _is_valid_transition(self, current_state: str, new_state: str) -> bool:
        """Check if state transition is valid."""
        return new_state in self.VALID_TRANSITIONS.get(current_state, [])

    def approve_proposal(
        self,
        queue_id: str,
        reviewer: str,
        rationale: str,
    ) -> PromotionAction | None:
        """Approve proposal for promotion.

        Creates promotion action with full attribution.
        """
        entry = next((e for e in self.queue if e.queue_id == queue_id), None)
        if not entry:
            return None

        if not self._is_valid_transition(entry.decision_state, "approved_for_promotion"):
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Update entry state
        entry.decision_state = "approved_for_promotion"
        entry.reviewer = reviewer
        entry.rationale = rationale
        entry.timestamp_decided = timestamp

        # Generate rollback token
        rollback_token = f"RB_{timestamp}_{queue_id}"
        entry.rollback_token = rollback_token

        # Create promotion action (bounded, attributed, reversible)
        action = self._create_promotion_action(entry, timestamp, rollback_token)
        if action:
            self.promotions.append(action)

        return action

    def _create_promotion_action(
        self,
        entry: PromotionQueueEntry,
        timestamp: str,
        rollback_token: str,
    ) -> PromotionAction | None:
        """Create bounded promotion action from approved entry."""
        proposal = entry.original_proposal

        # Determine what to actually change (bounded scope)
        if not entry.affected_targets:
            return None

        target = entry.affected_targets[0]  # Primary target

        # Get old/new values based on target type
        old_value, new_value = self._determine_change_values(target, proposal)

        action = PromotionAction(
            action_id=f"PA_{timestamp}_{entry.queue_id}",
            source_proposal_id=entry.proposal_id,
            source_queue_id=entry.queue_id,
            reviewer=entry.reviewer or "unknown",
            target_type=target,
            target_path=f"config/{target}/{proposal.category}",
            old_value=old_value,
            new_value=new_value,
            timestamp=timestamp,
            rationale=entry.rationale or "No rationale provided",
            rollback_token=rollback_token,
            reversible=True,
        )

        return action

    def _determine_change_values(self, target: str, proposal: ProposalPacket) -> tuple[Any, Any]:
        """Determine old and new values for promotion."""
        if target == "threshold_config":
            # Example: tuning threshold based on occurrence count
            old_val = "current_threshold"
            new_val = f"adjusted_threshold_based_on_{proposal.occurrence_count}_occurrences"
        elif target == "reporting_priority":
            old_val = "normal_priority"
            new_val = "elevated_priority"
        elif target == "remediation_wording":
            old_val = "current_wording"
            new_val = proposal.suggested_change[:50]
        else:
            old_val = "unchanged"
            new_val = "unchanged"

        return old_val, new_val

    def reject_proposal(
        self,
        queue_id: str,
        reviewer: str,
        rationale: str,
    ) -> bool:
        """Reject proposal from promotion."""
        entry = next((e for e in self.queue if e.queue_id == queue_id), None)
        if not entry:
            return False

        if not self._is_valid_transition(entry.decision_state, "rejected"):
            return False

        entry.decision_state = "rejected"
        entry.reviewer = reviewer
        entry.rationale = rationale
        entry.timestamp_decided = datetime.now().strftime("%Y%m%d_%H%M%S")

        return True

    def modify_then_approve(
        self,
        queue_id: str,
        reviewer: str,
        modified_suggestion: str,
        rationale: str,
    ) -> PromotionAction | None:
        """Modify proposal then approve."""
        entry = next((e for e in self.queue if e.queue_id == queue_id), None)
        if not entry:
            return None

        if not self._is_valid_transition(entry.decision_state, "modified_then_approved"):
            return None

        # Update proposal with modification
        original = entry.original_proposal
        entry.original_proposal = ProposalPacket(
            proposal_id=original.proposal_id,
            category=original.category,
            trigger_evidence=original.trigger_evidence,
            affected_signals=original.affected_signals,
            affected_layers=original.affected_layers,
            affected_files=original.affected_files,
            suggested_change=modified_suggestion,  # Modified!
            expected_benefit=original.expected_benefit,
            risk_assessment=original.risk_assessment,
            confidence_score=original.confidence_score * 0.9,  # Slightly reduced due to modification
            occurrence_count=original.occurrence_count,
            learning_window_runs=original.learning_window_runs,
            requires_human_review=True,
            promotion_status="modified_then_approved",
        )

        # Update entry
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        entry.decision_state = "modified_then_approved"
        entry.reviewer = reviewer
        entry.rationale = f"[MODIFIED] {rationale}"
        entry.timestamp_decided = timestamp

        rollback_token = f"RB_{timestamp}_{queue_id}"
        entry.rollback_token = rollback_token

        action = self._create_promotion_action(entry, timestamp, rollback_token)
        if action:
            self.promotions.append(action)

        return action

    def rollback_promotion(
        self,
        action_id: str,
        reviewer: str,
        rationale: str,
    ) -> RollbackAction | None:
        """Rollback a previously applied promotion."""
        action = next((a for a in self.promotions if a.action_id == action_id), None)
        if not action:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Find corresponding queue entry
        entry = next((e for e in self.queue if e.queue_id == action.source_queue_id), None)
        if entry:
            entry.decision_state = "rolled_back"

        rollback = RollbackAction(
            rollback_id=f"RBA_{timestamp}_{action_id}",
            source_action_id=action_id,
            source_proposal_id=action.source_proposal_id,
            reviewer=reviewer,
            target_type=action.target_type,
            target_path=action.target_path,
            restored_value=action.old_value,
            timestamp=timestamp,
            rationale=rationale,
        )

        self.rollbacks.append(rollback)
        return rollback

    def emit_promotion_artifacts(self) -> dict[str, Path | None]:
        """Emit all promotion workflow artifacts."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        paths = {}

        # Queue artifact
        if self.queue:
            queue_path = self.output_dir / f"adg_promotion_queue_{timestamp}.json"
            queue_data = {
                "timestamp": timestamp,
                "total_entries": len(self.queue),
                "pending_review": len([e for e in self.queue if e.decision_state == "queued_for_review"]),
                "approved": len([e for e in self.queue if e.decision_state == "approved_for_promotion"]),
                "rejected": len([e for e in self.queue if e.decision_state == "rejected"]),
                "modified_approved": len(
                    [e for e in self.queue if e.decision_state == "modified_then_approved"]
                ),
                "rolled_back": len([e for e in self.queue if e.decision_state == "rolled_back"]),
                "entries": [
                    {
                        "queue_id": e.queue_id,
                        "proposal_id": e.proposal_id,
                        "decision_state": e.decision_state,
                        "reviewer": e.reviewer,
                        "affected_targets": e.affected_targets,
                        "rollback_token": e.rollback_token,
                    }
                    for e in self.queue
                ],
            }
            with open(queue_path, "w", encoding="utf-8") as f:
                json.dump(queue_data, f, indent=2)
            paths["queue"] = queue_path

        # Promotion actions artifact
        if self.promotions:
            promo_path = self.output_dir / f"adg_promotion_actions_{timestamp}.json"
            promo_data = {
                "timestamp": timestamp,
                "total_promotions": len(self.promotions),
                "actions": [
                    {
                        "action_id": a.action_id,
                        "source_proposal_id": a.source_proposal_id,
                        "reviewer": a.reviewer,
                        "target_type": a.target_type,
                        "target_path": a.target_path,
                        "old_value": str(a.old_value),
                        "new_value": str(a.new_value),
                        "rollback_token": a.rollback_token,
                    }
                    for a in self.promotions
                ],
            }
            with open(promo_path, "w", encoding="utf-8") as f:
                json.dump(promo_data, f, indent=2)
            paths["promotions"] = promo_path

        # Rollbacks artifact
        if self.rollbacks:
            rollback_path = self.output_dir / f"adg_rollback_actions_{timestamp}.json"
            rollback_data = {
                "timestamp": timestamp,
                "total_rollbacks": len(self.rollbacks),
                "actions": [
                    {
                        "rollback_id": r.rollback_id,
                        "source_action_id": r.source_action_id,
                        "reviewer": r.reviewer,
                        "target_type": r.target_type,
                        "restored_value": str(r.restored_value),
                    }
                    for r in self.rollbacks
                ],
            }
            with open(rollback_path, "w", encoding="utf-8") as f:
                json.dump(rollback_data, f, indent=2)
            paths["rollbacks"] = rollback_path

        return paths

    def get_pending_reviews(self) -> list[PromotionQueueEntry]:
        """Get all proposals awaiting review."""
        return [e for e in self.queue if e.decision_state == "queued_for_review"]

    def get_audit_trail(self) -> list[dict]:
        """Get complete audit trail of all decisions."""
        trail = []

        for entry in tqdm(self.queue, desc="Processing", unit="item"):
            trail.append(
                {
                    "type": "queue_entry",
                    "queue_id": entry.queue_id,
                    "proposal_id": entry.proposal_id,
                    "state": entry.decision_state,
                    "reviewer": entry.reviewer,
                    "timestamp_queued": entry.timestamp_queued,
                    "timestamp_decided": entry.timestamp_decided,
                    "rationale": entry.rationale,
                }
            )

        for action in self.promotions:
            trail.append(
                {
                    "type": "promotion",
                    "action_id": action.action_id,
                    "reviewer": action.reviewer,
                    "target": action.target_path,
                    "timestamp": action.timestamp,
                }
            )

        for rollback in self.rollbacks:
            trail.append(
                {
                    "type": "rollback",
                    "rollback_id": rollback.rollback_id,
                    "source_action": rollback.source_action_id,
                    "reviewer": rollback.reviewer,
                    "timestamp": rollback.timestamp,
                }
            )

        return trail


class AcceptedBaselineManager:
    """Prompt 12: Explicit accepted baseline management.

    Replaces "most recent artifact" heuristic with governance-grade
    explicit baseline acceptance workflow.
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.active_state = self._load_active_state()

    def _load_active_state(self) -> ActiveState:
        """Load current active state from artifact if exists."""
        state_artifacts = sorted(self.output_dir.glob("adg_active_state_*.json"))
        if state_artifacts:
            try:
                with open(state_artifacts[-1], encoding="utf-8") as f:
                    data = json.load(f)
                    return ActiveState(
                        active_baseline_id=data.get("active_baseline_id"),
                        active_promotion_set_id=data.get("active_promotion_set_id"),
                        applied_promotion_ids=data.get("applied_promotion_ids", []),
                        last_applied_at=data.get("last_applied_at"),
                        last_updated_by=data.get("last_updated_by"),
                    )
            except (json.JSONDecodeError, OSError):
                pass

        return ActiveState(None, None, [], None, None)

    def _load_accepted_baselines(self) -> list[AcceptedBaseline]:
        """Load all accepted baseline records."""
        baseline_artifacts = sorted(self.output_dir.glob("adg_accepted_baseline_*.json"))
        baselines = []

        for artifact_path in tqdm(baseline_artifacts, desc="Processing", unit="item"):
            try:
                with open(artifact_path, encoding="utf-8") as f:
                    data = json.load(f)
                    baselines.append(
                        AcceptedBaseline(
                            baseline_id=data["baseline_id"],
                            source_run_artifact=data["source_run_artifact"],
                            accepted_by=data["accepted_by"],
                            accepted_at=data["accepted_at"],
                            rationale=data["rationale"],
                            active=data["active"],
                            metadata=data.get("metadata", {}),
                        )
                    )
            except (json.JSONDecodeError, KeyError, OSError):
                continue

        return baselines

    def get_active_baseline(self) -> AcceptedBaseline | None:
        """Get currently active accepted baseline."""
        if not self.active_state.active_baseline_id:
            return None

        baselines = self._load_accepted_baselines()
        for baseline in baselines:
            if baseline.baseline_id == self.active_state.active_baseline_id and baseline.active:
                return baseline

        return None

    def get_accepted_baseline_artifact_path(self) -> Path | None:
        """Get path to accepted baseline source artifact (for delta tracking)."""
        active_baseline = self.get_active_baseline()
        if not active_baseline:
            return None

        source_path = Path(active_baseline.source_run_artifact)
        if source_path.exists():
            return source_path

        # Fallback: try relative to output_dir
        alt_path = self.output_dir / source_path.name
        if alt_path.exists():
            return alt_path

        return None

    def accept_baseline(
        self,
        source_artifact_path: Path,
        accepted_by: str,
        rationale: str,
    ) -> AcceptedBaseline:
        """Accept a run artifact as the new active baseline."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        baseline_id = f"BL_{timestamp}_{source_artifact_path.stem}"

        # Deactivate previous baseline
        self._deactivate_current_baseline()

        # Create new accepted baseline
        baseline = AcceptedBaseline(
            baseline_id=baseline_id,
            source_run_artifact=str(source_artifact_path),
            accepted_by=accepted_by,
            accepted_at=timestamp,
            rationale=rationale,
            active=True,
            metadata={
                "previous_baseline_id": self.active_state.active_baseline_id,
                "acceptance_context": "explicit_governance_review",
            },
        )

        # Update active state
        self.active_state.active_baseline_id = baseline_id
        self.active_state.last_applied_at = timestamp
        self.active_state.last_updated_by = accepted_by

        # Persist
        self._emit_baseline_artifact(baseline)
        self._emit_active_state()

        return baseline

    def _deactivate_current_baseline(self) -> None:
        """Deactivate currently active baseline."""
        if not self.active_state.active_baseline_id:
            return

        # Reload and update all baseline artifacts
        baselines = self._load_accepted_baselines()
        for baseline in baselines:
            if baseline.baseline_id == self.active_state.active_baseline_id:
                baseline.active = False
                self._emit_baseline_artifact(baseline)

    def _emit_baseline_artifact(self, baseline: AcceptedBaseline) -> Path:
        """Emit accepted baseline artifact."""
        artifact_path = self.output_dir / f"adg_accepted_baseline_{baseline.baseline_id}.json"

        data = {
            "baseline_id": baseline.baseline_id,
            "source_run_artifact": baseline.source_run_artifact,
            "accepted_by": baseline.accepted_by,
            "accepted_at": baseline.accepted_at,
            "rationale": baseline.rationale,
            "active": baseline.active,
            "metadata": baseline.metadata,
        }

        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return artifact_path

    def _emit_active_state(self) -> Path:
        """Emit active state pointer artifact."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifact_path = self.output_dir / f"adg_active_state_{timestamp}.json"

        data = {
            "timestamp": timestamp,
            "active_baseline_id": self.active_state.active_baseline_id,
            "active_promotion_set_id": self.active_state.active_promotion_set_id,
            "applied_promotion_ids": self.active_state.applied_promotion_ids,
            "last_applied_at": self.active_state.last_applied_at,
            "last_updated_by": self.active_state.last_updated_by,
        }

        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return artifact_path

    def get_baseline_summary(self) -> dict[str, Any]:
        """Get summary of baseline state for reporting."""
        active = self.get_active_baseline()
        all_baselines = self._load_accepted_baselines()

        return {
            "has_accepted_baseline": active is not None,
            "active_baseline_id": active.baseline_id if active else None,
            "active_baseline_accepted_by": active.accepted_by if active else None,
            "active_baseline_accepted_at": active.accepted_at if active else None,
            "total_historical_baselines": len(all_baselines),
        }


class GovernedPromotionApplicator:
    """Prompt 12: Governed application of approved promotions to live state.

    Ensures only explicitly approved promotions can affect live ADG behavior,
    with full attribution and reversibility.
    """

    ALLOWED_TARGET_TYPES = {
        "threshold_config",
        "reporting_priority",
        "remediation_wording",
        "caveat_wording",
        "policy_metadata",
    }

    def __init__(self, output_dir: Path, baseline_manager: AcceptedBaselineManager):
        self.output_dir = output_dir
        self.baseline_manager = baseline_manager
        self.applications: list[PromotionApplication] = []
        self._load_existing_applications()

    def _load_existing_applications(self) -> None:
        """Load previously applied promotions."""
        app_artifacts = sorted(self.output_dir.glob("adg_promotion_application_*.json"))

        for artifact_path in tqdm(app_artifacts, desc="Processing", unit="item"):
            try:
                with open(artifact_path, encoding="utf-8") as f:
                    data = json.load(f)
                    # Artifacts are saved as individual objects, not wrapped in a list
                    if "application_id" in data:
                        self.applications.append(
                            PromotionApplication(
                                application_id=data["application_id"],
                                source_promotion_action_id=data["source_promotion_action_id"],
                                target_type=data["target_type"],
                                target_path=data["target_path"],
                                old_value=data["old_value"],
                                new_value=data["new_value"],
                                applied_by=data["applied_by"],
                                applied_at=data["timestamp"],  # Timestamp field is applied_at
                                rationale=data["rationale"],
                                rollback_token=data["rollback_token"],
                                active=data["active"],
                            )
                        )
            except (json.JSONDecodeError, KeyError, OSError):
                continue

    def apply_promotion(
        self,
        promotion_action: PromotionAction,
        applied_by: str,
        rationale: str,
    ) -> PromotionApplication | None:
        """Apply an approved promotion to live state.

        Creates application artifact with full attribution.
        """
        # Validate target type is allowed
        if promotion_action.target_type not in self.ALLOWED_TARGET_TYPES:
            return None

        # Prevent re-application of already-applied promotions
        existing = next(
            (
                a
                for a in self.applications
                if a.source_promotion_action_id == promotion_action.action_id and a.active
            ),
            None,
        )
        if existing:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        application_id = f"APP_{timestamp}_{promotion_action.action_id}"
        rollback_token = f"RBAPP_{timestamp}_{application_id}"

        application = PromotionApplication(
            application_id=application_id,
            source_promotion_action_id=promotion_action.action_id,
            target_type=promotion_action.target_type,
            target_path=promotion_action.target_path,
            old_value=promotion_action.old_value,
            new_value=promotion_action.new_value,
            applied_by=applied_by,
            applied_at=timestamp,
            rationale=rationale,
            rollback_token=rollback_token,
            active=True,
        )

        self.applications.append(application)

        # Update active state
        self.baseline_manager.active_state.applied_promotion_ids.append(application_id)
        self.baseline_manager.active_state.active_promotion_set_id = f"SET_{timestamp}"
        self.baseline_manager.active_state.last_applied_at = timestamp
        self.baseline_manager.active_state.last_updated_by = applied_by

        # Persist
        self._emit_application_artifact(application)
        self.baseline_manager._emit_active_state()

        return application

    def _emit_application_artifact(self, application: PromotionApplication) -> Path:
        """Emit promotion application artifact."""
        artifact_path = self.output_dir / f"adg_promotion_application_{application.application_id}.json"

        data = {
            "timestamp": application.applied_at,
            "application_id": application.application_id,
            "source_promotion_action_id": application.source_promotion_action_id,
            "target_type": application.target_type,
            "target_path": application.target_path,
            "old_value": str(application.old_value),
            "new_value": str(application.new_value),
            "applied_by": application.applied_by,
            "rationale": application.rationale,
            "rollback_token": application.rollback_token,
            "active": application.active,
        }

        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return artifact_path

    def rollback_application(
        self,
        application_id: str,
        rolled_back_by: str,
        rationale: str,
    ) -> dict[str, Any] | None:
        """Rollback an applied promotion."""
        application = next((a for a in self.applications if a.application_id == application_id), None)
        if not application or not application.active:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Mark application as inactive
        application.active = False

        # Remove from active state
        if application_id in self.baseline_manager.active_state.applied_promotion_ids:
            self.baseline_manager.active_state.applied_promotion_ids.remove(application_id)

        # Update active state
        self.baseline_manager.active_state.last_applied_at = timestamp
        self.baseline_manager.active_state.last_updated_by = rolled_back_by

        # Create rollback artifact
        rollback_data = {
            "rollback_id": f"RBAPP_{timestamp}_{application_id}",
            "application_id": application_id,
            "source_promotion_action_id": application.source_promotion_action_id,
            "restored_value": str(application.old_value),
            "rolled_back_by": rolled_back_by,
            "rolled_back_at": timestamp,
            "rationale": rationale,
        }

        rollback_path = self.output_dir / f"adg_promotion_rollback_{rollback_data['rollback_id']}.json"
        with open(rollback_path, "w", encoding="utf-8") as f:
            json.dump(rollback_data, f, indent=2)

        # Re-emit updated application artifact
        self._emit_application_artifact(application)
        self.baseline_manager._emit_active_state()

        return rollback_data

    def get_active_applications(self) -> list[PromotionApplication]:
        """Get all currently active (non-rolled-back) applications."""
        return [a for a in self.applications if a.active]

    def get_application_summary(self) -> dict[str, Any]:
        """Get summary of applied promotions for reporting."""
        active = self.get_active_applications()

        return {
            "has_active_promotions": len(active) > 0,
            "active_promotion_count": len(active),
            "active_promotion_set_id": self.baseline_manager.active_state.active_promotion_set_id,
            "applied_promotion_ids": self.baseline_manager.active_state.applied_promotion_ids,
            "last_applied_at": self.baseline_manager.active_state.last_applied_at,
            "last_updated_by": self.baseline_manager.active_state.last_updated_by,
        }


class ADGGovernanceDashboard:
    """Prompt 13: Governance dashboard for ADG graph intelligence workflow.

    Artifact-driven, no new control plane. Aggregates existing governed state
    from baseline, proposal, promotion, rollback, and active-state artifacts.

    Provides operators with unified view of:
    - Active baseline and promotion set
    - Pending review queue
    - Active promotion applications
    - Rollback candidates
    - Audit timeline
    - Health / consistency checks
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.baseline_manager = AcceptedBaselineManager(output_dir)
        self.promotion_manager = ADGProposalPromotionManager(output_dir)

    def generate_dashboard(self) -> dict[str, Any]:
        """Generate comprehensive governance dashboard.

        Aggregates all governed artifacts into unified operator view.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        dashboard = {
            "timestamp": timestamp,
            "dashboard_version": "1.0.0",
            "sections": {
                "active_state": self._get_active_state_view(),
                "pending_queue": self._get_pending_queue_view(),
                "active_promotions": self._get_active_promotions_view(),
                "rollback_candidates": self._get_rollback_candidates_view(),
                "audit_timeline": self._get_audit_timeline_view(),
                "health_summary": self._get_health_summary(),
            },
        }

        return dashboard

    def _get_active_state_view(self) -> dict[str, Any]:
        """A. Active State View - current accepted baseline and promotion set."""
        active_baseline = self.baseline_manager.get_active_baseline()
        baseline_summary = self.baseline_manager.get_baseline_summary()

        # Get active promotions from applicator
        applicator = GovernedPromotionApplicator(self.output_dir, self.baseline_manager)
        app_summary = applicator.get_application_summary()

        return {
            "has_active_baseline": active_baseline is not None,
            "active_baseline_id": active_baseline.baseline_id if active_baseline else None,
            "baseline_accepted_by": active_baseline.accepted_by if active_baseline else None,
            "baseline_accepted_at": active_baseline.accepted_at if active_baseline else None,
            "baseline_rationale": active_baseline.rationale if active_baseline else None,
            "active_promotion_set_id": app_summary.get("active_promotion_set_id"),
            "applied_promotions_count": app_summary.get("active_promotion_count", 0),
            "last_updated_by": self.baseline_manager.active_state.last_updated_by,
            "last_updated_at": self.baseline_manager.active_state.last_applied_at,
        }

    def _get_pending_queue_view(self) -> dict[str, Any]:
        """B. Pending Queue View - proposals awaiting review."""
        pending = self.promotion_manager.get_pending_reviews()

        # Get top pending proposals (bounded)
        top_pending = []
        for entry in tqdm(pending[:5], desc="Processing", unit="item"):  # Max 5 for bounded output
            proposal = entry.original_proposal
            top_pending.append(
                {
                    "queue_id": entry.queue_id,
                    "proposal_id": entry.proposal_id,
                    "category": proposal.category,
                    "confidence_score": proposal.confidence_score,
                    "affected_targets": entry.affected_targets,
                    "queued_at": entry.timestamp_queued,
                }
            )

        return {
            "pending_review_count": len(pending),
            "top_pending_proposals": top_pending,
            "oldest_pending_age_hours": self._calculate_oldest_pending_hours(pending),
        }

    def _calculate_oldest_pending_hours(self, pending: list[PromotionQueueEntry]) -> float | None:
        """Calculate age of oldest pending proposal in hours."""
        if not pending:
            return None

        now = datetime.now()
        oldest = None

        for entry in pending:
            try:
                queued_time = datetime.strptime(entry.timestamp_queued, "%Y%m%d_%H%M%S")
                age_hours = (now - queued_time).total_seconds() / 3600
                if oldest is None or age_hours > oldest:
                    oldest = age_hours
            except ValueError:
                continue

        return round(oldest, 1) if oldest else None

    def _get_active_promotions_view(self) -> dict[str, Any]:
        """C. Active Promotions View - currently applied promotions."""
        applicator = GovernedPromotionApplicator(self.output_dir, self.baseline_manager)
        active_apps = applicator.get_active_applications()

        # Format for display (bounded)
        promotions_display = []
        for app in tqdm(active_apps[:10], desc="Processing", unit="item"):  # Max 10 for bounded output
            promotions_display.append(
                {
                    "application_id": app.application_id,
                    "target_type": app.target_type,
                    "target_path": app.target_path,
                    "old_value": str(app.old_value),
                    "new_value": str(app.new_value),
                    "applied_by": app.applied_by,
                    "applied_at": app.applied_at,
                    "rollback_token": app.rollback_token,
                }
            )

        return {
            "active_count": len(active_apps),
            "active_promotions": promotions_display,
            "target_types_active": list(set(app.target_type for app in active_apps)),
        }

    def _get_rollback_candidates_view(self) -> dict[str, Any]:
        """D. Rollback Candidates View - recent active promotions eligible for rollback."""
        applicator = GovernedPromotionApplicator(self.output_dir, self.baseline_manager)
        active_apps = applicator.get_active_applications()

        # Sort by applied_at descending (most recent first)
        sorted_apps = sorted(
            active_apps,
            key=lambda a: a.applied_at,
            reverse=True,
        )

        # Recent candidates (last 5, applied within last 7 days)
        candidates = []
        now = datetime.now()

        for app in tqdm(sorted_apps[:5], desc="Processing", unit="item"):
            try:
                applied_time = datetime.strptime(app.applied_at, "%Y%m%d_%H%M%S")
                age_days = (now - applied_time).total_seconds() / 86400

                priority = "high" if age_days < 1 else "normal" if age_days < 7 else "low"

                candidates.append(
                    {
                        "application_id": app.application_id,
                        "target_type": app.target_type,
                        "applied_by": app.applied_by,
                        "applied_at": app.applied_at,
                        "age_days": round(age_days, 1),
                        "priority": priority,
                        "rollback_token": app.rollback_token,
                    }
                )
            except ValueError:
                continue

        return {
            "total_rollback_candidates": len(active_apps),
            "recent_candidates": candidates,
            "newest_candidate_age_days": candidates[0]["age_days"] if candidates else None,
        }

    def _get_audit_timeline_view(self) -> dict[str, Any]:
        """E. Audit Timeline View - recent accept/apply/reject/rollback events."""
        events = []

        # Get baseline acceptance events
        baselines = self.baseline_manager._load_accepted_baselines()
        for baseline in baselines:
            events.append(
                {
                    "type": "baseline_acceptance",
                    "actor": baseline.accepted_by,
                    "timestamp": baseline.accepted_at,
                    "entity_id": baseline.baseline_id,
                    "state": "active" if baseline.active else "inactive",
                }
            )

        # Get audit trail from promotion manager (queue decisions)
        trail = self.promotion_manager.get_audit_trail()
        for event in trail:
            events.append(
                {
                    "type": event.get("type", "unknown"),
                    "actor": event.get("reviewer", "unknown"),
                    "timestamp": event.get("timestamp_decided") or event.get("timestamp"),
                    "entity_id": event.get("queue_id") or event.get("action_id") or event.get("rollback_id"),
                    "state": event.get("state"),
                }
            )

        # Get promotion application events from applicator
        applicator = GovernedPromotionApplicator(self.output_dir, self.baseline_manager)
        for app in applicator.applications:
            events.append(
                {
                    "type": "promotion_application",
                    "actor": app.applied_by,
                    "timestamp": app.applied_at,
                    "entity_id": app.application_id,
                    "state": "active" if app.active else "rolled_back",
                }
            )

        # Sort all events by timestamp (most recent first) and bound
        recent_events = sorted(
            events,
            key=lambda e: e.get("timestamp") or "",
            reverse=True,
        )[:20]

        return {
            "total_events_tracked": len(events),
            "recent_events": recent_events,
            "event_types_recent": list(set(e["type"] for e in recent_events)),
        }

    def _get_health_summary(self) -> dict[str, Any]:
        """F. Health / Consistency Summary - validate governed state integrity."""
        issues = []
        checks = {}

        # Check 1: Exactly one active baseline
        active_baselines = [b for b in self.baseline_manager._load_accepted_baselines() if b.active]
        checks["exactly_one_active_baseline"] = len(active_baselines) == 1
        if len(active_baselines) != 1:
            issues.append(f"Expected 1 active baseline, found {len(active_baselines)}")

        # Check 2: No orphaned promotion applications
        applicator = GovernedPromotionApplicator(self.output_dir, self.baseline_manager)
        active_apps = applicator.get_active_applications()

        # All active apps should reference valid promotion actions
        orphaned = []
        for app in active_apps:
            # Check if source action exists in promotion manager
            source_action_exists = any(
                a.action_id == app.source_promotion_action_id for a in self.promotion_manager.promotions
            )
            if not source_action_exists:
                orphaned.append(app.application_id)

        checks["no_orphaned_promotions"] = len(orphaned) == 0
        if orphaned:
            issues.append(f"Found {len(orphaned)} orphaned promotion applications")

        # Check 3: No queue entries missing decisions (stuck in queued_for_review too long)
        pending = self.promotion_manager.get_pending_reviews()
        stale_pending = []
        now = datetime.now()

        for entry in pending:
            try:
                queued_time = datetime.strptime(entry.timestamp_queued, "%Y%m%d_%H%M%S")
                age_days = (now - queued_time).total_seconds() / 86400
                if age_days > 30:  # Stale after 30 days
                    stale_pending.append(entry.queue_id)
            except ValueError:
                continue

        checks["no_stale_queue_entries"] = len(stale_pending) == 0
        if stale_pending:
            issues.append(f"Found {len(stale_pending)} stale queue entries (>30 days)")

        # Check 4: Rollback token consistency
        token_mismatches = []
        for app in tqdm(active_apps, desc="Processing", unit="item"):
            # Find corresponding promotion action
            action = next(
                (
                    a
                    for a in self.promotion_manager.promotions
                    if a.action_id == app.source_promotion_action_id
                ),
                None,
            )
            if action and action.rollback_token != app.rollback_token:
                token_mismatches.append(app.application_id)

        checks["rollback_token_consistency"] = len(token_mismatches) == 0
        if token_mismatches:
            issues.append(f"Found {len(token_mismatches)} rollback token mismatches")

        # Overall health score
        health_score = sum(checks.values()) / len(checks) if checks else 1.0

        return {
            "health_score": round(health_score, 2),
            "all_checks_pass": len(issues) == 0,
            "checks": checks,
            "issues": issues[:10],  # Bounded
            "issue_count": len(issues),
        }

    def emit_dashboard_artifact(self) -> Path:
        """Emit dashboard as JSON artifact."""
        dashboard = self.generate_dashboard()
        timestamp = dashboard["timestamp"]
        artifact_path = self.output_dir / f"adg_governance_dashboard_{timestamp}.json"

        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(dashboard, f, indent=2)

        return artifact_path

    def generate_textual_summary(self, max_lines: int = 50) -> str:
        """Generate bounded textual summary for operators.

        Integrates with normal ADG reporting (E11 section).
        """
        dashboard = self.generate_dashboard()
        sections = dashboard["sections"]

        lines = [
            "",
            "╔══════════════════════════════════════════════════════════════╗",
            "║     ADG GOVERNANCE DASHBOARD (Prompt 13)                     ║",
            "╚══════════════════════════════════════════════════════════════╝",
            "",
            f"Dashboard generated: {dashboard['timestamp']}",
            "",
        ]

        # A. Active State
        active = sections["active_state"]
        lines.extend(
            [
                "[ACTIVE STATE]",
                f"  Baseline: {active['active_baseline_id'] or 'NONE'}",
            ]
        )
        if active["has_active_baseline"]:
            lines.append(
                f"    Accepted by: {active['baseline_accepted_by']} at {active['baseline_accepted_at']}"
            )
        lines.extend(
            [
                f"  Promotions: {active['applied_promotions_count']} active in set {active['active_promotion_set_id'] or 'NONE'}",
                f"  Last updated: {active['last_updated_by'] or 'N/A'} at {active['last_updated_at'] or 'N/A'}",
                "",
            ]
        )

        # B. Pending Queue
        pending = sections["pending_queue"]
        lines.extend(
            [
                "[PENDING REVIEW]",
                f"  Items awaiting review: {pending['pending_review_count']}",
            ]
        )
        if pending["oldest_pending_age_hours"]:
            lines.append(f"  Oldest pending: {pending['oldest_pending_age_hours']} hours")
        for item in pending["top_pending_proposals"]:
            lines.append(
                f"    - {item['proposal_id']}: {item['category']} (conf: {item['confidence_score']:.2f})"
            )
        lines.append("")

        # C. Active Promotions
        promotions = sections["active_promotions"]
        lines.extend(
            [
                "[ACTIVE PROMOTIONS]",
                f"  Total active: {promotions['active_count']}",
            ]
        )
        for promo in promotions["active_promotions"][:5]:  # Bounded
            lines.append(f"    - {promo['target_type']}: {promo['old_value']} → {promo['new_value']}")
        lines.append("")

        # D. Rollback Candidates
        rollback = sections["rollback_candidates"]
        lines.extend(
            [
                "[ROLLBACK CANDIDATES]",
                f"  Candidates available: {rollback['total_rollback_candidates']}",
            ]
        )
        for cand in rollback["recent_candidates"][:3]:  # Bounded
            lines.append(f"    - {cand['application_id']} ({cand['age_days']}d, {cand['priority']} priority)")
        lines.append("")

        # E. Health Summary
        health = sections["health_summary"]
        lines.extend(
            [
                "[HEALTH CHECK]",
                f"  Score: {health['health_score']:.0%}",
                f"  Status: {'HEALTHY' if health['all_checks_pass'] else 'ISSUES DETECTED'}",
            ]
        )
        if health["issues"]:
            lines.append("  Issues:")
            for issue in health["issues"][:5]:  # Bounded
                lines.append(f"    ⚠ {issue}")
        lines.append("")

        # Enforce line limit
        if len(lines) > max_lines:
            lines = lines[: max_lines - 2]
            lines.append("  ... (output bounded)")
            lines.append("")

        return "\n".join(lines)


class ADGPolicyReviewPack:
    """Prompt 14: Policy-tuning review pack for systematic governance review.

    Bounded, quarterly-style, no live mutation.
    Aggregates historical governance artifacts over defined window
    to surface policy-tuning questions for human review.

    Core principle: Generate review artifacts only.
    Never directly tune policy, update thresholds, or promote changes.
    """

    def __init__(self, output_dir: Path, review_window_days: int = 90):
        self.output_dir = output_dir
        self.review_window_days = review_window_days
        self.baseline_manager = AcceptedBaselineManager(output_dir)
        self.promotion_manager = ADGProposalPromotionManager(output_dir)
        self.dashboard = ADGGovernanceDashboard(output_dir)

    def generate_review_pack(self) -> dict[str, Any]:
        """Generate comprehensive policy-tuning review pack.

        Non-binding recommendations only.
        All output attributable and explicitly non-live-mutating.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        review_pack_id = f"RP_{timestamp}_{self.review_window_days}d"

        # Calculate review window boundaries
        window_end = datetime.now()
        window_start = window_end - timedelta(days=self.review_window_days)

        review_pack = {
            "review_pack_id": review_pack_id,
            "timestamp": timestamp,
            "review_pack_version": "1.0.0",
            "requires_human_review": True,
            "live_mutation": False,
            "review_window": {
                "days": self.review_window_days,
                "start_date": window_start.strftime("%Y%m%d_%H%M%S"),
                "end_date": window_end.strftime("%Y%m%d_%H%M%S"),
            },
            "source_artifacts": self._collect_source_artifacts(window_start, window_end),
            "sections": {
                "window_summary": self._get_window_summary(window_start, window_end),
                "hotspot_patterns": self._get_hotspot_pattern_summary(window_start, window_end),
                "proposal_summary": self._get_proposal_summary(window_start, window_end),
                "promotion_rollback_summary": self._get_promotion_rollback_summary(window_start, window_end),
                "policy_tuning_questions": self._get_policy_tuning_questions(),
                "non_binding_recommendations": self._get_non_binding_recommendations(),
            },
            "aggregate_metrics": self._compute_aggregate_metrics(window_start, window_end),
            "confidence_notes": self._get_confidence_notes(),
        }

        return review_pack

    def _collect_source_artifacts(self, window_start: datetime, window_end: datetime) -> dict[str, list[str]]:
        """Collect list of source artifacts included in review window."""
        artifacts = {
            "accepted_baselines": [],
            "promotion_applications": [],
            "promotion_rollbacks": [],
            "shadow_proposals": [],
            "governance_dashboards": [],
        }

        # Collect accepted baselines within window
        for baseline in self.baseline_manager._load_accepted_baselines():
            try:
                baseline_time = datetime.strptime(baseline.accepted_at, "%Y%m%d_%H%M%S")
                if window_start <= baseline_time <= window_end:
                    artifacts["accepted_baselines"].append(baseline.baseline_id)
            except ValueError:
                continue

        # Collect promotion applications within window
        applicator = GovernedPromotionApplicator(self.output_dir, self.baseline_manager)
        for app in applicator.applications:
            try:
                app_time = datetime.strptime(app.applied_at, "%Y%m%d_%H%M%S")
                if window_start <= app_time <= window_end:
                    artifacts["promotion_applications"].append(app.application_id)
            except ValueError:
                continue

        # Collect rollback artifacts within window
        rollback_artifacts = sorted(self.output_dir.glob("adg_promotion_rollback_*.json"))
        for artifact_path in tqdm(rollback_artifacts, desc="Processing", unit="item"):
            try:
                with open(artifact_path, encoding="utf-8") as f:
                    data = json.load(f)
                    rollback_time = datetime.strptime(
                        data.get("rolled_back_at", "19700101_000000"), "%Y%m%d_%H%M%S"
                    )
                    if window_start <= rollback_time <= window_end:
                        artifacts["promotion_rollbacks"].append(data.get("rollback_id", str(artifact_path)))
            except (ValueError, json.JSONDecodeError, OSError):
                continue

        # Collect shadow proposals within window
        for entry in self.promotion_manager.queue:
            try:
                queued_time = datetime.strptime(entry.timestamp_queued, "%Y%m%d_%H%M%S")
                if window_start <= queued_time <= window_end:
                    artifacts["shadow_proposals"].append(entry.proposal_id)
            except ValueError:
                continue

        return artifacts

    def _get_window_summary(self, window_start: datetime, window_end: datetime) -> dict[str, Any]:
        """A. Window Summary - overview of review period."""
        # Count accepted baselines in window
        baselines_in_window = 0
        for baseline in self.baseline_manager._load_accepted_baselines():
            try:
                baseline_time = datetime.strptime(baseline.accepted_at, "%Y%m%d_%H%M%S")
                if window_start <= baseline_time <= window_end:
                    baselines_in_window += 1
            except ValueError:
                continue

        # Count promotions applied in window
        applicator = GovernedPromotionApplicator(self.output_dir, self.baseline_manager)
        promotions_in_window = 0
        for app in applicator.applications:
            try:
                app_time = datetime.strptime(app.applied_at, "%Y%m%d_%H%M%S")
                if window_start <= app_time <= window_end:
                    promotions_in_window += 1
            except ValueError:
                continue

        # Count rollbacks in window
        rollbacks_in_window = 0
        rollback_artifacts = sorted(self.output_dir.glob("adg_promotion_rollback_*.json"))
        for artifact_path in tqdm(rollback_artifacts, desc="Processing", unit="item"):
            try:
                with open(artifact_path, encoding="utf-8") as f:
                    data = json.load(f)
                    rollback_time = datetime.strptime(
                        data.get("rolled_back_at", "19700101_000000"), "%Y%m%d_%H%M%S"
                    )
                    if window_start <= rollback_time <= window_end:
                        rollbacks_in_window += 1
            except (ValueError, json.JSONDecodeError, OSError):
                continue

        return {
            "runs_analyzed": "N/A",  # Would need run tracking
            "accepted_baselines_included": baselines_in_window,
            "promotions_applied": promotions_in_window,
            "rollbacks_observed": rollbacks_in_window,
            "review_window_days": self.review_window_days,
            "data_completeness": "partial" if baselines_in_window == 0 else "adequate",
        }

    def _get_hotspot_pattern_summary(self, window_start: datetime, window_end: datetime) -> dict[str, Any]:
        """B. Hotspot Pattern Summary - repeat offenders and persistent anomalies."""
        # Aggregate patterns from shadow proposals in window
        pattern_frequency: dict[str, int] = {}
        layer_regression_frequency: dict[str, int] = {}
        signal_type_frequency: dict[str, int] = {}

        for entry in tqdm(self.promotion_manager.queue, desc="Processing", unit="item"):
            try:
                queued_time = datetime.strptime(entry.timestamp_queued, "%Y%m%d_%H%M%S")
                if not (window_start <= queued_time <= window_end):
                    continue

                proposal = entry.original_proposal

                # Count by category
                pattern_frequency[proposal.category] = pattern_frequency.get(proposal.category, 0) + 1

                # Count by affected layer
                for layer in proposal.affected_layers:
                    layer_regression_frequency[layer] = layer_regression_frequency.get(layer, 0) + 1

                # Count by affected signal
                for signal in proposal.affected_signals:
                    signal_type_frequency[signal] = signal_type_frequency.get(signal, 0) + 1

            except ValueError:
                continue

        # Get top repeat offenders
        repeat_offenders = sorted(
            [(k, v) for k, v in pattern_frequency.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:5]

        # Most frequent protected-layer regressions
        protected_regressions = sorted(
            [(k, v) for k, v in layer_regression_frequency.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:3]

        # Most persistent graph anomaly types
        persistent_anomalies = sorted(
            [(k, v) for k, v in signal_type_frequency.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:3]

        return {
            "repeat_offenders": [{"pattern": p, "count": c} for p, c in repeat_offenders],
            "protected_layer_regressions": [{"layer": l, "count": c} for l, c in protected_regressions],
            "persistent_graph_anomalies": [{"signal": s, "count": c} for s, c in persistent_anomalies],
            "unique_pattern_types": len(pattern_frequency),
            "total_proposals_analyzed": sum(pattern_frequency.values()),
        }

    def _get_proposal_summary(self, window_start: datetime, window_end: datetime) -> dict[str, Any]:
        """C. Proposal Summary - proposal category frequency and approval rates."""
        category_counts: dict[str, int] = {}
        high_confidence_count = 0
        approved_count = 0
        pending_count = 0
        never_approved_count = 0

        for entry in tqdm(self.promotion_manager.queue, desc="Processing", unit="item"):
            try:
                queued_time = datetime.strptime(entry.timestamp_queued, "%Y%m%d_%H%M%S")
                if not (window_start <= queued_time <= window_end):
                    continue

                proposal = entry.original_proposal

                # Count by category
                category_counts[proposal.category] = category_counts.get(proposal.category, 0) + 1

                # High confidence proposals
                if proposal.confidence_score >= 0.8:
                    high_confidence_count += 1

                # Track decision states
                if entry.decision_state == "approved_for_promotion":
                    approved_count += 1
                elif entry.decision_state == "queued_for_review":
                    pending_count += 1
                elif entry.decision_state in ["rejected", "shadow_only"]:
                    never_approved_count += 1

            except ValueError:
                continue

        # Sort categories by frequency
        sorted_categories = sorted(
            [{"category": k, "count": v} for k, v in category_counts.items()],
            key=lambda x: x["count"],
            reverse=True,
        )

        return {
            "proposal_counts_by_category": sorted_categories[:10],  # Bounded
            "high_confidence_proposals": high_confidence_count,
            "proposals_approved": approved_count,
            "proposals_pending": pending_count,
            "proposals_never_approved": never_approved_count,
            "approval_rate": approved_count / (approved_count + never_approved_count)
            if (approved_count + never_approved_count) > 0
            else 0,
        }

    def _get_promotion_rollback_summary(self, window_start: datetime, window_end: datetime) -> dict[str, Any]:
        """D. Promotion / Rollback Summary - targets used, rollback rates, churn."""
        target_type_frequency: dict[str, int] = {}
        target_type_rollbacks: dict[str, int] = {}

        applicator = GovernedPromotionApplicator(self.output_dir, self.baseline_manager)

        # Track promotions in window
        for app in applicator.applications:
            try:
                app_time = datetime.strptime(app.applied_at, "%Y%m%d_%H%M%S")
                if window_start <= app_time <= window_end:
                    target_type_frequency[app.target_type] = target_type_frequency.get(app.target_type, 0) + 1
            except ValueError:
                continue

        # Track rollbacks in window
        rollback_artifacts = sorted(self.output_dir.glob("adg_promotion_rollback_*.json"))
        for artifact_path in tqdm(rollback_artifacts, desc="Processing", unit="item"):
            try:
                with open(artifact_path, encoding="utf-8") as f:
                    data = json.load(f)
                    rollback_time = datetime.strptime(
                        data.get("rolled_back_at", "19700101_000000"), "%Y%m%d_%H%M%S"
                    )
                    if window_start <= rollback_time <= window_end:
                        target_type = data.get("target_type", "unknown")
                        target_type_rollbacks[target_type] = target_type_rollbacks.get(target_type, 0) + 1
            except (ValueError, json.JSONDecodeError, OSError):
                continue

        # Calculate rollback rates
        rollback_rates = []
        for target_type, promotion_count in tqdm(
            target_type_frequency.items(), desc="Processing", unit="item"
        ):
            rollback_count = target_type_rollbacks.get(target_type, 0)
            rate = rollback_count / promotion_count if promotion_count > 0 else 0
            rollback_rates.append(
                {
                    "target_type": target_type,
                    "promotions": promotion_count,
                    "rollbacks": rollback_count,
                    "rollback_rate": round(rate, 2),
                }
            )

        # Sort by promotion frequency
        sorted_targets = sorted(rollback_rates, key=lambda x: x["promotions"], reverse=True)[:5]

        # Churn indicator: high rollback rate overall
        total_promotions = sum(target_type_frequency.values())
        total_rollbacks = sum(target_type_rollbacks.values())
        overall_rollback_rate = total_rollbacks / total_promotions if total_promotions > 0 else 0

        return {
            "most_used_promotion_targets": sorted_targets,
            "total_promotions_in_window": total_promotions,
            "total_rollbacks_in_window": total_rollbacks,
            "overall_rollback_rate": round(overall_rollback_rate, 2),
            "churn_indicator": "high"
            if overall_rollback_rate > 0.3
            else "moderate"
            if overall_rollback_rate > 0.1
            else "low",
        }

    def _get_policy_tuning_questions(self) -> list[dict[str, Any]]:
        """E. Policy-Tuning Questions - candidate questions for human review."""
        questions = []

        # Get current dashboard for context
        dashboard = self.dashboard.generate_dashboard()
        sections = dashboard["sections"]

        # Question 1: Fail threshold revisit
        hotspot_summary = sections.get("hotspot_patterns", {})
        repeat_offenders = hotspot_summary.get("repeat_offenders", [])
        if len(repeat_offenders) > 0 and repeat_offenders[0].get("count", 0) > 5:
            questions.append(
                {
                    "question": "Should fail threshold be revisited?",
                    "trigger": f"High frequency pattern: {repeat_offenders[0].get('pattern')} observed {repeat_offenders[0].get('count')} times",
                    "evidence_reference": f"Pattern {repeat_offenders[0].get('pattern')}",
                    "priority": "high" if repeat_offenders[0].get("count", 0) > 10 else "medium",
                }
            )

        # Question 2: Reporting priority ordering
        proposal_summary = sections.get("proposal_summary", {})
        category_counts = proposal_summary.get("proposal_counts_by_category", [])
        if len(category_counts) > 0:
            top_category = category_counts[0]
            if top_category.get("count", 0) > 3:
                questions.append(
                    {
                        "question": "Should reporting priority ordering change?",
                        "trigger": f"Dominant proposal category: {top_category.get('category')} ({top_category.get('count')} proposals)",
                        "evidence_reference": f"Category {top_category.get('category')}",
                        "priority": "medium",
                    }
                )

        # Question 3: Noisy proposal types
        never_approved = proposal_summary.get("proposals_never_approved", 0)
        total_proposals = proposal_summary.get("total_proposals_analyzed", 1)
        rejection_rate = never_approved / total_proposals if total_proposals > 0 else 0
        if rejection_rate > 0.5:
            questions.append(
                {
                    "question": "Are certain proposal types too noisy?",
                    "trigger": f"High rejection rate: {rejection_rate:.0%} of proposals never approved",
                    "evidence_reference": f"Rejection rate {rejection_rate:.0%}",
                    "priority": "medium",
                }
            )

        # Question 4: Caveat staleness
        health = sections.get("health_summary", {})
        if not health.get("all_checks_pass", True):
            questions.append(
                {
                    "question": "Are caveats misleading or stale?",
                    "trigger": "Health check issues detected",
                    "evidence_reference": f"Health issues: {health.get('issue_count', 0)}",
                    "priority": "high" if health.get("issue_count", 0) > 2 else "medium",
                }
            )

        # Question 5: Rollback pattern
        rollback_summary = self._get_promotion_rollback_summary(
            datetime.now() - timedelta(days=self.review_window_days), datetime.now()
        )
        if rollback_summary.get("overall_rollback_rate", 0) > 0.3:
            questions.append(
                {
                    "question": "Should promotion criteria be tightened?",
                    "trigger": f"High rollback rate: {rollback_summary.get('overall_rollback_rate', 0):.0%}",
                    "evidence_reference": f"Rollback rate {rollback_summary.get('overall_rollback_rate', 0):.0%}",
                    "priority": "high",
                }
            )

        return sorted(questions, key=lambda q: q.get("priority", "low"), reverse=True)[:5]  # Bounded

    def _get_non_binding_recommendations(self) -> list[dict[str, Any]]:
        """F. Non-Binding Recommendations - explicit suggestions for review only."""
        recommendations = []

        # Get window data
        window_end = datetime.now()
        window_start = window_end - timedelta(days=self.review_window_days)

        # Recommendation 1: Threshold review
        proposal_summary = self._get_proposal_summary(window_start, window_end)
        high_confidence = proposal_summary.get("high_confidence_proposals", 0)
        if high_confidence > 5:
            recommendations.append(
                {
                    "recommendation": "Consider reviewing threshold configurations for high-confidence proposal types",
                    "confidence": 0.7,
                    "evidence_references": [f"{high_confidence} high-confidence proposals in window"],
                    "non_binding": True,
                    "requires_human_review": True,
                }
            )

        # Recommendation 2: Policy consolidation
        hotspot_summary = self._get_hotspot_pattern_summary(window_start, window_end)
        unique_patterns = hotspot_summary.get("unique_pattern_types", 0)
        if unique_patterns > 10:
            recommendations.append(
                {
                    "recommendation": "Consider consolidating similar policy categories to reduce complexity",
                    "confidence": 0.6,
                    "evidence_references": [f"{unique_patterns} unique pattern types detected"],
                    "non_binding": True,
                    "requires_human_review": True,
                }
            )

        # Recommendation 3: Promotion policy review
        rollback_summary = self._get_promotion_rollback_summary(window_start, window_end)
        if rollback_summary.get("churn_indicator") == "high":
            recommendations.append(
                {
                    "recommendation": "Review promotion approval criteria due to high rollback rate",
                    "confidence": 0.8,
                    "evidence_references": [
                        f"Rollback rate: {rollback_summary.get('overall_rollback_rate', 0):.0%}"
                    ],
                    "non_binding": True,
                    "requires_human_review": True,
                }
            )

        # Recommendation 4: Baseline review cadence
        window_summary = self._get_window_summary(window_start, window_end)
        baselines_in_window = window_summary.get("accepted_baselines_included", 0)
        if baselines_in_window > 10:
            recommendations.append(
                {
                    "recommendation": "Consider whether baseline acceptance cadence is appropriate",
                    "confidence": 0.5,
                    "evidence_references": [
                        f"{baselines_in_window} baselines accepted in {self.review_window_days} days"
                    ],
                    "non_binding": True,
                    "requires_human_review": True,
                }
            )

        return recommendations[:5]  # Bounded

    def _compute_aggregate_metrics(self, window_start: datetime, window_end: datetime) -> dict[str, Any]:
        """Compute aggregate metrics for the review window."""
        return {
            "governance_velocity": {
                "proposals_per_day": 0,  # Would need accurate day counting
                "promotions_per_baseline": 0,  # Would need cross-referencing
            },
            "quality_indicators": {
                "high_confidence_proposal_rate": 0,
                "approval_rate": 0,
                "rollback_rate": 0,
            },
            "trend_indicators": {
                "increasing_pattern_frequency": [],
                "decreasing_pattern_frequency": [],
            },
        }

    def _get_confidence_notes(self) -> list[str]:
        """Provide confidence notes about the review pack."""
        return [
            "Review pack aggregates historical artifacts only.",
            "Metrics are indicative, not prescriptive.",
            "All recommendations require human validation before action.",
            "Policy tuning should follow established governance procedures.",
            "No automatic threshold updates or live mutations are performed.",
        ]

    def emit_review_pack_artifact(self) -> Path:
        """Emit review pack as JSON artifact."""
        review_pack = self.generate_review_pack()
        review_pack_id = review_pack["review_pack_id"]
        artifact_path = self.output_dir / f"adg_policy_review_pack_{review_pack_id}.json"

        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(review_pack, f, indent=2)

        return artifact_path

    def generate_textual_summary(self, max_lines: int = 60) -> str:
        """Generate bounded textual summary for human review.

        Answers:
        - what kept recurring?
        - what changed often?
        - what got rolled back?
        - what probably needs human policy review next?
        """
        review_pack = self.generate_review_pack()
        sections = review_pack["sections"]

        lines = [
            "",
            "╔══════════════════════════════════════════════════════════════╗",
            "║     ADG POLICY REVIEW PACK (Prompt 14)                       ║",
            "║     QUARTERLY-STYLE GOVERNANCE REVIEW                        ║",
            "╚══════════════════════════════════════════════════════════════╝",
            "",
            f"Review Pack ID: {review_pack['review_pack_id']}",
            f"Generated: {review_pack['timestamp']}",
            f"Review Window: {review_pack['review_window']['days']} days",
            f"Requires Human Review: YES",
            f"Live Mutation: NO",
            "",
        ]

        # Window Summary
        window = sections["window_summary"]
        lines.extend(
            [
                "[WINDOW SUMMARY]",
                f"  Baselines accepted: {window['accepted_baselines_included']}",
                f"  Promotions applied: {window['promotions_applied']}",
                f"  Rollbacks observed: {window['rollbacks_observed']}",
                f"  Data completeness: {window['data_completeness']}",
                "",
            ]
        )

        # Hotspot Patterns
        hotspots = sections["hotspot_patterns"]
        lines.extend(
            [
                "[HOTSPOT PATTERNS]",
                f"  Total proposals analyzed: {hotspots['total_proposals_analyzed']}",
                "  Repeat offenders:",
            ]
        )
        for offender in hotspots["repeat_offenders"][:3]:  # Bounded
            lines.append(f"    - {offender['pattern']}: {offender['count']} occurrences")
        lines.append("")

        # Proposal Summary
        proposals = sections["proposal_summary"]
        lines.extend(
            [
                "[PROPOSAL SUMMARY]",
                f"  High-confidence proposals: {proposals['high_confidence_proposals']}",
                f"  Approval rate: {proposals['approval_rate']:.0%}",
                "  Top categories:",
            ]
        )
        for cat in proposals["proposal_counts_by_category"][:3]:  # Bounded
            lines.append(f"    - {cat['category']}: {cat['count']} proposals")
        lines.append("")

        # Promotion / Rollback Summary
        pr = sections["promotion_rollback_summary"]
        lines.extend(
            [
                "[PROMOTION / ROLLBACK SUMMARY]",
                f"  Total promotions: {pr['total_promotions_in_window']}",
                f"  Total rollbacks: {pr['total_rollbacks_in_window']}",
                f"  Rollback rate: {pr['overall_rollback_rate']:.0%}",
                f"  Churn indicator: {pr['churn_indicator']}",
                "",
            ]
        )

        # Policy Questions
        questions = sections["policy_tuning_questions"]
        lines.extend(
            [
                "[POLICY-TUNING QUESTIONS FOR HUMAN REVIEW]",
            ]
        )
        for i, q in enumerate(questions[:4], 1):  # Bounded
            lines.append(f"  {i}. [{q['priority'].upper()}] {q['question']}")
            lines.append(f"     Trigger: {q['trigger']}")
        lines.append("")

        # Non-Binding Recommendations
        recs = sections["non_binding_recommendations"]
        lines.extend(
            [
                "[NON-BINDING RECOMMENDATIONS]",
                "  (These are suggestions only - require human validation)",
            ]
        )
        for i, rec in enumerate(recs[:3], 1):  # Bounded
            lines.append(f"  {i}. {rec['recommendation']}")
            lines.append(f"     Confidence: {rec['confidence']:.0%}")
        lines.append("")

        # Key Takeaways
        lines.extend(
            [
                "[KEY TAKEAWAYS]",
                f"  • What kept recurring: {hotspots['repeat_offenders'][0]['pattern'] if hotspots['repeat_offenders'] else 'None'}",
                f"  • What changed often: {pr['churn_indicator']} churn detected",
                f"  • What got rolled back: {pr['total_rollbacks_in_window']} rollbacks ({pr['overall_rollback_rate']:.0%} rate)",
            ]
        )
        if questions:
            lines.append(f"  • What needs review: {len(questions)} policy questions identified")
        lines.append("")

        # Enforce line limit
        if len(lines) > max_lines:
            lines = lines[: max_lines - 2]
            lines.append("  ... (output bounded)")
            lines.append("")

        return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python adg_graph_watchlist_builder.py <sqlite_path> [output_dir]")
        sys.exit(1)

    sqlite_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("artifacts/adg")
    output_dir.mkdir(parents=True, exist_ok=True)

    artifact = build_and_emit_graph_watchlist(sqlite_path, output_dir)
    print(f"\nGraph artifact written: {artifact}")
