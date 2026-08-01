"""W8 machine-readable C0.3 CI ratchet with one exact external baseline debt."""
from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Mapping

from apps_rg.runtime.c0.c03_resume_graph_contracts import stable_digest

SCHEMA_VERSION = "apps_rg.c03.ci_ratchet_receipt.v4"
GATE_RECEIPT_SCHEMA_VERSION = "apps_rg.ci_gate_receipt.v1"
REQUIRED_SCORE_GROUPS = (
    "retrieval_quality",
    "binding_accuracy",
    "factual_grounding",
    "section_quality",
    "whole_resume_quality",
    "runtime_repeatability",
    "evaluator_validity",
)
SCORE_GROUP_GATES = {
    "retrieval_quality": "G1",
    "binding_accuracy": "G2",
    "factual_grounding": "G3",
    "section_quality": "G4",
    "whole_resume_quality": "G4",
    "runtime_repeatability": "G5",
    "evaluator_validity": "G6",
}
_GATE_RECEIPT_FIELDS = {
    "schema_version",
    "score_group",
    "gate_id",
    "source_receipt_digest",
    "status",
    "metrics",
    "critical_failure_count",
    "required_unknown_count",
    "holdout_leakage_incidents",
    "unsupported_material_claim_count",
    "mutation_failure_count",
    "baseline_signature",
    "record_digest",
}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
KNOWN_EXTERNAL_NODEID = (
    "tests/_apps_contract/test_apps_rg_c0_ownership_split.py::"
    "TestAgenticCoreGraphSkillBoundary::"
    "test_agentic_core_does_not_embed_resume_graph_skill_authority_literals"
)
KNOWN_FAILURE_FRAGMENT = "augmented_skills_graph"


def _junit(path: Path) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    totals = dict.fromkeys(("tests", "failures", "errors", "skipped"), 0)
    cases: list[dict[str, Any]] = []
    for suite in suites:
        for key in totals:
            totals[key] += int(suite.attrib.get(key, 0))
        for case in suite.findall(".//testcase"):
            failure = case.find("failure")
            error = case.find("error")
            cases.append(
                {
                    "classname": case.attrib.get("classname", ""),
                    "name": case.attrib.get("name", ""),
                    "failure": (
                        (failure.attrib.get("message", "") + " " + (failure.text or "")).strip()
                        if failure is not None
                        else ""
                    ),
                    "error": (
                        (error.attrib.get("message", "") + " " + (error.text or "")).strip()
                        if error is not None
                        else ""
                    ),
                }
            )
    totals["executed"] = totals["tests"] - totals["skipped"]
    totals["cases"] = cases
    return totals


def seal_gate_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Seal one normalized score-group receipt for the CI aggregation boundary."""

    sealed = dict(receipt)
    sealed["record_digest"] = stable_digest(
        {key: value for key, value in sealed.items() if key != "record_digest"}
    )
    return sealed


def _validate_gate_receipts(
    receipts: Mapping[str, Mapping[str, Any]],
    expected_baselines: Mapping[str, str],
) -> tuple[list[str], dict[str, Any]]:
    failures: list[str] = []
    summaries: dict[str, Any] = {}
    missing = sorted(set(REQUIRED_SCORE_GROUPS) - set(receipts))
    extra = sorted(set(receipts) - set(REQUIRED_SCORE_GROUPS))
    failures.extend(f"evaluation_receipt_missing::{name}" for name in missing)
    failures.extend(f"evaluation_receipt_unexpected::{name}" for name in extra)
    baseline_missing = sorted(set(REQUIRED_SCORE_GROUPS) - set(expected_baselines))
    baseline_extra = sorted(set(expected_baselines) - set(REQUIRED_SCORE_GROUPS))
    failures.extend(f"evaluation_baseline_missing::{name}" for name in baseline_missing)
    failures.extend(f"evaluation_baseline_unexpected::{name}" for name in baseline_extra)
    for score_group in REQUIRED_SCORE_GROUPS:
        receipt = receipts.get(score_group)
        if not isinstance(receipt, Mapping):
            continue
        receipt_failures: list[str] = []
        if set(receipt) != _GATE_RECEIPT_FIELDS or receipt.get("schema_version") != GATE_RECEIPT_SCHEMA_VERSION:
            receipt_failures.append("schema_invalid")
        if receipt.get("score_group") != score_group:
            receipt_failures.append("score_group_mismatch")
        if receipt.get("gate_id") != SCORE_GROUP_GATES[score_group]:
            receipt_failures.append("gate_id_mismatch")
        if not isinstance(receipt.get("metrics"), Mapping):
            receipt_failures.append("metrics_invalid")
        source_digest = receipt.get("source_receipt_digest")
        if not isinstance(source_digest, str) or not _SHA256_RE.fullmatch(source_digest):
            receipt_failures.append("source_digest_invalid")
        digest = receipt.get("record_digest")
        if (
            not isinstance(digest, str)
            or not _SHA256_RE.fullmatch(digest)
            or digest
            != stable_digest({key: value for key, value in receipt.items() if key != "record_digest"})
        ):
            receipt_failures.append("record_digest_invalid")
        status = receipt.get("status")
        if status == "UNKNOWN":
            receipt_failures.append("required_status_unknown")
        elif status != "PASS":
            receipt_failures.append("critical_regression")
        counters = {
            "critical_failure_count": "critical_failure",
            "required_unknown_count": "required_unknown",
            "holdout_leakage_incidents": "holdout_leakage",
            "unsupported_material_claim_count": "unsupported_material_claim",
            "mutation_failure_count": "mutation_failure",
        }
        for field, code in counters.items():
            value = receipt.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                receipt_failures.append(f"{field}_invalid")
            elif value:
                receipt_failures.append(code)
        baseline = receipt.get("baseline_signature")
        if not isinstance(baseline, str) or not baseline:
            receipt_failures.append("baseline_signature_invalid")
        if baseline != expected_baselines.get(score_group):
            receipt_failures.append("unexpected_baseline_signature")
        failures.extend(
            f"evaluation_receipt::{score_group}::{code}" for code in sorted(set(receipt_failures))
        )
        summaries[score_group] = {
            "gate_id": receipt.get("gate_id"),
            "status": status,
            "source_receipt_digest": source_digest,
            "baseline_signature": baseline,
            "validation_status": "FAIL" if receipt_failures else "PASS",
            "failure_codes": sorted(set(receipt_failures)),
        }
    return failures, summaries


def build_ratchet_receipt(
    *,
    strict_junit: Path,
    baseline_junit: Path,
    source_commit: str,
    base_commit: str,
    evaluation_receipts: Mapping[str, Mapping[str, Any]] | None = None,
    expected_baselines: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    strict = _junit(strict_junit)
    baseline = _junit(baseline_junit)
    failures: list[str] = []
    if strict["executed"] <= 0:
        failures.append("strict_suite_executed_zero_tests")
    if strict["failures"] or strict["errors"]:
        failures.append("strict_suite_nonpass")

    baseline_nonpass = [
        case for case in baseline["cases"] if case["failure"] or case["error"]
    ]
    improvement = not baseline_nonpass and baseline["errors"] == 0
    exact_known_failure = False
    if len(baseline_nonpass) == 1:
        case = baseline_nonpass[0]
        identity = f"{case['classname']}::{case['name']}"
        detail = f"{case['failure']} {case['error']}"
        exact_known_failure = (
            case["name"]
            == "test_agentic_core_does_not_embed_resume_graph_skill_authority_literals"
            and "TestAgenticCoreGraphSkillBoundary" in identity
            and KNOWN_FAILURE_FRAGMENT in detail
        )
    if not improvement and not exact_known_failure:
        failures.append("external_baseline_signature_changed")
    if baseline["executed"] != 1:
        failures.append("external_baseline_diagnostic_not_exactly_one_test")

    evaluation_summaries: dict[str, Any] = {}
    if evaluation_receipts is None and expected_baselines is not None:
        failures.append("evaluation_receipt_bundle_missing")
    elif evaluation_receipts is not None and not isinstance(evaluation_receipts, Mapping):
        failures.append("evaluation_receipt_bundle_invalid")
    elif evaluation_receipts is not None and expected_baselines is None:
        failures.append("evaluation_baseline_bundle_missing")
    elif evaluation_receipts is not None and not isinstance(expected_baselines, Mapping):
        failures.append("evaluation_baseline_bundle_invalid")
    elif evaluation_receipts is not None:
        receipt_failures, evaluation_summaries = _validate_gate_receipts(
            evaluation_receipts, expected_baselines
        )
        failures.extend(receipt_failures)

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "source_commit": source_commit,
        "base_commit": base_commit,
        "status": "PASS" if not failures else "FAIL",
        "strict_suite": {
            key: strict[key]
            for key in ("tests", "failures", "errors", "skipped", "executed")
        },
        "external_baseline_diagnostic": {
            key: baseline[key]
            for key in ("tests", "failures", "errors", "skipped", "executed")
        },
        "accepted_external_baseline_debt": {
            "nodeid": KNOWN_EXTERNAL_NODEID,
            "owner": "agentic_core",
            "status": (
                "IMPROVED"
                if improvement
                else "ACCEPTED_EXTERNAL_BASELINE_DEBT"
                if exact_known_failure
                else "REJECTED"
            ),
            "reason": (
                "agentic_core/L0_routing/__init__.py contains augmented_skills_graph"
                if exact_known_failure
                else "known external failure no longer reproduces"
                if improvement
                else "unexpected diagnostic signature"
            ),
        },
        "failure_codes": sorted(failures),
        "evaluation_receipt_mode": (
            "SEALED_ALL_SCORE_GROUPS" if evaluation_receipts is not None else "LEGACY_JUNIT_ONLY"
        ),
        "evaluation_receipts": evaluation_summaries,
        "documentation_gates_included": False,
        "unknown_is_pass": False,
    }
    body["record_digest"] = stable_digest(body)
    return body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict-junit", type=Path, required=True)
    parser.add_argument("--baseline-junit", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--base-commit", required=True)
    parser.add_argument("--evaluation-receipts", type=Path)
    parser.add_argument("--expected-baselines", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    evaluation_receipts = (
        json.loads(args.evaluation_receipts.read_text(encoding="utf-8"))
        if args.evaluation_receipts
        else None
    )
    expected_baselines = (
        json.loads(args.expected_baselines.read_text(encoding="utf-8"))
        if args.expected_baselines
        else None
    )
    receipt = build_ratchet_receipt(
        strict_junit=args.strict_junit,
        baseline_junit=args.baseline_junit,
        source_commit=args.source_commit,
        base_commit=args.base_commit,
        evaluation_receipts=evaluation_receipts,
        expected_baselines=expected_baselines,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
