"""ADG importability contract for apps_shared/utils/json_parser_validator_util.py."""
from __future__ import annotations

import apps_shared.utils.json_parser_validator_util  # noqa: F401


def test_module_importable():
    """Module json_parser_validator_util must be importable."""
    assert apps_shared.utils.json_parser_validator_util is not None
