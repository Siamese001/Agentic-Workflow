"""SSOT-derived NOTION API/database constants for Cursor Agent hooks and scripts.

All `.claude/governance/scripts/*.py` and `tools/*.py` scripts that hit Notion's
REST API MUST import from this module instead of redefining literals.

**Source of truth (since 2026-06-14, plan notion-id-ssot-consolidation):**
the canonical data lives in ``config/notion_databases.yaml``. This module *loads*
that YAML at import and derives every constant from it. The literals below
(``_FALLBACK_*`` / ``_FALLBACK_DB``) are a **fail-soft fallback ONLY** — they are
used when the YAML SSOT is missing or unreadable so this module NEVER fails to
import (it is imported by ~76 governance hooks + CI gates; an import-time raise
would break the whole governance chain).

The fallback literals are asserted equal to the YAML by
``ops_scripts/ci/check_notion_id_ssot_parity.py`` so the mirror can never silently
drift from the SSOT. To change an ID: edit ``config/notion_databases.yaml`` (and
update the fallback to match — the parity gate enforces it), then regenerate the
AGENTS.md NOTION-MAP via ``python .claude/governance/scripts/sync_mcp_config.py``.

TWO IDs PER DATABASE (Notion 2025-09-03 API):
  - data_source_id (YAML ``id``)  → ``*_DATA_SOURCE_ID`` / ``*_DS_ID`` (reads, API-query-data-source)
  - database_id    (YAML ``database_id``) → ``*_DB_ID`` (writes, API-post-page)

Created: 2026-04-25 (audit-uncovered-gates plan, Wave 3).
Allowlisted as SSOT in `ops_scripts/ci/check_external_service_literal_ssot.py`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

# ============================================================================
# Fail-soft fallback literals — used ONLY when config/notion_databases.yaml is
# unavailable. Kept in lockstep with the YAML by check_notion_id_ssot_parity.py.
# ============================================================================

_FALLBACK_NOTION_API_VERSION: Final[str] = "2025-09-03"
_FALLBACK_NOTION_BASE: Final[str] = "https://api.notion.com/v1"
_FALLBACK_NOTION_HTTP_TIMEOUT_S: Final[float] = 15.0

# YAML key -> (database_id, data_source_id). Mirrors config/notion_databases.yaml.
_FALLBACK_DB: Final[dict[str, tuple[str, str]]] = {
    "backlog_items": (
        "aa8d2507-101e-4384-81d9-60ea3fe33876",
        "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7",
    ),
    "plans": (
        "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9",
        "ac53d31b-3068-4039-9ebe-856c12caab32",
    ),
    # ARCHIVED 2026-05-02 — filesystem SSOT (docs/architecture/adr/*.md).
    "adr_registry": (
        "6ed25e12-bd92-4352-ac7a-3a971311f024",
        "e59d7640-dc09-48f9-8bdc-b0c94bf98c2a",
    ),
    # ARCHIVED 2026-05-02 — SQLite SSOT (constitutional §30).
    "author_gate_ledger": (
        "18bb9145-1320-4191-8b14-6c309776bcf5",
        "5b60fdde-7259-491e-9f2d-e088f1f741ef",
    ),
    # ARCHIVED 2026-05-02 — filesystem SSOT (artifacts/adg/*.sqlite + violation JSON).
    "sc_ap_violation_backlog": (
        "0a3b8072-eabd-4516-9473-3c321bb011ff",
        "803834e1-0af8-4c3c-b45a-f513f80a7fef",
    ),
    # ARCHIVED 2026-05-02 — filesystem SSOT (root .mcp.json only).
    "mcp_registry": (
        "59693bbc-71b1-4c63-bc9f-b31eb8b08a0e",
        "e7b149b4-0496-4e98-a5dd-074dbe31881b",
    ),
    # ARCHIVED 2026-05-11 — 404 confirmed; filesystem SSOT (artifacts/adg/ ratchet files).
    "antipattern_burndown": (
        "80b30bc9-6622-4288-aa4c-6fc526b6a5c5",
        "4599fe37-8c24-4d89-96af-438b99a967c4",
    ),
}


def _find_ssot_yaml() -> Path | None:
    """Walk up from this file to the repo root holding config/notion_databases.yaml.

    Hooks run from arbitrary CWDs, so resolve relative to ``__file__`` rather than
    assuming ``parents[N]``. Returns None if not found (→ literal fallback).
    """
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "config" / "notion_databases.yaml"
        if candidate.is_file():
            return candidate
    return None


def _load_ssot() -> tuple[dict[str, object], dict[str, tuple[str, str]]]:
    """Return (api, {key: (database_id, data_source_id)}) from the YAML SSOT.

    Fail-soft: starts from the fallback literals and overrides with whatever the
    YAML provides. Any failure (missing PyYAML, unreadable/malformed file) leaves
    the fallbacks intact and never raises.
    """
    api: dict[str, object] = {
        "version": _FALLBACK_NOTION_API_VERSION,
        "base": _FALLBACK_NOTION_BASE,
        "http_timeout_s": _FALLBACK_NOTION_HTTP_TIMEOUT_S,
    }
    dbs: dict[str, tuple[str, str]] = dict(_FALLBACK_DB)

    path = _find_ssot_yaml()
    if path is None:
        return api, dbs

    try:
        import yaml  # noqa: PLC0415 — optional dep; absence falls back to literals

        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return api, dbs

        api_raw = raw.get("api")
        if isinstance(api_raw, dict):
            if api_raw.get("version"):
                api["version"] = str(api_raw["version"])
            if api_raw.get("base"):
                api["base"] = str(api_raw["base"])
            if api_raw.get("http_timeout_s") is not None:
                api["http_timeout_s"] = float(api_raw["http_timeout_s"])

        for row in raw.get("databases") or []:
            if not isinstance(row, dict):
                continue
            key = row.get("key")
            db_id = row.get("database_id")
            ds_id = row.get("id")
            if key and db_id and ds_id:
                dbs[str(key)] = (str(db_id), str(ds_id))

        return api, dbs
    except Exception:  # guardian: allow-broad-exception -- SSOT load is fail-soft; module MUST never fail to import (~76 governance consumers)
        return api, dbs


_API, _DB = _load_ssot()


# ============================================================================
# Notion API surface (SSOT: config/notion_databases.yaml -> api:)
# ============================================================================

NOTION_API_VERSION: Final[str] = str(_API["version"])
NOTION_BASE: Final[str] = str(_API["base"])
NOTION_POST_URL: Final[str] = f"{NOTION_BASE}/pages"
NOTION_HTTP_TIMEOUT_S: Final[float] = float(_API["http_timeout_s"])  # type: ignore[arg-type]


# ============================================================================
# Backlog Items DB (renamed from "Wave/Phase Convergence" 2026-04-23 W6).
# ============================================================================

BACKLOG_ITEMS_DB_ID: Final[str] = _DB["backlog_items"][0]
BACKLOG_ITEMS_DATA_SOURCE_ID: Final[str] = _DB["backlog_items"][1]
# Cross-session naming alias — a concurrent main migration used `_DS_ID`; keep both
# so all callers (either naming) resolve against this single SSOT.
BACKLOG_ITEMS_DS_ID: Final[str] = BACKLOG_ITEMS_DATA_SOURCE_ID

# Deprecated aliases — the DB was renamed "Wave/Phase Convergence" -> "Backlog
# Items" on 2026-04-23. The WAVE_PHASE_* names are kept because ~76 importers
# still reference them; they point at the SAME (Backlog Items) DB. Prefer the
# BACKLOG_ITEMS_* names in new code.
WAVE_PHASE_DB_ID: Final[str] = BACKLOG_ITEMS_DB_ID
WAVE_PHASE_DATA_SOURCE_ID: Final[str] = BACKLOG_ITEMS_DATA_SOURCE_ID


# ============================================================================
# Plans DB
# ============================================================================

PLANS_DB_ID: Final[str] = _DB["plans"][0]
PLANS_DATA_SOURCE_ID: Final[str] = _DB["plans"][1]


# ============================================================================
# Archived DBs — retained for reference only (filesystem/SQLite SSOT now).
# Do NOT write to these; see .claude/rules/notion-archived-databases.md.
# ============================================================================

# ADR Registry — ARCHIVED 2026-05-02 (filesystem SSOT: docs/architecture/adr/).
ADR_REGISTRY_DB_ID: Final[str] = _DB["adr_registry"][0]
ADR_REGISTRY_DS_ID: Final[str] = _DB["adr_registry"][1]

# Author-Gate Decision Ledger — ARCHIVED 2026-05-02 (SQLite SSOT, constitutional §30).
AUTHOR_GATE_LEDGER_DB_ID: Final[str] = _DB["author_gate_ledger"][0]
AUTHOR_GATE_LEDGER_DS_ID: Final[str] = _DB["author_gate_ledger"][1]

# SC/AP Violation Backlog — ARCHIVED 2026-05-02 (filesystem SSOT).
SCAP_BACKLOG_DB_ID: Final[str] = _DB["sc_ap_violation_backlog"][0]
SCAP_BACKLOG_DS_ID: Final[str] = _DB["sc_ap_violation_backlog"][1]

# MCP Registry — ARCHIVED 2026-05-02 (filesystem SSOT: root .mcp.json only).
MCP_REGISTRY_DB_ID: Final[str] = _DB["mcp_registry"][0]
MCP_REGISTRY_DS_ID: Final[str] = _DB["mcp_registry"][1]

# Anti-Pattern Burndown — ARCHIVED 2026-05-11 (404 confirmed; artifacts/adg/ ratchet files SSOT).
AP_BURNDOWN_DB_ID: Final[str] = _DB["antipattern_burndown"][0]
AP_BURNDOWN_DS_ID: Final[str] = _DB["antipattern_burndown"][1]


def query_url(data_source_id: str) -> str:
    """Return the Notion data-source query URL for a given data_source_id."""
    return f"{NOTION_BASE}/data_sources/{data_source_id}/query"


# Matches exactly 32 hex characters (Notion compact ID, no dashes).
_HEX32_RE = re.compile(r"([0-9a-f]{32})", re.IGNORECASE)

# Notion URL path pattern: slug-<32hex> (prioritised over bare hex match).
_PATH_ID_RE = re.compile(r"/[^/?#]+-([0-9a-f]{32})(?:[/?#]|$)", re.IGNORECASE)


def format_uuid(compact_id: str) -> str:
    """Format a 32-character compact hex ID into standard 8-4-4-4-12 UUID.

    Mirrors the Notion SDK's ``formatUuid`` in ``helpers.ts``.

    Args:
        compact_id: 32 hex chars, no dashes.

    Returns:
        Standard UUID string e.g. ``35727693-f55c-8118-95a8-d62d11d50c25``.

    Raises:
        ValueError: if ``compact_id`` is not exactly 32 hex characters.
    """
    s = compact_id.replace("-", "").lower()
    if not re.fullmatch(r"[0-9a-f]{32}", s):
        raise ValueError(f"Not a valid 32-char hex ID: {compact_id!r}")
    return f"{s[:8]}-{s[8:12]}-{s[12:16]}-{s[16:20]}-{s[20:]}"


def extract_page_id(url_or_id: str) -> str | None:
    """Extract and format a Notion page/database/block ID from any URL or raw ID.

    Mirrors the Notion SDK's ``extractPageId`` / ``extractDatabaseId`` in
    ``helpers.ts``:

    1. Try slug-path pattern first: ``/slug-name-<32hex>`` (avoids picking up
       view IDs from query params when the real ID is in the path).
    2. Fall back to any 32-char hex substring anywhere in the string.

    Args:
        url_or_id: A Notion URL, a compact 32-char hex string, or an already-
                   dashed UUID.

    Returns:
        Standard UUID string, or ``None`` if no 32-hex block found.
    """
    if url_or_id is None:
        return None
    trimmed = url_or_id.strip()

    path_match = _PATH_ID_RE.search(trimmed)
    if path_match:
        return format_uuid(path_match.group(1))

    any_match = _HEX32_RE.search(trimmed.replace("-", ""))
    if any_match:
        return format_uuid(any_match.group(1))

    return None


__all__ = [
    "NOTION_API_VERSION",
    "NOTION_BASE",
    "NOTION_POST_URL",
    "NOTION_HTTP_TIMEOUT_S",
    "BACKLOG_ITEMS_DB_ID",
    "BACKLOG_ITEMS_DATA_SOURCE_ID",
    "BACKLOG_ITEMS_DS_ID",
    "WAVE_PHASE_DB_ID",
    "WAVE_PHASE_DATA_SOURCE_ID",
    "PLANS_DB_ID",
    "PLANS_DATA_SOURCE_ID",
    "ADR_REGISTRY_DB_ID",
    "ADR_REGISTRY_DS_ID",
    "AUTHOR_GATE_LEDGER_DB_ID",
    "AUTHOR_GATE_LEDGER_DS_ID",
    "SCAP_BACKLOG_DB_ID",
    "SCAP_BACKLOG_DS_ID",
    "MCP_REGISTRY_DB_ID",
    "MCP_REGISTRY_DS_ID",
    "AP_BURNDOWN_DB_ID",
    "AP_BURNDOWN_DS_ID",
    "query_url",
    "format_uuid",
    "extract_page_id",
]
