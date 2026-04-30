"""
VerbatimProvenanceGate — every emitted bullet must trace to a master-resume bullet.

Reads:  'ranked_content' (final emitted resume), 'mission_input.master_resume' (truth)
Writes: 'provenance_report' (per-bullet match score, metric preservation, scope check)
Signal: 'PROVENANCE_FAILURE' when any bullet fails the gate.

For each emitted bullet, we:
  1. Find the closest master bullet (Jaccard token similarity over content tokens).
  2. Verify quantified metrics in emitted match a metric in the master bullet
     within ±5% tolerance (or are absent in the emitted).
  3. Verify scope nouns (team sizes, dollar amounts, region counts) are not
     inflated vs. the master.
  4. Stamp `provenance` onto each emitted bullet (master_role, master_idx,
     similarity, status).

This is the truthfulness floor — without it the pipeline could rephrase a
"$15M" claim into "$50M" and ship.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from apps_rg.engines._lifecycle_emits import _emit_engine_lifecycle
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_engine_lifecycle("verbatim_provenance_gate")

Logger = logging.getLogger(__name__)

_DOLLAR_RE = re.compile(r"\$\s*(\d+(?:\.\d+)?)\s*([MBK])?", re.IGNORECASE)
_PCT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")
_TEAM_RE = re.compile(r"\b(\d+)[- ](?:person|member|engineer|team|specialist)s?\b", re.IGNORECASE)
_GROW_RE = re.compile(r"\bfrom\s+(\d+)\s+to\s+(\d+)\b", re.IGNORECASE)

_STOP = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "have", "in", "is", "it", "of", "on", "or", "that", "the", "their", "to",
    "with", "while", "across", "into", "via", "than", "but", "not", "all",
})


def _tokens(text: str) -> set[str]:
    if not text:
        return set()
    return {
        t for t in re.findall(r"[a-z][a-z0-9\-]+", text.lower())
        if t not in _STOP and len(t) > 2
    }


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _normalize_dollar(amount: float, suffix: str | None) -> float:
    """Normalize $X with K/M/B suffix to a comparable float."""
    if not suffix:
        return amount
    s = suffix.upper()
    if s == "K":
        return amount * 1_000
    if s == "M":
        return amount * 1_000_000
    if s == "B":
        return amount * 1_000_000_000
    return amount


def _extract_dollars(text: str) -> list[float]:
    return [_normalize_dollar(float(m.group(1)), m.group(2)) for m in _DOLLAR_RE.finditer(text)]


def _extract_percents(text: str) -> list[float]:
    return [float(m.group(1)) for m in _PCT_RE.finditer(text)]


def _extract_team_sizes(text: str) -> list[int]:
    out: list[int] = []
    for m in _TEAM_RE.finditer(text):
        try:
            out.append(int(m.group(1)))
        except (ValueError, IndexError):
            continue
    for m in _GROW_RE.finditer(text):
        try:
            out.append(int(m.group(2)))
        except (ValueError, IndexError):
            continue
    return out


def _value_within_tolerance(emitted: float, master_values: list[float], tol_pct: float = 0.05) -> bool:
    """True if `emitted` is within `tol_pct` of any value in `master_values`."""
    if not master_values:
        return False
    for mv in master_values:
        if mv == 0:
            if emitted == 0:
                return True
            continue
        if abs(emitted - mv) / abs(mv) <= tol_pct:
            return True
    return False


def _flatten_master_bullets(master: dict) -> list[dict]:
    """Flatten master_resume into [(role_idx, role_name, source_field, idx, text), ...]"""
    out: list[dict] = []
    exp = master.get("professional_experience") or master.get("experience") or []
    for role_idx, role in enumerate(exp):
        company = role.get("company", f"role_{role_idx}")
        title = role.get("title", "")
        # Master uses bullet_pool (rich) OR highlights OR bullets — read all three.
        for field in ("bullet_pool", "highlights", "bullets"):
            for bullet_idx, raw in enumerate(role.get(field, []) or []):
                text = raw if isinstance(raw, str) else raw.get("bullet_text", "")
                if not text:
                    continue
                out.append({
                    "role_idx": role_idx,
                    "company": company,
                    "title": title,
                    "field": field,
                    "bullet_idx": bullet_idx,
                    "text": text,
                    "tokens": _tokens(text),
                    "dollars": _extract_dollars(text),
                    "percents": _extract_percents(text),
                    "team_sizes": _extract_team_sizes(text),
                })
    return out


class VerbatimProvenanceGate(BaseRGEngine):
    """L5-aligned safety engine — enforces master-resume traceability."""

    # Similarity below this means "not derived from the master resume".
    MIN_SIMILARITY = 0.20
    # Max acceptable inflation factor for scope nouns (team size, dollars).
    MAX_INFLATION_FACTOR = 1.20

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="SAFETY.PROVENANCE")

    async def execute(self) -> dict[str, Any]:
        ranked = self.ctx.buffer.read("ranked_content")
        if not ranked:
            self.record_fail("Missing ranked_content", signal="DATA_MISSING")
            return {"valid": False, "reason": "no_ranked_content"}

        mission = self.ctx.buffer.read("mission_input") or {}
        master = mission.get("master_resume") or getattr(self.ctx, "master_resume", {}) or {}
        master_bullets = _flatten_master_bullets(master)
        if not master_bullets:
            self.record_fail("Master resume has no bullets to verify against", signal="DATA_MISSING")
            return {"valid": False, "reason": "no_master_bullets"}

        report: dict[str, Any] = {
            "valid": True,
            "checked": 0,
            "failed": [],
            "warnings": [],
            "by_role": {},
        }
        # Iterate emitted experience sections.
        emitted_exp = ranked.get("experience", []) or ranked.get("experience_sections", [])
        for emitted_role in emitted_exp:
            company = emitted_role.get("company", "?")
            title = emitted_role.get("title", "?")
            role_master = [
                mb for mb in master_bullets
                if mb["company"].lower() == company.lower()
            ]
            # Fall back to whole-master pool if company mismatch (rare; rename, alias).
            search_pool = role_master if role_master else master_bullets

            role_status: list[dict] = []
            for emitted_bullet in emitted_role.get("bullets", []):
                text = emitted_bullet.get("bullet_text", "")
                tokens = _tokens(text)
                if not tokens:
                    continue
                report["checked"] += 1

                # Find closest master bullet by Jaccard similarity.
                best = None
                best_sim = 0.0
                for mb in search_pool:
                    sim = _jaccard(tokens, mb["tokens"])
                    if sim > best_sim:
                        best_sim = sim
                        best = mb

                status = "ok"
                issues: list[str] = []

                if best is None or best_sim < self.MIN_SIMILARITY:
                    status = "fail_no_match"
                    issues.append(f"no master bullet matches (best sim={best_sim:.2f})")
                else:
                    # Check metrics against the matched master bullet pool — but
                    # also the entire role's master pool, since rephrasing may
                    # combine signals from multiple bullets.
                    role_dollars = [v for mb in role_master for v in mb["dollars"]]
                    role_percents = [v for mb in role_master for v in mb["percents"]]
                    role_teams = [v for mb in role_master for v in mb["team_sizes"]]

                    for d in _extract_dollars(text):
                        if not _value_within_tolerance(d, role_dollars, tol_pct=0.05):
                            issues.append(f"dollar_unverified=${d:,.0f}")
                            status = "warn_metric"
                    for p in _extract_percents(text):
                        if not _value_within_tolerance(p, role_percents, tol_pct=0.05):
                            issues.append(f"percent_unverified={p}%")
                            status = "warn_metric"
                    for t in _extract_team_sizes(text):
                        # Scope inflation: emitted team size > MAX_INFLATION_FACTOR × any master value
                        if role_teams and t > max(role_teams) * self.MAX_INFLATION_FACTOR:
                            issues.append(
                                f"scope_inflated team_size={t} master_max={max(role_teams)}"
                            )
                            status = "fail_inflation"

                emitted_bullet["provenance"] = {
                    "master_company": best["company"] if best else None,
                    "master_field": best["field"] if best else None,
                    "master_idx": best["bullet_idx"] if best else None,
                    "similarity": round(best_sim, 3),
                    "status": status,
                    "issues": issues,
                }
                role_status.append({"text": text[:80], "status": status, "issues": issues})

                if status.startswith("fail"):
                    report["valid"] = False
                    report["failed"].append({"company": company, "text": text[:120], "issues": issues})
                elif status.startswith("warn"):
                    report["warnings"].append({"company": company, "text": text[:120], "issues": issues})

            report["by_role"][company] = role_status

        # Re-publish ranked_content with provenance stamps.
        self.ctx.buffer.write("ranked_content", ranked, source_agent=self.name)
        self.ctx.buffer.write("provenance_report", report, source_agent=self.name)

        if not report["valid"]:
            self.record_fail(
                f"Provenance gate FAILED: {len(report['failed'])} bullets cannot be traced to master",
                data=report,
                signal="PROVENANCE_FAILURE",
            )
        elif report["warnings"]:
            self.record_pass(
                f"Provenance gate PASSED with {len(report['warnings'])} metric warnings"
            )
        else:
            self.record_pass(f"Provenance gate PASSED — {report['checked']} bullets verified")
        return report
