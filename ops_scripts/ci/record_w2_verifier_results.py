"""W2 — Run all 5 integrated-runtime verifiers, capture exit codes, and
write the ledger ``artifacts/certification/integrated_runtime/verifier_results.json``.

This script is the SSOT for the verifier ledger that
``compose_semantic_cache_subclaims._map_integrated_runtime_proof``
consumes. It does NOT itself certify anything — it only RECORDS exit
codes. PASS = all 5 exit codes are 0.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "verifier_results.json"

VERIFIERS = (
    "verify_integrated_runtime_entrypoint",
    "verify_r1b_safe_reuse_integrated_runtime",
    "verify_integrated_runtime_artifact_chain",
    "verify_integrated_runtime_no_harness_stamp",
    "verify_integrated_runtime_exit_x3",
)


def main() -> int:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict] = {}
    for v in VERIFIERS:
        path = REPO_ROOT / "ops_scripts" / "ci" / f"{v}.py"
        t0 = time.time()
        try:
            proc = subprocess.run(
                [sys.executable, str(path)],
                capture_output=True,
                text=True,
                timeout=60,
                shell=False,
                cwd=str(REPO_ROOT),
            )
            ec = proc.returncode
            tail = (proc.stdout.splitlines()[-1] if proc.stdout.strip() else "") + (
                ("\n" + proc.stderr.splitlines()[-1]) if proc.stderr.strip() else ""
            )
        except subprocess.TimeoutExpired as exc:
            ec = 124
            tail = f"TIMEOUT: {exc}"
        results[v] = {
            "exit_code": ec,
            "duration_s": round(time.time() - t0, 3),
            "summary": tail,
        }
        print(f"[record_w2] {v}: exit={ec} ({results[v]['duration_s']}s)")

    LEDGER_PATH.write_text(
        json.dumps(
            {
                "recorded_at_epoch": time.time(),
                "verifiers": list(VERIFIERS),
                **results,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print(f"[record_w2] ledger written: {LEDGER_PATH.relative_to(REPO_ROOT)}")
    failed = [v for v in VERIFIERS if results[v]["exit_code"] != 0]
    if failed:
        print(f"[record_w2] FAIL: {len(failed)}/{len(VERIFIERS)} verifiers failed: {failed}")
        return 2
    print(f"[record_w2] PASS: all {len(VERIFIERS)} verifiers exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
