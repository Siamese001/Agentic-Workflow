"""Contract tests for apps_research FEC producer.

Plan: ``.windsurf/plans/apps-research-c0-fec-producer-wiring-e7a2c3.md`` W1.P3.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest


def test_import_registers_producer() -> None:
    import importlib

    from apps_shared.cert.fec_producer import _noop_producer, clear_registry, get_producer

    clear_registry()
    assert get_producer("apps_research") is _noop_producer
    # Force re-execution of the register_producer side-effect even when the
    # modules are already cached. Reload BOTH the cert package AND the
    # fec_producer submodule — reloading only the package doesn't re-run the
    # submodule's __init__, and the submodule is where the registration lives.
    import apps_research.cert as _cert  # noqa: PLC0415
    import apps_research.cert.fec_producer as _cert_fec  # noqa: PLC0415

    importlib.reload(_cert_fec)
    importlib.reload(_cert)

    assert get_producer("apps_research") is not _noop_producer


def test_template_only_path() -> None:
    from apps_research.cert.fec_producer import produce_fec

    fec = produce_fec({})
    assert fec["schema_version"] == "1.1"
    assert fec["producer"] == "apps_research.cert.fec_producer"
    assert fec["grounded"] is False
    assert fec["template_ids"] == ["company_brief_v1"]
    assert fec["retrieval_sources"] == []
    assert fec["route_id"] == "apps_research.company_brief_v1"
    assert fec["evidence_sufficiency"] == "template_only"


def test_grounded_path_via_hop_citations() -> None:
    from apps_research.cert.fec_producer import produce_fec

    fec = produce_fec({"hop_citations": ["https://acme.com/about", "crunchbase:acme", "crunchbase:acme"]})
    assert fec["grounded"] is True
    assert fec["retrieval_sources"] == ["https://acme.com/about", "crunchbase:acme"]
    assert fec["evidence_sufficiency"] == "grounded"


def test_grounded_path_via_research_result_attr() -> None:
    from apps_research.cert.fec_producer import produce_fec

    result = SimpleNamespace(hop_citations=["doc_a", "doc_b"])
    fec = produce_fec({"research_result": result})
    assert fec["retrieval_sources"] == ["doc_a", "doc_b"]


def test_explicit_c0_retrieval_sources_wins() -> None:
    from apps_research.cert.fec_producer import produce_fec

    fec = produce_fec(
        {"c0_retrieval_sources": ["override"], "hop_citations": ["other"]}
    )
    assert fec["retrieval_sources"] == ["override"]


def test_malformed_inputs_never_raise() -> None:
    from apps_research.cert.fec_producer import produce_fec

    assert isinstance(produce_fec(None), dict)  # type: ignore[arg-type]
    fec = produce_fec({"hop_citations": 42, "research_result": "not-an-object"})
    assert fec["retrieval_sources"] == []


def test_resolver_round_trip() -> None:
    from apps_shared.cert.fec_producer import clear_registry, register_producer, resolve_fec
    from apps_research.cert.fec_producer import produce_fec

    clear_registry()
    register_producer("apps_research", produce_fec)
    fec = resolve_fec("apps_research", {})
    assert fec["producer"] == "apps_research.cert.fec_producer"


def test_distinct_return_per_call() -> None:
    from apps_research.cert.fec_producer import produce_fec

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
