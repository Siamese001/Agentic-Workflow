from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class StaleDataViolation(Exception):
    """Raised when data is served that is older than the freshness policy allows."""

    def __init__(self, data_timestamp: datetime.datetime, policy_max_age: int):
        self.data_timestamp = data_timestamp
        self.policy_max_age = policy_max_age
        super().__init__(
            f"Data with timestamp {data_timestamp} is stale. "
            f"Policy requires data to be no older than {policy_max_age} seconds."
        )


@dataclass(frozen=True)
class FreshnessPolicy:
    """Defines the freshness window for a piece of data."""

    max_age_seconds: int


@dataclass(frozen=True)
class VersionedData:
    """Represents a piece of data with a timestamp for freshness validation."""

    content: Any
    timestamp: datetime.datetime  # ISO 8601 format in a real system


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
    # In a real system, we would use timezone-aware datetimes.
    # For this implementation, we assume UTC for all timestamps.
    now = datetime.datetime.utcnow()
    allowed_age = datetime.timedelta(seconds=policy.max_age_seconds)

    if (now - data.timestamp) > allowed_age:
        raise StaleDataViolation(data_timestamp=data.timestamp, policy_max_age=policy.max_age_seconds)

    # If no exception is raised, the data is considered fresh.
