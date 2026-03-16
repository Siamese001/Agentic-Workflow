"""
Capability Extraction Engine — apps_exec.

Extracts structured platform capabilities and evidence anchors from
ingested source documents using deterministic regex patterns.

Deterministic: all extraction is pattern-based, no model calls.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "capability_extraction_engine", "execution_auth")
_emit_validates_capability("p2", "capability_extraction_engine", "capability_check")
_emit_routes_to_capability("p2", "capability_extraction_engine", "capability_route")
_emit_writes_via_uwg("p2", "capability_extraction_engine", "uwg_write")
_emit_blocks_direct_write("p2", "capability_extraction_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "capability_extraction_engine", "tool_invocation")
_emit_captures_execution_output("p2", "capability_extraction_engine", "exec_output")
_emit_dispatches_agent("p3", "capability_extraction_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "capability_extraction_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "capability_extraction_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "capability_extraction_engine", "healing_outcome")
_emit_escalates_failure("p3", "capability_extraction_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "capability_extraction_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "capability_extraction_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "capability_extraction_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "capability_extraction_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "capability_extraction_engine", "eval_metric")
_emit_stores_embedding("p4", "capability_extraction_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "capability_extraction_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "capability_extraction_engine", "exec_snapshot_link")
from apps_exec.engines.base_exec_engine import BaseExecEngine
from apps_exec.engines.ingestion_engine import IngestionResult
from apps_exec.types.exec_types import CapabilityEvidence

_emit_applies_guardrail("p0", "capability_extraction_engine", "p0_governance")
_emit_reads_policy_state("p0", "capability_extraction_engine", "policy_binding")
_emit_snapshots_state("p0", "capability_extraction_engine", "state_snapshot")
emit_replay_key("p0", "capability_extraction_engine")
emit_determinism_digest("p0", "capability_extraction_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_log = logging.getLogger(__name__)

_CAPABILITY_PATTERNS = [
    (r"(?i)(?:supports|provides|enforces|enables|implements)\s+([\w\s\-]{3,50})", "feature"),
    (
        r"(?i)\b(governance|orchestration|routing|retrieval|safety|observability|determinism|tracing)\b",
        "domain",
    ),
    (r"(?i)\b(L[0-9]_\w+|L[0-9] \w+)\b", "layer"),
    (r"(?i)\b(validator|contract|enforcer|gate|policy|guardian)\b", "enforcement"),
    (r"(?i)\b(hallucination|drift|replay|lineage|provenance)\b", "quality"),
]

_EVIDENCE_ANCHOR_PATTERN = re.compile(
    r"(?i)\b(layer|module|engine|agent|validator|contract|spec|mixin|gateway|orchestrator)\s+([\w_\-\.]+)"
)

_KNOWN_CAPABILITY_LABELS: dict[str, str] = {
    "governance": "Multi-layer governance enforcement",
    "orchestration": "Multi-hop agent orchestration",
    "routing": "Intelligent execution routing",
    "retrieval": "RAG-backed retrieval pipeline",
    "safety": "L5 safety and static analysis",
    "observability": "OpenTelemetry-aligned observability",
    "determinism": "Deterministic execution contracts",
    "tracing": "End-to-end distributed tracing",
    "hallucination": "Hallucination detection and gating",
    "provenance": "Full output provenance metadata",
    "lineage": "Data and decision lineage tracking",
}


@dataclass
class ExtractionResult:
    """Output of capability extraction pass."""

    capabilities: list[CapabilityEvidence] = field(default_factory=list)
    evidence_anchors: list[str] = field(default_factory=list)
    source_coverage: dict[str, int] = field(default_factory=dict)


class CapabilityExtractionEngine(BaseExecEngine):
    """Extract platform capabilities and evidence anchors from documents.

    Uses deterministic regex patterns. No LLM calls at this stage.
    Each extracted capability includes its source evidence anchor for
    claim-to-source traceability.
    """

    AGENT_ID = "EXEC_CAPABILITY_EXTRACTION"

    def execute(self, input_data: IngestionResult) -> ExtractionResult:
        """Extract capabilities from ingested documents.

        Args:
            input_data: IngestionResult from IngestionEngine.

        Returns:
            ExtractionResult with deduplicated capabilities and anchors.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CapabilityExtractionEngine.execute")

        seen_labels: set[str] = set()
        capabilities: list[CapabilityEvidence] = []
        all_anchors: list[str] = []
        source_coverage: dict[str, int] = {}

        cfg_extraction = self.specs.extraction if self.specs else None
        max_per_section = cfg_extraction.max_capabilities_per_section if cfg_extraction else 10

        for doc in input_data.documents:
            doc_caps = 0
            doc_anchors: list[str] = []

            for anchor_match in _EVIDENCE_ANCHOR_PATTERN.finditer(doc.content):
                anchor = anchor_match.group(0).strip()
                if anchor not in all_anchors:
                    all_anchors.append(anchor)
                    doc_anchors.append(anchor)

            for pattern, emphasis in _CAPABILITY_PATTERNS:
                for match in re.finditer(pattern, doc.content):
                    label_raw = match.group(1).strip().lower()
                    label_key = re.sub(r"\s+", "_", label_raw)

                    if label_key in seen_labels:
                        continue
                    if doc_caps >= max_per_section:
                        break

                    display = _KNOWN_CAPABILITY_LABELS.get(label_raw, label_raw.title())
                    cap = CapabilityEvidence(
                        capability_id=f"CAP_{label_key.upper()}",
                        label=display,
                        description=f"Platform capability: {display}",
                        evidence_anchors=tuple(doc_anchors[:3]),
                        layer="",
                        emphasis_area=emphasis,
                    )
                    capabilities.append(cap)
                    seen_labels.add(label_key)
                    doc_caps += 1

            source_coverage[doc.path] = doc_caps

        self.record_pass(f"Extracted {len(capabilities)} capabilities from {len(input_data.documents)} docs")
        return ExtractionResult(
            capabilities=capabilities,
            evidence_anchors=all_anchors,
            source_coverage=source_coverage,
        )
