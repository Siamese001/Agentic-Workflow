"""HITL policy registry for apps_rg — AG-13.b implementation.

Per plan apps-rg-deferred-follow-ons-b3e9f1 W1.

Resolves a hitl_policy_ref string (e.g. "rg_release_approval_v1") into a
structured HitlPolicySpec object that the Exit binding attaches to the
X3Disposition for downstream HITL routing.

Design rules:
- All HITL capability code lives in agentic_core/ (never apps_rg/)
- resolve_hitl_policy() is pure and never raises — fail-soft returns
  HitlPolicySpec with trigger_kind=UNKNOWN and requires_hitl=False
- Policy specs are built from the known TRIGGER_KINDS vocabulary in
  apps_rg/hitl/hitl_schemas.py; the registry does NOT import from apps_rg/
  to keep the dependency direction correct (agentic_core depends on
  well-known policy names, not on the apps_rg HITL module).
"""
from __future__ import annotations

import dataclasses
import logging
import os
from typing import Any, Optional

_LOG = logging.getLogger(__name__)

_HITL_REGISTRY_FAIL_CLOSED_ENV: str = "APPS_RG_HITL_REGISTRY_FAIL_CLOSED"


# ---------------------------------------------------------------------------
# HitlPolicySpec — structured resolution of a hitl_policy_ref string
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class HitlPolicySpec:
    """Resolved HITL policy specification.

    Attributes:
        policy_ref:      Original string ref from U0 profile manifest.
        trigger_kind:    One of the canonical TRIGGER_KINDS vocab; "UNKNOWN"
                         when the ref is unrecognised.
        requires_hitl:   True when this run MUST obtain human release approval
                         before Exit disposition is finalised.
        trigger_threshold: Confidence floor below which HITL fires automatically
                           (0.0 = always fires; 1.0 = never fires automatically).
        operator_id:     Default operator responsible for review; None = any.
        policy_version:  Policy schema version; "v1" for all current refs.
        resolved:        False when registry lookup failed (unrecognised ref).
    """

    policy_ref: str
    trigger_kind: str
    requires_hitl: bool
    trigger_threshold: float
    operator_id: Optional[str]
    policy_version: str
    resolved: bool


# ---------------------------------------------------------------------------
# Built-in policy table (AG-13.b registry)
# ---------------------------------------------------------------------------

_BUILTIN_POLICIES: dict[str, dict[str, Any]] = {
    "rg_release_approval_v1": {
        "trigger_kind": "RELEASE_APPROVAL",
        "requires_hitl": True,
        "trigger_threshold": 0.80,
        "operator_id": "amit",
        "policy_version": "v1",
    },
    "rg_missing_brief_v1": {
        "trigger_kind": "MISSING_BRIEF",
        "requires_hitl": True,
        "trigger_threshold": 1.0,
        "operator_id": None,
        "policy_version": "v1",
    },
    "rg_stale_brief_v1": {
        "trigger_kind": "STALE_BRIEF",
        "requires_hitl": True,
        "trigger_threshold": 0.90,
        "operator_id": None,
        "policy_version": "v1",
    },
    "rg_low_confidence_v1": {
        "trigger_kind": "LOW_CONFIDENCE",
        "requires_hitl": True,
        "trigger_threshold": 0.70,
        "operator_id": None,
        "policy_version": "v1",
    },
    "rg_cache_promotion_v1": {
        "trigger_kind": "CACHE_PROMOTION",
        "requires_hitl": False,
        "trigger_threshold": 1.0,
        "operator_id": None,
        "policy_version": "v1",
    },
    "rg_no_hitl_v1": {
        "trigger_kind": "RELEASE_APPROVAL",
        "requires_hitl": False,
        "trigger_threshold": 1.0,
        "operator_id": None,
        "policy_version": "v1",
    },
}

_UNKNOWN_SPEC_TEMPLATE: dict[str, Any] = {
    "trigger_kind": "UNKNOWN",
    "requires_hitl": False,
    "trigger_threshold": 1.0,
    "operator_id": None,
    "policy_version": "unknown",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def resolve_hitl_policy(policy_ref: Optional[str]) -> HitlPolicySpec:
    """Resolve a hitl_policy_ref string to a HitlPolicySpec.

    Never raises. Returns a spec with resolved=False and trigger_kind='UNKNOWN'
    when the ref is unrecognised or None.

    Args:
        policy_ref: String ref from profile_manifest.hitl_policy_ref.  May be
                    None (when the U0 payload omits it) or an unrecognised ref.

    Returns:
        HitlPolicySpec with resolved=True for known refs, resolved=False otherwise.
    """
    if not policy_ref:
        return HitlPolicySpec(
            policy_ref="",
            trigger_kind="UNKNOWN",
            requires_hitl=False,
            trigger_threshold=1.0,
            operator_id=None,
            policy_version="unknown",
            resolved=False,
        )

    key = str(policy_ref).strip().lower()
    row = _BUILTIN_POLICIES.get(key) or _BUILTIN_POLICIES.get(policy_ref.strip())
    if row is None:
        fail_closed = os.environ.get(_HITL_REGISTRY_FAIL_CLOSED_ENV, "").strip() == "1"
        if fail_closed:
            _LOG.error(
                "[hitl_policy_registry] unrecognised hitl_policy_ref=%r; "
                "APPS_RG_HITL_REGISTRY_FAIL_CLOSED=1 — treating as requires_hitl=True",
                policy_ref,
            )
            return HitlPolicySpec(
                policy_ref=policy_ref,
                trigger_kind="UNKNOWN",
                requires_hitl=True,
                trigger_threshold=0.0,
                operator_id=None,
                policy_version="unknown",
                resolved=False,
            )
        _LOG.warning(
            "[hitl_policy_registry] unrecognised hitl_policy_ref=%r; "
            "returning UNKNOWN/requires_hitl=False (fail-soft)",
            policy_ref,
        )
        return HitlPolicySpec(
            policy_ref=policy_ref,
            trigger_kind="UNKNOWN",
            requires_hitl=False,
            trigger_threshold=1.0,
            operator_id=None,
            policy_version="unknown",
            resolved=False,
        )

    return HitlPolicySpec(
        policy_ref=policy_ref,
        trigger_kind=row["trigger_kind"],
        requires_hitl=row["requires_hitl"],
        trigger_threshold=row["trigger_threshold"],
        operator_id=row["operator_id"],
        policy_version=row["policy_version"],
        resolved=True,
    )


__all__ = [
    "HitlPolicySpec",
    "resolve_hitl_policy",
    "_BUILTIN_POLICIES",
]
