"""RTC-REQ-056 consensus-jury panel — Single Source of Truth.

Per operator directive 2026-05-01 13:39 UTC-04:00, the RTC-REQ-056
live-provider allow proof is certifiable ONLY through the explicit
three-juror LLM-as-Judge consensus panel defined here:

    1. google_gemini / gemini / gemini-3.1-pro-preview
    2. anthropic    / claude / claude-sonnet-4-6
    3. openai       / openai / gpt-5.4-mini

This module is the ONE authoritative registry consumed by:

  - Readiness probes       (probe_live_provider_readiness.py)
  - Rubric stability probe (probe_live_provider_rubric_stability.py)
  - Integrated runtime probe (probe_integrated_runtime_safe_reuse.py)
  - ConsensusVeto          (consensus_veto.py)
  - Juror clients          (consensus_juror_clients.py)
  - Attestation writer     (_live_provider_attestation.py)
  - Composer gates         (compose_semantic_cache_subclaims.py)
  - Verifier gates         (verify_semantic_cache_certification.py,
                            verify_runtime_certification_acceptance.py)

Do NOT hardcode a different provider list in any of those consumers.
Do NOT add providers to this registry without updating tests and ADR.

Related rule: .claude/rules/closed-loop-router-enforcement.md (L5/hitl).
Attestation path (ONLY valid path for RTC-REQ-056 certification):
    artifacts/certification/integrated_runtime/consensus_jury/
        live_provider_attestation.json
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final


# ---------------------------------------------------------------------------
# Attestation schema version
# ---------------------------------------------------------------------------

ATTESTATION_SCHEMA_VERSION: Final[int] = 3
"""Schema v3 = panel attestation with mandatory ``control_surface`` and
``purpose`` stamping at top-level AND per-juror. v2 was panel without
those labels (rejected since 2026-05-01 control-surface directive).
v1 = legacy single-provider (diagnostic only, never certified)."""


# ---------------------------------------------------------------------------
# Certification-scope + control-surface labels
# ---------------------------------------------------------------------------

CERTIFICATION_SCOPE: Final[str] = "RTC-REQ-056"
"""Scope label embedded in every panel attestation."""

CONTROL_SURFACE: Final[str] = "llm_as_judge"
"""Stamped on every panel attestation (top-level AND per-juror) to
distinguish the certification surface from the healing/remediation
surface (``control_surface = "healing"`` in
``agentic_core.L2_execution.healers.healing_cascade_registry``).

Hard rule: healing artifacts NEVER satisfy RTC-REQ-056, regardless of
verdict shape. Enforced by ``rtc_req_056_gate.validate_panel_attestation``.
"""

PURPOSE: Final[str] = "certification"
"""Stamped alongside ``control_surface``. Pair disambiguates the
surface even if one label is missing or spoofed."""


# ---------------------------------------------------------------------------
# Panel policy
# ---------------------------------------------------------------------------

JUDGE_MODE: Final[str] = "consensus_jury"
QUORUM_RULE: Final[str] = "all_required_safe"

# Policy toggles — hard-coded False for RTC-REQ-056. Do NOT flip in code.
FAIL_CLOSED_ON_ANY_NON_SAFE: Final[bool] = True
ALLOW_SINGLE_MODEL_FALLBACK: Final[bool] = False
ALLOW_LOCAL_QWEN_FOR_CERTIFICATION: Final[bool] = False
ALLOW_MOCK_SAFE_FOR_CERTIFICATION: Final[bool] = False
ALLOW_DETERMINISTIC_STAGE_FOR_CERTIFICATION: Final[bool] = False


# ---------------------------------------------------------------------------
# Juror registry (the three required jurors)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class JurorSpec:
    """Registry entry for one juror.

    Attributes:
        juror_id: Stable identifier joining family + provider + model.
        provider_family: Upper-level family name (e.g. "google_gemini").
        provider: Provider short name (e.g. "gemini").
        model_id: Exact model identifier that the SDK will be asked to serve.
        env_key: Primary API-key env-var name.
        env_key_aliases: Alternative env-var names accepted.
        model_env_override: Optional env var that allows swapping model_id;
            the override MUST match ``model_id`` or ``model_aliases``
            to be accepted; otherwise REJECT_UNREGISTERED_MODEL.
        model_aliases: Accepted aliases for ``model_id`` env override.
    """

    juror_id: str
    provider_family: str
    provider: str
    model_id: str
    env_key: str
    env_key_aliases: tuple[str, ...] = field(default_factory=tuple)
    model_env_override: str | None = None
    model_aliases: tuple[str, ...] = field(default_factory=tuple)


GEMINI_JUROR: Final[JurorSpec] = JurorSpec(
    juror_id="google_gemini_3_1_pro_preview",
    provider_family="google_gemini",
    provider="gemini",
    model_id="gemini-3.1-pro-preview",
    env_key="GOOGLE_API_KEY",
    env_key_aliases=("GEMINI_API_KEY",),  # GEMINI_API_KEY deprecated — use GOOGLE_API_KEY
    model_env_override="GOOGLE_AI_MODEL",
    model_aliases=("gemini-3.1-pro-preview",),
)

ANTHROPIC_JUROR: Final[JurorSpec] = JurorSpec(
    juror_id="anthropic_claude_sonnet_4_6",
    provider_family="anthropic",
    provider="claude",
    model_id="claude-sonnet-4-6",
    env_key="ANTHROPIC_API_KEY",
    env_key_aliases=(),
    model_env_override="ANTHROPIC_MODEL",
    model_aliases=("claude-sonnet-4-6",),
)

OPENAI_JUROR: Final[JurorSpec] = JurorSpec(
    juror_id="openai_gpt_5_4_mini",
    provider_family="openai",
    provider="openai",
    model_id="gpt-5.4-mini",
    env_key="OPENAI_API_KEY",
    env_key_aliases=(),
    model_env_override="OPENAI_MODEL",
    model_aliases=("gpt-5.4-mini",),
)


REQUIRED_JURORS: Final[tuple[JurorSpec, ...]] = (
    GEMINI_JUROR,
    ANTHROPIC_JUROR,
    OPENAI_JUROR,
)
REQUIRED_JUROR_COUNT: Final[int] = len(REQUIRED_JURORS)


# ---------------------------------------------------------------------------
# Explicit rejection reason codes (enumerated for composer/verifier use)
# ---------------------------------------------------------------------------


class RejectReason:
    """Rejection reason codes emitted by probes, composer, verifier, veto.

    Every condition that prevents RTC-REQ-056 from reaching ACCEPTED status
    MUST map to exactly one code here. The code is the machine-readable
    signal for downstream gates; the accompanying human message is the
    audit trail for humans.
    """

    # Provider / model identity
    REJECT_LOCAL_QWEN_FOR_RTC_REQ_056 = "REJECT_LOCAL_QWEN_FOR_RTC_REQ_056"
    REJECT_QWEN_FOR_RTC_REQ_056 = "REJECT_QWEN_FOR_RTC_REQ_056"
    REJECT_ANTHROPIC_HAIKU_FOR_RTC_REQ_056 = "REJECT_ANTHROPIC_HAIKU_FOR_RTC_REQ_056"
    REJECT_MOCK_SAFE_IN_CERTIFICATION = "REJECT_MOCK_SAFE_IN_CERTIFICATION"
    REJECT_DETERMINISTIC_STAGE_IN_CERTIFICATION = (
        "REJECT_DETERMINISTIC_STAGE_IN_CERTIFICATION"
    )
    REJECT_SINGLE_MODEL_JUDGE_FOR_RTC_REQ_056 = (
        "REJECT_SINGLE_MODEL_JUDGE_FOR_RTC_REQ_056"
    )
    REJECT_UNREGISTERED_PROVIDER = "REJECT_UNREGISTERED_PROVIDER"
    REJECT_UNREGISTERED_MODEL = "REJECT_UNREGISTERED_MODEL"
    REJECT_PROVIDER_MODEL_MISMATCH = "REJECT_PROVIDER_MODEL_MISMATCH"

    # Quorum / policy
    REJECT_MISSING_JUROR = "REJECT_MISSING_JUROR"
    REJECT_MISSING_QUORUM_RULE = "REJECT_MISSING_QUORUM_RULE"
    REJECT_PANEL_NOT_FULLY_SAFE = "REJECT_PANEL_NOT_FULLY_SAFE"

    # Attestation integrity
    REJECT_MISSING_PANEL_ATTESTATION = "REJECT_MISSING_PANEL_ATTESTATION"
    REJECT_MALFORMED_JUROR_OUTPUT = "REJECT_MALFORMED_JUROR_OUTPUT"

    # Per-juror failure modes
    REJECT_JUROR_UNKNOWN = "REJECT_JUROR_UNKNOWN"
    REJECT_JUROR_UNSAFE = "REJECT_JUROR_UNSAFE"
    REJECT_JUROR_TIMEOUT = "REJECT_JUROR_TIMEOUT"
    REJECT_JUROR_ERROR = "REJECT_JUROR_ERROR"
    REJECT_JUROR_PARSE_FAIL = "REJECT_JUROR_PARSE_FAIL"

    # Control-surface separation (operator directive 2026-05-01 14:15)
    REJECT_HEALING_OUTPUT_FOR_JUDGE_CERTIFICATION = (
        "REJECT_HEALING_OUTPUT_FOR_JUDGE_CERTIFICATION"
    )
    REJECT_CONTROL_SURFACE_MISSING = "REJECT_CONTROL_SURFACE_MISSING"
    REJECT_CONTROL_SURFACE_MISMATCH = "REJECT_CONTROL_SURFACE_MISMATCH"
    REJECT_DETERMINISTIC_HEALING_FOR_RTC_REQ_056 = (
        "REJECT_DETERMINISTIC_HEALING_FOR_RTC_REQ_056"
    )
    REJECT_QWEN_HEALING_FOR_RTC_REQ_056 = "REJECT_QWEN_HEALING_FOR_RTC_REQ_056"
    REJECT_GEMINI_FLASH_HEALING_FOR_RTC_REQ_056 = (
        "REJECT_GEMINI_FLASH_HEALING_FOR_RTC_REQ_056"
    )
    REJECT_HEALING_GEMINI_PRO_NOT_PANEL_JUROR = (
        "REJECT_HEALING_GEMINI_PRO_NOT_PANEL_JUROR"
    )

    # Infrastructure (not a hard reject — signals PENDING)
    INFRASTRUCTURE_GAP_MISSING_KEY = "INFRASTRUCTURE_GAP_MISSING_KEY"

    ALL_CODES: Final = frozenset({
        "REJECT_LOCAL_QWEN_FOR_RTC_REQ_056",
        "REJECT_QWEN_FOR_RTC_REQ_056",
        "REJECT_ANTHROPIC_HAIKU_FOR_RTC_REQ_056",
        "REJECT_MOCK_SAFE_IN_CERTIFICATION",
        "REJECT_DETERMINISTIC_STAGE_IN_CERTIFICATION",
        "REJECT_SINGLE_MODEL_JUDGE_FOR_RTC_REQ_056",
        "REJECT_UNREGISTERED_PROVIDER",
        "REJECT_UNREGISTERED_MODEL",
        "REJECT_PROVIDER_MODEL_MISMATCH",
        "REJECT_MISSING_JUROR",
        "REJECT_MISSING_QUORUM_RULE",
        "REJECT_PANEL_NOT_FULLY_SAFE",
        "REJECT_MISSING_PANEL_ATTESTATION",
        "REJECT_MALFORMED_JUROR_OUTPUT",
        "REJECT_JUROR_UNKNOWN",
        "REJECT_JUROR_UNSAFE",
        "REJECT_JUROR_TIMEOUT",
        "REJECT_JUROR_ERROR",
        "REJECT_JUROR_PARSE_FAIL",
        "REJECT_HEALING_OUTPUT_FOR_JUDGE_CERTIFICATION",
        "REJECT_CONTROL_SURFACE_MISSING",
        "REJECT_CONTROL_SURFACE_MISMATCH",
        "REJECT_DETERMINISTIC_HEALING_FOR_RTC_REQ_056",
        "REJECT_QWEN_HEALING_FOR_RTC_REQ_056",
        "REJECT_GEMINI_FLASH_HEALING_FOR_RTC_REQ_056",
        "REJECT_HEALING_GEMINI_PRO_NOT_PANEL_JUROR",
        "INFRASTRUCTURE_GAP_MISSING_KEY",
    })


# ---------------------------------------------------------------------------
# Control-surface / healing-tier classifier (operator directive 2026-05-01 14:15)
# ---------------------------------------------------------------------------


def classify_healing_tier_for_reject(
    control_surface: str | None,
    healing_tier: str | None,
    model_id: str | None,
) -> str | None:
    """Map a (control_surface, healing_tier, model_id) triple to the
    specific REJECT_ code that should fire for RTC-REQ-056.

    Rules (evaluated in order):

      1. ``control_surface is None`` (missing field) ->
         ``REJECT_CONTROL_SURFACE_MISSING``
      2. ``control_surface == "healing"`` dispatches by ``healing_tier``:
         - ``"deterministic"``  -> ``REJECT_DETERMINISTIC_HEALING_FOR_RTC_REQ_056``
         - ``"qwen"``           -> ``REJECT_QWEN_HEALING_FOR_RTC_REQ_056``
         - ``"gemini_flash"``   -> ``REJECT_GEMINI_FLASH_HEALING_FOR_RTC_REQ_056``
         - ``"gemini_pro"``     -> ``REJECT_HEALING_GEMINI_PRO_NOT_PANEL_JUROR``
         - anything else (or tier absent) ->
           ``REJECT_HEALING_OUTPUT_FOR_JUDGE_CERTIFICATION``
      3. ``control_surface`` present but not ``"llm_as_judge"`` ->
         ``REJECT_CONTROL_SURFACE_MISMATCH``
      4. Returns ``None`` when the surface is ``"llm_as_judge"`` (caller
         proceeds to the rest of the gate).

    ``model_id`` is accepted for future granularity (e.g. specific
    rejection codes per healing model pin) but is currently unused
    except in the generic healing bucket.
    """
    if control_surface is None or (
        isinstance(control_surface, str) and control_surface.strip() == ""
    ):
        return RejectReason.REJECT_CONTROL_SURFACE_MISSING

    surface = str(control_surface).strip().lower()

    if surface == "healing":
        tier = (healing_tier or "").strip().lower()
        if tier == "deterministic":
            return RejectReason.REJECT_DETERMINISTIC_HEALING_FOR_RTC_REQ_056
        if tier == "qwen":
            return RejectReason.REJECT_QWEN_HEALING_FOR_RTC_REQ_056
        if tier == "gemini_flash":
            return RejectReason.REJECT_GEMINI_FLASH_HEALING_FOR_RTC_REQ_056
        if tier == "gemini_pro":
            return RejectReason.REJECT_HEALING_GEMINI_PRO_NOT_PANEL_JUROR
        return RejectReason.REJECT_HEALING_OUTPUT_FOR_JUDGE_CERTIFICATION

    if surface != "llm_as_judge":
        return RejectReason.REJECT_CONTROL_SURFACE_MISMATCH

    return None


# ---------------------------------------------------------------------------
# Explicit rejection lists — names that MUST NOT satisfy RTC-REQ-056
# ---------------------------------------------------------------------------

REJECTED_PROVIDERS_FOR_CERT: Final[frozenset[str]] = frozenset({
    "local_qwen",
    "qwen",
    "anthropic_haiku",
    "mock",
    "mock_safe",
    "deterministic",
    "deterministic_proof_stage",
})
"""Provider names that MUST be rejected with a specific reason code."""

REJECTED_MODELS_FOR_CERT: Final[frozenset[str]] = frozenset({
    "Qwen/Qwen2.5-32B-Instruct-AWQ",
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen2.5-7B-Instruct",
    "Qwen2.5-32B-Instruct-AWQ",
    "claude-3-haiku-20240307",
    "claude-haiku-4-5",
})
"""Model IDs that MUST be rejected with REJECT_QWEN_FOR_RTC_REQ_056 /
REJECT_ANTHROPIC_HAIKU_FOR_RTC_REQ_056 / similar."""


def classify_rejected_provider(provider: str | None) -> str | None:
    """Map a provider name to its specific REJECT_ reason code.

    Returns ``None`` if the provider is not in the rejected list (caller
    should then continue to registry-lookup / unregistered checks).
    """
    if not provider:
        return None
    p = provider.strip().lower()
    if p in ("local_qwen", "qwen"):
        if p == "local_qwen":
            return RejectReason.REJECT_LOCAL_QWEN_FOR_RTC_REQ_056
        return RejectReason.REJECT_QWEN_FOR_RTC_REQ_056
    if p == "anthropic_haiku":
        return RejectReason.REJECT_ANTHROPIC_HAIKU_FOR_RTC_REQ_056
    if p in ("mock", "mock_safe"):
        return RejectReason.REJECT_MOCK_SAFE_IN_CERTIFICATION
    if p in ("deterministic", "deterministic_proof_stage"):
        return RejectReason.REJECT_DETERMINISTIC_STAGE_IN_CERTIFICATION
    return None


def classify_rejected_model(model_id: str | None) -> str | None:
    """Map a model_id to its specific REJECT_ reason code.

    Returns ``None`` if the model is not in the rejected list.
    """
    if not model_id:
        return None
    m = model_id.strip()
    # Normalized Qwen variants
    if "Qwen" in m or m.startswith("qwen"):
        return RejectReason.REJECT_QWEN_FOR_RTC_REQ_056
    if m.startswith("claude-3-haiku") or m.startswith("claude-haiku"):
        return RejectReason.REJECT_ANTHROPIC_HAIKU_FOR_RTC_REQ_056
    return None


# ---------------------------------------------------------------------------
# Juror lookup helpers
# ---------------------------------------------------------------------------


def get_juror_by_provider(provider: str) -> JurorSpec | None:
    """Find a registered juror by provider short-name (case-insensitive)."""
    if not provider:
        return None
    p = provider.strip().lower()
    for j in REQUIRED_JURORS:
        if j.provider.lower() == p:
            return j
    return None


def get_juror_by_family(family: str) -> JurorSpec | None:
    """Find a registered juror by provider_family (case-insensitive)."""
    if not family:
        return None
    f = family.strip().lower()
    for j in REQUIRED_JURORS:
        if j.provider_family.lower() == f:
            return j
    return None


def is_registered_model(provider: str, model_id: str) -> bool:
    """True iff (provider, model_id) exactly matches a registered juror
    (respecting ``model_aliases``)."""
    j = get_juror_by_provider(provider)
    if j is None:
        return False
    if model_id == j.model_id:
        return True
    return model_id in j.model_aliases


# ---------------------------------------------------------------------------
# Artifact path (only valid path for RTC-REQ-056 certification)
# ---------------------------------------------------------------------------

CONSENSUS_JURY_ARTIFACT_SUBDIR: Final[str] = "consensus_jury"
"""Subdirectory under ``artifacts/certification/integrated_runtime/`` where
panel attestations MUST be written. Legacy root-level
``live_provider_attestation.json`` is diagnostic-only and cannot certify."""

PANEL_ATTESTATION_FILENAME: Final[str] = "live_provider_attestation.json"


def panel_artifact_path(repo_root) -> "Path":  # noqa: F821 — forward ref to Path
    """Resolve the panel attestation path relative to repo root."""
    from pathlib import Path as _P
    return (
        _P(repo_root)
        / "artifacts"
        / "certification"
        / "integrated_runtime"
        / CONSENSUS_JURY_ARTIFACT_SUBDIR
        / PANEL_ATTESTATION_FILENAME
    )


__all__ = [
    "ALLOW_DETERMINISTIC_STAGE_FOR_CERTIFICATION",
    "ALLOW_LOCAL_QWEN_FOR_CERTIFICATION",
    "ALLOW_MOCK_SAFE_FOR_CERTIFICATION",
    "ALLOW_SINGLE_MODEL_FALLBACK",
    "ANTHROPIC_JUROR",
    "ATTESTATION_SCHEMA_VERSION",
    "CERTIFICATION_SCOPE",
    "CONSENSUS_JURY_ARTIFACT_SUBDIR",
    "CONTROL_SURFACE",
    "FAIL_CLOSED_ON_ANY_NON_SAFE",
    "GEMINI_JUROR",
    "JUDGE_MODE",
    "JurorSpec",
    "OPENAI_JUROR",
    "PANEL_ATTESTATION_FILENAME",
    "PURPOSE",
    "QUORUM_RULE",
    "REJECTED_MODELS_FOR_CERT",
    "REJECTED_PROVIDERS_FOR_CERT",
    "REQUIRED_JURORS",
    "REQUIRED_JUROR_COUNT",
    "RejectReason",
    "classify_healing_tier_for_reject",
    "classify_rejected_model",
    "classify_rejected_provider",
    "get_juror_by_family",
    "get_juror_by_provider",
    "is_registered_model",
    "panel_artifact_path",
]
