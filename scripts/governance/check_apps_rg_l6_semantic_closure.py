#!/usr/bin/env python3
"""Fail closed on apps_rg L6 authority, closure, and proof regressions."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
POST_X3 = ROOT / "apps_rg/runtime/post_x3_completion.py"
RUNNER = ROOT / "apps_rg/runtime/spine/l6_shadow_eval_runner.py"
BRIDGE = ROOT / "apps_eval/l6_shadow_bridge.py"
INDEPENDENT_PARITY = (
    ROOT / "agentic_core/L6_observability/shadow_eval/independent_parity.py"
)
WORKFLOW = ROOT / ".github/workflows/apps-rg-l6-semantic-closure.yml"


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse(path: Path, issues: list[str]) -> tuple[str, ast.Module | None]:
    if not path.is_file():
        issues.append(f"missing required file: {path.relative_to(ROOT)}")
        return "", None
    source = _source(path)
    try:
        tree = ast.parse(source, filename=path.as_posix())
    except SyntaxError as exc:
        issues.append(f"syntax error in {path.relative_to(ROOT)}:{exc.lineno}: {exc.msg}")
        return source, None
    return source, tree


def _top_level_function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    return next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == name
        ),
        None,
    )


def _call_lines(function: ast.FunctionDef, dotted_name: str) -> list[int]:
    """Return direct source locations for one semantically named call."""

    lines: list[int] = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue
        called = ""
        if isinstance(node.func, ast.Name):
            called = node.func.id
        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            called = f"{node.func.value.id}.{node.func.attr}"
        if called == dotted_name:
            lines.append(node.lineno)
    return sorted(lines)


def _validate_post_x3_authority_order(
    tree: ast.Module | None,
    issues: list[str],
) -> None:
    """Prove the active post-X3 path closes UWG before eval/L6 observation."""

    if tree is None:
        return
    authoritative = _top_level_function(tree, "_complete_apps_rg_post_x3")
    wrapper = _top_level_function(tree, "complete_apps_rg_post_x3")
    if authoritative is None or wrapper is None:
        issues.append("post-X3 authoritative routine or public wrapper not found")
        return

    wrapper_calls = _call_lines(wrapper, "_complete_apps_rg_post_x3")
    commit_lines = _call_lines(authoritative, "gateway.commit")
    eval_lines = _call_lines(authoritative, "_run_current_eval")
    if not wrapper_calls:
        issues.append("public post-X3 wrapper does not invoke the authoritative routine")
    if not commit_lines or not eval_lines:
        issues.append("post-X3 authority/eval call sites not found")
    elif max(commit_lines) >= min(eval_lines):
        issues.append("apps_eval/L6 executes before current-run UWG closure")


def validate() -> dict[str, Any]:
    issues: list[str] = []
    post_x3, post_x3_tree = _parse(POST_X3, issues)
    runner, _ = _parse(RUNNER, issues)
    bridge, _ = _parse(BRIDGE, issues)
    independent, _ = _parse(INDEPENDENT_PARITY, issues)
    if not WORKFLOW.is_file():
        issues.append("semantic-closure workflow is not registered")

    _validate_post_x3_authority_order(post_x3_tree, issues)
    if '"l6_influenced_current_uwg_decision": False' not in post_x3:
        issues.append("authority-order receipt does not deny L6 influence")
    if '"apps_eval_influenced_current_uwg_decision": False' not in post_x3:
        issues.append("authority-order receipt does not deny apps_eval influence")
    if "independent_persisted_observations" not in post_x3:
        issues.append("post-X3 binder does not use independent persisted observations")
    if "LEGACY_PACKAGE_ADVISORY" not in post_x3:
        issues.append("legacy packages are not explicitly advisory")

    if '"eval_binding_status": "PENDING"' not in runner:
        issues.append("section observability closure does not separate eval binding")
    if "grain_parity_pass" in runner or "apps_eval_bound_evidence" in runner:
        issues.append("section observability closure still requires apps_eval-bound proof")
    if "artifact_digests" not in runner or "closure_digest" not in runner:
        issues.append("section observability closure lacks digest sealing")

    if "projection_consistency_only" not in bridge:
        issues.append("apps_eval projection path is not labelled projection-only")
    if "independent_observation_required_for_bound_proof" not in bridge:
        issues.append("apps_eval bridge does not require independent observation proof")
    if "EVIDENCE_CLASS_APPS_EVAL_BOUND_PROOF" in bridge:
        issues.append("apps_eval projection bridge can mint bound-proof evidence")

    required_independent_tokens = (
        "duplicate_join_keys",
        "source_ref_mismatches",
        "runtime_exhaust_bundle_mismatches",
        "SEALED_APPS_RG_OBSERVATION_ORIGIN",
    )
    for token in required_independent_tokens:
        if token not in independent:
            issues.append(f"independent parity is missing {token}")

    return {
        "schema_version": "apps_rg.l6_semantic_closure_gate.v1",
        "status": "PASS" if not issues else "FAIL",
        "issue_count": len(issues),
        "issues": issues,
        "checked_files": [
            str(path.relative_to(ROOT))
            for path in (POST_X3, RUNNER, BRIDGE, INDEPENDENT_PARITY, WORKFLOW)
        ],
        "authority_order": "Exit->UWG->RuntimeBoundary->apps_eval/L6",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"apps_rg L6 semantic closure: {result['status']}")
        for issue in result["issues"]:
            print(f"- {issue}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
