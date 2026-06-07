#!/usr/bin/env python3
"""Gate J1 — canonical pipeline wiring (plan W1.3).

Fails CI when any 'active' stage in config/canonical_pipelines.yaml lacks a
caller from an allowed ingress layer. This is the primary wiring-CI gate:
it directly answers "does the code actually implement the pipeline the
architecture doc promises?" by asking the ADG instead of trusting prose.

Tier: B (blocking).

Queries (ADG-shape aware):
    ADG 'imports' edges point at SYMBOL nodes (from_import=144k, import=13k),
    never at module nodes. So we aggregate by the destination's resolved_path:

        SELECT DISTINCT src.resolved_path, src.layer
        FROM edges e
        JOIN nodes dst ON dst.id = e.dst_id
        JOIN nodes src ON src.id = e.src_id
        WHERE e.relation_type = 'imports'
          AND dst.resolved_path = ?
          AND src.resolved_path != dst.resolved_path   -- exclude intra-module
          AND src.layer IS NOT NULL

    Test-only wiring (src.layer == 'L_TEST') does NOT satisfy production
    ingress — a stage with only test callers is a production orphan.

Pass criteria for an 'active' stage:
    at least one 'imports' caller with non-test layer intersecting
    stage.min_fanin_from_layers.

Non-'active' stages (status=deferred | unimplemented) produce info rows
but never fail the gate — they are tracked, not enforced.

Run manually:
    python ops_scripts/ci/check_canonical_pipeline_wiring.py

Exit codes:
    0 — all active stages wired (or gate bypassed via WIRING_GATE_BYPASS=1)
    1 — at least one active stage lacks a required ingress caller
    2 — runner error (no snapshot, no manifest, schema invalid, etc.)

References:
    .claude/plans/adg-wiring-ci-hardening-7a5d84.md  (W1.3)
    .claude/plans/c0-context-engine-wiring-fix-9e42a1.md
    config/canonical_pipelines.yaml
    config/schemas/canonical_pipeline.schema.json
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sqlite3
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML is required. Install via `pip install pyyaml`.\n")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
)

MANIFEST = REPO_ROOT / "config" / "canonical_pipelines.yaml"


class CanonicalPipelineWiringGate(WiringGate):
    gate_id = "J1_canonical_pipeline_wiring"
    tier = "B"

    def __init__(self, snapshot: Path | None = None) -> None:
        super().__init__(snapshot=snapshot)
        self.manifest = _load_manifest()

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        violations: list[Violation] = []
        for pipeline in self.manifest.get("pipelines", []):
            pid = pipeline.get("id", "<unknown>")
            for stage in pipeline.get("stages", []):
                violations.extend(self._check_stage(conn, pid, stage))
        return violations

    # ------------------------------------------------------------------
    def _check_stage(
        self,
        conn: sqlite3.Connection,
        pipeline_id: str,
        stage: dict[str, Any],
    ) -> list[Violation]:
        sid = stage.get("id", "<unknown>")
        subject = f"{pipeline_id}::{sid}"
        status = stage.get("status", "active")
        module = stage.get("module")
        allowed = stage.get("min_fanin_from_layers", []) or []

        # Non-active stages: track but never fail.
        if status != "active":
            return [
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=subject,
                    rule="stage_status_not_active",
                    detail=f"status={status}; defer_ref={stage.get('defer_ref', '')!r}",
                    severity="warn",
                    extra={"status": status, "module": module},
                )
            ]

        if not module:
            return [
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=subject,
                    rule="active_stage_missing_module",
                    detail="status=active but module is null; manifest invariant broken",
                )
            ]

        # Resolve the module node in ADG (for layer reporting only).
        mod_row = conn.execute(
            "SELECT id, layer FROM nodes WHERE entity_type='module' AND resolved_path=? LIMIT 1",
            (module,),
        ).fetchone()
        if mod_row is None:
            return [
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=subject,
                    rule="module_not_in_adg",
                    detail=f"resolved_path={module} has no node in ADG — file missing or snapshot stale",
                    extra={"module": module},
                )
            ]
        node_id, node_layer = mod_row

        # Fan-in on 'imports' — edges target symbol nodes, so aggregate by
        # destination's resolved_path. Exclude intra-module edges.
        callers = conn.execute(
            """
            SELECT DISTINCT src.resolved_path, src.layer
            FROM edges e
            JOIN nodes dst ON dst.id = e.dst_id
            JOIN nodes src ON src.id = e.src_id
            WHERE e.relation_type = 'imports'
              AND dst.resolved_path = ?
              AND src.resolved_path != dst.resolved_path
              AND src.layer IS NOT NULL
            """,
            (module,),
        ).fetchall()
        all_caller_layers = sorted({c[1] for c in callers})
        prod_caller_layers = [layer for layer in all_caller_layers if layer != "L_TEST"]
        matching = [layer for layer in prod_caller_layers if layer in allowed]
        if matching:
            return []  # wired correctly from at least one allowed ingress

        # Classify the failure mode for clearer diagnostics.
        caller_paths_sample = [c[0] for c in callers[:10]]
        if not callers:
            rule = "no_caller_at_all"
            detail = f"module {module} (layer={node_layer}) has 0 import callers; required ≥1 from {allowed}"
        elif not prod_caller_layers:
            rule = "test_only_wiring"
            detail = (
                f"module {module} (layer={node_layer}) has {len(callers)} caller(s) "
                f"but only from tests ({all_caller_layers}); production orphan; "
                f"required ≥1 from {allowed}"
            )
        else:
            rule = "no_caller_from_ingress_layer"
            detail = (
                f"module {module} (layer={node_layer}) has {len(callers)} caller(s) "
                f"from layers {all_caller_layers}; none intersect required {allowed}"
            )

        return [
            Violation(
                gate_id=self.gate_id,
                tier=self.tier,
                subject=subject,
                rule=rule,
                detail=detail,
                extra={
                    "module": module,
                    "node_id": node_id,
                    "node_layer": node_layer,
                    "fan_in": len(callers),
                    "caller_layers_all": all_caller_layers,
                    "caller_layers_prod": prod_caller_layers,
                    "caller_paths_sample": caller_paths_sample,
                    "required_layers": allowed,
                },
            )
        ]


def _load_manifest() -> dict[str, Any]:
    if not MANIFEST.exists():
        sys.stderr.write(f"canonical pipeline manifest missing: {MANIFEST}\n")
        sys.exit(2)
    try:
        data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        sys.stderr.write(f"manifest YAML parse error: {exc}\n")
        sys.exit(2)
    if not isinstance(data, dict) or "pipelines" not in data:
        sys.stderr.write(f"manifest invalid (no 'pipelines' key): {MANIFEST}\n")
        sys.exit(2)
    return data


def main() -> int:
    gate = CanonicalPipelineWiringGate()
    result = gate.execute()
    return cli_exit(result)


if __name__ == "__main__":
    sys.exit(main())
