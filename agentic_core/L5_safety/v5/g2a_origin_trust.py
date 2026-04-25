"""G2a ORIGIN-TRUST AND CONTENT BOUNDARY LABELING (spec lines 165–191)."""

from __future__ import annotations

import re
from typing import Mapping

from agentic_core.L5_safety.v5.contracts import OriginTrustManifest
from agentic_core.L5_safety.v5.types import BoundaryClassification, OriginLabel


# Authority order — spec line 136. Lower index = higher authority.
_AUTHORITY_ORDER: tuple[OriginLabel, ...] = (
    OriginLabel.SYSTEM_POLICY,
    OriginLabel.GOVERNANCE_POLICY,
    OriginLabel.REGISTRY_CONFIG,
    OriginLabel.DEVELOPER_ADMIN,
    OriginLabel.HUMAN_REVIEW,
    OriginLabel.RETRIEVED,
    OriginLabel.TOOL_OUTPUT,
    OriginLabel.USER_TURN,
    OriginLabel.PRIOR_ARTIFACT,
)


# Trusted-instruction set (spec line 188 + authority order).
_TRUSTED_INSTRUCTION_LABELS = frozenset(
    {
        OriginLabel.SYSTEM_POLICY,
        OriginLabel.GOVERNANCE_POLICY,
        OriginLabel.REGISTRY_CONFIG,
        OriginLabel.DEVELOPER_ADMIN,
    }
)


# Default untrusted-data set: everything else, until quarantine triggers.
_UNTRUSTED_DATA_LABELS = frozenset(
    {
        OriginLabel.USER_TURN,
        OriginLabel.RETRIEVED,
        OriginLabel.TOOL_OUTPUT,
        OriginLabel.HUMAN_REVIEW,
        OriginLabel.PRIOR_ARTIFACT,
    }
)


# Quarantine triggers (spec line 183).
_QUARANTINE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"<!--.*?-->", re.DOTALL), "html_comment"),
    (re.compile(r"<\s*script\b", re.IGNORECASE), "script_tag"),
    (re.compile(r"\bjavascript\s*:", re.IGNORECASE), "javascript_uri"),
    (re.compile(r"data:\s*text/html", re.IGNORECASE), "data_uri_html"),
    (re.compile(r"\bbase64,[A-Za-z0-9+/=]{40,}"), "base64_blob"),
    (re.compile(r"-----BEGIN\s+[A-Z ]+-----"), "credential_pem"),
    (re.compile(r"\b[A-Za-z0-9_\-]{30,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\b"), "jwt_like"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "api_key_like"),
)


def _scan_for_quarantine(text: str) -> tuple[str, ...]:
    reasons: list[str] = []
    for pat, name in _QUARANTINE_PATTERNS:
        if pat.search(text):
            reasons.append(name)
    return tuple(reasons)


def classify_origins(
    *,
    raw_labels: Mapping[str, tuple[str, ...]],
    field_payloads: Mapping[str, str] | None = None,
) -> OriginTrustManifest:
    """Apply origin-trust labels and boundary classification.

    Args:
        raw_labels: mapping from origin-label string → tuple of field paths.
            Unknown labels are dropped (keeps the manifest closed-set).
        field_payloads: optional mapping from field path → text payload.
            Used for quarantine pattern scanning. If absent, the manifest
            simply records the labels and classifies as the highest-
            authority label present.
    """
    field_payloads = field_payloads or {}

    # Convert raw label keys to enum, dropping unknown labels.
    labeled_fields: dict[OriginLabel, tuple[str, ...]] = {}
    for label_str, paths in raw_labels.items():
        try:
            label = OriginLabel(label_str)
        except ValueError:
            continue
        labeled_fields[label] = tuple(paths)

    # Quarantine scan ------------------------------------------------
    quarantine_reasons: list[str] = []
    sanitized: dict[str, str] = {}
    rejected = False

    # Only scan untrusted-data fields; trusted-instruction sources are
    # treated as policy and not pattern-scanned (spec line 169–172).
    for label, paths in labeled_fields.items():
        if label not in _UNTRUSTED_DATA_LABELS:
            continue
        for path in paths:
            payload = field_payloads.get(path, "")
            if not payload:
                continue
            reasons = _scan_for_quarantine(payload)
            if reasons:
                quarantine_reasons.extend(f"{path}:{r}" for r in reasons)
                # Strip risky tokens to produce a sanitized payload.
                stripped = payload
                for pat, _ in _QUARANTINE_PATTERNS:
                    stripped = pat.sub("[REDACTED]", stripped)
                sanitized[path] = stripped
                if any(r in {"credential_pem", "api_key_like", "jwt_like"} for r in reasons):
                    rejected = True

    # --- Classify ----------------------------------------------------
    if rejected:
        classification = BoundaryClassification.REJECTED
    elif quarantine_reasons:
        classification = BoundaryClassification.QUARANTINED
    else:
        # Highest-authority label present wins. If only untrusted labels are
        # present → untrusted_data. If only trusted → trusted_instruction.
        # Mixed → choose by authority order: trusted wins for the headline,
        # but boundary is set per-field; we report the worst case (untrusted)
        # because the runtime lane needs to know to fence retrieved content.
        present_trusted = any(label in _TRUSTED_INSTRUCTION_LABELS for label in labeled_fields)
        present_untrusted = any(label in _UNTRUSTED_DATA_LABELS for label in labeled_fields)
        if present_untrusted:
            classification = BoundaryClassification.UNTRUSTED_DATA
        elif present_trusted:
            classification = BoundaryClassification.TRUSTED_INSTRUCTION
        else:
            classification = BoundaryClassification.UNTRUSTED_DATA

    return OriginTrustManifest(
        labeled_fields={label: paths for label, paths in labeled_fields.items()},
        boundary_classification=classification,
        sanitized_payload_map=sanitized,
        quarantine_reasons=tuple(quarantine_reasons),
    )


__all__ = ["classify_origins"]
