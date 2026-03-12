from __future__ import annotations
import datetime
from dataclasses import dataclass
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class StaleDataViolation(Exception):
    """Raised when data is served that is older than the freshness policy allows."""

    def __init__(self, data_timestamp: datetime.datetime, policy_max_age: int):
        self.data_timestamp = data_timestamp
        self.policy_max_age = policy_max_age
        super().__init__(f'Data with timestamp {data_timestamp} is stale. Policy requires data to be no older than {policy_max_age} seconds.')

@dataclass(frozen=True)
class FreshnessPolicy:
    """Defines the freshness window for a piece of data."""
    max_age_seconds: int

@dataclass(frozen=True)
class VersionedData:
    """Represents a piece of data with a timestamp for freshness validation."""
    content: Any
    timestamp: datetime.datetime

def validate_freshness(data: VersionedData, policy: FreshnessPolicy) -> None:
    """
    Validates that a piece of versioned data is not stale.

    This function enforces Guarantee #11 (Fresh data only at runtime) by comparing
    the data's timestamp against a configurable freshness window. It is a critical
    sovereign gate in L4 to prevent the use of outdated context or knowledge.

    Args:
        data: The versioned data to validate.
        policy: The freshness policy to apply.

    Raises:
        StaleDataViolation: If the data's timestamp is older than the allowed max age.
    """
    now = datetime.datetime.utcnow()
    allowed_age = datetime.timedelta(seconds=policy.max_age_seconds)
    if now - data.timestamp > allowed_age:
        raise StaleDataViolation(data_timestamp=data.timestamp, policy_max_age=policy.max_age_seconds)
