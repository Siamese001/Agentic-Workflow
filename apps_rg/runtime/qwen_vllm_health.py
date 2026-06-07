"""apps_rg-local Qwen/vLLM health settings and probe utilities."""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Final

_LOGGER = logging.getLogger(__name__)

VLLM_BASE_URL: Final[str] = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
QWEN_LOCAL_MODEL_ID: Final[str] = os.getenv(
    "VLLM_MODEL_NAME",
    "Qwen/Qwen2.5-32B-Instruct-AWQ",
)
QWEN_LOCAL_MAX_MODEL_LEN: Final[int] = int(os.getenv("VLLM_MAX_MODEL_LEN", "24576"))

_DEFAULT_TTL_SECONDS: float = float(os.getenv("VLLM_HEALTH_PROBE_TTL_SECONDS", "5.0"))
_DEFAULT_HTTP_TIMEOUT: float = float(os.getenv("VLLM_HEALTH_PROBE_TIMEOUT_SECONDS", "1.5"))

_HEALTHY: Final[str] = "healthy"
_UNHEALTHY: Final[str] = "unhealthy"
_UNKNOWN: Final[str] = "unknown"


@dataclass(frozen=True)
class VLLMHealth:
    """Snapshot of a local vLLM server `/v1/models` probe."""

    status: str
    model_id: str
    latency_ms: float
    checked_at: float
    error: str | None = None

    @property
    def is_healthy(self) -> bool:
        return self.status == _HEALTHY


class _ProbeCache:
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
    except TimeoutError as exc:
        return VLLMHealth(
            status=_UNHEALTHY,
            model_id="",
            latency_ms=(time.time() - started) * 1000.0,
            checked_at=time.time(),
            error=f"timeout:{exc!s}",
        )
    except (OSError, ValueError, TypeError) as exc:
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
    """Return a cached or fresh health snapshot for the local vLLM server."""

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
            "apps_rg vllm health probe: status=%s url=%s error=%s latency_ms=%.1f",
            health.status,
            url,
            health.error,
            health.latency_ms,
        )
    return health


def reset_cache_for_tests() -> None:
    _CACHE.clear()


__all__ = [
    "QWEN_LOCAL_MAX_MODEL_LEN",
    "QWEN_LOCAL_MODEL_ID",
    "VLLMHealth",
    "VLLM_BASE_URL",
    "probe",
    "reset_cache_for_tests",
]
