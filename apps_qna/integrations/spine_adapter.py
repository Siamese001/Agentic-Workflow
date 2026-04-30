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


__all__ = [
    "SPAN_NAMESPACE",
    "ensure_pack_dir",
    "get_tracer",
    "pack_build_span",
    "write_card_text",
    "write_pack_manifest_json",
]
