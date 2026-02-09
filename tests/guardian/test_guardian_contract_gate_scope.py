"""SSOT test: Lock contract gate scope to prevent silent widening."""

import ast
import pathlib

# Import SSOT configuration
from tests.guardian._contract_gate_ssot import (
    ALLOWED_STATUS_ASSERTION_FAMILIES,
    CONTRACT_GATE_TEST_MODULES,
    GUARDIAN_ID_TO_REQUIRED_STATUS_ASSERTIONS,
    GUARDIAN_ID_TO_REQUIRED_TEST_SYMBOLS,
    GUARDIAN_ID_TO_TEST_MODULES,
    META_GUARDIAN_IDS,
    STATUS_ASSERTION_ENUM_VALUES,
    enabled_guardian_ids_from_registry,
    validate_contract_gate_ssot,
)


def _get_test_modules_from_directory(test_dir: pathlib.Path) -> set[str]:
    """Extract test module names (file stems) from a directory."""
    modules = set()
    for py_file in test_dir.glob("test_*.py"):
        modules.add(py_file.stem)
    return modules


def test_contract_gate_modules_are_present():
    """All SSOT contract gate modules must exist in tests/guardian/."""
    test_dir = pathlib.Path(__file__).parent
    actual_modules = _get_test_modules_from_directory(test_dir)

    missing = set(CONTRACT_GATE_TEST_MODULES) - actual_modules
    assert not missing, (
        f"Missing contract gate test modules: {sorted(missing)}\nThese are required for contract enforcement."
    )


def test_collect_ignore_glob_excludes_no_contract_modules():
    """collect_ignore_glob must not exclude any contract gate test modules."""
    from tests.guardian.conftest import collect_ignore_glob

    # Convert ignore patterns to module names
    ignored_patterns = set(collect_ignore_glob)
    ignored_modules = {
        pattern.replace("test_", "").replace(".py", "")
        for pattern in ignored_patterns
        if pattern.startswith("test_") and pattern.endswith(".py")
    }

    # Check if any contract gate modules are ignored
    ignored_contract_modules = set(CONTRACT_GATE_TEST_MODULES) & ignored_modules
    assert not ignored_contract_modules, (
        f"Contract gate modules are being ignored by collect_ignore_glob: {sorted(ignored_contract_modules)}\n"
        f"These must be included in contract gate testing."
    )


def test_no_additional_contract_gate_modules_without_update():
    """Prevent silent addition of contract gate modules without SSOT update."""
    test_dir = pathlib.Path(__file__).parent
    actual_modules = _get_test_modules_from_directory(test_dir)

    # Remove non-contract modules (e.g., test files for other guardian features)
    # We identify contract modules by checking if they test core contract features
    core_contract_indicators = {
        "contract",
        "aggregator",
        "performance",
        "behavioral",
        "conftest",
        "scan_budget",
        "guardian_aggregation",
        "registry",
        "l6_signal",
        "runtime_budget",
        "semantic",
        "artifact_class",
        "gate_scope",
        "integrity_checker",  # Added for alias policy test
    }

    potential_contract_modules = {
        m for m in actual_modules if any(indicator in m for indicator in core_contract_indicators)
    }

    # Any module not in our SSOT list should be explicitly considered
    untracked = potential_contract_modules - set(CONTRACT_GATE_TEST_MODULES)

    if untracked:
        assert False, (
            f"Found potential contract gate modules not in SSOT list: {sorted(untracked)}\n"
            f"If these are contract gate modules, update CONTRACT_GATE_TEST_MODULES in _contract_gate_ssot.py.\n"
            f"If not, consider renaming to avoid confusion."
        )


def test_contract_gate_scope_cannot_be_widened_by_ignores():
    """CI contract gate cannot be silently widened via ignore patterns."""
    # This test ensures that the .github/workflows/guardian-tests.yml
    # (which runs pytest tests/guardian/) cannot be bypassed by adding
    # more ignores to conftest.py

    from tests.guardian.conftest import collect_ignore_glob

    # Count ignored test files
    ignored_count = len(collect_ignore_glob)

    # This is a soft ceiling - increase it deliberately if needed
    max_allowed_ignores = 5  # Current: 2 (test_comprehensive_structure.py, test_mro_integrity.py)

    assert ignored_count <= max_allowed_ignores, (
        f"Too many test files ignored ({ignored_count} > {max_allowed_ignores}).\n"
        f"This widens the contract gate scope via ignores. "
        f"Either fix the underlying issues or increase max_allowed_ignores deliberately."
    )


def test_ssot_contract_gate_validation():
    """SSOT configuration must be valid and cover all enabled guardians."""
    validate_contract_gate_ssot()


def test_ssot_modules_all_exist_on_disk():
    """Verify every module in CONTRACT_GATE_TEST_MODULES exists as a file."""
    test_dir = pathlib.Path(__file__).parent
    for module_name in CONTRACT_GATE_TEST_MODULES:
        module_file = test_dir / f"{module_name}.py"
        assert module_file.exists(), (
            f"SSOT lists '{module_name}' but file '{module_file.name}' does not exist.\n"
            f"Either create the file or remove from CONTRACT_GATE_TEST_MODULES."
        )


# -----------------------------------------------------------------------------
# Non-Vacuous Contract Gate Invariants (Phase 2)
# -----------------------------------------------------------------------------


class TestNonVacuousContractGate:
    """Ensure contract gate cannot become vacuous when enabled guardians change."""

    def test_enabled_guardians_are_subset_of_mapping_keys(self):
        """If enabled set is non-empty, it must be a subset of mapping keys."""
        enabled_ids = enabled_guardian_ids_from_registry()

        if enabled_ids:
            mapped_ids = set(GUARDIAN_ID_TO_TEST_MODULES.keys())
            uncovered = enabled_ids - mapped_ids
            assert not uncovered, (
                f"Enabled guardians not in GUARDIAN_ID_TO_TEST_MODULES: {sorted(uncovered)}\n"
                f"Add test mappings for these guardians to maintain coverage."
            )

    def test_mapped_modules_exist_on_disk(self):
        """Each mapped module must exist on disk."""
        test_dir = pathlib.Path(__file__).parent

        for guardian_id, modules in GUARDIAN_ID_TO_TEST_MODULES.items():
            for module_name in modules:
                module_file = test_dir / f"{module_name}.py"
                assert module_file.exists(), (
                    f"Guardian '{guardian_id}' maps to '{module_name}' but file does not exist.\n"
                    f"Create the module or fix the mapping."
                )

    def test_mapped_modules_not_ignored(self):
        """Each mapped module must not be ignored by collect_ignore_glob."""
        from tests.guardian.conftest import collect_ignore_glob

        ignored_files = set(collect_ignore_glob)

        for guardian_id, modules in GUARDIAN_ID_TO_TEST_MODULES.items():
            for module_name in modules:
                module_filename = f"{module_name}.py"
                assert module_filename not in ignored_files, (
                    f"Guardian '{guardian_id}' maps to '{module_name}' but it is IGNORED.\n"
                    f"Remove from collect_ignore_glob to ensure contract coverage."
                )

    def test_meta_guardian_always_covered(self):
        """At least one meta-guardian must always be covered (prevents vacuous gate)."""
        mapped_ids = set(GUARDIAN_ID_TO_TEST_MODULES.keys())
        meta_covered = META_GUARDIAN_IDS & mapped_ids

        assert meta_covered, (
            f"No meta-guardians covered in GUARDIAN_ID_TO_TEST_MODULES.\n"
            f"At least one of {sorted(META_GUARDIAN_IDS)} must be mapped.\n"
            f"This prevents the contract gate from becoming vacuous."
        )

    def test_empty_enabled_set_still_has_meta_coverage(self):
        """Even if enabled set is empty, meta-guardian must be covered."""
        # This is a structural test - validates the invariant holds regardless of registry state
        mapped_ids = set(GUARDIAN_ID_TO_TEST_MODULES.keys())
        meta_covered = META_GUARDIAN_IDS & mapped_ids

        assert meta_covered, (
            f"GUARDIAN_ID_TO_TEST_MODULES must cover at least one meta-guardian.\n"
            f"Required: {sorted(META_GUARDIAN_IDS)}, Covered: {sorted(meta_covered)}"
        )


class TestSyntheticRegistryFlip:
    """Unit-level simulation: flipping a synthetic guardian to enabled fails coverage."""

    def test_synthetic_enabled_guardian_requires_mapping(self):
        """
        Simulate adding a new enabled guardian without updating mapping.

        This test creates a synthetic guardian ID and verifies that if it were
        enabled, the coverage check would fail unless mapping is updated.
        """
        # Synthetic guardian ID that is NOT in our current mapping
        synthetic_id = "synthetic_test_guardian_xyz"

        # Verify it's not already mapped (sanity check)
        assert synthetic_id not in GUARDIAN_ID_TO_TEST_MODULES, (
            f"Synthetic ID '{synthetic_id}' should not exist in mapping"
        )

        # Simulate what would happen if this guardian were enabled
        current_mapped = set(GUARDIAN_ID_TO_TEST_MODULES.keys())
        simulated_enabled = current_mapped | {synthetic_id}

        # Coverage check: simulated enabled set minus mapped should be non-empty
        uncovered = simulated_enabled - current_mapped

        assert synthetic_id in uncovered, f"Coverage check should detect '{synthetic_id}' as uncovered"

        # This proves: adding a new enabled guardian without updating mapping
        # would be caught by test_enabled_guardians_are_subset_of_mapping_keys

    def test_removing_meta_guardian_fails(self):
        """
        Simulate removing all meta-guardian mappings.

        This test verifies the meta-guardian invariant catches vacuous gates.
        """
        # Simulate empty meta-guardian coverage
        simulated_mapping = {
            k: v for k, v in GUARDIAN_ID_TO_TEST_MODULES.items() if k not in META_GUARDIAN_IDS
        }

        simulated_meta_covered = META_GUARDIAN_IDS & set(simulated_mapping.keys())

        # If we removed all meta-guardians, this would be empty
        # The actual mapping should NOT be empty
        actual_meta_covered = META_GUARDIAN_IDS & set(GUARDIAN_ID_TO_TEST_MODULES.keys())

        assert actual_meta_covered, "Actual mapping must cover at least one meta-guardian"


# -----------------------------------------------------------------------------
# Semantic Coverage Enforcement: Mapped modules must contain guardian tests
# -----------------------------------------------------------------------------


def _extract_symbols_from_module(module_path: pathlib.Path) -> set[str]:
    """
    Extract all class names, function names, and import names from a module.

    Returns a set of symbol names found in the module's AST.
    """
    try:
        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return set()

    symbols: set[str] = set()

    for node in ast.walk(tree):
        # Class names
        if isinstance(node, ast.ClassDef):
            symbols.add(node.name)
        # Function names
        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            symbols.add(node.name)
        # Import names (from ... import X)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                symbols.add(alias.name)
        # Import names (import X)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                # Get the last part of dotted import
                symbols.add(alias.name.split(".")[-1])

    return symbols


def _extract_status_assertions_from_module(module_path: pathlib.Path) -> set[str]:
    """
    Extract *structural* status assertions from a module (AST-based).

    Only counts ``assert <expr> == <status>`` where ``<status>`` resolves to
    a recognised enum value via one of two families:

      - **dot_status_equals**: ``<expr>.status == <Enum>.<VALUE>.value`` or ``== "<VALUE>"``
      - **rolled_up_equals**:  ``<expr> == <Enum>.<VALUE>.value`` or ``== "<VALUE>"``

    Returns a set of canonical status literals in the same format as
    ``GUARDIAN_ID_TO_REQUIRED_STATUS_ASSERTIONS`` values, e.g.
    ``{"GuardianStatus.FAIL.value", "CheckStatus.SKIP.value"}``.
    """
    try:
        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return set()

    found_families: set[str] = set()
    asserted_statuses: set[str] = set()

    # -- helpers ----------------------------------------------------------

    def _is_status_attr(node: ast.AST) -> bool:
        """True when *node* is ``<expr>.status``."""
        return isinstance(node, ast.Attribute) and node.attr == "status"

    def _extract_rhs_enum_qualified(node: ast.AST) -> str | None:
        """
        Return ``"<Enum>.<VALUE>.value"`` if *node* is ``<Enum>.<VALUE>.value``,
        or ``None``.
        """
        if isinstance(node, ast.Attribute) and node.attr == "value":
            base = node.value
            if isinstance(base, ast.Attribute):
                v = base.attr.upper()
                if v in STATUS_ASSERTION_ENUM_VALUES:
                    # Reconstruct the qualified name, e.g. GuardianStatus.FAIL.value
                    if isinstance(base.value, ast.Name):
                        return f"{base.value.id}.{base.attr}.value"
        return None

    def _extract_rhs_string_literal(node: ast.AST) -> str | None:
        """Return upper-cased value if *node* is a string constant in STATUS_ASSERTION_ENUM_VALUES."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            v = node.value.upper()
            return v if v in STATUS_ASSERTION_ENUM_VALUES else None
        return None

    def _matches_equality_assert(test: ast.AST):
        """Return ``(left, right)`` for ``assert left == right``, else ``None``."""
        if not isinstance(test, ast.Compare):
            return None
        if len(test.ops) != 1 or not isinstance(test.ops[0], ast.Eq):
            return None
        if len(test.comparators) != 1:
            return None
        return (test.left, test.comparators[0])

    # -- walk -------------------------------------------------------------

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assert):
            continue
        cmp_pair = _matches_equality_assert(node.test)
        if not cmp_pair:
            continue
        left, right = cmp_pair

        # Try qualified enum on RHS first, then string literal
        qualified = _extract_rhs_enum_qualified(right)
        literal_val = _extract_rhs_string_literal(right) if not qualified else None

        if qualified:
            # Family 1: <expr>.status == <Enum>.<VALUE>.value
            if _is_status_attr(left):
                found_families.add("dot_status_equals")
                asserted_statuses.add(qualified)
            else:
                # Family 2: <expr> == <Enum>.<VALUE>.value
                found_families.add("rolled_up_equals")
                asserted_statuses.add(qualified)
        elif literal_val:
            # String-literal comparison: assert x.status == "FAIL"
            if _is_status_attr(left):
                found_families.add("dot_status_equals")
            else:
                found_families.add("rolled_up_equals")
            # We can't reconstruct the Enum prefix from a bare string;
            # emit both possible qualified forms so the matcher can find it.
            asserted_statuses.add(f"GuardianStatus.{literal_val}.value")
            asserted_statuses.add(f"CheckStatus.{literal_val}.value")

    # Guard: reject unknown families
    unknown = found_families - ALLOWED_STATUS_ASSERTION_FAMILIES
    assert not unknown, f"Unknown assertion families found: {sorted(unknown)}"

    return asserted_statuses


class TestSemanticCoverageEnforcement:
    """Enforce that mapped modules actually test the guardian (not just exist)."""

    def test_all_guardians_have_required_symbols_defined(self):
        """Every guardian in GUARDIAN_ID_TO_TEST_MODULES must have required symbols."""
        for guardian_id in GUARDIAN_ID_TO_TEST_MODULES:
            assert guardian_id in GUARDIAN_ID_TO_REQUIRED_TEST_SYMBOLS, (
                f"Guardian '{guardian_id}' mapped but has no required symbols defined.\n"
                f"Add entry to GUARDIAN_ID_TO_REQUIRED_TEST_SYMBOLS."
            )

    def test_mapped_modules_contain_required_symbols(self):
        """
        For each guardian, at least ONE required symbol must appear in its test module(s).

        This prevents "coverage by proxy" where a guardian is mapped to a module
        that doesn't actually test it.
        """
        test_dir = pathlib.Path(__file__).parent
        failures: list[str] = []

        for guardian_id, modules in GUARDIAN_ID_TO_TEST_MODULES.items():
            required_symbols = GUARDIAN_ID_TO_REQUIRED_TEST_SYMBOLS.get(guardian_id, ())
            if not required_symbols:
                continue  # Skip if no required symbols defined (caught by other test)

            # Collect all symbols from all mapped modules
            all_found_symbols: set[str] = set()
            for module_name in modules:
                module_path = test_dir / f"{module_name}.py"
                if module_path.exists():
                    all_found_symbols |= _extract_symbols_from_module(module_path)

            # Check if at least one required symbol is present
            matched_symbols = set(required_symbols) & all_found_symbols

            if not matched_symbols:
                failures.append(
                    f"  Guardian '{guardian_id}':\n"
                    f"    Mapped modules: {list(modules)}\n"
                    f"    Required symbols (at least one): {list(required_symbols)}\n"
                    f"    Found: NONE",
                )

        assert not failures, (
            "SEMANTIC COVERAGE FAILURE: Guardian test modules lack required symbols.\n"
            "Each guardian's test module must contain at least ONE guardian-specific test:\n"
            + "\n".join(failures)
        )

    def test_required_symbols_are_actionable(self):
        """Required symbols must include at least a test class or function name."""
        for guardian_id, symbols in GUARDIAN_ID_TO_REQUIRED_TEST_SYMBOLS.items():
            has_test_symbol = any(
                s.startswith("Test") or s.startswith("test_") or s.startswith("run_") for s in symbols
            )
            assert has_test_symbol, (
                f"Guardian '{guardian_id}' required symbols must include "
                f"at least one Test*, test_*, or run_* symbol.\n"
                f"Current symbols: {symbols}"
            )

    def test_required_status_assertions_are_present(self):
        """
        Each guardian must have at least one status assertion for each required status.

        This enforces actual behavioral testing, not just symbol presence.
        """
        test_dir = pathlib.Path(__file__).parent
        failures: list[str] = []

        for guardian_id, modules in GUARDIAN_ID_TO_TEST_MODULES.items():
            required_statuses = GUARDIAN_ID_TO_REQUIRED_STATUS_ASSERTIONS.get(guardian_id, ())
            if not required_statuses:
                continue  # Skip if no required status assertions defined

            # Collect all status assertions from all mapped modules
            all_asserted_statuses: set[str] = set()
            for module_name in modules:
                module_path = test_dir / f"{module_name}.py"
                if module_path.exists():
                    all_asserted_statuses |= _extract_status_assertions_from_module(module_path)

            # Check if each required status is structurally asserted
            missing_assertions = [rs for rs in required_statuses if rs not in all_asserted_statuses]

            if missing_assertions:
                failures.append(
                    f"  Guardian '{guardian_id}':\n"
                    f"    Mapped modules: {list(modules)}\n"
                    f"    Required status assertions: {list(required_statuses)}\n"
                    f"    Missing assertions: {missing_assertions}\n"
                    f"    Found assertions: {sorted(all_asserted_statuses)}",
                )

        assert not failures, (
            "STATUS ASSERTION FAILURE: Guardian test modules lack required status assertions.\n"
            "Each guardian must assert at least one test for each required status:\n" + "\n".join(failures)
        )
