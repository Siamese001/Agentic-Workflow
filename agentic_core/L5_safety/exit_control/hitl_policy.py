"""L5 runtime HITL policy classifier and resolver.

Per ADR-023 §3.1, L5 owns:
- ``classify_escalation_class(envelope, policy)`` — precedence-based classification
- ``resolve_approver_pool(hitl_class, tenant, time_of_day, policy)`` — approver-pool lookup
- ``set_timeout(hitl_class, policy)`` — per-class timeout in seconds
- ``set_fallback(hitl_class, policy)`` — per-class fallback directive

Policy SSOT: ``config/runtime_hitl_policy.yaml``.

No I/O is performed at import time. Callers pass a loaded ``HitlPolicy`` instance
or call ``load_policy()`` explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from agentic_core.L5_safety.exit_control.hitl_classes import (
    CLASS_NAMES,
    HitlClass,
)

DEFAULT_POLICY_PATH = Path("config/runtime_hitl_policy.yaml")


class PolicyLoadError(ValueError):
    """Raised when the runtime HITL policy YAML is missing, malformed, or incomplete."""


@dataclass(frozen=True)
class ClassPolicy:
    """Per-class policy record derived from YAML."""

    timeout_s: int
    fallback: str
    approver_pool: str
    description: str


@dataclass(frozen=True)
class HitlPolicy:
    """Loaded runtime HITL policy snapshot.

    Immutable; callers must re-``load_policy`` to pick up changes. The
    ``policy_snapshot`` field is a caller-supplied opaque string (e.g. git sha
    + mtime) used for audit binding per ADR-023 §3.6.
    """

    version: int
    novelty_min: float
    confidence_max: float
    classes: Mapping[HitlClass, ClassPolicy]
    precedence: tuple[HitlClass, ...]
    policy_snapshot: str = ""


def _coerce_class(name: str) -> HitlClass:
    if name not in CLASS_NAMES:
        raise PolicyLoadError(f"Unknown HITL class: {name!r}")
    return HitlClass(name)


def _validate_and_build(raw: Mapping[str, Any], snapshot: str) -> HitlPolicy:
    if not isinstance(raw, Mapping):
        raise PolicyLoadError("Policy root must be a mapping.")

    version = raw.get("version")
    if version != 1:
        raise PolicyLoadError(f"Unsupported policy version: {version!r}")

    thresholds = raw.get("thresholds") or {}
    try:
        novelty_min = float(thresholds["novelty_min"])
        confidence_max = float(thresholds["confidence_max"])
    except (KeyError, TypeError, ValueError) as exc:
        raise PolicyLoadError(f"Invalid thresholds: {exc}") from exc

    classes_raw = raw.get("classes") or {}
    if not isinstance(classes_raw, Mapping) or not classes_raw:
        raise PolicyLoadError("`classes` must be a non-empty mapping.")

    classes: dict[HitlClass, ClassPolicy] = {}
    for name, entry in classes_raw.items():
        hc = _coerce_class(str(name))
        if not isinstance(entry, Mapping):
            raise PolicyLoadError(f"Class {name!r} must be a mapping.")
        try:
            classes[hc] = ClassPolicy(
                timeout_s=int(entry["timeout_s"]),
                fallback=str(entry["fallback"]),
                approver_pool=str(entry["approver_pool"]),
                description=str(entry.get("description", "")),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise PolicyLoadError(f"Class {name!r}: {exc}") from exc

    missing = set(CLASS_NAMES) - {c.value for c in classes}
    if missing:
        raise PolicyLoadError(f"Missing class policies: {sorted(missing)}")

    precedence_raw = raw.get("precedence") or []
    if not isinstance(precedence_raw, list) or not precedence_raw:
        raise PolicyLoadError("`precedence` must be a non-empty list.")
    precedence = tuple(_coerce_class(str(p)) for p in precedence_raw)

    return HitlPolicy(
        version=version,
        novelty_min=novelty_min,
        confidence_max=confidence_max,
        classes=classes,
        precedence=precedence,
        policy_snapshot=snapshot,
    )


def load_policy(
    path: Path | str | None = None,
    policy_snapshot: str = "",
) -> HitlPolicy:
    """Load and validate the runtime HITL policy YAML.

    Args:
        path: Path to policy YAML. Defaults to ``config/runtime_hitl_policy.yaml``.
        policy_snapshot: Opaque audit binding (e.g. git sha + mtime).

    Raises:
        PolicyLoadError: on missing file, unreadable YAML, or schema violations.
    """
    resolved = Path(path) if path is not None else DEFAULT_POLICY_PATH
    try:
        text = resolved.read_text(encoding="utf-8")
    except OSError as exc:
        raise PolicyLoadError(f"Cannot read policy file {resolved}: {exc}") from exc
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise PolicyLoadError(f"Malformed YAML in {resolved}: {exc}") from exc
    return _validate_and_build(raw or {}, snapshot=policy_snapshot)


def classify_escalation_class(
    envelope: Mapping[str, Any],
    policy: HitlPolicy,
) -> HitlClass | None:
    """Classify a sealed-folder envelope against the policy precedence list.

    Returns the first matching ``HitlClass`` by precedence, or ``None`` if no
    class matches (caller dispatches COMMIT path).

    Envelope fields consumed (all optional; missing treated as False/neutral):
        - ``requires_policy_override`` (bool)
        - ``is_regulated`` (bool)
        - ``is_safety_impacting`` (bool)
        - ``is_financial`` (bool)
        - ``novelty_score`` (float, 0..1)
        - ``confidence_score`` (float, 0..1)
    """
    if not isinstance(envelope, Mapping):
        raise TypeError("envelope must be a mapping")

    novelty = _as_float(envelope.get("novelty_score"))
    confidence = _as_float(envelope.get("confidence_score"))

    checks: dict[HitlClass, bool] = {
        HitlClass.POLICY_OVERRIDE: bool(envelope.get("requires_policy_override")),
        HitlClass.REGULATED: bool(envelope.get("is_regulated")),
        HitlClass.SAFETY: bool(envelope.get("is_safety_impacting")),
        HitlClass.FINANCIAL: bool(envelope.get("is_financial")),
        HitlClass.NOVEL_CONTEXT: novelty is not None and novelty >= policy.novelty_min,
        HitlClass.LOW_CONFIDENCE: confidence is not None and confidence <= policy.confidence_max,
    }

    for hc in policy.precedence:
        if checks.get(hc, False):
            return hc
    return None


def resolve_approver_pool(
    hitl_class: HitlClass,
    policy: HitlPolicy,
    tenant: str | None = None,
    time_of_day: str | None = None,
) -> str:
    """Resolve approver pool for a class.

    v1: returns the class's default pool. Tenant / time-of-day routing is a
    future extension (W4+); parameters are accepted now for API stability.
    """
    # Parameters reserved for future tenant/time-of-day overlay.
    _ = tenant, time_of_day
    return _class_policy(hitl_class, policy).approver_pool


def set_timeout(hitl_class: HitlClass, policy: HitlPolicy) -> int:
    """Return the per-class timeout in seconds."""
    return _class_policy(hitl_class, policy).timeout_s


def set_fallback(hitl_class: HitlClass, policy: HitlPolicy) -> str:
    """Return the per-class fallback directive (e.g. ``DENY``)."""
    return _class_policy(hitl_class, policy).fallback


def _class_policy(hitl_class: HitlClass, policy: HitlPolicy) -> ClassPolicy:
    try:
        return policy.classes[hitl_class]
    except KeyError as exc:
        raise PolicyLoadError(f"Class {hitl_class!r} not in policy") from exc


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


__all__ = [
    "ClassPolicy",
    "DEFAULT_POLICY_PATH",
    "HitlPolicy",
    "PolicyLoadError",
    "classify_escalation_class",
    "load_policy",
    "resolve_approver_pool",
    "set_fallback",
    "set_timeout",
]
