"""Phase D.1 — ``CertificationDecisionRecord`` schema (ADR-080).

This module is **schema only**. It does not:

- evaluate certification (Phase D.2),
- write to any ledger (Phase D.3),
- execute smoke against real apps (Phase D.4),
- modify the scanner ``runtime_mode`` classification (Phase F),
- add CI gates (Phase E),
- change any app's ``runtime_certification_status``.

Every record constructed here carries
``runtime_certification_status_before == runtime_certification_status_after
== NOT_CERTIFIED``. This is enforced at construction time even when
``verdict == "certify"``: per ADR-080 §0, Phase D records *decisions*;
Phase F (out of scope here) owns scanner promotion. Until Phase F ships,
no app is certified, regardless of any decision verdict.

Field count
-----------
ADR-080 §5 narrates the record as a "17-field shape". Counting the two
``runtime_certification_status_before`` / ``runtime_certification_status_after``
columns explicitly, this implementation persists **19 fields** in the
dataclass. The discrepancy is a labelling artifact in §5; the field set
implemented here matches the §5 *table* exactly. The module avoids any
silent ambiguity by declaring this explicitly.

The 19 fields are::

    decision_id                          (1)
    generated_at_utc                     (2)
    app_name                             (3)
    route_shape                          (4)
    manifest_hash                        (5)
    evidence_kind                        (6)
    closeout_report_id                   (7)
    closeout_report_hash                 (8)
    trace_observed_n                     (9)
    trace_observed_success_n             (10)
    evidence_rate                        (11)
    wilson_lower                         (12)
    z_score                              (13)
    uplift                               (14)
    verdict                              (15)
    failure_reasons                      (16)
    next_review_utc                      (17)
    runtime_certification_status_before  (18)
    runtime_certification_status_after   (19)
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field, asdict
from typing import Tuple

# ---------------------------------------------------------------------------
# Constants — see ADR-080 §0 (Author-Gate decisions) and §5 (record shape).
# ---------------------------------------------------------------------------

NOT_CERTIFIED = "NOT_CERTIFIED"
"""Phase D records do not promote certification. Status remains
``NOT_CERTIFIED`` both before and after every decision. Promotion to
``RUNTIME_CERTIFIED`` / ``FORMAL_EXCEPTION_VERIFIED`` is Phase F's job
and explicitly out of scope for D.1."""

VERDICT_CERTIFY = "certify"
VERDICT_REJECT = "reject"
VERDICT_HOLD = "hold"
VERDICTS = frozenset({VERDICT_CERTIFY, VERDICT_REJECT, VERDICT_HOLD})

EVIDENCE_KIND_R3 = "r3"
EVIDENCE_KIND_BTC = "btc"
EVIDENCE_KIND_FORMAL_EXCEPTION = "formal_exception"
EVIDENCE_KIND_SKIPPED = "skipped"
EVIDENCE_KINDS = frozenset(
    {
        EVIDENCE_KIND_R3,
        EVIDENCE_KIND_BTC,
        EVIDENCE_KIND_FORMAL_EXCEPTION,
        EVIDENCE_KIND_SKIPPED,
    }
)

DECISION_ID_ALGORITHM = "sha256-canonical-json-v1"
"""Algorithm tag for ``compute_decision_id``. Versioned so a future
Phase D.x (e.g. four-field hash) can introduce ``v2`` without breaking
audit re-binding of historical records."""

_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
_APP_PREFIX = "apps_"


# ---------------------------------------------------------------------------
# decision_id helper — ADR-080 §0 Q5.
# ---------------------------------------------------------------------------


def compute_decision_id(
    app_name: str,
    manifest_hash: str,
    closeout_report_hash: str,
) -> str:
    """Compute the deterministic ``decision_id`` for a Phase D record.

    Returns a 64-char lowercase hex SHA-256 digest of the canonical-JSON
    serialization (sorted keys, compact separators, UTF-8 bytes) of::

        {"app_name": ..., "closeout_report_hash": ..., "manifest_hash": ...}

    Per ADR-080 §0 Q5 — JSON-with-sorted-keys is chosen over a delimiter-
    joined string for delimiter-injection safety, field-shape evolvability,
    and external auditor reproducibility.

    Raises
    ------
    TypeError
        If any argument is not a ``str``.
    ValueError
        If any argument is the empty string.
    """
    for label, value in (
        ("app_name", app_name),
        ("manifest_hash", manifest_hash),
        ("closeout_report_hash", closeout_report_hash),
    ):
        if not isinstance(value, str):
            raise TypeError(
                f"compute_decision_id: {label} must be str, got "
                f"{type(value).__name__}"
            )
        if value == "":
            raise ValueError(
                f"compute_decision_id: {label} must be a non-empty string"
            )

    payload = json.dumps(
        {
            "app_name": app_name,
            "manifest_hash": manifest_hash,
            "closeout_report_hash": closeout_report_hash,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------------------------
# Frozen dataclass — ADR-080 §5.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CertificationDecisionRecord:
    """One Phase D certification decision, as a frozen, JSON-safe row.

    See module docstring for the full 19-field enumeration. Construction
    validates every invariant from ADR-080 §5 + §0 in ``__post_init__``.
    """

    decision_id: str
    generated_at_utc: str
    app_name: str
    route_shape: str
    manifest_hash: str
    evidence_kind: str
    closeout_report_id: str
    closeout_report_hash: str
    trace_observed_n: int
    trace_observed_success_n: int
    evidence_rate: float
    wilson_lower: float
    z_score: float
    uplift: float
    verdict: str
    failure_reasons: Tuple[str, ...]
    next_review_utc: str
    runtime_certification_status_before: str = NOT_CERTIFIED
    runtime_certification_status_after: str = NOT_CERTIFIED

    def __post_init__(self) -> None:  # noqa: C901 — invariants are inherently many
        # --- string / shape invariants ----------------------------------
        if not isinstance(self.app_name, str) or not self.app_name.startswith(
            _APP_PREFIX
        ):
            raise ValueError(
                f"CertificationDecisionRecord.app_name must start with "
                f"{_APP_PREFIX!r}; got {self.app_name!r}"
            )
        if not isinstance(self.route_shape, str) or self.route_shape == "":
            raise ValueError(
                "CertificationDecisionRecord.route_shape must be a non-empty "
                "string"
            )
        if not isinstance(self.generated_at_utc, str) or self.generated_at_utc == "":
            raise ValueError(
                "CertificationDecisionRecord.generated_at_utc must be a "
                "non-empty string"
            )
        if not isinstance(self.next_review_utc, str) or self.next_review_utc == "":
            raise ValueError(
                "CertificationDecisionRecord.next_review_utc must be a "
                "non-empty string"
            )
        if not isinstance(self.closeout_report_id, str) or self.closeout_report_id == "":
            raise ValueError(
                "CertificationDecisionRecord.closeout_report_id must be a "
                "non-empty string"
            )

        # --- hash format ------------------------------------------------
        if not isinstance(self.manifest_hash, str) or not _HEX64_RE.match(
            self.manifest_hash
        ):
            raise ValueError(
                "CertificationDecisionRecord.manifest_hash must be 64 "
                "lowercase hex characters"
            )
        if not isinstance(self.closeout_report_hash, str) or not _HEX64_RE.match(
            self.closeout_report_hash
        ):
            raise ValueError(
                "CertificationDecisionRecord.closeout_report_hash must be 64 "
                "lowercase hex characters"
            )

        # --- enums ------------------------------------------------------
        if self.evidence_kind not in EVIDENCE_KINDS:
            raise ValueError(
                f"CertificationDecisionRecord.evidence_kind must be one of "
                f"{sorted(EVIDENCE_KINDS)}; got {self.evidence_kind!r}"
            )
        if self.verdict not in VERDICTS:
            raise ValueError(
                f"CertificationDecisionRecord.verdict must be one of "
                f"{sorted(VERDICTS)}; got {self.verdict!r}"
            )

        # --- counts -----------------------------------------------------
        if not isinstance(self.trace_observed_n, int) or isinstance(
            self.trace_observed_n, bool
        ):
            raise TypeError(
                "CertificationDecisionRecord.trace_observed_n must be int"
            )
        if not isinstance(self.trace_observed_success_n, int) or isinstance(
            self.trace_observed_success_n, bool
        ):
            raise TypeError(
                "CertificationDecisionRecord.trace_observed_success_n must be int"
            )
        if self.trace_observed_n < 0:
            raise ValueError(
                "CertificationDecisionRecord.trace_observed_n must be >= 0"
            )
        if self.trace_observed_success_n < 0:
            raise ValueError(
                "CertificationDecisionRecord.trace_observed_success_n must be >= 0"
            )
        if self.trace_observed_success_n > self.trace_observed_n:
            raise ValueError(
                "CertificationDecisionRecord.trace_observed_success_n must "
                "be <= trace_observed_n"
            )

        # --- rates / scores --------------------------------------------
        if not isinstance(self.evidence_rate, (int, float)) or isinstance(
            self.evidence_rate, bool
        ):
            raise TypeError(
                "CertificationDecisionRecord.evidence_rate must be float"
            )
        if not (0.0 <= float(self.evidence_rate) <= 1.0):
            raise ValueError(
                "CertificationDecisionRecord.evidence_rate must be in [0, 1]"
            )
        if not isinstance(self.wilson_lower, (int, float)) or isinstance(
            self.wilson_lower, bool
        ):
            raise TypeError(
                "CertificationDecisionRecord.wilson_lower must be float"
            )
        if not (0.0 <= float(self.wilson_lower) <= 1.0):
            raise ValueError(
                "CertificationDecisionRecord.wilson_lower must be in [0, 1]"
            )
        if not isinstance(self.z_score, (int, float)) or isinstance(
            self.z_score, bool
        ):
            raise TypeError(
                "CertificationDecisionRecord.z_score must be float"
            )
        if float(self.z_score) < 0.0:
            raise ValueError(
                "CertificationDecisionRecord.z_score must be >= 0"
            )
        if not isinstance(self.uplift, (int, float)) or isinstance(
            self.uplift, bool
        ):
            raise TypeError("CertificationDecisionRecord.uplift must be float")

        # --- failure_reasons -------------------------------------------
        if not isinstance(self.failure_reasons, tuple) or any(
            not isinstance(r, str) for r in self.failure_reasons
        ):
            raise TypeError(
                "CertificationDecisionRecord.failure_reasons must be tuple[str, ...]"
            )

        # --- Phase D non-promotion invariant (ADR-080 §0 scope) --------
        if self.runtime_certification_status_before != NOT_CERTIFIED:
            raise ValueError(
                "CertificationDecisionRecord.runtime_certification_status_before "
                f"must equal {NOT_CERTIFIED!r} in Phase D; got "
                f"{self.runtime_certification_status_before!r}"
            )
        if self.runtime_certification_status_after != NOT_CERTIFIED:
            # Even when verdict == certify, status_after stays NOT_CERTIFIED
            # in Phase D. Phase F owns scanner promotion. ADR-080 §0 + §14.
            raise ValueError(
                "CertificationDecisionRecord.runtime_certification_status_after "
                f"must equal {NOT_CERTIFIED!r} in Phase D (Phase F owns "
                f"scanner promotion); got "
                f"{self.runtime_certification_status_after!r}"
            )

        # --- decision_id derivation ------------------------------------
        expected_id = compute_decision_id(
            self.app_name, self.manifest_hash, self.closeout_report_hash
        )
        if self.decision_id != expected_id:
            raise ValueError(
                "CertificationDecisionRecord.decision_id must equal "
                "compute_decision_id(app_name, manifest_hash, "
                f"closeout_report_hash); expected {expected_id!r}, got "
                f"{self.decision_id!r}"
            )

    # ------------------------------------------------------------------
    # Serializers.
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return a JSON-safe dict view of the record.

        ``failure_reasons`` is rendered as a ``list`` for JSON-friendliness;
        the dataclass itself stores it as a tuple to preserve immutability.
        """
        d = asdict(self)
        d["failure_reasons"] = list(self.failure_reasons)
        return d

    def to_json(self) -> str:
        """Return a deterministic JSON string with sorted keys."""
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )


# ---------------------------------------------------------------------------
# Optional construction helper.
# ---------------------------------------------------------------------------


def make_certification_decision_record(
    *,
    generated_at_utc: str,
    app_name: str,
    route_shape: str,
    manifest_hash: str,
    evidence_kind: str,
    closeout_report_id: str,
    closeout_report_hash: str,
    trace_observed_n: int,
    trace_observed_success_n: int,
    evidence_rate: float,
    wilson_lower: float,
    z_score: float,
    uplift: float,
    verdict: str,
    failure_reasons: Tuple[str, ...] = (),
    next_review_utc: str,
    runtime_certification_status_before: str = NOT_CERTIFIED,
    runtime_certification_status_after: str = NOT_CERTIFIED,
) -> CertificationDecisionRecord:
    """Construct a record with ``decision_id`` computed from inputs.

    This is a thin convenience over the dataclass constructor; it does
    **not** evaluate certification (Phase D.2) — every metric, verdict,
    and failure reason must be supplied by the caller. All §5 invariants
    are still enforced via ``CertificationDecisionRecord.__post_init__``.
    """
    decision_id = compute_decision_id(
        app_name, manifest_hash, closeout_report_hash
    )
    return CertificationDecisionRecord(
        decision_id=decision_id,
        generated_at_utc=generated_at_utc,
        app_name=app_name,
        route_shape=route_shape,
        manifest_hash=manifest_hash,
        evidence_kind=evidence_kind,
        closeout_report_id=closeout_report_id,
        closeout_report_hash=closeout_report_hash,
        trace_observed_n=trace_observed_n,
        trace_observed_success_n=trace_observed_success_n,
        evidence_rate=float(evidence_rate),
        wilson_lower=float(wilson_lower),
        z_score=float(z_score),
        uplift=float(uplift),
        verdict=verdict,
        failure_reasons=tuple(failure_reasons),
        next_review_utc=next_review_utc,
        runtime_certification_status_before=runtime_certification_status_before,
        runtime_certification_status_after=runtime_certification_status_after,
    )


__all__ = [
    "NOT_CERTIFIED",
    "VERDICT_CERTIFY",
    "VERDICT_REJECT",
    "VERDICT_HOLD",
    "VERDICTS",
    "EVIDENCE_KIND_R3",
    "EVIDENCE_KIND_BTC",
    "EVIDENCE_KIND_FORMAL_EXCEPTION",
    "EVIDENCE_KIND_SKIPPED",
    "EVIDENCE_KINDS",
    "DECISION_ID_ALGORITHM",
    "compute_decision_id",
    "CertificationDecisionRecord",
    "make_certification_decision_record",
]
