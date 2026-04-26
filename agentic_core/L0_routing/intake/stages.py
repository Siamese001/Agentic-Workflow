"""
E1..E6 intake stages.

Each stage is a pure function over (envelope, policy, state) returning a
StageResult. Stages do NOT mutate global state directly; the pipeline owns
state mutation (quota counter, dedupe store).

Spec sections: E1..E6 DETAIL blocks (lines 153-497).

HARD INVARIANTS (enforced in tests):
- No model call.
- No retrieval.
- No tool execution.
- No durable mutation.
- No semantic interpretation. Field-name lookups and type checks only.
"""

from __future__ import annotations

import re
import time
import unicodedata
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, MutableMapping

from agentic_core.L0_routing.intake.envelope import (
    AttachmentManifestEntry,
    AttachmentManifestShell,
    ModalityManifest,
    RawIngressEnvelope,
)
from agentic_core.L0_routing.intake.hashing import hash_payload, hash_text
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode
from agentic_core.L0_routing.intake.verdicts import (
    AbusePrecheckStatus,
    AuthVerdict,
    IdempotencyStatus,
    NormalizationVerdict,
    PrincipalType,
    QuotaVerdict,
    SchemaVerdict,
    SourceClass,
    StageVerdict,
)


# ---------------------------------------------------------------------------
# Result envelope
# ---------------------------------------------------------------------------


@dataclass
class StageResult:
    """Common return shape for E1..E6.

    `passed` is the gate decision. `reason_codes` may be non-empty even on a
    pass — they then represent warnings carried into the validated_request.
    """

    passed: bool
    reason_codes: list[IngressReasonCode] = field(default_factory=list)
    fields: MutableMapping[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# E1 — IS IT A REAL REQUEST? (transport + presence)
# ---------------------------------------------------------------------------

# spec line 170: transport_allowed = chat | ui | api | batch | webhook | queue | alert
DEFAULT_ALLOWED_TRANSPORTS: frozenset[str] = frozenset(
    {"chat", "ui", "api", "batch", "webhook", "queue", "alert"}
)

# Map transport -> source_class. webhook+queue are treated by the spec as
# alert/batch ingress paths; we classify per the U1..U4 quadrant table.
_TRANSPORT_TO_SOURCE_CLASS: Mapping[str, SourceClass] = {
    "chat": SourceClass.USER,
    "ui": SourceClass.USER,
    "api": SourceClass.SERVICE,
    "batch": SourceClass.BATCH,
    "queue": SourceClass.BATCH,
    "webhook": SourceClass.WEBHOOK,
    "alert": SourceClass.ALERT,
}


def classify_source(transport: str) -> SourceClass | None:
    """Map a transport string to its U-tier source class, or None if unknown."""
    return _TRANSPORT_TO_SOURCE_CLASS.get(transport.lower().strip())


def run_e1_real_request(
    env: RawIngressEnvelope,
    *,
    allowed_transports: frozenset[str] = DEFAULT_ALLOWED_TRANSPORTS,
    consumed_frames: set[str] | None = None,
) -> StageResult:
    """Verify a request-shaped packet exists on a supported transport.

    Spec line 153-205. Assigns request_id / session_id / trace_root.
    """
    fields: dict[str, Any] = {}

    # 1. transport allowlist
    transport = (env.transport or "").lower().strip()
    if transport not in allowed_transports:
        return StageResult(
            passed=False,
            reason_codes=[IngressReasonCode.UNSUPPORTED_TRANSPORT],
            fields={"E1_verdict": StageVerdict.REJECT.value, "transport_normalized": transport},
        )

    # 2. body parser must not have failed at the transport layer
    if env.body_parser_failed:
        return StageResult(
            passed=False,
            reason_codes=[IngressReasonCode.MALFORMED_ENVELOPE],
            fields={"E1_verdict": StageVerdict.REJECT.value},
        )

    # 3. request shell must carry a payload (text|json|attachments)
    if not env.has_payload():
        return StageResult(
            passed=False,
            reason_codes=[IngressReasonCode.EMPTY_PAYLOAD],
            fields={"E1_verdict": StageVerdict.REJECT.value},
        )

    # 4. assign / bind identifiers
    request_id = env.request_id_hint or f"req-{uuid.uuid4().hex}"
    session_id = env.session_id_hint or f"sess-{uuid.uuid4().hex}"
    trace_root = env.upstream_traceparent or f"trace-{uuid.uuid4().hex}"

    # 5. duplicate transport frame guard (spec line 179)
    if consumed_frames is not None:
        frame_key = f"{transport}:{request_id}"
        if frame_key in consumed_frames:
            return StageResult(
                passed=False,
                reason_codes=[IngressReasonCode.DUPLICATE_REQUEST],
                fields={"E1_verdict": StageVerdict.REJECT.value, "request_id": request_id},
            )
        consumed_frames.add(frame_key)

    # 6. classify source
    source_class = classify_source(transport)
    if source_class is None:  # defensive — allowlist already covered, but explicit
        return StageResult(
            passed=False,
            reason_codes=[IngressReasonCode.UNSUPPORTED_TRANSPORT],
            fields={"E1_verdict": StageVerdict.REJECT.value},
        )

    # 7. attachment manifest captured-but-not-inspected
    attachment_manifest = env.attachments

    fields.update(
        {
            "E1_verdict": StageVerdict.PASS.value,
            "ingress_envelope_opened": True,
            "request_id": request_id,
            "session_id": session_id,
            "trace_root": trace_root,
            "source_channel": env.source_channel or transport,
            "source_class": source_class,
            "transport_normalized": transport,
            "raw_payload_ref": env.raw_payload_ref or f"raw://{request_id}",
            "attachment_manifest_shell": attachment_manifest,
            "ingress_time_unix": time.time(),
        }
    )
    return StageResult(passed=True, fields=fields)


# ---------------------------------------------------------------------------
# E2 — CHECKING LIBRARY CARDS (identity + tenant baseline)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IdentityResolution:
    """Output of an external IdentityResolver callable."""

    auth_verdict: AuthVerdict
    principal_type: PrincipalType
    principal_id: str | None
    tenant_bind: str | None
    workspace_bind: str | None
    region_scope_baseline: str | None
    baseline_entitlements: tuple[str, ...]
    reason_code: IngressReasonCode | None = None


IdentityResolver = Callable[[RawIngressEnvelope, SourceClass], IdentityResolution]


def default_identity_resolver(
    env: RawIngressEnvelope,
    source_class: SourceClass,
) -> IdentityResolution:
    """Stdlib-only default. Honors only mechanical fields on the envelope.

    - If `auth_credential` carries `kind` and `token` and is not expired,
      treat the caller as authenticated/service-bound depending on principal
      kind claims.
    - Anonymous chat with no credential → ANONYMOUS_LIMITED scope.
    - Service/batch/webhook/alert WITHOUT credential → AUTH_REQUIRED reject.
    - Expired credential → AUTH_EXPIRED reject.
    - Tenant claim conflict (claimed_tenant_id vs. credential tenant) →
      TENANT_MISMATCH reject.
    """
    cred: Mapping[str, Any] = env.auth_credential or {}
    now = time.time()

    # service-class transports REQUIRE a credential
    requires_cred = source_class in (
        SourceClass.SERVICE,
        SourceClass.BATCH,
        SourceClass.WEBHOOK,
        SourceClass.ALERT,
    )

    if not cred:
        if requires_cred:
            return IdentityResolution(
                auth_verdict=AuthVerdict.REJECTED,
                principal_type=PrincipalType.UNKNOWN,
                principal_id=None,
                tenant_bind=None,
                workspace_bind=None,
                region_scope_baseline=env.region,
                baseline_entitlements=(),
                reason_code=IngressReasonCode.AUTH_REQUIRED,
            )
        # USER on chat/ui without credential — anonymous-limited.
        return IdentityResolution(
            auth_verdict=AuthVerdict.ANONYMOUS_LIMITED,
            principal_type=PrincipalType.ANONYMOUS,
            principal_id=None,
            tenant_bind=env.claimed_tenant_id,
            workspace_bind=env.claimed_workspace_id,
            region_scope_baseline=env.region,
            baseline_entitlements=("anonymous:read",),
        )

    # expiry check
    expires_at = cred.get("expires_at_unix")
    if isinstance(expires_at, (int, float)) and expires_at < now:
        return IdentityResolution(
            auth_verdict=AuthVerdict.REJECTED,
            principal_type=PrincipalType.UNKNOWN,
            principal_id=None,
            tenant_bind=None,
            workspace_bind=None,
            region_scope_baseline=env.region,
            baseline_entitlements=(),
            reason_code=IngressReasonCode.AUTH_EXPIRED,
        )

    # blocked principal flag
    if cred.get("blocked") is True:
        return IdentityResolution(
            auth_verdict=AuthVerdict.REJECTED,
            principal_type=PrincipalType.UNKNOWN,
            principal_id=cred.get("principal_id") or env.claimed_user_id or env.claimed_service_id,
            tenant_bind=None,
            workspace_bind=None,
            region_scope_baseline=env.region,
            baseline_entitlements=(),
            reason_code=IngressReasonCode.PRINCIPAL_BLOCKED,
        )

    # tenant claim consistency
    cred_tenant = cred.get("tenant_id")
    if cred_tenant is not None and env.claimed_tenant_id is not None and cred_tenant != env.claimed_tenant_id:
        return IdentityResolution(
            auth_verdict=AuthVerdict.REJECTED,
            principal_type=PrincipalType.UNKNOWN,
            principal_id=None,
            tenant_bind=None,
            workspace_bind=None,
            region_scope_baseline=env.region,
            baseline_entitlements=(),
            reason_code=IngressReasonCode.TENANT_MISMATCH,
        )

    # Resolve principal kind
    if env.claimed_service_id or cred.get("principal_kind") == "service":
        principal_type = PrincipalType.SERVICE
        principal_id = env.claimed_service_id or cred.get("principal_id")
        verdict = AuthVerdict.SERVICE_BOUND
        entitlements = tuple(cred.get("scopes", ("service:internal",)))
    else:
        principal_type = PrincipalType.USER
        principal_id = env.claimed_user_id or cred.get("principal_id")
        verdict = AuthVerdict.AUTHENTICATED
        entitlements = tuple(cred.get("scopes", ("user:standard",)))

    return IdentityResolution(
        auth_verdict=verdict,
        principal_type=principal_type,
        principal_id=principal_id,
        tenant_bind=env.claimed_tenant_id or cred_tenant,
        workspace_bind=env.claimed_workspace_id,
        region_scope_baseline=env.region,
        baseline_entitlements=entitlements,
    )


def run_e2_identity(
    env: RawIngressEnvelope,
    source_class: SourceClass,
    *,
    resolver: IdentityResolver | None = None,
) -> StageResult:
    """Bind caller identity baseline. Spec line 207-260."""
    res = (resolver or default_identity_resolver)(env, source_class)
    fields: dict[str, Any] = {
        "auth_verdict": res.auth_verdict,
        "principal_type": res.principal_type,
        "principal_id": res.principal_id,
        "tenant_bind": res.tenant_bind,
        "workspace_bind": res.workspace_bind,
        "region_scope_baseline": res.region_scope_baseline,
        "baseline_entitlements": res.baseline_entitlements,
        "caller_scope_baseline": _derive_caller_scope(res),
    }
    if res.auth_verdict == AuthVerdict.REJECTED:
        return StageResult(
            passed=False,
            reason_codes=[res.reason_code or IngressReasonCode.AUTH_REQUIRED],
            fields=fields,
        )
    return StageResult(passed=True, fields=fields)


def _derive_caller_scope(res: IdentityResolution) -> str:
    if res.auth_verdict == AuthVerdict.AUTHENTICATED:
        return "user:standard"
    if res.auth_verdict == AuthVerdict.SERVICE_BOUND:
        return "service:internal"
    if res.auth_verdict == AuthVerdict.ANONYMOUS_LIMITED:
        return "anonymous:limited"
    return "rejected"


# ---------------------------------------------------------------------------
# E3 — CHECKING DAILY LIMITS (quota + dedupe + abuse)
# ---------------------------------------------------------------------------


@dataclass
class QuotaState:
    """Mutable in-memory quota store. Pluggable for production.

    Counter keys are bucket names. The pipeline owns one QuotaState shared
    across requests within a process; tests instantiate a fresh state per case.
    """

    rate_window_size: int = 60  # seconds
    rate_limit_per_window: int = 100
    burst_limit: int = 30
    concurrent_limit: int = 10
    max_attachment_count: int = 16
    max_envelope_bytes: int = 10 * 1024 * 1024  # 10 MiB
    max_batch_size: int = 1_000

    # internal state
    _window_counters: dict[str, list[float]] = field(default_factory=dict)
    _concurrent_in_flight: dict[str, int] = field(default_factory=dict)
    _seen_idempotency_keys: dict[str, str] = field(default_factory=dict)
    _seen_payload_hashes: dict[str, float] = field(default_factory=dict)
    _seen_webhook_deliveries: set[str] = field(default_factory=set)

    def _prune(self, bucket: str, now: float) -> None:
        cutoff = now - self.rate_window_size
        events = self._window_counters.setdefault(bucket, [])
        self._window_counters[bucket] = [t for t in events if t >= cutoff]

    def hit(self, bucket: str, now: float) -> int:
        self._prune(bucket, now)
        self._window_counters[bucket].append(now)
        return len(self._window_counters[bucket])


def run_e3_quota(
    env: RawIngressEnvelope,
    source_class: SourceClass,
    e1_fields: Mapping[str, Any],
    e2_fields: Mapping[str, Any],
    *,
    state: QuotaState,
) -> StageResult:
    """Enforce coarse rate / quota / dedupe / abuse controls. Spec line 262-315."""
    now = time.time()
    tenant = e2_fields.get("tenant_bind") or "anon"
    principal = e2_fields.get("principal_id") or "anon"
    bucket = f"{tenant}:{principal}"

    fields: dict[str, Any] = {
        "quota_bucket": bucket,
        "quota_verdict": QuotaVerdict.ALLOWED,
        "rate_window_state": "ok",
        "dedupe_status": "fresh",
        "idempotency_status": IdempotencyStatus.NOT_APPLICABLE,
        "abuse_precheck_status": AbusePrecheckStatus.CLEAR.value,
        "retry_after_seconds": None,
    }

    # 1. envelope size preflight
    approx_bytes = (
        len(env.body_text or "")
        + (len(str(env.body_json)) if env.body_json else 0)
        + env.attachments.total_bytes
    )
    if approx_bytes > state.max_envelope_bytes:
        fields["quota_verdict"] = QuotaVerdict.DENIED
        return StageResult(
            passed=False,
            reason_codes=[IngressReasonCode.PAYLOAD_TOO_LARGE],
            fields=fields,
        )
    if env.attachments.count > state.max_attachment_count:
        fields["quota_verdict"] = QuotaVerdict.DENIED
        return StageResult(
            passed=False,
            reason_codes=[IngressReasonCode.PAYLOAD_TOO_LARGE],
            fields=fields,
        )

    # 2. webhook replay check (delivery_id)
    if source_class in (SourceClass.WEBHOOK, SourceClass.ALERT) and env.webhook_delivery_id:
        if env.webhook_delivery_id in state._seen_webhook_deliveries:
            fields["quota_verdict"] = QuotaVerdict.DUPLICATE
            fields["dedupe_status"] = "webhook_replay"
            return StageResult(
                passed=False,
                reason_codes=[IngressReasonCode.WEBHOOK_REPLAY],
                fields=fields,
            )
        state._seen_webhook_deliveries.add(env.webhook_delivery_id)

    # 3. idempotency key check
    if env.idempotency_key:
        prior = state._seen_idempotency_keys.get(env.idempotency_key)
        if prior is not None:
            fields["quota_verdict"] = QuotaVerdict.DUPLICATE
            fields["idempotency_status"] = IdempotencyStatus.ALREADY_PROCESSED
            fields["dedupe_status"] = "idempotency_hit"
            return StageResult(
                passed=False,
                reason_codes=[IngressReasonCode.DUPLICATE_REQUEST],
                fields=fields,
            )
        state._seen_idempotency_keys[env.idempotency_key] = e1_fields.get("request_id", "unknown")
        fields["idempotency_status"] = IdempotencyStatus.NEW

    # 4. payload-hash dedupe (within rate window)
    payload_hash = hash_payload(
        env.body_text,
        env.body_json,
        tuple(a.ref for a in env.attachments.entries),
    )
    fields["raw_payload_hash"] = payload_hash
    last_seen = state._seen_payload_hashes.get(payload_hash)
    if last_seen is not None and (now - last_seen) < state.rate_window_size:
        fields["quota_verdict"] = QuotaVerdict.DUPLICATE
        fields["dedupe_status"] = "payload_hash_hit"
        return StageResult(
            passed=False,
            reason_codes=[IngressReasonCode.DUPLICATE_REQUEST],
            fields=fields,
        )
    state._seen_payload_hashes[payload_hash] = now

    # 5. rate window
    count = state.hit(bucket, now)
    fields["rate_window_state"] = f"{count}/{state.rate_limit_per_window}"
    if count > state.rate_limit_per_window:
        fields["quota_verdict"] = QuotaVerdict.THROTTLED
        fields["retry_after_seconds"] = state.rate_window_size
        return StageResult(
            passed=False,
            reason_codes=[IngressReasonCode.QUOTA_EXCEEDED],
            fields=fields,
        )

    # 6. burst cap (last 5s of the window)
    burst_cutoff = now - 5
    burst_count = sum(1 for t in state._window_counters[bucket] if t >= burst_cutoff)
    if burst_count > state.burst_limit:
        fields["quota_verdict"] = QuotaVerdict.THROTTLED
        fields["retry_after_seconds"] = 5
        return StageResult(
            passed=False,
            reason_codes=[IngressReasonCode.BURST_LIMIT],
            fields=fields,
        )

    return StageResult(passed=True, fields=fields)


# ---------------------------------------------------------------------------
# E4 — DID YOU FILL OUT THE FORM? (schema + envelope validity)
# ---------------------------------------------------------------------------

# Minimum supported envelope versions. We accept "1" and "1.x".
_SUPPORTED_ENVELOPE_VERSIONS: frozenset[str] = frozenset({"1", "1.0", "1.1", "1.2"})

# Recognized request shape classes inferred from source_class + body shape.
# Intake is shape-only — these labels do NOT decide route or intent.
_SHAPE_BY_SOURCE: Mapping[SourceClass, str] = {
    SourceClass.USER: "user_chat",
    SourceClass.SERVICE: "service_call",
    SourceClass.BATCH: "batch_job",
    SourceClass.WEBHOOK: "webhook_event",
    SourceClass.ALERT: "alert_event",
}

# Modalities intake recognizes by MIME prefix. Anything else is "unsupported".
_RECOGNIZED_MIME_PREFIXES: tuple[tuple[str, str], ...] = (
    ("text/", "text"),
    ("application/json", "text"),
    ("application/xml", "text"),
    ("application/pdf", "file"),
    ("application/octet-stream", "file"),
    ("image/", "image"),
    ("audio/", "audio"),
    ("video/", "video"),
)

_URL_RE = re.compile(r"^https?://[^\s]+$")
_MAX_TEXT_LEN = 256 * 1024  # 256 KiB
_MAX_PAYLOAD_DEPTH = 32


def _modality_from_mime(mime: str) -> str:
    mime = (mime or "").lower()
    for prefix, label in _RECOGNIZED_MIME_PREFIXES:
        if mime.startswith(prefix):
            return label
    return "unsupported"


def _depth(obj: Any, current: int = 0, limit: int = _MAX_PAYLOAD_DEPTH) -> int:
    if current > limit:
        return current
    if isinstance(obj, Mapping):
        return max((_depth(v, current + 1, limit) for v in obj.values()), default=current + 1)
    if isinstance(obj, (list, tuple)):
        return max((_depth(v, current + 1, limit) for v in obj), default=current + 1)
    return current


def run_e4_schema(
    env: RawIngressEnvelope,
    source_class: SourceClass,
    *,
    state: QuotaState,
) -> StageResult:
    """Verify recognized shape and structural validity. Spec line 317-372."""
    fields: dict[str, Any] = {}
    report: list[str] = []

    # 1. envelope version
    declared_version = str((env.extras or {}).get("envelope_version", "1"))
    if declared_version not in _SUPPORTED_ENVELOPE_VERSIONS:
        return StageResult(
            passed=False,
            reason_codes=[IngressReasonCode.MALFORMED_ENVELOPE],
            fields={
                "schema_verdict": SchemaVerdict.MALFORMED,
                "envelope_version": declared_version,
                "field_validation_report": ("envelope_version_unknown",),
            },
        )
    fields["envelope_version"] = declared_version

    # 2. request shape class
    shape_class = _SHAPE_BY_SOURCE.get(source_class, "unknown")
    fields["request_shape_class"] = shape_class

    # 3. text length cap
    if env.body_text is not None and len(env.body_text) > _MAX_TEXT_LEN:
        return StageResult(
            passed=False,
            reason_codes=[IngressReasonCode.PAYLOAD_TOO_LARGE],
            fields={"schema_verdict": SchemaVerdict.UNSUPPORTED, **fields},
        )

    # 4. payload depth bound
    if env.body_json is not None:
        d = _depth(env.body_json)
        if d > _MAX_PAYLOAD_DEPTH:
            return StageResult(
                passed=False,
                reason_codes=[IngressReasonCode.PAYLOAD_TOO_LARGE],
                fields={"schema_verdict": SchemaVerdict.UNSUPPORTED, **fields},
            )

    # 5. attachments — declared modality vs MIME
    declared_mods: list[str] = list(env.declared_modalities or ())
    observed_mods: list[str] = []
    for entry in env.attachments.entries:
        observed = _modality_from_mime(entry.mime_type)
        observed_mods.append(observed)
        if observed == "unsupported":
            return StageResult(
                passed=False,
                reason_codes=[IngressReasonCode.UNSUPPORTED_MODALITY],
                fields={
                    "schema_verdict": SchemaVerdict.UNSUPPORTED,
                    "field_validation_report": (f"unsupported_mime:{entry.mime_type}",),
                    **fields,
                },
            )

    if env.body_text is not None and "text" not in observed_mods:
        observed_mods.append("text")
    if not declared_mods and observed_mods:
        declared_mods = list(observed_mods)

    fields["modality_manifest"] = ModalityManifest(
        declared=tuple(declared_mods),
        observed=tuple(observed_mods),
    )
    fields["attachment_manifest_structural"] = env.attachments

    # 6. batch shape sanity
    if source_class == SourceClass.BATCH:
        # batch must declare a batch_id; missing is malformed
        if not env.batch_id:
            return StageResult(
                passed=False,
                reason_codes=[IngressReasonCode.MALFORMED_ENVELOPE],
                fields={
                    "schema_verdict": SchemaVerdict.MALFORMED,
                    "field_validation_report": ("missing_batch_id",),
                    **fields,
                },
            )
        # batch_size cap
        items = (env.body_json or {}).get("items") if env.body_json else None
        if isinstance(items, list) and len(items) > state.max_batch_size:
            return StageResult(
                passed=False,
                reason_codes=[IngressReasonCode.PAYLOAD_TOO_LARGE],
                fields={
                    "schema_verdict": SchemaVerdict.UNSUPPORTED,
                    "field_validation_report": (f"batch_oversize:{len(items)}",),
                    **fields,
                },
            )

    # 7. webhook signature shell (must declare delivery_id)
    if source_class in (SourceClass.WEBHOOK, SourceClass.ALERT):
        if not env.webhook_delivery_id and not env.alert_id:
            return StageResult(
                passed=False,
                reason_codes=[IngressReasonCode.MALFORMED_ENVELOPE],
                fields={
                    "schema_verdict": SchemaVerdict.MALFORMED,
                    "field_validation_report": ("missing_delivery_id",),
                    **fields,
                },
            )

    # 8. URL syntactic check (no fetch — spec line 342)
    if env.body_json:
        for k, v in env.body_json.items() if hasattr(env.body_json, "items") else []:
            if isinstance(v, str) and (k.lower().endswith("url") or k.lower() == "callback"):
                if not _URL_RE.match(v):
                    return StageResult(
                        passed=False,
                        reason_codes=[IngressReasonCode.FIELD_TYPE_MISMATCH],
                        fields={
                            "schema_verdict": SchemaVerdict.MALFORMED,
                            "field_validation_report": (f"bad_url:{k}",),
                            **fields,
                        },
                    )

    fields["schema_verdict"] = SchemaVerdict.VALID
    fields["field_validation_report"] = tuple(report)
    return StageResult(passed=True, fields=fields)


# ---------------------------------------------------------------------------
# E5 — FIXING MESSY HANDWRITING (safe normalization)
# ---------------------------------------------------------------------------

# Patterns flagged as "suspicious" — kept as data, never obeyed (spec line 401, 437).
_SUSPICIOUS_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_previous_instructions", re.compile(r"ignore (all )?previous instructions", re.I)),
    ("system_role_injection", re.compile(r"\bsystem\s*:\s*you are\b", re.I)),
    ("prompt_assistant_role_injection", re.compile(r"<\|im_start\|>", re.I)),
    ("tool_call_injection", re.compile(r"<tool_call>", re.I)),
)

_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_MULTI_WS_RE = re.compile(r"[ \t]+")


def normalize_text(text: str) -> tuple[str, list[str]]:
    """Return (normalized_text, normalization_report).

    Steps applied (all reversible / shape-only):
    - NFC Unicode canonicalization.
    - Strip control chars except \\n and \\t.
    - Normalize newlines to \\n.
    - Collapse runs of spaces/tabs to single space (within a line).
    - Strip leading/trailing whitespace.
    """
    report: list[str] = []
    out = unicodedata.normalize("NFC", text)
    if out != text:
        report.append("nfc_applied")

    if "\r\n" in out or "\r" in out:
        out = out.replace("\r\n", "\n").replace("\r", "\n")
        report.append("newlines_normalized")

    cleaned = _CONTROL_CHARS_RE.sub("", out)
    if cleaned != out:
        report.append("control_chars_stripped")
    out = cleaned

    new_lines = []
    for line in out.split("\n"):
        collapsed = _MULTI_WS_RE.sub(" ", line)
        new_lines.append(collapsed)
    rejoined = "\n".join(new_lines)
    if rejoined != out:
        report.append("whitespace_collapsed")
    out = rejoined.strip()
    if out != rejoined:
        report.append("trimmed")

    return out, report


def detect_suspicious_markers(text: str) -> list[str]:
    """Return marker labels for suspicious patterns. Never modifies the text."""
    markers: list[str] = []
    for label, pattern in _SUSPICIOUS_PATTERNS:
        if pattern.search(text):
            markers.append(label)
    return markers


def canonicalize_filename(name: str) -> str:
    """Strip path components, NFC normalize, replace path separators with underscore."""
    base = unicodedata.normalize("NFC", name)
    # Strip directory components (\, /).
    for sep in ("\\", "/"):
        if sep in base:
            base = base.rsplit(sep, 1)[-1]
    # Replace remaining path-like chars defensively.
    base = base.replace("\x00", "")
    return base.strip()


def canonicalize_mime(mime: str) -> str:
    """Lowercase, trim, strip parameters past first ';'."""
    if not mime:
        return ""
    head = mime.split(";", 1)[0].strip().lower()
    return head


def run_e5_normalize(
    env: RawIngressEnvelope,
    e1_fields: Mapping[str, Any],
) -> StageResult:
    """Normalize transport noise without changing intent. Spec line 374-438."""
    report: list[str] = []
    suspicious: list[str] = []
    fields: dict[str, Any] = {}

    raw_text = env.body_text or ""
    raw_payload_hash = hash_payload(
        env.body_text,
        env.body_json,
        tuple(a.ref for a in env.attachments.entries),
    )

    try:
        normalized_text, text_report = normalize_text(raw_text)
    except (UnicodeError, ValueError) as exc:
        return StageResult(
            passed=False,
            reason_codes=[IngressReasonCode.NORMALIZATION_UNSAFE],
            fields={
                "normalization_verdict": NormalizationVerdict.REJECTED,
                "normalization_report": (f"decode_failure:{exc.__class__.__name__}",),
            },
        )
    report.extend(text_report)

    if normalized_text:
        suspicious.extend(detect_suspicious_markers(normalized_text))

    # canonicalize attachments
    canonical_entries: list[AttachmentManifestEntry] = []
    for entry in env.attachments.entries:
        canonical_name = canonicalize_filename(entry.filename)
        canonical_mime = canonicalize_mime(entry.mime_type)
        if not canonical_name:
            return StageResult(
                passed=False,
                reason_codes=[IngressReasonCode.ATTACHMENT_MANIFEST_BAD],
                fields={
                    "normalization_verdict": NormalizationVerdict.REJECTED,
                    "normalization_report": ("bad_filename",),
                },
            )
        canonical_entries.append(
            AttachmentManifestEntry(
                filename=canonical_name,
                mime_type=canonical_mime,
                size_bytes=entry.size_bytes,
                ref=entry.ref,
                declared_modality=entry.declared_modality,
            )
        )

    canonical_manifest = AttachmentManifestShell(
        entries=tuple(canonical_entries),
        total_bytes=env.attachments.total_bytes,
    )

    normalized_payload_hash = hash_text(normalized_text)
    request_id = e1_fields.get("request_id", "unknown")

    verdict = NormalizationVerdict.NORMALIZED if report else NormalizationVerdict.PRESERVED

    fields.update(
        {
            "normalization_verdict": verdict,
            "normalized_payload": normalized_text,
            "normalized_payload_ref": f"normalized://{request_id}",
            "raw_payload_ref": e1_fields.get("raw_payload_ref", f"raw://{request_id}"),
            "raw_payload_hash": raw_payload_hash,
            "normalized_payload_hash": normalized_payload_hash,
            "normalization_report": tuple(report),
            "suspicious_field_markers": tuple(suspicious),
            "attachment_manifest_canonical": canonical_manifest,
        }
    )
    return StageResult(passed=True, fields=fields)


# ---------------------------------------------------------------------------
# E6 — STAMPING THE TICKET (final assembly)
# ---------------------------------------------------------------------------

# E6 itself does not have rejection conditions of its own beyond "trace
# binding failed" — the pipeline assembles fields from earlier stages.

__all__ = [
    "DEFAULT_ALLOWED_TRANSPORTS",
    "IdentityResolution",
    "IdentityResolver",
    "QuotaState",
    "StageResult",
    "canonicalize_filename",
    "canonicalize_mime",
    "classify_source",
    "default_identity_resolver",
    "detect_suspicious_markers",
    "normalize_text",
    "run_e1_real_request",
    "run_e2_identity",
    "run_e3_quota",
    "run_e4_schema",
    "run_e5_normalize",
]
