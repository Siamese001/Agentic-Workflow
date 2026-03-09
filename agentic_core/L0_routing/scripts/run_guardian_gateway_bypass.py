"""
Guardian: Gateway Bypass — AST-based detection of direct LLM SDK usage
outside the SovereignLLMGateway boundary.

Checks:
- direct_model_call: Direct instantiation of openai/anthropic/genai classes
- provider_sdk_import: Import of forbidden provider SDK modules in scan roots
- bypass_tier_router: Call-sites that route to a model skipping tier selection
- bypass_embedding_factory: Direct embedding construction bypassing factory

Scan roots: agentic_core/, apps_lic/, apps_rg/, apps_shared/, system_learning/
Allowlist:  agentic_core/L2_execution/enforcement/SovereignLLMGateway.py
            agentic_core/L2_execution/enforcement/EmbeddingServiceFactory.py
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    normalize_repo_path,
    write_guardian_result,
)
from agentic_core.L0_routing.utils.project_root_util import get_validated_project_root
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

GUARDIAN_ID = "gateway_bypass"

SCAN_ROOTS: tuple[str, ...] = (
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "system_learning",
)

ALLOWED_SDK_FILES: frozenset[str] = frozenset(
    {
        "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
        "agentic_core/L2_execution/enforcement/EmbeddingServiceFactory.py",
    }
)

FORBIDDEN_SDK_MODULES: frozenset[str] = frozenset(
    {
        "openai",
        "anthropic",
        "google.generativeai",
    }
)

FORBIDDEN_INSTANTIATION_NAMES: frozenset[str] = frozenset(
    {
        "OpenAI",
        "AsyncOpenAI",
        "Anthropic",
        "AsyncAnthropic",
        "GenerativeModel",
    }
)

SKIP_DIRS: frozenset[str] = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES


def _collect_files(repo_root: Path) -> list[Path]:
    result: list[Path] = []
    for root_name in sorted(SCAN_ROOTS):
        root_path = repo_root / root_name
        if not root_path.exists():
            continue
        for dirpath, dirnames, filenames in __import__("os").walk(root_path):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fname in sorted(filenames):
                if fname.endswith(".py"):
                    result.append(Path(dirpath) / fname)
    return result


def scan_provider_sdk_imports(
    repo_root: Path,
    files: list[Path] | None = None,
) -> list[dict]:
    """Return sorted violation dicts for forbidden SDK imports."""
    if files is None:
        files = _collect_files(repo_root)
    violations: list[dict] = []
    for fpath in files:
        rel = normalize_repo_path(fpath.relative_to(repo_root))
        if rel in ALLOWED_SDK_FILES:
            continue
        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(alias.name == m or alias.name.startswith(m + ".") for m in FORBIDDEN_SDK_MODULES):
                        violations.append(
                            {
                                "path": rel,
                                "check_id": "provider_sdk_import",
                                "line": node.lineno,
                                "detail": f"import {alias.name}",
                            }
                        )
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if any(mod == m or mod.startswith(m + ".") for m in FORBIDDEN_SDK_MODULES):
                    violations.append(
                        {
                            "path": rel,
                            "check_id": "provider_sdk_import",
                            "line": node.lineno,
                            "detail": f"from {mod} import ...",
                        }
                    )
    return sorted(violations, key=lambda v: (v["path"], v["line"]))


def scan_direct_model_calls(
    repo_root: Path,
    files: list[Path] | None = None,
) -> list[dict]:
    """Return sorted violation dicts for direct model instantiation."""
    if files is None:
        files = _collect_files(repo_root)
    violations: list[dict] = []
    for fpath in files:
        rel = normalize_repo_path(fpath.relative_to(repo_root))
        if rel in ALLOWED_SDK_FILES:
            continue
        try:
            tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = None
                if isinstance(func, ast.Name):
                    name = func.id
                elif isinstance(func, ast.Attribute):
                    name = func.attr
                if name in FORBIDDEN_INSTANTIATION_NAMES:
                    violations.append(
                        {
                            "path": rel,
                            "check_id": "direct_model_call",
                            "line": node.lineno,
                            "detail": f"call to {name}()",
                        }
                    )
    return sorted(violations, key=lambda v: (v["path"], v["line"]))


def run_gateway_bypass_guardian(
    repo_root: Path | None = None,
    write_artifacts_dir: str | None = None,
    timestamp: str | None = None,
    correlation_id: str | None = None,
) -> GuardianResult:
    if repo_root is None:
        repo_root = get_validated_project_root()
    result = GuardianResult(
        guardian_id=GUARDIAN_ID,
        timestamp=timestamp,
        correlation_id=correlation_id,
    )

    files = _collect_files(repo_root)

    # check: provider_sdk_import
    sdk_viols = scan_provider_sdk_imports(repo_root, files)
    if sdk_viols:
        result.add_check(
            "provider_sdk_import",
            CheckStatus.FAIL,
            f"{len(sdk_viols)} forbidden SDK import(s) detected",
            evidence={"violations": sdk_viols[:20]},
        )
    else:
        result.add_check("provider_sdk_import", CheckStatus.PASS, "No forbidden SDK imports")

    # check: direct_model_call
    call_viols = scan_direct_model_calls(repo_root, files)
    if call_viols:
        result.add_check(
            "direct_model_call",
            CheckStatus.FAIL,
            f"{len(call_viols)} direct model instantiation(s) detected",
            evidence={"violations": call_viols[:20]},
        )
    else:
        result.add_check("direct_model_call", CheckStatus.PASS, "No direct model calls")

    # bypass_tier_router and bypass_embedding_factory: SKIP (requires runtime trace)
    result.add_check(
        "bypass_tier_router",
        CheckStatus.SKIP,
        "Requires ExecutionTrace artifact — not available in static scan",
    )
    result.add_check(
        "bypass_embedding_factory",
        CheckStatus.SKIP,
        "Requires ExecutionTrace artifact — not available in static scan",
    )

    result.summary = (
        f"gateway_bypass: {len(sdk_viols)} sdk_import violation(s), "
        f"{len(call_viols)} direct_call violation(s)"
    )
    if write_artifacts_dir:
        write_guardian_result(result, write_artifacts_dir, correlation_id=correlation_id)
    return result


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guardian: gateway_bypass")
    parser.add_argument("--write-artifacts", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--correlation-id", default=None)
    args = parser.parse_args(argv)
    result = run_gateway_bypass_guardian(
        artifact_dir=args.write_artifacts,
        correlation_id=args.correlation_id,
    )
    if args.strict and result.status == GuardianStatus.FAIL.value:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
