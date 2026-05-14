"""W2 tests: C0 evidence metrics extractor, support_status enum alignment,
support_target_met dynamic computation, and apps_rg import boundary.

Plan: apps-rg-retrieval-metrics-ownership-and-c0-evidence-plan W2

Tests
-----
- Canonical enum: PARTIAL is absent; only the six allowed values are used.
- PARTIAL in FEC is coerced to WEAK_WITH_CAVEATS with a warning.
- support_target_met=True when all required prefixes present.
- support_target_met=False when a required prefix is absent.
- Empty target → support_target_met=True (vacuously).
- Single-prefix target evaluates correctly.
- No apps_rg import in evidence_metrics_extractor.py (AST scan).
- SUPPORT_STATUS_PARTIAL not in CANONICAL_SUPPORT_STATUS_VALUES.
- SUPPORT_STATUS_PASSING_VALUES contains only PASS.
- extract_evidence_metrics returns correct evidence_count.
- support_score_profile groups items by source class correctly.
- SUPPORT_STATUS_WEAK_WITH_CAVEATS is in canonical set.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.runtime.c0.evidence_metrics_extractor import (
    CANONICAL_SUPPORT_STATUS_VALUES,
    EvidenceMetrics,
    SupportTarget,
    extract_evidence_metrics,
)
from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_PASSING_VALUES,
    SUPPORT_STATUS_WEAK_WITH_CAVEATS,
    STATUS_UNKNOWN,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_EXTRACTOR_PATH = (
    Path(__file__).parents[2]
    / "agentic_core"
    / "runtime"
    / "c0"
    / "evidence_metrics_extractor.py"
)


def _make_fec(
    retrieval_sources: tuple[str, ...] = (),
    support_status: str = SUPPORT_STATUS_PASS,
    evidence_items: tuple[EvidenceItem, ...] = (),
) -> FinalEvidenceContract:
    return FinalEvidenceContract(
        request_id="test-req",
        run_id="test-run",
        app_id="apps_rg",
        trace_id="test-trace",
        evidence_items=evidence_items,
        retrieval_sources=retrieval_sources,
        support_target_met=True,
        support_target_partial=False,
        evidence_collection_timestamp="2026-01-01T00:00:00Z",
        schema_version="test",
        l5_certification_ref="test-ref",
        support_status=support_status,
    )


def _make_item(source: str, confidence: float = 0.9) -> EvidenceItem:
    return EvidenceItem(
        source=source,
        content="test content",
        content_type="text",
        confidence_score=confidence,
    )


# ---------------------------------------------------------------------------
# Enum alignment tests
# ---------------------------------------------------------------------------

class TestCanonicalEnum:
    def test_partial_not_in_canonical_set(self) -> None:
        assert "PARTIAL" not in CANONICAL_SUPPORT_STATUS_VALUES

    def test_weak_with_caveats_in_canonical_set(self) -> None:
        assert SUPPORT_STATUS_WEAK_WITH_CAVEATS in CANONICAL_SUPPORT_STATUS_VALUES

    def test_pass_in_canonical_set(self) -> None:
        assert SUPPORT_STATUS_PASS in CANONICAL_SUPPORT_STATUS_VALUES

    def test_six_canonical_values(self) -> None:
        expected = {"PASS", "WEAK_WITH_CAVEATS", "CONFLICTED", "EMPTY", "BLOCKED", "UNKNOWN"}
        assert CANONICAL_SUPPORT_STATUS_VALUES == expected

    def test_passing_values_contains_only_pass(self) -> None:
        assert SUPPORT_STATUS_PASSING_VALUES == frozenset({"PASS"})

    def test_partial_not_a_passing_value(self) -> None:
        assert "PARTIAL" not in SUPPORT_STATUS_PASSING_VALUES

    def test_weak_with_caveats_not_a_passing_value(self) -> None:
        assert SUPPORT_STATUS_WEAK_WITH_CAVEATS not in SUPPORT_STATUS_PASSING_VALUES


# ---------------------------------------------------------------------------
# PARTIAL coercion tests
# ---------------------------------------------------------------------------

class TestPartialCoercion:
    def test_partial_coerced_to_weak_with_caveats(self) -> None:
        fec = _make_fec(support_status="PARTIAL")
        target = SupportTarget.from_prefix_list([])
        metrics = extract_evidence_metrics(fec, target)
        assert metrics.support_status == SUPPORT_STATUS_WEAK_WITH_CAVEATS

    def test_partial_coercion_emits_warning(self) -> None:
        fec = _make_fec(support_status="PARTIAL")
        target = SupportTarget.from_prefix_list([])
        metrics = extract_evidence_metrics(fec, target)
        assert any("PARTIAL" in w for w in metrics.coercion_warnings)

    def test_weak_coerced_to_weak_with_caveats(self) -> None:
        fec = _make_fec(support_status="WEAK")
        target = SupportTarget.from_prefix_list([])
        metrics = extract_evidence_metrics(fec, target)
        assert metrics.support_status == SUPPORT_STATUS_WEAK_WITH_CAVEATS

    def test_pass_not_coerced(self) -> None:
        fec = _make_fec(support_status=SUPPORT_STATUS_PASS)
        target = SupportTarget.from_prefix_list([])
        metrics = extract_evidence_metrics(fec, target)
        assert metrics.support_status == SUPPORT_STATUS_PASS
        assert metrics.coercion_warnings == ()

    def test_unknown_status_coerced(self) -> None:
        fec = _make_fec(support_status="MADE_UP_STATUS")
        target = SupportTarget.from_prefix_list([])
        metrics = extract_evidence_metrics(fec, target)
        assert metrics.support_status == STATUS_UNKNOWN
        assert metrics.coercion_warnings


# ---------------------------------------------------------------------------
# support_target_met tests — proves computation is from supplied target
# ---------------------------------------------------------------------------

class TestSupportTargetMet:
    def test_both_prefixes_present_is_sufficient(self) -> None:
        fec = _make_fec(
            retrieval_sources=("jd_payload:jd_text", "resume_payload:resume_text")
        )
        target = SupportTarget.from_prefix_list(["jd_payload", "resume_payload"])
        metrics = extract_evidence_metrics(fec, target)
        assert metrics.support_target_met is True

    def test_missing_resume_not_sufficient(self) -> None:
        fec = _make_fec(retrieval_sources=("jd_payload:jd_text",))
        target = SupportTarget.from_prefix_list(["jd_payload", "resume_payload"])
        metrics = extract_evidence_metrics(fec, target)
        assert metrics.support_target_met is False

    def test_missing_jd_not_sufficient(self) -> None:
        fec = _make_fec(retrieval_sources=("resume_payload:resume_text",))
        target = SupportTarget.from_prefix_list(["jd_payload", "resume_payload"])
        metrics = extract_evidence_metrics(fec, target)
        assert metrics.support_target_met is False

    def test_empty_target_always_sufficient(self) -> None:
        fec = _make_fec(retrieval_sources=())
        target = SupportTarget.from_prefix_list([])
        metrics = extract_evidence_metrics(fec, target)
        assert metrics.support_target_met is True

    def test_single_prefix_target_true(self) -> None:
        fec = _make_fec(retrieval_sources=("chroma:candidate_profile",))
        target = SupportTarget.from_prefix_list(["chroma"])
        metrics = extract_evidence_metrics(fec, target)
        assert metrics.support_target_met is True

    def test_single_prefix_target_false(self) -> None:
        fec = _make_fec(retrieval_sources=("resume_payload:resume_text",))
        target = SupportTarget.from_prefix_list(["jd_payload"])
        metrics = extract_evidence_metrics(fec, target)
        assert metrics.support_target_met is False

    def test_target_label_preserved(self) -> None:
        fec = _make_fec()
        target = SupportTarget.from_prefix_list(["jd_payload"], label="my_target")
        metrics = extract_evidence_metrics(fec, target)
        assert metrics.support_target_label == "my_target"

    def test_different_targets_produce_different_results(self) -> None:
        """Prove target drives outcome, not hardcoded field names."""
        sources = ("jd_payload:jd_text", "resume_payload:resume_text")
        fec = _make_fec(retrieval_sources=sources)

        # Target that requires a source prefix NOT present
        strict_target = SupportTarget.from_prefix_list(
            ["jd_payload", "resume_payload", "chroma"]
        )
        # Target that only requires what IS present
        lenient_target = SupportTarget.from_prefix_list(["jd_payload"])

        strict_metrics = extract_evidence_metrics(fec, strict_target)
        lenient_metrics = extract_evidence_metrics(fec, lenient_target)

        assert strict_metrics.support_target_met is False
        assert lenient_metrics.support_target_met is True


# ---------------------------------------------------------------------------
# Extractor output shape tests
# ---------------------------------------------------------------------------

class TestExtractorOutput:
    def test_evidence_count(self) -> None:
        items = (_make_item("chroma:a"), _make_item("chroma:b"))
        fec = _make_fec(evidence_items=items)
        metrics = extract_evidence_metrics(fec, SupportTarget.from_prefix_list([]))
        assert metrics.evidence_count == 2

    def test_retrieval_sources_preserved(self) -> None:
        sources = ("jd_payload:jd_text", "resume_payload:resume_text")
        fec = _make_fec(retrieval_sources=sources)
        metrics = extract_evidence_metrics(fec, SupportTarget.from_prefix_list([]))
        assert metrics.retrieval_sources == sources

    def test_support_score_profile(self) -> None:
        items = (
            _make_item("chroma:candidate_profile"),
            _make_item("chroma:candidate_profile"),
            _make_item("chroma:project_evidence"),
        )
        fec = _make_fec(evidence_items=items)
        metrics = extract_evidence_metrics(fec, SupportTarget.from_prefix_list([]))
        assert metrics.support_score_profile["candidate_profile"] == 2
        assert metrics.support_score_profile["project_evidence"] == 1

    def test_returns_evidence_metrics_instance(self) -> None:
        fec = _make_fec()
        metrics = extract_evidence_metrics(fec, SupportTarget.from_prefix_list([]))
        assert isinstance(metrics, EvidenceMetrics)


# ---------------------------------------------------------------------------
# AST import boundary scan
# ---------------------------------------------------------------------------

class TestImportBoundary:
    def test_extractor_file_exists(self) -> None:
        assert _EXTRACTOR_PATH.exists(), (
            f"evidence_metrics_extractor.py not found at {_EXTRACTOR_PATH}"
        )

    def test_no_apps_rg_import_in_extractor(self) -> None:
        """AST scan: extractor must not import from apps_rg.*."""
        source = _EXTRACTOR_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        violations: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("apps_rg"):
                        violations.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.startswith("apps_rg"):
                    violations.append(f"from {module} import ...")
        assert not violations, (
            f"apps_rg import boundary violated in extractor: {violations}"
        )

    def test_no_apps_star_import_in_extractor(self) -> None:
        """AST scan: extractor must not import from any apps_* package."""
        source = _EXTRACTOR_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        violations: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("apps_"):
                        violations.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.startswith("apps_"):
                    violations.append(f"from {module} import ...")
        assert not violations, (
            f"apps_* import boundary violated in extractor: {violations}"
        )
