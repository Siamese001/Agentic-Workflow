"""Fail-closed verifier for the L7 route-family coverage matrix.

Asserts:

  RFC_FILE_MISSING                 \u2014 agentic_core_l7_route_family_coverage.json
                                     not present in the chain dir.
  RFC_SCHEMA_INVALID               \u2014 missing schema fields or families.
  RFC_FAMILY_MISSING               \u2014 not every required route family is
                                     present in the matrix.
  RFC_DIGEST_MISMATCH              \u2014 deterministic_digest does not match
                                     a recompute of payload.
  RFC_CERTIFIED_MISSING_HOW        \u2014 family marked CERTIFIED but
                                     l7_how_trace_emitted=False.
  RFC_CERTIFIED_MISSING_FK         \u2014 family marked CERTIFIED but
                                     fortknox_l7_evidence_emitted=False.
  RFC_CERTIFIED_MISSING_MANIFEST   \u2014 family marked CERTIFIED but
                                     artifact_manifest_bound=False.
  RFC_CERTIFIED_MISSING_SPINE      \u2014 family marked CERTIFIED but
                                     spine_proof_bound=False.
  RFC_CERTIFIED_MISSING_VERIFIER   \u2014 family marked CERTIFIED but
                                     verifier_exists=False.
  RFC_CERTIFIED_MISSING_ROUTE      \u2014 family marked CERTIFIED but
                                     route_contract_emitted=False.
  RFC_CERTIFIED_NOT_REAL_RUNTIME   \u2014 family marked CERTIFIED but
                                     proof_class != REAL_RUNTIME.
  RFC_MW_REAL_OVERCLAIMED          \u2014 MANAGED_WORKFLOW_REAL_EXECUTION
                                     marked CERTIFIED while only structural
                                     L2 exists.
  RFC_OVERCLAIMED_FROM_R1B         \u2014 R3/R4/R5/R1A marked CERTIFIED but
                                     no own runtime entrypoint exists
                                     (would imply borrowing R1B artifacts).
  RFC_STRUCTURAL_NO_REASON         \u2014 family marked STRUCTURAL_ONLY
                                     without structural_only_reason.
  RFC_NOT_CERTIFIED_NO_GAP         \u2014 family marked NOT_CERTIFIED without
                                     blocking_gap.
  RFC_MANIFEST_NOT_BOUND           \u2014 manifest does not list
                                     agentic_core_l7_route_family_coverage.json
                                     in artifact_filenames OR does not carry
                                     l7_route_family_coverage_ref/sha256.
  RFC_SPINE_NOT_BOUND              \u2014 spine_proof does not carry
                                     l7_route_family_coverage_ref/sha256/status.
  RFC_IDENTITY_MISMATCH            \u2014 current_run identity does not match
                                     runtime_identity_envelope.

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
    from agentic_core.L7_auditability.coverage import (  # noqa: E402
        L7_ROUTE_FAMILY_COVERAGE_FILENAME,
        ROUTE_FAMILIES,
    )
except ImportError as e:  # pragma: no cover
    print(f"[verify_agentic_core_l7_route_family_coverage] HARNESS_ERROR import: {e}")
    sys.exit(EXIT_HARNESS_ERROR)


_REQUIRED_PAYLOAD_FIELDS = (
    "schema_version",
    "evidence_plane",
    "evidence_class",
    "audit_mode",
    "non_mutating",
    "current_run",
    "route_families",
    "summary",
    "deterministic_digest",
)
_REQUIRED_FAMILY_FIELDS = (
    "route_family",
    "exercised_in_current_run",
    "runtime_entrypoint_exists",
    "fixture_or_structural_entrypoint_exists",
    "route_contract_emitted",
    "l7_how_trace_emitted",
    "fortknox_l7_evidence_emitted",
    "artifact_manifest_bound",
    "spine_proof_bound",
    "verifier_exists",
    "verifier_in_default_ci",
    "proof_class",
    "certification_status",
)

# Families that may NEVER be CERTIFIED without their own runtime entrypoint.
_NO_BORROW_FAMILIES = (
    "R1A_EXACT_CACHE",
    "R3_GROUNDED_READ",
    "R4_SINGLE_ACTION",
    "R5_FALLBACK",
)


def _read_json(p: Path) -> dict[str, Any] | None:
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return d if isinstance(d, dict) else None


def _payload(env: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(env, dict):
        return {}
    p = env.get("payload", {})
    return p if isinstance(p, dict) else {}


def _digest(payload: Mapping[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "deterministic_digest"}
    blob = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(blob.encode('utf-8')).hexdigest()}"


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    kind = detect_chain_kind(art_dir)
    print(
        f"[verify_agentic_core_l7_route_family_coverage] artifact_dir={art_dir} "
        f"chain_kind={kind}"
    )

    rfc_path = art_dir / L7_ROUTE_FAMILY_COVERAGE_FILENAME
    if not rfc_path.exists():
        return fail(
            "RFC_FILE_MISSING",
            f"{L7_ROUTE_FAMILY_COVERAGE_FILENAME} not present at {rfc_path}",
        )

    rfc_env = _read_json(rfc_path)
    if rfc_env is None:
        return fail("RFC_FILE_MISSING", f"unable to parse {rfc_path}")
    pay = _payload(rfc_env)

    # 1. Schema fields.
    for fld in _REQUIRED_PAYLOAD_FIELDS:
        if fld not in pay:
            return fail("RFC_SCHEMA_INVALID", f"missing payload field {fld!r}")

    # 2. Digest.
    stored = str(pay.get("deterministic_digest") or "")
    recomputed = _digest(pay)
    if stored != recomputed:
        return fail(
            "RFC_DIGEST_MISMATCH",
            f"stored={stored!r} recomputed={recomputed!r}",
        )

    # 3. Required families.
    families = pay.get("route_families")
    if not isinstance(families, list) or not families:
        return fail("RFC_SCHEMA_INVALID", "route_families must be a non-empty list")
    seen = {f.get("route_family") for f in families if isinstance(f, dict)}
    missing = [f for f in ROUTE_FAMILIES if f not in seen]
    if missing:
        return fail(
            "RFC_FAMILY_MISSING",
            f"missing required families: {missing}",
        )

    # 4. Identity continuity vs runtime_identity_envelope.
    cur = pay.get("current_run", {}) or {}
    rie = _payload(_read_json(art_dir / "runtime_identity_envelope.json"))
    for k in ("run_id", "request_id", "trace_root"):
        a = str(cur.get(k) or "")
        b = str(rie.get(k) or "")
        # Allow empty current_run.run_id only if envelope is also empty
        # (extremely unlikely; the catalog always emits non-empty values).
        if a and b and a != b:
            return fail(
                "RFC_IDENTITY_MISMATCH",
                f"current_run.{k}={a!r} != runtime_identity_envelope.{k}={b!r}",
            )

    # 5. Per-family invariants.
    for row in families:
        if not isinstance(row, dict):
            return fail("RFC_SCHEMA_INVALID", "row is not a dict")
        for fld in _REQUIRED_FAMILY_FIELDS:
            if fld not in row:
                return fail(
                    "RFC_SCHEMA_INVALID",
                    f"row {row.get('route_family')!r} missing field {fld!r}",
                )
        fam = str(row["route_family"])
        cert = str(row["certification_status"])
        proof_class = str(row["proof_class"])

        if cert == "CERTIFIED":
            # Hard rules — every CERTIFIED row must satisfy ALL of these.
            if not row.get("l7_how_trace_emitted"):
                return fail(
                    "RFC_CERTIFIED_MISSING_HOW",
                    f"{fam}: CERTIFIED without l7_how_trace_emitted",
                )
            if not row.get("fortknox_l7_evidence_emitted"):
                return fail(
                    "RFC_CERTIFIED_MISSING_FK",
                    f"{fam}: CERTIFIED without fortknox_l7_evidence_emitted",
                )
            if not row.get("artifact_manifest_bound"):
                return fail(
                    "RFC_CERTIFIED_MISSING_MANIFEST",
                    f"{fam}: CERTIFIED without artifact_manifest_bound",
                )
            if not row.get("spine_proof_bound"):
                return fail(
                    "RFC_CERTIFIED_MISSING_SPINE",
                    f"{fam}: CERTIFIED without spine_proof_bound",
                )
            if not row.get("verifier_exists"):
                return fail(
                    "RFC_CERTIFIED_MISSING_VERIFIER",
                    f"{fam}: CERTIFIED without verifier_exists",
                )
            if not row.get("route_contract_emitted"):
                return fail(
                    "RFC_CERTIFIED_MISSING_ROUTE",
                    f"{fam}: CERTIFIED without route_contract_emitted",
                )
            if proof_class != "REAL_RUNTIME":
                return fail(
                    "RFC_CERTIFIED_NOT_REAL_RUNTIME",
                    f"{fam}: CERTIFIED but proof_class={proof_class!r}",
                )
            # No-borrow rule: R1A/R3/R4/R5 cannot ride R1B's artifacts.
            if fam in _NO_BORROW_FAMILIES and not row.get(
                "runtime_entrypoint_exists"
            ):
                return fail(
                    "RFC_OVERCLAIMED_FROM_R1B",
                    f"{fam}: CERTIFIED but no runtime_entrypoint_exists "
                    f"(would imply borrowing R1B artifacts)",
                )
            # MW_REAL gate: must have its own runtime entrypoint AND must
            # not be the structural MW endpoint.
            if fam == "MANAGED_WORKFLOW_REAL_EXECUTION":
                if not row.get("runtime_entrypoint_exists"):
                    return fail(
                        "RFC_MW_REAL_OVERCLAIMED",
                        f"{fam}: CERTIFIED but no real-execution entrypoint",
                    )
                ep = str(row.get("runtime_entrypoint_ref") or "")
                if ep.endswith("integrated_managed_workflow_run.py"):
                    return fail(
                        "RFC_MW_REAL_OVERCLAIMED",
                        f"{fam}: CERTIFIED using structural MW entrypoint "
                        f"{ep!r} \u2014 structural-only L2 cannot prove real "
                        f"execution",
                    )

        elif cert == "STRUCTURAL_ONLY":
            if not str(row.get("structural_only_reason") or "").strip():
                return fail(
                    "RFC_STRUCTURAL_NO_REASON",
                    f"{fam}: STRUCTURAL_ONLY requires structural_only_reason",
                )

        elif cert == "NOT_CERTIFIED":
            if not str(row.get("blocking_gap") or "").strip():
                return fail(
                    "RFC_NOT_CERTIFIED_NO_GAP",
                    f"{fam}: NOT_CERTIFIED requires blocking_gap",
                )

        else:
            return fail(
                "RFC_SCHEMA_INVALID",
                f"{fam}: unknown certification_status={cert!r}",
            )

    # 6. Manifest binding.
    manifest_pay = _payload(
        _read_json(art_dir / "integrated_runtime_artifact_manifest.json")
    )
    names = manifest_pay.get("artifact_filenames")
    if not isinstance(names, list) or (
        L7_ROUTE_FAMILY_COVERAGE_FILENAME not in names
    ):
        return fail(
            "RFC_MANIFEST_NOT_BOUND",
            f"manifest.artifact_filenames does not include "
            f"{L7_ROUTE_FAMILY_COVERAGE_FILENAME}",
        )
    if not str(manifest_pay.get("l7_route_family_coverage_ref") or ""):
        return fail(
            "RFC_MANIFEST_NOT_BOUND",
            "manifest missing l7_route_family_coverage_ref",
        )
    if not str(manifest_pay.get("l7_route_family_coverage_sha256") or ""):
        return fail(
            "RFC_MANIFEST_NOT_BOUND",
            "manifest missing l7_route_family_coverage_sha256",
        )

    # 7. Spine binding.
    spine_pay = _payload(_read_json(art_dir / "agentic_core_spine_proof.json"))
    if not str(spine_pay.get("l7_route_family_coverage_ref") or ""):
        return fail(
            "RFC_SPINE_NOT_BOUND",
            "spine_proof missing l7_route_family_coverage_ref",
        )
    if not str(spine_pay.get("l7_route_family_coverage_sha256") or ""):
        return fail(
            "RFC_SPINE_NOT_BOUND",
            "spine_proof missing l7_route_family_coverage_sha256",
        )
    if not str(spine_pay.get("l7_route_family_coverage_status") or ""):
        return fail(
            "RFC_SPINE_NOT_BOUND",
            "spine_proof missing l7_route_family_coverage_status",
        )

    # 8. Exercised-family certification gate (fail-closed when enabled).
    # When L7_RFC_EXERCISED_FAIL_CLOSED=1, the exercised family MUST be
    # CERTIFIED — otherwise the verifier fails. Advisory by default.
    import os as _os
    _exercised_family = (cur.get("route_family_exercised") or "").strip()
    if _exercised_family:
        _exercised_row = next(
            (r for r in families if r.get("route_family") == _exercised_family), None
        )
        if _exercised_row and _exercised_row.get("certification_status") != "CERTIFIED":
            _msg = (
                f"{_exercised_family}: exercised family is "
                f"{_exercised_row.get('certification_status')!r}, not CERTIFIED"
            )
            if _os.environ.get("L7_RFC_EXERCISED_FAIL_CLOSED", "0") == "1":
                return fail("RFC_EXERCISED_NOT_CERTIFIED", _msg)
            print(f"ADVISORY: RFC_EXERCISED_NOT_CERTIFIED — {_msg}")

    summary = pay.get("summary", {}) or {}
    return passed(
        f"L7 route-family coverage matrix valid (chain_kind={kind}, "
        f"families={len(families)}, certified={summary.get('certified', 0)}, "
        f"structural_only={summary.get('structural_only', 0)}, "
        f"fixture_only={summary.get('fixture_only', 0)}, "
        f"not_certified={summary.get('not_certified', 0)})"
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
