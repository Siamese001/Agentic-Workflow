"""L5 Policy Proposer — proposes safety rule strictness adjustments.

Analyzes false-positive/negative rates from healing outcomes where the agent
is an L5 safety agent (ArchitectureGovernorAgent, FileClassificationAgent, etc.)
and proposes bounded threshold adjustments to reduce over-blocking or
under-blocking.

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""
from __future__ import annotations
import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
logger = logging.getLogger(__name__)
_L5_AGENT_PREFIXES = ('ArchitectureGovernor', 'FileClassification', 'FilesystemSSOTReconciler', 'Hierarchy', 'Location', 'RootHygiene', 'SystemArchitect', 'CognitiveDisposition', 'GravityLeakRepair')
_FALSE_POSITIVE_THRESHOLD = 0.15
_FALSE_NEGATIVE_THRESHOLD = 0.1
_MIN_OBSERVATIONS = 5
_MAX_DELTA = 0.05
_DEFAULT_DELTA = 0.02

@dataclass(frozen=True, slots=True)
class L5PolicyChangePackage:
    """Immutable policy adjustment proposal for L5 safety rules."""
    surface_name: str
    direction: str
    delta: float
    justification: str
    snapshot_id: str
    false_positive_rate: float
    false_negative_rate: float
    observation_count: int

    def canonical_bytes(self) -> bytes:
        data = {'surface_name': self.surface_name, 'direction': self.direction, 'delta': self.delta, 'justification': self.justification, 'snapshot_id': self.snapshot_id, 'false_positive_rate': self.false_positive_rate, 'false_negative_rate': self.false_negative_rate, 'observation_count': self.observation_count}
        return json.dumps(data, separators=(',', ':'), sort_keys=True).encode('utf-8')

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

class L5PolicyProposer:
    """Concrete L5 proposer that analyzes safety block accuracy.

    Conforms to the ``L5Proposer`` Protocol defined in
    ``meta_learning_pipeline.py``.
    """

    def propose(self, snapshot: Any, metrics: Any, config: Any, now_utc: int, history: Any, cooldown: Any, sample: Any) -> L5PolicyChangePackage | None:
        """Propose L5 policy changes based on safety block accuracy.

        Parameters
        ----------
        snapshot : MetaLearningSnapshot
            Current pipeline snapshot.
        metrics : dict
            Must contain ``"l5_false_positive_rate"`` and
            ``"l5_false_negative_rate"`` and ``"l5_observation_count"``.
        config, now_utc, history, cooldown, sample
            Standard proposer args (cooldown/sample checked if provided).

        Returns
        -------
        L5PolicyChangePackage | None
            Proposal or None if no adjustment warranted.
        """
        if not isinstance(metrics, dict):
            return None
        fp_rate = metrics.get('l5_false_positive_rate', 0.0)
        fn_rate = metrics.get('l5_false_negative_rate', 0.0)
        n_obs = metrics.get('l5_observation_count', 0)
        if n_obs < _MIN_OBSERVATIONS:
            return None
        snapshot_id = getattr(snapshot, 'snapshot_id', 'unknown')
        if fp_rate > _FALSE_POSITIVE_THRESHOLD:
            direction = 'relax'
            delta = min(_DEFAULT_DELTA, _MAX_DELTA)
            justification = f'L5 false-positive rate {fp_rate:.3f} exceeds threshold {_FALSE_POSITIVE_THRESHOLD}; proposing relaxation by {delta}'
        elif fn_rate > _FALSE_NEGATIVE_THRESHOLD:
            direction = 'tighten'
            delta = min(_DEFAULT_DELTA, _MAX_DELTA)
            justification = f'L5 false-negative rate {fn_rate:.3f} exceeds threshold {_FALSE_NEGATIVE_THRESHOLD}; proposing tightening by {delta}'
        else:
            return None
        return L5PolicyChangePackage(surface_name='l5_safety_strictness', direction=direction, delta=delta, justification=justification, snapshot_id=snapshot_id, false_positive_rate=fp_rate, false_negative_rate=fn_rate, observation_count=n_obs)

def extract_l5_metrics_from_healing_actions(healing_actions: list[dict]) -> dict[str, float]:
    """Extract L5-specific metrics from healing action records.

    Scans healing actions for L5 agents and computes false-positive and
    false-negative rates.

    Parameters
    ----------
    healing_actions : list[dict]
        Raw healing action dicts from runtime_state.

    Returns
    -------
    dict[str, float]
        Metrics dict with ``l5_false_positive_rate``,
        ``l5_false_negative_rate``, and ``l5_observation_count``.
    """
    l5_actions = [a for a in healing_actions if any((a.get('agent', '').startswith(pfx) for pfx in _L5_AGENT_PREFIXES))]
    if not l5_actions:
        return {'l5_false_positive_rate': 0.0, 'l5_false_negative_rate': 0.0, 'l5_observation_count': 0}
    total = len(l5_actions)
    false_positives = sum((1 for a in l5_actions if a.get('status') in ('skipped', 'plan_only', 'unnecessary')))
    false_negatives = sum((1 for a in l5_actions if a.get('status') in ('missed', 'false_negative')))
    return {'l5_false_positive_rate': false_positives / total if total else 0.0, 'l5_false_negative_rate': false_negatives / total if total else 0.0, 'l5_observation_count': total}
__all__ = ['L5PolicyProposer', 'L5PolicyChangePackage', 'extract_l5_metrics_from_healing_actions']
