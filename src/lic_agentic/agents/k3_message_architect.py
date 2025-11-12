"""Compose outreach drafts using reasoning toggles."""
from __future__ import annotations

from dataclasses import dataclass

from ..reasoning import cot, reflexion, tot
from ..reasoning.toggles import ReasoningToggles


@dataclass
class Draft:
    subject: str
    body: str

    def render(self) -> str:
        return f"Subject: {self.subject}\n\n{self.body}"


def score_quality(draft: str, reflexion: bool) -> int:
    """Return a simple heuristic quality score."""

    base = 5 if "value" in draft.lower() else 3
    return base + (2 if reflexion else 0)


class MessageArchitect:
    def __init__(self, toggles: ReasoningToggles):
        self.toggles = toggles

    def compose(self, sanitized_inputs, route_decision) -> str:
        prompt = getattr(sanitized_inputs, "prompt", "")
        steps = cot.expand(prompt, steps=3) if self.toggles.cot else []
        branches = tot.branch(prompt, branches=self.toggles.tot_branches)

        subject = f"Quick note for {sanitized_inputs.company_id or 'prospect'}"
        body_lines = [prompt or "Thanks for connecting!", "[artifact_id:baseline] Value proposition here."]
        if self.toggles.reflexion:
            body_lines.append("Reflexion insights applied.")
        body_lines.extend(steps)
        body_lines.extend(branches)
        draft = Draft(subject, "\n".join(body_lines)).render()

        if self.toggles.reflexion:
            draft = reflexion.apply_feedback(draft, "Highlight mutual benefit")
        return draft
