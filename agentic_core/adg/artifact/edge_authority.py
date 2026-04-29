"""Edge-authority classifier (SSOT).

Every edge in the canonical ADG ``edges`` table MUST carry an explicit
``authority`` value drawn from the closed enum:

| Authority           | Meaning                                                    |
|---------------------|------------------------------------------------------------|
| ``verified``        | Target node has a real ``resolved_path`` on disk.          |
| ``unresolved``      | Target node is internal-prefixed but has no resolved_path. |
| ``dynamic``         | Edge originated from importlib.import_module(...) /        |
|                     | __import__(...) / getattr(module, "...") literal-string    |
|                     | resolution. Cannot be statically guaranteed.               |
| ``external``        | Target is a third-party / stdlib package — no expectation  |
|                     | of in-repo resolution.                                     |
| ``test_only``       | Edge originates from a test file (under ``tests/``).       |
|                     | Should not feed production hotspot/governance analyses.    |
| ``runtime_observed``| Edge was emitted by the runtime ADG ingest path (otel),    |
|                     | not by static AST scanning.                                |

Precedence (highest to lowest) when multiple categories apply:

    runtime_observed > test_only > dynamic > external > verified > unresolved

Rationale: provenance of the edge dominates. A test-file edge is test_only
even if its target resolves on disk; a dynamic-string import is dynamic even
if the literal happens to resolve today.

Doctrinal source: 2026-04-28 user directive — "The ADG generator must stop
emitting unqualified edges. Every edge must be typed as verified, unresolved,
dynamic, external, test-only, or runtime-observed. Any downstream hotspot,
coverage, or governance analysis must exclude or downgrade unresolved edges."
"""

from __future__ import annotations

from typing import Final, Literal

# Closed enum — DO NOT extend without coordinating with downstream consumers
# (mv_edges_verified, mv_edges_unresolved, check_edge_authority_well_formed).
Authority = Literal[
    "verified",
    "unresolved",
    "dynamic",
    "external",
    "test_only",
    "runtime_observed",
]

ALL_AUTHORITIES: Final[frozenset[str]] = frozenset(
    {
        "verified",
        "unresolved",
        "dynamic",
        "external",
        "test_only",
        "runtime_observed",
    }
)

# Internal package roots — anything imported from one of these MUST resolve.
# Anything outside is `external` by definition.
INTERNAL_PACKAGE_ROOTS: Final[tuple[str, ...]] = (
    "agentic_core.",
    "apps_eval.",
    "apps_exec.",
    "apps_lic.",
    "apps_research.",
    "apps_rfp.",
    "apps_rg.",
    "apps_shared.",
    "apps_underwriting_ai.",
    "system_learning.",
    "ops_scripts.",
    "tools.",
    "infrastructure.",
    "scripts.",
)

# Antipattern relation_types whose authority is derived from the source edge.
# These are synthetic projections; we mark them based on context.
_ANTIPATTERN_RELATION = "antipattern"


def is_internal_module_name(name: str) -> bool:
    """Return True if a module/symbol path is rooted at a production package."""
    return any(name == root.rstrip(".") or name.startswith(root) for root in INTERNAL_PACKAGE_ROOTS)


def classify_authority(
    *,
    source_file: str,
    dst_resolved_path: str | None,
    dst_adg_name: str | None,
    is_dynamic: bool = False,
    is_runtime_observed: bool = False,
) -> Authority:
    """Compute edge authority from edge + target-node metadata.

    Args:
        source_file: ``edges.source_file`` (repo-relative, forward-slash).
        dst_resolved_path: ``nodes.resolved_path`` for the dst node. Empty/None
            is the unresolved signal.
        dst_adg_name: ``nodes.adg_name`` of the dst node. Used to decide
            internal-vs-external when ``dst_resolved_path`` is empty.
        is_dynamic: True if the edge was emitted from a dynamic-resolution AST
            site (``importlib.import_module``, ``__import__``, ``getattr`` on
            a module). The static scanner sets this on emission.
        is_runtime_observed: True if the edge came from runtime ADG ingest
            (otel telemetry), not static scanning.

    Returns:
        One of the six closed-enum values.
    """
    # Highest precedence: provenance overrides target-state.
    if is_runtime_observed:
        return "runtime_observed"

    if _is_test_source(source_file):
        return "test_only"

    if is_dynamic:
        return "dynamic"

    # Target-state classification.
    name = (dst_adg_name or "").strip()
    # Strip the canonical prefix for matching.
    if name.startswith("ADG::Symbol::"):
        name_body = name[len("ADG::Symbol::") :]
    elif name.startswith("ADG::Module::"):
        name_body = name[len("ADG::Module::") :]
    else:
        name_body = name

    has_resolved = bool((dst_resolved_path or "").strip())
    is_internal = is_internal_module_name(name_body) if name_body else False

    if not is_internal and not has_resolved:
        # Third-party / stdlib import.
        return "external"

    if has_resolved:
        return "verified"

    # Internal-prefixed name with no resolved path → broken target.
    return "unresolved"


def _is_test_source(source_file: str) -> bool:
    """Return True if the source file lives under a tests/ tree."""
    if not source_file:
        return False
    sf = source_file.replace("\\", "/")
    return sf.startswith("tests/") or "/tests/" in sf or sf.endswith("/conftest.py") or sf == "conftest.py"


# SQL CASE expression mirror of ``classify_authority`` for use by SQL-backfill
# paths (synthetic antipattern edges, runtime ADG ingest). Keep in lockstep
# with the Python implementation; tests assert the two paths agree.
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

# Backfill UPDATE: sets ``authority`` on every edge whose value is NULL by
# joining to the dst node and applying the SQL classifier above. Used after
# bulk insertion AND after synthetic antipattern emissions, since those are
# inserted without authority and must be backfilled.
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

# Materialized-view DDL: verified edges only. Downstream hotspot, coverage,
# and governance analyses MUST query this view (or filter authority directly).
SQL_MV_VERIFIED: Final[str] = """\
DROP VIEW IF EXISTS mv_edges_verified;
CREATE VIEW mv_edges_verified AS
SELECT *
FROM edges
WHERE authority = 'verified';
"""

# Materialized-view DDL: unresolved edges (governance bucket — "broken target"
# signal). Use to drive the unresolved-edges ratchet and dangling-import RCA.
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

# Materialized-view DDL: GOVERNANCE-grade edges. Per the 2026-04-28 directive
# ("downstream hotspot, coverage, or governance analysis must exclude or
# downgrade unresolved edges"), this is the canonical projection downstream
# consumers join on. Excludes BOTH unresolved AND dynamic — unresolved targets
# are broken; dynamic targets are statically unverifiable. test_only and
# external are INCLUDED because they are valid graph citizens (test_only is a
# test edge, external is a third-party dependency edge); consumers that want
# only-production-only-resolved should JOIN on mv_edges_verified instead.
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
