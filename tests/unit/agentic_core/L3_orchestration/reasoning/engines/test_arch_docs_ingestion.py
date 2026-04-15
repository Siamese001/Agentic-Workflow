"""Unit tests for Phase 2 ingestion hardening in ingest_arch_docs.py.

Tests:
  - SCAN_DIRS restricted to ["docs"]
  - EXCLUDE_DIRS covers noisy subdirs (reports, plans, evidence, windsurf)
  - _compute_authority_level() returns correct float per doc_type / path
  - _compute_doc_family() maps path hierarchy to family label
  - _is_canonical() correctly classifies canonical vs historical docs
  - _extract_title() extracts H1 heading or falls back to stem
  - chunk_by_headings() produces (heading_path, text) tuples
  - should_exclude() blocks noisy subdir paths
  - Rich metadata keys are present in every collected chunk
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[7]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.generate.ingestion.ingest_arch_docs import (
    EXCLUDE_DIRS,
    SCAN_DIRS,
    _compute_authority_level,
    _compute_doc_family,
    _compute_source_area,
    _extract_title,
    _is_canonical,
    chunk_by_headings,
    should_exclude,
)


# ---------------------------------------------------------------------------
# SCAN_DIRS scope
# ---------------------------------------------------------------------------


def test_scan_dirs_restricted_to_docs() -> None:
    assert SCAN_DIRS == ["docs"], f"Expected ['docs'], got {SCAN_DIRS}"


def test_scan_dirs_excludes_noisy_app_dirs() -> None:
    noisy = {"apps_eval", "apps_exec", "tools", "ops_scripts", "agentic_core", "system_learning"}
    assert not noisy.intersection(set(SCAN_DIRS)), "SCAN_DIRS must not include noisy app/tool dirs"


# ---------------------------------------------------------------------------
# EXCLUDE_DIRS coverage
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "noisy_dir",
    ["reports", "plans", "evidence", "windsurf", "_archive", "archives"],
)
def test_exclude_dirs_contains_noisy_subdirs(noisy_dir: str) -> None:
    assert noisy_dir in EXCLUDE_DIRS, f"EXCLUDE_DIRS must contain '{noisy_dir}'"


@pytest.mark.parametrize(
    "path_str",
    [
        "docs/reports/2025/some_report.md",
        "docs/plans/sprint_plan.md",
        "docs/evidence/phase1_evidence.md",
        "docs/windsurf/llms-full.txt",
        "docs/architecture/_archive/old_adr.md",
    ],
)
def test_should_exclude_noisy_paths(path_str: str) -> None:
    p = REPO_ROOT / path_str
    assert should_exclude(p), f"should_exclude() must return True for {path_str}"


def test_should_not_exclude_canonical_paths() -> None:
    canonical = [
        REPO_ROOT / "docs/architecture/adr001.md",
        REPO_ROOT / "docs/contracts/api_contract.md",
        REPO_ROOT / "docs/guides/dev_guide.md",
        REPO_ROOT / "README.md",
    ]
    for p in canonical:
        assert not should_exclude(p), f"should_exclude() must return False for {p}"


# ---------------------------------------------------------------------------
# _compute_authority_level
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rel_path,doc_type,expected_min,expected_max",
    [
        ("docs/architecture/adr001.md", "adr", 0.99, 1.01),
        ("docs/architecture/design_doc.md", "architecture", 0.84, 0.86),
        ("docs/contracts/api_contract.md", "contract", 0.74, 0.76),
        ("docs/specs/spec_v1.md", "spec", 0.64, 0.66),
        ("docs/guides/dev_guide.md", "guide", 0.54, 0.56),
        ("docs/reference/glossary.md", "doc", 0.39, 0.41),
        ("docs/reports/q1_report.md", "doc", 0.0, 0.15),
        ("docs/plans/sprint_plan.md", "doc", 0.0, 0.15),
    ],
)
def test_compute_authority_level(
    rel_path: str, doc_type: str, expected_min: float, expected_max: float
) -> None:
    path = Path(rel_path)
    level = _compute_authority_level(path, doc_type)
    assert expected_min <= level <= expected_max, (
        f"authority_level for {rel_path} ({doc_type}) = {level}, expected [{expected_min}, {expected_max}]"
    )


# ---------------------------------------------------------------------------
# _compute_doc_family
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rel_path,expected_family",
    [
        ("docs/adr/adr001.md", "adr"),
        ("docs/architecture/system_design.md", "architecture"),
        ("docs/contracts/api_contract.md", "contract"),
        ("docs/specs/spec_v1.md", "spec"),
        ("docs/standards/coding_standard.md", "standard"),
        ("docs/guides/dev_guide.md", "guide"),
        ("docs/reference/glossary.md", "reference"),
        ("docs/policies/security_policy.md", "policy"),
        ("README.md", "overview"),
        ("AGENTS.md", "overview"),
        ("docs/other/random.md", "doc"),
    ],
)
def test_compute_doc_family(rel_path: str, expected_family: str) -> None:
    path = Path(rel_path)
    family = _compute_doc_family(path)
    assert family == expected_family, f"doc_family for {rel_path} = {family!r}, expected {expected_family!r}"


# ---------------------------------------------------------------------------
# _is_canonical
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rel_path,doc_type,expected",
    [
        ("docs/architecture/adr001.md", "adr", True),
        ("docs/contracts/api.md", "contract", True),
        ("docs/specs/spec.md", "spec", True),
        ("docs/guides/guide.md", "guide", True),
        ("README.md", "overview", True),
        ("docs/reports/q1_report.md", "doc", False),
        ("docs/plans/sprint.md", "doc", False),
        ("docs/evidence/phase1.md", "doc", False),
    ],
)
def test_is_canonical(rel_path: str, doc_type: str, expected: bool) -> None:
    path = Path(rel_path)
    result = _is_canonical(path, doc_type)
    assert result is expected, f"_is_canonical({rel_path}, {doc_type}) = {result}, expected {expected}"


# ---------------------------------------------------------------------------
# _extract_title
# ---------------------------------------------------------------------------


def test_extract_title_from_h1() -> None:
    source = "# My Architecture Decision Record\n\nSome content here."
    path = Path("docs/architecture/adr001.md")
    title = _extract_title(source, path)
    assert title == "My Architecture Decision Record"


def test_extract_title_first_h1_only() -> None:
    source = "# First Heading\n\n## Second Level\n\n# Another H1"
    path = Path("docs/architecture/adr001.md")
    title = _extract_title(source, path)
    assert title == "First Heading"


def test_extract_title_fallback_to_stem() -> None:
    source = "No headings here, just plain text about architecture."
    path = Path("docs/architecture/system_design_v2.md")
    title = _extract_title(source, path)
    assert title == "system design v2"


def test_extract_title_not_h2() -> None:
    source = "## Only H2 heading\n\nContent without H1."
    path = Path("docs/architecture/adr001.md")
    title = _extract_title(source, path)
    assert title == "adr001"


def test_extract_title_truncated_at_200_chars() -> None:
    long_title = "A" * 300
    source = f"# {long_title}\n\nContent."
    path = Path("docs/architecture/long.md")
    title = _extract_title(source, path)
    assert len(title) <= 200


# ---------------------------------------------------------------------------
# chunk_by_headings
# ---------------------------------------------------------------------------


def test_chunk_by_headings_returns_tuples() -> None:
    text = "# Main Title\n\nSome content.\n\n## Section A\n\nMore content here about section A.\n"
    result = chunk_by_headings(text)
    assert isinstance(result, list)
    for item in result:
        assert isinstance(item, tuple)
        assert len(item) == 2
        heading_path, chunk_text = item
        assert isinstance(heading_path, str)
        assert isinstance(chunk_text, str)


def test_chunk_by_headings_heading_path_breadcrumb() -> None:
    filler = "word " * 20  # ~100 chars — safely above MIN_BODY_CHARS=80
    text = (
        f"# Architecture\n\n{filler}\n\n## Query Routing\n\n{filler}\n\n### Fallback Strategy\n\n{filler}\n"
    )
    result = chunk_by_headings(text)
    paths = [hp for hp, _ in result]
    assert any("Architecture" in hp for hp in paths)
    assert any("Query Routing" in hp for hp in paths)
    assert any("Fallback Strategy" in hp for hp in paths)


def test_chunk_by_headings_h1_resets_h2_h3() -> None:
    text = "# Section 1\n\n## Sub 1\n\nContent.\n\n# Section 2\n\n## Sub 2\n\nContent for section 2 sub 2.\n"
    result = chunk_by_headings(text)
    paths = [hp for hp, _ in result]
    # "Section 1" heading path must not appear alongside "Sub 2"
    assert not any("Section 1" in hp and "Sub 2" in hp for hp in paths)


def test_chunk_by_headings_no_headings_fallback() -> None:
    text = "A" * 100 + "\n\nSome plain text without any headings at all."
    result = chunk_by_headings(text, max_chars=200)
    assert len(result) >= 1
    for hp, chunk in result:
        assert hp == "no-headings"


def test_chunk_by_headings_skips_tiny_sections() -> None:
    text = "# Big Section\n\n" + "Content " * 50 + "\n\n## Tiny\n\na\n"
    result = chunk_by_headings(text)
    # The tiny section "a" (< MIN_BODY_CHARS=80) should be skipped
    tiny_chunks = [chunk for _, chunk in result if len(chunk.strip()) < 5]
    assert len(tiny_chunks) == 0


def test_chunk_by_headings_large_section_splits() -> None:
    big_content = "word " * 1000  # ~5000 chars, exceeds CHUNK_CHARS=2000
    text = f"# Large Section\n\n{big_content}\n"
    result = chunk_by_headings(text, max_chars=2000)
    assert len(result) > 1
    for hp, chunk in result:
        assert len(chunk) <= 2000 + 200  # allow overlap margin


# ---------------------------------------------------------------------------
# Rich metadata keys
# ---------------------------------------------------------------------------


_REQUIRED_METADATA_KEYS = {
    "artifact_type",
    "doc_type",
    "doc_family",
    "file_path",
    "layer",
    "chunk_index",
    "canonical_digest",
    "source",
    "title",
    "heading_path",
    "authority_level",
    "canonical",
    "retrieval_weight",
    "source_area",
}


def _make_test_chunk_metadata(
    rel_path: str = "docs/architecture/adr001.md",
    doc_type: str = "adr",
) -> dict:
    from tools.generate.ingestion.ingest_arch_docs import (
        compute_digest,
        detect_doc_type,
        detect_layer,
    )

    path = Path(rel_path)
    source = "# Test ADR\n\nContent for testing metadata presence."
    return {
        "artifact_type": "arch_doc",
        "doc_type": doc_type,
        "doc_family": _compute_doc_family(path),
        "file_path": rel_path,
        "layer": detect_layer(path),
        "chunk_index": 0,
        "canonical_digest": compute_digest(source),
        "source": "markdown",
        "title": _extract_title(source, path),
        "heading_path": "Test ADR",
        "authority_level": _compute_authority_level(path, doc_type),
        "canonical": _is_canonical(path, doc_type),
        "retrieval_weight": 1.0,
        "source_area": _compute_source_area(path),
    }


def test_metadata_contains_all_required_keys() -> None:
    meta = _make_test_chunk_metadata()
    missing = _REQUIRED_METADATA_KEYS - set(meta.keys())
    assert not missing, f"Metadata missing required keys: {missing}"


def test_metadata_authority_level_is_float() -> None:
    meta = _make_test_chunk_metadata()
    assert isinstance(meta["authority_level"], float)
    assert 0.0 <= meta["authority_level"] <= 1.0


def test_metadata_canonical_is_bool() -> None:
    meta = _make_test_chunk_metadata()
    assert isinstance(meta["canonical"], bool)


def test_metadata_retrieval_weight_values() -> None:
    canonical_meta = _make_test_chunk_metadata("docs/architecture/adr001.md", "adr")
    noisy_path = "docs/reports/q1_report.md"
    noisy_canonical = _is_canonical(Path(noisy_path), "doc")
    noisy_weight = 1.0 if noisy_canonical else 0.4
    assert canonical_meta["retrieval_weight"] == 1.0
    assert noisy_weight == 0.4


# ---------------------------------------------------------------------------
# GAP-R7: validate_dim failure path
# ---------------------------------------------------------------------------


def test_validate_dim_raises_on_mismatch() -> None:
    """Failure path: validate_dim() raises ValueError when embedding dim != expected."""
    from tools.generate.ingestion.ingest_arch_docs import validate_dim

    with pytest.raises(ValueError, match="dim="):
        validate_dim([[0.1, 0.2]], expected=3)  # dim=2, expected=3


def test_validate_dim_passes_on_match() -> None:
    """Happy path: validate_dim() does not raise when dims match."""
    from tools.generate.ingestion.ingest_arch_docs import validate_dim

    validate_dim([[0.1, 0.2, 0.3]], expected=3)  # dim=3 == expected=3 → no raise


# ---------------------------------------------------------------------------
# GAP-R8: chunk_text edge cases
# ---------------------------------------------------------------------------


def test_chunk_text_small_text_single_chunk() -> None:
    """Happy path: text shorter than chunk_size returns a single chunk."""
    from tools.generate.ingestion.ingest_arch_docs import chunk_text

    text = "Short text that fits in one chunk."
    result = chunk_text(text, chunk_size=200)
    assert len(result) == 1
    assert result[0] == text


def test_chunk_text_empty_string_returns_empty() -> None:
    """Edge case: empty / whitespace-only text returns []."""
    from tools.generate.ingestion.ingest_arch_docs import chunk_text

    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_overlap_zero_no_infinite_loop() -> None:
    """Edge case: overlap=0 must terminate and produce correct chunk count."""
    from tools.generate.ingestion.ingest_arch_docs import chunk_text

    text = "x" * 300
    result = chunk_text(text, chunk_size=100, overlap=0)
    assert len(result) >= 2
    for chunk in result:
        assert len(chunk) <= 100
