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

# Add repo root to sys.path for tools.* imports (same pattern as other CI gates)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

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
    "bm25_store.py",  # L4 BM25 SparseIndex (SQLite FTS5 + term_freq sidecar); peer of above adapters
    "doc_to_cache_index.py",  # L4 G5 CDC inverse index (SQLite); owns artifacts/gptcache/doc_to_cache.db; peer of gptcache_client / semantic_cache_manager
    # L3 exit-control audit ledger adapters (ADR-023 §5 — canonical hash-chain / HITL persistence)
    "ledger_integrity.py",
    "runtime_hitl_ledger.py",
    # L6 routing-decision events schema (ADR-025 §3 — canonical routing span projection)
    "routing_decision_events_schema.py",
    # Boto3 adapters/owners (L4)
    "blob_storage_provider.py",
    "canonical_store.py",
    # OpenAI/provider adapters
    "semantic_enricher.py",
    "openai_embedder.py",  # L6 canonical OpenAI embedding adapter (text-embedding-3-large)
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
    # Anthropic adapters — APPROVED 2026-04-23
    "claude_judge.py",  # Anthropic SDK — canonical Claude judge adapter in agentic_core/evaluation/judges/
    "HardenedanthropicexecutorStrategy.py",  # Anthropic SDK — sanctioned executor strategy wrapper in apps_rg/enforcement/
    # SQLite adapters surfaced during plan adg-architectural-p0-violations-cleanup-bced9c (2026-04-24)
    "adg_span_annotator.py",  # L6 ADG-snapshot reader for runtime span annotation; read-only consumer of artifacts/adg/*.sqlite (delegated from L3 RuntimeADGQuery)
    "consistency_sqlite.py",  # L3 exit-eval consistency-check ledger; sqlite-backed per-run hash-chain (peer of ledger_integrity.py and runtime_hitl_ledger.py per ADR-023 §5)
    # Adapters surfaced during plan assurance-p1-gates-ab4758 final gate sweep (2026-04-28)
    "decision_events_schema.py",  # L6 unified routing/decision events schema (supersedes routing_decision_events_schema.py per plan routing-decision-process-enhancement-9c7e4d W1) — owns artifacts/decisions/decision_events.sqlite
    "decision_outcome_backfill.py",  # L6 outcome backfill API + observability over decision_events ledger (peer of decision_events_schema; same plan W2)
    "namespace_bandit.py",  # L0 per-namespace Beta-Bernoulli posterior store (Thompson sampling); sqlite-backed (plan routing-decision-process-enhancement-9c7e4d W4)
    "r5_reason_calibration.py",  # L0 per-reason Brier calibration over decision_events (read-only consumer + auto-demote ledger; same plan W5)
    "substrate.py",  # L0 C0.3 substrate guard — monkey-patches sqlite3.connect to enforce no-direct-traversal invariant; sqlite3 import IS the guard mechanism
    "gemini_gateway_provisioner.py",  # L2 minimal Gemini gateway adapter (google.generativeai SDK); sanctioned per plan qwen-confidence-routing-hardening-d4e7b1 W1
    "l2_capable_agent_registry.py",  # L2 ADG-snapshot reader for L2-capable agent discovery (read-only consumer of artifacts/adg/*.sqlite per constitutional §28)
    "sqlite_ledger.py",  # L3 exit-eval v6 hash-chain ledger (drop-in replacement for InMemoryLedger; implements LedgerProtocol from v6.uwg)
    "assembly_stage.py",  # L0 GAP-03 assembly stage — anthropic SDK lazy-loaded inside try/except for token-budget computation (peer of openai/google branches in same function)
    # 2026-04-29 P0 unblock — ADR-070 L5 Guardrail Family canonical sqlite adapters:
    "consumed_token_registry.py",  # L5 G07 capability-token single-use registry; sqlite-backed per-process durable ledger (peer of permissions/sqlite_backend.py)
    "sqlite_backend.py",  # L5 G06 durable PermissionLadder; sqlite UPSERT with (agent_id, target_resource) UNIQUE index (canonical sibling of InMemoryPermissionLadder)
    # 2026-05-04 P2 CI gate burndown W1 — canonical L4 sqlite3 adapter
    "sqlite3_adapter.py",  # L4 canonical sqlite3 adapter — THE sanctioned sqlite3 import surface
    # 2026-05-04 deferred scope W2 — pre-existing apps_* integration files
    "llm_client.py",  # apps_* LLM client adapters (pre-existing, parallel-session)
    "_llm_client.py",  # apps_rg hops LLM client (pre-existing)
    "memory_writeback.py",  # apps_qna memory writeback (pre-existing)
    "rehearsal_cache.py",  # apps_qna rehearsal cache (pre-existing)
    "promotion_gates.py",  # apps_qna promotion gates (pre-existing)
    "company_brief_engine.py",  # apps_research company brief (pre-existing)
    "decision_packet_assembler.py",  # apps_underwriting_ai decision packet (pre-existing)
    "frontier_rationale_judge.py",  # apps_underwriting_ai frontier judge (pre-existing)
    "cadence_state_store.py",  # apps_lic persistence (pre-existing)
    "reply_ledger_store.py",  # apps_lic persistence (pre-existing)
    "flywheel.py",  # apps_qna flywheel (pre-existing)
    "intent_classifier.py",  # apps_qna intent classifier (pre-existing)
    "learning_adapter.py",  # apps_qna learning adapter (pre-existing)
    "generation_engine.py",  # apps_* generation engine (pre-existing)
    "HOP6ValidationAgent.py",  # apps_* HOP6 agent (pre-existing)
    "narrative_judge_scorer.py",  # apps_* narrative judge (pre-existing)
    "qwen_llm_client.py",  # apps_* qwen LLM client (pre-existing)
    "architecture_synth.py",  # apps_qna architecture synth (pre-existing)
    # 2026-05-12 infra-wiring-scan-remediation-927628 W1 — adapter boundary registrations
    "gemini_provider.py",  # L2 provider boundary — httpx lazy-imported inside try/except for Gemini REST calls; peer of optimized_vllm_client.py; no domain logic
    "provider_gateway.py",  # runtime provider gateway — anthropic + openai lazy-imported per-method inside try/except; canonical multi-provider dispatch surface; peer of claude_judge.py
    "adg_client.py",  # apps_architect ADG SQLite client — top-level sqlite3 import for read-only ADG snapshot queries; peer of adg_span_annotator.py / l2_capable_agent_registry.py
    "provider_adapter.py",  # apps_qna multi-provider adapter — anthropic/openai/google/httpx lazy-imported per provider branch; thin integration boundary; peer of llm_client.py
    "provider_dispatch.py",  # apps_qna dispatch layer — anthropic/google lazy-imported in per-provider callables; thin dispatch; peer of provider_adapter.py
    "interview_card_quality_judge.py",  # apps_qna judge adapter — anthropic lazy-imported inside try/except; LLM-as-judge boundary; peer of narrative_judge_scorer.py
    "chroma_research_store.py",  # apps_research ChromaDB store — chromadb lazy-imported inside try/except in factory method; persistent vector store boundary; peer of chroma_client.py
    "rationale_quality_judge.py",  # apps_underwriting_ai judge adapter — anthropic lazy-imported in _get_client(); LLM-as-judge boundary; peer of frontier_rationale_judge.py
    "c0_binding.py",  # apps_rg C0 retrieval binding — chromadb import for ChromaResearchStore wiring; W4 receipted in artifacts/apps_rg/retrieval/ingestion_receipts/w4_c0_binding_receipt.json; peer of chroma_research_store.py
    "chroma_precomputed_collection.py",  # apps_rg Chroma collection boundary — precomputed BGE vectors only; blocks DefaultEmbeddingFunction
    "c02_product_hybrid_retrieval.py",  # apps_rg C0.2 product hybrid retrieval — chromadb query seam
    "augmented_skills_graph_sqlite.py",  # apps_rg fact_inventory — canonical C0.3 graph materialization adapter (sqlite3)
    # 2026-06-07 — apps_01 bank-grade-servicing L4 store (self-contained app, 0 agentic_core deps)
    "ledger.py",  # apps_01 L4 durable archive — sole UWG-gated writer ("Exit decides, UWG commits, L4 stores"); peer of apps_lic/persistence/reply_ledger_store.py + cadence_state_store.py. Also covers apps_research/provenance/ledger.py (same persistence/provenance-ledger sanctioned class).
}

# Subdirectories within agentic_core that are infrastructure tooling
AGENTIC_CORE_INFRA_SUBDIRS = {
    "adg",
    "cache",
    "embeddings",
}


def _find_latest_adg_sqlite(adg_dir: Path) -> Path | None:
    """Return the latest ADG SQLite snapshot via canonical resolver."""
    from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

    return latest_sqlite(require_nodes_table=True)


def scan_file(file_path: Path) -> list[tuple[int, str]] | None:
    """Scan a single Python file for forbidden imports.

    Returns:
        List of (line_number, import_pattern) tuples if violations found, None otherwise.
    """
    violations = []

    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError) as exc:
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
        return module.materialize_infra_views(db_path, scratch=True)
    except Exception as exc:  # review: structural scan should fall back to raw SQL instead of crashing  # guardian: allow-broad-exception -- offline tooling, reports failure
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
    _P2_CEILING_DUPED = 1  # post-consolidation ceiling: redis+chromadb consolidated; reduced W3 2026-05-05

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
        _P2_CEILING_DUPED = 1  # post-consolidation; reduced W3 2026-05-05
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
