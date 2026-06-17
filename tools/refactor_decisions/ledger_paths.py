"""Canonical paths for the Author-Gate refactor decision ledger (W2 SSOT).

Writable SSOT: ``.claude/state/refactor_decisions/refactor_decision_ledger.sqlite``.

``.claude/state/...`` is a **legacy mirror** surface only (drift checks, one-way
migration). New code must not treat the legacy editor path as an alternate writer target.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# --- Canonical (legacy editor) — all writers should use this ---
REFACTOR_DECISIONS_DIR_SSO = REPO_ROOT / ".claude" / "state" / "refactor_decisions"
REFACTOR_DECISION_LEDGER_DB = REFACTOR_DECISIONS_DIR_SSO / "refactor_decision_ledger.sqlite"

# Aliases
LEDGER_DB_PATH = REFACTOR_DECISION_LEDGER_DB

# --- Legacy mirror (legacy editor) — migration / drift / parity tools only ---
REFACTOR_DECISIONS_DIR_WINDSURF_LEGACY = REPO_ROOT / ".claude" / "state" / "refactor_decisions"
REFACTOR_DECISION_LEDGER_DB_WINDSURF_LEGACY = (
    REFACTOR_DECISIONS_DIR_WINDSURF_LEGACY / "refactor_decision_ledger.sqlite"
)

LEGACY_MIRROR_LEDGER_DB_PATH = REFACTOR_DECISION_LEDGER_DB_WINDSURF_LEGACY
