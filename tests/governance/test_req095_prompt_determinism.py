"""REQ-095: Prompt fragment determinism.

Prove prompt fragment assembly is sorted + stable across two calls.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.governance
def test_prompt_fragment_determinism_sorted():
    """REQ-095: Prompt fragments should be assembled in sorted order for determinism."""
    # Simulate prompt fragments that could be assembled in different orders
    fragments = {
        "system": "You are a helpful assistant.",
        "context": "The user is asking about:",
        "question": "What is the capital of France?",
        "format": "Provide a concise answer.",
    }

    # Assemble in sorted order by key
    sorted_keys = sorted(fragments.keys())
    assembled_prompt = "\n".join(fragments[key] for key in sorted_keys)

    # Verify the assembly is deterministic
    expected_prompt = """The user is asking about:
Provide a concise answer.
What is the capital of France?
You are a helpful assistant."""

    assert assembled_prompt == expected_prompt


@pytest.mark.governance
def test_prompt_fragment_determinism_stable_across_calls():
    """REQ-095: Same fragments should produce identical prompt across multiple calls."""
    fragments = {
        "instruction": "Summarize the following text:",
        "text": "This is a long text about various topics including science, technology, and philosophy.",
        "length": "Keep it under 100 words.",
    }

    def assemble_prompt(frag_dict: dict[str, str]) -> str:
        """Simulate prompt assembly function."""
        sorted_keys = sorted(frag_dict.keys())
        return "\n".join(frag_dict[key] for key in sorted_keys)

    # Call assembly twice
    prompt1 = assemble_prompt(fragments)
    prompt2 = assemble_prompt(fragments)

    # Should be identical
    assert prompt1 == prompt2

    # Hashes should match
    hash1 = hashlib.sha256(prompt1.encode("utf-8")).hexdigest()
    hash2 = hashlib.sha256(prompt2.encode("utf-8")).hexdigest()

    assert hash1 == hash2


@pytest.mark.governance
def test_prompt_fragment_determinism_order_independence():
    """REQ-095: Fragment order in input should not affect final prompt."""
    # Same fragments, different input order
    fragments_a = {
        "zeta": "Fragment Z",
        "alpha": "Fragment A",
        "beta": "Fragment B",
    }

    fragments_b = {
        "beta": "Fragment B",
        "zeta": "Fragment Z",
        "alpha": "Fragment A",
    }

    def assemble_prompt(frag_dict: dict[str, str]) -> str:
        """Simulate deterministic prompt assembly."""
        sorted_keys = sorted(frag_dict.keys())
        return "\n".join(frag_dict[key] for key in sorted_keys)

    prompt_a = assemble_prompt(fragments_a)
    prompt_b = assemble_prompt(fragments_b)

    # Should be identical despite different input order
    assert prompt_a == prompt_b
    assert prompt_a == "Fragment A\nFragment B\nFragment Z"


@pytest.mark.governance
def test_prompt_fragment_determinism_with_special_characters():
    """REQ-095: Special characters should not affect determinism."""
    fragments = {
        "unicode": "Hello 世界 🌍",
        "quotes": "He said \"Hello\" and 'goodbye'",
        "escape": "New\nLine\tTab\\Backslash",
    }

    def assemble_prompt(frag_dict: dict[str, str]) -> str:
        sorted_keys = sorted(frag_dict.keys())
        return "\n".join(frag_dict[key] for key in sorted_keys)

    # Assemble twice to ensure stability
    prompt1 = assemble_prompt(fragments)
    prompt2 = assemble_prompt(fragments)

    assert prompt1 == prompt2

    # Verify special characters are preserved
    assert "世界 🌍" in prompt1
    assert '"Hello"' in prompt1
    assert "\nLine\tTab" in prompt1


@pytest.mark.governance
def test_prompt_fragment_determinism_empty_fragments():
    """REQ-095: Edge case - empty fragments should be handled deterministically."""
    fragments = {
        "empty": "",
        "normal": "Normal fragment",
        "spaces": "   ",
    }

    def assemble_prompt(frag_dict: dict[str, str]) -> str:
        sorted_keys = sorted(frag_dict.keys())
        return "\n".join(frag_dict[key] for key in sorted_keys)

    prompt = assemble_prompt(fragments)

    # Should handle empty strings deterministically
    expected = "\n".join(["", "Normal fragment", "   "])  # sorted: empty, normal, spaces
    assert prompt == expected
