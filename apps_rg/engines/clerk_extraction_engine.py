"""
HOP1 Clerk Engine - Structural Extraction Engine
Refactored from apply_clerk_extraction.py
Following Batch 2 specifications with hallucination detection

HARDENING: Removes direct arguments. Enforces reading 'mission_input' from Buffer
and writing 'hop1_extraction' to Buffer.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from apps_rg.engines.base_rg_engine import BaseRGEngine
from apps_rg.engines.hallucination_detector import HallucinationDetector

_emit_applies_guardrail("p0", "clerk_extraction_engine", "p0_governance")
_emit_reads_policy_state("p0", "clerk_extraction_engine", "policy_binding")
_emit_snapshots_state("p0", "clerk_extraction_engine", "state_snapshot")
emit_replay_key("p0", "clerk_extraction_engine")
emit_determinism_digest("p0", "clerk_extraction_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class ClerkExtractionEngine(BaseRGEngine):
    """
    HOP-1: Structural Extraction Engine.
    Reads 'mission_input' -> Writes 'hop1_extraction'.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="HOP.1.CLERK")
        self.detector = HallucinationDetector(ctx)

    async def execute(self) -> dict[str, Any]:
        """
        Execute HOP-1 extraction using Immutable Buffer data.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ClerkExtractionEngine.execute")

        mission_input = self.ctx.buffer.read("mission_input")
        if not mission_input or "master_resume" not in mission_input:
            self.record_fail("Missing 'mission_input' or 'master_resume' in Buffer", signal="DATA_MISSING")
            raise ValueError("Buffer missing mission_input")
        source = mission_input["master_resume"]
        self._mcp_audit("extraction_start")
        experience_sections = self._build_sections(source.get("experience", []))
        for section in experience_sections:
            for bullet in section.get("bullets", []):
                bullet["quantified_metrics"] = self._extract_metrics(bullet["bullet_text"])
        all_bullets = [b["bullet_text"] for s in experience_sections for b in s["bullets"]]
        validation = self.detector.check_batch(all_bullets)
        if not validation["valid"]:
            self.ctx.add_signal("SOURCE_DATA_UNRELIABLE")
        output = {
            "experience_sections": experience_sections,
            "education": source.get("education", []),
            "metadata": {"source_integrity": validation["score"]},
        }
        self.ctx.buffer.write("hop1_extraction", output, source_agent=self.name)
        self.record_pass("HOP-1 Extraction Complete", data={"sections": len(experience_sections)})
        return output

    def _build_sections(self, raw_exp: list[dict]) -> list[dict]:
        """Standardize raw experience into Sovereign segments."""
        sections = []
        for exp in raw_exp:
            sections.append(
                {
                    "company": exp.get("company", "Unknown"),
                    "title": exp.get("title", "Unknown"),
                    "bullets": [{"bullet_text": b} for b in exp.get("bullets", [])],
                }
            )
        return sections

    def _extract_metrics(self, text: str) -> list[str]:
        """Legacy regex extraction."""
        patterns = ["\\$\\d+\\.?\\d*[MBK]\\+?", "\\d+\\.?\\d*%", "\\d{1,3}(?:,\\d{3})+"]
        found = []
        for pattern in patterns:
            found.extend(re.findall(pattern, text))
        return found
