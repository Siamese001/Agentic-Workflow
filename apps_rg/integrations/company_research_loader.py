"""HOP-0.6-COMPANY-RESEARCH — 4-mode CompanyBrief loader.

Mode priority (per locked decision D1):
  1. Manual upload at apps_rg/scripts/_interactive_brief.json (highest priority,
     written by the apps_rg interactive wizard or supplied via --manual-brief)
  2. Cross-app generation via apps_research (when --research-via apps_research)
  3. Internal CompanyBriefEngine invocation (when --auto-research-internal)
  4. Tavily supplement only (fills null + stale fields, never produces from scratch)

Default with no flags AND no brief on disk: raise CompanyBriefMissingError.

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P2.1).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from apps_rg.types.company_research import (
    CompanyBrief,
    CompanyBriefMissingError,
    CompanyBriefSource,
)

_log = logging.getLogger(__name__)

# Wizard-managed default — prior hand-authored apps_rg/scripts/company_research.json
# was deleted 2026-05-06 (W1 plan apps-rg-vllm-followup-blocked-c4e8b2). Wizard
# (apps_rg/__main__.py::_interactive_wizard) writes here when user supplies
# briefing inline; --manual-brief flag overrides.
_DEFAULT_MANUAL_PATH = Path("apps_rg/scripts/_interactive_brief.json")


@dataclass(frozen=True)
class CompanyResearchLoadOptions:
    target_company: Optional[str] = None
    research_via: Optional[str] = None  # "apps_research" | None
    auto_research_internal: bool = False
    auto_research_tavily: bool = False
    manual_path: Path = _DEFAULT_MANUAL_PATH
    jd_path: Optional[Path] = None
    depth: str = "standard"
    cache_max_age_days: int = 30


def load_company_brief(opts: CompanyResearchLoadOptions) -> CompanyBrief:
    """Resolve a CompanyBrief through the priority chain.

    Raises CompanyBriefMissingError if no valid brief can be produced.
    """
    # Mode 1 — manual upload.
    brief = _try_manual(opts.manual_path)
    if brief is not None:
        if opts.auto_research_tavily:
            brief = _try_tavily_supplement(brief)
        return _stamp_loaded(brief)

    if not opts.target_company:
        raise CompanyBriefMissingError(
            "No manual company brief at "
            f"{opts.manual_path} and no --target-company specified. "
            "Per locked decision D2: pipeline aborts. "
            "Provide a brief, pass --target-company with --research-via apps_research, "
            "or upload one at the manual path."
        )

    # Mode 2 — cross-app via apps_research.
    if opts.research_via == "apps_research":
        brief = _try_apps_research(opts)
        if brief is not None:
            if opts.auto_research_tavily:
                brief = _try_tavily_supplement(brief)
            return _stamp_loaded(brief)

    # Mode 3 — internal direct invocation of CompanyBriefEngine.
    if opts.auto_research_internal:
        brief = _try_internal_engine(opts)
        if brief is not None:
            if opts.auto_research_tavily:
                brief = _try_tavily_supplement(brief)
            return _stamp_loaded(brief)

    raise CompanyBriefMissingError(
        f"No company brief could be produced for {opts.target_company!r}. "
        "Per locked decision D2: fail loudly. "
        "Pass --research-via apps_research or --auto-research-internal, "
        "or supply a manual brief at apps_rg/scripts/_interactive_brief.json "
        "(the apps_rg interactive wizard writes there when run on a TTY)."
    )


# ----------------------------------------------------------------------- modes

def _try_manual(path: Path) -> Optional[CompanyBrief]:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _log.warning("[company_research_loader] Manual brief unreadable at %s: %s", path, exc)
        return None
    # Mark source as user_uploaded if not already explicit.
    data.setdefault("source", CompanyBriefSource.USER_UPLOADED.value)
    try:
        return CompanyBrief.model_validate(data)
    except Exception as exc:  # guardian: allow-broad-exception -- pydantic v1/v2 validators raise heterogeneous; surface as warning, fall through
        _log.error("[company_research_loader] Manual brief failed schema: %s", exc)
        return None


def _try_apps_research(opts: CompanyResearchLoadOptions) -> Optional[CompanyBrief]:
    try:
        from apps_shared.adapters.research_facade import fetch_company_brief
    except ImportError as exc:
        _log.warning("[company_research_loader] research_facade unavailable: %s", exc)
        return None
    try:
        return fetch_company_brief(
            company=opts.target_company or "",
            jd_path=opts.jd_path,
            depth=opts.depth,
            cache_max_age_days=opts.cache_max_age_days,
        )
    except CompanyBriefMissingError as exc:
        _log.warning("[company_research_loader] apps_research path failed: %s", exc)
        return None
    except Exception as exc:  # guardian: allow-broad-exception -- subprocess + LLM init paths raise heterogeneous; fall through to next mode
        _log.warning("[company_research_loader] apps_research path errored: %s", exc)
        return None


def _try_internal_engine(opts: CompanyResearchLoadOptions) -> Optional[CompanyBrief]:
    try:
        from apps_research.engines.company_brief_engine import CompanyBriefEngine
    except ImportError as exc:
        _log.warning("[company_research_loader] CompanyBriefEngine unavailable: %s", exc)
        return None
    try:
        engine = CompanyBriefEngine()
        data = engine.execute(
            {
                "topic": opts.target_company,
                "jd_anchor": opts.jd_path,
                "depth": opts.depth,
            }
        )
        return CompanyBrief.model_validate(data)
    except Exception as exc:  # guardian: allow-broad-exception -- engine path raises heterogeneous (LLM/HTTP/parse); upstream caller decides if missing brief is fatal
        _log.warning("[company_research_loader] internal engine path errored: %s", exc)
        return None


def _try_tavily_supplement(brief: CompanyBrief) -> CompanyBrief:
    try:
        from apps_rg.integrations.tavily_supplement import supplement_company_brief
    except ImportError:
        return brief
    try:
        return supplement_company_brief(brief)
    except Exception as exc:  # guardian: allow-broad-exception -- supplement is fail-soft per locked decision D3; never aborts pipeline
        _log.warning("[company_research_loader] Tavily supplement failed: %s", exc)
        return brief


def _stamp_loaded(brief: CompanyBrief) -> CompanyBrief:
    if brief.is_stale(now=datetime.now(timezone.utc)):
        _log.warning(
            "[company_research_loader] Loaded brief for %s is stale (fetched_at=%s, ttl=%sd)",
            brief.company,
            brief.fetched_at,
            brief.freshness_ttl_days,
        )
    return brief


__all__ = [
    "CompanyResearchLoadOptions",
    "load_company_brief",
]
