"""Contract tests for apps_exec FEC producer.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-exec-c0-fec-producer-wiring-c2e8a5.md`` W1.P3.
"""

from __future__ import annotations

import pytest


def test_import_registers_producer() -> None:
    import importlib

    from apps_shared.cert.fec_producer import _noop_producer, clear_registry, get_producer

    clear_registry()
    assert get_producer("apps_exec") is _noop_producer
    # Force re-execution of the register_producer side-effect even when the
    # module is already cached in sys.modules (xdist + sibling tests import it).
    import apps_exec.cert as _cert  # noqa: PLC0415

    importlib.reload(_cert)

    assert get_producer("apps_exec") is not _noop_producer


def test_template_only_path() -> None:
    from apps_exec.cert.fec_producer import produce_fec

    fec = produce_fec({})
    assert fec["schema_version"] == "1.0"
    assert fec["producer"] == "apps_exec.cert.fec_producer"
    assert fec["grounded"] is False
    assert fec["template_ids"] == ["exec_brief_v1"]
    assert fec["retrieval_sources"] == []
    assert fec["route_id"] == "apps_exec.execution_v1"
    assert fec["evidence_sufficiency"] == "template_only"


def test_grounded_path_via_research_snippets() -> None:
    from apps_exec.cert.fec_producer import produce_fec

    fec = produce_fec({"research_snippets": ["s1", "s2", "s2"]})
    assert fec["grounded"] is True
    assert fec["retrieval_sources"] == ["s1", "s2"]
    assert fec["evidence_sufficiency"] == "grounded"


def test_explicit_c0_retrieval_sources_wins() -> None:
    from apps_exec.cert.fec_producer import produce_fec

    fec = produce_fec(
        {"c0_retrieval_sources": ["override"], "research_snippets": ["other"]}
    )
    assert fec["retrieval_sources"] == ["override"]


def test_malformed_inputs_never_raise() -> None:
    from apps_exec.cert.fec_producer import produce_fec

    assert isinstance(produce_fec(None), dict)  # type: ignore[arg-type]
    fec = produce_fec({"template_ids": 42, "research_snippets": "not-a-list"})
    assert fec["template_ids"] == ["exec_brief_v1"]
    assert fec["retrieval_sources"] == []


def test_resolver_round_trip() -> None:
    from apps_shared.cert.fec_producer import clear_registry, register_producer, resolve_fec
    from apps_exec.cert.fec_producer import produce_fec

    clear_registry()
    register_producer("apps_exec", produce_fec)
    fec = resolve_fec("apps_exec", {})
    assert fec["producer"] == "apps_exec.cert.fec_producer"


def test_distinct_return_per_call() -> None:
    from apps_exec.cert.fec_producer import produce_fec

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
