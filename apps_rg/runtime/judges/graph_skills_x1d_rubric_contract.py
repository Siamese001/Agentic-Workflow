"""X1D rubric port audit — graph-skills quality W4 (no masking)."""
from __future__ import annotations

import hashlib
import importlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"
MIN_PASS_THRESHOLD = 0.80
NON_CLAIM_NO_MASKING = (
    "Rubric port did not relax groundedness, specificity, or citation thresholds."
)

# Appendix W4 — per lane-family marker groups (any alias in a group must match).
FAMILY_MARKER_GROUPS: dict[str, tuple[tuple[str, ...], ...]] = {
    "executive_summary": (
        ("factual_support",),
        ("claim_ledger", "claim ledger"),
        ("jd-as-proof", "jd/briefing", "jd as proof"),
        ("briefing-as-proof", "briefing"),
        ("keyword", "stuffing"),
        ("decisive_failure",),
        ("source_fact", "source fact"),
    ),
    "headline": (
        ("factual_support",),
        ("claim_ledger", "claim ledger"),
        ("jd-as-proof", "jd ", "targeting"),
        ("briefing",),
        ("keyword", "stuffing"),
        ("decisive_failure",),
        ("source_fact", "source_fact", "bul_", "fact_"),
    ),
    "narrative": (
        ("factual_support", "fact_ledger_grounding"),
        ("claim_ledger", "claim ledger"),
        ("jd-as-proof", "jd/briefing", "jd ", "briefing"),
        ("keyword", "stuffing", "without_stuffing", "without becoming proof", "not proof"),
        ("decisive_failure",),
        ("source_fact", "source fact", "bul_", "resume facts"),
    ),
    "bullets": (
        ("factual_support",),
        ("claim_ledger", "claim ledger"),
        ("jd-as-proof", "jd-as-proof"),
        ("briefing-as-proof", "briefing"),
        ("keyword", "stuffing"),
        ("decisive_failure",),
        ("source_fact", "source_fact", "bul_"),
    ),
    "competencies": (
        ("factual_support",),
        ("claim_ledger", "claim ledger"),
        ("jd-as-proof", "jd-as-proof"),
        ("briefing",),
        ("keyword", "stuffing"),
        ("decisive_failure",),
        ("source_fact", "source_fact", "bul_"),
    ),
}

FORBIDDEN_RELAXATION_MARKERS: tuple[str, ...] = (
    "lower threshold",
    "relax threshold",
    "ignore unsupported",
    "optional factual",
    "jd may be used as proof",
    "briefing as proof allowed",
)


@dataclass(frozen=True, slots=True)
class LaneRubricSource:
    lane_family: str
    lane_id: str
    module_path: str
    rubric_version: str
    rubric_text: str
    default_threshold: float
    rubric_sha256: str
    dimension_count: int
    decisive_trigger_count: int
    missing_markers: tuple[str, ...]
    forbidden_markers_found: tuple[str, ...]


LANE_RUBRIC_MODULES: tuple[tuple[str, str, str], ...] = (
    ("executive_summary", "executive_summary", "apps_rg.runtime.judges.executive_summary_x1d"),
    ("headline", "headline", "apps_rg.runtime.judges.headline_x1d"),
    ("narrative", "unify_narrative", "apps_rg.runtime.judges.unify_narrative_x1d"),
    ("narrative", "ibm_narrative", "apps_rg.runtime.judges.ibm_narrative_x1d"),
    ("bullets", "unify_bullets", "apps_rg.runtime.judges.unify_bullets_x1d"),
    ("bullets", "ibm_bullets", "apps_rg.runtime.judges.ibm_bullets_x1d"),
    ("competencies", "competencies", "apps_rg.runtime.judges.competencies_x1d"),
)

RUBRIC_TEXT_ATTR: dict[str, str] = {
    "apps_rg.runtime.judges.executive_summary_x1d": "RUBRIC",
    "apps_rg.runtime.judges.headline_x1d": "HEADLINE_RUBRIC",
    "apps_rg.runtime.judges.unify_narrative_x1d": "NARRATIVE_RUBRIC",
    "apps_rg.runtime.judges.ibm_narrative_x1d": "NARRATIVE_RUBRIC",
    "apps_rg.runtime.judges.unify_bullets_x1d": "UNIFY_RUBRIC",
    "apps_rg.runtime.judges.ibm_bullets_x1d": "IBM_RUBRIC",
    "apps_rg.runtime.judges.competencies_x1d": "COMPETENCIES_RUBRIC",
}


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _count_dimensions(rubric: str) -> int:
    return len(re.findall(r"^\s*\d+\.\s+\w+", rubric, flags=re.MULTILINE))


def _count_decisive_triggers(rubric: str) -> int:
    block = rubric.lower()
    if "decisive failure" not in block:
        return 0
    tail = block.split("decisive failure", 1)[-1]
    return len(re.findall(r"^\s*-\s+", tail, flags=re.MULTILINE))


def _missing_markers(rubric: str, *, lane_family: str) -> list[str]:
    lower = rubric.lower()
    groups = FAMILY_MARKER_GROUPS.get(lane_family, FAMILY_MARKER_GROUPS["executive_summary"])
    missing: list[str] = []
    for idx, aliases in enumerate(groups):
        if not any(alias.lower() in lower for alias in aliases):
            missing.append(f"group_{idx}:{aliases[0]}")
    return missing


def _forbidden_markers(rubric: str) -> list[str]:
    lower = rubric.lower()
    return [m for m in FORBIDDEN_RELAXATION_MARKERS if m in lower]


def load_lane_rubric_source(family: str, lane_id: str, module_path: str) -> LaneRubricSource:
    mod = importlib.import_module(module_path)
    attr = RUBRIC_TEXT_ATTR.get(module_path, "RUBRIC")
    rubric = str(getattr(mod, attr, "") or "").strip()
    version = str(getattr(mod, "JUDGE_RUBRIC_VERSION", "") or "")
    threshold = float(getattr(mod, "DEFAULT_THRESHOLD", MIN_PASS_THRESHOLD))
    missing = _missing_markers(rubric, lane_family=family)
    forbidden = _forbidden_markers(rubric)
    return LaneRubricSource(
        lane_family=family,
        lane_id=lane_id,
        module_path=module_path,
        rubric_version=version,
        rubric_text=rubric,
        default_threshold=threshold,
        rubric_sha256=_sha256_text(rubric),
        dimension_count=_count_dimensions(rubric),
        decisive_trigger_count=_count_decisive_triggers(rubric),
        missing_markers=tuple(missing),
        forbidden_markers_found=tuple(forbidden),
    )


def collect_current_rubric_snapshots() -> list[LaneRubricSource]:
    return [load_lane_rubric_source(f, lane, mod) for f, lane, mod in LANE_RUBRIC_MODULES]


def snapshots_to_baseline_dict(snapshots: list[LaneRubricSource]) -> dict[str, Any]:
    families: dict[str, Any] = {}
    for snap in snapshots:
        fam = families.setdefault(
            snap.lane_family,
            {"lane_family": snap.lane_family, "lanes": [], "masking_relaxed": False},
        )
        fam["lanes"].append(
            {
                "lane_id": snap.lane_id,
                "module_path": snap.module_path,
                "rubric_version": snap.rubric_version,
                "default_threshold": snap.default_threshold,
                "rubric_sha256": snap.rubric_sha256,
                "dimension_count": snap.dimension_count,
                "decisive_trigger_count": snap.decisive_trigger_count,
                "required_markers_present": not snap.missing_markers,
                "missing_markers": list(snap.missing_markers),
            }
        )
    return {
        "schema": "graph_skills_x1d_rubric_baseline_w4_v1",
        "plan_id": PLAN_ID,
        "min_pass_threshold": MIN_PASS_THRESHOLD,
        "lane_families": families,
    }


def default_baseline_path(repo_root: Path) -> Path:
    return repo_root / "apps_rg/runtime/judges/graph_skills_x1d_rubric_baseline_w4.json"


def build_rubric_port_diff(
    *,
    repo_root: Path,
    baseline_path: Path | None = None,
) -> dict[str, Any]:
    """Compare current rubrics to frozen baseline; detect threshold/marker regressions."""
    baseline_file = baseline_path or default_baseline_path(repo_root)
    current = collect_current_rubric_snapshots()
    current_by_lane = {s.lane_id: s for s in current}

    if not baseline_file.is_file():
        baseline_payload = snapshots_to_baseline_dict(current)
        baseline_file.parent.mkdir(parents=True, exist_ok=True)
        baseline_file.write_text(json.dumps(baseline_payload, indent=2) + "\n", encoding="utf-8")
        baseline = baseline_payload
    else:
        baseline = json.loads(baseline_file.read_text(encoding="utf-8"))

    family_diffs: list[dict[str, Any]] = []
    any_relaxed = False
    invariant_failures: list[str] = []

    for snap in current:
        if snap.default_threshold < MIN_PASS_THRESHOLD:
            invariant_failures.append(f"{snap.lane_id}: threshold {snap.default_threshold} < {MIN_PASS_THRESHOLD}")
        if snap.missing_markers:
            invariant_failures.append(f"{snap.lane_id}: missing markers {snap.missing_markers}")
        if snap.forbidden_markers_found:
            invariant_failures.append(f"{snap.lane_id}: forbidden markers {snap.forbidden_markers_found}")

    for family, fam_blob in (baseline.get("lane_families") or {}).items():
        lanes_before = {row["lane_id"]: row for row in (fam_blob.get("lanes") or []) if isinstance(row, dict)}
        lanes_after: list[dict[str, Any]] = []
        family_relaxed = False
        for lane_id, before in lanes_before.items():
            after_snap = current_by_lane.get(lane_id)
            if after_snap is None:
                family_relaxed = True
                lanes_after.append({"lane_id": lane_id, "status": "MISSING_MODULE", "masking_relaxed": True})
                continue
            after_row = {
                "lane_id": lane_id,
                "rubric_version_before": before.get("rubric_version"),
                "rubric_version_after": after_snap.rubric_version,
                "threshold_before": before.get("default_threshold"),
                "threshold_after": after_snap.default_threshold,
                "rubric_sha256_before": before.get("rubric_sha256"),
                "rubric_sha256_after": after_snap.rubric_sha256,
                "dimension_count_before": before.get("dimension_count"),
                "dimension_count_after": after_snap.dimension_count,
                "decisive_trigger_count_before": before.get("decisive_trigger_count"),
                "decisive_trigger_count_after": after_snap.decisive_trigger_count,
            }
            relaxed = False
            if float(after_snap.default_threshold) < float(before.get("default_threshold") or MIN_PASS_THRESHOLD):
                relaxed = True
            if after_snap.dimension_count < int(before.get("dimension_count") or 0):
                relaxed = True
            if after_snap.decisive_trigger_count < int(before.get("decisive_trigger_count") or 0):
                relaxed = True
            if after_snap.rubric_sha256 != before.get("rubric_sha256"):
                # Hash change is not automatically relaxation — flag for human review only when thresholds dropped
                after_row["rubric_text_changed"] = True
            after_row["masking_relaxed"] = relaxed
            if relaxed:
                family_relaxed = True
            lanes_after.append(after_row)
        family_diffs.append(
            {
                "lane_family": family,
                "lanes": lanes_after,
                "masking_relaxed": family_relaxed,
            }
        )
        if family_relaxed:
            any_relaxed = True

    status = "PASS"
    if any_relaxed or invariant_failures:
        status = "FAIL"

    return {
        "schema": "graph_skills_x1d_rubric_port_diff_v1",
        "plan_id": PLAN_ID,
        "wave": "W4",
        "status": status,
        "non_claim": NON_CLAIM_NO_MASKING,
        "baseline_path": baseline_file.relative_to(repo_root).as_posix()
        if baseline_file.is_relative_to(repo_root)
        else str(baseline_file),
        "lane_families": family_diffs,
        "any_masking_relaxed": any_relaxed,
        "invariant_failures": invariant_failures,
        "current_snapshots": [
            {
                "lane_id": s.lane_id,
                "lane_family": s.lane_family,
                "rubric_version": s.rubric_version,
                "default_threshold": s.default_threshold,
                "rubric_sha256": s.rubric_sha256,
                "dimension_count": s.dimension_count,
                "decisive_trigger_count": s.decisive_trigger_count,
            }
            for s in current
        ],
    }


__all__ = [
    "MIN_PASS_THRESHOLD",
    "NON_CLAIM_NO_MASKING",
    "build_rubric_port_diff",
    "collect_current_rubric_snapshots",
    "default_baseline_path",
]
