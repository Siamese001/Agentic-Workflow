"""CLI entrypoint for the apps_* runtime proof harness.

W1 surface (working today):

    python -m apps_shared.proof.proof_runner --bypass-only \
        --adg artifacts/adg/adg_indexed_04252026_0843.sqlite \
        --export artifacts/runtime/apps_proof/latest

This command runs the ADG bypass queries against the supplied snapshot,
emits per-app JSON reports, writes a Markdown summary, and exits non-zero
if any P0 bypass is unresolved without an active waiver.

W2..W4 will extend this entrypoint with ``--all`` (per-app scenarios + replay
+ negative controls). For now ``--all`` is recognized but emits a
NOT_IMPLEMENTED record to keep contracts honest.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Make the repo importable when the script is invoked as
# ``python -m apps_shared.proof.proof_runner`` from the repo root.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from apps_shared.proof.adg_queries import AppBypassReport
from apps_shared.proof.app_inventory import discover_apps, required_apps
from apps_shared.proof.bypass_validator import (
    BypassValidationResult,
    Waiver,
    load_waivers,
    run_full_bypass_validation,
)
from apps_shared.proof.proof_contracts import (
    PROOF_STATUS_PASS,
    AppRunEvidencePacket,
    verify_packet_hash,
)
from apps_shared.proof.scenario_base import run_app_scenario
from apps_shared.proof.scenarios import SCENARIOS
from apps_shared.proof.validators import validate_scenario
from apps_shared.proof.negative_controls import run_negative_controls_for_all
from apps_shared.proof.write_sovereignty import validate_write_sovereignty


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, default=str),
        encoding="utf-8",
    )


def _bypass_report_to_dict(report: AppBypassReport) -> dict[str, object]:
    return {
        "app_id": report.app_id,
        "snapshot_path": report.snapshot_path,
        "p0_unresolved_total": report.p0_unresolved_total,
        "p1_unresolved_total": report.p1_unresolved_total,
        "p2_unresolved_total": report.p2_unresolved_total,
        "per_query": report.per_query,
    }


def _validation_to_dict(result: BypassValidationResult) -> dict[str, object]:
    return result.to_dict()


def _write_adg_bypass_report_md(
    *,
    out_path: Path,
    snapshot: Path,
    apps: tuple[str, ...],
    reports: dict[str, AppBypassReport],
    results: dict[str, BypassValidationResult],
) -> None:
    lines: list[str] = []
    lines.append("# ADG Bypass Report — apps_* runtime proof harness")
    lines.append("")
    lines.append(f"- Snapshot: `{snapshot}`")
    lines.append(f"- Generated: {_utcnow_iso()}")
    lines.append(f"- Apps validated: {len(apps)}")
    lines.append("")
    lines.append("## Per-app summary")
    lines.append("")
    lines.append("| App | P0 unresolved | P1 unresolved | P2 unresolved | Verdict |")
    lines.append("|---|---:|---:|---:|---|")
    for app in apps:
        r = reports[app]
        v = results[app]
        verdict = "PASS" if v.passed else "FAIL"
        lines.append(
            f"| `{app}` | {r.p0_unresolved_total} | {r.p1_unresolved_total} "
            f"| {r.p2_unresolved_total} | {verdict} |"
        )
    lines.append("")
    lines.append("## Per-query breakdown (P0 only)")
    lines.append("")
    for app in apps:
        r = reports[app]
        p0_rows: list[tuple[str, dict[str, object]]] = []
        for name, q in r.per_query.items():
            unresolved = q.get("unresolved")
            if q.get("severity") == "P0" and isinstance(unresolved, int) and unresolved > 0:
                p0_rows.append((name, q))
        if not p0_rows:
            continue
        lines.append(f"### `{app}`")
        lines.append("")
        lines.append("| Query | View | Unresolved |")
        lines.append("|---|---|---:|")
        for name, q in p0_rows:
            lines.append(f"| {name} | `{q['view']}` | {q['unresolved']} |")
        lines.append("")
    lines.append("## ADG Provenance")
    lines.append("")
    lines.append(f"backend=sqlite, snapshot={snapshot.name}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="apps_shared.proof.proof_runner",
        description="apps_* runtime proof harness",
    )
    p.add_argument(
        "--adg",
        required=True,
        type=Path,
        help="Path to ADG SQLite snapshot",
    )
    p.add_argument(
        "--export",
        required=True,
        type=Path,
        help="Output directory (e.g. artifacts/runtime/apps_proof/latest)",
    )
    p.add_argument(
        "--apps",
        nargs="*",
        default=None,
        help="Subset of app_ids to validate (default: all required apps)",
    )
    p.add_argument(
        "--waivers",
        type=Path,
        default=None,
        help="Optional path to waivers JSON",
    )
    p.add_argument(
        "--fail-on-p1",
        action="store_true",
        help="Treat P1 unresolved as failures too (strict coverage mode)",
    )
    p.add_argument(
        "--bypass-only",
        action="store_true",
        help="W1 mode: ADG bypass validation only, no runtime scenarios",
    )
    p.add_argument(
        "--all",
        action="store_true",
        help="W2+ mode: run per-app runtime scenarios",
    )
    p.add_argument(
        "--validate",
        action="store_true",
        help=(
            "W3 mode: also run trace tree + replay determinism + artifact "
            "inventory validators on each scenario. Implies --all."
        ),
    )
    p.add_argument(
        "--negative-controls",
        action="store_true",
        help=(
            "W4 mode: run 12 adversarial tampering tests proving each "
            "validator catches deliberate corruption. Implies --validate."
        ),
    )
    p.add_argument(
        "--write-sovereignty",
        action="store_true",
        help=(
            "W4 mode: run ADG-driven write-sovereignty validator (no apps_* "
            "may write outside UWG). Implies --all."
        ),
    )
    p.add_argument(
        "--full",
        action="store_true",
        help="W4+ mode: enables --validate, --negative-controls, --write-sovereignty.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    # --full implies all W4 flags
    if args.full:
        args.validate = True
        args.negative_controls = True
        args.write_sovereignty = True
    # --negative-controls requires the validators run first
    if args.negative_controls:
        args.validate = True
    # --validate / --write-sovereignty imply --all
    if args.validate or args.write_sovereignty:
        args.all = True

    if not args.bypass_only and not args.all:
        print(
            "ERROR: must pass --bypass-only (W1), --all (W2), --validate (W3), "
            "--negative-controls/--write-sovereignty/--full (W4).",
            file=sys.stderr,
        )
        return 2

    if not args.adg.exists():
        print(f"ERROR: ADG snapshot missing: {args.adg}", file=sys.stderr)
        return 2

    repo_root = _REPO_ROOT
    inventory = discover_apps(repo_root=repo_root, adg_snapshot=args.adg)
    required = required_apps(inventory)
    apps = tuple(args.apps) if args.apps else required

    export_root = args.export
    export_root.mkdir(parents=True, exist_ok=True)
    (export_root / "manifests").mkdir(parents=True, exist_ok=True)
    (export_root / "adg").mkdir(parents=True, exist_ok=True)

    # Always write the inventory regardless of mode.
    _write_json(
        export_root / "manifests" / "apps_inventory.json",
        {
            "snapshot": str(args.adg),
            "discovered": [
                {
                    "app_id": e.app_id,
                    "has_ingress_runner": e.has_ingress_runner,
                    "has_execution_adapter": e.has_execution_adapter,
                    "has_engines_dir": e.has_engines_dir,
                    "has_outputs_dir": e.has_outputs_dir,
                    "node_count_in_adg": e.node_count_in_adg,
                    "risk_class": e.risk_class,
                    "notes": list(e.notes),
                }
                for e in inventory
            ],
            "required_apps": list(required),
            "validated_apps": list(apps),
        },
    )

    # Run bypass queries for every selected app.
    waivers = load_waivers(args.waivers)
    reports, results = run_full_bypass_validation(
        snapshot=args.adg,
        apps=apps,
        waivers=waivers,
        fail_on_p1=args.fail_on_p1,
    )

    # Per-app JSON exports.
    for app_id, report in reports.items():
        _write_json(
            export_root / "adg" / f"{app_id}_bypass.json",
            _bypass_report_to_dict(report),
        )
    _write_json(
        export_root / "adg" / "app_gap_summary.json",
        {
            "snapshot": str(args.adg),
            "generated_at": _utcnow_iso(),
            "per_app": {a: _bypass_report_to_dict(r) for a, r in reports.items()},
            "validation": {a: _validation_to_dict(v) for a, v in results.items()},
            "fail_on_p1": args.fail_on_p1,
        },
    )
    _write_adg_bypass_report_md(
        out_path=export_root / "adg" / "adg_bypass_report.md",
        snapshot=args.adg,
        apps=apps,
        reports=reports,
        results=results,
    )

    overall_pass = all(v.passed for v in results.values())
    summary = {
        "run_id": uuid.uuid4().hex[:12],
        "generated_at": _utcnow_iso(),
        "process_id": os.getpid(),
        "python_executable": sys.executable,
        "command": " ".join(sys.argv),
        "snapshot": str(args.adg),
        "mode": "bypass_only" if args.bypass_only else "all",
        "apps": list(apps),
        "overall_pass": overall_pass,
        "per_app_results": {a: _validation_to_dict(v) for a, v in results.items()},
    }

    if args.all:
        scenario_results: dict[str, dict[str, object]] = {}
        for app_id in apps:
            registered = SCENARIOS.get(app_id)
            if registered is None:
                scenario_results[app_id] = {
                    "scenario_status": "NO_SCENARIO_REGISTERED",
                    "proof_status": "FAIL",
                }
                continue
            try:
                packet = run_app_scenario(
                    registered.spec,
                    export_root=export_root,
                    adg_snapshot=args.adg,
                    customizer=registered.customizer,
                )
            except (RuntimeError, ValueError, TypeError, AttributeError, ImportError) as exc:
                scenario_results[app_id] = {
                    "scenario_status": "EXCEPTION",
                    "proof_status": "FAIL",
                    "error": repr(exc),
                }
                continue
            # Verify the packet hash binds the on-disk JSON
            packet_path = (
                export_root / "contracts" / app_id / registered.spec.scenario_id / "evidence_packet.json"
            )
            hash_ok, hash_msg = verify_packet_hash(packet_path)

            # Count actual records on disk, not just inventory file entries
            def _count_records(rel_paths: list[str]) -> int:
                total = 0
                for rel in rel_paths:
                    fp = export_root / rel
                    if not fp.exists():
                        continue
                    try:
                        recs = json.loads(fp.read_text(encoding="utf-8"))
                    except (json.JSONDecodeError, OSError):
                        continue
                    if isinstance(recs, list):
                        total += len(recs)
                return total

            scenario_results[app_id] = {
                "scenario_id": registered.spec.scenario_id,
                "scenario_status": "PASS" if packet.proof_status == PROOF_STATUS_PASS else "FAIL",
                "proof_status": packet.proof_status,
                "fail_reasons": list(packet.fail_reasons),
                "trace_id": packet.trace_id,
                "request_id": packet.request_id,
                "run_id": packet.run_id,
                "packet_hash": packet.packet_hash,
                "packet_path": str(packet_path.relative_to(export_root)).replace("\\", "/"),
                "packet_hash_verified": hash_ok,
                "packet_hash_msg": hash_msg,
                "spans_count": _count_records(packet.span_inventory),
                "contracts_count": _count_records(packet.contract_inventory),
                "gates_count": _count_records(packet.gate_verdict_inventory),
            }
        summary["scenarios"] = scenario_results
        # Combine bypass + scenario verdicts for overall_pass
        scenarios_pass = all(r.get("proof_status") == PROOF_STATUS_PASS for r in scenario_results.values())
        summary["overall_pass"] = bool(summary["overall_pass"]) and scenarios_pass
        overall_pass = summary["overall_pass"]

        # W3 validators (trace tree + replay + artifact inventory)
        if args.validate:
            validation_results: dict[str, dict[str, object]] = {}
            for app_id in apps:
                registered = SCENARIOS.get(app_id)
                if registered is None:
                    validation_results[app_id] = {"ok": False, "reason": "no_scenario"}
                    continue
                # Reload packet from disk so the validator sees the canonical
                # on-disk content (not just an in-memory dataclass)
                packet_path = (
                    export_root / "contracts" / app_id / registered.spec.scenario_id / "evidence_packet.json"
                )
                if not packet_path.exists():
                    validation_results[app_id] = {"ok": False, "reason": "packet_missing"}
                    continue
                packet_dict = json.loads(packet_path.read_text(encoding="utf-8"))

                # Reconstruct packet — only the fields validators consume
                packet_obj = AppRunEvidencePacket(
                    app_id=packet_dict["app_id"],
                    scenario_id=packet_dict["scenario_id"],
                    command=packet_dict["command"],
                    cwd=packet_dict["cwd"],
                    process_id=packet_dict["process_id"],
                    python_executable=packet_dict["python_executable"],
                    git_commit_or_snapshot_ref=packet_dict.get("git_commit_or_snapshot_ref"),
                    adg_snapshot_ref=packet_dict["adg_snapshot_ref"],
                    request_id=packet_dict["request_id"],
                    session_id=packet_dict["session_id"],
                    run_id=packet_dict["run_id"],
                    trace_root=packet_dict["trace_root"],
                    trace_id=packet_dict["trace_id"],
                    span_inventory=list(packet_dict.get("span_inventory", [])),
                    contract_inventory=list(packet_dict.get("contract_inventory", [])),
                    gate_verdict_inventory=list(packet_dict.get("gate_verdict_inventory", [])),
                    artifact_inventory=list(packet_dict.get("artifact_inventory", [])),
                    packet_hash=packet_dict.get("packet_hash"),
                )
                try:
                    vr = validate_scenario(
                        registered=registered,
                        packet=packet_obj,
                        export_root=export_root,
                        adg_snapshot=args.adg,
                    )
                except (RuntimeError, ValueError, TypeError, AttributeError) as exc:
                    validation_results[app_id] = {"ok": False, "reason": f"validator_exception: {exc!r}"}
                    continue
                validation_results[app_id] = vr.to_dict()
            summary["validation"] = validation_results
            # Combine into overall verdict
            validators_pass = all(r.get("ok", False) for r in validation_results.values())
            summary["overall_pass"] = bool(summary["overall_pass"]) and validators_pass
            overall_pass = summary["overall_pass"]

        # W4 — write sovereignty (ADG structural check)
        if args.write_sovereignty:
            ws = validate_write_sovereignty(snapshot=args.adg, apps=apps)
            summary["write_sovereignty"] = ws.to_dict()
            summary["overall_pass"] = bool(summary["overall_pass"]) and ws.ok
            overall_pass = summary["overall_pass"]

        # W4 — negative controls (adversarial tampering tests)
        if args.negative_controls:
            nc = run_negative_controls_for_all(
                apps=apps,
                scenarios=SCENARIOS,
                primary_export_root=export_root,
                adg_snapshot=args.adg,
            )
            nc_summary: dict[str, dict[str, object]] = {}
            for app_id, controls in nc.items():
                caught = sum(1 for c in controls if c.caught)
                total = len(controls)
                nc_summary[app_id] = {
                    "caught": caught,
                    "total": total,
                    "all_caught": caught == total,
                    "controls": [c.to_dict() for c in controls],
                }
            summary["negative_controls"] = nc_summary
            nc_all_caught = all(s["all_caught"] for s in nc_summary.values())
            summary["overall_pass"] = bool(summary["overall_pass"]) and nc_all_caught
            overall_pass = summary["overall_pass"]

    _write_json(export_root / "proof_summary.json", summary)

    # proof_report.md
    if args.bypass_only:
        mode_label = "W1 (bypass-only)"
    elif args.negative_controls or args.write_sovereignty:
        mode_label = "W4 (full — scenarios + bypass + validators + negative controls + write sovereignty)"
    elif args.validate:
        mode_label = "W3 (scenarios + bypass + validators)"
    else:
        mode_label = "W2 (scenarios + bypass)"
    md = [
        f"# apps_* runtime proof harness — {mode_label}",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Generated: {summary['generated_at']}",
        f"- Snapshot: `{args.adg}`",
        f"- Mode: `{summary['mode']}`",
        f"- Apps validated: {len(apps)}",
        f"- Overall verdict: **{'PASS' if overall_pass else 'FAIL'}**",
        "",
        "## Per-app verdict",
        "",
        "| App | Verdict | P0 | P1 | P2 |",
        "|---|---|---:|---:|---:|",
    ]
    for app in apps:
        v = results[app]
        verdict = "PASS" if v.passed else "FAIL"
        md.append(f"| `{app}` | {verdict} | {v.p0_unresolved} | {v.p1_unresolved} | {v.p2_unresolved} |")
    md.extend(
        [
            "",
            "See `adg/adg_bypass_report.md` for per-query detail.",
            "",
        ]
    )

    if args.all and "scenarios" in summary:
        md.append("## Per-scenario verdict")
        md.append("")
        md.append("| App | Scenario | Status | Spans | Contracts | Gates | Hash OK |")
        md.append("|---|---|---|---:|---:|---:|---|")
        for app_id, r in summary["scenarios"].items():
            md.append(
                f"| `{app_id}` | `{r.get('scenario_id', '?')}` | "
                f"{r.get('scenario_status', '?')} | "
                f"{r.get('spans_count', '?')} | "
                f"{r.get('contracts_count', '?')} | "
                f"{r.get('gates_count', '?')} | "
                f"{'yes' if r.get('packet_hash_verified') else 'no'} |"
            )
        md.append("")

    if args.validate and "validation" in summary:
        md.append("## Per-scenario W3 validation")
        md.append("")
        md.append("| App | Trace | Replay | Inventory | Overall |")
        md.append("|---|---|---|---|---|")
        for app_id, v in summary["validation"].items():
            t = v.get("trace_verdict", {}).get("ok") if isinstance(v, dict) else None
            r = v.get("replay_verdict", {}).get("ok") if isinstance(v, dict) else None
            i = v.get("inventory_verdict", {}).get("ok") if isinstance(v, dict) else None
            ov = v.get("ok") if isinstance(v, dict) else False
            md.append(
                f"| `{app_id}` | {'PASS' if t else 'FAIL'} | "
                f"{'PASS' if r else 'FAIL'} | "
                f"{'PASS' if i else 'FAIL'} | "
                f"{'PASS' if ov else 'FAIL'} |"
            )
        md.append("")

    if "negative_controls" in summary:
        md.append("## Negative controls (W4 — tampering must be caught)")
        md.append("")
        md.append("| App | Caught | Total | All Caught |")
        md.append("|---|---:|---:|---|")
        for app_id, s in summary["negative_controls"].items():
            md.append(
                f"| `{app_id}` | {s.get('caught', '?')} | {s.get('total', '?')} | "
                f"{'PASS' if s.get('all_caught') else 'FAIL'} |"
            )
        md.append("")

    if "write_sovereignty" in summary:
        ws = summary["write_sovereignty"]
        md.append("## Write sovereignty (W4 — ADG structural)")
        md.append("")
        md.append(f"- Verdict: **{'PASS' if ws.get('ok') else 'FAIL'}**")
        if ws.get("fail_reasons"):
            md.append("- Fail reasons:")
            for r in ws["fail_reasons"]:
                md.append(f"  - {r}")
        md.append("")

    if args.negative_controls or args.write_sovereignty:
        md.extend(["## Out of scope (W4)", "", "- CI gate wiring → W5"])
    elif args.validate:
        md.extend(
            [
                "## Out of scope (W3)",
                "",
                "- Negative controls + write sovereignty + tests → W4",
                "- CI gate wiring → W5",
            ]
        )
    else:
        md.extend(
            [
                "## Out of scope (W2)",
                "",
                "- Trace/replay/artifact validators → W3",
                "- Negative controls + write sovereignty + tests → W4",
                "- CI gate wiring → W5",
            ]
        )
    (export_root / "proof_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
