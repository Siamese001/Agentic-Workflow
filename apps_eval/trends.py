"""Historical trend dashboard and release gate for apps_eval."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_eval.contracts import (
    ReleaseGateDecision,
    TrendDashboardSummary,
    TrendSample,
    TrendSuiteSummary,
)
from apps_eval.l6_shadow_bridge import L6_SHADOW_BRIDGE_ARTIFACT, emit_driver_l6_shadow_bridge


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected object in {path}")
    return data


def _canonical_digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _suite_split(suite_id: str) -> str:
    parts = suite_id.split(".")
    if len(parts) >= 3:
        return parts[1]
    return ""


def _sample_sort_key(sample: TrendSample) -> tuple[str, str, str]:
    return sample.created_at, sample.record_id, sample.record_path


def _counter_dict(counter: Counter[str]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def _dominant_key(counts: dict[str, int]) -> str:
    if not counts:
        return ""
    max_count = max(counts.values())
    return sorted(key for key, count in counts.items() if count == max_count)[0]


def _discover_eval_record_paths(records_root: Path) -> list[Path]:
    if not records_root.exists():
        return []
    return sorted(
        (path for path in records_root.rglob("eval_record.json") if path.is_file()),
        key=lambda path: path.as_posix(),
    )


def _int_count_map(payload: Any) -> dict[str, int]:
    if not isinstance(payload, dict):
        return {}
    result: dict[str, int] = {}
    for key, value in payload.items():
        try:
            result[str(key)] = int(value)
        except (TypeError, ValueError):
            continue
    return result


def _sample_from_record(path: Path, record: dict[str, Any]) -> TrendSample:
    suite_id = str(record.get("suite_id", ""))
    app_id = str(record.get("app_id", ""))
    created_at = str(record.get("created_at", ""))
    record_id = str(record.get("record_id", ""))
    if not suite_id:
        raise ValueError(f"missing suite_id in {path}")
    if not app_id:
        raise ValueError(f"missing app_id in {path}")
    if not created_at:
        raise ValueError(f"missing created_at in {path}")
    if not record_id:
        raise ValueError(f"missing record_id in {path}")

    scorecard = dict(record.get("scorecard") or {})
    regression = dict(record.get("regression") or {})
    run_metadata = dict(record.get("run_metadata") or {})
    failure_mode_counts = _int_count_map(scorecard.get("failure_mode_counts"))
    failure_family_counts = _int_count_map(scorecard.get("failure_family_counts"))
    dominant_failure_mode = _dominant_key(failure_mode_counts)
    dominant_failure_family = _dominant_key(failure_family_counts)
    score = float(scorecard.get("score", 0.0))
    block_failures = int(scorecard.get("block_failures", 0))

    return TrendSample(
        record_id=record_id,
        suite_id=suite_id,
        app_id=app_id,
        split=_suite_split(suite_id),
        created_at=created_at,
        score=score,
        scorecard_verdict=str(scorecard.get("verdict", "")),
        regression_verdict=str(regression.get("verdict", "")),
        block_failures=block_failures,
        dominant_failure_mode=dominant_failure_mode,
        dominant_failure_family=dominant_failure_family,
        record_seed_digest=str(run_metadata.get("record_seed_digest", "")),
        record_path=path.as_posix(),
        failure_mode_counts=failure_mode_counts,
        failure_family_counts=failure_family_counts,
    )


def _suite_summary_from_samples(
    suite_id: str,
    samples: list[TrendSample],
    window_size: int,
) -> TrendSuiteSummary:
    ordered = sorted(samples, key=_sample_sort_key)
    if not ordered:
        return TrendSuiteSummary(suite_id=suite_id, app_id="", split="", sample_count=0)

    window = ordered[-window_size:] if window_size < len(ordered) else list(ordered)
    latest = ordered[-1]
    previous = ordered[-2] if len(ordered) >= 2 else latest
    window_pass_count = sum(1 for sample in window if sample.scorecard_verdict == "pass")
    window_regression_count = sum(1 for sample in window if sample.regression_verdict == "regression")
    failure_mode_counts: Counter[str] = Counter()
    failure_family_counts: Counter[str] = Counter()
    for sample in ordered:
        failure_mode_counts.update(sample.failure_mode_counts)
        failure_family_counts.update(sample.failure_family_counts)

    latest_score = round(float(latest.score), 6)
    previous_score = round(float(previous.score), 6)
    score_delta = round(latest_score - previous_score, 6)
    if score_delta > 0.000001:
        trend_direction = "improving"
    elif score_delta < -0.000001:
        trend_direction = "degrading"
    else:
        trend_direction = "stable"

    return TrendSuiteSummary(
        suite_id=suite_id,
        app_id=latest.app_id,
        split=latest.split,
        sample_count=len(ordered),
        latest_record_id=latest.record_id,
        latest_created_at=latest.created_at,
        latest_score=latest_score,
        previous_score=previous_score,
        score_delta=score_delta,
        latest_scorecard_verdict=latest.scorecard_verdict,
        latest_regression_verdict=latest.regression_verdict,
        window_pass_rate=round(window_pass_count / len(window), 6),
        window_regression_rate=round(window_regression_count / len(window), 6),
        trend_direction=trend_direction,
        dominant_failure_mode=_dominant_key(_counter_dict(failure_mode_counts)),
        dominant_failure_family=_dominant_key(_counter_dict(failure_family_counts)),
        failure_mode_counts=_counter_dict(failure_mode_counts),
        failure_family_counts=_counter_dict(failure_family_counts),
        score_series=[round(float(sample.score), 6) for sample in window],
        verdict_series=[sample.scorecard_verdict for sample in window],
        regression_series=[sample.regression_verdict for sample in window],
        record_paths=[sample.record_path for sample in window],
    )


def _stable_trend_id(
    *,
    records_root: Path,
    app_id: str,
    split: str,
    window_size: int,
    history_limit: int,
    samples: list[TrendSample],
) -> str:
    payload = {
        "records_root": records_root.resolve().as_posix(),
        "app_id": app_id,
        "split": split,
        "window_size": window_size,
        "history_limit": history_limit,
        "samples": [
            {
                "record_id": sample.record_id,
                "created_at": sample.created_at,
                "score": sample.score,
                "scorecard_verdict": sample.scorecard_verdict,
                "regression_verdict": sample.regression_verdict,
                "record_seed_digest": sample.record_seed_digest,
                "record_path": sample.record_path,
            }
            for sample in samples
        ],
    }
    return _canonical_digest(payload)[:16]


def _stable_gate_id(
    *,
    trend_id: str,
    min_samples: int,
    min_latest_pass_rate: float,
    min_window_pass_rate: float,
    max_latest_score_drop: float,
) -> str:
    payload = {
        "trend_id": trend_id,
        "min_samples": min_samples,
        "min_latest_pass_rate": min_latest_pass_rate,
        "min_window_pass_rate": min_window_pass_rate,
        "max_latest_score_drop": max_latest_score_drop,
    }
    return _canonical_digest(payload)[:16]


def _build_suite_checks(
    dashboard: TrendDashboardSummary,
    *,
    min_samples: int,
    min_window_pass_rate: float,
    max_latest_score_drop: float,
) -> tuple[list[dict[str, Any]], list[str], bool]:
    suite_checks: list[dict[str, Any]] = []
    blocking_suite_ids: list[str] = []
    regression_detected = False
    for suite in dashboard.suite_summaries:
        reasons: list[str] = []
        status = "pass"
        score_drop = round(max(0.0, suite.previous_score - suite.latest_score), 6)
        regression_blocking = False
        if suite.sample_count < min_samples:
            reasons.append(f"insufficient samples: {suite.sample_count} < {min_samples}")
        else:
            if suite.latest_scorecard_verdict != "pass":
                reasons.append(f"latest scorecard verdict: {suite.latest_scorecard_verdict}")
            if suite.latest_regression_verdict == "regression":
                reasons.append("latest regression verdict: regression")
                regression_blocking = True
            if suite.window_pass_rate < min_window_pass_rate:
                reasons.append(
                    "window pass rate: "
                    f"{suite.window_pass_rate:.6f} < {min_window_pass_rate:.6f}"
                )
            if score_drop > max_latest_score_drop + 1e-12:
                reasons.append(f"latest score drop: {score_drop:.6f} > {max_latest_score_drop:.6f}")
                regression_blocking = True
        if reasons:
            blocking_suite_ids.append(suite.suite_id)
            status = "regression" if regression_blocking else "blocked"
            if regression_blocking:
                regression_detected = True
        suite_checks.append(
            {
                "suite_id": suite.suite_id,
                "app_id": suite.app_id,
                "split": suite.split,
                "sample_count": suite.sample_count,
                "latest_record_id": suite.latest_record_id,
                "latest_created_at": suite.latest_created_at,
                "latest_score": suite.latest_score,
                "previous_score": suite.previous_score,
                "score_delta": suite.score_delta,
                "score_drop": score_drop,
                "latest_scorecard_verdict": suite.latest_scorecard_verdict,
                "latest_regression_verdict": suite.latest_regression_verdict,
                "window_pass_rate": suite.window_pass_rate,
                "window_regression_rate": suite.window_regression_rate,
                "trend_direction": suite.trend_direction,
                "dominant_failure_mode": suite.dominant_failure_mode,
                "dominant_failure_family": suite.dominant_failure_family,
                "reasons": reasons,
                "status": status,
                "record_paths": list(suite.record_paths),
            }
        )
    return suite_checks, blocking_suite_ids, regression_detected


def build_trend_dashboard(
    *,
    records_root: str | Path,
    app_id: str = "",
    split: str = "",
    window_size: int = 5,
    history_limit: int = 20,
) -> TrendDashboardSummary:
    if window_size < 1:
        raise ValueError("window_size must be >= 1")
    if history_limit < 1:
        raise ValueError("history_limit must be >= 1")

    records_root_path = Path(records_root)
    samples: list[TrendSample] = []
    for record_path in _discover_eval_record_paths(records_root_path):
        record = _load_json(record_path)
        sample = _sample_from_record(record_path, record)
        if app_id and sample.app_id != app_id:
            continue
        if split and sample.split != split:
            continue
        samples.append(sample)

    samples = sorted(samples, key=_sample_sort_key)
    suite_groups: dict[tuple[str, str, str], list[TrendSample]] = defaultdict(list)
    for sample in samples:
        suite_groups[(sample.suite_id, sample.app_id, sample.split)].append(sample)

    suite_summaries = [
        _suite_summary_from_samples(suite_id, grouped_samples, window_size)
        for (suite_id, _app_id, _split), grouped_samples in suite_groups.items()
    ]
    suite_summaries = sorted(
        suite_summaries,
        key=lambda summary: (
            summary.latest_created_at or "",
            summary.latest_record_id or "",
            summary.suite_id,
        ),
        reverse=True,
    )

    mode_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    for sample in samples:
        mode_counts.update(sample.failure_mode_counts)
        family_counts.update(sample.failure_family_counts)

    latest_samples = sorted(samples, key=_sample_sort_key, reverse=True)
    latest_sample = latest_samples[0] if latest_samples else None
    latest_suite_summary = None
    if latest_sample is not None:
        for summary in suite_summaries:
            if summary.suite_id == latest_sample.suite_id:
                latest_suite_summary = summary
                break

    latest_pass_rate = (
        round(sum(1 for summary in suite_summaries if summary.latest_scorecard_verdict == "pass") / len(suite_summaries), 6)
        if suite_summaries
        else 0.0
    )
    latest_regression_rate = (
        round(
            sum(1 for summary in suite_summaries if summary.latest_regression_verdict == "regression")
            / len(suite_summaries),
            6,
        )
        if suite_summaries
        else 0.0
    )
    overall_pass_rate = round(sum(1 for sample in samples if sample.scorecard_verdict == "pass") / len(samples), 6) if samples else 0.0
    overall_regression_rate = (
        round(sum(1 for sample in samples if sample.regression_verdict == "regression") / len(samples), 6)
        if samples
        else 0.0
    )
    trend_id = _stable_trend_id(
        records_root=records_root_path,
        app_id=app_id,
        split=split,
        window_size=window_size,
        history_limit=history_limit,
        samples=samples,
    )

    return TrendDashboardSummary(
        generated_at=_now(),
        trend_id=trend_id,
        records_root=records_root_path.resolve().as_posix(),
        app_id=app_id,
        split=split,
        window_size=window_size,
        history_limit=history_limit,
        sample_count=len(samples),
        suite_count=len(suite_summaries),
        latest_pass_rate=latest_pass_rate,
        latest_regression_rate=latest_regression_rate,
        overall_pass_rate=overall_pass_rate,
        overall_regression_rate=overall_regression_rate,
        latest_record_id=latest_sample.record_id if latest_sample else "",
        latest_suite_id=latest_sample.suite_id if latest_sample else "",
        latest_created_at=latest_sample.created_at if latest_sample else "",
        latest_score=round(latest_sample.score, 6) if latest_sample else 0.0,
        latest_scorecard_verdict=latest_sample.scorecard_verdict if latest_sample else "",
        latest_regression_verdict=latest_sample.regression_verdict if latest_sample else "",
        latest_trend_direction=latest_suite_summary.trend_direction if latest_suite_summary else "stable",
        dominant_failure_mode=_dominant_key(_counter_dict(mode_counts)),
        dominant_failure_family=_dominant_key(_counter_dict(family_counts)),
        failure_mode_counts=_counter_dict(mode_counts),
        failure_family_counts=_counter_dict(family_counts),
        suite_summaries=suite_summaries,
        samples=latest_samples[:history_limit],
    )


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _format_rate(value: float) -> str:
    return f"{value:.2%}"


def render_trend_dashboard(dashboard: TrendDashboardSummary) -> str:
    lines = [
        f"# apps_eval trend dashboard: {dashboard.trend_id}",
        "",
        "## Scope",
        "",
        f"Schema version: `{dashboard.schema_version}`",
        f"Generated at: `{dashboard.generated_at}`",
        f"Trend digest: `{dashboard.trend_dashboard_digest or 'n/a'}`",
        f"Records root: `{dashboard.records_root}`",
        f"App filter: `{dashboard.app_id or 'all'}`",
        f"Split filter: `{dashboard.split or 'all'}`",
        f"Window size: `{dashboard.window_size}`",
        f"History limit: `{dashboard.history_limit}`",
        f"Samples scanned: `{dashboard.sample_count}`",
        f"Suites scanned: `{dashboard.suite_count}`",
        "",
        "## Overall Signals",
        "",
        f"Latest pass rate: `{_format_rate(dashboard.latest_pass_rate)}`",
        f"Latest regression rate: `{_format_rate(dashboard.latest_regression_rate)}`",
        f"Overall pass rate: `{_format_rate(dashboard.overall_pass_rate)}`",
        f"Overall regression rate: `{_format_rate(dashboard.overall_regression_rate)}`",
        f"Latest suite: `{dashboard.latest_suite_id or 'n/a'}`",
        f"Latest score: `{dashboard.latest_score:.6f}`",
        f"Latest verdict: `{dashboard.latest_scorecard_verdict or 'n/a'}`",
        f"Latest regression verdict: `{dashboard.latest_regression_verdict or 'n/a'}`",
        f"Latest trend direction: `{dashboard.latest_trend_direction or 'stable'}`",
        f"Dominant failure family: `{dashboard.dominant_failure_family or 'n/a'}`",
        f"Dominant failure mode: `{dashboard.dominant_failure_mode or 'n/a'}`",
        "",
        "## Suite Trends",
        "",
        "| Suite | App | Split | Samples | Latest Score | Delta | Latest Verdict | Regression Verdict | Window Pass Rate | Trend | Dominant Failure Mode |",
        "|---|---|---|---:|---:|---:|---|---|---:|---|---|",
    ]
    if dashboard.suite_summaries:
        for suite in dashboard.suite_summaries:
            lines.append(
                "| {suite} | {app} | {split} | {samples} | {score:.6f} | {delta:.6f} | {verdict} | {regression} | {window:.2%} | {trend} | {mode} |".format(
                    suite=_cell(suite.suite_id),
                    app=_cell(suite.app_id),
                    split=_cell(suite.split or "n/a"),
                    samples=suite.sample_count,
                    score=suite.latest_score,
                    delta=suite.score_delta,
                    verdict=_cell(suite.latest_scorecard_verdict or "n/a"),
                    regression=_cell(suite.latest_regression_verdict or "n/a"),
                    window=suite.window_pass_rate,
                    trend=_cell(suite.trend_direction),
                    mode=_cell(suite.dominant_failure_mode or "n/a"),
                )
            )
    else:
        lines.append("| _none_ | _none_ | _none_ | 0 | 0.000000 | 0.000000 | _n/a_ | _n/a_ | 0.00% | stable | _n/a_ |")
    lines.extend(
        [
            "",
            "## Failure Families",
            "",
            "| Family | Count |",
            "|---|---:|",
        ]
    )
    if dashboard.failure_family_counts:
        for family, count in sorted(dashboard.failure_family_counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"| {_cell(family)} | {count} |")
    else:
        lines.append("| _none_ | 0 |")
    lines.extend(
        [
            "",
            "## Failure Modes",
            "",
            "| Mode | Count |",
            "|---|---:|",
        ]
    )
    if dashboard.failure_mode_counts:
        for mode, count in sorted(dashboard.failure_mode_counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"| {_cell(mode)} | {count} |")
    else:
        lines.append("| _none_ | 0 |")
    lines.extend(
        [
            "",
            "## Recent Samples",
            "",
            "| Created At | Suite | Score | Verdict | Regression | Block Failures | Record |",
            "|---|---|---:|---|---|---:|---|",
        ]
    )
    if dashboard.samples:
        for sample in dashboard.samples:
            lines.append(
                f"| {_cell(sample.created_at)} | {_cell(sample.suite_id)} | {sample.score:.6f} | "
                f"{_cell(sample.scorecard_verdict or 'n/a')} | {_cell(sample.regression_verdict or 'n/a')} | "
                f"{sample.block_failures} | `{_cell(sample.record_path)}` |"
            )
    else:
        lines.append("| _none_ | _none_ | 0.000000 | _n/a_ | _n/a_ | 0 | _n/a_ |")
    return "\n".join(lines)


def evaluate_release_gate(
    dashboard: TrendDashboardSummary,
    *,
    min_samples: int = 2,
    min_latest_pass_rate: float = 1.0,
    min_window_pass_rate: float = 1.0,
    max_latest_score_drop: float = 0.05,
) -> ReleaseGateDecision:
    suite_checks, blocking_suite_ids, regression_detected = _build_suite_checks(
        dashboard,
        min_samples=min_samples,
        min_window_pass_rate=min_window_pass_rate,
        max_latest_score_drop=max_latest_score_drop,
    )
    reasons: list[str] = []
    if dashboard.sample_count == 0:
        reasons.append("no eval records found")
    if dashboard.latest_pass_rate < min_latest_pass_rate:
        reasons.append(
            f"latest pass rate: {dashboard.latest_pass_rate:.6f} < {min_latest_pass_rate:.6f}"
        )
    if dashboard.latest_regression_rate > 0.0:
        reasons.append(
            f"latest regression rate: {dashboard.latest_regression_rate:.6f} > 0.000000"
        )
    for suite_check in suite_checks:
        if suite_check["reasons"]:
            reasons.append(
                f"{suite_check['suite_id']}: " + "; ".join(suite_check["reasons"])
            )
    status = "pass"
    if reasons:
        status = "regression" if regression_detected else "blocked"

    gate_id = _stable_gate_id(
        trend_id=dashboard.trend_id,
        min_samples=min_samples,
        min_latest_pass_rate=min_latest_pass_rate,
        min_window_pass_rate=min_window_pass_rate,
        max_latest_score_drop=max_latest_score_drop,
    )
    return ReleaseGateDecision(
        generated_at=_now(),
        gate_id=gate_id,
        status=status,
        records_root=dashboard.records_root,
        app_id=dashboard.app_id,
        split=dashboard.split,
        trend_id=dashboard.trend_id,
        trend_dashboard_path=dashboard.artifact_paths.get("trend_dashboard", ""),
        trend_dashboard_digest=dashboard.artifact_paths.get("trend_dashboard_digest", ""),
        window_size=dashboard.window_size,
        history_limit=dashboard.history_limit,
        min_samples=min_samples,
        min_latest_pass_rate=min_latest_pass_rate,
        min_window_pass_rate=min_window_pass_rate,
        max_latest_score_drop=max_latest_score_drop,
        sample_count=dashboard.sample_count,
        suite_count=dashboard.suite_count,
        latest_pass_rate=dashboard.latest_pass_rate,
        latest_regression_rate=dashboard.latest_regression_rate,
        overall_pass_rate=dashboard.overall_pass_rate,
        overall_regression_rate=dashboard.overall_regression_rate,
        blocking_suite_ids=blocking_suite_ids,
        reasons=reasons,
        suite_checks=suite_checks,
    )


def render_release_gate(decision: ReleaseGateDecision) -> str:
    lines = [
        f"# apps_eval release gate: {decision.gate_id}",
        "",
        "## Status",
        "",
        f"Schema version: `{decision.schema_version}`",
        f"Generated at: `{decision.generated_at}`",
        f"Status: `{decision.status}`",
        f"Records root: `{decision.records_root}`",
        f"App filter: `{decision.app_id or 'all'}`",
        f"Split filter: `{decision.split or 'all'}`",
        f"Trend dashboard: `{decision.trend_dashboard_path or 'n/a'}`",
        f"Trend dashboard digest: `{decision.trend_dashboard_digest or 'n/a'}`",
        f"Sample count: `{decision.sample_count}`",
        f"Suite count: `{decision.suite_count}`",
        f"Latest pass rate: `{_format_rate(decision.latest_pass_rate)}`",
        f"Latest regression rate: `{_format_rate(decision.latest_regression_rate)}`",
        f"Overall pass rate: `{_format_rate(decision.overall_pass_rate)}`",
        f"Overall regression rate: `{_format_rate(decision.overall_regression_rate)}`",
        "",
        "## Thresholds",
        "",
        f"Min samples: `{decision.min_samples}`",
        f"Min latest pass rate: `{_format_rate(decision.min_latest_pass_rate)}`",
        f"Min window pass rate: `{_format_rate(decision.min_window_pass_rate)}`",
        f"Max latest score drop: `{decision.max_latest_score_drop:.6f}`",
        "",
        "## Blocking Reasons",
        "",
    ]
    if decision.reasons:
        for reason in decision.reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- _none_")
    lines.extend(
        [
            "",
            "## Suite Checks",
            "",
            "| Suite | Status | Latest Verdict | Window Pass Rate | Score Drop | Reasons |",
            "|---|---|---|---:|---:|---|",
        ]
    )
    if decision.suite_checks:
        for suite_check in decision.suite_checks:
            reasons = "; ".join(suite_check.get("reasons", [])) or "n/a"
            lines.append(
                f"| {_cell(suite_check.get('suite_id', ''))} | {_cell(suite_check.get('status', ''))} | "
                f"{_cell(suite_check.get('latest_scorecard_verdict', ''))} | {suite_check.get('window_pass_rate', 0.0):.2%} | "
                f"{suite_check.get('score_drop', 0.0):.6f} | {_cell(reasons)} |"
            )
    else:
        lines.append("| _none_ | _none_ | _n/a_ | 0.00% | 0.000000 | _n/a_ |")
    lines.extend(
        [
            "",
            "## Blocking Suites",
            "",
        ]
    )
    if decision.blocking_suite_ids:
        for suite_id in decision.blocking_suite_ids:
            lines.append(f"- `{suite_id}`")
    else:
        lines.append("- _none_")
    lines.extend(
        [
            "",
            "## Artifact Inventory",
            "",
        ]
    )
    for key, value in sorted(decision.artifact_paths.items()):
        lines.append(f"- `{key}`: `{value}`")
    return "\n".join(lines)


def _write_dashboard_artifacts(
    dashboard: TrendDashboardSummary,
    *,
    out_dir: str | Path,
    extra_artifact_paths: dict[str, str] | None = None,
) -> TrendDashboardSummary:
    output_dir = Path(out_dir) / dashboard.trend_id
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "trend_dashboard.json"
    md_path = output_dir / "trend_dashboard.md"
    artifact_paths = {
        "trend_dashboard": json_path.as_posix(),
        "trend_dashboard_report": md_path.as_posix(),
    }
    if extra_artifact_paths:
        artifact_paths.update(extra_artifact_paths)
    dashboard = replace(
        dashboard,
        artifact_paths=artifact_paths,
    )
    json_path.write_text(json.dumps(dashboard.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    digest = _canonical_digest(json.loads(json_path.read_text(encoding="utf-8")))
    dashboard = replace(
        dashboard,
        trend_dashboard_digest=digest,
    )
    json_path.write_text(json.dumps(dashboard.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_trend_dashboard(dashboard), encoding="utf-8")
    return dashboard


def emit_trend_dashboard(
    *,
    records_root: str | Path,
    app_id: str = "",
    split: str = "",
    window_size: int = 5,
    history_limit: int = 20,
    out_dir: str | Path = "artifacts/apps_eval/trends",
    emit_l6_shadow: bool = False,
) -> TrendDashboardSummary:
    dashboard = build_trend_dashboard(
        records_root=records_root,
        app_id=app_id,
        split=split,
        window_size=window_size,
        history_limit=history_limit,
    )
    extra_artifact_paths: dict[str, str] = {}
    if emit_l6_shadow:
        extra_artifact_paths["l6_shadow_bridge"] = (
            Path(out_dir) / dashboard.trend_id / L6_SHADOW_BRIDGE_ARTIFACT
        ).as_posix()
    dashboard = _write_dashboard_artifacts(
        dashboard,
        out_dir=out_dir,
        extra_artifact_paths=extra_artifact_paths or None,
    )
    if emit_l6_shadow:
        output_dir = Path(out_dir) / dashboard.trend_id
        bridge_paths = emit_driver_l6_shadow_bridge(
            output_dir,
            eval_id=dashboard.trend_id,
            app_scorecards=[suite.to_dict() for suite in dashboard.suite_summaries],
            output_refs={
                "trend_dashboard": dashboard.artifact_paths.get("trend_dashboard", ""),
                "trend_dashboard_report": dashboard.artifact_paths.get("trend_dashboard_report", ""),
                "trend_dashboard_digest": dashboard.trend_dashboard_digest,
                "trend_id": dashboard.trend_id,
                "records_root": dashboard.records_root,
                "app_id": dashboard.app_id,
                "split": dashboard.split or "all",
            },
        )
        dashboard = replace(
            dashboard,
            artifact_paths={
                **dashboard.artifact_paths,
                **bridge_paths,
            },
        )
    return dashboard


def _write_release_gate_artifacts(
    decision: ReleaseGateDecision,
    *,
    out_dir: str | Path,
) -> ReleaseGateDecision:
    output_dir = Path(out_dir) / decision.trend_id
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "release_gate.json"
    md_path = output_dir / "release_gate.md"
    decision = replace(
        decision,
        artifact_paths={
            **decision.artifact_paths,
            "release_gate": json_path.as_posix(),
            "release_gate_report": md_path.as_posix(),
        },
    )
    json_path.write_text(json.dumps(decision.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_release_gate(decision), encoding="utf-8")
    return decision


def emit_release_gate(
    *,
    records_root: str | Path,
    app_id: str = "",
    split: str = "",
    window_size: int = 5,
    history_limit: int = 20,
    min_samples: int = 2,
    min_latest_pass_rate: float = 1.0,
    min_window_pass_rate: float = 1.0,
    max_latest_score_drop: float = 0.05,
    out_dir: str | Path = "artifacts/apps_eval/trends",
    emit_l6_shadow: bool = False,
) -> ReleaseGateDecision:
    dashboard = emit_trend_dashboard(
        records_root=records_root,
        app_id=app_id,
        split=split,
        window_size=window_size,
        history_limit=history_limit,
        out_dir=out_dir,
        emit_l6_shadow=emit_l6_shadow,
    )
    decision = evaluate_release_gate(
        dashboard,
        min_samples=min_samples,
        min_latest_pass_rate=min_latest_pass_rate,
        min_window_pass_rate=min_window_pass_rate,
        max_latest_score_drop=max_latest_score_drop,
    )
    output_dir = Path(out_dir) / decision.trend_id
    artifact_paths = {
        **dashboard.artifact_paths,
    }
    if emit_l6_shadow:
        artifact_paths["l6_shadow_bridge"] = (output_dir / L6_SHADOW_BRIDGE_ARTIFACT).as_posix()
    decision = replace(
        decision,
        trend_dashboard_path=dashboard.artifact_paths.get("trend_dashboard", ""),
        trend_dashboard_digest=dashboard.trend_dashboard_digest,
        artifact_paths=artifact_paths,
    )
    decision = _write_release_gate_artifacts(decision, out_dir=out_dir)
    if emit_l6_shadow:
        emit_driver_l6_shadow_bridge(
            output_dir,
            eval_id=decision.gate_id,
            app_scorecards=decision.suite_checks,
            output_refs={
                "trend_dashboard": decision.trend_dashboard_path,
                "trend_dashboard_report": decision.artifact_paths.get("trend_dashboard_report", ""),
                "trend_dashboard_digest": decision.trend_dashboard_digest,
                "release_gate": decision.artifact_paths.get("release_gate", ""),
                "release_gate_report": decision.artifact_paths.get("release_gate_report", ""),
                "release_gate_status": decision.status,
                "gate_id": decision.gate_id,
                "trend_id": decision.trend_id,
                "records_root": decision.records_root,
                "app_id": decision.app_id,
                "split": decision.split or "all",
            },
        )
    return decision
