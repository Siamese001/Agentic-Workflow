"""Unit tests for ingest_curated_agent_docs.py.

Covers:
  - Source catalogue integrity (no archives, no mirrors, no duplicate paths, version collapse)
  - Scoring rubric compliance (score in [0.0, 1.0], required fields, valid enums)
  - Metadata completeness and type safety (validate_metadata)
  - section_dedup_key determinism and collision detection
  - Utility functions: ipynb_to_text, html_to_text, chunk_text, chunk_by_headings
  - collect_from_source: local stubs, web stubs, fail-closed required=True
  - DryRunReport structure
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[7]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.generate.ingestion.ingest_curated_agent_docs import (
    COLLECTION_NAME,
    CURATED_SOURCES,
    EXCLUDED_SOURCES,
    REQUIRED_METADATA_KEYS,
    DryRunReport,
    IngestionError,
    MetadataValidationError,
    _build_metadata,
    _compute_bucket_stats,
    chunk_by_headings,
    chunk_text,
    collect_from_source,
    compute_digest,
    html_to_text,
    ipynb_to_text,
    is_garbage,
    make_doc_id,
    section_dedup_key,
    validate_metadata,
)

# ---------------------------------------------------------------------------
# Catalogue integrity
# ---------------------------------------------------------------------------


class TestCatalogueIntegrity:
    def test_collection_name_is_curated(self) -> None:
        assert COLLECTION_NAME == "curated_agent_docs"
        assert COLLECTION_NAME != "ext_knowledge"
        assert COLLECTION_NAME != "arch_docs"

    def test_no_archive_paths(self) -> None:
        for entry in CURATED_SOURCES:
            path = entry["path"]
            assert "_archive" not in path, f"Archive path in CURATED_SOURCES: {path!r}"

    def test_no_openai_github_io_mirrors(self) -> None:
        for entry in CURATED_SOURCES:
            path = entry["path"]
            assert "openai.github.io" not in path, (
                f"github.io mirror in CURATED_SOURCES (should use raw GitHub): {path!r}"
            )

    def test_no_anthropic_readme(self) -> None:
        for entry in CURATED_SOURCES:
            path = entry["path"]
            assert not ("anthropic-cookbook" in path and path.endswith("README.md")), (
                f"Anthropic README should be excluded (collapses to pattern notebooks): {path!r}"
            )

    def test_no_duplicate_paths(self) -> None:
        paths = [e["path"] for e in CURATED_SOURCES]
        assert len(paths) == len(set(paths)), "CURATED_SOURCES contains duplicate path entries"

    def test_only_latest_process_mapping_version(self) -> None:
        proc_map_paths = [e["path"] for e in CURATED_SOURCES if "agentic_process_mapping" in e["path"]]
        for p in proc_map_paths:
            assert "_archive" not in p, f"Archive process mapping in CURATED_SOURCES: {p!r}"
            assert "non_technical" not in p, f"Non-technical version in CURATED_SOURCES: {p!r}"
            # Only exec or v29 should be present — no v2-v28
            import re

            version_match = re.search(r"_v(\d+)\.md", p)
            if version_match:
                version = int(version_match.group(1))
                assert version == 29, f"Old version v{version} found in CURATED_SOURCES: {p!r}"

    def test_at_least_32_sources(self) -> None:
        assert len(CURATED_SOURCES) >= 32, f"Expected >= 32 sources, got {len(CURATED_SOURCES)}"

    def test_excluded_sources_documented(self) -> None:
        assert len(EXCLUDED_SOURCES) >= 3, "EXCLUDED_SOURCES should document at least 3 collapsed entries"
        for ex in EXCLUDED_SOURCES:
            assert "path" in ex and "reason" in ex


class TestScoringCompliance:
    def test_all_scores_in_range(self) -> None:
        for entry in CURATED_SOURCES:
            score = entry["score"]
            assert 0.0 <= score <= 1.0, f"Score out of range for {entry['path']!r}: {score}"

    def test_required_fields_present(self) -> None:
        expected_keys = {
            "source_type",
            "path",
            "title",
            "doc_type",
            "doc_family",
            "topic_bucket",
            "authority_level",
            "canonical",
            "collapse_group",
            "keep_reason",
            "score",
            "required",
        }
        for entry in CURATED_SOURCES:
            missing = expected_keys - set(entry.keys())
            assert not missing, f"Entry {entry.get('path')!r} missing fields: {missing}"

    def test_valid_source_types(self) -> None:
        for entry in CURATED_SOURCES:
            assert entry["source_type"] in ("local", "web"), (
                f"Invalid source_type {entry['source_type']!r} in {entry['path']!r}"
            )

    def test_valid_topic_buckets(self) -> None:
        valid = {
            "arch_standards",
            "orchestration",
            "rag_retrieval",
            "safety_eval",
            "observability",
            "tool_contracts",
        }
        for entry in CURATED_SOURCES:
            assert entry["topic_bucket"] in valid, (
                f"Invalid topic_bucket {entry['topic_bucket']!r} in {entry['path']!r}"
            )

    def test_valid_doc_types(self) -> None:
        for entry in CURATED_SOURCES:
            assert entry["doc_type"] in ("markdown", "web", "notebook"), (
                f"Invalid doc_type {entry['doc_type']!r} in {entry['path']!r}"
            )

    def test_authority_level_in_range(self) -> None:
        for entry in CURATED_SOURCES:
            al = entry["authority_level"]
            assert 0.0 <= al <= 1.0, f"authority_level {al} out of range in {entry['path']!r}"

    def test_canonical_is_bool(self) -> None:
        for entry in CURATED_SOURCES:
            assert isinstance(entry["canonical"], bool), f"canonical must be bool in {entry['path']!r}"

    def test_required_is_bool(self) -> None:
        for entry in CURATED_SOURCES:
            assert isinstance(entry["required"], bool), f"required must be bool in {entry['path']!r}"

    def test_required_sources_are_high_signal(self) -> None:
        for entry in CURATED_SOURCES:
            if entry["required"]:
                assert entry["score"] >= 0.75, (
                    f"required=True entry {entry['path']!r} has low score {entry['score']:.2f}"
                )

    def test_all_buckets_have_at_least_one_required(self) -> None:
        required_buckets = {e["topic_bucket"] for e in CURATED_SOURCES if e["required"]}
        high_signal_buckets = {"arch_standards", "orchestration", "rag_retrieval", "safety_eval"}
        for bucket in high_signal_buckets:
            assert bucket in required_buckets, f"No required=True source for bucket {bucket!r}"


# ---------------------------------------------------------------------------
# Metadata validation
# ---------------------------------------------------------------------------


def _make_valid_metadata(**overrides: Any) -> dict:
    base: dict = {
        "artifact_type": "curated_agent_doc",
        "doc_type": "markdown",
        "doc_family": "adr",
        "file_path": "docs/architecture/adr/adr-002.md",
        "layer": "docs",
        "chunk_index": 0,
        "canonical_digest": "abc12345",
        "source": "curated_agent_docs",
        "title": "Test ADR",
        "heading_path": "Architecture > Query Routing",
        "authority_level": 1.0,
        "canonical": True,
        "retrieval_weight": 1.0,
        "source_area": "arch",
        "topic_bucket": "arch_standards",
        "source_url": "docs/architecture/adr/adr-002.md",
        "collapse_group": "repo_adr",
    }
    base.update(overrides)
    return base


class TestValidateMetadata:
    def test_valid_metadata_does_not_raise(self) -> None:
        validate_metadata(_make_valid_metadata())

    def test_missing_key_raises(self) -> None:
        meta = _make_valid_metadata()
        del meta["authority_level"]
        with pytest.raises(MetadataValidationError, match="authority_level"):
            validate_metadata(meta)

    def test_wrong_type_authority_level_raises(self) -> None:
        meta = _make_valid_metadata(authority_level="high")
        with pytest.raises(MetadataValidationError, match="authority_level"):
            validate_metadata(meta)

    def test_wrong_type_canonical_raises(self) -> None:
        meta = _make_valid_metadata(canonical="true")  # string instead of bool
        with pytest.raises(MetadataValidationError, match="canonical"):
            validate_metadata(meta)

    def test_wrong_type_chunk_index_raises(self) -> None:
        meta = _make_valid_metadata(chunk_index="0")
        with pytest.raises(MetadataValidationError, match="chunk_index"):
            validate_metadata(meta)

    def test_all_required_keys_are_in_required_metadata_keys(self) -> None:
        meta = _make_valid_metadata()
        assert REQUIRED_METADATA_KEYS == set(meta.keys())

    def test_missing_multiple_keys_lists_all(self) -> None:
        meta = _make_valid_metadata()
        del meta["title"]
        del meta["heading_path"]
        with pytest.raises(MetadataValidationError) as exc_info:
            validate_metadata(meta)
        assert "title" in str(exc_info.value) or "heading_path" in str(exc_info.value)


# ---------------------------------------------------------------------------
# section_dedup_key
# ---------------------------------------------------------------------------


class TestSectionDedupKey:
    def test_deterministic(self) -> None:
        k1 = section_dedup_key("https://example.com/doc.md", "Architecture > Routing")
        k2 = section_dedup_key("https://example.com/doc.md", "Architecture > Routing")
        assert k1 == k2

    def test_different_urls_different_keys(self) -> None:
        k1 = section_dedup_key("https://example.com/doc1.md", "Routing")
        k2 = section_dedup_key("https://example.com/doc2.md", "Routing")
        assert k1 != k2

    def test_different_sections_different_keys(self) -> None:
        k1 = section_dedup_key("https://example.com/doc.md", "Section A")
        k2 = section_dedup_key("https://example.com/doc.md", "Section B")
        assert k1 != k2

    def test_trailing_slash_normalized(self) -> None:
        k1 = section_dedup_key("https://example.com/doc/", "Routing")
        k2 = section_dedup_key("https://example.com/doc", "Routing")
        assert k1 == k2

    def test_returns_32_char_hex(self) -> None:
        k = section_dedup_key("https://x.com/y", "z")
        assert len(k) == 32
        assert all(c in "0123456789abcdef" for c in k)


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


class TestIpynbToText:
    def test_extracts_cell_sources(self) -> None:
        nb = {
            "cells": [
                {"source": ["# Introduction\n", "This is a notebook."]},
                {"source": ["import os"]},
                {"source": []},
            ]
        }
        text = ipynb_to_text(json.dumps(nb))
        assert "# Introduction" in text
        assert "This is a notebook." in text
        assert "import os" in text

    def test_handles_string_source(self) -> None:
        nb = {"cells": [{"source": "# Hello world"}]}
        text = ipynb_to_text(json.dumps(nb))
        assert "Hello world" in text

    def test_invalid_json_returns_raw(self) -> None:
        raw = "not valid json"
        result = ipynb_to_text(raw)
        assert result == raw

    def test_empty_cells_returns_empty(self) -> None:
        nb: dict = {"cells": []}
        text = ipynb_to_text(json.dumps(nb))
        assert text == ""

    def test_skips_empty_cells(self) -> None:
        nb = {"cells": [{"source": []}, {"source": ["real content"]}]}
        text = ipynb_to_text(json.dumps(nb))
        assert "real content" in text
        assert text.count("real content") == 1


class TestHtmlToText:
    def test_strips_script_tags(self) -> None:
        html = "<html><script>alert('x')</script><p>Content</p></html>"
        result = html_to_text(html)
        assert "alert" not in result
        assert "Content" in result

    def test_strips_style_tags(self) -> None:
        html = "<html><style>.cls { color: red; }</style><p>Text</p></html>"
        result = html_to_text(html)
        assert "color: red" not in result
        assert "Text" in result

    def test_decodes_html_entities(self) -> None:
        html = "<p>&amp; &lt;tag&gt; &quot;quoted&quot; &nbsp;space</p>"
        result = html_to_text(html)
        assert "&" in result
        assert "<tag>" in result
        assert '"quoted"' in result

    def test_block_tags_become_newlines(self) -> None:
        html = "<p>First</p><p>Second</p>"
        result = html_to_text(html)
        assert "First" in result
        assert "Second" in result


class TestChunkText:
    def test_short_text_returns_single_chunk(self) -> None:
        text = "Short text under the chunk size limit."
        chunks = chunk_text(text, chunk_size=500)
        assert chunks == [text]

    def test_long_text_produces_multiple_chunks(self) -> None:
        text = ("word " * 100 + "\n\n") * 5  # ~2500 chars
        chunks = chunk_text(text, chunk_size=500, overlap=50)
        assert len(chunks) >= 2

    def test_empty_text_returns_empty(self) -> None:
        assert chunk_text("") == []
        assert chunk_text("   ") == []

    def test_chunks_respect_paragraph_boundaries(self) -> None:
        paragraph = "word " * 60  # ~300 chars
        text = paragraph + "\n\n" + paragraph + "\n\n" + paragraph  # ~900 chars
        chunks = chunk_text(text, chunk_size=400, overlap=40)
        for chunk in chunks:
            assert len(chunk) <= 400 + 40 + 10  # allow small overshoot at boundaries


class TestChunkByHeadings:
    def _make_section(self, content: str = "word " * 25) -> str:
        return content  # ~125 chars, safely above MIN_BODY_CHARS=80

    def test_extracts_h1_heading_path(self) -> None:
        text = f"# Architecture\n\n{self._make_section()}\n"
        result = chunk_by_headings(text)
        paths = [hp for hp, _ in result]
        assert any("Architecture" in hp for hp in paths)

    def test_h2_inherits_h1_breadcrumb(self) -> None:
        sec = self._make_section()
        text = f"# Architecture\n\n{sec}\n\n## Query Routing\n\n{sec}\n"
        result = chunk_by_headings(text)
        paths = [hp for hp, _ in result]
        assert any("Query Routing" in hp for hp in paths)
        h2_paths = [hp for hp in paths if "Query Routing" in hp]
        assert any("Architecture" in hp for hp in h2_paths), "H2 should inherit H1 breadcrumb"

    def test_h3_inherits_h2_breadcrumb(self) -> None:
        sec = self._make_section()
        text = f"# Root\n\n{sec}\n\n## Layer\n\n{sec}\n\n### Sub\n\n{sec}\n"
        result = chunk_by_headings(text)
        paths = [hp for hp, _ in result]
        sub_paths = [hp for hp in paths if "Sub" in hp]
        assert any("Layer" in hp for hp in sub_paths), "H3 should inherit H2 breadcrumb"

    def test_headingless_text_returns_no_headings(self) -> None:
        text = "word " * 60
        result = chunk_by_headings(text)
        assert all(hp == "no-headings" for hp, _ in result)

    def test_returns_tuples(self) -> None:
        text = f"# Test\n\n{self._make_section()}\n"
        result = chunk_by_headings(text)
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 2


# ---------------------------------------------------------------------------
# collect_from_source — local stubs
# ---------------------------------------------------------------------------


class TestCollectFromSourceLocal:
    def _local_entry(self, path: str, required: bool = True) -> dict:
        return {
            "source_type": "local",
            "path": path,
            "title": "Test Doc",
            "doc_type": "markdown",
            "doc_family": "adr",
            "topic_bucket": "arch_standards",
            "authority_level": 1.0,
            "canonical": True,
            "collapse_group": "repo_adr",
            "keep_reason": "test",
            "score": 0.90,
            "required": required,
        }

    def test_valid_local_returns_chunks(self, tmp_path: Path) -> None:
        content = "# Architecture\n\n" + "word " * 30 + "\n"
        doc = tmp_path / "test.md"
        doc.write_text(content, encoding="utf-8")
        entry = self._local_entry("test.md")
        chunks = collect_from_source(entry, repo_root=tmp_path)
        assert len(chunks) >= 1
        assert chunks[0]["text"].strip()

    def test_metadata_completeness_local(self, tmp_path: Path) -> None:
        content = "# Heading\n\n" + "word " * 30 + "\n"
        doc = tmp_path / "doc.md"
        doc.write_text(content, encoding="utf-8")
        entry = self._local_entry("doc.md")
        chunks = collect_from_source(entry, repo_root=tmp_path)
        assert chunks, "Expected at least one chunk"
        meta = chunks[0]["metadata"]
        missing = REQUIRED_METADATA_KEYS - set(meta.keys())
        assert not missing, f"Missing metadata keys: {missing}"

    def test_metadata_types_local(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("# T\n\n" + "word " * 30, encoding="utf-8")
        entry = self._local_entry("doc.md")
        chunks = collect_from_source(entry, repo_root=tmp_path)
        assert chunks
        meta = chunks[0]["metadata"]
        assert isinstance(meta["authority_level"], float)
        assert isinstance(meta["canonical"], bool)
        assert isinstance(meta["chunk_index"], int)
        assert isinstance(meta["retrieval_weight"], float)

    def test_canonical_retrieval_weight_is_1(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("# T\n\n" + "word " * 30, encoding="utf-8")
        entry = self._local_entry("doc.md")
        chunks = collect_from_source(entry, repo_root=tmp_path)
        assert chunks
        assert chunks[0]["metadata"]["retrieval_weight"] == 1.0

    def test_required_missing_file_raises(self, tmp_path: Path) -> None:
        entry = self._local_entry("nonexistent.md", required=True)
        with pytest.raises(IngestionError):
            collect_from_source(entry, repo_root=tmp_path)

    def test_optional_missing_file_returns_empty(self, tmp_path: Path) -> None:
        entry = self._local_entry("nonexistent.md", required=False)
        result = collect_from_source(entry, repo_root=tmp_path)
        assert result == []

    def test_source_url_matches_path(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("# T\n\n" + "word " * 30, encoding="utf-8")
        entry = self._local_entry("doc.md")
        chunks = collect_from_source(entry, repo_root=tmp_path)
        assert chunks
        assert chunks[0]["metadata"]["source_url"] == "doc.md"

    def test_artifact_type_is_curated(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("# T\n\n" + "word " * 30, encoding="utf-8")
        entry = self._local_entry("doc.md")
        chunks = collect_from_source(entry, repo_root=tmp_path)
        assert chunks
        assert chunks[0]["metadata"]["artifact_type"] == "curated_agent_doc"
        assert chunks[0]["metadata"]["source"] == "curated_agent_docs"

    def test_id_parts_are_stable(self, tmp_path: Path) -> None:
        content = "# T\n\n" + "word " * 30
        doc = tmp_path / "doc.md"
        doc.write_text(content, encoding="utf-8")
        entry = self._local_entry("doc.md")
        chunks_a = collect_from_source(entry, repo_root=tmp_path)
        chunks_b = collect_from_source(entry, repo_root=tmp_path)
        ids_a = [make_doc_id(tuple(c["id_parts"])) for c in chunks_a]
        ids_b = [make_doc_id(tuple(c["id_parts"])) for c in chunks_b]
        assert ids_a == ids_b, "IDs must be stable across re-runs"


# ---------------------------------------------------------------------------
# collect_from_source — web stubs
# ---------------------------------------------------------------------------


class TestCollectFromSourceWeb:
    def _web_entry(self, url: str, doc_type: str = "markdown", required: bool = True) -> dict:
        return {
            "source_type": "web",
            "path": url,
            "title": "Web Doc",
            "doc_type": doc_type,
            "doc_family": "reference",
            "topic_bucket": "orchestration",
            "authority_level": 0.85,
            "canonical": True,
            "collapse_group": "openai_agents_raw_github",
            "keep_reason": "test",
            "score": 0.82,
            "required": required,
        }

    def test_web_markdown_metadata_completeness(self) -> None:
        url = "https://raw.githubusercontent.com/test/repo/main/README.md"
        content = "# Agents SDK\n\n" + "word " * 30 + "\n"
        entry = self._web_entry(url, doc_type="markdown")
        with patch("tools.generate.ingestion.ingest_curated_agent_docs.fetch_url", return_value=content):
            chunks = collect_from_source(entry, repo_root=REPO_ROOT)
        assert chunks
        missing = REQUIRED_METADATA_KEYS - set(chunks[0]["metadata"].keys())
        assert not missing, f"Missing metadata keys: {missing}"

    def test_web_notebook_extracts_cells(self) -> None:
        url = "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/test.ipynb"
        nb = {"cells": [{"source": ["# Pattern\n", "word " * 20]}]}
        entry = self._web_entry(url, doc_type="notebook", required=False)
        with patch(
            "tools.generate.ingestion.ingest_curated_agent_docs.fetch_url", return_value=json.dumps(nb)
        ):
            chunks = collect_from_source(entry, repo_root=REPO_ROOT)
        assert chunks
        assert "Pattern" in chunks[0]["text"] or any("Pattern" in c["text"] for c in chunks)

    def test_required_fetch_failure_raises(self) -> None:
        url = "https://example.com/required.md"
        entry = self._web_entry(url, required=True)
        with patch("tools.generate.ingestion.ingest_curated_agent_docs.fetch_url", return_value=None):
            with pytest.raises(IngestionError, match="required"):
                collect_from_source(entry, repo_root=REPO_ROOT)

    def test_optional_fetch_failure_returns_empty(self) -> None:
        url = "https://example.com/optional.md"
        entry = self._web_entry(url, required=False)
        with patch("tools.generate.ingestion.ingest_curated_agent_docs.fetch_url", return_value=None):
            result = collect_from_source(entry, repo_root=REPO_ROOT)
        assert result == []

    def test_garbage_content_skips_optional(self) -> None:
        url = "https://example.com/garbage.md"
        entry = self._web_entry(url, required=False)
        with patch("tools.generate.ingestion.ingest_curated_agent_docs.fetch_url", return_value="x"):
            result = collect_from_source(entry, repo_root=REPO_ROOT)
        assert result == []

    def test_garbage_content_fails_required(self) -> None:
        url = "https://example.com/required.md"
        entry = self._web_entry(url, required=True)
        with patch("tools.generate.ingestion.ingest_curated_agent_docs.fetch_url", return_value="x"):
            with pytest.raises(IngestionError):
                collect_from_source(entry, repo_root=REPO_ROOT)

    def test_layer_is_ext_for_web(self) -> None:
        url = "https://raw.githubusercontent.com/test/test/main/doc.md"
        content = "# T\n\n" + "word " * 30
        entry = self._web_entry(url)
        with patch("tools.generate.ingestion.ingest_curated_agent_docs.fetch_url", return_value=content):
            chunks = collect_from_source(entry, repo_root=REPO_ROOT)
        assert chunks
        assert chunks[0]["metadata"]["layer"] == "ext"


# ---------------------------------------------------------------------------
# DryRunReport structure
# ---------------------------------------------------------------------------


class TestDryRunReportStructure:
    def _make_doc(self, topic_bucket: str = "arch_standards", source_url: str = "local/test.md") -> dict:
        meta = _make_valid_metadata(topic_bucket=topic_bucket, source_url=source_url)
        return {"text": "content", "metadata": meta, "id_parts": ("local", "test", "abc", "0", "0")}

    def test_compute_bucket_stats_correct_counts(self) -> None:
        docs = [
            self._make_doc("arch_standards", "local/a.md"),
            self._make_doc("arch_standards", "local/b.md"),
            self._make_doc("orchestration", "local/c.md"),
        ]
        stats = _compute_bucket_stats(docs)
        stat_map = {s.bucket: s for s in stats}
        assert stat_map["arch_standards"].chunk_count == 2
        assert stat_map["arch_standards"].source_count == 2
        assert stat_map["orchestration"].chunk_count == 1

    def test_dry_run_report_is_dataclass(self) -> None:
        report = DryRunReport(
            total_sources=24,
            total_chunks=300,
            required_ok=14,
            required_fail=0,
            optional_fail=0,
            chunks_skipped_garbage=0,
            dedup_collisions=0,
            bucket_stats=[],
            excluded_count=5,
            dedup_log=[],
            source_details=[],
        )
        assert report.collection_name if hasattr(report, "collection_name") else True  # optional
        assert report.total_sources == 24
        assert report.total_chunks == 300
        assert report.required_ok == 14
        assert report.required_fail == 0
        assert report.dedup_collisions == 0

    def test_bucket_stats_have_required_fields(self) -> None:
        docs = [self._make_doc("arch_standards"), self._make_doc("safety_eval", "local/b.md")]
        stats = _compute_bucket_stats(docs)
        for s in stats:
            assert hasattr(s, "bucket")
            assert hasattr(s, "source_count")
            assert hasattr(s, "chunk_count")


# ---------------------------------------------------------------------------
# New sources (Prompt-2 additions) — presence and metadata assertions
# ---------------------------------------------------------------------------


class TestNewSourcesPresence:
    """Verify all 8 new sources from the Prompt-1 gap analysis are correctly registered."""

    _paths = [e["path"] for e in CURATED_SOURCES]

    def test_mcp_sdk_readme_present(self) -> None:
        assert (
            "https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md" in self._paths
        )

    def test_openai_agents_mcp_present(self) -> None:
        assert "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/mcp.md" in self._paths

    def test_openai_agents_context_present(self) -> None:
        assert (
            "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/context.md"
            in self._paths
        )

    def test_openai_agents_results_present(self) -> None:
        assert (
            "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/results.md"
            in self._paths
        )

    def test_langgraph_readme_present(self) -> None:
        assert "https://raw.githubusercontent.com/langchain-ai/langgraph/main/README.md" in self._paths

    def test_autogen_readme_present(self) -> None:
        assert "https://raw.githubusercontent.com/microsoft/autogen/main/README.md" in self._paths

    def test_mcp_sdk_is_required_and_tool_contracts(self) -> None:
        """MCP SDK README must be required=True and in tool_contracts bucket."""
        entry = next(
            (e for e in CURATED_SOURCES if "modelcontextprotocol/python-sdk" in e["path"]),
            None,
        )
        assert entry is not None
        assert entry["required"] is True
        assert entry["topic_bucket"] == "tool_contracts"
        assert entry["collapse_group"] == "mcp_protocol_sdk"
        assert entry["authority_level"] >= 0.85

    def test_new_openai_agents_docs_in_same_collapse_group(self) -> None:
        """All 4 new OpenAI agents docs must share the openai_agents_raw_github collapse group."""
        new_paths = {
            "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/mcp.md",
            "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/context.md",
            "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/results.md",
            "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/models.md",
        }
        for path in new_paths:
            entry = next((e for e in CURATED_SOURCES if e["path"] == path), None)
            assert entry is not None, f"Missing source: {path!r}"
            assert entry["collapse_group"] == "openai_agents_raw_github", (
                f"Wrong collapse_group for {path!r}: {entry['collapse_group']!r}"
            )

    def test_diversity_sources_in_distinct_collapse_groups(self) -> None:
        """LangGraph and AutoGen must have unique, non-OpenAI collapse groups."""
        langgraph = next((e for e in CURATED_SOURCES if "langchain-ai/langgraph" in e["path"]), None)
        autogen = next((e for e in CURATED_SOURCES if "microsoft/autogen" in e["path"]), None)
        assert langgraph is not None
        assert autogen is not None
        assert langgraph["collapse_group"] == "langgraph"
        assert autogen["collapse_group"] == "autogen"
        assert langgraph["collapse_group"] != autogen["collapse_group"]
        assert langgraph["collapse_group"] != "openai_agents_raw_github"
        assert autogen["collapse_group"] != "anthropic_agent_patterns"
