"""Compose outreach drafts using reasoning toggles."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from ..rag import ContentStore, EvidenceRegistry, RetrievalPlan
from ..rag.tool_registry import ToolRegistry, ToolResult
from ..reasoning import cot, reflexion, tot
from ..reasoning.toggles import ReasoningToggles


@dataclass
class DraftPackage:
    """Container for the composed draft and supporting metadata."""

    draft: str
    artifacts: Dict[str, str]
    total_latency_ms: int = 0


def score_quality(draft: str, reflexion: bool) -> int:
    """Return a simple heuristic quality score."""

    base = 5 if "value" in draft.lower() else 3
    return base + (2 if reflexion else 0)


class MessageArchitect:
    def __init__(
        self,
        toggles: ReasoningToggles,
        tool_registry: ToolRegistry | None = None,
        content_store: ContentStore | None = None,
        evidence_registry: EvidenceRegistry | None = None,
    ) -> None:
        self.toggles = toggles
        self.tool_registry = tool_registry or ToolRegistry.default_with_builtins()
        self.content_store = content_store or ContentStore()
        self.evidence_registry = evidence_registry or EvidenceRegistry()

    def update_toggles(self, toggles: ReasoningToggles) -> None:
        self.toggles = toggles

    def compose(self, sanitized_inputs, route_decision, *, max_calls: int | None = None) -> DraftPackage:
        prompt = getattr(sanitized_inputs, "prompt", "")
        steps = cot.expand(prompt, steps=3) if self.toggles.cot else []
        branches = tot.branch(prompt, branches=self.toggles.tot_branches)

        wants = self._derive_wants(prompt, sanitized_inputs)
        plan = self._build_plan(wants, sanitized_inputs)
        plan.dedupe()
        plan.budget(max_calls=max_calls or 6)
        retrievals = plan.execute(self.tool_registry, self.content_store)
        evidence_items, total_latency = self._record_evidence(retrievals, sanitized_inputs)

        subject = f"Quick note for {sanitized_inputs.company_id or 'prospect'}"
        first_line = prompt or "Thanks for connecting!"
        lowered = first_line.lower()
        if not any(keyword in lowered for keyword in ("hello", "hi", "thanks", "thank you")):
            first_line = f"Hello there — {first_line}" if first_line else "Hello there"
        body_lines = [first_line]
        for artifact_id, summary in evidence_items:
            body_lines.append(f"[artifact_id:{artifact_id}] {summary}")
        artifacts: Dict[str, str]
        if evidence_items:
            artifacts = {artifact_id: summary for artifact_id, summary in evidence_items}
        else:
            placeholder_summary = "Value proposition here."
            body_lines.append(f"[artifact_id:baseline] {placeholder_summary}")
            artifacts = {"baseline": placeholder_summary}
        if self.toggles.reflexion:
            body_lines.append("Reflexion insights applied.")
        body_lines.extend(steps)
        body_lines.extend(branches)
        draft = f"Subject: {subject}\n\n" + "\n".join(body_lines)

        if self.toggles.reflexion:
            draft = reflexion.apply_feedback(draft, "Highlight mutual benefit")
        return DraftPackage(draft=draft, artifacts=artifacts, total_latency_ms=total_latency)

    def _derive_wants(self, prompt: str, sanitized_inputs) -> List[str]:
        wants: List[str] = []
        company = getattr(sanitized_inputs, "company_id", None)
        contact = getattr(sanitized_inputs, "contact_id", None)
        if company:
            wants.append(f"{company} latest milestones")
            wants.append(f"{company} recent news")
        if contact:
            wants.append(f"{contact} profile highlights")
        if not wants and prompt:
            wants.append(f"Context for: {prompt}")
        return wants

    def _build_plan(self, wants: Sequence[str], sanitized_inputs) -> RetrievalPlan:
        context = {
            "company_id": getattr(sanitized_inputs, "company_id", None),
            "contact_id": getattr(sanitized_inputs, "contact_id", None),
            "ttl_s": 60 * 60 * 24 * 90,
        }
        plan = RetrievalPlan(wants, context)
        for want in wants:
            plan.add(self._job_from_want(want))
        return plan

    def _job_from_want(self, want: str) -> dict:
        want_lower = want.lower()
        if "profile" in want_lower or "contact" in want_lower:
            tool = "profile_lookup"
            section = "personalization"
        elif "news" in want_lower:
            tool = "news"
            section = "credibility"
        else:
            tool = "web_search"
            section = "value_wedge"
        return {"tool": tool, "query": want, "scope": "outreach", "section": section}

    def _record_evidence(
        self,
        retrievals: Sequence[tuple[str, object, object]],
        sanitized_inputs,
    ) -> Tuple[List[Tuple[str, str]], int]:
        items: List[Tuple[str, str]] = []
        total_latency = 0
        company = getattr(sanitized_inputs, "company_id", None)
        for _source, job_obj, result in retrievals:
            job = job_obj
            if isinstance(result, ToolResult):
                summary = result.content
                source_url = result.sources[0] if result.sources else "https://example.com"
                confidence = result.confidence
                total_latency += int(result.latency_ms)
            else:
                summary = str(result)
                source_url = "https://example.com"
                confidence = 0.5
            artifact_id = self.evidence_registry.upsert(
                scope=getattr(job, "scope", "outreach"),
                company_id=company,
                source_url=source_url,
                summary=summary,
                anchor_date=self._anchor_date(),
                confidence=confidence,
                used_in_section=getattr(job, "section", "value_wedge"),
            )
            items.append((artifact_id, summary))
        return items, total_latency

    def _anchor_date(self) -> str:
        return "2025-01-01"
