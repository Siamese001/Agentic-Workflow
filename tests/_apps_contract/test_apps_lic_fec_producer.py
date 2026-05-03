"""Contract tests for apps_lic FEC producer.

Plan: .windsurf/plans/dom007-fec-producers-followup-e9f3c1.md W2.P1.
"""

from __future__ import annotations

import pytest


def test_import_registers_producer() -> None:
    from apps_shared.cert.fec_producer import clear_registry, get_producer, _noop_producer  # noqa: PLC2701

    clear_registry()
    assert get_producer("apps_lic") is _noop_producer

    import apps_lic.cert  # noqa: F401

    resolved = get_producer("apps_lic")
    assert resolved is not _noop_producer
    assert callable(resolved)


def test_grounded_path_with_compliance_passed() -> None:
    from apps_lic.cert.fec_producer import produce_fec

    ctx = {
        "route_id": "apps_lic.outreach_v1",
        "profile_data_sources": ["profile_a.json", "profile_b.json"],
        "template_ids": ["outreach_t1"],
        "compliance_check_status": "passed",
    }
    fec = produce_fec(ctx)
    assert fec["schema_version"] == "1.0"
    assert fec["producer"] == "apps_lic.cert.fec_producer"
    assert fec["grounded"] is True
    assert fec["evidence_sufficiency"] == "grounded"
    assert fec["retrieval_sources"] == ["profile_a.json", "profile_b.json"]
    assert fec["template_ids"] == ["outreach_t1"]
    assert fec["compliance_check_status"] == "passed"


def test_grounded_compliance_pending() -> None:
    from apps_lic.cert.fec_producer import produce_fec

    ctx = {
        "profile_data_sources": ["p1.json"],
        "compliance_check_status": "pending",
    }
    fec = produce_fec(ctx)
    assert fec["grounded"] is True
    assert fec["evidence_sufficiency"] == "grounded_compliance_pending"


def test_template_only_path() -> None:
    from apps_lic.cert.fec_producer import produce_fec

    ctx = {"template_ids": ["t1"]}
    fec = produce_fec(ctx)
    assert fec["grounded"] is False
    assert fec["evidence_sufficiency"] == "template_only"


def test_empty_context_yields_shape_valid_empty() -> None:
    from apps_lic.cert.fec_producer import produce_fec

    fec = produce_fec({})
    assert fec["schema_version"] == "1.0"
    assert fec["grounded"] is False
    assert fec["retrieval_sources"] == []
    assert fec["template_ids"] == []
    assert fec["evidence_sufficiency"] == "empty"
    assert fec["compliance_check_status"] == "not_run"


def test_malformed_inputs_never_raise() -> None:
    from apps_lic.cert.fec_producer import produce_fec

    fec = produce_fec(None)  # type: ignore[arg-type]
    assert isinstance(fec, dict)
    fec = produce_fec({"profile_data_sources": "nope", "template_ids": 42})
    assert fec["retrieval_sources"] == []
    assert fec["template_ids"] == []


def test_resolver_round_trip() -> None:
    from apps_shared.cert.fec_producer import clear_registry, register_producer, resolve_fec
    from apps_lic.cert.fec_producer import produce_fec

    clear_registry()
    register_producer("apps_lic", produce_fec)

    fec = resolve_fec("apps_lic", {"profile_data_sources": ["p.json"], "compliance_check_status": "passed"})
    assert fec["producer"] == "apps_lic.cert.fec_producer"
    assert fec["evidence_sufficiency"] == "grounded"


@pytest.fixture(autouse=True)
def _restore_registry():
    from apps_shared.cert.fec_producer import clear_registry
    yield
    clear_registry()
