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
# Resolver: MCP server registry  (.cursor/mcp.json)
# ---------------------------------------------------------------------------


# Stable virtual root node — every MCP edge originates from here.
MCP_REGISTRY_ROOT: Final[str] = "Registry::MCP::root"


def resolve_mcp_config(config_path: Path | None = None) -> list[RegistryEdge]:
    """Resolve `.cursor/mcp.json` into registry-bucket edges.

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
        config_path = REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "mcp_config.json"

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
# Resolver: Route-contract policy pack  (agentic_core/L0_routing/config/v15_policy_pack.json)
# ---------------------------------------------------------------------------
# Plan: docs/archive/windsurf/legacy-tree/plans/three-bucket-otel-view-5db409.md (W5).
#
# The route-contract surface declared in `route_contract_v15.py` is realized
# at runtime by the v15 policy pack. Each rule entry in the JSON is a
# declarative gate that the pipeline MUST honor — registry-bucket evidence
# in its purest form.
#
# Prompt-slot resolver: DEFERRED. There is no canonical prompt-slot
# registry file at this time (slots are resolved at runtime via
# `agentic_core/prompt_governance/`). When/if a declarative slot manifest
# lands, this is the natural sibling resolver.


ROUTE_CONTRACT_REGISTRY_ROOT: Final[str] = "Registry::RouteContract::root"
DEFAULT_V15_POLICY_PACK: Final[Path] = (
    REPO_ROOT / "agentic_core" / "L0_routing" / "config" / "v15_policy_pack.json"
)


def resolve_route_contracts(
    policy_pack_path: Path | None = None,
) -> list[RegistryEdge]:
    """Resolve the v15 route-contract policy pack into registry-bucket edges.

    Each rule in the policy pack becomes one edge::

        Registry::RouteContract::root --ROUTE_CONTRACT_DECLARED--> Registry::RouteContract::<rule_id>

    Disabled rules (``enabled: false``) are emitted with
    ``resolution_status='DISABLED_REGISTRY'`` and
    ``authority_status='RISK_SIGNAL_ONLY'`` — they are declared but not
    permitted to fire. Missing or unparseable policy pack returns ``[]``
    consistent with the resolver convention from W3.

    Returns
    -------
    list[RegistryEdge]
        One edge per rule. Empty list when policy pack is missing /
        unparseable / has no ``rules`` array.
    """
    if policy_pack_path is None:
        policy_pack_path = DEFAULT_V15_POLICY_PACK

    if not policy_pack_path.exists():
        return []

    try:
        with policy_pack_path.open("r", encoding="utf-8") as f:
            pack = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    rules = pack.get("rules", [])
    if not isinstance(rules, list):
        return []

    rel_source = _rel_path(policy_pack_path)
    pack_version = str(pack.get("version", ""))

    edges: list[RegistryEdge] = []
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rule_id = rule.get("rule_id")
        if not isinstance(rule_id, str) or not rule_id:
            continue

        enabled = bool(rule.get("enabled", True))
        digest = _digest_json(rule)
        res_status, auth_status = _classify_entry_status(
            present=True, disabled=not enabled
        )

        evidence = {
            "registry_path": rel_source,
            "registry_digest": digest,
            "declaration_key": f"rules.{rule_id}",
            "applies_to": rule.get("applies_to", ""),
            "severity": rule.get("severity", ""),
            "policy_pack_version": pack_version,
            "enabled": enabled,
        }

        edges.append(
            RegistryEdge(
                src_name=ROUTE_CONTRACT_REGISTRY_ROOT,
                dst_name=f"Registry::RouteContract::{rule_id}",
                relation_type="ROUTE_CONTRACT_DECLARED",
                edge_kind="REGISTRY_DECLARATION",
                source_file=rel_source,
                symbol=rule_id,
                resolution_status=res_status,
                authority_status=auth_status,
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


PROMPT_SLOT_REGISTRY_ROOT: Final[str] = "Registry::PromptSlot::root"
DEFAULT_PROMPT_REGISTRY: Final[Path] = (
    REPO_ROOT / "agentic_core" / "prompt_governance" / "registry"
    / "prompt_registry_config.json"
)


def resolve_prompt_slots(
    registry_path: Path | None = None,
) -> list[RegistryEdge]:
    """Resolve the canonical prompt-slot registry into registry-bucket edges.

    Reads ``agentic_core/prompt_governance/registry/prompt_registry_config.json``
    (the SSOT for all registered Jinja prompt templates) and emits one edge
    per (slot, version) pair::

        Registry::PromptSlot::root --PROMPT_SLOT_DECLARED--> Registry::PromptSlot::<slot>::<version>

    The registry is keyed by template filename (e.g. ``file_placement.jinja``)
    with a list of versioned entries. Each entry has ``version``, ``purpose``,
    ``territory``, ``active``, ``author``, ``registered_date``. Inactive slots
    (``active: false``) are emitted with ``resolution_status='DISABLED_REGISTRY'``
    and ``authority_status='RISK_SIGNAL_ONLY'`` — registered but not in use,
    same convention as disabled route-contract rules in ``resolve_route_contracts``.

    Closes the W11.1 / P5.2 deferred scope from
    ``docs/archive/windsurf/legacy-tree/plans/three-bucket-otel-view-5db409.md`` once
    ``prompt_registry_config.json`` was confirmed as the canonical manifest.

    Returns
    -------
    list[RegistryEdge]
        One edge per (slot_name, version) pair. Empty list when the registry
        file is missing / unparseable / has no ``prompts`` mapping.
    """
    if registry_path is None:
        registry_path = DEFAULT_PROMPT_REGISTRY

    if not registry_path.exists():
        return []

    try:
        with registry_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    prompts = data.get("prompts", {})
    if not isinstance(prompts, dict):
        return []

    rel_source = _rel_path(registry_path)
    sovereign_version = str(data.get("sovereign_version", ""))

    edges: list[RegistryEdge] = []
    for slot_name, versions in sorted(prompts.items()):
        if not isinstance(slot_name, str) or not slot_name:
            continue
        if not isinstance(versions, list):
            continue
        for entry in versions:
            if not isinstance(entry, dict):
                continue
            version = entry.get("version")
            if not isinstance(version, str) or not version:
                continue

            active = bool(entry.get("active", True))
            digest = _digest_json({"slot": slot_name, **entry})
            res_status, auth_status = _classify_entry_status(
                present=True, disabled=not active,
            )

            evidence = {
                "registry_path": rel_source,
                "registry_digest": digest,
                "declaration_key": f"prompts.{slot_name}.{version}",
                "purpose": entry.get("purpose", ""),
                "territory": entry.get("territory", ""),
                "author": entry.get("author", ""),
                "registered_date": entry.get("registered_date", ""),
                "sovereign_version": sovereign_version,
                "active": active,
            }

            edges.append(
                RegistryEdge(
                    src_name=PROMPT_SLOT_REGISTRY_ROOT,
                    dst_name=f"Registry::PromptSlot::{slot_name}::{version}",
                    relation_type="PROMPT_SLOT_DECLARED",
                    edge_kind="REGISTRY_DECLARATION",
                    source_file=rel_source,
                    symbol=f"{slot_name}@{version}",
                    resolution_status=res_status,
                    authority_status=auth_status,
                    evidence_refs=evidence,
                )
            )

    return edges


def resolve_all_registries() -> list[RegistryEdge]:
    """Convenience: run every registered resolver and concatenate.

    Used by the CLI lift (`tools/adg/registry_bucket_lift.py`) and tests.
    """
    return [
        *resolve_mcp_config(),
        *resolve_agent_specs(),
        *resolve_route_contracts(),
        *resolve_prompt_slots(),
    ]
