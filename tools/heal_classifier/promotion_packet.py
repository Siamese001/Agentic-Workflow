"""Promotion packet builder and verifier."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from .constants import ARTIFACT_FILES, PROMOTION_PACKET_FILES
from .packager import PackageMetadata
from .report_generator import ThresholdCheckResult

# INVARIANT: proposed_activation_mode for the first packet is always "shadow".
# A second distinct UWG proposal is required to move to "active".
_FIRST_PACKET_ACTIVATION_MODE = "shadow"


@dataclass
class PromotionPacketResult:
    packet_dir: Path
    promotion_record: dict
    uwg_proposal: dict
    activation_mode: str  # Always "shadow" for the first packet


class PromotionPacketBuilder:
    def build(
        self,
        artifact_meta: PackageMetadata,
        threshold_result: ThresholdCheckResult,
        packet_dir: Path,
        promotion_author: str = "offline_trainer",
        shadow_rows_analyzed: int = 0,
        shadow_divergence_rate: float = 0.0,
    ) -> PromotionPacketResult:
        packet_dir.mkdir(parents=True, exist_ok=True)

        # Copy artifact directory into packet
        artifact_dest = packet_dir / "artifact"
        if artifact_dest.exists():
            shutil.rmtree(artifact_dest)
        shutil.copytree(artifact_meta.artifact_dir, artifact_dest)

        training_meta = json.loads((artifact_dest / "training_meta.json").read_text(encoding="utf-8"))

        uwg_packet_id = f"uwg-heal-classifier-v1-{artifact_meta.model_version_hash}"

        # promotion_record.json — proposed_activation_mode invariant enforced here
        promotion_record: dict = {
            "artifact_window_end": training_meta.get("window_end_run_clock", 0.0),
            "artifact_window_start": training_meta.get("window_start_run_clock", 0.0),
            "model_version_hash": artifact_meta.model_version_hash,
            "offline_eval_passed": threshold_result.passed,
            "promotion_author": promotion_author,
            "proposed_activation_mode": _FIRST_PACKET_ACTIVATION_MODE,
            "shadow_divergence_rate": shadow_divergence_rate,
            "shadow_rows_analyzed": shadow_rows_analyzed,
            "threshold_checks": threshold_result.checks,
            "uwg_packet_id": uwg_packet_id,
        }
        (packet_dir / "promotion_record.json").write_text(
            json.dumps(promotion_record, indent=2, sort_keys=True), encoding="utf-8"
        )

        # uwg_proposal.json
        uwg_proposal: dict = {
            "artifact_name": "heal_classifier",
            "artifact_version": "v1",
            "binding_instruction": (
                "Bind model_version_hash into "
                'EnvelopeBuilder.with_ml_model_hash("heal_classifier", <model_version_hash>) '
                "at E1 startup. "
                "Set ConfidenceScorer(shadow_mode=True, "
                "expected_model_hash=<model_version_hash>)."
            ),
            "model_version_hash": artifact_meta.model_version_hash,
            "promotion_author": promotion_author,
            "promotion_readiness": threshold_result.passed,
            "proposal_type": "model_artifact_activation",
            "proposed_activation_mode": _FIRST_PACKET_ACTIVATION_MODE,
            "requires_second_proposal_for_active_mode": True,
            "uwg_packet_id": uwg_packet_id,
        }
        (packet_dir / "uwg_proposal.json").write_text(
            json.dumps(uwg_proposal, indent=2, sort_keys=True), encoding="utf-8"
        )

        return PromotionPacketResult(
            packet_dir=packet_dir,
            promotion_record=promotion_record,
            uwg_proposal=uwg_proposal,
            activation_mode=_FIRST_PACKET_ACTIVATION_MODE,
        )


def verify_promotion_packet(packet_dir: Path) -> tuple[bool, list[str]]:
    """Return (is_complete, missing_or_invalid_items)."""
    issues: list[str] = []

    for item in PROMOTION_PACKET_FILES:
        if not (packet_dir / item).exists():
            issues.append(f"missing: {item}")

    artifact_dir = packet_dir / "artifact"
    if artifact_dir.exists():
        for fname in ARTIFACT_FILES:
            if not (artifact_dir / fname).exists():
                issues.append(f"missing: artifact/{fname}")
    else:
        issues.append("missing: artifact/")

    record_path = packet_dir / "promotion_record.json"
    if record_path.exists():
        record = json.loads(record_path.read_text(encoding="utf-8"))
        mode = record.get("proposed_activation_mode")
        if mode != _FIRST_PACKET_ACTIVATION_MODE:
            issues.append(
                f"invalid: proposed_activation_mode='{mode}' (must be '{_FIRST_PACKET_ACTIVATION_MODE}')"
            )

    return len(issues) == 0, issues
