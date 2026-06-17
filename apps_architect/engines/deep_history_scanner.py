"""Historical pattern archaeology — deep-time plan scanning.

Plan: ``.claude/plans/apps-architect-deferred-scope-b8e3f1.md`` DW3 DS-7.

Extends PlanPatternEngine to support configurable depth beyond 30 days,
including full-history scans and date-range filtering.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Tuple

from apps_architect.engines.plan_pattern_engine import PlanPatternEngine
from apps_architect.types.architect_types import Pattern

_log = logging.getLogger(__name__)


class DeepHistoryScanner:
    """Scans plan files across arbitrary date ranges for pattern archaeology."""

    def __init__(self, plans_dir: str | Path | None = None) -> None:
        self._engine = PlanPatternEngine(plans_dir)

    def scan_since(self, since_date: datetime) -> Tuple[Pattern, ...]:
        plan_files = sorted(
            self._engine._plans_dir.glob("*.md"),
            key=lambda p: p.stat().st_mtime, reverse=True,
        )
        patterns: list[Pattern] = []
        for fp in plan_files:
            mtime = datetime.fromtimestamp(fp.stat().st_mtime, tz=timezone.utc)
            if mtime >= since_date:
                patterns.extend(self._engine.extract_from_file(fp))
        return tuple(patterns)

    def scan_range(self, start: datetime, end: datetime) -> Tuple[Pattern, ...]:
        plan_files = sorted(
            self._engine._plans_dir.glob("*.md"),
            key=lambda p: p.stat().st_mtime, reverse=True,
        )
        patterns: list[Pattern] = []
        for fp in plan_files:
            mtime = datetime.fromtimestamp(fp.stat().st_mtime, tz=timezone.utc)
            if start <= mtime <= end:
                patterns.extend(self._engine.extract_from_file(fp))
        return tuple(patterns)

    def scan_all_time(self) -> Tuple[Pattern, ...]:
        plan_files = sorted(
            self._engine._plans_dir.glob("*.md"),
            key=lambda p: p.stat().st_mtime, reverse=True,
        )
        patterns: list[Pattern] = []
        for fp in plan_files:
            patterns.extend(self._engine.extract_from_file(fp))
        return tuple(patterns)

    def scan_last_n_days(self, days: int) -> Tuple[Pattern, ...]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        return self.scan_since(since)

    def scan_by_quarter(self, year: int, quarter: int) -> Tuple[Pattern, ...]:
        start_month = (quarter - 1) * 3 + 1
        start = datetime(year, start_month, 1, tzinfo=timezone.utc)
        if quarter == 4:
            end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end_month = start_month + 3
            end = datetime(year, end_month, 1, tzinfo=timezone.utc)
        return self.scan_range(start, end)


__all__ = ["DeepHistoryScanner"]
