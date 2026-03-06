"""Phase 3: SovereignLLMGateway 'no bypass' topology enforcement.

Policy: ADG::Policy::LLM_EGRESS_SINGLETON
Allowed topology: Agents/Tools -> SovereignLLMGateway -> Provider
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.client.mcp_client import ADGMCPClient
from agentic_core.adg.schema import (
    GATEWAY_ALLOWLIST,
    PROVIDER_SDK_SYMBOLS,
    canonical_name,
)

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

logger = logging.getLogger(__name__)

_POLICY_ID = "ADG::Policy::LLM_EGRESS_SINGLETON"
_GW_PATH = GATEWAY_ALLOWLIST["SovereignLLMGateway"]
_GW_NODE = canonical_name("Gateway", "SovereignLLMGateway")

_ALLOWED_DIRECT_PROVIDER_MODULES: frozenset[str] = frozenset(
    {
        _GW_PATH,
        "data/sdks_mcps/client_wrappers.py",
    }
)


@dataclass
class GatewayViolation:
    """A gateway topology violation."""

    from_module: str
    to_symbol: str
    source_file: str
    line_no: int
    policy_id: str = _POLICY_ID

    def format(self) -> str:
        return (
            f"GATEWAY-VIOLATION policy={self.policy_id}\n"
            f"  from:  {self.from_module}\n"
            f"  to:    {self.to_symbol}\n"
            f"  file:  {self.source_file}:{self.line_no}"
        )


@dataclass
class GatewayTopologyReport:
    """Result of gateway topology enforcement check."""

    violations: list[GatewayViolation] = field(default_factory=list)
    provider_invocations: int = 0
    gateway_routes: int = 0
    snapshot_digest: str = ""

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0


def _module_rel(adg_name: str) -> str:
    prefix = "ADG::Module::"
    return adg_name[len(prefix) :] if adg_name.startswith(prefix) else adg_name


def _symbol_name(adg_name: str) -> str:
    prefix = "ADG::Symbol::"
    return adg_name[len(prefix) :] if adg_name.startswith(prefix) else adg_name


def check_gateway_topology(
    result: ScanResult,
    client: ADGMCPClient | None = None,
) -> GatewayTopologyReport:
    """Check that all provider invocations route through SovereignLLMGateway."""
    provider_bases = {s.split(".")[0] for s in PROVIDER_SDK_SYMBOLS}
    provider_invocations = []
    gateway_routes = []

    for edge in result.edges:
        sym = _symbol_name(edge.to_name)
        sym_base = sym.split(".")[0]

        if edge.relation_type in ("imports", "invokes_provider") and sym_base in provider_bases:
            provider_invocations.append(edge)

        if edge.relation_type == "routes_through" and _GW_PATH in _symbol_name(edge.to_name):
            gateway_routes.append(edge)

    violations: list[GatewayViolation] = []
    for edge in provider_invocations:
        from_rel = _module_rel(edge.from_name)
        norm = from_rel.replace("\\", "/")
        if any(norm == allowed or norm.endswith(allowed) for allowed in _ALLOWED_DIRECT_PROVIDER_MODULES):
            continue
        sym = _symbol_name(edge.to_name)
        violations.append(
            GatewayViolation(
                from_module=from_rel,
                to_symbol=sym,
                source_file=edge.source_file,
                line_no=edge.line_no,
            )
        )

    proof_digest = _compute_proof_digest(result, violations)
    report = GatewayTopologyReport(
        violations=violations,
        provider_invocations=len(provider_invocations),
        gateway_routes=len(gateway_routes),
        snapshot_digest=proof_digest,
    )

    if client is not None:
        _persist_proof(result, report, client)

    return report


def _compute_proof_digest(result: ScanResult, violations: list[GatewayViolation]) -> str:
    lines = [result.digest]
    for v in sorted(violations, key=lambda x: (x.from_module, x.to_symbol, x.line_no)):
        lines.append(f"{v.from_module}|{v.to_symbol}|{v.line_no}")
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def _persist_proof(
    result: ScanResult,
    report: GatewayTopologyReport,
    client: ADGMCPClient,
) -> None:
    if not result.commit_sha:
        return
    proof_node = canonical_name("Snapshot", result.commit_sha, "gateway_topology_proof")
    client.upsert_entity(
        proof_node,
        "snapshot",
        [
            f"commit:{result.commit_sha}",
            f"snapshot_digest:{report.snapshot_digest}",
            f"provider_invocations:{report.provider_invocations}",
            f"gateway_routes:{report.gateway_routes}",
            f"violation_count:{len(report.violations)}",
            f"policy_id:{_POLICY_ID}",
        ],
    )
    client.upsert_relation(
        proof_node,
        "violates" if not report.passed else "allows",
        _GW_NODE,
    )


__all__ = ["check_gateway_topology", "GatewayTopologyReport", "GatewayViolation"]
