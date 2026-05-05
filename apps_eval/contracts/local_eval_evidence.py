"""Local evaluation evidence contract.

LocalEvalEvidenceContract — the sealed packet from apps_eval runs.
Unlike apps that surface C0 retrieval sources, apps_eval captures
evaluation provenance: calibrated rubric IDs, judge versions,
taxonomy match counts, self-contradiction checks.

Plan: apps-eval-agentic-spine-hardening-9d4f2e W2.3
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class JudgeCalibration:
    """Judge calibration provenance."""
    calibrated_rubric_id: str = ""
    judge_versions: list[str] = field(default_factory=list)
    taxonomy_match_count: int = 0
    self_contradiction_checked: bool = False


@dataclass
class LocalEvalEvidenceContract:
    """Sealed evidence contract from an evaluation run.

    Schema version 1.0 — compatible with ExitReviewPacket.final_evidence_contract.
    """
    schema_version: str = "1.0"
    producer: str = "apps_eval.cert.fec_producer"
    grounded: bool = False
    retrieval_sources: list[str] = field(default_factory=list)
    template_ids: list[str] = field(default_factory=list)
    route_id: str = ""
    evidence_sufficiency: str = "empty"  # "grounded" | "calibrated_only" | "empty"
    judge_calibration: JudgeCalibration = field(default_factory=JudgeCalibration)

    @classmethod
    def from_fec_dict(cls, fec: dict[str, Any]) -> "LocalEvalEvidenceContract":
        """Build contract from FEC-shaped dict."""
        jc = fec.get("judge_calibration", {})
        return cls(
            schema_version=fec.get("schema_version", "1.0"),
            producer=fec.get("producer", "apps_eval.cert.fec_producer"),
            grounded=fec.get("grounded", False),
            retrieval_sources=fec.get("retrieval_sources", []),
            template_ids=fec.get("template_ids", []),
            route_id=fec.get("route_id", ""),
            evidence_sufficiency=fec.get("evidence_sufficiency", "empty"),
            judge_calibration=JudgeCalibration(
                calibrated_rubric_id=jc.get("calibrated_rubric_id", ""),
                judge_versions=jc.get("judge_versions", []),
                taxonomy_match_count=jc.get("taxonomy_match_count", 0),
                self_contradiction_checked=jc.get("self_contradiction_checked", False),
            ),
        )

    def to_fec_dict(self) -> dict[str, Any]:
        """Export to FEC-shaped dict for Exit pipeline."""
        return {
            "schema_version": self.schema_version,
            "producer": self.producer,
            "grounded": self.grounded,
            "retrieval_sources": self.retrieval_sources,
            "template_ids": self.template_ids,
            "route_id": self.route_id,
            "evidence_sufficiency": self.evidence_sufficiency,
            "judge_calibration": {
                "calibrated_rubric_id": self.judge_calibration.calibrated_rubric_id,
                "judge_versions": self.judge_calibration.judge_versions,
                "taxonomy_match_count": self.judge_calibration.taxonomy_match_count,
                "self_contradiction_checked": self.judge_calibration.self_contradiction_checked,
            },
        }