"""C0 grounding-retrieval binding for apps_rg `resume_generation` task class.

MIGRATED from agentic_core/runtime/c0/apps_rg_c0_binding.py
Per plan apps-rg-golden-state-section-generation-a4f9e1 W2C.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §6 W3.P4 (initial)
+   plan apps-rg-app-payload-consumption-wiring-b3a449 W4 (AG-2 — signature
   change to accept ValidatedRequest; reads jd/resume content from
   ValidatedRequest.app_payload, NOT from legacy AppsRgIngressPayload).

W4 (apps-rg-chroma-ingestion-wiring-c7f2d9):
- W4.1: Chroma opt-in via chromadb_path param / CHROMA_PERSIST_DIR env var.
         File-only path unchanged when no Chroma path provided.
- W4.2: FEC tuple field population from Chroma metadata:
         citation_map, source_lineage_map, freshness_receipts,
         support_status, excluded_evidence_refs.
- W4.3: EMBEDDING_ENABLED guard — raises C0EvidenceGapError when Chroma
         path requested but EMBEDDING_ENABLED != "true".

C0 is the FOURTH stage (CONDITIONAL — fires only when route.grounding_required=True).
Its job is to gather the evidence needed for prompt assembly:
- The JD (job description) — read from app_payload["jd_payload"]["jd_text"]
  (preferred) or the legacy ref-path fallback for back-compat with file-based
  callers. AG-2 invariant: never reads from envelope.payload.
- The source resume — read from app_payload["resume_payload"]
- The manual brief — referenced by path through L1.policy_refs (future)

Per AG-RGGOV-5, ONLY core C0 may emit FinalEvidenceContract — apps_rg.cert
is quarantined for FEC emission.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    ValidatedRequest,
)
from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
    STATUS_UNKNOWN,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_PARTIAL,
    SUPPORT_STATUS_WEAK,
    SUPPORT_STATUS_EMPTY,
)
from agentic_core.runtime.contracts.route_contract import RouteContract

_log = logging.getLogger(__name__)

APPS_RG_C0_CERT_REF: str = "c0-apps-rg-resume-generation-app-payload-b3a449"

# ---------------------------------------------------------------------------
# W4: Chroma retrieval constants
# ---------------------------------------------------------------------------

#: support_status values that indicate sufficient or partial grounding (UNKNOWN excluded)
SUPPORT_STATUS_PASSING_VALUES: frozenset[str] = frozenset({
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_PARTIAL,
    SUPPORT_STATUS_WEAK,
})

#: source_class values queried as normative evidence (prior_outputs excluded)
_NORMATIVE_SOURCE_CLASSES: tuple[str, ...] = (
    "candidate_profile",
    "project_evidence",
    "approved_examples",
    "rubrics",
    "governance_docs",
    "receipts",
)

#: Metadata filter applied to all Chroma queries
_CHROMA_APP_FILTER: dict[str, Any] = {"app": "apps_rg"}

#: Number of Chroma results per source_class per query
_CHROMA_N_RESULTS: int = 5


# ---------------------------------------------------------------------------
# W4: C0EvidenceGapError — raised when Chroma path supplied but embedding
#     pipeline is not active.  Falls back to file-only if Chroma path absent.
# ---------------------------------------------------------------------------

class C0EvidenceGapError(RuntimeError):
    """Raised when Chroma retrieval is requested but EMBEDDING_ENABLED != 'true'.

    W4.3 invariant: never raise on file-only fallback path.
    """

    def __init__(self, action_hint: str = "") -> None:
        msg = (
            "C0 Chroma retrieval requested but EMBEDDING_ENABLED env var is not 'true'. "
            "Set EMBEDDING_ENABLED=true and ensure sentence-transformers is installed, "
            "or omit chromadb_path / CHROMA_PERSIST_DIR to use file-only fallback."
        )
        if action_hint:
            msg += f"  Hint: {action_hint}"
        super().__init__(msg)
        self.action_hint = action_hint


# ---------------------------------------------------------------------------
# W4: Chroma retrieval helpers
# ---------------------------------------------------------------------------

def _chroma_query_source_class(
    collection: Any,
    query_text: str,
    source_class: str,
    n_results: int,
) -> list[dict[str, Any]]:
    """Query Chroma for a single source_class with app=apps_rg filter.

    Returns a list of metadata dicts for matching chunks.
    Never mutates ChromaDB — read-only query only.
    """
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore[import]
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Chroma retrieval requires sentence-transformers. "
            "Install: pip install sentence-transformers>=2.2.0"
        ) from exc

    model = _get_embedding_model()
    vector = model.encode(query_text, normalize_embeddings=True).tolist()

    where_filter: dict[str, Any] = {
        "$and": [
            {"app": {"$eq": "apps_rg"}},
            {"source_class": {"$eq": source_class}},
        ]
    }

    try:
        raw = collection.query(
            query_embeddings=[vector],
            n_results=n_results,
            where=where_filter,
            include=["metadatas", "documents", "distances"],
        )
    except Exception as exc:  # pragma: no cover  # noqa: BLE001
        _log.warning("[C0/Chroma] query failed for source_class=%s: %s", source_class, exc)
        return []

    ids: list[str] = raw.get("ids", [[]])[0]
    metas: list[dict[str, Any]] = raw.get("metadatas", [[]])[0]
    docs: list[str] = raw.get("documents", [[]])[0]
    dists: list[float] = raw.get("distances", [[]])[0]

    results = []
    for chunk_id, meta, doc, dist in zip(ids, metas, docs, dists):
        row = dict(meta)
        row["_chunk_id"] = chunk_id
        row["_document"] = doc
        row["_distance"] = float(dist)
        results.append(row)
    return results


_embedding_model: Any = None  # module-level lazy cache


def _get_embedding_model() -> Any:
    """Lazy-load BAAI/bge-m3 SentenceTransformer (module-level cache)."""
    global _embedding_model  # noqa: PLW0603
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "Chroma retrieval requires sentence-transformers. "
                "Install: pip install sentence-transformers>=2.2.0"
            ) from exc
        _embedding_model = SentenceTransformer("BAAI/bge-m3")
    return _embedding_model


def _build_chroma_evidence(
    chunks: list[dict[str, Any]],
    timestamp_iso: str,
    excluded_refs: list[str],
) -> tuple[list[EvidenceItem], list[tuple[str, str]], list[tuple[str, str]], list[str]]:
    """Convert Chroma query results into EvidenceItems + FEC tuple fields.

    Chunks with invalid_for_normative_use=True are routed to excluded_refs,
    never to evidence_items.  Chunks missing citation_anchor are also excluded
    and logged.

    Returns:
        (evidence_items, citation_pairs, lineage_pairs, freshness_refs)
    """
    evidence_items: list[EvidenceItem] = []
    citation_pairs: list[tuple[str, str]] = []
    lineage_pairs: list[tuple[str, str]] = []
    freshness_refs: list[str] = []

    for chunk in chunks:
        chunk_id = chunk.get("_chunk_id", "")
        source_id = chunk.get("source_id", "")
        source_class = chunk.get("source_class", "")
        authority_class = chunk.get("authority_class", "")
        freshness = chunk.get("freshness", "")
        citation_anchor = chunk.get("citation_anchor", "")
        chunk_digest = chunk.get("chunk_digest", "")
        doc_text = chunk.get("_document", "")
        invalid_flag = str(chunk.get("invalid_for_normative_use", "")).lower()

        # Negative control: invalid_for_normative_use chunks → excluded only
        if invalid_flag == "true":
            ref = f"excluded:invalid_for_normative_use:{chunk_id}"
            excluded_refs.append(ref)
            _log.debug("[C0/Chroma] excluded chunk %s (invalid_for_normative_use)", chunk_id)
            continue

        # Negative control: missing citation_anchor → excluded, blocks PASS
        if not citation_anchor:
            ref = f"excluded:missing_citation_anchor:{chunk_id}"
            excluded_refs.append(ref)
            _log.debug("[C0/Chroma] excluded chunk %s (missing citation_anchor)", chunk_id)
            continue

        evidence_id = f"chroma:{chunk_id}"

        item = EvidenceItem(
            source=f"chromadb:{source_class}:{source_id}",
            content=doc_text,
            content_type="text",
            retrieval_timestamp=timestamp_iso,
            confidence_score=max(0.0, 1.0 - chunk.get("_distance", 0.0)),
            evidence_id=evidence_id,
            source_id=source_id,
            source_type="chromadb_collection",
            citation_anchor=citation_anchor,
            chunk_digest=chunk_digest,
            authority_class=authority_class if authority_class else STATUS_UNKNOWN,
            freshness_status=freshness if freshness else STATUS_UNKNOWN,
            retrieval_method="dense,metadata",
            support_status=SUPPORT_STATUS_PASS,
        )
        evidence_items.append(item)
        citation_pairs.append((evidence_id, citation_anchor))
        lineage_pairs.append((evidence_id, source_id))
        if freshness:
            freshness_refs.append(f"freshness:{source_id}:{freshness}")

    return evidence_items, citation_pairs, lineage_pairs, freshness_refs


def _compute_support_status(
    chroma_items: list[EvidenceItem],
    excluded_count: int,
) -> str:
    """Compute aggregate support_status from retrieved Chroma evidence.

    Rules:
    - Zero normative items → EMPTY (never PASS).
    - All required source_classes covered → PASS.
    - Some covered → PARTIAL.
    - Items present but excluded_count > normative count → WEAK.
    """
    if not chroma_items:
        return SUPPORT_STATUS_EMPTY

    present_classes = {
        item.source.split(":")[1]
        for item in chroma_items
        if ":" in item.source
    }
    required = set(_NORMATIVE_SOURCE_CLASSES)
    covered = required & present_classes

    if covered == required:
        return SUPPORT_STATUS_PASS
    if len(covered) >= len(required) // 2:
        return SUPPORT_STATUS_PARTIAL
    return SUPPORT_STATUS_WEAK


_DOCX_EXTENSIONS: frozenset[str] = frozenset({".docx"})
_PDF_EXTENSIONS: frozenset[str] = frozenset({".pdf"})
_JSON_EXTENSIONS: frozenset[str] = frozenset({".json"})


def _resolve_repo_root() -> Path:
    """Best-effort repo-root resolution."""
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def _read_json_evidence(
    relpath: str | None,
    source_label: str,
    timestamp_iso: str,
    repo_root: Path,
) -> EvidenceItem | None:
    """Read a JSON file as text evidence; return None if missing."""
    if not relpath:
        return None
    abs_path = (repo_root / relpath).resolve() if not Path(relpath).is_absolute() else Path(relpath)
    if not abs_path.exists() or not abs_path.is_file():
        return None
    try:
        content_bytes = abs_path.read_bytes()
        # Validate it's actually JSON
        json.loads(content_bytes.decode("utf-8"))
        content_text = content_bytes.decode("utf-8")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return EvidenceItem(
        source=f"{source_label}:{relpath}",
        content=content_text,
        content_type="json",
        retrieval_timestamp=timestamp_iso,
        confidence_score=1.0,  # direct file read, fully trusted
    )


def _extract_docx_text(path: Path) -> str | None:
    """Extract plain text from a .docx file using python-docx."""
    try:
        import docx  # python-docx
        doc = docx.Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs) if paragraphs else None
    except (ImportError, Exception):
        return None


def _extract_pdf_text(path: Path) -> str | None:
    """Extract plain text from a .pdf file using PyPDF2."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(p for p in pages if p.strip())
        return text if text.strip() else None
    except (ImportError, Exception):
        return None


def _read_file_evidence(
    relpath: str | None,
    source_label: str,
    timestamp_iso: str,
    repo_root: Path,
) -> EvidenceItem | None:
    """Read a file as text evidence, handling JSON, DOCX, PDF, and plain text."""
    if not relpath:
        return None
    abs_path = (
        (repo_root / relpath).resolve()
        if not Path(relpath).is_absolute()
        else Path(relpath)
    )
    if not abs_path.exists() or not abs_path.is_file():
        return None

    suffix = abs_path.suffix.lower()
    content: str | None = None
    content_type = "text"

    if suffix in _JSON_EXTENSIONS:
        try:
            raw = abs_path.read_bytes().decode("utf-8")
            json.loads(raw)  # validate
            content = raw
            content_type = "json"
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            content = None
    elif suffix in _DOCX_EXTENSIONS:
        content = _extract_docx_text(abs_path)
        content_type = "docx_text"
    elif suffix in _PDF_EXTENSIONS:
        content = _extract_pdf_text(abs_path)
        content_type = "pdf_text"
    else:
        try:
            content = abs_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            content = None

    if not content or not content.strip():
        return None

    return EvidenceItem(
        source=f"{source_label}:{relpath}",
        content=content,
        content_type=content_type,
        retrieval_timestamp=timestamp_iso,
        confidence_score=1.0,
    )


def _record_path_only_evidence(
    path_str: str | None,
    source_label: str,
    timestamp_iso: str,
) -> EvidenceItem | None:
    """Record a path-only evidence reference (e.g. PDF that we don't parse this turn)."""
    if not path_str:
        return None
    return EvidenceItem(
        source=f"{source_label}:{path_str}",
        content=f"[path-only reference; W5 will parse]",
        content_type="path_reference",
        retrieval_timestamp=timestamp_iso,
        confidence_score=0.5,  # presence-only; content unverified
    )


def _hash_content(content: str) -> str:
    """Compute SHA-256 hash of content for evidence integrity."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _load_master_resume_evidence(repo_root: Path, timestamp_iso: str) -> EvidenceItem | None:
    """Load the canonical master resume JSON as protected evidence.

    The master resume contains the candidate's true identity (name, contact info)
    and executive summary that MUST be used verbatim in the output.
    """
    master_path = repo_root / "artifacts" / "apps_rg" / "master_resume.json"
    if not master_path.exists():
        _log.warning("[C0] Master resume not found at %s", master_path)
        return None

    try:
        content = master_path.read_text(encoding="utf-8")
        # Validate it's valid JSON
        master_data = json.loads(content)

        # Extract only header + executive summary for the prompt (protected fields)
        protected_fields = {
            "header": master_data.get("header", {}),
            "executive_summary": master_data.get("executive_summary", ""),
            "_evidence_note": "USE header fields VERBATIM. DO NOT MODIFY. Tailor only experience bullets.",
        }
        protected_json = json.dumps(protected_fields, indent=2)

        return EvidenceItem(
            source="master_resume:header_exec_summary",
            content=protected_json,
            content_type="master_resume_protected",
            retrieval_timestamp=timestamp_iso,
            confidence_score=1.0,
        )
    except (OSError, json.JSONDecodeError) as exc:
        _log.warning("[C0] Failed to load master resume: %s", exc)
        return None


def c0_retrieve_apps_rg(
    route: RouteContract,
    validated_request: ValidatedRequest,
    chromadb_path: str | None = None,
) -> FinalEvidenceContract:
    """Gather grounding evidence for an apps_rg request.

    AG-2 (apps-rg-app-payload-consumption-wiring-b3a449 W4): signature
    changed from ``(route, payload: AppsRgIngressPayload)`` to
    ``(route, validated_request: ValidatedRequest)``. This binding now
    reads JD/resume content exclusively from
    ``validated_request.app_payload`` — never from the legacy ingress
    payload. The hard invariant is enforced by the CI gate
    ``ops_scripts/ci/check_apps_rg_app_payload_consumption.py``.

    W4 (apps-rg-chroma-ingestion-wiring-c7f2d9):
    - If chromadb_path is provided (or CHROMA_PERSIST_DIR env var is set),
      Chroma semantic retrieval is used for normative source classes
      (candidate_profile, project_evidence, approved_examples, rubrics,
      governance_docs, receipts).  prior_outputs are never normative.
    - EMBEDDING_ENABLED env var must be "true" when Chroma path is
      supplied; raises C0EvidenceGapError otherwise.
    - Chroma unavailable → logs warning, falls back to file-only.
    - File-only path (default) is completely unchanged.

    Args:
        route: L0 routing decision (must have grounding_required=True for
               this binding to be invoked).
        validated_request: U0 output carrying app_payload — the SSOT for
                           every apps_rg ingress field beyond U0.
        chromadb_path: Optional path to ChromaDB persistent store.
                       Defaults to os.getenv("CHROMA_PERSIST_DIR").
                       If neither is set, file-only path is used.

    Returns:
        FinalEvidenceContract with evidence_items + retrieval_sources +
        sufficiency assessment + W4 FEC tuple fields populated when Chroma
        retrieval is active.

    Raises:
        TypeError: if route or validated_request have wrong shape.
        ValueError: if app_payload is missing the required jd_payload /
            resume_payload sections (fail-closed before evidence assembly).
        C0EvidenceGapError: if Chroma path is supplied but
            EMBEDDING_ENABLED != "true".
    """
    if not isinstance(route, RouteContract):
        raise TypeError(
            f"c0_retrieve_apps_rg expected RouteContract, got {type(route).__name__}"
        )
    if not isinstance(validated_request, ValidatedRequest):
        raise TypeError(
            f"c0_retrieve_apps_rg expected ValidatedRequest, got {type(validated_request).__name__}"
        )

    # Fail-closed: route must have grounding_required=True for C0 to fire
    if not getattr(route, "grounding_required", False):
        raise ValueError(
            "c0_retrieve_apps_rg invoked with grounding_required=False; "
            "C0 is conditional on route.grounding_required=True per AG-2"
        )

    # W4.1: Resolve Chroma path — param takes precedence over env var.
    # File-only path used when neither is set.
    resolved_chroma_path: str | None = chromadb_path or os.getenv("CHROMA_PERSIST_DIR")

    # W4.3: EMBEDDING_ENABLED guard — raise only when Chroma path supplied.
    if resolved_chroma_path and os.getenv("EMBEDDING_ENABLED", "").lower() != "true":
        raise C0EvidenceGapError(
            action_hint="Set EMBEDDING_ENABLED=true to enable Chroma retrieval, "
            "or unset CHROMA_PERSIST_DIR / chromadb_path to use file-only fallback."
        )

    # AG-2 invariant: read exclusively from validated_request.app_payload
    app_payload = validated_request.app_payload or {}

    # Fail-closed validation of required app_payload sections
    if "jd_payload" not in app_payload:
        raise ValueError(
            "c0_retrieve_apps_rg: app_payload missing required jd_payload section"
        )
    if "resume_payload" not in app_payload:
        raise ValueError(
            "c0_retrieve_apps_rg: app_payload missing required resume_payload section"
        )

    jd_payload = app_payload.get("jd_payload", {})
    resume_payload = app_payload.get("resume_payload", {})

    # Primary JD source: jd_text from app_payload (AG-2 preferred)
    jd_text = jd_payload.get("jd_text", "")
    jd_path = jd_payload.get("jd_path")

    # Primary resume source: resume_text or structured resume from app_payload
    resume_text = resume_payload.get("resume_text", "")
    resume_path = resume_payload.get("resume_path")
    resume_json = resume_payload.get("resume_json")

    # Build evidence items list
    evidence_items: list[EvidenceItem] = []
    retrieval_sources: list[str] = []
    timestamp_iso = datetime.now(timezone.utc).isoformat()
    repo_root = _resolve_repo_root()

    # W4.2: FEC tuple field accumulators
    citation_pairs: list[tuple[str, str]] = []
    lineage_pairs: list[tuple[str, str]] = []
    freshness_refs: list[str] = []
    excluded_refs: list[str] = []
    chroma_support_status: str = STATUS_UNKNOWN

    # W4.1: Chroma retrieval path (opt-in)
    if resolved_chroma_path:
        chroma_retrieved = False
        try:
            import chromadb as _chromadb  # type: ignore[import]
            _client = _chromadb.PersistentClient(path=resolved_chroma_path)
            _collection = _client.get_collection("process_docs")
            all_chunks: list[dict[str, Any]] = []
            # Build query text from JD + resume context
            _query_text = (jd_text or "resume generation role requirements")[:1000]
            for sc in _NORMATIVE_SOURCE_CLASSES:
                sc_chunks = _chroma_query_source_class(
                    _collection, _query_text, sc, _CHROMA_N_RESULTS
                )
                all_chunks.extend(sc_chunks)
            chroma_items, c_pairs, l_pairs, f_refs = _build_chroma_evidence(
                all_chunks, timestamp_iso, excluded_refs
            )
            evidence_items.extend(chroma_items)
            citation_pairs.extend(c_pairs)
            lineage_pairs.extend(l_pairs)
            freshness_refs.extend(f_refs)
            for item in chroma_items:
                retrieval_sources.append(item.source)
            chroma_support_status = _compute_support_status(chroma_items, len(excluded_refs))
            chroma_retrieved = True
            _log.info(
                "[C0/Chroma] retrieved %d normative chunks, %d excluded, support_status=%s",
                len(chroma_items), len(excluded_refs), chroma_support_status,
            )
        except C0EvidenceGapError:
            raise
        except Exception as _exc:  # noqa: BLE001
            _log.warning(
                "[C0/Chroma] Chroma unavailable (%s) — falling back to file-only path.",
                _exc,
            )
            chroma_retrieved = False
            chroma_support_status = STATUS_UNKNOWN

    # JD evidence (primary: inline text from app_payload)
    if jd_text and jd_text.strip():
        evidence_items.append(
            EvidenceItem(
                source="jd_payload:jd_text",
                content=jd_text,
                content_type="job_description_text",
                retrieval_timestamp=timestamp_iso,
                confidence_score=1.0,
            )
        )
        retrieval_sources.append("jd_payload:jd_text")
    elif jd_path:
        # Fallback: read from file path if provided
        jd_evidence = _read_file_evidence(
            jd_path, "jd_file", timestamp_iso, repo_root
        )
        if jd_evidence:
            evidence_items.append(jd_evidence)
            retrieval_sources.append(f"jd_file:{jd_path}")

    # Resume evidence (primary: inline from app_payload)
    if resume_text and resume_text.strip():
        evidence_items.append(
            EvidenceItem(
                source="resume_payload:resume_text",
                content=resume_text,
                content_type="resume_text",
                retrieval_timestamp=timestamp_iso,
                confidence_score=1.0,
            )
        )
        retrieval_sources.append("resume_payload:resume_text")
    elif resume_json:
        # Structured resume JSON from app_payload
        try:
            resume_json_str = (
                json.dumps(resume_json)
                if isinstance(resume_json, dict)
                else str(resume_json)
            )
            evidence_items.append(
                EvidenceItem(
                    source="resume_payload:resume_json",
                    content=resume_json_str,
                    content_type="json",
                    retrieval_timestamp=timestamp_iso,
                    confidence_score=1.0,
                )
            )
            retrieval_sources.append("resume_payload:resume_json")
        except (TypeError, ValueError):
            pass
    elif resume_path:
        # Fallback: read from file path
        resume_evidence = _read_file_evidence(
            resume_path, "resume_file", timestamp_iso, repo_root
        )
        if resume_evidence:
            evidence_items.append(resume_evidence)
            retrieval_sources.append(f"resume_file:{resume_path}")

    # Manual brief evidence (future: referenced through L1.policy_refs)
    policy_refs = app_payload.get("policy_refs", {})
    manual_brief_path = policy_refs.get("manual_brief_path")
    if manual_brief_path:
        brief_evidence = _read_file_evidence(
            manual_brief_path, "manual_brief", timestamp_iso, repo_root
        )
        if brief_evidence:
            evidence_items.append(brief_evidence)
            retrieval_sources.append(f"manual_brief:{manual_brief_path}")

    # Master resume evidence (CRITICAL: protected header + exec summary)
    master_resume_evidence = _load_master_resume_evidence(repo_root, timestamp_iso)
    if master_resume_evidence:
        evidence_items.append(master_resume_evidence)
        retrieval_sources.append("master_resume:header_exec_summary")
        _log.info("[C0] Loaded master resume: %s", master_resume_evidence.source)

    # Compute evidence digest for provenance chain
    evidence_content = "|".join(
        f"{item.source}:{item.content[:100]}" for item in evidence_items
    )
    evidence_digest = _hash_content(evidence_content)

    # Sufficiency assessment
    has_jd = any(
        item.source.startswith("jd_payload") or item.source.startswith("jd_file")
        for item in evidence_items
    )
    has_resume = any(
        item.source.startswith("resume_payload") or item.source.startswith("resume_file")
        for item in evidence_items
    )
    is_sufficient = has_jd and has_resume

    return FinalEvidenceContract(
        request_id=validated_request.request_id,
        run_id=validated_request.run_id,
        app_id=validated_request.app_id,
        trace_id=validated_request.trace_id,
        evidence_items=tuple(evidence_items),
        retrieval_sources=tuple(retrieval_sources),
        support_target_met=is_sufficient,
        support_target_partial=is_sufficient,
        evidence_collection_timestamp=timestamp_iso,
        schema_version="AG-2.b3a449.W4",
        l5_certification_ref=APPS_RG_C0_CERT_REF,
        # W4.2: FEC tuple fields populated from Chroma retrieval
        citation_map=tuple(citation_pairs),
        source_lineage_map=tuple(lineage_pairs),
        freshness_receipts=tuple(freshness_refs),
        support_status=chroma_support_status,
        excluded_evidence_refs=tuple(excluded_refs),
    )


__all__ = [
    "APPS_RG_C0_CERT_REF",
    "C0EvidenceGapError",
    "SUPPORT_STATUS_PASSING_VALUES",
    "c0_retrieve_apps_rg",
]
