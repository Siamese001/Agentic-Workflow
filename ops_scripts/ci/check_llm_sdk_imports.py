"""CI guard G7/G13: no LLM SDK or network client imports outside the gateway seam.

Blocks: openai, anthropic, google.generativeai, vertexai,
        requests, httpx, aiohttp, urllib.request (outside allowed boundary).
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

BLOCKED_TOP_LEVEL = {
    "openai",
    "anthropic",
    "vertexai",
    "requests",
    "httpx",
    "aiohttp",
    # Embedding SDK imports blocked outside EmbeddingServiceFactory (Spec: Sovereign LLM Gateway)
    "faiss",
    "sentence_transformers",
    "tiktoken",
}
BLOCKED_FROM = {("google", "generativeai"), ("urllib", "request")}

ALLOWED_PATHS = {
    "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
    "data/sdks_mcps/client_wrappers.py",
    "apps_shared/utils/providers_google_genai_client_util.py",
    # EmbeddingServiceFactory is the sole allowed seam for embedding SDK imports
    "system_learning/engines/embedding_service_factory.py",
    # OpenAI embedder: sovereign seam for OpenAI embedding API (wrapped by EmbeddingServiceFactory)
    "system_learning/engines/openai_embedder.py",
    # Healing provider adapters: sovereign seam for LLM SDK calls in the healing subsystem
    "agentic_core/L2_execution/healers/healing_provider_adapters.py",
    # LateInteractionReranker: sovereign seam for cross-encoder re-ranking (lazy imports, try/except fallback)
    "apps_shared/utils/late_interaction_reranker_util.py",
}

SCAN_ROOTS = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, SYSTEM_LEARNING_DIR]


def _blocked(node: ast.Import | ast.ImportFrom) -> str | None:
    if isinstance(node, ast.Import):
        for alias in node.names:
            top = alias.name.split(".")[0]
            if top in BLOCKED_TOP_LEVEL:
                return alias.name
    if isinstance(node, ast.ImportFrom) and node.module:
        parts = node.module.split(".")
        if parts[0] in BLOCKED_TOP_LEVEL:
            return node.module
        if len(parts) >= 2 and tuple(parts[:2]) in BLOCKED_FROM:
            return node.module
    return None


def main() -> int:
    violations: list[str] = []
    for root in SCAN_ROOTS:
        for path in (REPO_ROOT / root).rglob("*.py"):
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel in ALLOWED_PATHS:
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    hit = _blocked(node)
                    if hit:
                        violations.append(f"{rel}:{node.lineno}: blocked import '{hit}'")
    if violations:
        print(f"FAIL: {len(violations)} LLM/network SDK import violation(s):")
        for v in violations:
            print(f"  {v}")
        return 1
    print("OK: no forbidden LLM/network SDK imports")
    return 0


if __name__ == "__main__":
    sys.exit(main())
