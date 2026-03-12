"""G18 (gap): Config governance runtime.

Tracks every governed-config read and schema-validation event:
  caller → reads_governed_config → ConfigReader
  caller → validates_config_schema → GovernedConfig
  caller → caches_config → ConfigLoader

Data structures only — no side-effects on import.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConfigReadOutcome(str, Enum):
    """Outcome of a config read attempt."""

    HIT = "hit"
    MISS = "miss"
    CACHED = "cached"
    INVALID = "invalid"
    SCHEMA_FAIL = "schema_fail"


class ConfigSchemaStatus(str, Enum):
    """Result of config schema validation."""

    VALID = "valid"
    INVALID = "invalid"
    MISSING_KEY = "missing_key"
    TYPE_MISMATCH = "type_mismatch"
    EXTRA_KEYS = "extra_keys"


@dataclass
class ConfigReadEvent:
    """A single config read event."""

    event_id: str = field(default_factory=lambda: f"cre-{uuid.uuid4().hex[:12]}")
    agent_id: str = ""
    run_id: str = ""
    config_key: str = ""
    config_source: str = ""
    outcome: ConfigReadOutcome = ConfigReadOutcome.HIT
    schema_status: ConfigSchemaStatus = ConfigSchemaStatus.VALID
    read_at: float = field(default_factory=time.time)
    cached: bool = False
    validation_errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "config_key": self.config_key,
            "config_source": self.config_source,
            "outcome": self.outcome.value,
            "schema_status": self.schema_status.value,
            "read_at": self.read_at,
            "cached": self.cached,
            "validation_errors": list(self.validation_errors),
        }


@dataclass
class ConfigGovernanceReport:
    """Aggregated config governance report for a run."""

    agent_id: str
    run_id: str
    events: list[ConfigReadEvent] = field(default_factory=list)

    @property
    def total_reads(self) -> int:
        return len(self.events)

    @property
    def cached_count(self) -> int:
        return sum(1 for e in self.events if e.cached)

    @property
    def schema_fail_count(self) -> int:
        return sum(1 for e in self.events if e.schema_status != ConfigSchemaStatus.VALID)

    @property
    def unique_keys(self) -> set[str]:
        return {e.config_key for e in self.events}

    @property
    def by_outcome(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for e in self.events:
            result[e.outcome.value] = result.get(e.outcome.value, 0) + 1
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "total_reads": self.total_reads,
            "cached_count": self.cached_count,
            "schema_fail_count": self.schema_fail_count,
            "unique_key_count": len(self.unique_keys),
            "by_outcome": self.by_outcome,
            "events": [e.to_dict() for e in self.events],
        }


class ConfigGovernor:
    """G18 runtime recorder: tracks governed config reads and validations.

    Lifecycle:
        gov = ConfigGovernor(agent_id, run_id)
        event = gov.read_config("db.host", source="env")
        gov.validate_config("db.host", errors=[])
        report = gov.report
    """

    def __init__(self, agent_id: str, run_id: str) -> None:
        self._agent_id = agent_id
        self._run_id = run_id
        self._report = ConfigGovernanceReport(agent_id=agent_id, run_id=run_id)
        self._cache: dict[str, Any] = {}

    @property
    def report(self) -> ConfigGovernanceReport:
        return self._report

    def read_config(
        self,
        config_key: str,
        source: str = "env",
        outcome: ConfigReadOutcome = ConfigReadOutcome.HIT,
    ) -> ConfigReadEvent:
        """Record a config read event."""
        cached = config_key in self._cache
        # guardian: allow-config-with-logic
        if cached:
            outcome = ConfigReadOutcome.CACHED
        else:
            self._cache[config_key] = True
        event = ConfigReadEvent(
            agent_id=self._agent_id,
            run_id=self._run_id,
            config_key=config_key,
            config_source=source,
            outcome=outcome,
            cached=cached,
        )
        self._report.events.append(event)
        return event

    def validate_config(
        self,
        config_key: str,
        errors: list[str] | None = None,
        source: str = "schema",
    ) -> ConfigReadEvent:
        """Record a config schema validation event."""
        errs = errors or []
        status = ConfigSchemaStatus.VALID if not errs else ConfigSchemaStatus.INVALID
        event = ConfigReadEvent(
            agent_id=self._agent_id,
            run_id=self._run_id,
            config_key=config_key,
            config_source=source,
            outcome=ConfigReadOutcome.HIT if not errs else ConfigReadOutcome.SCHEMA_FAIL,
            schema_status=status,
            validation_errors=list(errs),
        )
        self._report.events.append(event)
        return event

    def invalidate_cache(self) -> int:
        """Clear the config cache. Returns number of keys invalidated."""
        count = len(self._cache)
        self._cache.clear()
        return count
