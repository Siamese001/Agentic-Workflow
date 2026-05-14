"""W1 acceptance tests — apps_rg retrieval requirements profile.

Validates that:
1. The profile YAML loads and passes structural validation.
2. Required inputs (JD, candidate resume, master resume) are declared.
3. All four briefing modes are declared (UPLOADED_BRIEFING, DELEGATED_APPS_RESEARCH,
   NATIVE_C0, NONE) and exactly those four.
4. _NORMATIVE_SOURCE_CLASSES values (candidate_profile, project_evidence,
   approved_examples, rubrics, governance_docs, receipts) are all present in
   required_source_classes.
5. The profile loader returns the profile-derived tuple from c0_binding.
6. The profile does NOT reference agentic_core (ownership boundary scan).
7. The retrieval_requirements.py module does NOT import from agentic_core.
8. The profile file does NOT contain retrieval, scoring, or artifact-writing logic.
9. get_normative_source_classes() matches the hardcoded fallback in c0_binding.

Plan: apps-rg-retrieval-metrics-ownership-and-c0-evidence-plan W1
"""
from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Fixtures / module-level setup
# ---------------------------------------------------------------------------

PROFILE_PATH = (
    Path(__file__).parents[2]
    / "apps_rg"
    / "config"
    / "domain_contract"
    / "retrieval_requirements_profile.resume_generation.v1.yaml"
)

LOADER_MODULE = "apps_rg.runtime.profiles.retrieval_requirements"
C0_BINDING_MODULE = "apps_rg.runtime.bindings.c0_binding"

_EXPECTED_BRIEFING_MODES: frozenset[str] = frozenset({
    "UPLOADED_BRIEFING",
    "DELEGATED_APPS_RESEARCH",
    "NATIVE_C0",
    "NONE",
})

_EXPECTED_NORMATIVE_CLASSES: frozenset[str] = frozenset({
    "candidate_profile",
    "project_evidence",
    "approved_examples",
    "rubrics",
    "governance_docs",
    "receipts",
})

_EXPECTED_REQUIRED_INPUTS: frozenset[str] = frozenset({
    "jd_payload",
    "resume_payload",
    "master_resume",
})


@pytest.fixture(scope="module")
def profile() -> dict:
    assert PROFILE_PATH.exists(), f"Profile file not found: {PROFILE_PATH}"
    with PROFILE_PATH.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), "Profile must be a YAML mapping"
    return data


@pytest.fixture(scope="module")
def loader():
    """Import the retrieval_requirements loader module."""
    # Invalidate lru_cache between test runs in the same process.
    mod = importlib.import_module(LOADER_MODULE)
    mod.load_retrieval_requirements_profile.cache_clear()
    return mod


# ---------------------------------------------------------------------------
# T1: Profile structural validation
# ---------------------------------------------------------------------------

class TestProfileStructure:
    def test_profile_loads_without_error(self, profile):
        assert profile  # truthy non-empty dict

    def test_required_top_level_keys_present(self, profile):
        required_keys = {
            "profile_id",
            "app_id",
            "task_class",
            "version",
            "status",
            "required_source_classes",
            "optional_source_classes",
            "support_target",
            "briefing_source_types",
            "default_briefing_source_type",
            "company_brief_provenance_policy",
            "freshness_profile",
            "citation_requirement",
            "jd_requirement_policy",
            "candidate_fact_policy",
            "minimum_grounding_thresholds",
            "overfit_threshold",
        }
        missing = required_keys - profile.keys()
        assert not missing, f"Profile missing keys: {sorted(missing)}"

    def test_profile_id_format(self, profile):
        assert profile["profile_id"] == "rrp::apps_rg::resume_generation::v1"

    def test_app_id_is_apps_rg(self, profile):
        assert profile["app_id"] == "apps_rg"

    def test_task_class_is_resume_generation(self, profile):
        assert profile["task_class"] == "resume_generation"

    def test_status_is_active(self, profile):
        assert profile["status"] == "active"


# ---------------------------------------------------------------------------
# T2: Required evidence inputs declared
# ---------------------------------------------------------------------------

class TestRequiredInputsDeclaration:
    def test_jd_payload_in_required_inputs(self, profile):
        required = set(profile["support_target"].get("required_inputs", []))
        assert "jd_payload" in required, "jd_payload must be in support_target.required_inputs"

    def test_resume_payload_in_required_inputs(self, profile):
        required = set(profile["support_target"].get("required_inputs", []))
        assert "resume_payload" in required

    def test_master_resume_in_required_inputs(self, profile):
        required = set(profile["support_target"].get("required_inputs", []))
        assert "master_resume" in required

    def test_all_expected_required_inputs_declared(self, profile):
        declared = set(profile["support_target"].get("required_inputs", []))
        missing = _EXPECTED_REQUIRED_INPUTS - declared
        assert not missing, f"Missing required inputs in support_target: {missing}"

    def test_briefing_is_optional_not_required(self, profile):
        optional = set(profile["support_target"].get("optional_inputs", []))
        required = set(profile["support_target"].get("required_inputs", []))
        assert "briefing" in optional, "briefing must be optional"
        assert "briefing" not in required, "briefing must NOT be required"

    def test_jd_requirement_policy_declares_required(self, profile):
        assert profile["jd_requirement_policy"]["required"] is True

    def test_candidate_fact_policy_declares_source_resume_required(self, profile):
        assert profile["candidate_fact_policy"]["source_resume_required"] is True

    def test_candidate_fact_policy_declares_master_resume_required(self, profile):
        assert profile["candidate_fact_policy"]["master_resume_required"] is True


# ---------------------------------------------------------------------------
# T3: Briefing mode taxonomy — exactly four modes, exact names
# ---------------------------------------------------------------------------

class TestBriefingModes:
    def test_exactly_four_briefing_source_types(self, profile):
        declared = set(profile["briefing_source_types"])
        assert declared == _EXPECTED_BRIEFING_MODES, (
            f"briefing_source_types mismatch.\n"
            f"  expected: {sorted(_EXPECTED_BRIEFING_MODES)}\n"
            f"  got:      {sorted(declared)}"
        )

    @pytest.mark.parametrize("mode", sorted(_EXPECTED_BRIEFING_MODES))
    def test_briefing_mode_present(self, profile, mode):
        assert mode in profile["briefing_source_types"]

    def test_default_briefing_source_type_is_valid(self, profile):
        default = profile["default_briefing_source_type"]
        assert default in _EXPECTED_BRIEFING_MODES, (
            f"default_briefing_source_type '{default}' not in declared modes"
        )

    def test_no_extra_briefing_modes(self, profile):
        declared = set(profile["briefing_source_types"])
        extras = declared - _EXPECTED_BRIEFING_MODES
        assert not extras, f"Unexpected briefing modes declared: {extras}"


# ---------------------------------------------------------------------------
# T4: Normative source classes match _NORMATIVE_SOURCE_CLASSES_HARDCODED
# ---------------------------------------------------------------------------

class TestNormativeSourceClasses:
    def test_all_normative_classes_in_required_source_classes(self, profile):
        declared = set(profile["required_source_classes"])
        missing = _EXPECTED_NORMATIVE_CLASSES - declared
        assert not missing, (
            f"required_source_classes missing classes that c0_binding.py "
            f"_NORMATIVE_SOURCE_CLASSES_HARDCODED declares: {missing}"
        )

    @pytest.mark.parametrize("cls", sorted(_EXPECTED_NORMATIVE_CLASSES))
    def test_normative_class_in_profile(self, profile, cls):
        assert cls in profile["required_source_classes"]

    def test_loader_get_normative_source_classes_returns_tuple(self, loader):
        result = loader.get_normative_source_classes()
        assert isinstance(result, tuple)

    def test_loader_normative_classes_match_expected(self, loader):
        result = set(loader.get_normative_source_classes())
        assert result == _EXPECTED_NORMATIVE_CLASSES, (
            f"Profile normative classes mismatch.\n"
            f"  expected: {sorted(_EXPECTED_NORMATIVE_CLASSES)}\n"
            f"  got:      {sorted(result)}"
        )

    def test_c0_binding_normative_classes_derived_from_profile(self, loader):
        """After import, c0_binding._NORMATIVE_SOURCE_CLASSES must match profile."""
        c0 = importlib.import_module(C0_BINDING_MODULE)
        profile_classes = set(loader.get_normative_source_classes())
        binding_classes = set(c0._NORMATIVE_SOURCE_CLASSES)
        assert binding_classes == profile_classes, (
            f"c0_binding._NORMATIVE_SOURCE_CLASSES does not match profile.\n"
            f"  profile:  {sorted(profile_classes)}\n"
            f"  binding:  {sorted(binding_classes)}"
        )

    def test_hardcoded_fallback_matches_profile(self, loader):
        """_NORMATIVE_SOURCE_CLASSES_HARDCODED must equal profile required classes.

        If this fails, the hardcoded fallback has drifted from the profile.
        """
        c0 = importlib.import_module(C0_BINDING_MODULE)
        profile_classes = set(loader.get_normative_source_classes())
        hardcoded = set(c0._NORMATIVE_SOURCE_CLASSES_HARDCODED)
        assert hardcoded == profile_classes, (
            f"_NORMATIVE_SOURCE_CLASSES_HARDCODED drifted from profile.\n"
            f"  profile:  {sorted(profile_classes)}\n"
            f"  hardcoded:{sorted(hardcoded)}"
        )


# ---------------------------------------------------------------------------
# T5: Loader module does not import from agentic_core
# ---------------------------------------------------------------------------

class TestOwnershipBoundary:
    def test_loader_module_does_not_import_agentic_core(self):
        """AST scan of retrieval_requirements.py must show zero agentic_core imports."""
        loader_path = (
            Path(__file__).parents[2]
            / "apps_rg"
            / "runtime"
            / "profiles"
            / "retrieval_requirements.py"
        )
        tree = ast.parse(loader_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module:
                    assert not node.module.startswith("agentic_core"), (
                        f"retrieval_requirements.py must not import agentic_core; "
                        f"found: {node.module}"
                    )
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        assert not alias.name.startswith("agentic_core"), (
                            f"retrieval_requirements.py must not import agentic_core; "
                            f"found: {alias.name}"
                        )

    def test_profile_yaml_does_not_contain_agentic_core_references(self):
        """Non-comment YAML lines must not reference agentic_core as an import target.

        Comments may mention agentic_core for context (e.g. "interpreted by core"),
        but no YAML value or key may name an agentic_core module path.
        """
        lines = PROFILE_PATH.read_text(encoding="utf-8").splitlines()
        non_comment_lines = [
            line for line in lines
            if not line.lstrip().startswith("#")
        ]
        for line in non_comment_lines:
            # Values should not contain Python import paths to agentic_core
            assert "agentic_core." not in line, (
                f"Profile YAML non-comment line references agentic_core module: {line!r}"
            )

    def test_profile_yaml_does_not_contain_python_code(self):
        """Profile is declarative YAML only — no Python import/def/lambda statements.

        'class' appears in 'task_class' YAML keys so we test for Python
        statement forms specifically (e.g. 'class Foo', 'def foo(', 'import x').
        """
        lines = PROFILE_PATH.read_text(encoding="utf-8").splitlines()
        non_comment_lines = [
            line for line in lines
            if not line.lstrip().startswith("#")
        ]
        # Match Python statement syntax, not substrings in field names/values.
        import re
        python_stmt_patterns = [
            r"^\s*import\s+\w",          # import statement
            r"^\s*from\s+\w.*\s+import",  # from ... import
            r"^\s*def\s+\w+\s*\(",        # def function
            r"^\s*class\s+\w+[:\(]",       # class declaration
            r"lambda\s+\w*\s*:",           # lambda expression
        ]
        for line in non_comment_lines:
            for pattern in python_stmt_patterns:
                assert not re.search(pattern, line), (
                    f"Profile YAML appears to contain Python code matching '{pattern}': {line!r}"
                )

    def test_profile_yaml_does_not_contain_retrieval_calls(self):
        """Profile must not call retrieve(), query(), score(), or write artifacts."""
        content = PROFILE_PATH.read_text(encoding="utf-8").lower()
        forbidden = ["retrieve(", "query(", "score(", "write_artifact(", "emit("]
        for token in forbidden:
            assert token not in content, (
                f"Profile YAML must not contain retrieval/scoring/artifact calls; "
                f"found: '{token}'"
            )


# ---------------------------------------------------------------------------
# T6: Profile thresholds and policies are well-formed
# ---------------------------------------------------------------------------

class TestThresholdsAndPolicies:
    def test_minimum_grounding_thresholds_are_floats_in_range(self, profile):
        thresholds = profile["minimum_grounding_thresholds"]
        for key, value in thresholds.items():
            assert isinstance(value, (int, float)), f"{key} must be numeric"
            assert 0.0 <= float(value) <= 1.0, f"{key}={value} out of [0,1] range"

    def test_overfit_threshold_mimicry_max_in_range(self, profile):
        ot = profile["overfit_threshold"]
        v = float(ot["mimicry_max"])
        assert 0.0 <= v <= 1.0

    def test_jd_requirement_policy_coverage_floor_in_range(self, profile):
        floor = float(profile["jd_requirement_policy"]["coverage_floor"])
        assert 0.0 <= floor <= 1.0

    def test_company_brief_provenance_policy_required_fields_non_empty(self, profile):
        fields = profile["company_brief_provenance_policy"]["required_fields_when_present"]
        assert len(fields) >= 1

    def test_freshness_profile_has_max_age_hours_per_source_class(self, profile):
        ages = profile["freshness_profile"]["max_age_hours"]
        for cls in _EXPECTED_NORMATIVE_CLASSES:
            assert cls in ages, f"freshness_profile.max_age_hours missing class: {cls}"
