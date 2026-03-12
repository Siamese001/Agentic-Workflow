"""Addendum 1.3: Healing Visibility Enforcement.

Every healing loop MUST emit a HealingAttemptEvent. Silent retries are forbidden.

Schema:
    HealingAttemptEvent:
      - trace_id
      - attempt_number
      - failure_class
      - healer_selected
      - model_used
      - outcome
"""
from __future__ import annotations
import json
import logging
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
logger = logging.getLogger(__name__)
_DEFAULT_LOG_PATH = Path('artifacts/healing/healing_events.jsonl')
_LOCK = threading.Lock()

@dataclass
class HealingAttemptEvent:
    """Single healing attempt record."""
    trace_id: str
    attempt_number: int
    failure_class: str
    healer_selected: str
    model_used: str
    outcome: str
    metadata: dict[str, Any] | None = None

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=True)

class HealingEventEmitter:
    """Emitter for healing attempt events.

    Wire into all healing orchestrators (RG, LIC, core).
    """

    def __init__(self, log_path: Path | None=None) -> None:
        self._path = log_path or _DEFAULT_LOG_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._emitted: list[HealingAttemptEvent] = []

    def emit(self, trace_id: str, attempt_number: int, failure_class: str, healer_selected: str, model_used: str, outcome: str, metadata: dict[str, Any] | None=None) -> HealingAttemptEvent:
        """Emit a healing attempt event to the log and in-memory list."""
        event = HealingAttemptEvent(trace_id=trace_id, attempt_number=attempt_number, failure_class=failure_class, healer_selected=healer_selected, model_used=model_used, outcome=outcome, metadata=metadata)
        with _LOCK:
            try:
                with open(self._path, 'a', encoding='utf-8') as f:
                    f.write(event.to_jsonl() + '\n')
            except OSError as exc:
                logger.warning('HealingEventEmitter: write failed: %s', exc)
            self._emitted.append(event)
        logger.info('HealingAttempt[%d] trace=%s healer=%s outcome=%s failure=%s', attempt_number, trace_id, healer_selected, outcome, failure_class)
        return event

    def emitted_events(self) -> list[HealingAttemptEvent]:
        """Return all events emitted in this session (in-memory only)."""
        with _LOCK:
            return list(self._emitted)
_DEFAULT_EMITTER: HealingEventEmitter | None = None

def get_healing_emitter(path: Path | None=None) -> HealingEventEmitter:
    """Return module-level singleton emitter."""
    global _DEFAULT_EMITTER
    if _DEFAULT_EMITTER is None:
        _DEFAULT_EMITTER = HealingEventEmitter(log_path=path)
    return _DEFAULT_EMITTER
__all__ = ['HealingAttemptEvent', 'HealingEventEmitter', 'get_healing_emitter']
