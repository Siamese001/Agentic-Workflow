"""R2: ADG Cache Loader — load ScanResult from cache or trigger fresh scan.

Cache key: commit_sha + scanner_version + schema_version + python_ast_version
Cache is invalidated when any key dimension changes.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)
_CACHE_PATH = Path("artifacts/adg/scan_result_cache.json")


def _get_commit_sha() -> str:
    """Read HEAD commit SHA from git, or return empty string on failure."""
    try:
        import subprocess

        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=DEFAULT_TIMEOUT
        )
        return r.stdout.strip() if r.returncode == 0 else ""
    # guardian: allow-silent-swallow
    except Exception:
        return ""


def _cache_key(scanner_version: str, schema_version: str) -> str:
    commit = _get_commit_sha()
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    return f"{commit}::{scanner_version}::{schema_version}::{py_ver}"


def _is_cache_valid(cached: dict) -> bool:
    """Return True iff the cached data matches current cache key dimensions."""
    from agentic_core.adg.extraction.static_scanner import _SCANNER_VERSION, _SCHEMA_VERSION

    expected_key = _cache_key(_SCANNER_VERSION, _SCHEMA_VERSION)
    return cached.get("_cache_key") == expected_key


def load_or_scan(repo_root: str | None = None, cache_path: Path | None = None) -> ScanResult:
    """R2: Load ADG ScanResult from cache if valid, otherwise run fresh scan.

    Cache key: commit_sha + scanner_version + schema_version + python_ast_version.
    """
    from agentic_core.adg.extraction.static_scanner import (
        _SCANNER_VERSION,
        _SCHEMA_VERSION,
        ADGStaticScanner,
        ScanResult,
    )

    cache = cache_path or _CACHE_PATH
    if cache.exists():
        try:
            cached = json.loads(cache.read_text(encoding="utf-8"))
            if _is_cache_valid(cached):
                logger.info("ADG cache hit: %s", cache)
                return ScanResult.from_dict(cached)
            logger.info("ADG cache miss (key changed): %s", cache)
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.warning("ADG cache read error (%s): %s — running fresh scan", cache, exc)
    root = Path(repo_root) if repo_root else Path.cwd()
    scanner = ADGStaticScanner(repo_root=root)
    result = scanner.scan()
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        payload["_cache_key"] = _cache_key(_SCANNER_VERSION, _SCHEMA_VERSION)
        cache.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("ADG cache written: %s (%d edges)", cache, len(result.edges))
    # guardian: allow-silent-swallow
    except Exception as exc:
        logger.warning("ADG cache write failed: %s", exc)
    return result


def invalidate_cache(cache_path: Path | None = None) -> None:
    """Force-invalidate the ADG cache by deleting the cache file."""
    cache = cache_path or _CACHE_PATH
    if cache.exists():
        cache.unlink()
        logger.info("ADG cache invalidated: %s", cache)


__all__ = ["load_or_scan", "invalidate_cache"]
