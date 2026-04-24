"""Per-request budget envelope (ADR-038).

Resolution order at ingress E3 (first non-None wins, clamped by tenant ceiling):

    1. caller-supplied envelope (U2 API entry only)
    2. tenant default from config/runtime_budget_policy.yaml
    3. route-class default
    4. global fallback

At §5 exit, consumed values are compared against the envelope axis-by-axis.
A single axis over-budget sets ``budget_fit = False``. Severity band maps
the worst axis's overrun ratio against thresholds in the policy YAML.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover - yaml is required by many other modules
    yaml = None  # type: ignore[assignment]

_DEFAULT_POLICY_PATH = Path("config/runtime_budget_policy.yaml")


class BudgetPolicyError(ValueError):
    """Raised when the budget policy YAML is missing or malformed."""


@dataclass(frozen=True)
class BudgetEnvelope:
    """Per-request resource envelope. Any field may be None (unbounded)."""

    tokens_max: int | None = None
    latency_ms_max: int | None = None
    tool_calls_max: int | None = None
    cost_usd_max: float | None = None
    origin: str = "global_fallback"

    def as_dict(self) -> dict[str, Any]:
        return {
            "tokens_max": self.tokens_max,
            "latency_ms_max": self.latency_ms_max,
            "tool_calls_max": self.tool_calls_max,
            "cost_usd_max": self.cost_usd_max,
            "origin": self.origin,
        }


@dataclass(frozen=True)
class BudgetConsumed:
    """Per-request consumed resources as observed in the sealed trace."""

    tokens: int = 0
    latency_ms: int = 0
    tool_calls: int = 0
    cost_usd: float = 0.0


@dataclass(frozen=True)
class BudgetFit:
    """Result of comparing consumed against envelope."""

    budget_fit: bool
    per_axis: Mapping[str, bool] = field(default_factory=dict)
    worst_overrun_ratio: float = 0.0
    severity_band: str = "info"


def _axis_fit(consumed: float | None, envelope: float | None) -> tuple[bool, float]:
    """Return (fit_bool, overrun_ratio). Unbounded envelope → always fits, ratio 0."""
    if envelope is None:
        return True, 0.0
    if consumed is None:
        return True, 0.0
    if envelope <= 0:
        # Degenerate envelope: any consumption is over-budget.
        return (consumed <= 0), (float("inf") if consumed > 0 else 0.0)
    ratio = consumed / envelope
    return (ratio <= 1.0), ratio


def _severity_for_ratio(ratio: float, thresholds: Mapping[str, float]) -> str:
    critical = thresholds.get("critical_threshold", 2.00)
    high = thresholds.get("high_threshold", 1.50)
    medium = thresholds.get("medium_threshold", 1.20)
    warn = thresholds.get("warn_threshold", 1.00)
    if ratio >= critical:
        return "critical"
    if ratio >= high:
        return "high"
    if ratio >= medium:
        return "medium"
    if ratio > warn:
        return "low"
    return "info"


def check_fit(
    consumed: BudgetConsumed,
    envelope: BudgetEnvelope,
    *,
    severity_thresholds: Mapping[str, float] | None = None,
) -> BudgetFit:
    """Compare consumed against envelope; return a ``BudgetFit``."""
    axes: list[tuple[str, bool, float]] = []
    for axis, cons, env in (
        ("tokens", consumed.tokens, envelope.tokens_max),
        ("latency_ms", consumed.latency_ms, envelope.latency_ms_max),
        ("tool_calls", consumed.tool_calls, envelope.tool_calls_max),
        ("cost_usd", consumed.cost_usd, envelope.cost_usd_max),
    ):
        fit, ratio = _axis_fit(cons, env)
        axes.append((axis, fit, ratio))

    per_axis = {name: fit for name, fit, _ in axes}
    all_fit = all(fit for _, fit, _ in axes)
    worst_ratio = max((ratio for _, _, ratio in axes), default=0.0)
    thresholds = severity_thresholds or {
        "warn_threshold": 1.00,
        "medium_threshold": 1.20,
        "high_threshold": 1.50,
        "critical_threshold": 2.00,
    }
    band = _severity_for_ratio(worst_ratio, thresholds)
    return BudgetFit(
        budget_fit=all_fit,
        per_axis=per_axis,
        worst_overrun_ratio=worst_ratio,
        severity_band=band,
    )


def _load_policy(path: Path) -> Mapping[str, Any]:
    if yaml is None:
        raise BudgetPolicyError("PyYAML is required to load the budget policy")
    if not path.exists():
        raise BudgetPolicyError(f"budget policy YAML missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    if not isinstance(raw, Mapping):
        raise BudgetPolicyError(f"budget policy root must be a mapping: {path}")
    return raw


def _envelope_from_mapping(
    data: Mapping[str, Any] | None, origin: str
) -> BudgetEnvelope | None:
    if not isinstance(data, Mapping):
        return None
    return BudgetEnvelope(
        tokens_max=data.get("tokens_max"),
        latency_ms_max=data.get("latency_ms_max"),
        tool_calls_max=data.get("tool_calls_max"),
        cost_usd_max=data.get("cost_usd_max"),
        origin=origin,
    )


def _clamp_int(value: int | None, ceiling: int | None) -> int | None:
    if value is None:
        return ceiling
    if ceiling is None:
        return value
    return min(value, ceiling)


def _clamp_float(value: float | None, ceiling: float | None) -> float | None:
    if value is None:
        return ceiling
    if ceiling is None:
        return value
    return min(value, ceiling)


def resolve_envelope(
    *,
    caller_envelope: BudgetEnvelope | None = None,
    tenant: str | None = None,
    route_class: str | None = None,
    policy_path: Path | None = None,
) -> BudgetEnvelope:
    """Resolve a per-request envelope from the YAML policy.

    Precedence: caller → tenant default → route-class default → global_fallback.
    Caller-supplied values are clamped by tenant ceiling.
    """
    path = policy_path or _DEFAULT_POLICY_PATH
    policy = _load_policy(path)

    global_fallback = (
        _envelope_from_mapping(policy.get("global_fallback"), "global_fallback")
        or BudgetEnvelope(origin="global_fallback")
    )

    route_defaults: Mapping[str, Any] = policy.get("route_class_defaults", {}) or {}
    route_env = (
        _envelope_from_mapping(route_defaults.get(route_class), f"route:{route_class}")
        if route_class
        else None
    )

    tenants: Mapping[str, Any] = policy.get("tenants", {}) or {}
    tenant_key = tenant if tenant is not None else "_default"
    tenant_entry: Mapping[str, Any] = (
        tenants.get(tenant_key) or tenants.get("_default") or {}
    )
    tenant_env = _envelope_from_mapping(
        tenant_entry.get("defaults"), f"tenant:{tenant or '_default'}"
    )
    tenant_ceiling = _envelope_from_mapping(
        tenant_entry.get("ceiling"), "tenant_ceiling"
    )

    if caller_envelope is not None and tenant_ceiling is not None:
        return BudgetEnvelope(
            tokens_max=_clamp_int(
                caller_envelope.tokens_max, tenant_ceiling.tokens_max
            ),
            latency_ms_max=_clamp_int(
                caller_envelope.latency_ms_max, tenant_ceiling.latency_ms_max
            ),
            tool_calls_max=_clamp_int(
                caller_envelope.tool_calls_max, tenant_ceiling.tool_calls_max
            ),
            cost_usd_max=_clamp_float(
                caller_envelope.cost_usd_max, tenant_ceiling.cost_usd_max
            ),
            origin="caller",
        )
    if caller_envelope is not None:
        return caller_envelope

    for candidate in (tenant_env, route_env, global_fallback):
        if candidate is not None:
            return candidate
    return global_fallback


__all__ = [
    "BudgetConsumed",
    "BudgetEnvelope",
    "BudgetFit",
    "BudgetPolicyError",
    "check_fit",
    "resolve_envelope",
]
