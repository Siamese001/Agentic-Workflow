"""apps_rg PA boundary anti-bypass scanner — W6 of plan apps-rg-spine-hardening-7e3b9c.

AST-based scanner that detects PA boundary bypass patterns in apps_rg and the shared
agentic_core/prompt_governance/ surface (expanded per ADR-083 D4):

- VIOLATION_DIRECT_PROVIDER_CALL_BYPASS — direct anthropic.Anthropic / openai.OpenAI / vllm
  client construction outside the sanctioned allowlist.
- VIOLATION_PROVIDER_READY_PROMPT_OUTSIDE_PA — provider message arrays
  (list of {"role":..., "content":...} dicts) constructed outside `apps_rg/prompt_assembly/`
  or `agentic_core/prompt_governance/prompt_assembly/`.
- VIOLATION_RAW_STRING_LLM_CALL — calls to .messages.create / .chat.completions.create
  with a hardcoded prompt string literal (not a CompiledPromptArtifact).

CONDITIONAL_V1 baseline: sites in CONDITIONAL_V1_BASELINE are known direct-SDK callers
with PA-BOM receipts; they are reported as WARN (not ERROR) until NEXT_STEP-1 completes.

Posture:
- Advisory by default (exit 0 with warnings).
- Fail-closed when APPS_RG_PA_BOUNDARY_FAIL_CLOSED=1 (exit 1 on any ERROR finding).
- Bypass via APPS_RG_PA_BOUNDARY_BYPASS=1 (logged, exit 0).

Output:
- Stdout: human-readable findings table.
- artifacts/windsurf/apps_rg_pa_boundary_violations.jsonl — durable audit log.

Per constitutional §22 + ADR-083 + adg-graph-layer-enforcement.md.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_RG = REPO_ROOT / "apps_rg"
APPS_QNA = REPO_ROOT / "apps_qna"
PROMPT_GOVERNANCE = REPO_ROOT / "agentic_core" / "prompt_governance"
ASSEMBLY_STAGE = REPO_ROOT / "agentic_core" / "L0_routing" / "reasoning" / "assembly_stage.py"
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "apps_rg_pa_boundary_violations.jsonl"

# Files SANCTIONED to construct provider clients / messages in apps_rg
ALLOWLIST_FILES = {
    "apps_rg/integrations/llm_client.py",
    "apps_rg/utils/anthropic_rag_entrypoint.py",
    "apps_rg/prompt_assembly/compiler.py",
    "apps_rg/prompt_assembly/provider_request.py",
    "apps_rg/prompt_assembly/pa_local.py",
    # Hardened executor — circuit-breaker + retry wrapper; direct SDK call
    # is the sanctioned low-level path for this resilience middleware.
    # Pillar 8 (Tool Ecosystem Resilience). ADR-083 D2.
    "apps_rg/enforcement/HardenedanthropicexecutorStrategy.py",
    "apps_rg/validators/enforcement/HardenedanthropicexecutorStrategy.py",
    # apps_qna sanctioned shim — re-exports from infrastructure/sdks_mcps;
    # NOT a bypass; re-exports are not direct constructions. W5 P5.1.
    "apps_qna/integrations/llm_client.py",
}

# Files SANCTIONED in agentic_core/prompt_governance (canonical PA pipeline constructs
# provider message arrays legitimately inside pa6_provider_rendering.py)
ALLOWLIST_AGENTIC_CORE = {
    "agentic_core/prompt_governance/prompt_assembly/pa6_provider_rendering.py",
    "agentic_core/prompt_governance/prompt_assembly/pa0_boundary.py",
    "agentic_core/prompt_governance/core/prompt_assembler.py",
    "agentic_core/prompt_governance/core/sovereign_prompt_renderer.py",
}

# CONDITIONAL_V1 baseline — known direct-SDK callers with PA-BOM receipts present.
# Reported as WARN (not ERROR) until NEXT_STEP-1 (SovereignLLMGateway wiring) completes.
# ADR-083 D3: ratified 2026-05-09.
#
# Note: hops/_llm_client.py V2/V3 findings (provider message arrays + raw-string calls)
# are also baselined here because they co-locate with the baselined V1 sites and
# share the same NEXT_STEP-1 remediation path. All findings from this file are WARN
# until SovereignLLMGateway wiring is complete.
CONDITIONAL_V1_BASELINE = {
    "apps_rg/integrations/hops/_llm_client.py",
    # apps_qna W5 P5.1 — lazy-import, env-gated, fail-soft SDK callers;
    # same NEXT_STEP-1 (SovereignLLMGateway wiring) remediation path.
    # Baselined 2026-05-09.
    "apps_qna/engines/dispatch/provider_dispatch.py",
    "apps_qna/integrations/intent_classifier.py",
    "apps_qna/engines/judges/interview_card_quality_judge.py",
    "apps_qna/integrations/provider_adapter.py",
}

# Provider client constructors (high-confidence)
PROVIDER_CLIENTS = {
    "Anthropic",
    "AsyncAnthropic",
    "OpenAI",
    "AsyncOpenAI",
    "AzureOpenAI",
    "VertexAI",
    "Groq",
}

# LLM call methods that should consume CompiledPromptArtifact
LLM_CALL_METHODS = {
    "create",  # .messages.create / .chat.completions.create
    "complete",
    "completion",
}


@dataclass
class Finding:
    severity: str  # ERROR | WARN | INFO
    code: str
    file: str
    line: int
    message: str
    extra: dict = field(default_factory=dict)


def _is_allowlisted(rel_path: str) -> bool:
    rel_norm = rel_path.replace("\\", "/")
    return rel_norm in ALLOWLIST_FILES or rel_norm in ALLOWLIST_AGENTIC_CORE


def _is_conditional_v1(rel_path: str) -> bool:
    """Return True if this file is in the CONDITIONAL_V1 baseline (WARN not ERROR)."""
    return rel_path.replace("\\", "/") in CONDITIONAL_V1_BASELINE


def _scan_file(path: Path) -> list[Finding]:
    """Scan a single .py file for PA boundary violations."""
    findings: list[Finding] = []
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return findings

    rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    allowlisted = _is_allowlisted(rel)

    for node in ast.walk(tree):
        # V1: direct provider client construction
        if isinstance(node, ast.Call):
            ctor_name = ""
            if isinstance(node.func, ast.Name):
                ctor_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                ctor_name = node.func.attr
            if ctor_name in PROVIDER_CLIENTS and not allowlisted:
                conditional = _is_conditional_v1(rel)
                findings.append(Finding(
                    severity="WARN" if conditional else "ERROR",
                    code="CONDITIONAL_V1_BASELINED" if conditional else "VIOLATION_DIRECT_PROVIDER_CALL_BYPASS",
                    file=rel,
                    line=node.lineno,
                    message=(
                        f"Direct {ctor_name} client — CONDITIONAL_V1 (PA-BOM receipt present; NEXT_STEP-1 pending)"
                        if conditional else
                        f"Direct {ctor_name} client constructed outside sanctioned shim"
                    ),
                    extra={"constructor": ctor_name, "conditional_v1": conditional},
                ))

        # V3: raw-string LLM call — .messages.create(model=..., messages=[{"role": "user", "content": "literal"}])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in LLM_CALL_METHODS and not allowlisted:
                # Check if any kwarg is a list of dicts with hardcoded "content" string
                for kw in node.keywords:
                    if kw.arg == "messages" and isinstance(kw.value, ast.List):
                        for item in kw.value.elts:
                            if isinstance(item, ast.Dict):
                                for k, v in zip(item.keys, item.values):
                                    if (
                                        isinstance(k, ast.Constant)
                                        and k.value == "content"
                                        and isinstance(v, ast.Constant)
                                        and isinstance(v.value, str)
                                        and len(v.value) > 40
                                    ):
                                        conditional_v3 = _is_conditional_v1(rel)
                                        findings.append(Finding(
                                            severity="WARN" if conditional_v3 else "ERROR",
                                            code="CONDITIONAL_V1_BASELINED" if conditional_v3 else "VIOLATION_RAW_STRING_LLM_CALL",
                                            file=rel,
                                            line=node.lineno,
                                            message=(
                                                f".{node.func.attr}() — CONDITIONAL_V1 (raw-string call; NEXT_STEP-1 pending)"
                                                if conditional_v3 else
                                                f".{node.func.attr}() called with hardcoded message content string"
                                            ),
                                            extra={"method": node.func.attr, "conditional_v1": conditional_v3},
                                        ))
                                        break

        # V2: provider message array constructed outside PA
        # Heuristic: literal list of dicts where every dict has "role" and "content" keys
        if isinstance(node, ast.List) and not allowlisted:
            if len(node.elts) >= 1 and all(isinstance(e, ast.Dict) for e in node.elts):
                all_have_role_content = True
                for d in node.elts:
                    keys = {k.value for k in d.keys if isinstance(k, ast.Constant)}
                    if not ({"role", "content"} <= keys):
                        all_have_role_content = False
                        break
                if all_have_role_content and "/prompt_assembly/" not in rel and "prompt_governance/prompt_assembly" not in rel:
                    findings.append(Finding(
                        severity="WARN",
                        code="VIOLATION_PROVIDER_READY_PROMPT_OUTSIDE_PA",
                        file=rel,
                        line=node.lineno,
                        message=(
                            "Provider message array (list of {role,content}) constructed outside "
                            "apps_rg/prompt_assembly/ — must consume CompiledPromptArtifact"
                        ),
                        extra={"item_count": len(node.elts)},
                    ))

    return findings


def _iter_apps_rg_files() -> Iterator[Path]:
    for path in APPS_RG.rglob("*.py"):
        rel = path.relative_to(REPO_ROOT)
        parts = rel.parts
        if "__pycache__" in parts or "tests" in parts or "_archive" in parts:
            continue
        yield path


def _iter_apps_qna_files() -> Iterator[Path]:
    """Iterate apps_qna PA surface. W5 P5.1."""
    for path in APPS_QNA.rglob("*.py"):
        rel = path.relative_to(REPO_ROOT)
        parts = rel.parts
        if "__pycache__" in parts or "tests" in parts or "_archive" in parts:
            continue
        yield path


def _iter_agentic_core_pa_files() -> Iterator[Path]:
    """Iterate agentic_core PA surface: prompt_governance/ + assembly_stage.py.

    ADR-083 D4: expanded scanner scope.
    """
    if PROMPT_GOVERNANCE.exists():
        for path in PROMPT_GOVERNANCE.rglob("*.py"):
            rel = path.relative_to(REPO_ROOT)
            parts = rel.parts
            if "__pycache__" in parts or "tests" in parts:
                continue
            yield path
    if ASSEMBLY_STAGE.exists():
        yield ASSEMBLY_STAGE


def _emit_violations_log(findings: list[Finding], bypassed: bool) -> None:
    """Append a summary row to the violations log."""
    VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scanner": "check_apps_rg_pa_boundary",
        "bypassed": bypassed,
        "finding_count": len(findings),
        "by_severity": {
            "ERROR": sum(1 for f in findings if f.severity == "ERROR"),
            "WARN": sum(1 for f in findings if f.severity == "WARN"),
            "INFO": sum(1 for f in findings if f.severity == "INFO"),
        },
        "findings": [
            {
                "severity": f.severity,
                "code": f.code,
                "file": f.file,
                "line": f.line,
                "message": f.message,
                "extra": f.extra,
            }
            for f in findings
        ],
    }
    with VIOLATIONS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true", help="suppress per-finding output")
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    parser.add_argument(
        "--scan-dir",
        default=None,
        help="Limit scan to a specific directory (relative to repo root). Omit to scan all surfaces.",
    )
    parser.add_argument(
        "--no-agentic-core",
        action="store_true",
        help="Skip agentic_core/prompt_governance/ scan (apps_rg only).",
    )
    parser.add_argument(
        "--no-apps-qna",
        action="store_true",
        help="Skip apps_qna/ scan.",
    )
    args = parser.parse_args(argv)

    if os.environ.get("APPS_RG_PA_BOUNDARY_BYPASS") == "1":
        print("[apps_rg-pa-boundary] BYPASSED via APPS_RG_PA_BOUNDARY_BYPASS=1")
        _emit_violations_log([], bypassed=True)
        return 0

    fail_closed = os.environ.get("APPS_RG_PA_BOUNDARY_FAIL_CLOSED") == "1"

    all_findings: list[Finding] = []
    file_count = 0

    if args.scan_dir:
        # Targeted scan of a specific directory
        target = REPO_ROOT / args.scan_dir
        for path in target.rglob("*.py") if target.is_dir() else [target]:
            rel = path.relative_to(REPO_ROOT)
            parts = rel.parts
            if "__pycache__" in parts or "tests" in parts or "_archive" in parts:
                continue
            file_count += 1
            all_findings.extend(_scan_file(path))
    else:
        # Full scan: apps_rg + apps_qna + agentic_core PA surface
        for path in _iter_apps_rg_files():
            file_count += 1
            all_findings.extend(_scan_file(path))
        if not args.no_apps_qna:
            for path in _iter_apps_qna_files():
                file_count += 1
                all_findings.extend(_scan_file(path))
        if not args.no_agentic_core:
            for path in _iter_agentic_core_pa_files():
                file_count += 1
                all_findings.extend(_scan_file(path))

    error_count = sum(1 for f in all_findings if f.severity == "ERROR")
    warn_count = sum(1 for f in all_findings if f.severity == "WARN")

    conditional_count = sum(1 for f in all_findings if f.code == "CONDITIONAL_V1_BASELINED")

    if args.json:
        print(json.dumps({
            "scanner": "check_apps_rg_pa_boundary",
            "files_scanned": file_count,
            "conditional_v1_baselined": conditional_count,
            "findings": [
                {"severity": f.severity, "code": f.code, "file": f.file, "line": f.line, "message": f.message}
                for f in all_findings
            ],
        }, indent=2))
    else:
        print(f"[apps_rg-pa-boundary] scanned {file_count} files")
        print(f"[apps_rg-pa-boundary] ERROR={error_count} WARN={warn_count} (CONDITIONAL_V1_BASELINED={conditional_count})")
        if not args.quiet:
            for f in all_findings:
                print(f"  {f.severity:5s} {f.code:50s} {f.file}:{f.line}  {f.message}")
        if conditional_count:
            print(f"[apps_rg-pa-boundary] {conditional_count} CONDITIONAL_V1 site(s) baselined — ADR-083 D3; NEXT_STEP-1 tracks SovereignLLMGateway wiring")
        if fail_closed:
            print("[apps_rg-pa-boundary] mode=fail-closed (APPS_RG_PA_BOUNDARY_FAIL_CLOSED=1)")
        else:
            print("[apps_rg-pa-boundary] mode=advisory (set APPS_RG_PA_BOUNDARY_FAIL_CLOSED=1 to enforce)")

    _emit_violations_log(all_findings, bypassed=False)

    if fail_closed and error_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
