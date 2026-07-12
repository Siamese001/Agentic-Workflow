"""Deterministic tests for the ADG metric contract registry."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ops_scripts.ci.check_adg_metric_registry import main as check_registry_main
from tools.adg.contracts.metric_registry import (
    DEFAULT_METRIC_REGISTRY,
    MetricRegistryError,
    load_metric_registry,
    validate_registry_document,
)


def _document() -> dict:
    return json.loads(DEFAULT_METRIC_REGISTRY.read_text(encoding="utf-8"))


def test_default_registry_is_valid_and_has_unique_ids() -> None:
    contracts = load_metric_registry()
    assert contracts
    assert len({contract.metric_id for contract in contracts}) == len(contracts)
    assert validate_registry_document(_document()) == ()


def test_every_contract_has_evidence_and_remediation() -> None:
    for contract in load_metric_registry():
        assert contract.evidence_query.startswith(("SELECT ", "WITH "))
        assert contract.key_columns
        assert contract.value_columns
        assert contract.consumers
        assert contract.remediation


def test_duplicate_metric_id_is_rejected() -> None:
    document = _document()
    duplicate = copy.deepcopy(document["metrics"][0])
    duplicate_id = duplicate["metric_id"]
    document["metrics"].append(duplicate)
    errors = validate_registry_document(document)
    assert any(
        f"duplicates {duplicate_id}" in error
        for error in errors
    )


def test_missing_contract_field_is_rejected() -> None:
    document = _document()
    del document["metrics"][0]["remediation"]
    errors = validate_registry_document(document)
    assert any("missing fields: remediation" in error for error in errors)


def test_unknown_contract_field_is_rejected() -> None:
    document = _document()
    document["metrics"][0]["shadow_authority"] = True
    errors = validate_registry_document(document)
    assert any("unknown fields: shadow_authority" in error for error in errors)


def test_unsupported_exactness_is_rejected() -> None:
    document = _document()
    document["metrics"][0]["exactness"] = "probably_exact"
    errors = validate_registry_document(document)
    assert any("exactness must be one of" in error for error in errors)


def test_mutating_evidence_query_is_rejected() -> None:
    document = _document()
    document["metrics"][0]["evidence_query"] = "DELETE FROM mv_snapshot_regression_summary"
    errors = validate_registry_document(document)
    assert any("read-only SELECT SQL" in error for error in errors)
    assert any("non-read-only SQL" in error for error in errors)


def test_load_invalid_registry_raises(tmp_path: Path) -> None:
    invalid_path = tmp_path / "invalid_metric_registry.json"
    document = _document()
    document["metrics"][0]["minimum_sample_size"] = -1
    invalid_path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(MetricRegistryError, match="minimum_sample_size"):
        load_metric_registry(invalid_path)


def test_ci_entrypoint_accepts_default_registry() -> None:
    assert check_registry_main(["check_adg_metric_registry.py"]) == 0


def test_ci_entrypoint_rejects_invalid_registry(tmp_path: Path) -> None:
    invalid_path = tmp_path / "invalid_metric_registry.json"
    invalid_path.write_text("{}", encoding="utf-8")
    assert check_registry_main(["check_adg_metric_registry.py", str(invalid_path)]) == 1
