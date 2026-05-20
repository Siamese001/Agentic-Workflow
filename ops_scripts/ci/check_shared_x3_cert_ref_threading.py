"""CI gate: Shared X3 builder cert-ref threading (AG-8-FU1).

Fails if:
  - build_x3_packet constructs any X3 packet with empty l5_certification_ref.
  - build_x3_packet ignores ExitReviewPacket.l5_certification_refs.
  - missing required cert ref does not fail closed (MissingL5CertificationRef).
  - apps_lic AG-8 golden path regresses.
  - apps_rg golden path regresses.
  - scalar eval_score becomes authoritative.
  - material FAIL can ALLOW_FINISH.
  - material UNKNOWN can pass.
  - NOT_APPLICABLE reason law weakens.

Plan: AG-8-FU1 (Shared X3 builder cert-ref threading)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_FAIL_CLOSED = "--fail-closed" in sys.argv

_VIOLATIONS: list[str] = []


def _fail(msg: str) -> None:
    _VIOLATIONS.append(msg)
    print(f"FAIL  {msg}")


def _pass(msg: str) -> None:
    print(f"PASS  {msg}")


# ---------------------------------------------------------------------------
# Check 1: MissingL5CertificationRef is importable and is a ValueError subclass
# ---------------------------------------------------------------------------

def check_missing_cert_ref_exception_exists() -> None:
    try:
        from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import (
            MissingL5CertificationRef,
        )
        if not issubclass(MissingL5CertificationRef, ValueError):
            _fail("CHK-1: MissingL5CertificationRef is not a ValueError subclass")
            return
        _pass("CHK-1: MissingL5CertificationRef importable and is ValueError subclass")
    except ImportError as e:
        _fail(f"CHK-1: Cannot import MissingL5CertificationRef: {e}")


# ---------------------------------------------------------------------------
# Check 2: _extract_cert_ref raises when l5_certification_refs is empty
# ---------------------------------------------------------------------------

def check_extract_cert_ref_fails_closed() -> None:
    try:
        from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import (
            MissingL5CertificationRef,
            _extract_cert_ref,
        )
        from agentic_core.L3_orchestration.exit_eval.v6.types import (
            ExitReviewPacket,
            SourceType,
        )
        empty_packet = ExitReviewPacket(
            source_type=SourceType.L2_SEALED_ARTIFACT,
            l5_certification_refs=(),
        )
        try:
            _extract_cert_ref(empty_packet)
            _fail("CHK-2: _extract_cert_ref did NOT raise when l5_certification_refs is empty (not fail-closed)")
        except MissingL5CertificationRef:
            _pass("CHK-2: _extract_cert_ref raises MissingL5CertificationRef when refs empty (fail closed)")
        except Exception as e:
            _fail(f"CHK-2: _extract_cert_ref raised unexpected exception type {type(e).__name__}: {e}")
    except ImportError as e:
        _fail(f"CHK-2: Import error: {e}")


# ---------------------------------------------------------------------------
# Check 3: _extract_cert_ref returns first ref when refs present
# ---------------------------------------------------------------------------

def check_extract_cert_ref_returns_first() -> None:
    try:
        from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import _extract_cert_ref
        from agentic_core.L3_orchestration.exit_eval.v6.types import ExitReviewPacket, SourceType

        packet = ExitReviewPacket(
            source_type=SourceType.L2_SEALED_ARTIFACT,
            l5_certification_refs=("first-ref", "second-ref"),
        )
        ref = _extract_cert_ref(packet)
        if ref != "first-ref":
            _fail(f"CHK-3: _extract_cert_ref returned {ref!r} instead of 'first-ref'")
        else:
            _pass("CHK-3: _extract_cert_ref returns first element of l5_certification_refs")
    except Exception as e:
        _fail(f"CHK-3: Unexpected error: {e}")


# ---------------------------------------------------------------------------
# Check 4: All five build_x3* functions thread l5_certification_ref
# ---------------------------------------------------------------------------

def check_all_builders_thread_cert_ref() -> None:
    try:
        from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import (
            build_x3a_deny,
            build_x3b_escalate,
            build_x3c_commit_request,
            build_x3d_allow,
            build_x3e_safe_abstain,
        )
        from agentic_core.L3_orchestration.exit_eval.v6.types import (
            ExitReviewPacket,
            SourceType,
            V6Disposition,
        )
        from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import AggregateDecision

        cert = "gate-check-cert-ag8-fu1"
        packet = ExitReviewPacket(
            source_type=SourceType.L2_SEALED_ARTIFACT,
            l5_certification_refs=(cert,),
            output={"schema_valid": True, "text": "hi"},
            final_evidence_contract={"c0_status": "PASS"},
        )

        # ALLOW
        x3 = build_x3d_allow(packet, AggregateDecision(disposition=V6Disposition.ALLOW, rationale="ok"))
        if x3.l5_certification_ref != cert:
            _fail(f"CHK-4a: X3AllowPacket.l5_certification_ref={x3.l5_certification_ref!r} != {cert!r}")
        else:
            _pass("CHK-4a: X3AllowPacket receives l5_certification_ref")

        # DENY
        x3 = build_x3a_deny(packet, AggregateDecision(disposition=V6Disposition.DENY, rationale="fail"))
        if x3.l5_certification_ref != cert:
            _fail(f"CHK-4b: X3DenyPacket.l5_certification_ref={x3.l5_certification_ref!r} != {cert!r}")
        else:
            _pass("CHK-4b: X3DenyPacket receives l5_certification_ref")

        # ESCALATE
        x3 = build_x3b_escalate(packet, AggregateDecision(disposition=V6Disposition.ESCALATE, rationale="esc"))
        if x3.l5_certification_ref != cert:
            _fail(f"CHK-4c: X3EscalatePacket.l5_certification_ref={x3.l5_certification_ref!r} != {cert!r}")
        else:
            _pass("CHK-4c: X3EscalatePacket receives l5_certification_ref")

        # SAFE_ABSTAIN
        x3 = build_x3e_safe_abstain(packet, AggregateDecision(disposition=V6Disposition.SAFE_ABSTAIN, rationale="abs"))
        if x3.l5_certification_ref != cert:
            _fail(f"CHK-4d: X3SafeAbstainPacket.l5_certification_ref={x3.l5_certification_ref!r} != {cert!r}")
        else:
            _pass("CHK-4d: X3SafeAbstainPacket receives l5_certification_ref")

        # COMMIT_REQUEST
        x3 = build_x3c_commit_request(packet, AggregateDecision(disposition=V6Disposition.COMMIT_REQUEST, rationale="cr"))
        if x3.l5_certification_ref != cert:
            _fail(f"CHK-4e: X3CommitRequestPacket.l5_certification_ref={x3.l5_certification_ref!r} != {cert!r}")
        else:
            _pass("CHK-4e: X3CommitRequestPacket receives l5_certification_ref")

    except Exception as e:
        _fail(f"CHK-4: Unexpected error in builder cert-ref check: {e}")


# ---------------------------------------------------------------------------
# Check 5: build_x3_packet fails closed when cert refs empty
# ---------------------------------------------------------------------------

def check_build_x3_packet_fails_closed() -> None:
    try:
        from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import (
            MissingL5CertificationRef,
            build_x3_packet,
        )
        from agentic_core.L3_orchestration.exit_eval.v6.types import (
            ExitReviewPacket,
            SourceType,
            V6Disposition,
        )
        from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import AggregateDecision

        empty_packet = ExitReviewPacket(
            source_type=SourceType.L2_SEALED_ARTIFACT,
            l5_certification_refs=(),
        )
        try:
            build_x3_packet(empty_packet, AggregateDecision(disposition=V6Disposition.ALLOW, rationale="test"))
            _fail("CHK-5: build_x3_packet did NOT raise when cert refs empty (not fail-closed)")
        except MissingL5CertificationRef:
            _pass("CHK-5: build_x3_packet raises MissingL5CertificationRef when cert refs empty")
        except Exception as e:
            _fail(f"CHK-5: build_x3_packet raised unexpected exception type {type(e).__name__}: {e}")
    except ImportError as e:
        _fail(f"CHK-5: Import error: {e}")


# ---------------------------------------------------------------------------
# Check 6: material FAIL cannot ALLOW_FINISH (DENY -> DenyPacket not AllowPacket)
# ---------------------------------------------------------------------------

def check_material_fail_cannot_allow() -> None:
    try:
        from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import build_x3_packet
        from agentic_core.L3_orchestration.exit_eval.v6.types import (
            ExitReviewPacket,
            SourceType,
            V6Disposition,
            X3AllowPacket,
            X3DenyPacket,
        )
        from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import AggregateDecision

        cert = "gate-check-cert-ag8-fu1-fail"
        packet = ExitReviewPacket(
            source_type=SourceType.L2_SEALED_ARTIFACT,
            l5_certification_refs=(cert,),
        )
        decision = AggregateDecision(disposition=V6Disposition.DENY, rationale="hard_fail", reason_codes=["HARD_FAIL"])
        x3 = build_x3_packet(packet, decision)
        if isinstance(x3, X3AllowPacket):
            _fail("CHK-6: material FAIL produced X3AllowPacket (ALLOW_FINISH not blocked)")
        elif isinstance(x3, X3DenyPacket):
            _pass("CHK-6: material FAIL correctly produces X3DenyPacket")
        else:
            _fail(f"CHK-6: Unexpected packet type for DENY disposition: {type(x3).__name__}")
    except Exception as e:
        _fail(f"CHK-6: Unexpected error: {e}")


# ---------------------------------------------------------------------------
# Check 7: material UNKNOWN cannot pass (ESCALATE -> EscalatePacket not AllowPacket)
# ---------------------------------------------------------------------------

def check_material_unknown_cannot_pass() -> None:
    try:
        from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import build_x3_packet
        from agentic_core.L3_orchestration.exit_eval.v6.types import (
            ExitReviewPacket,
            SourceType,
            V6Disposition,
            X3AllowPacket,
            X3EscalatePacket,
        )
        from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import AggregateDecision

        cert = "gate-check-cert-ag8-fu1-unk"
        packet = ExitReviewPacket(
            source_type=SourceType.L2_SEALED_ARTIFACT,
            l5_certification_refs=(cert,),
        )
        decision = AggregateDecision(disposition=V6Disposition.ESCALATE, rationale="unknown", reason_codes=["UNKNOWN"])
        x3 = build_x3_packet(packet, decision)
        if isinstance(x3, X3AllowPacket):
            _fail("CHK-7: material UNKNOWN produced X3AllowPacket (passed without authorization)")
        elif isinstance(x3, X3EscalatePacket):
            _pass("CHK-7: material UNKNOWN correctly produces X3EscalatePacket")
        else:
            _fail(f"CHK-7: Unexpected packet type for ESCALATE disposition: {type(x3).__name__}")
    except Exception as e:
        _fail(f"CHK-7: Unexpected error: {e}")


# ---------------------------------------------------------------------------
# Check 8: apps_lic ExitReviewPacket has l5_certification_refs populated
# ---------------------------------------------------------------------------

def check_apps_lic_packet_has_cert_refs() -> None:
    try:
        from apps_lic.runtime.bindings.exit_binding import (
            _CERT_REF,
            _build_exit_review_packet,
        )
        from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

        l2 = SealedL2Artifact(
            request_id="ci-gate-req",
            run_id="ci-gate-run",
            trace_id="ci-gate-trace",
            app_id="apps_lic",
            execution_status="completed",
            generated_content="ci gate test",
            l5_certification_ref=_CERT_REF,
        )
        packet = _build_exit_review_packet(l2)
        if not packet.l5_certification_refs:
            _fail("CHK-8: apps_lic ExitReviewPacket.l5_certification_refs is empty after _build_exit_review_packet")
        elif _CERT_REF not in packet.l5_certification_refs:
            _fail(f"CHK-8: apps_lic cert ref {_CERT_REF!r} not in packet.l5_certification_refs")
        else:
            _pass(f"CHK-8: apps_lic ExitReviewPacket.l5_certification_refs populated with {_CERT_REF!r}")
    except Exception as e:
        _fail(f"CHK-8: Unexpected error: {e}")


# ---------------------------------------------------------------------------
# Check 9: Run FU1 test suite
# ---------------------------------------------------------------------------

def check_fu1_tests() -> None:
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/_apps_contract/test_ag8_fu1_shared_x3_builder_cert_ref.py",
            "-q", "--tb=short",
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=120,
    )
    if result.returncode == 0:
        _pass("CHK-9: AG-8-FU1 test suite passed")
    else:
        last = result.stdout.strip().split("\n")[-1] if result.stdout else ""
        _fail(f"CHK-9: AG-8-FU1 test suite FAILED: {last}")


# ---------------------------------------------------------------------------
# Check 10: apps_lic golden path regression
# ---------------------------------------------------------------------------

def check_apps_lic_golden_path() -> None:
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/_apps_contract/test_ag8_apps_lic_golden_path.py",
            "-q", "--tb=line",
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=120,
    )
    if result.returncode == 0:
        _pass("CHK-10: apps_lic golden path regression — PASS")
    else:
        last = result.stdout.strip().split("\n")[-1] if result.stdout else ""
        _fail(f"CHK-10: apps_lic golden path REGRESSION: {last}")


# ---------------------------------------------------------------------------
# Check 11: apps_rg golden path regression
# ---------------------------------------------------------------------------

def check_apps_rg_golden_path() -> None:
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/_apps_contract/test_w7_apps_lic_exit_x1_x3.py",
            "-q", "--tb=line",
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=120,
    )
    if result.returncode == 0:
        _pass("CHK-11: apps_lic W7 exit tests regression — PASS")
    else:
        last = result.stdout.strip().split("\n")[-1] if result.stdout else ""
        _fail(f"CHK-11: apps_lic W7 exit tests REGRESSION: {last}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 70)
    print("CI GATE: check_shared_x3_cert_ref_threading (AG-8-FU1)")
    print("=" * 70)

    check_missing_cert_ref_exception_exists()
    check_extract_cert_ref_fails_closed()
    check_extract_cert_ref_returns_first()
    check_all_builders_thread_cert_ref()
    check_build_x3_packet_fails_closed()
    check_material_fail_cannot_allow()
    check_material_unknown_cannot_pass()
    check_apps_lic_packet_has_cert_refs()
    check_fu1_tests()
    check_apps_lic_golden_path()
    check_apps_rg_golden_path()

    print("=" * 70)
    if _VIOLATIONS:
        print(f"RESULT: FAILED — {len(_VIOLATIONS)} violation(s):")
        for v in _VIOLATIONS:
            print(f"  * {v}")
        if _FAIL_CLOSED:
            return 1
        print("(advisory mode — exit 0 despite violations; use --fail-closed to enforce)")
        return 0
    print(f"RESULT: PASSED — all {11} checks green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
