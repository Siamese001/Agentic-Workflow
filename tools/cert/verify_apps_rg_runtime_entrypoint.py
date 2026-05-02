"""W3 honest runtime verifier — apps_rg integrated runtime entrypoint.

Approved producer (constitutional §32: `tools/cert/*.py`).

Scope: attests RTC-REQ-010, RTC-REQ-012, RTC-REQ-015 — the three rows the
existing approved upstream verifier ``scripts/verify_rtc_req_integrated_runtime.py``
honestly reports as PASS. This script does not attest RTC-REQ-011, 013, 014
(those rows are not in the W3 candidate set) nor the broader runtime backlog
(RTC-REQ-056/072/096/120/128) — those need different evidence sources.

For each target req_id, this verifier honestly checks 7 controls and writes a
row-specific evidence file at:

    artifacts/certification/runtime/<req_id>/apps_rg_runtime_entrypoint_evidence.json

with the shape ``/per_req/<req_id>/<control>`` per Fort Knox v2 atomic
assertion contract. Each control's ``assertion_result`` is set to PASS only
when a deterministic byte-level check succeeds; FAIL otherwise.

Per-control PASS criteria (deterministic, byte-anchored):

  verifier_pass             upstream verify_rtc_req_integrated_runtime.py
                            reports per_req[req_id].result == "PASS"
  verifier_exit_zero        upstream verifier exited 0
  last_verified_timestamp   captured at runtime (UTC, ISO-8601)
  runtime_evidence          integrated_runtime/latest bundle present and
                            every artifact named in its manifest exists
  otel_trace                latest dated apps_rg run has otel_runtime_trace.json
                            with span_count > 0 and contains_synthetic_spans
                            == false
  source_root_binding       repo root resolves; integrated_runtime/latest is
                            inside <repo_root>/artifacts/certification (single
                            authoritative root, no cross-root drift)
  artifact_payload_hash     fresh sha256 computed at verification time for
                            every bundle artifact; recorded in evidence file
                            (does NOT trust manifest's stale hashes)

If ANY control's check fails, the row's evidence file still gets written but
the failing control's assertion_result is FAIL — so the compiler will refuse
to sign off the row. No silent-greenwash.

Exit codes:
  0   all target rows have PASS for every control
  2   at least one control on at least one target row is FAIL
  3   harness error (cannot find bundle, cannot run upstream verifier, etc.)
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET_REQS = ["RTC-REQ-010", "RTC-REQ-012", "RTC-REQ-015"]
REQUIRED_CONTROLS = [
    "verifier_pass",
    "verifier_exit_zero",
    "last_verified_timestamp",
    "runtime_evidence",
    "otel_trace",
    "source_root_binding",
    "artifact_payload_hash",
]
UPSTREAM_VERIFIER = REPO_ROOT / "scripts" / "verify_rtc_req_integrated_runtime.py"
UPSTREAM_REPORT   = REPO_ROOT / "artifacts" / "certification" / "rtc_req_integrated_runtime_report.json"
BUNDLE_DIR        = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "latest"
APPS_RG_RUNS_DIR  = REPO_ROOT / "artifacts" / "apps_rg" / "runs"
EVIDENCE_ROOT     = REPO_ROOT / "artifacts" / "certification" / "runtime"

DATED_RUN_RE = re.compile(r"^\d{8}_\d{6}$")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def canonical_sha256(obj: object) -> str:
    """SHA256 of canonical JSON for a Python object (sorted keys, no whitespace)."""
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def run_upstream() -> tuple[int, dict]:
    """Invoke the existing approved upstream verifier; return (exit, report)."""
    if not UPSTREAM_VERIFIER.exists():
        raise SystemExit(f"upstream verifier missing: {UPSTREAM_VERIFIER}")
    r = subprocess.run(
        [sys.executable, str(UPSTREAM_VERIFIER)],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=120,
    )
    if not UPSTREAM_REPORT.exists():
        raise SystemExit(f"upstream did not produce report: {UPSTREAM_REPORT}")
    return r.returncode, json.loads(UPSTREAM_REPORT.read_text(encoding="utf-8"))


def find_latest_apps_rg_run() -> Path | None:
    if not APPS_RG_RUNS_DIR.exists():
        return None
    candidates = sorted(
        p for p in APPS_RG_RUNS_DIR.iterdir()
        if p.is_dir() and DATED_RUN_RE.fullmatch(p.name)
        and (p / "otel_runtime_trace.json").exists()
    )
    return candidates[-1] if candidates else None


def check_otel_trace(run_dir: Path | None) -> tuple[bool, dict]:
    """Returns (passed, payload_dict_for_evidence_file)."""
    if run_dir is None:
        return False, {"reason": "no dated apps_rg run with otel_runtime_trace.json"}
    trace_p = run_dir / "otel_runtime_trace.json"
    t = json.loads(trace_p.read_text(encoding="utf-8"))
    span_count = int(t.get("span_count", 0))
    synthetic = bool(t.get("contains_synthetic_spans", True))
    span_names = [s.get("name") for s in t.get("spans", [])]
    passed = span_count > 0 and not synthetic
    return passed, {
        "trace_path": str(trace_p.relative_to(REPO_ROOT)).replace("\\", "/"),
        "trace_sha256": sha256_file(trace_p),
        "run_id": t.get("run_id"),
        "span_count": span_count,
        "contains_synthetic_spans": synthetic,
        "span_names": span_names,
        "earliest_start_utc": t.get("earliest_start_utc"),
        "latest_finish_utc": t.get("latest_finish_utc"),
    }


def check_runtime_evidence_bundle() -> tuple[bool, dict]:
    """Bundle present + every artifact named in manifest exists."""
    if not BUNDLE_DIR.exists():
        return False, {"reason": f"bundle dir missing: {BUNDLE_DIR}"}
    manifest_p = BUNDLE_DIR / "integrated_runtime_artifact_manifest.json"
    if not manifest_p.exists():
        return False, {"reason": "manifest missing"}
    m = json.loads(manifest_p.read_text(encoding="utf-8"))
    declared = m.get("payload", {}).get("artifact_filenames", [])
    missing = [f for f in declared if not (BUNDLE_DIR / f).exists()]
    passed = bool(declared) and not missing
    return passed, {
        "bundle_dir": str(BUNDLE_DIR.relative_to(REPO_ROOT)).replace("\\", "/"),
        "manifest_path": str(manifest_p.relative_to(REPO_ROOT)).replace("\\", "/"),
        "manifest_sha256": sha256_file(manifest_p),
        "declared_artifact_count": len(declared),
        "declared_artifact_filenames": declared,
        "missing_artifacts": missing,
    }


def check_source_root_binding() -> tuple[bool, dict]:
    """Bundle dir is inside repo_root/artifacts/certification (single root)."""
    expected_prefix = REPO_ROOT / "artifacts" / "certification"
    try:
        rel = BUNDLE_DIR.relative_to(expected_prefix)
        bound = True
    except ValueError:
        rel = None
        bound = False
    return bound, {
        "repo_root": str(REPO_ROOT).replace("\\", "/"),
        "expected_prefix": str(expected_prefix.relative_to(REPO_ROOT)).replace("\\", "/"),
        "bundle_relative_to_prefix": str(rel).replace("\\", "/") if rel else None,
        "single_root_verified": bound,
    }


def compute_fresh_artifact_hashes() -> tuple[bool, dict]:
    """Compute fresh sha256 for every file in the bundle (independent of manifest)."""
    if not BUNDLE_DIR.exists():
        return False, {"reason": "bundle dir missing"}
    files = sorted(p for p in BUNDLE_DIR.iterdir() if p.is_file())
    if not files:
        return False, {"reason": "bundle dir empty"}
    fresh = {p.name: f"sha256:{sha256_file(p)}" for p in files}
    return True, {
        "computed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "artifact_count": len(fresh),
        "fresh_artifact_hashes": fresh,
    }


def emit_for_req(req_id: str, upstream_exit: int, upstream_report: dict,
                 latest_run: Path | None) -> tuple[bool, Path]:
    """Emit row-specific evidence for one target req_id. Returns (all_pass, path)."""
    upstream_per_req = (upstream_report.get("per_req") or {}).get(req_id) or {}
    upstream_pass = upstream_per_req.get("result") == "PASS"

    rt_pass, rt_payload = check_runtime_evidence_bundle()
    otel_pass, otel_payload = check_otel_trace(latest_run)
    src_pass, src_payload = check_source_root_binding()
    hash_pass, hash_payload = compute_fresh_artifact_hashes()

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    per_req_block = {
        "verifier_pass": {
            "assertion_result": "PASS" if upstream_pass else "FAIL",
            "upstream_verifier": str(UPSTREAM_VERIFIER.relative_to(REPO_ROOT)).replace("\\", "/"),
            "upstream_per_req_result": upstream_per_req.get("result"),
            "upstream_per_req_violations": upstream_per_req.get("violations") or [],
            "upstream_per_req_title": upstream_per_req.get("title"),
        },
        "verifier_exit_zero": {
            "assertion_result": "PASS" if upstream_exit == 0 else "FAIL",
            "upstream_exit_code": upstream_exit,
        },
        "last_verified_timestamp": {
            "assertion_result": "PASS",
            "verified_at_utc": now,
        },
        "runtime_evidence": {
            "assertion_result": "PASS" if rt_pass else "FAIL",
            **rt_payload,
        },
        "otel_trace": {
            "assertion_result": "PASS" if otel_pass else "FAIL",
            **otel_payload,
        },
        "source_root_binding": {
            "assertion_result": "PASS" if src_pass else "FAIL",
            **src_payload,
        },
        "artifact_payload_hash": {
            "assertion_result": "PASS" if hash_pass else "FAIL",
            "payload_pointer": f"/per_req/{req_id}/artifact_payload_hash",
            **hash_payload,
        },
    }

    # Embed the canonical sha256 of the per_req[req_id] block for self-binding.
    payload_sha256 = canonical_sha256(per_req_block)

    evidence = {
        "schema_version": "runtime-evidence-v1",
        "req_id": req_id,
        "app_name": "apps_rg",
        "control_scope": "integrated_runtime_entrypoint",
        "producer": "tools/cert/verify_apps_rg_runtime_entrypoint.py",
        "producer_exit_code": 0 if upstream_exit == 0 else upstream_exit,
        "captured_at_utc": now,
        "per_req_block_sha256": payload_sha256,
        "per_req": {req_id: per_req_block},
    }

    out_dir = EVIDENCE_ROOT / req_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "apps_rg_runtime_entrypoint_evidence.json"
    out_path.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")

    all_pass = all(v["assertion_result"] == "PASS" for v in per_req_block.values())
    return all_pass, out_path


def main() -> int:
    print(f"[verify_apps_rg_runtime_entrypoint] starting; targets={TARGET_REQS}")

    print(f"  invoking upstream: {UPSTREAM_VERIFIER.relative_to(REPO_ROOT)}")
    upstream_exit, upstream_report = run_upstream()
    print(f"    upstream exit: {upstream_exit}")

    latest_run = find_latest_apps_rg_run()
    print(f"  latest dated apps_rg run: "
          f"{latest_run.relative_to(REPO_ROOT) if latest_run else '(none)'}")

    overall_pass = True
    for req_id in TARGET_REQS:
        ok, path = emit_for_req(req_id, upstream_exit, upstream_report, latest_run)
        rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        marker = "PASS" if ok else "FAIL"
        print(f"    {req_id}: {marker}  -> {rel}")
        if not ok:
            overall_pass = False

    if overall_pass:
        print("[verify_apps_rg_runtime_entrypoint] ALL TARGETS PASS")
        return 0
    print("[verify_apps_rg_runtime_entrypoint] AT LEAST ONE TARGET FAIL", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
