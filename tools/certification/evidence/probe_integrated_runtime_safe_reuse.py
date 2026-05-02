"""RTC-REQ-056 integrated-runtime safe-reuse probe.

Invokes ConsensusVeto with the real juror_call_impl for the three-model
panel. On a 3/3 SAFE outcome, writes the canonical panel attestation to:

    artifacts/certification/integrated_runtime/consensus_jury/
        live_provider_attestation.json

On any juror failure, writes NO attestation and emits a structured
failure report instead:

    artifacts/certification/integrated_runtime/consensus_jury/
        integrated_runtime_probe_failure.json

Per operator directive 2026-05-01 13:39 UTC-04:00.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.certification.evidence._panel_attestation import (
    build_panel_attestation,
    panel_attestation_path,
    write_panel_attestation,
)
from tools.certification.safety.consensus_juror_clients import (
    DEFAULT_RUBRIC_PATH,
    make_real_juror_call_impl,
)
from tools.certification.safety.consensus_veto import (
    ConsensusVeto,
    JurorVerdict,
)
from tools.certification.safety.rtc_req_056_gate import (
    validate_panel_attestation,
)
from tools.certification.safety.rtc_req_056_panel import (
    CERTIFICATION_SCOPE,
    REQUIRED_JUROR_COUNT,
    RejectReason,
)
from tools.certification.safety.veto_protocol import VetoStatus

FAILURE_REPORT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "certification"
    / "integrated_runtime"
    / "consensus_jury"
    / "integrated_runtime_probe_failure.json"
)

# Canonical semantic-cache candidate pair used for the integrated run.
# Intentionally uses a paraphrase with same intent and safe-to-reuse
# public-knowledge answer.
CANDIDATE_QUERY = "What is the capital of France?"
CANDIDATE_CACHED_QUERY = "What city is the capital of France?"
CANDIDATE_CACHED_ANSWER = (
    "Paris is the capital city of France. It is located in north-"
    "central France on the Seine River."
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_integrated_runtime_probe() -> dict[str, Any]:
    """Run the RTC-REQ-056 certification probe.

    Returns a structured run report. Only writes the panel attestation
    when the full consensus panel returns SAFE.
    """
    impl = make_real_juror_call_impl(rubric_path=DEFAULT_RUBRIC_PATH)
    veto = ConsensusVeto(
        juror_call_impl=impl,
        rubric_path=DEFAULT_RUBRIC_PATH,
    )

    # Fail early if keys missing — emit INFRASTRUCTURE_GAP
    if not veto.is_available():
        failure = {
            "schema_version": 2,
            "certification_scope": CERTIFICATION_SCOPE,
            "status": "INFRASTRUCTURE_GAP",
            "reason_code": RejectReason.INFRASTRUCTURE_GAP_MISSING_KEY,
            "message": (
                "One or more required juror API keys missing. "
                "Run probe_live_provider_readiness.py to inspect."
            ),
            "panel_attestation_written": False,
            "executed_at_utc": _utc_now_iso(),
        }
        FAILURE_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        FAILURE_REPORT_PATH.write_text(
            json.dumps(failure, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return failure

    result = veto.evaluate(
        CANDIDATE_QUERY, CANDIDATE_CACHED_QUERY, CANDIDATE_CACHED_ANSWER
    )
    per_juror_dicts = result.metadata.get("per_juror", [])
    jurors = [
        JurorVerdict(
            juror_id=d["juror_id"],
            family=d["family"],
            model_id=d["model_id"],
            verdict=d["verdict"],
            confidence=d.get("confidence", 0.0),
            rationale=d.get("rationale", ""),
            latency_ms=d.get("latency_ms", 0.0),
            raw_response_sha256=d.get("raw_response_sha256", ""),
        )
        for d in per_juror_dicts
    ]

    panel_allow = (
        result.status == VetoStatus.SAFE
        and result.metadata.get("consensus_mode") == "unanimous"
        and len(jurors) == REQUIRED_JUROR_COUNT
    )
    final_verdict = "SAFE" if panel_allow else "NOT_SAFE"
    final_x3 = "X3D" if panel_allow else "X3_DENIED_FAIL_CLOSED"

    attestation = build_panel_attestation(
        jurors=jurors,
        final_consensus_verdict=final_verdict,
        final_safe_reuse_allow=panel_allow,
        final_x3_disposition=final_x3,
        rubric_path=DEFAULT_RUBRIC_PATH,
        request_text=CANDIDATE_QUERY,
        cache_candidate_text=CANDIDATE_CACHED_QUERY,
        invocation_count=len(jurors),
    )
    gate_result = validate_panel_attestation(attestation)

    report: dict[str, Any] = {
        "schema_version": 2,
        "certification_scope": CERTIFICATION_SCOPE,
        "status": gate_result.row_status,
        "gate_accepted": gate_result.accepted,
        "reason_codes": list(gate_result.reason_codes),
        "messages": list(gate_result.messages),
        "final_consensus_verdict": final_verdict,
        "final_safe_reuse_allow": panel_allow,
        "final_x3_disposition": final_x3,
        "consensus_mode": result.metadata.get("consensus_mode"),
        "executed_at_utc": _utc_now_iso(),
    }

    # Only write the canonical panel attestation when the gate accepts.
    # Otherwise, write a failure report and emit no attestation.
    out_dir = panel_attestation_path(REPO_ROOT).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    if gate_result.accepted:
        written = write_panel_attestation(out_dir, attestation)
        report["panel_attestation_written"] = True
        report["panel_attestation_path"] = str(written.relative_to(REPO_ROOT))
        # Clear stale failure report from prior runs
        if FAILURE_REPORT_PATH.exists():
            FAILURE_REPORT_PATH.unlink()
    else:
        report["panel_attestation_written"] = False
        FAILURE_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        FAILURE_REPORT_PATH.write_text(
            json.dumps(
                {
                    **report,
                    "attestation_preview": attestation,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        # Also remove any stale accepted attestation so a downstream
        # verifier never sees a lingering ACCEPTED file after a failure.
        canonical = panel_attestation_path(REPO_ROOT)
        if canonical.exists():
            canonical.unlink()

    return report


def main() -> int:
    report = run_integrated_runtime_probe()
    print(
        f"[integrated] scope={report.get('certification_scope')} "
        f"status={report.get('status')} "
        f"accepted={report.get('gate_accepted')}"
    )
    for code in report.get("reason_codes", []):
        print(f"[integrated]   reject={code}")
    if report.get("panel_attestation_written"):
        print(f"[integrated] panel_attestation={report['panel_attestation_path']}")
    else:
        print(
            f"[integrated] no panel attestation written; "
            f"failure_report={FAILURE_REPORT_PATH.relative_to(REPO_ROOT)}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
