"""L5 source-register policy gate — Wave 3 phase 3.4.

Promotes the historical LINT-2 advisory ("every claim should have a
SRC- citation") to a true L5 safety-plane gate that can BLOCK pack
emission when claims-without-citations exceed a configurable budget.

Architecture
------------
The gate runs on a built pack directory (post-render). It:
  1. Walks each emitted card markdown.
  2. Identifies claim-shaped lines (sentences containing numbers,
     dollar amounts, percentages, or strong assertion words).
  3. Counts how many claims have an inline SRC- reference vs. none.
  4. Returns a verdict (block / warn / clean) based on thresholds.

Constitutional alignment
------------------------
- §3 anti-bypass: gate runs in the validation phase that the builder
  emits via the OTEL span; bypass via ``APPS_QNA_SOURCE_GATE_BYPASS=1``
  is logged but allowed (matches sibling guardian-exemption rules).
- §29 closed-loop: each gate run emits one ``event_kind="pack_lint"``
  ledger row with the claim counts so calibration can tune thresholds.

Threshold semantics
-------------------
- ``coverage`` = (claims_with_citation) / max(1, total_claims)
- ``BLOCK`` when ``coverage < 0.30 AND total_claims >= 10`` — pack has
  many uncited claims; treat as a real failure
- ``WARN`` when ``coverage < 0.60 AND total_claims >= 5`` — gap exists
  but pack has enough cited content to be paste-ready
- ``CLEAN`` otherwise
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from apps_qna.integrations.spine_adapter import emit_pack_lifecycle_event

_log = logging.getLogger(__name__)

_BYPASS_ENV: str = "APPS_QNA_SOURCE_GATE_BYPASS"

# Heuristic: a "claim" is a line that contains a numeric anchor (number,
# %, $, M, B, K) OR a strong assertion verb. We INTENTIONALLY don't try
# to detect every claim — false negatives are fine; false positives
# would create spurious lint failures. The point is to catch the
# load-bearing factual assertions.
_CLAIM_NUMERIC_RE = re.compile(
    r"\$?\d[\d,]*(?:\.\d+)?\s*(?:%|x|M|B|K|MM|million|billion|thousand)?",
    re.IGNORECASE,
)
_CLAIM_ASSERTION_VERBS: frozenset[str] = frozenset(
    {
        "delivered", "achieved", "generated", "scaled", "led",
        "built", "shipped", "reduced", "expanded", "compressed",
        "won", "secured", "produced", "drove", "captured",
    }
)
# An inline SRC reference matches `[SRC-...]` or `(SRC-...)` or bare `SRC-...`.
_SRC_REF_RE = re.compile(r"\bSRC-[\w-]+\b")

# Sections that are GENERIC PROSE (purpose, navigation, instructions) and
# don't need citations even if they contain numbers — exclude them by
# matching specific heading prefixes commonly emitted by the templates.
_NON_CLAIM_HEADING_PREFIXES: tuple[str, ...] = (
    "## Purpose",
    "## Routing manifest",
    "## How to use",
    "## When to invoke",
    "## Tuning rules",
    "## Story-selection rules",
    "## Realism gate",
    "## Answer shape",
    "## Always-on",
    "## Live mode",
    "## Citation discipline",
    "## Paste rules",
)


@dataclass
class ClaimAudit:
    """Per-card claim/citation audit."""

    card_filename: str
    total_claims: int = 0
    cited_claims: int = 0
    uncited_examples: list[str] = field(default_factory=list)
    """Up to 3 example sentences that look like claims but lack SRC- refs."""


@dataclass
class GateVerdict:
    """Top-level verdict for the policy gate."""

    status: str
    """One of ``CLEAN`` / ``WARN`` / ``BLOCK`` / ``BYPASSED``."""

    total_claims: int
    cited_claims: int
    coverage: float
    per_card: list[ClaimAudit]
    reason: str = ""

    @property
    def should_block(self) -> bool:
        return self.status == "BLOCK"


def _is_claim_line(line: str) -> bool:
    """Heuristic: does this line carry a load-bearing factual assertion?"""
    stripped = line.strip()
    if not stripped or len(stripped) < 20:
        return False
    if stripped.startswith(("#", ">", "```", "|", "-", "*", "+")):
        # Headings, blockquotes, code fences, table rows, list markers
        # excluded — claims live in prose lines.
        if not stripped.startswith(("- ", "* ", "+ ")):
            return False
    if _CLAIM_NUMERIC_RE.search(stripped):
        # Numeric claims: $22M, 99.9%, 8 to 28, etc.
        return True
    lower = stripped.lower()
    for verb in _CLAIM_ASSERTION_VERBS:
        # Word-boundary verb check.
        if re.search(rf"\b{verb}\b", lower):
            return True
    return False


def _strip_non_claim_sections(text: str) -> list[tuple[str, str]]:
    """Return [(section_heading, body)] excluding non-claim sections."""
    # Split by markdown ## headings.
    parts = re.split(r"(?m)^(## .+)$", text)
    sections: list[tuple[str, str]] = []
    if parts and parts[0].strip():
        sections.append(("(preamble)", parts[0]))
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        if any(heading.startswith(prefix) for prefix in _NON_CLAIM_HEADING_PREFIXES):
            continue
        sections.append((heading, body))
    return sections


def audit_card_claims(card_path: Path) -> ClaimAudit:
    """Audit a single card markdown file for claims and citations."""
    audit = ClaimAudit(card_filename=card_path.name)
    if not card_path.is_file():
        return audit
    try:
        text = card_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return audit
    for _heading, body in _strip_non_claim_sections(text):
        for line in body.splitlines():
            if not _is_claim_line(line):
                continue
            audit.total_claims += 1
            if _SRC_REF_RE.search(line):
                audit.cited_claims += 1
            elif len(audit.uncited_examples) < 3:
                # Trim to keep ledger metadata bounded.
                audit.uncited_examples.append(line.strip()[:160])
    return audit


def evaluate_pack(pack_dir: Path) -> GateVerdict:
    """Run the source-register gate against an emitted pack directory."""
    if os.environ.get(_BYPASS_ENV, "").strip() in {"1", "true", "TRUE", "yes"}:
        _log.warning(
            "source-register gate BYPASSED via %s=1 — pack emitted without "
            "citation enforcement",
            _BYPASS_ENV,
        )
        return GateVerdict(
            status="BYPASSED",
            total_claims=0,
            cited_claims=0,
            coverage=1.0,
            per_card=[],
            reason=f"Bypass env var {_BYPASS_ENV} active",
        )

    if not pack_dir.is_dir():
        return GateVerdict(
            status="CLEAN",
            total_claims=0,
            cited_claims=0,
            coverage=1.0,
            per_card=[],
            reason="No pack directory to audit",
        )

    audits = [
        audit_card_claims(card)
        for card in sorted(pack_dir.glob("*.md"))
    ]
    total = sum(a.total_claims for a in audits)
    cited = sum(a.cited_claims for a in audits)
    coverage = (cited / total) if total > 0 else 1.0

    if coverage < 0.30 and total >= 10:
        status = "BLOCK"
        reason = (
            f"Citation coverage {coverage:.1%} on {total} claims is below "
            f"the 30% block threshold."
        )
    elif coverage < 0.60 and total >= 5:
        status = "WARN"
        reason = (
            f"Citation coverage {coverage:.1%} on {total} claims is below "
            f"the 60% warn threshold."
        )
    else:
        status = "CLEAN"
        reason = (
            f"Citation coverage {coverage:.1%} on {total} claims meets "
            "thresholds."
        )

    verdict = GateVerdict(
        status=status,
        total_claims=total,
        cited_claims=cited,
        coverage=coverage,
        per_card=audits,
        reason=reason,
    )

    # Constitutional §29: emit pack_lint ledger row capturing the verdict.
    emit_pack_lifecycle_event(
        event_kind="pack_lint",
        prediction={
            "gate": "source_register",
            "pack_dir": str(pack_dir),
            "claim_threshold_block_pct": 30,
            "claim_threshold_warn_pct": 60,
        },
        outcome={
            "status": status,
            "total_claims": total,
            "cited_claims": cited,
            "coverage_pct": round(coverage * 100, 1),
            "per_card_uncited_examples": [
                {"card": a.card_filename, "examples": a.uncited_examples}
                for a in audits
                if a.uncited_examples
            ],
        },
        score_band=(
            "clean" if status == "CLEAN" else "lint_failed"
        ),
        repo_area=str(pack_dir),
    )

    return verdict


def format_verdict_for_cli(verdict: GateVerdict) -> str:
    """Human-readable verdict block for the CLI."""
    lines = [
        f"Source-register gate: {verdict.status}",
        f"  total claims:    {verdict.total_claims}",
        f"  cited claims:    {verdict.cited_claims}",
        f"  coverage:        {verdict.coverage:.1%}",
        f"  reason:          {verdict.reason}",
    ]
    if verdict.status in {"WARN", "BLOCK"}:
        lines.append("  uncited examples:")
        for audit in verdict.per_card:
            if audit.uncited_examples:
                lines.append(f"    [{audit.card_filename}]")
                for ex in audit.uncited_examples:
                    lines.append(f"      - {ex}")
    return "\n".join(lines)


__all__ = [
    "ClaimAudit",
    "GateVerdict",
    "audit_card_claims",
    "evaluate_pack",
    "format_verdict_for_cli",
]
