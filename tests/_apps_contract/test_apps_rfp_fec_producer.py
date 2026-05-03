"""Contract tests for apps_rfp FEC producer.

Plan: ``.windsurf/plans/apps-rfp-c0-fec-producer-wiring-b9d4f1.md`` W1.P3.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest


def test_import_registers_producer() -> None:
    from apps_shared.cert.fec_producer import _noop_producer, clear_registry, get_producer

    clear_registry()
    assert get_producer("apps_rfp") is _noop_producer
    import apps_rfp.cert  # noqa: F401

    assert get_producer("apps_rfp") is not _noop_producer


def test_template_only_path() -> None:
    from apps_rfp.cert.fec_producer import produce_fec

    fec = produce_fec({})
    assert fec["schema_version"] == "1.0"
    assert fec["producer"] == "apps_rfp.cert.fec_producer"
    assert fec["grounded"] is False
    assert fec["template_ids"] == ["proposal_assembly_v1"]
    assert fec["retrieval_sources"] == []
    assert fec["route_id"] == "apps_rfp.proposal_assembly_v1"
    assert fec["evidence_sufficiency"] == "template_only"


def test_grounded_path_via_sections_cited() -> None:
    from apps_rfp.cert.fec_producer import produce_fec

    fec = produce_fec({"rfp_sections_cited": ["S1.2", "S3.1", "S1.2"]})
    assert fec["grounded"] is True
    assert fec["retrieval_sources"] == ["S1.2", "S3.1"]
    assert fec["evidence_sufficiency"] == "grounded"


def test_grounded_path_via_result_attr() -> None:
    from apps_rfp.cert.fec_producer import produce_fec

    result = SimpleNamespace(sections_cited=["S5.1", "S5.2"])
    fec = produce_fec({"proposal_result": result})
    assert fec["retrieval_sources"] == ["S5.1", "S5.2"]


def test_explicit_c0_retrieval_sources_wins() -> None:
    from apps_rfp.cert.fec_producer import produce_fec

    fec = produce_fec(
        {"c0_retrieval_sources": ["override"], "rfp_sections_cited": ["other"]}
    )
    assert fec["retrieval_sources"] == ["override"]


def test_malformed_inputs_never_raise() -> None:
    from apps_rfp.cert.fec_producer import produce_fec

    assert isinstance(produce_fec(None), dict)  # type: ignore[arg-type]
    fec = produce_fec({"rfp_sections_cited": 42, "proposal_result": "not-an-object"})
    assert fec["retrieval_sources"] == []


def test_resolver_round_trip() -> None:
    from apps_shared.cert.fec_producer import clear_registry, register_producer, resolve_fec
    from apps_rfp.cert.fec_producer import produce_fec

    clear_registry()
    register_producer("apps_rfp", produce_fec)
    fec = resolve_fec("apps_rfp", {})
    assert fec["producer"] == "apps_rfp.cert.fec_producer"


def test_distinct_return_per_call() -> None:
    from apps_rfp.cert.fec_producer import produce_fec

    a = produce_fec({})
    b = produce_fec({})
    assert a == b
    assert a is not b
    a["template_ids"].append("mutated")
    assert "mutated" not in b["template_ids"]


@pytest.fixture(autouse=True)
def _restore_registry():
    from apps_shared.cert.fec_producer import clear_registry

    yield
    clear_registry()
