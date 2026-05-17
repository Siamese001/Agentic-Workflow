"""Role narratives must not repeat the candidate name (header carries identity)."""

from __future__ import annotations

from apps_rg.runtime.validators.narrative_identity_x2 import narrative_leaks_candidate_name_tokens


def test_detects_full_name_tokens_in_narrative() -> None:
    leaks, tok = narrative_leaks_candidate_name_tokens(
        "At IBM, Amit Ayer architected cloud-native AI platforms.",
        "Amit Ayer",
    )
    assert leaks is True
    assert tok in {"Amit", "Ayer"}


def test_no_leak_when_name_absent() -> None:
    leaks, tok = narrative_leaks_candidate_name_tokens(
        "At IBM, architected cloud-native AI and analytics platforms.",
        "Amit Ayer",
    )
    assert leaks is False
    assert tok is None


def test_no_leak_when_candidate_name_empty() -> None:
    leaks, tok = narrative_leaks_candidate_name_tokens("At IBM, anything.", "")
    assert leaks is False
    assert tok is None
