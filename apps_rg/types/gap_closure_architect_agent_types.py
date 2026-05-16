"""Typed competencies + GapClosureArchitect agent stubs for RG unit ADG probes."""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin


@dataclass
class CompetencyItem:
    """Single competency hypothesis."""

    name: str = ""


@dataclass
class CompetenciesOutput:
    """Aggregate competencies response."""

    items: list[CompetencyItem] = field(default_factory=list)


class GapClosureArchitectAgent(SubatomicTestingMixin):
    """Architect agent shell — implements gap coverage hooks for probes."""

    def generate_competencies(self, jd: str | None = None) -> CompetenciesOutput:
        del jd
        return CompetenciesOutput()

    def _calculate_gap_coverage(self) -> float:
        return 0.0

    def _check_industry_first_ranking(self, *_args: object, **_kwargs: object) -> bool:
        return False


__all__ = ["CompetenciesOutput", "CompetencyItem", "GapClosureArchitectAgent"]
