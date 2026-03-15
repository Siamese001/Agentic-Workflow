"""
adg_behavioral_mixin.py — ADG Behavioral Signal Mixin (Phase 0)

Provides lazy-loaded ADG behavioral profile properties to any agent that
inherits from SovereignBaseAgent (via MRO injection in Phase 4).

Design constraints:
  - ZERO dependencies on agentic_core internals — imports only from
    agentic_core.adg.runtime.behavioral_index (stdlib-only, safe from any layer)
  - All properties are @cached_property — loaded once per instance, zero cost
    when ADG SQLite is absent (graceful neutral fallback)
  - No __init__ side effects — purely additive
  - Thread-safety: each instance owns its own profile cache via cached_property

Signal reference (from behavioral_index.py):
  behavioral_score > 0.7  → agent-like
  behavioral_score < 0.4  → script-like
  0.4–0.7               → mixed/unknown (default: 0.5)
"""

from __future__ import annotations

import logging
from functools import cached_property
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)


class ADGBehavioralMixin:
    """
    Mixin that exposes ADG behavioral profile as lazy cached properties.

    Consumed by:
      - HealingPolicyMixin.heal_repository() — confidence adjustment (Phase 3a)
      - SelfDiagnosisMixin.self_diagnose()  — antipattern fold (Phase 3b)
      - All agents inheriting SovereignBaseAgent after Phase 4 root injection

    Usage (once injected via SovereignBaseAgent):
        if self.adg_is_agent_like:
            confidence -= 0.05
        for signal in self.adg_antipattern_signals:
            report["adg_antipatterns"].append(signal)
    """

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _adg_resolved_self_path(self) -> str | None:
        """Return repo-relative path for this agent's source file, or None."""
        try:
            import inspect

            src = inspect.getfile(type(self))
            project_root = getattr(self, "project_root", None)
            if project_root is None:
                return None
            rel = Path(src).resolve().relative_to(Path(project_root).resolve())
            return rel.as_posix()
        except Exception:
            return None

    def _adg_load_profile(self) -> Any:
        """Load ADGBehavioralIndex profile for this agent's own source file.

        Returns a BehavioralProfile (or neutral fallback) — never raises.
        """
        try:
            from agentic_core.adg.runtime.behavioral_index import ADGBehavioralIndex

            project_root = getattr(self, "project_root", None)
            if project_root is None:
                return None

            idx = ADGBehavioralIndex.from_latest(Path(project_root))
            if idx is None:
                return None

            resolved = self._adg_resolved_self_path()
            if resolved is None:
                return None

            return idx.profile_for(resolved)
        except Exception as exc:
            logger.debug("[ADGBehavioralMixin] Profile load failed: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Public cached properties
    # ------------------------------------------------------------------

    @cached_property
    def adg_profile_available(self) -> bool:
        """True when ADG SQLite artifact is present and profile was loaded."""
        return self._adg_load_profile() is not None

    @cached_property
    def adg_behavioral_score(self) -> float:
        """Behavioral score [0.0–1.0]. >0.7 agent-like, <0.4 script-like. Default 0.5."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ADGBehavioralMixin.adg_behavioral_score")

        profile = self._adg_load_profile()
        return profile.behavioral_score if profile is not None else 0.5

    @cached_property
    def adg_is_agent_like(self) -> bool:
        """True when behavioral_score > 0.7 (strong agent-side evidence)."""
        return self.adg_behavioral_score > 0.7

    @cached_property
    def adg_is_script_like(self) -> bool:
        """True when file has ≥1 script signal and 0 agent signals (deterministic_coverage)."""
        profile = self._adg_load_profile()
        if profile is None:
            return False
        return profile.deterministic_coverage or profile.behavioral_score < 0.4

    @cached_property
    def adg_antipattern_signals(self) -> list[str]:
        """ADG-confirmed antipattern symbols for this agent's source file."""
        profile = self._adg_load_profile()
        if profile is None:
            return []
        return sorted(profile.antipattern_signals)

    @cached_property
    def adg_agent_signals(self) -> list[str]:
        """ADG-confirmed agent-side edge types present on this file."""
        profile = self._adg_load_profile()
        if profile is None:
            return []
        return sorted(profile.agent_signals)

    @cached_property
    def adg_script_signals(self) -> list[str]:
        """ADG-confirmed script-side edge types present on this file."""
        profile = self._adg_load_profile()
        if profile is None:
            return []
        return sorted(profile.script_signals)

    @cached_property
    def adg_dead_import_count(self) -> int:
        """Count of ADG-confirmed dead imports for this agent's source file.

        Queried directly via SQLite (not in BehavioralProfile — added here).
        Returns 0 when ADG is unavailable.
        """
        try:
            from agentic_core.adg.runtime.behavioral_index import ADGBehavioralIndex

            project_root = getattr(self, "project_root", None)
            if project_root is None:
                return 0

            idx = ADGBehavioralIndex.from_latest(Path(project_root))
            if idx is None or not idx._connect():
                return 0

            resolved = self._adg_resolved_self_path()
            if resolved is None:
                return 0

            assert idx._con is not None
            cur = idx._con.execute(
                """
                SELECT COUNT(*) FROM edges e
                JOIN nodes n ON n.id = e.src_id
                WHERE e.relation_type = 'dead_imports'
                  AND n.resolved_path = ?
                  AND n.entity_type = 'module'
                """,
                (resolved,),
            )
            row = cur.fetchone()
            return int(row[0]) if row else 0
        except Exception as exc:
            logger.debug("[ADGBehavioralMixin] dead_import_count query failed: %s", exc)
            return 0

    def adg_behavioral_summary(self) -> dict:
        """Return a structured summary of this agent's ADG behavioral profile.

        Useful for audit trails and self-diagnosis reports.
        """
        return {
            "adg_profile_available": self.adg_profile_available,
            "adg_behavioral_score": self.adg_behavioral_score,
            "adg_is_agent_like": self.adg_is_agent_like,
            "adg_is_script_like": self.adg_is_script_like,
            "adg_antipattern_signals": self.adg_antipattern_signals,
            "adg_agent_signals": self.adg_agent_signals,
            "adg_script_signals": self.adg_script_signals,
            "adg_dead_import_count": self.adg_dead_import_count,
        }
