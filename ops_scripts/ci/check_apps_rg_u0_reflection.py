#!/usr/bin/env python3
"""CI gate — apps_rg U0 reflection harness must remain on the live runtime path.

Per plan apps-rg-u0-reflection-live-wiring-105147 W5.

Runs the contract-first reflection harness over the canonical fixtures:
    - valid_ingress_contract.v1.json must produce a passing receipt
    - invalid_missing_jd_hash.json must raise MissingJdHashError
    - invalid_unknown_generation_mode.json must raise UnknownGenerationModeError
    - invalid_missing_policy_ref.json must raise MissingPolicyRefsError

Then exercises the LIVE runtime path (apps_rg_parse → u0_validate_apps_rg)
to prove the harness is wired in, not just available as a sidecar:
    - the produced ValidatedRequest must carry a populated app_payload
    - the reflection_receipt must be attached
    - audit_refs must include a reflection:<digest> entry
    - the receipt's pass_status must be True
    - both digests must be deterministic across two runs

Exit codes:
    0 — all assertions hold; harness is live and fixtures behave correctly
    1 — one or more assertions failed (CI must fail the build)

Constitutional:
    - subprocess-free, deterministic, ≤30s
    - utf-8 stdio, specific exception types only
    - SSOT folder per §31: ops_scripts/ci/check_*.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import traceback
from dataclasses import replace as _replace
from pathlib import Path
from typing import Any

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

# Imports happen after sys.path tweak so the script runs standalone.
from agentic_core.runtime.contracts.apps_rg_ingress_payload import (  # noqa: E402
    ValidatedRequest,
)
from apps_rg.runtime.dispatch import apps_rg_parse  # noqa: E402
from agentic_core.runtime.entry.u0_apps_rg_binding import u0_validate_apps_rg  # noqa: E402
from agentic_core.runtime.u0 import (  # noqa: E402
    AppsRgU0ReflectionReceipt,
    MissingJdHashError,
    MissingPolicyRefsError,
    UnknownGenerationModeError,
    apps_rg_u0_adapt,
)


FIXTURE_DIR: Path = REPO_ROOT / "tests" / "fixtures" / "apps_rg"


# ---------------------------------------------------------------------------
# Result accumulator
# ---------------------------------------------------------------------------


class CheckRecorder:
    """Collects assertion results into a list of (name, ok, detail) triples.

    A single failure does not abort — we report all failures together so CI
    output is informative.
    """

    def __init__(self) -> None:
        self._records: list[tuple[str, bool, str]] = []

    def assert_(self, name: str, condition: bool, detail: str = "") -> None:
        self._records.append((name, bool(condition), detail))

    def fail(self, name: str, detail: str) -> None:
        self._records.append((name, False, detail))

    @property
    def passed(self) -> bool:
        return all(ok for _, ok, _ in self._records)

    def render(self) -> str:
        lines: list[str] = []
        for name, ok, detail in self._records:
            mark = "OK" if ok else "FAIL"
            lines.append(f"[{mark}] {name}{(': ' + detail) if detail and not ok else ''}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_fixture(name: str) -> dict[str, Any]:
    path = FIXTURE_DIR / name
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _live_thin_payload() -> dict[str, Any]:
    """The shape ``apps_rg/__main__.py`` builds today."""

    return {
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "target_company": "Acme Corp",
        "target_role": "Senior Director of AI Engineering",
        "target_level": "EXECUTIVE",
        "source_resume_text": "Resume content sample",
        "job_description_text": "JD content sample",
    }


# ---------------------------------------------------------------------------
# Sidecar fixture coverage
# ---------------------------------------------------------------------------


def check_valid_fixture_passes(rec: CheckRecorder) -> None:
    raw = _load_fixture("valid_ingress_contract.v1.json")
    try:
        validated, receipt = apps_rg_u0_adapt(raw)
    except Exception as exc:  # guardian: allow-broad -- CI surface; surface and continue
        rec.fail("valid_fixture_passes", f"unexpected exception: {exc}")
        return

    rec.assert_(
        "valid_fixture_validated_request",
        isinstance(validated, ValidatedRequest),
        f"expected ValidatedRequest, got {type(validated).__name__}",
    )
    rec.assert_(
        "valid_fixture_receipt_emitted",
        isinstance(receipt, AppsRgU0ReflectionReceipt),
    )
    rec.assert_(
        "valid_fixture_zero_silently_dropped",
        receipt.silently_dropped == (),
        f"silently_dropped={receipt.silently_dropped}",
    )
    rec.assert_(
        "valid_fixture_zero_unknown_mappings",
        receipt.unknown_mappings == (),
        f"unknown_mappings={receipt.unknown_mappings}",
    )
    rec.assert_(
        "valid_fixture_pass_status_true",
        receipt.pass_status is True,
    )
    rec.assert_(
        "valid_fixture_input_digest_64hex",
        len(receipt.input_payload_digest) == 64
        and all(c in "0123456789abcdef" for c in receipt.input_payload_digest),
    )
    rec.assert_(
        "valid_fixture_validated_digest_64hex",
        len(receipt.validated_request_digest) == 64,
    )


def check_missing_jd_hash_fails(rec: CheckRecorder) -> None:
    raw = _load_fixture("invalid_missing_jd_hash.json")
    try:
        apps_rg_u0_adapt(raw)
        rec.fail(
            "missing_jd_hash_fails", "expected MissingJdHashError, got success"
        )
    except MissingJdHashError:
        rec.assert_("missing_jd_hash_fails", True)
    except Exception as exc:  # guardian: allow-broad -- CI surface
        rec.fail(
            "missing_jd_hash_fails", f"wrong exception: {type(exc).__name__}"
        )


def check_unknown_generation_mode_fails(rec: CheckRecorder) -> None:
    raw = _load_fixture("invalid_unknown_generation_mode.json")
    try:
        apps_rg_u0_adapt(raw)
        rec.fail(
            "unknown_generation_mode_fails",
            "expected UnknownGenerationModeError, got success",
        )
    except UnknownGenerationModeError:
        rec.assert_("unknown_generation_mode_fails", True)
    except Exception as exc:  # guardian: allow-broad -- CI surface
        rec.fail(
            "unknown_generation_mode_fails",
            f"wrong exception: {type(exc).__name__}",
        )


def check_missing_policy_ref_fails(rec: CheckRecorder) -> None:
    raw = _load_fixture("invalid_missing_policy_ref.json")
    try:
        apps_rg_u0_adapt(raw)
        rec.fail(
            "missing_policy_ref_fails",
            "expected MissingPolicyRefsError, got success",
        )
    except MissingPolicyRefsError:
        rec.assert_("missing_policy_ref_fails", True)
    except Exception as exc:  # guardian: allow-broad -- CI surface
        rec.fail(
            "missing_policy_ref_fails",
            f"wrong exception: {type(exc).__name__}",
        )


# ---------------------------------------------------------------------------
# Live-path coverage — proves the harness is on the runtime path, not sidecar
# ---------------------------------------------------------------------------


def check_live_path_runs_harness(rec: CheckRecorder) -> None:
    envelope = apps_rg_parse(_live_thin_payload())
    if envelope is None:
        rec.fail("live_path_envelope", "apps_rg_parse returned None for valid thin payload")
        return

    try:
        validated = u0_validate_apps_rg(envelope)
    except Exception as exc:  # guardian: allow-broad -- CI surface
        rec.fail("live_path_runs_harness", f"u0_validate_apps_rg raised: {exc}")
        return

    rec.assert_(
        "live_path_returns_validated_request",
        isinstance(validated, ValidatedRequest),
    )
    rec.assert_(
        "live_path_app_payload_populated",
        bool(validated.app_payload) and "transport" in validated.app_payload,
        f"app_payload keys: {sorted(validated.app_payload.keys()) if validated.app_payload else []}",
    )
    rec.assert_(
        "live_path_reflection_receipt_set",
        validated.reflection_receipt is not None
        and isinstance(validated.reflection_receipt, AppsRgU0ReflectionReceipt),
    )
    rec.assert_(
        "live_path_receipt_pass_status",
        bool(validated.reflection_receipt and validated.reflection_receipt.pass_status),
    )
    reflection_audit = [r for r in validated.audit_refs if r.startswith("reflection:")]
    rec.assert_(
        "live_path_audit_ref_threaded",
        len(reflection_audit) == 1,
        f"audit_refs={validated.audit_refs}",
    )


def check_live_path_digests_deterministic(rec: CheckRecorder) -> None:
    envelope = apps_rg_parse(_live_thin_payload())
    if envelope is None:
        rec.fail("live_path_determinism", "apps_rg_parse returned None")
        return

    pinned = {
        "request_id": "rg-req-ci-pin",
        "run_id": "rg-run-ci-pin",
        "trace_id": "rg-trace-ci-pin",
        "submitted_at": "2026-05-10T12:00:00+00:00",
        "tenant_id": "apps_rg",
    }
    e1 = _replace(envelope, **pinned)
    e2 = _replace(envelope, **pinned)

    try:
        vr1 = u0_validate_apps_rg(e1)
        vr2 = u0_validate_apps_rg(e2)
    except Exception as exc:  # guardian: allow-broad -- CI surface
        rec.fail("live_path_determinism", f"u0_validate_apps_rg raised: {exc}")
        return

    rec.assert_(
        "live_path_input_digest_deterministic",
        vr1.reflection_receipt.input_payload_digest
        == vr2.reflection_receipt.input_payload_digest,
    )
    rec.assert_(
        "live_path_validated_digest_deterministic",
        vr1.reflection_receipt.validated_request_digest
        == vr2.reflection_receipt.validated_request_digest,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    rec = CheckRecorder()
    try:
        check_valid_fixture_passes(rec)
        check_missing_jd_hash_fails(rec)
        check_unknown_generation_mode_fails(rec)
        check_missing_policy_ref_fails(rec)
        check_live_path_runs_harness(rec)
        check_live_path_digests_deterministic(rec)
    except Exception as exc:  # guardian: allow-broad -- top-level CI safety net
        traceback.print_exc()
        print(f"FATAL: harness check raised unexpectedly: {exc}", file=sys.stderr)
        return 1

    print(rec.render())
    if rec.passed:
        print()
        print("apps_rg U0 reflection harness: LIVE on runtime path, all checks passed.")
        return 0
    print()
    print(
        "apps_rg U0 reflection harness FAILED — the harness must remain on the "
        "live apps_rg runtime path (plan apps-rg-u0-reflection-live-wiring-105147).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
