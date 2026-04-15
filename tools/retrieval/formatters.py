"""Formatting layer for converting service reports into MCP-friendly strings."""

from __future__ import annotations

import json

from .vector_schemas import (
    CollectionInfoReport,
    CollectionSummary,
    EmbedTextReport,
    QueryCollectionReport,
    ReadinessReport,
    SemanticSearchReport,
    VectorStatsReport,
)


def format_collection_listing(collections: list[CollectionSummary]) -> str:
    lines = [f"Vector Collections ({len(collections)} total):", ""]
    for collection in collections:
        lines.append(f"📁 {collection.name}")
        lines.append(f"   ID: {collection.id}")
        if collection.metadata:
            lines.append(f"   Metadata: {json.dumps(collection.metadata, indent=6)}")
        lines.append("   Count: use get_collection_info or vector_stats")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def format_query_collection(report: QueryCollectionReport) -> str:
    result = [
        f"Query Results for '{report.collection_name}'",
        f'Query: "{report.query_text}"',
        f"Embedding time: {report.embedding_time_s:.3f}s",
        f"Query time: {report.query_time_s:.3f}s",
        f"Results: {report.requested_results}",
        "",
    ]
    for idx, hit in enumerate(report.hits, start=1):
        result.append(f"Result {idx}:")
        result.append(f"  Document: {hit.document[:200]}{'...' if len(hit.document) > 200 else ''}")
        if hit.distance is not None:
            result.append(f"  Distance: {hit.distance:.4f}")
        if hit.metadata:
            result.append(f"  Metadata: {json.dumps(hit.metadata, indent=4)}")
        result.append("")
    return "\n".join(result).rstrip() + "\n"


def format_collection_info(report: CollectionInfoReport) -> str:
    lines = [
        f"Collection Info: '{report.name}'",
        f"ID: {report.id}",
        f"Document count: {report.document_count if report.document_count is not None else 'Unknown'}",
        f"sample_error: {report.sample_error if report.sample_error is not None else 'None'}",
    ]
    if report.metadata:
        lines.append("Metadata:")
        lines.append(json.dumps(report.metadata, indent=2))
    if report.sample_documents:
        lines.append("")
        lines.append("Sample documents:")
        for idx, doc in enumerate(report.sample_documents, start=1):
            lines.append(f"{idx}. {doc[:100]}{'...' if len(doc) > 100 else ''}")
    return "\n".join(lines).rstrip() + "\n"


def format_embed_text(report: EmbedTextReport) -> str:
    lines = [
        "Embedding Results",
        f"Texts processed: {report.texts_processed}",
        f"Processing time: {report.processing_time_s:.2f}s",
        f"Embedding dimension: {report.embedding_dimension}",
        f"Texts per second: {report.texts_per_second:.1f}",
        f"return_vectors: {report.return_vectors}",
        "",
        "Sample embeddings (first 5 dimensions):",
    ]
    for idx, preview in enumerate(report.previews, start=1):
        lines.append(f"")
        lines.append(f'{idx}. "{preview.text[:50]}{"..." if len(preview.text) > 50 else ""}"')
        lines.append(f"   [{', '.join(f'{x:.4f}' for x in preview.preview)}, ...]")
    if report.return_vectors:
        lines.append("")
        lines.append("Full vectors:")
        for idx, preview in enumerate(report.previews, start=1):
            lines.append(f"{idx}. {json.dumps(preview.full_vector)}")
    return "\n".join(lines).rstrip() + "\n"


def format_semantic_search(report: SemanticSearchReport) -> str:
    lines = [
        "Semantic Search Results",
        f'Query: "{report.query}"',
        f"Collections searched: {len(report.collections)}",
        f"Total results: {len(report.hits)}",
        f"Total search time: {report.total_search_time_s:.3f}s",
    ]
    if report.collection_errors:
        lines.append(f"Collection errors: {len(report.collection_errors)}")
        for name, error in report.collection_errors.items():
            lines.append(f"  {name}: {error}")
    lines.append("")
    for rank, hit in enumerate(report.hits, start=1):
        dist = f"{hit.distance:.4f}" if hit.distance is not None else "null"
        lines.append(
            f"{rank}. [{hit.collection}] (dist: {dist}) "
            f"{hit.document[:100]}{'...' if len(hit.document) > 100 else ''}"
        )
    return "\n".join(lines).rstrip() + "\n"


def format_vector_stats(report: VectorStatsReport) -> str:
    lines = [
        "Vector Database Statistics",
        f"ChromaDB path: {report.chroma_path}",
        f"Total collections: {report.total_collections}",
        f"Embedding model: {report.embedding_model}",
        f"Model loaded: {report.model_loaded}",
        f"Embedding dimension: {report.embedding_dimension}",
        f"Encode timeout: {report.encode_timeout_s:.0f}s",
        f"Encode queue wait timeout: {report.encode_queue_wait_timeout_s:.0f}s",
        f"Per-collection query timeout: {report.query_timeout_s:.0f}s",
        f"Per-collection semantic search timeout: {report.search_per_collection_timeout_s:.0f}s",
        f"Startup prewarm enabled: {report.background_prewarm_enabled}",
        "",
        "Collection Details:",
    ]
    for collection in report.collections:
        count_text = str(collection.count) if collection.count is not None else "N/A"
        line = f"  📁 {collection.name}: {count_text} documents"
        if collection.metadata:
            line += f" ({json.dumps(collection.metadata)})"
        lines.append(line)
        if collection.count_error:
            lines.append(f"     Count error: {collection.count_error}")
    lines.append("")
    lines.append(f"Total documents across all collections: {report.total_documents}")
    lines.append(f"Disk bytes: {report.disk_bytes if report.disk_bytes is not None else 'Unknown'}")
    return "\n".join(lines).rstrip() + "\n"


def format_readiness(report: ReadinessReport) -> str:
    lines = [
        "Vector DB Readiness",
        f"Chroma ready: {report.chroma_ready}",
        f"Chroma loading: {report.chroma_loading}",
        f"Embedding model ready: {report.embedding_model_ready}",
        f"Embedding model loading: {report.embedding_model_loading}",
        f"Chroma timeout: {report.chroma_timeout_s:.0f}s",
        f"Model timeout: {report.model_timeout_s:.0f}s",
        f"Encode timeout: {report.encode_timeout_s:.0f}s",
        f"Query timeout: {report.query_timeout_s:.0f}s",
        f"Startup prewarm enabled: {report.background_prewarm_enabled}",
    ]
    if report.chroma_ready and report.embedding_model_ready:
        lines.append("Ready for full semantic operations")
    else:
        lines.append("Lazy-load still in progress or has not started")
    return "\n".join(lines).rstrip() + "\n"
