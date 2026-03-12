"""Addendum 5.1: Meta-Learning Stage Barrier Enforcer.

Enforces strict stage ordering:
    S1 audit → S2 telemetry → S3 config → S4 snapshot →
    S5 RCA → S6 propose → S7 validate → S8 intake → S9 commit

Rule: Only S9 outputs may modify L0 routing or L1 weights.
"""
from __future__ import annotations
import logging
from enum import IntEnum
from agentic_core.L5_safety.types.hardening_errors import RuntimePolicyMutationViolation
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
logger = logging.getLogger(__name__)

class MetaLearningStage(IntEnum):
    S1_AUDIT = 1
    S2_TELEMETRY = 2
    S3_CONFIG = 3
    S4_SNAPSHOT = 4
    S5_RCA = 5
    S6_PROPOSE = 6
    S7_VALIDATE = 7
    S8_INTAKE = 8
    S9_COMMIT = 9
_STAGE_NAMES = {MetaLearningStage.S1_AUDIT: 'audit', MetaLearningStage.S2_TELEMETRY: 'telemetry', MetaLearningStage.S3_CONFIG: 'config', MetaLearningStage.S4_SNAPSHOT: 'snapshot', MetaLearningStage.S5_RCA: 'RCA', MetaLearningStage.S6_PROPOSE: 'propose', MetaLearningStage.S7_VALIDATE: 'validate', MetaLearningStage.S8_INTAKE: 'intake', MetaLearningStage.S9_COMMIT: 'commit'}

class StageBarrierEnforcer:
    """Tracks current meta-learning stage and enforces ordering invariants.

    Usage:
        enforcer = StageBarrierEnforcer()
        enforcer.advance_to(MetaLearningStage.S1_AUDIT)
        # ...
        enforcer.advance_to(MetaLearningStage.S9_COMMIT)
        enforcer.assert_config_mutation_allowed()  # only passes at S9
    """

    def __init__(self) -> None:
        self._current: int = 0

    @property
    def current_stage(self) -> int:
        return self._current

    def advance_to(self, stage: MetaLearningStage) -> None:
        """Advance to the next stage. Raises if attempting to go backwards."""
        if stage <= self._current:
            raise RuntimePolicyMutationViolation(f'Stage barrier violated: cannot move from S{self._current} to S{stage.value}. Stages must advance strictly forward.')
        logger.debug('MetaLearning stage: S%d → S%d (%s)', self._current, stage.value, _STAGE_NAMES.get(stage, 'unknown'))
        self._current = stage.value

    def assert_config_mutation_allowed(self) -> None:
        """Raise unless we are at S9 commit — only S9 may modify L0/L1."""
        if self._current < MetaLearningStage.S9_COMMIT:
            raise RuntimePolicyMutationViolation(f'Config mutation blocked: current stage is S{self._current}. Only S9 (commit) may modify L0 routing or L1 weights.')

    def is_commit_stage(self) -> bool:
        return self._current >= MetaLearningStage.S9_COMMIT

    def reset(self) -> None:
        self._current = 0
__all__ = ['StageBarrierEnforcer', 'MetaLearningStage']
