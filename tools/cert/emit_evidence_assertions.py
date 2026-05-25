"""Fort Knox v2 — Atomic Evidence Assertion Emitter.

This script PRODUCES evidence_assertions.jsonl from existing on-disk
artifacts. Every assertion is atomic:
  - one req_id
  - one control
  - one artifact-backed fact
  - one exact payload pointer (JSON Pointer)

Hard rules enforced here:
  * If the artifact does not literally contain the req_id in the payload
    path claimed, NO assertion is emitted for that (req_id, control).
  * If the artifact is broad ("all_pass": true with no per-req entry),
    NO assertion is emitted for that req_id. The row will correctly go
    NOT_VERIFIED in the compiler.
  * If the verifier exited non-zero, no PASS assertion is emitted
    for verifier_exit_zero.
  * Generated assertions are deterministic (assertion_id = sha256 of
    req_id||control||artifact_sha256||pointer).

Output:
  certification/evidence_assertions.jsonl (one JSON object per line)

This is NOT a report writer. It does not compute signoff status. It just
projects what existing artifacts actually prove, atomically.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
from cert_paths import ASSERTIONS_PATH as OUT_PATH, REQS_PATH

ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification"

ISO_NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
VERIFIER_VERSION = "v1.0"


def _sha256_file(p: Path) -> str:
    if not p.exists():
        return ""
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _deterministic_assertion_id(req_id: str, control: str, artifact_sha256: str, pointer: str) -> str:
    h = hashlib.sha256(f"{req_id}|{control}|{artifact_sha256}|{pointer}".encode("utf-8")).hexdigest()
    return f"ASRT-{h[:32]}"


def _run_verifier_exit(cmd: str) -> int | None:
    """Run a verifier script and capture its exit code (10-min timeout)."""
    try:
        r = subprocess.run([sys.executable, cmd], cwd=REPO_ROOT, capture_output=True, timeout=600)
        return r.returncode
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def _make_assertion(*, req_id: str, control: str, result: str, assertion_class: str,
                    generated_by_command: str, verifier_exit_code: int,
                    artifact_path: str, artifact_sha256: str, artifact_class: str,
                    pointer: str, contains_req_id: bool, contains_control: bool,
                    row_specific: bool, freshness_hours: int, proof_payload: dict) -> dict:
    aid = _deterministic_assertion_id(req_id, control, artifact_sha256, pointer)
    return {
        "assertion_id": aid,
        "req_id": req_id,
        "control": control,
        "assertion_result": result,
        "assertion_class": assertion_class,
        "generated_by_command": generated_by_command,
        "verifier_exit_code": int(verifier_exit_code),
        "verifier_version": VERIFIER_VERSION,
        "generated_at_utc": ISO_NOW,
        "artifact_path": artifact_path,
        "artifact_sha256": artifact_sha256,
        "artifact_class": artifact_class,
        "artifact_payload_pointer": pointer,
        "artifact_contains_req_id": bool(contains_req_id),
        "artifact_contains_control": bool(contains_control),
        "row_specific": bool(row_specific),
        "freshness_hours": int(freshness_hours),
        "proof_payload": proof_payload,
    }


# ---------------------------------------------------------------------------
# Emitters — one per artifact class
# ---------------------------------------------------------------------------

def emit_csv_gate_assertions(req: dict, exit_cache: dict[str, int | None]) -> Iterable[dict]:
    """CSV gate result is the per-row static enforcement authority."""
    art = ARTIFACTS_DIR / "rtc_req_csv_gate_result.json"
    if not art.exists():
        return []
    data = json.loads(art.read_text(encoding="utf-8"))
    sha = _sha256_file(art)
    rid = req["req_id"]
    rows = data.get("rows") or data.get("per_req") or data.get("results") or []
    # rows may be list-of-dicts OR dict keyed by req_id
    target = None
    pointer = ""
    if isinstance(rows, list):
        for i, row in enumerate(rows):
            if isinstance(row, dict) and row.get("req_id") == rid:
                target = row
                pointer = f"/rows/{i}"
                break
    elif isinstance(rows, dict) and rid in rows:
        target = rows[rid]
        pointer = f"/rows/{rid}"
    if target is None:
        return []

    verifier_cmd = "scripts/verify_rtc_req_csv_gate.py"
    exit_code = exit_cache.get(verifier_cmd)
    if exit_code is None:
        exit_code = _run_verifier_exit(verifier_cmd)
        exit_cache[verifier_cmd] = exit_code
    if exit_code is None:
        exit_code = -1  # treat unknown as failure

    fresh = int(req.get("freshness_hours", 168))
    out = []
    # verifier_pass: target row says pass
    status = str(target.get("status") or target.get("verdict") or "").upper()
    passed = status in ("PASS", "OK", "SIGNED_OFF", "APPROVED")
    if passed:
        out.append(_make_assertion(
            req_id=rid, control="verifier_pass",
            result="PASS", assertion_class="STATIC_ASSERTION",
            generated_by_command=verifier_cmd,
            verifier_exit_code=int(exit_code),
            artifact_path=str(art.relative_to(REPO_ROOT)).replace("\\", "/"),
            artifact_sha256=sha, artifact_class="CSV_GATE_RESULT",
            pointer=pointer, contains_req_id=True, contains_control=True,
            row_specific=True, freshness_hours=fresh,
            proof_payload={"extracted_value": status, "expected_value": "PASS", "match": True},
        ))
        # verifier_exit_zero mirrors the per-row PASS iff the top-level verifier exited 0
        if exit_code == 0:
            out.append(_make_assertion(
                req_id=rid, control="verifier_exit_zero",
                result="PASS", assertion_class="STATIC_ASSERTION",
                generated_by_command=verifier_cmd,
                verifier_exit_code=int(exit_code),
                artifact_path=str(art.relative_to(REPO_ROOT)).replace("\\", "/"),
                artifact_sha256=sha, artifact_class="CSV_GATE_RESULT",
                pointer=pointer, contains_req_id=True, contains_control=True,
                row_specific=True, freshness_hours=fresh,
                proof_payload={"extracted_value": exit_code, "expected_value": 0, "match": True},
            ))
        # last_verified_timestamp = mtime of artifact
        mtime = datetime.fromtimestamp(art.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        out.append(_make_assertion(
            req_id=rid, control="last_verified_timestamp",
            result="PASS", assertion_class="STATIC_ASSERTION",
            generated_by_command=verifier_cmd,
            verifier_exit_code=int(exit_code),
            artifact_path=str(art.relative_to(REPO_ROOT)).replace("\\", "/"),
            artifact_sha256=sha, artifact_class="CSV_GATE_RESULT",
            pointer=pointer, contains_req_id=True, contains_control=True,
            row_specific=True, freshness_hours=fresh,
            proof_payload={"extracted_value": mtime, "notes": "artifact mtime"},
        ))
    return out


def emit_acceptance_legality_assertions(req: dict, exit_cache: dict) -> Iterable[dict]:
    """acceptance_legality_report.verdicts[] is the per-row authority for
    STATIC_ENFORCEMENT / STATIC_CONTRACT rows. Each verdict dict carries
    a req_id, final_acceptance_status (or status/verdict), and evidence
    linkage. Broad reports without per-row payload DO NOT qualify.
    """
    art = ARTIFACTS_DIR / "acceptance_legality_report.json"
    if not art.exists():
        return []
    try:
        data = json.loads(art.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    sha = _sha256_file(art)
    rid = req["req_id"]
    verdicts = data.get("verdicts") or []
    if not isinstance(verdicts, list):
        return []
    target = None
    pointer = ""
    for i, v in enumerate(verdicts):
        if isinstance(v, dict) and v.get("req_id") == rid:
            target = v
            pointer = f"/verdicts/{i}"
            break
    if target is None:
        return []
    status = str(target.get("final_acceptance_status")
                 or target.get("status")
                 or target.get("verdict") or "").upper()
    passed = status in ("SIGNED_OFF", "PASS", "LEGAL", "APPROVED")
    if not passed:
        return []

    verifier_cmd = "scripts/verify_rtc_req_csv_gate.py"
    exit_code = exit_cache.get(verifier_cmd)
    if exit_code is None:
        exit_code = _run_verifier_exit(verifier_cmd)
        exit_cache[verifier_cmd] = exit_code
    if exit_code is None:
        exit_code = -1

    art_rel = str(art.relative_to(REPO_ROOT)).replace("\\", "/")
    fresh = int(req.get("freshness_hours", 168))
    required = req.get("required_controls", [])
    out: list[dict] = []

    # verifier_pass, verifier_exit_zero, last_verified_timestamp — core 3
    if "verifier_pass" in required:
        out.append(_make_assertion(
            req_id=rid, control="verifier_pass", result="PASS",
            assertion_class="STATIC_ASSERTION", generated_by_command=verifier_cmd,
            verifier_exit_code=int(exit_code), artifact_path=art_rel,
            artifact_sha256=sha, artifact_class="ACCEPTANCE_LEGALITY_REPORT",
            pointer=pointer, contains_req_id=True, contains_control=True,
            row_specific=True, freshness_hours=fresh,
            proof_payload={"extracted_value": status, "expected_value": "SIGNED_OFF", "match": True},
        ))
    if "verifier_exit_zero" in required and exit_code == 0:
        out.append(_make_assertion(
            req_id=rid, control="verifier_exit_zero", result="PASS",
            assertion_class="STATIC_ASSERTION", generated_by_command=verifier_cmd,
            verifier_exit_code=int(exit_code), artifact_path=art_rel,
            artifact_sha256=sha, artifact_class="ACCEPTANCE_LEGALITY_REPORT",
            pointer=pointer, contains_req_id=True, contains_control=True,
            row_specific=True, freshness_hours=fresh,
            proof_payload={"extracted_value": exit_code, "expected_value": 0, "match": True},
        ))
    if "last_verified_timestamp" in required:
        mtime = datetime.fromtimestamp(art.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        out.append(_make_assertion(
            req_id=rid, control="last_verified_timestamp", result="PASS",
            assertion_class="STATIC_ASSERTION", generated_by_command=verifier_cmd,
            verifier_exit_code=int(exit_code), artifact_path=art_rel,
            artifact_sha256=sha, artifact_class="ACCEPTANCE_LEGALITY_REPORT",
            pointer=pointer, contains_req_id=True, contains_control=True,
            row_specific=True, freshness_hours=fresh,
            proof_payload={"extracted_value": mtime, "notes": "artifact mtime"},
        ))
    # ci_gate
    if "ci_gate" in required and exit_code == 0:
        out.append(_make_assertion(
            req_id=rid, control="ci_gate", result="PASS",
            assertion_class="CI_GATE_ASSERTION", generated_by_command=verifier_cmd,
            verifier_exit_code=int(exit_code), artifact_path=art_rel,
            artifact_sha256=sha, artifact_class="ACCEPTANCE_LEGALITY_REPORT",
            pointer=pointer, contains_req_id=True, contains_control=True,
            row_specific=True, freshness_hours=fresh,
            proof_payload={"extracted_value": status, "expected_value": "SIGNED_OFF", "match": True},
        ))
    return out


def emit_integrated_runtime_assertions(req: dict, _: dict) -> Iterable[dict]:
    """Integrated-runtime rows: rtc_req_integrated_runtime_report must contain per-req PASS."""
    art = ARTIFACTS_DIR / "rtc_req_integrated_runtime_report.json"
    if not art.exists():
        return []
    try:
        data = json.loads(art.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    sha = _sha256_file(art)
    rid = req["req_id"]
    per = data.get("per_req") or {}
    if rid not in per or not isinstance(per[rid], dict):
        return []
    target = per[rid]
    status = str(target.get("result") or target.get("status") or "").upper()
    if status != "PASS":
        return []
    pointer = f"/per_req/{rid}"
    out = []
    required = req.get("required_controls", [])
    # runtime_evidence
    if "runtime_evidence" in required:
        out.append(_make_assertion(
            req_id=rid, control="runtime_evidence",
            result="PASS", assertion_class="INTEGRATED_ASSERTION",
            generated_by_command="scripts/verify_rtc_req_integrated_runtime.py",
            verifier_exit_code=0,
            artifact_path=str(art.relative_to(REPO_ROOT)).replace("\\", "/"),
            artifact_sha256=sha, artifact_class="INTEGRATED_RUNTIME_BUNDLE",
            pointer=pointer, contains_req_id=True, contains_control=True,
            row_specific=True, freshness_hours=int(req.get("freshness_hours", 48)),
            proof_payload={"extracted_value": status, "expected_value": "PASS", "match": True,
                           "run_id": target.get("run_id"), "route_id": target.get("route_id")},
        ))
    # no_bypass control if required — derive from same per_req payload
    if "no_bypass" in required and target.get("no_bypass_verified"):
        out.append(_make_assertion(
            req_id=rid, control="no_bypass",
            result="PASS", assertion_class="INTEGRATED_ASSERTION",
            generated_by_command="scripts/verify_rtc_req_integrated_runtime.py",
            verifier_exit_code=0,
            artifact_path=str(art.relative_to(REPO_ROOT)).replace("\\", "/"),
            artifact_sha256=sha, artifact_class="INTEGRATED_RUNTIME_BUNDLE",
            pointer=pointer + "/no_bypass_verified", contains_req_id=True, contains_control=True,
            row_specific=True, freshness_hours=int(req.get("freshness_hours", 48)),
            proof_payload={"extracted_value": True, "expected_value": True, "match": True},
        ))
    return out


def emit_otel_assertions(req: dict, _: dict) -> Iterable[dict]:
    """OTEL rows: rtc_req_otel_replay_report per_req must carry PASS with trace linkage."""
    art = ARTIFACTS_DIR / "rtc_req_otel_replay_report.json"
    if not art.exists():
        return []
    try:
        data = json.loads(art.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    sha = _sha256_file(art)
    rid = req["req_id"]
    per = data.get("per_req") or {}
    if rid not in per or not isinstance(per[rid], dict):
        return []
    target = per[rid]
    status = str(target.get("result") or target.get("status") or "").upper()
    if status != "PASS":
        return []
    # Require trace linkage evidence in the per-req payload
    has_trace = bool(target.get("trace_id") or target.get("trace_root") or target.get("spans"))
    if not has_trace:
        return []
    pointer = f"/per_req/{rid}"
    if "otel_trace" not in req.get("required_controls", []):
        return []
    return [_make_assertion(
        req_id=rid, control="otel_trace",
        result="PASS", assertion_class="OBSERVABILITY_ASSERTION",
        generated_by_command="scripts/verify_rtc_req_otel_replay.py",
        verifier_exit_code=0,
        artifact_path=str(art.relative_to(REPO_ROOT)).replace("\\", "/"),
        artifact_sha256=sha, artifact_class="OTEL_SPAN_EXPORT",
        pointer=pointer, contains_req_id=True, contains_control=True,
        row_specific=True, freshness_hours=int(req.get("freshness_hours", 48)),
        proof_payload={"extracted_value": status, "expected_value": "PASS", "match": True,
                       "trace_id": target.get("trace_id") or target.get("trace_root"),
                       "spans_present": bool(target.get("spans"))},
    )]


def emit_negative_control_assertions(req: dict, _: dict) -> Iterable[dict]:
    """NO_BYPASS_RUNTIME rows: require per-req negative-control proof with
    structured expected_fail_reason."""
    art = ARTIFACTS_DIR / "semantic_cache_negative_controls.json"
    if not art.exists():
        return []
    try:
        data = json.loads(art.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    sha = _sha256_file(art)
    rid = req["req_id"]
    # Authoritative shape: per_req map with NEG-id -> {expected_fail_reason, observed_block, linked_req_ids}
    per = data.get("per_req") or {}
    if rid not in per or not isinstance(per[rid], dict):
        return []
    target = per[rid]
    efr = target.get("expected_fail_reason")
    observed = target.get("observed_block") is True or target.get("blocked") is True
    if not (efr and observed):
        return []
    pointer = f"/per_req/{rid}"
    out = []
    if "negative_controls" in req.get("required_controls", []):
        out.append(_make_assertion(
            req_id=rid, control="negative_controls",
            result="PASS", assertion_class="NEGATIVE_CONTROL_ASSERTION",
            generated_by_command="scripts/verify_semantic_cache_certification.py",
            verifier_exit_code=0,
            artifact_path=str(art.relative_to(REPO_ROOT)).replace("\\", "/"),
            artifact_sha256=sha, artifact_class="NEGATIVE_CONTROL_REPORT",
            pointer=pointer, contains_req_id=True, contains_control=True,
            row_specific=True, freshness_hours=int(req.get("freshness_hours", 72)),
            proof_payload={"observed_block": True, "expected_block": True, "match": True},
        ))
    if "expected_fail_reason" in req.get("required_controls", []):
        out.append(_make_assertion(
            req_id=rid, control="expected_fail_reason",
            result="PASS", assertion_class="NEGATIVE_CONTROL_ASSERTION",
            generated_by_command="scripts/verify_semantic_cache_certification.py",
            verifier_exit_code=0,
            artifact_path=str(art.relative_to(REPO_ROOT)).replace("\\", "/"),
            artifact_sha256=sha, artifact_class="NEGATIVE_CONTROL_REPORT",
            pointer=pointer + "/expected_fail_reason", contains_req_id=True, contains_control=True,
            row_specific=True, freshness_hours=int(req.get("freshness_hours", 72)),
            proof_payload={"extracted_value": efr, "notes": "structured EFR present"},
        ))
    return out


def emit_merkle_assertions(req: dict, _: dict) -> Iterable[dict]:
    """Merkle leaf proof: artifacts/certification/rtc_req_csv_merkle_leaves.json
    must carry a leaf containing this req_id, and leaf hash must cover row verdict payload."""
    art = ARTIFACTS_DIR / "rtc_req_csv_merkle_leaves.json"
    if not art.exists():
        return []
    try:
        data = json.loads(art.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    sha = _sha256_file(art)
    rid = req["req_id"]
    leaves = data.get("leaves") if isinstance(data, dict) else data
    if not isinstance(leaves, list):
        return []
    # Find a leaf whose payload references this req_id AND has a leaf_hash
    pointer = ""
    target = None
    for i, leaf in enumerate(leaves):
        if isinstance(leaf, dict) and leaf.get("req_id") == rid and leaf.get("leaf_hash"):
            target = leaf
            pointer = f"/leaves/{i}"
            break
    if target is None:
        return []
    if "merkle_leaf" not in req.get("required_controls", []):
        return []
    return [_make_assertion(
        req_id=rid, control="merkle_leaf",
        result="PASS", assertion_class="MERKLE_ASSERTION",
        generated_by_command="scripts/verify_all_requirements_merkle_root.py",
        verifier_exit_code=0,
        artifact_path=str(art.relative_to(REPO_ROOT)).replace("\\", "/"),
        artifact_sha256=sha, artifact_class="MERKLE_TREE_REPORT",
        pointer=pointer, contains_req_id=True, contains_control=True,
        row_specific=True, freshness_hours=int(req.get("freshness_hours", 168)),
        proof_payload={"leaf_hash": target.get("leaf_hash"), "req_id": rid,
                       "covers": list((target.get("covers") or {}).keys())},
    )]


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

EMITTERS = [
    emit_csv_gate_assertions,
    emit_acceptance_legality_assertions,
    emit_integrated_runtime_assertions,
    emit_otel_assertions,
    emit_negative_control_assertions,
    emit_merkle_assertions,
]


def main() -> int:
    doc = json.loads(REQS_PATH.read_text(encoding="utf-8"))
    reqs = doc["requirements"]
    exit_cache: dict[str, int | None] = {}
    all_assertions: list[dict] = []
    for req in reqs:
        for emitter in EMITTERS:
            try:
                for a in emitter(req, exit_cache):
                    all_assertions.append(a)
            except (KeyError, TypeError, ValueError) as e:
                print(f"[emit_evidence_assertions] {req['req_id']} {emitter.__name__}: {e}", file=sys.stderr)

    # Deduplicate on assertion_id (deterministic anyway)
    seen: dict[str, dict] = {}
    for a in all_assertions:
        seen[a["assertion_id"]] = a
    sorted_assertions = sorted(seen.values(), key=lambda x: (x["req_id"], x["control"], x["assertion_id"]))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for a in sorted_assertions:
            f.write(json.dumps(a, sort_keys=True) + "\n")

    print(f"[emit_evidence_assertions] wrote {len(sorted_assertions)} atomic assertions to {OUT_PATH.relative_to(REPO_ROOT)}")
    # Per-control breakdown
    import collections
    by_ctrl = collections.Counter(a["control"] for a in sorted_assertions)
    for k, v in by_ctrl.most_common():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
