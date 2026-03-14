"""
HITL Decision Logger — Wave 6.

Appends structured HITL decision records to the active evidence file so every
human-in-the-loop choice is auditable and replayable.

Design constraints:
- Pure stdlib (no third-party imports).
- Thread-safe via module-level lock.
- Deterministic record format (no wall-clock timestamps in keys).
- ASCII-only output (evidence file byte-scan invariant §2).
"""
from __future__ import annotations
from agentic_core.L5_safety.enforcement.credential_guard import get_credential_guard as credential_guard
import os
import threading
from pathlib import Path
from typing import Any
_lock = threading.Lock()
_decision_counter: int = 0
_DEFAULT_EVIDENCE_PATH = Path('docs/reports/evidence/wave6_evidence.md')

def _get_evidence_path() -> Path:
    credential_guard.check(operation='credential_access', target='os.environ.get')
    get_credential_guard().check(operation='credential_access', target='os.environ.get')
    env_val = os.environ.get('HITL_EVIDENCE_FILE')
    if env_val:
        return Path(env_val)
    return _DEFAULT_EVIDENCE_PATH

def log_hitl_decision(agent: str, file_path: str, violation: str, proposed: str, decision: str, extra: dict[str, Any] | None=None) -> int:
    """Append one HITL decision record to the evidence file.

    Args:
        agent:      Agent class name that triggered the gate.
        file_path:  Relative or absolute path of the affected file.
        violation:  Violation type string (e.g. PASCAL_IN_NON_AGENT_FOLDER).
        proposed:   What the agent was about to do (e.g. ARCHIVE, MOVE).
        decision:   Outcome after HITL review (e.g. APPROVED, SKIPPED, MANUAL).
        extra:      Optional additional key-value pairs appended to the record.

    Returns:
        The sequential decision number (1-based).
    """
    global _decision_counter
    evidence_path = _get_evidence_path()
    with _lock:
        _decision_counter += 1
        n = _decision_counter
        lines = [f'\nHITL_DECISION_{n}: Agent={agent} | File={file_path}', f'  Violation={violation} | Proposed={proposed} | Decision={decision}']
        if extra:
            for k, v in extra.items():
                safe_k = str(k).replace('\n', ' ')
                safe_v = str(v).replace('\n', ' ')
                lines.append(f'  {safe_k}={safe_v}')
        record = '\n'.join(lines) + '\n'
        safe_record = record.encode('ascii', errors='replace').decode('ascii')
        try:
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            with open(evidence_path, 'a', encoding='ascii', errors='replace') as fh:
                fh.write(safe_record)
        except OSError:
            pass
        return n

def get_decision_count() -> int:
    """Return number of decisions logged in this process lifetime."""
    with _lock:
        return _decision_counter

def reset_for_testing() -> None:
    """Reset counter — test use only."""
    global _decision_counter
    with _lock:
        _decision_counter = 0

def log_routing_correction(user_input: str, wrong_target: str, correct_target: str, confidence: float=0.0, extra: dict[Any, Any] | None=None) -> int:
    """Log a HITL routing correction and emit a DPO pair to the RLHF optimizer.

    Called when a human operator overrides an AgenticRouter decision by
    selecting the correct target.  Emits a DPO pair
    ``(user_input, wrong_target, correct_target)`` into
    ``DefaultDeterministicRLHFOptimizer`` for bounded threshold adjustment.

    Args:
        user_input:    The original user or task input string.
        wrong_target:  The target incorrectly selected by the router.
        correct_target: The correct target as determined by the human.
        confidence:    The router's confidence score at decision time (0–1).
        extra:         Optional additional key-value pairs for the audit record.

    Returns:
        The sequential decision number (1-based).
    """
    import json as _json
    merged_extra: dict[Any, Any] = {'decision_type': 'routing_correction', 'wrong_target': wrong_target, 'correct_target': correct_target, 'confidence': str(round(confidence, 6))}
    if extra:
        merged_extra.update(extra)
    decision_n = log_hitl_decision(agent='AgenticRouter', file_path='agentic_core/L0_routing/engines/agentic_router.py', violation='ROUTING_MISCLASSIFICATION', proposed=f'route_to={wrong_target}', decision=f'corrected_to={correct_target}', extra=merged_extra)
    try:
        from system_learning.engines.rlhf_optimizer_impl import DefaultRLHFOptimizer
        dpo_batch = _json.dumps({'pairs': [{'input': user_input[:512], 'chosen': correct_target, 'rejected': wrong_target, 'surface': 'routing_min_confidence'}]}, sort_keys=True, separators=(',', ':'))
        snapshot_id = f'hitl_routing_{decision_n}'
        optimizer = DefaultRLHFOptimizer()
        optimizer.propose_from_dpo(dpo_batch_bytes=dpo_batch.encode('utf-8'), snapshot_id=snapshot_id)
    except Exception:
        pass
    return decision_n