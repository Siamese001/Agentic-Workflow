"""Wave 5 ADG testing-hotspots — apps_eval deterministic graders pure surface.

Substitution note: the plan listed ``apps_eval/validators/eval_gate_validator.py``
which does not exist. The nearest untested equivalent — deterministic pass/fail
grading logic — is ``apps_eval/graders/deterministic/core.py``. Each grader is a
pure ``(fixture, snapshot) -> GraderFinding`` transform; this module exercises
the helper functions, the default registry, and every grader's pass/fail branch
with real (constructed) snapshots and fixtures. No mocks.
"""

from __future__ import annotations

import pytest

from apps_eval.contracts import AppOutputSnapshot, EvalFixture, EvalScenario
from apps_eval.graders.deterministic.core import (
    ArtifactPresenceGrader,
    DeterminismGrader,
    EscalationGrader,
    ForbiddenContentGrader,
    GroundedClaimGrader,
    LengthBoundsGrader,
    ProvenanceGrader,
    SchemaGrader,
    SectionStructureGrader,
    SideEffectGrader,
    X3DispositionGrader,
    _canonical_hash,
    _contains_term,
    _text_blob,
    build_default_graders,
)


def _fixture(expected: dict) -> EvalFixture:
    scenario = EvalScenario(
        scenario_id="sc1",
        suite_id="su",
        app_id="apps_rg",
        description="d",
        fixture_path="/x",
        graders=(),
        rubric_id="r1",
    )
    return EvalFixture(
        scenario=scenario,
        input_dir="i",
        expected_dir="e",
        snapshot_path="p",
        artifacts_dir="a",
        expected=expected,
    )


def _snapshot(**overrides) -> AppOutputSnapshot:
    base = dict(app_id="apps_rg", scenario_id="sc1", x3_disposition="X3A", output={})
    base.update(overrides)
    return AppOutputSnapshot(**base)


class TestHelpers:
    def test_text_blob_handles_nested(self):
        blob = _text_blob({"a": ["x", "y"], "b": {"c": "z"}})
        assert "x" in blob and "y" in blob and "z" in blob

    def test_text_blob_scalar(self):
        assert _text_blob(42) == "42"

    @pytest.mark.parametrize(
        "blob,term,expected",
        [
            ("the cat sat", "cat", True),
            ("category here", "cat", False),  # word-boundary, not substring
            ("a phrase match here", "phrase match", True),
            ("nothing", "", False),
        ],
    )
    def test_contains_term(self, blob, term, expected):
        assert _contains_term(blob, term) is expected

    def test_canonical_hash_ignores_existing_hash_field(self):
        a = _snapshot(output={"k": 1}, deterministic_hash="")
        b = _snapshot(output={"k": 1}, deterministic_hash="stale")
        assert _canonical_hash(a) == _canonical_hash(b)

    def test_canonical_hash_changes_with_payload(self):
        assert _canonical_hash(_snapshot(output={"k": 1})) != _canonical_hash(
            _snapshot(output={"k": 2})
        )


class TestDefaultRegistry:
    def test_build_default_graders_count_and_unique_ids(self):
        graders = build_default_graders()
        assert len(graders) == 11
        ids = [g.grader_id for g in graders]
        assert len(ids) == len(set(ids))

    def test_length_bounds_is_warn_severity(self):
        assert LengthBoundsGrader().severity == "warn"

    def test_other_graders_default_block(self):
        assert SchemaGrader().severity == "block"


class TestSchemaGrader:
    def test_pass_when_keys_present(self):
        f = SchemaGrader().grade(
            _fixture({"required_output_keys": ["k1"]}), _snapshot(output={"k1": 1})
        )
        assert f.passed is True
        assert f.score == 1.0

    def test_fail_when_key_missing(self):
        f = SchemaGrader().grade(
            _fixture({"required_output_keys": ["k1", "k2"]}), _snapshot(output={"k1": 1})
        )
        assert f.passed is False
        assert f.evidence["missing"] == ["k2"]
        assert f.score == 0.0


class TestArtifactPresenceGrader:
    def test_pass(self):
        f = ArtifactPresenceGrader().grade(
            _fixture({"required_artifacts": ["a.json"]}),
            _snapshot(artifacts=["a.json", "b.json"]),
        )
        assert f.passed is True

    def test_fail(self):
        f = ArtifactPresenceGrader().grade(
            _fixture({"required_artifacts": ["missing.json"]}), _snapshot(artifacts=[])
        )
        assert f.passed is False
        assert f.evidence["missing"] == ["missing.json"]


class TestX3DispositionGrader:
    def test_match(self):
        f = X3DispositionGrader().grade(
            _fixture({"expected_x3": "X3A"}), _snapshot(x3_disposition="X3A")
        )
        assert f.passed is True

    def test_mismatch(self):
        f = X3DispositionGrader().grade(
            _fixture({"expected_x3": "X3A"}), _snapshot(x3_disposition="X3B")
        )
        assert f.passed is False

    def test_empty_expected_fails(self):
        f = X3DispositionGrader().grade(_fixture({}), _snapshot(x3_disposition="X3A"))
        assert f.passed is False


class TestForbiddenContentGrader:
    def test_clean_passes(self):
        f = ForbiddenContentGrader().grade(
            _fixture({"forbidden_terms": ["badword"]}),
            _snapshot(output={"text": "all good here"}),
        )
        assert f.passed is True

    def test_hit_fails(self):
        f = ForbiddenContentGrader().grade(
            _fixture({"forbidden_terms": ["badword"]}),
            _snapshot(output={"text": "contains badword inside"}),
        )
        assert f.passed is False
        assert "badword" in f.evidence["hits"]


class TestGroundedClaimGrader:
    def test_grounding_not_required(self):
        f = GroundedClaimGrader().grade(
            _fixture({"grounded_claims_required": False}), _snapshot()
        )
        assert f.passed is True

    def test_all_claims_grounded(self):
        f = GroundedClaimGrader().grade(
            _fixture({}),
            _snapshot(claims=[{"id": "c1", "supported": True, "source_ids": ["s1"]}]),
        )
        assert f.passed is True

    def test_ungrounded_claim_fails(self):
        f = GroundedClaimGrader().grade(
            _fixture({}),
            _snapshot(claims=[{"id": "c1", "supported": False, "source_ids": []}]),
        )
        assert f.passed is False
        assert "c1" in f.evidence["bad_claims"]

    def test_no_claims_fails_when_required(self):
        f = GroundedClaimGrader().grade(_fixture({}), _snapshot(claims=[]))
        assert f.passed is False


class TestProvenanceGrader:
    def test_pass(self):
        f = ProvenanceGrader().grade(
            _fixture({"required_provenance": ["e1"]}),
            _snapshot(provenance={"evidence_refs": ["e1", "e2"]}),
        )
        assert f.passed is True

    def test_missing_provenance_fails(self):
        f = ProvenanceGrader().grade(
            _fixture({"required_provenance": ["e9"]}),
            _snapshot(provenance={"evidence_refs": ["e1"]}),
        )
        assert f.passed is False


class TestSectionStructureGrader:
    def test_sections_dict_present(self):
        f = SectionStructureGrader().grade(
            _fixture({"required_sections": ["intro"]}),
            _snapshot(output={"sections": {"intro": "..."}}),
        )
        assert f.passed is True

    def test_missing_section_fails(self):
        f = SectionStructureGrader().grade(
            _fixture({"required_sections": ["conclusion"]}),
            _snapshot(output={"sections": {"intro": "..."}}),
        )
        assert f.passed is False
        assert "conclusion" in f.evidence["missing"]


class TestLengthBoundsGrader:
    def test_within_bounds(self):
        f = LengthBoundsGrader().grade(
            _fixture({"length_bounds": {"min_words": 1, "max_words": 10}}),
            _snapshot(output={"text": "one two three"}),
        )
        assert f.passed is True
        assert f.evidence["word_count"] == 3

    def test_below_min_fails(self):
        f = LengthBoundsGrader().grade(
            _fixture({"length_bounds": {"min_words": 5, "max_words": 10}}),
            _snapshot(output={"text": "too short"}),
        )
        assert f.passed is False


class TestSideEffectGrader:
    def test_clean_passes(self):
        f = SideEffectGrader().grade(_fixture({}), _snapshot(side_effects={}))
        assert f.passed is True

    def test_writes_fail_when_not_allowed(self):
        f = SideEffectGrader().grade(
            _fixture({"allow_side_effects": False}),
            _snapshot(side_effects={"writes": ["w1"]}),
        )
        assert f.passed is False

    def test_writes_allowed_when_permitted(self):
        f = SideEffectGrader().grade(
            _fixture({"allow_side_effects": True}),
            _snapshot(side_effects={"writes": ["w1"], "product_state_mutated": True}),
        )
        assert f.passed is True


class TestEscalationGrader:
    def test_escalation_required_and_present(self):
        f = EscalationGrader().grade(
            _fixture({"escalation_required": True}),
            _snapshot(x3_disposition="X3B_ESCALATE_HITL"),
        )
        assert f.passed is True

    def test_escalation_required_but_absent(self):
        f = EscalationGrader().grade(
            _fixture({"escalation_required": True}), _snapshot(x3_disposition="X3A")
        )
        assert f.passed is False

    def test_no_escalation_required_and_none(self):
        f = EscalationGrader().grade(
            _fixture({"escalation_required": False}), _snapshot(x3_disposition="X3A")
        )
        assert f.passed is True


class TestDeterminismGrader:
    def test_matching_hash_passes(self):
        snap = _snapshot(output={"k": 1})
        snap_with_hash = AppOutputSnapshot.from_dict(
            {**snap.to_dict(), "deterministic_hash": _canonical_hash(snap)}
        )
        f = DeterminismGrader().grade(_fixture({}), snap_with_hash)
        assert f.passed is True

    def test_mismatched_hash_fails(self):
        f = DeterminismGrader().grade(
            _fixture({}), _snapshot(output={"k": 1}, deterministic_hash="wrong")
        )
        assert f.passed is False

    def test_empty_hash_fails(self):
        f = DeterminismGrader().grade(_fixture({}), _snapshot(deterministic_hash=""))
        assert f.passed is False
