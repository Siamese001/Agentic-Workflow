"""
Synthesis Engine Service — apps_research

Synthesizes insights from multiple sources into coherent findings.
Aligned with apps_lic service pattern with lifecycle trace integration.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
    _emit_routes_to_capability,
    _emit_snapshots_state,
    _emit_stores_embedding,
)

_log = logging.getLogger(__name__)


class SynthesisEngineService:
    """Service for synthesizing research findings."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the synthesis engine service."""
        self.config = config or {}
        self._synthesized_findings: list[dict[str, Any]] = []
        _emit_snapshots_state("p0", "synthesis_engine", "init")

    def synthesize_findings(
        self,
        insights: list[dict[str, Any]],
        synthesis_mode: str = "thematic",
        target_audience: str = "technical",
    ) -> dict[str, Any]:
        """Synthesize multiple insights into coherent findings.

        Args:
            insights: List of extracted insights
            synthesis_mode: Synthesis approach (thematic, chronological, comparative)
            target_audience: Target audience for synthesis

        Returns:
            Synthesized findings with metadata
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "SynthesisEngineService.synthesize_findings",
        )
        _emit_routes_to_capability("p2", "synthesis_engine", "insight_integration")
        _emit_stores_embedding("p4", "synthesis_engine", "synthesis_embedding")
        _emit_records_telemetry_event("p4", "synthesis_engine", "synthesis_start")

        if not insights:
            _log.warning("No insights provided for synthesis")
            return {
                "synthesis_id": f"synth_{_trace_id[:8]}",
                "findings": [],
                "mode": synthesis_mode,
                "insight_count": 0,
            }

        # Group insights by theme (simplified implementation)
        themes: dict[str, list[dict[str, Any]]] = {}
        for insight in insights:
            theme = insight.get("theme", "general")
            if theme not in themes:
                themes[theme] = []
            themes[theme].append(insight)

        # Generate findings per theme
        findings: list[dict[str, Any]] = []
        for theme, theme_insights in themes.items():
            finding = {
                "theme": theme,
                "summary": f"Synthesis of {len(theme_insights)} insights on {theme}",
                "key_points": [i.get("key_point", "") for i in theme_insights[:5]],
                "confidence": sum(i.get("confidence", 0.5) for i in theme_insights)
                / len(theme_insights),
                "source_count": len(set(i.get("source_id") for i in theme_insights)),
            }
            findings.append(finding)

        synthesis = {
            "synthesis_id": f"synth_{_trace_id[:8]}",
            "mode": synthesis_mode,
            "target_audience": target_audience,
            "insight_count": len(insights),
            "theme_count": len(themes),
            "findings": findings,
        }

        self._synthesized_findings.append(synthesis)

        _log.info(
            "Synthesized %d insights into %d themes for %s audience",
            len(insights),
            len(themes),
            target_audience,
        )
        _emit_records_telemetry_event(
            "p4", "synthesis_engine", f"synthesis_complete:{len(findings)}",
        )

        return synthesis

    def get_synthesized_findings(self) -> list[dict[str, Any]]:
        """Get all synthesized findings."""
        return self._synthesized_findings.copy()

    def compare_syntheses(
        self,
        synthesis_a_id: str,
        synthesis_b_id: str,
    ) -> dict[str, Any]:
        """Compare two syntheses for divergence/convergence."""
        synth_a = next(
            (s for s in self._synthesized_findings if s.get("synthesis_id") == synthesis_a_id),
            None,
        )
        synth_b = next(
            (s for s in self._synthesized_findings if s.get("synthesis_id") == synthesis_b_id),
            None,
        )

        if not synth_a or not synth_b:
            return {"error": "One or both syntheses not found"}

        themes_a = {f.get("theme") for f in synth_a.get("findings", [])}
        themes_b = {f.get("theme") for f in synth_b.get("findings", [])}

        return {
            "common_themes": list(themes_a & themes_b),
            "unique_to_a": list(themes_a - themes_b),
            "unique_to_b": list(themes_b - themes_a),
            "coverage_ratio": len(themes_a & themes_b) / max(len(themes_a | themes_b), 1),
        }
