"""Tests for ``agentic_core.L6_observability.semconv.runtime`` SSOT.

Covers:
  - Every spec stage (1..14) appears in STAGE_SPANS.
  - Every span name in ALL_SPAN_NAMES has the correct stage label.
  - Every required attribute set is non-empty.
  - Helper functions ``stage_for_span`` / ``attrs_for_stage`` /
    ``label_for_stage`` are coherent.
  - The ASCII spec doc has at least one matching SPAN_* constant per stage box.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from agentic_core.L6_observability.semconv import runtime as R

REPO_ROOT = Path(__file__).resolve().parents[5]
SPEC_DOC = REPO_ROOT / "docs" / "reference" / "OTEL" / "Runtime ADG and OTEL Spans.md"


# ---------------------------------------------------------------------------
# Structural — stages, registries
# ---------------------------------------------------------------------------


def test_all_14_stages_present():
    assert set(R.STAGE_SPANS.keys()) == set(range(1, 15))


def test_every_stage_has_at_least_one_span():
    for stage_num, (label, spans, _attrs) in R.STAGE_SPANS.items():
        assert label, f"stage {stage_num} missing label"
        assert spans, f"stage {stage_num} ({label}) has no span names"


def test_every_stage_has_signature_attrs():
    for stage_num, (label, _spans, attrs) in R.STAGE_SPANS.items():
        assert attrs, f"stage {stage_num} ({label}) has empty signature attrs"
        # Every signature attr must be non-empty string
        for a in attrs:
            assert isinstance(a, str) and a, (
                f"stage {stage_num} ({label}) has malformed attr {a!r}"
            )


def test_all_span_names_indexable_to_a_stage():
    for span in R.ALL_SPAN_NAMES:
        stage = R.stage_for_span(span)
        assert stage is not None and 1 <= stage <= 14, (
            f"span {span!r} did not resolve to a 1..14 stage"
        )


def test_all_span_names_match_aggregated_stage_membership():
    aggregate = set()
    for _label, spans, _attrs in R.STAGE_SPANS.values():
        aggregate.update(spans)
    assert aggregate == R.ALL_SPAN_NAMES


def test_node_and_edge_registries_non_empty():
    assert len(R.ALL_NODE_TYPES) >= 30
    assert len(R.ALL_EDGE_TYPES) >= 30


def test_layer_constants_unique():
    layer_values = {
        R.LAYER_U0,
        R.LAYER_L0,
        R.LAYER_L1,
        R.LAYER_L2,
        R.LAYER_L3,
        R.LAYER_L4,
        R.LAYER_L5,
        R.LAYER_L6,
        R.LAYER_L7,
    }
    assert len(layer_values) == 9
    assert layer_values == R.ALL_LAYERS


def test_disposition_enum_complete():
    expected = {"allow", "deny", "reroute", "escalate", "commit_request"}
    assert R.VALID_DISPOSITIONS == expected


def test_retrieval_mode_enum_complete():
    expected = {"dense", "sparse", "hybrid", "graph"}
    assert R.VALID_RETRIEVAL_MODES == expected


def test_execution_form_enum_complete():
    expected = {"terminal", "single_step", "managed_workflow"}
    assert R.VALID_EXECUTION_FORMS == expected


# ---------------------------------------------------------------------------
# Helper coherence
# ---------------------------------------------------------------------------


def test_stage_for_span_unknown_returns_none():
    assert R.stage_for_span("does.not.exist") is None


def test_label_for_stage_resolves_known():
    assert R.label_for_stage(1) == "trace_root"
    assert R.label_for_stage(14) == "meta_learning"
    assert R.label_for_stage(99) == ""


def test_attrs_for_stage_unknown_returns_empty():
    assert R.attrs_for_stage(99) == frozenset()


# ---------------------------------------------------------------------------
# Cross-check against the spec doctrine document
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def spec_text() -> str:
    if not SPEC_DOC.exists():
        pytest.skip(f"spec doc missing: {SPEC_DOC}")
    return SPEC_DOC.read_text(encoding="utf-8")


def _extract_span_lines(text: str) -> set[str]:
    """Pull out span identifiers like ``L0.route.select`` from the doc.

    Span names follow the pattern ``[A-Z][\\w]+(\\.[\\w_]+)+``.
    """
    pattern = re.compile(r"\b([A-Z][\w]+(?:\.[\w_]+)+)\b")
    found: set[str] = set()
    for m in pattern.finditer(text):
        token = m.group(1)
        # Filter out markdown filename-ish patterns and obvious paths.
        if token.endswith(".md") or "/" in token or "\\" in token:
            continue
        # Heuristic: span names contain a lowercase word boundary (e.g. .intake.)
        # rather than being TitleCase paths like ``Foo.Bar.Baz``.
        if any(seg and seg[0].islower() for seg in token.split(".")[1:]):
            found.add(token)
    return found


def test_every_stage_in_doc_has_a_constant(spec_text: str) -> None:
    """Every span name appearing in the spec doc must exist as a constant.

    We extract candidate span names from the doc, then assert each one is
    present in ``ALL_SPAN_NAMES`` OR is one of the C0/RAG names that lives
    in ``rag.py`` (covered separately).
    """
    from agentic_core.L6_observability.semconv import rag as rag_semconv

    rag_names = set(rag_semconv.ALL_SPAN_NAMES)
    runtime_names = set(R.ALL_SPAN_NAMES)
    # Doc-only allowance: some span tokens like ``service.name`` /
    # ``deployment.environment`` are OTel resource attributes, not span names.
    OTEL_RESOURCE_ATTRS = {"service.name", "deployment.environment"}

    found = _extract_span_lines(spec_text)
    missing: list[str] = []
    for span in sorted(found):
        if span in OTEL_RESOURCE_ATTRS:
            continue
        if span in runtime_names or span in rag_names:
            continue
        # Filter known doc-only labels (e.g. ``terminal_class``, ``ingress_channel``)
        # are attribute names, not span names. Span names always have a dotted
        # segment beginning with a lowercase 'l', 'u', 'p', 'c', 'r', or 'e' verb-section.
        # Ours always start with uppercase prefix (L0, L1, U0, C0, PA, MetaLearning, etc.).
        first = span.split(".", 1)[0]
        if first not in {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "U0", "C0", "PA", "Exit", "UWG", "Response", "Runtime", "MetaLearning"}:
            continue
        missing.append(span)
    assert not missing, (
        f"Spec doc references span names absent from semconv: {missing}\n"
        "Add the missing constant to runtime.py and update STAGE_SPANS."
    )


def test_every_stage_box_has_section_in_doc(spec_text: str) -> None:
    """Sanity: each spec stage label has a corresponding header in the doc."""
    expected_headers = [
        "TRACE ROOT",
        "INTAKE",
        "L1 REASONING",
        "L0 ROUTE DECISION",
        "DIRECT",
        "L3 ORCHESTRATION",
        "C0 RETRIEVAL",
        "PROMPT ASSEMBLY",
        "L2 EXECUTION",
        "EXIT EVAL",
        "RESPONSE",
        "UWG / L4 COMMIT",
        "L6 EVAL",
        "META-LEARNING",
    ]
    for header in expected_headers:
        assert header in spec_text, f"spec doc missing section header: {header}"
