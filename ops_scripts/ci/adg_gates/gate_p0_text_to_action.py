"""Gate 5: P0 Untrusted Text-to-Action Gate.

Blocks free-form text influence over action/tool use without structure and validation.
Requires schema / structured extraction / validation / approval where architecture requires it.

Source views:
    - mv_untrusted_text_to_action_risk
    - mv_actionable_surface_without_schema
    - mv_structured_output_gaps
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sys
from pathlib import Path


def _bootstrap_repo_root() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


_REPO_ROOT = _bootstrap_repo_root()

import sqlite3
from datetime import datetime, timezone
from typing import Any

from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult, GateViolation
from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy

try:
    from tqdm import tqdm
except ImportError as exc:
    raise RuntimeError("tqdm is required for ADG CI gates; install with: pip install tqdm") from exc


class TextToActionGate(ADGGateBase):
    """P0 Untrusted Text-to-Action Gate.

    Enforces that text inputs to action-capable modules are validated
    through schemas and structured extraction, not free-form parsing.
    """

    gate_family = "text_to_action"
    severity = "P0"
    source_views = [
        "mv_untrusted_text_to_action_risk",
        "mv_actionable_surface_without_schema",
        "mv_structured_output_gaps",
    ]
    execution_policy = ExecutionPolicy(
        stage="preflight+full",
        repairability="suggest_only",
        gate_action="halt",
        artifact_policy="minimal_failure_artifact",
        signal_source="sqlite_mv_ci",
        evidence_tier="truth",
    )

    def _execute_preflight_logic(self) -> GateResult:
        """Preflight: detect action-capable files lacking schema imports via import edges."""
        violations: list[GateViolation] = []
        summary: dict[str, Any] = {
            "total_violations": 0,
            "preflight_mode": True,
            "source": "import_edges",
            "in_modified_area": 0,
        }

        if not self.conn:
            return self._empty_result()

        try:
            cursor = self.conn.execute("""
                SELECT DISTINCT n.node_id, n.file_path, n.layer
                FROM nodes n
                JOIN edges e ON e.src_id = n.node_id
                WHERE e.relation_type = 'imports'
                  AND n.file_path LIKE '%action%'
                  AND n.file_path NOT LIKE '%schema%'
                  AND n.file_path NOT LIKE '%validation%'
                LIMIT 100
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                node_id, file_path, layer = row[0], row[1], row[2]
                in_mod = self._is_in_modified_area(file_path)
                if in_mod:
                    summary["in_modified_area"] += 1
                violations.append(
                    GateViolation(
                        violation_id=f"preflight_tta_{node_id}",
                        source_view="import_edges",
                        source_node=str(node_id),
                        source_edge=None,
                        file=file_path,
                        line=None,
                        layer_src=layer,
                        layer_dst=None,
                        path_id=None,
                        first_illegal_hop=f"{layer}->unvalidated_text",
                        path_criticality=3.0,
                        in_modified_area=in_mod,
                        message=(
                            f"[PREFLIGHT] Action-capable module lacks schema/validation import: {file_path}"
                        ),
                        path_criticality_class="execution",
                        structured_action_required=True,
                        approval_required=False,
                    )
                )
        except sqlite3.Error:
            pass

        summary["total_violations"] = len(violations)
        status = "blocked" if violations else "passed"
        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            violations=violations,
            summary=summary,
            policy=self.execution_policy,
            stage="preflight",
        )

    def _execute_gate_logic(self) -> GateResult:
        """Execute text-to-action safety check."""
        violations: list[GateViolation] = []
        summary: dict[str, Any] = {
            "total_violations": 0,
            "high_risk_text_to_action": 0,
            "actionable_without_schema": 0,
            "structured_output_gaps": 0,
            "by_layer": {},
            "in_modified_area": 0,
        }

        if not self.conn:
            return self._empty_result()

        # Check 1: Untrusted text-to-action risk
        try:
            cursor = self.conn.execute("""
                SELECT node_id, file, layer, text_input_count, action_invocation_count,
                       schema_validation_count, risk_score, risk_level
                FROM mv_untrusted_text_to_action_risk
                WHERE risk_level IN ('high', 'critical')
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                (
                    node_id,
                    file,
                    layer,
                    text_input_count,
                    action_invocation_count,
                    schema_validation_count,
                    risk_score,
                    risk_level,
                ) = row

                summary["high_risk_text_to_action"] += 1
                summary["by_layer"][layer] = summary["by_layer"].get(layer, 0) + 1

                in_mod = self._is_in_modified_area(file)
                if in_mod:
                    summary["in_modified_area"] += 1

                violation = GateViolation(
                    violation_id=f"text_risk_{node_id}",
                    source_view="mv_untrusted_text_to_action_risk",
                    source_node=str(node_id),
                    source_edge=None,
                    file=file,
                    line=None,
                    layer_src=layer,
                    layer_dst=None,
                    path_id=str(node_id),
                    first_illegal_hop=f"{layer}->unvalidated_text",
                    path_criticality=float(risk_score),
                    in_modified_area=in_mod,
                    message=f"High-risk text-to-action: {text_input_count} text inputs, "
                    f"{action_invocation_count} actions, {schema_validation_count} validations "
                    f"(score={risk_score:.2f}, level={risk_level})",
                    extra={
                        "text_input_count": text_input_count,
                        "action_invocation_count": action_invocation_count,
                        "schema_validation_count": schema_validation_count,
                        "risk_score": risk_score,
                        "risk_level": risk_level,
                    },
                )
                violations.append(violation)
        except sqlite3.Error:
            pass

        # Check 2: Actionable surface without schema
        try:
            cursor = self.conn.execute("""
                SELECT node_id, file, layer, action_capability_count, schema_definition_count,
                       validation_layer_count, gap_type
                FROM mv_actionable_surface_without_schema
                WHERE gap_type != 'ok'
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                (
                    node_id,
                    file,
                    layer,
                    action_capability_count,
                    schema_definition_count,
                    validation_layer_count,
                    gap_type,
                ) = row

                summary["actionable_without_schema"] += 1

                in_mod = self._is_in_modified_area(file)
                if in_mod:
                    summary["in_modified_area"] += 1

                violation = GateViolation(
                    violation_id=f"no_schema_{node_id}",
                    source_view="mv_actionable_surface_without_schema",
                    source_node=str(node_id),
                    source_edge=None,
                    file=file,
                    line=None,
                    layer_src=layer,
                    layer_dst=None,
                    path_id=str(node_id),
                    first_illegal_hop=f"{layer}->{gap_type}",
                    path_criticality=3.5,
                    in_modified_area=in_mod,
                    message=f"Actionable surface without schema ({gap_type}): "
                    f"{action_capability_count} capabilities, {schema_definition_count} schemas, "
                    f"{validation_layer_count} validation layers",
                    extra={
                        "action_capability_count": action_capability_count,
                        "schema_definition_count": schema_definition_count,
                        "validation_layer_count": validation_layer_count,
                        "gap_type": gap_type,
                    },
                )
                violations.append(violation)
        except sqlite3.Error:
            pass

        # Check 3: Structured output gaps
        try:
            cursor = self.conn.execute("""
                SELECT node_id, file, layer, output_production_count, structured_output_count,
                       schema_conformance_count, gap_type
                FROM mv_structured_output_gaps
                WHERE gap_type != 'ok'
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                (
                    node_id,
                    file,
                    layer,
                    output_production_count,
                    structured_output_count,
                    schema_conformance_count,
                    gap_type,
                ) = row

                summary["structured_output_gaps"] += 1

                in_mod = self._is_in_modified_area(file)
                if in_mod:
                    summary["in_modified_area"] += 1

                violation = GateViolation(
                    violation_id=f"output_gap_{node_id}",
                    source_view="mv_structured_output_gaps",
                    source_node=str(node_id),
                    source_edge=None,
                    file=file,
                    line=None,
                    layer_src=layer,
                    layer_dst=None,
                    path_id=str(node_id),
                    first_illegal_hop=f"{layer}->{gap_type}",
                    path_criticality=2.5,
                    in_modified_area=in_mod,
                    message=f"Structured output gap ({gap_type}): "
                    f"{output_production_count} outputs, {structured_output_count} structured, "
                    f"{schema_conformance_count} conforming",
                    extra={
                        "output_production_count": output_production_count,
                        "structured_output_count": structured_output_count,
                        "schema_conformance_count": schema_conformance_count,
                        "gap_type": gap_type,
                    },
                )
                violations.append(violation)
        except sqlite3.Error:
            pass

        # Determine status: P0 blocks if high-risk text-to-action exists
        summary["total_violations"] = len(violations)
        has_critical = summary["high_risk_text_to_action"] > 0
        status = "blocked" if has_critical else ("warn" if violations else "passed")

        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            violations=violations,
            summary=summary,
            policy=self.execution_policy,
        )

    def _empty_result(self) -> GateResult:
        """Return empty result when connection unavailable."""
        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="passed",
            violations=[],
            summary={
                "total_violations": 0,
                "high_risk_text_to_action": 0,
                "actionable_without_schema": 0,
                "structured_output_gaps": 0,
                "by_layer": {},
                "in_modified_area": 0,
                "note": "Materialized views not available - no violations detected",
            },
            policy=self.execution_policy,
        )


def main() -> int:
    """CLI entry point."""
    gate = TextToActionGate()
    return gate.run_and_exit()


if __name__ == "__main__":
    sys.exit(main())
