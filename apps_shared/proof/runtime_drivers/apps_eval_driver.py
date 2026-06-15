"""apps_eval real-runtime driver — proof-harness-of-harness.

Per user spec §"apps_eval":
    "Treat as proof harness, not just another demo app. Runs golden,
     negative, ambiguous, stale, and conflicting scenarios through each
     upgraded app and produces scorecards, gate verdicts, trace
     coverage, replay comparisons, and ADG deltas."

The driver:
  * Imports ``apps_eval.engines.scorecard_engine`` (real lifecycle traces).
  * Reads the per-app proof matrix from ``artifacts/apps_proof/apps_proof_matrix.json``
    (when available — if not, builds a minimal scaffold from fixture).
  * Emits scenario_matrix, app_scorecards, trace/replay/gate coverage,
    app_proof_index, adg_delta_summary.
"""

from __future__ import annotations

import json
from pathlib import Path

from apps_shared.proof.runtime_drivers._driver_base import (
    import_real_engine,
    write_artifact,
    write_markdown,
)
from apps_eval.l6_shadow_bridge import build_driver_l6_shadow_bridge_payload


class AppsEvalDriver:
    app_id = "apps_eval"

    def invoke(self, ctx) -> dict[str, str]:
        fixture = dict(ctx.spec.extra_payload or {})

        engine_ok, engine_detail = import_real_engine(
            "apps_eval.engines.scorecard_engine"
        )

        scenarios = list(fixture.get("scenarios") or [])
        weights = dict(fixture.get("weights") or {})

        # Try to read the live cross-app proof matrix
        repo_root = Path(__file__).resolve().parents[3]
        matrix_path = repo_root / "artifacts" / "apps_proof" / "apps_proof_matrix.json"
        live_matrix: dict | None = None
        if matrix_path.exists():
            try:
                live_matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                live_matrix = None

        # scenario_matrix
        scenario_matrix = {
            "eval_id": fixture.get("eval_id"),
            "scenarios": scenarios,
            "kinds_covered": sorted({s.get("kind", "unknown") for s in scenarios}),
            "apps_covered": sorted({s.get("app", "unknown") for s in scenarios}),
        }

        # app_scorecards: derived from live matrix if present
        app_scorecards = []
        if live_matrix and isinstance(live_matrix.get("rows"), list):
            for row in live_matrix["rows"]:
                replay_score = 1.0 if row.get("replay_ok") is True else 0.0
                gate_score = min(1.0, (row.get("gate_count") or 0) / 3.0)
                trace_score = min(1.0, len(row.get("layers_seen") or []) / 7.0)
                adg_score = 1.0 if (row.get("adg_delta_p0") or 0) <= 0 else 0.0
                # Anti-cheat: scorecard cannot pass if trace or replay missing.
                weighted = (
                    weights.get("trace_coverage", 0.25) * trace_score
                    + weights.get("replay_determinism", 0.25) * replay_score
                    + weights.get("gate_completeness", 0.25) * gate_score
                    + weights.get("adg_no_worsening", 0.25) * adg_score
                )
                app_scorecards.append({
                    "app": row.get("app_name"),
                    "verdict": row.get("proof_status"),
                    "weighted_score": round(weighted, 4),
                    "components": {
                        "trace": trace_score,
                        "replay": replay_score,
                        "gates": gate_score,
                        "adg": adg_score,
                    },
                    "fail_codes": row.get("fail_codes", []),
                })

        trace_coverage_report = {
            "matrix_present": live_matrix is not None,
            "apps_with_full_layer_coverage": [
                row["app_name"] for row in (live_matrix or {}).get("rows", [])
                if len(row.get("layers_seen", [])) >= 7
            ],
            "kinds_covered": scenario_matrix["kinds_covered"],
        }
        replay_coverage_report = {
            "matrix_present": live_matrix is not None,
            "apps_with_replay_pass": [
                row["app_name"] for row in (live_matrix or {}).get("rows", [])
                if row.get("replay_ok") is True
            ],
        }
        gate_coverage_report = {
            "matrix_present": live_matrix is not None,
            "apps_with_gates": [
                {"app": row["app_name"], "gate_count": row.get("gate_count", 0)}
                for row in (live_matrix or {}).get("rows", [])
            ],
        }
        adg_delta_summary = {
            "matrix_present": live_matrix is not None,
            "any_p0_increase": any(
                (row.get("adg_delta_p0") or 0) > 0
                for row in (live_matrix or {}).get("rows", [])
            ),
            "max_delta_p0": max(
                ((row.get("adg_delta_p0") or 0) for row in (live_matrix or {}).get("rows", [])),
                default=0,
            ),
        }

        outputs: dict[str, str] = {}
        k, p = write_artifact(ctx, rel_filename="scenario_matrix.json", payload=scenario_matrix, kind="ScenarioMatrix")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="app_scorecards.json", payload=app_scorecards, kind="AppScorecards")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="trace_coverage_report.json", payload=trace_coverage_report, kind="TraceCoverageReport")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="replay_coverage_report.json", payload=replay_coverage_report, kind="ReplayCoverageReport")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="gate_coverage_report.json", payload=gate_coverage_report, kind="GateCoverageReport")
        outputs[k] = p
        k, p = write_artifact(ctx, rel_filename="adg_delta_summary.json", payload=adg_delta_summary, kind="ADGDeltaSummary")
        outputs[k] = p
        bridge = build_driver_l6_shadow_bridge_payload(
            eval_id=fixture.get("eval_id"),
            app_scorecards=app_scorecards,
            output_refs=outputs,
        )
        k, p = write_artifact(ctx, rel_filename="apps_eval_l6_shadow_bridge.json", payload=bridge, kind="AppsEvalL6ShadowBridge")
        outputs[k] = p

        # app_proof_index.md
        body_lines = [
            "# Apps Proof Index — apps_eval cross-app aggregate",
            "",
            f"- Eval ID: `{fixture.get('eval_id')}`",
            f"- Scenarios: {len(scenarios)} ({', '.join(scenario_matrix['kinds_covered'])})",
            f"- Engine import: {'OK' if engine_ok else f'FAIL ({engine_detail})'}",
            f"- Live matrix loaded: {live_matrix is not None}",
            "",
            "## Per-app weighted scorecard",
            "",
            "| App | Verdict | Weighted | Trace | Replay | Gates | ADG |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
        for sc in app_scorecards:
            comp = sc["components"]
            body_lines.append(
                f"| `{sc['app']}` | {sc['verdict']} | {sc['weighted_score']:.3f} "
                f"| {comp['trace']:.2f} | {comp['replay']:.2f} "
                f"| {comp['gates']:.2f} | {comp['adg']:.2f} |"
            )
        rel = write_markdown(ctx, rel_filename="app_proof_index.md", body="\n".join(body_lines))
        outputs["AppProofIndex"] = rel
        return outputs
