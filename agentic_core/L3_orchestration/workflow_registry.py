"""Workflow registry resolver — W4.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W4
Purpose: Resolve a managed-workflow route entry from an apps_rg-style
route_registry.yaml into a WorkflowResolutionReceipt that L0 can attach
to RouteContract.

Scope constraints (non-negotiable):
  - This module does NOT execute workflows.
  - This module does NOT call L2, L3 runners, or any provider.
  - This module does NOT write to L4.
  - This module does NOT import apps_rg.integrations.hops or gates.
  - Registry is read from disk on demand; no singleton state.
  - Resolution is fail-closed on every error path.

resolution_status values:
  RESOLVED         — one active (or test-enabled) MANAGED_WORKFLOW route found,
                     workflow_manifest_ref non-empty.
  DISABLED         — route found but status=registered_not_active and not
                     test-enabled; production default.
  ZERO_MATCH       — no MANAGED_WORKFLOW routes in registry.
  MULTIPLE_MATCH   — more than one MANAGED_WORKFLOW route; ambiguous.
  DIGEST_MISMATCH  — manifest file digest does not match expected digest.
  INVALID          — any other structural / parse / missing-ref failure.
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

_log = logging.getLogger(__name__)

# Status constants ──────────────────────────────────────────────────────────
RESOLVED = "RESOLVED"
DISABLED = "DISABLED"
ZERO_MATCH = "ZERO_MATCH"
MULTIPLE_MATCH = "MULTIPLE_MATCH"
DIGEST_MISMATCH = "DIGEST_MISMATCH"
INVALID = "INVALID"

_MANAGED_WORKFLOW_FORM = "MANAGED_WORKFLOW"
_STATUS_NOT_ACTIVE = "registered_not_active"


# ── Public exceptions ────────────────────────────────────────────────────────

class WorkflowRegistryResolutionError(Exception):
    """Raised by resolve_managed_workflow_route on any fail-closed path."""

    def __init__(self, resolution_status: str, decisive_reason: str) -> None:
        self.resolution_status = resolution_status
        self.decisive_reason = decisive_reason
        super().__init__(
            f"WorkflowRegistryResolutionError: status={resolution_status} "
            f"reason={decisive_reason!r}"
        )


# ── Receipt dataclass ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class WorkflowResolutionReceipt:
    """Result of resolving a managed-workflow route from route_registry.yaml.

    Populated by resolve_managed_workflow_route() and attached to RouteContract
    as registry_resolution_receipt_ref (serialised JSON).

    Immutable — frozen dataclass.
    """

    route_id: str
    workflow_ref: str                  # canonical workflow ID string
    workflow_manifest_ref: str         # e.g. "wfm::apps_rg::resume_generation::v1"
    workflow_manifest_path: str        # repo-relative path to manifest YAML
    manifest_digest: str               # sha256 hex of manifest bytes, or "" if not available
    route_registry_ref: str            # repo-relative path to the registry YAML
    route_status: str                  # e.g. "registered_not_active"
    l3_required: bool
    execution_form: str                # always "MANAGED_WORKFLOW" on RESOLVED
    resolution_status: str             # RESOLVED | DISABLED | … (see module docstring)
    decisive_reason: str               # short human-readable explanation
    test_activated: bool               # True iff APPS_RG_MANAGED_WORKFLOW_TEST_ENABLED was set

    def as_json(self) -> str:
        """Serialize to compact JSON for RouteContract.registry_resolution_receipt_ref."""
        return json.dumps(
            {
                "route_id": self.route_id,
                "workflow_ref": self.workflow_ref,
                "workflow_manifest_ref": self.workflow_manifest_ref,
                "workflow_manifest_path": self.workflow_manifest_path,
                "manifest_digest": self.manifest_digest,
                "route_registry_ref": self.route_registry_ref,
                "route_status": self.route_status,
                "l3_required": self.l3_required,
                "execution_form": self.execution_form,
                "resolution_status": self.resolution_status,
                "decisive_reason": self.decisive_reason,
                "test_activated": self.test_activated,
            },
            separators=(",", ":"),
        )

    @classmethod
    def from_json(cls, raw: str) -> "WorkflowResolutionReceipt":
        d = json.loads(raw)
        return cls(
            route_id=d["route_id"],
            workflow_ref=d["workflow_ref"],
            workflow_manifest_ref=d["workflow_manifest_ref"],
            workflow_manifest_path=d.get("workflow_manifest_path", ""),
            manifest_digest=d.get("manifest_digest", ""),
            route_registry_ref=d.get("route_registry_ref", ""),
            route_status=d.get("route_status", ""),
            l3_required=bool(d.get("l3_required", True)),
            execution_form=d.get("execution_form", _MANAGED_WORKFLOW_FORM),
            resolution_status=d["resolution_status"],
            decisive_reason=d.get("decisive_reason", ""),
            test_activated=bool(d.get("test_activated", False)),
        )


# ── Internal helpers ─────────────────────────────────────────────────────────

def _resolve_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def _compute_digest(path: Path) -> str:
    """Return sha256 hex digest of *path* bytes, or '' on failure."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _load_route_registry(registry_path: Path) -> List[Dict[str, Any]]:
    """Load routes list from YAML route_registry.  Returns [] on failure."""
    try:
        import yaml  # type: ignore[import-untyped]
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
        routes = data.get("routes", [])
        if not isinstance(routes, list):
            return []
        return [r for r in routes if isinstance(r, dict)]
    except Exception as exc:  # guardian: allow-broad-exception -- P1 ADG burndown
        _log.warning("[workflow_registry] Failed to parse %s: %s", registry_path, exc)
        return []


def _is_test_activated(env_override: Optional[str]) -> bool:
    """Return True iff test activation is in effect.

    env_override: explicit string value passed by the caller.  When None,
    test activation is inactive (the caller is responsible for reading the
    app-specific env flag and passing it here).
    """
    if env_override is not None:
        return env_override in ("1", "true", "yes")
    return False


# ── Public resolver ──────────────────────────────────────────────────────────

def resolve_managed_workflow_route(
    registry_relpath: str,
    *,
    repo_root: Optional[Path] = None,
    expected_manifest_digest: str = "",
    _test_activation_env_override: Optional[str] = None,
) -> WorkflowResolutionReceipt:
    """Resolve the apps_rg managed workflow route entry.

    Args:
        registry_relpath: repo-relative path to the route_registry.yaml.
        repo_root: override repo root (test injection; auto-detected otherwise).
        expected_manifest_digest: if non-empty, verify the resolved manifest
            file's sha256 digest matches this value.  Mismatch → DIGEST_MISMATCH.
        _test_activation_env_override: inject test activation flag value
            without mutating os.environ (used in tests only).

    Returns:
        WorkflowResolutionReceipt with resolution_status=RESOLVED when exactly
        one active (or test-enabled) MANAGED_WORKFLOW route is found.

    Raises:
        WorkflowRegistryResolutionError: on any fail-closed path (DISABLED,
            ZERO_MATCH, MULTIPLE_MATCH, DIGEST_MISMATCH, INVALID).
    """
    root = repo_root or _resolve_repo_root()
    registry_path = root / registry_relpath
    test_activated = _is_test_activated(_test_activation_env_override)

    # ── 1. Load registry ─────────────────────────────────────────────────
    if not registry_path.exists():
        reason = f"route_registry not found: {registry_relpath}"
        _log.error("[workflow_registry] %s", reason)
        raise WorkflowRegistryResolutionError(INVALID, reason)

    all_routes = _load_route_registry(registry_path)
    if not all_routes:
        reason = f"route_registry empty or unparseable: {registry_relpath}"
        raise WorkflowRegistryResolutionError(INVALID, reason)

    # ── 2. Filter to MANAGED_WORKFLOW routes ─────────────────────────────
    managed = [
        r for r in all_routes
        if r.get("execution_form") == _MANAGED_WORKFLOW_FORM
    ]

    if len(managed) == 0:
        reason = f"No MANAGED_WORKFLOW routes in {registry_relpath}"
        _log.warning("[workflow_registry] ZERO_MATCH: %s", reason)
        raise WorkflowRegistryResolutionError(ZERO_MATCH, reason)

    if len(managed) > 1:
        ids = [r.get("route_id", "?") for r in managed]
        reason = (
            f"Multiple MANAGED_WORKFLOW routes found: {ids}. "
            "Exactly one is required — ambiguous selection fails closed."
        )
        _log.error("[workflow_registry] MULTIPLE_MATCH: %s", reason)
        raise WorkflowRegistryResolutionError(MULTIPLE_MATCH, reason)

    route = managed[0]

    # ── 3. Extract route fields ───────────────────────────────────────────
    route_id: str = str(route.get("route_id", ""))
    route_status: str = str(route.get("status", ""))
    l3_required: bool = bool(route.get("l3_required", True))
    execution_form: str = str(route.get("execution_form", _MANAGED_WORKFLOW_FORM))
    workflow_manifest_ref: str = str(route.get("workflow_manifest_ref", ""))
    workflow_manifest_path: str = str(route.get("workflow_manifest_path", ""))

    if not route_id:
        raise WorkflowRegistryResolutionError(INVALID, "route_id missing in registry entry")

    if execution_form != _MANAGED_WORKFLOW_FORM:
        reason = f"Unexpected execution_form={execution_form!r} — only MANAGED_WORKFLOW allowed"
        raise WorkflowRegistryResolutionError(INVALID, reason)

    # ── 4. workflow_manifest_ref must be present ──────────────────────────
    if not workflow_manifest_ref:
        reason = (
            f"route_id={route_id!r}: workflow_manifest_ref missing or empty. "
            "Missing workflow_manifest_ref fails closed."
        )
        _log.error("[workflow_registry] INVALID: %s", reason)
        raise WorkflowRegistryResolutionError(INVALID, reason)

    # ── 5. Activation check (registered_not_active → DISABLED in prod) ───
    if route_status == _STATUS_NOT_ACTIVE and not test_activated:
        reason = (
            f"route_id={route_id!r} is status=registered_not_active. "
            "Production L0 does not activate registered_not_active routes. "
            "Pass _test_activation_env_override='1' to enable in test mode."
        )
        _log.info("[workflow_registry] DISABLED: %s", reason)
        raise WorkflowRegistryResolutionError(DISABLED, reason)

    # ── 6. Manifest digest verification (if requested) ────────────────────
    manifest_digest = ""
    if workflow_manifest_path:
        manifest_file = root / workflow_manifest_path
        manifest_digest = _compute_digest(manifest_file)
        if expected_manifest_digest and manifest_digest != expected_manifest_digest:
            reason = (
                f"Manifest digest mismatch for {workflow_manifest_path!r}: "
                f"expected={expected_manifest_digest[:16]}… "
                f"actual={manifest_digest[:16]}…"
            )
            _log.error("[workflow_registry] DIGEST_MISMATCH: %s", reason)
            raise WorkflowRegistryResolutionError(DIGEST_MISMATCH, reason)

    # ── 7. Build canonical workflow_ref ──────────────────────────────────
    # workflow_ref is the manifest_ref string — the stable registry key.
    workflow_ref = workflow_manifest_ref

    decisive_reason = (
        f"Resolved route_id={route_id!r} workflow_ref={workflow_ref!r} "
        f"test_activated={test_activated}"
    )

    receipt = WorkflowResolutionReceipt(
        route_id=route_id,
        workflow_ref=workflow_ref,
        workflow_manifest_ref=workflow_manifest_ref,
        workflow_manifest_path=workflow_manifest_path,
        manifest_digest=manifest_digest,
        route_registry_ref=registry_relpath,
        route_status=route_status,
        l3_required=l3_required,
        execution_form=execution_form,
        resolution_status=RESOLVED,
        decisive_reason=decisive_reason,
        test_activated=test_activated,
    )

    _log.info(
        "[workflow_registry] RESOLVED route_id=%r workflow_ref=%r manifest_digest=%s...",
        route_id,
        workflow_ref,
        manifest_digest[:12],
    )
    return receipt


__all__ = [
    "RESOLVED",
    "DISABLED",
    "ZERO_MATCH",
    "MULTIPLE_MATCH",
    "DIGEST_MISMATCH",
    "INVALID",
    "WorkflowRegistryResolutionError",
    "WorkflowResolutionReceipt",
    "resolve_managed_workflow_route",
]
