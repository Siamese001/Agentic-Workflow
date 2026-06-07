"""vLLM health probe — fast, TTL-cached liveness check for the local vLLM server.

Used by ``HealingRouter._dispatch_qwen`` (and any future caller in L2) to
preflight the Qwen tier before paying a 30s inference timeout. The probe is:

- Bounded (default 1.5s HTTP timeout)
- Cached (default 5s TTL — short enough to detect a restart, long enough to
  amortise across heal queues)
- Thread-safe (single Lock guards the cache)
- Fail-open in the sense that a probe ERROR is reported as "unknown" — the
  caller decides whether to dispatch or demote. The probe does not raise.

Plan ref: ``docs/archive/windsurf/legacy-tree/plans/qwen-confidence-routing-hardening-d4e7b1.md`` Wave 1.
"""

from __future__ import annotations

import logging
import os
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from agentic_core.L0_routing.config.model_registry import (  # guardian: allow-layer-violation -- L2 healer reads URL constant from L0 SSOT
    VLLM_BASE_URL,
)

_LOGGER = logging.getLogger(__name__)

# Default 5-second TTL: shorter than typical heal queue interarrival but
# long enough that a burst of MEDIUM dispatches share one probe.
_DEFAULT_TTL_SECONDS: float = float(os.getenv("VLLM_HEALTH_PROBE_TTL_SECONDS", "5.0"))
_DEFAULT_HTTP_TIMEOUT: float = float(os.getenv("VLLM_HEALTH_PROBE_TIMEOUT_SECONDS", "1.5"))

_HEALTHY: str = "healthy"
_UNHEALTHY: str = "unhealthy"
_UNKNOWN: str = "unknown"


@dataclass(frozen=True)
class VLLMHealth:
    """Snapshot of vLLM server health.

    Attributes:
        status: One of "healthy", "unhealthy", "unknown".
        model_id: The model id reported by the server, or "" if unknown.
        latency_ms: Probe latency in milliseconds.
        checked_at: Unix timestamp of the probe.
        error: None on healthy; short string on unhealthy/unknown.
    """

    status: str
    model_id: str
    latency_ms: float
    checked_at: float
    error: str | None = None

    @property
    def is_healthy(self) -> bool:
        """True iff the server replied within timeout with a model id."""
        return self.status == _HEALTHY


class _ProbeCache:
    """TTL cache for the most recent probe result.

    A single shared cache keyed by base URL; concurrent probes coalesce to
    one network call.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cache: dict[str, VLLMHealth] = {}

    def get_fresh(self, base_url: str, ttl: float) -> VLLMHealth | None:
        with self._lock:
            cached = self._cache.get(base_url)
        if cached is None:
            return None
        if (time.time() - cached.checked_at) > ttl:
            return None
        return cached

    def put(self, base_url: str, health: VLLMHealth) -> None:
        with self._lock:
            self._cache[base_url] = health

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()


_CACHE = _ProbeCache()


def _do_probe(base_url: str, timeout: float) -> VLLMHealth:
    """Single-shot uncached probe. Hits ``/v1/models`` (cheap, no inference)."""
    url = base_url.rstrip("/") + "/models"
    started = time.time()
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return VLLMHealth(
                    status=_UNHEALTHY,
                    model_id="",
                    latency_ms=(time.time() - started) * 1000.0,
                    checked_at=time.time(),
                    error=f"http_{resp.status}",
                )
            import json  # noqa: PLC0415 — local import keeps cold module load cheap

            body = json.loads(resp.read())
            data = body.get("data") or []
            model_id = (data[0].get("id") if data else "") or ""
            return VLLMHealth(
                status=_HEALTHY,
                model_id=model_id,
                latency_ms=(time.time() - started) * 1000.0,
                checked_at=time.time(),
                error=None,
            )
    except urllib.error.URLError as exc:
        return VLLMHealth(
            status=_UNHEALTHY,
            model_id="",
            latency_ms=(time.time() - started) * 1000.0,
            checked_at=time.time(),
            error=f"url_error:{getattr(exc, 'reason', exc)!s}",
        )
    except TimeoutError as exc:  # raised on socket timeout
        return VLLMHealth(
            status=_UNHEALTHY,
            model_id="",
            latency_ms=(time.time() - started) * 1000.0,
            checked_at=time.time(),
            error=f"timeout:{exc!s}",
        )
    except (OSError, ValueError) as exc:
        return VLLMHealth(
            status=_UNKNOWN,
            model_id="",
            latency_ms=(time.time() - started) * 1000.0,
            checked_at=time.time(),
            error=f"{type(exc).__name__}:{exc!s}",
        )


def probe(
    base_url: str | None = None,
    *,
    ttl_seconds: float | None = None,
    timeout_seconds: float | None = None,
    force_refresh: bool = False,
) -> VLLMHealth:
    """Return a cached or fresh health snapshot for the local vLLM server.

    Args:
        base_url: Override the SSOT ``VLLM_BASE_URL`` (used by tests).
        ttl_seconds: Override the default 5s TTL.
        timeout_seconds: Override the default 1.5s HTTP timeout.
        force_refresh: When True, bypass the cache and probe live.

    Returns:
        A :class:`VLLMHealth` snapshot. Never raises.
    """
    url = base_url or VLLM_BASE_URL
    ttl = ttl_seconds if ttl_seconds is not None else _DEFAULT_TTL_SECONDS
    timeout = timeout_seconds if timeout_seconds is not None else _DEFAULT_HTTP_TIMEOUT

    if not force_refresh:
        cached = _CACHE.get_fresh(url, ttl)
        if cached is not None:
            return cached

    health = _do_probe(url, timeout)
    _CACHE.put(url, health)

    if not health.is_healthy:
        _LOGGER.info(
            "vllm health probe: status=%s url=%s error=%s latency_ms=%.1f",
            health.status,
            url,
            health.error,
            health.latency_ms,
        )
    return health


def is_qwen_available(
    *,
    base_url: str | None = None,
    expected_model_substring: str = "Qwen",
) -> bool:
    """Convenience: True iff the server is healthy AND serves a Qwen model.

    Used by ``HealingRouter._dispatch_qwen`` as the preflight gate. A False
    result triggers automatic demotion to Gemini Flash (Wave 1).

    The substring match (default "Qwen") is intentionally permissive so the
    probe stays valid across model-version bumps (e.g. 14B → 32B → future).
    """
    health = probe(base_url=base_url)
    if not health.is_healthy:
        return False
    return expected_model_substring in (health.model_id or "")


def reset_cache_for_tests() -> None:
    """Clear the probe cache. Test-only; production callers should not use this."""
    _CACHE.clear()


__all__ = [
    "VLLMHealth",
    "is_qwen_available",
    "probe",
    "reset_cache_for_tests",
]
