# from archives.legacy_root_folders.infra.sandbox.networking import default_network_policy, is_destination_allowed  # DEPRECATED: Archive import removed to protect archives from validation edits


def test_default_network_policy_denies_all() -> None:
    policy = default_network_policy()
    assert is_destination_allowed(policy, "example.com") is False


def test_allowlist_allows_specific_host() -> None:
    policy = default_network_policy()
    policy["allow_network"] = True
    policy["allowlist"] = ["example.com"]

    assert is_destination_allowed(policy, "example.com") is True
    assert is_destination_allowed(policy, "other.com") is False
