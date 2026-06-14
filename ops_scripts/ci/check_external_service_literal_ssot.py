#!/usr/bin/env python3
"""Gate AUDIT-3 — external-service literal SSOT (source scan).

Detects hardcoded Notion API version / base URL and Notion database / data-source
IDs in ``*.py`` source OUTSIDE the SSOT allowlist.

History (2026-06-14, plan notion-id-ssot-consolidation Wave 4): this gate
previously queried the ADG ``violations`` table (``evidence LIKE '%pattern%'``).
That mechanism was inert — the ADG never records Notion-UUID literals as
violations, so every pattern matched 0 rows and the baseline stayed ``count: 0``;
the gate had never actually caught a hardcoded ID. It now scans source files
directly (no ADG dependency).

SSOT for the IDs: ``config/notion_databases.yaml`` via
``.claude/governance/scripts/_notion_constants.py`` — the canonical UUID set is
imported from there, so this gate auto-tracks ID changes.

Tier R (ratchet): fails only when the literal count exceeds the locked baseline
(``ops_scripts/ci/baselines/audit_external_service_literal_ssot.json``). Frozen
one-shot scripts that already embed IDs are baseline-locked; NEW hardcoded IDs
push the count over baseline and fail. Bypass: ``EXTERNAL_SERVICE_LITERAL_SSOT_BYPASS=1``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_DIR = REPO_ROOT / "ops_scripts" / "ci" / "baselines"
BASELINE_FILE = BASELINE_DIR / "audit_external_service_literal_ssot.json"
_GOV_SCRIPTS = REPO_ROOT / ".claude" / "governance" / "scripts"

# Non-UUID Notion API-surface literals. SSOT: _notion_constants.NOTION_API_VERSION / NOTION_BASE.
# Scoped to Notion (the audited drift). Provider-SDK base URLs (anthropic.com /
# openai.com) are a separate concern with many legitimate occurrences and are
# intentionally NOT scanned here to keep the ratchet signal meaningful.
LITERAL_PATTERNS = (
    "2025-09-03",  # Notion API version
    "api.notion.com",  # Notion endpoint
)

# Files that may legitimately contain these literals (SSOT modules + this gate's
# own fail-soft fallback set). Repo-relative, forward-slash.
SSOT_ALLOWLIST = (
    ".claude/governance/scripts/_notion_constants.py",
    "config/notion_databases.yaml",
    # Sanctioned pure-logic mirrors — these modules carry documented
    # "zero cross-imports / no I/O at import" contracts and intentionally embed
    # the IDs to stay import-free for early-hook safety. Exempt by design.
    ".claude/governance/scripts/_notion_plans_status_check.py",
    ".claude/governance/scripts/_plans_dup_detector.py",
    ".claude/governance/scripts/_notion_canonical.py",
    "apps_shared/config/environment_config.py",
    "agentic_core/L0_routing/config/path_constants.py",
    "agentic_core/L0_routing/config/external_apis_config.py",
    "ops_scripts/ci/check_external_service_literal_ssot.py",
    # SSOT consumers with a defensive `try: from _notion_constants ... except: <literal>`
    # import fallback — they already import from the SSOT; their literals are only a
    # fail-soft fallback, sanctioned like the SSOT module itself.
    "ops_scripts/ci/check_notion_backlog_no_duplicates.py",
    "ops_scripts/ci/check_notion_backlog_plan_linkage.py",
    "ops_scripts/ci/check_plan_done_notion_status.py",
)

# Path segments excluded from scanning (history / tests / generated / vendored).
_EXCLUDED_DIR_PARTS = frozenset(
    {
        ".git",
        "node_modules",
        "tests",
        "archives",
        "docs",
        "plans",
        "_archive",
        "apps_eval_legacy",
        ".chat-worktrees",
        "__pycache__",
        "_zero_loss_originals",
    }
)

_UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def notion_id_patterns() -> tuple[str, ...]:
    """Canonical Notion DB/DS UUID literals from the _notion_constants SSOT.

    Fail-soft: if the SSOT module cannot be imported, fall back to the
    most-copied Plans/Backlog IDs so the gate still enforces them.
    """
    if str(_GOV_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(_GOV_SCRIPTS))
    try:
        import _notion_constants as nc  # type: ignore[import-not-found]

        ids = {
            val
            for name in getattr(nc, "__all__", [])
            for val in (getattr(nc, name, None),)
            if isinstance(val, str) and _UUID_RE.fullmatch(val)
        }
        if ids:
            return tuple(sorted(ids))
    except Exception:  # guardian: allow-broad-exception -- gate fail-soft; SSOT import optional
        pass
    return (
        "ac53d31b-3068-4039-9ebe-856c12caab32",  # PLANS_DATA_SOURCE_ID
        "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9",  # PLANS_DB_ID
        "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7",  # BACKLOG_ITEMS_DATA_SOURCE_ID
        "aa8d2507-101e-4384-81d9-60ea3fe33876",  # BACKLOG_ITEMS_DB_ID
    )


@dataclass
class LiteralHit:
    file_path: str  # repo-relative, forward-slash
    line_no: int
    pattern: str
    evidence: str


def _is_allowlisted(rel: str) -> bool:
    return any(rel == ok or rel.endswith("/" + ok) for ok in SSOT_ALLOWLIST)


def _is_excluded(rel: str) -> bool:
    return any(seg in _EXCLUDED_DIR_PARTS for seg in rel.split("/"))


def _scan_file(py: Path, root: Path, patterns: tuple[str, ...]) -> list[LiteralHit]:
    """Return literal hits in a single file ([] if skipped/allowlisted/clean)."""
    rel = py.relative_to(root).as_posix()
    if _is_excluded(rel) or _is_allowlisted(rel):
        return []
    try:
        text = py.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    if not any(pat in text for pat in patterns):
        return []
    hits: list[LiteralHit] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for pat in patterns:
            if pat in line:
                hits.append(LiteralHit(rel, line_no, pat, line.strip()[:120]))
    return hits


def find_literal_violations(root: Path, patterns: tuple[str, ...]) -> list[LiteralHit]:
    """Scan ``*.py`` under ``root`` for any of ``patterns`` outside the SSOT
    allowlist / excluded dirs. Returns one hit per (file, line, pattern)."""
    hits: list[LiteralHit] = []
    for py in root.rglob("*.py"):
        hits.extend(_scan_file(py, root, patterns))
    return hits


class ExternalServiceLiteralSsotGate:
    """Tier-R source-scan ratchet for hardcoded external-service literals."""

    gate_id = "AUDIT_3_external_service_literal_ssot"
    tier = "R"
    baseline_filename = "audit_external_service_literal_ssot.json"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or REPO_ROOT

    def run(self, conn: object | None = None) -> list[LiteralHit]:
        """Scan source files. ``conn`` is accepted and ignored (back-compat)."""
        patterns = LITERAL_PATTERNS + notion_id_patterns()
        return find_literal_violations(self.root, patterns)

    def baseline_count(self) -> int:
        if not BASELINE_FILE.exists():
            return 0
        try:
            return int(json.loads(BASELINE_FILE.read_text(encoding="utf-8")).get("count", 0))
        except (json.JSONDecodeError, ValueError, OSError):
            return 0

    def seed_baseline(self, count: int) -> None:
        BASELINE_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "gate_id": self.gate_id,
            "count": count,
            "seeded_at": datetime.now(timezone.utc).isoformat(),
            "mechanism": "source_scan",
        }
        BASELINE_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AUDIT-3 external-service literal SSOT")
    parser.add_argument("--seed", action="store_true", help="lock current count as baseline")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    if os.getenv("EXTERNAL_SERVICE_LITERAL_SSOT_BYPASS") == "1" or os.getenv("WIRING_GATE_BYPASS") == "1":
        print("WARNING: AUDIT-3 bypassed")
        return 0

    gate = ExternalServiceLiteralSsotGate()
    hits = gate.run()

    if args.seed:
        gate.seed_baseline(len(hits))
        print(f"[{gate.gate_id}] baseline seeded: count={len(hits)} (mechanism=source_scan)")
        return 0

    baseline = gate.baseline_count()
    status = "fail" if len(hits) > baseline else "pass"
    if args.json:
        print(
            json.dumps(
                {
                    "gate_id": gate.gate_id,
                    "tier": gate.tier,
                    "status": status,
                    "count": len(hits),
                    "baseline": baseline,
                    "hits": [asdict(h) for h in hits[:50]],
                },
                indent=2,
            )
        )
    else:
        print(f"[{gate.gate_id}] tier=R status={status} count={len(hits)} baseline={baseline}")
        for h in hits[:50]:
            print(f"  - {h.file_path}:{h.line_no} :: {h.pattern} — {h.evidence}")
        if len(hits) > 50:
            print(f"  ... {len(hits) - 50} more")
        if status == "fail":
            print(
                "\nFix: import IDs from _notion_constants (SSOT) instead of hardcoding; "
                "or re-seed if this is an accepted frozen-script baseline change."
            )
    return 1 if status == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
