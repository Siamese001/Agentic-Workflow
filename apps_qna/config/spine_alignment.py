"""Cross-app spine alignment report — D4.3.

Compares apps_qna's spine_manifest.yaml claimed_routes against the
cross-app pattern registry to verify architectural alignment. The
registry maps route types to expected contract sets and known apps
that correctly implement that pattern.

This module is purely analytical — reads YAML from disk, returns a
typed AlignmentReport. No mutations, no external calls.

Known route types (from docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md):
  build_time_compiler   — zero canonical authority contracts (paste-pack)
  R3_grounded_read      — read-only retrieval (apps_rg pattern)
  R3_action             — read + deterministic action (no durable write)
  R4_SINGLE_ACTION      — full spine with UWG optional write
  R3R4_managed_workflow — full spine with required UWG durable write

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-deferred-e9c5b3.md D4.3
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


_APPS_QNA_MANIFEST = Path(__file__).parent.parent / "spine_manifest.yaml"

_KNOWN_ROUTE_TYPES: dict[str, dict[str, Any]] = {
    "build_time_compiler": {
        "description": "Zero canonical authority contracts; operator paste-pack",
        "required_contracts": [],
        "uwg_required": False,
        "known_apps": ["apps_qna", "apps_eval"],
    },
    "R3_grounded_read": {
        "description": "Read-only C0 grounded retrieval; no durable write",
        "required_contracts": ["L1PlanContract", "RouteContract", "FinalEvidenceContract"],
        "uwg_required": False,
        "known_apps": ["apps_rg", "apps_research"],
    },
    "R3_action": {
        "description": "Read + deterministic action; no UWG",
        "required_contracts": ["L1PlanContract", "RouteContract", "FinalEvidenceContract"],
        "uwg_required": False,
        "known_apps": ["apps_exec"],
    },
    "R4_SINGLE_ACTION": {
        "description": "Full spine; UWG optional durable write",
        "required_contracts": [
            "L1PlanContract",
            "RouteContract",
            "FinalEvidenceContract",
            "ExitReviewPacket",
        ],
        "uwg_required": False,
        "known_apps": ["apps_qna", "apps_underwriting_ai"],
    },
    "R3R4_managed_workflow": {
        "description": "Full spine; UWG durable write required",
        "required_contracts": [
            "L1PlanContract",
            "RouteContract",
            "FinalEvidenceContract",
            "ExitReviewPacket",
            "CommitRequest",
        ],
        "uwg_required": True,
        "known_apps": ["apps_lic"],
    },
}


@dataclass(frozen=True)
class ClaimedRoute:
    """A route declared in a spine_manifest.yaml."""

    route_type: str
    description: str = ""
    route_ids: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class RouteAlignmentEntry:
    """Alignment result for a single claimed route.

    Attributes:
        route_type: The route type string.
        known: True when route_type is in the cross-app registry.
        required_contracts: Contracts expected for this route type.
        uwg_required: Whether UWG is required for this route type.
        known_peer_apps: Other apps implementing the same pattern.
        notes: Notes from the manifest entry.
        warning: Non-empty when a potential misalignment is detected.
    """

    route_type: str
    known: bool = False
    required_contracts: tuple[str, ...] = ()
    uwg_required: bool = False
    known_peer_apps: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    warning: str = ""


@dataclass(frozen=True)
class AlignmentReport:
    """Cross-app spine alignment report for apps_qna.

    Attributes:
        app: The app being analysed.
        claimed_routes: Routes declared in spine_manifest.yaml.
        route_entries: Per-route alignment entries.
        unknown_route_types: Route types not in the cross-app registry.
        aligned: True when all routes are known and have no warnings.
        manifest_path: Path to the spine_manifest.yaml read.
    """

    app: str = ""
    claimed_routes: tuple[ClaimedRoute, ...] = ()
    route_entries: tuple[RouteAlignmentEntry, ...] = ()
    unknown_route_types: tuple[str, ...] = ()
    aligned: bool = False
    manifest_path: str = ""


def _load_manifest(path: Path) -> dict[str, Any]:
    """Load the spine_manifest.yaml. Returns {} on failure."""
    try:
        import yaml  # type: ignore[import]
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _parse_claimed_routes(manifest: dict[str, Any]) -> list[ClaimedRoute]:
    raw = manifest.get("claimed_routes") or []
    routes: list[ClaimedRoute] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        route_ids_raw = entry.get("route_ids") or []
        notes_raw = entry.get("notes") or []
        routes.append(ClaimedRoute(
            route_type=str(entry.get("type", "")),
            description=str(entry.get("description", "")),
            route_ids=tuple(str(r) for r in route_ids_raw),
            notes=tuple(str(n) for n in notes_raw),
        ))
    return routes


def check_spine_alignment(
    manifest_path: Path | None = None,
    app: str = "apps_qna",
    route_registry: dict[str, dict[str, Any]] | None = None,
) -> AlignmentReport:
    """Check apps_qna spine_manifest.yaml against the cross-app route registry.

    Args:
        manifest_path: Override path to spine_manifest.yaml.
        app: App name (used for peer-app filtering).
        route_registry: Override route type registry (for testing).

    Returns:
        AlignmentReport with per-route alignment entries.
    """
    target_path = manifest_path or _APPS_QNA_MANIFEST
    registry = route_registry or _KNOWN_ROUTE_TYPES
    manifest = _load_manifest(target_path)
    claimed_routes = _parse_claimed_routes(manifest)

    route_entries: list[RouteAlignmentEntry] = []
    unknown_types: list[str] = []

    for route in claimed_routes:
        rtype = route.route_type
        reg_entry = registry.get(rtype)
        if reg_entry is None:
            unknown_types.append(rtype)
            route_entries.append(RouteAlignmentEntry(
                route_type=rtype,
                known=False,
                notes=route.notes,
                warning=f"route_type '{rtype}' not in cross-app registry",
            ))
            continue

        peer_apps = tuple(
            a for a in (reg_entry.get("known_apps") or []) if a != app
        )
        required = tuple(reg_entry.get("required_contracts") or [])
        uwg_req = bool(reg_entry.get("uwg_required", False))

        warning = ""
        if uwg_req and "CommitRequest" not in required:
            warning = "uwg_required but CommitRequest not in required_contracts"

        route_entries.append(RouteAlignmentEntry(
            route_type=rtype,
            known=True,
            required_contracts=required,
            uwg_required=uwg_req,
            known_peer_apps=peer_apps,
            notes=route.notes,
            warning=warning,
        ))

    aligned = (
        not unknown_types
        and all(not e.warning for e in route_entries)
        and len(claimed_routes) > 0
    )

    return AlignmentReport(
        app=str(manifest.get("app", app)),
        claimed_routes=tuple(claimed_routes),
        route_entries=tuple(route_entries),
        unknown_route_types=tuple(unknown_types),
        aligned=aligned,
        manifest_path=str(target_path),
    )


def get_peer_apps_for_route(route_type: str) -> list[str]:
    """Return known peer apps implementing the given route type.

    Args:
        route_type: Route type string.

    Returns:
        Sorted list of peer app names.
    """
    entry = _KNOWN_ROUTE_TYPES.get(route_type, {})
    return sorted(entry.get("known_apps", []))


__all__ = [
    "AlignmentReport",
    "ClaimedRoute",
    "RouteAlignmentEntry",
    "check_spine_alignment",
    "get_peer_apps_for_route",
]
