from __future__ import annotations

from apps_rg.runtime.validators.verb_canonicalizer_validator import (
    VerbCanonicalizer,
    canonicalize,
    check_for_forbidden_verbs,
)


def test_forbidden_verb_scan_uses_word_boundaries() -> None:
    class Adapter:
        FORBIDDEN_VERBS = VerbCanonicalizer._FORBIDDEN_VERBS

    found = check_for_forbidden_verbs(
        Adapter(),
        "Spearheaded delivery but did not transform the roadmap; transformed the launch plan.",
    )

    assert found == ["spearheaded", "transformed"]


def test_canonical_catalog_keeps_approved_forms_separate_from_forbidden_forms() -> None:
    approved = set(VerbCanonicalizer._CANONICAL_VERBS)
    forbidden = set(VerbCanonicalizer._FORBIDDEN_VERBS)

    assert {"led", "built", "drove", "delivered"} <= approved
    assert "spearheaded" in forbidden
    assert approved.isdisjoint(forbidden)


def test_canonicalize_runtime_surface_returns_canonical_verbs() -> None:
    text = "Led cloud modernization and built platform controls."

    assert canonicalize(VerbCanonicalizer(), text) == ["led", "built"]
    assert VerbCanonicalizer.canonicalize(text) == ["led", "built"]
