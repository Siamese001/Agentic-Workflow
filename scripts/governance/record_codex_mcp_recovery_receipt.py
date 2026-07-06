"""Record Codex MCP transport recovery evidence without performing recovery.

This helper is receipt-only. It does not launch MCP servers, reconnect Codex,
kill duplicate processes, or call Codex MCP tools directly. Operators use it
after a manual host/TUI reconnect or Codex restart to compare a saved before
diagnosis with a fresh after diagnosis.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GOVERNANCE_DIR = ROOT / "scripts" / "governance"
if str(GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_DIR))

import diagnose_codex_mcp_transport  # noqa: E402


SCHEMA_VERSION = "codex-mcp-recovery-receipt/v1"
RECEIPT_DIR = ROOT / "artifacts" / "mcp" / "recovery_receipts"
FRESH_PROOF_STATUS = "healthy"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _epoch(diagnosis: dict[str, Any]) -> dict[str, Any]:
    evidence = diagnosis.get("evidence")
    if not isinstance(evidence, dict):
        return {}
    epoch = evidence.get("callability_epoch")
    return epoch if isinstance(epoch, dict) else {}


def _proof_statuses(diagnosis: dict[str, Any]) -> list[str]:
    statuses: list[str] = []
    epoch = _epoch(diagnosis)
    if epoch.get("status"):
        statuses.append(str(epoch["status"]))

    evidence = diagnosis.get("evidence")
    evidence = evidence if isinstance(evidence, dict) else {}
    route_state = evidence.get("route_state")
    if isinstance(route_state, dict):
        route_proof = route_state.get("callability_proof")
        if isinstance(route_proof, dict) and route_proof.get("status"):
            statuses.append(str(route_proof["status"]))

    adg_status = evidence.get("adg_transport_status")
    if isinstance(adg_status, dict):
        callable_proof = adg_status.get("callable_proof")
        if isinstance(callable_proof, dict) and callable_proof.get("status"):
            statuses.append(str(callable_proof["status"]))
        file_proof = callable_proof.get("file_proof") if isinstance(callable_proof, dict) else None
        if isinstance(file_proof, dict) and file_proof.get("status"):
            statuses.append(str(file_proof["status"]))

    return statuses or ["absent"]


def _primary_proof_status(diagnosis: dict[str, Any]) -> str:
    statuses = _proof_statuses(diagnosis)
    if FRESH_PROOF_STATUS in statuses:
        return FRESH_PROOF_STATUS
    return statuses[0]


def _has_fresh_active_tool_proof(diagnosis: dict[str, Any]) -> bool:
    return (
        str(diagnosis.get("classification") or "") in {"callable", "codex_http_route_callable"}
        and FRESH_PROOF_STATUS in _proof_statuses(diagnosis)
    )


def _validation(after_diagnosis: dict[str, Any], unsafe_process_kill_used: bool) -> dict[str, str]:
    after_classification = str(after_diagnosis.get("classification") or "unknown")
    if unsafe_process_kill_used:
        return {
            "status": "FAIL",
            "reason": "unsafe_process_kill_used",
            "detail": "Unsafe process termination cannot be recorded as a successful Codex MCP recovery.",
        }
    if after_classification in {"process_only_callability_unproven", "duplicate_cohort"}:
        return {
            "status": "FAIL",
            "reason": "process_only_proof_rejected",
            "detail": "Process presence or duplicate-cohort state is not active Codex MCP callability proof.",
        }
    if not _has_fresh_active_tool_proof(after_diagnosis):
        return {
            "status": "FAIL",
            "reason": "active_tool_proof_missing",
            "detail": "After-state lacks fresh active-session callability proof.",
        }
    return {
        "status": "PASS",
        "reason": "fresh_active_tool_proof_present",
        "detail": "After-state has fresh active-session MCP callability proof.",
    }


def build_recovery_receipt(
    *,
    server_id: str,
    before_diagnosis: dict[str, Any],
    after_diagnosis: dict[str, Any],
    operator_action: str,
    codex_restart_used: bool,
    host_tui_reconnect_used: bool,
    unsafe_process_kill_used: bool = False,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    generated = generated_at or datetime.now(UTC)
    before_epoch = _epoch(before_diagnosis)
    after_epoch = _epoch(after_diagnosis)
    validation = _validation(after_diagnosis, unsafe_process_kill_used)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated.isoformat(),
        "server_id": server_id,
        "before_classification": before_diagnosis.get("classification", "unknown"),
        "before_epoch_id": before_epoch.get("epoch_id"),
        "before_proof_status": _primary_proof_status(before_diagnosis),
        "operator_action": operator_action,
        "after_classification": after_diagnosis.get("classification", "unknown"),
        "after_epoch_id": after_epoch.get("epoch_id"),
        "after_proof_status": _primary_proof_status(after_diagnosis),
        "active_tool_proof_required": True,
        "codex_restart_used": codex_restart_used,
        "host_tui_reconnect_used": host_tui_reconnect_used,
        "unsafe_process_kill_used": unsafe_process_kill_used,
        "script_performed_recovery": False,
        "recovery_status": "PASS" if validation["status"] == "PASS" else "FAIL_CLOSED",
        "validation": validation,
    }


def write_recovery_receipt(receipt: dict[str, Any], receipt_dir: Path = RECEIPT_DIR) -> Path:
    receipt_dir.mkdir(parents=True, exist_ok=True)
    server_id = str(receipt.get("server_id") or "unknown").replace("/", "_").replace("\\", "_")
    generated_at = str(receipt.get("generated_at") or datetime.now(UTC).isoformat())
    digest = hashlib.sha256(json.dumps(receipt, sort_keys=True).encode("utf-8")).hexdigest()[:6]
    stamp = generated_at.replace(":", "").replace("-", "").split(".")[0].replace("+0000", "Z")
    path = receipt_dir / f"{stamp}_{server_id}_{digest}.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _before_from_args(args: argparse.Namespace) -> dict[str, Any]:
    if args.before_diagnosis:
        return _load_json(args.before_diagnosis)
    return {
        "classification": args.before_classification,
        "evidence": {
            "callability_epoch": {
                "epoch_id": args.before_epoch_id,
                "status": args.before_proof_status,
            }
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", required=True, help="Stable MCP server id, such as adg_sqlite")
    parser.add_argument("--before-diagnosis", type=Path, help="Saved JSON output from diagnose_codex_mcp_transport.py")
    parser.add_argument("--after-diagnosis", type=Path, help="Optional saved after-diagnosis JSON for offline receipt tests")
    parser.add_argument("--before-classification", default="unknown", help="Manual before classification when --before-diagnosis is absent")
    parser.add_argument("--before-epoch-id", default=None, help="Manual before epoch id when --before-diagnosis is absent")
    parser.add_argument("--before-proof-status", default="absent", help="Manual before proof status when --before-diagnosis is absent")
    parser.add_argument("--operator-action", required=True, help="Manual operator action, such as host_tui_reconnect or codex_restart")
    parser.add_argument("--codex-restart-used", action="store_true", help="Record that the operator restarted Codex")
    parser.add_argument("--host-tui-reconnect-used", action="store_true", help="Record that the operator used host/TUI MCP reconnect")
    parser.add_argument("--unsafe-process-kill-used", action="store_true", help="Record and fail closed if unsafe process killing was used")
    parser.add_argument("--output-dir", type=Path, default=RECEIPT_DIR, help="Receipt output directory")
    parser.add_argument("--json", action="store_true", help="Emit JSON result")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    before_diagnosis = _before_from_args(args)
    after_diagnosis = (
        _load_json(args.after_diagnosis)
        if args.after_diagnosis
        else diagnose_codex_mcp_transport.build_diagnosis(args.server)
    )
    receipt = build_recovery_receipt(
        server_id=args.server,
        before_diagnosis=before_diagnosis,
        after_diagnosis=after_diagnosis,
        operator_action=args.operator_action,
        codex_restart_used=args.codex_restart_used,
        host_tui_reconnect_used=args.host_tui_reconnect_used,
        unsafe_process_kill_used=args.unsafe_process_kill_used,
    )
    path = write_recovery_receipt(receipt, args.output_dir)
    result = {"receipt_path": str(path), "receipt": receipt}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"receipt_path: {path}")
        print(f"recovery_status: {receipt['recovery_status']}")
        print(f"validation: {receipt['validation']['reason']}")
    return 0 if receipt["validation"]["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
