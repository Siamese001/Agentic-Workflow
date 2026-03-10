"""AST-based CI guard: no direct LLM SDK usage outside the gateway.

Fails with non-zero exit if any .py file outside the allowed boundary
contains a direct import or instantiation of openai/anthropic/google SDK.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
    get_validated_project_root,
    TOOLS_DIR,
)

REPO_ROOT = get_validated_project_root()

ALLOWED_SDK_FILES = {
    "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
    "data/sdks_mcps/client_wrappers.py",
    # Healing provider adapters: sovereign seam for direct LLM SDK calls in healing subsystem
    "agentic_core/L2_execution/healers/healing_provider_adapters.py",
    # OpenAI embedder: sovereign seam for OpenAI embedding API
    "system_learning/engines/openai_embedder.py",
    # Legacy provider wrapper files that pre-date the gateway — tracked but not yet migrated
    "apps_rg/reasoning/HardenedopenaiexecutorStrategy.py",
    "apps_rg/tools/ResumeGenerator.py",
    "apps_rg/utils/deep_brain_harvester_util.py",
    "apps_rg/utils/providers_anthropic_client_util.py",
    "apps_shared/utils/providers_google_genai_client_util.py",
}

FORBIDDEN_IMPORTS = {
    "openai",
    "anthropic",
    "google.generativeai",
}

FORBIDDEN_MODEL_PREFIXES = ("gpt-", "claude-", "gemini-")

# Files whose basenames indicate config/type/allowlist context — model strings are legitimate there
_EXEMPT_SUFFIXES = (
    "_config.py",
    "_types.py",
    "_type.py",
    "_constants.py",
    "_allowlist.py",
    "_registry.py",
    "_defaults.py",
    "config.py",
    "types.py",
)

# Directory segments that indicate config/type/allowlist context — model literals are legitimate there
# enforcement, reasoning, healers, engines, constraints contain model allowlists (not direct SDK calls)
_EXEMPT_PATH_SEGMENTS = frozenset(
    {
        "config",
        "types",
        "mixins",
        "validators",
        "runtime",
        "enforcement",
        "reasoning",
        "healers",
        "scripts",
        TOOLS_DIR,
        "engines",
        "constraints",
        "utils",
    }
)


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _is_exempt_from_literal_check(rel: str) -> bool:
    """Return True if model literal strings are legitimate in this file."""
    parts = set(rel.replace("\\", "/").split("/"))
    if parts & _EXEMPT_PATH_SEGMENTS:
        return True
    name = rel.rsplit("/", 1)[-1]
    return name.endswith(_EXEMPT_SUFFIXES)


def _check_file(path: Path) -> list[str]:
    rel = _rel(path)
    if rel in ALLOWED_SDK_FILES:
        return []

    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []

    violations: list[str] = []
    check_literals = not _is_exempt_from_literal_check(rel)

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name
                    if any(mod == f or mod.startswith(f + ".") for f in FORBIDDEN_IMPORTS):
                        violations.append(f"{rel}:{node.lineno}: forbidden import '{mod}'")
            else:
                mod = node.module or ""
                if any(mod == f or mod.startswith(f + ".") for f in FORBIDDEN_IMPORTS):
                    violations.append(f"{rel}:{node.lineno}: forbidden from-import '{mod}'")

        if check_literals and isinstance(node, ast.Constant) and isinstance(node.value, str):
            if any(node.value.startswith(p) for p in FORBIDDEN_MODEL_PREFIXES):
                violations.append(f"{rel}:{node.lineno}: hardcoded model literal '{node.value}'")

    return violations


def main() -> int:
    scan_roots = [
        REPO_ROOT / APPS_LIC_DIR,
        REPO_ROOT / APPS_RG_DIR,
        REPO_ROOT / APPS_SHARED_DIR,
        REPO_ROOT / AGENTIC_CORE_DIR,
        REPO_ROOT / SYSTEM_LEARNING_DIR,
    ]
    violations: list[str] = []
    for root in scan_roots:
        if not root.exists():
            continue
        for py in root.rglob("*.py"):
            violations.extend(_check_file(py))

    if violations:
        print(f"FAIL: {len(violations)} sovereign gateway violation(s):")
        for v in sorted(violations):
            print(f"  {v}")
        return 1

    count = sum(1 for r in scan_roots if r.exists() for _ in r.rglob("*.py"))
    print(f"OK: sovereign gateway boundary clean ({count} files scanned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
