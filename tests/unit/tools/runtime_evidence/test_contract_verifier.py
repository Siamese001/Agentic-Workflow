"""Unit tests for the Pact-style REQ Coverage Contract verifier."""
from __future__ import annotations

import sqlite3
import time

import pytest

yaml = pytest.importorskip("yaml")

from tools.runtime_evidence.contract_verifier import (  # noqa: E402
    load_contracts,
    verify_all,
    verify_one,
)
from tools.runtime_evidence.ledger_writer import (  # noqa: E402
    ensure_schema,
    write_emissions,
)


def _write_contract(dirpath, req_id, **overrides):
    payload = {
        "req_id": req_id,
        "description": f"test contract for {req_id}",
        "status": "experimental",
        "freshness_sla_days": 7,
        "expects_spans": {
            "layers": ["L6_OBSERVABILITY"],
            "apps": ["apps_rg"],
            "edge_kinds": ["test_edge"],
            "min_count_per_run": 1,
            "must_carry_trace_id": True,
        },
    }
    for k, v in overrides.items():
        if k == "expects_spans":
            payload["expects_spans"].update(v)
        else:
            payload[k] = v
    path = dirpath / f"{req_id}.contract.yaml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    return path


def _spans_for(req_id, *, layer="L6_OBSERVABILITY", edge_kind="test_edge",
               app="apps_rg", trace_id="t1", observed_at=None):
    return [
        {
            "name": f"adg.{edge_kind}",
            "trace_id": trace_id,
            "attributes": {
                "agentic.req.ids": [req_id],
                "agentic.req.layer": layer,
                "agentic.req.edge_kind": edge_kind,
            },
            "observed_at": observed_at or int(time.time()),
        },
    ]


def test_load_contracts_finds_yaml(tmp_path):
    _write_contract(tmp_path, "REQ-T-1")
    _write_contract(tmp_path, "REQ-T-2")
    contracts = load_contracts(tmp_path)
    assert len(contracts) == 2
    ids = {c["req_id"] for c in contracts}
    assert ids == {"REQ-T-1", "REQ-T-2"}


def test_verify_one_pass(tmp_path):
    cdir = tmp_path / "contracts"
    cdir.mkdir()
    _write_contract(cdir, "REQ-T-1")
    ledger = tmp_path / "ledger.sqlite"
    write_emissions(_spans_for("REQ-T-1"), app_id="apps_rg", source="test", db_path=ledger)
    contracts = load_contracts(cdir)
    result = verify_one(contracts[0], ledger_path=ledger)
    assert result.status == "PASS"
    assert result.matches_in_window == 1


def test_verify_one_empty(tmp_path):
    cdir = tmp_path / "contracts"
    cdir.mkdir()
    _write_contract(cdir, "REQ-T-1")
    ledger = tmp_path / "ledger.sqlite"
    ensure_schema(ledger)  # empty
    contracts = load_contracts(cdir)
    result = verify_one(contracts[0], ledger_path=ledger)
    assert result.status == "EMPTY"


def test_verify_one_stale(tmp_path):
    cdir = tmp_path / "contracts"
    cdir.mkdir()
    _write_contract(cdir, "REQ-T-1", freshness_sla_days=1)
    ledger = tmp_path / "ledger.sqlite"
    old_ts = int(time.time()) - 30 * 24 * 3600
    write_emissions(
        _spans_for("REQ-T-1", observed_at=old_ts),
        app_id="apps_rg", source="test", db_path=ledger,
    )
    contracts = load_contracts(cdir)
    result = verify_one(contracts[0], ledger_path=ledger)
    assert result.status == "STALE"


def test_verify_one_fail_on_layer_mismatch(tmp_path):
    cdir = tmp_path / "contracts"
    cdir.mkdir()
    _write_contract(cdir, "REQ-T-1", expects_spans={"layers": ["L0_ROUTING"]})
    ledger = tmp_path / "ledger.sqlite"
    write_emissions(
        _spans_for("REQ-T-1", layer="L6_OBSERVABILITY"),
        app_id="apps_rg", source="test", db_path=ledger,
    )
    contracts = load_contracts(cdir)
    result = verify_one(contracts[0], ledger_path=ledger)
    assert result.status == "FAIL"
    assert any("expected layers" in n for n in result.notes)


def test_verify_one_fail_on_min_count(tmp_path):
    cdir = tmp_path / "contracts"
    cdir.mkdir()
    _write_contract(cdir, "REQ-T-1", expects_spans={"min_count_per_run": 5})
    ledger = tmp_path / "ledger.sqlite"
    write_emissions(_spans_for("REQ-T-1"), app_id="apps_rg", source="test", db_path=ledger)
    contracts = load_contracts(cdir)
    result = verify_one(contracts[0], ledger_path=ledger)
    assert result.status == "FAIL"
    assert any("min_count" in n for n in result.notes)


def test_verify_all_summary(tmp_path):
    cdir = tmp_path / "contracts"
    cdir.mkdir()
    _write_contract(cdir, "REQ-T-PASS")
    _write_contract(cdir, "REQ-T-EMPTY")  # no ledger writes
    ledger = tmp_path / "ledger.sqlite"
    write_emissions(_spans_for("REQ-T-PASS"), app_id="apps_rg", source="test", db_path=ledger)
    summary = verify_all(cdir, ledger)
    assert summary["total"] == 2
    by_status = summary["by_status"]
    assert by_status.get("PASS") == 1
    assert by_status.get("EMPTY") == 1
    # An EMPTY-experimental contract is acceptable, so overall ok=True.
    assert summary["ok"] is True


def test_verify_all_fails_when_stable_is_empty(tmp_path):
    cdir = tmp_path / "contracts"
    cdir.mkdir()
    _write_contract(cdir, "REQ-T-STABLE-EMPTY", status="stable")
    ledger = tmp_path / "ledger.sqlite"
    ensure_schema(ledger)
    summary = verify_all(cdir, ledger)
    assert summary["ok"] is False
    assert any(r["req_id"] == "REQ-T-STABLE-EMPTY" for r in summary["failures"])
