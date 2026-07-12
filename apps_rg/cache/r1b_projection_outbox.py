"""Execute R1B filesystem and Chroma work only from durable L4 outbox tasks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from apps_rg.cache.r1b_filesystem_projector import (
    R1BFilesystemProjectionReceipt,
    project_r1b_filesystem_from_outbox,
)


@dataclass(frozen=True)
class R1BOutboxProjectionOutcome:
    status: str
    commit_receipt_id: str
    projection_id: str
    filesystem_receipt: dict[str, Any] | None = None
    chroma_receipt: dict[str, Any] | None = None
    reconciliation: dict[str, Any] | None = None
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _artifact_dir_from_candidate(candidate: Any) -> Path | None:
    ref = str(getattr(candidate, "x3_disposition_ref", "") or "")
    if not ref:
        return None
    path = Path(ref)
    return path.parent if path.name == "x3_disposition.json" else None


def project_r1b_commit_from_outbox(
    *,
    gateway: Any,
    candidate: Any,
    outcome: Any,
    projection_root: Path | str,
    artifact_dir: Path | str | None = None,
    section_id: str = "integrated_whole_run",
    run_id: str | None = None,
    raw_request: dict[str, Any] | None = None,
) -> R1BOutboxProjectionOutcome:
    """Claim, execute, verify and complete the committed R1B projection task."""

    commit_receipt_id = str(getattr(outcome, "uwg_commit_receipt_id", "") or "")
    backend = getattr(gateway, "canonical_backend", None)
    if not commit_receipt_id or backend is None:
        return R1BOutboxProjectionOutcome(
            status="FAILED",
            commit_receipt_id=commit_receipt_id,
            projection_id="",
            reason="canonical_backend_or_commit_receipt_missing",
        )
    tasks = gateway.projection_tasks(
        commit_receipt_id=commit_receipt_id,
        statuses=("PENDING", "FAILED", "COMPLETE"),
    )
    if not tasks:
        return R1BOutboxProjectionOutcome(
            status="FAILED",
            commit_receipt_id=commit_receipt_id,
            projection_id="",
            reason="projection_outbox_task_missing",
        )
    task = tasks[0]
    if task.status == "COMPLETE":
        return R1BOutboxProjectionOutcome(
            status="COMPLETE",
            commit_receipt_id=commit_receipt_id,
            projection_id=task.projection_id,
            reconciliation=backend.reconcile_commit(commit_receipt_id),
            reason="idempotent_projection_replay",
        )

    claimed = backend.claim_projection(task.projection_id)
    try:
        if not getattr(outcome, "uwg_commit_receipt", None):
            receipt = gateway.get_commit_receipt(commit_receipt_id)
            if receipt is None:
                raise RuntimeError("core commit receipt lookup failed")
            outcome.uwg_commit_receipt = asdict(receipt)

        fs_receipt: R1BFilesystemProjectionReceipt = (
            project_r1b_filesystem_from_outbox(
                projection_root=projection_root,
                candidate=candidate,
                outcome=outcome,
                outbox_payload_digest=claimed.payload_digest,
            )
        )
        if fs_receipt.status != "COMPLETE":
            raise RuntimeError(fs_receipt.reason or "filesystem projection failed")

        resolved_artifact_dir = (
            Path(artifact_dir).resolve()
            if artifact_dir is not None
            else _artifact_dir_from_candidate(candidate)
        )
        if resolved_artifact_dir is None:
            raise RuntimeError(
                "R1B Chroma projection requires the source artifact directory"
            )
        from apps_rg.cache.r1b_chroma_read_surface_projection import (
            CHROMA_COLLECTION_INDEX_ARTIFACT,
            CHROMA_READ_AFTER_WRITE_ARTIFACT,
            project_governed_chroma_read_surface,
        )

        chroma = project_governed_chroma_read_surface(
            artifact_dir=resolved_artifact_dir,
            section_id=section_id,
            run_id=run_id or str(candidate.source_run_id),
            record=candidate.record,
            chunks=candidate.chunks,
            commit_request_id=str(getattr(outcome, "commit_request_id", "")),
            uwg_commit_receipt_id=commit_receipt_id,
            raw_request=dict(raw_request or {}),
        )
        chroma_payload = chroma.to_dict()
        if not chroma.chroma_projection_complete:
            raise RuntimeError(chroma.reason or "chroma projection not complete")

        import json

        index_doc = json.loads(
            (resolved_artifact_dir / CHROMA_COLLECTION_INDEX_ARTIFACT).read_text(
                encoding="utf-8"
            )
        )
        raw_doc = json.loads(
            (resolved_artifact_dir / CHROMA_READ_AFTER_WRITE_ARTIFACT).read_text(
                encoding="utf-8"
            )
        )
        index_payload = index_doc.get("payload") or index_doc
        raw_payload = raw_doc.get("payload") or raw_doc
        if index_payload.get("record_id") != candidate.record.record_id:
            raise RuntimeError("Chroma projection record identity mismatch")
        if raw_payload.get("read_after_write_status") != "PASS":
            raise RuntimeError("Chroma read-after-write receipt did not pass")
        chroma_payload.update(
            {
                "outbox_projection_id": claimed.projection_id,
                "outbox_payload_digest": claimed.payload_digest,
                "source_commit_receipt_id": commit_receipt_id,
            }
        )

        gateway.complete_projection(
            claimed.projection_id,
            observed_payload_digest=claimed.payload_digest,
            receipt_payload={
                "filesystem": fs_receipt.to_dict(),
                "chroma": chroma_payload,
            },
        )
        reconciliation = backend.reconcile_commit(commit_receipt_id)
        return R1BOutboxProjectionOutcome(
            status="COMPLETE",
            commit_receipt_id=commit_receipt_id,
            projection_id=claimed.projection_id,
            filesystem_receipt=fs_receipt.to_dict(),
            chroma_receipt=chroma_payload,
            reconciliation=reconciliation,
        )
    except Exception as exc:
        gateway.fail_projection(
            claimed.projection_id, error=f"{type(exc).__name__}: {exc}"
        )
        return R1BOutboxProjectionOutcome(
            status="FAILED",
            commit_receipt_id=commit_receipt_id,
            projection_id=claimed.projection_id,
            reason=f"{type(exc).__name__}: {exc}",
            reconciliation=backend.reconcile_commit(commit_receipt_id),
        )


__all__ = ["R1BOutboxProjectionOutcome", "project_r1b_commit_from_outbox"]
