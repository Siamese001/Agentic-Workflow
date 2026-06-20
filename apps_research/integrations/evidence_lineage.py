"""Map governed research substrate outputs to bridge-facing evidence lineage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ResearchEvidenceLineageItem:
    """Single evidence row consumed by AppsResearchBridge._translate()."""

    source_id: str
    label: str
    uri: str
    source_type: str
    field_ref: str
    confidence: float = 0.0


def _chunk_lineage(chunk: Any, index: int, *, default_confidence: float) -> ResearchEvidenceLineageItem:
    meta = getattr(chunk, "metadata", {}) or {}
    chunk_id = str(getattr(chunk, "chunk_id", "") or f"chunk-{index}")
    uri = (
        str(meta.get("source_url") or "")
        or str(meta.get("canonical_digest") or "")
        or str(meta.get("file_path") or "")
        or f"chunk:{chunk_id}"
    )
    label = (
        str(meta.get("title") or "")
        or str(getattr(chunk, "content", "") or "")[:120]
        or chunk_id
    )
    source_type = str(meta.get("source_type") or meta.get("doc_type") or "web")
    field_ref = str(meta.get("field_ref") or "recipient_brief_ref")
    try:
        confidence = float(getattr(chunk, "combined_score", default_confidence) or default_confidence)
    except (TypeError, ValueError):
        confidence = default_confidence
    return ResearchEvidenceLineageItem(
        source_id=chunk_id,
        label=label,
        uri=uri,
        source_type=source_type,
        field_ref=field_ref,
        confidence=max(0.0, min(1.0, confidence)),
    )


def evidence_from_c0_bundle(bundle: Any, *, default_confidence: float = 0.0) -> tuple[ResearchEvidenceLineageItem, ...]:
    """Build lineage items from a shaped EvidenceBundle."""
    if bundle is None:
        return ()
    items: list[ResearchEvidenceLineageItem] = []
    for index, chunk in enumerate(getattr(bundle, "ranked_chunks", []) or []):
        items.append(_chunk_lineage(chunk, index, default_confidence=default_confidence))
    return tuple(items)


def evidence_from_company_brief(
    brief: dict[str, Any],
    *,
    default_confidence: float = 0.75,
) -> tuple[ResearchEvidenceLineageItem, ...]:
    """Build lineage items from CompanyBriefEngine ``_c0_bundle`` source portfolio."""
    c0_bundle = brief.get("_c0_bundle") if isinstance(brief, dict) else {}
    if not isinstance(c0_bundle, dict):
        return ()
    portfolio = c0_bundle.get("source_portfolio_summary") or {}
    urls = portfolio.get("source_urls") or []
    items: list[ResearchEvidenceLineageItem] = []
    for index, url in enumerate(urls):
        url_str = str(url or "").strip()
        if not url_str:
            continue
        items.append(
            ResearchEvidenceLineageItem(
                source_id=f"brief-url-{index}",
                label=url_str[:120],
                uri=url_str,
                source_type="web",
                field_ref="company_brief_ref",
                confidence=default_confidence,
            )
        )
    if items:
        return tuple(items)

    # Grounded content lines (non-URL) when Tavily is offline but findings exist.
    claim_map = c0_bundle.get("claim_evidence_map") or {}
    supported = int(claim_map.get("supported_count", 0) or 0)
    if supported > 0:
        topic = str(brief.get("company_name") or brief.get("topic") or "company_brief")
        return (
            ResearchEvidenceLineageItem(
                source_id="brief-supported-claims",
                label=f"{topic} briefing claims ({supported} supported)",
                uri=f"brief://{topic.replace(' ', '_')[:64]}",
                source_type="company_brief",
                field_ref="company_brief_ref",
                confidence=default_confidence,
            ),
        )
    return ()


def materialize_research_evidence(
    *,
    bundle: Any,
    request: Any,
    support_coverage: float,
) -> tuple[ResearchEvidenceLineageItem, ...]:
    """Prefer C0 bundle chunks; fall back to CompanyBriefEngine when C0 is empty."""
    default_conf = max(0.0, min(1.0, float(support_coverage or 0.0)))
    items = evidence_from_c0_bundle(bundle, default_confidence=default_conf or 0.5)
    if items:
        return items

    topic = str(getattr(request, "topic", "") or "").strip()
    if not topic:
        return ()

    try:
        from apps_research.engines.company_brief_engine import CompanyBriefEngine  # noqa: PLC0415
    except ImportError:
        return ()

    depth_profile = str(getattr(request, "depth_profile", "") or "COMPANY_BRIEF_STANDARD")
    raw_depth = depth_profile.split("_")[-1].lower() if depth_profile else "standard"
    if raw_depth not in ("shallow", "standard", "deep"):
        raw_depth = "standard"

    try:
        brief = CompanyBriefEngine().execute(
            {
                "topic": topic,
                "depth": raw_depth,
                "jd_context": getattr(request, "jd_context", None) or {},
            }
        )
    except (ImportError, RuntimeError, TypeError, ValueError, AttributeError, OSError):
        return ()

    if not isinstance(brief, dict):
        return ()
    return evidence_from_company_brief(brief, default_confidence=default_conf or 0.75)
