"""parse_intent — turn a raw user request into a typed :class:`IntentFrame`.

Doctrine: ``02_L1_Reasoning_Plan_Generation_v4.md`` § PARSE INTENT (I1-I4).

This is the L1 reasoning entrypoint that runs *before* plan drafting.
It is deterministic and never retrieves evidence or calls tools — it
only inspects the visible request text and any caller-supplied hints.

Heuristic (small, defensible, replaceable by an LLM classifier later):

* I1 goal / success: caller supplies; if missing, derived from the first
  imperative clause of ``request_text``.
* I2 constraints: caller supplies; the parser also auto-extracts
  ``must / should / avoid`` keyword anchors as soft hints.
* I3 details: caller supplies; otherwise empty.
* I4 work class: re-uses :func:`classify_work_class` from the
  grounding-need feature module so the same WorkClass taxonomy
  drives both routing features and the IntentFrame.
"""

from __future__ import annotations

import re
from typing import Iterable

from agentic_core.L1_cognition.reasoning.ml_decision_support.features.grounding_need_features import (
    classify_work_class,
)
from agentic_core.L1_cognition.types.intent_frame_types import (
    ActionRequirement,
    AmbiguityRegister,
    AmbiguityResolutionStrategy,
    ArtifactRequirement,
    ConstraintBinding,
    FreshnessClass,
    IntentFrame,
    OutputTargetKind,
    WorkClass,
)

__all__ = ["parse_intent"]


_HIGH_RISK_TOKENS: frozenset[str] = frozenset(
    {
        "delete",
        "drop",
        "rm",
        "shutdown",
        "halt",
        "wire",
        "transfer",
        "deploy",
        "production",
        "irreversible",
        "force",
        "purge",
    }
)

_OUTPUT_KIND_HINTS: tuple[tuple[str, OutputTargetKind], ...] = (
    ("plan", OutputTargetKind.PLAN),
    ("artifact", OutputTargetKind.ARTIFACT),
    ("file", OutputTargetKind.ARTIFACT),
    ("report", OutputTargetKind.ARTIFACT),
    ("clarify", OutputTargetKind.CLARIFICATION),
    ("clarification", OutputTargetKind.CLARIFICATION),
    ("execute", OutputTargetKind.ACTION),
    ("perform", OutputTargetKind.ACTION),
    ("run", OutputTargetKind.ACTION),
)

# v5 doctrine inference tables.
_FRESHNESS_HINTS: tuple[tuple[re.Pattern[str], FreshnessClass], ...] = (
    (re.compile(r"\blive\b|\breal[- ]?time\b|\bstreaming\b", re.IGNORECASE), FreshnessClass.LIVE),
    (
        re.compile(r"\b(today|now|currently|right now|present|this conversation)\b", re.IGNORECASE),
        FreshnessClass.CURRENT,
    ),
    (re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\bon \w+ \d{1,2}\b", re.IGNORECASE), FreshnessClass.EXACT_DATE),
    (
        re.compile(r"\b(latest|recent|past (week|month|year)|last \d+|yesterday)\b", re.IGNORECASE),
        FreshnessClass.RECENT,
    ),
)

_ACTION_REQUIREMENT_HINTS: tuple[tuple[re.Pattern[str], ActionRequirement], ...] = (
    (
        re.compile(
            r"\b(delete|drop|wipe|purge|deploy to production|launch|fire|publish|send to all|broadcast|charge|wire transfer|terminate)\b",
            re.IGNORECASE,
        ),
        ActionRequirement.HIGH_IMPACT,
    ),
    (
        re.compile(
            r"\b(commit|merge|approve|finalize|sign off|push to|migrate|persist|store permanently|write to (db|database|disk))\b",
            re.IGNORECASE,
        ),
        ActionRequirement.WRITE_PROPOSAL,
    ),
    (
        re.compile(
            r"\b(toggle|draft|simulate|preview|dry[- ]?run|stage|disable|enable temporarily)\b", re.IGNORECASE
        ),
        ActionRequirement.REVERSIBLE,
    ),
    (
        re.compile(r"\b(read|fetch|retrieve|look up|show me|display|get|find|search)\b", re.IGNORECASE),
        ActionRequirement.READ_ONLY,
    ),
)

_ARTIFACT_HINTS: tuple[tuple[re.Pattern[str], ArtifactRequirement], ...] = (
    (
        re.compile(r"\bdiagram\b|\bflowchart\b|\bgraph\b|\bascii art\b", re.IGNORECASE),
        ArtifactRequirement.DIAGRAM,
    ),
    (
        re.compile(r"\bspreadsheet\b|\bxlsx?\b|\bcsv\b|\btable of\b", re.IGNORECASE),
        ArtifactRequirement.SPREADSHEET,
    ),
    (re.compile(r"\bslide\b|\bdeck\b|\bpresentation\b|\bpptx?\b", re.IGNORECASE), ArtifactRequirement.SLIDE),
    (
        re.compile(r"\bcode\b|\bscript\b|\bfunction\b|\bclass\b|\bsnippet\b", re.IGNORECASE),
        ArtifactRequirement.CODE,
    ),
    (
        re.compile(r"\bdoc(ument)?\b|\bword\b|\bdocx\b|\bmemo\b|\bemail\b", re.IGNORECASE),
        ArtifactRequirement.DOC,
    ),
    (re.compile(r"\bfile\b|\bupload\b|\bdownload\b", re.IGNORECASE), ArtifactRequirement.FILE),
)

_SEVERITY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bmust\b", re.IGNORECASE), "must"),
    (re.compile(r"\brequired\b", re.IGNORECASE), "must"),
    (re.compile(r"\bshould\b", re.IGNORECASE), "should"),
    (re.compile(r"\bprefer\b", re.IGNORECASE), "should"),
    (re.compile(r"\bavoid\b", re.IGNORECASE), "avoid"),
    (re.compile(r"\bdo not\b|\bdon't\b|\bnever\b", re.IGNORECASE), "avoid"),
)


def _infer_output_target(text: str) -> OutputTargetKind:
    lowered = text.lower()
    for needle, kind in _OUTPUT_KIND_HINTS:
        if needle in lowered:
            return kind
    return OutputTargetKind.ANSWER


def _infer_high_risk(text: str) -> bool:
    lowered = text.lower()
    return any(token in lowered for token in _HIGH_RISK_TOKENS)


def _infer_freshness_class(text: str) -> FreshnessClass:
    """v5 § INTENT FRAME — pick the most specific freshness signal.

    Order in ``_FRESHNESS_HINTS`` is most-specific-first; falls back to STABLE
    when no temporal signal is present.
    """
    for pattern, cls in _FRESHNESS_HINTS:
        if pattern.search(text):
            return cls
    return FreshnessClass.STABLE


def _infer_action_requirement(text: str) -> ActionRequirement:
    """v5 § INTENT FRAME — pick the most severe action class.

    Order is high-to-low so the strongest match wins (deploy beats read).
    """
    for pattern, req in _ACTION_REQUIREMENT_HINTS:
        if pattern.search(text):
            return req
    return ActionRequirement.NONE


def _infer_artifact_requirement(text: str) -> ArtifactRequirement:
    """v5 § INTENT FRAME — pick the most specific artifact form.

    Order is most-specific-first; defaults to INLINE so plain answers stay
    inline rather than auto-promoting to a file.
    """
    for pattern, req in _ARTIFACT_HINTS:
        if pattern.search(text):
            return req
    return ArtifactRequirement.INLINE


def _extract_constraint_hints(text: str) -> tuple[ConstraintBinding, ...]:
    """Pull rough must/should/avoid anchors. Conservative — no false-positive guard."""
    bindings: list[ConstraintBinding] = []
    seen: set[tuple[str, str]] = set()
    for sentence in re.split(r"[.;\n]+", text):
        s = sentence.strip()
        if not s:
            continue
        for pattern, severity in _SEVERITY_PATTERNS:
            if pattern.search(s):
                key = (s.lower(), severity)
                if key in seen:
                    continue
                seen.add(key)
                bindings.append(ConstraintBinding(statement=s, severity=severity, source="user"))
                break
    return tuple(bindings)


def parse_intent(
    request_text: str,
    *,
    request_id: str,
    goal: str | None = None,
    success_condition: str | None = None,
    constraints: Iterable[ConstraintBinding] | None = None,
    details: Iterable[str] | None = None,
    output_target_kind: OutputTargetKind | None = None,
    work_class: WorkClass | str | None = None,
    audience: str = "user",
    high_risk: bool | None = None,
    known: Iterable[str] = (),
    assumed: Iterable[str] = (),
    unresolved: Iterable[str] = (),
    resolution_strategy: AmbiguityResolutionStrategy | None = None,
    freshness_class: FreshnessClass | None = None,
    action_requirement: ActionRequirement | None = None,
    artifact_requirement: ArtifactRequirement | None = None,
) -> IntentFrame:
    """Build a validated :class:`IntentFrame` from a raw request.

    All ``None`` inputs are inferred from ``request_text`` deterministically.
    A caller that already classified the request (e.g., L0 ingress) should
    pass the explicit values to bypass inference.

    Raises:
        IntentFrameViolation: from the underlying ``IntentFrame.validate()``.
    """
    if not isinstance(request_text, str):
        raise TypeError("request_text must be str")
    text = request_text.strip()

    resolved_goal = (goal or text or "Respond to the user request").strip()
    resolved_success = (
        success_condition or "User receives a complete, policy-compliant deliverable."
    ).strip()

    # Constraints: caller-supplied first, then auto-extracted.
    user_constraints: tuple[ConstraintBinding, ...] = tuple(constraints) if constraints is not None else ()
    inferred = _extract_constraint_hints(text) if not user_constraints else ()
    resolved_constraints: tuple[ConstraintBinding, ...] = user_constraints + inferred

    resolved_details: tuple[str, ...] = tuple(details) if details is not None else ()

    if output_target_kind is None:
        resolved_output_kind = _infer_output_target(text)
    else:
        resolved_output_kind = output_target_kind

    if work_class is None:
        resolved_work_class: WorkClass = classify_work_class(text)
    elif isinstance(work_class, WorkClass):
        resolved_work_class = work_class
    else:
        resolved_work_class = WorkClass(work_class)

    resolved_high_risk: bool = _infer_high_risk(text) if high_risk is None else bool(high_risk)

    resolved_resolution = (
        resolution_strategy
        if resolution_strategy is not None
        else (AmbiguityResolutionStrategy.CLARIFY if any(unresolved) else AmbiguityResolutionStrategy.ASSUME)
    )

    ambiguity = AmbiguityRegister(
        known=tuple(known),
        assumed=tuple(assumed),
        unresolved=tuple(unresolved),
        resolution_strategy=resolved_resolution,
    )

    resolved_freshness = freshness_class if freshness_class is not None else _infer_freshness_class(text)
    resolved_action_req = (
        action_requirement if action_requirement is not None else _infer_action_requirement(text)
    )
    resolved_artifact_req = (
        artifact_requirement if artifact_requirement is not None else _infer_artifact_requirement(text)
    )

    frame = IntentFrame(
        request_id=request_id,
        goal=resolved_goal,
        success_condition=resolved_success,
        constraints=resolved_constraints,
        details=resolved_details,
        output_target_kind=resolved_output_kind,
        work_class=resolved_work_class,
        audience=audience,
        high_risk=resolved_high_risk,
        ambiguity=ambiguity,
        freshness_class=resolved_freshness,
        action_requirement=resolved_action_req,
        artifact_requirement=resolved_artifact_req,
    )
    frame.validate()
    return frame
