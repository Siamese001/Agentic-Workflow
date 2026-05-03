"""SSOT for NOTION API/database constants used by Cascade hooks and scripts.

All `.windsurf/scripts/*.py` and `tools/*.py` scripts that hit Notion's
REST API MUST import from this module instead of redefining literals.

Mirrored canonical IDs are in AGENTS.md (Notion Workspace Map).

Created: 2026-04-25 (audit-uncovered-gates plan, Wave 3).
Allowlisted as SSOT in `ops_scripts/ci/check_external_service_literal_ssot.py`.
"""

from __future__ import annotations

# Notion API surface
NOTION_API_VERSION: str = "2025-09-03"
NOTION_BASE: str = "https://api.notion.com/v1"
NOTION_POST_URL: str = f"{NOTION_BASE}/pages"
NOTION_HTTP_TIMEOUT_S: float = 15.0


# Wave/Phase Convergence DB
WAVE_PHASE_DB_ID: str = "aa8d2507-101e-4384-81d9-60ea3fe33876"
WAVE_PHASE_DATA_SOURCE_ID: str = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"


# Plans DB
PLANS_DB_ID: str = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"
PLANS_DATA_SOURCE_ID: str = "ac53d31b-3068-4039-9ebe-856c12caab32"


# ADR Registry DB
ADR_REGISTRY_DB_ID: str = "6ed25e12-bd92-4352-ac7a-3a971311f024"
ADR_REGISTRY_DS_ID: str = "e59d7640-dc09-48f9-8bdc-b0c94bf98c2a"


# Author-Gate Decision Ledger
AUTHOR_GATE_LEDGER_DB_ID: str = "18bb9145-1320-4191-8b14-6c309776bcf5"
AUTHOR_GATE_LEDGER_DS_ID: str = "5b60fdde-7259-491e-9f2d-e088f1f741ef"


# SC/AP Violation Backlog
SCAP_BACKLOG_DB_ID: str = "0a3b8072-eabd-4516-9473-3c321bb011ff"
SCAP_BACKLOG_DS_ID: str = "803834e1-0af8-4c3c-b45a-f513f80a7fef"


# MCP Registry
MCP_REGISTRY_DB_ID: str = "59693bbc-71b1-4c63-bc9f-b31eb8b08a0e"
MCP_REGISTRY_DS_ID: str = "e7b149b4-0496-4e98-a5dd-074dbe31881b"


# Anti-Pattern Burndown
AP_BURNDOWN_DB_ID: str = "80b30bc9-6622-4288-aa4c-6fc526b6a5c5"
AP_BURNDOWN_DS_ID: str = "4599fe37-8c24-4d89-96af-438b99a967c4"


def query_url(data_source_id: str) -> str:
    """Return the Notion data-source query URL for a given data_source_id."""
    return f"{NOTION_BASE}/data_sources/{data_source_id}/query"


__all__ = [
    "NOTION_API_VERSION",
    "NOTION_BASE",
    "NOTION_POST_URL",
    "NOTION_HTTP_TIMEOUT_S",
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
]
