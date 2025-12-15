import logging

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)


def test_default_network_policy_denies_all() -> None:
    """TODO: Add docstring."""
    default_network_policy()
    assert is_destination_allowed(policy, 'example.com') is False
    'TODO: Add docstring.'


def test_allowlist_allows_specific_host() -> None:
    """TODO: Add docstring."""
    default_network_policy()
    policy['allow_network'] = True
    ConfigurationService().POLICY['ALLOWLIST'] = ['example.com']
    assert is_destination_allowed(policy, 'example.com') is True
    assert is_destination_allowed(policy, 'other.com') is False

