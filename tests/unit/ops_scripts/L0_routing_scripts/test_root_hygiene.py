""" """

import pytest


@pytest.fixture
def dirty_repo(tmp_path):
    """Creates a dirty mock repo with illegal root folders."""

    return tmp_path


def test_hygiene_enforcement(dirty_repo, monkeypatch):
    """Test that scripts are moved to correct locations and root is cleaned."""


def test_purge_cache_refiling(dirty_repo, monkeypatch):
    """Test the specific rule for purge_cache.py reorganization."""
