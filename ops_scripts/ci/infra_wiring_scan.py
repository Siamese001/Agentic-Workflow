"""
Infrastructure Wiring Scan Script

Scans for direct infrastructure imports in forbidden layers.
Blocks commits if violations are found.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_log = logging.getLogger(__name__)

# Forbidden direct imports in production layers
FORBIDDEN_IMPORTS = [
    "import redis",
    "from redis",
    "import chromadb",
    "from chromadb",
    "import sqlite3",
    "from sqlite3",
    "import boto3",
    "from boto3",
    "import openai",
    "from openai",
    "import anthropic",
    "from anthropic",
    "import httpx",
    "from httpx",
    "import requests",
    "from requests",
]

# Allowed directories for direct infra usage
ALLOWED_DIRS = {
    "tools",
    "infrastructure",
    "system_learning",
    "tests",
    "archives",
}

# Sanctioned adapter/owner files that MUST import raw infra
# These are the canonical wrappers — direct import is their job
SANCTIONED_ADAPTER_FILES = {
    # Redis adapters/owners (L2)
    "redis_cache_client.py",
    "RedisSovereignAgent.py",
    "sovereign_redis_orchestrator.py",
    "EmbeddingSovereignAgent.py",
    "CachedStateLedger.py",
    "semantic_cache_manager.py",
    # ChromaDB adapters/owners (L4)
    "chroma_client.py",
    "gptcache_client.py",
    "retrieval_layers.py",
    "in_memory_vector_cache.py",
    # SQLite adapters/owners (L4)
    "graph_knowledge_store.py",
    "chunk_manifest_registry.py",
    "completeness_snapshot_registry.py",
    "retrieval_eval_registry.py",
    "verdict_store.py",
    "evidence_assembler.py",
    # Boto3 adapters/owners (L4)
    "blob_storage_provider.py",
    "canonical_store.py",
    # OpenAI/provider adapters
    "semantic_enricher.py",
    # HTTP adapters
    "api_gateway_integration.py",
    "documentation_framework.py",
    # L3 ADG integration (reads ADG SQLite directly)
    "adg_integration.py",
    "hybrid_search_engine.py",
}

# Subdirectories within agentic_core that are infrastructure tooling
AGENTIC_CORE_INFRA_SUBDIRS = {
    "adg",
    "cache",
    "embeddings",
}


def scan_file(file_path: Path) -> list[tuple[int, str]] | None:
    """Scan a single Python file for forbidden imports.

    Returns:
        List of (line_number, import_pattern) tuples if violations found, None otherwise.
    """
    violations = []

    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, IOError, UnicodeDecodeError) as exc:
        _log.warning("Could not read %s: %s", file_path, exc)
        return None

    for line_num, line in enumerate(lines, start=1):
        line_stripped = line.strip()
        for forbidden in FORBIDDEN_IMPORTS:
            if line_stripped.startswith(forbidden):
                violations.append((line_num, forbidden))

    return violations if violations else None


def is_allowed_path(file_path: Path) -> bool:
    """Check if file is in an allowed directory for direct infra usage."""
    parts = file_path.parts

    # Check if any part of the path is in ALLOWED_DIRS
    for part in parts:
        if part in ALLOWED_DIRS:
            return True

    # apps_shared is shared infrastructure, not apps surface
    if "apps_shared" in parts:
        return True

    # Sanctioned adapter/owner files can import raw infra
    if file_path.name in SANCTIONED_ADAPTER_FILES:
        return True

    # agentic_core infrastructure subdirectories (adg, cache, embeddings)
    if "agentic_core" in parts:
        for subdir in AGENTIC_CORE_INFRA_SUBDIRS:
            if subdir in parts:
                return True

    return False


def scan_directory(root_dir: Path) -> dict[str, list[tuple[int, str]]]:
    """Scan all Python files in root directory.

    Returns:
        Dict mapping file paths to violations (line_number, import_pattern).
    """
    violations = {}

    # Scan agentic_core
    for py_file in root_dir.glob("agentic_core/**/*.py"):
        if not is_allowed_path(py_file):
            file_violations = scan_file(py_file)
            if file_violations:
                violations[str(py_file)] = file_violations

    # Scan apps_* (excluding apps_shared)
    for apps_dir in root_dir.glob("apps_*/"):
        if apps_dir.name != "apps_shared":
            for py_file in apps_dir.rglob("*.py"):
                if not is_allowed_path(py_file):
                    file_violations = scan_file(py_file)
                    if file_violations:
                        violations[str(py_file)] = file_violations

    return violations


def main() -> int:
    """Main entry point."""
    root_dir = Path(__file__).parent.parent.parent

    violations = scan_directory(root_dir)

    if violations:
        print("❌ Infrastructure Wiring Violations Detected")
        print("=" * 60)
        for file_path, file_violations in violations.items():
            print(f"\n{file_path}:")
            for line_num, import_pattern in file_violations:
                print(f"  Line {line_num}: {import_pattern}")
        print("\n" + "=" * 60)
        print("❌ Scan FAILED: Direct infra imports detected in forbidden layers")
        print("Fix: Use sanctioned adapters from L4 or infrastructure/sdks_mcps")
        return 1
    else:
        print("✅ Infrastructure Wiring Scan PASSED")
        print("No direct infra imports detected in forbidden layers")
        return 0


if __name__ == "__main__":
    sys.exit(main())
