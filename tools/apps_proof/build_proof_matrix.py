"""W6 — apps_* proof matrix builder.

Aggregates every per-run ``proof_verdict.json`` under
``artifacts/apps_proof/<app>/<run_id>/verifier/`` into a cross-app
status matrix.

CLI:

    python -m tools.apps_proof.build_proof_matrix \
        --proof-root artifacts/apps_proof \
        --out artifacts/apps_proof/apps_proof_matrix.json

Outputs:
    apps_proof_matrix.json — machine-readable
    apps_proof_matrix.md   — human-readable summary

For each app, the matrix records the most recent run's verdict, with
columns: app_name, target scenario, run_id, ADG risk tier, route shape,
required spans seen, contracts emitted, gates count, replay status,
ADG delta status, sabotage status (when present), proof status, fail
reasons.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AppMatrixRow:
    app_name: str
    run_id: str = ""
    scenario_id: str = ""
    risk_tier: str = "UNKNOWN"
    grounded: bool = False
    proof_status: str = "NO_RUN"
    fail_codes: list[str] = field(default_factory=list)
    layers_seen: list[str] = field(default_factory=list)
    contract_count: int = 0
    gate_count: int = 0
    replay_ok: bool | None = None
    adg_delta_p0: int | None = None
    sabotage_total: int | None = None
    sabotage_caught: int | None = None
    proof_verdict_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_name": self.app_name,
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "risk_tier": self.risk_tier,
            "grounded": self.grounded,
            "proof_status": self.proof_status,
            "fail_codes": list(self.fail_codes),
            "layers_seen": list(self.layers_seen),
            "contract_count": self.contract_count,
            "gate_count": self.gate_count,
            "replay_ok": self.replay_ok,
            "adg_delta_p0": self.adg_delta_p0,
            "sabotage_total": self.sabotage_total,
            "sabotage_caught": self.sabotage_caught,
            "proof_verdict_path": self.proof_verdict_path,
        }


def _load_json(p: Path) -> Any:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _scan_app(app_dir: Path) -> AppMatrixRow:
    """Return the latest run's matrix row for one app."""
    runs = sorted(
        [d for d in app_dir.iterdir() if d.is_dir() and not d.name.startswith("_")],
        key=lambda d: d.stat().st_mtime,
        reverse=True,
    )
    row = AppMatrixRow(app_name=app_dir.name)
    if not runs:
        return row
    latest = runs[0]
    row.run_id = latest.name
    verdict_path = latest / "verifier" / "proof_verdict.json"
    row.proof_verdict_path = str(verdict_path)

    manifest = _load_json(latest / "run_manifest.json") or {}
    row.scenario_id = manifest.get("scenario_id", "")
    row.grounded = bool(manifest.get("grounding_required", False))

    coverage = _load_json(latest / "trace" / "span_coverage.json") or {}
    row.layers_seen = list(coverage.get("layers_seen", []))

    contracts_dir = latest / "contracts"
    if contracts_dir.exists():
        row.contract_count = sum(1 for _ in contracts_dir.glob("*.json"))

    gate_path = latest / "gates" / "gate_verdicts.jsonl"
    if gate_path.exists():
        row.gate_count = sum(
            1 for line in gate_path.read_text(encoding="utf-8").splitlines() if line.strip()
        )

    replay = _load_json(latest / "replay" / "replay_comparison.json")
    if isinstance(replay, dict):
        row.replay_ok = bool(replay.get("ok", False))

    adg_delta = _load_json(latest / "adg" / "adg_delta.json")
    if isinstance(adg_delta, dict):
        row.adg_delta_p0 = int(adg_delta.get("delta_p0", 0))

    verdict = _load_json(verdict_path)
    if isinstance(verdict, dict):
        row.proof_status = str(verdict.get("final_status", "NO_VERDICT"))
        row.fail_codes = sorted({
            str(fc.get("fail_code"))
            for fc in verdict.get("failed_checks", [])
            if fc.get("fail_code")
        })

    sabotage = _load_json(latest / "verifier" / "sabotage_results.json")
    if isinstance(sabotage, dict):
        # Prefer the new "applicable" denominator (excludes N/A cases) when
        # present; fall back to "total" for older sabotage results files.
        applicable = sabotage.get("applicable")
        row.sabotage_total = int(applicable if applicable is not None else sabotage.get("total", 0))
        row.sabotage_caught = int(sabotage.get("caught", 0))

    # Risk tier — derived from app_id; matches plan ADG_HOTSPOT_REPORT.
    risk_tiers = {
        "apps_underwriting_ai": "LOW (HIGH_IMPACT semantics)",
        "apps_rfp": "LOW",
        "apps_research": "LOW-MED",
        "apps_exec": "MED",
        "apps_eval": "MED (proof harness)",
        "apps_lic": "HIGH (privacy/egress)",
        "apps_rg": "HIGH (read-only only)",
        "apps_shared": "SUBSTRATE",
    }
    row.risk_tier = risk_tiers.get(app_dir.name, "UNKNOWN")
    return row


def build_matrix(proof_root: Path) -> dict[str, Any]:
    if not proof_root.exists():
        return {"proof_root": str(proof_root), "rows": [], "summary": {}}
    rows: list[AppMatrixRow] = []
    for app_dir in sorted(proof_root.iterdir()):
        if not app_dir.is_dir():
            continue
        if not app_dir.name.startswith("apps_"):
            continue
        rows.append(_scan_app(app_dir))
    summary = {
        "total": len(rows),
        "passing": sum(1 for r in rows if r.proof_status == "PASS"),
        "failing": sum(1 for r in rows if r.proof_status == "FAIL"),
        "no_run": sum(1 for r in rows if r.proof_status == "NO_RUN"),
    }
    return {
        "proof_root": str(proof_root),
        "rows": [r.to_dict() for r in rows],
        "summary": summary,
    }


def _write_md(matrix: dict[str, Any], out_md: Path) -> None:
    lines: list[str] = []
    lines.append("# apps_* Proof Matrix")
    lines.append("")
    lines.append(f"- Proof root: `{matrix['proof_root']}`")
    s = matrix["summary"]
    lines.append(f"- Apps: {s['total']} | PASS: {s['passing']} | FAIL: {s['failing']} | NO_RUN: {s['no_run']}")
    lines.append("")
    lines.append(
        "| App | Verdict | Run | Scenario | Risk | Grounded | Layers | Contracts | Gates | Replay | ADG ΔP0 | Sabotage |"
    )
    lines.append("|---|---|---|---|---|---|---|---:|---:|---|---:|---|")
    for r in matrix["rows"]:
        replay = "OK" if r["replay_ok"] is True else ("FAIL" if r["replay_ok"] is False else "-")
        sab = (
            f"{r['sabotage_caught']}/{r['sabotage_total']}"
            if r["sabotage_total"] is not None
            else "-"
        )
        adg = str(r["adg_delta_p0"]) if r["adg_delta_p0"] is not None else "-"
        layers = ",".join(r["layers_seen"][:6]) + ("…" if len(r["layers_seen"]) > 6 else "")
        lines.append(
            f"| `{r['app_name']}` | {r['proof_status']} | `{r['run_id']}` "
            f"| `{r['scenario_id']}` | {r['risk_tier']} "
            f"| {'yes' if r['grounded'] else 'no'} | {layers} "
            f"| {r['contract_count']} | {r['gate_count']} | {replay} "
            f"| {adg} | {sab} |"
        )
    failing = [r for r in matrix["rows"] if r["proof_status"] == "FAIL"]
    if failing:
        lines.append("")
        lines.append("## Failing apps — fail codes")
        lines.append("")
        for r in failing:
            lines.append(f"- **{r['app_name']}** (`{r['run_id']}`): {', '.join(r['fail_codes']) or '-'}")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tools.apps_proof.build_proof_matrix",
        description="Aggregate per-run proof_verdict.json into a cross-app matrix.",
    )
    parser.add_argument("--proof-root", type=Path, default=Path("artifacts/apps_proof"))
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/apps_proof/apps_proof_matrix.json"),
    )
    args = parser.parse_args(argv)
    matrix = build_matrix(args.proof_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(matrix, indent=2, sort_keys=True), encoding="utf-8")
    _write_md(matrix, args.out.with_suffix(".md"))
    print(
        f"matrix: {matrix['summary']['passing']}/{matrix['summary']['total']} "
        f"PASS, {matrix['summary']['failing']} FAIL, {matrix['summary']['no_run']} NO_RUN"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
