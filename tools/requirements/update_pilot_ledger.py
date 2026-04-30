"""Update ledger rows for the W4d-4/W4d-5 pilot REQs only.

Two modes:
  --mode=staged  (W4d-4 default): set evidence_status=PROOF_PARTIAL,
                  last_passed_commit blank, hardening_notes +=
                  PROOF_READY_PENDING_COMMIT:<head>.
  --mode=bound   (W4d-5): set evidence_status=PROOF_PRESENT,
                  final_acceptance_status=ACCEPTED, implementation_status=
                  IMPLEMENTED, last_passed_commit=<current head>,
                  hardening_notes += EVIDENCE_BOUND_TO_COMMIT:<head>
                  (supersedes PROOF_READY_PENDING_COMMIT).

The bound mode is REJECTED if:
  - the proof-binding scope is dirty
  - any bundle file is missing
  - any bundle says proof_status != EVIDENCE_PRESENT
  - any bundle's content_hash fails tamper check

This script is idempotent. It writes to disk.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "docs" / "reports" / "design" / "10c_reconciliation" / "10c_semantic_requirement_ledger.csv"
BUNDLES_DIR = REPO_ROOT / "artifacts" / "requirements" / "proof_bundles"

# Allow direct script invocation in addition to module invocation.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.requirements._binding_scope import (
    CRITICAL_BINDING_SCOPE as _CRITICAL_BINDING_SCOPE,
    CRITICAL_REQ_IDS as _CRITICAL_REQ_IDS,
)

# SSOT-imported from tools/requirements/_binding_scope.py.
PILOT_REQ_IDS = frozenset(_CRITICAL_REQ_IDS)
PILOT_BINDING_SCOPE: tuple[str, ...] = _CRITICAL_BINDING_SCOPE


def _git_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False, timeout=10,
        )
        return (result.stdout or "").strip()
    except (subprocess.SubprocessError, OSError):
        return ""


def _path_exists(rel_path: str) -> str:
    p = (rel_path or "").strip()
    if not p:
        return ""
    return "true" if (REPO_ROOT / p).exists() else "false"


def _scoped_dirty_paths() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", *PILOT_BINDING_SCOPE],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False, timeout=10,
        )
    except (subprocess.SubprocessError, OSError):
        return ["__git_unavailable__"]
    return [line for line in (result.stdout or "").splitlines() if line.strip()]


def _deterministic_digest(payload: object) -> str:
    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
        default=str, ensure_ascii=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _validate_bundle_for_binding(req_id: str, current_head: str) -> list[str]:
    """Return list of error messages; empty list means bundle is binding-ready."""
    p = BUNDLES_DIR / f"{req_id.lower()}.json"
    if not p.exists():
        return [f"{req_id}: bundle missing at {p.relative_to(REPO_ROOT)}"]
    try:
        b = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{req_id}: bundle unreadable: {exc}"]

    errs: list[str] = []
    if b.get("req_id") != req_id:
        errs.append(f"{req_id}: bundle.req_id mismatch: '{b.get('req_id')}'")
    if b.get("proof_status") != "EVIDENCE_PRESENT":
        errs.append(f"{req_id}: bundle.proof_status='{b.get('proof_status')}', need EVIDENCE_PRESENT")
    if b.get("git_dirty_at_test_time") is not False:
        errs.append(f"{req_id}: bundle.git_dirty_at_test_time={b.get('git_dirty_at_test_time')!r}, need false")
    if (b.get("git_head_at_test_time") or "").strip() != current_head:
        errs.append(
            f"{req_id}: bundle.git_head_at_test_time='{b.get('git_head_at_test_time', '')[:12]}' "
            f"!= current HEAD '{current_head[:12]}'"
        )
    declared = b.get("content_hash", "")
    bundle_no_hash = {k: v for k, v in b.items() if k != "content_hash"}
    if declared != _deterministic_digest(bundle_no_hash):
        errs.append(f"{req_id}: bundle content_hash tamper-check failed")
    return errs


def _apply_staged(r: dict, git_head: str, ci_gate_repoint_note: str) -> dict:
    """W4d-4: PROOF_PARTIAL state, last_passed_commit blank."""
    r["evidence_status"] = "PROOF_PARTIAL"
    marker = f"PROOF_READY_PENDING_COMMIT:{git_head[:12] if git_head else 'unknown'}"
    existing_notes = r.get("hardening_notes", "")
    cleaned_parts = [
        part for part in (existing_notes.split(" | ") if existing_notes else [])
        if not part.startswith("PROOF_READY_PENDING_COMMIT:")
        and not part.startswith("CI_GATE_REPOINTED_TO_PILOT:")
        and not part.startswith("EVIDENCE_BOUND_TO_COMMIT:")
    ]
    new_parts = cleaned_parts + [marker]
    if ci_gate_repoint_note:
        new_parts.append(ci_gate_repoint_note)
    r["hardening_notes"] = " | ".join(p for p in new_parts if p)
    return r


def _apply_bound(r: dict, git_head: str, ci_gate_repoint_note: str) -> dict:
    """W4d-5: PROOF_PRESENT + ACCEPTED + IMPLEMENTED + last_passed_commit set."""
    r["evidence_status"] = "PROOF_PRESENT"
    r["final_acceptance_status"] = "ACCEPTED"
    r["implementation_status"] = "IMPLEMENTED"
    r["last_passed_commit"] = git_head
    bound_marker = f"EVIDENCE_BOUND_TO_COMMIT:{git_head[:12]}"
    existing_notes = r.get("hardening_notes", "")
    cleaned_parts = [
        part for part in (existing_notes.split(" | ") if existing_notes else [])
        # Supersede the staged marker on transition; preserve repoint note
        # unless we're overwriting it just below.
        if not part.startswith("PROOF_READY_PENDING_COMMIT:")
        and not part.startswith("EVIDENCE_BOUND_TO_COMMIT:")
        and not (ci_gate_repoint_note and part.startswith("CI_GATE_REPOINTED_TO_PILOT:"))
    ]
    new_parts = cleaned_parts + [bound_marker]
    if ci_gate_repoint_note:
        new_parts.append(ci_gate_repoint_note)
    r["hardening_notes"] = " | ".join(p for p in new_parts if p)
    return r


def main() -> int:
    parser = argparse.ArgumentParser(description="Update 5 pilot ledger rows.")
    parser.add_argument(
        "--mode", choices=["staged", "bound"], default="staged",
        help="staged = W4d-4 PROOF_PARTIAL; bound = W4d-5 PROOF_PRESENT/ACCEPTED",
    )
    args = parser.parse_args()

    csv.field_size_limit(2_000_000)
    if not LEDGER.exists():
        print(f"FATAL: ledger not found at {LEDGER}")
        return 2

    git_head = _git_head()
    print(f"[update_pilot_ledger mode={args.mode}] git HEAD={git_head[:12]}")

    # W4d-5 bound mode requires:
    #   1) the *test-time* surface (test files, fixtures, validators, gate,
    #      bundle emitter) clean at this HEAD — these prove the tests
    #   2) 5 valid bundles (EVIDENCE_PRESENT + git_dirty=false +
    #      head=current + content_hash valid)
    # The ledger CSV and bundle dir are EXCLUDED from precheck because
    # they are the writeback target of this script — expected dirty.
    if args.mode == "bound":
        test_time_scope = tuple(
            p for p in PILOT_BINDING_SCOPE
            if not p.endswith("10c_semantic_requirement_ledger.csv")
            and not p.endswith("proof_bundles/")
        )
        try:
            r = subprocess.run(
                ["git", "status", "--porcelain", "--", *test_time_scope],
                cwd=REPO_ROOT, capture_output=True, text=True, check=False, timeout=10,
            )
            test_time_dirty = [
                line for line in (r.stdout or "").splitlines() if line.strip()
            ]
        except (subprocess.SubprocessError, OSError) as exc:
            print(f"FATAL: git status failed: {exc}", file=sys.stderr)
            return 3
        if test_time_dirty:
            print("FATAL: cannot bind — test-time scope is dirty:", file=sys.stderr)
            for line in test_time_dirty:
                print(f"  {line}", file=sys.stderr)
            return 3
        all_errors: list[str] = []
        for req_id in PILOT_REQ_IDS:
            all_errors.extend(_validate_bundle_for_binding(req_id, git_head))
        if all_errors:
            print("FATAL: cannot bind — bundle precondition failures:", file=sys.stderr)
            for e in all_errors:
                print(f"  {e}", file=sys.stderr)
            return 4
        print(f"[update_pilot_ledger] precheck OK: test-time scope clean + 5 bundles binding-ready at HEAD {git_head[:12]}")

    with LEDGER.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    n_updated = 0
    for r in rows:
        if r["req_id"] not in PILOT_REQ_IDS:
            continue

        test_file = r.get("test_file_expected", "")
        bundle = f"artifacts/requirements/proof_bundles/{r['req_id'].lower()}.json"

        # W4d-4: until per-surface gates ship, the pilot gate is the
        # authoritative gate that proves this row. Re-point ci_gate_name and
        # acceptance_command to the pilot gate so existence checks reflect
        # reality. The harden script will reset to the per-surface gate name
        # deterministically when per-surface gates land.
        original_ci_gate = r.get("ci_gate_name", "")
        pilot_ci_gate = "ops_scripts/ci/check_10c_pilot_proof_evidence.py"
        if original_ci_gate != pilot_ci_gate:
            r["ci_gate_name"] = pilot_ci_gate
            ci_gate_repoint_note = (
                f"CI_GATE_REPOINTED_TO_PILOT:was='{original_ci_gate}'"
            )
        else:
            ci_gate_repoint_note = ""
        ci_gate = r["ci_gate_name"]

        old_test = r.get("test_file_exists", "")
        old_gate = r.get("ci_gate_exists", "")
        old_bundle = r.get("proof_bundle_exists", "")

        r["test_file_exists"] = _path_exists(test_file)
        r["ci_gate_exists"] = _path_exists(ci_gate)
        r["proof_bundle_exists"] = _path_exists(bundle)

        if args.mode == "staged":
            _apply_staged(r, git_head, ci_gate_repoint_note)
        else:
            _apply_bound(r, git_head, ci_gate_repoint_note)

        n_updated += 1
        print(
            f"  {r['req_id']:<15} test:{old_test or '-'}->{r['test_file_exists']}  "
            f"gate:{old_gate or '-'}->{r['ci_gate_exists']}  "
            f"bundle:{old_bundle or '-'}->{r['proof_bundle_exists']}  "
            f"evidence_status->{r['evidence_status']}  "
            f"final_acceptance_status->{r['final_acceptance_status']}"
        )

    if n_updated != len(PILOT_REQ_IDS):
        print(f"WARNING: updated {n_updated}/{len(PILOT_REQ_IDS)} pilot rows")

    with LEDGER.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[update_pilot_ledger mode={args.mode}] wrote {len(rows)} rows; {n_updated} pilot rows updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
