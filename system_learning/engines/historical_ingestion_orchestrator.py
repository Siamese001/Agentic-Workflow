"""Historical ingestion orchestrator for Plan A.

Materializes deterministic JSONL corpora and builds indexes via
LocalEmbeddingPopulationService.
"""

from __future__ import annotations

from pathlib import Path

from system_learning.config.embedding_storage_layout import EmbeddingStorageLayout
from system_learning.engines.embedding_corpus_extraction import (
    extract_dpo_pair_records,
    extract_healing_context_records,
    extract_telemetry_event_records,
    write_jsonl_records,
)
from system_learning.engines.local_embedding_population_service import (
    EmbeddingProvider,
    LocalEmbeddingPopulationService,
)
from system_learning.engines.local_faiss_store import LocalFAISSStore
from system_learning.types.index_build_metadata_types import IndexBuildMetadata


def ingest_and_build_indexes(
    *,
    base_path: Path,
    built_at_utc: int,
    healing_source: list[dict],
    telemetry_source: list[dict],
    dpo_source: list[dict],
    embedding_model_version: str,
    embedding_model_checksum: str,
    canonicalization_version: str,
) -> dict[str, IndexBuildMetadata]:
    """Ingest historical data and build embedding indexes.

    Args:
        base_path: Base path for all storage operations.
        built_at_utc: Build timestamp (injected, not wall clock).
        healing_source: List of healing context source dictionaries.
        telemetry_source: List of telemetry event source dictionaries.
        dpo_source: List of DPO pair source dictionaries.
        embedding_model_version: Version of embedding model.
        embedding_model_checksum: SHA-256 checksum of embedding model.
        canonicalization_version: Canonicalization format version.

    Returns:
        Mapping of index_id to IndexBuildMetadata for all built indexes.
    """
    # Setup storage layout
    layout = EmbeddingStorageLayout(base_path)

    # Setup FAISS store and population service
    store = LocalFAISSStore(base_path=base_path)

    # Note: embedder will be injected by caller (tests use FakeEmbedder)
    # For production, this would be EmbeddingSovereignAgent
    embedder = None  # Will be set below

    # Create population service with embedder placeholder
    service = LocalEmbeddingPopulationService(
        faiss_store=store,
        embedder=embedder,  # Will be replaced
        canonicalization_version=canonicalization_version,
        embedding_model_version=embedding_model_version,
        embedding_model_checksum=embedding_model_checksum,
        build_seed=42,
    )

    # Extract records for each namespace
    healing_records = extract_healing_context_records(healing_source)
    telemetry_records = extract_telemetry_event_records(telemetry_source)
    dpo_records = extract_dpo_pair_records(dpo_source)

    # Write JSONL files to raw_staging
    healing_jsonl = layout.raw_staging_dir / "healing_contexts.jsonl"
    telemetry_jsonl = layout.raw_staging_dir / "telemetry_events.jsonl"
    dpo_jsonl = layout.raw_staging_dir / "dpo_pairs.jsonl"

    layout.raw_staging_dir.mkdir(parents=True, exist_ok=True)

    write_jsonl_records(healing_jsonl, healing_records)
    write_jsonl_records(telemetry_jsonl, telemetry_records)
    write_jsonl_records(dpo_jsonl, dpo_records)

    # Build indexes - need to inject embedder for each call
    # This is a bit awkward but maintains the service interface
    results = {}

    # Helper to build index with injected embedder
    def build_with_embedder(
        embedder: EmbeddingProvider,
        index_id: str,
        source_file: Path,
        dimension: int,
    ) -> IndexBuildMetadata:
        # Create new service instance with injected embedder
        service_with_embedder = LocalEmbeddingPopulationService(
            faiss_store=store,
            embedder=embedder,
            canonicalization_version=canonicalization_version,
            embedding_model_version=embedding_model_version,
            embedding_model_checksum=embedding_model_checksum,
            build_seed=42,
        )
        return service_with_embedder.populate_from_jsonl(
            index_id=index_id,
            source_files=[source_file],
            dimension=dimension,
            built_at_utc=built_at_utc,
        )

    # Note: The embedder parameter is passed via closure capture
    # This allows tests to inject a FakeEmbedder while maintaining
    # the pure function signature

    # For now, we'll raise an error if embedder is None
    # In practice, this function should be called from a context
    # that can provide the embedder
    if service.embedder is None:
        raise RuntimeError(
            "embedder must be injected. "
            "This function should be called from a wrapper that provides the embedder."
        )

    # Build healing contexts index (dim=768)
    results["healing_contexts_v1"] = service.populate_from_jsonl(
        index_id="healing_contexts_v1",
        source_files=[healing_jsonl],
        dimension=768,
        built_at_utc=built_at_utc,
    )

    # Build telemetry events index (dim=384)
    results["telemetry_events_v1"] = service.populate_from_jsonl(
        index_id="telemetry_events_v1",
        source_files=[telemetry_jsonl],
        dimension=384,
        built_at_utc=built_at_utc,
    )

    # Build DPO pairs index (dim=768)
    results["dpo_pairs_v1"] = service.populate_from_jsonl(
        index_id="dpo_pairs_v1",
        source_files=[dpo_jsonl],
        dimension=768,
        built_at_utc=built_at_utc,
    )

    return results


def ingest_and_build_indexes_with_embedder(
    *,
    base_path: Path,
    built_at_utc: int,
    healing_source: list[dict],
    telemetry_source: list[dict],
    dpo_source: list[dict],
    embedding_model_version: str,
    embedding_model_checksum: str,
    canonicalization_version: str,
    embedder: EmbeddingProvider,
) -> dict[str, IndexBuildMetadata]:
    """Convenience wrapper that accepts embedder parameter.

    This function provides a cleaner interface for tests and production
    by accepting the embedder directly rather than requiring injection.
    """
    # Setup storage layout
    layout = EmbeddingStorageLayout(base_path)

    # Setup FAISS store and population service
    store = LocalFAISSStore(base_path=base_path)
    service = LocalEmbeddingPopulationService(
        faiss_store=store,
        embedder=embedder,
        canonicalization_version=canonicalization_version,
        embedding_model_version=embedding_model_version,
        embedding_model_checksum=embedding_model_checksum,
        build_seed=42,
    )

    # Extract records for each namespace
    healing_records = extract_healing_context_records(healing_source)
    telemetry_records = extract_telemetry_event_records(telemetry_source)
    dpo_records = extract_dpo_pair_records(dpo_source)

    # Write JSONL files to raw_staging
    healing_jsonl = layout.raw_staging_dir / "healing_contexts.jsonl"
    telemetry_jsonl = layout.raw_staging_dir / "telemetry_events.jsonl"
    dpo_jsonl = layout.raw_staging_dir / "dpo_pairs.jsonl"

    layout.raw_staging_dir.mkdir(parents=True, exist_ok=True)

    write_jsonl_records(healing_jsonl, healing_records)
    write_jsonl_records(telemetry_jsonl, telemetry_records)
    write_jsonl_records(dpo_jsonl, dpo_records)

    # Build indexes
    results = {}

    # Build healing contexts index (dim=768)
    results["healing_contexts_v1"] = service.populate_from_jsonl(
        index_id="healing_contexts_v1",
        source_files=[healing_jsonl],
        dimension=768,
        built_at_utc=built_at_utc,
    )

    # Build telemetry events index (dim=384)
    results["telemetry_events_v1"] = service.populate_from_jsonl(
        index_id="telemetry_events_v1",
        source_files=[telemetry_jsonl],
        dimension=384,
        built_at_utc=built_at_utc,
    )

    # Build DPO pairs index (dim=768)
    results["dpo_pairs_v1"] = service.populate_from_jsonl(
        index_id="dpo_pairs_v1",
        source_files=[dpo_jsonl],
        dimension=768,
        built_at_utc=built_at_utc,
    )

    return results


# For backward compatibility, expose the wrapper as the main function
ingest_and_build_indexes = ingest_and_build_indexes_with_embedder


__all__ = [
    "ingest_and_build_indexes",
    "ingest_and_build_indexes_with_embedder",
]
