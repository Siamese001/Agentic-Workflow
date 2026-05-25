"""HITL policy registry — generic capability layer (agentic_core).

Per plan apps-rg-deferred-follow-ons-b3e9f1 W1.
Core Addition Author-Gate cleanup: app-specific rg_* policy table moved to
apps_rg/config/domain_contract/hitl_policies.resume_generation.v1.yaml.

Resolves a hitl_policy_ref string into a HitlPolicySpec.  The registry owns:
  - the HitlPolicySpec dataclass (generic)
  - load_hitl_policy_table() — loads an app-owned YAML policy file
  - resolve_hitl_policy() — pure lookup against a caller-supplied table

The registry does NOT own any app-specific policy definitions.  Every
apps_* defines its own policy YAML under apps_*/config/domain_contract/.

Design rules:
- All HITL capability code lives in agentic_core/ (never apps_rg/)
- resolve_hitl_policy() is pure and never raises — fail-soft returns
  HitlPolicySpec with trigger_kind=UNKNOWN and requires_hitl=False
- App policy tables are loaded by load_hitl_policy_table(path) and passed
  to resolve_hitl_policy(ref, policy_table=table) by app-owned bindings.
- _BUILTIN_POLICIES is intentionally empty; preserved for import compatibility.
"""
from __future__ import annotations

import dataclasses
import logging
import os
from pathlib import Path
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
# Built-in policy table — intentionally empty.
# App-specific policies live under apps_*/config/domain_contract/.
# Preserved as empty dict so existing `from ... import _BUILTIN_POLICIES`
# imports continue to work without error.
# ---------------------------------------------------------------------------

_BUILTIN_POLICIES: dict[str, dict[str, Any]] = {}

_UNKNOWN_SPEC_TEMPLATE: dict[str, Any] = {
    "trigger_kind": "UNKNOWN",
    "requires_hitl": False,
    "trigger_threshold": 1.0,
    "operator_id": None,
    "policy_version": "unknown",
}


# ---------------------------------------------------------------------------
# App-owned policy table loader
# ---------------------------------------------------------------------------

def load_hitl_policy_table(policy_yaml_path: "str | Path") -> dict[str, dict[str, Any]]:
    """Load an app-owned HITL policy YAML and return a normalized policy table.

    The YAML must be a mapping of policy_ref → {trigger_kind, requires_hitl,
    trigger_threshold, operator_id, policy_version}.

    Never raises — returns an empty dict on any load/parse failure so that
    callers fall through to the UNKNOWN/fail-soft path.

    Args:
        policy_yaml_path: Absolute or repo-relative path to the app's
                          hitl_policies.<task_class>.<version>.yaml file.

    Returns:
        Dict mapping lowercase policy_ref to row dict, ready to pass to
        resolve_hitl_policy(ref, policy_table=...).
    """
    try:
        import yaml  # soft dep — stdlib not available; apps that use HITL must have pyyaml
    except ImportError:
        _LOG.warning(
            "[hitl_policy_registry] PyYAML not available — cannot load %s; "
            "all policy lookups will return UNKNOWN",
            policy_yaml_path,
        )
        return {}

    path = Path(policy_yaml_path)
    if not path.is_absolute():
        _repo_root = Path(__file__).resolve().parents[3]
        path = _repo_root / policy_yaml_path

    if not path.exists():
        _LOG.warning(
            "[hitl_policy_registry] policy file not found: %s — "
            "all policy lookups will return UNKNOWN",
            path,
        )
        return {}

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # guardian: allow-broad-exception -- P1 ADG burndown
        _LOG.warning(
            "[hitl_policy_registry] failed to parse %s: %s — "
            "all policy lookups will return UNKNOWN",
            path, exc,
        )
        return {}

    if not isinstance(raw, dict):
        _LOG.warning(
            "[hitl_policy_registry] %s did not parse as a dict — "
            "all policy lookups will return UNKNOWN",
            path,
        )
        return {}

    # Normalize: lowercase keys, cast types defensively
    table: dict[str, dict[str, Any]] = {}
    for ref, row in raw.items():
        if not isinstance(row, dict):
            continue
        table[str(ref).strip().lower()] = {
            "trigger_kind": str(row.get("trigger_kind", "UNKNOWN")),
            "requires_hitl": bool(row.get("requires_hitl", False)),
            "trigger_threshold": float(row.get("trigger_threshold", 1.0)),
            "operator_id": row.get("operator_id") or None,
            "policy_version": str(row.get("policy_version", "v1")),
        }
    return table


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def resolve_hitl_policy(
    policy_ref: Optional[str],
    policy_table: Optional[dict[str, dict[str, Any]]] = None,
) -> HitlPolicySpec:
    """Resolve a hitl_policy_ref string to a HitlPolicySpec.

    Never raises. Returns a spec with resolved=False and trigger_kind='UNKNOWN'
    when the ref is unrecognised or None.

    Args:
        policy_ref:   String ref from profile_manifest.hitl_policy_ref.  May be
                      None (when the U0 payload omits it) or an unrecognised ref.
        policy_table: App-owned policy table returned by load_hitl_policy_table().
                      When None, only the (empty) built-in table is searched,
                      which means any non-empty ref will resolve to UNKNOWN.

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
    effective_table = policy_table if policy_table is not None else _BUILTIN_POLICIES
    row = effective_table.get(key) or effective_table.get(policy_ref.strip())

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
    "load_hitl_policy_table",
    "resolve_hitl_policy",
    "_BUILTIN_POLICIES",
]
