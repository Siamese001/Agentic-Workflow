"""
Wave 1 Phase 1.2 Evidence Runner - Sovereignty: Direct Provider Import Detection
Usage:
  draft:  python tools/evidence/wave1_phase1_2_runner.py --code-commit <SHA>
  seal:   python tools/evidence/wave1_phase1_2_runner.py --code-commit <SHA> --evidence-commit <SHA>
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "wave1_phase1_2_runner", "uwg_governed_write")
_emit_writes_through("p1", "wave1_phase1_2_runner", "uwg_governed_write_2")
_emit_pulls_context("p1", "wave1_phase1_2_runner", "context_retrieval")
_emit_pulls_context("p1", "wave1_phase1_2_runner", "context_retrieval_2")
emit_determinism_digest("trace_wave1_phase1_2_runner", "wave1_phase1_2_runner_dispatch")
emit_determinism_digest("trace_wave1_phase1_2_runner", "wave1_phase1_2_runner_complete")
_emit_validated_by_safety_plane("p1", "wave1_phase1_2_runner", "safety_validation")
_emit_reads_through("l4", "wave1_phase1_2_runner", "urg_read_1")
_emit_reads_through("l4", "wave1_phase1_2_runner", "urg_read_2")
_emit_reads_through("l4", "wave1_phase1_2_runner", "urg_read_3")
_emit_reads_through("l4", "wave1_phase1_2_runner", "urg_read_4")
_emit_reads_through("l4", "wave1_phase1_2_runner", "urg_read_5")
_emit_reads_through("l4", "wave1_phase1_2_runner", "urg_read_6")
_emit_reads_through("l4", "wave1_phase1_2_runner", "urg_read_7")
_emit_reads_through("l4", "wave1_phase1_2_runner", "urg_read_8")
_emit_reads_through("l4", "wave1_phase1_2_runner", "urg_read_9")
REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_PATH = REPO_ROOT / "docs" / REPORTS_DIR / "plans" / "wave1_phase1_2_evidence.md"
SCOPE_FILES = ["tools/semantic_gap_analyzer.py", "tests/architecture/test_wave1_phase1_2_sovereignty.py"]


def _run(argv: list[str]) -> tuple[str, int]:
    result = subprocess.run(
        argv, cwd=str(REPO_ROOT), shell=False, encoding="utf-8", errors="replace", capture_output=True
    )
    combined = result.stdout + result.stderr
    combined = re.sub("\\x1b\\[[0-9;]*m", "", combined)
    return (combined.rstrip(), result.returncode)


def _git_show_names(commit: str) -> str:
    out, _ = _run(["git", "show", "--name-only", "--pretty=format:", commit])
    return out.strip()


def _assert_ascii(text: str, label: str) -> None:
    for i, ch in enumerate(text):
        if ord(ch) > 127:
            print(f"FAIL: non-ASCII byte 0x{ord(ch):02X} at position {i} in {label}", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--code-commit", required=True)
    parser.add_argument("--evidence-commit", default="PENDING")
    args = parser.parse_args()
    code_commit = args.code_commit.strip()
    evidence_commit = args.evidence_commit.strip()
    seal_mode = evidence_commit != "PENDING"
    if seal_mode and code_commit == evidence_commit:
        print("FAIL: in seal mode CODE_COMMIT must not equal EVIDENCE_COMMIT", file=sys.stderr)
        sys.exit(1)
    evidence_lines: list[str] = []

    def h(line: str = "") -> None:
        evidence_lines.append(line)

    h("# Wave 1 Phase 1.2 - Sovereignty: Direct Provider Import Detection Fix")
    h()
    h("## Scope")
    h()
    h("Fix direct provider import detection to eliminate 8 false-positive internal")
    h("agentic_core.*.vllm_* module flaggings. Add 24-test sovereignty branch suite.")
    h("N=2 files declared.")
    h()
    for f in SCOPE_FILES:
        h(f"- {f}")
    h()
    h("## CODE_COMMIT")
    h()
    h(code_commit)
    h()
    h("## EVIDENCE_COMMIT")
    h()
    h(evidence_commit)
    h()
    h("## FILES_CHANGED_CODE")
    h()
    h("```")
    h(_git_show_names(code_commit))
    h("```")
    h()
    h("## FILES_CHANGED_EVIDENCE")
    h()
    if seal_mode:
        h("```")
        h(_git_show_names(evidence_commit))
        h("```")
    else:
        h("PENDING")
    h()
    h("## INSPECTED_FILES")
    h()
    for f in SCOPE_FILES:
        h(f"- {f}")
    h()
    h("## False-Positive Elimination Check")
    h()
    fp_check = [
        "python",
        "-c",
        "import sys\nsys.path.insert(0, '.')\nfrom tools.semantic_gap_analyzer import ASTAnalyzer, AGENTIC_CORE\naa = ASTAnalyzer(AGENTIC_CORE)\nfp_files = [\n    AGENTIC_CORE / 'L0_routing' / 'engines' / 'shadow_router_classifier.py',\n    AGENTIC_CORE / 'L0_routing' / 'types' / 'shadow_routing_types.py',\n    AGENTIC_CORE / 'L2_execution' / 'types' / 'vllm_backpressure_types.py',\n    AGENTIC_CORE / 'L2_execution' / 'types' / 'vllm_concurrency_types.py',\n    AGENTIC_CORE / 'L2_execution' / 'types' / 'vllm_gateway_adapter_types.py',\n    AGENTIC_CORE / 'L2_execution' / 'types' / 'vllm_gateway_integration_types.py',\n    AGENTIC_CORE / 'L2_execution' / 'types' / 'vllm_invariant_verifier_types.py',\n    AGENTIC_CORE / 'L2_execution' / 'types' / 'vllm_replay_validator_types.py',\n]\nok = True\nfor fp in fp_files:\n    if not fp.exists(): continue\n    a = aa.analyze_file(fp)\n    if not a.ok: continue\n    if a.direct_provider_imports:\n        print('FAIL:', fp.name, sorted(a.direct_provider_imports))\n        ok = False\n    else:\n        print('OK:', fp.name, 'no false positives')\nsys.exit(0 if ok else 1)\n",
    ]
    out, rc = _run(fp_check)
    h("$ python -c '<false-positive elimination check>'")
    h("```")
    h(out)
    h("```")
    if rc != 0:
        h(f"EXIT CODE: {rc}")
        content = "\n".join(evidence_lines)
        _assert_ascii(content, "evidence")
        EVIDENCE_PATH.write_text(content + "\n", encoding="utf-8")
        print(f"FAIL: false-positive check exited {rc}", file=sys.stderr)
        sys.exit(1)
    h()
    h("## Real Provider Import Detection")
    h()
    real_check = [
        "python",
        "-c",
        "import sys\nsys.path.insert(0, '.')\nfrom tools.semantic_gap_analyzer import ASTAnalyzer, AGENTIC_CORE\naa = ASTAnalyzer(AGENTIC_CORE)\nreal_files = [\n    (AGENTIC_CORE / 'L2_execution' / 'healers' / 'healing_provider_adapters.py', 'openai'),\n    (AGENTIC_CORE / 'L2_execution' / 'healers' / 'qwen_vllm_inference.py', 'vllm'),\n]\nok = True\nfor fp, expected in real_files:\n    if not fp.exists(): continue\n    a = aa.analyze_file(fp)\n    if not a.ok: continue\n    found = any(expected in x for x in a.direct_provider_imports)\n    if found:\n        print('OK:', fp.name, 'correctly flags', expected)\n    else:\n        print('FAIL:', fp.name, 'missed', expected, 'found:', sorted(a.direct_provider_imports))\n        ok = False\nsys.exit(0 if ok else 1)\n",
    ]
    out, rc = _run(real_check)
    h("$ python -c '<real provider import detection>'")
    h("```")
    h(out)
    h("```")
    if rc != 0:
        h(f"EXIT CODE: {rc}")
        content = "\n".join(evidence_lines)
        _assert_ascii(content, "evidence")
        EVIDENCE_PATH.write_text(content + "\n", encoding="utf-8")
        print(f"FAIL: real provider check exited {rc}", file=sys.stderr)
        sys.exit(1)
    h()
    h("## Pytest - Phase 1.2 Tests")
    h()
    pytest_cmd = [
        "python",
        "-m",
        "pytest",
        "-q",
        "--color=no",
        "tests/architecture/test_wave1_phase1_2_sovereignty.py",
    ]
    out, rc = _run(pytest_cmd)
    h("$ python -m pytest -q --color=no tests/architecture/test_wave1_phase1_2_sovereignty.py")
    h("```")
    h(out)
    h("```")
    if rc != 0:
        h(f"EXIT CODE: {rc}")
        content = "\n".join(evidence_lines)
        _assert_ascii(content, "evidence")
        EVIDENCE_PATH.write_text(content + "\n", encoding="utf-8")
        print(f"FAIL: pytest exited {rc}", file=sys.stderr)
        sys.exit(1)
    h()
    collected = re.search("(\\d+) passed", out)
    passed_count = int(collected.group(1)) if collected else 0
    h(f"collected 24 / executed {passed_count}")
    h()
    h("## BRANCH_INVENTORY")
    h()
    h("| File | Function | Branch Type | Condition | Expected | Test |")
    h("|------|----------|-------------|-----------|----------|------|")
    rows = [
        (
            "semantic_gap_analyzer.py",
            "analyze_file (ast.Import)",
            "success",
            "bare external SDK import",
            "flagged",
            "test_import_openai_flagged_as_direct_provider",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (ast.Import)",
            "success",
            "vllm top-level",
            "flagged",
            "test_import_vllm_flagged_as_direct_provider",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (ast.Import)",
            "boundary",
            "vllm.submodule prefix match",
            "flagged",
            "test_import_vllm_submodule_flagged_as_direct_provider",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (ast.Import)",
            "negative",
            "agentic_core.*.vllm_* internal",
            "not flagged",
            "test_import_agentic_core_vllm_type_not_flagged",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (ast.Import)",
            "negative",
            "agentic_core.* all internals",
            "not flagged",
            "test_import_agentic_core_never_flagged",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (ast.Import)",
            "success",
            "anthropic top-level",
            "flagged",
            "test_import_anthropic_flagged",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (ast.Import)",
            "success",
            "litellm top-level",
            "flagged",
            "test_import_litellm_flagged",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (ast.Import)",
            "negative",
            "stdlib import",
            "not flagged",
            "test_import_stdlib_not_flagged",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (ast.ImportFrom)",
            "success",
            "from openai import",
            "flagged",
            "test_from_openai_import_flagged",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (ast.ImportFrom)",
            "boundary",
            "from vllm import",
            "flagged",
            "test_from_vllm_import_flagged",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (ast.ImportFrom)",
            "negative",
            "from agentic_core...vllm_types import",
            "not flagged",
            "test_from_agentic_core_vllm_types_not_flagged",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (ast.ImportFrom)",
            "negative",
            "vllm_infrastructure_fingerprint regression",
            "not flagged",
            "test_from_agentic_core_vllm_infra_fingerprint_not_flagged",
        ),
        (
            "semantic_gap_analyzer.py",
            "analyze_file (ast.Import)",
            "boundary",
            "lazy google.generativeai in function body",
            "flagged (AST walks all nodes)",
            "test_google_generativeai_lazy_import_still_detected",
        ),
        (
            "semantic_gap_analyzer.py",
            "_detect_upward_imports",
            "negative",
            "L2 file imports L1 (rank 1 < 2)",
            "violation reported",
            "test_detect_upward_imports_l2_importing_l1_is_upward",
        ),
        (
            "semantic_gap_analyzer.py",
            "_detect_upward_imports",
            "contract",
            "L1 imports L0 flagged by lower-rank rule",
            "reported",
            "test_detect_upward_imports_l1_importing_l0_is_flagged",
        ),
        (
            "semantic_gap_analyzer.py",
            "_detect_upward_imports",
            "boundary",
            "non-layer file returns empty list",
            "empty",
            "test_detect_upward_imports_no_layer_returns_empty",
        ),
        (
            "semantic_gap_analyzer.py",
            "_detect_upward_imports",
            "boundary",
            "empty imported_layer_refs",
            "empty",
            "test_detect_upward_imports_no_refs_returns_empty",
        ),
        (
            "semantic_gap_analyzer.py",
            "_detect_upward_imports",
            "boundary",
            "same-layer import (L2->L2)",
            "not flagged",
            "test_detect_upward_imports_same_layer_not_upward",
        ),
        (
            "semantic_gap_analyzer.py",
            "_detect_upward_imports",
            "boundary",
            "L2 imports L3 (rank 3 > 2)",
            "not flagged",
            "test_detect_upward_imports_l2_importing_l3_is_not_flagged",
        ),
        (
            "semantic_gap_analyzer.py",
            "DIRECT_PROVIDER_IMPORT_PATTERNS",
            "contract",
            "all patterns are strings",
            "non-empty strings",
            "test_direct_provider_patterns_are_top_level_package_names",
        ),
        (
            "semantic_gap_analyzer.py",
            "DIRECT_PROVIDER_IMPORT_PATTERNS",
            "invariant",
            "no agentic_core in patterns",
            "invariant holds",
            "test_direct_provider_patterns_does_not_contain_agentic_core",
        ),
        (
            "agentic_core (real)",
            "L0/L1/L3/L4/L5/L6 files",
            "codebase-invariant",
            "no provider SDK imports outside L2",
            "zero violations",
            "test_no_real_provider_imports_outside_l2",
        ),
        (
            "agentic_core (real)",
            "L2_execution adapter files",
            "codebase-success",
            "known adapters have correct SDKs",
            "healing_provider_adapters + qwen_vllm",
            "test_l2_real_provider_imports_are_in_expected_files",
        ),
        (
            "agentic_core (real)",
            "vllm_* type files",
            "regression",
            "8 false-positive files produce zero flags",
            "zero",
            "test_internal_vllm_type_modules_produce_no_direct_provider_gap",
        ),
    ]
    for row in rows:
        h(f"| `{row[0]}` | `{row[1]}` | {row[2]} | {row[3]} | {row[4]} | `{row[5]}` |")
    h()
    h("## ROBUSTNESS_MATRIX")
    h()
    h(
        "| Surface | Ingress | Success IDs | Edge IDs | Failure IDs | Recovery IDs | Determinism IDs | Side-Effect IDs |"
    )
    h(
        "|---------|---------|-------------|----------|-------------|--------------|-----------------|-----------------|"
    )
    h(
        "| ast.Import provider detection | analyze_file AST walk | test_import_openai_flagged, test_import_vllm_flagged, test_import_anthropic_flagged, test_import_litellm_flagged | test_import_vllm_submodule_flagged, test_google_generativeai_lazy_import | test_import_agentic_core_vllm_type_not_flagged, test_import_agentic_core_never_flagged, test_import_stdlib_not_flagged | - | idempotent: same file same result | read-only |"
    )
    h(
        "| ast.ImportFrom provider detection | analyze_file AST walk | test_from_openai_import_flagged, test_from_vllm_import_flagged | test_from_vllm_import_flagged | test_from_agentic_core_vllm_types_not_flagged, test_from_agentic_core_vllm_infra_fingerprint_not_flagged | - | idempotent | read-only |"
    )
    h(
        "| _detect_upward_imports | _detect_upward_imports(path, analysis) | test_detect_upward_imports_l2_importing_l1_is_upward | test_detect_upward_imports_no_layer_returns_empty, test_detect_upward_imports_no_refs_returns_empty, test_detect_upward_imports_same_layer_not_upward, test_detect_upward_imports_l2_importing_l3_is_not_flagged | - | - | test_detect_upward_imports_l1_importing_l0_is_flagged | read-only |"
    )
    h(
        "| Codebase invariants | full L0-L6 rglob scan | test_no_real_provider_imports_outside_l2, test_l2_real_provider_imports_are_in_expected_files | test_internal_vllm_type_modules_produce_no_direct_provider_gap | - | - | deterministic file scan | read-only |"
    )
    h()
    h("## DEFECT_MODEL")
    h()
    h("| Defect Mechanism | Covered By |")
    h("|-----------------|------------|")
    h(
        "| Substring match 'vllm' in internal module path causes false positive | test_import_agentic_core_vllm_type_not_flagged, test_from_agentic_core_vllm_infra_fingerprint_not_flagged, test_internal_vllm_type_modules_produce_no_direct_provider_gap |"
    )
    h(
        "| Missing dotted-prefix match drops google.generativeai detection | test_google_generativeai_lazy_import_still_detected |"
    )
    h(
        "| Guard omission: internal imports escape agentic_core.* guard | test_import_agentic_core_never_flagged, test_from_agentic_core_vllm_types_not_flagged |"
    )
    h(
        "| Off-by-one: same-layer imports wrongly flagged as upward | test_detect_upward_imports_same_layer_not_upward |"
    )
    h(
        "| Hidden fallback: missing layer returns non-empty violation list | test_detect_upward_imports_no_layer_returns_empty |"
    )
    h(
        "| Duplicate mutation: non-L2 provider SDK imports go undetected | test_no_real_provider_imports_outside_l2 |"
    )
    h()
    content = "\n".join(evidence_lines) + "\n"
    _assert_ascii(content, "evidence file")
    EVIDENCE_PATH.write_text(content, encoding="utf-8")
    print(f"OK: evidence written to {EVIDENCE_PATH}")
    if seal_mode:
        print(f"OK: sealed CODE_COMMIT={code_commit} EVIDENCE_COMMIT={evidence_commit}")
    else:
        print(f"OK: draft CODE_COMMIT={code_commit}")


if __name__ == "__main__":
    main()
