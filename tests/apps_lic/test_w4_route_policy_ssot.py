from __future__ import annotations

from pathlib import Path

import yaml

from apps_lic.types.linkedin_route_envelope import (
    CONNECTION_REQUEST_CHAR_CAP,
    INMAIL_BODY_CHAR_CAP,
    resolve_linkedin_route_envelope,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_COPY = REPO_ROOT / "apps_lic" / "policy" / "pre_flight_policy.yaml"
VALIDATOR_COPY = REPO_ROOT / "apps_lic" / "validators" / "policy" / "pre_flight_policy.yaml"


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_w4_pre_flight_policy_copies_are_byte_identical_until_deduped() -> None:
    assert POLICY_COPY.read_text(encoding="utf-8") == VALIDATOR_COPY.read_text(encoding="utf-8")


def test_w4_pre_flight_policy_core_routes_match_canonical_envelope() -> None:
    policy = _load_yaml(POLICY_COPY)
    rules = {rule["rule_id"]: rule["then"] for rule in policy["rules"]}

    inmail = resolve_linkedin_route_envelope(
        connection_status="NOT_CONNECTED",
        premium_available=True,
    )
    connection = resolve_linkedin_route_envelope(
        connection_status="NOT_CONNECTED",
        premium_available=False,
    )
    explicit = resolve_linkedin_route_envelope(
        connection_status="NOT_CONNECTED",
        premium_available=False,
        route_override="INMAIL",
    )

    assert rules["inmail_default"]["route"] == inmail.route
    assert rules["inmail_default"]["char_limit"] == INMAIL_BODY_CHAR_CAP
    assert rules["inmail_default"]["signature_required"] == inmail.signature_required

    assert rules["connection_req_default"]["route"] == connection.route
    assert rules["connection_req_default"]["char_limit"] == CONNECTION_REQUEST_CHAR_CAP
    assert rules["connection_req_default"]["signature_required"] == connection.signature_required

    assert rules["explicit_override"]["route"] == "OVERRIDE"
    assert rules["explicit_override"]["char_limit"] == explicit.hard_cap_chars
    assert rules["explicit_override"]["signature_required"] == explicit.signature_required
