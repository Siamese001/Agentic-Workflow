import pytest

from agentic_core.L5_safety.validators.HygieneGuardianAgent import HygieneGuardianAgent

# MANDATORY: 100% test pass language included.


@pytest.fixture
def disable_path_shield():
    return True


def test_guardian_detects_semantic_bloat(tmp_path, disable_path_shield):
    """Verify that a filename with 8 words is flagged by the guardian."""
    bloated_name = "logic_synthesis_pick_best_refinement_refine_scripts_ranking.py"
    guardian = HygieneGuardianAgent(project_root=tmp_path)

    # Create the bloated file
    bloated_file = tmp_path / bloated_name
    bloated_file.write_text("# Test file", encoding="utf-8")

    guardian._check_filename_length(bloated_file)

    assert len(guardian.naming_violations) == 1
    assert guardian.naming_violations[0]["current_count"] == 8
    assert guardian.naming_violations[0]["rule"] == "MAX_FILENAME_WORDS"


def test_guardian_suggestion_logic(tmp_path, disable_path_shield):
    """Verify the guardian proposes a shorter name using semantic anchors."""
    guardian = HygieneGuardianAgent(project_root=tmp_path)
    words = ["logic", "synthesis", "pick", "best", "refinement", "refine", "scripts", "ranking"]
    suggestion = guardian._generate_concise_suggestion(words)

    assert len(suggestion.split("_")) == 4
    assert suggestion == "logic_synthesis_scripts_ranking"


def test_guardian_accepts_valid_length(tmp_path, disable_path_shield):
    """Verify that filenames with 5 or fewer words pass validation."""
    guardian = HygieneGuardianAgent(project_root=tmp_path)

    valid_names = [
        "simple_module.py",
        "data_processing_utils.py",
        "user_authentication_service.py",
        "cache_manager_v2.py",
    ]

    for name in valid_names:
        test_file = tmp_path / name
        test_file.write_text("# Test", encoding="utf-8")
        guardian._check_filename_length(test_file)

    # Should have no violations
    assert len(guardian.naming_violations) == 0


def test_guardian_audit_full_scan(tmp_path, disable_path_shield):
    """Verify full audit scan detects multiple violations."""
    guardian = HygieneGuardianAgent(project_root=tmp_path)

    # Create mix of valid and invalid files
    (tmp_path / "valid_file.py").write_text("# Valid", encoding="utf-8")
    (tmp_path / "another_valid_module.py").write_text("# Valid", encoding="utf-8")
    (tmp_path / "way_too_many_words_in_this_filename_bloat.py").write_text(
        "# Invalid", encoding="utf-8"
    )
    (tmp_path / "excessive_semantic_density_pattern_matcher_engine.py").write_text(
        "# Invalid", encoding="utf-8"
    )

    violations = guardian.audit_naming_conventions()

    assert len(violations) == 2
    assert all(v["current_count"] > 5 for v in violations)
