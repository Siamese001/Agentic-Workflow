"""Unit tests for SubjectLineVariantSelector (W1-P1).

Covers:
- every archetype produces a non-empty rendered subject
- variant_id is always in the admissible set for the archetype
- record_outcome updates the underlying bandit posterior
- long templates truncate to SUBJECT_LINE_MAX_CHARS with ellipsis
- missing context keys degrade to empty-string substitution, not KeyError
- OTHER-archetype fallback engages for unknown archetypes
- deterministic behaviour when seeded
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.reasoning.namespace_bandit import NamespaceBandit

from apps_lic.config.subject_line_bandit_config import (
    ADMISSIBLE_VARIANTS,
    ARCHETYPES,
    SUBJECT_LINE_MAX_CHARS,
    admissible_variants_for,
    build_namespace,
    template_for,
)
from apps_lic.engines.subject_line_variant_selector import (
    SubjectLineSelection,
    SubjectLineVariantSelector,
)


BASE_CONTEXT = {
    "recipient_first_name": "Priya",
    "recipient_company": "Acme Corp",
    "observation": "recent Series C raise",
    "mutual_name": "Dana",
}


class TestSubjectLineBanditConfig:
    def test_all_archetypes_have_three_admissible_variants(self) -> None:
        for archetype in ARCHETYPES:
            variants = ADMISSIBLE_VARIANTS[archetype]
            assert len(variants) == 3, f"{archetype} must have 3 arms for Wilson-CI convergence"
            assert len(set(variants)) == 3, f"{archetype} has duplicate variant IDs"

    def test_namespace_prefix_is_stable(self) -> None:
        assert build_namespace("EXECUTIVE") == "apps_lic.subject_line.executive"
        assert build_namespace("C_LEVEL") == "apps_lic.subject_line.c_level"

    def test_admissible_fallback_for_unknown_archetype(self) -> None:
        assert admissible_variants_for("UNKNOWN_X") == ADMISSIBLE_VARIANTS["OTHER"]

    def test_every_admissible_variant_has_a_template(self) -> None:
        from apps_lic.config.subject_line_bandit_config import SUBJECT_TEMPLATES

        for archetype, variants in ADMISSIBLE_VARIANTS.items():
            for variant in variants:
                assert (
                    archetype,
                    variant,
                ) in SUBJECT_TEMPLATES, f"missing template for ({archetype}, {variant})"

    def test_template_fallback_for_unknown_variant(self) -> None:
        fallback = template_for("EXECUTIVE", "does_not_exist")
        assert fallback == template_for("OTHER", "question")


class TestSubjectLineVariantSelector:
    def test_select_returns_admissible_variant_per_archetype(self) -> None:
        selector = SubjectLineVariantSelector(seed=42)
        for archetype in ARCHETYPES:
            sel = selector.select(archetype=archetype, context=BASE_CONTEXT)
            assert isinstance(sel, SubjectLineSelection)
            assert sel.archetype == archetype
            assert sel.variant_id in ADMISSIBLE_VARIANTS[archetype]
            assert sel.rendered_subject, f"empty subject for {archetype}"

    def test_rendered_subject_respects_max_chars(self) -> None:
        selector = SubjectLineVariantSelector(seed=7)
        huge_context = {
            **BASE_CONTEXT,
            "recipient_company": "A" * 200,
            "observation": "B" * 200,
        }
        for archetype in ARCHETYPES:
            sel = selector.select(archetype=archetype, context=huge_context)
            assert len(sel.rendered_subject) <= SUBJECT_LINE_MAX_CHARS

    def test_missing_context_keys_do_not_raise(self) -> None:
        selector = SubjectLineVariantSelector(seed=1)
        sel = selector.select(archetype="EXECUTIVE", context={"recipient_first_name": "Sam"})
        # Missing keys collapse to empty + the safe renderer collapses double spaces.
        assert "Sam" in sel.rendered_subject or sel.rendered_subject  # either substituted or degraded-but-nonempty
        assert "{" not in sel.rendered_subject  # no unresolved placeholders

    def test_unknown_archetype_falls_back_to_other(self) -> None:
        selector = SubjectLineVariantSelector(seed=3)
        sel = selector.select(archetype="MARTIAN", context=BASE_CONTEXT)
        # Variant must belong to the OTHER admissible set.
        assert sel.variant_id in ADMISSIBLE_VARIANTS["OTHER"]
        assert sel.namespace == "apps_lic.subject_line.martian"

    def test_record_outcome_updates_posterior(self) -> None:
        bandit = NamespaceBandit(seed=99)
        selector = SubjectLineVariantSelector(bandit=bandit)
        sel = selector.select(archetype="RECRUITER", context=BASE_CONTEXT)

        post_before = bandit.posterior(sel.namespace, sel.variant_id)
        selector.record_outcome(sel, replied=True)
        post_after_success = bandit.posterior(sel.namespace, sel.variant_id)
        assert post_after_success.alpha == pytest.approx(post_before.alpha + 1.0)
        assert post_after_success.beta == pytest.approx(post_before.beta)

        sel2 = selector.select(archetype="RECRUITER", context=BASE_CONTEXT)
        selector.record_outcome(sel2, replied=False)
        # Some beta should have incremented for the chosen arm.
        post_after_fail = bandit.posterior(sel2.namespace, sel2.variant_id)
        assert post_after_fail.beta > 1.0

    def test_deterministic_given_fixed_seed_and_shared_bandit(self) -> None:
        """Two selectors sharing the same seeded bandit produce identical output."""
        bandit_a = NamespaceBandit(seed=2026)
        bandit_b = NamespaceBandit(seed=2026)
        selector_a = SubjectLineVariantSelector(bandit=bandit_a)
        selector_b = SubjectLineVariantSelector(bandit=bandit_b)
        for archetype in ARCHETYPES:
            sel_a = selector_a.select(archetype=archetype, context=BASE_CONTEXT)
            sel_b = selector_b.select(archetype=archetype, context=BASE_CONTEXT)
            assert sel_a.variant_id == sel_b.variant_id
            assert sel_a.rendered_subject == sel_b.rendered_subject

    def test_select_with_no_context_still_renders(self) -> None:
        selector = SubjectLineVariantSelector(seed=5)
        sel = selector.select(archetype="OTHER", context=None)
        assert sel.rendered_subject  # non-empty even with empty context
        assert "{" not in sel.rendered_subject

    def test_convergence_exploration_covers_all_arms(self) -> None:
        """Over many calls, all 3 arms for EXECUTIVE must be sampled.

        Sanity check that Thompson sampling isn't degenerating to a single arm
        before the bandit has seen outcomes.
        """
        selector = SubjectLineVariantSelector(seed=2026)
        seen = set()
        for _ in range(60):
            sel = selector.select(archetype="EXECUTIVE", context=BASE_CONTEXT)
            seen.add(sel.variant_id)
        assert seen == set(ADMISSIBLE_VARIANTS["EXECUTIVE"])
