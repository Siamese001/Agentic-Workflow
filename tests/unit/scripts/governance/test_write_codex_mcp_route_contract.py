"""Tests for scripts/governance/write_codex_mcp_route_contract.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import audit_codex_mcp_transports as audit  # noqa: E402
import write_codex_mcp_route_contract as mod  # noqa: E402


def test_writer_refuses_healthy_without_evidence(tmp_path: Path) -> None:
    output = tmp_path / "contract.json"

    rc = mod.main(
        [
            "--server",
            "memory",
            "--callable-status",
            "healthy",
            "--tool",
            "mcp__memory.mem_get_stats",
            "--output",
            str(output),
            "--json",
        ]
    )

    assert rc == 2
    assert not output.exists()


def test_writer_emits_contract_consumed_by_audit(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("CODEX_MCP_CALLABLE_MEMORY", raising=False)
    output = tmp_path / "codex_mcp_live_route_contract.json"

    contract = mod.write_contract(
        output=output,
        server="memory",
        callable_status="healthy",
        tool="mcp__memory.mem_get_stats",
        evidence='{"total_entities": 351, "total_observations": 190}',
        proved_at="2026-06-21T16:02:39.4664076-04:00",
    )
    written = json.loads(output.read_text(encoding="utf-8"))
    evidence = audit.build_route_evidence(written, {}, trust_contract_callable_proof=True)

    assert contract["routes"][0]["selected_codex_route"] == "raw_mcp_callable"
    assert contract["status"] == "degraded"
    assert set(contract["blocker"]["missing_servers"]) == {"adg_sqlite", "GitKraken"}
    assert written["routes"][0]["proof"]["tool"] == "mcp__memory.mem_get_stats"
    assert evidence["servers"]["memory"]["classification"] == "CALLABLE"
    assert evidence["servers"]["memory"]["callable_status"] == "healthy"


def test_contract_status_requires_all_always_on_core_routes(tmp_path: Path) -> None:
    output = tmp_path / "codex_mcp_live_route_contract.json"
    for server, tool in [
        ("adg_sqlite", "mcp__adg_sqlite.adg_health"),
        ("memory", "mcp__memory.mem_get_stats"),
        ("GitKraken", "mcp__GitKraken.git_status"),
    ]:
        contract = mod.write_contract(
            output=output,
            server=server,
            callable_status="healthy",
            tool=tool,
            evidence="ok",
            proved_at="2026-06-27T08:00:00+00:00",
        )

    assert contract["status"] == "callable"
    assert contract["blocker"] == {
        "id": "NONE",
        "summary": "Required Codex MCP callable-route proofs are recorded.",
    }
