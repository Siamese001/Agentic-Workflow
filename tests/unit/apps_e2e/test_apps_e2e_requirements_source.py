"""W1 of plan apps-fort-knox-parity-c5d9a3 — catalog tests.

Validates the apps_e2e catalog at data/certification/apps_e2e_requirements_source.json
against its schema and enforces hand-authored invariants:

    - Schema-valid against apps_e2e_requirements.schema.json
    - req_id uniqueness + APPS-REQ-NNN / APPS-DOM-NNN namespaces
    - depends_on_req_ids all resolve to existing rows
    - Exactly one is_positive_control=true row (APPS-REQ-001)
    - Every claim_type's claim_type_required_controls entries are present
      on every non-domain row of that claim_type
    - Per-app rows cover exactly the 8 runtime app_names
    - Expected row count (45 = 33 REQ + 12 DOM) matches requirement_count
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
from tools.cert.cert_paths import APPS_REQS_PATH, APPS_REQS_SCHEMA  # noqa: E402

CATALOG_PATH = APPS_REQS_PATH
SCHEMA_PATH = APPS_REQS_SCHEMA

EXPECTED_ROW_COUNT = 45
EXPECTED_APPS_REQ_COUNT = 33
EXPECTED_APPS_DOM_COUNT = 12
_REQ_ID_RE = re.compile(r"^APPS-REQ-\d{3}$")
_DOM_ID_RE = re.compile(r"^APPS-DOM-\d{3}$")
_DOMAIN_CLAIM_TYPES = frozenset(
    {"APPS_DOMAIN_WIRING", "APPS_DOMAIN_GATING", "APPS_DOMAIN_PROOF"}
)
EXPECTED_POSITIVE_CONTROL = "APPS-REQ-001"
EXPECTED_SCHEMA_VERSION = "apps_e2e_fortknox-v1"

# AppSpec owner_app coverage: the 6 certified runtime apps + 2 waivers.
EXPECTED_PER_APP_OWNERS = {
    "apps_rg",
    "apps_exec",
    "apps_eval",
    "apps_research",
    "apps_rfp",
    "apps_lic",
    # Promoted from waiver to APPS_SPINE_CERTIFIED in W11 (apps_qna)
    # and W12 (apps_underwriting_ai) per plan apps-fort-knox-parity-c5d9a3.
    "apps_qna",
    "apps_underwriting_ai",
}
EXPECTED_WAIVER_OWNERS: set[str] = set()  # All apps are runtime-certified post-W12.


@pytest.fixture(scope="module")
def catalog() -> dict:
    assert CATALOG_PATH.exists(), f"Catalog not found at {CATALOG_PATH}"
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def schema() -> dict:
    assert SCHEMA_PATH.exists(), f"Schema not found at {SCHEMA_PATH}"
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_catalog_parses_as_json(catalog: dict) -> None:
    assert isinstance(catalog, dict)


def test_schema_version_is_v1(catalog: dict) -> None:
    assert catalog["schema_version"] == EXPECTED_SCHEMA_VERSION


def test_catalog_validates_against_schema(catalog: dict, schema: dict) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(catalog), key=lambda e: e.path)
    assert not errors, "\n".join(f"{list(e.path)}: {e.message}" for e in errors)


def test_requirement_count_matches_declared(catalog: dict) -> None:
    assert catalog["requirement_count"] == len(catalog["requirements"])
    assert catalog["requirement_count"] == EXPECTED_ROW_COUNT


def test_req_ids_are_unique(catalog: dict) -> None:
    ids = [r["req_id"] for r in catalog["requirements"]]
    dupes = {i for i in ids if ids.count(i) > 1}
    assert not dupes, f"Duplicate req_ids: {sorted(dupes)}"


def test_req_id_pattern(catalog: dict) -> None:
    for r in catalog["requirements"]:
        rid = r["req_id"]
        assert _REQ_ID_RE.match(rid) or _DOM_ID_RE.match(rid), f"Invalid req_id: {rid}"


def test_req_namespace_counts(catalog: dict) -> None:
    ids = [r["req_id"] for r in catalog["requirements"]]
    req_ids = [i for i in ids if i.startswith("APPS-REQ-")]
    dom_ids = [i for i in ids if i.startswith("APPS-DOM-")]
    assert len(req_ids) == EXPECTED_APPS_REQ_COUNT
    assert len(dom_ids) == EXPECTED_APPS_DOM_COUNT


def test_apps_req_ids_are_sequential_001_to_033(catalog: dict) -> None:
    req_ids = [r["req_id"] for r in catalog["requirements"] if r["req_id"].startswith("APPS-REQ-")]
    expected = [f"APPS-REQ-{i:03d}" for i in range(1, EXPECTED_APPS_REQ_COUNT + 1)]
    assert req_ids == expected, f"APPS-REQ block not sequential. got={req_ids[:5]}..."


def test_apps_dom_ids_are_sequential_001_to_012(catalog: dict) -> None:
    dom_ids = [r["req_id"] for r in catalog["requirements"] if r["req_id"].startswith("APPS-DOM-")]
    expected = [f"APPS-DOM-{i:03d}" for i in range(1, EXPECTED_APPS_DOM_COUNT + 1)]
    assert dom_ids == expected, f"APPS-DOM block not sequential. got={dom_ids[:5]}..."


def test_catalog_order_req_block_then_dom_block(catalog: dict) -> None:
    ids = [r["req_id"] for r in catalog["requirements"]]
    first_dom = next(i for i, rid in enumerate(ids) if rid.startswith("APPS-DOM-"))
    assert all(rid.startswith("APPS-REQ-") for rid in ids[:first_dom])
    assert all(rid.startswith("APPS-DOM-") for rid in ids[first_dom:])


def test_no_positive_control_in_dom_rows(catalog: dict) -> None:
    dom_canaries = [
        r
        for r in catalog["requirements"]
        if r["req_id"].startswith("APPS-DOM-") and r["is_positive_control"]
    ]
    assert not dom_canaries


def test_dom_rows_use_domain_claim_types(catalog: dict) -> None:
    for r in catalog["requirements"]:
        if r["req_id"].startswith("APPS-DOM-"):
            assert r["claim_type"] in _DOMAIN_CLAIM_TYPES, (
                f"{r['req_id']}: unexpected claim_type {r['claim_type']}"
            )


def test_exactly_one_positive_control_row(catalog: dict) -> None:
    canaries = [r for r in catalog["requirements"] if r["is_positive_control"]]
    assert len(canaries) == 1, f"Expected exactly 1 positive control; got {len(canaries)}"
    assert canaries[0]["req_id"] == EXPECTED_POSITIVE_CONTROL


def test_positive_control_req_id_header_matches(catalog: dict) -> None:
    assert catalog["positive_control_req_id"] == EXPECTED_POSITIVE_CONTROL


def test_depends_on_references_resolve(catalog: dict) -> None:
    known = {r["req_id"] for r in catalog["requirements"]}
    for r in catalog["requirements"]:
        for dep in r.get("depends_on_req_ids", []):
            assert dep in known, f"{r['req_id']} depends on unknown {dep}"


def test_no_self_dependency(catalog: dict) -> None:
    for r in catalog["requirements"]:
        assert r["req_id"] not in r["depends_on_req_ids"], (
            f"{r['req_id']} depends on itself"
        )


def test_claim_type_required_controls_are_present_per_row(catalog: dict) -> None:
    ct_req = catalog["claim_type_required_controls"]
    for r in catalog["requirements"]:
        if r["claim_type"] in _DOMAIN_CLAIM_TYPES:
            continue
        required = set(ct_req.get(r["claim_type"], []))
        present = set(r["required_controls"])
        missing = required - present
        assert not missing, (
            f"{r['req_id']} (claim_type={r['claim_type']}) missing required controls: "
            f"{sorted(missing)}"
        )


def test_per_app_rows_cover_all_runtime_apps(catalog: dict) -> None:
    owners = {
        r.get("owner_app")
        for r in catalog["requirements"]
        if r["claim_type"] == "APPS_SPINE_CERTIFIED" and r.get("owner_app")
    }
    assert owners == EXPECTED_PER_APP_OWNERS, (
        f"Per-app certified row coverage mismatch: "
        f"missing={EXPECTED_PER_APP_OWNERS - owners}, extra={owners - EXPECTED_PER_APP_OWNERS}"
    )


def test_waiver_rows_cover_all_waived_apps(catalog: dict) -> None:
    waiver_owners = {
        r.get("owner_app")
        for r in catalog["requirements"]
        if r["claim_type"] == "APPS_WAIVER" and r.get("owner_app")
    }
    assert waiver_owners == EXPECTED_WAIVER_OWNERS


def test_waiver_rows_have_non_empty_reason(catalog: dict) -> None:
    for r in catalog["requirements"]:
        if r["claim_type"] == "APPS_WAIVER":
            assert r.get("waiver_reason"), f"{r['req_id']}: waiver_reason missing"
            assert r.get("fail_closed_if_missing") is False, (
                f"{r['req_id']}: waiver rows must NOT fail-closed"
            )


def test_canary_row_has_canary_evidence_depth(catalog: dict) -> None:
    canary = next(r for r in catalog["requirements"] if r["is_positive_control"])
    assert canary["required_proof_depth"] == "CANARY_EVIDENCE"
    assert canary["claim_type"] == "APPS_POSITIVE_CONTROL"


def test_all_allowed_verifier_commands_exist(catalog: dict) -> None:
    """Soft check: each allowed_verifier_commands entry is a plausible repo path.

    We don't require the file to exist yet (W2+ haven't shipped), but we
    require the path to be non-empty, posix-style, and under an expected
    top-level directory.
    """
    allowed_roots = {"scripts/", "tools/cert/", "tools/certification/"}
    for r in catalog["requirements"]:
        for cmd in r["allowed_verifier_commands"]:
            assert cmd and not cmd.startswith("/"), f"{r['req_id']}: bad cmd {cmd!r}"
            assert any(cmd.startswith(root) for root in allowed_roots), (
                f"{r['req_id']}: verifier command {cmd!r} not under allowed roots"
            )


def test_priority_values_are_canonical(catalog: dict) -> None:
    allowed = {"P0", "P1", "P2", "P3"}
    for r in catalog["requirements"]:
        assert r["priority"] in allowed, f"{r['req_id']}: bad priority"


def test_fail_closed_semantics_waiver_vs_hardrows(catalog: dict) -> None:
    """Non-waiver rows MUST be fail_closed_if_missing=True (the whole point
    of a Fort Knox catalog is that every non-waiver claim is load-bearing)."""
    for r in catalog["requirements"]:
        if r["claim_type"] == "APPS_WAIVER":
            continue
        assert r["fail_closed_if_missing"] is True, (
            f"{r['req_id']}: non-waiver row must be fail_closed_if_missing=true"
        )
