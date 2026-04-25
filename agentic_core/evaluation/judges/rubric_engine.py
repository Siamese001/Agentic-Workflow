"""Rubric Engine — loads, selects, and renders evaluation rubrics.

Bridges rubrics.json definitions and the judge execution layer.
Handles rubric loading, filtering by dimension/layer/scoring method,
and prompt rendering for LLM-based rubrics.

Usage::

    engine = RubricEngine()
    deterministic = engine.get_deterministic_rubrics()
    arch_rubrics = engine.get_rubrics_for_dimension("architecture")
    prompt = engine.render_prompt("GOV-001", target="my_module.py",
                                  source_code="...", adg_edges="...")
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from agentic_core.evaluation.judges.types import (
    EvidenceRequirement,
    RubricDefinition,
    ScoringCriterion,
)
from tqdm import tqdm

_log = logging.getLogger(__name__)

_DEFAULT_RUBRICS_PATH = Path(__file__).parent / "rubrics.json"


def _parse_rubric(data: dict[str, Any]) -> RubricDefinition:
    """Parse a single rubric dict into a RubricDefinition."""
    evidence_reqs = tuple(
        EvidenceRequirement(
            evidence_type=r.get("evidence_type", ""),
            relation=r.get("relation", ""),
            description=r.get("description", ""),
        )
        for r in data.get("evidence_requirements", [])
    )

    criteria = tuple(
        ScoringCriterion(
            criterion_id=c["criterion_id"],
            description=c.get("description", ""),
            weight=c.get("weight", 1.0),
            pass_threshold=c.get("pass_threshold", 1.0),
            warn_threshold=c.get("warn_threshold", 0.9),
        )
        for c in data.get("scoring_criteria", [])
    )

    return RubricDefinition(
        rubric_id=data["rubric_id"],
        dimension=data["dimension"],
        display_name=data.get("display_name", data["rubric_id"]),
        description=data.get("description", ""),
        scoring_method=data.get("scoring_method", "deterministic"),
        severity=data.get("severity", "MEDIUM"),
        applies_to=data.get("applies_to", {}),
        evidence_requirements=evidence_reqs,
        scoring_criteria=criteria,
        deterministic_check=data.get("deterministic_check", ""),
        score_formula=data.get("score_formula", ""),
        pass_threshold=data.get("pass_threshold", 1.0),
        warn_threshold=data.get("warn_threshold", 0.9),
        prompt_template=data.get("prompt_template", ""),
    )


class RubricEngine:
    """Loads and manages evaluation rubrics from JSON configuration.

    Provides filtering, selection, and prompt rendering for both
    deterministic and LLM-based rubrics.
    """

    def __init__(self, rubrics_path: str | Path = "") -> None:
        self._rubrics_path = Path(rubrics_path) if rubrics_path else _DEFAULT_RUBRICS_PATH
        self._rubrics: dict[str, RubricDefinition] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Lazy-load rubrics from JSON on first access."""
        if self._loaded:
            return
        self._load()

    def _load(self) -> None:
        """Load rubrics from the JSON file."""
        if not self._rubrics_path.is_file():
            _log.warning("[RubricEngine] Rubrics file not found: %s", self._rubrics_path)
            self._loaded = True
            return

        try:
            text = self._rubrics_path.read_text(encoding="utf-8")
            data = json.loads(text)
            raw_rubrics = data.get("rubrics", [])
            for raw in raw_rubrics:
                rubric = _parse_rubric(raw)
                self._rubrics[rubric.rubric_id] = rubric
            _log.info(
                "[RubricEngine] Loaded %d rubrics from %s",
                len(self._rubrics),
                self._rubrics_path,
            )
        except (
            json.JSONDecodeError,
            KeyError,
            TypeError,
        ) as exc:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            _log.error("[RubricEngine] Failed to parse rubrics: %s", exc)

        self._loaded = True

    def reload(self) -> int:
        """Force reload rubrics from disk. Returns count loaded."""
        self._rubrics.clear()
        self._loaded = False
        self._ensure_loaded()
        return len(self._rubrics)

    @property
    def all_rubrics(self) -> list[RubricDefinition]:
        """All loaded rubrics."""
        self._ensure_loaded()
        return list(self._rubrics.values())

    @property
    def rubric_ids(self) -> list[str]:
        """All rubric IDs."""
        self._ensure_loaded()
        return list(self._rubrics.keys())

    def get(self, rubric_id: str) -> RubricDefinition | None:
        """Get a specific rubric by ID."""
        self._ensure_loaded()
        return self._rubrics.get(rubric_id)

    def get_deterministic_rubrics(self) -> list[RubricDefinition]:
        """Get all deterministic (non-LLM) rubrics."""
        self._ensure_loaded()
        return [r for r in self._rubrics.values() if r.is_deterministic]

    def get_llm_rubrics(self) -> list[RubricDefinition]:
        """Get all LLM-based rubrics."""
        self._ensure_loaded()
        return [r for r in self._rubrics.values() if not r.is_deterministic]

    def get_rubrics_for_dimension(self, dimension: str) -> list[RubricDefinition]:
        """Get all rubrics for a specific evaluation dimension."""
        self._ensure_loaded()
        return [r for r in self._rubrics.values() if r.dimension == dimension]

    def get_rubrics_for_layer(self, layer: str) -> list[RubricDefinition]:
        """Get rubrics applicable to a specific architecture layer."""
        self._ensure_loaded()
        results = []
        for rubric in self._rubrics.values():
            layer_filter = rubric.applies_to.get("layer_filter", [])
            if not layer_filter or layer in layer_filter:
                results.append(rubric)
        return results

    def get_rubrics_for_severity(self, severity: str) -> list[RubricDefinition]:
        """Get rubrics matching a specific severity level."""
        self._ensure_loaded()
        return [r for r in self._rubrics.values() if r.severity == severity]

    def get_applicable_rubrics(
        self,
        layer: str = "",
        entity_type: str = "",
        deterministic_only: bool = False,
    ) -> list[RubricDefinition]:
        """Get all rubrics applicable to a target with given properties.

        Args:
            layer: Architecture layer (e.g. "L2").
            entity_type: Entity type (e.g. "module", "class").
            deterministic_only: If True, exclude LLM-based rubrics.
        """
        self._ensure_loaded()
        results = []
        for rubric in tqdm(self._rubrics.values(), desc="Processing", unit="item"):
            if deterministic_only and not rubric.is_deterministic:
                continue

            applies = rubric.applies_to
            layer_filter = applies.get("layer_filter", [])
            if layer_filter and layer and layer not in layer_filter:
                continue

            entity_filter = applies.get("entity_types", [])
            if entity_filter and entity_type and entity_type not in entity_filter:
                continue

            results.append(rubric)
        return results

    def render_prompt(
        self,
        rubric_id: str,
        **kwargs: str,
    ) -> str | None:
        """Render an LLM rubric's prompt template with provided variables.

        Common kwargs: target, source_code, adg_edges

        Returns None if rubric not found or has no prompt template.
        """
        self._ensure_loaded()
        rubric = self._rubrics.get(rubric_id)
        if not rubric or not rubric.prompt_template:
            return None

        try:
            return rubric.prompt_template.format(**kwargs)
        except KeyError as exc:
            _log.warning(
                "[RubricEngine] Missing template variable for %s: %s",
                rubric_id,
                exc,
            )
            return rubric.prompt_template

    def evidence_requirements_for(self, rubric_id: str) -> list[dict[str, str]]:
        """Get evidence requirements as dicts for use with EvidenceAssembler."""
        self._ensure_loaded()
        rubric = self._rubrics.get(rubric_id)
        if not rubric:
            return []
        return [
            {
                "evidence_type": req.evidence_type,
                "relation": req.relation,
                "description": req.description,
            }
            for req in rubric.evidence_requirements
        ]

    def summary(self) -> dict[str, Any]:
        """Get a summary of loaded rubrics by dimension and method."""
        self._ensure_loaded()
        by_dimension: dict[str, int] = {}
        by_method: dict[str, int] = {}
        by_severity: dict[str, int] = {}

        for rubric in self._rubrics.values():
            by_dimension[rubric.dimension] = by_dimension.get(rubric.dimension, 0) + 1
            by_method[rubric.scoring_method] = by_method.get(rubric.scoring_method, 0) + 1
            by_severity[rubric.severity] = by_severity.get(rubric.severity, 0) + 1

        return {
            "total_rubrics": len(self._rubrics),
            "by_dimension": by_dimension,
            "by_method": by_method,
            "by_severity": by_severity,
            "rubric_ids": list(self._rubrics.keys()),
        }


__all__ = ["RubricEngine"]
