"""SubjectLineVariantSelector — archetype-conditioned subject-line bandit wrapper.

W1-P1 of the apps_lic LinkedIn response-rate maximization plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35, Bundle A).

Bundle A rationale: rather than build a parallel bandit implementation,
this module is a thin wrapper around the existing
``agentic_core.L0_routing.reasoning.namespace_bandit.NamespaceBandit``.
Binding:

- ``namespace`` = ``apps_lic.subject_line.<archetype>`` (via
  ``subject_line_bandit_config.build_namespace``)
- ``admissible`` = ``ADMISSIBLE_VARIANTS[archetype]`` (3 arms per archetype)
- Wilson-CI promotion, closed-loop ROUTER_DECISION telemetry, and weekly
  calibration reports are inherited for free from the L0 bandit stack
  (constitutional §29, ADR-050 intelligence-ledger-family).

The selector emits the chosen variant ID plus a rendered subject-line
string. Outcome feedback (reply received → ``success=True``) is plumbed
back via ``record_outcome`` which simply delegates to
``NamespaceBandit.update``.

Deterministic when seeded — pass ``seed`` to the constructor or to
``NamespaceBandit`` before injection for reproducible tests.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from agentic_core.L0_routing.reasoning.namespace_bandit import NamespaceBandit

from apps_lic.config.subject_line_bandit_config import (
    SUBJECT_LINE_MAX_CHARS,
    admissible_variants_for,
    build_namespace,
    template_for,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class SubjectLineSelection:
    """Return value of ``SubjectLineVariantSelector.select``.

    Holds enough context to (a) render the subject line, (b) bind the
    outcome back to the bandit via ``record_outcome``.
    """

    archetype: str
    variant_id: str
    namespace: str
    rendered_subject: str
    template: str
    context: Mapping[str, Any] = field(default_factory=dict)


class SubjectLineVariantSelector:
    """Thin wrapper around ``NamespaceBandit`` for subject-line variant choice.

    Usage:
        selector = SubjectLineVariantSelector()
        sel = selector.select(
            archetype="EXECUTIVE",
            context={
                "recipient_first_name": "Priya",
                "recipient_company": "Acme Corp",
                "observation": "recent Series C raise",
                "mutual_name": "Dana",
            },
        )
        # ... send message ...
        selector.record_outcome(sel, replied=True)
    """

    def __init__(
        self,
        bandit: Optional[NamespaceBandit] = None,
        *,
        seed: Optional[int] = None,
    ) -> None:
        """Construct the selector.

        Args:
            bandit: Pre-existing bandit to reuse. Pass this to share posterior
                state with other callers in the same process. When ``None``
                a fresh bandit is created seeded with ``seed``.
            seed: RNG seed for a freshly-constructed bandit. Ignored when
                ``bandit`` is not None.
        """
        self._bandit = bandit if bandit is not None else NamespaceBandit(seed=seed)

    @property
    def bandit(self) -> NamespaceBandit:
        """Expose the underlying bandit — read-only in practice."""
        return self._bandit

    def select(
        self,
        archetype: str,
        context: Optional[Mapping[str, Any]] = None,
    ) -> SubjectLineSelection:
        """Choose a subject-line variant for ``archetype`` + render it.

        The variant ID is selected via Thompson sampling on the bandit
        cell ``apps_lic.subject_line.<archetype>``. The template for the
        (archetype, variant_id) pair is then substituted with keys from
        ``context``. Missing template keys are tolerated — they expand to
        the empty string so partial context never breaks rendering.

        Args:
            archetype: One of the five ProfilePlanner archetype labels
                (C_LEVEL, EXECUTIVE, SENIOR_TA, RECRUITER, OTHER). Unknown
                values are tolerated via the OTHER fallback in
                ``admissible_variants_for``.
            context: Mapping of template-key → value. Expected keys are
                ``recipient_first_name``, ``recipient_company``,
                ``observation``, ``mutual_name``. Missing keys expand to
                the empty string. Extra keys are ignored.

        Returns:
            ``SubjectLineSelection`` with all fields populated. Truncates
            the rendered subject to ``SUBJECT_LINE_MAX_CHARS`` when longer.
        """
        ctx = dict(context) if context else {}
        namespace = build_namespace(archetype)
        admissible = admissible_variants_for(archetype)
        variant_id = self._bandit.choose(namespace=namespace, admissible=list(admissible))
        template = template_for(archetype, variant_id)
        rendered = self._safe_render(template, ctx)
        return SubjectLineSelection(
            archetype=archetype,
            variant_id=variant_id,
            namespace=namespace,
            rendered_subject=rendered,
            template=template,
            context=ctx,
        )

    def record_outcome(
        self,
        selection: SubjectLineSelection,
        *,
        replied: bool,
    ) -> None:
        """Bind the reply outcome back to the bandit posterior.

        ``replied=True`` counts as a Bernoulli success → α increment on
        the ``(namespace, variant_id)`` cell. ``replied=False`` → β
        increment. Delegates to ``NamespaceBandit.update`` which also
        closes the ROUTER_DECISION ledger row under §29 closed-loop wiring.

        Args:
            selection: The exact ``SubjectLineSelection`` returned by a
                previous ``select`` call. The namespace + variant_id are
                the binding key.
            replied: Whether the recipient replied (any engagement signal
                that qualifies as "reply" in the campaign's definition).
        """
        self._bandit.update(
            namespace=selection.namespace,
            route=selection.variant_id,
            success=replied,
        )

    @staticmethod
    def _safe_render(template: str, context: Mapping[str, Any]) -> str:
        """Render ``template`` with ``context``, tolerating missing keys.

        Uses ``str.format_map`` with a defaultdict-like wrapper so missing
        keys render as empty. Also truncates to the LinkedIn visual cap.
        Never raises on malformed keys — degrades to the raw template.
        """
        try:
            rendered = template.format_map(_DefaultMissing(context))
        except (ValueError, IndexError):  # guardian: allow-log-and-swallow -- malformed format spec degrades to template
            _LOGGER.debug("SubjectLineVariantSelector template render failed", exc_info=True)
            rendered = template
        # Collapse any accidental double-spaces produced by empty substitutions.
        rendered = " ".join(rendered.split())
        if len(rendered) > SUBJECT_LINE_MAX_CHARS:
            rendered = rendered[: SUBJECT_LINE_MAX_CHARS - 1].rstrip() + "\u2026"
        return rendered


class _DefaultMissing(dict):
    """dict subclass that returns '' for missing keys during ``format_map``.

    Prevents ``KeyError`` when a template references a context key that
    the caller did not supply. Missing keys render as the empty string.
    """

    def __missing__(self, key: str) -> str:  # noqa: D401 -- dict hook
        return ""


__all__ = [
    "SubjectLineSelection",
    "SubjectLineVariantSelector",
]
