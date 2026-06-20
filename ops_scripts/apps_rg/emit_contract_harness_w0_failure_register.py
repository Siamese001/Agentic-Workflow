#!/usr/bin/env python3
"""W0: classify filtered ``tests/_apps_contract`` failures into harness-modernization buckets."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

PLAN_ID = "apps-rg-contract-harness-modernization-f4e8b2"
REPORTS = REPO / "docs" / "reports" / "apps_rg"
JUNIT_PATH = REPORTS / "contract_harness_w0_junit.xml"
REGISTER_MD = REPORTS / "contract_harness_failure_register_20260526.md"
RECEIPT_JSON = REPORTS / "contract_harness_modernization_w0_receipt.json"

PYTEST_K = (
    "competencies or prompt_judge or product_shape or executive_summary_x2 "
    "or unify_bullets or ibm_bullets or unify_narrative or ibm_narrative"
)

BUCKETS: dict[str, str] = {
    "B1": "CLI subprocess uses removed ``--provider mock`` (product allows qwen_vllm only)",
    "B2": "Legacy ``claim_evidence_source_type`` / proof_source enums omit ``augmented_skills_graph``",
    "B3": "Tests pass wrong ``proof_pool_type`` vs ``evidence_authority='augmented_skills_graph'``",
    "B4": "``SectionFrontSpinePreconditionError`` — proof pool before front spine bridge",
    "B5": "Other contract drift (competencies, product_shape, PA tiering, pipeline mocks)",
}


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return out.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def _classify(nodeid: str, message: str) -> str:
    blob = f"{nodeid}\n{message}"
    if "SectionFrontSpinePreconditionError" in blob:
        return "B4"
    if "invalid choice" in blob and "mock" in blob:
        return "B1"
    if "--provider mock" in blob or "'mock'" in blob and "provider" in blob.lower():
        return "B1"
    if "evidence_authority='augmented_skills_graph'" in blob or (
        "evidence_authority" in blob and "proof_pool_type is not an authority" in blob
    ):
        return "B3"
    if "assert 'augmented_skills_graph' in" in blob or (
        "augmented_skills_graph" in blob and "candidate_fact_ledger" in blob
    ):
        return "B2"
    if "proof_source='augmented_skills_graph'" in blob and "broad_skills_ledger" in blob:
        return "B2"
    return "B5"


def _sub_bucket(nodeid: str) -> str:
    path = nodeid.split("::", 1)[0].replace("\\", "/")
    if "competencies" in path.lower():
        return "competencies"
    if "augmented_skills_graph" in path:
        return "graph_skills_authority"
    if "unify" in path:
        return "unify_lane"
    if "ibm" in path:
        return "ibm_lane"
    if "product_shape" in path or "section_x2" in path:
        return "product_shape_x2"
    if "pa_binding" in path or "resume_section_treatment" in path:
        return "pa_tiering"
    if "executive_summary" in path:
        return "executive_summary"
    if "commercial_medium" in path:
        return "commercial_medium"
    return "other"


def _run_pytest() -> tuple[int, str]:
    REPORTS.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/_apps_contract/",
        "-k",
        PYTEST_K,
        "-q",
        "--tb=no",
        f"--junitxml={JUNIT_PATH}",
        "-o",
        "addopts=",
    ]
    env = {**dict(**__import__("os").environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "PYTHONPATH": str(REPO)}
    completed = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900,
        env=env,
        check=False,
    )
    summary = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, summary[-4000:] if len(summary) > 4000 else summary


def _parse_junit() -> tuple[list[dict[str, str]], dict[str, int]]:
    if not JUNIT_PATH.is_file():
        return [], {}
    root = ET.parse(JUNIT_PATH).getroot()
    rows: list[dict[str, str]] = []
    counts: dict[str, int] = {"failed": 0, "error": 0, "passed": 0, "skipped": 0}
    root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
    if root_tag == "testsuites":
        for key in ("failures", "errors", "skipped", "tests"):
            if key in root.attrib:
                val = int(root.attrib[key])
                if key == "failures":
                    counts["failed"] = val
                elif key == "errors":
                    counts["error"] = val
                elif key == "skipped":
                    counts["skipped"] = val
                elif key == "tests":
                    total = val
                    counts["passed"] = max(0, total - counts["failed"] - counts["error"] - counts["skipped"])
    for suite in root.iter("testsuite"):
        if root_tag == "testsuites":
            break
        for key in counts:
            if key in suite.attrib:
                counts[key] += int(suite.attrib.get(key, 0))
    for case in root.iter("testcase"):
        nodeid = f"{case.attrib.get('classname', '')}::{case.attrib.get('name', '')}"
        if not nodeid.strip(":"):
            file_attr = case.attrib.get("file", "")
            nodeid = f"{file_attr}::{case.attrib.get('name', '')}"
        failure = case.find("failure")
        error = case.find("error")
        if failure is None and error is None:
            continue
        elem = failure if failure is not None else error
        kind = "failed" if failure is not None else "error"
        message = (elem.attrib.get("message") or "") + "\n" + (elem.text or "")
        bucket = _classify(nodeid, message)
        rows.append(
            {
                "nodeid": nodeid,
                "kind": kind,
                "bucket": bucket,
                "sub_bucket": _sub_bucket(nodeid),
                "message_excerpt": message.strip().replace("\n", " ")[:240],
            }
        )
    return rows, counts


def _write_register(rows: list[dict[str, str]], counts: dict[str, int], pytest_tail: str) -> None:
    by_bucket: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_bucket[row["bucket"]].append(row)

    lines = [
        "# Apps RG Contract Harness — Failure Register (W0)",
        "",
        f"**Plan:** [{PLAN_ID}](../../.codex/plans/{PLAN_ID}.md)  ",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}  ",
        f"**Filter:** `pytest tests/_apps_contract/ -k \"{PYTEST_K}\"`  ",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|------:|",
        f"| Failed | {counts.get('failed', 0)} |",
        f"| Errors | {counts.get('error', 0)} |",
        f"| Passed | {counts.get('passed', 0)} |",
        f"| Skipped | {counts.get('skipped', 0)} |",
        f"| Classified rows | {len(rows)} |",
        "",
        "## Bucket totals",
        "",
        "| ID | Wave | Count | Description |",
        "|----|------|------:|-------------|",
    ]
    wave_map = {"B1": "W1", "B2": "W2", "B3": "W2", "B4": "W3", "B5": "W4"}
    for bid in ("B1", "B2", "B3", "B4", "B5"):
        lines.append(
            f"| {bid} | {wave_map[bid]} | {len(by_bucket.get(bid, []))} | {BUCKETS[bid]} |"
        )

    sub_counts = Counter(r["sub_bucket"] for r in rows)
    lines.extend(["", "## Sub-bucket (B5 tail)", "", "| Sub-bucket | Count |", "|------------|------:|"])
    for name, cnt in sub_counts.most_common():
        lines.append(f"| {name} | {cnt} |")

    for bid in ("B1", "B2", "B3", "B4", "B5"):
        items = by_bucket.get(bid, [])
        if not items:
            continue
        lines.extend(["", f"## {bid} — {BUCKETS[bid]}", ""])
        file_counts = Counter(i["nodeid"].split("::")[0] for i in items)
        lines.append("| Test module | Failures |")
        lines.append("|-------------|----------:|")
        for mod, cnt in file_counts.most_common(25):
            lines.append(f"| `{mod}` | {cnt} |")
        if len(file_counts) > 25:
            lines.append(f"| … | {len(file_counts) - 25} more modules |")

    lines.extend(
        [
            "",
            "## Remediation waves (Track B)",
            "",
            "| Wave | Bucket | Exit criteria |",
            "|------|--------|---------------|",
            "| W1 | B1 | No contract test expects CLI `--provider mock` exit 0 |",
            "| W2 | B2, B3 | Graph authority contracts assert `augmented_skills_graph` |",
            "| W3 | B4 | Front-spine bridge before `resolve_section_proof_pool` |",
            "| W4 | B5 | Competencies / product_shape / PA tiering green |",
            "| W5 | all | Filtered `_apps_contract` gate 0 failed |",
            "",
            "## Pytest tail (excerpt)",
            "",
            "```text",
            pytest_tail.strip() or "(empty)",
            "```",
            "",
        ]
    )
    REGISTER_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    from ops_scripts.apps_rg.l6_benchmarks.receipt_links import enrich_manifest_links, path_link

    code, pytest_tail = _run_pytest()
    rows, counts = _parse_junit()
    _write_register(rows, counts, pytest_tail)
    commit = _git_commit()
    bucket_totals = dict(Counter(r["bucket"] for r in rows))
    # W0 succeeds when taxonomy is captured (not when pytest is green).
    status = "PASS" if len(rows) >= 1 and REGISTER_MD.is_file() else "FAIL"

    receipt = enrich_manifest_links(
        {
            "schema": "contract_harness_modernization_wave_receipt_v1",
            "plan_id": PLAN_ID,
            "wave_id": "W0",
            "status": status,
            "git_commit": commit,
            "pytest_exit_code": code,
            "pytest_filter_k": PYTEST_K,
            "counts": counts,
            "classified_count": len(rows),
            "bucket_totals": bucket_totals,
            "register_path": "docs/reports/apps_rg/contract_harness_failure_register_20260526.md",
            "junit_path": "docs/reports/apps_rg/contract_harness_w0_junit.xml",
            "phase_gate": f"PHASE_GATE: wave=W0 status={status} gate=G-W0",
        }
    )
    receipt["register_path_link"] = path_link(receipt["register_path"])
    RECEIPT_JSON.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "classified": len(rows), "receipt": str(RECEIPT_JSON.relative_to(REPO))}, indent=2))
    return 0 if status in ("PASS", "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
