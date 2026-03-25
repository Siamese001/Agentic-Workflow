"""ADG importability contract for apps_shared/types/app_heal_contract_types.py."""
from __future__ import annotations

import apps_shared.types.app_heal_contract_types  # noqa: F401


def test_module_importable():
    """Module app_heal_contract_types must be importable."""
    assert apps_shared.types.app_heal_contract_types is not None
