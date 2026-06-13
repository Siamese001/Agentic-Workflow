"""Absorb the current floor into wiring_ci ratchet baselines.

Designed-mechanism counterpart to ``--regenerate-baseline`` flags on the
file-counter gates (``check_config_references.py`` /
``check_lifecycle_pairs.py``). The wiring_ci ratchets in
``ops_scripts/ci/baselines/wiring_*_ratchet.json`` are a single-int
``count`` ceiling: ``current_violations <= baseline.count`` = pass.

When the floor moves (legitimate refactor that introduces violations
faster than they are paid down), the gate signals "regressed" and exits
non-zero. The designed remediation is to absorb the new floor into the
baseline so the gate continues to catch *future* regressions beyond it.

This script:

  1. Reads the latest ``artifacts/adg/adg_gate_results_*.json``.
  2. For every row with ``classification == 'regressed'`` AND
     ``owner == 'wiring_ci'`` (file-backed external baseline), writes the
     current count to its baseline file.
  3. Appends a structured ``loosen_history`` entry with timestamp,
     snapshot id, ``from`` count, ``to`` count, and a free-text reason.
     Mirrors the existing ``tighten_history`` schema for symmetry.
  4. Resets ``zero_run_streak`` to 0 (auto-promotion logic must restart).
  5. Updates ``last_run_at`` and ``last_run_snapshot``.

Out of scope:

  * ``adg_gates``-owned ratchets (``owner == 'adg_gates'``) — those are
    auto-managed by ``ADGGateBase._compute_ratchet`` and have key-level
    rather than count-level baselines under ``artifacts/adg/ci_ratchets/``.
    They need per-gate investigation, not bulk absorb.
  * BLOCK-class gates — those have no baseline; they require real fixes.

Usage::

    python tools/reports/absorb_ratchet_floor.py --reason "<why>"
    python tools/reports/absorb_ratchet_floor.py --dry-run
"""

from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
GATE_RESULTS_GLOB = "artifacts/adg/adg_gate_results_*.json"
BASELINE_DIR = REPO / "ops_scripts" / "ci" / "baselines"

# gate_id -> baseline filename. Mirrors the canonical name_map in
# ops_scripts/ci/adg_gates/run.py:_load_baseline. Keep in sync.
WIRING_CI_BASELINE_FILES: dict[str, str] = {
    "A3_dead_public_symbol_ratchet": "wiring_dead_symbol_ratchet.json",
    "E1_trace_stub_module": "wiring_trace_stub_ratchet.json",
    "L2_lpg_drift_ratchet": "wiring_lpg_drift_ratchet.json",
    "M1_module_loc_ratchet": "wiring_module_loc_ratchet.json",
    "S2_uwg_bypass_ratchet": "wiring_uwg_bypass_ratchet.json",
    "S4_unused_imports_ratchet": "wiring_unused_imports_ratchet.json",
    "G_REACH_l0_reachability": "wiring_graph_reach_ratchet.json",
    "G_ISLAND_connected_components": "wiring_graph_island_ratchet.json",
    "G_WATCHLIST_DELTA_hotspot_regressions": "wiring_graph_watchlist_delta_ratchet.json",
    "B2_layer_skip_ratchet": "wiring_layer_skip_ratchet.json",
    "Q2_cyclomatic_complexity_ratchet": "wiring_cyclomatic_complexity_ratchet.json",
    "C3_silent_writes_ratchet": "wiring_silent_writes_ratchet.json",
    "C4_policy_without_audit_ratchet": "wiring_policy_without_audit_ratchet.json",
    "C5_unresolved_callsites_ratchet": "wiring_unresolved_callsites_ratchet.json",
    "I1_exit_disposition_ratchet": "wiring_exit_disposition_ratchet.json",
    "I2_replay_surface_gaps_ratchet": "wiring_replay_surface_gaps_ratchet.json",
    "O_tool_call_parity_ratchet": "wiring_tool_call_parity_ratchet.json",
    "N_guardrail_separation_ratchet": "wiring_guardrail_separation_ratchet.json",
    "M_taint_actionable_ratchet": "wiring_taint_actionable_ratchet.json",
    "P_structured_output_ratchet": "wiring_structured_output_ratchet.json",
    "F1_untyped_seam_ratchet": "wiring_untyped_seam_ratchet.json",
    "F2_broken_contract_ratchet": "wiring_broken_contract_ratchet.json",
    "H1_new_orphans_delta_ratchet": "wiring_new_orphans_delta_ratchet.json",
    "H2_fanin_collapse_ratchet": "wiring_fanin_collapse_ratchet.json",
    "H4_mv_staleness_ratchet": "wiring_mv_staleness_ratchet.json",
}


def _latest_gate_results() -> Path:
    candidates = sorted(glob.glob(str(REPO / GATE_RESULTS_GLOB)))
    if not candidates:
        raise FileNotFoundError(f"no {GATE_RESULTS_GLOB} files found under {REPO}")
    return Path(candidates[-1])


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data: dict[str, Any] = json.load(fh)
    return data


def _save_json(path: Path, data: dict[str, Any]) -> None:
    content = json.dumps(data, indent=2) + "\n"
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)


def absorb(
    reason: str,
    dry_run: bool,
    margin: int = 0,
) -> int:
    gate_results_path = _latest_gate_results()
    print(f"[absorb_ratchet_floor] using gate results: {gate_results_path.relative_to(REPO)}")
    doc = _load_json(gate_results_path)
    snapshot = doc.get("snapshot", "unknown")
    now_iso = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")

    regressed_wiring = [
        g for g in doc["gates"]
        if g.get("classification") == "regressed" and g.get("owner") == "wiring_ci"
    ]
    if not regressed_wiring:
        print("[absorb_ratchet_floor] no wiring_ci ratchets are regressed; nothing to do.")
        return 0

    print(f"[absorb_ratchet_floor] {len(regressed_wiring)} regressed wiring_ci ratchet(s):")
    skipped: list[str] = []
    absorbed: list[tuple[str, int, int]] = []

    target_floor = lambda c: c + margin  # noqa: E731 -- tiny inline helper
    for gate in regressed_wiring:
        gate_id = gate["gate_id"]
        cur = int(gate["violation_count"])
        new_ceiling = target_floor(cur)
        prev = gate.get("baseline_count")
        filename = WIRING_CI_BASELINE_FILES.get(gate_id)
        if filename is None:
            print(f"  - SKIP {gate_id}: no baseline filename mapping")
            skipped.append(gate_id)
            continue
        bpath = BASELINE_DIR / filename
        if not bpath.exists():
            print(f"  - SKIP {gate_id}: baseline file missing {bpath.relative_to(REPO)}")
            skipped.append(gate_id)
            continue

        baseline = _load_json(bpath)
        old_count = int(baseline.get("count", prev or 0))
        if new_ceiling <= old_count:
            print(f"  - SKIP {gate_id}: current={cur} +margin={margin} already <= baseline={old_count}")
            continue

        loosen_entry = {
            "at": now_iso,
            "snapshot": snapshot,
            "from": old_count,
            "to": new_ceiling,
            "raw_violation_count": cur,
            "margin": margin,
            "reason": reason,
        }
        baseline["count"] = new_ceiling
        baseline.setdefault("loosen_history", []).append(loosen_entry)
        baseline["loosened_at"] = now_iso
        baseline["zero_run_streak"] = 0  # auto-promotion restarts
        baseline["last_run_at"] = now_iso
        baseline["last_run_snapshot"] = snapshot

        if dry_run:
            print(f"  - DRY {gate_id}: would absorb {old_count} -> {new_ceiling} (raw={cur}, margin=+{margin})")
        else:
            _save_json(bpath, baseline)
            print(f"  - DONE {gate_id}: absorbed {old_count} -> {new_ceiling} (raw={cur}, margin=+{margin}) ({bpath.name})")
        absorbed.append((gate_id, old_count, new_ceiling))

    print()
    print(f"[absorb_ratchet_floor] absorbed: {len(absorbed)} skipped: {len(skipped)}")
    if absorbed:
        delta = sum(cur - old for _, old, cur in absorbed)
        print(f"[absorb_ratchet_floor] total ceiling raise: +{delta} violations")
    if dry_run:
        print("[absorb_ratchet_floor] dry-run: no files written")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument(
        "--reason",
        required=False,
        default="finish-deferred-scope: absorb current floor; future regressions still caught",
        help="Free-text reason persisted in loosen_history audit trail.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing baseline files.",
    )
    parser.add_argument(
        "--margin",
        type=int,
        default=0,
        help=(
            "Pad the new ceiling by this many violations above the current "
            "count. Useful when the ADG generation itself produces small "
            "churn (~2-5 per run) and you want to avoid immediate re-trip."
        ),
    )
    args = parser.parse_args(argv)
    return absorb(args.reason, args.dry_run, args.margin)


if __name__ == "__main__":
    raise SystemExit(main())
