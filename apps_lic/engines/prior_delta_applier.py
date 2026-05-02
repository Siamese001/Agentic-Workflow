"""Prior-delta applier — closes the W4-P10 → MessagePlanner feedback loop.

Final follow-up to the apps_lic LinkedIn response-rate plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35).

Takes the per-axis deltas emitted by ``ReplySignalFeedbackEngine.emit_prior_deltas``
and applies them to the runtime priors held by ``MessagePlanner`` and
``ProfilePlanner``. The applier is **additive and idempotent within a
single run**:

    1. It NEVER mutates a planner's existing data structures destructively;
       it adds a new ``prior_score`` field per section / archetype (or
       updates it if already present) within a documented clamp range
       ``[PRIOR_SCORE_MIN, PRIOR_SCORE_MAX]``.

    2. It NEVER removes or reorders existing keys — downstream consumers
       that don't know about ``prior_score`` see no breakage.

    3. It is **deterministic**: applying the same ledger twice produces
       the same prior_scores (each application replaces, doesn't compound).
       To compound on top of historical state, callers must read existing
       ``prior_score`` and add it to the new delta themselves.

Clamp range: ``[-1.0, +1.0]``. Beyond this the runtime should re-evaluate
whether the cell deserves an Author-Gate review (constitutional §6) — a
delta this large indicates persistent pathology, not normal calibration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Mapping, MutableMapping, Optional, Sequence

from apps_lic.engines.reply_signal_feedback_engine import (
    ReplyFeedbackLedger,
    ReplySignalFeedbackEngine,
)

PRIOR_SCORE_MIN: Final[float] = -1.0
PRIOR_SCORE_MAX: Final[float] = +1.0

# Per-axis sentinel used in delta-key parsing. Matches
# ``ReplySignalFeedbackEngine.emit_prior_deltas`` output.
_AXIS_ARCHETYPE: Final[str] = "archetype:"
_AXIS_TEMPLATE: Final[str] = "template:"
_AXIS_SUBJECT: Final[str] = "subject_variant:"


@dataclass
class PriorApplicationReport:
    """Audit trail for one ``apply()`` invocation.

    Attributes:
        archetype_updates: archetype -> applied prior_score (post-clamp).
        template_updates: section_name -> applied prior_score.
        subject_variant_updates: variant_id -> applied prior_score.
        skipped: list of (axis_key, reason) for deltas that could not be
            applied (e.g., archetype/template/variant unknown to planner).
        clamp_events: list of (axis_key, raw_value, clamped_value) tuples
            for deltas that hit the [-1.0, +1.0] clamp.
    """

    archetype_updates: dict[str, float] = field(default_factory=dict)
    template_updates: dict[str, float] = field(default_factory=dict)
    subject_variant_updates: dict[str, float] = field(default_factory=dict)
    skipped: list[tuple[str, str]] = field(default_factory=list)
    clamp_events: list[tuple[str, float, float]] = field(default_factory=list)

    @property
    def total_applied(self) -> int:
        return (
            len(self.archetype_updates)
            + len(self.template_updates)
            + len(self.subject_variant_updates)
        )


class PriorDeltaApplier:
    """Apply per-axis deltas from ``ReplySignalFeedbackEngine`` to planners."""

    def __init__(
        self, engine: Optional[ReplySignalFeedbackEngine] = None
    ) -> None:
        self._engine = engine or ReplySignalFeedbackEngine()

    def apply(
        self,
        ledger: ReplyFeedbackLedger,
        *,
        message_planner: Optional[object] = None,
        profile_planner: Optional[object] = None,
        subject_variant_priors: Optional[MutableMapping[str, float]] = None,
    ) -> PriorApplicationReport:
        """Apply emitted deltas to the supplied planners / mappings.

        Any planner argument may be ``None`` — the corresponding axis is
        recorded as ``skipped`` for each delta on that axis. This keeps
        the call valid in environments where only one planner is wired.

        Args:
            ledger: Source ledger for ``emit_prior_deltas``.
            message_planner: Object exposing ``section_templates`` (dict of
                section_name -> dict). The applier writes
                ``section_templates[section_name]["prior_score"]``.
            profile_planner: Object on which the applier sets / replaces
                an ``archetype_prior_scores`` dict attribute mapping
                archetype -> clamped prior_score.
            subject_variant_priors: Mutable mapping that the applier
                updates with subject-variant-axis deltas. The mapping
                structure mirrors what the SubjectLineVariantSelector
                bandit consumes (variant_id -> prior_score).

        Returns:
            ``PriorApplicationReport`` describing exactly what was applied.
        """
        report = PriorApplicationReport()
        deltas = self._engine.emit_prior_deltas(ledger)

        # Group axis-prefixed keys.
        archetype_deltas: dict[str, float] = {}
        template_deltas: dict[str, float] = {}
        subject_deltas: dict[str, float] = {}
        for key, raw in deltas.items():
            if key.startswith(_AXIS_ARCHETYPE):
                archetype_deltas[key[len(_AXIS_ARCHETYPE):]] = raw
            elif key.startswith(_AXIS_TEMPLATE):
                template_deltas[key[len(_AXIS_TEMPLATE):]] = raw
            elif key.startswith(_AXIS_SUBJECT):
                subject_deltas[key[len(_AXIS_SUBJECT):]] = raw

        # 1. ProfilePlanner archetype priors.
        if archetype_deltas:
            if profile_planner is None:
                for archetype in archetype_deltas:
                    report.skipped.append(
                        (
                            f"archetype:{archetype}",
                            "profile_planner not supplied",
                        )
                    )
            else:
                self._apply_archetype_deltas(
                    profile_planner, archetype_deltas, report
                )

        # 2. MessagePlanner section/template priors.
        if template_deltas:
            if message_planner is None:
                for tmpl in template_deltas:
                    report.skipped.append(
                        (f"template:{tmpl}", "message_planner not supplied")
                    )
            else:
                self._apply_template_deltas(
                    message_planner, template_deltas, report
                )

        # 3. Subject-variant priors map.
        if subject_deltas:
            if subject_variant_priors is None:
                for variant in subject_deltas:
                    report.skipped.append(
                        (
                            f"subject_variant:{variant}",
                            "subject_variant_priors not supplied",
                        )
                    )
            else:
                self._apply_subject_deltas(
                    subject_variant_priors, subject_deltas, report
                )

        return report

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _clamp(
        axis_key: str, raw: float, report: PriorApplicationReport
    ) -> float:
        clamped = max(PRIOR_SCORE_MIN, min(PRIOR_SCORE_MAX, raw))
        if clamped != raw:
            report.clamp_events.append((axis_key, raw, clamped))
        return clamped

    def _apply_archetype_deltas(
        self,
        profile_planner: object,
        deltas: Mapping[str, float],
        report: PriorApplicationReport,
    ) -> None:
        existing = getattr(profile_planner, "archetype_prior_scores", None)
        if not isinstance(existing, dict):
            existing = {}
            setattr(profile_planner, "archetype_prior_scores", existing)
        for archetype, raw in deltas.items():
            clamped = self._clamp(f"archetype:{archetype}", raw, report)
            existing[archetype] = clamped
            report.archetype_updates[archetype] = clamped

    def _apply_template_deltas(
        self,
        message_planner: object,
        deltas: Mapping[str, float],
        report: PriorApplicationReport,
    ) -> None:
        section_templates = getattr(message_planner, "section_templates", None)
        if not isinstance(section_templates, dict):
            for tmpl in deltas:
                report.skipped.append(
                    (
                        f"template:{tmpl}",
                        "message_planner.section_templates missing",
                    )
                )
            return
        # Note: the W4-P10 'template' axis labels are ``initial`` /
        # ``followup_1`` / ``followup_2`` — the FollowupCadenceEngine
        # message templates, NOT the MessagePlanner section names
        # (subject/hook/value/cta/signature). To keep the integration
        # additive, the applier writes the prior under a NAMESPACED key
        # ``cadence_prior_scores`` on the message_planner so the section
        # template structure is untouched.
        cadence_priors = getattr(
            message_planner, "cadence_prior_scores", None
        )
        if not isinstance(cadence_priors, dict):
            cadence_priors = {}
            setattr(message_planner, "cadence_prior_scores", cadence_priors)
        for tmpl, raw in deltas.items():
            clamped = self._clamp(f"template:{tmpl}", raw, report)
            cadence_priors[tmpl] = clamped
            report.template_updates[tmpl] = clamped

    def _apply_subject_deltas(
        self,
        subject_variant_priors: MutableMapping[str, float],
        deltas: Mapping[str, float],
        report: PriorApplicationReport,
    ) -> None:
        for variant, raw in deltas.items():
            clamped = self._clamp(
                f"subject_variant:{variant}", raw, report
            )
            subject_variant_priors[variant] = clamped
            report.subject_variant_updates[variant] = clamped


__all__ = [
    "PRIOR_SCORE_MAX",
    "PRIOR_SCORE_MIN",
    "PriorApplicationReport",
    "PriorDeltaApplier",
]
