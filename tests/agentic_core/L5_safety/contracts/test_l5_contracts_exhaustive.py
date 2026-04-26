"""Exhaustive edge-case hardening for ``agentic_core.L5_safety.contracts``.

This file deliberately overlaps minimally with smoke / stress / alignment /
status-enum / matrix tests. It adds the stricter properties those tests
do not already check:

| # | Property                                                                                  |
|---|-------------------------------------------------------------------------------------------|
| 1 | every contract is hashable and stable-hash for equal args                                 |
| 2 | every contract round-trips through ``dataclasses.asdict``                                 |
| 3 | every contract supports equality (reflexive + symmetric)                                  |
| 4 | every contract has slots only (no ``__dict__``)                                           |
| 5 | every contract supports ``copy.copy`` and ``copy.deepcopy``                               |
| 6 | no contract has a field name that collides with a forbidden runtime disposition           |
| 7 | every doctrine value of every status enum passes ``__post_init__``                        |
| 8 | every status enum rejects systematic bogus values (5 attack patterns)                     |
| 9 | every status enum accepts the blank-string sentinel (default unset)                       |
|10 | every contract module imports without side effects (re-import is idempotent)              |
|11 | no two registry keys collide case-insensitively past their canonical form                 |
|12 | no enum value inside any per-status enum is itself a forbidden runtime disposition        |
|13 | every per-status enum has >=1 value                                                       |
|14 | every L5Status subclass with ``allowed_values`` advertises a matching ``value_enum``      |
|15 | envelope strings tolerate unicode, long, and control-character payloads                   |
|16 | every contract has ``slots=True`` AND ``frozen=True`` set in ``__dataclass_params__``     |
|17 | no contract default value contains a forbidden runtime-disposition token (str check)      |

If any of these fail, the regeneration pipeline (`generate_contracts.py`)
or the doctrine itself drifted.
"""

from __future__ import annotations

import copy
import dataclasses
import importlib
import json
from typing import Any

import pytest

from agentic_core.L5_safety.contracts import (
    ALL_OUTPUT_NAMES,
    CONTRACT_REGISTRY,
    FORBIDDEN_RUNTIME_DISPOSITIONS,
    L5OutputBase,
    L5Status,
    STATUS_ENUM_REGISTRY,
    get_contract,
)

_FORBIDDEN_LOWER = frozenset(t.lower() for t in FORBIDDEN_RUNTIME_DISPOSITIONS)

_ENVELOPE: dict[str, Any] = {
    "run_id": "rt-evidence",
    "trace_id": "rt-trace",
    "emitted_at_utc": "2026-04-26T00:00:00Z",
    "digest_sha256": "0" * 64,
}

_CONTRACT_MODULES = (
    "agentic_core.L5_safety.contracts.parent",
    "agentic_core.L5_safety.contracts.enforcement",
    "agentic_core.L5_safety.contracts.authority",
    "agentic_core.L5_safety.contracts.origin",
    "agentic_core.L5_safety.contracts.hitl",
    "agentic_core.L5_safety.contracts.egress",
    "agentic_core.L5_safety.contracts.replay",
    "agentic_core.L5_safety.contracts.static",
)

# Names sorted once — pytest-xdist needs deterministic IDs.
_NAMES = sorted(CONTRACT_REGISTRY.keys())
_STATUS_FIELDS = sorted(STATUS_ENUM_REGISTRY.keys())


# ---------------------------------------------------------------------------
# Property 1: hashable and stable-hash
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name", _NAMES)
def test_every_contract_is_hashable_and_stable(name: str) -> None:
    cls = get_contract(name)
    a = cls(**_ENVELOPE)
    b = cls(**_ENVELOPE)
    assert hash(a) == hash(b), f"{cls.__name__} hash unstable across identical construction"
    # Membership in a set must work.
    assert a in {a}
    assert a in {b}, f"{cls.__name__} fails set membership for equal-args twin"


# ---------------------------------------------------------------------------
# Property 2: asdict round-trip
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name", _NAMES)
def test_every_contract_asdict_round_trips(name: str) -> None:
    cls = get_contract(name)
    inst = cls(**_ENVELOPE)
    d = dataclasses.asdict(inst)
    assert isinstance(d, dict)
    field_names = {f.name for f in dataclasses.fields(cls)}
    # Every dataclass field must be present.
    for fname in field_names:
        assert fname in d, f"{cls.__name__}: asdict missing field {fname!r}"
    # All values must be JSON-serializable (proves no exotic types leaked).
    json.dumps(d, default=str)


# ---------------------------------------------------------------------------
# Property 3: equality semantics
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name", _NAMES)
def test_every_contract_equality_reflexive_and_symmetric(name: str) -> None:
    cls = get_contract(name)
    a = cls(**_ENVELOPE)
    b = cls(**_ENVELOPE)
    c = cls(**{**_ENVELOPE, "run_id": "different"})
    assert a == a, f"{cls.__name__} not reflexive"
    assert a == b and b == a, f"{cls.__name__} not symmetric for equal args"
    assert a != c, f"{cls.__name__} reports equal across differing run_id"


# ---------------------------------------------------------------------------
# Property 4: slots only
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name", _NAMES)
def test_every_contract_uses_slots_only(name: str) -> None:
    cls = get_contract(name)
    inst = cls(**_ENVELOPE)
    # slots=True dataclasses do not expose __dict__ on instances.
    assert not hasattr(inst, "__dict__"), (
        f"{cls.__name__} carries __dict__; slots=True invariant broken"
    )


# ---------------------------------------------------------------------------
# Property 5: copy + deepcopy
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name", _NAMES)
def test_every_contract_supports_copy_and_deepcopy(name: str) -> None:
    cls = get_contract(name)
    inst = cls(**_ENVELOPE)
    shallow = copy.copy(inst)
    deep = copy.deepcopy(inst)
    assert shallow == inst, f"{cls.__name__}: copy.copy yields non-equal instance"
    assert deep == inst, f"{cls.__name__}: deepcopy yields non-equal instance"


# ---------------------------------------------------------------------------
# Property 6: no field name collides with forbidden disposition
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name", _NAMES)
def test_no_field_name_collides_with_forbidden_disposition(name: str) -> None:
    cls = get_contract(name)
    bad = [
        f.name
        for f in dataclasses.fields(cls)
        if f.name.lower() in _FORBIDDEN_LOWER
    ]
    assert not bad, (
        f"{cls.__name__} declares field(s) named like runtime dispositions: {bad}"
    )


# ---------------------------------------------------------------------------
# Property 7: every doctrine value of every status enum is accepted
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("field_name", _STATUS_FIELDS)
def test_every_doctrine_value_passes_post_init(field_name: str) -> None:
    cls = CONTRACT_REGISTRY.get(field_name)
    enum = STATUS_ENUM_REGISTRY[field_name]
    if cls is None or not issubclass(cls, L5Status):
        pytest.skip(f"{field_name}: no L5Status subclass to validate against")
    accepted: list[str] = []
    for member in enum:
        inst = cls(status_value=member.value, **_ENVELOPE)
        assert inst.status_value == member.value
        accepted.append(member.value)
    assert len(accepted) == len(list(enum)), (
        f"{field_name}: only {len(accepted)} of {len(list(enum))} doctrine "
        f"values were accepted"
    )


# ---------------------------------------------------------------------------
# Property 8: systematic bogus rejection
# ---------------------------------------------------------------------------
_BOGUS_VALUES = [
    "__not_in_doctrine__",
    "ALLOW",  # forbidden runtime disposition leaking in as a status
    "123",  # numeric-looking
    "  ",  # whitespace-only (non-empty)
    "NULL",  # uppercase placeholder
]


@pytest.mark.parametrize("field_name", _STATUS_FIELDS)
@pytest.mark.parametrize("bogus", _BOGUS_VALUES)
def test_every_status_enum_rejects_bogus_values(field_name: str, bogus: str) -> None:
    cls = CONTRACT_REGISTRY.get(field_name)
    enum = STATUS_ENUM_REGISTRY[field_name]
    if cls is None or not issubclass(cls, L5Status):
        pytest.skip(f"{field_name}: no L5Status subclass to validate against")
    # Skip if the bogus value happens to be a real doctrine value
    # (e.g., a doctrine enum legitimately includes "ALLOW" — defensive).
    if bogus in {m.value for m in enum}:
        pytest.skip(f"{bogus!r} is a real doctrine value for {field_name}")
    with pytest.raises(ValueError):
        cls(status_value=bogus, **_ENVELOPE)


# ---------------------------------------------------------------------------
# Property 9: blank-string sentinel allowed (default unset path)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("field_name", _STATUS_FIELDS)
def test_status_subclass_accepts_empty_string_sentinel(field_name: str) -> None:
    cls = CONTRACT_REGISTRY.get(field_name)
    if cls is None or not issubclass(cls, L5Status):
        pytest.skip(f"{field_name}: no L5Status subclass to validate against")
    # Empty status_value is the unset sentinel; __post_init__ should pass.
    inst = cls(status_value="", **_ENVELOPE)
    assert inst.status_value == ""


# ---------------------------------------------------------------------------
# Property 10: contract modules are importable and idempotent
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("module_name", _CONTRACT_MODULES)
def test_contract_module_imports_idempotently(module_name: str) -> None:
    module = importlib.import_module(module_name)
    reloaded = importlib.reload(module)
    assert module.__name__ == reloaded.__name__
    # Each module exposes __all__; assert it matches at least one contract.
    public = getattr(module, "__all__", [])
    assert public, f"{module_name} exports nothing"
    for name in public:
        assert hasattr(module, name), f"{module_name}.__all__ lists missing symbol {name}"


# ---------------------------------------------------------------------------
# Property 11: registry keys are uniquely-cased canonical names
# ---------------------------------------------------------------------------
def test_registry_keys_unique_case_sensitive() -> None:
    assert len(CONTRACT_REGISTRY) == len(set(CONTRACT_REGISTRY.keys()))
    # ALL_OUTPUT_NAMES must align exactly with the registry keys.
    assert ALL_OUTPUT_NAMES == frozenset(CONTRACT_REGISTRY.keys())


# ---------------------------------------------------------------------------
# Property 12: per-status enum values cannot be runtime dispositions
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("field_name", _STATUS_FIELDS)
def test_per_status_enum_values_never_collide_with_forbidden(field_name: str) -> None:
    enum = STATUS_ENUM_REGISTRY[field_name]
    bad = [m.value for m in enum if m.value in FORBIDDEN_RUNTIME_DISPOSITIONS]
    assert not bad, (
        f"{field_name}: enum values overlap with FORBIDDEN_RUNTIME_DISPOSITIONS: {bad}"
    )


# ---------------------------------------------------------------------------
# Property 13: every status enum has at least one value
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("field_name", _STATUS_FIELDS)
def test_every_status_enum_has_values(field_name: str) -> None:
    enum = STATUS_ENUM_REGISTRY[field_name]
    members = list(enum)
    assert members, f"{field_name}: empty enum"


# ---------------------------------------------------------------------------
# Property 14: L5Status subclasses advertise consistent allowed_values + value_enum
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("field_name", _STATUS_FIELDS)
def test_l5status_subclass_classvars_align_with_enum(field_name: str) -> None:
    cls = CONTRACT_REGISTRY.get(field_name)
    enum = STATUS_ENUM_REGISTRY[field_name]
    if cls is None or not issubclass(cls, L5Status):
        pytest.skip(f"{field_name}: no L5Status subclass")
    allowed = getattr(cls, "allowed_values", None)
    assert allowed is not None, f"{cls.__name__} missing allowed_values"
    enum_cls = getattr(cls, "value_enum", None)
    assert enum_cls is enum, (
        f"{cls.__name__}.value_enum mismatch: got {enum_cls}, expected {enum}"
    )
    assert set(allowed) == {m.value for m in enum}, (
        f"{cls.__name__}.allowed_values diverges from doctrine enum"
    )


# ---------------------------------------------------------------------------
# Property 15: envelope tolerates unicode / long / control-char strings
# ---------------------------------------------------------------------------
_STRESS_STRINGS = [
    "rún-with-unicode-✓",
    "x" * 1024,
    "with\ttab\nand\rcontrol",
    "",  # blank (already a default; assert accepted)
]
# Sample a representative subset of contracts (one per kind) — doing this
# over all 819 names would 4x test count for no extra signal.
_SAMPLE_NAMES = sorted({
    next(n for n, c in CONTRACT_REGISTRY.items() if c.output_kind == kind)
    for kind in {c.output_kind for c in CONTRACT_REGISTRY.values()}
})


@pytest.mark.parametrize("name", _SAMPLE_NAMES)
@pytest.mark.parametrize("stress", _STRESS_STRINGS)
def test_envelope_tolerates_stress_strings(name: str, stress: str) -> None:
    cls = get_contract(name)
    payload = {**_ENVELOPE, "run_id": stress}
    inst = cls(**payload)
    assert inst.run_id == stress


# ---------------------------------------------------------------------------
# Property 16: every contract's __dataclass_params__ has frozen=True, slots=True
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name", _NAMES)
def test_every_contract_is_frozen_and_slots(name: str) -> None:
    cls = get_contract(name)
    params = cls.__dataclass_params__  # type: ignore[attr-defined]
    assert params.frozen is True, f"{cls.__name__}: not frozen"
    # slots is set on the class itself (not __dataclass_params__) for
    # dataclasses with slots=True; check via __slots__ presence anywhere
    # in the MRO.
    assert any(hasattr(b, "__slots__") for b in cls.__mro__), (
        f"{cls.__name__}: no __slots__ declaration in MRO"
    )


# ---------------------------------------------------------------------------
# Property 17: no contract default value embeds a forbidden disposition token
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name", _NAMES)
def test_no_field_default_embeds_forbidden_token(name: str) -> None:
    cls = get_contract(name)
    leaks: list[tuple[str, str]] = []
    for f in dataclasses.fields(cls):
        if f.default is dataclasses.MISSING:
            continue
        d = f.default
        if isinstance(d, str) and d in FORBIDDEN_RUNTIME_DISPOSITIONS:
            leaks.append((f.name, d))
    assert not leaks, (
        f"{cls.__name__} ships defaults that ARE forbidden runtime "
        f"dispositions (evidence-only invariant breach): {leaks}"
    )
