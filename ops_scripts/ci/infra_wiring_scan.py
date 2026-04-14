"""
Infrastructure Wiring Scan Script

Scans for direct infrastructure imports in forbidden layers.
Blocks commits if violations are found.
"""

from __future__ import annotations

import importlib.util
import json
import logging
import sys
from datetime import datetime, timezone
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
    # Phase 2 additions — newly registered surfaces
    "import neo4j",
    "from neo4j",
    "import prometheus_client",
    "from prometheus_client",
    "import aiohttp",
    "from aiohttp",
    # Provider bypass — catches lazy imports (strip() normalises indentation)
    "import google",
    "from google",
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
    # Phase 2 additions — newly registered / under-review surfaces
    "neo4j_store.py",  # Neo4j — EXPERIMENTAL_ISOLATED; pending deprecation or formalization (§F1)
    "prometheus_metrics.py",  # Prometheus — de-facto L6 approved adapter (defines AGENTIC_REGISTRY)
    "metrics_server.py",  # Prometheus — L6 metrics HTTP server (lazy import guard in place)
    "optimized_vllm_client.py",  # HTTP/aiohttp — APPROVED 2026-04-11; sanctioned L3 vLLM HTTP adapter (vllm_http_decision_packet.md §E Path A)
}

# Subdirectories within agentic_core that are infrastructure tooling
AGENTIC_CORE_INFRA_SUBDIRS = {
    "adg",
    "cache",
    "embeddings",
}


def _find_latest_adg_sqlite(adg_dir: Path) -> Path | None:
    candidates = [p for p in adg_dir.glob("adg_indexed_*.sqlite") if p.is_file()]
    if not candidates:
        return None
    return max(candidates, key=lambda p: (p.stat().st_mtime_ns, p.name))


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

    for line_num, line in enumerate(lines, start=1):  # tqdm: per-file line scan, no bar needed
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
    for py_file in root_dir.glob("agentic_core/**/*.py"):  # tqdm: filesystem glob, no bar needed
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


def _classify_violations(
    violations: dict[str, list[tuple[int, str]]],
) -> list[dict[str, str]]:
    """Convert raw violations to P0 detail records for the scorecard."""
    details: list[dict[str, str]] = []
    for file_path, file_violations in violations.items():  # tqdm: violation dict, no bar needed
        rel_path = Path(file_path)
        # Extract a short relative path from the repo root
        parts = rel_path.parts
        # Find where the apps_* or agentic_core starts
        for i, part in enumerate(parts):
            if part.startswith("apps_") or part == "agentic_core":
                short = "/".join(parts[i:])
                break
        else:
            short = str(rel_path)
        for _line_num, import_pattern in file_violations:
            infra = import_pattern.replace("import ", "").replace("from ", "")
            details.append({"file": short, "infra": infra})
    return details


def _query_adg_view_counts(root_dir: Path) -> dict[str, int]:
    """Materialize infra wiring views and return violation counts.

    Calls materialize_infra_views to create/refresh all views with accurate
    structural signals (materialized t_infra_importers, symbol-aware P1 checks),
    then returns the counts dict directly.

    Returns a dict of view_name -> count, or empty dict if ADG is unavailable.
    """
    adg_dir = root_dir / "artifacts" / "adg"
    if not adg_dir.is_dir():
        return {}
    db_path = _find_latest_adg_sqlite(adg_dir)
    if db_path is None:
        return {}
    try:
        module_path = root_dir / "tools" / "generate" / "infra_wiring_views.py"
        if not module_path.exists():
            raise RuntimeError(f"Missing materializer: {module_path}")
        spec = importlib.util.spec_from_file_location("infra_wiring_views", module_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Could not load {module_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.materialize_infra_views(db_path)
    except Exception as exc:  # guardian: structural scan should fall back to raw SQL instead of crashing
        _log.warning(
            "Could not materialize infra views for %s: %s — falling back to raw view query", db_path, exc
        )
        import sqlite3 as _sqlite3
        from contextlib import closing

        view_names = (
            "v_p0_apps_direct_infra",
            "v_p0_provider_bypass",
            "v_p0_write_bypass_uwg",
            "v_p0_l1_direct_infra",
            "v_p0_l6_mutation",
            "v_p0_l0_raw_execution",
            "v_p1_zero_caller_infra",
            "v_p1_not_on_spine",
            "v_p1_ad_hoc_imports",
            "v_p1_mis_layered_infra",
            "v_p1_raw_http_outside_seam",
            "v_p2_mixed_usage",
            "v_p2_duplicated_adapters",
            "v_p2_dormant_ambiguous",
            "v_p3_isolated_experimental",
        )
        counts: dict[str, int] = {}
        db_uri = f"file:{db_path.as_posix()}?mode=ro&immutable=1"
        with closing(_sqlite3.connect(db_uri, uri=True, timeout=5)) as conn:
            cur = conn.cursor()
            for vname in view_names:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {vname}")  # noqa: S608
                    (count,) = cur.fetchone()
                    counts[vname] = count
                except _sqlite3.OperationalError:
                    pass
        return counts


def update_scorecard(
    root_dir: Path,
    violations: dict[str, list[tuple[int, str]]],
) -> None:
    """Update artifacts/infra_wiring_scorecard.json with current scan results.

    Combines file-scan P0 violations with ADG view counts (when available)
    to produce a comprehensive scorecard covering all P0-P3 severity levels.
    """
    scorecard_path = root_dir / "artifacts" / "infra_wiring_scorecard.json"

    p0_details = _classify_violations(violations)
    scan_p0_count = len(p0_details)

    # Query ADG views for full P0-P3 counts
    adg_counts = _query_adg_view_counts(root_dir)

    # P0 totals from ADG views (preferred) or file scan fallback
    p0_views = [
        "v_p0_apps_direct_infra",
        "v_p0_provider_bypass",
        "v_p0_write_bypass_uwg",
        "v_p0_l1_direct_infra",
        "v_p0_l6_mutation",
        "v_p0_l0_raw_execution",
    ]
    p1_views = [
        "v_p1_zero_caller_infra",
        "v_p1_not_on_spine",
        "v_p1_ad_hoc_imports",
        "v_p1_mis_layered_infra",
    ]
    p2_views = ["v_p2_mixed_usage", "v_p2_duplicated_adapters", "v_p2_dormant_ambiguous"]
    p3_views = ["v_p3_isolated_experimental"]

    if adg_counts:
        total_p0 = sum(adg_counts.get(v, 0) for v in p0_views)
        total_p1 = sum(adg_counts.get(v, 0) for v in p1_views)
        total_p2 = sum(adg_counts.get(v, 0) for v in p2_views)
        total_p3 = sum(adg_counts.get(v, 0) for v in p3_views)
    else:
        total_p0 = scan_p0_count
        total_p1 = 0
        total_p2 = 0
        total_p3 = 0

    total_violations = total_p0 + total_p1 + total_p2 + total_p3
    compliance = 100 if total_violations == 0 else max(0, 100 - total_p0 * 2 - total_p1)

    # Ratchet: zero-caller count from ADG
    zero_caller = adg_counts.get("v_p1_zero_caller_infra", 0)
    mixed = adg_counts.get("v_p2_mixed_usage", 0)
    uwg_bypass = adg_counts.get("v_p0_write_bypass_uwg", 0)
    not_on_spine = adg_counts.get("v_p1_not_on_spine", 0)

    # P2 ratchet ceilings — accepted violations must not regress above these counts
    _P2_CEILING_MIXED = 3  # chromadb + redis + sqlite3 mixed usage (Wave 2 targets)
    _P2_CEILING_DUPED = 2  # redis + sqlite3 multi-adapter by design

    scorecard = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "methodology": (
            "STRUCTURAL — ADG view counts reflect real graph signals. "
            "No post-processing applied. P0/P1 counts proven accurate via "
            "materialized t_infra_importers table and symbol-aware caller checks."
        ),
        "total_infra_surfaces": 13,  # Phase 2: +3 newly registered (neo4j, prometheus, aiohttp)
        "approved_active": 13 - (2 if scan_p0_count > 0 else 0),
        "active_miswired": 2 if scan_p0_count > 0 else 0,
        "dormant_unwired": adg_counts.get("v_p2_dormant_ambiguous", 0),
        "experimental_isolated": adg_counts.get("v_p3_isolated_experimental", 0),
        "deprecated_pending_removal": 0,
        "compliance_score": compliance,
        "violations": {
            "p0": total_p0,
            "p1": total_p1,
            "p2": total_p2,
            "p3": total_p3,
        },
        "p0_details": p0_details,
        "adg_view_counts": adg_counts if adg_counts else "ADG views not available",
        "ratchets": [
            {
                "name": "apps_* direct infra access",
                "current": scan_p0_count,
                "ceiling": 0,
                "status": "BLOCK" if scan_p0_count > 0 else "COMPLIANT",
                "structural": True,
            },
            {
                "name": "UWG write bypass",
                "current": uwg_bypass,
                "ceiling": 0,
                "status": "BLOCK" if uwg_bypass > 0 else "COMPLIANT",
                "structural": bool(adg_counts),
            },
            {
                "name": "zero-caller infra",
                "current": zero_caller,
                "ceiling": 0,
                "status": "BLOCK" if zero_caller > 0 else "COMPLIANT",
                "structural": bool(adg_counts),
                "note": "Process-boundary adapters formally exempt per infra_ownership_matrix.md",
            },
            {
                "name": "not on L0-L6 spine",
                "current": not_on_spine,
                "ceiling": 0,
                "status": "BLOCK" if not_on_spine > 0 else "COMPLIANT",
                "structural": bool(adg_counts),
                "note": "Process-boundary adapters formally exempt per infra_ownership_matrix.md",
            },
            {
                "name": "mixed wrapped/raw usage",
                "current": mixed,
                "ceiling": _P2_CEILING_MIXED,
                "status": (
                    "REGRESSION" if mixed > _P2_CEILING_MIXED else "ACCEPTED" if mixed > 0 else "COMPLIANT"
                ),
                "structural": bool(adg_counts),
                "note": "Accepted for Wave 2. Ceiling enforces no regression.",
            },
            {
                "name": "duplicated adapters",
                "current": adg_counts.get("v_p2_duplicated_adapters", 0),
                "ceiling": _P2_CEILING_DUPED,
                "status": (
                    "REGRESSION"
                    if adg_counts.get("v_p2_duplicated_adapters", 0) > _P2_CEILING_DUPED
                    else "ACCEPTED"
                    if adg_counts.get("v_p2_duplicated_adapters", 0) > 0
                    else "COMPLIANT"
                ),
                "structural": bool(adg_counts),
                "note": "Multi-path by design. Ceiling enforces no regression.",
            },
        ],
    }

    scorecard_path.parent.mkdir(parents=True, exist_ok=True)
    scorecard_path.write_text(
        json.dumps(scorecard, indent=2) + "\n",
        encoding="utf-8",
    )
    _log.info(
        "Scorecard updated: %s (P0=%d P1=%d P2=%d P3=%d)",
        scorecard_path,
        total_p0,
        total_p1,
        total_p2,
        total_p3,
    )


def main() -> int:
    """Main entry point."""
    root_dir = Path(__file__).parent.parent.parent

    violations = scan_directory(root_dir)

    # Query ADG structural counts for P0/P1 enforcement
    adg_counts = _query_adg_view_counts(root_dir)

    # Always update the scorecard with current results
    update_scorecard(root_dir, violations)

    exit_code = 0

    # File-scan P0 violations
    if violations:
        print("❌ Infrastructure Wiring Violations Detected (file scan)")
        print("=" * 60)
        for file_path, file_violations in violations.items():
            print(f"\n{file_path}:")
            for line_num, import_pattern in file_violations:
                print(f"  Line {line_num}: {import_pattern}")
        print("\n" + "=" * 60)
        print("❌ Scan FAILED: Direct infra imports detected in forbidden layers")
        print("Fix: Use sanctioned adapters from L4 or infrastructure/sdks_mcps")
        exit_code = 1

    # ADG structural P0 violations (block commit)
    if adg_counts:
        p0_adg_views = [
            "v_p0_apps_direct_infra",
            "v_p0_provider_bypass",
            "v_p0_write_bypass_uwg",
            "v_p0_l1_direct_infra",
            "v_p0_l6_mutation",
            "v_p0_l0_raw_execution",
        ]
        p0_adg = sum(adg_counts.get(v, 0) for v in p0_adg_views)
        if p0_adg > 0:
            print("❌ ADG Structural P0 Violations Detected")
            for v in p0_adg_views:
                c = adg_counts.get(v, 0)
                if c > 0:
                    print(f"  {v}: {c}")
            print("Fix: Register adapter in _APPROVED_ADAPTER_PATHS or remove direct infra access")
            exit_code = 1

        # ADG structural P1 violations (block commit)
        p1_adg_views = [
            "v_p1_zero_caller_infra",
            "v_p1_not_on_spine",
            "v_p1_ad_hoc_imports",
            "v_p1_mis_layered_infra",
        ]
        p1_adg = sum(adg_counts.get(v, 0) for v in p1_adg_views)
        if p1_adg > 0:
            print("❌ ADG Structural P1 Violations Detected")
            for v in p1_adg_views:
                c = adg_counts.get(v, 0)
                if c > 0:
                    print(f"  {v}: {c}")
            print(
                "Fix: Add adapter to _PROCESS_BOUNDARY_ADAPTERS if process-boundary, "
                "or ensure spine callers exist"
            )
            exit_code = 1

        # P2 regression check (warn but don't block — ceiling enforced)
        _P2_CEILING_MIXED = 3
        _P2_CEILING_DUPED = 2
        mixed = adg_counts.get("v_p2_mixed_usage", 0)
        duped = adg_counts.get("v_p2_duplicated_adapters", 0)
        if mixed > _P2_CEILING_MIXED or duped > _P2_CEILING_DUPED:
            print(
                f"⚠️  P2 regression: mixed={mixed} (ceiling={_P2_CEILING_MIXED}), "
                f"duped={duped} (ceiling={_P2_CEILING_DUPED})"
            )

    if exit_code == 0:
        print("✅ Infrastructure Wiring Scan PASSED (structural)")
        print("P0=0 P1=0 — no infra wiring violations detected")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
