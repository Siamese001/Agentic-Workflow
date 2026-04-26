"""
01.4 — Ingress origin labels and payload security findings.

Origin and authority labels are *evidence*, not authority decisions. They
describe where each payload segment came from (user_turn, transport_metadata,
quoted_untrusted, ...) and what authority weight (if any) the segment may
carry downstream.

INVARIANT: Intake never declares user-supplied content authoritative. The
strongest authority label intake can attach to user-provided payload is
`user_intent_only`. Anything quoted, executable-looking, or suspicious is
explicitly downgraded to `data_only`, `quoted_untrusted`, or `no_authority`.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from agentic_core.L0_routing.intake.envelope import RawIngressEnvelope


# ---------------------------------------------------------------------------
# Label constants — spec line 261-276 of 01.4
# ---------------------------------------------------------------------------

ORIGIN_LABELS: frozenset[str] = frozenset({
    "user_turn",
    "user_supplied_quote",
    "user_supplied_code",
    "user_supplied_url",
    "user_supplied_attachment_ref",
    "transport_metadata",
    "unknown_untrusted",
})

AUTHORITY_LABELS: frozenset[str] = frozenset({
    "user_intent_only",
    "data_only",
    "quoted_untrusted",
    "executable_untrusted",
    "metadata_only",
    "no_authority",
})

SECURITY_FINDING_CLASSES: frozenset[str] = frozenset({
    "prompt_injection_like_text",
    "system_override_claim",
    "credential_or_secret_pattern",
    "executable_payload",
    "cross_tenant_hint",
    "suspicious_url",
    "malformed_serialized_object",
    "html_or_markdown_control_payload",
    "oversized_embedded_blob",
})


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PayloadSegment:
    """A bounded slice of the normalized payload."""

    segment_ref: str
    text: str
    kind: str  # "text" | "quoted" | "code" | "url" | "attachment" | "metadata"


@dataclass(frozen=True)
class PayloadSecurityFinding:
    """01.4 §5 — security finding emitted as evidence (never as authority)."""

    finding_id: str
    finding_class: str
    segment_ref: str
    severity: str  # "info" | "low" | "medium" | "high" | "critical"
    safe_summary: str
    quarantine_candidate: bool = False
    redaction_candidate: bool = False
    downstream_attention_hint: str = ""
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class IngressOriginLabelManifest:
    """01.4 §4 — manifest of origin/authority labels per payload segment."""

    manifest_id: str
    payload_segment_refs: tuple[str, ...]
    segment_origin_labels: tuple[str, ...]
    segment_authority_labels: tuple[str, ...]
    quoted_or_pasted_content_refs: tuple[str, ...] = ()
    system_like_claim_refs: tuple[str, ...] = ()
    instruction_like_payload_refs: tuple[str, ...] = ()
    executable_payload_refs: tuple[str, ...] = ()
    user_data_only_refs: tuple[str, ...] = ()
    manifest_hash: str = ""

    def with_hash(self) -> "IngressOriginLabelManifest":
        payload = json.dumps(
            {
                "segments": list(self.payload_segment_refs),
                "origin": list(self.segment_origin_labels),
                "authority": list(self.segment_authority_labels),
                "quoted": list(self.quoted_or_pasted_content_refs),
                "system_like": list(self.system_like_claim_refs),
                "instruction_like": list(self.instruction_like_payload_refs),
                "executable": list(self.executable_payload_refs),
                "user_data_only": list(self.user_data_only_refs),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        h = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return IngressOriginLabelManifest(
            manifest_id=self.manifest_id,
            payload_segment_refs=self.payload_segment_refs,
            segment_origin_labels=self.segment_origin_labels,
            segment_authority_labels=self.segment_authority_labels,
            quoted_or_pasted_content_refs=self.quoted_or_pasted_content_refs,
            system_like_claim_refs=self.system_like_claim_refs,
            instruction_like_payload_refs=self.instruction_like_payload_refs,
            executable_payload_refs=self.executable_payload_refs,
            user_data_only_refs=self.user_data_only_refs,
            manifest_hash=h,
        )


# ---------------------------------------------------------------------------
# Detection patterns (tight; only flag, never modify, never obey)
# ---------------------------------------------------------------------------

_QUOTE_BLOCK_RE = re.compile(r"```[\s\S]*?```|^\s*>", re.MULTILINE)
_SYSTEM_LIKE_RE = re.compile(
    r"\b(system\s*:\s*you are|you are now\s+the\s+system|act\s+as\s+a\s+system)\b",
    re.IGNORECASE,
)
_INSTRUCTION_LIKE_RE = re.compile(
    r"\b(ignore\s+(all\s+)?previous\s+instructions|disregard\s+(all\s+)?prior\s+rules|do\s+not\s+follow\s+the\s+system\s+prompt)\b",
    re.IGNORECASE,
)
_TOOL_INJECTION_RE = re.compile(r"<\|im_start\|>|<tool_call>", re.IGNORECASE)
_EXECUTABLE_RE = re.compile(
    r"(?:^|\n)\s*(?:#!\s*/|<\?php|<script\b|powershell\s+-|bash\s+-c\s)",
    re.IGNORECASE,
)
_CRED_RE = re.compile(
    r"(?i)(api[-_ ]?key\s*[:=]\s*[A-Za-z0-9_\-]{16,}|aws_secret\w*\s*[:=]\s*\S{16,}|"
    r"sk-[A-Za-z0-9]{16,}|bearer\s+[A-Za-z0-9_\-\.]{20,})"
)
_URL_RE = re.compile(r"https?://[^\s<>\"]+", re.IGNORECASE)
_SUSPICIOUS_URL_HINTS = ("@", "%00", "javascript:", "data:text/html")
_HTML_CONTROL_RE = re.compile(r"</?\s*(script|iframe|object|embed)\b", re.IGNORECASE)


# Reasonable upper bound for a single embedded blob (5 MiB) before flagging.
_EMBEDDED_BLOB_BYTES = 5 * 1024 * 1024


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


def segment_payload(
    normalized_text: str,
    attachment_refs: Sequence[str] = (),
    transport_metadata_keys: Sequence[str] = (),
) -> tuple[PayloadSegment, ...]:
    """Cut the normalized payload into bounded segments.

    Heuristic — fenced code blocks become 'code' segments, blockquoted lines
    become 'quoted', URLs become 'url' segments, attachments and metadata
    become their own segments. Whatever remains is the 'text' segment.
    """
    segments: list[PayloadSegment] = []
    base_idx = 0

    if normalized_text:
        # Code blocks (```...```)
        residual = normalized_text
        for m in re.finditer(r"```[\s\S]*?```", normalized_text):
            block = m.group(0)
            ref = f"seg:code:{base_idx}"
            segments.append(PayloadSegment(segment_ref=ref, text=block, kind="code"))
            base_idx += 1
            residual = residual.replace(block, "", 1)

        # Block quotes
        for line in residual.split("\n"):
            if line.lstrip().startswith(">"):
                ref = f"seg:quoted:{base_idx}"
                segments.append(PayloadSegment(segment_ref=ref, text=line, kind="quoted"))
                base_idx += 1

        # URLs
        for m in _URL_RE.finditer(residual):
            ref = f"seg:url:{base_idx}"
            segments.append(PayloadSegment(segment_ref=ref, text=m.group(0), kind="url"))
            base_idx += 1

        # Remaining text
        ref = f"seg:text:{base_idx}"
        segments.append(PayloadSegment(segment_ref=ref, text=residual, kind="text"))
        base_idx += 1

    for i, ref in enumerate(attachment_refs):
        segments.append(
            PayloadSegment(
                segment_ref=f"seg:att:{i}",
                text=f"<attachment {ref}>",
                kind="attachment",
            )
        )

    for i, key in enumerate(transport_metadata_keys):
        segments.append(
            PayloadSegment(
                segment_ref=f"seg:meta:{i}",
                text=f"<metadata {key}>",
                kind="metadata",
            )
        )

    return tuple(segments)


def _origin_for(segment: PayloadSegment) -> str:
    if segment.kind == "code":
        return "user_supplied_code"
    if segment.kind == "quoted":
        return "user_supplied_quote"
    if segment.kind == "url":
        return "user_supplied_url"
    if segment.kind == "attachment":
        return "user_supplied_attachment_ref"
    if segment.kind == "metadata":
        return "transport_metadata"
    return "user_turn"


def _authority_for(segment: PayloadSegment, has_security_finding: bool) -> str:
    """Apply downgrade rules — anything suspicious or executable becomes data_only.

    The authority assigned here is *advisory*. Downstream layers (PA, L5)
    apply the actual authority gates.
    """
    if segment.kind == "metadata":
        return "metadata_only"
    if has_security_finding and segment.kind in ("code", "url"):
        return "executable_untrusted"
    if has_security_finding:
        return "quoted_untrusted"
    if segment.kind == "code":
        # Even non-suspicious code from user is data, never authority.
        return "data_only"
    if segment.kind == "quoted":
        return "quoted_untrusted"
    if segment.kind == "url":
        return "data_only"
    if segment.kind == "attachment":
        return "data_only"
    return "user_intent_only"


def _findings_for_segment(
    segment: PayloadSegment, max_blob_bytes: int = _EMBEDDED_BLOB_BYTES
) -> list[PayloadSecurityFinding]:
    findings: list[PayloadSecurityFinding] = []
    text = segment.text
    if not text:
        return findings

    # 1. instruction-like / prompt-injection patterns
    if _INSTRUCTION_LIKE_RE.search(text) or _TOOL_INJECTION_RE.search(text):
        findings.append(
            PayloadSecurityFinding(
                finding_id=f"finding:{segment.segment_ref}:instr",
                finding_class="prompt_injection_like_text",
                segment_ref=segment.segment_ref,
                severity="medium",
                safe_summary=(
                    "Payload segment contains text that resembles a prompt-injection "
                    "instruction. Flagged as data, never followed as authority."
                ),
                quarantine_candidate=False,
                redaction_candidate=False,
                downstream_attention_hint="Treat as user_data_only; never elevate authority.",
            )
        )

    # 2. system-role override claims
    if _SYSTEM_LIKE_RE.search(text):
        findings.append(
            PayloadSecurityFinding(
                finding_id=f"finding:{segment.segment_ref}:sys",
                finding_class="system_override_claim",
                segment_ref=segment.segment_ref,
                severity="high",
                safe_summary="Payload claims system-role authority. Demoted to data_only.",
                quarantine_candidate=False,
                redaction_candidate=False,
                downstream_attention_hint="Strip system-role framing in PA airlock.",
            )
        )

    # 3. credential/secret-shaped substrings
    if _CRED_RE.search(text):
        findings.append(
            PayloadSecurityFinding(
                finding_id=f"finding:{segment.segment_ref}:cred",
                finding_class="credential_or_secret_pattern",
                segment_ref=segment.segment_ref,
                severity="high",
                safe_summary="Payload contains text matching a credential pattern.",
                quarantine_candidate=True,
                redaction_candidate=True,
                downstream_attention_hint="Redact before logs/prompt; do not echo back.",
            )
        )

    # 4. executable payload markers
    if _EXECUTABLE_RE.search(text) or (
        segment.kind == "code" and _EXECUTABLE_RE.search(text or "")
    ):
        findings.append(
            PayloadSecurityFinding(
                finding_id=f"finding:{segment.segment_ref}:exec",
                finding_class="executable_payload",
                segment_ref=segment.segment_ref,
                severity="high",
                safe_summary="Payload segment looks executable.",
                quarantine_candidate=True,
                redaction_candidate=False,
                downstream_attention_hint="Mark executable_untrusted; sandbox before any execution decision.",
            )
        )

    # 5. suspicious URLs
    if segment.kind == "url":
        url = text.strip()
        if any(hint in url.lower() for hint in _SUSPICIOUS_URL_HINTS):
            findings.append(
                PayloadSecurityFinding(
                    finding_id=f"finding:{segment.segment_ref}:url",
                    finding_class="suspicious_url",
                    segment_ref=segment.segment_ref,
                    severity="medium",
                    safe_summary="URL contains a suspicious pattern.",
                    quarantine_candidate=False,
                    redaction_candidate=False,
                    downstream_attention_hint="Warn C0 before any fetch.",
                )
            )

    # 6. HTML/markdown control payloads
    if _HTML_CONTROL_RE.search(text):
        findings.append(
            PayloadSecurityFinding(
                finding_id=f"finding:{segment.segment_ref}:html",
                finding_class="html_or_markdown_control_payload",
                segment_ref=segment.segment_ref,
                severity="medium",
                safe_summary="Payload contains active HTML/markdown control elements.",
                quarantine_candidate=False,
                redaction_candidate=True,
                downstream_attention_hint="Strip <script>/<iframe> in any rendered output path.",
            )
        )

    # 7. oversized embedded blob
    if len(text.encode("utf-8", errors="replace")) > max_blob_bytes:
        findings.append(
            PayloadSecurityFinding(
                finding_id=f"finding:{segment.segment_ref}:blob",
                finding_class="oversized_embedded_blob",
                segment_ref=segment.segment_ref,
                severity="low",
                safe_summary="Embedded text segment exceeds size limit.",
                quarantine_candidate=False,
                redaction_candidate=False,
                downstream_attention_hint="Consider attachment-mode handling.",
            )
        )

    return findings


def build_origin_label_manifest(
    env: RawIngressEnvelope,
    *,
    normalized_text: str,
    request_id: str,
    max_blob_bytes: int = _EMBEDDED_BLOB_BYTES,
) -> tuple[IngressOriginLabelManifest, tuple[PayloadSecurityFinding, ...]]:
    """Build the origin-label manifest and security findings for a request.

    Pure function — no I/O, no mutation. Deterministic given the same input.
    """
    attachment_refs = tuple(a.ref for a in env.attachments.entries)
    metadata_keys = tuple(k for k in ("upstream_traceparent", "client_version", "platform")
                          if getattr(env, k, None))

    segments = segment_payload(
        normalized_text,
        attachment_refs=attachment_refs,
        transport_metadata_keys=metadata_keys,
    )

    all_findings: list[PayloadSecurityFinding] = []
    seg_to_findings: dict[str, list[PayloadSecurityFinding]] = {}
    for seg in segments:
        f = _findings_for_segment(seg, max_blob_bytes=max_blob_bytes)
        if f:
            seg_to_findings[seg.segment_ref] = f
            all_findings.extend(f)

    seg_refs: list[str] = []
    origin_labels: list[str] = []
    authority_labels: list[str] = []
    quoted_refs: list[str] = []
    system_like_refs: list[str] = []
    instruction_like_refs: list[str] = []
    executable_refs: list[str] = []
    user_data_only_refs: list[str] = []

    for seg in segments:
        seg_refs.append(seg.segment_ref)
        origin = _origin_for(seg)
        origin_labels.append(origin)
        has_finding = seg.segment_ref in seg_to_findings
        authority = _authority_for(seg, has_security_finding=has_finding)
        authority_labels.append(authority)

        if seg.kind == "quoted":
            quoted_refs.append(seg.segment_ref)
        if has_finding:
            finds = seg_to_findings[seg.segment_ref]
            if any(f.finding_class == "system_override_claim" for f in finds):
                system_like_refs.append(seg.segment_ref)
            if any(f.finding_class == "prompt_injection_like_text" for f in finds):
                instruction_like_refs.append(seg.segment_ref)
            if any(f.finding_class == "executable_payload" for f in finds):
                executable_refs.append(seg.segment_ref)
        if authority in ("data_only", "metadata_only"):
            user_data_only_refs.append(seg.segment_ref)

    manifest = IngressOriginLabelManifest(
        manifest_id=f"manifest:{request_id}",
        payload_segment_refs=tuple(seg_refs),
        segment_origin_labels=tuple(origin_labels),
        segment_authority_labels=tuple(authority_labels),
        quoted_or_pasted_content_refs=tuple(quoted_refs),
        system_like_claim_refs=tuple(system_like_refs),
        instruction_like_payload_refs=tuple(instruction_like_refs),
        executable_payload_refs=tuple(executable_refs),
        user_data_only_refs=tuple(user_data_only_refs),
    ).with_hash()

    return manifest, tuple(all_findings)


__all__ = [
    "AUTHORITY_LABELS",
    "IngressOriginLabelManifest",
    "ORIGIN_LABELS",
    "PayloadSecurityFinding",
    "PayloadSegment",
    "SECURITY_FINDING_CLASSES",
    "build_origin_label_manifest",
    "segment_payload",
]
