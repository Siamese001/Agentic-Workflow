"""Synthetic draft simulator."""

import random
from typing import Any, Dict

from simulations.models.draft_simulation import (
    DraftSimMetrics,
    DraftSimRequest,
    DraftSimResult,
)
from simulations.utils import model_to_payload


class DraftSimulator:
    """Simulates draft-level properties."""

    async def run(self, request: DraftSimRequest) -> DraftSimResult:
        section_count = len(request.draft_sections)
        entropy = round(random.uniform(0.2, 0.9), 3)
        cohesion = round(max(0.0, min(1.0, 0.5 + section_count * 0.05 + random.uniform(-0.2, 0.3))), 3)
        rhythm_score = round(random.uniform(0.3, 0.95), 3)
        metrics = DraftSimMetrics(entropy=entropy, cohesion=cohesion, rhythm_score=rhythm_score)
        preview: Dict[str, Any] = {}
        if request.draft_sections:
            first_key = next(iter(request.draft_sections))
            preview = {first_key: request.draft_sections[first_key]}
        return DraftSimResult(
            simulation_id=request.simulation_id,
            success=True,
            metrics=model_to_payload(metrics),
            details={"section_preview": preview},
        )
