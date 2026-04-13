"""Evaluation report generator and threshold checker."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .constants import (
    AUROC_MIN,
    ECE_MAX,
    FALLBACK_RATE_MAX,
    INFERENCE_LATENCY_US_BUDGET,
    MACRO_F1_MIN,
    NON_UNKNOWN_CLASSES,
    OOD_FPR_MAX,
    PER_CLASS_F1_MIN,
)


@dataclass
class ThresholdCheckResult:
    passed: bool
    checks: dict[str, bool]
    details: dict[str, str]
    failing_checks: list[str] = field(default_factory=list)


def check_promotion_thresholds(
    macro_f1: float,
    per_failure_class_f1: dict[str, float],
    ece: float,
    macro_auroc: float,
    fallback_rate: float,
    inference_latency_us: float,
    ood_fpr_train: float,
) -> ThresholdCheckResult:
    """Return pass/fail for every promotion threshold.

    All checks must pass for offline_eval_passed=True.
    """
    checks: dict[str, bool] = {}
    details: dict[str, str] = {}

    checks["macro_f1"] = macro_f1 >= MACRO_F1_MIN
    details["macro_f1"] = f"{macro_f1:.4f} (required >= {MACRO_F1_MIN})"

    for fc_name in NON_UNKNOWN_CLASSES:
        fc_f1 = per_failure_class_f1.get(fc_name, 0.0)
        key = f"per_class_f1_{fc_name}"
        checks[key] = fc_f1 >= PER_CLASS_F1_MIN
        details[key] = f"{fc_f1:.4f} (required >= {PER_CLASS_F1_MIN})"

    checks["ece"] = ece <= ECE_MAX
    details["ece"] = f"{ece:.4f} (required <= {ECE_MAX})"

    checks["macro_auroc"] = macro_auroc >= AUROC_MIN
    details["macro_auroc"] = f"{macro_auroc:.4f} (required >= {AUROC_MIN})"

    checks["fallback_rate"] = fallback_rate <= FALLBACK_RATE_MAX
    details["fallback_rate"] = f"{fallback_rate:.4f} (required <= {FALLBACK_RATE_MAX})"

    checks["inference_latency"] = inference_latency_us <= INFERENCE_LATENCY_US_BUDGET
    details["inference_latency"] = (
        f"{inference_latency_us:.1f}us (required <= {INFERENCE_LATENCY_US_BUDGET}us)"
    )

    checks["ood_fpr"] = ood_fpr_train <= OOD_FPR_MAX
    details["ood_fpr"] = f"{ood_fpr_train:.4f} (required <= {OOD_FPR_MAX})"

    failing = [k for k, v in checks.items() if not v]
    return ThresholdCheckResult(
        passed=len(failing) == 0,
        checks=checks,
        details=details,
        failing_checks=failing,
    )


def _status_badge(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


class EvalReportGenerator:
    def generate(
        self,
        packet_dir: Path,
        artifact_dir: Path,
        threshold_result: ThresholdCheckResult,
        shadow_data: dict | None = None,
        hitl_data: dict | None = None,
    ) -> None:
        packet_dir.mkdir(parents=True, exist_ok=True)
        self._write_offline_eval_report(packet_dir, threshold_result, artifact_dir)
        self._write_shadow_divergence_report(packet_dir, shadow_data)
        self._write_hitl_cohort_review(packet_dir, hitl_data)

    def _write_offline_eval_report(
        self,
        packet_dir: Path,
        result: ThresholdCheckResult,
        artifact_dir: Path,
    ) -> None:
        overall = _status_badge(result.passed)
        lines = [
            "# Offline Evaluation Report — heal_classifier v1",
            "",
            f"**Overall verdict: {overall}**",
            "",
            "## Threshold Checks",
            "",
            "| Check | Detail | Status |",
            "|---|---|---|",
        ]
        for check_name, passed in result.checks.items():
            detail = result.details.get(check_name, "")
            lines.append(f"| {check_name} | {detail} | {_status_badge(passed)} |")

        if result.failing_checks:
            lines += [
                "",
                "## Failing Checks",
                "",
                *[f"- `{c}`" for c in result.failing_checks],
            ]

        calib_path = artifact_dir / "calibration_meta.json"
        if calib_path.exists():
            calib = json.loads(calib_path.read_text(encoding="utf-8"))
            lines += [
                "",
                "## Classification Report (Validation Set)",
                "",
                "```",
                calib.get("classification_report", "(not available)"),
                "```",
            ]

        (packet_dir / "offline_eval_report.md").write_text("\n".join(lines), encoding="utf-8")

    def _write_shadow_divergence_report(
        self,
        packet_dir: Path,
        shadow_data: dict | None,
    ) -> None:
        lines = [
            "# Shadow Divergence Report — heal_classifier v1",
            "",
        ]
        if shadow_data is None:
            lines += [
                "_No shadow telemetry data provided._ Complete after shadow-mode activation.",
                "",
                "Required fields:",
                "- `shadow_rows_analyzed`",
                "- `divergence_rate`",
                "- `divergence_by_failure_class`",
                "- `ood_rate`",
                "- `fallback_rate`",
            ]
        else:
            rows = shadow_data.get("shadow_rows_analyzed", "N/A")
            div_rate = shadow_data.get("divergence_rate", "N/A")
            lines += [
                f"**Shadow rows analyzed:** {rows}",
                f"**Divergence rate (ML != heuristic):** {div_rate}",
                "",
                "### Divergence by failure_class",
                "",
                "| failure_class | divergence_rate |",
                "|---|---|",
            ]
            for fc, rate in shadow_data.get("divergence_by_failure_class", {}).items():
                lines.append(f"| {fc} | {rate} |")

        (packet_dir / "shadow_divergence_report.md").write_text("\n".join(lines), encoding="utf-8")

    def _write_hitl_cohort_review(
        self,
        packet_dir: Path,
        hitl_data: dict | None,
    ) -> None:
        lines = [
            "# HITL Cohort Review — heal_classifier v1",
            "",
        ]
        if hitl_data is None:
            lines += [
                "_No HITL cohort data provided._ Required before mixing HITL examples into main training.",
                "",
                "Required fields:",
                "- `hitl_rows_reviewed`",
                "- `hitl_defensible_fraction`",
                "- `systematic_pattern_summary`",
            ]
        else:
            rows = hitl_data.get("hitl_rows_reviewed", "N/A")
            defensible = hitl_data.get("hitl_defensible_fraction", "N/A")
            lines += [
                f"**HITL rows reviewed:** {rows}",
                f"**Defensible fraction:** {defensible}",
                "",
                "### Pattern Summary",
                "",
                hitl_data.get("systematic_pattern_summary", "_No summary provided._"),
            ]

        (packet_dir / "hitl_cohort_review.md").write_text("\n".join(lines), encoding="utf-8")
