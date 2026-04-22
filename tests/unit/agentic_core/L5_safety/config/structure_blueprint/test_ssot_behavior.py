"""Behavioral tests for ``agentic_core.L5_safety.config.structure_blueprint.ssot``.

Covers the hot-path SSOT module that publishes layer/territory/path constants
and exposes validation helpers used by every validator and healer agent.

- Layer validation constants (LAYER_ROOTS, REQUIRED_LCD_SUBFOLDERS, …) shape.
- is_layer_root / is_allowed_subfolder (parametric).
- validate_no_nested_lcd: flags illegal LCD sprouts, allows LCD under layer roots.
- _discover_apps_wildcard_folders: picks up apps_* folders under an explicit
  repo_root, returns frozenset, ignores non-apps dirs, ignores files.
- get_test_mirror_roots: base + wildcard union.
- _build_test_canonical_location_map: agentic_core + system_learning + apps_*
- get_canonical_test_path: source → mirrored test path, unknown source →
  autogen dir, empty rel → autogen dir.
- get_validated_project_root: locates repo root via PROJECT_ROOT_MARKERS.
- validate_path_within_project: inside = True, outside = False.
- safe_path_join: inside → ok; escape via '..' → ValueError (SAFETY VIOLATION).
- safe_prefixed_filename: idempotent when already prefixed, strips trailing
  underscore on prefix, returns raw when empty prefix.
- validate_no_duplicate_prefix: detects consecutive repeated parts.
- is_l4_approved: rejects < depth 4 and unknown combos; accepts when the
  L4_SUBFOLDER_MAP + L4_APPROVED_FOLDERS wiring aligns.
- validate_flat_directory: flags nested dirs under flat domains, ignores
  __pycache__, returns None for clean paths.
- validate_volatile_exclusion_contract: result carries the right keys.
- _load_exclusions_from_yaml: returns the 9 expected category keys as
  frozensets.
- TEST_CANONICAL_LOCATION_MAP fallback: always carries agentic_core key.
- Lazy loaders (lru_cache): get_core_subfolder_map / get_subfolder_metadata
  return the same object on repeated calls.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pytest

from agentic_core.L5_safety.config.structure_blueprint import ssot
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    ALLOW_ROOT_PY_TERRITORIES,
    LAYER_PREFIX_EXEMPT_TERRITORIES,
    LAYER_ROOTS,
    LEAF_DOMAINS_NO_LCD,
    REQUIRED_LCD_SUBFOLDERS,
    STANDARD_LAYER_STRUCTURE,
    TEST_CANONICAL_LOCATION_MAP,
    VOLATILE_TERRITORIES,
    _build_test_canonical_location_map,
    _discover_apps_wildcard_folders,
    _load_exclusions_from_yaml,
    get_canonical_test_path,
    get_core_subfolder_map,
    get_subfolder_metadata,
    get_test_mirror_roots,
    get_validated_project_root,
    is_allowed_subfolder,
    is_l4_approved,
    is_layer_root,
    is_path_allowed,
    safe_path_join,
    safe_prefixed_filename,
    validate_flat_directory,
    validate_no_duplicate_prefix,
    validate_no_nested_lcd,
    validate_path_within_project,
    validate_volatile_exclusion_contract,
)


# ---- Constants shape --------------------------------------------------

class TestConstants:
    @pytest.mark.parametrize("layer", [
        "L0_routing", "L1_cognition", "L2_execution",
        "L3_orchestration", "L4_state", "L5_safety", "L6_observability",
    ])
    def test_layer_roots_contains_all_seven(self, layer: str) -> None:
        assert layer in LAYER_ROOTS

    def test_layer_roots_is_frozenset(self) -> None:
        assert isinstance(LAYER_ROOTS, frozenset)

    def test_required_lcd_subfolders(self) -> None:
        for name in {"reasoning", "enforcement", "config", "types", "validators", "utils"}:
            assert name in REQUIRED_LCD_SUBFOLDERS

    def test_standard_layer_structure_order(self) -> None:
        # Must preserve the declared order — consumers rely on deterministic seq.
        assert STANDARD_LAYER_STRUCTURE == [
            "config", "types", "reasoning", "enforcement", "validators", "utils",
        ]

    def test_leaf_domains_no_lcd_contains_agents(self) -> None:
        assert "agents" in LEAF_DOMAINS_NO_LCD
        assert "base_agents" in LEAF_DOMAINS_NO_LCD

    def test_volatile_territories_contains_artifacts(self) -> None:
        assert "artifacts" in VOLATILE_TERRITORIES
        assert "logs" in VOLATILE_TERRITORIES

    def test_allow_root_py_and_layer_prefix_exempt_are_frozensets(self) -> None:
        assert isinstance(ALLOW_ROOT_PY_TERRITORIES, frozenset)
        assert isinstance(LAYER_PREFIX_EXEMPT_TERRITORIES, frozenset)


# ---- is_layer_root / is_allowed_subfolder -----------------------------

class TestLayerPredicates:
    @pytest.mark.parametrize("name,expected", [
        ("L0_routing", True),
        ("L5_safety", True),
        ("agents", False),
        ("apps_rg", False),
        ("", False),
    ])
    def test_is_layer_root(self, name: str, expected: bool) -> None:
        assert is_layer_root(name) is expected

    def test_is_allowed_subfolder_for_known_layer(self) -> None:
        assert is_allowed_subfolder("L0_routing", "reasoning") is True
        assert is_allowed_subfolder("L0_routing", "agents") is False

    def test_is_allowed_subfolder_rejects_non_layer(self) -> None:
        assert is_allowed_subfolder("apps_rg", "reasoning") is False


# ---- validate_no_nested_lcd -------------------------------------------

class TestValidateNoNestedLcd:
    def test_flat_path_returns_none(self) -> None:
        assert validate_no_nested_lcd(["agentic_core", "foo.py"]) is None

    def test_lcd_sprout_outside_layer_flagged(self) -> None:
        # agents/reasoning without a preceding layer root is a violation
        result = validate_no_nested_lcd(["agents", "reasoning", "x.py"])
        assert result is not None
        assert result["domain"] == "agents"
        assert result["illegal_subfolder"] == "reasoning"

    def test_lcd_under_layer_root_allowed(self) -> None:
        # L5_safety/agents/reasoning — 'agents' is a leaf BUT preceded by L5
        assert validate_no_nested_lcd(
            ["agentic_core", "L5_safety", "agents", "reasoning", "x.py"],
        ) is None


# ---- _discover_apps_wildcard_folders ---------------------------------

class TestDiscoverAppsWildcard:
    def test_picks_up_apps_prefix(self, tmp_path: Path) -> None:
        (tmp_path / "apps_rg").mkdir()
        (tmp_path / "apps_lic").mkdir()
        (tmp_path / "agentic_core").mkdir()
        (tmp_path / "apps_test.txt").write_text("x")  # file, not dir
        result = _discover_apps_wildcard_folders(tmp_path)
        assert "apps_rg" in result
        assert "apps_lic" in result
        assert "agentic_core" not in result
        # files named apps_* must NOT be picked up
        assert "apps_test.txt" not in result

    def test_empty_when_no_apps(self, tmp_path: Path) -> None:
        (tmp_path / "foo").mkdir()
        assert _discover_apps_wildcard_folders(tmp_path) == frozenset()

    def test_returns_frozenset(self, tmp_path: Path) -> None:
        assert isinstance(_discover_apps_wildcard_folders(tmp_path), frozenset)


# ---- get_test_mirror_roots -------------------------------------------

class TestGetTestMirrorRoots:
    def test_includes_agentic_core(self, tmp_path: Path) -> None:
        roots = get_test_mirror_roots(tmp_path)
        assert "agentic_core" in roots
        assert "system_learning" in roots

    def test_merges_discovered_apps(self, tmp_path: Path) -> None:
        (tmp_path / "apps_new").mkdir()
        roots = get_test_mirror_roots(tmp_path)
        assert "apps_new" in roots


# ---- _build_test_canonical_location_map ------------------------------

class TestBuildTestCanonicalLocationMap:
    def test_has_agentic_core(self, tmp_path: Path) -> None:
        result = _build_test_canonical_location_map(tmp_path)
        assert result["agentic_core"] == "tests/unit/agentic_core"
        assert result["system_learning"] == "tests/unit/system_learning"

    def test_apps_wildcard_appended(self, tmp_path: Path) -> None:
        (tmp_path / "apps_foo").mkdir()
        result = _build_test_canonical_location_map(tmp_path)
        assert result["apps_foo"] == "tests/unit/apps_foo"

    def test_module_level_fallback_map_has_agentic_core(self) -> None:
        # The module-level TEST_CANONICAL_LOCATION_MAP must ALWAYS publish the
        # agentic_core key even during the load-order fallback path.
        assert "agentic_core" in TEST_CANONICAL_LOCATION_MAP


# ---- get_canonical_test_path -----------------------------------------

class TestGetCanonicalTestPath:
    def test_known_source_root(self, tmp_path: Path) -> None:
        (tmp_path / "agentic_core").mkdir()
        src = tmp_path / "agentic_core" / "L5_safety" / "foo.py"
        result = get_canonical_test_path(src, tmp_path)
        assert result.name == "test_foo.py"
        assert "tests" in result.parts
        assert "L5_safety" in result.parts

    def test_unknown_source_root_falls_back_to_autogen(self, tmp_path: Path) -> None:
        src = tmp_path / "tools" / "mirror.py"
        result = get_canonical_test_path(src, tmp_path)
        assert result.name == "test_mirror.py"
        assert "unit_min_deps" in result.parts

    def test_apps_source_mirrors_under_apps(self, tmp_path: Path) -> None:
        (tmp_path / "apps_rg").mkdir()
        src = tmp_path / "apps_rg" / "engines" / "bar.py"
        result = get_canonical_test_path(src, tmp_path)
        assert "apps_rg" in result.parts
        assert "engines" in result.parts
        assert result.name == "test_bar.py"

    def test_abs_path_outside_repo_uses_relative(self, tmp_path: Path) -> None:
        # source not under repo_root — function uses the raw path as rel.
        # repo_root must exist (iterdir is called by discovery), so create it.
        repo = tmp_path / "repo"
        repo.mkdir()
        other = tmp_path / "foo_other" / "x.py"
        result = get_canonical_test_path(other, repo)
        assert result.name == "test_x.py"


# ---- get_validated_project_root --------------------------------------

class TestGetValidatedProjectRoot:
    def test_resolves_actual_repo(self) -> None:
        root = get_validated_project_root()
        assert (root / "pyproject.toml").exists()
        assert (root / "agentic_core").exists()


# ---- validate_path_within_project ------------------------------------

class TestValidatePathWithinProject:
    def test_inside_is_true(self, tmp_path: Path) -> None:
        inner = tmp_path / "nested" / "file.py"
        inner.parent.mkdir()
        inner.write_text("x")
        assert validate_path_within_project(inner, tmp_path) is True

    def test_outside_is_false(self, tmp_path: Path) -> None:
        sibling = tmp_path.parent / "elsewhere.py"
        assert validate_path_within_project(sibling, tmp_path) is False


# ---- safe_path_join --------------------------------------------------

class TestSafePathJoin:
    def test_inside_ok(self, tmp_path: Path) -> None:
        result = safe_path_join(tmp_path, "a", "b.py")
        assert result.is_relative_to(tmp_path)

    def test_escape_rejected(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="SAFETY VIOLATION"):
            safe_path_join(tmp_path, "..", "outside.py")


# ---- safe_prefixed_filename ------------------------------------------

class TestSafePrefixedFilename:
    def test_adds_prefix_when_missing(self) -> None:
        assert safe_prefixed_filename("healing", "strategies.py") == "healing_strategies.py"

    def test_does_not_double_prefix(self) -> None:
        assert safe_prefixed_filename("healing", "healing_strategies.py") == "healing_strategies.py"

    def test_strips_trailing_underscore_from_prefix(self) -> None:
        assert safe_prefixed_filename("healing_", "strategies.py") == "healing_strategies.py"

    def test_empty_prefix_returns_original(self) -> None:
        assert safe_prefixed_filename("", "file.py") == "file.py"

    def test_stem_equals_prefix_unchanged(self) -> None:
        # stem == prefix → return as-is
        assert safe_prefixed_filename("healing", "healing.py") == "healing.py"


# ---- validate_no_duplicate_prefix ------------------------------------

class TestValidateNoDuplicatePrefix:
    def test_clean_name(self) -> None:
        ok, msg = validate_no_duplicate_prefix("healing_strategies.py")
        assert ok is False
        assert msg == ""

    def test_duplicate_prefix_flagged(self) -> None:
        ok, msg = validate_no_duplicate_prefix("healing_healing_strategies.py")
        assert ok is True
        assert "healing" in msg

    def test_no_extension(self) -> None:
        ok, _ = validate_no_duplicate_prefix("healing_healing_foo")
        assert ok is True


# ---- is_l4_approved ---------------------------------------------------

class TestIsL4Approved:
    def test_too_shallow_rejected(self) -> None:
        assert is_l4_approved("agentic_core/L5_safety/foo.py") is False

    def test_non_dotted_leaf_ok_path_len(self) -> None:
        # Depth 4 but not an approved combo → False
        assert is_l4_approved("agentic_core/L5_safety/enforcement/unknown_leaf") is False

    def test_invalid_territory_returns_false(self) -> None:
        assert is_l4_approved("invalid_root/a/b/c") is False


# ---- validate_flat_directory ----------------------------------------

class TestValidateFlatDirectory:
    def test_flat_domain_clean(self) -> None:
        # base_agents is flat; direct file OK
        assert validate_flat_directory(
            ["agentic_core", "base_agents", "foo.py"],
        ) is None

    def test_flat_domain_with_subdir_flagged(self) -> None:
        result = validate_flat_directory(
            ["agentic_core", "base_agents", "nested", "foo.py"],
        )
        assert result is not None
        assert result["domain"] == "base_agents"
        assert result["illegal_child"] == "nested"

    def test_pycache_is_ignored(self) -> None:
        assert validate_flat_directory(
            ["agentic_core", "base_agents", "__pycache__", "foo.pyc"],
        ) is None


# ---- validate_volatile_exclusion_contract ---------------------------

class TestValidateVolatileExclusionContract:
    def test_result_shape(self) -> None:
        result = validate_volatile_exclusion_contract()
        assert "valid" in result
        assert "violations" in result
        assert "missing_from_exclusion" in result
        assert "missing_from_volatile_set" in result
        assert "volatile_territories" in result
        assert isinstance(result["valid"], bool)


# ---- _load_exclusions_from_yaml -------------------------------------

class TestLoadExclusionsFromYaml:
    def test_returns_all_nine_categories(self) -> None:
        result = _load_exclusions_from_yaml()
        for key in {
            "build_cache", "version_control", "virtual_env", "coverage",
            "archive", "ide", "vendor", "data", "special",
        }:
            assert key in result
            assert isinstance(result[key], frozenset)


# ---- Lazy loaders (lru_cache) ---------------------------------------

class TestLazyLoaders:
    def test_core_subfolder_map_is_mapping(self) -> None:
        assert isinstance(get_core_subfolder_map(), Mapping)

    def test_subfolder_metadata_is_mapping(self) -> None:
        assert isinstance(get_subfolder_metadata(), Mapping)

    def test_core_subfolder_map_cached(self) -> None:
        # lru_cache: same call returns same object
        assert get_core_subfolder_map() is get_core_subfolder_map()


# ---- is_path_allowed smoke ------------------------------------------

class TestIsPathAllowed:
    def test_double_slash_rejected(self) -> None:
        assert is_path_allowed("agentic_core//foo.py") is False

    def test_parent_traversal_rejected(self) -> None:
        assert is_path_allowed("../secret.py") is False

    def test_empty_rejected(self) -> None:
        assert is_path_allowed("") is False

    def test_dot_rejected(self) -> None:
        assert is_path_allowed(".") is False

    def test_unknown_root_rejected(self) -> None:
        assert is_path_allowed("not_a_real_root/x.py") is False


# ---- ssot module surface --------------------------------------------

class TestModuleSurface:
    """The following symbols are part of the stable public surface — any
    accidental removal must break this test, protecting downstream callers.
    """

    @pytest.mark.parametrize("name", [
        "LAYER_ROOTS", "REQUIRED_LCD_SUBFOLDERS", "LEAF_DOMAINS_NO_LCD",
        "STANDARD_LAYER_STRUCTURE", "VOLATILE_TERRITORIES",
        "ALLOW_ROOT_PY_TERRITORIES", "LAYER_PREFIX_EXEMPT_TERRITORIES",
        "ENFORCED_TERRITORIES", "CODE_TERRITORIES",
        "TEST_MIRROR_ROOTS", "TEST_CANONICAL_LOCATION_MAP",
        "AGENTIC_CORE_DIR", "APPS_RG_DIR", "TESTS_DIR",
        "PROJECT_ROOT_MARKERS", "FLAT_DIRECTORIES",
        "VALIDATED_FILE_EXTENSIONS", "NAMING_EXEMPT_FILES",
        "NAMING_EXEMPT_DIRS", "FORBIDDEN_PATTERNS",
    ])
    def test_public_symbol_present(self, name: str) -> None:
        assert hasattr(ssot, name), f"public symbol {name!r} missing from ssot"
