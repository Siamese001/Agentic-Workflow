"""ADG importability contract for apps_shared/scripts/app_remediation_dispatcher.py."""
from __future__ import annotations


def test_module_importable():
    """Module app_remediation_dispatcher must be importable."""
    import apps_shared.scripts.app_remediation_dispatcher  # noqa: F401

    assert apps_shared.scripts.app_remediation_dispatcher is not None
