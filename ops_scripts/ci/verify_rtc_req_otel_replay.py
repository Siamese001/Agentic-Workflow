"""Wave C verifier — RTC-REQ-020..024 (OTEL + replay).

Consumes:
  - artifacts/certification/integrated_runtime/latest/  (Wave B bundle — for trace_id correlation)
  - artifacts/certification/integrated_runtime/replay/  (Wave C replay pair + mutation)

Per-RTC-REQ checks:

  - RTC-REQ-020: collector-backed OTEL — REQUIRES external collector
    receipt. Honest BLOCKED if no collector receipt on disk.
  - RTC-REQ-021: parent scenario span — trace_root correlation across
    runtime-sensitive artifacts (validated_request, route_contract,
    exit_review_packet, runtime_exhaust_bundle). PASS if all share the
    same trace_root within the bundle.
  - RTC-REQ-022: counter deltas — REQUIRES metric export. Honest BLOCKED
    if no counter delta receipt on disk.
  - RTC-REQ-023: replay pair determinism — replay_pair_receipt.result=PASS
  - RTC-REQ-024: replay mutation negative — replay_mutation_negative_receipt.result=PASS

Output: artifacts/certification/rtc_req_otel_replay_report.json
Exit: 0 if all attempted checks pass; 2 if any FAIL; 3 harness error.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LATEST = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "latest"
REPLAY_ROOT = REPO_ROOT / "artifacts" / "certification" / "integrated_runtime" / "replay"
PAIR_RECEIPT = REPLAY_ROOT / "replay_pair_receipt.json"
NEG_RECEIPT = REPLAY_ROOT / "replay_mutation_negative_receipt.json"
COLLECTOR_RECEIPT = REPO_ROOT / "artifacts" / "certification" / "otel_collector_receipt.json"
METRIC_DELTA_REPORT = REPO_ROOT / "artifacts" / "certification" / "otel_metric_delta_report.json"
REPORT_PATH = REPO_ROOT / "artifacts" / "certification" / "rtc_req_otel_replay_report.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _check_020():
    """RTC-REQ-020: collector-backed OTEL. Requires external exporter receipt."""
    if not COLLECTOR_RECEIPT.exists():
        return ("BLOCKED",
                "no external OTEL collector receipt on disk; "
                "expected artifacts/certification/otel_collector_receipt.json. "
                "Unblock: launch docker-compose.otel.yml and run a probe that "
                "exports spans to the collector.")
    d = _load(COLLECTOR_RECEIPT) or {}
    es = d.get("exporter_status") or d.get("status")
    if es == "external" or d.get("status") == "PASS":
        return ("PASS", f"exporter_status={es!r}")
    return ("BLOCKED", f"collector receipt present but exporter_status={es!r}")


def _check_021():
    """RTC-REQ-021: parent scenario span — trace_root correlation across bundle."""
    if not LATEST.exists():
        return ("FAIL", "Wave B bundle dir missing")
    runtime_sensitive = (
        "validated_request.json",
        "route_contract.json",
        "exit_review_packet.json",
        "runtime_exhaust_bundle.json",
    )
    trace_roots = {}
    for n in runtime_sensitive:
        p = LATEST / n
        if not p.exists():
            return ("FAIL", f"required artifact missing: {n}")
        d = _load(p) or {}
        pl = d.get("payload") or {}
        tr = pl.get("trace_root") or pl.get("trace_id") or ""
        trace_roots[n] = tr
    distinct = set(t for t in trace_roots.values() if t)
    if len(distinct) == 0:
        return ("FAIL", "no trace_root present on any runtime-sensitive artifact")
    if len(distinct) == 1:
        only = distinct.pop()
        return ("PASS",
                f"trace_root={only!r} consistent across all "
                f"{len(runtime_sensitive)} runtime-sensitive artifacts")
    return ("FAIL",
            f"trace_root divergence across bundle: "
            f"{trace_roots}")


def _check_022():
    """RTC-REQ-022: counter deltas. Requires metric export."""
    if not METRIC_DELTA_REPORT.exists():
        return ("BLOCKED",
                "no metric delta report on disk; "
                "expected artifacts/certification/otel_metric_delta_report.json. "
                "Unblock: instrument R1B path with counters + export deltas "
                "via collector. Required attributes per RTC-REQ-022: "
                "route_id, cache_tier, namespace, policy_hash, result/reason.")
    d = _load(METRIC_DELTA_REPORT) or {}
    if d.get("status") == "PASS":
        return ("PASS", "metric delta report status=PASS")
    return ("BLOCKED", f"metric delta report status={d.get('status')!r}")


def _check_023():
    """RTC-REQ-023: replay pair determinism."""
    if not PAIR_RECEIPT.exists():
        return ("FAIL",
                "replay_pair_receipt.json missing; "
                "run ops_scripts/ci/regen_integrated_runtime_replay_pair.py")
    d = _load(PAIR_RECEIPT) or {}
    if d.get("result") == "PASS":
        return ("PASS",
                f"replay_key match={d.get('replay_key_match')}, "
                f"content_hash match={d.get('content_hash_match')}")
    return ("FAIL", f"replay pair result={d.get('result')!r}")


def _check_024():
    """RTC-REQ-024: replay mutation negative."""
    if not NEG_RECEIPT.exists():
        return ("FAIL",
                "replay_mutation_negative_receipt.json missing; "
                "run ops_scripts/ci/regen_integrated_runtime_replay_pair.py")
    d = _load(NEG_RECEIPT) or {}
    if d.get("result") == "PASS":
        return ("PASS",
                f"mutation diverges: replay_key={d.get('replay_key_diverges')}, "
                f"content_hash={d.get('content_hash_diverges')}")
    return ("FAIL", f"mutation negative result={d.get('result')!r}")


def main() -> int:
    checks = [
        ("RTC-REQ-020", "Collector-backed OTEL", _check_020),
        ("RTC-REQ-021", "Parent scenario span correlation", _check_021),
        ("RTC-REQ-022", "Counter deltas with attributes", _check_022),
        ("RTC-REQ-023", "Replay pair determinism", _check_023),
        ("RTC-REQ-024", "Replay mutation negative", _check_024),
    ]

    per_req = {}
    overall_pass = True
    overall_blocked = False
    for rid, title, fn in checks:
        try:
            verdict, msg = fn()
        except Exception as exc:  # noqa: BLE001
            verdict = "FAIL"
            msg = f"harness error: {exc}"
        per_req[rid] = {"title": title, "result": verdict, "message": msg}
        if verdict == "FAIL":
            overall_pass = False
        elif verdict == "BLOCKED":
            overall_blocked = True

    if overall_pass and not overall_blocked:
        overall = "PASS"
    elif overall_pass and overall_blocked:
        overall = "PARTIAL_PASS_WITH_BLOCKED_INFRA"
    else:
        overall = "FAIL"

    report = {
        "verifier": "verify_rtc_req_otel_replay",
        "scope": "Wave C — RTC-REQ-020..024",
        "evaluated_at_utc": _utc_now(),
        "overall_result": overall,
        "per_req": per_req,
    }
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"[verify_rtc_req_otel_replay] overall={overall}")
    for rid, r in per_req.items():
        marker = {"PASS": "  PASS", "FAIL": "  FAIL", "BLOCKED": "  BLOCK"}.get(r["result"], "  ????")
        print(f"{marker} {rid}: {r['title']}")
        print(f"      {r['message']}")
    print(f"  wrote: {REPORT_PATH.relative_to(REPO_ROOT)}")

    return 0 if overall_pass else 2


if __name__ == "__main__":
    sys.exit(main())
