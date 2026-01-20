"""Compose outreach drafts using reasoning toggles and retrieval evidence."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Sequence, Tuple

from ..rag import ContentStore, EvidenceRegistry, RetrievalPlan
from ..rag.tool_registry import ToolRegistry, ToolResult
from ..reasoning import cot, reflexion, tot
from ..reasoning.toggles import ReasoningToggles

_ANCHOR_WINDOW_S = 60 * 60 * 24 * 90


@dataclass(frozen=True)
class Draft:
    subject: str
    body: str

    def render(self) -> str:
        return f"Subject: {self.subject}\n\n{self.body}"


@dataclass(frozen=True)
class DraftPackage:
    """Container describing the composed draft and supporting evidence."""  # pragma: no cover

    draft: str
    artifacts: Dict[str, str]
    total_latency_ms: int = 0

    def with_draft(self, new_draft: str) -> "DraftPackage":
        return DraftPackage(new_draft, dict(self.artifacts), self.total_latency_ms)


def score_quality(draft: str, reflexion: bool) -> int:
    """Return a simple heuristic quality score."""  # pragma: no cover

    base = 5 if "value" in draft.lower() else 3
    return base + (2 if reflexion else 0)


class MessageArchitect:
    """Construct outreach drafts with retrieval-backed evidence."""  # pragma: no cover

    def __init__(
        self,
        toggles: ReasoningToggles,
        *,
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

    def compose(
        self,
        sanitized_inputs,
        route_decision,
        *,
        max_calls: int | None = None,
    ) -> DraftPackage:
        prompt = getattr(sanitized_inputs, "prompt", "")
        wants = self._derive_wants(prompt, sanitized_inputs)
        plan = self._build_plan(wants, sanitized_inputs)
        plan.dedupe()
        plan.budget(max_calls or self._default_budget())
        retrievals = plan.execute(self.tool_registry, self.content_store)
        evidence = self._record_evidence(retrievals, sanitized_inputs)

        body_lines = self._compose_body(prompt, evidence)
        subject = self._subject_line(sanitized_inputs)
        draft = Draft(subject, "\n".join(body_lines)).render()

        if self.toggles.reflexion:
            draft = reflexion.apply_feedback(draft, "Highlight mutual benefit")

        artifacts = {artifact_id: summary for artifact_id, summary, _ in evidence}
        total_latency = sum(meta.get("latency_ms", 0) for _aid, _summary, meta in evidence)
        if not evidence:
            artifacts = {"baseline": "Value proposition here."}
        return DraftPackage(draft=draft, artifacts=artifacts, total_latency_ms=total_latency)

    # ------------------------------------------------------------------
    # Planning helpers
    # ------------------------------------------------------------------
    def _derive_wants(self, prompt: str, inputs) -> List[str]:
        wants: List[str] = []
        normalized_prompt = (prompt or "").strip()
        company_id = getattr(inputs, "company_id", None)
        contact_id = getattr(inputs, "contact_id", None)

        if normalized_prompt and not (company_id or contact_id):
            wants.append(f"Context for: {normalized_prompt}")
        if company_id:
            wants.append(f"{company_id} latest milestones")
            wants.append(f"{company_id} recent news")
        if contact_id:
            wants.append(f"{contact_id} profile highlights")

        if not wants:
            wants.append("Context for: prospect overview")
        return wants

    def _build_plan(self, wants: Sequence[str], inputs) -> RetrievalPlan:
        context = {
            "company_id": getattr(inputs, "company_id", None),
            "contact_id": getattr(inputs, "contact_id", None),
            "ttl_s": _ANCHOR_WINDOW_S,
        }
        plan = RetrievalPlan(wants, context)
        for want in wants[:6]:
            plan.add({"tool": self._select_tool_for_want(want), "query": want})
        return plan

    def _select_tool_for_want(self, want: str) -> str:
        lowered = want.lower()
        if "profile" in lowered or "contact" in lowered:
            return "profile_lookup"
        if "news" in lowered:
            return "news"
        return "web_search"

    def _default_budget(self) -> int:
        return max(2, min(6, int(self.toggles.tot_branches) + 2))

    # ------------------------------------------------------------------
    # Evidence helpers
    # ------------------------------------------------------------------
    def _record_evidence(self, retrievals, inputs) -> List[Tuple[str, str, Dict[str, object]]]:
        company_id = getattr(inputs, "company_id", None)
        scope = "outreach"
        evidence: List[Tuple[str, str, Dict[str, object]]] = []
        for source, job, payload in retrievals:
            summary, metadata = self._summarize_payload(payload, source)
            artifact_id = self.evidence_registry.upsert(
                scope=job.scope if hasattr(job, "scope") else scope,
                company_id=company_id,
                source_url=metadata["source"],
                summary=summary,
                anchor_date=datetime.utcnow().date().isoformat(),
                confidence=float(metadata.get("confidence", 0.6)),
                used_in_section=job.section if hasattr(job, "section") else "value_wedge",
                artifact_id=self._stable_artifact_id(job, company_id),
            )
            metadata["latency_ms"] = int(metadata.get("latency_ms", 0))
            evidence.append((artifact_id, summary, metadata))
        return evidence

    def _summarize_payload(self, payload, source_label: str) -> Tuple[str, Dict[str, object]]:
        if isinstance(payload, ToolResult):
            summary = payload.content
            source_url = payload.sources[0] if payload.sources else source_label
            metadata = {
                "source": source_url,
                "confidence": payload.confidence,
                "latency_ms": payload.latency_ms,
            }
            return summary, metadata
        summary = str(payload)
        return summary, {"source": source_label, "confidence": 0.5, "latency_ms": 0}

    # ------------------------------------------------------------------
    # Draft construction helpers
    # ------------------------------------------------------------------
    def _compose_body(
        self, prompt: str, evidence: Iterable[Tuple[str, str, Dict[str, object]]]
    ) -> List[str]:
        body_lines: List[str] = []
        intro = prompt or "Thanks for connecting!"
        body_lines.append(intro)

        for artifact_id, summary, _ in evidence:
            body_lines.append(f"[artifact_id:{artifact_id}] {summary}")

        if not evidence:
            body_lines.append("[artifact_id:baseline] Value proposition here.")

        if self.toggles.cot:
            body_lines.extend(cot.expand(intro, steps=self.toggles.min_tot_depth))
        branches = tot.branch(intro, branches=int(self.toggles.tot_branches))
        if branches:
            body_lines.append(branches[0])
        return body_lines

    def _subject_line(self, inputs) -> str:
        company_id = getattr(inputs, "company_id", None) or "prospect"
        return f"Quick note for {company_id}"

    def _stable_artifact_id(self, job, company_id: str | None) -> str:
        seed = f"{company_id or 'na'}|{getattr(job, 'tool', 'tool')}|{getattr(job, 'query', 'query')}|{getattr(job, 'section', 'section')}"
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
