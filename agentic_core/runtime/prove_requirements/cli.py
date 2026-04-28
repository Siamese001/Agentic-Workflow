"""
CLI entrypoint for the requirements proof system.

Phase 0 + Phase 1 are wired in this build; Phases 2-11 will be added in
subsequent commits behind explicit Author-Gate decisions.

Usage:
    python -m agentic_core.runtime.prove_requirements [--repo-root PATH] [--export DIR] \\
        [--sources FOLDER ...] [--scenario all]

Exit codes:
    0  -- Phase 0 and Phase 1 succeeded; artifacts written.
    2  -- Phase 0 validation failed (missing folders, empty folders, etc.).
    3  -- Phase 1 produced zero requirements (sanity check failure).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from agentic_core.runtime.prove_requirements.code_symbol_catalog import (
    build_catalog,
    file_count,
)
from agentic_core.runtime.prove_requirements.constants import REPO_ROOT
from agentic_core.runtime.prove_requirements.coverage_matrix_builder import (
    build_coverage_rows,
)
from agentic_core.runtime.prove_requirements.implementation_mapper import (
    build_mappings,
)
from agentic_core.runtime.prove_requirements.anti_bypass_negatives import NEGATIVES
from agentic_core.runtime.prove_requirements.otel_contract import (
    RUNTIME_SPAN_NAMES,
    validate_scenario_shape,
    validate_trace,
)
from agentic_core.runtime.prove_requirements.otel_harness import (
    SCENARIO_FNS,
    run_all_scenarios,
)
from agentic_core.runtime.prove_requirements.proof_report import write_proof_report
from agentic_core.runtime.prove_requirements.replay_engine import (
    replay_digest,
    run_full_replay_suite,
)
from agentic_core.runtime.prove_requirements.requirement_extractor import (
    extract_from_file,
)
from agentic_core.runtime.prove_requirements.source_manifest import (
    build_manifest,
    validate_manifest,
)
from agentic_core.runtime.prove_requirements.test_evidence_scanner import (
    scan_test_files_for_anchors,
)
from agentic_core.runtime.prove_requirements.writers import (
    write_coverage_matrix,
    write_implementation_map,
    write_manifest,
    write_requirements_index,
)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="agentic_core.runtime.prove_requirements",
        description=(
            "Build runtime requirements proof artifacts (Phase 0 + Phase 1). "
            "Subsequent phases (2-11) gated by Author-Gate."
        ),
    )
    p.add_argument(
        "--sources",
        action="append",
        default=None,
        help=(
            "Override one source folder. Repeat for multiple. "
            "Defaults to the canonical 12. NOTE: this build always validates "
            "against the canonical 12 — overrides are advisory only and used "
            "for testing."
        ),
    )
    p.add_argument(
        "--scenario",
        default="all",
        help="Reserved for Phase 8 E2E scenarios. Currently unused.",
    )
    p.add_argument(
        "--export",
        default="artifacts/runtime/requirements_proof",
        help="Export directory (relative to repo-root or absolute).",
    )
    p.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repo root override. Default: package-resolved repo root.",
    )
    return p


def _resolve_export_dir(repo_root: Path, export_arg: str) -> Path:
    p = Path(export_arg)
    if p.is_absolute():
        return p.resolve()
    return (repo_root / export_arg).resolve()


def _write_gaps(
    out_dir: Path,
    manifest: dict,
    record_count: int,
    impl_summary: dict | None = None,
    coverage_summary: dict | None = None,
    otel_summary: dict | None = None,
) -> None:
    lines: List[str] = [
        "# Requirements Proof — Gaps Remaining",
        "",
        "This document is the honest gap report for the current build of",
        "`agentic_core.runtime.prove_requirements`. It is written by the CLI",
        "after every successful Phase 0 + Phase 1 run.",
        "",
        f"- generated_at_utc: `{manifest['summary']['generated_at_utc']}`",
        f"- files_ingested: {manifest['summary']['file_count_ingested']}",
        f"- normative_requirements_extracted: {record_count}",
        "",
        "## Phases NOT delivered in this build",
        "",
        "| Phase | Description | Status |",
        "|---|---|---|",
        "| Phase 0 | Source manifest builder | DELIVERED |",
        "| Phase 1 | Normative requirement extractor | DELIVERED |",
        f"| Phase 2 | Map every requirement to code symbols (implementation_map.{{json,csv}}, missing_requirements.md) | {'DELIVERED' if impl_summary else 'NOT_STARTED'} |",
        f"| Phase 3 | Coverage matrix joining requirements + tests + OTEL + replay (coverage_matrix.{{json,csv,md}}) | {'DELIVERED' if coverage_summary else 'NOT_STARTED'} |",
        f"| Phase 4 | Implement runtime gaps with bounded edits per layer | {'CONTRACT_ONLY' if otel_summary else 'NOT_STARTED'} |",
        f"| Phase 5 | OTEL spans across U0/L1/L0/C0/PA/L3/L2/Exit/UWG/L6 with required attributes | {'CONTRACT_PLUS_HARNESS' if otel_summary else 'NOT_STARTED'} |",
        f"| Phase 6 | Deterministic replay (replay_run_1/2.json + replay_comparison.json) | {'DELIVERED' if otel_summary else 'NOT_STARTED'} |",
        f"| Phase 7 | Anti-bypass negative tests (30 invariants from spec) | {'DELIVERED' if otel_summary else 'NOT_STARTED'} |",
        f"| Phase 8 | E2E proof scenarios A/B/C/D | {'DELIVERED_VIA_HARNESS' if otel_summary else 'NOT_STARTED'} |",
        f"| Phase 9 | Full prove_requirements CLI (Phases 0-7 wired; Phase 4 wiring to live runtime pending) | {'PARTIAL' if otel_summary else 'PARTIAL'} |",
        f"| Phase 10 | 14 named tests in tests/runtime/ (7 of 14 delivered after this build) | PARTIAL |",
        f"| Phase 11 | Final response with all coverage statuses | {'PARTIAL' if coverage_summary else 'NOT_APPLICABLE_until_phase_3'} |",
        "",
        "## Honest status of all extracted requirements",
        "",
        (
            "Phase 0+1 records start at status=UNMAPPED in requirements_index.json. "
            "After Phase 2+3, the canonical status lives in coverage_matrix.json under "
            "the `coverage_status` field per row. PROVEN status remains gated on "
            "Phase 5 (OTEL), Phase 6 (replay), and Phase 7 (anti-bypass) evidence "
            "and is expected to be zero in this build."
        ),
        "",
        f"## Phase 2 implementation_map summary: `{impl_summary or 'not_yet_built'}`",
        "",
        f"## Phase 3 coverage_matrix summary: `{(coverage_summary or {}).get('by_coverage_status', 'not_yet_built')}`",
        "",
        f"## Phase 5 OTEL trace harness summary: `{otel_summary or 'not_yet_built'}`",
        "",
        (
            "Phase 5 in this build delivers the OTEL CONTRACT (26 canonical span "
            "names + required/conditional/optional attribute schema + parent graph) "
            "and a 4-scenario harness that emits a complete validated trace per "
            "scenario. The harness does NOT wire OTEL emission into the live "
            "runtime layers (L0_routing/L1_cognition/...). That wiring is a future "
            "Phase-4 sub-task gated by per-stage Author-Gate. Until then, OTEL "
            "evidence credits the *contract*, not the runtime."
        ),
        "",
        "## Test files NOT yet created",
        "",
        "- tests/runtime/test_intake_contract.py",
        "- tests/runtime/test_route_contract.py",
        "- tests/runtime/test_c0_evidence_contract.py",
        "- tests/runtime/test_l2_execution_seal.py",
        "- tests/runtime/test_exit_eval_control.py",
        "- tests/runtime/test_uwg_write_sovereignty.py",
        "- tests/runtime/test_l6_learning_firewall.py",
        "- tests/runtime/test_runtime_gates_g01_g29.py",
        "- tests/runtime/test_end_to_end_grounded_read.py",
        "- tests/runtime/test_requirements_coverage_matrix.py",
        "",
        "Test files DELIVERED in this build:",
        "",
        "- tests/runtime/test_source_manifest_integrity.py (Phase 0)",
        "- tests/runtime/test_requirements_index_completeness.py (Phase 1; covers source-line mapping equivalent to test_requirements_source_line_mapping.py)",
        "- tests/runtime/test_implementation_map_completeness.py (Phase 2)",
        "- tests/runtime/test_coverage_matrix_consistency.py (Phase 3)",
        "- tests/runtime/test_otel_trace_completeness.py (Phase 5 contract)",
        "- tests/runtime/test_deterministic_replay.py (Phase 6)",
        "- tests/runtime/test_anti_bypass_runtime_cheat_proof.py (Phase 7)",
        "",
        "## What changes are needed to flip a requirement to PROVEN",
        "",
        "1. Phase 2: locate the implementation symbol (file + line range).",
        "2. Phase 4: if missing, write the runtime code for the smallest",
        "   coherent change that satisfies the requirement without expanding",
        "   scope.",
        "3. Phase 5: ensure the runtime stage emits the required OTEL span",
        "   with the attribute set listed in the user spec.",
        "4. Phase 6: verify deterministic replay diff is empty for the digests",
        "   touched by this requirement.",
        "5. Phase 7: where applicable, ensure the negative bypass test fails",
        "   loudly when the invariant is broken.",
        "6. Phase 3: emit the row in coverage_matrix.{json,csv,md} with",
        "   status=PROVEN.",
        "",
        "Without all of the above, the record stays UNMAPPED, PARTIAL, or",
        "MISSING — the foolproof rule from the user spec ('Do not infer. Do",
        "not claim.') is enforced at the writer level.",
        "",
    ]
    (out_dir / "GAPS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    out_dir = _resolve_export_dir(repo_root, args.export)

    print(f"[prove_requirements] repo_root={repo_root}", file=sys.stderr)
    print(f"[prove_requirements] export_dir={out_dir}", file=sys.stderr)

    # Phase 0 -- source manifest
    print("[prove_requirements] Phase 0: build source manifest", file=sys.stderr)
    manifest = build_manifest(repo_root)
    write_manifest(manifest, out_dir)
    ok, errors = validate_manifest(manifest)
    print(
        f"[prove_requirements] Phase 0: files_ingested="
        f"{manifest['summary']['file_count_ingested']}",
        file=sys.stderr,
    )
    if not ok:
        print(f"[prove_requirements] Phase 0 FAIL: {errors}", file=sys.stderr)
        return 2

    # Phase 1 -- requirement extraction
    print(
        "[prove_requirements] Phase 1: extract normative requirements",
        file=sys.stderr,
    )
    files = manifest["files"]
    reporter = None
    try:
        from tools.progress_display import ProgressReporter  # guardian: allow-layer-violation -- CLI entry point legitimately imports operator-facing progress UI from tools/; keeps the prove_requirements core free of UI dependencies

        reporter = ProgressReporter(
            total=len(files),
            label="Extracting normative requirements",
            unit="file",
        )
    except ImportError:
        reporter = None

    all_records = []
    for entry in files:
        rel = entry["relative_path"]
        recs = extract_from_file(repo_root, rel)
        all_records.extend(recs)
        if reporter is not None:
            reporter.update(label=f"Extracted {Path(rel).name}")
    if reporter is not None:
        reporter.done()

    if not all_records:
        print(
            "[prove_requirements] Phase 1 FAIL: zero requirements extracted; "
            "this is a sanity-check failure given the source folders are non-empty.",
            file=sys.stderr,
        )
        return 3

    write_requirements_index(all_records, out_dir)
    print(
        f"[prove_requirements] Phase 1: requirements_extracted={len(all_records)}",
        file=sys.stderr,
    )

    # Phase 2 -- implementation_map
    print(
        "[prove_requirements] Phase 2: build code symbol catalog + map requirements",
        file=sys.stderr,
    )
    py_count = file_count(repo_root)
    print(
        f"[prove_requirements] Phase 2: scanning {py_count} python files for symbols",
        file=sys.stderr,
    )
    catalog = build_catalog(repo_root)
    print(
        f"[prove_requirements] Phase 2: catalog has {len(catalog)} unique symbol names",
        file=sys.stderr,
    )
    mappings = build_mappings(all_records, catalog)
    write_implementation_map(mappings, out_dir)
    impl_summary: dict[str, int] = {}
    for m in mappings:
        impl_summary[m.implementation_status] = impl_summary.get(m.implementation_status, 0) + 1
    print(
        f"[prove_requirements] Phase 2: implementation_map summary={impl_summary}",
        file=sys.stderr,
    )

    # Phase 3 -- coverage_matrix
    print(
        "[prove_requirements] Phase 3: scan tests + build coverage_matrix",
        file=sys.stderr,
    )
    matched_anchor_set: set[str] = set()
    for m in mappings:
        for a in m.matched_anchors:
            matched_anchor_set.add(a)
    test_index = scan_test_files_for_anchors(repo_root, matched_anchor_set)
    print(
        f"[prove_requirements] Phase 3: scanned tests; {len(test_index)} anchors have test references",
        file=sys.stderr,
    )
    coverage_rows = build_coverage_rows(all_records, mappings, test_index)
    write_coverage_matrix(coverage_rows, out_dir)
    coverage_summary: dict[str, int] = {}
    for row in coverage_rows:
        coverage_summary[row.coverage_status] = coverage_summary.get(row.coverage_status, 0) + 1
    print(
        f"[prove_requirements] Phase 3: coverage_matrix summary={coverage_summary}",
        file=sys.stderr,
    )

    # Phase 5 -- OTEL trace harness (contract-only; not wired to live runtime)
    print(
        "[prove_requirements] Phase 5: emit canonical OTEL traces for 4 scenarios",
        file=sys.stderr,
    )
    traces_dir = out_dir / "traces"
    trace_paths = run_all_scenarios(traces_dir)
    # Validate each trace immediately; refuse to claim Phase 5 success without it.
    trace_validation: dict[str, dict] = {}
    all_valid = True
    for scen, fpath in trace_paths.items():
        td = json.loads(Path(fpath).read_text(encoding="utf-8"))
        ok, errs = validate_trace(td)
        trace_validation[scen] = {
            "path": fpath,
            "ok": ok,
            "span_count": td.get("span_count"),
            "errors": errs,
        }
        if not ok:
            all_valid = False
            print(
                f"[prove_requirements] Phase 5 trace {scen} INVALID: {errs[:3]}",
                file=sys.stderr,
            )
    print(
        f"[prove_requirements] Phase 5: {len(trace_paths)} scenarios written; "
        f"all_valid={all_valid}; canonical span vocabulary size={len(RUNTIME_SPAN_NAMES)}",
        file=sys.stderr,
    )
    if not all_valid:
        # Trace contract violations are a hard fail -- Phase 5 cannot be claimed.
        return 4

    # Phase 6 -- deterministic replay. Run each scenario twice; compare digests.
    print(
        "[prove_requirements] Phase 6: replay each scenario pair-wise and diff digests",
        file=sys.stderr,
    )
    replay_dir = out_dir / "replay"
    replay_summary = run_full_replay_suite(SCENARIO_FNS, replay_dir)
    print(
        f"[prove_requirements] Phase 6: all_scenarios_match={replay_summary['all_scenarios_match']}; "
        f"per_scenario_match={replay_summary['per_scenario_match']}",
        file=sys.stderr,
    )
    if not replay_summary["all_scenarios_match"]:
        return 5

    # Phase 7 -- anti-bypass negatives. Drive every mutator and confirm at
    # least one detector fires for each.
    print(
        f"[prove_requirements] Phase 7: drive {len(NEGATIVES)} anti-bypass negatives",
        file=sys.stderr,
    )
    baseline_traces: dict[str, dict] = {}
    baseline_digests: dict[str, str] = {}
    for scen_name, fn in SCENARIO_FNS:
        t = fn().to_dict()
        baseline_traces[scen_name] = t
        baseline_digests[scen_name] = replay_digest(t)
    negatives_log: list[dict] = []
    escaped: list[str] = []
    for n in NEGATIVES:
        base = baseline_traces[n.scenario]
        mutated = n.mutator(base)
        ok_contract, errs_contract = validate_trace(mutated)
        ok_shape, errs_shape = validate_scenario_shape(mutated, n.scenario)
        try:
            mut_digest = replay_digest(mutated)
            replay_drift = mut_digest != baseline_digests[n.scenario]
        except (KeyError, TypeError, ValueError):
            replay_drift = True
        detected = (not ok_contract) or (not ok_shape) or replay_drift
        negatives_log.append({
            "code": n.code,
            "name": n.name,
            "scenario": n.scenario,
            "description": n.description,
            "detected": detected,
            "layers": {
                "contract_ok": ok_contract,
                "shape_ok": ok_shape,
                "replay_drift": replay_drift,
            },
            "contract_errors": errs_contract[:3] if errs_contract else [],
            "shape_errors": errs_shape[:3] if errs_shape else [],
        })
        if not detected:
            escaped.append(n.code)
    (out_dir / "anti_bypass_results.json").write_text(
        json.dumps(
            {
                "negatives_total": len(NEGATIVES),
                "negatives_detected": sum(1 for r in negatives_log if r["detected"]),
                "negatives_escaped": escaped,
                "results": negatives_log,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        f"[prove_requirements] Phase 7: {len(NEGATIVES) - len(escaped)}/{len(NEGATIVES)} "
        f"negatives detected; escaped={escaped}",
        file=sys.stderr,
    )
    if escaped:
        return 6

    # Honest gap report
    _write_gaps(
        out_dir,
        manifest,
        len(all_records),
        impl_summary={"by_implementation_status": impl_summary},
        coverage_summary={"by_coverage_status": coverage_summary},
        otel_summary={
            "scenarios": list(trace_paths.keys()),
            "span_vocabulary_size": len(RUNTIME_SPAN_NAMES),
            "validation": trace_validation,
        },
    )
    print(f"[prove_requirements] gap report written to {out_dir / 'GAPS.md'}", file=sys.stderr)

    # Phase 11 -- final aggregate proof_report.md
    report_path = write_proof_report(out_dir)
    print(f"[prove_requirements] Phase 11: proof_report.md written to {report_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
