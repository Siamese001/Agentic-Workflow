"""Three-state activation machine for the C3 heal-classifier.

States:
  ABSENT  — no artifact configured; heuristic-only; no ML inference attempted
  SHADOW  — artifact loaded; heuristic routing; ML scoring runs for telemetry only
  ACTIVE  — artifact loaded; ML tier drives routing; rollback monitor engaged

ACTIVE requires a second governed promotion:
  1. artifact_dir/activation_record.json with activation_mode="active"
  2. artifact_hash in the record must match the verified model_version_hash
  3. Evidence in the record must pass check_activation_criteria()

Without a valid record the machine stays in SHADOW (safe default).
The activation_record.json is written by the governed activation workflow after
UWG approval of the second promotion packet; it must NOT be created ad hoc.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

from .activation_criteria import (
    ActivationCriteria,
    CriteriaEvidence,
    CriteriaResult,
    check_activation_criteria,
)


ACTIVATION_RECORD_FILENAME: str = "activation_record.json"


class ActivationMode(Enum):
    """Runtime activation state of the heal-classifier."""

    ABSENT = auto()   # No artifact; heuristic-only
    SHADOW = auto()   # Artifact present; heuristic routing; ML telemetry-only
    ACTIVE = auto()   # Artifact present; ML tier drives routing


@dataclass
class ActivationRecord:
    """Deserialized contents of activation_record.json.

    Written by the governed activation workflow after UWG approval of the
    second promotion packet.  Must not be created ad hoc outside the
    tools/heal_classifier promotion workflow.
    """

    activation_mode: str        # "shadow" or "active"
    artifact_hash: str          # Must equal verified model_version_hash
    shadow_event_count: int = 0
    divergence_rate: float = 0.0
    repair_success_rate: float = 1.0
    ood_rate: float = 0.0
    latency_p99_us: int = 0
    manual_review_passed: bool = False
    replay_binding_present: bool = False


def load_activation_record(artifact_dir: Path) -> ActivationRecord | None:
    """Read activation_record.json; return None if absent or malformed."""
    record_path = artifact_dir / ACTIVATION_RECORD_FILENAME
    if not record_path.exists():
        return None
    try:
        data = json.loads(record_path.read_text(encoding="utf-8"))
        return ActivationRecord(
            activation_mode=str(data.get("activation_mode", "shadow")),
            artifact_hash=str(data.get("artifact_hash", "")),
            shadow_event_count=int(data.get("shadow_event_count", 0)),
            divergence_rate=float(data.get("divergence_rate", 0.0)),
            repair_success_rate=float(data.get("repair_success_rate", 1.0)),
            ood_rate=float(data.get("ood_rate", 0.0)),
            latency_p99_us=int(data.get("latency_p99_us", 0)),
            manual_review_passed=bool(data.get("manual_review_passed", False)),
            replay_binding_present=bool(data.get("replay_binding_present", False)),
        )
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def resolve_activation_mode(
    artifact_dir: Path | None,
    mvh: str,
    criteria: ActivationCriteria | None = None,
) -> tuple[ActivationMode, CriteriaResult | None]:
    """Determine the correct activation mode given an artifact directory and hash.

    Safe-default logic (fails toward SHADOW, never toward unauthorized ACTIVE):
      - artifact_dir is None           → ABSENT
      - mvh is empty (load failed)     → SHADOW
      - No activation_record.json      → SHADOW (implicit first activation)
      - Record activation_mode != "active"       → SHADOW
      - Record artifact_hash != verified mvh     → SHADOW (hash mismatch)
      - Criteria evidence check fails            → SHADOW
      - All criteria pass                        → ACTIVE

    Args:
        artifact_dir: Path to the artifact package directory.
        mvh:          Verified model_version_hash from load_artifact().
        criteria:     Optional override for activation thresholds.

    Returns:
        (ActivationMode, CriteriaResult | None) — CriteriaResult is None unless
        an active-mode record was found and evaluated.
    """
    if artifact_dir is None:
        return ActivationMode.ABSENT, None

    if not mvh:
        return ActivationMode.SHADOW, None

    record = load_activation_record(artifact_dir)
    if record is None:
        return ActivationMode.SHADOW, None

    if record.activation_mode != "active":
        return ActivationMode.SHADOW, None

    if record.artifact_hash != mvh:
        return ActivationMode.SHADOW, None

    evidence = CriteriaEvidence(
        shadow_event_count=record.shadow_event_count,
        divergence_rate=record.divergence_rate,
        repair_success_rate=record.repair_success_rate,
        ood_rate=record.ood_rate,
        latency_p99_us=record.latency_p99_us,
        artifact_hash_valid=True,
        replay_binding_present=record.replay_binding_present,
        manual_review_passed=record.manual_review_passed,
    )

    result = check_activation_criteria(evidence, criteria)
    if result.passed:
        return ActivationMode.ACTIVE, result
    return ActivationMode.SHADOW, result
