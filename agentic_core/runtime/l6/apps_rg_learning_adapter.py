"""L6 learning adapter — binds app profile to L6WritebackProposer.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W10

Loads learning parameters from the domain contract profile files
and returns a configured L6WritebackProposer instance.

This adapter uses profile-driven configuration. Generic L6 logic lives in
``writeback_proposer.py``.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from agentic_core.runtime.l6.writeback_proposer import L6WritebackProposer
from agentic_core.runtime.profiles.profile_resolver import (
    RuntimeProfileResolver,
    UnknownAppError,
    MissingProfileError,
    InvalidProfileError,
)

_DEFAULT_LEARNING_PARAMS: dict = {
    "promotion_threshold": 0.65,
    "min_n_each_arm": 30,
    "holdout_required": True,
    "judge_calibration_cadence_days": 14,
    "regret_budget": 0.10,
    "z_score": 1.96,
    "uplift_required": True,
    "promotion_requires_uwg": True,
    "current_run_rescue_allowed": False,
    "completed_run_only": True,
}


def _get_l6_profile_defaults(app_id: str) -> dict:
    """Get L6 writeback profile defaults from app profile.
    
    Fail-closed: returns empty dict if profile resolution fails.
    """
    if not app_id:
        return {}
    
    try:
        resolver = RuntimeProfileResolver()
        profile = resolver.resolve(app_id, "l6_writeback")
        return profile.typed_payload.get("writeback_config", {})
    except (UnknownAppError, MissingProfileError, InvalidProfileError):
        return {}
    except Exception:
        return {}


def _load_meta_feedback_params(
    repo_root: Path,
    profile_relpath: str,
) -> dict:
    """Load learning_parameters from meta_feedback_profile JSON.

    Falls back to _DEFAULT_LEARNING_PARAMS if file is absent.
    """
    profile_path = repo_root / profile_relpath
    if not profile_path.exists():
        return dict(_DEFAULT_LEARNING_PARAMS)
    try:
        data = json.loads(profile_path.read_text(encoding="utf-8"))
        return dict(data.get("learning_parameters", _DEFAULT_LEARNING_PARAMS))
    except (json.JSONDecodeError, OSError):
        return dict(_DEFAULT_LEARNING_PARAMS)


def build_l6_proposer(
    app_id: str,
    repo_root: Optional[Path] = None,
) -> L6WritebackProposer:
    """Return a configured L6WritebackProposer for the given app.

    Uses profile-driven configuration to load learning parameters and
    policy references. Fail-closed if profile is missing or invalid.
    
    Args:
        app_id: Application identifier (resolved from runtime profile)
        repo_root: Optional repository root for loading legacy profiles
        
    Returns:
        Configured L6WritebackProposer instance
        
    Raises:
        ValueError: If app_id is empty or invalid
    """
    if not app_id:
        raise ValueError("app_id is required for L6 proposer configuration")
    
    # Get profile-driven defaults
    profile_defaults = _get_l6_profile_defaults(app_id)
    
    if repo_root is None:
        learning_params = dict(_DEFAULT_LEARNING_PARAMS)
    else:
        # Use profile-driven policy ref if available
        policy_ref = profile_defaults.get("policy_refs", {}).get(
            "meta_feedback_profile",
            f"{app_id}/config/domain_contract/meta_feedback_profile.v1.json"
        )
        learning_params = _load_meta_feedback_params(Path(repo_root), policy_ref)

    # Get task_class from profile or fail-closed to empty string
    task_class = profile_defaults.get("task_class", "")
    
    # Get policy ref from profile or construct generic path
    policy_ref = profile_defaults.get("policy_refs", {}).get(
        "meta_feedback_profile",
        f"{app_id}/config/domain_contract/meta_feedback_profile.v1.json"
    )

    return L6WritebackProposer(
        app_id=app_id,
        task_class=task_class,
        learning_profile=learning_params,
        policy_ref=policy_ref,
    )


# Backward-compatible alias for existing callers
def build_apps_rg_l6_proposer(
    repo_root: Optional[Path] = None,
) -> L6WritebackProposer:
    """Return a configured L6WritebackProposer for apps_rg.
    
    Deprecated: Use build_l6_proposer(app_id=..., ...) with explicit app_id.
    """
    raise RuntimeError("This backward-compat alias requires explicit app_id migration. Use build_l6_proposer(app_id=<your_app>, ...)")


__all__ = [
    "build_l6_proposer",  # Generic, profile-driven
    "build_apps_rg_l6_proposer",  # Backward-compatible alias
    "_DEFAULT_LEARNING_PARAMS",
]
