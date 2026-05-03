"""Cross-app facade — apps_rg → apps_research company-brief invocation.

Provides a synchronous `fetch_company_brief()` entrypoint that:
1. Returns a recent cached CompanyBrief if one exists within cache_max_age_days.
2. Otherwise invokes `python -m apps_research --mode company` and parses the
   produced artifact under `artifacts/apps_research/runs/<ts>/`.

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P2.2).
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_log = logging.getLogger(__name__)

_DEFAULT_CACHE_ROOT = Path("artifacts/apps_research/runs")


def fetch_company_brief(
    *,
    company: str,
    jd_path: Optional[Path] = None,
    depth: str = "standard",
    cache_max_age_days: int = 30,
    cache_root: Optional[Path] = None,
):
    """Synchronous invocation of apps_research --mode company.

    Returns a validated CompanyBrief (apps_rg.types.company_research.CompanyBrief)
    or raises CompanyBriefMissingError.
    """
    from apps_rg.types.company_research import CompanyBrief, CompanyBriefMissingError

    cache_root = cache_root or _DEFAULT_CACHE_ROOT
    cached = _find_cached_brief(
        company=company, cache_root=cache_root, max_age_days=cache_max_age_days
    )
    if cached is not None:
        return cached

    artifact_path = _invoke_apps_research(
        company=company, jd_path=jd_path, depth=depth, cache_root=cache_root
    )
    if artifact_path is None or not artifact_path.exists():
        raise CompanyBriefMissingError(
            f"apps_research did not produce a company brief for {company!r}; "
            "check apps_research logs and rerun"
        )

    try:
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
        return CompanyBrief.model_validate(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise CompanyBriefMissingError(
            f"apps_research produced an unreadable brief at {artifact_path}: {exc}"
        ) from exc


def _find_cached_brief(
    *, company: str, cache_root: Path, max_age_days: int
):
    """Look for a recent company_research.json under cache_root for this company."""
    from apps_rg.types.company_research import CompanyBrief

    if not cache_root.exists():
        return None
    candidates = sorted(
        cache_root.glob("*/company_research.json"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    for candidate in candidates:
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if str(data.get("company", "")).strip().lower() != company.strip().lower():
            continue
        try:
            brief = CompanyBrief.model_validate(data)
        except Exception:  # guardian: allow-broad-exception -- pydantic v1/v2 validators raise heterogeneous; one bad cache entry must not block lookup
            continue
        if brief.is_stale(now=datetime.now(timezone.utc)):
            continue
        # Honor the caller's stricter cache_max_age_days override.
        age_days = (
            datetime.now(timezone.utc)
            - (
                brief.fetched_at
                if brief.fetched_at.tzinfo
                else brief.fetched_at.replace(tzinfo=timezone.utc)
            )
        ).total_seconds() / 86400.0
        if age_days <= max_age_days:
            _log.info("[research_facade] Using cached company brief: %s", candidate)
            return brief
    return None


def _invoke_apps_research(
    *, company: str, jd_path: Optional[Path], depth: str, cache_root: Path
) -> Optional[Path]:
    out_dir = cache_root.parent  # apps_research output_dir is the parent of "runs/"
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "apps_research",
        "--topic",
        company,
        "--mode",
        "company",
        "--depth",
        depth,
        "--out",
        str(out_dir),
    ]
    if jd_path:
        cmd.extend(["--jd-anchor", str(jd_path)])

    _log.info("[research_facade] Invoking: %s", " ".join(cmd))
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        _log.error("[research_facade] apps_research timed out after 300s")
        return None
    except OSError as exc:
        _log.error("[research_facade] apps_research subprocess failed: %s", exc)
        return None

    if completed.returncode != 0:
        _log.error(
            "[research_facade] apps_research exit=%s\nstderr=%s",
            completed.returncode,
            completed.stderr,
        )
        return None

    # The newly produced run is the most recent runs/<ts>/company_research.json.
    runs_dir = out_dir / "runs"
    if not runs_dir.exists():
        return None
    latest = sorted(
        runs_dir.glob("*/company_research.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return latest[0] if latest else None


def lookup_cached_brief(company: str, tenant_id: str = "default") -> Optional[dict]:
    """Lookup a cached company brief without invoking apps_research.

    This is used by the L0 prerequisite validator to check if a valid
    historical briefing exists before routing to apps_research.

    Returns the brief as a dict if found and fresh, None otherwise.
    """
    cache_root = _DEFAULT_CACHE_ROOT
    if not cache_root.exists():
        return None

    # Find matching brief
    candidates = sorted(
        cache_root.glob("*/company_research.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    for candidate in candidates:
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        # Check company match
        if str(data.get("company", "")).strip().lower() != company.strip().lower():
            continue

        # Check if fresh (not stale)
        from apps_rg.types.company_research import CompanyBrief

        try:
            brief = CompanyBrief.model_validate(data)
            if brief.is_stale(now=datetime.now(timezone.utc)):
                continue
            return data  # Return as dict for the validator
        except Exception:
            continue

    return None


__all__ = ["fetch_company_brief", "lookup_cached_brief"]
