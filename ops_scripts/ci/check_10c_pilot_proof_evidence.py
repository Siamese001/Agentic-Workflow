"""Narrow CI gate for the W4d-4 proof-evidence pilot.

This gate enforces proof evidence ONLY for the 5 pilot REQs. It does NOT
require all 200 ledger rows to have proof evidence; that is the eventual
goal but not in scope for this gate.

For each of the 5 pilot REQs, the gate checks:

  P1. The proof bundle JSON exists at
      artifacts/requirements/proof_bundles/<req_id_lower>.json
  P2. The bundle's req_id, canonical_owner_surface, otel_span_ref match
      the ledger row.
  P3. The bundle's content_hash matches the recomputed hash of the
      bundle (tamper detection).
  P4. The bundle's proof_status is EVIDENCE_STAGED or EVIDENCE_PRESENT.
  P5. The test file named in the ledger exists on disk.
  P6. The test file actually runs and passes (one targeted pytest run).

If proof_status is EVIDENCE_PRESENT, the bundle's git_head_at_test_time
must match the current git HEAD (commit-bound evidence).

Exit codes:
  0 = all 5 pilot REQs have valid proof evidence
  1 = at least one pilot REQ failed proof evidence
  2 = bundle file missing or unreadable; fixture environment broken
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "docs" / "reports" / "design" / "10c_reconciliation" / "10c_semantic_requirement_ledger.csv"
BUNDLES_DIR = REPO_ROOT / "artifacts" / "requirements" / "proof_bundles"
ARTIFACTS = REPO_ROOT / "artifacts" / "requirements"
JSON_OUT = ARTIFACTS / "10c_pilot_proof_evidence.json"
MD_OUT = ARTIFACTS / "10c_pilot_proof_evidence.md"

# Allow direct script invocation (the CI gate is run both as a module by
# run_contract_gates.py and directly by pre-commit; both must work).
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.requirements._binding_scope import CRITICAL_REQ_IDS as _CRITICAL_REQ_IDS

# SSOT-imported. Includes the original 5 W4d-4/W4d-5 pilots and the 24
# Wave 1 CRITICAL rows. Variable name kept as PILOT_REQ_IDS for back-compat
# with downstream report consumers.
PILOT_REQ_IDS: tuple[str, ...] = _CRITICAL_REQ_IDS


def _load_ledger() -> dict[str, dict[str, str]]:
    csv.field_size_limit(2_000_000)
    with LEDGER.open("r", encoding="utf-8", newline="") as fh:
        return {row["req_id"]: row for row in csv.DictReader(fh)}


def _deterministic_digest(payload: object) -> str:
    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
        default=str, ensure_ascii=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _git_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False, timeout=10,
        )
        return (result.stdout or "").strip()
    except (subprocess.SubprocessError, OSError):
        return ""


def _run_pytest(test_file: str) -> tuple[bool, str]:
    """Run a single pytest file in an isolated, plugin-disabled subprocess.

    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 prevents xdist/testmon/coverage from
    spinning up worker pools that previously hung this gate on Windows.
    Only the timeout plugin is loaded explicitly for safety.
    """
    import os
    env = os.environ.copy()
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    try:
        result = subprocess.run(
            [
                "python", "-m", "pytest", test_file,
                "-q", "--no-header",
                "-p", "no:cacheprovider",
                "-p", "no:xdist",
                "-p", "no:testmon",
                "--rootdir", str(REPO_ROOT),
                "-c", "/dev/null" if os.name != "nt" else "NUL",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
            env=env,
        )
        passed = result.returncode == 0
        out = (result.stdout or "") + (result.stderr or "")
        return passed, out[-400:]
    except (subprocess.SubprocessError, OSError) as exc:
        return False, f"pytest invocation failed: {exc}"


def _check_one(
    req_id: str,
    ledger: dict[str, dict[str, str]],
    current_head: str,
    *,
    skip_pytest: bool = False,
) -> dict:
    result = {
        "req_id": req_id,
        "checks": {},
        "errors": [],
        "passed": False,
    }
    if req_id not in ledger:
        result["errors"].append(f"P0: req_id {req_id} not in ledger")
        return result
    row = ledger[req_id]

    # P1: bundle exists
    bundle_path = BUNDLES_DIR / f"{req_id.lower()}.json"
    bundle_exists = bundle_path.exists()
    result["checks"]["P1_bundle_exists"] = bundle_exists
    if not bundle_exists:
        result["errors"].append(f"P1: proof bundle missing at {bundle_path.relative_to(REPO_ROOT)}")
        return result
    try:
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result["errors"].append(f"P1: proof bundle unreadable: {exc}")
        return result

    # P2: bundle vs ledger metadata match
    p2_ok = True
    for key, ledger_key in (
        ("req_id", "req_id"),
        ("canonical_owner_surface", "canonical_owner_surface"),
        ("otel_span_ref", "otel_span_expected"),
    ):
        if bundle.get(key) != row.get(ledger_key):
            result["errors"].append(
                f"P2: bundle.{key}='{bundle.get(key)}' != ledger.{ledger_key}='{row.get(ledger_key)}'"
            )
            p2_ok = False
    result["checks"]["P2_bundle_ledger_match"] = p2_ok

    # P3: bundle content_hash valid (recompute over bundle without content_hash)
    declared_hash = bundle.get("content_hash", "")
    bundle_no_hash = {k: v for k, v in bundle.items() if k != "content_hash"}
    recomputed_hash = _deterministic_digest(bundle_no_hash)
    p3_ok = (declared_hash == recomputed_hash)
    result["checks"]["P3_bundle_content_hash_valid"] = p3_ok
    if not p3_ok:
        result["errors"].append(
            f"P3: content_hash mismatch (tamper detection): declared={declared_hash[:16]}..., "
            f"recomputed={recomputed_hash[:16]}..."
        )

    # P4: proof_status is in valid set
    proof_status = bundle.get("proof_status", "")
    p4_ok = proof_status in {"EVIDENCE_STAGED", "EVIDENCE_PRESENT"}
    result["checks"]["P4_proof_status_valid"] = p4_ok
    if not p4_ok:
        result["errors"].append(
            f"P4: invalid proof_status '{proof_status}'; "
            f"must be EVIDENCE_STAGED or EVIDENCE_PRESENT"
        )

    # If EVIDENCE_PRESENT, verify git head matches current HEAD
    if proof_status == "EVIDENCE_PRESENT":
        bundle_head = bundle.get("git_head_at_test_time", "")
        if bundle_head != current_head:
            result["errors"].append(
                f"P4b: proof_status=EVIDENCE_PRESENT but bundle git_head '{bundle_head[:8]}' "
                f"!= current HEAD '{current_head[:8]}'; rebuild bundle or downgrade to EVIDENCE_STAGED"
            )

    # P5: test file exists
    test_file = row.get("test_file_expected", "")
    test_path = REPO_ROOT / test_file
    p5_ok = bool(test_file) and test_path.exists()
    result["checks"]["P5_test_file_exists"] = p5_ok
    if not p5_ok:
        result["errors"].append(f"P5: test file missing at {test_file}")

    # P6: test passes
    p6_ok = False
    test_output_tail = ""
    if skip_pytest:
        if p5_ok:
            p6_ok = True
            test_output_tail = ""
            result["checks"]["P6_test_passes"] = "SKIPPED"
        else:
            p6_ok = False
            result["checks"]["P6_test_passes"] = False
    elif p5_ok:
        p6_ok, test_output_tail = _run_pytest(test_file)
        result["checks"]["P6_test_passes"] = p6_ok
        if not p6_ok:
            result["errors"].append(
                f"P6: test failed; output tail: {test_output_tail.strip()[-300:]}"
            )
    else:
        result["checks"]["P6_test_passes"] = False

    result["passed"] = all((p2_ok, p3_ok, p4_ok, p5_ok, p6_ok)) and not result["errors"]
    result["test_output_tail"] = test_output_tail
    result["bundle_path"] = str(bundle_path.relative_to(REPO_ROOT)).replace("\\", "/")
    result["test_file"] = test_file
    result["proof_status"] = proof_status
    return result


def _emit_report(results: list[dict], current_head: str) -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    n_pass = sum(1 for r in results if r["passed"])
    n_total = len(results)

    payload = {
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "current_git_head": current_head,
        "pilot_req_ids": list(PILOT_REQ_IDS),
        "passed_count": n_pass,
        "total_count": n_total,
        "all_passed": n_pass == n_total,
        "results": results,
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md = ["# 10C Pilot Proof Evidence Gate Report (W4d-4)", ""]
    md.append(f"- Validated at (UTC): {payload['validated_at_utc']}")
    md.append(f"- Current git HEAD: `{current_head[:12] if current_head else '(unknown)'}`")
    md.append(f"- Result: **{n_pass}/{n_total} pilot REQs proof-evidence-complete**")
    md.append("")
    md.append("## Per-REQ result")
    md.append("")
    md.append("| REQ ID | Surface | Test file | Bundle | Proof status | Pass |")
    md.append("|---|---|---|---|---|:---:|")
    for r in results:
        owner = r.get("checks", {})
        md.append(
            f"| `{r['req_id']}` "
            f"| `{r.get('proof_status', '?')}` "
            f"| `{r.get('test_file', '')}` "
            f"| `{r.get('bundle_path', '')}` "
            f"| `{r.get('proof_status', '?')}` "
            f"| {'✅' if r['passed'] else '❌'} |"
        )
    md.append("")
    if any(not r["passed"] for r in results):
        md.append("## Errors")
        md.append("")
        for r in results:
            for e in r["errors"]:
                md.append(f"- `{r['req_id']}`: {e}")
        md.append("")
    MD_OUT.write_text("\n".join(md), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="W4d-4 pilot proof-evidence gate.")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any failure (default).")
    parser.add_argument("--no-strict", dest="strict", action="store_false")
    parser.add_argument(
        "--skip-pytest", action="store_true",
        help="Skip the pytest invocation step (P6); useful when integrating into a "
             "larger gate run that already executes pytest separately.",
    )
    parser.set_defaults(strict=True)
    args = parser.parse_args()

    print("[10C pilot proof-evidence gate W4d-4]")
    if not LEDGER.exists():
        print(f"FATAL: ledger not found at {LEDGER}", file=sys.stderr)
        return 2

    ledger = _load_ledger()
    current_head = _git_head()

    results: list[dict] = []
    for req_id in PILOT_REQ_IDS:
        r = _check_one(
            req_id,
            ledger,
            current_head,
            skip_pytest=args.skip_pytest,
        )
        results.append(r)
        flag = "PASS" if r["passed"] else "FAIL"
        print(f"  {r['req_id']:<15} {flag:<5} status={r.get('proof_status', '?'):<18} bundle={r.get('bundle_path', '?')}")
        for e in r["errors"]:
            print(f"      ERROR: {e}")

    _emit_report(results, current_head)

    n_pass = sum(1 for r in results if r["passed"])
    print(f"\n  artifacts: {JSON_OUT.relative_to(REPO_ROOT)}, {MD_OUT.relative_to(REPO_ROOT)}")
    print(f"  result   : {n_pass}/{len(results)} pilot REQs proof-evidence-complete")

    if n_pass == len(results):
        print("OK  W4d-4 pilot proof evidence gate passed.")
        return 0

    print("FAIL -- pilot proof evidence gate", file=sys.stderr)
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
