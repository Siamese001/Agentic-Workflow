"""W3 — shared repo-area / layer matching for Author-Gate precedent lookup.

Used by lookup_refactor_decisions to reduce FTS false positives and enforce
plan author-gate-learning-harden-f4e8a2 scope guards.
"""

from __future__ import annotations


def normalize_repo_path(value: str) -> str:
    return (value or "").strip().replace("\\", "/").strip("/")


def repo_areas_compatible_strong(query_area: str, row_area: str) -> bool:
    """Prefix-strict overlap required for **strong** precedent.

    When the query carries a repo_area, the ledger row must record a
    compatible path (row is query or extends query). Empty row area with a
    non-empty query never yields strong.
    """
    q = normalize_repo_path(query_area)
    r = normalize_repo_path(row_area)
    if not q:
        return True
    if not r:
        return False
    return r == q or r.startswith(q + "/")


def repo_areas_compatible_suggestive(query_area: str, row_area: str) -> bool:
    """Looser overlap for **suggestive** only (still blocks obvious cross-app noise).

    - No query area → any row area OK.
    - Query area set but row empty → reject (unknown scope).
    - Otherwise allow hierarchical prefix in either direction, or same top-level
      segment (e.g. ``agentic_core/...`` vs ``agentic_core/other``).
    """
    q = normalize_repo_path(query_area)
    r = normalize_repo_path(row_area)
    if not q:
        return True
    if not r:
        return False
    if r == q:
        return True
    if r.startswith(q) or q.startswith(r):
        return True
    q0 = q.split("/", 1)[0]
    r0 = r.split("/", 1)[0]
    return bool(q0 and q0 == r0)


def layer_matches(query_layer: str, row_layer: str | None) -> bool:
    if not (query_layer or "").strip():
        return True
    ql = query_layer.strip()
    rl = (row_layer or "").strip()
    if not rl:
        return True
    return rl == ql
