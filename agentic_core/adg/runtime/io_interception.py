"""G12 (gap): Network / I/O interception runtime.

Models external call interception, immutable response capture, and hard-fail
on un-transcripted network calls.

Data structures only — no side-effects on import.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class InterceptionOutcome(str, Enum):
    TRANSCRIPTED = "transcripted"
    HARD_FAILED = "hard_failed"
    BYPASSED = "bypassed"
    BLOCKED = "blocked"


@dataclass
class NetworkTranscript:
    """Immutable capture of a single external API response."""

    transcript_id: str = field(default_factory=lambda: f"tx-{uuid.uuid4().hex[:12]}")
    url: str = ""
    method: str = "GET"
    request_hash: str = ""
    response_hash: str = ""
    status_code: int = 0
    captured_at: float = field(default_factory=time.time)
    run_id: str = ""
    agent_id: str = ""
    immutable: bool = True

    def capture(self, url: str, method: str, request_body: str, response_body: str, status: int) -> None:
        self.url = url
        self.method = method
        self.request_hash = hashlib.sha256(request_body.encode()).hexdigest()
        self.response_hash = hashlib.sha256(response_body.encode()).hexdigest()
        self.status_code = status
        self.captured_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "transcript_id": self.transcript_id,
            "url": self.url,
            "method": self.method,
            "request_hash": self.request_hash,
            "response_hash": self.response_hash,
            "status_code": self.status_code,
            "captured_at": self.captured_at,
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "immutable": self.immutable,
        }


@dataclass
class IOInterceptionEvent:
    """Single interception event (transcripted, hard-failed, or blocked)."""

    event_id: str = field(default_factory=lambda: f"ioe-{uuid.uuid4().hex[:8]}")
    outcome: InterceptionOutcome = InterceptionOutcome.TRANSCRIPTED
    url: str = ""
    method: str = ""
    transcript_id: str = ""
    failure_reason: str = ""
    ts: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "outcome": self.outcome.value,
            "url": self.url,
            "method": self.method,
            "transcript_id": self.transcript_id,
            "failure_reason": self.failure_reason,
            "ts": self.ts,
        }


@dataclass
class IOInterceptionReport:
    """Aggregated report for all interception events in one session."""

    agent_id: str = ""
    run_id: str = ""
    events: list[IOInterceptionEvent] = field(default_factory=list)
    transcripts: list[NetworkTranscript] = field(default_factory=list)

    @property
    def transcripted_count(self) -> int:
        return sum(1 for e in self.events if e.outcome == InterceptionOutcome.TRANSCRIPTED)

    @property
    def hard_failed_count(self) -> int:
        return sum(1 for e in self.events if e.outcome == InterceptionOutcome.HARD_FAILED)

    @property
    def blocked_count(self) -> int:
        return sum(1 for e in self.events if e.outcome == InterceptionOutcome.BLOCKED)

    @property
    def total_events(self) -> int:
        return len(self.events)

    def outcomes_distribution(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for ev in self.events:
            key = ev.outcome.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "total_events": self.total_events,
            "transcripted_count": self.transcripted_count,
            "hard_failed_count": self.hard_failed_count,
            "blocked_count": self.blocked_count,
            "transcript_count": len(self.transcripts),
            "outcomes_distribution": self.outcomes_distribution(),
        }

    @property
    def summary(self) -> str:
        return (
            f"IOInterception [{self.agent_id}] — "
            f"{self.total_events} events: "
            f"{self.transcripted_count} transcripted, "
            f"{self.hard_failed_count} hard-failed, "
            f"{self.blocked_count} blocked"
        )


class IOInterceptor:
    """Runtime interceptor that enforces transcription of all external calls."""

    def __init__(self, agent_id: str, run_id: str, hard_fail_on_untranscripted: bool = True) -> None:
        self.report = IOInterceptionReport(agent_id=agent_id, run_id=run_id)
        self.hard_fail_on_untranscripted = hard_fail_on_untranscripted

    def intercept_io(
        self,
        url: str,
        method: str = "GET",
        request_body: str = "",
        response_body: str = "",
        status_code: int = 200,
    ) -> IOInterceptionEvent:
        transcript = NetworkTranscript(run_id=self.report.run_id, agent_id=self.report.agent_id)
        transcript.capture(url, method, request_body, response_body, status_code)
        self.report.transcripts.append(transcript)
        ev = IOInterceptionEvent(
            outcome=InterceptionOutcome.TRANSCRIPTED,
            url=url,
            method=method,
            transcript_id=transcript.transcript_id,
        )
        self.report.events.append(ev)
        return ev

    def transcript_response(self, url: str, response_body: str, status_code: int = 200) -> NetworkTranscript:
        transcript = NetworkTranscript(run_id=self.report.run_id, agent_id=self.report.agent_id)
        transcript.capture(url, "RESPONSE", "", response_body, status_code)
        self.report.transcripts.append(transcript)
        ev = IOInterceptionEvent(
            outcome=InterceptionOutcome.TRANSCRIPTED,
            url=url,
            method="RESPONSE",
            transcript_id=transcript.transcript_id,
        )
        self.report.events.append(ev)
        return transcript

    def hard_fail_untranscripted(self, url: str, reason: str = "untranscripted_call") -> IOInterceptionEvent:
        ev = IOInterceptionEvent(
            outcome=InterceptionOutcome.HARD_FAILED,
            url=url,
            method="UNKNOWN",
            failure_reason=reason,
        )
        self.report.events.append(ev)
        if self.hard_fail_on_untranscripted:
            raise RuntimeError(f"Hard-fail: untranscripted network call to {url!r}: {reason}")
        return ev

    def capture_response(self, url: str, response_body: str, status_code: int = 200) -> NetworkTranscript:
        return self.transcript_response(url, response_body, status_code)
