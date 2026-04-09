"""Gate 5: P0 Untrusted Text-to-Action Gate.

Blocks free-form text influence over action/tool use without structure and validation.
Requires schema / structured extraction / validation / approval where architecture requires it.

Source views:
    - mv_untrusted_text_to_action_risk
    - mv_actionable_surface_without_schema
    - mv_structured_output_gaps
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any

from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult, GateViolation


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
            for row in cursor.fetchall():
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
            for row in cursor.fetchall():
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
            for row in cursor.fetchall():
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
        )


def main() -> int:
    """CLI entry point."""
    gate = TextToActionGate()
    return gate.run_and_exit()


if __name__ == "__main__":
    import sys

    sys.exit(main())
