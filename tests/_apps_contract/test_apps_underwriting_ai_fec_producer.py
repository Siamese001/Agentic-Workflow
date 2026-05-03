"""Contract tests for apps_underwriting_ai FEC producer.

Plan: ``.windsurf/plans/apps-underwriting-ai-c0-fec-producer-wiring-f6b3d9.md`` W1.P3.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest


def test_import_registers_producer() -> None:
    from apps_shared.cert.fec_producer import _noop_producer, clear_registry, get_producer

    clear_registry()
    assert get_producer("apps_underwriting_ai") is _noop_producer

    import apps_underwriting_ai.cert  # noqa: F401

    resolved = get_producer("apps_underwriting_ai")
    assert resolved is not _noop_producer
    assert callable(resolved)


def test_template_only_path() -> None:
    from apps_underwriting_ai.cert.fec_producer import produce_fec

    fec = produce_fec({"route_id": "apps_underwriting_ai.decision_packet_v1"})
    assert fec["schema_version"] == "1.0"
    assert fec["producer"] == "apps_underwriting_ai.cert.fec_producer"
    assert fec["grounded"] is False
    assert fec["template_ids"] == ["decision_packet_v1"]
    assert fec["retrieval_sources"] == []
    assert fec["route_id"] == "apps_underwriting_ai.decision_packet_v1"
    assert fec["evidence_sufficiency"] == "template_only"


def test_grounded_path_via_register_rows() -> None:
    from apps_underwriting_ai.cert.fec_producer import produce_fec

    uw_result = SimpleNamespace(
        register=SimpleNamespace(
            rows=[
                SimpleNamespace(source_doc="bank_stmt_2024Q1.pdf"),
                SimpleNamespace(source_doc="tax_return_2023.pdf"),
            ]
        )
    )
    fec = produce_fec({"uw_result": uw_result})
    assert fec["grounded"] is True
    assert fec["evidence_sufficiency"] == "grounded"
    assert fec["retrieval_sources"] == ["bank_stmt_2024Q1.pdf", "tax_return_2023.pdf"]


def test_grounded_path_via_statements_fallback() -> None:
    from apps_underwriting_ai.cert.fec_producer import produce_fec

    uw_result = SimpleNamespace(
        register=SimpleNamespace(rows=[]),
        request=SimpleNamespace(
            statements=[SimpleNamespace(document_id="stmt_1"), SimpleNamespace(id="stmt_2")]
        ),
    )
    fec = produce_fec({"uw_result": uw_result})
    assert fec["grounded"] is True
    assert fec["retrieval_sources"] == ["stmt_1", "stmt_2"]


def test_explicit_c0_retrieval_sources_wins() -> None:
    from apps_underwriting_ai.cert.fec_producer import produce_fec

    uw_result = SimpleNamespace(register=SimpleNamespace(rows=[SimpleNamespace(source_doc="A")]))
    fec = produce_fec({"c0_retrieval_sources": ["override.pdf"], "uw_result": uw_result})
    assert fec["retrieval_sources"] == ["override.pdf"]


def test_malformed_inputs_never_raise() -> None:
    from apps_underwriting_ai.cert.fec_producer import produce_fec

    assert isinstance(produce_fec(None), dict)  # type: ignore[arg-type]
    fec = produce_fec({"uw_result": SimpleNamespace()})
    assert fec["evidence_sufficiency"] == "template_only"


def test_resolver_round_trip() -> None:
    from apps_shared.cert.fec_producer import clear_registry, register_producer, resolve_fec
    from apps_underwriting_ai.cert.fec_producer import produce_fec

    clear_registry()
    register_producer("apps_underwriting_ai", produce_fec)

    fec = resolve_fec("apps_underwriting_ai", {})
    assert fec["producer"] == "apps_underwriting_ai.cert.fec_producer"


def test_distinct_return_per_call() -> None:
    from apps_underwriting_ai.cert.fec_producer import produce_fec

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
