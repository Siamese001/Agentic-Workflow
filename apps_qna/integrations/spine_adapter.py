"""apps_qna ↔ agentic_core spine adapter.

Single integration surface between the apps_qna domain (interview taxonomy,
paste-budget arithmetic, route registry) and the agentic_core platform spine
(L2 Universal Write Gateway, L6 OpenTelemetry observability, future L0/L1/L2
reasoning surfaces in subsequent waves).

This module is the adapter-per-concern entrypoint per the constitutional
"every apps_* must leverage agentic_core spine" invariant. apps_qna depends
on it; nothing in agentic_core depends back on apps_qna (gravity preserved).

Wave 1 (foundation) coverage:
    - ``write_card_text`` / ``write_pack_manifest_json`` / ``ensure_pack_dir``
      -> route every apps_qna filesystem mutation through the L2 UWG
      (atomic writes, audit trail, anti-bypass — constitutional §3 alignment).
    - ``pack_build_span`` -> wrap the build pipeline in an OTel span tied
      to the canonical ``apps_qna.v1.*`` namespace, so a single trace covers
      ingest -> validation -> render -> write -> manifest.

Wave 2+ will extend this module with L1 retrieval-router calls (PDF
chunking), L2 execution callsites (STAR/RCA synthesis), L0 routing-bandit
hooks (route selection), and the ``apps_qna_pack_lifecycle`` ledger
writeback. That ledger is intentionally deferred — registry maintenance is
a separate concern; tracked under W1.4 of plan ``apps-qna-spine-integration``.

Template precedent: ``apps_eval/integrations/tracing.py`` (the OTel adapter
shape) and ``apps_shared/`` (the apps→spine boundary canon — 54.1% spine
coverage, all 7 layers touched).
"""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

# ---- L2 Universal Write Gateway (canonical write authority) -----------------

from agentic_core.L2_execution.utils.write_gateway import (
    ensure_dir as _uwg_ensure_dir,
    write_text as _uwg_write_text,
)

logger = logging.getLogger(__name__)

SPAN_NAMESPACE: str = "apps_qna.v1"
"""Canonical OTel tracer name for apps_qna spans."""

_ENV_ENABLE_SDK = "APPS_QNA_OTEL_SDK"
_PROVIDER_INSTALLED: bool = False


# ---- Filesystem mutation surface (UWG-routed) -------------------------------


def write_card_text(path: str | Path, content: str, *, encoding: str = "utf-8") -> str:
    """Write a rendered markdown card via the L2 Universal Write Gateway.

    Replaces the legacy ``Path.write_bytes`` / ``Path.write_text`` direct
    mutation. The UWG provides:

      * Atomic writes (temp file + ``os.replace``)
      * Source-root protection (rejects writes into ``agentic_core/``,
        ``apps_shared/``, ``ops_scripts/``, ``tests/`` — pack output lives
        in ``reports/qna/<slug>/`` which is not protected)
      * Mutation-ledger audit trail when ``set_mutation_ledger_path`` is
        active for the run
      * Lifecycle trace contract emission
      * Write-amplification + size-cap guards

    Line-ending normalization is the caller's responsibility; this function
    preserves bytes exactly as encoded from ``content``.
    """
    return _uwg_write_text(str(path), content, encoding=encoding)


def write_pack_manifest_json(path: str | Path, payload: str) -> str:
    """Write the pack_manifest.json file via UWG.

    The caller serializes the manifest to its canonical JSON string (so that
    pydantic ``model_dump`` + ``json.dumps`` ordering and indentation stay
    in apps_qna, not the spine). This function only handles the durable
    write boundary.
    """
    return _uwg_write_text(str(path), payload, encoding="utf-8")


def ensure_pack_dir(path: str | Path) -> Path:
    """Create the pack output directory via UWG ``ensure_dir``."""
    return _uwg_ensure_dir(str(path))


# ---- L6 Observability surface (OTel spans) ----------------------------------


def _try_install_sdk_provider() -> bool:
    """Best-effort SDK provider install when ``APPS_QNA_OTEL_SDK=1``.

    Returns True if a provider was installed by this call. When the env var
    is unset, the OTel API returns a NoOp tracer whose context manager
    still works — so callers never need to branch.
    """
    global _PROVIDER_INSTALLED
    if _PROVIDER_INSTALLED:
        return False
    if os.environ.get(_ENV_ENABLE_SDK, "").strip() not in {"1", "true", "TRUE", "yes"}:
        return False
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (
            BatchSpanProcessor,
            ConsoleSpanExporter,
        )
    except ImportError:
        return False

    if not isinstance(trace.get_tracer_provider(), TracerProvider):
        provider = TracerProvider()
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(provider)
        logger.info("apps_qna installed OTel SDK TracerProvider (ConsoleSpanExporter)")
    _PROVIDER_INSTALLED = True
    return True


def get_tracer(name: str = SPAN_NAMESPACE) -> Any:
    """Return the current OTel tracer (SDK or NoOp).

    When no SDK provider is configured the API returns a NoOpTracer whose
    context manager still works, so callers can always write::

        with get_tracer().start_as_current_span("apps_qna.v1.pack.build") as span:
            span.set_attribute("qna.slug", slug)
    """
    try:
        from opentelemetry import trace
    except ImportError:
        return _FallbackTracer()
    _try_install_sdk_provider()
    return trace.get_tracer(name)


class _FallbackTracer:
    """Last-resort tracer when even the opentelemetry-api package is missing."""

    @contextmanager
    def start_as_current_span(
        self,
        name: str,  # noqa: ARG002 - match OTel signature
        attributes: dict[str, Any] | None = None,  # noqa: ARG002
        **_: Any,
    ) -> Iterator["_FallbackSpan"]:
        yield _FallbackSpan()


class _FallbackSpan:
    """No-op span surface matching the subset of the OTel span API used here."""

    def set_attribute(self, key: str, value: Any) -> None:  # noqa: ARG002
        return None

    def set_attributes(self, attrs: dict[str, Any]) -> None:  # noqa: ARG002
        return None

    def record_exception(self, exception: BaseException) -> None:  # noqa: ARG002
        return None

    def set_status(self, status: Any) -> None:  # noqa: ARG002
        return None


@contextmanager
def pack_build_span(
    name: str,
    *,
    attributes: dict[str, Any] | None = None,
    tracer_name: str = SPAN_NAMESPACE,
) -> Iterator[Any]:
    """Wrap an apps_qna build operation in an OTel span.

    Example::

        from apps_qna.integrations.spine_adapter import pack_build_span

        with pack_build_span(
            "apps_qna.v1.pack.build",
            attributes={"qna.slug": slug, "qna.template_set": "v2"},
        ) as span:
            cards = builder.build(interview, output_dir)
            span.set_attribute("qna.cards_emitted", len(cards))
    """
    tracer = get_tracer(tracer_name)
    with tracer.start_as_current_span(name, attributes=attributes or {}) as span:
        try:
            yield span
        except BaseException as exc:  # guardian: allow-broad-exception -- OTel span exception recorder; catches all (incl. KeyboardInterrupt/SystemExit) to call span.record_exception then re-raises unchanged so original control flow is preserved
            try:
                span.record_exception(exc)
            except (
                AttributeError,
                TypeError,
                RuntimeError,
            ):  # guardian: allow-log-and-swallow -- span exception recording is best-effort telemetry; failure here must not mask the original exception about to re-raise
                logger.debug("pack_build_span: exception recording failed for %s", name)
            raise


# ---- L1 Cognition surface: topic classification (Wave 2) -------------------
#
# The PDF section-classification problem: a research-brief PDF is converted
# to plain text by pdfplumber/pypdf; the regex heading detector in
# ``from_research_brief._split_sections`` finds heading boundaries, but
# **classifying** a heading like "AMERICAS STRATEGY" against the canonical
# ResearchInputs targets used to be a substring-match heuristic that
# silently failed on PDFs whose headings did not contain any of the
# pre-baked hint strings. The Searce research brief landed entirely in one
# section because none of its headings matched the regex-substring map.
#
# Spine fix: embed each candidate target's textual descriptor once via
# BGE-M3 (cached for the process), and at classification time embed the
# section text + cosine-rank against descriptors. This is genuine semantic
# routing, not surface keyword matching.
#
# Graceful degradation contract: when sentence-transformers is not
# installed OR the BGE-M3 weights are not locally cached AND
# ``BGE_ALLOW_MODEL_DOWNLOAD`` is unset, the function falls back to a
# transparent keyword-overlap scorer. Tests run on the fallback path —
# embedding-based classification is opt-in via either pre-cached weights
# or ``BGE_ALLOW_MODEL_DOWNLOAD=true``.

import re as _re

_CANDIDATE_VEC_CACHE: dict[tuple[tuple[str, str], ...], dict[str, list[float]]] = {}


def _get_candidate_embeddings(
    candidates: dict[str, str],
) -> dict[str, list[float]] | None:
    """Embed the candidate descriptors once per process. Returns None on failure."""
    cache_key = tuple(sorted(candidates.items()))
    if cache_key in _CANDIDATE_VEC_CACHE:
        return _CANDIDATE_VEC_CACHE[cache_key]
    try:
        from agentic_core.embeddings.bge_runtime import bge_embed_batch

        keys = list(candidates.keys())
        descs = list(candidates.values())
        vecs = bge_embed_batch(descs)
        result = dict(zip(keys, vecs, strict=True))
    except (ImportError, RuntimeError, OSError, ValueError):
        # ImportError: sentence-transformers absent
        # RuntimeError: BGE_DIM_MISMATCH or BGEInstallError
        # OSError: model files not locally cached and BGE_ALLOW_MODEL_DOWNLOAD=false
        # ValueError: empty input from a misconfigured caller
        # All paths fall through to keyword scoring; this is the documented degradation.
        return None
    _CANDIDATE_VEC_CACHE[cache_key] = result
    return result


def _cosine_normalized(v1: list[float], v2: list[float]) -> float:
    """Cosine similarity for L2-normalized vectors == dot product."""
    return float(sum(a * b for a, b in zip(v1, v2, strict=True)))


def _keyword_classify(
    text: str, candidates: dict[str, str]
) -> tuple[str, float]:
    """Word-overlap fallback when BGE is unavailable.

    Score = |text_words ∩ descriptor_words| / |descriptor_words|.
    Imperfect, but transparent and deterministic.
    """
    text_words = set(_re.findall(r"\b[a-z]{3,}\b", text.lower()))
    if not text_words:
        return ("", 0.0)
    scores: dict[str, float] = {}
    for key, desc in candidates.items():
        desc_words = set(_re.findall(r"\b[a-z]{3,}\b", desc.lower()))
        if not desc_words:
            scores[key] = 0.0
            continue
        scores[key] = len(text_words & desc_words) / len(desc_words)
    if not scores:
        return ("", 0.0)
    best_key, best_score = max(scores.items(), key=lambda kv: kv[1])
    return (best_key, best_score)


def classify_section_topic(
    text: str,
    candidates: dict[str, str],
    *,
    max_chars: int = 2000,
) -> tuple[str, float, str]:
    """Classify a free-text section against named topic descriptors.

    Args:
        text: Raw section body.
        candidates: ``{topic_key: descriptor_text}`` map. The descriptor is
            the prose against which ``text`` is ranked. ``topic_key`` is the
            caller's symbol for the topic (e.g. ``"role_areas"``).
        max_chars: Cap on how much of ``text`` is fed to the embedder.
            BGE-M3 has a ~512-token effective limit; 2000 chars covers
            ≈400 tokens with English text and avoids silent truncation
            artifacts.

    Returns:
        ``(best_topic_key, score, mode)`` where:
            - ``best_topic_key`` is the highest-ranked key in ``candidates``
              (or empty string if neither path could classify).
            - ``score`` ∈ [0.0, 1.0] for the keyword path; ∈ [-1.0, 1.0]
              for the cosine path (in practice 0–1 since descriptors and
              section text are both English prose).
            - ``mode`` ∈ ``{"embedding", "keyword", "empty"}`` so callers
              can apply different thresholds per mode.

    Notes:
        Embedding path uses ``agentic_core.embeddings.bge_runtime`` (BGE-M3,
        1024-dim, L2-normalized). When unavailable, falls through to
        word-overlap. The embedding path is cached: candidate descriptors
        are embedded once per process; only the section text is embedded
        per call.
    """
    if not text or not text.strip():
        return ("", 0.0, "empty")
    if not candidates:
        return ("", 0.0, "empty")

    truncated = text.strip()[:max_chars]

    # Try the embedding path first.
    candidate_vecs = _get_candidate_embeddings(candidates)
    if candidate_vecs is not None:
        try:
            from agentic_core.embeddings.bge_runtime import bge_embed_query

            text_vec = bge_embed_query(truncated)
            scores = {
                k: _cosine_normalized(text_vec, v)
                for k, v in candidate_vecs.items()
            }
            best_key, best_score = max(scores.items(), key=lambda kv: kv[1])
            return (best_key, best_score, "embedding")
        except (ImportError, RuntimeError, OSError, ValueError):
            # Fall through to keyword scoring; same exception envelope as
            # _get_candidate_embeddings — keep the contract symmetric.
            pass

    best_key, best_score = _keyword_classify(truncated, candidates)
    return (best_key, best_score, "keyword")


# ---- L6 Observability surface: pack-lifecycle ledger writer (Wave 1.4) -----
#
# Every apps_qna pack build / lint / self-eval / route-select / paste-set /
# promote decision routes through this helper. The L6 ledger
# ``apps_qna_pack_lifecycle`` is the durable record surface W4 routers
# (NamespaceBandit, paste-set bandit, Wilson CI promotion) and W5
# system_learning consume for cross-interview transfer per constitutional
# §29 closed-loop router enforcement.
#
# Fail-soft contract: any ledger error is logged at debug and swallowed.
# Build pipelines NEVER crash because of ledger issues (matches
# tools.ledgers.hook_helpers.emit_ledger_event's own fail-soft envelope).


_PACK_LIFECYCLE_LEDGER_NAME: str = "apps_qna_pack_lifecycle"


def emit_pack_lifecycle_event(
    *,
    event_kind: str,
    prediction: Any = None,
    outcome: Any = None,
    score_band: str | None = None,
    score_numeric: float | None = None,
    repo_area: str = "",
    latency_ms: int | None = None,
    metadata: Any = None,
) -> str:
    """Emit one row to the apps_qna_pack_lifecycle ledger.

    Args:
        event_kind: one of ``pack_build``, ``pack_lint``,
            ``pack_self_eval``, ``route_select``, ``paste_set_select``,
            ``promote_decision``, ``interview_outcome`` (per the schema
            file's documented taxonomy).
        prediction: ledger-specific JSON-serializable dict; see schema
            comments for per-event_kind shapes.
        outcome: optional JSON-serializable dict bound at outcome time.
            None means "outcome not yet known"; can be late-bound via
            ``tools.ledgers.hook_helpers.bind_ledger_outcome``.
        score_band: per-event_kind banding (see schema comments).
        score_numeric: raw score before banding.
        repo_area: file/module path most relevant to the event. For
            ``pack_build``, this is typically ``reports/qna/<slug>/``.
        latency_ms: prediction-to-write duration when applicable.
        metadata: freeform JSON dict.

    Returns:
        The event_id on success, an empty string on any error or when
        ``LEDGER_WRITER_BYPASS=1`` is set.

    Notes:
        Constitutional §29 contract: this helper is the LIBRARY-CALL
        half of the paired ``ROUTER_DECISION:`` marker + ledger write.
        W4 routers (W4.1 NamespaceBandit, W4.2 paste-set bandit, W4.3
        promotion_decision) MUST emit both the marker AND call this
        helper in the same code path; missing either side is a §29
        violation logged by post_cascade_router_decision_audit.py.
    """
    try:
        from tools.ledgers.hook_helpers import emit_ledger_event

        return emit_ledger_event(
            ledger=_PACK_LIFECYCLE_LEDGER_NAME,
            event_kind=event_kind,
            prediction=prediction,
            outcome=outcome,
            score_band=score_band,
            score_numeric=score_numeric,
            repo_area=repo_area,
            latency_ms=latency_ms,
            metadata=metadata,
        )
    except Exception as exc:  # guardian: allow-broad-except -- ledger emit MUST be fail-soft per §29 contract; build pipeline cannot abort because of telemetry-emission error; the underlying emit_ledger_event already swallows exceptions but we double-wrap to also catch ImportError on environments where tools.ledgers is unavailable
        logger.debug("emit_pack_lifecycle_event suppressed: %r", exc)
        return ""


__all__ = [
    "SPAN_NAMESPACE",
    "classify_section_topic",
    "emit_pack_lifecycle_event",
    "ensure_pack_dir",
    "get_tracer",
    "pack_build_span",
    "write_card_text",
    "write_pack_manifest_json",
]
