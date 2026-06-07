"""Harness-scoped AppDomainStore loader.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-dom-runtime-evidence-real-b4c9e2.md W2.P1.

Builds an :class:`InMemoryAppDomainStore` populated with per-app
AppEvalRubricRecord / AppThresholdProfileRecord / AppGraderRosterRecord
records read from each app's `<app>/config/domain_contract/*.yaml`.

Why this exists:
  At CI time, the default `get_default_app_domain_store()` returns an
  empty singleton. Production apps populate it at boot via their init
  paths; the runtime harness skips that init, so the evaluator's
  `rubric_ref` lookups fail with `UnknownAppContractError` and bubble
  out as `bound=True, passed=False, fail_reasons=["unknown_app_contract::..."]`.
  This loader reads the same YAMLs production would, constructs real
  domain records, and seeds a harness-local store for injection into
  `AppSpecificEvaluator(store=<this>)`.

Fail policy:
  Loading is fail-soft per-app. A malformed YAML for one app does NOT
  prevent the other 7 apps from loading. The loader returns a list of
  per-app load reports so callers can surface which apps succeeded.

Authority:
  READ-ONLY on YAML. Writes only into the returned fresh store instance.
  Never mutates production singletons.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    read_dim_score_from_output,
)
from agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator import (
    AppSpecificEvaluator,
)
from agentic_core.L4_state.contracts.app_domain import (
    AppEvalRubricRecord,
    AppGraderRosterRecord,
    AppThresholdProfileRecord,
    ScoreDimension,
)
from agentic_core.L4_state.contracts.app_domain_lookup import InMemoryAppDomainStore

_LOGGER = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class LoadReport:
    """Per-app outcome of the loader."""

    app: str
    rubric_loaded: bool = False
    threshold_loaded: bool = False
    grader_roster_loaded: bool = False
    warnings: list[str] = field(default_factory=list)
    rubric_id: str = ""
    threshold_profile_id: str = ""
    grader_roster_id: str = ""

    @property
    def ok(self) -> bool:
        """True when at least the rubric + threshold loaded (grader roster optional)."""
        return self.rubric_loaded and self.threshold_loaded


def _load_first_yaml(path: Path) -> Any:
    """Load a YAML file and return its first entry if a list, else the root dict.

    Returns None on any error (fail-soft).
    """
    if not path.exists():
        return None
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError) as exc:
        _LOGGER.warning("[store_loader] %s unreadable: %s", path, exc)
        return None
    if isinstance(doc, list) and doc:
        return doc[0]
    if isinstance(doc, dict):
        return doc
    return None


def _build_score_dimension(spec: dict[str, Any]) -> ScoreDimension | None:
    """Convert a rubric YAML `score_dimensions[i]` entry into a ScoreDimension.

    Returns None if required fields are missing or validation fails.
    """
    try:
        return ScoreDimension(
            dimension_id=str(spec.get("dimension_id") or spec.get("id") or ""),
            description=str(spec.get("description", "")),
            weight=float(spec.get("weight", 0.0)),
            grader_type=str(spec.get("grader_type") or "deterministic"),
            min_required_score=float(spec.get("min_required_score", -1.0)),
            evidence_required=bool(spec.get("evidence_required", True)),
            fail_closed_if_unknown=bool(spec.get("fail_closed_if_unknown", True)),
            trajectory_match_mode=str(spec.get("trajectory_match_mode", "")),
            score_bands=tuple(spec.get("score_bands", []) or []),
            taxonomy_class=str(spec.get("taxonomy_class", "")),
        )
    except (ValueError, TypeError) as exc:
        _LOGGER.warning(
            "[store_loader] ScoreDimension build failed for %s: %s",
            spec.get("dimension_id", "?"), exc,
        )
        return None


def _build_rubric_record(rubric_yaml: dict[str, Any]) -> AppEvalRubricRecord | None:
    dims = []
    for d in rubric_yaml.get("score_dimensions", []) or []:
        if not isinstance(d, dict):
            continue
        sd = _build_score_dimension(d)
        if sd is not None:
            dims.append(sd)
    if not dims:
        return None
    try:
        return AppEvalRubricRecord(
            eval_rubric_id=str(rubric_yaml.get("eval_rubric_id") or rubric_yaml.get("rubric_id", "")),
            app_id=str(rubric_yaml.get("app_id", "")),
            task_class=str(rubric_yaml.get("task_class", "")),
            version=str(rubric_yaml.get("version", "1.0.0")),
            status=str(rubric_yaml.get("status", "active")),
            policy_hash=str(rubric_yaml.get("policy_hash", "")),
            blueprint_hash=str(rubric_yaml.get("blueprint_hash", "")),
            deterministic_digest=str(rubric_yaml.get("deterministic_digest", "")),
            score_dimensions=tuple(dims),
            source_app_config_ref=str(rubric_yaml.get("source_app_config_ref", "")),
            created_at=str(rubric_yaml.get("created_at", "")),
        )
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- loader is fail-soft per-app
        _LOGGER.warning("[store_loader] rubric build failed: %s", exc)
        return None


def _build_threshold_record(
    threshold_yaml: dict[str, Any],
) -> AppThresholdProfileRecord | None:
    try:
        dim_mins = threshold_yaml.get("dimension_minimums") or {}
        if not isinstance(dim_mins, dict):
            dim_mins = {}
        return AppThresholdProfileRecord(
            threshold_profile_id=str(threshold_yaml.get("threshold_profile_id", "")),
            app_id=str(threshold_yaml.get("app_id", "")),
            task_class=str(threshold_yaml.get("task_class", "")),
            version=str(threshold_yaml.get("version", "1.0.0")),
            status=str(threshold_yaml.get("status", "active")),
            overall_pass_threshold=float(threshold_yaml.get("overall_pass_threshold", 0.75)),
            risk_tier=str(threshold_yaml.get("risk_tier", "standard")),
            route_id=str(threshold_yaml.get("route_id", "")),
            unknown_policy=str(threshold_yaml.get("unknown_policy", "fail_closed")),
            abstain_policy=str(threshold_yaml.get("abstain_policy", "soft")),
            hitl_policy=str(threshold_yaml.get("hitl_policy", "none")),
            policy_hash=str(threshold_yaml.get("policy_hash", "")),
            deterministic_digest=str(threshold_yaml.get("deterministic_digest", "")),
            dimension_minimums={str(k): float(v) for k, v in dim_mins.items()},
            source_app_config_ref=str(threshold_yaml.get("source_app_config_ref", "")),
            created_at=str(threshold_yaml.get("created_at", "")),
        )
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- loader is fail-soft per-app
        _LOGGER.warning("[store_loader] threshold build failed: %s", exc)
        return None


def _build_roster_record(
    roster_yaml: dict[str, Any],
) -> AppGraderRosterRecord | None:
    try:
        return AppGraderRosterRecord(
            grader_roster_id=str(roster_yaml.get("grader_roster_id", "")),
            app_id=str(roster_yaml.get("app_id", "")),
            task_class=str(roster_yaml.get("task_class", "")),
            version=str(roster_yaml.get("version", "1.0.0")),
            status=str(roster_yaml.get("status", "active")),
            fallback_behavior=str(roster_yaml.get("fallback_behavior", "fail_closed")),
            deterministic_digest=str(roster_yaml.get("deterministic_digest", "")),
            deterministic_graders=tuple(roster_yaml.get("deterministic_graders", []) or []),
            llm_judge_graders=tuple(roster_yaml.get("llm_judge_graders", []) or []),
            ensemble_or_consensus_graders=tuple(
                roster_yaml.get("ensemble_or_consensus_graders", []) or []
            ),
            calibration_refs=tuple(roster_yaml.get("calibration_refs", []) or []),
            source_app_config_ref=str(roster_yaml.get("source_app_config_ref", "")),
            created_at=str(roster_yaml.get("created_at", "")),
        )
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- roster is optional, loader is fail-soft
        _LOGGER.warning("[store_loader] roster build failed: %s", exc)
        return None


def load_app_into_store(
    store: InMemoryAppDomainStore, app: str,
) -> LoadReport:
    """Load a single app's domain records into `store`. Returns a LoadReport."""
    report = LoadReport(app=app)
    contract_dir = _REPO_ROOT / app / "config" / "domain_contract"

    # Rubric
    rubric_yaml = _load_first_yaml(contract_dir / "eval_rubrics.yaml")
    if rubric_yaml is None:
        report.warnings.append("eval_rubrics.yaml missing or empty")
    else:
        rubric = _build_rubric_record(rubric_yaml)
        if rubric is None:
            report.warnings.append("eval_rubrics.yaml failed to build AppEvalRubricRecord")
        else:
            store.put_eval_rubric(rubric)
            report.rubric_loaded = True
            report.rubric_id = rubric.eval_rubric_id

    # Threshold profile
    thresh_yaml = _load_first_yaml(contract_dir / "threshold_profiles.yaml")
    if thresh_yaml is None:
        report.warnings.append("threshold_profiles.yaml missing or empty")
    else:
        threshold = _build_threshold_record(thresh_yaml)
        if threshold is None:
            report.warnings.append(
                "threshold_profiles.yaml failed to build AppThresholdProfileRecord"
            )
        else:
            store.put_threshold_profile(threshold)
            report.threshold_loaded = True
            report.threshold_profile_id = threshold.threshold_profile_id

    # Grader roster (optional; evaluator tolerates missing roster lookups)
    roster_yaml = _load_first_yaml(contract_dir / "grader_roster.yaml")
    if roster_yaml is not None:
        roster = _build_roster_record(roster_yaml)
        if roster is None:
            report.warnings.append(
                "grader_roster.yaml failed to build AppGraderRosterRecord"
            )
        else:
            store.put_grader_roster(roster)
            report.grader_roster_loaded = True
            report.grader_roster_id = roster.grader_roster_id

    return report


def build_harness_store(
    apps: Iterable[str],
) -> tuple[InMemoryAppDomainStore, list[LoadReport]]:
    """Return a fresh store populated with every app's records + per-app reports."""
    store = InMemoryAppDomainStore()
    reports = [load_app_into_store(store, app) for app in apps]
    return store, reports


def build_harness_evaluator(
    apps: Iterable[str],
) -> tuple[AppSpecificEvaluator, list[LoadReport]]:
    """Convenience: return an AppSpecificEvaluator wired to a harness-loaded store.

    The evaluator will now resolve every app's rubric_ref + threshold_profile_ref
    successfully, allowing real per-dim verdicts against real rubric config.
    """
    store, reports = build_harness_store(apps)
    # Match build_default_app_evaluator: read_dim_score_from_output is the
    # fallback grader, reading scores from run_context.output.dim_scores[dim].
    # Combined with our populated store, the evaluator now behaves exactly
    # like production — just with records loaded from on-disk YAML instead
    # of from an in-memory init step.
    evaluator = AppSpecificEvaluator(
        store=store,
        default_grader=read_dim_score_from_output,
    )
    return evaluator, reports


__all__ = [
    "LoadReport",
    "build_harness_store",
    "build_harness_evaluator",
    "load_app_into_store",
]
