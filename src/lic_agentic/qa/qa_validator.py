"""Schema and evidence validation for outreach drafts."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, Sequence, Tuple


@dataclass(frozen=True)
class QAResult:
    """Outcome of a QA validation pass."""

    ok: bool
    reasons: Tuple[str, ...]
    missing_sections: Tuple[str, ...] = ()
    missing_artifacts: Tuple[str, ...] = ()

    def __bool__(self) -> bool:  # pragma: no cover - convenience
        return self.ok


class QAValidator:
    """Check structural and evidence requirements for outreach drafts."""

    _OPENER_KEYWORDS = ("hello", "hi", "thanks", "thank you", "appreciate")
    _CTA_KEYWORDS = ("cta:", "chat", "call", "meeting", "connect")
    _SIGNATURE_KEYWORDS = ("regards", "sincerely", "cheers", "best")

    def __init__(self, *, max_body_chars: int = 1500) -> None:
        self.max_body_chars = max_body_chars

    def validate(
        self,
        draft: str,
        artifacts: Dict[str, str],
        *,
        pii_placeholders: Iterable[str] = (),
    ) -> QAResult:
        lines = [line.rstrip() for line in draft.splitlines()]
        reasons: list[str] = []
        missing_sections: list[str] = []

        if not lines or not lines[0].lower().startswith("subject:"):
            reasons.append("Missing subject line")
            missing_sections.append("subject")

        body_lines = self._body_lines(lines)
        opener_line = next((line for line in body_lines if line.strip()), "")
        if not self._contains_keyword(opener_line, self._OPENER_KEYWORDS):
            reasons.append("Missing friendly opener")
            missing_sections.append("opener")

        artifact_pattern = re.compile(r"\[artifact_id:([^\]]+)\]")
        artifact_markers = set(artifact_pattern.findall(draft))
        if not artifact_markers:
            reasons.append("No evidence anchors present")
            missing_sections.append("value_wedge")

        missing_artifacts = sorted(set(artifacts.keys()) - artifact_markers)
        if missing_artifacts:
            reasons.append("Artifacts missing from draft: " + ", ".join(missing_artifacts))

        unknown_artifacts = sorted(artifact_markers - set(artifacts.keys()))
        if unknown_artifacts:
            reasons.append("Unknown artifact references: " + ", ".join(unknown_artifacts))

        body_text = "\n".join(body_lines)
        if len(body_text) > self.max_body_chars:
            reasons.append("Body exceeds character budget")

        if not self._has_keyword(body_lines, self._CTA_KEYWORDS):
            reasons.append("Missing call-to-action")
            missing_sections.append("cta")

        if not self._has_keyword(body_lines[-3:], self._SIGNATURE_KEYWORDS):
            reasons.append("Missing signature")
            missing_sections.append("signature")

        for placeholder in pii_placeholders:
            if placeholder and placeholder not in draft:
                reasons.append(f"Placeholder {placeholder} was not restored")

        missing_sections = tuple(dict.fromkeys(missing_sections))
        result = QAResult(
            ok=not reasons,
            reasons=tuple(reasons),
            missing_sections=missing_sections,
            missing_artifacts=tuple(missing_artifacts),
        )
        return result

    @staticmethod
    def _body_lines(lines: Sequence[str]) -> Sequence[str]:
        if not lines:
            return []
        body = list(lines[1:])
        while body and body[0] == "":
            body.pop(0)
        return body

    @staticmethod
    def _contains_keyword(text: str, keywords: Sequence[str]) -> bool:
        lowered = text.lower()
        return any(keyword in lowered for keyword in keywords)

    @classmethod
    def _has_keyword(cls, lines: Sequence[str], keywords: Sequence[str]) -> bool:
        return any(cls._contains_keyword(line, keywords) for line in lines if line.strip())
