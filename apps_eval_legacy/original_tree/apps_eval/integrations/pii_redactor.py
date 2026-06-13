"""apps_eval.integrations.pii_redactor — field-level PII redaction layer.

Plan: ``apps-eval-harness-phase2-b5f3c1`` W2/AE-2.

Purpose
-------
Configurable field-level scrubber that removes or masks PII from
production-log rows before they are ingested into eval fixture sets.
Intended to be wired into ``production_log_miner.set_redactor()`` before
any real-traffic run.

Supported strategies per field:
- ``mask``   — replace the field value with a fixed placeholder string
               (e.g. ``"[REDACTED]"``).
- ``hash``   — replace with a stable SHA-256 hex digest (last 16 chars)
               so records can still be deduplicated without leaking the
               raw value.
- ``drop``   — remove the key from the output dict entirely.

Default scrub fields (covers the most common PII carriers in eval logs):
    name, email, phone, company, address, ip_address, user_id,
    candidate_name, hiring_manager, org_name

Operators may extend or override via ``PiiRedactorConfig.field_policies``.

Usage
-----
    from apps_eval.integrations.pii_redactor import PiiRedactor, PiiRedactorConfig

    redactor = PiiRedactor()          # default config
    clean = redactor.redact(raw_row)

    # register with production_log_miner
    from ops_scripts.calibration.production_log_miner import set_redactor
    set_redactor(redactor.redact)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Mapping

_DEFAULT_FIELD_POLICIES: dict[str, str] = {
    "name": "mask",
    "email": "hash",
    "phone": "mask",
    "company": "mask",
    "address": "mask",
    "ip_address": "hash",
    "user_id": "hash",
    "candidate_name": "mask",
    "hiring_manager": "mask",
    "org_name": "mask",
}

_MASK_PLACEHOLDER = "[REDACTED]"
_HASH_PREFIX = "sha256:"


def _hash_value(value: Any) -> str:
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()
    return f"{_HASH_PREFIX}{digest[-16:]}"


@dataclass
class PiiRedactorConfig:
    field_policies: dict[str, str] = field(default_factory=lambda: dict(_DEFAULT_FIELD_POLICIES))
    """Map of field_name -> strategy (mask | hash | drop)."""

    recursive: bool = True
    """If True, scrub nested dicts recursively."""


class PiiRedactor:
    """Field-level PII redactor.

    Args:
        config: Redaction config. Uses defaults if not provided.
    """

    IS_STUB: bool = False

    def __init__(self, config: PiiRedactorConfig | None = None) -> None:
        self._config = config or PiiRedactorConfig()

    def redact(self, row: Mapping[str, Any]) -> dict[str, Any]:
        """Return a new dict with PII fields scrubbed per policy.

        Never mutates the input. Never raises — returns input unchanged
        if it is not a Mapping (fail-soft for pipeline safety).
        """
        if not isinstance(row, Mapping):
            return dict(row) if isinstance(row, dict) else {}
        return self._scrub(dict(row))

    def _scrub(self, obj: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        policies = self._config.field_policies
        for key, value in obj.items():
            policy = policies.get(str(key))
            if policy == "drop":
                continue
            elif policy == "mask":
                result[key] = _MASK_PLACEHOLDER
            elif policy == "hash":
                result[key] = _hash_value(value)
            elif self._config.recursive and isinstance(value, dict):
                result[key] = self._scrub(value)
            elif self._config.recursive and isinstance(value, list):
                result[key] = [
                    self._scrub(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result


__all__ = ["PiiRedactor", "PiiRedactorConfig"]
