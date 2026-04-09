"""Tests for ContentMetadata security fields (B00 — GAP-014, REQ-022).

Verifies:
- 6 security fields exist on ContentMetadata with None defaults (non-breaking)
- validate_security_fields() raises IngestionSecurityError when any field is None
- validate_security_fields() passes when all 6 fields are populated
- IngestionSecurityError lists the specific missing field names
- to_dict() serialises all 6 security fields
- Negative: existing ContentMetadata construction without security fields still works
"""

import pytest

from agentic_core.knowledge.ingestion.modality_types import (
    ContentMetadata,
    ContentType,
    DocumentModality,
    IngestionSecurityError,
)


def _minimal_metadata(**overrides) -> ContentMetadata:
    """Construct a ContentMetadata with minimum required non-security fields."""
    defaults = dict(
        file_path="/tmp/test.txt",
        content_type=ContentType.TEXT,
        modality=DocumentModality.TEXT_ONLY,
        file_size_bytes=100,
        estimated_tokens=50,
    )
    defaults.update(overrides)
    return ContentMetadata(**defaults)


def _secure_metadata(**overrides) -> ContentMetadata:
    """Construct ContentMetadata with all 6 security fields populated."""
    base = _minimal_metadata()
    base.acl_policy_ref = "acl://policy/default"
    base.tenant_id = "tenant-abc"
    base.source_trust_level = "trusted"
    base.classification_label = "internal"
    base.ingestion_authorized_by = "system-ingestion-agent"
    base.scope_boundary = "knowledge-base-alpha"
    for k, v in overrides.items():
        setattr(base, k, v)
    return base


class TestContentMetadataSecurityFieldsExist:
    def test_six_security_fields_present_with_none_defaults(self):
        meta = _minimal_metadata()
        assert hasattr(meta, "acl_policy_ref")
        assert hasattr(meta, "tenant_id")
        assert hasattr(meta, "source_trust_level")
        assert hasattr(meta, "classification_label")
        assert hasattr(meta, "ingestion_authorized_by")
        assert hasattr(meta, "scope_boundary")

    def test_security_fields_default_to_none(self):
        meta = _minimal_metadata()
        assert meta.acl_policy_ref is None
        assert meta.tenant_id is None
        assert meta.source_trust_level is None
        assert meta.classification_label is None
        assert meta.ingestion_authorized_by is None
        assert meta.scope_boundary is None

    def test_existing_construction_without_security_fields_is_non_breaking(self):
        meta = _minimal_metadata()
        assert meta.file_path == "/tmp/test.txt"
        assert meta.content_type == ContentType.TEXT


class TestValidateSecurityFields:
    def test_passes_when_all_six_fields_populated(self):
        meta = _secure_metadata()
        meta.validate_security_fields()

    def test_raises_when_acl_policy_ref_missing(self):
        meta = _secure_metadata(acl_policy_ref=None)
        with pytest.raises(IngestionSecurityError) as exc:
            meta.validate_security_fields()
        assert "acl_policy_ref" in str(exc.value)

    def test_raises_when_tenant_id_missing(self):
        meta = _secure_metadata(tenant_id=None)
        with pytest.raises(IngestionSecurityError) as exc:
            meta.validate_security_fields()
        assert "tenant_id" in str(exc.value)

    def test_raises_when_source_trust_level_missing(self):
        meta = _secure_metadata(source_trust_level=None)
        with pytest.raises(IngestionSecurityError) as exc:
            meta.validate_security_fields()
        assert "source_trust_level" in str(exc.value)

    def test_raises_when_classification_label_missing(self):
        meta = _secure_metadata(classification_label=None)
        with pytest.raises(IngestionSecurityError) as exc:
            meta.validate_security_fields()
        assert "classification_label" in str(exc.value)

    def test_raises_when_ingestion_authorized_by_missing(self):
        meta = _secure_metadata(ingestion_authorized_by=None)
        with pytest.raises(IngestionSecurityError) as exc:
            meta.validate_security_fields()
        assert "ingestion_authorized_by" in str(exc.value)

    def test_raises_when_scope_boundary_missing(self):
        meta = _secure_metadata(scope_boundary=None)
        with pytest.raises(IngestionSecurityError) as exc:
            meta.validate_security_fields()
        assert "scope_boundary" in str(exc.value)

    def test_error_message_lists_all_missing_fields_when_all_absent(self):
        meta = _minimal_metadata()
        with pytest.raises(IngestionSecurityError) as exc:
            meta.validate_security_fields()
        msg = str(exc.value)
        for field in (
            "acl_policy_ref",
            "tenant_id",
            "source_trust_level",
            "classification_label",
            "ingestion_authorized_by",
            "scope_boundary",
        ):
            assert field in msg

    def test_raises_ingestion_security_error_not_generic_exception(self):
        meta = _minimal_metadata()
        with pytest.raises(IngestionSecurityError):
            meta.validate_security_fields()

    def test_ingestion_security_error_is_value_error_subclass(self):
        meta = _minimal_metadata()
        with pytest.raises(ValueError):
            meta.validate_security_fields()

    def test_empty_string_fields_treated_as_missing(self):
        meta = _secure_metadata(acl_policy_ref="")
        with pytest.raises(IngestionSecurityError) as exc:
            meta.validate_security_fields()
        assert "acl_policy_ref" in str(exc.value)

    def test_whitespace_only_field_treated_as_missing(self):
        meta = _secure_metadata(tenant_id="   ")
        with pytest.raises(IngestionSecurityError) as exc:
            meta.validate_security_fields()
        assert "tenant_id" in str(exc.value)


class TestToDict:
    def test_to_dict_includes_all_six_security_fields(self):
        meta = _secure_metadata()
        d = meta.to_dict()
        assert d["acl_policy_ref"] == "acl://policy/default"
        assert d["tenant_id"] == "tenant-abc"
        assert d["source_trust_level"] == "trusted"
        assert d["classification_label"] == "internal"
        assert d["ingestion_authorized_by"] == "system-ingestion-agent"
        assert d["scope_boundary"] == "knowledge-base-alpha"

    def test_to_dict_with_none_security_fields_serialises_as_none(self):
        meta = _minimal_metadata()
        d = meta.to_dict()
        assert d["acl_policy_ref"] is None
        assert d["tenant_id"] is None
        assert d["scope_boundary"] is None
