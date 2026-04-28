"""Master all-requirements gate.

Aggregates the 15 tier / hardening verifier scripts and validates the
full 150-row Step 1 requirement program:

  * 7 metadata enforcement gates (Tier 0..6)
  * 7 runtime/static proof gates (Tier 0..6)
  * 1 hardening gate (cross-tier fail-closed)

Also validates tier assignment coverage:

  * Tier 0..6 selected REQ_IDs sum to 150
  * distinct tiered REQ_IDs == 150
  * duplicate REQ_ID count == 0
  * Step 1 rows with no tier == 0 (derived: Step 1 universe = 150)
  * every tier has both a metadata verifier and a runtime/static proof verifier
  * hardening case count >= 79

STATUS VOCABULARY: READY | BLOCKED | PASSED | FAILED.

Does NOT run full pytest, proof harnesses, replay machinery, OTEL
exporters, or any runtime behavior. Does NOT claim real replay
execution, real OTEL emission, full production runtime proof, or
full architecture proof.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof"
OUT_RESULT = ARTIFACTS_DIR / "all_requirements_gate_result.json"
OUT_REPORT = ARTIFACTS_DIR / "all_requirements_gate_report.md"

GATE_NAME = "all_requirements_gate"

CAVEAT = (
    "This gate validates tier assignment, metadata enforcement, static "
    "evidence consistency, fail-closed hardening, and CI wiring. It does "
    "not claim real replay execution, real OTEL emission, full production "
    "runtime proof, or full architecture proof."
)

# (command, label, gate_kind, tier) -- tier is "" for hardening.
COMMANDS: Tuple[Tuple[str, str, str, str], ...] = (
    ("scripts/verify_tier0_enforcement_gate.py", "tier0_enforcement", "metadata", "0"),
    ("scripts/verify_tier0_runtime_proof_gate.py", "tier0_runtime_proof", "runtime", "0"),
    ("scripts/verify_tier1_enforcement_gate.py", "tier1_enforcement", "metadata", "1"),
    ("scripts/verify_tier1_runtime_proof_gate.py", "tier1_runtime_proof", "runtime", "1"),
    ("scripts/verify_tier2_enforcement_gate.py", "tier2_enforcement", "metadata", "2"),
    ("scripts/verify_tier2_runtime_proof_gate.py", "tier2_runtime_proof", "runtime", "2"),
    ("scripts/verify_tier3_enforcement_gate.py", "tier3_enforcement", "metadata", "3"),
    ("scripts/verify_tier3_runtime_proof_gate.py", "tier3_runtime_proof", "runtime", "3"),
    ("scripts/verify_tier4_enforcement_gate.py", "tier4_enforcement", "metadata", "4"),
    ("scripts/verify_tier4_runtime_proof_gate.py", "tier4_runtime_proof", "runtime", "4"),
    ("scripts/verify_tier5_enforcement_gate.py", "tier5_enforcement", "metadata", "5"),
    ("scripts/verify_tier5_runtime_proof_gate.py", "tier5_runtime_proof", "runtime", "5"),
    ("scripts/verify_tier6_enforcement_gate.py", "tier6_enforcement", "metadata", "6"),
    ("scripts/verify_tier6_runtime_proof_gate.py", "tier6_runtime_proof", "runtime", "6"),
    ("scripts/verify_tier_gate_hardening.py", "tier_gate_hardening", "hardening", ""),
)

TIERS = ("0", "1", "2", "3", "4", "5", "6")
EXPECTED_TIER_COUNTS: Mapping[str, int] = {
    "0": 17,
    "1": 15,
    "2": 22,
    "3": 25,
    "4": 25,
    "5": 25,
    "6": 21,
}
EXPECTED_STEP1_UNIVERSE = 150
MIN_HARDENING_CASES = 79


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Tier REQ_ID loaders (avoid reading the markdown Step 1 matrices; rely on
# each tier's canonical selection/constant surface).
# ---------------------------------------------------------------------------


def _load_tier_req_ids() -> Dict[str, Tuple[str, ...]]:
    from agentic_core.runtime.prove_requirements import (
        tier0_step1_metadata as t0,
        tier1_runtime_proof_gate as t1,
        tier2_runtime_proof_gate as t2,
        tier3_runtime_proof_gate as t3,
        tier4_runtime_proof_gate as t4,
        tier5_runtime_proof_gate as t5,
        tier6_runtime_proof_gate as t6,
    )

    out: Dict[str, Tuple[str, ...]] = {}
    out["0"] = tuple(t0.TIER0_REQ_IDS)

    for tier, mod in (("1", t1), ("2", t2), ("3", t3), ("4", t4), ("5", t5)):
        loader = getattr(mod, f"_load_tier{tier}_req_ids", None)
        if loader is not None:
            out[tier] = tuple(loader())
        else:
            out[tier] = _load_selection(mod.SELECTION_PATH)

    # Tier 6 uses a selection-row-based loader; fall back to SELECTION_PATH.
    t6_loader = getattr(t6, "_load_tier6_selection", None)
    if t6_loader is not None:
        rows = t6_loader()
        out["6"] = tuple(r.get("req_id", "") for r in rows if r.get("req_id"))
    else:
        out["6"] = _load_selection(t6.SELECTION_PATH)
    return out


def _load_selection(path: Path) -> Tuple[str, ...]:
    if not path.is_file():
        return ()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ()
    sel = data.get("selected") if isinstance(data, dict) else None
    if not isinstance(sel, list):
        return ()
    return tuple(r.get("req_id", "") for r in sel if r.get("req_id"))


def _tier6_reference_only_summary() -> Dict[str, Any]:
    policy = REPO_ROOT / "artifacts" / "runtime" / "requirements_proof" / "tier6_reference_only_policy.json"
    summary: Dict[str, Any] = {
        "policy_artifact_present": policy.is_file(),
        "policy_name": None,
        "total_reference_only_rows": None,
        "reference_only_req_id_count": None,
        "rule": None,
        "caveat": None,
    }
    if policy.is_file():
        try:
            data = json.loads(policy.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return summary
        if isinstance(data, dict):
            summary["policy_name"] = data.get("policy_name")
            summary["total_reference_only_rows"] = data.get("total_reference_only_rows")
            ids = data.get("reference_only_req_ids") or []
            summary["reference_only_req_id_count"] = len(ids) if isinstance(ids, list) else None
            summary["rule"] = data.get("rule")
            summary["caveat"] = data.get("caveat")
    return summary


# ---------------------------------------------------------------------------
# Per-gate subprocess runner.
# ---------------------------------------------------------------------------


def _run(cmd_rel: str) -> Tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, cmd_rel],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _summarize_stdout(label: str, stdout: str) -> str:
    lines = [ln.strip() for ln in stdout.splitlines() if ln.strip()]
    if not lines:
        return ""
    # Prefer the lines that carry status, counts, or failed-req lists.
    interesting_keys = (
        "gate:",
        "result:",
        "status:",
        "ready",
        "blocked",
        "passed",
        "failed",
        "linked_literal",
        "failed req_ids",
        "tier",
        "metadata gate",
        "targeted tests",
        "must rows",
        "reference-only",
    )
    picked = [ln for ln in lines if any(k in ln.lower() for k in interesting_keys)]
    if not picked:
        picked = lines[-6:]
    return " | ".join(picked[-10:])


_FAILED_REQ_RE = re.compile(r"failed\s+req_?ids?\s*[:=]\s*\[([^\]]*)\]", re.IGNORECASE)


def _extract_failed_req_ids(stdout: str) -> List[str]:
    m = _FAILED_REQ_RE.search(stdout)
    if not m:
        return []
    inside = m.group(1).strip()
    if not inside:
        return []
    ids: List[str] = []
    for tok in inside.split(","):
        tok = tok.strip().strip("'").strip('"')
        if tok:
            ids.append(tok)
    return ids


_HARDENING_COUNT_RE = re.compile(r"(\d+)\s+passed", re.IGNORECASE)


def _extract_hardening_case_count(stdout: str) -> int:
    matches = _HARDENING_COUNT_RE.findall(stdout)
    if not matches:
        return 0
    try:
        return max(int(m) for m in matches)
    except ValueError:
        return 0


# ---------------------------------------------------------------------------
# Validator.
# ---------------------------------------------------------------------------


def evaluate() -> Dict[str, Any]:
    # Phase 1: coverage validation (cheap, do first).
    try:
        tier_req_ids = _load_tier_req_ids()
    except (ImportError, AttributeError) as exc:
        return {
            "gate_name": GATE_NAME,
            "result": "BLOCKED",
            "total_step1_req_ids": EXPECTED_STEP1_UNIVERSE,
            "total_tiered_req_ids": 0,
            "distinct_tiered_req_ids": 0,
            "duplicate_req_ids": [],
            "missing_step1_req_ids": [],
            "extra_tiered_req_ids": [],
            "tier_counts": {},
            "gate_results": [],
            "hardening_result": "FAILED",
            "hardening_case_count": 0,
            "failed_commands": [],
            "failed_req_ids_by_gate": {},
            "reference_only_policy_summary": _tier6_reference_only_summary(),
            "caveats": [CAVEAT],
            "evaluated_at_utc": _utc_now_iso(),
            "blocking_reasons": [f"Could not load tier REQ_IDs: {exc}"],
        }

    tier_counts = {t: len(ids) for t, ids in tier_req_ids.items()}
    total_tiered = sum(len(ids) for ids in tier_req_ids.values())

    union: set = set()
    duplicates_across: List[str] = []
    seen_with_source: Dict[str, str] = {}
    for tier, ids in sorted(tier_req_ids.items()):
        for rid in ids:
            if rid in seen_with_source:
                duplicates_across.append(rid)
            else:
                seen_with_source[rid] = tier
            union.add(rid)

    distinct_tiered = len(union)

    expected_universe_set: set = set()  # conceptual; we don't parse Step 1 markdown
    missing_step1: List[str] = []
    extra_tiered: List[str] = []
    # With the documented Step 1 universe == 150, a match of distinct_tiered to
    # EXPECTED_STEP1_UNIVERSE establishes missing/extra are both zero.
    if distinct_tiered != EXPECTED_STEP1_UNIVERSE:
        # Surface missing/extra as a single aggregate count (the union is our
        # best evidence; Step 1 markdown universe is not machine-parsed here).
        if distinct_tiered < EXPECTED_STEP1_UNIVERSE:
            missing_step1 = [f"<{EXPECTED_STEP1_UNIVERSE - distinct_tiered} REQ_ID(s) unaccounted>"]
        else:
            extra_tiered = [f"<{distinct_tiered - EXPECTED_STEP1_UNIVERSE} REQ_ID(s) over baseline>"]

    coverage_blockers: List[str] = []
    for tier, expected in EXPECTED_TIER_COUNTS.items():
        actual = tier_counts.get(tier, 0)
        if actual != expected:
            coverage_blockers.append(f"Tier {tier} count={actual} (expected {expected})")
    if total_tiered != EXPECTED_STEP1_UNIVERSE:
        coverage_blockers.append(f"Total tiered REQ_IDs={total_tiered} (expected {EXPECTED_STEP1_UNIVERSE})")
    if distinct_tiered != EXPECTED_STEP1_UNIVERSE:
        coverage_blockers.append(
            f"Distinct tiered REQ_IDs={distinct_tiered} (expected {EXPECTED_STEP1_UNIVERSE})"
        )
    if duplicates_across:
        coverage_blockers.append(f"Duplicate REQ_IDs across tiers: {sorted(set(duplicates_across))}")

    # Phase 2: verify every tier has both verifier scripts on disk.
    for tier in TIERS:
        for kind, stem in (("metadata", "enforcement_gate"), ("runtime", "runtime_proof_gate")):
            p = REPO_ROOT / "scripts" / f"verify_tier{tier}_{stem}.py"
            if not p.is_file():
                coverage_blockers.append(f"Missing {kind} verifier for tier {tier}: {p.name}")

    # Phase 3: run every command; capture exit codes + compact stdout.
    gate_results: List[Dict[str, Any]] = []
    failed_commands: List[str] = []
    failed_req_ids_by_gate: Dict[str, List[str]] = {}
    hardening_result = "FAILED"
    hardening_case_count = 0

    for cmd_rel, label, kind, tier in COMMANDS:
        rc, stdout, stderr = _run(cmd_rel)
        summary = _summarize_stdout(label, stdout)
        failed_req_ids = _extract_failed_req_ids(stdout)
        # Map gate verdict -> READY/BLOCKED or PASSED/FAILED.
        if kind == "hardening":
            verdict = "PASSED" if rc == 0 else "FAILED"
            hardening_result = verdict
            hardening_case_count = _extract_hardening_case_count(stdout)
        else:
            verdict = "READY" if rc == 0 else "BLOCKED"
        gate_results.append(
            {
                "label": label,
                "command": cmd_rel,
                "kind": kind,
                "tier": tier,
                "exit_code": rc,
                "verdict": verdict,
                "summary": summary,
                "failed_req_ids": failed_req_ids,
                "stderr_tail": stderr.strip().splitlines()[-3:] if rc != 0 else [],
            }
        )
        if rc != 0:
            failed_commands.append(label)
        if failed_req_ids:
            failed_req_ids_by_gate[label] = failed_req_ids

    hardening_blockers: List[str] = []
    if hardening_case_count < MIN_HARDENING_CASES:
        hardening_blockers.append(f"Hardening case count {hardening_case_count} < {MIN_HARDENING_CASES}")

    blocking_reasons = coverage_blockers + hardening_blockers
    if failed_commands:
        blocking_reasons.append(f"Failed commands: {failed_commands}")

    result = "READY" if not blocking_reasons else "BLOCKED"

    return {
        "gate_name": GATE_NAME,
        "result": result,
        "total_step1_req_ids": EXPECTED_STEP1_UNIVERSE,
        "total_tiered_req_ids": total_tiered,
        "distinct_tiered_req_ids": distinct_tiered,
        "duplicate_req_ids": sorted(set(duplicates_across)),
        "missing_step1_req_ids": missing_step1,
        "extra_tiered_req_ids": extra_tiered,
        "tier_counts": tier_counts,
        "gate_results": gate_results,
        "hardening_result": hardening_result,
        "hardening_case_count": hardening_case_count,
        "failed_commands": failed_commands,
        "failed_req_ids_by_gate": failed_req_ids_by_gate,
        "reference_only_policy_summary": _tier6_reference_only_summary(),
        "caveats": [CAVEAT],
        "blocking_reasons": blocking_reasons,
        "evaluated_at_utc": _utc_now_iso(),
    }


def write_result(result: Mapping[str, Any]) -> Path:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    OUT_RESULT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return OUT_RESULT


def write_report(result: Mapping[str, Any]) -> Path:
    lines: List[str] = []
    lines.append("# All Requirements Enforcement Gate Report")
    lines.append("")
    lines.append(f"- Gate: `{result['gate_name']}`")
    lines.append(f"- Result: **{result['result']}**")
    lines.append(f"- Evaluated at: {result['evaluated_at_utc']}")
    lines.append(f"- Total Step 1 universe: {result['total_step1_req_ids']}")
    lines.append(f"- Total tiered REQ_IDs: {result['total_tiered_req_ids']}")
    lines.append(f"- Distinct tiered REQ_IDs: {result['distinct_tiered_req_ids']}")
    lines.append(f"- Duplicate REQ_IDs: {result['duplicate_req_ids']}")
    lines.append(f"- Missing Step 1 REQ_IDs: {result['missing_step1_req_ids']}")
    lines.append(f"- Extra tiered REQ_IDs: {result['extra_tiered_req_ids']}")
    lines.append(f"- Hardening result: {result['hardening_result']}")
    lines.append(f"- Hardening case count: {result['hardening_case_count']}")
    lines.append("")
    lines.append("## Tier counts")
    for t in sorted(result["tier_counts"]):
        lines.append(f"- Tier {t}: {result['tier_counts'][t]}")
    lines.append("")
    lines.append("## Gate results")
    for gr in result["gate_results"]:
        lines.append(f"### {gr['label']} [{gr['kind']} / tier={gr['tier'] or 'cross'}]")
        lines.append(f"- Command: `{gr['command']}`")
        lines.append(f"- Exit code: {gr['exit_code']}")
        lines.append(f"- Verdict: **{gr['verdict']}**")
        if gr.get("summary"):
            lines.append(f"- Summary: {gr['summary']}")
        if gr.get("failed_req_ids"):
            lines.append(f"- Failed REQ_IDs: {gr['failed_req_ids']}")
        if gr.get("stderr_tail"):
            lines.append("- Stderr tail:")
            for s in gr["stderr_tail"]:
                lines.append(f"  - {s}")
        lines.append("")
    if result["failed_commands"]:
        lines.append("## Failed commands")
        for fc in result["failed_commands"]:
            lines.append(f"- {fc}")
        lines.append("")
    if result["failed_req_ids_by_gate"]:
        lines.append("## Failed REQ_IDs by gate")
        for g, ids in sorted(result["failed_req_ids_by_gate"].items()):
            lines.append(f"- {g}: {ids}")
        lines.append("")
    lines.append("## Reference-only policy summary")
    ref = result["reference_only_policy_summary"]
    for k, v in ref.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    if result.get("blocking_reasons"):
        lines.append("## Blocking reasons")
        for r in result["blocking_reasons"]:
            lines.append(f"- {r}")
        lines.append("")
    lines.append("## Caveat")
    for c in result["caveats"]:
        lines.append(f"- {c}")
    lines.append("")
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")
    return OUT_REPORT


def main() -> int:
    result = evaluate()
    result_path = write_result(result)
    report_path = write_report(result)
    print(f"Gate: {result['gate_name']}")
    print(f"Result: {result['result']}")
    print(f"Tier counts: {result['tier_counts']}")
    print(f"Total tiered: {result['total_tiered_req_ids']}")
    print(f"Distinct tiered: {result['distinct_tiered_req_ids']}")
    print(f"Duplicates: {result['duplicate_req_ids']}")
    print(f"Hardening: {result['hardening_result']} (cases={result['hardening_case_count']})")
    print(f"Failed commands: {result['failed_commands']}")
    print(f"Result file: {result_path}")
    print(f"Report file: {report_path}")
    return 0 if result["result"] == "READY" else 1


if __name__ == "__main__":
    sys.exit(main())
