"""ADG Graph Persister -- writes ScanResult into Memory MCP via ADGMCPClient.

Persists:
- ADG::Commit::<sha> entity
- ADG::Snapshot::<sha>::<digest> entity
- ADG::Module::<path> entities
- ADG::Symbol::<qualified> entities
- ADG::Layer::L0..L6 entities
- All edges as relations
- Observations on each node (commit, digest, path, line_no, edge_kind, etc.)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from agentic_core.adg.client.mcp_client import ADGMCPClient
from agentic_core.adg.schema import (
    GATEWAY_ALLOWLIST,
    canonical_name,
    module_path_to_layer,
)

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

logger = logging.getLogger(__name__)

_LAYER_LABELS = (
    "L0",
    "L1",
    "L2",
    "L3",
    "L4",
    "L5",
    "L6",
    "L_APP",
    "L_SL",
    "L_TOOLS",
    "L_OPS",
    "L_UNKNOWN",
)


def persist_scan_result(result: ScanResult, client: ADGMCPClient) -> None:
    """Persist a full ScanResult into the ADG graph via client.

    All writes are commit-scoped and snapshot-scoped.
    Idempotent: safe to call multiple times with the same result.
    """
    scan_time = datetime.now(timezone.utc).isoformat()

    _ensure_layer_nodes(client)
    _ensure_gateway_nodes(client)

    if result.commit_sha:
        commit_node = canonical_name("Commit", result.commit_sha)
        client.upsert_entity(
            commit_node,
            "commit",
            [f"commit:{result.commit_sha}", f"scan_time:{scan_time}"],
        )

    snapshot_node: str | None = None
    if result.commit_sha and result.digest:
        snapshot_node = canonical_name("Snapshot", result.commit_sha, result.digest)
        client.upsert_entity(
            snapshot_node,
            "snapshot",
            [
                f"commit:{result.commit_sha}",
                f"snapshot_digest:{result.digest}",
                f"scan_time:{scan_time}",
            ],
        )

    _persist_modules(result, client, result.commit_sha, scan_time)
    _persist_edges(result, client, snapshot_node)


def _ensure_layer_nodes(client: ADGMCPClient) -> None:
    for label in _LAYER_LABELS:
        node = canonical_name("Layer", label)
        client.upsert_entity(node, "layer", [f"layer_label:{label}"])


def _ensure_gateway_nodes(client: ADGMCPClient) -> None:
    for gw_name, gw_path in GATEWAY_ALLOWLIST.items():
        node = canonical_name("Gateway", gw_name)
        client.upsert_entity(
            node,
            "gateway",
            [f"path:{gw_path}", f"gateway_name:{gw_name}"],
        )
        module_node = canonical_name("Module", gw_path)
        client.upsert_entity(module_node, "module", [f"path:{gw_path}"])
        layer_label = module_path_to_layer(gw_path)
        layer_node = canonical_name("Layer", layer_label)
        client.upsert_relation(module_node, "belongs_to_layer", layer_node)
        client.upsert_relation(module_node, "implements", node)


def _persist_modules(
    result: ScanResult,
    client: ADGMCPClient,
    commit_sha: str,
    scan_time: str,
) -> None:
    for rel in result.modules:
        module_node = canonical_name("Module", rel)
        layer_label = module_path_to_layer(rel)
        obs = [f"path:{rel}", f"scan_time:{scan_time}"]
        if commit_sha:
            obs.append(f"commit:{commit_sha}")
        client.upsert_entity(module_node, "module", obs)
        layer_node = canonical_name("Layer", layer_label)
        client.upsert_relation(module_node, "belongs_to_layer", layer_node)


def _persist_edges(
    result: ScanResult,
    client: ADGMCPClient,
    snapshot_node: str | None,
) -> None:
    symbol_obs_map: dict[str, list[str]] = {}

    for edge in result.edges:
        client.upsert_relation(edge.from_name, edge.relation_type, edge.to_name)

        sym_node = edge.to_name
        if sym_node not in symbol_obs_map:
            symbol_obs_map[sym_node] = []

        obs_list = [
            f"edge_kind:{edge.edge_kind}",
            f"symbol:{edge.symbol}",
            f"source_file:{edge.source_file}",
            f"line_no:{edge.line_no}",
        ]
        # G16: attach structured rule_id to violation/bypass edges
        rule_id = _derive_rule_id(edge.relation_type, edge.symbol)
        if rule_id:
            obs_list.append(f"rule_id:{rule_id}")

        for obs in obs_list:
            if obs not in symbol_obs_map[sym_node]:
                symbol_obs_map[sym_node].append(obs)

    for sym_node, obs_list in sorted(symbol_obs_map.items()):
        entity_type = _infer_entity_type(sym_node)
        client.upsert_entity(sym_node, entity_type, sorted(obs_list))

    if snapshot_node:
        client.add_observation(snapshot_node, [f"edge_count:{len(result.edges)}"])


_RULE_TYPE_MAP: dict[str, str] = {
    "violates": "LAYER_GRAVITY",
    "bypasses_uwg": "UWG_BYPASS",
    "seam_bypass": "SEAM_BYPASS",
}


def _derive_rule_id(relation_type: str, symbol: str) -> str:
    """G16: Return structured rule_id for violation/bypass edges, else empty string."""
    prefix = _RULE_TYPE_MAP.get(relation_type, "")
    if not prefix:
        return ""
    if symbol:
        return f"{prefix}:{symbol}"
    return prefix


def _infer_entity_type(adg_name: str) -> str:
    parts = adg_name.split("::")
    if len(parts) >= 2:
        t = parts[1].lower()
        # G2: map canonical ADG prefix to entity_type
        _prefix_to_type: dict[str, str] = {
            "symbol": "symbol",
            "module": "module",
            "gateway": "gateway",
            "layer": "layer",
            "seam": "seam",
            "provider": "provider",
            "promptslot": "prompt_slot",
            "prompttemplate": "prompt_template",
        }
        if t in _prefix_to_type:
            return _prefix_to_type[t]
    return "symbol"


__all__ = ["persist_scan_result"]
