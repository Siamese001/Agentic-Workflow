"""Strict, process-shared, transactional UWG gateway for apps_rg R1B."""

from __future__ import annotations

import os
import tempfile
import threading
from dataclasses import replace
from pathlib import Path
from typing import Any

from agentic_core.L4_state.contracts.records import stamp_digest
from agentic_core.L4_state.storage.sqlite_backend import SQLiteL4Backend
from agentic_core.L4_state.uwg.durable_write_gateway import compute_state_diffs_digest
from agentic_core.L4_state.uwg.transactional_durable_write_gateway import (
    TransactionalDurableWriteGateway,
)
from apps_rg.cache.r1b_commit_authority import validate_r1b_commit_request_evidence


class R1BStrictUWGGateway(TransactionalDurableWriteGateway):
    """R1B gateway with evidence verification and canonical L4 persistence."""

    def __init__(
        self,
        *,
        canonical_backend: SQLiteL4Backend | None = None,
        **kwargs: Any,
    ) -> None:
        backend = canonical_backend
        if backend is None:
            from agentic_core.L4_state.storage.sqlite_backend import get_default_backend

            backend = get_default_backend()
        if backend is None:
            backend = SQLiteL4Backend(
                Path(tempfile.gettempdir())
                / f"agentic-r1b-{os.getpid()}-{id(self)}.sqlite3"
            )
        super().__init__(canonical_backend=backend, **kwargs)
        self._r1b_validation_cache: dict[tuple[str, ...], Any] = {}
        self._r1b_validation_lock = threading.RLock()

    @staticmethod
    def _r1b_validation_key(
        commit_request: Any,
        state_diffs: list[Any],
        rollback_plan: Any,
        refresh_plan: Any,
    ) -> tuple[str, ...]:
        return (
            str(getattr(commit_request, "commit_request_id", "") or ""),
            str(getattr(commit_request, "deterministic_digest", "") or ""),
            compute_state_diffs_digest(state_diffs),
            str(getattr(rollback_plan, "rollback_plan_id", "") or ""),
            str(getattr(refresh_plan, "refresh_plan_id", "") or ""),
        )

    def register_candidate(
        self,
        *,
        candidate: Any,
        projection_root: Path | str | None = None,
        artifact_dir: Path | str | None = None,
    ) -> None:
        commit_request_id = f"r1b_cr:{candidate.record.record_id}"
        payload = {
            "schema_version": "apps_rg.r1b_canonical_state.v1",
            "record": candidate.record.to_dict(),
            "chunks": [row.to_dict() for row in candidate.chunks],
            "post_exit_eligibility": candidate.post_exit_eligibility,
            "source_run_id": candidate.source_run_id,
            "x3_disposition_ref": candidate.x3_disposition_ref,
            "proof_eligibility_ref": candidate.proof_eligibility_ref,
        }
        self.stage_state_payload(
            commit_request_id=commit_request_id,
            state_diff_id=f"r1b_sd:{candidate.record.record_id}",
            payload=payload,
        )
        self.stage_projection_context(
            commit_request_id=commit_request_id,
            context={
                "app_id": "apps_rg",
                "record_id": candidate.record.record_id,
                "projection_root": str(projection_root or ""),
                "artifact_dir": str(artifact_dir or ""),
                "source_run_id": candidate.source_run_id,
            },
        )

    def _validate(
        self,
        commit_request: Any,
        state_diffs: list[Any],
        rollback_plan: Any,
        refresh_plan: Any,
    ) -> Any:
        key = self._r1b_validation_key(
            commit_request, state_diffs, rollback_plan, refresh_plan
        )
        with self._r1b_validation_lock:
            cached = self._r1b_validation_cache.get(key)
            if cached is not None:
                return cached
            validation = super()._validate(
                commit_request, state_diffs, rollback_plan, refresh_plan
            )
            extra_failed, extra_reasons = validate_r1b_commit_request_evidence(
                commit_request
            )
            if extra_failed or extra_reasons:
                validation = replace(
                    validation,
                    validation_status="FAIL",
                    failed_rules=tuple(
                        dict.fromkeys((*validation.failed_rules, *extra_failed))
                    ),
                    reason_codes=tuple(
                        dict.fromkeys((*validation.reason_codes, *extra_reasons))
                    ),
                    deterministic_digest="",
                )
                validation = stamp_digest(validation)
                self._validations[validation.uwg_validation_receipt_id] = validation
            self._r1b_validation_cache[key] = validation
            return validation


_DEFAULT_R1B_GATEWAY: R1BStrictUWGGateway | None = None
_DEFAULT_R1B_GATEWAY_LOCK = threading.Lock()


def get_r1b_strict_gateway() -> R1BStrictUWGGateway:
    """Return the process-shared R1B gateway and shared canonical backend."""

    global _DEFAULT_R1B_GATEWAY  # noqa: PLW0603
    with _DEFAULT_R1B_GATEWAY_LOCK:
        if _DEFAULT_R1B_GATEWAY is None:
            _DEFAULT_R1B_GATEWAY = R1BStrictUWGGateway()
        return _DEFAULT_R1B_GATEWAY


def reset_r1b_strict_gateway() -> None:
    """Reset only the process object; durable canonical state is retained."""

    global _DEFAULT_R1B_GATEWAY  # noqa: PLW0603
    with _DEFAULT_R1B_GATEWAY_LOCK:
        _DEFAULT_R1B_GATEWAY = R1BStrictUWGGateway()


__all__ = [
    "R1BStrictUWGGateway",
    "get_r1b_strict_gateway",
    "reset_r1b_strict_gateway",
]
