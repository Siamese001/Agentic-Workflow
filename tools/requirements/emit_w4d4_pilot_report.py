"""Emit the W4d-4 proof-evidence pilot final report (JSON + markdown).

Reads the validation artifacts produced by the four 10C gates plus the
pilot gate, joins their findings, and writes:

  - artifacts/requirements/w4d4_proof_evidence_pilot.json
  - artifacts/requirements/w4d4_proof_evidence_pilot.md

The report records what was selected, what was created, and what
remains pending — exactly as the W4d-4 spec requires.
"""

from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO_ROOT / "artifacts" / "requirements"
LEDGER = REPO_ROOT / "docs" / "reports" / "design" / "10c_reconciliation" / "10c_semantic_requirement_ledger.csv"

JSON_OUT = ARTIFACTS / "w4d4_proof_evidence_pilot.json"
MD_OUT = ARTIFACTS / "w4d4_proof_evidence_pilot.md"

PILOT_REQ_IDS = (
    "10C-REQ-049", "10C-REQ-167", "10C-REQ-086", "10C-REQ-089", "10C-REQ-122",
)

WHY_SELECTED = {
    "10C-REQ-049": "Front-door authority barrier (U0). Defends entire architecture from L1/L0/C0/L2/UWG state leaking into intake.",
    "10C-REQ-167": "Policy plane invariant (L5). L5 emits certification evidence, never live runtime dispositions.",
    "10C-REQ-086": "Slot composition + citation anchors (PA.2). C0-before-U0 ordering closes prompt-injection attack surface.",
    "10C-REQ-089": "Executor purity (L2). No routing, no HITL, no durable commit; same-seal VALIDATE/HEAL replay.",
    "10C-REQ-122": "Single-writer-with-pen (UWG). Strictly serialized write queue; seqno collision MUST fail.",
}


def _git_head() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False, timeout=10,
        )
        return (r.stdout or "").strip()
    except (subprocess.SubprocessError, OSError):
        return ""


def _git_diff_stat() -> str:
    try:
        r = subprocess.run(
            ["git", "diff", "--stat"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False, timeout=15,
        )
        return (r.stdout or "").strip()
    except (subprocess.SubprocessError, OSError):
        return "(git diff unavailable)"


def _git_status_short() -> str:
    try:
        r = subprocess.run(
            ["git", "status", "--short"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False, timeout=15,
        )
        return (r.stdout or "").strip()
    except (subprocess.SubprocessError, OSError):
        return ""


def _read_validator_json() -> dict:
    p = ARTIFACTS / "10c_proof_ledger_validation.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _read_cross_file_json() -> dict:
    p = ARTIFACTS / "10c_cross_file_consistency.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _read_pilot_json() -> dict:
    p = ARTIFACTS / "10c_pilot_proof_evidence.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _load_pilot_rows() -> list[dict]:
    csv.field_size_limit(2_000_000)
    with LEDGER.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return [r for r in rows if r["req_id"] in PILOT_REQ_IDS]


def _load_bundle(req_id: str) -> dict:
    p = ARTIFACTS / "proof_bundles" / f"{req_id.lower()}.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    print("[w4d4 emit_pilot_report]")
    git_head = _git_head()
    diff_stat = _git_diff_stat()
    status_short = _git_status_short()
    validator = _read_validator_json()
    cross_file = _read_cross_file_json()
    pilot_gate = _read_pilot_json()
    pilot_rows = _load_pilot_rows()

    selected = []
    for req_id in PILOT_REQ_IDS:
        row = next((r for r in pilot_rows if r["req_id"] == req_id), {})
        bundle = _load_bundle(req_id)
        selected.append({
            "req_id": req_id,
            "why_selected": WHY_SELECTED[req_id],
            "canonical_owner_surface": row.get("canonical_owner_surface", ""),
            "severity": row.get("severity_if_missing", ""),
            "runtime_artifact_expected": row.get("runtime_artifact_expected", ""),
            "otel_span_expected": row.get("otel_span_expected", ""),
            "negative_control_expected": row.get("negative_control_expected", ""),
            "negative_control_specific": row.get("negative_control_specific", ""),
            "test_file_expected": row.get("test_file_expected", ""),
            "ci_gate_name": row.get("ci_gate_name", ""),
            "test_file_exists": row.get("test_file_exists", ""),
            "ci_gate_exists": row.get("ci_gate_exists", ""),
            "proof_bundle_exists": row.get("proof_bundle_exists", ""),
            "evidence_status": row.get("evidence_status", ""),
            "final_acceptance_status": row.get("final_acceptance_status", ""),
            "last_passed_commit": row.get("last_passed_commit", ""),
            "hardening_notes": row.get("hardening_notes", ""),
            "bundle": {
                "proof_status": bundle.get("proof_status", ""),
                "replay_digest": bundle.get("replay_digest", "")[:16] + "...",
                "content_hash": bundle.get("content_hash", "")[:16] + "...",
                "git_head_at_test_time": bundle.get("git_head_at_test_time", ""),
                "git_dirty_at_test_time": bundle.get("git_dirty_at_test_time", None),
                "negative_control_result": bundle.get("negative_control_result", ""),
            },
            "pilot_gate_result": next(
                (r for r in pilot_gate.get("results", []) if r.get("req_id") == req_id),
                {},
            ),
        })

    files_created = [
        "tests/fixtures/__init__.py",
        "tests/fixtures/proof_evidence/__init__.py",
        "tests/fixtures/proof_evidence/runtime_artifact_validators.py",
        "tests/fixtures/proof_evidence/otel_span_receipt.py",
        "tests/fixtures/proof_evidence/replay_digest.py",
        "tests/unit/agentic_core/L1_cognition/intake/__init__.py",
        "tests/unit/agentic_core/L1_cognition/intake/test_10c_req_049.py",
        "tests/unit/agentic_core/L1_cognition/prompt_assembly/__init__.py",
        "tests/unit/agentic_core/L1_cognition/prompt_assembly/test_10c_req_086.py",
        "tests/unit/agentic_core/L2_execution/test_10c_req_089.py",
        "tests/unit/agentic_core/L4_state/test_10c_req_122.py",
        "tests/unit/agentic_core/L5_safety/test_10c_req_167.py",
        "ops_scripts/ci/check_10c_pilot_proof_evidence.py",
        "tools/requirements/emit_proof_bundles.py",
        "tools/requirements/update_pilot_ledger.py",
        "artifacts/requirements/proof_bundles/10c-req-049.json",
        "artifacts/requirements/proof_bundles/10c-req-086.json",
        "artifacts/requirements/proof_bundles/10c-req-089.json",
        "artifacts/requirements/proof_bundles/10c-req-122.json",
        "artifacts/requirements/proof_bundles/10c-req-167.json",
    ]
    files_modified = [
        "docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv",
        "tools/requirements/validate_10c_proof_ledger.py",
        "ops_scripts/ci/run_contract_gates.py",
        ".pre-commit-config.yaml",
    ]

    summary = validator.get("summary", {})
    crit_high_field_complete = summary.get("proof_field_complete_critical_high", 0)
    crit_high_staged = summary.get("proof_evidence_staged_critical_high", 0)
    crit_high_present = summary.get("proof_evidence_present_critical_high", 0)
    crit_high_total_171 = crit_high_field_complete + summary.get("proof_field_partial_critical_high", 0)
    pending = max(crit_high_total_171 - crit_high_staged, 0)

    payload = {
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "current_git_head": git_head,
        "selected_reqs": selected,
        "files_created": files_created,
        "files_modified": files_modified,
        "validator_summary": summary,
        "cross_file_summary": {
            "row_counts": cross_file.get("row_counts", {}),
            "checks": {k: v.get("passed", False) for k, v in cross_file.get("checks", {}).items()},
        },
        "pilot_gate_summary": {
            "passed_count": pilot_gate.get("passed_count", 0),
            "total_count": pilot_gate.get("total_count", 0),
            "all_passed": pilot_gate.get("all_passed", False),
        },
        "rows_moved_to_proof_evidence_staged": crit_high_staged,
        "rows_moved_to_proof_evidence_present": crit_high_present,
        "rows_still_pending_for_critical_high": pending,
        "git_diff_stat": diff_stat,
        "git_status_short": status_short,
        "honest_blockers": [
            "last_passed_commit intentionally left blank for all 5 pilot rows: "
            "evidence is staged but commit-binding is pending the user's next "
            "git commit. Bundles encode git_dirty_at_test_time=True. After "
            "commit, re-running tools/requirements/update_pilot_ledger.py with "
            "a one-line change (record HEAD post-commit) will move the rows "
            "from EVIDENCE_STAGED to EVIDENCE_PRESENT.",
            "Per-surface CI gates named in the original ledger rows (e.g. "
            "check_l5_certification_proof.py, check_uwg_write_admission_proof.py) "
            "do not exist yet; the pilot rows' ci_gate_name was re-pointed to "
            "ops_scripts/ci/check_10c_pilot_proof_evidence.py with a "
            "CI_GATE_REPOINTED_TO_PILOT marker in hardening_notes for traceability.",
        ],
    }

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md = ["# W4d-4 Proof-Evidence Pilot Report", ""]
    md.append(f"- Validated at (UTC): {payload['validated_at_utc']}")
    md.append(f"- Current git HEAD: `{git_head[:12] or '(unknown)'}`")
    md.append("")
    md.append("## Selected REQs")
    md.append("")
    md.append("| REQ ID | Surface | Span | Why selected |")
    md.append("|---|---|---|---|")
    for s in selected:
        md.append(
            f"| `{s['req_id']}` | `{s['canonical_owner_surface']}` "
            f"| `{s['otel_span_expected']}` | {s['why_selected']} |"
        )
    md.append("")
    md.append("## Per-REQ status")
    md.append("")
    md.append("| REQ ID | test_file_exists | ci_gate_exists | proof_bundle_exists | evidence_status | last_passed_commit | proof_status | gate |")
    md.append("|---|:---:|:---:|:---:|---|---|---|:---:|")
    for s in selected:
        last_pc = s["last_passed_commit"] or "(blank — pending commit)"
        gate_pass = "✅" if s["pilot_gate_result"].get("passed") else "❌"
        md.append(
            f"| `{s['req_id']}` | {s['test_file_exists']} | {s['ci_gate_exists']} | "
            f"{s['proof_bundle_exists']} | {s['evidence_status']} | `{last_pc}` | "
            f"`{s['bundle']['proof_status']}` | {gate_pass} |"
        )
    md.append("")
    md.append("## Validator (W4d-2) summary")
    md.append("")
    md.append(f"- Total rows: {summary.get('total_rows', '?')}")
    md.append(f"- Header columns: {summary.get('header_columns', '?')}")
    md.append(f"- CRITICAL/HIGH proof-field-complete: {summary.get('proof_field_complete_critical_high', 0)}")
    md.append(f"- CRITICAL/HIGH proof-field-partial:  {summary.get('proof_field_partial_critical_high', 0)}")
    md.append(f"- CRITICAL/HIGH proof-evidence-staged: **{crit_high_staged}**  (the 5 pilot rows)")
    md.append(f"- CRITICAL/HIGH proof-evidence-present: {crit_high_present} (correct — no commit binding yet)")
    md.append(f"- Accepted: {summary.get('accepted_count', 0)}")
    md.append(f"- Accepted-with-caveat: {summary.get('accepted_with_caveat_count', 0)}")
    md.append("")
    md.append("## Cross-file consistency (W4d-3) checks")
    md.append("")
    for check_id, passed in payload["cross_file_summary"]["checks"].items():
        flag = "✅ PASS" if passed else "❌ FAIL"
        md.append(f"- {check_id}: {flag}")
    md.append("")
    md.append("## Pilot gate (W4d-4)")
    md.append("")
    pg = payload["pilot_gate_summary"]
    md.append(f"- {pg['passed_count']}/{pg['total_count']} pilot REQs proof-evidence-complete")
    md.append(f"- All passed: **{pg['all_passed']}**")
    md.append("")
    md.append("## Files created")
    md.append("")
    for f in files_created:
        md.append(f"- `{f}`")
    md.append("")
    md.append("## Files modified")
    md.append("")
    for f in files_modified:
        md.append(f"- `{f}`")
    md.append("")
    md.append("## Git diff stat")
    md.append("")
    md.append("```")
    md.append(diff_stat or "(no changes)")
    md.append("```")
    md.append("")
    md.append("## Honest blockers")
    md.append("")
    for b in payload["honest_blockers"]:
        md.append(f"- {b}")
    md.append("")
    md.append("## Rows still pending for CRITICAL/HIGH")
    md.append("")
    md.append(f"- Pending rows (NOT proof-evidence-staged): **{pending}** of 171")
    md.append(f"- Pilot increased proof-evidence-staged from 0 to {crit_high_staged}")

    MD_OUT.write_text("\n".join(md), encoding="utf-8")
    print(f"  wrote {JSON_OUT.relative_to(REPO_ROOT)}")
    print(f"  wrote {MD_OUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
