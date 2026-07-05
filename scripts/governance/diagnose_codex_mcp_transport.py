"""Diagnose Codex MCP transport state without touching MCP processes.

This script is intentionally read-only. It does not launch MCP servers, kill
processes, call Codex MCP tools, or treat direct SQLite access as ADG MCP
callability. It composes existing Codex transport evidence into one recovery
recommendation for a single server.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GOVERNANCE_DIR = ROOT / "scripts" / "governance"
CODEX_GOVERNANCE_SCRIPTS = ROOT / ".codex" / "governance" / "scripts"
for candidate in (GOVERNANCE_DIR, ROOT, CODEX_GOVERNANCE_SCRIPTS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import audit_codex_mcp_transports  # noqa: E402
import codex_readiness  # noqa: E402
import mcp_callability_epoch  # noqa: E402


SCHEMA_VERSION = "codex-mcp-transport-diagnosis/v1"
AGGREGATE_SCHEMA_VERSION = "codex-mcp-transport-diagnosis-aggregate/v1"
REQUIRED_CORE_SERVERS = tuple(codex_readiness.DEFAULT_REQUIRED_CALLABLE_ROUTES)
DUPLICATE_PROCESS_CLASSIFICATIONS = {"duplicate", "duplicate_launch_tree"}
STALE_PROOF_STATUSES = {
    "stale_epoch",
    "stale_age",
    "stale_file_proof",
    "malformed_proof",
    "session_mismatch",
    "dead_pid",
}
CALLABLE_CLASSIFICATIONS = {"CALLABLE"}
PLUGIN_CLASSIFICATIONS = {"PLUGIN_SUBSTITUTE"}
SUBSTITUTE_CLASSIFICATIONS = {"SUBSTITUTE_CALLABLE"}
NON_BLOCKING_CLASSIFICATIONS = {"callable", "plugin_substitute", "substitute_callable"}


def _load_configured_servers(root: Path = ROOT) -> set[str]:
    registry_path = root / ".mcp.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return set()
    servers = registry.get("mcpServers")
    if not isinstance(servers, dict):
        return set()
    return {str(server_id) for server_id in servers}


def _attached_pid_from_env(server_id: str, env: dict[str, str] | None = None) -> int | None:
    resolved_env = env if env is not None else os.environ
    value = resolved_env.get(f"CODEX_MCP_ATTACHED_{server_id.upper()}_PID", "").strip()
    if not value:
        return None
    try:
        pid = int(value)
    except ValueError:
        return None
    return pid if pid > 0 else None


def _epoch_proof_status(server_id: str, root: Path = ROOT) -> dict[str, Any]:
    try:
        return mcp_callability_epoch.proof_status(server_id, repo_root=root)
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        return {
            "server_id": server_id,
            "status": "error",
            "reason": f"{type(exc).__name__}: {exc}",
        }


def _adg_transport_status(
    runtime_root: Path = ROOT,
    transport_checker: Any | None = None,
) -> dict[str, Any] | None:
    try:
        from tools.adg.mcp import supervisor
    except (ImportError, OSError) as exc:
        return {"status": "error", "reason": f"{type(exc).__name__}: {exc}"}

    checker = transport_checker or supervisor.transport_status
    try:
        return checker(
            state_path=runtime_root / supervisor.DEFAULT_STATE_RELATIVE_PATH,
            proof_path=runtime_root / supervisor.DEFAULT_CALLABLE_PROOF_RELATIVE_PATH,
        )
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        return {"status": "error", "reason": f"{type(exc).__name__}: {exc}"}


def _process_cleanup_state(server_id: str, process_state: dict[str, Any]) -> tuple[bool | str, dict[str, Any]]:
    process_classification = str(process_state.get("classification") or "none").strip()
    duplicate = process_classification in DUPLICATE_PROCESS_CLASSIFICATIONS
    attached_pid = _attached_pid_from_env(server_id)
    detail = {
        "process_classification": process_classification,
        "process_count": process_state.get("process_count", 0),
        "attached_pid_env_present": attached_pid is not None,
        "attached_pid": attached_pid,
    }
    if not duplicate:
        return False, detail
    if attached_pid is None:
        detail["cleanup_blocker"] = "attached_pid_required"
        return "requires_attached_pid", detail
    detail["cleanup_note"] = "Attached PID proof is present; use cleanup helper, not this diagnostic wrapper, if cleanup is required."
    return True, detail


def _is_closed_transport(route_state: dict[str, Any], adg_status: dict[str, Any] | None) -> bool:
    return (
        str(route_state.get("callable_status") or "").strip().lower() == "closed_transport"
        or str(route_state.get("fallback_message_key") or "").strip().lower() == "closed_transport"
        or str(route_state.get("classification") or "").strip().upper() == "EXPOSED_BLOCKED"
        or str((adg_status or {}).get("status") or "").strip().lower() == "closed_transport"
    )


def _stale_proof_status(route_state: dict[str, Any], epoch_proof: dict[str, Any], adg_status: dict[str, Any] | None) -> str:
    route_proof = route_state.get("callability_proof")
    if isinstance(route_proof, dict):
        route_status = str(route_proof.get("status") or "").strip().lower()
        if route_status in STALE_PROOF_STATUSES:
            return route_status
    epoch_status = str(epoch_proof.get("status") or "").strip().lower()
    if epoch_status in STALE_PROOF_STATUSES:
        return epoch_status
    callable_proof = (adg_status or {}).get("callable_proof")
    if isinstance(callable_proof, dict):
        status = str(callable_proof.get("status") or "").strip().lower()
        if status in STALE_PROOF_STATUSES:
            return status
        file_proof = callable_proof.get("file_proof")
        if isinstance(file_proof, dict):
            file_status = str(file_proof.get("status") or "").strip().lower()
            if file_status in STALE_PROOF_STATUSES:
                return file_status
    return ""


def _classify(
    server_id: str,
    *,
    configured_servers: set[str],
    route_evidence: dict[str, Any],
    route_state: dict[str, Any],
    process_state: dict[str, Any],
    cleanup_state: bool | str,
    epoch_proof: dict[str, Any],
    adg_status: dict[str, Any] | None,
) -> str:
    if server_id not in configured_servers and not route_state:
        return "not_configured"
    if not route_evidence.get("available"):
        return "no_route_contract"
    if not route_state:
        return "no_route_contract"

    route_classification = str(route_state.get("classification") or "").strip().upper()
    callable_status = str(route_state.get("callable_status") or "").strip().lower()
    if route_classification in CALLABLE_CLASSIFICATIONS or callable_status == "healthy":
        return "callable"
    if route_classification in PLUGIN_CLASSIFICATIONS or callable_status == "plugin_callable":
        return "plugin_substitute"
    if route_classification in SUBSTITUTE_CLASSIFICATIONS or callable_status == "substitute_callable":
        return "substitute_callable"
    if _is_closed_transport(route_state, adg_status):
        return "server_healthy_codex_transport_closed"

    stale_status = _stale_proof_status(route_state, epoch_proof, adg_status)
    if stale_status:
        return "stale_callability_proof"

    if cleanup_state == "requires_attached_pid":
        return "duplicate_cohort"
    if route_classification == "PROCESS_ONLY":
        return "process_only_callability_unproven"
    if route_classification == "HOST_MCP_REQUIRED" or route_classification == "NOT_EXPOSED":
        return "host_mcp_required"
    if route_classification == "DEGRADED_FALLBACK":
        return "degraded_fallback_available"
    return "unknown"


def _recommended_action(classification: str, server_id: str) -> str:
    proof_tool = "mcp__adg_sqlite.adg_health" if server_id == "adg_sqlite" else f"mcp__{server_id}.<health_or_identity_tool>"
    if classification == "callable":
        return "No recovery needed; active Codex MCP callability proof is present."
    if classification == "plugin_substitute":
        return "Use the documented Codex plugin substitute; no raw MCP transport recovery is required for this route."
    if classification == "substitute_callable":
        return "Use the documented callable substitute and do not claim raw MCP parity."
    if classification == "server_healthy_codex_transport_closed":
        return (
            "Host/TUI MCP reconnect is required; a shell cannot reattach Codex to a closed stdio transport. "
            f"Use Codex host MCP management, then prove a live {proof_tool} call before setting callability overrides."
        )
    if classification == "duplicate_cohort":
        return (
            "Duplicate Codex-owned MCP process cohorts are present. Do not kill them without active host-attached PID proof; "
            "request process-identity proof first, then use the guarded cleanup helper if cleanup is still needed."
        )
    if classification == "stale_callability_proof":
        return (
            "Discard stale callability proof. Prove a fresh active Codex MCP tool call in the current session, "
            "or keep this route blocked."
        )
    if classification == "process_only_callability_unproven":
        return "Process presence is not callability proof; prove an active Codex tool call or keep this route blocked."
    if classification == "host_mcp_required":
        return "Sync MCP config and start a new Codex session or use host MCP management; do not mark green until active tool-call proof exists."
    if classification == "degraded_fallback_available":
        return "Use only the explicitly stamped degraded fallback; do not count it as green readiness."
    if classification == "no_route_contract":
        return "No route contract evidence is available for this server; provide --route-contract or regenerate current route evidence before recovery."
    if classification == "not_configured":
        return "Server is not configured in root .mcp.json; do not attempt MCP recovery unless the registry is intentionally updated."
    return "Transport state is unknown; keep the route blocked and collect fresh audit evidence."


def _codex_restart_required(classification: str) -> bool | str:
    if classification in {"callable", "plugin_substitute", "substitute_callable", "degraded_fallback_available", "not_configured"}:
        return False
    if classification == "host_mcp_required":
        return True
    return "unknown"


def _degraded_fallback_available(classification: str) -> bool:
    return classification == "degraded_fallback_available"


def build_diagnosis(
    server_id: str,
    *,
    route_contract_path: Path | None = None,
    report: dict[str, Any] | None = None,
    adg_transport_checker: Any | None = None,
    root: Path = ROOT,
) -> dict[str, Any]:
    audit_report = report if report is not None else audit_codex_mcp_transports.build_report(route_contract_path)
    runtime_root = root
    raw_runtime_root = audit_report.get("primary_root")
    if isinstance(raw_runtime_root, str) and raw_runtime_root.strip():
        candidate = Path(raw_runtime_root)
        if candidate.exists():
            runtime_root = candidate
    route_evidence = audit_report.get("route_evidence", {})
    if not isinstance(route_evidence, dict):
        route_evidence = {}
    route_servers = route_evidence.get("servers", {})
    if not isinstance(route_servers, dict):
        route_servers = {}
    route_state = route_servers.get(server_id)
    route_state = route_state if isinstance(route_state, dict) else {}

    process_servers = audit_report.get("processes", {}).get("servers", {})
    if not isinstance(process_servers, dict):
        process_servers = {}
    process_state = process_servers.get(server_id)
    process_state = process_state if isinstance(process_state, dict) else {}

    cleanup_state, cleanup_evidence = _process_cleanup_state(server_id, process_state)
    epoch_proof = _epoch_proof_status(server_id, runtime_root)
    adg_status = _adg_transport_status(runtime_root, adg_transport_checker) if server_id == "adg_sqlite" else None
    configured_servers = _load_configured_servers(root)
    classification = _classify(
        server_id,
        configured_servers=configured_servers,
        route_evidence=route_evidence,
        route_state=route_state,
        process_state=process_state,
        cleanup_state=cleanup_state,
        epoch_proof=epoch_proof,
        adg_status=adg_status,
    )
    evidence = {
        "route_contract_path": audit_report.get("route_contract_path"),
        "diagnosis_root": str(root),
        "runtime_root": str(runtime_root),
        "route_evidence_available": route_evidence.get("available", False),
        "route_counts": route_evidence.get("counts", {}),
        "route_state": route_state,
        "process_state": process_state,
        "cleanup": cleanup_evidence,
        "callability_epoch": epoch_proof,
        "configured_in_mcp_json": server_id in configured_servers,
    }
    if adg_status is not None:
        evidence["adg_transport_status"] = adg_status
    if classification == "server_healthy_codex_transport_closed":
        evidence["transport_rca"] = codex_readiness._closed_transport_rca(server_id, route_state)  # noqa: SLF001

    return {
        "schema_version": SCHEMA_VERSION,
        "server_id": server_id,
        "classification": classification,
        "recommended_action": _recommended_action(classification, server_id),
        "codex_restart_required": _codex_restart_required(classification),
        "shell_reopen_supported": False,
        "safe_to_cleanup_processes": cleanup_state,
        "degraded_fallback_available": _degraded_fallback_available(classification),
        "evidence": evidence,
    }


def _dedupe_server_ids(server_ids: list[str] | tuple[str, ...]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for server_id in server_ids:
        normalized = str(server_id).strip()
        if normalized and normalized not in seen:
            ordered.append(normalized)
            seen.add(normalized)
    return ordered


def _proof_status_from_diagnosis(diagnosis: dict[str, Any]) -> str:
    evidence = diagnosis.get("evidence")
    if not isinstance(evidence, dict):
        return "absent"
    callability_epoch = evidence.get("callability_epoch")
    if isinstance(callability_epoch, dict):
        status = str(callability_epoch.get("status") or "").strip()
        if status:
            return status
    route_state = evidence.get("route_state")
    if isinstance(route_state, dict):
        route_proof = route_state.get("callability_proof")
        if isinstance(route_proof, dict):
            status = str(route_proof.get("status") or "").strip()
            if status:
                return status
    adg_status = evidence.get("adg_transport_status")
    if isinstance(adg_status, dict):
        callable_proof = adg_status.get("callable_proof")
        if isinstance(callable_proof, dict):
            status = str(callable_proof.get("status") or "").strip()
            if status:
                return status
    return "absent"


def _diagnosis_summary(diagnosis: dict[str, Any]) -> dict[str, Any]:
    evidence = diagnosis.get("evidence")
    evidence = evidence if isinstance(evidence, dict) else {}
    route_state = evidence.get("route_state")
    route_state = route_state if isinstance(route_state, dict) else {}
    process_state = evidence.get("process_state")
    process_state = process_state if isinstance(process_state, dict) else {}
    return {
        "server_id": diagnosis.get("server_id"),
        "classification": diagnosis.get("classification"),
        "callable_proof_status": _proof_status_from_diagnosis(diagnosis),
        "callable_status": route_state.get("callable_status"),
        "process_state": {
            "classification": process_state.get("classification", "none"),
            "process_count": process_state.get("process_count", 0),
        },
        "cleanup_safety": diagnosis.get("safe_to_cleanup_processes"),
        "degraded_fallback_available": diagnosis.get("degraded_fallback_available"),
        "recommended_action": diagnosis.get("recommended_action"),
    }


def _aggregate_counts(diagnoses: dict[str, dict[str, Any]], configured_servers: set[str]) -> dict[str, Any]:
    classification_counts: dict[str, int] = {}
    for diagnosis in diagnoses.values():
        classification = str(diagnosis.get("classification") or "unknown")
        classification_counts[classification] = classification_counts.get(classification, 0) + 1

    return {
        "required_route_count": sum(1 for server_id in REQUIRED_CORE_SERVERS if server_id in diagnoses),
        "diagnosed_route_count": len(diagnoses),
        "configured_route_count": len(configured_servers),
        "callable_count": classification_counts.get("callable", 0),
        "blocked_count": sum(
            1
            for diagnosis in diagnoses.values()
            if str(diagnosis.get("classification") or "unknown") not in NON_BLOCKING_CLASSIFICATIONS
        ),
        "process_only_count": classification_counts.get("process_only_callability_unproven", 0),
        "duplicate_cohort_count": classification_counts.get("duplicate_cohort", 0),
        "stale_proof_count": classification_counts.get("stale_callability_proof", 0),
        "classification_counts": dict(sorted(classification_counts.items())),
    }


def build_aggregate_diagnosis(
    server_ids: list[str] | tuple[str, ...],
    *,
    mode: str,
    route_contract_path: Path | None = None,
    report: dict[str, Any] | None = None,
    adg_transport_checker: Any | None = None,
    root: Path = ROOT,
    summary: bool = False,
) -> dict[str, Any]:
    audit_report = report if report is not None else audit_codex_mcp_transports.build_report(route_contract_path)
    configured_servers = _load_configured_servers(root)
    selected_server_ids = _dedupe_server_ids(server_ids)
    diagnoses = {
        server_id: build_diagnosis(
            server_id,
            route_contract_path=route_contract_path,
            report=audit_report,
            adg_transport_checker=adg_transport_checker,
            root=root,
        )
        for server_id in selected_server_ids
    }
    server_payload = {
        server_id: _diagnosis_summary(diagnosis) if summary else diagnosis
        for server_id, diagnosis in diagnoses.items()
    }
    return {
        "schema_version": AGGREGATE_SCHEMA_VERSION,
        "mode": mode,
        "summary": summary,
        "counts": _aggregate_counts(diagnoses, configured_servers),
        "required_servers": list(REQUIRED_CORE_SERVERS),
        "diagnosed_servers": selected_server_ids,
        "servers": server_payload,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--server", help="Stable MCP server id, such as adg_sqlite")
    target.add_argument("--all-required", action="store_true", help="Diagnose required core Codex MCP routes")
    target.add_argument("--all-configured", action="store_true", help="Diagnose every server configured in root .mcp.json")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--summary", action="store_true", help="Emit compact per-server evidence instead of full diagnosis evidence")
    parser.add_argument(
        "--route-contract",
        type=Path,
        help="Optional Codex route contract JSON. Defaults to the audit helper's current route-contract resolution.",
    )
    args = parser.parse_args(argv)

    if args.server:
        diagnosis = build_diagnosis(args.server, route_contract_path=args.route_contract)
        payload = _diagnosis_summary(diagnosis) if args.summary else diagnosis
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"server_id: {payload['server_id']}")
            print(f"classification: {payload['classification']}")
            print(f"recommended_action: {payload['recommended_action']}")
            if not args.summary:
                print(f"codex_restart_required: {payload['codex_restart_required']}")
                print(f"safe_to_cleanup_processes: {payload['safe_to_cleanup_processes']}")
        return 0

    if args.all_required:
        server_ids = list(REQUIRED_CORE_SERVERS)
        mode = "all_required"
    else:
        server_ids = sorted(_load_configured_servers(ROOT))
        mode = "all_configured"

    diagnosis = build_aggregate_diagnosis(
        server_ids,
        mode=mode,
        route_contract_path=args.route_contract,
        summary=args.summary,
    )
    if args.json:
        print(json.dumps(diagnosis, indent=2, sort_keys=True))
    else:
        counts = diagnosis["counts"]
        print(f"mode: {diagnosis['mode']}")
        print(f"required_route_count: {counts['required_route_count']}")
        print(f"callable_count: {counts['callable_count']}")
        print(f"blocked_count: {counts['blocked_count']}")
        for server_id, server in diagnosis["servers"].items():
            print(f"{server_id}: {server['classification']} - {server['recommended_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
