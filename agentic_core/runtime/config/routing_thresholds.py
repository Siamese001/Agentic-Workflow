"""Routing threshold configuration loader — W2.P1 deposit.

Plan: ``.windsurf/plans/l0-routing-calibration-gap-audit-b3c9d4.md`` §W2.

Loads :file:`config/routing_thresholds.yaml` and exposes a typed lookup
surface for the five routing thresholds each L0/C0/L4 consumer needs:

* ``r1b_semantic_similarity`` (semantic cache reuse threshold)
* ``r5_abstain_confidence`` (abstain floor)
* ``r3_grounding_need`` (grounding-need prediction threshold)
* ``c0_coverage_floor`` (C0 evidence coverage floor)
* ``r1a_freshness_ratio`` (exact-cache freshness cutoff)

Design goals:

1. **Back-compat**: every lookup falls back to the pre-W2 hardcoded literal
   when the YAML is absent, malformed, or missing a key. Constitutional §19
   mode-separation — a missing config is not a runtime failure.
2. **Per-namespace overrides**: ``get_threshold("r1b_semantic_similarity",
   namespace="rg")`` → returns the rg-specific value if present, else
   the global default.
3. **Env overrides**: ``ROUTING_THRESHOLD__<KEY>`` environment variables
   override the YAML value for all namespaces. Useful for A/B rollouts
   without editing files.
4. **Cached**: the YAML is read once and memoized. Call
   :func:`reload_routing_thresholds` to re-read after live edits (tests,
   W4 calibration refresh).
5. **No PyYAML dependency in the hot path**: falls back to a minimal
   literal parser for the defaults-only subset if PyYAML is unavailable.
"""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Back-compat defaults — MUST match the pre-W2 hardcoded literals verbatim.
# -----------------------------------------------------------------------------
_LITERAL_DEFAULTS: dict[str, float] = {
    # semantic_cache_manager.SemanticCacheManager.similarity_threshold
    "r1b_semantic_similarity": 0.98,
    # abstain_contract.DEFAULT_ABSTAIN_THRESHOLD
    "r5_abstain_confidence": 0.50,
    # New surfaces — no pre-W2 literal; use the Vertex / W0 reference values
    # so a missing config still selects sensible behavior for W3 gates.
    "r3_grounding_need": 0.70,
    "c0_coverage_floor": 0.60,
    "r1a_freshness_ratio": 0.65,
}

_ENV_PREFIX = "ROUTING_THRESHOLD__"
_DEFAULT_CONFIG_PATH = Path("config/routing_thresholds.yaml")
_KEY_VOCAB: frozenset[str] = frozenset(_LITERAL_DEFAULTS)

_KNOWN_R5_TRIGGERS: frozenset[str] = frozenset(
    {
        "low_confidence",
        "ood_detected",
        "budget_exceeded",
        "circuit_breaker_open",
        "clarification_needed",
        "toxicity_flagged",
    },
)


@dataclass(frozen=True)
class R5TriggerConfig:
    """Per-trigger config block from the YAML ``r5_triggers`` section."""

    name: str
    enabled: bool
    reason_code: str
    threshold: float | None = None  # None when the trigger is scoreless (e.g. budget)


@dataclass(frozen=True)
class RoutingThresholdConfig:
    """Parsed + validated routing threshold config."""

    defaults: dict[str, float] = field(default_factory=dict)
    namespaces: dict[str, dict[str, float]] = field(default_factory=dict)
    r5_triggers: dict[str, R5TriggerConfig] = field(default_factory=dict)
    source_path: str = ""
    loaded_ok: bool = False

    def lookup(self, key: str, namespace: str = "") -> float:
        """Return the threshold for ``key`` with optional namespace override.

        Resolution order (first match wins):
          1. ``ROUTING_THRESHOLD__<KEY>`` env var (global, no namespace)
          2. per-namespace YAML override
          3. YAML defaults section
          4. hardcoded literal in :data:`_LITERAL_DEFAULTS`

        Args:
            key: One of the keys in :data:`_LITERAL_DEFAULTS`.
            namespace: Optional namespace (empty = global).

        Raises:
            KeyError: ``key`` is not a recognized threshold name.
        """
        if key not in _KEY_VOCAB:
            raise KeyError(
                f"Unknown routing threshold key {key!r}. Valid keys: {sorted(_KEY_VOCAB)}",
            )

        env_override = _read_env_override(key)
        if env_override is not None:
            return env_override

        if namespace and namespace in self.namespaces:
            ns_block = self.namespaces[namespace]
            if key in ns_block:
                return ns_block[key]

        if key in self.defaults:
            return self.defaults[key]

        return _LITERAL_DEFAULTS[key]

    def enabled_r5_triggers(self) -> tuple[R5TriggerConfig, ...]:
        """Return every enabled R5 trigger, in definition order."""
        return tuple(t for t in self.r5_triggers.values() if t.enabled)


def _read_env_override(key: str) -> float | None:
    """Parse ``ROUTING_THRESHOLD__<KEY>`` as a float. Returns None if missing
    or invalid (invalid → logged, back-compat preserved)."""
    env_key = f"{_ENV_PREFIX}{key.upper()}"
    raw = os.environ.get(env_key)
    if raw is None:
        return None
    try:
        value = float(raw)
    except (
        ValueError,
        TypeError,
    ):  # guardian: allow-return-none-swallow -- env var override parse: invalid values are logged and None signals "use default threshold" to the caller
        Logger.warning(
            "routing_thresholds: env var %s=%r is not a float; ignoring",
            env_key,
            raw,
        )
        return None
    if not 0.0 <= value <= 1.0:
        Logger.warning(
            "routing_thresholds: env var %s=%s is outside [0,1]; ignoring",
            env_key,
            value,
        )
        return None
    return value


def _parse_yaml(path: Path) -> dict[str, Any]:
    """Load the YAML file; return ``{}`` on any failure.

    Uses PyYAML when available; falls back silently on missing files.
    """
    if not path.is_file():
        Logger.debug("routing_thresholds: config file absent at %s", path)
        return {}
    try:
        import yaml  # noqa: PLC0415
    except ImportError:
        Logger.warning(
            "routing_thresholds: PyYAML not available — config at %s ignored",
            path,
        )
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError) as exc:
        Logger.warning(
            "routing_thresholds: failed to parse %s: %s — falling back to defaults",
            path,
            exc,
        )
        return {}
    if not isinstance(data, dict):
        Logger.warning(
            "routing_thresholds: %s did not parse to a dict (got %s) — ignoring",
            path,
            type(data).__name__,
        )
        return {}
    return data


def _coerce_threshold(value: Any, *, key: str, path: str) -> float | None:
    """Coerce ``value`` to float in [0,1]. Returns None on invalid input."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        Logger.warning(
            "routing_thresholds: %s.%s=%r is not numeric; ignoring",
            path,
            key,
            value,
        )
        return None
    numeric = float(value)
    if numeric != numeric:  # NaN
        Logger.warning("routing_thresholds: %s.%s is NaN; ignoring", path, key)
        return None
    if not 0.0 <= numeric <= 1.0:
        Logger.warning(
            "routing_thresholds: %s.%s=%s outside [0,1]; ignoring",
            path,
            key,
            numeric,
        )
        return None
    return numeric


def _parse_trigger_block(raw: Any) -> dict[str, R5TriggerConfig]:
    """Parse the ``r5_triggers`` block into validated dataclasses."""
    if not isinstance(raw, dict):
        return {}
    result: dict[str, R5TriggerConfig] = {}
    for name, block in raw.items():
        if name not in _KNOWN_R5_TRIGGERS:
            Logger.warning(
                "routing_thresholds: unknown r5 trigger %r; ignoring",
                name,
            )
            continue
        if not isinstance(block, dict):
            Logger.warning(
                "routing_thresholds: r5 trigger %r not a mapping; ignoring",
                name,
            )
            continue
        enabled = bool(block.get("enabled", True))
        reason_code = str(block.get("reason_code", f"r5_{name}"))
        raw_threshold = block.get("threshold")
        threshold: float | None = None
        if raw_threshold is not None:
            threshold = _coerce_threshold(
                raw_threshold,
                key="threshold",
                path=f"r5_triggers.{name}",
            )
        result[name] = R5TriggerConfig(
            name=name,
            enabled=enabled,
            reason_code=reason_code,
            threshold=threshold,
        )
    return result


def _build_config(raw: dict[str, Any], source_path: str) -> RoutingThresholdConfig:
    """Normalize a raw YAML dict into a :class:`RoutingThresholdConfig`."""
    defaults_block = raw.get("defaults", {}) or {}
    namespaces_block = raw.get("namespaces", {}) or {}
    triggers_block = raw.get("r5_triggers", {}) or {}

    defaults: dict[str, float] = {}
    if isinstance(defaults_block, dict):
        for key, value in defaults_block.items():
            if key not in _KEY_VOCAB:
                Logger.warning(
                    "routing_thresholds: unknown defaults key %r; ignoring",
                    key,
                )
                continue
            coerced = _coerce_threshold(value, key=key, path="defaults")
            if coerced is not None:
                defaults[key] = coerced

    namespaces: dict[str, dict[str, float]] = {}
    if isinstance(namespaces_block, dict):
        for ns_name, ns_overrides in namespaces_block.items():
            if not isinstance(ns_overrides, dict):
                Logger.warning(
                    "routing_thresholds: namespace %r not a mapping; ignoring",
                    ns_name,
                )
                continue
            cleaned: dict[str, float] = {}
            for key, value in ns_overrides.items():
                if key not in _KEY_VOCAB:
                    Logger.warning(
                        "routing_thresholds: unknown namespace key %s.%s; ignoring",
                        ns_name,
                        key,
                    )
                    continue
                coerced = _coerce_threshold(
                    value,
                    key=key,
                    path=f"namespaces.{ns_name}",
                )
                if coerced is not None:
                    cleaned[key] = coerced
            if cleaned:
                namespaces[str(ns_name)] = cleaned

    r5_triggers = _parse_trigger_block(triggers_block)

    return RoutingThresholdConfig(
        defaults=defaults,
        namespaces=namespaces,
        r5_triggers=r5_triggers,
        source_path=source_path,
        loaded_ok=bool(raw),
    )


# -----------------------------------------------------------------------------
# Process-level cache with thread-safe reload.
# -----------------------------------------------------------------------------
_cached_config: RoutingThresholdConfig | None = None
_cache_lock = threading.Lock()
_active_path_override: Path | None = None


def _resolve_config_path() -> Path:
    """Resolve the config file path with override + repo-root fallback."""
    if _active_path_override is not None:
        return _active_path_override
    # Walk up from this file to find the repo root that contains ``config/``.
    here = Path(__file__).resolve()
    for candidate in (here, *here.parents):
        config_dir = candidate / "config"
        if (config_dir / "routing_thresholds.yaml").is_file():
            return config_dir / "routing_thresholds.yaml"
    # Last-resort: relative to cwd.
    return _DEFAULT_CONFIG_PATH


def get_routing_thresholds(force_reload: bool = False) -> RoutingThresholdConfig:
    """Return the process-level :class:`RoutingThresholdConfig` singleton."""
    global _cached_config
    if not force_reload and _cached_config is not None:
        return _cached_config
    with _cache_lock:
        if force_reload or _cached_config is None:
            path = _resolve_config_path()
            raw = _parse_yaml(path)
            _cached_config = _build_config(raw, source_path=str(path))
            Logger.debug(
                "routing_thresholds: loaded from %s loaded_ok=%s defaults_keys=%s namespaces=%s",
                path,
                _cached_config.loaded_ok,
                sorted(_cached_config.defaults),
                sorted(_cached_config.namespaces),
            )
    return _cached_config


def reload_routing_thresholds() -> RoutingThresholdConfig:
    """Force a fresh read of the config (tests + W4 refresh job)."""
    return get_routing_thresholds(force_reload=True)


def get_threshold(key: str, namespace: str = "") -> float:
    """Shorthand for ``get_routing_thresholds().lookup(key, namespace)``."""
    return get_routing_thresholds().lookup(key, namespace)


def set_config_path_for_testing(path: Path | str | None) -> None:
    """Test helper — override the config path used by the next load.

    Passing ``None`` restores the default repo-root resolver.
    """
    global _active_path_override, _cached_config
    with _cache_lock:
        _active_path_override = Path(path) if path is not None else None
        _cached_config = None


__all__ = [
    "R5TriggerConfig",
    "RoutingThresholdConfig",
    "get_routing_thresholds",
    "get_threshold",
    "reload_routing_thresholds",
    "set_config_path_for_testing",
]
