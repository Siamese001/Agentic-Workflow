"""Registry consumer-edge resolver — emit edges from real code modules to
registry-anchor nodes (W1.future of plan three-bucket-gap-remediation-069806).

The base registry resolvers (`registry_resolvers.py::resolve_*`) emit
ANCHOR-only edges:

    Registry::MCP::root        --MCP_SERVER_DECLARED-->  Registry::MCP::<name>
    Registry::Agent::root      --AGENT_SPEC_DECLARED-->  Registry::Agent::<app>::<spec>
    Registry::RouteContract::root --ROUTE_CONTRACT_DECLARED--> ...

These show "what the registry declares exists" — a closed top-down picture,
but they have ZERO overlap with code edges, so every static edge classifies
as REGISTRY_DRIFT.

The CONSUMER resolver in this module emits the OTHER half of each registry
relationship: code modules that physically reference the declared name.

For each registry source we mine a name-to-consumers index by AST/grep,
then emit BOTH a `bucket='static'` edge AND a `bucket='registry'` edge for
every (consumer_module, registry_anchor, relation_type) triple. That gives
the gap classifier the SAME (src, dst, rel) tuple in two buckets, so when
the runtime view also attests it, the row classifies as TRIPLET_ATTESTED.

Three resolvers ship in this module:

  * resolve_mcp_consumer_edges() — code that references MCP server names
  * resolve_agent_spec_consumer_edges() — code that loads agent_specs.json
  * resolve_route_contract_consumer_edges() — code that loads policy packs

Each returns a list of `ConsumerEdge` records. The lift script writes them
in pairs (static + registry) so the gap classifier sees them in both buckets.

Plan: ``docs/archive/windsurf/legacy-tree/plans/three-bucket-gap-remediation-069806.md`` (W1.future).
"""

from __future__ import annotations

# Reads source files via AST/grep for consumer detection.
__adg_consumer_mode__ = "inventory"

import json
import os
import re
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Final

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.registry.registry_resolvers import (  # noqa: E402
    AGENT_REGISTRY_ROOT,
    AUTHORITY_AUTHORITATIVE_REGISTRY,
    MCP_REGISTRY_ROOT,
    RESOLUTION_STABLE,
    RegistryEdge,
)


@dataclass(frozen=True)
class ConsumerEdge:
    """A static-AST consumer edge that mirrors a registry-anchor relationship.

    Each ConsumerEdge represents "this real Python module references a
    name that the registry declares". The lift then writes TWO rows for
    each ConsumerEdge:

      1. bucket='static' / authority='static_canonical' — code referenced it
      2. bucket='registry' / authority='registry_declared' — registry allowed it

    This is the canonical pattern from the gap-classifier doctrine: an edge
    triple with multiple bucket attestations classifies as TRIPLET when the
    runtime bucket also fires.
    """

    consumer_file: str
    consumer_module: str  # ADG::Module::<path> form
    registry_anchor: str  # ADG::Symbol::Registry::* form
    relation_type: str
    line_no: int = 0
    evidence: dict[str, object] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _module_adg_name(rel_path: str) -> str:
    """Convert a repo-relative path to ADG module-name form."""
    return f"ADG::Module::{rel_path}"


def _scan_files(root: Path, pattern: str, exts: tuple[str, ...] = (".py",)) -> dict[str, list[int]]:
    """Return {rel_path: [line_no, ...]} for every file under root that
    matches `pattern` (regex). Skips test / archive / venv directories.
    """
    skip_parts = {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "_archived",
        "archives",
        "lib",
        "lib64",
        "node_modules",
        "site-packages",
        "tests",
        "venv",
        "worktrees",
    }
    rx = re.compile(pattern)
    results: dict[str, list[int]] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_parts]
        current = Path(dirpath)
        if any(part in skip_parts for part in current.parts):
            continue
        for filename in filenames:
            p = current / filename
            if p.suffix not in exts:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            hits: list[int] = []
            for line_no, line in enumerate(text.splitlines(), start=1):
                if rx.search(line):
                    hits.append(line_no)
            if hits:
                try:
                    rel = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
                except ValueError:
                    rel = p.name
                results[rel] = hits
    return results


# ---------------------------------------------------------------------------
# Resolver: MCP consumer edges
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def resolve_mcp_consumer_edges() -> list[ConsumerEdge]:
    """Mine code that references MCP server names declared in mcp_config.json.

    Detection heuristic: any source line that contains either:
      * a literal MCP server name from the registry (matched as a quoted
        string token), OR
      * the string ``mcp_config.json`` itself (broad consumer signal)

    A consumer-edge is emitted from the consuming module to the
    `Registry::MCP::<name>` anchor when the literal name match fires.
    Files that load the full `mcp_config.json` get one edge per declared
    server (the consumer doesn't statically pin a single server name, but
    it has read access to the entire registry).
    """
    config_path = REPO_ROOT / ".mcp.json"
    if not config_path.exists():
        return []
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    server_names = sorted((config.get("mcpServers") or {}).keys())
    if not server_names:
        return []

    edges: list[ConsumerEdge] = []
    seen: set[tuple[str, str]] = set()

    # 1) Per-server name match — narrow consumers (most signal).
    for name in server_names:
        # Match the name only when it's a quoted-string literal — reduces
        # false positives from comments / partial substring matches.
        # Also require the name to be at least 4 chars to skip false hits
        # like 'redis' showing up in unrelated docs.
        if len(name) < 4:
            continue
        pattern = re.escape(f'"{name}"') + r"|" + re.escape(f"'{name}'")
        hits = _scan_files(REPO_ROOT, pattern)
        anchor = f"Registry::MCP::{name}"
        for rel_path, line_nos in hits.items():
            if rel_path == ".mcp.json":
                continue  # the registry source itself is not a consumer
            consumer_module = _module_adg_name(rel_path)
            key = (consumer_module, anchor)
            if key in seen:
                continue
            seen.add(key)
            edges.append(
                ConsumerEdge(
                    consumer_file=rel_path,
                    consumer_module=consumer_module,
                    registry_anchor=anchor,
                    relation_type="references_mcp_server",
                    line_no=line_nos[0],
                    evidence={
                        "mcp_server": name,
                        "first_match_line": line_nos[0],
                        "match_count": len(line_nos),
                    },
                )
            )

    return edges


# ---------------------------------------------------------------------------
# Resolver: Agent-spec consumer edges
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def resolve_agent_spec_consumer_edges() -> list[ConsumerEdge]:
    """Mine code that loads or references agent_specs.json keys.

    Two detection heuristics, restricted to .py files under apps_*/ to
    bound search cost and false positives:

    1. Quoted-string match — ``"<spec_key>"`` or ``'<spec_key>'``
       (covers ``load_spec("clerk_extraction")``-style consumption).
    2. Bare-identifier-with-safe-context match — ``\\b<spec_key>\\b``
       followed by one of ``: = (`` (TypedDict field, assignment, or
       call). This catches the apps_lic/apps_rg pattern where spec keys
       appear as Python attribute names in TypedDict-like declarations
       (``sender_grounding_agent: SenderGroundingConfig``).

    Spec keys shorter than 6 characters are skipped to avoid colliding
    with common identifiers. The legacy ``"_agent" not in spec_key``
    filter was removed (post-W7 remediation) — apps_rg-style keys like
    ``clerk_extraction`` are now also detected, closing the
    ``cross_bucket.impossible_states`` I6 gap for app-side specs.
    """
    spec_paths = list(REPO_ROOT.glob("apps_*/config/agent_specs.json")) + list(
        REPO_ROOT.glob("apps_*/config/*_agent_specs.json")
    )

    edges: list[ConsumerEdge] = []
    seen: set[tuple[str, str]] = set()

    for path in spec_paths:
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(spec, dict):
            continue
        try:
            app_prefix = path.relative_to(REPO_ROOT).parts[0]
        except ValueError:
            app_prefix = "unknown"

        for spec_key in spec.keys():
            # Bare-identifier matching is collision-prone for short keys
            # (e.g. "spec", "agent"); enforce a 6-char floor.
            if not isinstance(spec_key, str) or len(spec_key) < 6:
                continue

            quoted = re.escape(f'"{spec_key}"') + r"|" + re.escape(f"'{spec_key}'")
            # Bare identifier followed by one of the safe-context tokens
            # — TypedDict field (``: ``), assignment (``=``), or call
            # (``(``). These are syntactic shapes that strongly indicate
            # the bare name is being USED, not a string literal mention.
            bare_with_ctx = (
                r"\b" + re.escape(spec_key) + r"\b\s*[:=(]"
            )
            pattern = f"{quoted}|{bare_with_ctx}"
            hits = _scan_files(REPO_ROOT, pattern)
            anchor = f"Registry::Agent::{app_prefix}::{spec_key}"
            for rel_path, line_nos in hits.items():
                if rel_path.endswith("agent_specs.json") or rel_path.endswith(
                    "agent_specs"
                ):
                    continue  # registry source itself
                # Restrict to the SAME app as the spec source (apps_lic
                # specs only count when consumed under apps_lic/...).
                # This bounds false positives across apps.
                if not rel_path.startswith(f"{app_prefix}/"):
                    continue
                consumer_module = _module_adg_name(rel_path)
                key = (consumer_module, anchor)
                if key in seen:
                    continue
                seen.add(key)
                edges.append(
                    ConsumerEdge(
                        consumer_file=rel_path,
                        consumer_module=consumer_module,
                        registry_anchor=anchor,
                        relation_type="references_agent_spec",
                        line_no=line_nos[0],
                        evidence={
                            "spec_key": spec_key,
                            "app": app_prefix,
                            "first_match_line": line_nos[0],
                            "match_count": len(line_nos),
                        },
                    )
                )

    return edges


@lru_cache(maxsize=1)
def resolve_route_contract_consumer_edges() -> list[ConsumerEdge]:
    """Mine code that references route-contract identifiers declared in
    ``agentic_core/L0_routing/config/v15_policy_pack.json`` (or successors).

    Detection heuristic: quoted-string match for each top-level route-id
    key. Route IDs are upper_snake_case and bounded in length; bare-
    identifier matching is intentionally NOT enabled here because route
    IDs are too short to safely match without context, and the policy
    pack itself contains the canonical declarations.

    Closes the ROUTE_CONTRACT side of cross-bucket impossible-states I6.
    """
    pack_paths = list(
        REPO_ROOT.glob("agentic_core/L0_routing/config/*_policy_pack.json")
    )
    edges: list[ConsumerEdge] = []
    seen: set[tuple[str, str]] = set()

    for path in pack_paths:
        try:
            pack = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(pack, dict):
            continue

        # Route IDs may live under a top-level "routes" or "contracts" key,
        # or directly. Tolerate both shapes.
        candidate_dicts = [pack]
        for key in ("routes", "contracts", "route_contracts"):
            sub = pack.get(key)
            if isinstance(sub, dict):
                candidate_dicts.append(sub)

        route_ids: set[str] = set()
        for d in candidate_dicts:
            for k in d.keys():
                if isinstance(k, str) and k.isupper() and "_" in k and len(k) >= 8:
                    route_ids.add(k)

        for route_id in route_ids:
            pattern = re.escape(f'"{route_id}"') + r"|" + re.escape(f"'{route_id}'")
            hits = _scan_files(REPO_ROOT, pattern)
            anchor = f"Registry::RouteContract::{route_id}"
            for rel_path, line_nos in hits.items():
                if rel_path.endswith(".json"):
                    continue  # registry source itself
                consumer_module = _module_adg_name(rel_path)
                key = (consumer_module, anchor)
                if key in seen:
                    continue
                seen.add(key)
                edges.append(
                    ConsumerEdge(
                        consumer_file=rel_path,
                        consumer_module=consumer_module,
                        registry_anchor=anchor,
                        relation_type="references_route_contract",
                        line_no=line_nos[0],
                        evidence={
                            "route_id": route_id,
                            "first_match_line": line_nos[0],
                            "match_count": len(line_nos),
                        },
                    )
                )

    return edges


# ---------------------------------------------------------------------------
# Aggregator
# ---------------------------------------------------------------------------


def resolve_all_consumer_edges() -> list[ConsumerEdge]:
    """Run every consumer resolver and concat results."""
    return [
        *resolve_mcp_consumer_edges(),
        *resolve_agent_spec_consumer_edges(),
        *resolve_route_contract_consumer_edges(),
    ]


# ---------------------------------------------------------------------------
# Convert ConsumerEdge -> two RegistryEdge rows (static + registry buckets)
# ---------------------------------------------------------------------------


def consumer_edge_to_registry_edges(c: ConsumerEdge) -> list[RegistryEdge]:
    """Materialize a ConsumerEdge as TWO RegistryEdges that the lift will
    write into the canonical edges table.

    The first (bucket='static') represents "code has this reference"; the
    second (bucket='registry') represents "registry sanctions this binding".
    Both share the same (src_name, dst_name, relation_type), so the gap
    classifier sees them as one logical edge with two bucket attestations.
    """
    base = RegistryEdge(
        src_name=c.consumer_module,
        dst_name=c.registry_anchor,
        relation_type=c.relation_type,
        edge_kind="REGISTRY_CONSUMER",
        source_file=c.consumer_file,
        line_no=c.line_no,
        symbol="",
        bucket="registry",
        resolution_status=RESOLUTION_STABLE,
        authority_status=AUTHORITY_AUTHORITATIVE_REGISTRY,
        evidence_refs=dict(c.evidence),
    )
    # Static-bucket twin — same endpoints, different bucket. The lift
    # writes both twins with authority='verified' (in-enum SSOT label
    # per agentic_core/adg/artifact/edge_authority.py:ALL_AUTHORITIES);
    # the bucket field is the discriminator between code-side and
    # registry-side membership.
    static_twin = RegistryEdge(
        src_name=c.consumer_module,
        dst_name=c.registry_anchor,
        relation_type=c.relation_type,
        edge_kind="REGISTRY_CONSUMER",
        source_file=c.consumer_file,
        line_no=c.line_no,
        symbol="",
        bucket="static",
        resolution_status="VERIFIED_MODULE",  # static reference verified by file scan
        authority_status="AUTHORITATIVE",
        evidence_refs={**dict(c.evidence), "twin_bucket": "registry"},
    )
    return [static_twin, base]
