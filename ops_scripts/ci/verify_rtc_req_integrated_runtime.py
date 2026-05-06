"""Wave B verifier — RTC-REQ-010..015 (integrated runtime bundle).

Consumes the latest integrated runtime bundle at
``artifacts/certification/integrated_runtime/latest/`` and produces a
per-RTC-REQ verdict for the six reqs covered by Wave B:

  - RTC-REQ-010: integrated runtime entrypoint required (single
    production entry point; full artifact bundle producer-owned)
  - RTC-REQ-011: harness observes only; no harness-stamped artifact
  - RTC-REQ-012: ExitReviewPacket + exactly one X3 disposition
  - RTC-REQ-013: terminal cache route does not execute L2
  - RTC-REQ-014: every artifact has provenance fields
  - RTC-REQ-015: runtime-sensitive artifacts bind authority fields

Bundle contract (R1B short-circuit path):
  - validated_request.json
  - l1_plan_contract.json
  - route_contract.json
  - runtime_gate_verdict_bundle.json
  - terminal_ret_packet.json (R1B short-circuit case; SealedL2Artifact NA)
  - semantic_cache_safe_reuse_decision.json (FinalEvidenceContract for R1B)
  - exit_review_packet.json
  - x3_disposition_receipt.json
  - runtime_exhaust_bundle.json
  - no_harness_stamp_receipt.json
  - integrated_runtime_artifact_manifest.json
  - integrated_runtime_entrypoint_invocation.json

OTELSpanTree, ReplayReceipt, CompiledPromptArtifact, X1VerdictBundle are
covered in later waves (C for OTEL+replay; D for cache; B's claim is
short-circuit R1B).

Output: ``artifacts/certification/rtc_req_integrated_runtime_report.json``
Exit codes: 0 = all 6 reqs PASS; 2 = any req FAIL; 3 = harness error.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_DIR = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "latest"
REPORT_PATH = REPO_ROOT / "artifacts" / "certification" / "rtc_req_integrated_runtime_report.json"

EXPECTED_BUNDLE_FILES = (
    "validated_request.json",
    "l1_plan_contract.json",
    "route_contract.json",
    "runtime_gate_verdict_bundle.json",
    "terminal_ret_packet.json",
    "semantic_cache_safe_reuse_decision.json",
    "exit_review_packet.json",
    "x3_disposition_receipt.json",
    "runtime_exhaust_bundle.json",
    "no_harness_stamp_receipt.json",
    "integrated_runtime_artifact_manifest.json",
    "integrated_runtime_entrypoint_invocation.json",
)

PROVENANCE_FIELDS = (
    "producer_component",
    "producer_module",
    "producer_function_or_class",
    "emitted_at",
    "artifact_hash",
    "upstream_artifact_ref",
)

AUTHORITY_FIELDS = ("policy_hash", "blueprint_hash", "replay_key")

# Artifacts that MUST carry authority binding (runtime-sensitive)
RUNTIME_SENSITIVE_ARTIFACTS = (
    "route_contract.json",
    "terminal_ret_packet.json",
    "exit_review_packet.json",
)

# Production source path regex — producer_component must match this
PRODUCTION_PRODUCER_RE = re.compile(
    r"^agentic_core\.(runtime|L[0-6]_\w+)\."
)
HARNESS_PRODUCER_BAD_RE = re.compile(
    r"^(scripts\.proof|tests\.|harness\.)", re.IGNORECASE
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load(p: Path) -> dict | None:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _check_010(bundle: dict[str, dict]) -> tuple[bool, list[str]]:
    """RTC-REQ-010: single production runtime entrypoint, full bundle."""
    msgs: list[str] = []

    # All required bundle artifacts must exist
    missing = [n for n in EXPECTED_BUNDLE_FILES if n not in bundle]
    if missing:
        msgs.append(f"missing bundle artifacts: {missing}")

    # Manifest must declare integrated_runtime_entrypoint_used=True
    manifest = bundle.get("integrated_runtime_artifact_manifest.json", {})
    payload = manifest.get("payload") or {}
    if not payload.get("integrated_runtime_entrypoint_used"):
        msgs.append(
            "manifest payload.integrated_runtime_entrypoint_used != True"
        )

    # entry_point must point at production module
    ep = payload.get("entry_point", "")
    if not ep or "agentic_core.runtime.entrypoints" not in ep:
        msgs.append(f"entry_point not a production runtime entrypoint: {ep!r}")

    return (not msgs, msgs)


def _check_011(bundle: dict[str, dict]) -> tuple[bool, list[str]]:
    """RTC-REQ-011: no harness-stamped artifact."""
    msgs: list[str] = []
    for fname, doc in bundle.items():
        producer = doc.get("producer_component") or ""
        if HARNESS_PRODUCER_BAD_RE.match(producer):
            msgs.append(f"{fname}: harness-stamped producer={producer!r}")
            continue
        if not PRODUCTION_PRODUCER_RE.match(producer):
            msgs.append(
                f"{fname}: producer_component={producer!r} not under "
                f"production source"
            )

    # Cross-check: no_harness_stamp_receipt must self-attest
    nhsr = bundle.get("no_harness_stamp_receipt.json", {}).get("payload") or {}
    if not nhsr.get("all_artifacts_stamped_by_production"):
        msgs.append(
            "no_harness_stamp_receipt.payload.all_artifacts_stamped_by_production != True"
        )
    return (not msgs, msgs)


def _check_012(bundle: dict[str, dict]) -> tuple[bool, list[str]]:
    """RTC-REQ-012: ExitReviewPacket + exactly one X3 disposition."""
    msgs: list[str] = []
    erp = bundle.get("exit_review_packet.json")
    x3 = bundle.get("x3_disposition_receipt.json")
    if erp is None:
        msgs.append("exit_review_packet.json missing")
    if x3 is None:
        msgs.append("x3_disposition_receipt.json missing")
        return (False, msgs)

    x3_payload = x3.get("payload") or {}
    if "x3_disposition" not in x3_payload:
        msgs.append("x3_disposition_receipt.payload.x3_disposition missing")
    # verdict_count assertion — exactly one X3
    vc = x3_payload.get("verdict_count")
    if vc is not None and vc != 1:
        msgs.append(f"x3_disposition_receipt.payload.verdict_count={vc} (expected 1)")
    return (not msgs, msgs)


def _check_013(bundle: dict[str, dict]) -> tuple[bool, list[str]]:
    """RTC-REQ-013: R1A/R1B terminal short-circuit emits TerminalRetPacket
    and goes to Exit, NOT L2."""
    msgs: list[str] = []
    trp = bundle.get("terminal_ret_packet.json")
    if trp is None:
        msgs.append("terminal_ret_packet.json missing")
        return (False, msgs)

    trp_payload = trp.get("payload") or {}
    if trp_payload.get("execution_form") != "TERMINAL_SHORTCIRCUIT":
        msgs.append(
            f"terminal_ret_packet.payload.execution_form="
            f"{trp_payload.get('execution_form')!r} (expected TERMINAL_SHORTCIRCUIT)"
        )
    if not trp_payload.get("no_l2_execution_assertion"):
        msgs.append("terminal_ret_packet.payload.no_l2_execution_assertion not truthy")
    if not trp_payload.get("exit_review_required"):
        msgs.append("terminal_ret_packet.payload.exit_review_required not truthy")

    # No SealedL2Artifact in bundle
    if "sealed_l2_artifact.json" in bundle or "l2_sealed_artifact.json" in bundle:
        msgs.append("SealedL2Artifact present in R1B short-circuit bundle")

    return (not msgs, msgs)


def _check_014(bundle: dict[str, dict]) -> tuple[bool, list[str]]:
    """RTC-REQ-014: every artifact has full provenance envelope."""
    msgs: list[str] = []
    for fname, doc in bundle.items():
        for f in PROVENANCE_FIELDS:
            if f not in doc:
                msgs.append(f"{fname}: missing top-level field {f!r}")
                break
    return (not msgs, msgs)


def _check_015(bundle: dict[str, dict]) -> tuple[bool, list[str]]:
    """RTC-REQ-015: runtime-sensitive artifacts bind authority fields."""
    msgs: list[str] = []
    for fname in RUNTIME_SENSITIVE_ARTIFACTS:
        doc = bundle.get(fname)
        if doc is None:
            msgs.append(f"{fname}: required for authority check, missing")
            continue
        payload = doc.get("payload") or {}
        for f in AUTHORITY_FIELDS:
            if f not in payload:
                msgs.append(f"{fname}: payload.{f} missing")
    return (not msgs, msgs)


def main() -> int:
    if not BUNDLE_DIR.exists():
        print(f"[verify_rtc_req_integrated_runtime] BUNDLE_DIR missing: {BUNDLE_DIR}")
        return 3

    # Load bundle
    bundle: dict[str, dict] = {}
    for p in BUNDLE_DIR.glob("*.json"):
        d = _load(p)
        if isinstance(d, dict):
            bundle[p.name] = d

    checks = [
        ("RTC-REQ-010", _check_010, "Integrated runtime entrypoint required"),
        ("RTC-REQ-011", _check_011, "Harness observes only"),
        ("RTC-REQ-012", _check_012, "Exit + exactly one X3 disposition"),
        ("RTC-REQ-013", _check_013, "Terminal cache route does not execute L2"),
        ("RTC-REQ-014", _check_014, "Provenance fields on every artifact"),
        ("RTC-REQ-015", _check_015, "Authority binding on runtime artifacts"),
    ]

    per_req = {}
    overall_pass = True
    for rid, fn, title in checks:
        ok, msgs = fn(bundle)
        per_req[rid] = {
            "title": title,
            "result": "PASS" if ok else "FAIL",
            "violations": msgs,
        }
        if not ok:
            overall_pass = False

    report = {
        "verifier": "verify_rtc_req_integrated_runtime",
        "scope": "Wave B — RTC-REQ-010..015",
        "bundle_dir": str(BUNDLE_DIR.relative_to(REPO_ROOT)),
        "bundle_artifact_count": len(bundle),
        "evaluated_at_utc": _utc_now(),
        "overall_result": "PASS" if overall_pass else "FAIL",
        "per_req": per_req,
    }
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"[verify_rtc_req_integrated_runtime] overall={'PASS' if overall_pass else 'FAIL'}")
    print(f"  bundle: {BUNDLE_DIR.relative_to(REPO_ROOT)} ({len(bundle)} artifacts)")
    for rid, r in per_req.items():
        marker = "  PASS" if r["result"] == "PASS" else "  FAIL"
        print(f"{marker} {rid}: {r['title']}")
        for v in r["violations"]:
            print(f"      - {v}")
    print(f"  wrote: {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0 if overall_pass else 2


if __name__ == "__main__":
    sys.exit(main())
