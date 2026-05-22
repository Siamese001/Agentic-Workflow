"""W3 tests: durable apps_rg per-run C0 metrics artifact.

Covers:
- Schema structure: all required keys always present.
- Canonical support_status enum enforcement (no PARTIAL).
- EMPTY / BLOCKED / UNKNOWN explicit states written, never silent absence.
- support_target_met computation.
- final_evidence_digest computed from evidence content.
- Artifact written to correct path on disk.
- c0_minimum_safety.py: PARTIAL removed from _PASSING_SUPPORT_STATUSES.
- Fixture example validates against schema.
- agentic_core remains app-agnostic (no apps_rg imports in extractor).
"""
from __future__ import annotations

import ast
import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
)
from apps_rg.runtime.bindings.c0_binding import APPS_RG_C0_CERT_REF
from apps_rg.runtime.bindings.c0_metrics_writer import (
    SCHEMA_VERSION,
    build_c0_metrics,
    make_empty_fec,
    write_c0_metrics,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REQUIRED_KEYS = {
    "schema_version",
    "run_id",
    "route_id",
    "retrieval_mode",
    "source_class_coverage",
    "support_status",
    "support_target_met",
    "evidence_counts",
    "retrieval_sources",
    "excluded_evidence_refs",
    "blocked_source_refs",
    "freshness_receipts",
    "citation_map",
    "support_score_profile",
    "final_evidence_digest",
    "briefing_source_type",
    "company_brief_provenance",
}

_CANONICAL_SUPPORT_STATUSES = {
    "PASS", "WEAK_WITH_CAVEATS", "CONFLICTED", "EMPTY", "BLOCKED", "UNKNOWN",
}

_EVIDENCE_COUNTS_KEYS = {"total", "excluded", "blocked"}

_REPO_ROOT = Path(__file__).parents[2]
_SCHEMA_PATH = _REPO_ROOT / "apps_rg" / "runtime" / "schemas" / "c0_metrics.schema.json"
_FIXTURE_PATH = _REPO_ROOT / "tests" / "_fixtures" / "c0_metrics_example.json"


def _make_fec(
    run_id: str = "run_test_001",
    sources: tuple[str, ...] = ("jd_payload:jd_text", "resume_payload:resume_text"),
    support_status: str = "PASS",
    support_target_met: bool = True,
    extra_items: tuple[EvidenceItem, ...] = (),
) -> FinalEvidenceContract:
    items = (
        EvidenceItem(source="jd_payload:jd_text", content="Software Engineer role at Acme"),
        EvidenceItem(source="resume_payload:resume_text", content="10 years Python"),
    ) + extra_items
    return FinalEvidenceContract(
        request_id=run_id,
        run_id=run_id,
        app_id="apps_rg",
        trace_id=run_id,
        evidence_items=items,
        retrieval_sources=sources,
        support_target_met=support_target_met,
        support_status=support_status,
        l5_certification_ref=APPS_RG_C0_CERT_REF,
    )


# ---------------------------------------------------------------------------
# TestSchemaStructure
# ---------------------------------------------------------------------------

class TestSchemaStructure:
    """All required keys must be present in every output, no exceptions."""

    def test_required_keys_present_native_c0(self):
        fec = _make_fec()
        result = build_c0_metrics(
            fec=fec, run_id="run_001", route_id="R2_GROUNDED_DRAFT",
            retrieval_mode="NATIVE_C0", briefing_source_type="NONE",
        )
        missing = _REQUIRED_KEYS - result.keys()
        assert not missing, f"Missing keys: {missing}"

    def test_schema_version_constant(self):
        fec = _make_fec()
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R0")
        assert result["schema_version"] == SCHEMA_VERSION == "c0_metrics.v1"

    def test_evidence_counts_sub_keys(self):
        fec = _make_fec()
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R0")
        missing = _EVIDENCE_COUNTS_KEYS - result["evidence_counts"].keys()
        assert not missing

    def test_evidence_counts_non_negative(self):
        fec = _make_fec()
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R0")
        counts = result["evidence_counts"]
        assert counts["total"] >= 0
        assert counts["excluded"] >= 0
        assert counts["blocked"] >= 0

    def test_run_id_preserved(self):
        fec = _make_fec(run_id="run_xyz_789")
        result = build_c0_metrics(fec=fec, run_id="run_xyz_789", route_id="R0")
        assert result["run_id"] == "run_xyz_789"

    def test_route_id_preserved(self):
        fec = _make_fec()
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R2_GROUNDED_DRAFT")
        assert result["route_id"] == "R2_GROUNDED_DRAFT"

    def test_citation_map_is_list_of_pairs(self):
        fec = _make_fec()
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R0")
        for pair in result["citation_map"]:
            assert isinstance(pair, list)
            assert len(pair) == 2

    def test_company_brief_provenance_null_by_default(self):
        fec = _make_fec()
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R0")
        assert result["company_brief_provenance"] is None

    def test_company_brief_provenance_populated(self):
        fec = _make_fec()
        prov = {"source": "tavily", "fetched_at": "2026-05-14T12:00:00Z", "freshness_ttl_days": 7}
        result = build_c0_metrics(
            fec=fec, run_id="r", route_id="R0",
            company_brief_provenance=prov,
        )
        assert result["company_brief_provenance"] == prov


# ---------------------------------------------------------------------------
# TestSupportStatusEnum
# ---------------------------------------------------------------------------

class TestSupportStatusEnum:
    """support_status in output must always be in the canonical six-value set."""

    @pytest.mark.parametrize("status", list(_CANONICAL_SUPPORT_STATUSES))
    def test_canonical_statuses_pass_through(self, status):
        fec = _make_fec(support_status=status)
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R0")
        assert result["support_status"] == status

    def test_partial_coerced_to_unknown(self):
        from unittest.mock import patch
        from agentic_core.runtime.c0.evidence_metrics_extractor import EvidenceMetrics
        import apps_rg.runtime.bindings.c0_metrics_writer as writer_mod

        fec = _make_fec(support_status="PASS")
        partial_metrics = EvidenceMetrics(
            support_status="PARTIAL",
            support_target_met=False,
            support_target_label="test",
            evidence_count=0,
            retrieval_sources=(),
            excluded_evidence_refs=(),
            blocked_source_refs=(),
            confidence_scores=(),
            freshness_receipts=(),
            citation_map=(),
            final_evidence_digest="",
            support_score_profile={},
            coercion_warnings=("coerced",),
        )
        with patch.object(writer_mod, "extract_evidence_metrics", return_value=partial_metrics):
            result = build_c0_metrics(fec=fec, run_id="r", route_id="R0")
        assert result["support_status"] == "UNKNOWN", (
            "PARTIAL is not in canonical enum; writer must coerce to UNKNOWN"
        )

    def test_output_support_status_never_partial(self):
        for status in _CANONICAL_SUPPORT_STATUSES:
            fec = _make_fec(support_status=status)
            result = build_c0_metrics(fec=fec, run_id="r", route_id="R0")
            assert result["support_status"] != "PARTIAL"

    def test_c0_minimum_safety_no_partial_in_passing(self):
        from apps_rg.runtime.bindings import c0_minimum_safety
        source = Path(c0_minimum_safety.__file__).read_text(encoding="utf-8")
        assert "_PARTIAL" not in source, (
            "_PARTIAL constant must be removed from c0_minimum_safety.py"
        )
        assert "PARTIAL" not in getattr(
            c0_minimum_safety, "_PASSING_SUPPORT_STATUSES", frozenset()
        ), "PARTIAL must not be in _PASSING_SUPPORT_STATUSES"


# ---------------------------------------------------------------------------
# TestRetrievalModes
# ---------------------------------------------------------------------------

class TestRetrievalModes:
    """Every retrieval mode produces an explicit, non-silent artifact."""

    @pytest.mark.parametrize("mode", [
        "UPLOADED_BRIEFING", "DELEGATED_APPS_RESEARCH", "NATIVE_C0", "NONE", "UNKNOWN",
    ])
    def test_valid_retrieval_modes(self, mode):
        fec = _make_fec()
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R0", retrieval_mode=mode)
        assert result["retrieval_mode"] == mode

    def test_none_mode_uses_make_empty_fec(self):
        fec = make_empty_fec("run_none_001", support_status="EMPTY")
        result = build_c0_metrics(
            fec=fec, run_id="run_none_001", route_id="R0",
            retrieval_mode="NONE",
        )
        assert result["retrieval_mode"] == "NONE"
        assert result["support_status"] == "EMPTY"
        assert result["support_target_met"] is False

    def test_blocked_mode_explicit(self):
        fec = make_empty_fec("run_blocked", support_status="BLOCKED")
        result = build_c0_metrics(
            fec=fec, run_id="run_blocked", route_id="R0",
            retrieval_mode="NONE",
        )
        assert result["support_status"] == "BLOCKED"
        assert result["support_target_met"] is False

    def test_unknown_mode_explicit(self):
        fec = make_empty_fec("run_unknown", support_status="UNKNOWN")
        result = build_c0_metrics(
            fec=fec, run_id="run_unknown", route_id="R0",
            retrieval_mode="UNKNOWN",
        )
        assert result["support_status"] == "UNKNOWN"
        assert result["support_target_met"] is False

    def test_unknown_retrieval_mode_coerced(self):
        fec = _make_fec()
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R0", retrieval_mode="GARBAGE")
        assert result["retrieval_mode"] == "UNKNOWN"

    def test_none_retrieval_mode_coerced(self):
        fec = _make_fec()
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R0", retrieval_mode=None)
        assert result["retrieval_mode"] == "UNKNOWN"


# ---------------------------------------------------------------------------
# TestSupportTargetMet
# ---------------------------------------------------------------------------

class TestSupportTargetMet:
    """support_target_met computed from profile-driven prefixes, not hardcoded."""

    def test_proof_prefixes_present_true(self):
        fec = _make_fec(
            sources=(
                "fact:allowed_1",
                "ledger:candidate_fact_ledger",
                "proof_pool:section_pool",
                "srfs:bundle_ref",
            ),
            support_target_met=True,
        )
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R0")
        assert result["support_target_met"] is True

    def test_missing_ledger_prefix_false(self):
        fec_stripped = FinalEvidenceContract(
            request_id="r", run_id="r", app_id="apps_rg", trace_id="r",
            evidence_items=(
                EvidenceItem(source="fact:allowed_1", content="proof fact"),
            ),
            retrieval_sources=("fact:allowed_1",),
            support_target_met=False,
            support_status="WEAK_WITH_CAVEATS",
            l5_certification_ref=APPS_RG_C0_CERT_REF,
        )
        result = build_c0_metrics(fec=fec_stripped, run_id="r", route_id="R0")
        assert result["support_target_met"] is False

    def test_empty_sources_false(self):
        fec = make_empty_fec("r", support_status="EMPTY")
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R0")
        assert result["support_target_met"] is False


# ---------------------------------------------------------------------------
# TestFinalEvidenceDigest
# ---------------------------------------------------------------------------

class TestFinalEvidenceDigest:
    """final_evidence_digest must be deterministic and non-empty."""

    def test_digest_non_empty(self):
        fec = _make_fec()
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R0")
        assert result["final_evidence_digest"]
        assert len(result["final_evidence_digest"]) == 64  # SHA-256 hex

    def test_digest_deterministic(self):
        fec = _make_fec(run_id="run_det")
        r1 = build_c0_metrics(fec=fec, run_id="run_det", route_id="R0")
        r2 = build_c0_metrics(fec=fec, run_id="run_det", route_id="R0")
        assert r1["final_evidence_digest"] == r2["final_evidence_digest"]

    def test_digest_differs_for_different_evidence(self):
        fec1 = _make_fec(run_id="r1")
        fec2 = _make_fec(
            run_id="r2",
            extra_items=(EvidenceItem(source="project_evidence:pe_001", content="Extra"),),
        )
        r1 = build_c0_metrics(fec=fec1, run_id="r1", route_id="R0")
        r2 = build_c0_metrics(fec=fec2, run_id="r2", route_id="R0")
        assert r1["final_evidence_digest"] != r2["final_evidence_digest"]

    def test_empty_fec_digest_is_sha256_of_empty(self):
        fec = make_empty_fec("r")
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R0")
        expected = hashlib.sha256("".encode("utf-8")).hexdigest()
        assert result["final_evidence_digest"] == expected


# ---------------------------------------------------------------------------
# TestArtifactWriter
# ---------------------------------------------------------------------------

class TestArtifactWriter:
    """write_c0_metrics creates the file at the correct path."""

    def test_writes_to_run_dir(self, tmp_path):
        fec = _make_fec(run_id="run_write_001")
        artifact = write_c0_metrics(
            fec=fec,
            run_id="run_write_001",
            route_id="R0",
            retrieval_mode="NATIVE_C0",
            runs_root=tmp_path,
        )
        assert artifact is not None
        assert artifact.exists()
        assert artifact.name == "c0_metrics.json"
        assert artifact.parent.name == "run_write_001"

    def test_written_content_is_valid_json(self, tmp_path):
        fec = _make_fec()
        artifact = write_c0_metrics(fec=fec, run_id="run_json", route_id="R0", runs_root=tmp_path)
        assert artifact is not None
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        assert isinstance(payload, dict)

    def test_written_content_has_required_keys(self, tmp_path):
        fec = _make_fec()
        artifact = write_c0_metrics(fec=fec, run_id="run_keys", route_id="R0", runs_root=tmp_path)
        assert artifact is not None
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        missing = _REQUIRED_KEYS - payload.keys()
        assert not missing

    def test_fail_soft_on_bad_path(self, tmp_path):
        blocker = tmp_path / "blocking_file"
        blocker.write_text("block", encoding="utf-8")
        fec = _make_fec()
        result = write_c0_metrics(
            fec=fec, run_id="run_x", route_id="R0",
            runs_root=blocker,
        )
        assert result is None  # fail-soft: runs_root is a file, mkdir raises OSError

    def test_empty_mode_writes_explicit_empty(self, tmp_path):
        fec = make_empty_fec("run_empty_001", support_status="EMPTY")
        artifact = write_c0_metrics(
            fec=fec, run_id="run_empty_001", route_id="R0",
            retrieval_mode="NONE",
            runs_root=tmp_path,
        )
        assert artifact is not None
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        assert payload["support_status"] == "EMPTY"
        assert payload["retrieval_mode"] == "NONE"
        assert payload["evidence_counts"]["total"] == 0


# ---------------------------------------------------------------------------
# TestFixtureAndSchema
# ---------------------------------------------------------------------------

class TestFixtureAndSchema:
    """Validate committed fixture against the JSON schema and required keys."""

    def test_fixture_file_exists(self):
        assert _FIXTURE_PATH.exists(), f"Missing fixture: {_FIXTURE_PATH}"

    def test_schema_file_exists(self):
        assert _SCHEMA_PATH.exists(), f"Missing schema: {_SCHEMA_PATH}"

    def test_fixture_valid_json(self):
        payload = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
        assert isinstance(payload, dict)

    def test_fixture_has_required_keys(self):
        payload = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
        missing = _REQUIRED_KEYS - payload.keys()
        assert not missing

    def test_fixture_schema_version(self):
        payload = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
        assert payload["schema_version"] == "c0_metrics.v1"

    def test_fixture_support_status_canonical(self):
        payload = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
        assert payload["support_status"] in _CANONICAL_SUPPORT_STATUSES

    def test_schema_required_keys_match(self):
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        schema_required = set(schema.get("required", []))
        assert schema_required == _REQUIRED_KEYS

    def test_fixture_validates_against_schema_required_keys(self):
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        fixture = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
        schema_required = set(schema.get("required", []))
        missing = schema_required - fixture.keys()
        assert not missing

    def test_fixture_retrieval_mode_valid(self):
        payload = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
        valid_modes = {"UPLOADED_BRIEFING", "DELEGATED_APPS_RESEARCH", "NATIVE_C0", "NONE", "UNKNOWN"}
        assert payload["retrieval_mode"] in valid_modes

    def test_fixture_briefing_source_type_valid(self):
        payload = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
        valid_types = {"UPLOADED_BRIEFING", "DELEGATED_APPS_RESEARCH", "NATIVE_C0", "NONE", "UNKNOWN"}
        assert payload["briefing_source_type"] in valid_types


# ---------------------------------------------------------------------------
# TestImportBoundary
# ---------------------------------------------------------------------------

class TestImportBoundary:
    """agentic_core extractor must not import from apps_rg.*"""

    def test_extractor_has_no_apps_rg_import(self):
        extractor_path = (
            _REPO_ROOT
            / "agentic_core" / "runtime" / "c0" / "evidence_metrics_extractor.py"
        )
        source = extractor_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module:
                    assert not node.module.startswith("apps_rg"), (
                        f"agentic_core extractor must not import apps_rg.*: "
                        f"found 'from {node.module} import ...' at line {node.lineno}"
                    )
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        assert not alias.name.startswith("apps_rg"), (
                            f"agentic_core extractor must not import apps_rg.*: "
                            f"found 'import {alias.name}' at line {node.lineno}"
                        )

    def test_writer_is_not_in_agentic_core(self):
        writer_path = (
            _REPO_ROOT
            / "apps_rg" / "runtime" / "bindings" / "c0_metrics_writer.py"
        )
        assert writer_path.exists(), "Writer must exist in apps_rg, not agentic_core"
        agentic_core_writer = (
            _REPO_ROOT
            / "agentic_core" / "runtime" / "bindings" / "c0_metrics_writer.py"
        )
        assert not agentic_core_writer.exists(), "Writer must NOT exist in agentic_core"
