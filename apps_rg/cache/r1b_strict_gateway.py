"""Strict, process-shared UWG gateway for apps_rg R1B promotion."""

from __future__ import annotations

import threading
from dataclasses import replace
from typing import Any

from agentic_core.L4_state.contracts.records import stamp_digest
from agentic_core.L4_state.uwg.durable_write_gateway import (
    DurableWriteGateway,
    compute_state_diffs_digest,
)
from apps_rg.cache.r1b_commit_authority import validate_r1b_commit_request_evidence


class R1BStrictUWGGateway(DurableWriteGateway):
    """R1B gateway with evidence verification and stable validation receipts.

    The governed receipt emitter performs a preflight validation before calling
    ``commit``. Core ``commit`` validates again. This subclass memoizes the
    first validation result by deterministic request inputs so both operations
    reference the same receipt rather than emitting two unrelated UUID-backed
    validation receipts.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
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

    def _validate(
        self,
        commit_request: Any,
        state_diffs: list[Any],
        rollback_plan: Any,
        refresh_plan: Any,
    ) -> Any:
        key = self._r1b_validation_key(
            commit_request,
            state_diffs,
            rollback_plan,
            refresh_plan,
        )
        with self._r1b_validation_lock:
            cached = self._r1b_validation_cache.get(key)
            if cached is not None:
                return cached

            validation = super()._validate(
                commit_request,
                state_diffs,
                rollback_plan,
                refresh_plan,
            )
            extra_failed, extra_reasons = validate_r1b_commit_request_evidence(
                commit_request
            )
            if extra_failed or extra_reasons:
                validation = replace(
                    validation,
                    validation_status="FAIL",
                    failed_rules=tuple(dict.fromkeys((*validation.failed_rules, *extra_failed))),
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
    """Return the process-shared R1B gateway and therefore shared write locks."""

    global _DEFAULT_R1B_GATEWAY  # noqa: PLW0603
    with _DEFAULT_R1B_GATEWAY_LOCK:
        if _DEFAULT_R1B_GATEWAY is None:
            _DEFAULT_R1B_GATEWAY = R1BStrictUWGGateway()
        return _DEFAULT_R1B_GATEWAY


def reset_r1b_strict_gateway() -> None:
    """Reset the process-shared gateway for hermetic tests."""

    global _DEFAULT_R1B_GATEWAY  # noqa: PLW0603
    with _DEFAULT_R1B_GATEWAY_LOCK:
        _DEFAULT_R1B_GATEWAY = R1BStrictUWGGateway()


__all__ = [
    "R1BStrictUWGGateway",
    "get_r1b_strict_gateway",
    "reset_r1b_strict_gateway",
]
