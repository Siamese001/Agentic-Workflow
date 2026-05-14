"""W5 tests: apps_rg briefing path identity proof.

Covers:
- All four modes produce distinct retrieval_mode in c0_metrics artifact.
- company_brief_provenance is preserved for UPLOADED_BRIEFING and
  DELEGATED_APPS_RESEARCH modes.
- NONE path emits explicit NONE, not silent success or UNKNOWN.
- retrieval_mode and briefing_source_type are never inferred from loose strings.
- Delegated apps_research evidence treated as input, not apps_rg-owned research.
- No briefing-mode logic present in agentic_core.
- W1-W4 tests remain importable (regression guard).
- assert_mode_is_canonical rejects non-canonical values.
"""
from __future__ import annotations

import ast
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
)
from apps_rg.runtime.bindings.briefing_mode_classifier import (
    BRIEFING_MODE_DELEGATED,
    BRIEFING_MODE_NATIVE_C0,
    BRIEFING_MODE_NONE,
    BRIEFING_MODE_UPLOADED,
    BriefingModeDecision,
    _VALID_BRIEFING_MODES,
    assert_mode_is_canonical,
    classify_briefing_mode,
)
from apps_rg.runtime.bindings.c0_metrics_writer import (
    SCHEMA_VERSION,
    build_c0_metrics,
    write_c0_metrics,
)

_REPO_ROOT = Path(__file__).parents[2]
_CERT_REF = "c0-apps-rg-w5-test"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fec(run_id: str = "run_w5", support_status: str = "PASS") -> FinalEvidenceContract:
    return FinalEvidenceContract(
        request_id=run_id,
        run_id=run_id,
        app_id="apps_rg",
        trace_id=run_id,
        evidence_items=(
            EvidenceItem(source="jd_payload:jd_text", content="SWE role"),
            EvidenceItem(source="resume_payload:resume_text", content="10y Python"),
        ),
        retrieval_sources=("jd_payload:jd_text", "resume_payload:resume_text"),
        support_target_met=True,
        support_status=support_status,
        l5_certification_ref=_CERT_REF,
    )


def _payload_uploaded(brief_path: str = "/tmp/brief.json") -> dict[str, Any]:
    return {
        "jd_payload": {"jd_text": "SWE role"},
        "resume_payload": {"resume_text": "10y Python"},
        "policy_refs": {
            "manual_brief_path": brief_path,
            "brief_fetched_at": "2026-05-01T00:00:00Z",
            "brief_freshness_ttl_days": 7,
        },
    }


def _payload_delegated() -> dict[str, Any]:
    return {
        "jd_payload": {"jd_text": "SWE role"},
        "resume_payload": {"resume_text": "10y Python"},
        "research_via": "apps_research",
        "briefing": {
            "research_via": "apps_research",
            "fetched_at": "2026-05-02T00:00:00Z",
            "freshness_ttl_days": 3,
        },
        "policy_refs": {},
    }


def _payload_native_c0() -> dict[str, Any]:
    return {
        "jd_payload": {"jd_text": "SWE role"},
        "resume_payload": {"resume_text": "10y Python"},
        "policy_refs": {},
    }


def _payload_none() -> dict[str, Any]:
    return {
        "jd_payload": {"jd_text": "SWE role"},
        "resume_payload": {"resume_text": "10y Python"},
        "policy_refs": {},
    }


# ---------------------------------------------------------------------------
# TestBriefingModeClassifier
# ---------------------------------------------------------------------------

class TestBriefingModeClassifier:
    """Unit tests for classify_briefing_mode — strict precedence, no loose inference."""

    def test_uploaded_briefing_when_manual_brief_path_present(self):
        decision = classify_briefing_mode(
            app_payload=_payload_uploaded("/docs/brief.json"),
            chroma_path_resolved=None,
        )
        assert decision.retrieval_mode == BRIEFING_MODE_UPLOADED
        assert decision.briefing_source_type == BRIEFING_MODE_UPLOADED

    def test_uploaded_briefing_overrides_chroma_path(self):
        """manual_brief_path takes precedence over chroma_path (precedence order)."""
        decision = classify_briefing_mode(
            app_payload=_payload_uploaded("/docs/brief.json"),
            chroma_path_resolved="/data/chroma",
        )
        assert decision.retrieval_mode == BRIEFING_MODE_UPLOADED

    def test_uploaded_briefing_overrides_research_via(self):
        """manual_brief_path takes precedence over research_via."""
        payload = _payload_delegated()
        payload["policy_refs"]["manual_brief_path"] = "/docs/brief.json"
        decision = classify_briefing_mode(app_payload=payload, chroma_path_resolved=None)
        assert decision.retrieval_mode == BRIEFING_MODE_UPLOADED

    def test_delegated_when_research_via_apps_research(self):
        decision = classify_briefing_mode(
            app_payload=_payload_delegated(),
            chroma_path_resolved=None,
        )
        assert decision.retrieval_mode == BRIEFING_MODE_DELEGATED

    def test_delegated_from_caller_override(self):
        """research_via parameter overrides missing payload value."""
        decision = classify_briefing_mode(
            app_payload=_payload_none(),
            chroma_path_resolved=None,
            research_via="apps_research",
        )
        assert decision.retrieval_mode == BRIEFING_MODE_DELEGATED

    def test_delegated_overrides_chroma_path(self):
        """research_via takes precedence over chroma_path."""
        decision = classify_briefing_mode(
            app_payload=_payload_delegated(),
            chroma_path_resolved="/data/chroma",
        )
        assert decision.retrieval_mode == BRIEFING_MODE_DELEGATED

    def test_native_c0_when_chroma_path_present(self):
        decision = classify_briefing_mode(
            app_payload=_payload_native_c0(),
            chroma_path_resolved="/data/chroma",
        )
        assert decision.retrieval_mode == BRIEFING_MODE_NATIVE_C0

    def test_none_mode_when_no_brief_no_chroma(self):
        decision = classify_briefing_mode(
            app_payload=_payload_none(),
            chroma_path_resolved=None,
        )
        assert decision.retrieval_mode == BRIEFING_MODE_NONE

    def test_none_mode_explicit_not_unknown(self):
        """NONE must be explicit — not coerced to UNKNOWN silently."""
        decision = classify_briefing_mode(
            app_payload=_payload_none(),
            chroma_path_resolved=None,
        )
        assert decision.retrieval_mode == BRIEFING_MODE_NONE
        assert decision.retrieval_mode != "UNKNOWN"

    def test_briefing_source_type_matches_retrieval_mode(self):
        """artifact field alias must always match retrieval_mode."""
        for payload, chroma in [
            (_payload_uploaded(), None),
            (_payload_delegated(), None),
            (_payload_native_c0(), "/data/chroma"),
            (_payload_none(), None),
        ]:
            d = classify_briefing_mode(payload, chroma)
            assert d.briefing_source_type == d.retrieval_mode, (
                f"briefing_source_type mismatch for mode={d.retrieval_mode}"
            )

    def test_all_modes_are_canonical(self):
        for payload, chroma, via in [
            (_payload_uploaded(), None, None),
            (_payload_delegated(), None, None),
            (_payload_native_c0(), "/data/chroma", None),
            (_payload_none(), None, None),
        ]:
            d = classify_briefing_mode(payload, chroma, via)
            assert_mode_is_canonical(d.retrieval_mode)  # must not raise


# ---------------------------------------------------------------------------
# TestProvenancePreservation
# ---------------------------------------------------------------------------

class TestProvenancePreservation:
    """company_brief_provenance is preserved for uploaded/delegated, None otherwise."""

    def test_uploaded_provenance_has_source_and_path(self):
        decision = classify_briefing_mode(
            app_payload=_payload_uploaded("/docs/brief.json"),
            chroma_path_resolved=None,
        )
        assert decision.company_brief_provenance is not None
        assert decision.company_brief_provenance["source"] == "uploaded_brief"
        assert decision.company_brief_provenance["path"] == "/docs/brief.json"

    def test_uploaded_provenance_has_fetched_at(self):
        decision = classify_briefing_mode(
            app_payload=_payload_uploaded(),
            chroma_path_resolved=None,
        )
        prov = decision.company_brief_provenance
        assert prov is not None
        assert "fetched_at" in prov

    def test_uploaded_provenance_has_freshness_ttl(self):
        decision = classify_briefing_mode(
            app_payload=_payload_uploaded(),
            chroma_path_resolved=None,
        )
        prov = decision.company_brief_provenance
        assert prov is not None
        assert prov.get("freshness_ttl_days") == 7

    def test_delegated_provenance_marks_delegate(self):
        decision = classify_briefing_mode(
            app_payload=_payload_delegated(),
            chroma_path_resolved=None,
        )
        prov = decision.company_brief_provenance
        assert prov is not None
        assert prov["source"] == "delegated_apps_research"
        assert prov["delegate"] == "apps_research"

    def test_delegated_provenance_not_apps_rg_owned(self):
        """Delegated evidence is input, not apps_rg-owned. Source must say delegated."""
        decision = classify_briefing_mode(
            app_payload=_payload_delegated(),
            chroma_path_resolved=None,
        )
        prov = decision.company_brief_provenance
        assert prov is not None
        assert prov["source"] != "apps_rg_research"
        assert prov["source"] == "delegated_apps_research"

    def test_native_c0_provenance_is_none(self):
        decision = classify_briefing_mode(
            app_payload=_payload_native_c0(),
            chroma_path_resolved="/data/chroma",
        )
        assert decision.company_brief_provenance is None

    def test_none_mode_provenance_is_none(self):
        decision = classify_briefing_mode(
            app_payload=_payload_none(),
            chroma_path_resolved=None,
        )
        assert decision.company_brief_provenance is None


# ---------------------------------------------------------------------------
# TestFourModesInArtifact
# ---------------------------------------------------------------------------

class TestFourModesInArtifact:
    """Each mode produces distinct retrieval_mode in c0_metrics artifact."""

    @pytest.mark.parametrize("mode,expected", [
        (BRIEFING_MODE_UPLOADED, "UPLOADED_BRIEFING"),
        (BRIEFING_MODE_DELEGATED, "DELEGATED_APPS_RESEARCH"),
        (BRIEFING_MODE_NATIVE_C0, "NATIVE_C0"),
        (BRIEFING_MODE_NONE, "NONE"),
    ])
    def test_mode_preserved_in_build_c0_metrics(self, mode, expected):
        fec = _make_fec()
        result = build_c0_metrics(
            fec=fec,
            run_id="run_w5",
            route_id="R0",
            retrieval_mode=mode,
            briefing_source_type=mode,
        )
        assert result["retrieval_mode"] == expected
        assert result["schema_version"] == SCHEMA_VERSION

    def test_all_four_modes_produce_distinct_artifacts(self):
        fec = _make_fec()
        modes = [
            BRIEFING_MODE_UPLOADED,
            BRIEFING_MODE_DELEGATED,
            BRIEFING_MODE_NATIVE_C0,
            BRIEFING_MODE_NONE,
        ]
        seen_modes = set()
        for mode in modes:
            result = build_c0_metrics(fec=fec, run_id="r", route_id="R0", retrieval_mode=mode)
            seen_modes.add(result["retrieval_mode"])
        assert len(seen_modes) == 4, f"Expected 4 distinct modes, got {seen_modes}"

    def test_none_mode_artifact_not_silent_success(self):
        """NONE mode must emit explicit NONE, not coerce to UNKNOWN or PASS."""
        fec = _make_fec(support_status="EMPTY")
        result = build_c0_metrics(
            fec=fec,
            run_id="r",
            route_id="R0",
            retrieval_mode=BRIEFING_MODE_NONE,
            briefing_source_type=BRIEFING_MODE_NONE,
        )
        assert result["retrieval_mode"] == "NONE"
        # support_status must reflect actual evidence state, not inferred
        assert result["support_status"] in ("EMPTY", "UNKNOWN", "BLOCKED")

    def test_uploaded_mode_preserves_provenance_in_artifact(self):
        provenance = {"source": "uploaded_brief", "path": "/docs/brief.json", "fetched_at": "2026-05-01"}
        fec = _make_fec()
        result = build_c0_metrics(
            fec=fec,
            run_id="r",
            route_id="R0",
            retrieval_mode=BRIEFING_MODE_UPLOADED,
            briefing_source_type=BRIEFING_MODE_UPLOADED,
            company_brief_provenance=provenance,
        )
        assert result["company_brief_provenance"] == provenance

    def test_delegated_mode_preserves_provenance_in_artifact(self):
        provenance = {"source": "delegated_apps_research", "delegate": "apps_research"}
        fec = _make_fec()
        result = build_c0_metrics(
            fec=fec,
            run_id="r",
            route_id="R0",
            retrieval_mode=BRIEFING_MODE_DELEGATED,
            company_brief_provenance=provenance,
        )
        assert result["company_brief_provenance"] == provenance

    def test_native_c0_provenance_null_in_artifact(self):
        fec = _make_fec()
        result = build_c0_metrics(
            fec=fec,
            run_id="r",
            route_id="R0",
            retrieval_mode=BRIEFING_MODE_NATIVE_C0,
            company_brief_provenance=None,
        )
        assert result["company_brief_provenance"] is None

    def test_none_mode_provenance_null_in_artifact(self):
        fec = _make_fec()
        result = build_c0_metrics(
            fec=fec,
            run_id="r",
            route_id="R0",
            retrieval_mode=BRIEFING_MODE_NONE,
            company_brief_provenance=None,
        )
        assert result["company_brief_provenance"] is None


# ---------------------------------------------------------------------------
# TestWritePathPerMode
# ---------------------------------------------------------------------------

class TestWritePathPerMode:
    """c0_metrics.json written to correct run dir for every mode."""

    def _write_and_read(self, mode: str, run_id: str) -> dict[str, Any]:
        fec = _make_fec(run_id=run_id)
        with tempfile.TemporaryDirectory() as tmpdir:
            runs_root = Path(tmpdir)
            path = write_c0_metrics(
                fec=fec,
                run_id=run_id,
                route_id="R0",
                retrieval_mode=mode,
                briefing_source_type=mode,
                runs_root=runs_root,
            )
            assert path is not None, f"write_c0_metrics returned None for mode={mode}"
            expected = runs_root / run_id / "c0_metrics.json"
            assert path == expected, f"path={path} expected={expected}"
            return json.loads(path.read_text(encoding="utf-8"))

    @pytest.mark.parametrize("mode", [
        BRIEFING_MODE_UPLOADED,
        BRIEFING_MODE_DELEGATED,
        BRIEFING_MODE_NATIVE_C0,
        BRIEFING_MODE_NONE,
    ])
    def test_artifact_written_to_correct_run_dir(self, mode):
        data = self._write_and_read(mode, f"run_{mode.lower()}")
        assert data["retrieval_mode"] == mode
        assert data["run_id"] == f"run_{mode.lower()}"
        assert data["schema_version"] == SCHEMA_VERSION

    def test_none_mode_artifact_has_explicit_none_not_unknown(self):
        data = self._write_and_read(BRIEFING_MODE_NONE, "run_none_explicit")
        assert data["retrieval_mode"] == "NONE"

    def test_uploaded_mode_artifact_roundtrip(self):
        fec = _make_fec(run_id="run_up")
        provenance = {"source": "uploaded_brief", "path": "/tmp/brief.json"}
        with tempfile.TemporaryDirectory() as tmpdir:
            path = write_c0_metrics(
                fec=fec,
                run_id="run_up",
                route_id="R1",
                retrieval_mode=BRIEFING_MODE_UPLOADED,
                briefing_source_type=BRIEFING_MODE_UPLOADED,
                company_brief_provenance=provenance,
                runs_root=Path(tmpdir),
            )
            assert path is not None
            data = json.loads(path.read_text(encoding="utf-8"))
        assert data["retrieval_mode"] == "UPLOADED_BRIEFING"
        assert data["company_brief_provenance"] == provenance

    def test_run_id_in_path(self):
        fec = _make_fec(run_id="my_run_abc")
        with tempfile.TemporaryDirectory() as tmpdir:
            path = write_c0_metrics(
                fec=fec,
                run_id="my_run_abc",
                route_id="R0",
                retrieval_mode=BRIEFING_MODE_NONE,
                runs_root=Path(tmpdir),
            )
        assert path is not None
        assert "my_run_abc" in str(path)


# ---------------------------------------------------------------------------
# TestCanonicalModeEnforcement
# ---------------------------------------------------------------------------

class TestCanonicalModeEnforcement:
    """retrieval_mode must be one of the four exact values."""

    def test_valid_modes_set_contains_exactly_four(self):
        assert len(_VALID_BRIEFING_MODES) == 4
        assert _VALID_BRIEFING_MODES == {
            "UPLOADED_BRIEFING", "DELEGATED_APPS_RESEARCH", "NATIVE_C0", "NONE"
        }

    @pytest.mark.parametrize("mode", [
        "UPLOADED_BRIEFING", "DELEGATED_APPS_RESEARCH", "NATIVE_C0", "NONE"
    ])
    def test_canonical_modes_pass_assert(self, mode):
        assert_mode_is_canonical(mode)  # must not raise

    @pytest.mark.parametrize("bad_mode", [
        "UNKNOWN", "PARTIAL", "uploaded_briefing", "native", "none", "",
        "APPS_RESEARCH", "DELEGATED", "BRIEF", "MANUAL"
    ])
    def test_non_canonical_modes_rejected(self, bad_mode):
        with pytest.raises(ValueError, match="Non-canonical briefing mode"):
            assert_mode_is_canonical(bad_mode)

    def test_loose_string_inference_prevented(self):
        """Classifier never returns a mode that fails canonical assertion."""
        test_cases = [
            (_payload_uploaded(), None, None),
            (_payload_delegated(), None, None),
            (_payload_native_c0(), "/data/chroma", None),
            (_payload_none(), None, None),
        ]
        for payload, chroma, via in test_cases:
            d = classify_briefing_mode(payload, chroma, via)
            # This should never raise — proves only canonical modes are returned
            assert_mode_is_canonical(d.retrieval_mode)
            assert_mode_is_canonical(d.briefing_source_type)

    def test_build_c0_metrics_coerces_unknown_mode(self):
        """build_c0_metrics coerces non-canonical string to UNKNOWN (W3 coercer)."""
        fec = _make_fec()
        result = build_c0_metrics(
            fec=fec, run_id="r", route_id="R0", retrieval_mode="some_garbage_string"
        )
        assert result["retrieval_mode"] == "UNKNOWN"


# ---------------------------------------------------------------------------
# TestDelegatedEvidenceOwnership
# ---------------------------------------------------------------------------

class TestDelegatedEvidenceOwnership:
    """Delegated apps_research evidence treated as input, not apps_rg-owned research."""

    def test_delegated_source_is_delegate_not_apps_rg(self):
        decision = classify_briefing_mode(
            app_payload=_payload_delegated(),
            chroma_path_resolved=None,
        )
        prov = decision.company_brief_provenance
        assert prov is not None
        assert "apps_research" in prov["delegate"]
        # Must NOT claim ownership
        assert prov.get("owned_by") != "apps_rg"

    def test_delegated_mode_classified_from_signal_not_inferred(self):
        decision = classify_briefing_mode(
            app_payload=_payload_delegated(),
            chroma_path_resolved=None,
        )
        assert "apps_research" in decision.classified_from.lower()

    def test_delegated_without_chroma_is_not_native_c0(self):
        """Delegated must not fall through to NATIVE_C0 even if chroma is present."""
        decision = classify_briefing_mode(
            app_payload=_payload_delegated(),
            chroma_path_resolved="/data/chroma",
        )
        assert decision.retrieval_mode == BRIEFING_MODE_DELEGATED
        assert decision.retrieval_mode != BRIEFING_MODE_NATIVE_C0


# ---------------------------------------------------------------------------
# TestAgenticCoreNoBriefingModeLogic
# ---------------------------------------------------------------------------

class TestAgenticCoreNoBriefingModeLogic:
    """No briefing-mode logic may enter agentic_core."""

    def _get_agentic_core_py_files(self) -> list[Path]:
        agentic_core = _REPO_ROOT / "agentic_core"
        return list(agentic_core.rglob("*.py"))

    def test_briefing_mode_logic_not_in_agentic_core(self):
        """W5 classifier logic must not appear in agentic_core.

        The string constants UPLOADED_BRIEFING / DELEGATED_APPS_RESEARCH exist
        legitimately in agentic_core's generic delegation contract vocabulary
        (apps_research_runtime_package.py, generic_payload_validator.py) — those
        are pre-existing generic enum values, not apps_rg briefing-mode logic.

        We check for the W5 *logic* identifiers that must stay in apps_rg:
        the classifier function, dataclass, and module name.
        """
        forbidden = [
            "classify_briefing_mode",
            "BriefingModeDecision",
            "briefing_mode_classifier",
            "assert_mode_is_canonical",
        ]
        violations = []
        for path in self._get_agentic_core_py_files():
            text = path.read_text(encoding="utf-8")
            for literal in forbidden:
                if literal in text:
                    rel = path.relative_to(_REPO_ROOT)
                    violations.append(f"{rel}: contains '{literal}'")
        assert not violations, (
            "agentic_core contains W5 apps_rg briefing-mode logic (boundary violation):\n"
            + "\n".join(violations)
        )

    def test_briefing_mode_classifier_has_no_agentic_core_imports(self):
        """briefing_mode_classifier.py must not import from agentic_core."""
        classifier_path = (
            _REPO_ROOT
            / "apps_rg"
            / "runtime"
            / "bindings"
            / "briefing_mode_classifier.py"
        )
        tree = ast.parse(classifier_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module:
                    assert not node.module.startswith("agentic_core"), (
                        f"briefing_mode_classifier imports from agentic_core: {node.module}"
                    )


# ---------------------------------------------------------------------------
# TestRegressionGuard
# ---------------------------------------------------------------------------

class TestRegressionGuard:
    """W1-W4 modules remain importable — zero regressions."""

    @pytest.mark.parametrize("modpath", [
        "tests._apps_contract.test_rg_w1_retrieval_requirements_profile",
        "tests._apps_contract.test_rg_w2_c0_metrics_extractor",
        "tests._apps_contract.test_rg_w3_c0_metrics_artifact",
        "tests._apps_contract.test_rg_w4_exit_binding",
    ])
    def test_prior_wave_module_importable(self, modpath):
        import importlib
        mod = importlib.import_module(modpath)
        assert mod is not None

    def test_briefing_mode_classifier_importable(self):
        from apps_rg.runtime.bindings import briefing_mode_classifier  # noqa: F401
        assert briefing_mode_classifier is not None

    def test_c0_metrics_writer_importable(self):
        from apps_rg.runtime.bindings import c0_metrics_writer  # noqa: F401
        assert c0_metrics_writer is not None

    def test_c0_binding_importable(self):
        from apps_rg.runtime.bindings import c0_binding  # noqa: F401
        assert c0_binding is not None
