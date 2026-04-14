"""ADG Prompt Assembly Contracts — core types for evidence, packets, and status.

These dataclasses define the formal contracts between:
    - Retrieval adapters (C0 side) → EvidenceItem, EvidenceBundle
    - Packet builders → PromptEnvelope
    - Assembly tracking → PromptAssemblyStatus

No retrieval, routing, or execution logic lives here — types only.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Literal


# ---------------------------------------------------------------------------
# Evidence Contract
# ---------------------------------------------------------------------------

SourceType = Literal[
    "sqlite",
    "json_report",
    "graph_db",
    "infra_view",
    "ratchet",
    "structural",
]


@dataclass
class EvidenceItem:
    """A single piece of evidence from a canonical or derived ADG source."""

    source_artifact: str
    source_type: SourceType
    snapshot_id: str
    commit_sha: str = ""
    scanner_digest: str = ""
    artifact_digest: str = ""
    row_references: list[str] = field(default_factory=list)
    cited_spans: list[str] = field(default_factory=list)
    support_score: float = 1.0
    coverage_score: float = 1.0
    is_derived: bool = False
    freshness: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_artifact": self.source_artifact,
            "source_type": self.source_type,
            "snapshot_id": self.snapshot_id,
            "commit_sha": self.commit_sha,
            "scanner_digest": self.scanner_digest,
            "artifact_digest": self.artifact_digest,
            "row_references": self.row_references,
            "cited_spans": self.cited_spans,
            "support_score": self.support_score,
            "coverage_score": self.coverage_score,
            "is_derived": self.is_derived,
            "freshness": self.freshness,
            "data": self.data,
        }


@dataclass
class ContradictionFlag:
    """An explicit disagreement between two evidence sources."""

    field_name: str
    source_a: str
    value_a: Any
    source_b: str
    value_b: Any
    severity: Literal["minor", "major"] = "minor"
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_name": self.field_name,
            "source_a": self.source_a,
            "value_a": self.value_a,
            "source_b": self.source_b,
            "value_b": self.value_b,
            "severity": self.severity,
            "description": self.description,
        }


@dataclass
class EvidenceBundle:
    """Shaped evidence ready for packet assembly."""

    items: list[EvidenceItem] = field(default_factory=list)
    coverage_score: float = 0.0
    contradiction_status: Literal["none", "minor", "major"] = "none"
    contradictions: list[ContradictionFlag] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    freshness: str = ""
    weak_support: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_count": len(self.items),
            "coverage_score": self.coverage_score,
            "contradiction_status": self.contradiction_status,
            "contradictions": [c.to_dict() for c in self.contradictions],
            "gaps": self.gaps,
            "freshness": self.freshness,
            "weak_support": self.weak_support,
        }


# ---------------------------------------------------------------------------
# Prompt Envelope Contract
# ---------------------------------------------------------------------------


@dataclass
class PromptEnvelope:
    """A bounded, deterministic prompt packet assembled from ADG evidence.

    Block order is strict and canonical:
        1. system_block      — operator mode / role
        2. policy_block      — invariants / constraints
        3. task_block         — what the consumer should do
        4. must_use_evidence  — canonical evidence (source-of-truth)
        5. optional_evidence  — derived/augmenting evidence
        6. contradiction_flags — explicit disagreements (NEVER hidden)
        7. abstain_instructions — when/how to refuse
        8. refine_instructions — what to request if insufficient
        9. output_schema      — expected response format
       10. replay_metadata    — provenance for deterministic replay
    """

    # Header
    packet_type: str
    packet_id: str = ""
    schema_version: str = "1.0.0"

    # Blocks (ordered)
    system_block: str = ""
    policy_block: str = ""
    task_block: str = ""
    must_use_evidence: list[dict[str, Any]] = field(default_factory=list)
    optional_evidence: list[dict[str, Any]] = field(default_factory=list)

    # Integrity
    contradiction_flags: list[dict[str, Any]] = field(default_factory=list)
    abstain_instructions: str = ""
    refine_instructions: str = ""

    # Output
    output_schema: dict[str, Any] = field(default_factory=dict)
    replay_metadata: dict[str, Any] = field(default_factory=dict)

    # Status
    assembly_status: PromptAssemblyStatus | None = None

    def __post_init__(self) -> None:
        if not self.packet_id:
            self.packet_id = self._generate_packet_id()
        if self.assembly_status is not None and not self.assembly_status.packet_id:
            self.assembly_status.packet_id = self.packet_id

    def _generate_packet_id(self) -> str:
        """Generate a deterministic packet ID from type + replay metadata."""
        seed = json.dumps(
            {"packet_type": self.packet_type, "replay": self.replay_metadata},
            sort_keys=True,
        )
        return hashlib.sha256(seed.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "packet_type": self.packet_type,
            "packet_id": self.packet_id,
            "schema_version": self.schema_version,
            "system_block": self.system_block,
            "policy_block": self.policy_block,
            "task_block": self.task_block,
            "must_use_evidence": self.must_use_evidence,
            "optional_evidence": self.optional_evidence,
            "contradiction_flags": self.contradiction_flags,
            "abstain_instructions": self.abstain_instructions,
            "refine_instructions": self.refine_instructions,
            "output_schema": self.output_schema,
            "replay_metadata": self.replay_metadata,
        }
        if self.assembly_status is not None:
            result["assembly_status"] = self.assembly_status.to_dict()
        return result

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=False)

    def to_markdown(self) -> str:
        """Render as analyst-friendly markdown."""
        lines = [
            f"# ADG Packet: {self.packet_type}",
            f"**Packet ID**: `{self.packet_id}`",
            f"**Schema**: v{self.schema_version}",
            "",
        ]
        if self.system_block:
            lines += ["## System", self.system_block, ""]
        if self.policy_block:
            lines += ["## Policy / Invariants", self.policy_block, ""]
        if self.task_block:
            lines += ["## Task", self.task_block, ""]
        if self.must_use_evidence:
            lines += ["## Must-Use Evidence"]
            for i, ev in enumerate(self.must_use_evidence, 1):
                src = ev.get("source_artifact", "unknown")
                lines.append(f"### Evidence {i} — `{src}`")
                lines.append(f"```json\n{json.dumps(ev, indent=2)}\n```")
            lines.append("")
        if self.optional_evidence:
            lines += ["## Optional Evidence (Derived)"]
            for i, ev in enumerate(self.optional_evidence, 1):
                src = ev.get("source_artifact", "unknown")
                lines.append(f"### Derived {i} — `{src}`")
                lines.append(f"```json\n{json.dumps(ev, indent=2)}\n```")
            lines.append("")
        if self.contradiction_flags:
            lines += ["## Contradiction Flags"]
            for cf in self.contradiction_flags:
                lines.append(
                    f"- **{cf.get('field_name', '?')}**: "
                    f"`{cf.get('source_a')}` = {cf.get('value_a')} vs "
                    f"`{cf.get('source_b')}` = {cf.get('value_b')} "
                    f"[{cf.get('severity', 'minor')}]"
                )
            lines.append("")
        if self.abstain_instructions:
            lines += ["## Abstain Instructions", self.abstain_instructions, ""]
        if self.refine_instructions:
            lines += ["## Refine Instructions", self.refine_instructions, ""]
        if self.output_schema:
            lines += [
                "## Output Schema",
                f"```json\n{json.dumps(self.output_schema, indent=2)}\n```",
                "",
            ]
        if self.replay_metadata:
            lines += [
                "## Replay Metadata",
                f"```json\n{json.dumps(self.replay_metadata, indent=2)}\n```",
                "",
            ]
        if self.assembly_status:
            lines += [
                "## Assembly Status",
                f"- **Result**: {self.assembly_status.assembly_result}",
                f"- **Evidence**: {self.assembly_status.evidence_contract_status}",
                f"- **Contradictions**: {self.assembly_status.contradiction_status}",
                f"- **Token Budget**: {self.assembly_status.token_budget_status}",
                f"- **Overflow Action**: {self.assembly_status.overflow_action}",
                "",
            ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Assembly Status Contract
# ---------------------------------------------------------------------------


@dataclass
class PromptAssemblyStatus:
    """Tracks the assembly process for audit and replay."""

    packet_type: str
    packet_id: str = ""
    input_artifacts: list[str] = field(default_factory=list)
    evidence_contract_status: Literal["complete", "partial", "empty"] = "empty"
    contradiction_status: Literal["none", "minor", "major"] = "none"
    token_budget_status: Literal["within_budget", "trimmed", "split"] = "within_budget"
    overflow_action: Literal["none", "summarized", "narrowed", "split", "abstained"] = "none"
    assembly_result: Literal["pass", "fail", "partial"] = "pass"
    replay_metadata: dict[str, Any] = field(default_factory=dict)
    assembly_timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.assembly_timestamp:
            replay_ts = self.replay_metadata.get("assembly_timestamp", "")
            self.assembly_timestamp = replay_ts if isinstance(replay_ts, str) else ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_type": self.packet_type,
            "packet_id": self.packet_id,
            "input_artifacts": self.input_artifacts,
            "evidence_contract_status": self.evidence_contract_status,
            "contradiction_status": self.contradiction_status,
            "token_budget_status": self.token_budget_status,
            "overflow_action": self.overflow_action,
            "assembly_result": self.assembly_result,
            "replay_metadata": self.replay_metadata,
            "assembly_timestamp": self.assembly_timestamp,
        }
