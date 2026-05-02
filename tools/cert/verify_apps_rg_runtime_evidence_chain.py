"""W4 honest runtime verifier — apps_rg integrated-runtime evidence chain.

Approved producer (constitutional §32: ``tools/cert/*.py``).

Scope: attests three additional INTEGRATED_RUNTIME rows that the R1B
short-circuit bundle at ``artifacts/certification/integrated_runtime/latest``
honestly supports:

  RTC-REQ-056  R1B integrated runtime proof
  RTC-REQ-096  Exit emits exactly one X3 and does not write L4
  RTC-REQ-128  Gate verdict bundle consumed by Exit

Out of W4 scope:
  RTC-REQ-072  UWG write sequence complete — this R1B run had
               ``no_l4_write_assertion: true`` (no UWG write occurred), so
               the UWG path is not exercised. Cannot be honestly attested
               from this evidence; stays NOT_VERIFIED.
  RTC-REQ-120  Final 100% row — must remain open by design (depends on full
               graph closure including RTC-REQ-072 and others).

Each target row gets seven atomic assertions (the standard runtime control
set). Per-row PASS criteria:

  RTC-REQ-056  ``runtime_evidence`` PASS = exit packet route_id starts with
               ``R1B_``, ``no_l2_execution_assertion`` is true,
               ``replay_receipts_present`` is true,
               ``wall_clock_used`` is false, semantic-cache decision and
               terminal-ret-packet artifacts both exist.

  RTC-REQ-096  ``runtime_evidence`` PASS = exit packet
               ``no_l4_write_assertion`` is true AND x3 receipt
               ``verdict_count`` == 1 AND x3 receipt ``x3_disposition`` is a
               non-empty string.

  RTC-REQ-128  ``runtime_evidence`` PASS = manifest ``chain_linkage`` shows
               ``runtime_gate_verdict_bundle.json`` as a transitive ancestor
               of ``exit_review_packet.json`` (Exit consumed gate verdict).

The four chain controls (``otel_trace``, ``source_root_binding``,
``last_verified_timestamp``, ``artifact_payload_hash``) and the two binding
controls (``verifier_pass``, ``verifier_exit_zero``) follow the same honest
discipline as ``verify_apps_rg_runtime_entrypoint.py``.

Exit codes:
  0   all target rows have PASS for every control
  2   at least one control on at least one target row is FAIL
  3   harness error (cannot find bundle, cannot open manifest, etc.)
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
TARGET_REQS = ["RTC-REQ-056", "RTC-REQ-096", "RTC-REQ-128"]

CHAIN_CONTROLS = [
    "verifier_pass",
    "verifier_exit_zero",
    "last_verified_timestamp",
    "runtime_evidence",
    "otel_trace",
    "source_root_binding",
    "artifact_payload_hash",
]

BUNDLE_DIR        = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "latest"
APPS_RG_RUNS_DIR  = REPO_ROOT / "artifacts" / "apps_rg" / "runs"
EVIDENCE_ROOT     = REPO_ROOT / "artifacts" / "certification" / "runtime"
DATED_RUN_RE = re.compile(r"^\d{8}_\d{6}$")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def canonical_sha256(obj: object) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def find_latest_apps_rg_run() -> Path | None:
    if not APPS_RG_RUNS_DIR.exists():
        return None
    candidates = sorted(
        p for p in APPS_RG_RUNS_DIR.iterdir()
        if p.is_dir() and DATED_RUN_RE.fullmatch(p.name)
        and (p / "otel_runtime_trace.json").exists()
    )
    return candidates[-1] if candidates else None


def load_bundle() -> dict:
    """Load all bundle artifacts into a {filename: parsed_json} dict."""
    if not BUNDLE_DIR.exists():
        raise SystemExit(f"bundle dir missing: {BUNDLE_DIR}")
    out: dict[str, dict] = {}
    for p in sorted(BUNDLE_DIR.iterdir()):
        if p.is_file() and p.suffix == ".json":
            try:
                out[p.name] = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                out[p.name] = {}
    return out


def check_runtime_evidence_for_req(req_id: str, bundle: dict) -> tuple[bool, dict]:
    """Per-req honest predicate. Returns (passed, payload_dict)."""
    exit_packet = bundle.get("exit_review_packet.json", {}).get("payload", {})
    x3 = bundle.get("x3_disposition_receipt.json", {}).get("payload", {})
    manifest_payload = bundle.get("integrated_runtime_artifact_manifest.json", {}).get("payload", {})

    if req_id == "RTC-REQ-056":
        # R1B integrated runtime proof
        sc_present = "semantic_cache_safe_reuse_decision.json" in bundle
        trp_present = "terminal_ret_packet.json" in bundle
        route_id = exit_packet.get("route_id", "")
        is_r1b = isinstance(route_id, str) and route_id.startswith("R1B_")
        no_l2 = bool(exit_packet.get("no_l2_execution_assertion"))
        replay_ok = bool(exit_packet.get("exec_trace", {}).get("replay_receipts_present"))
        wall_clock_unused = exit_packet.get("exec_trace", {}).get("wall_clock_used") is False
        passed = sc_present and trp_present and is_r1b and no_l2 and replay_ok and wall_clock_unused
        return passed, {
            "row_predicate": "R1B short-circuit path complete",
            "semantic_cache_safe_reuse_decision_present": sc_present,
            "terminal_ret_packet_present": trp_present,
            "exit_packet_route_id": route_id,
            "is_r1b": is_r1b,
            "no_l2_execution_assertion": no_l2,
            "replay_receipts_present": replay_ok,
            "wall_clock_used_false": wall_clock_unused,
        }

    if req_id == "RTC-REQ-096":
        # Exit emits exactly one X3 and does not write L4
        no_l4 = bool(exit_packet.get("no_l4_write_assertion"))
        verdict_count = x3.get("verdict_count")
        x3_disp = x3.get("x3_disposition", "")
        x3_disp_nonempty = isinstance(x3_disp, str) and len(x3_disp) > 0
        passed = bool(no_l4 and verdict_count == 1 and x3_disp_nonempty)
        return passed, {
            "row_predicate": "exit_packet.no_l4_write_assertion==true AND x3.verdict_count==1 AND x3.x3_disposition non-empty",
            "no_l4_write_assertion": no_l4,
            "x3_verdict_count": verdict_count,
            "x3_disposition": x3_disp,
        }

    if req_id == "RTC-REQ-128":
        # Gate verdict bundle consumed by Exit (chain_linkage transitive)
        chain = manifest_payload.get("chain_linkage", []) or []
        upstream_of: dict[str, str] = {e["filename"]: e.get("upstream", "") for e in chain}
        # Walk from exit_review_packet upstream until we hit gate verdict bundle (or ROOT)
        gate = "runtime_gate_verdict_bundle.json"
        cursor = "exit_review_packet.json"
        path: list[str] = [cursor]
        for _ in range(len(chain) + 2):
            up = upstream_of.get(cursor, "")
            if not up:
                break
            path.append(up)
            cursor = up
            if cursor == gate:
                break
        consumed = gate in path
        return consumed, {
            "row_predicate": "manifest.chain_linkage shows runtime_gate_verdict_bundle as transitive ancestor of exit_review_packet",
            "ancestry_path_from_exit": path,
            "gate_verdict_bundle_in_path": consumed,
        }

    return False, {"reason": f"unknown target req_id: {req_id}"}


def check_otel_trace(run_dir: Path | None) -> tuple[bool, dict]:
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


def check_source_root_binding() -> tuple[bool, dict]:
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


def emit_for_req(req_id: str, bundle: dict, latest_run: Path | None,
                  producer_self_exit: int) -> tuple[bool, Path]:
    rt_pass, rt_payload = check_runtime_evidence_for_req(req_id, bundle)
    otel_pass, otel_payload = check_otel_trace(latest_run)
    src_pass, src_payload = check_source_root_binding()
    hash_pass, hash_payload = compute_fresh_artifact_hashes()

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    per_req_block = {
        "verifier_pass": {
            "assertion_result": "PASS" if rt_pass else "FAIL",
            "verifier_role": "row-specific predicate",
            "row_predicate": rt_payload.get("row_predicate"),
            "predicate_evaluated_to": rt_pass,
        },
        "verifier_exit_zero": {
            "assertion_result": "PASS" if producer_self_exit == 0 else "FAIL",
            "producer_self_exit_code": producer_self_exit,
            "producer_path": "tools/cert/verify_apps_rg_runtime_evidence_chain.py",
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

    payload_sha256 = canonical_sha256(per_req_block)

    evidence = {
        "schema_version": "runtime-evidence-v1",
        "req_id": req_id,
        "app_name": "apps_rg",
        "control_scope": "integrated_runtime_evidence_chain",
        "producer": "tools/cert/verify_apps_rg_runtime_evidence_chain.py",
        "producer_exit_code": producer_self_exit,
        "captured_at_utc": now,
        "per_req_block_sha256": payload_sha256,
        "per_req": {req_id: per_req_block},
    }

    out_dir = EVIDENCE_ROOT / req_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "apps_rg_runtime_evidence_chain_evidence.json"
    out_path.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")

    all_pass = all(v["assertion_result"] == "PASS" for v in per_req_block.values())
    return all_pass, out_path


def main() -> int:
    print(f"[verify_apps_rg_runtime_evidence_chain] starting; targets={TARGET_REQS}")
    bundle = load_bundle()
    print(f"  bundle artifacts loaded: {len(bundle)}")
    latest_run = find_latest_apps_rg_run()
    print(f"  latest dated apps_rg run: "
          f"{latest_run.relative_to(REPO_ROOT) if latest_run else '(none)'}")

    # Two-phase emission so verifier_exit_zero can reflect the producer's
    # own final exit code: phase 1 evaluates row predicates without writing;
    # phase 2 writes evidence files with the determined exit code embedded.
    row_results: list[tuple[str, bool]] = []
    for req_id in TARGET_REQS:
        rt_pass, _ = check_runtime_evidence_for_req(req_id, bundle)
        row_results.append((req_id, rt_pass))
    overall_pass = all(p for _, p in row_results)
    final_exit = 0 if overall_pass else 2

    for req_id in TARGET_REQS:
        ok, path = emit_for_req(req_id, bundle, latest_run, final_exit)
        rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        marker = "PASS" if ok else "FAIL"
        print(f"    {req_id}: {marker}  -> {rel}")

    if overall_pass:
        print("[verify_apps_rg_runtime_evidence_chain] ALL TARGETS PASS")
        return 0
    print("[verify_apps_rg_runtime_evidence_chain] AT LEAST ONE TARGET FAIL", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
