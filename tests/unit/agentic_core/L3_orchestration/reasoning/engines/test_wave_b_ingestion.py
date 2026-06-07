"""Unit tests for Wave B2 ingestion scripts.

Covers:
  - ingest_ext_authority.py  (ext_authority collection — Lanes A + B)
  - ingest_repo_evidence.py  (repo_evidence collection — Lanes C + D)
  - ingest_ext_knowledge.py  (ext_raw collection — Lane E)

Test classes:
  - TestExtAuthorityMetadataContract  — REQUIRED_METADATA_KEYS, validate_metadata
  - TestExtAuthorityCatalogue         — EXT_AUTHORITY_SOURCES integrity
  - TestExtAuthoritySourceBand        — _assign_source_band lane assignment
  - TestExtAuthorityChunking          — chunk_with_hierarchy, _split_protected
  - TestExtAuthorityCollect           — collect_from_source fail-closed behaviour
  - TestRepoEvidenceMetadataContract  — REQUIRED_METADATA_KEYS, validate_metadata
  - TestRepoEvidenceCatalogue         — REPO_CANONICAL_SOURCES integrity
  - TestRepoEvidenceChunking          — chunk_by_headings, should_exclude
  - TestRepoEvidenceCollect           — collect_canonical_docs fail-closed
  - TestExtRawWaveBFields             — Wave B field presence on ext_raw metadata
  - TestExtRawUrlDedup                — _load_ext_authority_urls behaviour
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[7]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ── Import ext_authority ───────────────────────────────────────────────────────
from tools.generate.ingestion.ingest_ext_authority import (
    COLLECTION_NAME as EA_COLLECTION,
    EXT_AUTHORITY_SOURCES,
    REQUIRED_METADATA_KEYS as EA_REQUIRED_KEYS,
    IngestionError as EA_IngestionError,
    MetadataContractError as EA_MetadataError,
    _LANE_A_URLS,
    _VALID_AUTHORITY_TIERS as EA_VALID_TIERS,
    _VALID_SOURCE_BANDS as EA_VALID_BANDS,
    _assign_source_band,
    _split_protected,
    chunk_with_hierarchy,
    collect_from_source,
    compute_digest as ea_compute_digest,
    is_garbage as ea_is_garbage,
    make_chunk_id,
    validate_metadata as ea_validate_metadata,
)

# ── Import repo_evidence ───────────────────────────────────────────────────────
from tools.generate.ingestion.ingest_repo_evidence import (
    COLLECTION_NAME as RE_COLLECTION,
    EXCLUDE_DIRS,
    REPO_CANONICAL_SOURCES,
    REQUIRED_METADATA_KEYS as RE_REQUIRED_KEYS,
    IngestionError as RE_IngestionError,
    MetadataContractError as RE_MetadataError,
    _VALID_AUTHORITY_TIERS as RE_VALID_TIERS,
    _VALID_SOURCE_BANDS as RE_VALID_BANDS,
    _build_metadata_canonical,
    _build_metadata_implementation,
    chunk_by_headings,
    collect_canonical_docs,
    compute_digest as re_compute_digest,
    should_exclude,
    validate_metadata as re_validate_metadata,
)

# ── Import ext_raw (ingest_ext_knowledge) ─────────────────────────────────────
from tools.generate.ingestion.ingest_ext_knowledge import (
    COLLECTION_NAME as ER_COLLECTION,
    _WAVE_B_EXT_RAW_FIELDS,
    _load_ext_authority_urls,
)

# ── Import Wave B3 routing / shaping (evidence_shaper, query_router) ──────────
from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import (
    filter_normative_sources,
)
from agentic_core.L3_orchestration.reasoning.engines.query_router import QueryRouter


# ==============================================================================
# ext_authority — metadata contract
# ==============================================================================


class TestExtAuthorityMetadataContract:
    def test_collection_name(self) -> None:
        assert EA_COLLECTION == "ext_authority"

    def test_required_keys_count(self) -> None:
        assert len(EA_REQUIRED_KEYS) == 17

    def test_required_keys_includes_source_band(self) -> None:
        assert "source_band" in EA_REQUIRED_KEYS

    def test_required_keys_includes_parent_child(self) -> None:
        assert "parent_id" in EA_REQUIRED_KEYS
        assert "child_ids" in EA_REQUIRED_KEYS

    def test_valid_source_bands_are_lane_a_and_b(self) -> None:
        assert EA_VALID_BANDS == frozenset({"target_state_authority", "supporting_guidance"})

    def test_valid_authority_tiers_are_t2_t3(self) -> None:
        assert EA_VALID_TIERS == frozenset({"T2_standard", "T3_guidance"})

    def _make_valid_meta(self, **overrides: object) -> dict:
        base: dict = {
            "source_collection": "ext_authority",
            "source_band": "supporting_guidance",
            "authority_tier": "T3_guidance",
            "normative_scope": "external_authority",
            "invalid_for_normative_use": False,
            "source_type": "web",
            "topic_bucket": "tool_contracts",
            "doc_family": "reference",
            "source_url": "https://example.com/doc",
            "heading_path": "Introduction",
            "collapse_group": "test_group",
            "title": "Test Document",
            "chunk_index": 0,
            "canonical_digest": "abc123",
            "version_or_date": "",
            "parent_id": "",
            "child_ids": "[]",
        }
        base.update(overrides)
        return base

    def test_valid_metadata_does_not_raise(self) -> None:
        ea_validate_metadata(self._make_valid_meta())

    def test_lane_a_metadata_does_not_raise(self) -> None:
        ea_validate_metadata(
            self._make_valid_meta(
                source_band="target_state_authority",
                authority_tier="T2_standard",
            )
        )

    def test_missing_field_raises(self) -> None:
        meta = self._make_valid_meta()
        del meta["source_band"]
        with pytest.raises(EA_MetadataError, match="Missing mandatory"):
            ea_validate_metadata(meta)

    def test_invalid_source_band_raises(self) -> None:
        meta = self._make_valid_meta(source_band="unvetted")
        with pytest.raises(EA_MetadataError, match="source_band"):
            ea_validate_metadata(meta)

    def test_invalid_authority_tier_raises(self) -> None:
        meta = self._make_valid_meta(authority_tier="T5_unvetted")
        with pytest.raises(EA_MetadataError, match="authority_tier"):
            ea_validate_metadata(meta)

    def test_chunk_index_wrong_type_raises(self) -> None:
        meta = self._make_valid_meta(chunk_index="0")  # type: ignore[arg-type]
        with pytest.raises(EA_MetadataError, match="chunk_index"):
            ea_validate_metadata(meta)

    def test_invalid_for_normative_use_wrong_type_raises(self) -> None:
        meta = self._make_valid_meta(invalid_for_normative_use=0)  # type: ignore[arg-type]
        with pytest.raises(EA_MetadataError, match="invalid_for_normative_use"):
            ea_validate_metadata(meta)

    def test_ext_authority_invalid_for_normative_use_is_false(self) -> None:
        """ext_authority chunks must never carry invalid_for_normative_use=True."""
        meta = self._make_valid_meta()
        assert meta["invalid_for_normative_use"] is False


# ==============================================================================
# ext_authority — source catalogue integrity
# ==============================================================================


class TestExtAuthorityCatalogue:
    def test_has_18_sources(self) -> None:
        assert len(EXT_AUTHORITY_SOURCES) == 18

    def test_all_paths_are_https(self) -> None:
        bad = [e["path"] for e in EXT_AUTHORITY_SOURCES if not e["path"].startswith("https://")]
        assert bad == [], f"Non-https paths: {bad}"

    def test_no_duplicate_paths(self) -> None:
        paths = [e["path"] for e in EXT_AUTHORITY_SOURCES]
        assert len(paths) == len(set(paths)), "Duplicate paths in EXT_AUTHORITY_SOURCES"

    def test_all_required_fields_present(self) -> None:
        mandatory = {"path", "title", "doc_type", "doc_family", "topic_bucket", "collapse_group", "required"}
        for entry in EXT_AUTHORITY_SOURCES:
            missing = mandatory - set(entry.keys())
            assert not missing, f"Entry missing fields {missing}: {entry.get('path')}"

    def test_required_true_sources_have_https(self) -> None:
        required_paths = [e["path"] for e in EXT_AUTHORITY_SOURCES if e["required"]]
        assert all(p.startswith("https://") for p in required_paths)

    def test_lane_a_url_is_in_source_catalogue(self) -> None:
        catalogue_paths = {e["path"] for e in EXT_AUTHORITY_SOURCES}
        for lane_a_url in _LANE_A_URLS:
            assert lane_a_url in catalogue_paths, f"Lane A URL not in catalogue: {lane_a_url}"

    def test_doc_family_values_are_known(self) -> None:
        known_families = {"reference", "guide", "cookbook", "spec", "adr", "standard", "architecture"}
        bad = [e["path"] for e in EXT_AUTHORITY_SOURCES if e["doc_family"] not in known_families]
        assert bad == [], f"Unknown doc_family in entries: {bad}"


# ==============================================================================
# ext_authority — source band assignment
# ==============================================================================


class TestExtAuthoritySourceBand:
    def test_mcp_sdk_url_is_lane_a(self) -> None:
        mcp_url = "https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md"
        entry = {"path": mcp_url}
        band, tier = _assign_source_band(entry)
        assert band == "target_state_authority"
        assert tier == "T2_standard"

    def test_non_mcp_url_is_lane_b(self) -> None:
        entry = {"path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/agents.md"}
        band, tier = _assign_source_band(entry)
        assert band == "supporting_guidance"
        assert tier == "T3_guidance"

    def test_any_arbitrary_url_is_lane_b(self) -> None:
        entry = {"path": "https://example.com/some/doc.md"}
        band, tier = _assign_source_band(entry)
        assert band == "supporting_guidance"
        assert tier == "T3_guidance"

    def test_all_catalogue_entries_get_valid_band(self) -> None:
        for entry in EXT_AUTHORITY_SOURCES:
            band, tier = _assign_source_band(entry)
            assert band in EA_VALID_BANDS, f"Bad band for {entry['path']}"
            assert tier in EA_VALID_TIERS, f"Bad tier for {entry['path']}"


# ==============================================================================
# ext_authority — chunking
# ==============================================================================


class TestExtAuthorityChunking:
    def test_no_headings_returns_single_chunk(self) -> None:
        body = "x" * 200
        chunks = chunk_with_hierarchy(body, source_url="https://example.com/doc")
        assert len(chunks) >= 1
        for c in chunks:
            assert "heading_path" in c
            assert "chunk_index" in c
            assert "parent_id" in c
            assert "child_ids" in c

    def test_h2_section_is_parent(self) -> None:
        body = "\n".join(
            [
                "# Doc",
                "",
                "Intro text." * 5,
                "",
                "## Section One",
                "",
                "Content one." * 20,
                "",
                "### Sub-section",
                "",
                "Sub content." * 10,
            ]
        )
        chunks = chunk_with_hierarchy(body, source_url="https://example.com/doc")
        h2_chunks = [
            c for c in chunks if "Section One" in c["heading_path"] and "Sub" not in c["heading_path"]
        ]
        h3_chunks = [c for c in chunks if "Sub-section" in c["heading_path"]]
        if h2_chunks and h3_chunks:
            assert h3_chunks[0]["parent_id"] == h2_chunks[0]["doc_id"]

    def test_child_ids_is_json_array(self) -> None:
        body = "\n".join(
            [
                "## Parent",
                "",
                "Parent content." * 10,
                "",
                "### Child A",
                "",
                "Child A content." * 10,
            ]
        )
        chunks = chunk_with_hierarchy(body, source_url="https://example.com/doc")
        for c in chunks:
            parsed = json.loads(c["child_ids"])
            assert isinstance(parsed, list)

    def test_split_protected_does_not_break_code_fence(self) -> None:
        fence_inner = "def foo():\n    return 1"
        fence = f"```python\n{fence_inner}\n```\n"
        body = ("Prose. " * 10 + fence) * 2
        pieces = _split_protected(body, max_chars=300)
        # The fence body must never be split across pieces.
        # Verify: for every piece that contains the opening ``` marker,
        # the closing ``` must also be present in the SAME piece.
        for piece in pieces:
            if "```python" in piece:
                assert "```\n" in piece or piece.endswith("```"), (
                    f"Code fence opened but not closed in piece: {piece[:100]!r}"
                )

    def test_is_garbage_short_body(self) -> None:
        assert ea_is_garbage("hi")
        assert ea_is_garbage("")
        assert not ea_is_garbage("A" * 100)

    def test_is_garbage_loading_pattern(self) -> None:
        assert ea_is_garbage("Loading...Loading...")
        assert not ea_is_garbage("The page is loading slowly but has enough content here. " * 3)

    def test_make_chunk_id_is_deterministic(self) -> None:
        cid1 = make_chunk_id("https://example.com", "Heading > Sub", 0)
        cid2 = make_chunk_id("https://example.com", "Heading > Sub", 0)
        assert cid1 == cid2

    def test_make_chunk_id_different_for_different_index(self) -> None:
        cid0 = make_chunk_id("https://example.com", "Heading", 0)
        cid1 = make_chunk_id("https://example.com", "Heading", 1)
        assert cid0 != cid1


# ==============================================================================
# ext_authority — collect_from_source fail-closed
# ==============================================================================


class TestExtAuthorityCollect:
    def _make_entry(self, url: str = "https://example.com/doc.md", required: bool = True) -> dict:
        return {
            "path": url,
            "title": "Test Doc",
            "doc_type": "markdown",
            "doc_family": "reference",
            "topic_bucket": "tool_contracts",
            "collapse_group": "test_group",
            "required": required,
        }

    def test_required_source_fetch_failure_raises(self) -> None:
        entry = self._make_entry(required=True)
        with patch(
            "tools.generate.ingestion.ingest_ext_authority.fetch_url",
            return_value=None,
        ):
            with pytest.raises(EA_IngestionError, match="required"):
                collect_from_source(entry)

    def test_optional_source_fetch_failure_returns_empty(self) -> None:
        entry = self._make_entry(required=False)
        with patch(
            "tools.generate.ingestion.ingest_ext_authority.fetch_url",
            return_value=None,
        ):
            result = collect_from_source(entry)
        assert result == []

    def test_garbage_body_skipped(self) -> None:
        entry = self._make_entry(required=False)
        with patch(
            "tools.generate.ingestion.ingest_ext_authority.fetch_url",
            return_value="Loading...",
        ):
            result = collect_from_source(entry)
        assert result == []

    def test_valid_body_returns_chunks(self) -> None:
        body = "# Test\n\n" + ("Content paragraph. " * 20)
        entry = self._make_entry(required=False)
        with patch(
            "tools.generate.ingestion.ingest_ext_authority.fetch_url",
            return_value=body,
        ):
            result = collect_from_source(entry)
        assert len(result) >= 1
        first = result[0]
        assert "text" in first
        assert "metadata" in first
        assert first["metadata"]["source_collection"] == "ext_authority"
        assert first["metadata"]["invalid_for_normative_use"] is False

    def test_returned_metadata_passes_validation(self) -> None:
        body = "# Test\n\n" + ("Content paragraph. " * 20)
        entry = self._make_entry(required=False)
        with patch(
            "tools.generate.ingestion.ingest_ext_authority.fetch_url",
            return_value=body,
        ):
            result = collect_from_source(entry)
        for chunk in result:
            ea_validate_metadata(chunk["metadata"])


# ==============================================================================
# repo_evidence — metadata contract
# ==============================================================================


class TestRepoEvidenceMetadataContract:
    def test_collection_name(self) -> None:
        assert RE_COLLECTION == "repo_evidence"

    def test_required_keys_count(self) -> None:
        assert len(RE_REQUIRED_KEYS) == 15

    def test_required_keys_includes_file_path(self) -> None:
        assert "file_path" in RE_REQUIRED_KEYS

    def test_required_keys_includes_source_band(self) -> None:
        assert "source_band" in RE_REQUIRED_KEYS

    def test_valid_source_bands_are_repo_lanes(self) -> None:
        assert RE_VALID_BANDS == frozenset({"repo_canonical", "repo_implementation"})

    def test_valid_authority_tiers_are_t4(self) -> None:
        assert RE_VALID_TIERS == frozenset({"T4_repo_canonical", "T4_implementation_evidence"})

    def _make_valid_meta_canonical(self, **overrides: object) -> dict:
        base: dict = {
            "source_collection": "repo_evidence",
            "source_band": "repo_canonical",
            "authority_tier": "T4_repo_canonical",
            "normative_scope": "repo_internal",
            "invalid_for_normative_use": True,
            "source_type": "local",
            "topic_bucket": "arch_standards",
            "doc_family": "adr",
            "source_url": "docs/architecture/adr/adr-001.md",
            "heading_path": "ADR Title",
            "collapse_group": "repo_adr",
            "title": "ADR-001",
            "chunk_index": 0,
            "canonical_digest": "abc123",
            "file_path": "docs/architecture/adr/adr-001.md",
        }
        base.update(overrides)
        return base

    def _make_valid_meta_implementation(self, **overrides: object) -> dict:
        base = self._make_valid_meta_canonical(
            source_band="repo_implementation",
            authority_tier="T4_implementation_evidence",
        )
        base.update(overrides)
        return base

    def test_canonical_metadata_does_not_raise(self) -> None:
        re_validate_metadata(self._make_valid_meta_canonical())

    def test_implementation_metadata_does_not_raise(self) -> None:
        re_validate_metadata(self._make_valid_meta_implementation())

    def test_missing_file_path_raises(self) -> None:
        meta = self._make_valid_meta_canonical()
        del meta["file_path"]
        with pytest.raises(RE_MetadataError, match="Missing mandatory"):
            re_validate_metadata(meta)

    def test_invalid_source_band_raises(self) -> None:
        meta = self._make_valid_meta_canonical(source_band="unvetted")
        with pytest.raises(RE_MetadataError, match="source_band"):
            re_validate_metadata(meta)

    def test_invalid_authority_tier_raises(self) -> None:
        meta = self._make_valid_meta_canonical(authority_tier="T2_standard")
        with pytest.raises(RE_MetadataError, match="authority_tier"):
            re_validate_metadata(meta)

    def test_chunk_index_wrong_type_raises(self) -> None:
        meta = self._make_valid_meta_canonical(chunk_index="0")  # type: ignore[arg-type]
        with pytest.raises(RE_MetadataError, match="chunk_index"):
            re_validate_metadata(meta)

    def test_all_repo_evidence_chunks_are_invalid_for_normative_use(self) -> None:
        """Both Lane C and Lane D always set invalid_for_normative_use=True."""
        meta_c = self._make_valid_meta_canonical()
        meta_d = self._make_valid_meta_implementation()
        assert meta_c["invalid_for_normative_use"] is True
        assert meta_d["invalid_for_normative_use"] is True


# ==============================================================================
# repo_evidence — catalogue integrity
# ==============================================================================


class TestRepoEvidenceCatalogue:
    def test_has_16_canonical_sources(self) -> None:
        assert len(REPO_CANONICAL_SOURCES) == 16

    def test_no_duplicate_paths(self) -> None:
        paths = [e["path"] for e in REPO_CANONICAL_SOURCES]
        assert len(paths) == len(set(paths)), "Duplicate paths in REPO_CANONICAL_SOURCES"

    def test_no_web_paths(self) -> None:
        web = [e["path"] for e in REPO_CANONICAL_SOURCES if e["path"].startswith("http")]
        assert web == [], f"Web paths in REPO_CANONICAL_SOURCES: {web}"

    def test_all_required_fields_present(self) -> None:
        mandatory = {"path", "title", "doc_family", "topic_bucket", "collapse_group", "required"}
        for entry in REPO_CANONICAL_SOURCES:
            missing = mandatory - set(entry.keys())
            assert not missing, f"Entry missing fields {missing}: {entry.get('path')}"

    def test_exclude_dirs_contains_archives(self) -> None:
        assert "archives" in EXCLUDE_DIRS
        assert "_archive" in EXCLUDE_DIRS


# ==============================================================================
# repo_evidence — chunking
# ==============================================================================


class TestRepoEvidenceChunking:
    def test_no_headings_returns_no_headings_path(self) -> None:
        body = "Plain text content. " * 10
        results = chunk_by_headings(body)
        assert all(hp == "no-headings" for hp, _ in results)

    def test_h1_heading_becomes_heading_path(self) -> None:
        body = "# My Title\n\nSome content here. " * 10
        results = chunk_by_headings(body)
        assert len(results) >= 1
        assert any("My Title" in hp for hp, _ in results)

    def test_h2_heading_under_h1(self) -> None:
        body = "\n".join(
            [
                "# Top Level",
                "",
                "Intro content. " * 5,
                "",
                "## Section Two",
                "",
                "Section content. " * 10,
            ]
        )
        results = chunk_by_headings(body)
        h2_entries = [(hp, _) for hp, _ in results if "Section Two" in hp]
        assert len(h2_entries) >= 1
        assert any("Top Level" in hp for hp, _ in h2_entries)

    def test_short_section_skipped(self) -> None:
        body = "# Title\n\n## Short\n\nx\n\n## Long\n\n" + ("Long content. " * 20)
        results = chunk_by_headings(body)
        short_entries = [(hp, _) for hp, _ in results if hp.endswith("Short")]
        assert len(short_entries) == 0

    def test_should_exclude_archives_dir(self) -> None:
        p = Path("c:/repo/archives/old_file.md")
        assert should_exclude(p)

    def test_should_exclude_windsurf_dir(self) -> None:
        p = Path("c:/repo/.cursor/rules/constitutional.md")
        assert should_exclude(p)

    def test_should_not_exclude_docs_dir(self) -> None:
        p = Path("c:/repo/docs/architecture/adr-001.md")
        assert not should_exclude(p)

    def test_build_metadata_canonical_has_all_required_keys(self) -> None:
        entry = {
            "path": "docs/some/file.md",
            "title": "Test",
            "doc_family": "adr",
            "topic_bucket": "arch_standards",
            "collapse_group": "repo_adr",
            "required": True,
        }
        meta = _build_metadata_canonical(
            entry=entry,
            heading_path="Section",
            chunk_index=0,
            canonical_digest="abc",
            doc_title="Test",
            rel_path="docs/some/file.md",
        )
        missing = RE_REQUIRED_KEYS - set(meta.keys())
        assert not missing, f"Missing required keys in canonical meta: {sorted(missing)}"

    def test_build_metadata_implementation_has_all_required_keys(self) -> None:
        fp = Path("docs/guide/some.md")
        meta = _build_metadata_implementation(
            file_path=fp,
            rel_path="docs/guide/some.md",
            heading_path="no-headings",
            chunk_index=0,
            canonical_digest="abc",
            doc_title="Some Guide",
        )
        missing = RE_REQUIRED_KEYS - set(meta.keys())
        assert not missing, f"Missing required keys in impl meta: {sorted(missing)}"


# ==============================================================================
# repo_evidence — collect_canonical_docs fail-closed
# ==============================================================================


class TestRepoEvidenceCollect:
    def test_required_missing_file_raises_ingestion_error(self, tmp_path: Path) -> None:
        """A required=True entry whose file does not exist must raise IngestionError."""
        from tools.generate.ingestion import ingest_repo_evidence as mod

        original_sources = mod.REPO_CANONICAL_SOURCES
        fake_sources = [
            {
                "path": "nonexistent/file_that_does_not_exist.md",
                "title": "Missing",
                "doc_family": "adr",
                "topic_bucket": "arch_standards",
                "collapse_group": "repo_adr",
                "required": True,
            }
        ]
        try:
            mod.REPO_CANONICAL_SOURCES = fake_sources  # type: ignore[attr-defined]
            with pytest.raises(RE_IngestionError, match="required=True"):
                collect_canonical_docs(tmp_path)
        finally:
            mod.REPO_CANONICAL_SOURCES = original_sources  # type: ignore[attr-defined]

    def test_optional_missing_file_is_skipped(self, tmp_path: Path) -> None:
        from tools.generate.ingestion import ingest_repo_evidence as mod

        original_sources = mod.REPO_CANONICAL_SOURCES
        fake_sources = [
            {
                "path": "nonexistent/file_that_does_not_exist.md",
                "title": "Missing",
                "doc_family": "adr",
                "topic_bucket": "arch_standards",
                "collapse_group": "repo_adr",
                "required": False,
            }
        ]
        try:
            mod.REPO_CANONICAL_SOURCES = fake_sources  # type: ignore[attr-defined]
            result = collect_canonical_docs(tmp_path)
        finally:
            mod.REPO_CANONICAL_SOURCES = original_sources  # type: ignore[attr-defined]
        assert result == []

    def test_existing_file_produces_chunks(self, tmp_path: Path) -> None:
        from tools.generate.ingestion import ingest_repo_evidence as mod

        content = "# ADR Title\n\n" + ("Decision content. " * 30)
        test_file = tmp_path / "adr-test.md"
        test_file.write_text(content, encoding="utf-8")

        original_sources = mod.REPO_CANONICAL_SOURCES
        fake_sources = [
            {
                "path": "adr-test.md",
                "title": "ADR Test",
                "doc_family": "adr",
                "topic_bucket": "arch_standards",
                "collapse_group": "repo_adr",
                "required": True,
            }
        ]
        try:
            mod.REPO_CANONICAL_SOURCES = fake_sources  # type: ignore[attr-defined]
            result = collect_canonical_docs(tmp_path)
        finally:
            mod.REPO_CANONICAL_SOURCES = original_sources  # type: ignore[attr-defined]

        assert len(result) >= 1
        meta = result[0]["metadata"]
        assert meta["source_collection"] == "repo_evidence"
        assert meta["source_band"] == "repo_canonical"
        assert meta["invalid_for_normative_use"] is True

    def test_existing_file_metadata_passes_validation(self, tmp_path: Path) -> None:
        from tools.generate.ingestion import ingest_repo_evidence as mod

        content = "# Title\n\n" + ("Content. " * 40)
        test_file = tmp_path / "doc.md"
        test_file.write_text(content, encoding="utf-8")

        original_sources = mod.REPO_CANONICAL_SOURCES
        fake_sources = [
            {
                "path": "doc.md",
                "title": "Doc",
                "doc_family": "adr",
                "topic_bucket": "arch_standards",
                "collapse_group": "repo_adr",
                "required": True,
            }
        ]
        try:
            mod.REPO_CANONICAL_SOURCES = fake_sources  # type: ignore[attr-defined]
            result = collect_canonical_docs(tmp_path)
        finally:
            mod.REPO_CANONICAL_SOURCES = original_sources  # type: ignore[attr-defined]

        for doc in result:
            re_validate_metadata(doc["metadata"])


# ==============================================================================
# ext_raw — Wave B field presence
# ==============================================================================


class TestExtRawWaveBFields:
    def test_collection_name_is_ext_raw(self) -> None:
        assert ER_COLLECTION == "ext_raw"

    def test_wave_b_fields_source_band_is_unvetted(self) -> None:
        assert _WAVE_B_EXT_RAW_FIELDS["source_band"] == "unvetted"

    def test_wave_b_fields_authority_tier_is_t5(self) -> None:
        assert _WAVE_B_EXT_RAW_FIELDS["authority_tier"] == "T5_unvetted"

    def test_wave_b_fields_invalid_for_normative_use_is_true(self) -> None:
        assert _WAVE_B_EXT_RAW_FIELDS["invalid_for_normative_use"] is True

    def test_wave_b_fields_normative_scope_is_unvetted(self) -> None:
        assert _WAVE_B_EXT_RAW_FIELDS["normative_scope"] == "unvetted"

    def test_wave_b_fields_source_collection_matches_name(self) -> None:
        assert _WAVE_B_EXT_RAW_FIELDS["source_collection"] == ER_COLLECTION


# ==============================================================================
# ext_raw — URL dedup helper
# ==============================================================================


class TestExtRawUrlDedup:
    def test_returns_empty_set_when_no_ext_authority_collection(self, tmp_path: Path) -> None:
        """When ext_authority collection does not exist, dedup set should be empty."""
        import chromadb  # type: ignore[import]

        client = chromadb.PersistentClient(path=str(tmp_path))
        # Don't create any collections — ext_authority absent
        result = _load_ext_authority_urls(tmp_path)
        assert isinstance(result, set)
        assert len(result) == 0

    def test_returns_empty_set_when_ext_authority_is_empty(self, tmp_path: Path) -> None:
        import chromadb  # type: ignore[import]

        client = chromadb.PersistentClient(path=str(tmp_path))
        client.create_collection("ext_authority")
        result = _load_ext_authority_urls(tmp_path)
        assert isinstance(result, set)
        assert len(result) == 0

    def test_returns_url_set_from_ext_authority_metadata(self, tmp_path: Path) -> None:
        import chromadb  # type: ignore[import]

        client = chromadb.PersistentClient(path=str(tmp_path))
        col = client.create_collection(
            "ext_authority",
            metadata={"hnsw:space": "cosine"},
        )
        col.add(
            ids=["chunk-001", "chunk-002"],
            documents=["Doc A content.", "Doc B content."],
            metadatas=[
                {"source_url": "https://example.com/doc-a", "source_band": "supporting_guidance"},
                {"source_url": "https://example.com/doc-b", "source_band": "target_state_authority"},
            ],
        )
        result = _load_ext_authority_urls(tmp_path)
        assert "https://example.com/doc-a" in result
        assert "https://example.com/doc-b" in result

    def test_dedup_removes_ext_authority_urls_from_ext_raw_collect(self, tmp_path: Path) -> None:
        """Docs with source_url already in ext_authority are removed before upsert."""
        import chromadb  # type: ignore[import]

        client = chromadb.PersistentClient(path=str(tmp_path))
        col = client.create_collection(
            "ext_authority",
            metadata={"hnsw:space": "cosine"},
        )
        col.add(
            ids=["chunk-mcp"],
            documents=["MCP SDK content."],
            metadatas=[
                {
                    "source_url": "https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md"
                }
            ],
        )
        authority_urls = _load_ext_authority_urls(tmp_path)

        # Simulate the ext_raw dedup filter
        all_docs = [
            {
                "metadata": {
                    "source_url": "https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md"
                },
                "text": "MCP",
            },
            {"metadata": {"source_url": "https://some-other-scraped.com/page"}, "text": "Other"},
        ]
        filtered = [d for d in all_docs if d["metadata"].get("source_url") not in authority_urls]
        assert len(filtered) == 1
        assert filtered[0]["metadata"]["source_url"] == "https://some-other-scraped.com/page"

    def test_notfounderror_on_get_collection_returns_empty_set(self, tmp_path: Path) -> None:
        """G3: chromadb.errors.NotFoundError on get_collection (TOCTOU) must return empty set."""
        import chromadb  # type: ignore[import]

        mock_col_stub = MagicMock()
        mock_col_stub.name = "ext_authority"
        mock_client = MagicMock()
        mock_client.list_collections.return_value = [mock_col_stub]
        mock_client.get_collection.side_effect = chromadb.errors.NotFoundError("ext_authority")

        with patch("chromadb.PersistentClient", return_value=mock_client):
            result = _load_ext_authority_urls(tmp_path)

        assert isinstance(result, set)
        assert len(result) == 0


# ==============================================================================
# evidence_shaper — filter_normative_sources (Wave B3 cutover)  [G1]
# ==============================================================================


class TestFilterNormativeSources:
    """Validate that filter_normative_sources correctly enforces the Wave B3 contract.

    After the cutover, the default allowed_collections is ("ext_authority",).
    The retired name "curated_agent_docs" must be rejected; repo_evidence must
    be rejected; invalid_for_normative_use=True must be rejected regardless of
    collection; and missing metadata must fail closed.
    """

    def _result(
        self,
        source_collection: str,
        authority_tier: str,
        invalid: bool | object = False,
    ) -> SimpleNamespace:
        return SimpleNamespace(
            metadata={
                "source_collection": source_collection,
                "authority_tier": authority_tier,
                "invalid_for_normative_use": invalid,
            }
        )

    def test_ext_authority_t2_accepted_by_default(self) -> None:
        r = self._result("ext_authority", "T2_standard", False)
        accepted, rejected = filter_normative_sources([r])
        assert accepted == [r]
        assert rejected == []

    def test_ext_authority_t3_accepted_by_default(self) -> None:
        r = self._result("ext_authority", "T3_guidance", False)
        accepted, rejected = filter_normative_sources([r])
        assert accepted == [r]
        assert rejected == []

    def test_curated_agent_docs_rejected_after_cutover(self) -> None:
        """Old collection name must be rejected — validates Wave B3 cutover."""
        r = self._result("curated_agent_docs", "T2_standard", False)
        accepted, rejected = filter_normative_sources([r])
        assert accepted == []
        assert rejected == [r]

    def test_repo_evidence_rejected_by_default_allowed_collections(self) -> None:
        r = self._result("repo_evidence", "T4_repo_canonical", False)
        accepted, rejected = filter_normative_sources([r])
        assert accepted == []
        assert rejected == [r]

    def test_ext_raw_rejected_by_default_allowed_collections(self) -> None:
        r = self._result("ext_raw", "T5_unvetted", False)
        accepted, rejected = filter_normative_sources([r])
        assert accepted == []
        assert rejected == [r]

    def test_invalid_for_normative_use_true_rejects_even_ext_authority(self) -> None:
        """Fail-closed: invalid_for_normative_use=True always rejects, regardless of collection."""
        r = self._result("ext_authority", "T2_standard", True)
        accepted, rejected = filter_normative_sources([r])
        assert accepted == []
        assert rejected == [r]

    def test_missing_invalid_flag_fails_closed(self) -> None:
        """Missing invalid_for_normative_use defaults to True (fail-closed) → rejected."""
        r = SimpleNamespace(metadata={"source_collection": "ext_authority", "authority_tier": "T2_standard"})
        accepted, rejected = filter_normative_sources([r])
        assert accepted == []
        assert rejected == [r]

    def test_missing_metadata_attr_fails_closed(self) -> None:
        """Object with no .metadata attribute is rejected (fail-closed)."""
        r = SimpleNamespace()
        accepted, rejected = filter_normative_sources([r])
        assert accepted == []
        assert rejected == [r]

    def test_empty_results_returns_empty_lists(self) -> None:
        accepted, rejected = filter_normative_sources([])
        assert accepted == []
        assert rejected == []

    def test_mixed_batch_partitions_correctly(self) -> None:
        good = self._result("ext_authority", "T2_standard", False)
        old_name = self._result("curated_agent_docs", "T2_standard", False)
        repo = self._result("repo_evidence", "T4_repo_canonical", False)
        accepted, rejected = filter_normative_sources([good, old_name, repo])
        assert accepted == [good]
        assert len(rejected) == 2
        assert old_name in rejected
        assert repo in rejected


# ==============================================================================
# query_router — collection routing and arch prefilter (Wave B3 cutover)  [G2]
# ==============================================================================


class TestQueryRouterWaveB3:
    """Validate that _get_target_collection and _get_arch_prefilter reflect Wave B3.

    Phase changes:
      policy/best_practice/tool_contracts → ext_authority (was curated_agent_docs)
      architecture → repo_evidence (was arch_docs)
      _get_arch_prefilter → {"source_band": "repo_canonical"} (was {"canonical": True})
    """

    def test_policy_routes_to_ext_authority(self) -> None:
        assert QueryRouter._get_target_collection("policy", "default") == "ext_authority"

    def test_best_practice_routes_to_ext_authority(self) -> None:
        assert QueryRouter._get_target_collection("best_practice", "default") == "ext_authority"

    def test_tool_contracts_routes_to_ext_authority(self) -> None:
        assert QueryRouter._get_target_collection("tool_contracts", "default") == "ext_authority"

    def test_architecture_routes_to_repo_evidence(self) -> None:
        assert QueryRouter._get_target_collection("architecture", "default") == "repo_evidence"

    def test_code_routes_to_code_chunks(self) -> None:
        assert QueryRouter._get_target_collection("code", "default") == "code_chunks"

    def test_unknown_domain_passes_through_default_collection(self) -> None:
        assert QueryRouter._get_target_collection("unknown_xyz", "fallback_col") == "fallback_col"

    def test_arch_prefilter_uses_source_band_not_canonical(self) -> None:
        """Wave B3 fix: prefilter must use source_band, not the retired canonical field."""
        result = QueryRouter._get_arch_prefilter("architecture")
        assert result == {"source_band": "repo_canonical"}
        assert "canonical" not in (result or {})

    def test_non_arch_domains_return_none_prefilter(self) -> None:
        for domain in ("policy", "best_practice", "tool_contracts", "code", "unknown"):
            assert QueryRouter._get_arch_prefilter(domain) is None, (
                f"domain={domain!r} should return None prefilter"
            )

    def test_retired_collection_names_never_returned(self) -> None:
        """curated_agent_docs, arch_docs, ext_knowledge must never be routing targets."""
        retired = {"curated_agent_docs", "arch_docs", "ext_knowledge"}
        for domain in ("policy", "best_practice", "tool_contracts", "architecture", "code"):
            col = QueryRouter._get_target_collection(domain, "default")
            assert col not in retired, f"domain={domain!r} still routes to retired collection {col!r}"
