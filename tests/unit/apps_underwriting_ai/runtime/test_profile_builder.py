"""Wave 5 ADG testing-hotspots — apps_underwriting_ai.runtime.profile_builder.

``parse_payload`` is a pure dict -> UnderwritingIngressEnvelope | None transform
implementing the AppRuntimeProfile.parse contract; it has many branches
(non-dict input, missing required fields, document/metadata normalization,
generated ids). ``build_app_runtime_contract`` wires the AppRuntimeProfile with
all 7 stage refs. This module covers the parse branches, the required-fields
constant, and the assembled profile shape. No mocks.
"""

from __future__ import annotations

from apps_underwriting_ai.runtime.profile_builder import (
    UW_REQUIRED_FIELDS,
    build_app_runtime_contract,
    parse_payload,
)


class TestRequiredFields:
    def test_required_fields_constant(self):
        assert UW_REQUIRED_FIELDS == ("applicant_id", "product_class")


class TestParsePayloadRejection:
    def test_non_dict_returns_none(self):
        assert parse_payload("not a dict") is None  # type: ignore[arg-type]

    def test_missing_applicant_id_returns_none(self):
        assert parse_payload({"product_class": "auto"}) is None

    def test_missing_product_class_returns_none(self):
        assert parse_payload({"applicant_id": "a1"}) is None

    def test_empty_string_fields_return_none(self):
        assert parse_payload({"applicant_id": "", "product_class": ""}) is None


class TestParsePayloadSuccess:
    def test_minimal_valid_payload(self):
        env = parse_payload({"applicant_id": "a1", "product_class": "auto"})
        assert env is not None
        assert env.applicant_id == "a1"
        assert env.product_class == "auto"

    def test_generates_request_and_trace_ids(self):
        env = parse_payload({"applicant_id": "a1", "product_class": "auto"})
        assert env is not None
        assert env.request_id.startswith("uw-req-")
        assert env.trace_id.startswith("uw-trace-")
        assert env.submitted_at  # auto-filled ISO timestamp

    def test_preserves_supplied_ids(self):
        env = parse_payload(
            {
                "applicant_id": "a1",
                "product_class": "auto",
                "request_id": "REQ-9",
                "trace_id": "TRACE-9",
            }
        )
        assert env is not None
        assert env.request_id == "REQ-9"
        assert env.trace_id == "TRACE-9"

    def test_documents_filtered_to_dicts(self):
        env = parse_payload(
            {
                "applicant_id": "a1",
                "product_class": "auto",
                "documents": [{"k": 1}, "bad", 42, {"k": 2}],
            }
        )
        assert env is not None
        assert env.documents == ({"k": 1}, {"k": 2})

    def test_non_list_documents_normalized_to_empty(self):
        env = parse_payload(
            {"applicant_id": "a1", "product_class": "auto", "documents": "oops"}
        )
        assert env is not None
        assert env.documents == ()

    def test_non_dict_metadata_normalized_to_empty(self):
        env = parse_payload(
            {"applicant_id": "a1", "product_class": "auto", "metadata": ["bad"]}
        )
        assert env is not None
        assert env.metadata == {}

    def test_metadata_preserved(self):
        env = parse_payload(
            {"applicant_id": "a1", "product_class": "auto", "metadata": {"region": "EU"}}
        )
        assert env is not None
        assert env.metadata == {"region": "EU"}


class TestBuildAppRuntimeContract:
    def test_app_id_and_required_fields(self):
        profile = build_app_runtime_contract()
        assert profile.app_id == "apps_underwriting_ai"
        assert profile.required_fields == UW_REQUIRED_FIELDS
        assert profile.profile_version == "1"

    def test_all_seven_stage_refs_wired(self):
        profile = build_app_runtime_contract()
        for stage in ("u0", "l1", "l0", "c0", "pa", "l2", "exit"):
            assert getattr(profile, stage) is not None, stage

    def test_parse_ref_is_module_parse_payload(self):
        profile = build_app_runtime_contract()
        assert profile.parse is parse_payload
