"""Phase 4: UWG Write Authority side-effect control.

Policy: ADG::Policy::UWG_WRITE_AUTHORITY
All filesystem writes, network calls, database writes, and subprocess
executions must route through UniversalWriteGateway.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.client.mcp_client import ADGMCPClient
from agentic_core.adg.schema import (
    GATEWAY_ALLOWLIST,
    canonical_name,
)

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

logger = logging.getLogger(__name__)

_POLICY_ID = "ADG::Policy::UWG_WRITE_AUTHORITY"
_UWG_PATH = GATEWAY_ALLOWLIST["UniversalWriteGateway"]
_UWG_NODE = canonical_name("Gateway", "UniversalWriteGateway")

_SIDE_EFFECT_ENDPOINTS: dict[str, frozenset[str]] = {
    "filesystem_write": frozenset(
        {
            "open",
            "write",
            "os.remove",
            "os.rename",
            "os.makedirs",
            "os.mkdir",
            "shutil.copy",
            "shutil.move",
            "shutil.rmtree",
            "pathlib.Path.write_text",
            "pathlib.Path.write_bytes",
            "write_text",
            "write_bytes",
        }
    ),
    "subprocess_exec": frozenset(
        {
            "subprocess.run",
            "subprocess.Popen",
            "subprocess.call",
            "subprocess.check_call",
            "subprocess.check_output",
        }
    ),
    "network_call": frozenset(
        {
            "requests.get",
            "requests.post",
            "requests.put",
            "requests.delete",
            "requests.patch",
            "httpx.get",
            "httpx.post",
            "httpx.Client",
            "httpx.AsyncClient",
            "aiohttp.ClientSession",
            "urllib.request.urlopen",
        }
    ),
    "database_write": frozenset(
        {
            "cursor.execute",
            "session.add",
            "session.commit",
            "collection.insert",
            "collection.update",
            "redis.set",
            "redis.hset",
        }
    ),
}

_ALLOWED_WRITE_MODULES: frozenset[str] = frozenset(
    {
        _UWG_PATH,
        "agentic_core/L2_execution/audit/hash_chain_audit_log.py",
        "tools/capture_evidence.py",
        "ops_scripts/ci/",
    }
)


def _module_rel(adg_name: str) -> str:
    prefix = "ADG::Module::"
    return adg_name[len(prefix) :] if adg_name.startswith(prefix) else adg_name


def _symbol_name(adg_name: str) -> str:
    prefix = "ADG::Symbol::"
    return adg_name[len(prefix) :] if adg_name.startswith(prefix) else adg_name


def _is_allowed_module(rel_path: str) -> bool:
    norm = rel_path.replace("\\", "/")
    for allowed in _ALLOWED_WRITE_MODULES:
        if norm == allowed or norm.startswith(allowed):
            return True
    if "test_" in norm or norm.startswith("tests/"):
        return True
    return False


def _classify_side_effect(sym: str) -> str:
    sym_tail = sym.split(".")[-1]
    for endpoint_type, syms in _SIDE_EFFECT_ENDPOINTS.items():
        if sym in syms:
            return endpoint_type
        if any(s.endswith(sym_tail) for s in syms if "." in s):
            return endpoint_type
    return "filesystem_write"


@dataclass
class UWGViolation:
    """A UWG write authority violation."""

    from_module: str
    to_symbol: str
    endpoint_type: str
    source_file: str
    line_no: int
    policy_id: str = _POLICY_ID

    def format(self) -> str:
        return (
            f"UWG-VIOLATION policy={self.policy_id} endpoint={self.endpoint_type}\n"
            f"  from:  {self.from_module}\n"
            f"  to:    {self.to_symbol}\n"
            f"  file:  {self.source_file}:{self.line_no}"
        )


@dataclass
class UWGReport:
    """Result of UWG write authority check."""

    violations: list[UWGViolation] = field(default_factory=list)
    write_edges_count: int = 0
    snapshot_digest: str = ""

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0


def check_uwg_write_authority(
    result: ScanResult,
    client: ADGMCPClient | None = None,
) -> UWGReport:
    """Check that all side-effect writes route through UniversalWriteGateway."""
    write_edges = [e for e in result.edges if e.edge_kind == "write" and e.relation_type == "writes_to"]

    violations: list[UWGViolation] = []
    for edge in write_edges:
        from_rel = _module_rel(edge.from_name)
        if _is_allowed_module(from_rel):
            continue
        sym = _symbol_name(edge.to_name)
        endpoint_type = _classify_side_effect(sym)
        violations.append(
            UWGViolation(
                from_module=from_rel,
                to_symbol=sym,
                endpoint_type=endpoint_type,
                source_file=edge.source_file,
                line_no=edge.line_no,
            )
        )

    proof_digest = _compute_proof_digest(result, violations)
    report = UWGReport(
        violations=violations,
        write_edges_count=len(write_edges),
        snapshot_digest=proof_digest,
    )

    if client is not None:
        _persist_proof(result, report, client)

    return report


def _compute_proof_digest(result: ScanResult, violations: list[UWGViolation]) -> str:
    lines = [result.digest]
    for v in sorted(violations, key=lambda x: (x.from_module, x.to_symbol, x.line_no)):
        lines.append(f"{v.from_module}|{v.to_symbol}|{v.endpoint_type}|{v.line_no}")
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def _persist_proof(
    result: ScanResult,
    report: UWGReport,
    client: ADGMCPClient,
) -> None:
    if not result.commit_sha:
        return
    proof_node = canonical_name("Snapshot", result.commit_sha, "uwg_write_authority_proof")
    client.upsert_entity(
        proof_node,
        "snapshot",
        [
            f"commit:{result.commit_sha}",
            f"snapshot_digest:{report.snapshot_digest}",
            f"write_edges_count:{report.write_edges_count}",
            f"violation_count:{len(report.violations)}",
            f"policy_id:{_POLICY_ID}",
        ],
    )
    client.upsert_relation(
        proof_node,
        "violates" if not report.passed else "allows",
        _UWG_NODE,
    )


__all__ = ["check_uwg_write_authority", "UWGReport", "UWGViolation"]
