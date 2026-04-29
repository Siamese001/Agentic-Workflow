"""Registry-bucket resolvers (W3) — emit ADG edges from declarative sources.

Per the three-bucket authority model, the **REGISTRY GRAPH** answers the
question "What is allowed?" — i.e. what configuration declares as wired,
authorized, or scoped. This module hosts resolvers that read declarative
sources (MCP server configs, agent spec catalogs, route-contract YAMLs)
and emit `bucket='registry'` edges into the unified ADG.

Every resolver returns a list of `RegistryEdge` records. The edges are
later inserted into the static snapshot's `edges` table by
`tools/adg/registry_bucket_lift.py`.

Resolution-status / authority-status mapping (per W1 closed enums):

    Source state                | resolution_status     | authority_status
    ----------------------------|-----------------------|------------------
    Stable + present + parsed   | STABLE_REGISTRY       | AUTHORITATIVE_REGISTRY
    Disabled (disabled=true)    | DISABLED_REGISTRY     | RISK_SIGNAL_ONLY
    Stale (digest mismatch)     | STALE_REGISTRY        | RISK_SIGNAL_ONLY
    Mismatched (schema invalid) | MISMATCHED_REGISTRY   | RISK_SIGNAL_ONLY
    Unresolved (lookup fail)    | UNRESOLVED_REGISTRY   | UNKNOWN_NOT_PROOF
    Missing (file not found)    | UNRESOLVED_REGISTRY   | UNKNOWN_NOT_PROOF

Doctrinal source: 2026-04-29 user directive — "Registry resolver (W3)".
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Closed enums for registry resolution
# ---------------------------------------------------------------------------

# Mirror agentic_core/adg/artifact/edge_authority.py REGISTRY_RESOLUTION_STATUSES.
RESOLUTION_STABLE: Final[str] = "STABLE_REGISTRY"
RESOLUTION_STALE: Final[str] = "STALE_REGISTRY"
RESOLUTION_MISMATCHED: Final[str] = "MISMATCHED_REGISTRY"
RESOLUTION_UNRESOLVED: Final[str] = "UNRESOLVED_REGISTRY"
RESOLUTION_DISABLED: Final[str] = "DISABLED_REGISTRY"

AUTHORITY_AUTHORITATIVE_REGISTRY: Final[str] = "AUTHORITATIVE_REGISTRY"
AUTHORITY_RISK_SIGNAL_ONLY: Final[str] = "RISK_SIGNAL_ONLY"
AUTHORITY_UNKNOWN_NOT_PROOF: Final[str] = "UNKNOWN_NOT_PROOF"


# ---------------------------------------------------------------------------
# Registry edge dataclass — what each resolver returns
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RegistryEdge:
    """One row's worth of registry-bucket evidence.

    Mirrors the ``edges`` table contract: src_name + dst_name resolve to
    node ids at lift time, and bucket/resolution_status/authority_status
    populate the new W1 columns.
    """

    src_name: str
    dst_name: str
    relation_type: str
    edge_kind: str
    source_file: str
    line_no: int = 0
    symbol: str = ""
    bucket: str = "registry"
    resolution_status: str = RESOLUTION_STABLE
    authority_status: str = AUTHORITY_AUTHORITATIVE_REGISTRY
    evidence_refs: dict[str, object] = field(default_factory=dict)

    def evidence_refs_json(self) -> str:
        return json.dumps(self.evidence_refs, sort_keys=True, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Common helpers
# ---------------------------------------------------------------------------


def _digest_json(blob: object) -> str:
    """Deterministic SHA-256 over a JSON-serializable blob.

    Used as the per-entry registry_digest for evidence_refs.
    """
    serialized = json.dumps(blob, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _classify_entry_status(*, present: bool, disabled: bool) -> tuple[str, str]:
    """Map source state → (resolution_status, authority_status)."""
    if not present:
        return (RESOLUTION_UNRESOLVED, AUTHORITY_UNKNOWN_NOT_PROOF)
    if disabled:
        return (RESOLUTION_DISABLED, AUTHORITY_RISK_SIGNAL_ONLY)
    return (RESOLUTION_STABLE, AUTHORITY_AUTHORITATIVE_REGISTRY)


def _rel_path(path: Path) -> str:
    """Best-effort POSIX-style relative path from ``REPO_ROOT``.

    Falls back to the path's basename when ``path`` lies outside the repo
    (e.g. test fixtures under ``tmp_path``). This keeps resolvers usable in
    isolated tests without leaking absolute filesystem paths into the
    persisted ``source_file`` column.
    """
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return path.name


# ---------------------------------------------------------------------------
# Resolver: MCP server registry  (.windsurf/mcp_config.json)
# ---------------------------------------------------------------------------


# Stable virtual root node — every MCP edge originates from here.
MCP_REGISTRY_ROOT: Final[str] = "Registry::MCP::root"


def resolve_mcp_config(config_path: Path | None = None) -> list[RegistryEdge]:
    """Resolve `.windsurf/mcp_config.json` into registry-bucket edges.

    Each `mcpServers` entry becomes one edge:

        Registry::MCP::root --MCP_SERVER_DECLARED--> Registry::MCP::<name>

    Disabled servers are emitted with resolution_status='DISABLED_REGISTRY'
    and authority_status='RISK_SIGNAL_ONLY' — they are declared but not
    permitted to run.

    Returns an empty list when the config file is missing or unparseable —
    a single ``UNRESOLVED_REGISTRY`` placeholder edge is NOT emitted because
    consumers should treat 'no MCP file' as 'no registry evidence', not as
    'one unresolved entry'.
    """
    if config_path is None:
        config_path = REPO_ROOT / ".windsurf" / "mcp_config.json"

    if not config_path.exists():
        return []

    try:
        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    servers = config.get("mcpServers", {})
    if not isinstance(servers, dict):
        return []

    edges: list[RegistryEdge] = []
    for name, server_config in servers.items():
        if not isinstance(server_config, dict):
            continue
        disabled = bool(server_config.get("disabled", False))
        digest = _digest_json(server_config)
        res_status, auth_status = _classify_entry_status(present=True, disabled=disabled)

        evidence = {
            "registry_path": _rel_path(config_path),
            "registry_digest": digest,
            "declaration_key": f"mcpServers.{name}",
            "disabled": disabled,
            "command": server_config.get("command", ""),
        }

        edges.append(
            RegistryEdge(
                src_name=MCP_REGISTRY_ROOT,
                dst_name=f"Registry::MCP::{name}",
                relation_type="MCP_SERVER_DECLARED",
                edge_kind="REGISTRY_DECLARATION",
                source_file=evidence["registry_path"],
                symbol=name,
                resolution_status=res_status,
                authority_status=auth_status,
                evidence_refs=evidence,
            )
        )

    return edges


# ---------------------------------------------------------------------------
# Resolver: Agent spec registries  (apps_*/config/agent_specs*.json)
# ---------------------------------------------------------------------------


AGENT_REGISTRY_ROOT: Final[str] = "Registry::Agent::root"


def resolve_agent_specs(spec_paths: list[Path] | None = None) -> list[RegistryEdge]:
    """Resolve every ``apps_*/config/agent_specs*.json`` into registry edges.

    Each top-level key in the JSON object is treated as one declared agent
    spec. The edge target name follows ``Registry::Agent::<app>::<spec_key>``
    so two apps can both declare e.g. `research_agent` without colliding.
    """
    if spec_paths is None:
        spec_paths = [
            *REPO_ROOT.glob("apps_*/config/agent_specs.json"),
            *REPO_ROOT.glob("apps_*/config/*_agent_specs.json"),
        ]

    edges: list[RegistryEdge] = []

    for path in spec_paths:
        if not path.exists():
            continue
        try:
            with path.open("r", encoding="utf-8") as f:
                spec = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(spec, dict):
            continue

        # Derive app prefix from the path (apps_lic / apps_rg / ...).
        try:
            app_prefix = path.relative_to(REPO_ROOT).parts[0]
        except ValueError:
            # Fixture path outside REPO_ROOT — use the grandparent dir name
            # if it looks like an app folder, otherwise the first parent.
            try:
                app_prefix = path.parent.parent.name or "unknown"
            except (AttributeError, IndexError):
                app_prefix = "unknown"

        rel_source = _rel_path(path)

        for spec_key, spec_value in spec.items():
            if not isinstance(spec_key, str):
                continue
            digest = _digest_json(spec_value)
            evidence = {
                "registry_path": rel_source,
                "registry_digest": digest,
                "declaration_key": spec_key,
                "app": app_prefix,
            }
            edges.append(
                RegistryEdge(
                    src_name=AGENT_REGISTRY_ROOT,
                    dst_name=f"Registry::Agent::{app_prefix}::{spec_key}",
                    relation_type="AGENT_SPEC_DECLARED",
                    edge_kind="REGISTRY_DECLARATION",
                    source_file=rel_source,
                    symbol=spec_key,
                    resolution_status=RESOLUTION_STABLE,
                    authority_status=AUTHORITY_AUTHORITATIVE_REGISTRY,
                    evidence_refs=evidence,
                )
            )

    return edges


# ---------------------------------------------------------------------------
# Aggregate registry digest (ties an SSOTDecisionRecord to a snapshot)
# ---------------------------------------------------------------------------


def compute_registry_digest_set(edges: list[RegistryEdge]) -> list[str]:
    """Build the canonical ``registry_digest_set`` for SSOTDecisionRecord.

    The set is the sorted list of unique per-entry registry_digests from
    the supplied edges. SSOT records pin their reconciliation to this set
    so a registry change between two runs produces a different
    ``manifest_hash``.
    """
    digests = {
        str(e.evidence_refs.get("registry_digest", ""))
        for e in edges
        if e.evidence_refs.get("registry_digest")
    }
    return sorted(digests)


def resolve_all_registries() -> list[RegistryEdge]:
    """Convenience: run every registered resolver and concatenate.

    Used by the CLI lift (`tools/adg/registry_bucket_lift.py`) and tests.
    """
    return [
        *resolve_mcp_config(),
        *resolve_agent_specs(),
    ]
