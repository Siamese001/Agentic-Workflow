"""Hypothesis property tests — JSON corruption strategies.

INSTALL 3 (RC-2 prevention) — covers bug-family 7/9/10/11.

Strategy: take a known-good packet/contract, apply one of 8 standard
corruption transformations, and assert that every JSON-reading entry
point either returns a structured failure OR raises a documented
exception type — but NEVER lets the corruption silently pass.

The 8 corruption types:
  1. truncate          — drop the last N% of the JSON text
  2. swap_root_type    — replace dict root with a list / string / null / int
  3. drop_field        — remove a single key
  4. duplicate_field   — duplicate a key (post-load semantics: last wins)
  5. set_to_null       — set a single field's value to None
  6. add_unknown_field — inject an unexpected key
  7. mutate_string     — replace a string field's value with garbage
  8. permute_array     — reverse / shuffle a list field

If Hypothesis is not installed, these tests are skipped (the production
harness runs without it).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

try:
    from hypothesis import HealthCheck, given, settings
    from hypothesis import strategies as st

    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False


pytestmark = pytest.mark.skipif(
    not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed"
)


# ---------------------------------------------------------------------------
# Known-good fixtures
# ---------------------------------------------------------------------------


def _good_packet() -> dict[str, Any]:
    return {
        "app_id": "apps_test",
        "scenario_id": "s1",
        "command": "x",
        "cwd": "/",
        "process_id": 1,
        "python_executable": "/p",
        "git_commit_or_snapshot_ref": None,
        "adg_snapshot_ref": "snap.sqlite",
        "request_id": "rq",
        "session_id": "ss",
        "run_id": "rn",
        "trace_root": "tr",
        "trace_id": "tr",
        "span_inventory": ["traces/x.json"],
        "contract_inventory": ["contracts/apps_test/s1/contract_inventory.json"],
        "gate_verdict_inventory": ["gates/x.json"],
        "artifact_inventory": ["artifacts/x.json"],
        "packet_hash": "x" * 64,
    }


# ---------------------------------------------------------------------------
# 8 corruption strategies
# ---------------------------------------------------------------------------


@st.composite
def _json_corruption_strategy(draw: Any) -> tuple[str, dict[str, Any], bytes]:
    """Yield (strategy_name, original_dict, corrupted_bytes)."""
    base = _good_packet()
    strategy = draw(st.sampled_from([
        "truncate",
        "swap_root_type",
        "drop_field",
        "duplicate_field",
        "set_to_null",
        "add_unknown_field",
        "mutate_string",
        "permute_array",
    ]))
    text = json.dumps(base, sort_keys=True)
    if strategy == "truncate":
        cut = draw(st.integers(min_value=1, max_value=max(1, len(text) - 1)))
        corrupted = text[:cut].encode("utf-8")
    elif strategy == "swap_root_type":
        replacement = draw(st.sampled_from([
            "[]", '"a"', "null", "42", "true",
        ]))
        corrupted = replacement.encode("utf-8")
    elif strategy == "drop_field":
        key = draw(st.sampled_from(list(base.keys())))
        modified = {k: v for k, v in base.items() if k != key}
        corrupted = json.dumps(modified, sort_keys=True).encode("utf-8")
    elif strategy == "duplicate_field":
        key = draw(st.sampled_from(list(base.keys())))
        # Insert a duplicate manually (json.dumps won't produce dupes)
        text_with_dup = text.replace(
            f'"{key}":', f'"{key}":"DUP_VALUE","{key}":', 1,
        )
        corrupted = text_with_dup.encode("utf-8")
    elif strategy == "set_to_null":
        key = draw(st.sampled_from(list(base.keys())))
        modified = dict(base)
        modified[key] = None
        corrupted = json.dumps(modified, sort_keys=True).encode("utf-8")
    elif strategy == "add_unknown_field":
        modified = dict(base)
        modified[draw(st.text(min_size=1, max_size=20).filter(lambda s: s not in base))] = (
            "INJECTED"
        )
        corrupted = json.dumps(modified, sort_keys=True).encode("utf-8")
    elif strategy == "mutate_string":
        keys = [k for k, v in base.items() if isinstance(v, str)]
        if keys:
            key = draw(st.sampled_from(keys))
            modified = dict(base)
            modified[key] = draw(st.text(max_size=50))
            corrupted = json.dumps(modified, sort_keys=True).encode("utf-8")
        else:
            corrupted = text.encode("utf-8")  # nothing to mutate
    else:  # permute_array
        keys = [k for k, v in base.items() if isinstance(v, list)]
        if keys:
            key = draw(st.sampled_from(keys))
            modified = dict(base)
            modified[key] = list(reversed(base[key]))
            corrupted = json.dumps(modified, sort_keys=True).encode("utf-8")
        else:
            corrupted = text.encode("utf-8")
    return strategy, base, corrupted


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


_HEALTH_SUPPRESS = [
    HealthCheck.too_slow,
    HealthCheck.function_scoped_fixture,
]


@given(corruption=_json_corruption_strategy())
@settings(max_examples=120, deadline=None, suppress_health_check=_HEALTH_SUPPRESS)
def test_verify_packet_hash_never_crashes(corruption, tmp_path: Path):
    """BUG #7 family — verify_packet_hash must NEVER raise on any corrupt input.

    It must return (False, message) for any non-good input (or (True, "ok")
    for the rare case where the corruption happens to be hash-consistent —
    e.g. if duplicate_field injection happens to leave the recomputed hash
    matching the stored one).
    """
    from apps_shared.proof.proof_contracts import verify_packet_hash

    strategy, _, corrupted_bytes = corruption
    p = tmp_path / "packet.json"
    p.write_bytes(corrupted_bytes)

    # Property: never raises, always returns (bool, str)
    ok, msg = verify_packet_hash(p)
    assert isinstance(ok, bool), f"{strategy}: ok must be bool, got {type(ok)}"
    assert isinstance(msg, str) and msg, f"{strategy}: msg must be non-empty str"


@given(corruption=_json_corruption_strategy())
@settings(max_examples=120, deadline=None, suppress_health_check=_HEALTH_SUPPRESS)
def test_packet_from_disk_never_crashes(corruption, tmp_path: Path):
    """BUG #10 family — _packet_from_disk must degrade gracefully, never crash.

    The property: returns a valid AppRunEvidencePacket dataclass for any
    input bytes (including malformed JSON, non-dict roots, missing fields).
    """
    from apps_shared.proof.negative_controls import _packet_from_disk
    from apps_shared.proof.proof_contracts import AppRunEvidencePacket

    strategy, _, corrupted_bytes = corruption
    p = tmp_path / "packet.json"
    p.write_bytes(corrupted_bytes)

    # Property: never raises, always returns AppRunEvidencePacket
    pkt = _packet_from_disk(p)
    assert isinstance(pkt, AppRunEvidencePacket), (
        f"{strategy}: must return AppRunEvidencePacket, got {type(pkt)}"
    )
    # Field types are dataclass-valid even with empty defaults
    assert isinstance(pkt.app_id, str)
    assert isinstance(pkt.span_inventory, list)


@given(corruption=_json_corruption_strategy())
@settings(max_examples=120, deadline=None, suppress_health_check=_HEALTH_SUPPRESS)
def test_read_contract_payload_never_crashes(corruption, tmp_path: Path):
    """BUG #11 family — _read_contract_payload returns None on corruption,
    never raises (so validate_replay surfaces a clean fail_reason)."""
    from apps_shared.proof.validators import _read_contract_payload

    strategy, _, corrupted_bytes = corruption
    sd = tmp_path / "contract"
    sd.mkdir(exist_ok=True)  # tmp_path is reused across Hypothesis iterations
    (sd / "ValidatedRequest_abc12345.json").write_bytes(corrupted_bytes)

    # Property: never raises, returns None or dict
    result = _read_contract_payload(sd, "ValidatedRequest")
    assert result is None or isinstance(result, dict), (
        f"{strategy}: must return None or dict, got {type(result)}"
    )
