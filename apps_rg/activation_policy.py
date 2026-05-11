"""Activation profile loader and validator for apps_rg managed workflow route.

Per RB12 guarded activation readiness — the activation profile is the
single source of truth for whether the managed workflow route may be
selected. Route registry status alone is not sufficient.
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


class ActivationMode(Enum):
    """Supported activation modes for the managed workflow route."""
    DISABLED = "disabled"
    TEST_ONLY = "test_only"
    GUARDED = "guarded"
    ACTIVE = "active"


class ProviderMode(Enum):
    """Provider call policy."""
    STUB_ONLY = "stub_only"
    LIVE_ALLOWED = "live_allowed"


@dataclass(frozen=True)
class ActivationProfile:
    """Immutable activation profile for apps_rg managed workflow route."""
    activation_profile_id: str
    app_id: str
    task_class: str
    route_id: str
    target_execution_form: str
    activation_mode: ActivationMode
    default_mode: ActivationMode
    allowed_modes: tuple[ActivationMode, ...]
    rollout_percentage: int
    allowed_tenants: frozenset[str]
    allowed_users: frozenset[str]
    required_certification_receipts: tuple[str, ...]
    required_gate_profiles: tuple[str, ...]
    required_e2e_receipts: tuple[str, ...]
    provider_mode: ProviderMode
    rollback_policy: dict[str, Any]
    activation_owner: str | None
    activation_reason: str | None
    activated_at: str | None
    expires_at: str | None
    deterministic_digest: str
    raw: dict[str, Any]

    @property
    def is_expired(self) -> bool:
        """Check if activation profile has expired."""
        if not self.expires_at:
            return False
        try:
            expiry = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
            return datetime.now(timezone.utc) > expiry
        except (ValueError, TypeError):
            _log.warning("Invalid expires_at format: %s", self.expires_at)
            return True

    @property
    def is_activated(self) -> bool:
        """Check if profile has been activated (has activation timestamp)."""
        return self.activated_at is not None

    def allows_tenant(self, tenant_id: str) -> bool:
        """Check if tenant is in allowed list (empty list = none allowed)."""
        if not self.allowed_tenants:
            return False
        return tenant_id in self.allowed_tenants

    def allows_user(self, user_id: str) -> bool:
        """Check if user is in allowed list (empty list = none allowed)."""
        if not self.allowed_users:
            return False
        return user_id in self.allowed_users

    def can_activate(self, mode: ActivationMode) -> bool:
        """Check if requested mode is in allowed modes."""
        return mode in self.allowed_modes


class ActivationError(Exception):
    """Base exception for activation policy violations."""
    pass


class ActivationProfileNotFound(ActivationError):
    """Activation profile file not found."""
    pass


class ActivationProfileInvalid(ActivationError):
    """Activation profile schema validation failed."""
    pass


class ActivationNotPermitted(ActivationError):
    """Route activation blocked by policy."""
    pass


class ProviderModeViolation(ActivationError):
    """Provider mode incompatible with execution request."""
    pass


class CertificationReceiptMissing(ActivationError):
    """Required certification receipt not found."""
    pass


# RB12: canonical path for activation profile
ACTIVATION_PROFILE_RELPATH: str = "apps_rg/config/domain_contract/activation_profile.resume_generation.v1.json"

# RB12: receipt paths that must exist for guarded activation
RB12_REQUIRED_RECEIPTS: tuple[str, ...] = (
    "artifacts/apps_rg/apps_rg_w11_final_no_bypass_certification_receipt.json",
    "artifacts/apps_rg/apps_rg_plan_rebaseline_after_w11_receipt.json",
    "artifacts/apps_rg/apps_rg_w9_full_spine_stubbed_e2e_receipt.json",
    "artifacts/apps_rg/apps_rg_w10_l6_uwg_writeback_receipt.json",
)


def _resolve_repo_root() -> Path:
    """Find repository root (contains pyproject.toml)."""
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def load_activation_profile(
    repo_root: Path | None = None,
    profile_relpath: str = ACTIVATION_PROFILE_RELPATH,
) -> ActivationProfile:
    """Load and validate activation profile from JSON file.

    Args:
        repo_root: Repository root path. Auto-resolved if None.
        profile_relpath: Relative path to activation profile JSON.

    Returns:
        Validated ActivationProfile dataclass.

    Raises:
        ActivationProfileNotFound: if file doesn't exist.
        ActivationProfileInvalid: if JSON is malformed or invalid.
    """
    if repo_root is None:
        repo_root = _resolve_repo_root()

    profile_path = repo_root / profile_relpath
    if not profile_path.exists():
        raise ActivationProfileNotFound(f"Activation profile not found: {profile_path}")

    try:
        raw = json.loads(profile_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ActivationProfileInvalid(f"Invalid JSON in activation profile: {exc}")

    # Validate required fields
    required_fields = [
        "activation_profile_id", "app_id", "task_class", "route_id",
        "target_execution_form", "activation_mode", "default_mode",
        "provider_mode", "deterministic_digest",
    ]
    for field in required_fields:
        if field not in raw:
            raise ActivationProfileInvalid(f"Missing required field: {field}")

    # Parse activation mode
    try:
        activation_mode = ActivationMode(raw.get("activation_mode", "disabled"))
    except ValueError as exc:
        raise ActivationProfileInvalid(f"Invalid activation_mode: {exc}")

    # Parse default mode
    try:
        default_mode = ActivationMode(raw.get("default_mode", "disabled"))
    except ValueError as exc:
        raise ActivationProfileInvalid(f"Invalid default_mode: {exc}")

    # Parse allowed modes
    allowed_modes_raw = raw.get("allowed_modes", ["disabled"])
    try:
        allowed_modes = tuple(ActivationMode(m) for m in allowed_modes_raw)
    except ValueError as exc:
        raise ActivationProfileInvalid(f"Invalid allowed_modes: {exc}")

    # Parse provider mode
    try:
        provider_mode = ProviderMode(raw.get("provider_mode", "stub_only"))
    except ValueError as exc:
        raise ActivationProfileInvalid(f"Invalid provider_mode: {exc}")

    return ActivationProfile(
        activation_profile_id=raw["activation_profile_id"],
        app_id=raw["app_id"],
        task_class=raw["task_class"],
        route_id=raw["route_id"],
        target_execution_form=raw["target_execution_form"],
        activation_mode=activation_mode,
        default_mode=default_mode,
        allowed_modes=allowed_modes,
        rollout_percentage=raw.get("rollout_percentage", 0),
        allowed_tenants=frozenset(raw.get("allowed_tenants", [])),
        allowed_users=frozenset(raw.get("allowed_users", [])),
        required_certification_receipts=tuple(raw.get("required_certification_receipts", [])),
        required_gate_profiles=tuple(raw.get("required_gate_profiles", [])),
        required_e2e_receipts=tuple(raw.get("required_e2e_receipts", [])),
        provider_mode=provider_mode,
        rollback_policy=raw.get("rollback_policy", {}),
        activation_owner=raw.get("activation_owner"),
        activation_reason=raw.get("activation_reason"),
        activated_at=raw.get("activated_at"),
        expires_at=raw.get("expires_at"),
        deterministic_digest=raw.get("deterministic_digest", ""),
        raw=raw,
    )


def check_certification_receipts_exist(
    repo_root: Path,
    receipts: tuple[str, ...] | None = None,
) -> dict[str, bool]:
    """Verify that required certification receipts exist on disk.

    Args:
        repo_root: Repository root path.
        receipts: Tuple of receipt relative paths. Uses RB12 defaults if None.

    Returns:
        Dict mapping receipt path to existence status.
    """
    if receipts is None:
        receipts = RB12_REQUIRED_RECEIPTS

    results: dict[str, bool] = {}
    for receipt_relpath in receipts:
        receipt_path = repo_root / receipt_relpath
        exists = receipt_path.exists()
        results[receipt_relpath] = exists
        if not exists:
            _log.warning("Required certification receipt missing: %s", receipt_relpath)
    return results


def evaluate_route_activation(
    tenant_id: str,
    user_id: str | None = None,
    requested_mode: ActivationMode | None = None,
    repo_root: Path | None = None,
    _test_activation_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate whether managed workflow route may be activated.

    RB12 guarded activation policy:
    1. Load activation profile
    2. Check certification receipts exist
    3. Verify activation_mode permits route selection
    4. Verify tenant/user in allowed lists (for guarded mode)
    5. Verify provider_mode is stub_only (RB12 — no live providers yet)
    6. Verify profile not expired

    Args:
        tenant_id: Requesting tenant ID.
        user_id: Optional requesting user ID.
        requested_mode: Desired activation mode (defaults to profile's mode).
        repo_root: Repository root (auto-resolved if None).
        _test_activation_override: Test injection for activation profile fields.

    Returns:
        Dict with evaluation result including:
        - permitted: bool
        - reason: str (human-readable explanation)
        - activation_mode: ActivationMode
        - provider_mode: ProviderMode
        - blockers: list[str] (why activation was denied)
    """
    if repo_root is None:
        repo_root = _resolve_repo_root()

    blockers: list[str] = []

    # Load activation profile
    try:
        profile = load_activation_profile(repo_root)
    except ActivationProfileNotFound as exc:
        return {
            "permitted": False,
            "reason": f"Activation profile not found: {exc}",
            "activation_mode": ActivationMode.DISABLED,
            "provider_mode": ProviderMode.STUB_ONLY,
            "blockers": ["activation_profile_missing"],
        }
    except ActivationProfileInvalid as exc:
        return {
            "permitted": False,
            "reason": f"Activation profile invalid: {exc}",
            "activation_mode": ActivationMode.DISABLED,
            "provider_mode": ProviderMode.STUB_ONLY,
            "blockers": ["activation_profile_invalid"],
        }

    # Apply test override if provided (test injection only)
    if _test_activation_override:
        raw = dict(profile.raw)
        raw.update(_test_activation_override)
        # Re-parse with override
        try:
            profile = ActivationProfile(
                activation_profile_id=raw["activation_profile_id"],
                app_id=raw["app_id"],
                task_class=raw["task_class"],
                route_id=raw["route_id"],
                target_execution_form=raw["target_execution_form"],
                activation_mode=ActivationMode(raw.get("activation_mode", "disabled")),
                default_mode=ActivationMode(raw.get("default_mode", "disabled")),
                allowed_modes=tuple(ActivationMode(m) for m in raw.get("allowed_modes", ["disabled"])),
                rollout_percentage=raw.get("rollout_percentage", 0),
                allowed_tenants=frozenset(raw.get("allowed_tenants", [])),
                allowed_users=frozenset(raw.get("allowed_users", [])),
                required_certification_receipts=tuple(raw.get("required_certification_receipts", [])),
                required_gate_profiles=tuple(raw.get("required_gate_profiles", [])),
                required_e2e_receipts=tuple(raw.get("required_e2e_receipts", [])),
                provider_mode=ProviderMode(raw.get("provider_mode", "stub_only")),
                rollback_policy=raw.get("rollback_policy", {}),
                activation_owner=raw.get("activation_owner"),
                activation_reason=raw.get("activation_reason"),
                activated_at=raw.get("activated_at"),
                expires_at=raw.get("expires_at"),
                deterministic_digest=raw.get("deterministic_digest", ""),
                raw=raw,
            )
        except (KeyError, ValueError) as exc:
            return {
                "permitted": False,
                "reason": f"Test override produced invalid profile: {exc}",
                "activation_mode": ActivationMode.DISABLED,
                "provider_mode": ProviderMode.STUB_ONLY,
                "blockers": ["test_override_invalid"],
            }

    # Check certification receipts
    receipt_status = check_certification_receipts_exist(repo_root, profile.required_certification_receipts)
    missing_receipts = [p for p, exists in receipt_status.items() if not exists]
    if missing_receipts:
        blockers.append(f"missing_certification_receipts: {missing_receipts}")

    # Check activation mode
    effective_mode = requested_mode or profile.activation_mode

    if effective_mode == ActivationMode.DISABLED:
        blockers.append("activation_mode_is_disabled")

    if not profile.can_activate(effective_mode):
        blockers.append(f"mode_not_allowed: {effective_mode.value}")

    # For guarded mode, check tenant/user allowlists
    if effective_mode == ActivationMode.GUARDED:
        if not profile.allows_tenant(tenant_id):
            blockers.append(f"tenant_not_allowed: {tenant_id}")
        if user_id and not profile.allows_user(user_id):
            blockers.append(f"user_not_allowed: {user_id}")

    # RB12: provider_mode must be stub_only
    if profile.provider_mode != ProviderMode.STUB_ONLY:
        blockers.append(f"provider_mode_not_stub_only: {profile.provider_mode.value}")

    # Check expiration
    if profile.is_expired:
        blockers.append("activation_profile_expired")

    # Build result
    permitted = len(blockers) == 0

    reason = (
        f"Route activation {'permitted' if permitted else 'blocked'} "
        f"for mode={effective_mode.value}, tenant={tenant_id}"
    )
    if not permitted:
        reason += f"; blockers={blockers}"

    return {
        "permitted": permitted,
        "reason": reason,
        "activation_mode": effective_mode,
        "provider_mode": profile.provider_mode,
        "blockers": blockers,
        "profile": profile,
    }


__all__ = [
    "ActivationMode",
    "ProviderMode",
    "ActivationProfile",
    "ActivationError",
    "ActivationProfileNotFound",
    "ActivationProfileInvalid",
    "ActivationNotPermitted",
    "ProviderModeViolation",
    "CertificationReceiptMissing",
    "load_activation_profile",
    "check_certification_receipts_exist",
    "evaluate_route_activation",
    "ACTIVATION_PROFILE_RELPATH",
    "RB12_REQUIRED_RECEIPTS",
]
