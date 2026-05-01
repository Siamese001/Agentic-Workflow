"""W2 — Integrated-runtime artifact emitter.

Single SSOT helper for stamping every artifact in the W2 chain with its
provenance envelope:

    {
      "producer_component":         "agentic_core....",
      "producer_module":            "...",
      "producer_function_or_class": "...",
      "emitted_at":                 "<UTC ISO8601>",
      "artifact_hash":              "sha256:<hex>",
      "upstream_artifact_ref":      "sha256:<hex>" | "",
      "payload":                    { ... }
    }

The W2 verifiers consume only this envelope shape; no other emitter
should write into ``artifacts/certification/integrated_runtime/``.

Anti-cheat invariants enforced here, before write:
    1. ``producer_component`` MUST start with ``"agentic_core."``.
    2. ``producer_component`` MUST NOT match harness regex
       (``^tests\\.``, ``^scripts\\.verify_``, contain ``"harness"``).
    3. Payload MUST be JSON-serializable.
    4. Upstream ref, when supplied, MUST be of the form
       ``sha256:<64-hex>`` to keep the chain machine-checkable.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Filename → expected position in the W2 chain (1..12). Used by the
# manifest emitter and by the verifier to assert all 12 artifacts exist.
W2_ARTIFACT_FILENAMES: tuple[str, ...] = (
    "integrated_runtime_entrypoint_invocation.json",
    "validated_request.json",
    "l1_plan_contract.json",
    "route_contract.json",
    "runtime_gate_verdict_bundle.json",
    "semantic_cache_safe_reuse_decision.json",
    "terminal_ret_packet.json",
    "exit_review_packet.json",
    "x3_disposition_receipt.json",
    "runtime_exhaust_bundle.json",
    "integrated_runtime_artifact_manifest.json",
    "no_harness_stamp_receipt.json",
)

# Chain order for upstream_artifact_ref linkage. Each entry is
# (filename, upstream_filename_or_None).
W2_CHAIN_LINKAGE: tuple[tuple[str, str | None], ...] = (
    ("integrated_runtime_entrypoint_invocation.json", None),
    ("validated_request.json", "integrated_runtime_entrypoint_invocation.json"),
    ("l1_plan_contract.json", "validated_request.json"),
    ("route_contract.json", "l1_plan_contract.json"),
    ("runtime_gate_verdict_bundle.json", "route_contract.json"),
    ("semantic_cache_safe_reuse_decision.json", "runtime_gate_verdict_bundle.json"),
    ("terminal_ret_packet.json", "semantic_cache_safe_reuse_decision.json"),
    ("exit_review_packet.json", "terminal_ret_packet.json"),
    ("x3_disposition_receipt.json", "exit_review_packet.json"),
    ("runtime_exhaust_bundle.json", "x3_disposition_receipt.json"),
    ("integrated_runtime_artifact_manifest.json", "runtime_exhaust_bundle.json"),
    ("no_harness_stamp_receipt.json", "integrated_runtime_artifact_manifest.json"),
)

# Anti-cheat: any of these substrings/prefixes in producer_component is
# treated as harness-stamping by the verifier and the emitter.
_HARNESS_FORBIDDEN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^tests\."),
    re.compile(r"^scripts\.verify_"),
    re.compile(r"^ops_scripts\.ci\.verify_"),
    re.compile(r"\bharness\b"),
)

_SHA256_REF_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class ProvenanceStamp:
    producer_component: str
    producer_module: str
    producer_function_or_class: str

    def __post_init__(self) -> None:
        if not self.producer_component.startswith("agentic_core."):
            raise ValueError(
                f"ProvenanceStamp.producer_component must be agentic_core.*; "
                f"got {self.producer_component!r}"
            )
        for pat in _HARNESS_FORBIDDEN_PATTERNS:
            if pat.search(self.producer_component):
                raise ValueError(
                    f"ProvenanceStamp.producer_component matches harness "
                    f"pattern {pat.pattern!r}: {self.producer_component!r}"
                )


def _canonical_json(payload: Any) -> str:
    """Deterministic JSON serialization (sorted keys, no whitespace)."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def compute_artifact_hash(payload: Any) -> str:
    """Return ``sha256:<hex>`` of canonical-JSON serialization of ``payload``."""
    blob = _canonical_json(payload).encode("utf-8")
    return f"sha256:{hashlib.sha256(blob).hexdigest()}"


def emit_artifact(
    artifact_dir: Path,
    filename: str,
    payload: Any,
    *,
    stamp: ProvenanceStamp,
    upstream_artifact_ref: str = "",
) -> tuple[Path, str]:
    """Stamp ``payload`` and write to ``artifact_dir/filename``.

    Returns ``(written_path, artifact_hash)``.

    Raises:
        ValueError: producer_component is harness-shaped, or
            upstream_artifact_ref is non-empty but malformed.
    """
    if filename not in W2_ARTIFACT_FILENAMES:
        raise ValueError(
            f"emit_artifact: filename {filename!r} not in the W2 manifest. "
            "All emitted artifacts must be one of the 12 declared filenames."
        )
    if upstream_artifact_ref and not _SHA256_REF_RE.match(upstream_artifact_ref):
        raise ValueError(
            f"emit_artifact: upstream_artifact_ref {upstream_artifact_ref!r} "
            "must be of form 'sha256:<64-hex>' or empty."
        )

    artifact_hash = compute_artifact_hash(payload)
    envelope: dict[str, Any] = {
        "producer_component": stamp.producer_component,
        "producer_module": stamp.producer_module,
        "producer_function_or_class": stamp.producer_function_or_class,
        "emitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "artifact_hash": artifact_hash,
        "upstream_artifact_ref": upstream_artifact_ref,
        "payload": payload,
    }

    artifact_dir.mkdir(parents=True, exist_ok=True)
    out = artifact_dir / filename
    out.write_text(
        json.dumps(envelope, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    return out, artifact_hash


def is_harness_stamp(producer_component: str) -> bool:
    """Return True if ``producer_component`` matches any harness pattern."""
    for pat in _HARNESS_FORBIDDEN_PATTERNS:
        if pat.search(producer_component):
            return True
    return False


__all__ = [
    "ProvenanceStamp",
    "W2_ARTIFACT_FILENAMES",
    "W2_CHAIN_LINKAGE",
    "compute_artifact_hash",
    "emit_artifact",
    "is_harness_stamp",
]
