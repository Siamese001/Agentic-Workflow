"""Edge-authority classifier (SSOT) — three-bucket model.

This module is the SSOT for ADG edge classification under the 2026-04-29
**three-bucket authority model**:

    bucket ∈ {static, runtime, registry}
    resolution_status ∈ {VERIFIED_MODULE, ..., UNKNOWN}
    authority_status ∈ {AUTHORITATIVE, AUTHORITATIVE_RUNTIME, AUTHORITATIVE_REGISTRY,
                        PARTIAL, NON_AUTHORITATIVE_HINT, RISK_SIGNAL_ONLY,
                        EXCLUDED_TEST_ONLY, EXCLUDED_TYPE_ONLY, EXTERNAL_ONLY,
                        UNKNOWN_NOT_PROOF}

Three buckets:

* **static** — what the code can reference (AST imports, calls, type-only
  refs, dynamic literal-string imports, etc.)
* **runtime** — what actually happened during execution (OTel traces,
  receipts, sealed L2 artifacts)
* **registry** — what configuration/registries declare (agent_specs.json,
  MCP config, tool registries, prompt slots, route declarations)

Authority law:

* **proof** = ``authority_status ∈ {AUTHORITATIVE, AUTHORITATIVE_RUNTIME,
  AUTHORITATIVE_REGISTRY}``. Only these may be used as proof for
  governance/hotspot/coverage/refactor-impact claims.
* **risk** = ``authority_status ∈ {RISK_SIGNAL_ONLY, UNKNOWN_NOT_PROOF,
  PARTIAL}``. Used for cleanup backlog, risk triage. Never proof.
* **inventory_only** = anything else (``EXCLUDED_*``, ``EXTERNAL_ONLY``,
  ``NON_AUTHORITATIVE_HINT``). Used for debugging/audits. Never proof,
  not flagged as risk.

Back-compat with the 2026-04-28 single-axis ``authority`` column:

| Legacy ``authority`` | New ``bucket`` | New ``resolution_status``  | New ``authority_status``     |
|----------------------|----------------|----------------------------|------------------------------|
| ``verified``         | ``static``     | ``VERIFIED_MODULE``        | ``AUTHORITATIVE``            |
| ``unresolved``       | ``static``     | ``UNRESOLVED_MODULE``      | ``RISK_SIGNAL_ONLY``         |
| ``dynamic``          | ``static``     | ``UNRESOLVED_DYNAMIC``     | ``UNKNOWN_NOT_PROOF``        |
| ``external``         | ``static``     | ``NOT_APPLICABLE``         | ``EXTERNAL_ONLY``            |
| ``test_only``        | ``static``     | ``VERIFIED_MODULE``        | ``EXCLUDED_TEST_ONLY``       |
| ``runtime_observed`` | ``runtime``    | ``VERIFIED_RUNTIME``       | ``AUTHORITATIVE_RUNTIME``    |

Tests in ``tests/unit/agentic_core/adg/artifact/test_edge_authority.py``
assert this mapping holds in lockstep across the Python and SQL paths.

Doctrinal source: 2026-04-29 user directive — "Redesign and harden ADG
around the correct three-bucket graph authority model."
"""

from __future__ import annotations

from typing import Final, Literal

# ---------------------------------------------------------------------------
# Closed enum: bucket
# ---------------------------------------------------------------------------

Bucket = Literal["static", "runtime", "registry"]

ALL_BUCKETS: Final[frozenset[str]] = frozenset({"static", "runtime", "registry"})

# ---------------------------------------------------------------------------
# Closed enum: resolution_status (per spec Section 1)
# ---------------------------------------------------------------------------

STATIC_RESOLUTION_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "VERIFIED_MODULE",
        "VERIFIED_SYMBOL",
        "UNRESOLVED_MODULE",
        "UNRESOLVED_SYMBOL",
        "UNRESOLVED_DYNAMIC",
        "PARTIAL",
        "NOT_CHECKED",
        "NOT_APPLICABLE",
        "UNKNOWN",
    }
)

RUNTIME_RESOLUTION_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "VERIFIED_RUNTIME",
        "VERIFIED_TRACE",
        "VERIFIED_RECEIPT",
        "PARTIAL_TRACE",
        "MISSING_TRACE",
        "NOT_APPLICABLE",
        "UNKNOWN",
    }
)

REGISTRY_RESOLUTION_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "VERIFIED_REGISTRY",
        "VERIFIED_CONFIG",
        "UNRESOLVED_REGISTRY",
        "STALE_REGISTRY",
        "MISMATCHED_REGISTRY",
        "SUBSTITUTED_REGISTRY",
        "NOT_APPLICABLE",
        "UNKNOWN",
    }
)

ALL_RESOLUTION_STATUSES: Final[frozenset[str]] = (
    STATIC_RESOLUTION_STATUSES | RUNTIME_RESOLUTION_STATUSES | REGISTRY_RESOLUTION_STATUSES
)

# ---------------------------------------------------------------------------
# Closed enum: authority_status (per spec Section 2)
# ---------------------------------------------------------------------------

AuthorityStatus = Literal[
    "AUTHORITATIVE",
    "AUTHORITATIVE_RUNTIME",
    "AUTHORITATIVE_REGISTRY",
    "PARTIAL",
    "NON_AUTHORITATIVE_HINT",
    "RISK_SIGNAL_ONLY",
    "EXCLUDED_TEST_ONLY",
    "EXCLUDED_TYPE_ONLY",
    "EXTERNAL_ONLY",
    "UNKNOWN_NOT_PROOF",
]

ALL_AUTHORITY_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "AUTHORITATIVE",
        "AUTHORITATIVE_RUNTIME",
        "AUTHORITATIVE_REGISTRY",
        "PARTIAL",
        "NON_AUTHORITATIVE_HINT",
        "RISK_SIGNAL_ONLY",
        "EXCLUDED_TEST_ONLY",
        "EXCLUDED_TYPE_ONLY",
        "EXTERNAL_ONLY",
        "UNKNOWN_NOT_PROOF",
    }
)

PROOF_STATUSES: Final[frozenset[str]] = frozenset(
    {"AUTHORITATIVE", "AUTHORITATIVE_RUNTIME", "AUTHORITATIVE_REGISTRY"}
)

RISK_STATUSES: Final[frozenset[str]] = frozenset({"RISK_SIGNAL_ONLY", "UNKNOWN_NOT_PROOF", "PARTIAL"})

INVENTORY_ONLY_STATUSES: Final[frozenset[str]] = frozenset(
    {"EXCLUDED_TEST_ONLY", "EXCLUDED_TYPE_ONLY", "EXTERNAL_ONLY", "NON_AUTHORITATIVE_HINT"}
)

# Sanity invariants — every authority_status is in exactly one law-bucket.
assert PROOF_STATUSES.isdisjoint(RISK_STATUSES)
assert PROOF_STATUSES.isdisjoint(INVENTORY_ONLY_STATUSES)
assert RISK_STATUSES.isdisjoint(INVENTORY_ONLY_STATUSES)
assert PROOF_STATUSES | RISK_STATUSES | INVENTORY_ONLY_STATUSES == ALL_AUTHORITY_STATUSES


def is_proof(authority_status: str) -> bool:
    """True iff this status may be used as proof.

    Proof statuses: AUTHORITATIVE, AUTHORITATIVE_RUNTIME, AUTHORITATIVE_REGISTRY.
    Used by ``proof_view`` / proof_mode consumers (governance, hotspot,
    coverage, refactor-impact, layer-boundary claims).
    """
    return authority_status in PROOF_STATUSES


def is_risk(authority_status: str) -> bool:
    """True iff this status is a risk signal — NOT proof.

    Risk statuses: RISK_SIGNAL_ONLY, UNKNOWN_NOT_PROOF, PARTIAL. Used by
    ``risk_view`` / risk_mode consumers (cleanup backlog, missing-trace,
    incomplete instrumentation).
    """
    return authority_status in RISK_STATUSES


def is_inventory_only(authority_status: str) -> bool:
    """True iff this status is inventory-only — NOT proof, NOT risk.

    Inventory-only statuses: EXCLUDED_TEST_ONLY, EXCLUDED_TYPE_ONLY,
    EXTERNAL_ONLY, NON_AUTHORITATIVE_HINT. Visible only in
    ``inventory_view`` / inventory_mode consumers.
    """
    return authority_status in INVENTORY_ONLY_STATUSES


# ---------------------------------------------------------------------------
# Legacy ``authority`` enum (2026-04-28) — kept for back-compat
# ---------------------------------------------------------------------------

Authority = Literal[
    "verified",
    "unresolved",
    "dynamic",
    "external",
    "test_only",
    "runtime_observed",
]

ALL_AUTHORITIES: Final[frozenset[str]] = frozenset(
    {"verified", "unresolved", "dynamic", "external", "test_only", "runtime_observed"}
)

LEGACY_AUTHORITY_TO_TRIPLET: Final[dict[str, tuple[str, str, str]]] = {
    "verified": ("static", "VERIFIED_MODULE", "AUTHORITATIVE"),
    "unresolved": ("static", "UNRESOLVED_MODULE", "RISK_SIGNAL_ONLY"),
    "dynamic": ("static", "UNRESOLVED_DYNAMIC", "UNKNOWN_NOT_PROOF"),
    "external": ("static", "NOT_APPLICABLE", "EXTERNAL_ONLY"),
    "test_only": ("static", "VERIFIED_MODULE", "EXCLUDED_TEST_ONLY"),
    "runtime_observed": ("runtime", "VERIFIED_RUNTIME", "AUTHORITATIVE_RUNTIME"),
}


def map_legacy_authority(legacy: str) -> tuple[str, str, str]:
    """Return ``(bucket, resolution_status, authority_status)`` for a legacy
    ``authority`` value. Raises ``KeyError`` for unknown values — that is
    the SSOT signal that a downstream caller has fabricated an out-of-enum
    value.
    """
    return LEGACY_AUTHORITY_TO_TRIPLET[legacy]


# ---------------------------------------------------------------------------
# Static-bucket classifier (the original 2026-04-28 work, preserved verbatim)
# ---------------------------------------------------------------------------

INTERNAL_PACKAGE_ROOTS: Final[tuple[str, ...]] = (
    "agentic_core.",
    "apps_eval.",
    "apps_exec.",
    "apps_lic.",
    "apps_research.",
    "apps_rg.",
    "apps_shared.",
    "apps_underwriting_ai.",
    "system_learning.",
    "ops_scripts.",
    "tools.",
    "infrastructure.",
    "scripts.",
)


def is_internal_module_name(name: str) -> bool:
    """Return True iff a module/symbol path is rooted at a production package."""
    return any(name == root.rstrip(".") or name.startswith(root) for root in INTERNAL_PACKAGE_ROOTS)


def classify_authority(
    *,
    source_file: str,
    dst_resolved_path: str | None,
    dst_adg_name: str | None,
    is_dynamic: bool = False,
    is_runtime_observed: bool = False,
) -> Authority:
    """Compute legacy ``authority`` value (preserved for back-compat).

    See ``classify_triplet`` for the new three-bucket classifier.
    """
    if is_runtime_observed:
        return "runtime_observed"

    if _is_test_source(source_file):
        return "test_only"

    if is_dynamic:
        return "dynamic"

    name = (dst_adg_name or "").strip()
    if name.startswith("ADG::Symbol::"):
        name_body = name[len("ADG::Symbol::") :]
    elif name.startswith("ADG::Module::"):
        name_body = name[len("ADG::Module::") :]
    else:
        name_body = name

    has_resolved = bool((dst_resolved_path or "").strip())
    is_internal = is_internal_module_name(name_body) if name_body else False

    if not is_internal and not has_resolved:
        return "external"

    if has_resolved:
        return "verified"

    return "unresolved"


def classify_triplet(
    *,
    source_file: str,
    dst_resolved_path: str | None,
    dst_adg_name: str | None,
    is_dynamic: bool = False,
    is_runtime_observed: bool = False,
) -> tuple[str, str, str]:
    """Compute the (bucket, resolution_status, authority_status) triplet.

    This is the canonical Python classifier under the 2026-04-29 model.
    Internally derives the legacy authority and runs ``map_legacy_authority``,
    guaranteeing the two paths agree.
    """
    legacy = classify_authority(
        source_file=source_file,
        dst_resolved_path=dst_resolved_path,
        dst_adg_name=dst_adg_name,
        is_dynamic=is_dynamic,
        is_runtime_observed=is_runtime_observed,
    )
    return map_legacy_authority(legacy)


def _is_test_source(source_file: str) -> bool:
    """Return True iff the source file lives under a tests/ tree."""
    if not source_file:
        return False
    sf = source_file.replace("\\", "/")
    return sf.startswith("tests/") or "/tests/" in sf or sf.endswith("/conftest.py") or sf == "conftest.py"


# ---------------------------------------------------------------------------
# SQL: legacy backfill (preserved verbatim from 2026-04-28)
# ---------------------------------------------------------------------------

SQL_AUTHORITY_CASE: Final[str] = """\
CASE
    WHEN :is_runtime_observed = 1 THEN 'runtime_observed'
    WHEN e.source_file LIKE 'tests/%'
      OR e.source_file LIKE '%/tests/%'
      OR e.source_file = 'conftest.py'
      OR e.source_file LIKE '%/conftest.py'
        THEN 'test_only'
    WHEN :is_dynamic = 1 THEN 'dynamic'
    WHEN (n.resolved_path IS NOT NULL AND n.resolved_path != '')
        THEN 'verified'
    WHEN n.adg_name LIKE 'ADG::Symbol::agentic_core.%'
      OR n.adg_name LIKE 'ADG::Symbol::apps_%'
      OR n.adg_name LIKE 'ADG::Symbol::system_learning.%'
      OR n.adg_name LIKE 'ADG::Symbol::ops_scripts.%'
      OR n.adg_name LIKE 'ADG::Symbol::tools.%'
      OR n.adg_name LIKE 'ADG::Symbol::infrastructure.%'
      OR n.adg_name LIKE 'ADG::Symbol::scripts.%'
      OR n.adg_name LIKE 'ADG::Module::agentic_core.%'
      OR n.adg_name LIKE 'ADG::Module::apps_%'
      OR n.adg_name LIKE 'ADG::Module::system_learning.%'
      OR n.adg_name LIKE 'ADG::Module::ops_scripts.%'
      OR n.adg_name LIKE 'ADG::Module::tools.%'
      OR n.adg_name LIKE 'ADG::Module::infrastructure.%'
      OR n.adg_name LIKE 'ADG::Module::scripts.%'
        THEN 'unresolved'
    ELSE 'external'
END
"""

SQL_AUTHORITY_BACKFILL: Final[str] = """\
UPDATE edges
SET authority = (
    SELECT
        CASE
            WHEN edges.source_file LIKE 'tests/%'
              OR edges.source_file LIKE '%/tests/%'
              OR edges.source_file = 'conftest.py'
              OR edges.source_file LIKE '%/conftest.py'
                THEN 'test_only'
            WHEN edges.edge_kind = 'dynamic_import'
              OR edges.dynamic_resolution = 'dynamic'
                THEN 'dynamic'
            WHEN (n.resolved_path IS NOT NULL AND n.resolved_path != '')
                THEN 'verified'
            WHEN n.adg_name LIKE 'ADG::Symbol::agentic_core.%'
              OR n.adg_name LIKE 'ADG::Symbol::apps_%'
              OR n.adg_name LIKE 'ADG::Symbol::system_learning.%'
              OR n.adg_name LIKE 'ADG::Symbol::ops_scripts.%'
              OR n.adg_name LIKE 'ADG::Symbol::tools.%'
              OR n.adg_name LIKE 'ADG::Symbol::infrastructure.%'
              OR n.adg_name LIKE 'ADG::Symbol::scripts.%'
              OR n.adg_name LIKE 'ADG::Module::agentic_core.%'
              OR n.adg_name LIKE 'ADG::Module::apps_%'
              OR n.adg_name LIKE 'ADG::Module::system_learning.%'
              OR n.adg_name LIKE 'ADG::Module::ops_scripts.%'
              OR n.adg_name LIKE 'ADG::Module::tools.%'
              OR n.adg_name LIKE 'ADG::Module::infrastructure.%'
              OR n.adg_name LIKE 'ADG::Module::scripts.%'
                THEN 'unresolved'
            ELSE 'external'
        END
    FROM nodes n
    WHERE n.id = edges.dst_id
)
WHERE authority IS NULL
"""

# ---------------------------------------------------------------------------
# SQL: triplet backfill (the new 2026-04-29 path)
# ---------------------------------------------------------------------------

# After ``SQL_AUTHORITY_BACKFILL`` populates ``edges.authority``, this UPDATE
# fans the legacy value out into ``bucket`` / ``resolution_status`` /
# ``authority_status``. Keep the CASE in lockstep with ``LEGACY_AUTHORITY_TO_TRIPLET``.
SQL_TRIPLET_BACKFILL: Final[str] = """\
UPDATE edges
SET
    bucket = CASE authority
        WHEN 'runtime_observed' THEN 'runtime'
        ELSE 'static'
    END,
    resolution_status = CASE authority
        WHEN 'verified'         THEN 'VERIFIED_MODULE'
        WHEN 'unresolved'       THEN 'UNRESOLVED_MODULE'
        WHEN 'dynamic'          THEN 'UNRESOLVED_DYNAMIC'
        WHEN 'external'         THEN 'NOT_APPLICABLE'
        WHEN 'test_only'        THEN 'VERIFIED_MODULE'
        WHEN 'runtime_observed' THEN 'VERIFIED_RUNTIME'
        ELSE 'UNKNOWN'
    END,
    authority_status = CASE authority
        WHEN 'verified'         THEN 'AUTHORITATIVE'
        WHEN 'unresolved'       THEN 'RISK_SIGNAL_ONLY'
        WHEN 'dynamic'          THEN 'UNKNOWN_NOT_PROOF'
        WHEN 'external'         THEN 'EXTERNAL_ONLY'
        WHEN 'test_only'        THEN 'EXCLUDED_TEST_ONLY'
        WHEN 'runtime_observed' THEN 'AUTHORITATIVE_RUNTIME'
        ELSE 'UNKNOWN_NOT_PROOF'
    END
WHERE bucket IS NULL OR resolution_status IS NULL OR authority_status IS NULL
"""

# ---------------------------------------------------------------------------
# Materialized views — proof_view / risk_view / inventory_view (canonical)
# ---------------------------------------------------------------------------

# proof_view — only AUTHORITATIVE / AUTHORITATIVE_RUNTIME / AUTHORITATIVE_REGISTRY.
# Governance / hotspot / coverage / refactor-impact / layer-boundary claims
# MUST consume this view.
SQL_PROOF_VIEW: Final[str] = """\
DROP VIEW IF EXISTS proof_view;
CREATE VIEW proof_view AS
SELECT *
FROM edges
WHERE authority_status IN (
    'AUTHORITATIVE',
    'AUTHORITATIVE_RUNTIME',
    'AUTHORITATIVE_REGISTRY'
);
"""

# risk_view — RISK_SIGNAL_ONLY / UNKNOWN_NOT_PROOF / PARTIAL. The cleanup-
# backlog / missing-trace / incomplete-instrumentation surface. Consumers
# MUST label output as risk, not proof.
SQL_RISK_VIEW: Final[str] = """\
DROP VIEW IF EXISTS risk_view;
CREATE VIEW risk_view AS
SELECT *
FROM edges
WHERE authority_status IN (
    'RISK_SIGNAL_ONLY',
    'UNKNOWN_NOT_PROOF',
    'PARTIAL'
);
"""

# inventory_view — every edge regardless of authority. Used for debugging,
# audits, migrations, before/after comparison. Consumers MUST label output
# as inventory, not proof.
SQL_INVENTORY_VIEW: Final[str] = """\
DROP VIEW IF EXISTS inventory_view;
CREATE VIEW inventory_view AS
SELECT *
FROM edges;
"""

# ---------------------------------------------------------------------------
# Legacy materialized views (2026-04-28) — kept as deprecation aliases.
# ---------------------------------------------------------------------------

SQL_MV_VERIFIED: Final[str] = """\
DROP VIEW IF EXISTS mv_edges_verified;
CREATE VIEW mv_edges_verified AS
SELECT *
FROM edges
WHERE authority = 'verified';
"""

SQL_MV_UNRESOLVED: Final[str] = """\
DROP VIEW IF EXISTS mv_edges_unresolved;
CREATE VIEW mv_edges_unresolved AS
SELECT
    e.id,
    e.relation_type,
    e.edge_kind,
    e.source_file,
    e.line_no,
    e.symbol,
    e.authority,
    n.adg_name AS dst_adg_name
FROM edges e
JOIN nodes n ON n.id = e.dst_id
WHERE e.authority = 'unresolved';
"""

SQL_MV_GOVERNANCE: Final[str] = """\
DROP VIEW IF EXISTS mv_edges_governance;
CREATE VIEW mv_edges_governance AS
SELECT *
FROM edges
WHERE authority IN ('verified', 'external', 'test_only', 'runtime_observed');
"""

# Authority distribution snapshot — quick health signal.
SQL_AUTHORITY_HISTOGRAM: Final[str] = (
    "SELECT authority, COUNT(*) AS n FROM edges GROUP BY authority ORDER BY n DESC"
)

# Three-bucket histogram — health signal under the new model.
SQL_TRIPLET_HISTOGRAM: Final[str] = (
    "SELECT bucket, authority_status, COUNT(*) AS n FROM edges "
    "GROUP BY bucket, authority_status ORDER BY n DESC"
)

# ---------------------------------------------------------------------------
# Runtime bucket as VIEW (not lift) — 2026-04-29 Mid-Day Pivot
# ---------------------------------------------------------------------------
#
# Doctrinal source: 2026-04-29 user critique — "the runtime ADG isnt that a
# fake concept? should it is OTEL traces". Validated against:
#
#   - OpenTelemetry GenAI SIG semconv (gen-ai-agent-spans)
#   - OpenAI Agents SDK Tracing docs
#   - Anthropic Claude Code Monitoring docs
#   - CNCF "single source of truth for telemetry" principle
#
# Architectural pivot:
#
#   OLD:  OTel spans -> runtime_adg.sqlite -> LIFT into edges.bucket=runtime
#   NEW:  OTel spans -> runtime_adg_store (the OTel sink) -> SUMMARIZE into
#         v_runtime_proof TABLE at snapshot generation time
#
# v_runtime_proof is a SQLite TABLE (not a VIEW — needs to hold persisted
# summary rows, not be a live reflection of `edges`). The "view" naming is
# logical: it is a deterministic projection of the OTel store at snapshot
# time. Consumers query it just like the canonical 3-views; CI gates assert
# every row has trace_id evidence.
#
# Schema rules:
#
#   bucket             always 'runtime'
#   resolution_status  ∈ {VERIFIED_RUNTIME, PARTIAL_TRACE, MISSING_TRACE}
#   authority_status   ∈ {AUTHORITATIVE_RUNTIME, PARTIAL, UNKNOWN_NOT_PROOF}
#   evidence_refs      JSON: {"trace_ids": [...top 5...], "run_ids": [...]}
#   attesting_trace_count >= 1 for any AUTHORITATIVE_RUNTIME row
#
# proof_view does NOT change — it stays bound to `edges`. Consumers wanting
# all-bucket proof use the convenience helper proof_view_all (defined below)
# which UNIONs edges-proof with runtime-proof on a normalized projection.
SQL_CREATE_V_RUNTIME_PROOF: Final[str] = """\
CREATE TABLE IF NOT EXISTS v_runtime_proof (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    src_name              TEXT NOT NULL,
    dst_name              TEXT NOT NULL,
    relation_type         TEXT NOT NULL,
    edge_kind             TEXT NOT NULL DEFAULT 'RUNTIME_OBSERVED',
    static_edge_id        INTEGER DEFAULT NULL,
    attesting_trace_count INTEGER NOT NULL DEFAULT 0,
    latest_trace_id       TEXT DEFAULT '',
    latest_span_id        TEXT DEFAULT '',
    last_seen_at          TEXT DEFAULT '',
    evidence_refs         TEXT DEFAULT NULL,
    bucket                TEXT NOT NULL DEFAULT 'runtime',
    resolution_status     TEXT NOT NULL DEFAULT 'VERIFIED_RUNTIME',
    authority_status      TEXT NOT NULL DEFAULT 'AUTHORITATIVE_RUNTIME',
    UNIQUE(src_name, dst_name, relation_type)
);
CREATE INDEX IF NOT EXISTS idx_v_runtime_proof_static_edge
    ON v_runtime_proof(static_edge_id) WHERE static_edge_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_v_runtime_proof_authority
    ON v_runtime_proof(authority_status);
CREATE INDEX IF NOT EXISTS idx_v_runtime_proof_relation
    ON v_runtime_proof(relation_type);
"""

# All-bucket proof view: convenience UNION over edges-proof and runtime-proof.
# Projection is the minimal common set so the two row sources align.
# Static / registry rows come from `edges`; runtime rows come from
# `v_runtime_proof`. CI gates that need to query "every authoritative edge
# regardless of bucket" should use this view.
SQL_PROOF_VIEW_ALL: Final[str] = """\
DROP VIEW IF EXISTS proof_view_all;
CREATE VIEW proof_view_all AS
SELECT
    'edges'                AS source_table,
    e.id                   AS source_row_id,
    s.adg_name             AS src_name,
    d.adg_name             AS dst_name,
    e.relation_type        AS relation_type,
    e.edge_kind            AS edge_kind,
    e.bucket               AS bucket,
    e.resolution_status    AS resolution_status,
    e.authority_status     AS authority_status,
    e.evidence_refs        AS evidence_refs
FROM edges e
JOIN nodes s ON s.id = e.src_id
JOIN nodes d ON d.id = e.dst_id
WHERE e.authority_status IN ('AUTHORITATIVE', 'AUTHORITATIVE_REGISTRY')
UNION ALL
SELECT
    'v_runtime_proof'      AS source_table,
    r.id                   AS source_row_id,
    r.src_name             AS src_name,
    r.dst_name             AS dst_name,
    r.relation_type        AS relation_type,
    r.edge_kind            AS edge_kind,
    r.bucket               AS bucket,
    r.resolution_status    AS resolution_status,
    r.authority_status     AS authority_status,
    r.evidence_refs        AS evidence_refs
FROM v_runtime_proof r
WHERE r.authority_status = 'AUTHORITATIVE_RUNTIME';
"""

# Histogram of runtime proof rows — health signal for OTel coverage.
SQL_RUNTIME_PROOF_HISTOGRAM: Final[str] = (
    "SELECT authority_status, COUNT(*) AS n FROM v_runtime_proof "
    "GROUP BY authority_status ORDER BY n DESC"
)


def runtime_authority_for(
    *, attesting_trace_count: int, partial_trace_count: int = 0
) -> tuple[str, str]:
    """Classify a runtime evidence summary into (resolution_status, authority_status).

    Maps OTel evidence count to the closed three-bucket runtime enums.

    Rules:
      - >=1 verified trace, no partials -> (VERIFIED_RUNTIME, AUTHORITATIVE_RUNTIME)
      - >=1 verified trace, some partials -> (VERIFIED_RUNTIME, AUTHORITATIVE_RUNTIME)
        (any verified trace is sufficient; partials don't reduce confidence
        as long as ANY full trace attests)
      - 0 verified, >=1 partial -> (PARTIAL_TRACE, PARTIAL)
      - 0 of either -> (MISSING_TRACE, UNKNOWN_NOT_PROOF)
    """
    if attesting_trace_count >= 1:
        return ("VERIFIED_RUNTIME", "AUTHORITATIVE_RUNTIME")
    if partial_trace_count >= 1:
        return ("PARTIAL_TRACE", "PARTIAL")
    return ("MISSING_TRACE", "UNKNOWN_NOT_PROOF")
