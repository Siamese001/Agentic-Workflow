"""C6 Gauntlet Gate - Three-stage promotion validation.

10C-REQ-165: Gauntlet Stage 1 Shadow Replay
10C-REQ-166: Gauntlet Stage 2 Regression Pass
10C-REQ-167: Gauntlet Stage 3 SME Sign-Off
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class GauntletStage(Enum):
    """Gauntlet promotion stages."""
    SHADOW_REPLAY = auto()      # Stage 1
    REGRESSION_PASS = auto()    # Stage 2
    SME_SIGN_OFF = auto()       # Stage 3


class GauntletResult(Enum):
    """Gauntlet stage results."""
    PASS = auto()
    FAIL = auto()
    PENDING = auto()


@dataclass
class StageStatus:
    """Status of a gauntlet stage."""
    stage: GauntletStage
    result: GauntletResult
    evidence: dict[str, Any]
    validated_by: str
    validated_at: float


class GauntletGate:
    """C6 Gauntlet Gate.

    10C-REQ-165/166/167: Three-stage promotion pipeline.
    """

    def __init__(self) -> None:
        self._stages: dict[str, dict[GauntletStage, StageStatus]] = {}
        self._sme_registry: set[str] = set()

    def register_sme(self, sme_id: str) -> None:
        """Register authorized SME for sign-off."""
        self._sme_registry.add(sme_id)

    def submit_stage(
        self,
        rule_id: str,
        stage: GauntletStage,
        result: GauntletResult,
        evidence: dict[str, Any],
        validator: str,
        timestamp: float,
    ) -> StageStatus:
        """Submit stage result for a rule."""
        # Validate SME for Stage 3
        if stage == GauntletStage.SME_SIGN_OFF and validator not in self._sme_registry:
            raise PermissionError(f"Validator {validator} not in SME registry")

        if rule_id not in self._stages:
            self._stages[rule_id] = {}

        status = StageStatus(
            stage=stage,
            result=result,
            evidence=evidence,
            validated_by=validator,
            validated_at=timestamp,
        )

        self._stages[rule_id][stage] = status
        return status

    def check_promotion_ready(self, rule_id: str) -> bool:
        """Check if rule passed all three gauntlet stages."""
        stages = self._stages.get(rule_id, {})

        required = [
            GauntletStage.SHADOW_REPLAY,
            GauntletStage.REGRESSION_PASS,
            GauntletStage.SME_SIGN_OFF,
        ]

        for stage in required:
            status = stages.get(stage)
            if not status or status.result != GauntletResult.PASS:
                return False

        return True

    def get_stage_status(self, rule_id: str, stage: GauntletStage) -> StageStatus | None:
        """Get status of specific stage for rule."""
        return self._stages.get(rule_id, {}).get(stage)

    def get_gauntlet_summary(self, rule_id: str) -> dict[str, Any]:
        """Get gauntlet summary for rule."""
        stages = self._stages.get(rule_id, {})

        return {
            "rule_id": rule_id,
            "shadow_replay": stages.get(GauntletStage.SHADOW_REPLAY, None),
            "regression_pass": stages.get(GauntletStage.REGRESSION_PASS, None),
            "sme_sign_off": stages.get(GauntletStage.SME_SIGN_OFF, None),
            "promotion_ready": self.check_promotion_ready(rule_id),
        }
