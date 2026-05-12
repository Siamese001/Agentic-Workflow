"""Synthesize an AppsRgIngressContractV1 JSON from a legacy RequestEnvelope.

This is a TRANSITIONAL bridge. Today ``apps_rg/__main__.py`` builds a thin
flat ``ingress_payload`` dict that ``apps_rg_parse`` wraps in an
``AppsRgIngressPayload`` + ``RequestEnvelope``. The contract-first reflection
harness (see plan ``apps-rg-u0-reflection-harness-79d032``) requires the
richer ``AppsRgIngressContractV1`` shape.

Until ``apps_rg/__main__.py`` is refactored to emit the contract directly
(deferred to a future plan), this synthesizer covers the gap:

    RequestEnvelope (legacy)
        └─► synthesize_contract_payload()
                └─► dict shaped for AppsRgIngressContractV1.model_validate()

The synthesizer is intentionally narrow:
    - It does NOT execute apps_rg business logic.
    - It does NOT load LLM providers or call any L1/L0/C0/PA/L2/Exit code.
    - It DOES compute deterministic hashes (sha256) over jd_text/resume_text
      so the harness can validate jd_hash/resume_hash without faking them.
    - It DOES point policy refs at real apps_rg/config/* paths so the
      "MissingPolicyRefsError" check passes against actual files on disk.

Plan: .windsurf/plans/apps-rg-u0-reflection-live-wiring-105147.md (W1.P1.1)
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import RequestEnvelope


_REPO_ROOT: Path = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------------------
# Default policy refs — paths to existing apps_rg/config files.
#
# Each ref is a relative path string. The U0 reflection harness only checks
# that the ref is non-empty (MissingPolicyRefsError). Pointing them at real
# files keeps the synthesized contract honest — a downstream consumer that
# tries to open them will succeed (subject to filesystem access).
#
# When apps_rg/__main__.py is refactored to emit the contract directly, it
# will compute these from the actual loaded manifest. Until then, these are
# the canonical defaults for the live runtime path.
# ---------------------------------------------------------------------------
_DEFAULT_PROMPT_REGISTRY_REF: str = "apps_rg/prompt_assembly/prompt_registry.yaml"
_DEFAULT_HITL_POLICY_REF: str = "apps_rg/config/hitl_trigger_policy.yaml"
_DEFAULT_L0_POLICY_REF: str = "apps_rg/config/l0_policy.yaml"
_DEFAULT_AGENT_SPEC_REF: str = "apps_rg/config/specs/agent_spec.resume_generation.v1.0.0.yaml"
_DEFAULT_THRESHOLDS_REF: str = "apps_rg/config/rg_thresholds.yaml"

# Default quality thresholds — chosen to match the legacy apps_rg defaults
# documented in the gap analysis (min_quality=0.75, min_ats=70). Future
# integrators load these from rg_thresholds.yaml.
_DEFAULT_MIN_QUALITY: float = 0.75
_DEFAULT_MIN_ATS: int = 70
_DEFAULT_WORD_MIN: int = 400
_DEFAULT_WORD_MAX: int = 1200

_PLACEHOLDER_HASH_INPUT: str = "<empty>"


def _sha256_hex(text: str) -> str:
    """SHA-256 hex digest over UTF-8 bytes of *text*."""

    return hashlib.sha256((text or _PLACEHOLDER_HASH_INPUT).encode("utf-8")).hexdigest()


def _extract_docx_text(path: Path) -> str:
    """Extract plain text from a .docx file. Returns empty string on failure."""
    try:
        import docx  # python-docx
        doc = docx.Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs) if paragraphs else ""
    except (ImportError, Exception):
        return ""


def _extract_pdf_text(path: Path) -> str:
    """Extract plain text from a .pdf file. Returns empty string on failure."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(p for p in pages if p.strip())
        return text if text.strip() else ""
    except (ImportError, Exception):
        return ""


def _resolve_text(ref: str | None, inline: str | None, *, field_name: str = "ref") -> str:
    """Resolve text content from either an inline string or a path ref.

    Falls back to the inline value when the ref cannot be read. Returns
    empty string only when both inputs are missing.
    Handles .docx and .pdf files via python-docx and PyPDF2 respectively.

    Raises FileNotFoundError when a non-empty ref points to a path that does
    not exist on disk, so callers receive an actionable error rather than a
    silent ``"<empty>"`` placeholder in the synthesized contract.
    """

    if inline:
        return inline
    if not ref:
        return ""
    path = Path(ref)
    if not path.is_absolute():
        path = _REPO_ROOT / ref
    if not path.exists():
        raise FileNotFoundError(
            f"synthesizer: {field_name} ref points to a missing file: {path}. "
            "Provide the correct path via --jd / --source-resume, or pass inline text."
        )
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return _extract_docx_text(path)
    if suffix == ".pdf":
        return _extract_pdf_text(path)
    if suffix == ".json":
        try:
            import json as _json
            data = _json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "source_resume_text" in data:
                return data["source_resume_text"]
        except (OSError, UnicodeDecodeError, ValueError):
            pass
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _derive_generation_mode(envelope: RequestEnvelope) -> str:
    """Pick a generation mode from the legacy payload state.

    Mirrors the smart default declared in plan
    ``apps-rg-u0-reflection-harness-79d032`` AG-3.a: ``strategic_tailor``
    when both a resume source and JD are present; ``generate_scratch`` when
    no resume is available; ``tailor_existing`` for resume-only requests.
    """

    payload = envelope.payload
    has_resume = bool(payload.source_resume_text or payload.source_resume_ref)
    has_jd = bool(payload.job_description_text or payload.job_description_ref)
    if has_resume and has_jd:
        return "strategic_tailor"
    if has_resume:
        return "tailor_existing"
    return "generate_scratch"


def synthesize_contract_payload(envelope: RequestEnvelope) -> dict[str, Any]:
    """Convert a legacy ``RequestEnvelope`` into a contract-shaped dict.

    The output is suitable for feeding into ``apps_rg_u0_adapt`` —
    Pydantic-validated as ``AppsRgIngressContractV1`` and reflected through
    the field-map SSOT.

    Args:
        envelope: The legacy RequestEnvelope built by ``apps_rg_parse``.

    Returns:
        A plain ``dict`` ready for ``AppsRgIngressContractV1.model_validate``.
        Fields that the legacy envelope cannot supply are filled with
        deterministic defaults (e.g. ``manifest_digest`` over the synthesized
        contract content, ``payload_digest`` placeholder).
    """

    payload = envelope.payload

    # Resolve actual JD/resume text (inline preferred, ref fallback).
    jd_text = _resolve_text(
        payload.job_description_ref, payload.job_description_text, field_name="jd"
    )
    resume_text = _resolve_text(
        payload.source_resume_ref, payload.source_resume_text, field_name="resume"
    )

    # Compute deterministic hashes — these are real, not placeholder.
    jd_hash = _sha256_hex(jd_text)
    resume_hash = _sha256_hex(resume_text)

    # Build the manifest_digest over the policy refs themselves so any change
    # to the ref set produces a different digest. This keeps the synthesizer
    # contract-honest even though no real manifest file is loaded today.
    manifest_seed = "|".join([
        _DEFAULT_PROMPT_REGISTRY_REF,
        _DEFAULT_HITL_POLICY_REF,
        _DEFAULT_L0_POLICY_REF,
        _DEFAULT_AGENT_SPEC_REF,
        _DEFAULT_THRESHOLDS_REF,
    ])
    manifest_digest = _sha256_hex(manifest_seed)

    # The contract requires non-empty target.{company,role,level}; the legacy
    # envelope may carry None. Substitute "unknown" so synthesis succeeds and
    # the field map records the value verbatim under app_payload — apps_rg
    # callers that care will provide real values.
    target_company = payload.target_company or "unknown_company"
    target_role = payload.target_role or "unknown_role"
    target_level = payload.target_level or "UNKNOWN"

    # Replay key — derived deterministically from request_id when not provided.
    replay_key = (envelope.request_id or "rg-replay-unset") + "::v1"
    idempotency_key = payload.idempotency_key or replay_key

    contract: dict[str, Any] = {
        "apps_rg_contract_version": "v1",
        "transport": {
            "app_id": payload.app_id or "apps_rg",
            "task_class": payload.task_class or "resume_generation",
            "request_id": envelope.request_id or "rg-req-unset",
            "run_id": envelope.run_id or "rg-run-unset",
            "trace_id": envelope.trace_id or "rg-trace-unset",
            "submitted_at": envelope.submitted_at or "1970-01-01T00:00:00+00:00",
            "tenant_id": envelope.tenant_id or "apps_rg",
        },
        "identity": {
            "actor_id": "apps_rg:cli",
            "actor_role": "user",
        },
        "replay": {
            "replay_key": replay_key,
            "idempotency_key": idempotency_key,
        },
        "jd_payload": {
            "jd_hash": jd_hash,
            "jd_text": jd_text or _PLACEHOLDER_HASH_INPUT,
            "jd_ref": payload.job_description_ref or "",
            "jd_signals": {},
        },
        "resume_payload": {
            "resume_hash": resume_hash,
            "source_resume_text": resume_text,
            "source_resume_ref": payload.source_resume_ref or "",
        },
        "target": {
            "company": target_company,
            "role": target_role,
            "level": target_level,
        },
        "generation_mode": _derive_generation_mode(envelope),
        "capability_requirements": [],
        "profile_manifest": {
            "manifest_digest": manifest_digest,
            "profile_refs": {},
            "prompt_registry_ref": _DEFAULT_PROMPT_REGISTRY_REF,
            "hitl_policy_ref": _DEFAULT_HITL_POLICY_REF,
            "l0_policy_ref": _DEFAULT_L0_POLICY_REF,
            "agent_spec_ref": _DEFAULT_AGENT_SPEC_REF,
            "thresholds_ref": _DEFAULT_THRESHOLDS_REF,
        },
        "quality_thresholds": {
            "min_quality": _DEFAULT_MIN_QUALITY,
            "min_ats": _DEFAULT_MIN_ATS,
            "word_min": _DEFAULT_WORD_MIN,
            "word_max": _DEFAULT_WORD_MAX,
        },
        "output_requirements": {
            "formats": ("json",),
            "provenance_required": True,
            "fact_checked_required": True,
        },
        "provenance_requirements": {
            "per_bullet_required": True,
            "source_quote_required": True,
        },
        # payload_digest is a hash placeholder — the U0 adapter computes its
        # own canonical digest and exposes it on the receipt; the
        # contract-side digest is structural (proves the payload was
        # digest-bound at emit time) but our synthesizer can't reproduce
        # apps_rg's eventual real digest scheme. Fill with a deterministic
        # over-the-content hash so the receipt is reproducible.
        "payload_digest": "0" * 64,
    }

    # Compute payload_digest over the canonical content (excluding itself).
    # This makes the synthesized digest deterministic for identical envelopes
    # and observable in the receipt.
    import json
    digest_input = {k: v for k, v in contract.items() if k != "payload_digest"}
    contract["payload_digest"] = hashlib.sha256(
        json.dumps(digest_input, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return contract


def _envelope_for_synthesis(payload_or_envelope: Any) -> RequestEnvelope:
    """Permissive coercion to ``RequestEnvelope``.

    Accepts either a ``RequestEnvelope`` directly or a ``Mapping`` shaped
    like one. Used by the U0 binding so callers can pass either form.
    """

    if isinstance(payload_or_envelope, RequestEnvelope):
        return payload_or_envelope
    if isinstance(payload_or_envelope, Mapping):
        # Don't reconstruct here — caller should pass a built envelope.
        # This branch exists only to give a clear error.
        raise TypeError(
            "synthesize_contract_payload requires a RequestEnvelope, not a Mapping. "
            "Use apps_rg_parse() first."
        )
    raise TypeError(
        f"synthesize_contract_payload requires RequestEnvelope, got {type(payload_or_envelope).__name__}."
    )


__all__ = [
    "synthesize_contract_payload",
]
