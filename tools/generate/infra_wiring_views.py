"""Post-generation ADG enrichment: infrastructure wiring violation views.

Materializes SQL views into the ADG SQLite database that detect
infrastructure wiring violations per the ownership matrix defined in
docs/reports/plans/infra_ownership_matrix.md.

Called by generate_full_adg.py after artifact write and before Redis ingest.
"""

from __future__ import annotations

import ast
import shutil
import sqlite3
import tempfile
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[2]
_C03_RECEIPT_PATH = "apps_rg/fact_inventory/c03_graph_kpi_health.py"
_C03_RECEIPT_SYMBOL = "output.write_text"


def _validate_sqlite_path(sqlite_path: Path) -> Path:
    sqlite_path = sqlite_path.expanduser().resolve()
    if not sqlite_path.exists():
        raise FileNotFoundError(f"ADG SQLite not found: {sqlite_path}")
    if not sqlite_path.is_file():
        raise ValueError(f"ADG SQLite path is not a file: {sqlite_path}")
    return sqlite_path


def _receipt_ast_sites(repo_root: Path) -> list[tuple[str, str, int, int, int]]:
    """Return exact AST sites for the one operator-receipt write exemption.

    Missing, unreadable, or invalid source produces no authority rows. Column
    offsets distinguish multiple calls on one physical line even when the ADG
    extractor currently records line numbers only.
    """
    source_path = repo_root / _C03_RECEIPT_PATH
    try:
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    except (OSError, SyntaxError, UnicodeError):
        return []

    sites: list[tuple[int, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "write_text"
            and isinstance(func.value, ast.Name)
            and func.value.id == "output"
        ):
            sites.append((node.lineno, node.col_offset))

    site_count = len(sites)
    return [
        (_C03_RECEIPT_PATH, _C03_RECEIPT_SYMBOL, line_no, column_no, site_count)
        for line_no, column_no in sorted(sites)
    ]


def materialize_receipt_ast_sites(
    conn: sqlite3.Connection,
    *,
    repo_root: Path | None = None,
) -> None:
    """Materialize source-bound receipt sites for fail-closed SQL exemptions."""
    conn.execute("DROP TABLE IF EXISTS t_exact_receipt_ast_sites")
    conn.execute(
        """
        CREATE TABLE t_exact_receipt_ast_sites (
            resolved_path TEXT NOT NULL,
            symbol TEXT NOT NULL,
            line_no INTEGER NOT NULL,
            column_no INTEGER NOT NULL,
            site_count INTEGER NOT NULL,
            PRIMARY KEY (resolved_path, symbol, line_no, column_no)
        )
        """
    )
    rows = _receipt_ast_sites((repo_root or _REPO_ROOT).resolve())
    if rows:
        conn.executemany(
            "INSERT INTO t_exact_receipt_ast_sites VALUES (?, ?, ?, ?, ?)",
            rows,
        )


# Forbidden raw infra packages
_RAW_INFRA_PACKAGES = (
    "redis",
    "chromadb",
    "sqlite3",
    "boto3",
    "openai",
    "anthropic",
    "httpx",
    "requests",
    # Phase 2 additions — newly registered surfaces (infra_ownership_matrix.md Phase 1)
    "neo4j",  # Graph DB — EXPERIMENTAL_ISOLATED; pending formalization (§F1)
    "prometheus_client",  # Metrics   — de-facto L6 adapter, now formally registered (§R5)
    "aiohttp",  # HTTP      — raw client in L3 vLLM; pending architecture ruling (§F2)
)

# Approved adapter files (canonical wrappers that MUST import raw infra)
# Each entry requires formal justification:
#   redis_cache_client.py       — canonical Redis adapter (L_SHARED, cross-cutting)
#   chroma_client.py            — canonical ChromaDB adapter (L4 state)
#   embedding_factory.py        — canonical embedding adapter (L2/L_SHARED)
#   infrastructure/sdks_mcps/   — provider SDK control plane (boundary layer)
#   enhanced_http_server.py     — MCP HTTP server (process-boundary, no Python imports)
#   sqlite_memory_store.py      — canonical SQLite memory adapter (tools)
#   canonical_store.py          — canonical filesystem store (L4, process-boundary)
#   sovereign_redis_orchestrator.py — L3 sovereign Redis orchestrator with MCP routing,
#                                     fail-closed semantics, and trace emission. Approved
#                                     per infra_ownership_matrix.md §Redis/L3.
#   repo_signal_adapter.py      — L_APP read-only ADG/signal adapter. Uses sqlite3 for
#                                 SELECT COUNT(*) introspection only (no mutations).
#                                 Uses path.open("r") for line counting (read-only).
#                                 Approved per infra_ownership_matrix.md §SQLite/L_APP.
_APPROVED_ADAPTER_PATHS = (
    "agentic_core/cache/redis_cache_client.py",
    "agentic_core/L4_state/utils/client/chroma_client.py",
    "agentic_core/embeddings/embedding_factory.py",
    "infrastructure/sdks_mcps/__init__.py",
    "tools/mcp/enhanced_http_server.py",
    "tools/memory/sqlite_memory_store.py",
    "agentic_core/L4_state/utils/memory/canonical_store.py",
    "agentic_core/L3_orchestration/reasoning/engines/sovereign_redis_orchestrator.py",
    "apps_shared/data_adapters/repo_signal_adapter.py",
    # Phase 2 additions — closing sanctioned-vs-approved coverage gaps
    "apps_shared/utils/open_telemetry_tracing_adapter_util.py",  # Corrected OTel canonical adapter (replaces tools/otel/otel_mcp_server.py)
    # REMOVED 2026-04-11 R-A2: blob_storage_provider.py deregistered — zero callers, dormant (F-P1-004). File retained on disk.
    # REMOVED 2026-04-11 R-A1: cache/core/redis_cache_client.py deregistered — dead duplicate of cache/redis_cache_client.py (F-P1-005). File retained on disk.
    "agentic_core/L6_observability/utils/metrics/prometheus_metrics.py",  # Prometheus — de-facto approved adapter at L6 (defines AGENTIC_REGISTRY)
    "agentic_core/L4_state/enforcement/neo4j_store.py",  # Neo4j — EXPERIMENTAL_ISOLATED; zero callers expected; tracked for P1 visibility
    # APPROVED 2026-04-11 vllm-path-a: optimized_vllm_client.py — sanctioned L3 vLLM HTTP adapter.
    # Approved hosts: localhost / 127.0.0.1 port 8000-8099 only (Qwen vLLM OpenAI-compat API).
    # Approved callers: qwen_inference_gateway.py, hardened_vllm_client.py, test harnesses only.
    # Must NOT be imported from apps_* or any layer outside L3 qwen_vllm subtree.
    # Lifecycle: start() before first request, close() on shutdown. ADG enforcement: file-scanner only.
    # Decision packet: docs/reports/plans/vllm_http_decision_packet.md §E (Path A).
    "agentic_core/L3_orchestration/inference/qwen_vllm/engines/optimized_vllm_client.py",
    # ENROLLED 2026-04-22 semcache-make-live-7a2d4b / rca-adg-ci-missed-gaps C1:
    # These L4 semantic-cache adapters were structurally orphaned from the ADG
    # static-imports view while being documented as LIVE. Enrolling forces the
    # zero-caller check to report them; they are simultaneously listed under
    # _PROCESS_BOUNDARY_ADAPTERS below because their only callers are lazy
    # (inside try-blocks in L0 methods). When edge-kind `lazy_imports` lands
    # (RCA §C2), the process-boundary exemption can be removed.
    "agentic_core/L4_state/utils/memory/semantic_cache_manager.py",
    "agentic_core/L4_state/utils/memory/sovereign_semantic_cache.py",
    "agentic_core/L4_state/cache/gptcache_client.py",
    # apps_rg Chroma seams (mirror _SANCTIONED_APP_DIRECT_INFRA — exclude from t_infra_importers)
    "apps_rg/runtime/chroma_precomputed_collection.py",
    "apps_rg/runtime/c0/c02_product_hybrid_retrieval.py",
    # apps_rg C0.3 canonical SQLite materializer. Its maintenance lock is
    # adapter-local and must not be classified as a direct-infra write bypass.
    "apps_rg/fact_inventory/augmented_skills_graph_sqlite.py",
    # apps_lic W7 Claude X1D judge adapter — sanctioned anthropic SDK caller for Exit-layer judging
    "apps_lic/engines/x1d_claude_judge_adapter.py",
)

# Process-boundary adapters: invoked at process level (MCP server launch, filesystem access)
# rather than via Python import. These will always show zero `imports` callers in the ADG
# and are formally exempt from P1-7 (zero-caller) and P1-8 (not-on-spine) checks.
# Documented in infra_ownership_matrix.md §Process-Boundary Adapters.
_PROCESS_BOUNDARY_ADAPTERS = (
    "infrastructure/sdks_mcps/__init__.py",  # Provider SDK MCP server — launched as process
    "tools/mcp/enhanced_http_server.py",  # HTTP MCP server — launched as process
    "agentic_core/L4_state/utils/memory/canonical_store.py",  # Filesystem store — accessed via path
    "agentic_core/L3_orchestration/reasoning/engines/sovereign_redis_orchestrator.py",  # Redis orchestrator — instantiated via registry
    "apps_shared/data_adapters/repo_signal_adapter.py",  # Signal reader — instantiated by signal collection scripts
    # 2026-04-22 semcache-make-live-7a2d4b / rca-adg-ci-missed-gaps:
    # Lazy-import-only adapters. Sole callers are `from ... import` statements
    # inside function bodies in L0 / apps_shared (invisible to AST top-level
    # extraction). Temporary exemption until `lazy_imports` edge kind lands
    # (RCA §C2). Expected-wiring coverage is asserted via
    # `config/expected_wiring.yaml` + `check_expected_wiring.py`.
    "agentic_core/L4_state/utils/memory/semantic_cache_manager.py",
    "agentic_core/L4_state/utils/memory/sovereign_semantic_cache.py",
    "agentic_core/L4_state/cache/gptcache_client.py",
    # 2026-04-28 plan assurance-p1-gates-ab4758 W-cleanup:
    # neo4j_store.py is EXPERIMENTAL_ISOLATED with zero callers BY DESIGN
    # (per existing comment in _APPROVED_ADAPTER_PATHS). Promoting it to
    # process-boundary suppresses both v_p1_zero_caller_infra and
    # v_p1_not_on_spine without weakening the spine check for real adapters.
    "agentic_core/L4_state/enforcement/neo4j_store.py",
)

# Pre-existing apps_* files that use infra directly by design (legacy, pre-adapter era).
# These are NOT infrastructure adapters — they are app-layer files that were grandfathered in.
# They are excluded ONLY from v_p0_apps_direct_infra (not from P1 adapter checks).
# Do NOT add new entries; route new code through canonical adapters instead.
_SANCTIONED_APP_DIRECT_INFRA = (
    # apps_lic persistence adapters (sqlite3) — pre-existing, parallel-session
    "apps_lic/persistence/cadence_state_store.py",
    "apps_lic/persistence/reply_ledger_store.py",
    "apps_lic/services/persistence/cadence_state_store.py",
    "apps_lic/services/persistence/reply_ledger_store.py",
    # apps_qna integration files (sqlite3) — pre-existing, parallel-session
    "apps_qna/engines/router/promotion_gates.py",
    "apps_qna/integrations/architecture_synth.py",
    "apps_qna/integrations/flywheel.py",
    "apps_qna/integrations/learning_adapter.py",
    "apps_qna/integrations/memory_writeback.py",
    "apps_qna/integrations/rehearsal_cache.py",
    "apps_qna/router/promotion_gates.py",
    # 2026-05-12 infra-wiring-scan-remediation-927628 — adapter boundary files (V-4 through V-9)
    "apps_architect/engines/adg_client.py",  # ADG SQLite client — read-only snapshot queries
    "apps_qna/integrations/provider_adapter.py",  # Multi-provider adapter — anthropic/openai/google/httpx
    "apps_qna/engines/dispatch/provider_dispatch.py",  # Provider dispatch — anthropic/google
    "apps_qna/engines/judges/interview_card_quality_judge.py",  # Judge adapter — anthropic
    "apps_research/engines/integration/chroma_research_store.py",  # ChromaDB store — persistent vector store
    "apps_underwriting_ai/engines/judges/rationale_quality_judge.py",  # Judge adapter — anthropic
    # 2026-05-12 adg-snapshot-regen-check-rg-chroma-e2f8b1 — C0 binding already in file-scan allowlist
    "apps_rg/runtime/bindings/c0_binding.py",  # C0 ChromaDB binding — receipted in W4 of apps-rg-chroma-ingestion-wiring-c7f2d9; peer of chroma_research_store.py
    "apps_rg/runtime/chroma_precomputed_collection.py",  # apps_rg Chroma collection boundary — precomputed BGE only
    "apps_rg/runtime/c0/c02_product_hybrid_retrieval.py",  # C0.2 product hybrid retrieval seam
    "apps_rg/fact_inventory/augmented_skills_graph_sqlite.py",  # C0.3 skills graph materialization — sqlite3 adapter for augmented_skills_graph ledger
    # apps_lic W7 X1D judge — sanctioned anthropic SDK caller for Exit-layer judging (peer of apps_qna/apps_underwriting_ai judge adapters above)
    "apps_lic/engines/x1d_claude_judge_adapter.py",
)

# Provider SDKs that must route through infrastructure/sdks_mcps
_PROVIDER_SDKS = ("openai", "anthropic", "google")

# Paths exempt from provider bypass check
_PROVIDER_EXEMPT_PREFIXES = (
    "infrastructure/sdks_mcps/",
    "tools/",
    "system_learning/",
    "agentic_core/embeddings/",
)


def _build_infra_name_clause() -> str:
    """Build SQL IN clause for raw infra package names."""
    names = ", ".join(f"'{p}'" for p in _RAW_INFRA_PACKAGES)
    return f"({names})"


def _build_adapter_path_clause() -> str:
    """Build SQL IN clause for approved adapter resolved_path values."""
    paths = ", ".join(f"'{p}'" for p in _APPROVED_ADAPTER_PATHS)
    return f"({paths})"


def _build_process_boundary_clause() -> str:
    """Build SQL IN clause for process-boundary adapter paths (exempt from P1 checks)."""
    paths = ", ".join(f"'{p}'" for p in _PROCESS_BOUNDARY_ADAPTERS)
    return f"({paths})"


def _build_sanctioned_app_clause() -> str:
    """Build SQL IN clause for pre-existing apps_* files sanctioned for direct infra usage."""
    paths = ", ".join(f"'{p}'" for p in _SANCTIONED_APP_DIRECT_INFRA)
    return f"({paths})"


def _build_provider_name_clause() -> str:
    """Build SQL IN clause for provider SDK names."""
    names = ", ".join(f"'{p}'" for p in _PROVIDER_SDKS)
    return f"({names})"


# --- View definitions ---

_VIEW_P0_APPS_DIRECT_INFRA = """
CREATE VIEW IF NOT EXISTS v_p0_apps_direct_infra AS
SELECT
    e.id         AS violation_edge_id,
    n_src.id     AS consumer_id,
    n_src.resolved_path AS consumer_file,
    n_src.layer  AS consumer_layer,
    e.symbol     AS import_symbol,
    e.line_no    AS import_line,
    'P0: apps_* direct infra import' AS violation_type
FROM edges e
JOIN nodes n_src ON e.src_id = n_src.id
JOIN nodes n_dst ON e.dst_id = n_dst.id
WHERE e.relation_type = 'imports'
  AND n_dst.adg_name IN ({infra_adg_names})
  AND n_src.resolved_path LIKE 'apps_%'
  AND n_src.resolved_path NOT LIKE 'apps_shared/%'
  AND n_src.resolved_path NOT LIKE 'apps_%/tests/%'
  AND n_src.resolved_path NOT IN {sanctioned_app_paths}
"""


_VIEW_P0_PROVIDER_BYPASS = """
CREATE VIEW IF NOT EXISTS v_p0_provider_bypass AS
SELECT
    e.id         AS violation_edge_id,
    n_src.id     AS consumer_id,
    n_src.resolved_path AS consumer_file,
    n_src.layer  AS consumer_layer,
    e.symbol     AS import_symbol,
    e.line_no    AS import_line,
    'P0: provider control plane bypass' AS violation_type
FROM edges e
JOIN nodes n_src ON e.src_id = n_src.id
JOIN nodes n_dst ON e.dst_id = n_dst.id
WHERE e.relation_type = 'imports'
  AND n_dst.adg_name IN ({provider_adg_names})
  AND n_src.resolved_path NOT LIKE 'infrastructure/sdks_mcps/%'
  AND n_src.resolved_path NOT LIKE 'tools/%'
  AND n_src.resolved_path NOT LIKE 'system_learning/%'
  AND n_src.resolved_path NOT LIKE 'agentic_core/embeddings/%'
"""


_VIEW_P0_CORE_IMPORTS_APPS = """
CREATE VIEW IF NOT EXISTS v_p0_core_imports_apps AS
SELECT
    e.id         AS violation_edge_id,
    n_src.id     AS consumer_id,
    n_src.resolved_path AS consumer_file,
    n_src.layer  AS consumer_layer,
    n_dst.resolved_path AS app_file,
    e.symbol     AS import_symbol,
    e.line_no    AS import_line,
    'P0: agentic_core imports apps_*' AS violation_type
FROM edges e
JOIN nodes n_src ON e.src_id = n_src.id
JOIN nodes n_dst ON e.dst_id = n_dst.id
WHERE e.relation_type = 'imports'
  AND n_src.resolved_path LIKE 'agentic_core/%'
  AND n_dst.resolved_path LIKE 'apps_%/%'
  AND n_dst.resolved_path NOT LIKE 'apps_shared/%'
  AND n_src.resolved_path NOT LIKE 'agentic_core/%/tests/%'
  AND n_src.resolved_path NOT LIKE 'agentic_core/%/docs/%'
"""


# P1-7: Critical infra adapter with no approved runtime callers.
# Checks BOTH module-level imports (dst_id = module node) AND symbol-level imports
# (dst_id = any symbol node whose resolved_path matches the adapter).
# This fixes the false positive where callers use `from adapter import Symbol` —
# those create an imports edge to the symbol node, not the module node.
# Architecture rule: every approved adapter must have at least one caller in the graph.
_VIEW_P1_ZERO_CALLER_INFRA = """
CREATE VIEW IF NOT EXISTS v_p1_zero_caller_infra AS
SELECT adapter_id, adapter_file, adapter_name, caller_count, violation_type
FROM (
    SELECT
        n_adapter.id            AS adapter_id,
        n_adapter.resolved_path AS adapter_file,
        n_adapter.adg_name      AS adapter_name,
        (
            SELECT COUNT(*)
            FROM edges e
            JOIN nodes n_node ON e.dst_id = n_node.id
            WHERE e.relation_type = 'imports'
              AND n_node.resolved_path = n_adapter.resolved_path
        ) AS caller_count,
        'P1: infra adapter with no callers' AS violation_type
    FROM nodes n_adapter
    WHERE n_adapter.resolved_path IN {adapter_paths}
      AND n_adapter.resolved_path NOT IN {process_boundary_paths}
      AND n_adapter.entity_type = 'module'
)
WHERE caller_count = 0
"""


_VIEW_P2_MIXED_USAGE = """
CREATE VIEW IF NOT EXISTS v_p2_mixed_usage AS
SELECT
    n_infra.adg_name AS infra_name,
    COUNT(DISTINCT CASE
        WHEN n_consumer.resolved_path NOT IN {adapter_paths}
         AND n_consumer.resolved_path NOT LIKE 'tools/%'
         AND n_consumer.resolved_path NOT LIKE 'infrastructure/%'
        THEN n_consumer.id
    END) AS direct_count,
    COUNT(DISTINCT CASE
        WHEN n_consumer.resolved_path IN {adapter_paths}
        THEN n_consumer.id
    END) AS wrapped_count,
    'P2: mixed direct and wrapped usage' AS violation_type
FROM edges e
JOIN nodes n_consumer ON e.src_id = n_consumer.id
JOIN nodes n_infra ON e.dst_id = n_infra.id
WHERE e.relation_type = 'imports'
  AND n_infra.adg_name IN ({infra_adg_names})
GROUP BY n_infra.adg_name
HAVING direct_count > 0 AND wrapped_count > 0
"""


# P0-3: Durable write bypass outside UWG
# Only flags files that BOTH import raw infra AND have writes_to/writes_through edges.
# This filters out plain filesystem I/O (config writes, logging, artifact generation)
# and only surfaces true infra write bypasses (e.g. writing directly to Redis/Chroma/SQLite
# without going through the UWG adapter chain).
# Architecture rule: writes_to/writes_through on a file that imports raw infra = bypass.
# Precision mechanism: t_infra_importers materialized table (injected at view creation time).
_VIEW_P0_WRITE_BYPASS_UWG = """
CREATE VIEW IF NOT EXISTS v_p0_write_bypass_uwg AS
SELECT
    e.id         AS violation_edge_id,
    n_src.id     AS writer_id,
    n_src.resolved_path AS writer_file,
    n_src.layer  AS writer_layer,
    e.symbol     AS write_symbol,
    e.line_no    AS write_line,
    'P0: durable write bypass outside UWG' AS violation_type
FROM edges e
JOIN nodes n_src ON e.src_id = n_src.id
JOIN t_infra_importers ti ON ti.resolved_path = n_src.resolved_path
WHERE e.relation_type IN ('writes_to', 'writes_through')
  AND n_src.resolved_path NOT LIKE '%UniversalWrite%'
  AND n_src.resolved_path NOT LIKE '%write_gateway%'
  AND n_src.resolved_path NOT LIKE '%uwg%'
  AND n_src.resolved_path NOT LIKE '%mutation_prohibition%'
  -- L3 sqlite ledger adapters (ADR-023 §5 hash-chain / consistency / HITL).
  -- Peers of ledger_integrity.py and runtime_hitl_ledger.py which already
  -- ship without flagging because their writes are wrapped through the
  -- ledger contract (no plain Path.mkdir at module surface). This adapter
  -- writes only to its own ledger db file under the per-run artifacts dir.
  -- Added 2026-04-24 by plan adg-architectural-p0-violations-cleanup-bced9c.
  AND n_src.resolved_path NOT LIKE '%/exit_eval/consistency_sqlite%'
  -- L0 C0.3 substrate guard — uses path.open('r') for line counting (read-only),
  -- not a durable write. Sanctioned per plan assurance-p1-gates-ab4758 W-cleanup
  -- and infra_ownership_matrix.md §SQLite/L_APP.
  AND n_src.resolved_path NOT LIKE '%/c0_3_enhanced/substrate.py'
  AND n_src.resolved_path NOT LIKE 'tools/%'
  AND n_src.resolved_path NOT LIKE 'tests/%'
  AND n_src.resolved_path NOT LIKE 'ops_scripts/%'
  AND n_src.resolved_path NOT LIKE 'infrastructure/%'
  AND n_src.layer IN ('L0', 'L1', 'L3', 'L_APP')
  AND e.symbol NOT LIKE '%_wg.write_text%'
  AND e.symbol NOT LIKE '%assert_no_persistent_write%'
  -- apps_rg C0.3 graph-health output is an explicit operator receipt, not
  -- durable application state. Exempt it only while the graph contains one
  -- distinct, fully resolved AST call site. Source AST authority includes the
  -- column offset, so two calls on one physical line still fail closed.
  AND NOT (
      n_src.resolved_path = 'apps_rg/fact_inventory/c03_graph_kpi_health.py'
      AND e.symbol = 'output.write_text'
      AND COALESCE(e.source_file, '') = n_src.resolved_path
      AND COALESCE(e.line_no, 0) > 0
      AND EXISTS (
          SELECT 1
          FROM t_exact_receipt_ast_sites exact_site
          WHERE exact_site.resolved_path = n_src.resolved_path
            AND exact_site.symbol = e.symbol
            AND exact_site.line_no = e.line_no
            AND exact_site.site_count = 1
      )
      AND NOT EXISTS (
          SELECT 1
          FROM edges receipt_edge
          JOIN nodes receipt_src ON receipt_src.id = receipt_edge.src_id
          WHERE receipt_edge.relation_type IN ('writes_to', 'writes_through')
            AND receipt_src.resolved_path = n_src.resolved_path
            AND receipt_edge.symbol = e.symbol
            AND (
                receipt_edge.source_file IS NULL
                OR receipt_edge.line_no IS NULL
                OR receipt_edge.source_file <> e.source_file
                OR receipt_edge.line_no <> e.line_no
            )
      )
  )
"""


# P0-4: L1 direct execution infra use
_VIEW_P0_L1_DIRECT_INFRA = """
CREATE VIEW IF NOT EXISTS v_p0_l1_direct_infra AS
SELECT
    e.id         AS violation_edge_id,
    n_src.id     AS consumer_id,
    n_src.resolved_path AS consumer_file,
    n_src.layer  AS consumer_layer,
    e.symbol     AS import_symbol,
    e.line_no    AS import_line,
    'P0: L1 direct execution infra use' AS violation_type
FROM edges e
JOIN nodes n_src ON e.src_id = n_src.id
JOIN nodes n_dst ON e.dst_id = n_dst.id
WHERE e.relation_type = 'imports'
  AND n_src.layer = 'L1'
  AND n_dst.adg_name IN ({infra_adg_names})
"""


# P0-5: L6 live mutation path
# L6 should be observability only — no durable infra writes except telemetry stores.
# Only flags L6 files that BOTH import raw infra AND have writes_to/writes_through edges.
# Observability report writes (file I/O, CSV, JSON) are NOT violations — only writes that
# touch raw infra (Redis, SQLite, ChromaDB) without going through the UWG chain.
# Architecture rule: L6 + infra import + durable write = live mutation violation.
# Precision mechanism: t_infra_importers materialized table (injected at view creation time).
_VIEW_P0_L6_MUTATION = """
CREATE VIEW IF NOT EXISTS v_p0_l6_mutation AS
SELECT
    e.id         AS violation_edge_id,
    n_src.id     AS writer_id,
    n_src.resolved_path AS writer_file,
    n_src.layer  AS writer_layer,
    e.symbol     AS write_symbol,
    e.line_no    AS write_line,
    'P0: L6 live mutation path' AS violation_type
FROM edges e
JOIN nodes n_src ON e.src_id = n_src.id
JOIN t_infra_importers ti ON ti.resolved_path = n_src.resolved_path
WHERE e.relation_type IN ('writes_to', 'writes_through')
  AND n_src.layer = 'L6'
  AND n_src.resolved_path NOT LIKE '%telemetry_store%'
  AND n_src.resolved_path NOT LIKE '%otel%'
  AND e.symbol NOT LIKE '%_wg.write_text%'
  AND e.symbol NOT LIKE '%assert_no_persistent_write%'
"""


# P0-6: L0 route authority collapsing into raw infra execution
_VIEW_P0_L0_RAW_EXECUTION = """
CREATE VIEW IF NOT EXISTS v_p0_l0_raw_execution AS
SELECT
    e.id         AS violation_edge_id,
    n_src.id     AS consumer_id,
    n_src.resolved_path AS consumer_file,
    n_src.layer  AS consumer_layer,
    e.symbol     AS import_symbol,
    e.line_no    AS import_line,
    'P0: L0 raw infra execution' AS violation_type
FROM edges e
JOIN nodes n_src ON e.src_id = n_src.id
JOIN nodes n_dst ON e.dst_id = n_dst.id
WHERE e.relation_type = 'imports'
  AND n_src.layer = 'L0'
  AND n_dst.adg_name IN ({infra_adg_names})
  -- Sanctioned L0 SQLite-backed adapters — per plan
  -- routing-decision-process-enhancement-9c7e4d (W4/W5) and the C0.3
  -- substrate guard. namespace_bandit owns the per-namespace Beta-Bernoulli
  -- posterior store; r5_reason_calibration owns per-reason Brier calibration
  -- over decision_events; substrate.py monkey-patches sqlite3.connect AS the
  -- substrate-violation guard (the import IS the guard mechanism). Each is
  -- listed in SANCTIONED_ADAPTER_FILES in ops_scripts/ci/infra_wiring_scan.py.
  AND n_src.resolved_path NOT LIKE '%/reasoning/namespace_bandit.py'
  AND n_src.resolved_path NOT LIKE '%/reasoning/r5_reason_calibration.py'
  AND n_src.resolved_path NOT LIKE '%/c0_3_enhanced/substrate.py'
"""


# P1-7: Critical infra has no approved runtime caller (zero incoming imports)
# Already exists as v_p1_zero_caller_infra

# P1-8: Critical infra not on sanctioned L0-L6 spine.
# Checks that at least one SPINE caller (L0-L6) imports the adapter — checking
# BOTH module node AND symbol nodes for the same reason as P1-7.
# Architecture rule: every approved adapter must be reachable from L0-L6 spine.
_VIEW_P1_NOT_ON_SPINE = """
CREATE VIEW IF NOT EXISTS v_p1_not_on_spine AS
SELECT adapter_id, adapter_file, adapter_layer, adapter_name, spine_caller_count, violation_type
FROM (
    SELECT
        n_adapter.id            AS adapter_id,
        n_adapter.resolved_path AS adapter_file,
        n_adapter.layer         AS adapter_layer,
        n_adapter.adg_name      AS adapter_name,
        (
            SELECT COUNT(*)
            FROM edges e2
            JOIN nodes n_caller ON e2.src_id = n_caller.id
            JOIN nodes n_node   ON e2.dst_id = n_node.id
            WHERE e2.relation_type = 'imports'
              AND n_node.resolved_path = n_adapter.resolved_path
              AND n_caller.layer IN ('L0','L1','L2','L3','L4','L5','L6','L_APP','L_SHARED')
        ) AS spine_caller_count,
        'P1: infra not on sanctioned L0-L6 spine' AS violation_type
    FROM nodes n_adapter
    WHERE n_adapter.resolved_path IN {adapter_paths}
      AND n_adapter.resolved_path NOT IN {process_boundary_paths}
      AND n_adapter.entity_type = 'module'
)
WHERE spine_caller_count = 0
"""


# P1-9: Infra imported through ad hoc / service-locator style paths
# Detects infra imports via dynamic resolution (invokes_dynamic relation)
_VIEW_P1_AD_HOC_IMPORTS = """
CREATE VIEW IF NOT EXISTS v_p1_ad_hoc_imports AS
SELECT
    e.id         AS violation_edge_id,
    n_src.id     AS consumer_id,
    n_src.resolved_path AS consumer_file,
    n_src.layer  AS consumer_layer,
    e.symbol     AS import_symbol,
    e.line_no    AS import_line,
    'P1: ad hoc / service-locator infra import' AS violation_type
FROM edges e
JOIN nodes n_src ON e.src_id = n_src.id
JOIN nodes n_dst ON e.dst_id = n_dst.id
WHERE e.relation_type = 'imports'
  AND e.edge_kind = 'dead_import'
  AND n_dst.adg_name IN ({infra_adg_names})
  AND n_src.resolved_path NOT LIKE 'tests/%'
  AND n_src.resolved_path NOT LIKE 'tools/%'
  AND n_src.resolved_path NOT LIKE 'archives/%'
"""


# P1-10: Retrieval/governance/telemetry infra not wired to expected owning layer
# Checks that infra adapters live in their declared owner layer
_VIEW_P1_MIS_LAYERED_INFRA = """
CREATE VIEW IF NOT EXISTS v_p1_mis_layered_infra AS
SELECT
    n.id           AS adapter_id,
    n.resolved_path AS adapter_file,
    n.layer        AS actual_layer,
    'P1: infra adapter not in expected owner layer' AS violation_type
FROM nodes n
WHERE n.entity_type = 'module'
  AND (
    (n.resolved_path = 'agentic_core/cache/redis_cache_client.py' AND n.layer NOT IN ('L2', 'L_SHARED'))
    OR (n.resolved_path = 'agentic_core/L4_state/utils/client/chroma_client.py' AND n.layer != 'L4')
    OR (n.resolved_path = 'agentic_core/L4_state/utils/memory/canonical_store.py' AND n.layer != 'L4')
    OR (n.resolved_path = 'agentic_core/embeddings/embedding_factory.py' AND n.layer NOT IN ('L2', 'L_SHARED'))
    -- Phase 2 additions
    OR (n.resolved_path = 'agentic_core/L6_observability/utils/metrics/prometheus_metrics.py' AND n.layer != 'L6')
    OR (n.resolved_path = 'agentic_core/L4_state/enforcement/neo4j_store.py' AND n.layer != 'L4')
  )
"""


# P2-11: Infra duplicated across multiple adapter patterns
# Detects infra surface with more than one approved adapter
_VIEW_P2_DUPLICATED_ADAPTERS = """
CREATE VIEW IF NOT EXISTS v_p2_duplicated_adapters AS
SELECT
    n_infra.adg_name AS infra_name,
    COUNT(DISTINCT n_adapter.resolved_path) AS adapter_count,
    GROUP_CONCAT(DISTINCT n_adapter.resolved_path) AS adapter_files,
    'P2: duplicated infra adapters' AS violation_type
FROM edges e
JOIN nodes n_adapter ON e.src_id = n_adapter.id
JOIN nodes n_infra ON e.dst_id = n_infra.id
WHERE e.relation_type = 'imports'
  AND n_infra.adg_name IN ({infra_adg_names})
  AND n_adapter.resolved_path IN {adapter_paths}
GROUP BY n_infra.adg_name
HAVING adapter_count > 1
"""


# P2-13: Dormant infra in production tree with ambiguous ownership
# Infra adapter with zero callers AND zero outgoing infra imports
_VIEW_P2_DORMANT_AMBIGUOUS = """
CREATE VIEW IF NOT EXISTS v_p2_dormant_ambiguous AS
SELECT
    n.id           AS adapter_id,
    n.resolved_path AS adapter_file,
    n.layer        AS adapter_layer,
    (SELECT COUNT(*) FROM edges e_in
     WHERE e_in.dst_id = n.id AND e_in.relation_type = 'imports') AS incoming_count,
    'P2: dormant infra with ambiguous ownership' AS violation_type
FROM nodes n
WHERE n.resolved_path IN {adapter_paths}
  AND n.entity_type = 'module'
  AND (SELECT COUNT(*) FROM edges e_in WHERE e_in.dst_id = n.id AND e_in.relation_type = 'imports') = 0
  AND (SELECT COUNT(*) FROM edges e_out
       JOIN nodes n_tgt ON e_out.dst_id = n_tgt.id
       WHERE e_out.src_id = n.id
         AND e_out.relation_type = 'imports'
         AND n_tgt.identity_kind = 'external_module') = 0
"""


# P3-14: Isolated experimental infra outside production path
_VIEW_P3_ISOLATED_EXPERIMENTAL = """
CREATE VIEW IF NOT EXISTS v_p3_isolated_experimental AS
SELECT
    n.id           AS node_id,
    n.resolved_path AS file_path,
    n.layer        AS layer,
    (SELECT COUNT(*) FROM edges e_in
     WHERE e_in.dst_id = n.id AND e_in.relation_type = 'imports') AS incoming_count,
    'P3: isolated experimental infra' AS violation_type
FROM nodes n
WHERE n.entity_type = 'module'
  AND n.resolved_path NOT LIKE 'tests/%'
  AND (
    n.resolved_path LIKE '%playground%'
    OR n.resolved_path LIKE '%experiment%'
    OR n.resolved_path LIKE '%sandbox%'
    OR n.resolved_path LIKE '%prototype%'
  )
  AND (SELECT COUNT(*) FROM edges e_in
       WHERE e_in.dst_id = n.id AND e_in.relation_type = 'imports') = 0
"""


# P1-15: Raw HTTP client (aiohttp/httpx/requests) used outside sanctioned HTTP seam.
# Sanctioned HTTP paths: tools/mcp/enhanced_http_server.py (process-boundary MCP) and
# agentic_core/gateway/api_gateway_integration.py (L0/L1 gateway health check).
# The vLLM client (optimized_vllm_client.py) appears here intentionally — UNDER_REVIEW,
# pending architecture ruling on L3 direct HTTP (infra_ownership_matrix.md §F2).
_VIEW_P1_RAW_HTTP_OUTSIDE_SEAM = """
CREATE VIEW IF NOT EXISTS v_p1_raw_http_outside_seam AS
SELECT
    e.id         AS violation_edge_id,
    n_src.id     AS consumer_id,
    n_src.resolved_path AS consumer_file,
    n_src.layer  AS consumer_layer,
    e.symbol     AS import_symbol,
    e.line_no    AS import_line,
    'P1: raw HTTP client outside sanctioned seam' AS violation_type
FROM edges e
JOIN nodes n_src ON e.src_id = n_src.id
JOIN nodes n_dst ON e.dst_id = n_dst.id
WHERE e.relation_type = 'imports'
  AND n_dst.adg_name IN ({http_adg_names})
  AND n_src.resolved_path NOT LIKE 'tools/%'
  AND n_src.resolved_path NOT LIKE 'infrastructure/%'
  AND n_src.resolved_path NOT LIKE 'apps_shared/%'
  AND n_src.resolved_path NOT LIKE 'tests/%'
  AND n_src.resolved_path NOT LIKE '%api_gateway_integration%'
  AND n_src.resolved_path NOT LIKE '%optimized_vllm_client%'
"""


# Summary view that unions all P0 violations for easy querying
_VIEW_INFRA_VIOLATIONS_SUMMARY = """
CREATE VIEW IF NOT EXISTS v_infra_violations_summary AS
SELECT violation_edge_id, consumer_file, consumer_layer, import_symbol, import_line, violation_type
FROM v_p0_apps_direct_infra
UNION ALL
SELECT violation_edge_id, consumer_file, consumer_layer, import_symbol, import_line, violation_type
FROM v_p0_provider_bypass
UNION ALL
SELECT violation_edge_id, consumer_file, consumer_layer, import_symbol, import_line, violation_type
FROM v_p0_core_imports_apps
UNION ALL
SELECT violation_edge_id, writer_file AS consumer_file, writer_layer AS consumer_layer,
       write_symbol AS import_symbol, write_line AS import_line, violation_type
FROM v_p0_write_bypass_uwg
UNION ALL
SELECT violation_edge_id, consumer_file, consumer_layer, import_symbol, import_line, violation_type
FROM v_p0_l1_direct_infra
UNION ALL
SELECT violation_edge_id, writer_file AS consumer_file, writer_layer AS consumer_layer,
       write_symbol AS import_symbol, write_line AS import_line, violation_type
FROM v_p0_l6_mutation
UNION ALL
SELECT violation_edge_id, consumer_file, consumer_layer, import_symbol, import_line, violation_type
FROM v_p0_l0_raw_execution
"""


def materialize_infra_views(sqlite_path: Path, *, scratch: bool = False) -> dict[str, int]:
    """Create infrastructure wiring violation views on the ADG SQLite (or a scratch copy).

    When ``scratch`` is False (default), materializes directly on ``sqlite_path``
    (``generate_full_adg`` / unit tests expect views persisted on the target DB).

    When ``scratch`` is True, copies ``sqlite_path`` to a temp file first. Used by
    ``infra_wiring_scan`` so CI does not rewrite canonical ``adg_indexed_*.sqlite``
    bytes (DSSE / gate 3B4).

    Returns a dict of view_name -> row_count for each view.
    """
    src = _validate_sqlite_path(sqlite_path)
    if scratch:
        with tempfile.TemporaryDirectory(dir=str(src.parent)) as tdir:
            work_db = Path(tdir) / "infra_wiring_scratch.sqlite"
            shutil.copy2(src, work_db)
            return _materialize_infra_views_mutating(work_db)
    return _materialize_infra_views_mutating(src)


def _materialize_infra_views_mutating(work_db: Path) -> dict[str, int]:
    conn = sqlite3.connect(str(work_db), timeout=30)
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        cursor = conn.cursor()
        # Find ADG node names for raw infra packages (they use ADG::Symbol:: prefix)
        infra_adg_names = []
        for pkg in _RAW_INFRA_PACKAGES:
            cursor.execute(
                "SELECT DISTINCT adg_name FROM nodes WHERE adg_name = ? AND identity_kind IN ('external_module', 'external_provider')",
                (f"ADG::Symbol::{pkg}",),
            )
            rows = cursor.fetchall()
            for (name,) in rows:
                infra_adg_names.append(name)

        # HTTP-specific subset for v_p1_raw_http_outside_seam
        _http_pkg_set = {"aiohttp", "httpx", "requests"}
        http_adg_names = [n for n in infra_adg_names if any(n == f"ADG::Symbol::{p}" for p in _http_pkg_set)]
        http_in = ", ".join(f"'{n}'" for n in http_adg_names) if http_adg_names else "'__none__'"

        # Find ADG node names for provider SDKs
        provider_adg_names = []
        for pkg in _PROVIDER_SDKS:
            cursor.execute(
                "SELECT DISTINCT adg_name FROM nodes WHERE adg_name = ? AND identity_kind IN ('external_module', 'external_provider')",
                (f"ADG::Symbol::{pkg}",),
            )
            rows = cursor.fetchall()
            for (name,) in rows:
                provider_adg_names.append(name)

        # Drop existing views (idempotent recreation) — order matters for dependencies
        for vname in (  # tqdm: small fixed tuple of view names, no bar needed
            "v_infra_violations_summary",  # depends on P0 views, drop first
            "v_p0_apps_direct_infra",
            "v_p0_provider_bypass",
            "v_p0_core_imports_apps",
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
        ):
            cursor.execute(f"DROP VIEW IF EXISTS {vname}")

        # Build parameterized SQL for IN clauses
        infra_in = ", ".join(f"'{n}'" for n in infra_adg_names) if infra_adg_names else "'__none__'"
        provider_in = ", ".join(f"'{n}'" for n in provider_adg_names) if provider_adg_names else "'__none__'"
        adapter_paths_clause = _build_adapter_path_clause()
        process_boundary_clause = _build_process_boundary_clause()

        # Materialize t_infra_importers: the set of resolved_path values that import raw infra.
        # This is used by P0-3 (write bypass) and P0-5 (L6 mutation) to scope those views to
        # files that actually touch raw infra packages, excluding plain filesystem I/O.
        # Using a real table (not a VIEW) so it can be JOINed efficiently without correlated subqueries.
        cursor.execute("DROP TABLE IF EXISTS t_infra_importers")
        cursor.execute(
            f"""
            CREATE TABLE t_infra_importers AS
            SELECT DISTINCT n_src.resolved_path
            FROM edges e
            JOIN nodes n_src ON e.src_id = n_src.id
            JOIN nodes n_dst ON e.dst_id = n_dst.id
            WHERE e.relation_type = 'imports'
              AND n_dst.adg_name IN ({infra_in})
              AND n_src.resolved_path NOT IN {adapter_paths_clause}
        """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_t_infra_importers_path ON t_infra_importers(resolved_path)"
        )
        materialize_receipt_ast_sites(conn)

        # Create all views with actual node names
        # P0 views
        sanctioned_app_clause = _build_sanctioned_app_clause()
        cursor.execute(
            _VIEW_P0_APPS_DIRECT_INFRA.format(
                infra_adg_names=infra_in, sanctioned_app_paths=sanctioned_app_clause
            )
        )
        cursor.execute(_VIEW_P0_PROVIDER_BYPASS.format(provider_adg_names=provider_in))
        cursor.execute(_VIEW_P0_CORE_IMPORTS_APPS)
        cursor.execute(_VIEW_P0_WRITE_BYPASS_UWG.format(infra_adg_names=infra_in))
        cursor.execute(_VIEW_P0_L1_DIRECT_INFRA.format(infra_adg_names=infra_in))
        cursor.execute(_VIEW_P0_L6_MUTATION.format(infra_adg_names=infra_in))
        cursor.execute(_VIEW_P0_L0_RAW_EXECUTION.format(infra_adg_names=infra_in))
        # P1 views
        cursor.execute(
            _VIEW_P1_ZERO_CALLER_INFRA.format(
                adapter_paths=adapter_paths_clause, process_boundary_paths=process_boundary_clause
            )
        )
        cursor.execute(
            _VIEW_P1_NOT_ON_SPINE.format(
                adapter_paths=adapter_paths_clause, process_boundary_paths=process_boundary_clause
            )
        )
        cursor.execute(_VIEW_P1_AD_HOC_IMPORTS.format(infra_adg_names=infra_in))
        cursor.execute(_VIEW_P1_MIS_LAYERED_INFRA)
        cursor.execute(_VIEW_P1_RAW_HTTP_OUTSIDE_SEAM.format(http_adg_names=http_in))
        # P2 views
        cursor.execute(
            _VIEW_P2_MIXED_USAGE.format(
                adapter_paths=adapter_paths_clause,
                infra_adg_names=infra_in,
            )
        )
        cursor.execute(
            _VIEW_P2_DUPLICATED_ADAPTERS.format(
                adapter_paths=adapter_paths_clause,
                infra_adg_names=infra_in,
            )
        )
        cursor.execute(_VIEW_P2_DORMANT_AMBIGUOUS.format(adapter_paths=adapter_paths_clause))
        # P3 view
        cursor.execute(_VIEW_P3_ISOLATED_EXPERIMENTAL)
        # Summary view (must be last — depends on P0 views)
        cursor.execute(_VIEW_INFRA_VIOLATIONS_SUMMARY)

        conn.commit()

        # Query row counts for all views
        _ALL_VIEW_NAMES = (
            "v_p0_apps_direct_infra",
            "v_p0_provider_bypass",
            "v_p0_core_imports_apps",
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
            "v_infra_violations_summary",
        )
        counts: dict[str, int] = {}
        for vname in _ALL_VIEW_NAMES:
            cursor.execute(f"SELECT COUNT(*) FROM {vname}")
            (count,) = cursor.fetchone()
            counts[vname] = count

        return counts
    finally:
        conn.close()


def enrich_and_report(sqlite_path: Path) -> None:
    """Enrich ADG SQLite with infra views and print summary."""
    print("[ADG] Materializing infrastructure wiring views (16 checks)...")
    counts = materialize_infra_views(sqlite_path)

    p0_views = [
        "v_p0_apps_direct_infra",
        "v_p0_provider_bypass",
        "v_p0_core_imports_apps",
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
        "v_p1_raw_http_outside_seam",
    ]
    p2_views = ["v_p2_mixed_usage", "v_p2_duplicated_adapters", "v_p2_dormant_ambiguous"]
    p3_views = ["v_p3_isolated_experimental"]

    total_p0 = sum(counts.get(v, 0) for v in p0_views)
    total_p1 = sum(counts.get(v, 0) for v in p1_views)
    total_p2 = sum(counts.get(v, 0) for v in p2_views)
    total_p3 = sum(counts.get(v, 0) for v in p3_views)

    print(f"[ADG] Infra wiring: P0={total_p0} P1={total_p1} P2={total_p2} P3={total_p3}")
    for v in p0_views:
        c = counts.get(v, 0)
        if c > 0:
            print(f"[ADG]   {v}: {c}")
    for v in p1_views:
        c = counts.get(v, 0)
        if c > 0:
            print(f"[ADG]   {v}: {c}")
    for v in p2_views:
        c = counts.get(v, 0)
        if c > 0:
            print(f"[ADG]   {v}: {c}")
    for v in p3_views:
        c = counts.get(v, 0)
        if c > 0:
            print(f"[ADG]   {v}: {c}")
