"""Canonical R1B promotion: Exit evidence -> transactional UWG -> outbox projections."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from apps_rg.cache.r1b_projection_outbox import (
    R1BOutboxProjectionOutcome,
    project_r1b_commit_from_outbox,
)
from apps_rg.cache.r1b_strict_gateway import (
    R1BStrictUWGGateway,
    get_r1b_strict_gateway,
)
from apps_rg.cache.r1b_uwg_promotion import (
    R1BCachePromotionCandidate,
    R1BPromotionOutcome,
    build_r1b_commit_bundle,
    governance_receipt_with_l5_packet,
    write_blocked_promotion_receipt,
)
from apps_rg.cache.r1b_uwg_receipt_contract import (
    build_governance_receipt_bundle,
    validate_commit_request_governance,
)


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    fd, tmp = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def _materialize_commit_evidence(
    *,
    artifact_dir: Path | str | None,
    candidate: R1BCachePromotionCandidate,
    commit_request: Any,
    state_diffs: list[Any],
    validation: Any,
    commit_receipt: Any,
) -> None:
    if artifact_dir is None:
        return
    root = Path(artifact_dir).resolve()

    def envelope(name: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "schema_version": "apps_rg.r1b_transactional_evidence.v1",
            "producer": "apps_rg.cache.r1b_transactional_promotion",
            "artifact_name": name,
            "payload": payload,
        }

    _atomic_write_json(
        root / "commit_request.json",
        envelope("commit_request.json", asdict(commit_request)),
    )
    if state_diffs:
        _atomic_write_json(
            root / "proposed_state_diff_ref.json",
            envelope("proposed_state_diff_ref.json", asdict(state_diffs[0])),
        )
    _atomic_write_json(
        root / "state_diff_validation_result.json",
        envelope("state_diff_validation_result.json", asdict(validation)),
    )
    _atomic_write_json(
        root / "uwg_commit_receipt.json",
        envelope("uwg_commit_receipt.json", asdict(commit_receipt)),
    )
    _atomic_write_json(
        root / "l4_namespace_object_ref.json",
        envelope(
            "l4_namespace_object_ref.json",
            {
                "target_l4_namespace": "l4.apps_rg.r1b_semantic_cache",
                "affected_state_surfaces": list(
                    commit_receipt.affected_state_surfaces
                ),
                "state_diff_refs": list(commit_receipt.state_diff_refs),
                "commit_request_ref": commit_request.commit_request_id,
                "uwg_commit_receipt_id": commit_receipt.commit_receipt_id,
                "source_commit_content_hash": commit_receipt.content_hash,
                "parent_intent_record": candidate.record.to_dict(),
                "child_output_chunks": [
                    row.to_dict() for row in candidate.chunks
                ],
                "canonical_store": "sqlite",
                "read_surface_role": "projection_not_truth",
            },
        ),
    )


@dataclass(frozen=True)
class R1BTransactionalPromotionResult:
    promotion: R1BPromotionOutcome
    projection: R1BOutboxProjectionOutcome | None

    @property
    def complete(self) -> bool:
        return (
            self.promotion.status == "ADMITTED"
            and self.projection is not None
            and self.projection.status == "COMPLETE"
        )


def promote_r1b_transactionally(
    *,
    candidate: R1BCachePromotionCandidate,
    projection_root: Path | str,
    artifact_dir: Path | str | None = None,
    section_id: str = "integrated_whole_run",
    run_id: str | None = None,
    raw_request: dict[str, Any] | None = None,
    gateway: R1BStrictUWGGateway | None = None,
) -> R1BTransactionalPromotionResult:
    """Commit canonical R1B state and execute only its durable outbox task."""

    gw = (
        gateway
        if gateway is not None and hasattr(gateway, "register_candidate")
        else get_r1b_strict_gateway()
    )
    exit_metadata = dict(candidate.post_exit_eligibility.get("exit_metadata") or {})
    x3_code = str(
        exit_metadata.get("x3_disposition")
        or candidate.record.x3_disposition
        or ""
    ).strip().upper()
    if x3_code != "X3C":
        outcome = R1BPromotionOutcome(
            status="BLOCKED",
            record_id=candidate.record.record_id,
            durable_write_path="none",
            blocked_reason_codes=("x3_commit_authority_required",),
        )
        write_blocked_promotion_receipt(
            projection_root=Path(projection_root),
            candidate=candidate,
            outcome=outcome,
        )
        return R1BTransactionalPromotionResult(outcome, None)
    if not candidate.cache_admissible:
        outcome = R1BPromotionOutcome(
            status="BLOCKED",
            record_id=candidate.record.record_id,
            durable_write_path="none",
            blocked_reason_codes=("cache_not_admissible",),
        )
        write_blocked_promotion_receipt(
            projection_root=Path(projection_root),
            candidate=candidate,
            outcome=outcome,
        )
        return R1BTransactionalPromotionResult(outcome, None)

    commit_request, state_diffs, rollback, refresh = build_r1b_commit_bundle(candidate)
    governance = validate_commit_request_governance(commit_request)
    if not governance.valid:
        bundle = build_governance_receipt_bundle(
            commit_request=commit_request, state_diffs=state_diffs
        )
        outcome = R1BPromotionOutcome(
            status="BLOCKED",
            record_id=candidate.record.record_id,
            durable_write_path="none",
            commit_request_id=commit_request.commit_request_id,
            blocked_reason_codes=governance.reason_codes,
            missing_contract_fields=governance.missing_fields,
            governance_receipt=governance_receipt_with_l5_packet(
                bundle.to_dict(), candidate
            ),
        )
        write_blocked_promotion_receipt(
            projection_root=Path(projection_root),
            candidate=candidate,
            outcome=outcome,
        )
        return R1BTransactionalPromotionResult(outcome, None)

    gw.register_candidate(
        candidate=candidate,
        projection_root=projection_root,
        artifact_dir=artifact_dir,
    )
    commit_receipt, blocked_receipt, _pending = gw.commit(
        commit_request=commit_request,
        state_diffs=state_diffs,
        rollback_plan=rollback,
        refresh_plan=refresh,
    )
    if commit_receipt is None:
        blocked_codes = tuple(
            getattr(blocked_receipt, "blocked_reason_codes", ()) or ()
        )
        bundle = build_governance_receipt_bundle(
            commit_request=commit_request,
            state_diffs=state_diffs,
            blocked_receipt=blocked_receipt,
        )
        outcome = R1BPromotionOutcome(
            status="BLOCKED",
            record_id=candidate.record.record_id,
            durable_write_path="none",
            commit_request_id=commit_request.commit_request_id,
            blocked_commit_receipt_id=str(
                getattr(blocked_receipt, "blocked_commit_receipt_id", "") or ""
            ),
            blocked_reason_codes=blocked_codes,
            governance_receipt=governance_receipt_with_l5_packet(
                bundle.to_dict(), candidate
            ),
        )
        write_blocked_promotion_receipt(
            projection_root=Path(projection_root),
            candidate=candidate,
            outcome=outcome,
        )
        return R1BTransactionalPromotionResult(outcome, None)

    bundle = build_governance_receipt_bundle(
        commit_request=commit_request,
        state_diffs=state_diffs,
        commit_receipt=commit_receipt,
    )
    outcome = R1BPromotionOutcome(
        status="ADMITTED",
        record_id=candidate.record.record_id,
        durable_write_path="UWG→L4(transactional)",
        commit_request_id=commit_request.commit_request_id,
        uwg_commit_receipt_id=commit_receipt.commit_receipt_id,
        governance_receipt=governance_receipt_with_l5_packet(
            bundle.to_dict(), candidate
        ),
        uwg_commit_receipt=asdict(commit_receipt),
    )
    validation_receipt = gw.get_validation_receipt(
        commit_receipt.uwg_validation_receipt_ref
    )
    if validation_receipt is None:
        raise RuntimeError("transactional commit missing validation receipt")
    _materialize_commit_evidence(
        artifact_dir=artifact_dir,
        candidate=candidate,
        commit_request=commit_request,
        state_diffs=state_diffs,
        validation=validation_receipt,
        commit_receipt=commit_receipt,
    )
    projection = project_r1b_commit_from_outbox(
        gateway=gw,
        candidate=candidate,
        outcome=outcome,
        projection_root=projection_root,
        artifact_dir=artifact_dir,
        section_id=section_id,
        run_id=run_id or candidate.source_run_id,
        raw_request=raw_request,
    )
    return R1BTransactionalPromotionResult(outcome, projection)


__all__ = ["R1BTransactionalPromotionResult", "promote_r1b_transactionally"]
