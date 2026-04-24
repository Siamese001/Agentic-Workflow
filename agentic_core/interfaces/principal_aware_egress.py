"""Principal-Aware Egress Adapter — L5 v4 G-04 W3.

Attaches a `PrincipalChain` to every external-egress call (LLM provider,
MCP connector, HTTP tool, A2A protocol) so the audit/replay record can
reconstruct which `invoking_user` authorized the call. Mirrors
`principal_aware_write.py` (W2) for the egress path instead of the write path.

Covers two egress surfaces:

1. **LLM Gateway egress** — `SovereignLLMGateway` outbound provider calls.
   The audit record emitted by the gateway MUST carry the principal_chain
   alongside the request/response digests so forensic replay can tie a
   provider response back to the specific invoking_user that requested it.

2. **MCP connector envelope** — every MCP tool call crossing the
   `infrastructure/sdks_mcps/client_wrappers.py` boundary. Per SAIF
   Principle 3 + identity_propagation.md §3.5, the MCP envelope must
   include the principal_chain so the remote MCP server can enforce its
   own `allowed_principals` + `connector_allowlist` match.

Rationale for an additive helper (same pattern as W2):
- Existing LLM Gateway + MCP client wrappers have large blast radius.
- Additive helper lets v4-aware call sites emit a principal-bound envelope
  without forcing a sweeping refactor of the underlying gateway.
- The helper emits a deterministic `egress_replay_key` suitable for
  inclusion in the replay_envelope (see calibration_assurance_planes.md §4.2).

Reference:
  - docs/contracts/identity_propagation.md §3.4, §3.5, §3.6
  - docs/reference/00_L5_Policy_Plane/Governance & Safety v4.md (Egress Inspection)
Parent plan: .windsurf/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Literal

from agentic_core.interfaces.principal_aware_write import (
    compute_principal_chain_digest,
)
from agentic_core.interfaces.principal_chain_types import PrincipalChain

EgressKind = Literal["llm_provider", "mcp_connector", "http_tool", "a2a_agent"]


def compute_egress_replay_key(
    *,
    egress_kind: EgressKind,
    target_id: str,
    request_digest: str,
    response_digest: str,
    principal_chain: PrincipalChain,
) -> str:
    """Deterministic replay key for an egress call bound to a principal.

    `target_id` is the egress endpoint identifier:
      - llm_provider: symbolic provider name (e.g., "anthropic:claude-opus-4")
      - mcp_connector: connector id from MCP Connector Registry
      - http_tool: tool id from Tool Registry
      - a2a_agent: target agent id

    Forensic replay reconstruction requires the egress_kind + target_id +
    request/response digests + principal_chain digest to all match. Any
    mismatch implies the replay envelope was tampered with or the audit
    record diverged from ground truth.
    """
    principal_digest = compute_principal_chain_digest(principal_chain)
    canonical = json.dumps(
        {
            "egress_kind": egress_kind,
            "principal_digest": principal_digest,
            "request_digest": request_digest,
            "response_digest": response_digest,
            "target_id": target_id,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PrincipalEgressEnvelope:
    """Immutable record binding an egress call to an invoking principal.

    Produced at the egress site, consumed by:
      - LLM Gateway audit log (W3)
      - MCP connector request envelope (W3)
      - safety_audit_emitter attribution (W5)
      - replay_envelope forensic reconstruction (W6 per spec)
    """

    egress_kind: EgressKind
    target_id: str
    request_digest: str
    response_digest: str
    principal_chain: PrincipalChain
    principal_chain_digest: str
    egress_replay_key: str

    def __post_init__(self) -> None:
        if self.egress_kind not in ("llm_provider", "mcp_connector", "http_tool", "a2a_agent"):
            raise ValueError(
                "PrincipalEgressEnvelope: egress_kind must be "
                "llm_provider|mcp_connector|http_tool|a2a_agent, "
                f"got '{self.egress_kind}'",
            )
        if not self.target_id:
            raise ValueError("PrincipalEgressEnvelope: target_id required")
        if not self.request_digest:
            raise ValueError("PrincipalEgressEnvelope: request_digest required")
        if not self.response_digest:
            raise ValueError("PrincipalEgressEnvelope: response_digest required")
        if not self.principal_chain_digest:
            raise ValueError(
                "PrincipalEgressEnvelope: principal_chain_digest required",
            )
        if not self.egress_replay_key:
            raise ValueError(
                "PrincipalEgressEnvelope: egress_replay_key required",
            )

    def to_dict(self) -> dict[str, object]:
        """Deterministic dict used as the audit-log payload and the MCP envelope extension."""
        return {
            "egress_kind": self.egress_kind,
            "egress_replay_key": self.egress_replay_key,
            "principal_chain": self.principal_chain.to_dict(),
            "principal_chain_digest": self.principal_chain_digest,
            "request_digest": self.request_digest,
            "response_digest": self.response_digest,
            "target_id": self.target_id,
        }

    def to_mcp_envelope_extension(self) -> dict[str, object]:
        """MCP request-envelope extension shape (subset of to_dict).

        The full principal_chain is inlined so the remote MCP server can
        evaluate `allowed_principals` without an out-of-band lookup. The
        egress_replay_key is included so the server's audit log can
        cross-reference the caller's replay envelope.
        """
        return {
            "x_agentic_principal_chain": self.principal_chain.to_dict(),
            "x_agentic_principal_digest": self.principal_chain_digest,
            "x_agentic_egress_replay_key": self.egress_replay_key,
        }


def attach_principal_to_egress(
    *,
    egress_kind: EgressKind,
    target_id: str,
    request_digest: str,
    response_digest: str,
    principal_chain: PrincipalChain,
) -> PrincipalEgressEnvelope:
    """Factory: compute digest + replay key and return the egress envelope."""
    principal_digest = compute_principal_chain_digest(principal_chain)
    replay_key = compute_egress_replay_key(
        egress_kind=egress_kind,
        target_id=target_id,
        request_digest=request_digest,
        response_digest=response_digest,
        principal_chain=principal_chain,
    )
    return PrincipalEgressEnvelope(
        egress_kind=egress_kind,
        target_id=target_id,
        request_digest=request_digest,
        response_digest=response_digest,
        principal_chain=principal_chain,
        principal_chain_digest=principal_digest,
        egress_replay_key=replay_key,
    )


__all__ = [
    "EgressKind",
    "PrincipalEgressEnvelope",
    "attach_principal_to_egress",
    "compute_egress_replay_key",
]
