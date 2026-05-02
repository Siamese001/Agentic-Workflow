"""Fort Knox L7 evidence verifier — fail-closed.

Verifies row-specific Fort Knox evidence emitted by
``agentic_core.L7_auditability.fortknox.emit_l7_fortknox_evidence``
under ``<artifact_dir>/fortknox_l7_evidence/``.

Fail-closed rejection rules (each emits exit 2 with a specific code):

  L7FK_DIR_MISSING                 — fortknox_l7_evidence/ absent
  L7FK_REQ_FILE_MISSING            — a required RTC-REQ row file absent
  L7FK_LINKED_REQ_IDS_ONLY         — evidence has only ``linked_req_ids``
                                     and no row-specific assertion
  L7FK_GENERIC_ALL_PASS_ROLLUP     — evidence is a generic "all_pass=true"
                                     rollup with no per-row claim
  L7FK_UNAPPROVED_VERIFIER         — approved_verifier not in allowlist
  L7FK_STATIC_FOR_RUNTIME          — claim_type names runtime_* but
                                     artifact_class is static_*
  L7FK_RUNTIME_NO_RUN_IDENTITY     — runtime_* claim missing
                                     run_id / request_id / trace_root
  L7FK_OTEL_NO_SPAN_PAYLOAD        — claim_type contains 'otel' but no
                                     span payload fields present
  L7FK_HASH_MISMATCH               — recomputed deterministic_digest
                                     differs from stored value
  L7FK_POINTER_MISSING             — evidence_payload_pointer references
                                     a path that does not exist on disk
  L7FK_ARTIFACT_HASH_MISMATCH      — stored source_artifact_sha256
                                     differs from recomputed file hash

Exit codes: 0 PASS / 2 FAIL_CLOSED / 3 HARNESS_ERROR.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parents[1]))

from _w2_verifier_common import (  # noqa: E402
    EXIT_HARNESS_ERROR,
    detect_chain_kind,
    fail,
    passed,
    resolve_artifact_dir,
)

try:
    from agentic_core.L7_auditability.fortknox.emit_l7_fortknox_evidence import (  # noqa: E402
        APPROVED_VERIFIERS,
        ROW_TO_FORBIDDEN_ASSERTION,
        ROW_TO_STAGE,
    )
except ImportError as e:  # pragma: no cover
    print(f"[verify_l7_fortknox_evidence] HARNESS_ERROR import: {e}")
    sys.exit(EXIT_HARNESS_ERROR)


_REQUIRED_ROWS: tuple[str, ...] = tuple(
    list(ROW_TO_STAGE.keys())
    + list(ROW_TO_FORBIDDEN_ASSERTION.keys())
    + ["RTC-REQ-081", "RTC-REQ-123"]
)

_REQUIRED_FIELDS: tuple[str, ...] = (
    "schema_version",
    "req_id",
    "claim_type",
    "control",
    "artifact_class",
    "generated_by_command",
    "approved_verifier",
    "verifier_exit_code",
    "assertion_result",
    "run_id",
    "request_id",
    "trace_root",
    "source_artifact_ref",
    "source_artifact_sha256",
    "evidence_payload_pointer",
    "artifact_payload_sha256",
    "last_verified_utc",
    "deterministic_digest",
)


def _digest(payload: Mapping[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "deterministic_digest"}
    blob = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
    return f"sha256:{hashlib.sha256(blob.encode('utf-8')).hexdigest()}"


def _file_sha256(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        blob = path.read_bytes()
    except OSError:
        return ""
    return f"sha256:{hashlib.sha256(blob).hexdigest()}"


def _read_json(p: Path) -> dict[str, Any] | None:
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return d if isinstance(d, dict) else None


def _verify_row(
    *,
    req_id: str,
    body: Mapping[str, Any],
    fk_dir: Path,
    art_dir: Path,
) -> tuple[bool, str, str]:
    """Verify one row evidence body. Returns (ok, code, message)."""
    # Required-fields check.
    for fld in _REQUIRED_FIELDS:
        if fld not in body:
            return False, "L7FK_REQ_FILE_MISSING", (
                f"{req_id}: missing required field {fld!r}"
            )

    if body.get("req_id") != req_id:
        return False, "L7FK_REQ_FILE_MISSING", (
            f"{req_id}: body.req_id={body.get('req_id')!r} != filename req_id"
        )

    # Reject linked_req_ids-only evidence (no row-specific assertion).
    if "linked_req_ids" in body and "claim_type" not in body:
        return False, "L7FK_LINKED_REQ_IDS_ONLY", (
            f"{req_id}: linked_req_ids-only evidence is not row-specific"
        )
    if isinstance(body.get("control"), str) and body["control"].lower().startswith(
        "linked_req_ids"
    ):
        return False, "L7FK_LINKED_REQ_IDS_ONLY", (
            f"{req_id}: control field is linked_req_ids-only"
        )

    # Reject generic all_pass rollups.
    ct = str(body.get("claim_type") or "").lower()
    if "all_pass" in ct or "rollup" in ct or ct == "generic":
        return False, "L7FK_GENERIC_ALL_PASS_ROLLUP", (
            f"{req_id}: claim_type={body.get('claim_type')!r} is generic rollup"
        )

    # Approved verifier allowlist.
    av = str(body.get("approved_verifier") or "")
    if av not in APPROVED_VERIFIERS:
        return False, "L7FK_UNAPPROVED_VERIFIER", (
            f"{req_id}: approved_verifier={av!r} not in allowlist"
        )

    # Static-for-runtime detection.
    artifact_class = str(body.get("artifact_class") or "").lower()
    if ct.startswith("runtime") and artifact_class.startswith("static"):
        return False, "L7FK_STATIC_FOR_RUNTIME", (
            f"{req_id}: runtime claim {ct!r} backed by static artifact_class "
            f"{artifact_class!r}"
        )

    # Runtime claims require run_id/request_id/trace_root.
    if ct.startswith("runtime"):
        for ident in ("run_id", "request_id", "trace_root"):
            if not str(body.get(ident) or ""):
                return False, "L7FK_RUNTIME_NO_RUN_IDENTITY", (
                    f"{req_id}: runtime claim missing {ident}"
                )

    # OTEL claims require span payload fields.
    if "otel" in ct or "otel" in str(body.get("control") or "").lower():
        spf = body.get("span_payload") or body.get("span_attributes")
        if not isinstance(spf, (dict, list)) or not spf:
            return False, "L7FK_OTEL_NO_SPAN_PAYLOAD", (
                f"{req_id}: OTEL claim missing span_payload/span_attributes"
            )

    # Deterministic digest recomputation.
    stored_digest = str(body.get("deterministic_digest") or "")
    recomputed = _digest(body)
    if stored_digest != recomputed:
        return False, "L7FK_HASH_MISMATCH", (
            f"{req_id}: deterministic_digest stored={stored_digest!r} != "
            f"recomputed={recomputed!r}"
        )

    # Evidence pointer presence.
    pointer = str(body.get("evidence_payload_pointer") or "")
    if pointer:
        # The pointer is "<chain_dir>/<filename>"; resolve relative to
        # the parent of the chain directory (i.e. art_dir.parent).
        candidate_paths = [
            art_dir.parent / pointer,
            art_dir / Path(pointer).name,
        ]
        if not any(p.exists() for p in candidate_paths):
            return False, "L7FK_POINTER_MISSING", (
                f"{req_id}: evidence_payload_pointer={pointer!r} not found "
                f"on disk under {art_dir.parent} or {art_dir}"
            )

    # Source artifact hash recomputation (when ref is artifact://<filename>).
    src_ref = str(body.get("source_artifact_ref") or "")
    if src_ref.startswith("artifact://"):
        fname = src_ref[len("artifact://"):]
        src_path = art_dir / fname
        if src_path.exists():
            stored_src_sha = str(body.get("source_artifact_sha256") or "")
            recomputed_src_sha = _file_sha256(src_path)
            if stored_src_sha and recomputed_src_sha and stored_src_sha != recomputed_src_sha:
                return False, "L7FK_ARTIFACT_HASH_MISMATCH", (
                    f"{req_id}: source_artifact_sha256 stored={stored_src_sha!r} "
                    f"!= recomputed={recomputed_src_sha!r} for {fname}"
                )

    return True, "PASS", f"{req_id} OK"


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    kind = detect_chain_kind(art_dir)
    print(
        f"[verify_l7_fortknox_evidence] artifact_dir={art_dir} chain_kind={kind}"
    )

    fk_dir = art_dir / "fortknox_l7_evidence"
    if not fk_dir.exists() or not fk_dir.is_dir():
        return fail(
            "L7FK_DIR_MISSING",
            f"fortknox_l7_evidence/ directory not found at {fk_dir}",
        )

    rows_verified = 0
    for req_id in _REQUIRED_ROWS:
        path = fk_dir / f"{req_id}__l7_evidence.json"
        body = _read_json(path)
        if body is None:
            return fail(
                "L7FK_REQ_FILE_MISSING",
                f"{req_id}: evidence file missing or unreadable at {path}",
            )
        ok, code, msg = _verify_row(
            req_id=req_id, body=body, fk_dir=fk_dir, art_dir=art_dir
        )
        if not ok:
            return fail(code, msg)
        rows_verified += 1

    return passed(
        f"L7 Fort Knox evidence valid (chain_kind={kind}, "
        f"rows_verified={rows_verified}, dir={fk_dir.name})"
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
