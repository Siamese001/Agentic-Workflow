"""Write explicit Codex MCP callable-route proof into the live route contract."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "codex" / "codex_mcp_live_route_contract.json"
VALID_CALLABLE_STATUSES = frozenset({"healthy"})
DEFAULT_ALWAYS_ON_CORE = ["adg_sqlite", "memory", "GitKraken"]


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _base_contract() -> dict[str, Any]:
    return {
        "generated_at": datetime.now(UTC).date().isoformat(),
        "plan_id": "codex-mcp-callable-route-proof",
        "wave": "callable-route-proof",
        "status": "degraded",
        "always_on_core": DEFAULT_ALWAYS_ON_CORE,
        "routes": [],
    }


def load_contract(path: Path) -> dict[str, Any]:
    if not path.exists():
        return _base_contract()
    return json.loads(path.read_text(encoding="utf-8"))


def validate_proof(*, callable_status: str, tool: str, evidence: str) -> None:
    status = callable_status.strip().lower()
    if status not in VALID_CALLABLE_STATUSES:
        raise ValueError(f"unsupported callable status: {callable_status!r}")
    if not tool.strip():
        raise ValueError("healthy callable proof requires --tool")
    if not evidence.strip():
        raise ValueError("healthy callable proof requires --evidence")


def build_route(
    *,
    server: str,
    callable_status: str,
    tool: str,
    evidence: str,
    proved_at: str,
    existing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_proof(callable_status=callable_status, tool=tool, evidence=evidence)
    route = dict(existing or {})
    route.update(
        {
            "server_id": server,
            "codex_route": "raw_mcp",
            "selected_codex_route": "raw_mcp_callable",
            "status": "callable",
            "callable_status": callable_status.strip().lower(),
            "contract": "Callable only when backed by explicit active Codex MCP tool-call proof.",
            "proof": {
                "proved_at": proved_at,
                "tool": tool.strip(),
                "tool_calls": [tool.strip()],
                "evidence": evidence.strip(),
            },
        }
    )
    return route


def upsert_route(contract: dict[str, Any], route: dict[str, Any]) -> dict[str, Any]:
    server = route["server_id"]
    routes = list(contract.get("routes") or [])
    for index, existing in enumerate(routes):
        if existing.get("server_id") == server:
            routes[index] = route
            break
    else:
        routes.append(route)
    contract["routes"] = routes
    contract["generated_at"] = datetime.now(UTC).date().isoformat()
    _refresh_contract_status(contract)
    return contract


def _refresh_contract_status(contract: dict[str, Any]) -> None:
    required = {"memory", "GitKraken"}
    proven = {
        str(route.get("server_id"))
        for route in contract.get("routes", [])
        if str(route.get("callable_status") or "").lower() == "healthy"
        and route.get("selected_codex_route") == "raw_mcp_callable"
        and isinstance(route.get("proof"), dict)
        and str(route["proof"].get("tool") or "").strip()
        and str(route["proof"].get("evidence") or "").strip()
    }
    missing = sorted(required - proven)
    if missing:
        contract["status"] = "degraded"
        contract["blocker"] = {
            "id": "HOST-MCP-ROUTE-PROOF-MISSING",
            "summary": "Required Codex MCP callable-route proof is missing.",
            "missing_servers": missing,
        }
    else:
        contract["status"] = "callable"
        contract["blocker"] = {
            "id": "NONE",
            "summary": "Required Memory and GitKraken callable-route proofs are recorded.",
        }


def write_contract(
    *,
    output: Path,
    server: str,
    callable_status: str,
    tool: str,
    evidence: str,
    proved_at: str | None = None,
) -> dict[str, Any]:
    contract = load_contract(output)
    existing = next((route for route in contract.get("routes", []) if route.get("server_id") == server), None)
    route = build_route(
        server=server,
        callable_status=callable_status,
        tool=tool,
        evidence=evidence,
        proved_at=proved_at or _now_iso(),
        existing=existing,
    )
    updated = upsert_route(contract, route)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(updated, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return updated


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", required=True, help="MCP server id, for example memory or GitKraken.")
    parser.add_argument("--callable-status", required=True, choices=sorted(VALID_CALLABLE_STATUSES))
    parser.add_argument("--tool", default="", help="Exact successful Codex MCP tool name.")
    parser.add_argument("--evidence", default="", help="Short shape or summary of the successful tool result.")
    parser.add_argument("--proved-at", default="", help="Timestamp for the live tool-call proof.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        contract = write_contract(
            output=args.output,
            server=args.server,
            callable_status=args.callable_status,
            tool=args.tool,
            evidence=args.evidence,
            proved_at=args.proved_at or None,
        )
    except ValueError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        else:
            print(f"error: {exc}")
        return 2
    summary = {
        "ok": True,
        "output": str(args.output),
        "server": args.server,
        "status": contract.get("status"),
    }
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
