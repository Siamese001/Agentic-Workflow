"""W8 machine-readable C0.3 CI ratchet with one exact external baseline debt."""
from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from apps_rg.runtime.c0.c03_resume_graph_contracts import stable_digest

SCHEMA_VERSION = "apps_rg.c03.ci_ratchet_receipt.v3"
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


def build_ratchet_receipt(
    *,
    strict_junit: Path,
    baseline_junit: Path,
    source_commit: str,
    base_commit: str,
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
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    receipt = build_ratchet_receipt(
        strict_junit=args.strict_junit,
        baseline_junit=args.baseline_junit,
        source_commit=args.source_commit,
        base_commit=args.base_commit,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
