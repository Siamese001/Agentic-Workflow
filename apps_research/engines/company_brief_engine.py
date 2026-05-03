"""CompanyBriefEngine — apps_research --mode company.

Produces a CompanyBrief conforming to apps_rg/schemas/company_research.schema.json.
Driven by Tavily research (when available) plus a synthesizing LLM call. Falls
back to a structured stub when neither is wired so the pipeline stays green
in offline test environments.

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P1.2).
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from apps_research.engines.base_research_engine import BaseResearchEngine

# Plan §P1.4 — V2 retrieval pipeline behind feature flag.
_RETRIEVAL_V2_FLAG = "APPS_RESEARCH_RETRIEVAL_V2"


def _v2_enabled() -> bool:
    """True when the V2 retrieval pipeline is opted-in via env flag."""
    return os.environ.get(_RETRIEVAL_V2_FLAG, "").strip() in {"1", "true", "yes", "on"}

_log = logging.getLogger(__name__)


def _emit_company_brief_marker(
    *,
    accepted: bool,
    model_used: str,
    fallback_reason: str,
    latency_ms: float = 0.0,
) -> None:
    """Best-effort ``JUDGE_DECISION`` emission for synthesis observability.

    Wave 3 P3.1 (plan apps-eval-qwen32b-rollout-b7c4d9). The marker is
    treated as a synthesis-availability observation — the
    judge-calibration harness uses it to track Qwen-vLLM uptime,
    parse-success rate, and cloud-fallback ratio for company-brief
    synthesis. Never raises.
    """
    try:
        from tools.capture.append_marker import append_marker  # noqa: PLC0415
    except ImportError:
        return
    payload = (
        "JUDGE_DECISION: type=judge_decision, "
        "app_name=apps_research.company_brief, "
        "rubric_id=company_brief_synthesis_v1, "
        "rubric_hash=inline, "
        f"accepted={accepted}, "
        "composite=0.0, "
        f"model_used={model_used}, "
        f"fallback_reason={fallback_reason}, "
        "first_failed_gate=none, "
        f"latency_ms={latency_ms:.1f}"
    )
    try:
        append_marker(payload, session_hint="apps_research.company_brief")
    except (OSError, PermissionError):
        pass


class CompanyBriefEngine(BaseResearchEngine):
    """Generates a CompanyBrief for a target company.

    Inputs:
        topic: company name (e.g., "Blend360")
        jd_anchor: optional path to job_description.json for facet weighting
        depth: shallow | standard | deep

    Output: dict matching the CompanyBrief schema. The caller is responsible
    for persisting and validating against pydantic.
    """

    AGENT_ID = "apps_research.company_brief_engine"

    # --- Tavily query templates (one per facet, decomposed; W1 Author-Gate B) -----
    _FACET_QUERIES = [
        ("overview", '{company} company overview tagline founding "core offerings"'),
        ("strategic_priorities", '{company} strategic priorities 2025 2026 announcements roadmap'),
        ("customer_profile", '{company} customers verticals industries case studies'),
        ("tech_stack_signals", '{company} technology stack platforms partners "we use"'),
        ("cultural_cues", '{company} culture values careers leadership philosophy'),
        ("leadership", '{company} leadership team CEO CTO executives'),
        ("competitive_set", '{company} competitors alternatives "vs"'),
        ("pain_points_inferred", '{company} challenges market pressures industry issues'),
        ("recent_moves", '{company} news 2025 acquisition partnership launch'),
        ("language", '{company} marketing copy "about us" mission positioning'),
    ]

    def execute(self, input_data: Any) -> Dict[str, Any]:
        topic: str = self._extract(input_data, "topic")
        if not topic or not isinstance(topic, str):
            raise ValueError("CompanyBriefEngine requires non-empty 'topic' (company name)")

        jd_anchor: Optional[Path] = None
        raw_anchor = self._extract(input_data, "jd_anchor", default=None)
        if raw_anchor:
            jd_anchor = Path(raw_anchor) if not isinstance(raw_anchor, Path) else raw_anchor

        depth = str(self._extract(input_data, "depth", default="standard"))

        jd_facets = self._load_jd_facets(jd_anchor)
        if _v2_enabled():
            research_findings = self._run_research_v2(topic=topic, depth=depth)
        else:
            research_findings = self._run_research(topic=topic, depth=depth)
        synthesized = self._synthesize(
            topic=topic, findings=research_findings, jd_facets=jd_facets, depth=depth
        )

        brief = self._assemble_brief(topic=topic, synthesis=synthesized)
        self.record_pass(
            f"CompanyBrief assembled for {topic}",
            data={"facets_synthesized": len(synthesized)},
        )
        return brief

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _extract(payload: Any, key: str, *, default: Any = None) -> Any:
        if hasattr(payload, key):
            return getattr(payload, key)
        if isinstance(payload, dict):
            return payload.get(key, default)
        return default

    def _load_jd_facets(self, jd_anchor: Optional[Path]) -> List[str]:
        if not jd_anchor or not jd_anchor.exists():
            return []
        try:
            data = json.loads(jd_anchor.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.logger.warning("[CompanyBriefEngine] JD anchor unreadable: %s", exc)
            return []
        # Light extraction — pull repeated nouns from the JD body if present.
        facets: List[str] = []
        for key in ("must_have", "nice_to_have", "responsibilities", "keywords"):
            v = data.get(key)
            if isinstance(v, list):
                facets.extend(str(x) for x in v if x)
        return facets

    def _run_research_v2(self, *, topic: str, depth: str) -> Dict[str, str]:
        """V2 retrieval pipeline: decompose → retrieve (parallel) → rerank → assemble.

        Plan §P1.4 + §P2.4 (parallel dispatch). Degrades to empty blobs
        when TAVILY_API_KEY or SDK unavailable. Uses a thread pool for
        per-sub-query retrieval (I/O-bound HTTP calls to Tavily) so
        wall-clock scales sub-linearly with fan-out.
        """
        import concurrent.futures

        from apps_research.engines.query_decomposer import SubQuery, decompose
        from apps_research.integrations.reranker_adapter import rerank
        from apps_research.integrations.tavily_retrieval import (
            apply_contextual_prefix,
            retrieve,
        )

        depth_norm = depth if depth in {"shallow", "standard", "deep"} else "standard"
        try:
            sub_queries = decompose(topic, depth=depth_norm)  # type: ignore[arg-type]
        except ValueError as exc:
            self.logger.warning("[CompanyBriefEngine v2] decompose failed: %s", exc)
            return {}

        def _fetch(sq: SubQuery) -> tuple[str, str]:
            try:
                docs = retrieve(sq.text, top_k=10)
            except (RuntimeError, ValueError) as exc:
                self.logger.info(
                    "[CompanyBriefEngine v2] retrieve skipped for facet=%s: %s",
                    sq.facet,
                    exc,
                )
                return sq.facet, ""
            top = rerank(sq.text, docs, cutoff=5)
            # Plan §P4.5 — wrap each chunk with Anthropic contextual prefix
            # so the downstream synthesizer sees the same template audit
            # grep uses (<document>/<chunk_context>).
            blob = "\n\n".join(
                apply_contextual_prefix(
                    f"- {d.title}: {d.snippet} ({d.url})",
                    doc_title=d.title,
                    surrounding_text=sq.text,
                )
                for d in top
                if d.snippet
            )
            return sq.facet, blob

        findings: Dict[str, str] = {}
        max_workers = max(1, min(5, len(sub_queries)))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            for facet, blob in pool.map(_fetch, sub_queries):
                findings[facet] = blob
        return findings

    def _run_research(self, *, topic: str, depth: str) -> Dict[str, str]:
        """Best-effort Tavily research per facet.

        Returns a dict {facet_name: text_blob}. Missing Tavily → empty blobs;
        the synthesizer downstream will produce a structured stub.
        """
        findings: Dict[str, str] = {f: "" for f, _ in self._FACET_QUERIES}
        try:
            from tools.retrieval.tavily_client import TavilySearchClient  # type: ignore
        except ImportError:
            self.logger.info(
                "[CompanyBriefEngine] Tavily client unavailable; using stub synthesis path"
            )
            return findings

        max_queries = {"shallow": 3, "standard": 6, "deep": 10}.get(depth, 6)
        try:
            client = TavilySearchClient()
        except Exception as exc:  # guardian: allow-broad-exception -- Tavily client init heterogeneous (HTTPError/ValueError/EnvironmentError); fail-soft to stub
            self.logger.warning("[CompanyBriefEngine] Tavily init failed: %s", exc)
            return findings

        for facet, q_template in self._FACET_QUERIES[:max_queries]:
            query = q_template.format(company=topic)
            try:
                resp = client.search(query=query, max_results=5)
                snippets = [r.get("content", "") for r in (resp or {}).get("results", [])]
                findings[facet] = "\n".join(snippets)[:4000]
            except Exception as exc:  # guardian: allow-broad-exception -- Tavily HTTP errors heterogeneous; per-facet fail-soft preserves partial brief
                self.logger.warning("[CompanyBriefEngine] Tavily query failed (%s): %s", facet, exc)
        return findings

    def _synthesize(
        self,
        *,
        topic: str,
        findings: Dict[str, str],
        jd_facets: List[str],
        depth: str,
    ) -> Dict[str, Any]:
        """LLM-synthesize raw research into structured facets.

        Wave 3 P3.1 (plan apps-eval-qwen32b-rollout-b7c4d9): try local
        Qwen-32B vLLM first; fall through to SovereignLLMGateway (cloud)
        when the local server is unavailable; deterministic stub when
        both gateways fail. Matches the cascade pattern established in
        Wave 2 for narrative_judge_scorer.
        """
        prompt = self._build_synthesis_prompt(topic=topic, findings=findings, jd_facets=jd_facets)

        qwen_payload = self._qwen_synthesize(prompt=prompt, topic=topic, jd_facets=jd_facets)
        if qwen_payload is not None:
            return qwen_payload

        try:
            from agentic_core.runtime.llm.sovereign_llm_gateway import (  # type: ignore
                SovereignLLMGateway,
            )
        except ImportError:
            return self._stub_synthesis(topic=topic, jd_facets=jd_facets)

        try:
            gateway = SovereignLLMGateway()
        except Exception as exc:  # guardian: allow-broad-exception -- LLM gateway init heterogeneous; fail-soft to stub keeps pipeline usable offline
            self.logger.warning(
                "[CompanyBriefEngine] LLM gateway unavailable (%s); using stub synthesis", exc
            )
            return self._stub_synthesis(topic=topic, jd_facets=jd_facets)

        try:
            resp = gateway.generate(prompt=prompt, max_tokens=2000, temperature=0.2)
            text = resp.text if hasattr(resp, "text") else str(resp)
            return self._parse_synthesis(text, topic=topic, jd_facets=jd_facets)
        except Exception as exc:  # guardian: allow-broad-exception -- LLM call paths raise heterogeneous (timeout/HTTP/parse); fail-soft to stub
            self.logger.warning("[CompanyBriefEngine] LLM synthesis failed: %s", exc)
            return self._stub_synthesis(topic=topic, jd_facets=jd_facets)

    def _qwen_synthesize(
        self,
        *,
        prompt: str,
        topic: str,
        jd_facets: List[str],
    ) -> Dict[str, Any] | None:
        """Synthesize via the local Qwen vLLM server.

        Returns the parsed synthesis dict on success, ``None`` when any
        guard rejects (preflight fail, SDK absent, model_registry absent,
        gateway exception, parse failure). The ``None`` return signals
        :meth:`_synthesize` to fall through to the cloud gateway.

        Emits a ``JUDGE_DECISION`` marker per call (treating the
        synthesis as a free-text generation that the calibration ledger
        observes; ``app_name=apps_research.company_brief``) so the
        weekly judge-calibration harness can spot drift in synthesis
        availability + parse-success rate.
        """
        try:
            from agentic_core.L2_execution.healers.vllm_health_probe import (  # noqa: PLC0415
                is_qwen_available,
            )
        except ImportError:
            return None
        if not is_qwen_available():
            _emit_company_brief_marker(
                accepted=False,
                model_used="deterministic_fallback",
                fallback_reason="preflight_failed",
            )
            return None

        try:
            import openai  # type: ignore  # noqa: PLC0415
        except ImportError:
            return None

        try:
            from agentic_core.L0_routing.config.model_registry import (  # noqa: PLC0415
                QWEN_LOCAL_MODEL_ID,
                VLLM_BASE_URL,
            )
        except ImportError:
            return None

        started = time.time()
        try:
            client = openai.OpenAI(
                base_url=VLLM_BASE_URL,
                api_key="not-needed",
                timeout=60.0,
            )
            resp = client.chat.completions.create(
                model=QWEN_LOCAL_MODEL_ID,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a corporate intelligence analyst producing strict "
                            "JSON output. Respond ONLY with valid JSON."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=2000,
            )
        except Exception as exc:  # guardian: allow-broad-exception -- OpenAI-SDK-over-vLLM raises heterogeneous (APIError/Connection/Timeout); fail-soft preserves cloud fallback
            self.logger.info("[CompanyBriefEngine] qwen call failed, falling back: %s", exc)
            _emit_company_brief_marker(
                accepted=False,
                model_used=QWEN_LOCAL_MODEL_ID,
                fallback_reason="gateway_exception",
                latency_ms=(time.time() - started) * 1000.0,
            )
            return None

        text = (resp.choices[0].message.content or "") if resp.choices else ""
        if not text.strip():
            _emit_company_brief_marker(
                accepted=False,
                model_used=QWEN_LOCAL_MODEL_ID,
                fallback_reason="empty_response",
                latency_ms=(time.time() - started) * 1000.0,
            )
            return None

        parsed = self._parse_synthesis(text, topic=topic, jd_facets=jd_facets)
        # _parse_synthesis returns the stub on any parse failure, which we
        # treat as a soft fallback (return None so the cloud path can try).
        if parsed.get("tagline", "").endswith("stub synthesis — research unavailable)"):
            _emit_company_brief_marker(
                accepted=False,
                model_used=QWEN_LOCAL_MODEL_ID,
                fallback_reason="parse_failure",
                latency_ms=(time.time() - started) * 1000.0,
            )
            return None

        _emit_company_brief_marker(
            accepted=True,
            model_used=QWEN_LOCAL_MODEL_ID,
            fallback_reason="none",
            latency_ms=(time.time() - started) * 1000.0,
        )
        return parsed

    @staticmethod
    def _build_synthesis_prompt(
        *, topic: str, findings: Dict[str, str], jd_facets: List[str]
    ) -> str:
        joined = "\n\n".join(
            f"### {facet}\n{(blob or '(no research available)')[:2000]}"
            for facet, blob in findings.items()
        )
        jd_hint = ", ".join(jd_facets[:25]) if jd_facets else "(none provided)"
        return (
            f"You are a corporate intelligence analyst. Produce a structured JSON brief "
            f"about the company {topic} suitable for downstream resume narrative work.\n\n"
            f"Use the research notes below; do NOT invent facts. If a facet is empty, "
            f"return a best-effort inference clearly marked or an empty list.\n\n"
            f"Job-description anchor terms (for relevance weighting): {jd_hint}\n\n"
            f"Research notes:\n{joined}\n\n"
            "Return strictly JSON with keys: tagline, core_offerings (list[str]), "
            "strategic_priorities (list[str], min 2), verticals (list[str]), "
            "buyer_titles (list[str]), tech_stack_signals (list[str]), "
            "cultural_cues (list[str]), leadership (list of {name,title,background}), "
            "competitive_set (list[str]), pain_points_inferred (list[str]), "
            "recent_moves (list of {date,event,signal}), language_to_mirror (list[str], min 3), "
            "language_to_avoid (list[str])."
        )

    def _parse_synthesis(
        self, text: str, *, topic: str, jd_facets: List[str]
    ) -> Dict[str, Any]:
        try:
            # Tolerant JSON extraction.
            first = text.find("{")
            last = text.rfind("}")
            if first >= 0 and last > first:
                return json.loads(text[first : last + 1])
        except (json.JSONDecodeError, ValueError) as exc:
            self.logger.warning("[CompanyBriefEngine] could not parse LLM JSON: %s", exc)
        return self._stub_synthesis(topic=topic, jd_facets=jd_facets)

    @staticmethod
    def _stub_synthesis(*, topic: str, jd_facets: List[str]) -> Dict[str, Any]:
        # Deterministic minimal-but-valid synthesis so the pipeline stays green
        # in offline/test environments. Marked clearly so downstream HOPs can
        # detect synthetic provenance.
        mirror_seed = jd_facets[:5] if jd_facets else [
            "consulting", "transformation", "data", "analytics", "AI"
        ]
        return {
            "tagline": f"{topic} (stub synthesis — research unavailable)",
            "core_offerings": ["consulting", "data engineering", "AI enablement"],
            "strategic_priorities": [
                "AI/agentic transformation for enterprise customers",
                "scaling consulting delivery across regulated industries",
            ],
            "verticals": ["financial services", "insurance", "healthcare", "retail"],
            "buyer_titles": ["Chief Data Officer", "Chief AI Officer", "VP Data"],
            "tech_stack_signals": ["AWS", "Snowflake", "Databricks"],
            "cultural_cues": ["partnership", "outcome-driven", "consultative"],
            "leadership": [],
            "competitive_set": [],
            "pain_points_inferred": [
                "scaling AI proofs-of-concept into production",
                "regulated-industry compliance for AI workloads",
            ],
            "recent_moves": [],
            "language_to_mirror": list(dict.fromkeys(mirror_seed + ["partnership", "outcomes"])),
            "language_to_avoid": ["world-class", "best-in-class", "leverage", "synergy"],
        }

    @staticmethod
    def _assemble_brief(*, topic: str, synthesis: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "company": topic,
            "fetched_at": now,
            "source": "apps_research",
            "freshness_ttl_days": 30,
            "overview": {
                "tagline": synthesis.get("tagline", topic),
                "founded": synthesis.get("founded"),
                "size_band": synthesis.get("size_band"),
                "ownership": synthesis.get("ownership"),
                "headquarters": synthesis.get("headquarters"),
                "core_offerings": synthesis.get("core_offerings", []) or [],
            },
            "strategic_priorities": synthesis.get("strategic_priorities", []) or [],
            "customer_profile": {
                "verticals": synthesis.get("verticals", []) or [],
                "buyer_titles": synthesis.get("buyer_titles", []) or [],
                "typical_engagement_size": synthesis.get("typical_engagement_size"),
            },
            "tech_stack_signals": synthesis.get("tech_stack_signals", []) or [],
            "cultural_cues": synthesis.get("cultural_cues", []) or [],
            "leadership": synthesis.get("leadership", []) or [],
            "competitive_set": synthesis.get("competitive_set", []) or [],
            "pain_points_inferred": synthesis.get("pain_points_inferred", []) or [],
            "recent_moves": synthesis.get("recent_moves", []) or [],
            "language_to_mirror": synthesis.get("language_to_mirror", []) or [],
            "language_to_avoid": synthesis.get("language_to_avoid", []) or [],
        }


__all__ = ["CompanyBriefEngine"]
