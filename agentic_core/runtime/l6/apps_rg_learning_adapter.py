"""apps_rg L6 learning adapter — binds apps_rg profile to L6WritebackProposer.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W10

Loads apps_rg learning parameters from the domain contract profile files
and returns a configured L6WritebackProposer instance.

This adapter is the apps_rg-specific wiring.  Generic L6 logic lives in
``writeback_proposer.py``.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from agentic_core.runtime.l6.writeback_proposer import L6WritebackProposer


_LEARNING_PROFILE_RELPATH = (
    "apps_rg/config/domain_contract/learning_profiles.yaml"
)
_META_FEEDBACK_PROFILE_RELPATH = (
    "apps_rg/config/domain_contract/meta_feedback_profile.resume_generation.v1.json"
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


def _load_meta_feedback_params(repo_root: Path) -> dict:
    """Load learning_parameters from meta_feedback_profile JSON.

    Falls back to _DEFAULT_LEARNING_PARAMS if file is absent.
    """
    profile_path = repo_root / _META_FEEDBACK_PROFILE_RELPATH
    if not profile_path.exists():
        return dict(_DEFAULT_LEARNING_PARAMS)
    try:
        data = json.loads(profile_path.read_text(encoding="utf-8"))
        return dict(data.get("learning_parameters", _DEFAULT_LEARNING_PARAMS))
    except (json.JSONDecodeError, OSError):
        return dict(_DEFAULT_LEARNING_PARAMS)


def build_apps_rg_l6_proposer(
    repo_root: Optional[Path] = None,
) -> L6WritebackProposer:
    """Return a configured L6WritebackProposer for apps_rg.

    Loads learning parameters from the domain contract profile if repo_root
    is provided; falls back to defaults otherwise.
    """
    if repo_root is None:
        learning_params = dict(_DEFAULT_LEARNING_PARAMS)
    else:
        learning_params = _load_meta_feedback_params(Path(repo_root))

    return L6WritebackProposer(
        app_id="apps_rg",
        task_class="resume_generation",
        learning_profile=learning_params,
        policy_ref=_META_FEEDBACK_PROFILE_RELPATH,
    )


__all__ = [
    "build_apps_rg_l6_proposer",
    "_DEFAULT_LEARNING_PARAMS",
    "_META_FEEDBACK_PROFILE_RELPATH",
    "_LEARNING_PROFILE_RELPATH",
]
