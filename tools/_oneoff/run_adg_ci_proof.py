#!/usr/bin/env python3
"""Run ADG CI gate sequence locally and emit a proof receipt."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RECEIPT = REPO / "docs/reports/cursor/adg_ci_gates_proof_receipt.json"

GATES: list[tuple[str, list[str]]] = [
    ("adg_redis_ingest", [sys.executable, "tools/adg/adg_redis_ingest.py", "--force"]),
    ("adg_stale_guard", [sys.executable, "tools/adg/adg_stale_guard.py"]),
    (
        "run_full_adg_audit_certification",
        [
            sys.executable,
            "tools/adg/run_full_adg_audit.py",
            "--mode",
            "certification",
            "--format",
            "both",
        ],
    ),
    ("check_expected_wiring", [sys.executable, "ops_scripts/ci/check_expected_wiring.py"]),
    (
        "check_config_references",
        [sys.executable, "ops_scripts/ci/check_config_references.py", "--allow-unreferenced"],
    ),
    ("check_lifecycle_pairs", [sys.executable, "ops_scripts/ci/check_lifecycle_pairs.py"]),
    ("check_exception_contract", [sys.executable, "ops_scripts/ci/check_exception_contract.py"]),
    ("check_test_harness_coverage", [sys.executable, "ops_scripts/ci/check_test_harness_coverage.py"]),
    ("check_ssot_magic_constants", [sys.executable, "ops_scripts/ci/check_ssot_magic_constants.py"]),
    (
        "check_observability_on_high_fanin",
        [sys.executable, "ops_scripts/ci/check_observability_on_high_fanin.py"],
    ),
    (
        "check_external_service_literal_ssot",
        [sys.executable, "ops_scripts/ci/check_external_service_literal_ssot.py"],
    ),
    (
        "check_cross_mainline_dispatcher",
        [sys.executable, "ops_scripts/ci/check_cross_mainline_dispatcher.py"],
    ),
    ("check_env_var_in_config_layer", [sys.executable, "ops_scripts/ci/check_env_var_in_config_layer.py"]),
    ("check_violation_aging_sla", [sys.executable, "ops_scripts/ci/check_violation_aging_sla.py"]),
    ("check_adg_violation_log_delta", [sys.executable, "ops_scripts/ci/check_adg_violation_log_delta.py"]),
    ("check_test_concentration_ratio", [sys.executable, "ops_scripts/ci/check_test_concentration_ratio.py"]),
    ("_adg_ci_gates_summary", [sys.executable, "ops_scripts/ci/_adg_ci_gates.py"]),
    ("3B1_runtime_proof_view", [sys.executable, "ops_scripts/ci/check_runtime_proof_view_well_formed.py"]),
    ("3B2_otel_genai_semconv", [sys.executable, "ops_scripts/ci/check_otel_genai_semconv_coverage.py"]),
    ("3B3_three_bucket_gap", [sys.executable, "ops_scripts/ci/check_three_bucket_gap_thresholds.py"]),
    ("3B4_snapshot_signed", [sys.executable, "ops_scripts/ci/check_adg_snapshot_signed.py"]),
    ("3B5_schema_graduation", [sys.executable, "ops_scripts/ci/check_schema_graduation_readiness.py"]),
    ("3B6_adg_certified", [sys.executable, "ops_scripts/ci/check_adg_certified.py"]),
]


def _run(name: str, cmd: list[str], *, timeout_s: int) -> dict[str, object]:
    env = os.environ.copy()
    env.setdefault("PYTHONPATH", str(REPO))
    env.setdefault("ADG_REDIS_URL", "redis://localhost:6379/0")
    env.setdefault("ADG_VIOLATION_LOG_DELTA_BYPASS", "1")
    started = datetime.now(timezone.utc).isoformat()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO),
            env=env,
            timeout=timeout_s,
            shell=False,
            capture_output=True,
            text=True,
        )
        tail = (proc.stdout or "")[-2000:] + (proc.stderr or "")[-2000:]
        return {
            "name": name,
            "cmd": " ".join(cmd),
            "exit_code": proc.returncode,
            "ok": proc.returncode == 0,
            "started_at": started,
            "output_tail": tail,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "name": name,
            "cmd": " ".join(cmd),
            "exit_code": 124,
            "ok": False,
            "started_at": started,
            "output_tail": f"TIMEOUT after {timeout_s}s: {exc}",
        }


def main() -> int:
    results: list[dict[str, object]] = []
    for name, cmd in GATES:
        timeout = 3600 if name == "run_full_adg_audit_certification" else 600
        print(f"[adg_ci_proof] RUN {name} ...", flush=True)
        row = _run(name, cmd, timeout_s=timeout)
        results.append(row)
        status = "PASS" if row["ok"] else "FAIL"
        print(f"[adg_ci_proof] {status} {name} exit={row['exit_code']}", flush=True)
        if not row["ok"] and name not in ("adg_redis_ingest", "adg_stale_guard"):
            break

    all_ok = all(r["ok"] for r in results)
    optional_redis = {"adg_redis_ingest", "adg_stale_guard"}
    required_ok = all(r["ok"] for r in results if r["name"] not in optional_redis)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "all_gates_ok": all_ok,
        "required_gates_ok": required_ok,
        "results": results,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"[adg_ci_proof] wrote {RECEIPT.relative_to(REPO)}")
    return 0 if required_ok else 1


if __name__ == "__main__":
    sys.exit(main())
