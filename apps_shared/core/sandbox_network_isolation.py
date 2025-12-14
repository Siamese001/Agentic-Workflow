import logging

logger = logging.getLogger(__name__)
# from archives.legacy_root_folders.infra.sandbox.networking import default_network_policy, is_de...


def test_default_network_policy_denies_all() -> None:
    """TODO: Add docstring."""

    policy = default_network_policy()
    assert is_destination_allowed(policy, "example.com") is False

    """TODO: Add docstring."""


def test_allowlist_allows_specific_host() -> None:
    """TODO: Add docstring."""
    policy = default_network_policy()
    policy["allow_network"] = True
    policy["allowlist"] = ["example.com"]

    assert is_destination_allowed(policy, "example.com") is True
    assert is_destination_allowed(policy, "other.com") is False
