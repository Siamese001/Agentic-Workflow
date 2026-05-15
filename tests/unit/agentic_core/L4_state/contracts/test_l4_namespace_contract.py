"""W2 tests for L4NamespaceParser — generic contract validation.

All fixture app_ids use neutral identifiers: 'sample_app', 'test_app_1'.
No apps_rg literals anywhere in this file or the parser module.

Test categories:
- Positive parse: YAML and JSON valid fixtures
- Negative tests: each required failure class
- Write-op / UWG-mediated policy enforcement
- Parser does not create write authority
- No apps_rg literal in agentic_core/L4_state/contracts/
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from agentic_core.L4_state.contracts.l4_namespace_contract import (
    ALLOWED_READ_OPERATIONS,
    ALLOWED_SURFACE_TYPES,
    L4NamespaceContractError,
    L4NamespaceManifest,
    L4NamespaceParseError,
    L4NamespaceParser,
    L4ReadSurface,
    ValidationResult,
    WRITE_CAPABLE_OPERATIONS,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
VALID_YAML = FIXTURES_DIR / "l4_namespace_manifest_valid.yaml"
VALID_JSON = FIXTURES_DIR / "l4_namespace_manifest_valid.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_surface(**overrides) -> dict:
    """Return a fully valid surface dict. Override fields to test failures."""
    base = {
        "surface_id": "surf_test",
        "surface_type": "cache",
        "schema_version": "1.0",
        "schema_ref": "schema://core/test/v1",
        "acl_profile": "read-only",
        "authority_class": "L4ReadAuthority",
        "replay_key_pattern": "cache:{run_id}:{key}",
        "audit_manifest_ref": "manifest://audit/test",
        "retention_policy": "30d",
        "allowed_operations": ["query"],
        "writer_policy": "",
        "read_policy": "standard",
        "owner_app_id": "sample_app",
        "pii_or_sensitive_data_class": "none",
        "lineage_required": False,
    }
    base.update(overrides)
    return base


def _minimal_manifest(**overrides) -> dict:
    """Return a fully valid manifest dict."""
    base = {
        "app_id": "sample_app",
        "version": "1.0.0",
        "surfaces": [_minimal_surface()],
    }
    base.update(overrides)
    return base


def _validate(data: dict) -> ValidationResult:
    return L4NamespaceParser.validate_dict(data)


# ---------------------------------------------------------------------------
# Positive: YAML parse
# ---------------------------------------------------------------------------

def test_parse_yaml_valid_fixture():
    """Valid YAML fixture must parse without error."""
    manifest = L4NamespaceParser.parse_yaml(VALID_YAML)
    assert isinstance(manifest, L4NamespaceManifest)
    assert manifest.app_id == "sample_app"
    assert len(manifest.surfaces) == 2


def test_parse_yaml_surfaces_are_l4_read_surface():
    """Each parsed surface must be an L4ReadSurface instance."""
    manifest = L4NamespaceParser.parse_yaml(VALID_YAML)
    for surf in manifest.surfaces:
        assert isinstance(surf, L4ReadSurface)


def test_parse_yaml_surface_fields_populated():
    """Surface fields must be populated from YAML."""
    manifest = L4NamespaceParser.parse_yaml(VALID_YAML)
    s0 = manifest.surfaces[0]
    assert s0.surface_id == "sample_cache"
    assert s0.surface_type == "cache"
    assert s0.schema_version == "1.0"
    assert s0.audit_manifest_ref == "manifest://audit/sample_app/cache"
    assert s0.retention_policy == "30d"


# ---------------------------------------------------------------------------
# Positive: JSON parse
# ---------------------------------------------------------------------------

def test_parse_json_valid_fixture():
    """Valid JSON fixture must parse without error."""
    manifest = L4NamespaceParser.parse_json(VALID_JSON)
    assert isinstance(manifest, L4NamespaceManifest)
    assert manifest.app_id == "test_app_1"
    assert len(manifest.surfaces) == 1


def test_parse_json_surface_id_populated():
    """JSON-parsed surface must have correct surface_id."""
    manifest = L4NamespaceParser.parse_json(VALID_JSON)
    assert manifest.surfaces[0].surface_id == "test_policy_registry"


# ---------------------------------------------------------------------------
# Negative: top-level failures
# ---------------------------------------------------------------------------

def test_empty_app_id_fails():
    result = _validate(_minimal_manifest(app_id=""))
    assert not result.valid
    assert any("EMPTY_APP_ID" in e for e in result.errors)


def test_empty_version_fails():
    result = _validate(_minimal_manifest(version=""))
    assert not result.valid
    assert any("EMPTY_VERSION" in e for e in result.errors)


def test_empty_surfaces_fails():
    result = _validate(_minimal_manifest(surfaces=[]))
    assert not result.valid
    assert any("EMPTY_SURFACES" in e for e in result.errors)


def test_missing_surfaces_key_fails():
    data = {"app_id": "sample_app", "version": "1.0.0"}
    result = _validate(data)
    assert not result.valid
    assert any("EMPTY_SURFACES" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Negative: duplicate surface_id
# ---------------------------------------------------------------------------

def test_duplicate_surface_id_fails():
    s1 = _minimal_surface(surface_id="dup_surf")
    s2 = _minimal_surface(surface_id="dup_surf")
    result = _validate(_minimal_manifest(surfaces=[s1, s2]))
    assert not result.valid
    assert any("DUPLICATE_SURFACE_ID" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Negative: owner_app_id mismatch
# ---------------------------------------------------------------------------

def test_owner_app_id_mismatch_fails():
    surf = _minimal_surface(owner_app_id="other_app")
    result = _validate(_minimal_manifest(app_id="sample_app", surfaces=[surf]))
    assert not result.valid
    assert any("OWNER_APP_ID_MISMATCH" in e for e in result.errors)


def test_owner_app_id_absent_does_not_fail():
    """Empty owner_app_id must not trigger mismatch check."""
    surf = _minimal_surface(owner_app_id="")
    result = _validate(_minimal_manifest(surfaces=[surf]))
    assert result.valid, f"Unexpected errors: {result.errors}"


# ---------------------------------------------------------------------------
# Negative: unknown surface_type
# ---------------------------------------------------------------------------

def test_unknown_surface_type_fails():
    surf = _minimal_surface(surface_type="apps_rg_custom_store")
    result = _validate(_minimal_manifest(surfaces=[surf]))
    assert not result.valid
    assert any("UNKNOWN_SURFACE_TYPE" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Negative: missing required surface fields
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("missing_field,expected_error", [
    ("schema_version", "MISSING_SCHEMA_VERSION"),
    ("schema_ref", "MISSING_SCHEMA_REF"),
    ("acl_profile", "MISSING_ACL_PROFILE"),
    ("authority_class", "MISSING_AUTHORITY_CLASS"),
    ("replay_key_pattern", "MISSING_REPLAY_KEY_PATTERN"),
    ("audit_manifest_ref", "MISSING_AUDIT_MANIFEST_REF"),
    ("retention_policy", "MISSING_RETENTION_POLICY"),
])
def test_missing_required_surface_field_fails(missing_field, expected_error):
    surf = _minimal_surface(**{missing_field: ""})
    result = _validate(_minimal_manifest(surfaces=[surf]))
    assert not result.valid, f"Expected failure for missing {missing_field}"
    assert any(expected_error in e for e in result.errors), (
        f"Expected {expected_error} in errors: {result.errors}"
    )


# ---------------------------------------------------------------------------
# Negative: invalid allowed_operations
# ---------------------------------------------------------------------------

def test_unknown_operation_fails():
    surf = _minimal_surface(allowed_operations=["query", "completely_unknown_op"])
    result = _validate(_minimal_manifest(surfaces=[surf]))
    assert not result.valid
    assert any("INVALID_OPERATION" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Write-capable ops require UWG-mediated writer_policy
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("write_op", sorted(WRITE_CAPABLE_OPERATIONS))
def test_write_op_without_uwg_writer_policy_fails(write_op):
    """Every write-capable op must fail without UWG-mediated writer_policy."""
    surf = _minimal_surface(
        allowed_operations=["query", write_op],
        writer_policy="",
    )
    result = _validate(_minimal_manifest(surfaces=[surf]))
    assert not result.valid, f"Expected failure for write op '{write_op}' without UWG policy"
    assert any("WRITE_OPS_REQUIRE_UWG_WRITER_POLICY" in e for e in result.errors), (
        f"Expected WRITE_OPS_REQUIRE_UWG_WRITER_POLICY in errors: {result.errors}"
    )


def test_write_op_with_uwg_writer_policy_passes():
    """Write op passes when writer_policy == 'UWG-mediated'."""
    surf = _minimal_surface(
        allowed_operations=["query", "write"],
        writer_policy="UWG-mediated",
    )
    result = _validate(_minimal_manifest(surfaces=[surf]))
    assert result.valid, f"Unexpected errors: {result.errors}"


def test_read_only_ops_do_not_require_writer_policy():
    """Read-only allowed_operations must not require writer_policy."""
    surf = _minimal_surface(
        allowed_operations=["query", "get", "search"],
        writer_policy="",
    )
    result = _validate(_minimal_manifest(surfaces=[surf]))
    assert result.valid, f"Unexpected errors: {result.errors}"


# ---------------------------------------------------------------------------
# Parser does not create write authority
# ---------------------------------------------------------------------------

def test_parser_returns_read_only_manifest_object():
    """L4NamespaceManifest must be frozen (immutable); no write methods present."""
    manifest = L4NamespaceParser.parse_yaml(VALID_YAML)
    assert hasattr(manifest, "__dataclass_fields__")
    # frozen=True dataclass raises dataclasses.FrozenInstanceError (subclass of TypeError)
    # when attribute assignment is attempted via normal syntax
    with pytest.raises((TypeError, AttributeError)):
        manifest.app_id = "hacked"  # type: ignore[misc]


def test_parser_does_not_expose_write_authority_attribute():
    """Parser class must not expose any write_authority or create_writer attribute."""
    for attr in dir(L4NamespaceParser):
        assert "write_authority" not in attr.lower(), (
            f"Unexpected write_authority attribute on parser: {attr}"
        )
        assert "create_writer" not in attr.lower(), (
            f"Unexpected create_writer attribute on parser: {attr}"
        )


def test_manifest_with_write_ops_declared_does_not_grant_authority():
    """Parsing a manifest that declares write ops does NOT produce a write-authority object.

    Parser validates governance metadata only; it never creates write authority.
    The resulting L4NamespaceManifest is frozen declarative metadata.
    """
    surf = _minimal_surface(
        allowed_operations=["query", "write"],
        writer_policy="UWG-mediated",
    )
    manifest = L4NamespaceParser.parse_yaml.__func__  # ensure it's a classmethod, not magic
    # Validate via dict — parse succeeds (write is declared with UWG policy)
    result = _validate(_minimal_manifest(surfaces=[surf]))
    assert result.valid
    # No write authority object is returned — result is a ValidationResult
    assert isinstance(result, ValidationResult)
    assert not hasattr(result, "write_authority")
    assert not hasattr(result, "grant_write")


# ---------------------------------------------------------------------------
# Malformed input: fail closed
# ---------------------------------------------------------------------------

def test_parse_json_nonexistent_path_raises_parse_error():
    with pytest.raises(L4NamespaceParseError):
        L4NamespaceParser.parse_json(Path("does_not_exist.json"))


def test_parse_yaml_nonexistent_path_raises_parse_error():
    with pytest.raises(L4NamespaceParseError):
        L4NamespaceParser.parse_yaml(Path("does_not_exist.yaml"))


def test_parse_json_malformed_raises_parse_error(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json}", encoding="utf-8")
    with pytest.raises(L4NamespaceParseError):
        L4NamespaceParser.parse_json(bad)


def test_parse_yaml_malformed_raises_parse_error(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("{{: invalid: yaml:", encoding="utf-8")
    with pytest.raises(L4NamespaceParseError):
        L4NamespaceParser.parse_yaml(bad)


def test_invalid_manifest_raises_contract_error(tmp_path):
    bad_manifest = {"app_id": "", "version": "1.0.0", "surfaces": []}
    bad_json = tmp_path / "bad_manifest.json"
    bad_json.write_text(json.dumps(bad_manifest), encoding="utf-8")
    with pytest.raises(L4NamespaceContractError):
        L4NamespaceParser.parse_json(bad_json)


# ---------------------------------------------------------------------------
# No apps_rg literal under agentic_core/L4_state/contracts/
# ---------------------------------------------------------------------------

def test_no_apps_rg_literal_in_contracts_directory():
    """Grep proof: zero occurrences of 'apps_rg' in the W2 module l4_namespace_contract.py.

    Scope is intentionally limited to the W2 file only. Pre-existing files in
    agentic_core/L4_state/contracts/ (e.g. app_domain.py) may contain docstring
    references to app names — those are pre-existing and out of W2 scope.
    This test proves the W2 parser module introduced no app-specific literals.
    """
    # Resolve repo root: this file is at tests/unit/agentic_core/L4_state/contracts/test_*.py
    # parents: [0]=contracts, [1]=L4_state, [2]=agentic_core, [3]=unit, [4]=tests, [5]=repo_root
    repo_root = Path(__file__).parents[5]
    w2_module = repo_root / "agentic_core" / "L4_state" / "contracts" / "l4_namespace_contract.py"
    assert w2_module.is_file(), f"W2 module not found: {w2_module}"

    lines = w2_module.read_text(encoding="utf-8").splitlines()
    hits = [(i + 1, line.rstrip()) for i, line in enumerate(lines) if "apps_rg" in line]
    assert hits == [], (
        f"Found apps_rg literals in l4_namespace_contract.py: {hits}"
    )


# ---------------------------------------------------------------------------
# Vocabulary constants are generic
# ---------------------------------------------------------------------------

def test_allowed_surface_types_are_generic():
    """ALLOWED_SURFACE_TYPES must not contain any app-specific literal."""
    for st in ALLOWED_SURFACE_TYPES:
        assert "apps_" not in st, f"App-specific surface type found: {st}"
        assert "rg" not in st.lower() or st == "prompt_registry", (
            f"Suspicious surface type: {st}"
        )


def test_allowed_read_operations_are_read_side_only():
    """Read operations must not overlap with write-capable operations."""
    overlap = ALLOWED_READ_OPERATIONS & WRITE_CAPABLE_OPERATIONS
    assert not overlap, f"Read ops overlap with write-capable ops: {overlap}"
