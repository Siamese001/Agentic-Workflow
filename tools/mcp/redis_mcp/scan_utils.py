"""Reusable SCAN helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .client import redis_lib


@dataclass(frozen=True)
class RedisScanResult:
    """Normalized result for SCAN-based traversals."""

    keys: list[str]
    scanned_keys: int
    cursor_complete: bool
    result_limit_hit: bool
    scan_cap_hit: bool

    @property
    def truncated(self) -> bool:
        return self.result_limit_hit or self.scan_cap_hit or not self.cursor_complete


def scan_keys(
    client: redis_lib.Redis,
    *,
    match: str | None = None,
    count: int = 100,
    result_limit: int | None = None,
    scan_cap: int | None = None,
) -> RedisScanResult:
    """Collect keys via Redis SCAN with optional response and traversal caps."""
    results: list[str] = []
    cursor = 0
    scanned_keys = 0
    result_limit_hit = False
    scan_cap_hit = False
    cursor_complete = False

    while True:
        cursor, keys = client.scan(cursor, match=match, count=count)
        batch = list(keys)
        scanned_keys += len(batch)

        if result_limit is None:
            results.extend(batch)
        else:
            remaining = max(result_limit - len(results), 0)
            if remaining > 0:
                results.extend(batch[:remaining])
            if len(results) >= result_limit:
                result_limit_hit = True
                if cursor == 0:
                    cursor_complete = True
                break

        if cursor == 0:
            cursor_complete = True
            break

        if scan_cap is not None and scanned_keys >= scan_cap:
            scan_cap_hit = True
            break

    return RedisScanResult(
        keys=results,
        scanned_keys=scanned_keys,
        cursor_complete=cursor_complete,
        result_limit_hit=result_limit_hit,
        scan_cap_hit=scan_cap_hit,
    )
