"""Chunk resume output into reusable segments with metadata."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class ResumeChunk:
    """A single reusable chunk of resume output."""

    # Identity
    chunk_id: str  # UUID for this chunk
    artifact_id: str  # Parent artifact (the full resume)

    # Content
    section_type: str  # header, summary, experience, skills, education
    content: str  # The actual text content
    content_hash: str  # SHA-256 of content for integrity

    # Lineage (linking to source)
    source_run_id: str  # The run that produced this chunk
    source_request_id: str  # The request id
    source_input_intent_hash: str  # Hash of input intent that generated this

    # Metadata
    target_job_metadata: dict  # Company, role, level for this chunk
    policy_hash: str  # Policy under which this chunk was produced
    blueprint_hash: str  # Resume structure blueprint version

    # Freshness
    freshness_status: str  # fresh, bounded, stale
    generated_at: str  # ISO timestamp

    # Scope
    tenant_id: str
    user_scope: str  # Anonymous user identifier

    # Provenance
    lineage_refs: list[str]  # References to parent chunks (if derived)
    replay_refs: list[str]  # References to replay runs
    exit_disposition_ref: str  # Reference to Exit disposition proving clearance
    uwg_commit_receipt: str  # UWG receipt proving durable admission

    def to_dict(self) -> dict:
        """Convert to serializable dict."""
        return {
            "chunk_id": self.chunk_id,
            "artifact_id": self.artifact_id,
            "section_type": self.section_type,
            "content": self.content,
            "content_hash": self.content_hash,
            "lineage": {
                "source_run_id": self.source_run_id,
                "source_request_id": self.source_request_id,
                "source_input_intent_hash": self.source_input_intent_hash,
            },
            "target_job_metadata": self.target_job_metadata,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "freshness_status": self.freshness_status,
            "generated_at": self.generated_at,
            "scope": {
                "tenant_id": self.tenant_id,
                "user_scope": self.user_scope,
            },
            "provenance": {
                "lineage_refs": self.lineage_refs,
                "replay_refs": self.replay_refs,
                "exit_disposition_ref": self.exit_disposition_ref,
                "uwg_commit_receipt": self.uwg_commit_receipt,
            },
        }


class ResumeChunker:
    """Chunk resume into reusable sections."""

    SECTION_ORDER = [
        "header",
        "summary",
        "experience",
        "skills",
        "education",
        "certifications",
        "projects",
        "awards",
    ]

    def chunk_resume(
        self,
        resume_content: dict,
        run_context: dict,
        intent_hash: str,
    ) -> list[ResumeChunk]:
        """Chunk a generated resume into reusable segments."""
        chunks = []
        artifact_id = run_context.get("run_id", "unknown")

        for section_type in self.SECTION_ORDER:
            section_content = resume_content.get(section_type)
            if not section_content:
                continue

            chunk = self._create_chunk(
                section_type=section_type,
                content=section_content,
                artifact_id=artifact_id,
                run_context=run_context,
                intent_hash=intent_hash,
            )
            chunks.append(chunk)

        return chunks

    def _create_chunk(
        self,
        section_type: str,
        content: Any,
        artifact_id: str,
        run_context: dict,
        intent_hash: str,
    ) -> ResumeChunk:
        """Create a single chunk with full lineage."""
        # Normalize content to string
        if isinstance(content, list):
            content_str = "\n\n".join(str(item) for item in content)
        elif isinstance(content, dict):
            content_str = json.dumps(content, indent=2)
        else:
            content_str = str(content)

        # Derive content hash
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()[:32]

        # Get target job metadata from run context
        target_job = run_context.get("target_job", {})
        if isinstance(target_job, dict):
            target_job_metadata = target_job
        else:
            target_job_metadata = {}

        return ResumeChunk(
            chunk_id=str(uuid.uuid4())[:16],
            artifact_id=artifact_id,
            section_type=section_type,
            content=content_str,
            content_hash=content_hash,
            source_run_id=run_context.get("run_id", "unknown"),
            source_request_id=run_context.get("request_id", "unknown"),
            source_input_intent_hash=intent_hash,
            target_job_metadata=target_job_metadata,
            policy_hash=run_context.get("policy_hash", "unknown"),
            blueprint_hash=run_context.get("blueprint_hash", "unknown"),
            freshness_status="fresh",
            generated_at=datetime.now(timezone.utc).isoformat(),
            tenant_id=run_context.get("tenant_id", "default"),
            user_scope=run_context.get("user_scope", "anonymous"),
            lineage_refs=run_context.get("lineage_refs", []),
            replay_refs=run_context.get("replay_refs", []),
            exit_disposition_ref=run_context.get("exit_disposition_ref", ""),
            uwg_commit_receipt=run_context.get("uwg_commit_receipt", ""),
        )


__all__ = ["ResumeChunk", "ResumeChunker"]
