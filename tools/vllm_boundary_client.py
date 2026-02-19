"""vLLM Boundary Client.

Sole permitted location for vllm, transformers, and torch imports.
All other L0-L6 layers must not import these libraries directly
or transitively.

Compliance: REV 5 - routing_invariants_version = 1
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import math
from dataclasses import asdict, is_dataclass
from decimal import Decimal
from enum import Enum
from typing import Any

_DEFAULT_TIMEOUT_SECONDS = 30  # guardian: allow-magic_configuration


def normalize_payload(payload: Any) -> Any:
    """Idempotent canonical normalization for hashing.

    Applies 16 type rules in order. Idempotency holds:
        normalize_payload(normalize_payload(x)) == normalize_payload(x)

    Raises:
        TypeError: For datetime, bytes, complex, NaN, Inf, or unknown types.
    """
    # Rule 1: None
    if payload is None:
        return None

    # Rule 2: bool (must precede int — bool is subclass of int)
    if isinstance(payload, bool):
        return payload

    # Rule 3: int
    if isinstance(payload, int):
        return payload

    # Rule 4: float
    if isinstance(payload, float):
        if math.isnan(payload) or math.isinf(payload):
            raise TypeError(f"NaN and Infinity are not supported in canonical normalization: {payload!r}")
        # Normalize -0.0 → 0.0 before rounding
        if payload == 0.0:
            return 0.0
        return round(payload, 12)

    # Rule 5: str
    if isinstance(payload, str):
        return payload

    # Rule 6: Decimal
    if isinstance(payload, Decimal):
        return str(payload)

    # Rule 7: Enum
    if isinstance(payload, Enum):
        return payload.name

    # Rule 8: datetime — reject
    if isinstance(payload, (_dt.datetime, _dt.date, _dt.time)):
        raise TypeError(f"datetime objects are not supported in canonical normalization: {type(payload)!r}")

    # Rule 9: bytes
    if isinstance(payload, bytes):
        raise TypeError("bytes objects are not supported in canonical normalization")

    # Rule 10: complex
    if isinstance(payload, complex):
        raise TypeError("complex objects are not supported in canonical normalization")

    # Rule 11: set
    if isinstance(payload, set):
        return sorted(normalize_payload(item) for item in payload)

    # Rule 12: list
    if isinstance(payload, list):
        return [normalize_payload(item) for item in payload]

    # Rule 13: tuple — preserve order, no sorting
    if isinstance(payload, tuple):
        return [normalize_payload(item) for item in payload]

    # Rule 14: dict — cast keys to str, sort by key, recurse on values
    if isinstance(payload, dict):
        return {str(k): normalize_payload(v) for k, v in sorted(payload.items())}

    # Rule 15: dataclass
    if is_dataclass(payload) and not isinstance(payload, type):
        return normalize_payload(asdict(payload))

    # Rule 16: all else — reject
    raise TypeError(
        f"Unsupported type for canonical normalization: {type(payload)!r}. "
        "Supported: None, bool, int, float, str, Decimal, Enum, "
        "set, list, tuple, dict, dataclass."
    )


def canonical_hash(payload: dict) -> str:
    """Generate SHA-256 canonical hash of a dict payload.

    Args:
        payload: Must be a dict at the top level.

    Returns:
        SHA-256 hex digest of the canonical JSON representation.

    Raises:
        TypeError: If payload is not a dict, or contains unsupported types.
    """
    if not isinstance(payload, dict):
        raise TypeError(f"canonical_hash expects dict at top level, got {type(payload)!r}")
    normalized = normalize_payload(payload)
    json_str = json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(json_str.encode("utf-8")).hexdigest()


def generate_proposal(prompt: str, config: dict) -> dict:
    """Generate a vLLM proposal with full audit trail.

    Args:
        prompt: Input prompt string.
        config: Configuration dictionary including routing_version.

    Returns:
        Proposal dict with text, proposal_hash, routing_version, config_hash.

    Raises:
        TimeoutError: If vLLM request exceeds _DEFAULT_TIMEOUT_SECONDS.
        RuntimeError: If vLLM request fails.
    """
    config_hash = canonical_hash(config)
    routing_version = config.get("routing_version", "unknown")

    try:
        text = _call_vllm(prompt, config)
    except TimeoutError:
        raise TimeoutError(f"vLLM request timed out after {_DEFAULT_TIMEOUT_SECONDS}s. No retries.")
    except Exception as exc:
        raise RuntimeError(f"vLLM request failed: {exc}") from exc

    return {
        "text": text,
        "proposal_hash": canonical_hash({"text": text}),
        "routing_version": routing_version,
        "config_hash": config_hash,
    }


def _call_vllm(prompt: str, config: dict) -> str:  # noqa: ARG001
    """Internal vLLM call. Model imports isolated here.

    Only location where vllm/transformers/torch may be imported.
    No other module in L0-L6 may import these.
    """
    # import vllm          # noqa: F401 (uncomment when installed)
    # import transformers  # noqa: F401 (uncomment when installed)
    # import torch         # noqa: F401 (uncomment when installed)
    return f"[vLLM proposal for prompt: {prompt[:50]}]"
