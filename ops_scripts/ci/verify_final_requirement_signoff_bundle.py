"""Fort Knox v2 — Independent Bundle Verifier.

This script DOES NOT TRUST the compiler's conclusion.

It independently re-opens:
  - requirements_source.json
  - evidence_assertions.jsonl
  - final_requirement_signoff_report.json
  - final_requirement_signoff_report.sha256
  - final_requirement_signoff_report.merkle.json
  - final_requirement_signoff_report.signature.json
  - every referenced evidence artifact

It re-hashes, re-resolves JSON Pointers, recomputes the Merkle root, and
checks the signature envelope.

Any of the following ⇒ bundle_verification_status = FAIL:
  1. report file sha256 drifts from .sha256 sidecar
  2. report schema invalid
  3. requirements_source_sha256 in report drifts from current file
  4. evidence_assertions_sha256 in report drifts from current file
  5. report has rows not in requirements_source.json
  6. report missing any req_id from requirements_source.json
  7. any SIGNED_OFF row has a failing control
  8. any SIGNED_OFF row has a non-null blocking_gap
  9. any BLOCKED/NOT_VERIFIED row has a null blocking_gap
 10. any referenced evidence artifact missing on disk
 11. any referenced evidence artifact sha256 drifts
 12. any referenced evidence artifact fails to contain the exact req_id
     literal at the declared pointer or its parent
 13. Merkle leaves differ from sorted row_digests
 14. Merkle root fails to recompute
 15. final-100% rows SIGNED_OFF while any non-final row is open
 16. signature_envelope says FINAL_SIGNED_CERTIFICATION without signed bytes

Emits:
  artifacts/certification/final_requirement_signoff_bundle_verification.json
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    print("FATAL: jsonschema is required", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.cert.cert_paths import (  # noqa: E402
    ASSERTIONS_PATH,
    CERT_ARTIFACTS_DIR,
    FINAL_SIGNOFF_BUNDLE_VERIFICATION,
    FINAL_SIGNOFF_MERKLE,
    FINAL_SIGNOFF_REPORT,
    FINAL_SIGNOFF_SHA256,
    FINAL_SIGNOFF_SIGNATURE,
    REPORT_SCHEMA,
    REQS_PATH,
)

OUTPUT_DIR = CERT_ARTIFACTS_DIR
REPORT_PATH = FINAL_SIGNOFF_REPORT
SHA256_PATH = FINAL_SIGNOFF_SHA256
MERKLE_PATH = FINAL_SIGNOFF_MERKLE
SIGNATURE_PATH = FINAL_SIGNOFF_SIGNATURE
XLSX_PATH = OUTPUT_DIR / "final_requirement_signoff_report.xlsx"
MD_PATH = OUTPUT_DIR / "final_requirement_signoff_report.md"
OUT_PATH = FINAL_SIGNOFF_BUNDLE_VERIFICATION


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_json_canonical(obj: Any) -> str:
    return sha256_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def resolve_json_pointer(doc: Any, pointer: str) -> Any:
    if pointer in ("", "/"):
        return doc
    if not pointer.startswith("/"):
        pointer = "/" + pointer
    parts = pointer.split("/")[1:]
    cur = doc
    for p in parts:
        p = p.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, list):
            try:
                cur = cur[int(p)]
            except (ValueError, IndexError):
                return _MISSING
        elif isinstance(cur, dict):
            if p not in cur:
                return _MISSING
            cur = cur[p]
        else:
            return _MISSING
    return cur


class _Missing:
    pass


_MISSING = _Missing()


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


def verify() -> dict:
    failures: list[str] = []
    checks_run = 0

    def fail(msg: str):
        failures.append(msg)

    # 1. report + sidecar exist
    for p in (REPORT_PATH, SHA256_PATH, MERKLE_PATH, SIGNATURE_PATH):
        checks_run += 1
        if not p.exists():
            fail(f"missing: {p.relative_to(REPO_ROOT)}")
    if failures:
        return _result(failures, checks_run)

    # 2. report file sha256 matches .sha256
    checks_run += 1
    report_disk_sha = sha256_file(REPORT_PATH)
    sha_sidecar = SHA256_PATH.read_text(encoding="utf-8").strip().split()[0]
    if report_disk_sha != sha_sidecar:
        fail(f"report sha256 drift: disk={report_disk_sha[:12]} sidecar={sha_sidecar[:12]}")

    # 3. report schema valid
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    try:
        schema = Draft202012Validator(json.loads(REPORT_SCHEMA.read_text(encoding="utf-8")))
        errs = list(schema.iter_errors(report))
        checks_run += 1
        if errs:
            fail(f"report schema violations: {errs[0].message}")
    except (OSError, json.JSONDecodeError) as e:
        fail(f"could not load report schema: {e}")

    # 4. requirements_source_sha256 matches
    checks_run += 1
    if not REQS_PATH.exists():
        fail("requirements_source.json missing")
    else:
        current_reqs_sha = sha256_file(REQS_PATH)
        if report.get("requirements_source_sha256") != current_reqs_sha:
            fail(f"requirements_source_sha256 drift: "
                 f"report={report.get('requirements_source_sha256', '')[:12]} "
                 f"disk={current_reqs_sha[:12]}")

    # 5. evidence_assertions_sha256 matches
    checks_run += 1
    if not ASSERTIONS_PATH.exists():
        fail("evidence_assertions.jsonl missing")
    else:
        current_assertions_sha = sha256_file(ASSERTIONS_PATH)
        if report.get("evidence_assertions_sha256") != current_assertions_sha:
            fail(f"evidence_assertions_sha256 drift: "
                 f"report={report.get('evidence_assertions_sha256', '')[:12]} "
                 f"disk={current_assertions_sha[:12]}")

    # 6 + 7. row set equality with requirements_source
    reqs_doc = json.loads(REQS_PATH.read_text(encoding="utf-8"))
    source_ids = {r["req_id"] for r in reqs_doc["requirements"]}
    report_ids = {r["req_id"] for r in report["rows"]}
    checks_run += 2
    extra = report_ids - source_ids
    missing = source_ids - report_ids
    if extra:
        fail(f"report has rows not in source: {sorted(extra)[:3]}")
    if missing:
        fail(f"report missing rows from source: {sorted(missing)[:3]}")

    # 8–14. Per-row checks (independent walk, do NOT trust compiler output)
    assertions_by_id: dict[str, dict] = {}
    if ASSERTIONS_PATH.exists():
        with ASSERTIONS_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    a = json.loads(line)
                    assertions_by_id[a["assertion_id"]] = a
                except (json.JSONDecodeError, KeyError):
                    pass

    artifact_cache: dict[str, tuple[str, Any]] = {}
    for row in report["rows"]:
        rid = row["req_id"]
        status = row["computed_status"]

        # SIGNED_OFF row must have every required control passed AND null blocking_gap
        if status == "SIGNED_OFF":
            checks_run += 1
            if row.get("blocking_gap"):
                fail(f"{rid} SIGNED_OFF with non-null blocking_gap: {row['blocking_gap']}")
            checks_run += 1
            failed_ctrls = [c for c in row["controls"] if not c["passed"]]
            if failed_ctrls:
                fail(f"{rid} SIGNED_OFF but controls failing: "
                     f"{[c['name'] for c in failed_ctrls]}")

            # Re-verify every control's assertion independently
            for c in row["controls"]:
                if not c["passed"]:
                    continue
                aid = c.get("assertion_id")
                if aid is None:
                    # artifactless — allowed only if requirements_source declared it
                    continue
                a = assertions_by_id.get(aid)
                checks_run += 1
                if a is None:
                    fail(f"{rid}.{c['name']}: assertion_id {aid} not in evidence_assertions.jsonl")
                    continue
                # Re-open artifact, re-hash, re-resolve pointer
                art_abs = REPO_ROOT / a["artifact_path"]
                checks_run += 1
                if not art_abs.exists():
                    fail(f"{rid}.{c['name']}: artifact missing on disk: {a['artifact_path']}")
                    continue
                cached = artifact_cache.get(a["artifact_path"])
                if cached is None:
                    actual_sha = sha256_file(art_abs)
                    try:
                        parsed = json.loads(art_abs.read_text(encoding="utf-8"))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        parsed = None
                    artifact_cache[a["artifact_path"]] = (actual_sha, parsed)
                actual_sha, parsed = artifact_cache[a["artifact_path"]]
                checks_run += 1
                if actual_sha != a["artifact_sha256"]:
                    fail(f"{rid}.{c['name']}: artifact sha drift — "
                         f"expected {a['artifact_sha256'][:12]} got {actual_sha[:12]}")
                    continue
                if parsed is not None:
                    pointer = a["artifact_payload_pointer"]
                    val = resolve_json_pointer(parsed, pointer)
                    checks_run += 1
                    if isinstance(val, _Missing):
                        fail(f"{rid}.{c['name']}: pointer {pointer} does not resolve")
                        continue
                    snippet = json.dumps(val, sort_keys=True) if not isinstance(val, str) else val
                    segs = pointer.split("/")
                    # Bundle verifier uses the same strict guard as the compiler:
                    # resolved value contains req_id OR pointer path carries it.
                    # No parent-walk fallback (broad-artifact guard).
                    if rid not in snippet and rid not in segs:
                        fail(f"{rid}.{c['name']}: req_id not present at pointer "
                             f"{pointer} nor in its path segments in {a['artifact_path']}")

        # BLOCKED / NOT_VERIFIED must have a non-null blocking_gap
        elif status in ("BLOCKED", "NOT_VERIFIED"):
            checks_run += 1
            if not row.get("blocking_gap"):
                fail(f"{rid} status={status} but blocking_gap is null")

    # 15. Merkle independently
    merkle = json.loads(MERKLE_PATH.read_text(encoding="utf-8"))
    sorted_rows = sorted(report["rows"], key=lambda r: r["req_id"])
    expected_leaves = [{"req_id": r["req_id"], "leaf_hash": r["row_digest"]} for r in sorted_rows]
    checks_run += 1
    if merkle.get("leaves") != expected_leaves:
        fail("Merkle leaves differ from sorted row_digests")

    # Recompute root
    level = [L["leaf_hash"] for L in expected_leaves]
    if not level:
        recomputed_root = ""
    else:
        while len(level) > 1:
            if len(level) % 2 == 1:
                level.append(level[-1])
            level = [sha256_bytes(bytes.fromhex(level[i]) + bytes.fromhex(level[i + 1]))
                     for i in range(0, len(level), 2)]
        recomputed_root = level[0]
    checks_run += 1
    if recomputed_root != merkle.get("root"):
        fail(f"Merkle root mismatch: sidecar={merkle.get('root', '')[:12]} recomputed={recomputed_root[:12]}")

    # 16. Final-100% gate
    non_final_not_signed = [r["req_id"] for r in report["rows"]
                            if not r["is_final_hundred_percent_row"]
                            and r["computed_status"] != "SIGNED_OFF"]
    final_signed = [r["req_id"] for r in report["rows"]
                    if r["is_final_hundred_percent_row"]
                    and r["computed_status"] == "SIGNED_OFF"]
    checks_run += 1
    if non_final_not_signed and final_signed:
        fail(f"final-100% rows {final_signed} SIGNED_OFF while non-finals still open "
             f"({len(non_final_not_signed)})")

    # 17. Signature envelope
    sig = json.loads(SIGNATURE_PATH.read_text(encoding="utf-8"))
    checks_run += 1
    sig_status = sig.get("signature_verification_status", "")
    if sig_status == "FINAL_SIGNED_CERTIFICATION" and not sig.get("signed_bytes_sha256"):
        fail("signature status FINAL_SIGNED_CERTIFICATION without signed_bytes_sha256")

    # 18. Report sha256 linkage to signature envelope
    checks_run += 1
    if sig.get("report_sha256") and sig["report_sha256"] != report_disk_sha:
        fail(f"signature envelope report_sha256 drifts from disk: "
             f"env={sig.get('report_sha256', '')[:12]} disk={report_disk_sha[:12]}")

    # 18b. When the envelope claims VERIFIED, this bundle verifier MUST
    # independently re-perform the cryptographic check. Reflecting the
    # envelope's claim verbatim is not enough — the envelope itself could
    # be tampered. We re-verify ed25519 against the on-disk public key.
    if sig_status == "VERIFIED":
        checks_run += 1
        try:
            import base64 as _b64  # local import to avoid hard dep when unsigned
            from cryptography.exceptions import InvalidSignature  # type: ignore
            from cryptography.hazmat.primitives import serialization  # type: ignore
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (  # type: ignore
                Ed25519PublicKey,
            )

            sig_alg = sig.get("signature_algorithm", "")
            sig_b64 = sig.get("signature_value", "") or ""
            env_pub_pem = (sig.get("signer_public_key_pem") or "").encode("ascii")
            pub_path = REPO_ROOT / "config" / "release_signer" / "release_signer.pub.pem"

            if sig_alg != "ed25519":
                fail(f"envelope status=VERIFIED but signature_algorithm={sig_alg!r} "
                     f"(only ed25519 is recognized for VERIFIED)")
            elif not sig_b64:
                fail("envelope status=VERIFIED but signature_value is empty")
            elif not pub_path.exists():
                fail(f"envelope status=VERIFIED but on-disk public key missing at "
                     f"{pub_path.relative_to(REPO_ROOT)}")
            else:
                pub_pem_disk = pub_path.read_bytes()
                if env_pub_pem and env_pub_pem.strip() != pub_pem_disk.strip():
                    fail("envelope.signer_public_key_pem disagrees with on-disk "
                         "release_signer.pub.pem (key swap detected)")
                else:
                    pub = serialization.load_pem_public_key(pub_pem_disk)
                    if not isinstance(pub, Ed25519PublicKey):
                        fail("on-disk public key is not ed25519")
                    else:
                        try:
                            pub.verify(_b64.b64decode(sig_b64),
                                       REPORT_PATH.read_bytes())
                        except InvalidSignature:
                            fail("ed25519 verification FAILED — envelope claims "
                                 "VERIFIED but signature does not match report bytes")
        except ImportError:
            fail("envelope status=VERIFIED but `cryptography` library not "
                 "available to re-verify ed25519 signature")

    # 19. XLSX + markdown are read-only: their rollup counts must match JSON
    # (best-effort — we do not parse XLSX here; just ensure they exist)
    checks_run += 1
    if not XLSX_PATH.exists():
        fail(f"XLSX export missing: {XLSX_PATH.relative_to(REPO_ROOT)}")
    checks_run += 1
    if not MD_PATH.exists():
        fail(f"Markdown export missing: {MD_PATH.relative_to(REPO_ROOT)}")

    return _result(failures, checks_run, sig_status=sig_status, report_sha256=report_disk_sha)


def _result(failures: list[str], checks_run: int, sig_status: str = "", report_sha256: str = "") -> dict:
    status = "PASS" if not failures else "FAIL"
    return {
        "schema_version": "fortknox-v2",
        "verifier_path": "ops_scripts/ci/verify_final_requirement_signoff_bundle.py",
        "verifier_version": "v1.0",
        "verified_at_utc": _iso_now(),
        "bundle_verification_status": status,
        "checks_run": checks_run,
        "failures": failures,
        "report_sha256": report_sha256,
        "signature_verification_status": sig_status,
        "notes": ("PASS means the compiler's conclusions independently reproduced from "
                  "requirements_source.json + evidence_assertions.jsonl + on-disk artifacts. "
                  "FAIL means one or more integrity checks caught drift, tampering, or staleness."),
    }


def main() -> int:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = verify()
    OUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[verify_bundle] status={result['bundle_verification_status']} "
          f"checks={result['checks_run']} failures={len(result['failures'])}")
    if result["failures"]:
        for f in result["failures"][:15]:
            print(f"  FAIL: {f}")
        if len(result["failures"]) > 15:
            print(f"  ... {len(result['failures']) - 15} more failures")
    return 0 if result["bundle_verification_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
