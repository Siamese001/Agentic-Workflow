"""EQ-10 — bundled I0 mixin bank.

Plan: ``.windsurf/plans/prompt-assembly-best-practices-gap-b4e1c2.md``
ADR:  ADR-PROMPT-ASSEMBLY-002 §3, §4, §5
"""

from __future__ import annotations

import pytest

from agentic_core.prompt_governance.mixins import (
    BUNDLED_MIXIN_IDS,
    MixinNotFoundError,
    bundled_mixin_content_hash,
    get_bundled_mixin,
    is_bundled_mixin,
)


class TestBundledMixinIds:
    def test_registry_lists_expected_three(self) -> None:
        assert set(BUNDLED_MIXIN_IDS) == {
            "agentic_persistence",
            "tool_first",
            "plan_then_act",
        }

    def test_registry_is_tuple_for_immutability(self) -> None:
        assert isinstance(BUNDLED_MIXIN_IDS, tuple)


class TestGetBundledMixin:
    @pytest.mark.parametrize("mixin_id", BUNDLED_MIXIN_IDS)
    def test_returns_non_empty_content(self, mixin_id: str) -> None:
        content = get_bundled_mixin(mixin_id)
        assert isinstance(content, str)
        assert content.strip(), f"{mixin_id!r} is empty"

    @pytest.mark.parametrize("mixin_id", BUNDLED_MIXIN_IDS)
    def test_content_starts_with_markdown_header(self, mixin_id: str) -> None:
        content = get_bundled_mixin(mixin_id)
        assert content.lstrip().startswith("# Mixin: ")

    def test_missing_mixin_raises_mixin_not_found(self) -> None:
        with pytest.raises(MixinNotFoundError):
            get_bundled_mixin("nonexistent_mixin")

    def test_content_is_deterministic_across_calls(self) -> None:
        first = get_bundled_mixin("tool_first")
        second = get_bundled_mixin("tool_first")
        assert first == second


class TestBundledMixinContentHash:
    @pytest.mark.parametrize("mixin_id", BUNDLED_MIXIN_IDS)
    def test_hash_is_64_char_hex(self, mixin_id: str) -> None:
        digest = bundled_mixin_content_hash(mixin_id)
        assert len(digest) == 64
        int(digest, 16)  # Must be valid hex — raises ValueError otherwise.

    def test_hashes_are_distinct_across_mixins(self) -> None:
        hashes = {mixin_id: bundled_mixin_content_hash(mixin_id) for mixin_id in BUNDLED_MIXIN_IDS}
        # All three bundled mixins must have different content.
        assert len(set(hashes.values())) == len(BUNDLED_MIXIN_IDS)

    def test_hash_is_stable_across_calls(self) -> None:
        assert bundled_mixin_content_hash("plan_then_act") == bundled_mixin_content_hash("plan_then_act")


class TestIsBundledMixin:
    @pytest.mark.parametrize("mixin_id", BUNDLED_MIXIN_IDS)
    def test_known_ids_return_true(self, mixin_id: str) -> None:
        assert is_bundled_mixin(mixin_id) is True

    def test_unknown_id_returns_false(self) -> None:
        assert is_bundled_mixin("some_other_thing") is False
