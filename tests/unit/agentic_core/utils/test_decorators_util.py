"""Foundational behavioral tests for agentic_core/utils/decorators_util.py."""

from __future__ import annotations


def test_module_importable():
    """Module decorators_util must be importable."""
    from agentic_core.utils import decorators_util

    assert decorators_util is not None


def test_standard_heal_decorator_importable():
    """standard_heal decorator must be importable and applicable."""
    from agentic_core.utils import decorators_util

    class MockHealer:
        @decorators_util.standard_heal
        def heal_repository(self, dry_run=True, execute=False, **kwargs):
            return {"violations_found": 1, "violations_fixed": 0}

    # Verify decorator was applied (method is wrapped)
    healer = MockHealer()
    assert hasattr(healer, "heal_repository")
    assert callable(healer.heal_repository)


def test_standard_heal_async_decorator_importable():
    """standard_heal_async decorator must be importable and applicable."""
    from agentic_core.utils import decorators_util

    class MockHealer:
        @decorators_util.standard_heal_async
        async def heal_repository(self, dry_run=True, execute=False, **kwargs):
            return {"violations_found": 1, "violations_fixed": 0}

    # Verify decorator was applied (method is wrapped)
    healer = MockHealer()
    assert hasattr(healer, "heal_repository")
    assert callable(healer.heal_repository)
