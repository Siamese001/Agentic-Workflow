"""Per-status doctrine value-set binding tests.

Proves: every doctrine `<x>_status = a | b | c` declaration produces a
``StrEnum`` exposed through ``STATUS_ENUM_REGISTRY``, and the
corresponding ``L5Status`` subclass rejects values outside the doctrine
set at construction time.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from agentic_core.L5_safety.contracts import (
    CONTRACT_REGISTRY,
    STATUS_ENUM_REGISTRY,
)
from agentic_core.L5_safety.contracts._status_enums import (
    ClassificationStatus,
)

REPO = pathlib.Path(__file__).resolve().parents[4]
SRC_JSON = REPO / "tools" / "l5_contracts" / "_l5_status_enums.json"


@pytest.fixture(scope="module")
def doctrine_payload() -> dict:
    return json.loads(SRC_JSON.read_text(encoding="utf-8"))


def test_every_doctrine_status_field_has_an_enum(doctrine_payload: dict) -> None:
    for field_name, values in doctrine_payload["enums"].items():
        assert field_name in STATUS_ENUM_REGISTRY, (
            f"Doctrine status field {field_name!r} has no enum binding."
        )
        enum = STATUS_ENUM_REGISTRY[field_name]
        actual = {e.value for e in enum}
        assert set(values) == actual, f"{field_name}: doctrine values {values} != enum values {actual}"


def test_status_subclass_rejects_value_outside_doctrine() -> None:
    cls = CONTRACT_REGISTRY["classification_status"]
    # Valid value constructs cleanly.
    inst = cls(status_value=ClassificationStatus.CLASSIFIED.value)
    assert inst.status_value == "classified"

    # Invalid value raises at __post_init__.
    with pytest.raises(ValueError, match="not in doctrine value set"):
        cls(status_value="bogus_value")


def test_default_empty_status_value_is_allowed() -> None:
    """Empty default is permitted so smoke parametrization still works."""
    cls = CONTRACT_REGISTRY["classification_status"]
    inst = cls()  # no status_value -> ""
    assert inst.status_value == ""


def test_every_status_subclass_has_value_set_classvar() -> None:
    """Every L5Status subclass whose canonical name is a doctrine status
    field must expose ``allowed_values`` and ``value_enum`` ClassVars.
    """
    miss: list[str] = []
    for field_name in STATUS_ENUM_REGISTRY:
        cls = CONTRACT_REGISTRY.get(field_name)
        if cls is None:
            miss.append(f"{field_name}: no contract class")
            continue
        if not hasattr(cls, "allowed_values"):
            miss.append(f"{field_name}: missing allowed_values ClassVar")
        if not hasattr(cls, "value_enum"):
            miss.append(f"{field_name}: missing value_enum ClassVar")
    assert miss == [], "\n".join(miss)


def test_registry_size_matches_doctrine_extraction(doctrine_payload: dict) -> None:
    assert len(STATUS_ENUM_REGISTRY) == len(doctrine_payload["enums"])
    assert len(STATUS_ENUM_REGISTRY) == 53  # 51 prior + certification_status + match_status from 00A.8
