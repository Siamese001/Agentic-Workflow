"""CompanyBriefEngine — apps_research --mode company.

Produces a CompanyBrief conforming to apps_rg/schemas/company_research.schema.json.
Driven by Tavily research (when available) plus a synthesizing LLM call. Falls
back to a structured stub when neither is wired so the pipeline stays green
in offline test environments.

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P1.2).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from apps_research.engines.base_research_engine import BaseResearchEngine

# W2 (apps-research-spine-deferred-followup-9c3e1a P2.2) — import catalog
# and helpers from query_decomposer (L1 cognition layer). Re-export them
# here so existing test imports from company_brief_engine continue to work
# as a backward-compat shim.
from apps_research.engines.query_decomposer import (  # noqa: F401
    QueryPlan,
    _COVERAGE_FAMILY_CATALOG,
    _DEPTH_PARAM_MAP,
    _DEPTH_PROFILES,
    _PROFILE_REQUIRED_FAMILIES,
    _resolve_depth_profile,
    decompose_coverage_families,
)

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
        _t0 = time.perf_counter()
        _sub_stages: list[dict[str, Any]] = []

        topic: str = self._extract(input_data, "topic")
        if not topic or not isinstance(topic, str):
            raise ValueError("CompanyBriefEngine requires non-empty 'topic' (company name)")

        raw_depth = str(self._extract(input_data, "depth", default="standard"))
        depth_profile = _resolve_depth_profile(raw_depth)

        # --- Sub-stage: intake ---
        _t_intake = time.perf_counter()
        jd_context: Dict[str, Any] = self._resolve_jd_context(input_data)
        _sub_stages.append({
            "sub_stage_id": "research.intake",
            "sub_stage_name": "Intake + JD Resolution",
            "status": "PASS",
            "duration_ms": round((time.perf_counter() - _t_intake) * 1000, 3),
            "meta": {"topic": topic, "depth": depth_profile},
        })

        # --- Sub-stage: research ---
        _t_research = time.perf_counter()
        if _v2_enabled():
            research_findings = self._run_research_v2(topic=topic, depth=raw_depth)
        else:
            research_findings = self._run_research_adaptive(
                topic=topic, depth_profile=depth_profile, jd_context=jd_context
            )
        _sub_stages.append({
            "sub_stage_id": "research.fetch",
            "sub_stage_name": "Evidence Retrieval",
            "status": "PASS",
            "duration_ms": round((time.perf_counter() - _t_research) * 1000, 3),
            "meta": {"v2": _v2_enabled()},
        })

        # --- Sub-stage: JD facets ---
        _t_jd = time.perf_counter()
        jd_anchor: Optional[Path] = None
        raw_anchor = self._extract(input_data, "jd_anchor", default=None)
        if raw_anchor:
            jd_anchor = Path(raw_anchor) if not isinstance(raw_anchor, Path) else raw_anchor
        jd_facets = self._load_jd_facets(jd_anchor)
        _sub_stages.append({
            "sub_stage_id": "research.jd_facets",
            "sub_stage_name": "JD Facet Extraction",
            "status": "PASS",
            "duration_ms": round((time.perf_counter() - _t_jd) * 1000, 3),
            "meta": {"facets_count": len(jd_facets)},
        })

        # --- Sub-stage: synthesize ---
        _t_synth = time.perf_counter()
        profile_cfg = _DEPTH_PROFILES[depth_profile]
        synthesized = self._synthesize(
            topic=topic,
            findings=research_findings,
            jd_facets=jd_facets,
            depth=depth_profile,
            jd_context=jd_context,
            jd_anchor=jd_anchor,
        )
        _sub_stages.append({
            "sub_stage_id": "research.synthesize",
            "sub_stage_name": "LLM Synthesis",
            "status": "PASS",
            "duration_ms": round((time.perf_counter() - _t_synth) * 1000, 3),
            "meta": {"facets": len(synthesized)},
        })

        # --- Sub-stage: C0 bundle + gate ---
        _t_c0 = time.perf_counter()
        c0_bundle = self._build_c0_bundle(
            topic=topic,
            depth_profile=depth_profile,
            profile_cfg=profile_cfg,
            findings=research_findings,
            synthesis=synthesized,
            jd_context=jd_context,
        )
        gate_verdict, gate_caveat, degraded_reason = self._evaluate_c0_pa_gate(
            c0_bundle=c0_bundle, depth_profile=depth_profile
        )
        c0_bundle["synthesis_guidance"]["gate_verdict"] = gate_verdict
        c0_bundle["synthesis_guidance"]["gate_caveat"] = gate_caveat
        c0_bundle["synthesis_guidance"]["degraded_packet_reason"] = degraded_reason
        _sub_stages.append({
            "sub_stage_id": "research.c0_gate",
            "sub_stage_name": "C0 Bundle + Gate Evaluation",
            "status": "PASS" if gate_verdict == "PASS" else "FAIL",
            "duration_ms": round((time.perf_counter() - _t_c0) * 1000, 3),
            "meta": {"gate_verdict": gate_verdict},
        })

        # --- Sub-stage: assemble ---
        _t_assemble = time.perf_counter()
        brief = self._assemble_brief(topic=topic, synthesis=synthesized)
        brief["_c0_bundle"] = c0_bundle
        brief["_depth_profile"] = depth_profile
        brief["_gate_verdict"] = gate_verdict
        brief["_sub_stages"] = _sub_stages
        if jd_context:
            brief["_jd_context"] = dict(jd_context)
        targeting_md = str(synthesized.get("apps_rg_targeting_brief_markdown") or "").strip()
        if targeting_md:
            brief["apps_rg_targeting_brief_text"] = targeting_md
            brief["company_brief_text"] = targeting_md
        _sub_stages.append({
            "sub_stage_id": "research.assemble",
            "sub_stage_name": "Brief Assembly",
            "status": "PASS",
            "duration_ms": round((time.perf_counter() - _t_assemble) * 1000, 3),
            "meta": {},
        })

        self.record_pass(
            f"CompanyBrief assembled for {topic} [{depth_profile}] gate={gate_verdict}",
            data={"facets_synthesized": len(synthesized), "depth_profile": depth_profile,
                  "gate_verdict": gate_verdict, "jd_present": bool(jd_context),
                  "total_ms": round((time.perf_counter() - _t0) * 1000, 1)},
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
        jd_context: Dict[str, Any] | None = None,
        jd_anchor: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """LLM-synthesize raw research into structured facets.

        Wave 3 P3.1 (plan apps-eval-qwen32b-rollout-b7c4d9): try local
        Qwen-32B vLLM first; fall through to SovereignLLMGateway (cloud)
        when the local server is unavailable; deterministic stub when
        both gateways fail. Matches the cascade pattern established in
        Wave 2 for narrative_judge_scorer.

        When ``apps_rg_targeting_brief_enabled`` (env or jd_context), emits
        apps_rg targeting markdown per ``apps_rg_targeting_brief_v1.md``.
        """
        from apps_research.prompt_assembly.apps_rg_targeting_brief import (  # noqa: PLC0415
            apps_rg_targeting_brief_enabled,
        )

        if apps_rg_targeting_brief_enabled(jd_context=jd_context):
            return self._synthesize_apps_rg_targeting_brief(
                topic=topic,
                findings=findings,
                jd_context=jd_context or {},
                jd_anchor=jd_anchor,
            )

        prompt = self._build_synthesis_prompt(topic=topic, findings=findings, jd_facets=jd_facets)

        # Strict mode: fail loud with categorized diagnostic when the operator
        # explicitly required Qwen (APPS_RESEARCH_REQUIRE_QWEN=1). Distinguishes
        # Docker Desktop down vs vLLM container down vs model not loaded so the
        # error message is actionable. Cloud/stub fallbacks are intentionally
        # bypassed in strict mode.
        from apps_research.integrations.qwen_strict_probe import (
            maybe_enforce_qwen_strict_requirement,
        )

        maybe_enforce_qwen_strict_requirement()

        qwen_payload = self._qwen_synthesize(prompt=prompt, topic=topic, jd_facets=jd_facets)
        if qwen_payload is not None:
            return qwen_payload

        gemini_payload = self._gemini_synthesize(prompt=prompt, topic=topic, jd_facets=jd_facets)
        if gemini_payload is not None:
            return gemini_payload

        return self._stub_synthesis(topic=topic, jd_facets=jd_facets)

    def _gemini_synthesize(
        self,
        *,
        prompt: str,
        topic: str,
        jd_facets: List[str],
    ) -> Dict[str, Any] | None:
        """Synthesize via Google Gemini 3.1 Pro Preview (cloud cascade tier 2).

        Mirrors :meth:`_qwen_synthesize`. Reads `GOOGLE_API_KEY` and
        ``GOOGLE_AI_PRO_MODEL`` (deprecated alias ``GEMINI_PRO_MODEL``,
        default ``gemini-3.1-pro-preview``) from the
        environment. Returns the parsed synthesis dict on success, ``None``
        when any guard rejects (SDK absent, key missing, API exception,
        empty response, parse failure). The ``None`` return signals
        :meth:`_synthesize` to fall through to the deterministic stub.

        Per `.env.example` doctrine, ``GOOGLE_AI_PRO_MODEL`` is the
        synthesis-quality / structural-novel-failure escalation tier;
        ``GOOGLE_AI_MODEL`` / ``GEMINI_MODEL`` (flash) is for cheap fallback
        when Pro is exhausted or mismatched vs Pro.
        """
        import os  # noqa: PLC0415 — local import keeps module cold-load cheap

        try:
            from google import genai  # noqa: PLC0415
        except ImportError:
            self.logger.info("[CompanyBriefEngine] google-genai SDK not installed; skipping Gemini fallback")
            return None

        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            self.logger.info("[CompanyBriefEngine] GOOGLE_API_KEY/GEMINI_API_KEY not set; skipping Gemini fallback")
            return None

        # Try Pro first (synthesis-quality tier) then Flash (cheap-fast). Free-tier
        # Google AI Studio accounts have limit:0 for Pro models so the cascade
        # resolves to Flash; paid-tier accounts hit Pro and never reach Flash.
        from agentic_core.config.google_ai_env_reads import (  # noqa: PLC0415
            google_ai_flash_model_env,
            google_ai_pro_model_env,
        )

        candidates: list[str] = []
        pro_model = google_ai_pro_model_env(legacy_default="gemini-3.1-pro-preview").strip()
        flash_model = google_ai_flash_model_env(legacy_default="gemini-3-flash-preview").strip()
        if pro_model:
            candidates.append(pro_model)
        if flash_model and flash_model != pro_model:
            candidates.append(flash_model)
        if not candidates:
            return None

        client = genai.Client(api_key=api_key)
        last_error: Exception | None = None
        for model_name in candidates:
            started = time.time()
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=(
                        "You are a research analyst producing structured company briefs. "
                        "Always answer with strict JSON matching the schema in the user prompt.\n\n"
                        + prompt
                    ),
                    config={
                        "temperature": 0.2,
                        "max_output_tokens": 2000,
                    },
                )
            except Exception as exc:  # guardian: allow-broad-exception -- google-genai raises heterogeneous (APIError/Connection/Timeout/InvalidArgument); fail-soft preserves stub fallback
                last_error = exc
                self.logger.info(
                    "[CompanyBriefEngine] gemini model=%s failed (%s); trying next candidate",
                    model_name,
                    type(exc).__name__,
                )
                _emit_company_brief_marker(
                    accepted=False,
                    model_used=model_name,
                    fallback_reason="gemini_exception",
                    latency_ms=(time.time() - started) * 1000.0,
                )
                continue

            text = (resp.text or "").strip() if hasattr(resp, "text") else ""
            if not text:
                _emit_company_brief_marker(
                    accepted=False,
                    model_used=model_name,
                    fallback_reason="gemini_empty_response",
                    latency_ms=(time.time() - started) * 1000.0,
                )
                continue

            parsed = self._parse_synthesis(text, topic=topic, jd_facets=jd_facets)
            if parsed.get("tagline", "").endswith("stub synthesis — research unavailable)"):
                _emit_company_brief_marker(
                    accepted=False,
                    model_used=model_name,
                    fallback_reason="gemini_parse_failure",
                    latency_ms=(time.time() - started) * 1000.0,
                )
                continue

            _emit_company_brief_marker(
                accepted=True,
                model_used=model_name,
                fallback_reason="none",
                latency_ms=(time.time() - started) * 1000.0,
            )
            return parsed

        if last_error is not None:
            self.logger.info(
                "[CompanyBriefEngine] all Gemini candidates exhausted (last error: %s); falling back to stub",
                last_error,
            )
        return None

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
            from apps_research.integrations.llm_client import OpenAI as _OpenAI  # noqa: PLC0415
            if _OpenAI is None:
                return None
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
            client = _OpenAI(
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

    def _synthesize_apps_rg_targeting_brief(
        self,
        *,
        topic: str,
        findings: Dict[str, str],
        jd_context: Dict[str, Any],
        jd_anchor: Optional[Path],
    ) -> Dict[str, Any]:
        """Synthesize apps_rg === SECTION === targeting brief (plain markdown)."""
        from apps_research.prompt_assembly.apps_rg_targeting_brief import (  # noqa: PLC0415
            build_targeting_brief_prompt,
            extract_jd_text,
            format_research_findings,
        )

        jd_text = extract_jd_text(jd_context=jd_context, jd_anchor=jd_anchor)
        research_notes = format_research_findings(findings)
        prompt = build_targeting_brief_prompt(
            jd_text=jd_text,
            research_notes=research_notes,
            target_entity=topic,
        )
        markdown = self._call_llm_plain_markdown(prompt)
        if not markdown.strip():
            markdown = self._stub_targeting_brief_markdown(topic=topic, jd_text=jd_text)
        stub = self._stub_synthesis(topic=topic, jd_facets=[])
        stub["apps_rg_targeting_brief_markdown"] = markdown.strip()
        stub["synthesis_template"] = "apps_rg_targeting_brief_synthesis_v1"
        return stub

    def _call_llm_plain_markdown(self, prompt: str) -> str:
        """Qwen → Gemini cascade for plain-text targeting brief output."""
        from apps_research.integrations.qwen_strict_probe import (  # noqa: PLC0415
            maybe_enforce_qwen_strict_requirement,
        )

        maybe_enforce_qwen_strict_requirement()
        text = self._qwen_synthesize_plain(prompt=prompt)
        if text:
            return text
        text = self._gemini_synthesize_plain(prompt=prompt)
        return text or ""

    def _qwen_synthesize_plain(self, *, prompt: str) -> str | None:
        try:
            from agentic_core.L2_execution.healers.vllm_health_probe import (  # noqa: PLC0415
                is_qwen_available,
            )
        except ImportError:
            return None
        if not is_qwen_available():
            return None
        try:
            from apps_research.integrations.llm_client import OpenAI as _OpenAI  # noqa: PLC0415
            if _OpenAI is None:
                return None
        except ImportError:
            return None
        try:
            from agentic_core.L0_routing.config.model_registry import (  # noqa: PLC0415
                QWEN_LOCAL_MODEL_ID,
                VLLM_BASE_URL,
            )
        except ImportError:
            return None
        try:
            client = _OpenAI(base_url=VLLM_BASE_URL, api_key="not-needed", timeout=90.0)
            resp = client.chat.completions.create(
                model=QWEN_LOCAL_MODEL_ID,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You produce apps_rg targeting briefs only. "
                            "Output plain markdown exactly as instructed. No JSON. No fences."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=1200,
            )
        except Exception as exc:  # guardian: allow-broad-exception -- vLLM fail-soft
            self.logger.info("[CompanyBriefEngine] targeting brief qwen failed: %s", exc)
            return None
        return (resp.choices[0].message.content or "").strip() if resp.choices else ""

    def _gemini_synthesize_plain(self, *, prompt: str) -> str | None:
        import os  # noqa: PLC0415

        try:
            from google import genai  # noqa: PLC0415
        except ImportError:
            return None
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None
        from agentic_core.config.google_ai_env_reads import (  # noqa: PLC0415
            google_ai_flash_model_env,
            google_ai_pro_model_env,
        )

        candidates: list[str] = []
        pro_model = google_ai_pro_model_env(legacy_default="gemini-3.1-pro-preview").strip()
        flash_model = google_ai_flash_model_env(legacy_default="gemini-3-flash-preview").strip()
        if pro_model:
            candidates.append(pro_model)
        if flash_model and flash_model != pro_model:
            candidates.append(flash_model)
        if not candidates:
            return None
        client = genai.Client(api_key=api_key)
        for model_name in candidates:
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=(
                        "You produce apps_rg targeting briefs only. "
                        "Output plain markdown exactly as instructed. No JSON. No fences.\n\n"
                        + prompt
                    ),
                    config={"temperature": 0.2, "max_output_tokens": 1200},
                )
            except Exception as exc:  # guardian: allow-broad-exception -- gemini fail-soft
                self.logger.info(
                    "[CompanyBriefEngine] targeting brief gemini model=%s failed: %s",
                    model_name,
                    exc,
                )
                continue
            text = (resp.text or "").strip() if hasattr(resp, "text") else ""
            if text:
                return text
        return None

    @staticmethod
    def _stub_targeting_brief_markdown(*, topic: str, jd_text: str) -> str:
        role_line = "target role"
        for line in jd_text.splitlines()[:8]:
            low = line.lower()
            if "title" in low or "role" in low or "position" in low:
                role_line = line.strip()[:80] or role_line
                break
        return (
            f"{topic} (TBD) - {role_line} targeting brief\n"
            "| TBD | TBD | Reports to TBD (TBD) |\n\n"
            "=== STRATEGIC MANDATE ===\n"
            f"- {topic} (stub synthesis — research unavailable)\n"
            "- Core strategic pressure TBD pending verified research\n"
            "- Recent AI or platform move TBD\n"
            "- Central tension: growth vs control TBD\n\n"
            "=== LEADERSHIP ===\n"
            "- CEO: TBD\n"
            "- Technology leader: TBD\n"
            "- Data or AI leader: TBD\n"
            "- Key EVP: TBD\n\n"
            "=== TECH & AI PLATFORM ===\n"
            "- Platform posture TBD\n"
            "- Cloud or integration angle TBD\n"
            "- M&A or transformation fact TBD\n"
            "- Peer move TBD\n\n"
            "=== BUSINESS CONTEXT (JD alignment hooks) ===\n"
            "- Segment 1: TBD\n"
            "- Segment 2: TBD\n"
            "- AI or data priority TBD\n"
            "- Culture or execution hook TBD\n\n"
            "=== EXEC SUMMARY FRAMING (not proof) ===\n"
            "- Lead with commercial outcome TBD\n"
            "- Mirror verified company priority TBD\n"
            "- 12-month win TBD\n"
        )

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

    # ------------------------------------------------------------------
    # W2 C0 pipeline methods
    # (apps-research-spine-deferred-followup-9c3e1a P2.2)
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_jd_context(input_data: Any) -> Dict[str, Any]:
        """Extract and normalise JD context from input_data.

        Accepts either a plain dict under 'jd_context' key or a
        'jd_anchor' path. Computes jd_content_hash when absent.
        """
        jd: Any = None
        if isinstance(input_data, dict):
            jd = input_data.get("jd_context")
        elif hasattr(input_data, "jd_context"):
            jd = getattr(input_data, "jd_context", None)

        if not isinstance(jd, dict) or not jd:
            return {}

        result: Dict[str, Any] = dict(jd)
        # Compute content hash when absent
        if not result.get("jd_content_hash"):
            content = str(result.get("content") or result.get("jd_ref") or "")
            if content:
                result["jd_content_hash"] = "sha256-" + hashlib.sha256(
                    content.encode("utf-8")
                ).hexdigest()[:16]
        return result

    def _run_research_adaptive(
        self,
        *,
        topic: str,
        depth_profile: str,
        jd_context: Dict[str, Any],
    ) -> Dict[str, str]:
        """Run research using coverage-family fan-out from query_decomposer.

        Delegates family selection + query generation to
        ``decompose_coverage_families()``. Uses
        ``apps_research.integrations.tavily_retrieval.retrieve`` (the
        canonical Tavily adapter) for the actual searches. Degrades
        gracefully when ``TAVILY_API_KEY`` is unset or the SDK is missing
        — returns empty blobs per family so offline test environments
        stay green.
        """
        plans = decompose_coverage_families(topic, depth_profile, jd_context or None)
        findings: Dict[str, str] = {p.family: "" for p in plans}

        try:
            from apps_research.integrations.tavily_retrieval import retrieve
        except ImportError:
            self.logger.info(
                "[CompanyBriefEngine] tavily_retrieval module unavailable; returning stub findings"
            )
            return findings

        profile_cfg = _DEPTH_PROFILES.get(depth_profile, _DEPTH_PROFILES["COMPANY_BRIEF_STANDARD"])
        max_queries = profile_cfg["max_queries"]

        for plan in plans[:max_queries]:
            try:
                docs = retrieve(plan.query, top_k=5)
            except RuntimeError as exc:
                # TAVILY_API_KEY missing or SDK absent — first failure aborts
                # the whole loop because every retrieve() call would fail
                # the same way; preserves any blobs already collected.
                self.logger.warning(
                    "[CompanyBriefEngine] Tavily unavailable (%s); aborting fan-out", exc
                )
                break
            except Exception as exc:  # guardian: allow-broad-exception -- per-family Tavily HTTP errors heterogeneous; fail-soft preserves partial brief
                self.logger.warning(
                    "[CompanyBriefEngine] Tavily query failed (family=%s): %s",
                    plan.family,
                    exc,
                )
                continue
            snippets: list[str] = []
            for d in docs:
                if not (d.snippet or "").strip():
                    continue
                snippets.append(f"{d.title}: {d.snippet}")
                if d.url:
                    # URL on its own line so _build_c0_bundle's
                    # startswith("http") extractor picks it up for
                    # source_portfolio_summary.source_urls.
                    snippets.append(d.url)
            findings[plan.family] = "\n".join(snippets)[:4000]
        return findings

    def _build_c0_bundle(
        self,
        *,
        topic: str,
        depth_profile: str,
        profile_cfg: Dict[str, Any],
        findings: Dict[str, str],
        synthesis: Dict[str, Any],
        jd_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build the 7-object C0 output bundle from research findings + synthesis."""
        required_families = list(
            _PROFILE_REQUIRED_FAMILIES.get(depth_profile, [])
        )
        jd_present = bool(jd_context)

        # ── BriefingCoverageMatrix ──────────────────────────────────────────
        coverage_entries: List[Dict[str, Any]] = []
        covered = 0
        for fam in required_families:
            blob = findings.get(fam, "")
            has_content = bool(blob and blob.strip())
            if has_content:
                covered += 1
            coverage_entries.append({"family": fam, "covered": has_content, "source_count": len(blob.split("\n")) if has_content else 0})

        jd_req_families = ["role_context", "tech_stack_and_tools"] if jd_present else []
        jd_covered = sum(
            1 for f in jd_req_families if (findings.get(f) or "").strip()
        )
        overall_coverage_score = covered / len(required_families) if required_families else 0.0
        jd_coverage_score = jd_covered / len(jd_req_families) if jd_req_families else 0.0
        briefing_coverage_matrix = {
            "profile_id": depth_profile,
            "families": coverage_entries,
            "overall_coverage_score": round(overall_coverage_score, 4),
            "jd_coverage_score": round(jd_coverage_score, 4),
            "recruiter_outreach_overlay_present": False,
        }

        # ── SourcePortfolioSummary ──────────────────────────────────────────
        # Count explicit URL lines for grounded evidence; fall back to
        # non-empty content lines as citation-anchor proxies (offline/stub mode).
        all_urls: List[str] = []
        all_content_lines: List[str] = []
        for blob in findings.values():
            for line in blob.split("\n"):
                stripped_line = line.strip()
                if not stripped_line:
                    continue
                all_content_lines.append(stripped_line)
                if stripped_line.startswith("http"):
                    all_urls.append(stripped_line)

        total_url_sources = len(set(all_urls))
        total_citation_anchors = len(all_urls) if all_urls else len(all_content_lines)
        # total_final_sources: prefer unique URL count; fall back to covered family count
        total_sources = total_url_sources if total_url_sources > 0 else covered
        source_portfolio_summary = {
            "total_final_sources": total_sources,
            "total_citation_anchors": total_citation_anchors,
            "authoritative_anchor_present": total_sources > 0,
            "source_urls": sorted(set(all_urls))[:50],
        }

        # ── ClaimEvidenceMap ────────────────────────────────────────────────
        unsupported = max(0, len(required_families) - covered)
        claim_evidence_map = {
            "total_claims": len(required_families),
            "supported_count": covered,
            "unsupported_direct_evidence_count": unsupported,
            "unsupported_claim_count": unsupported,
        }

        # ── ContradictionMatrix ─────────────────────────────────────────────
        contradiction_matrix = {
            "total_contradictions": 0,
            "unresolved_critical": 0,
            "resolved_count": 0,
        }

        # ── FreshnessReport ─────────────────────────────────────────────────
        freshness_report = {
            "policy_id": f"freshness::apps_research::{depth_profile.split('_')[-1].lower()}",
            "sources": [],
            "stale_excluded_count": 0,
            "gate_fail_triggered": False,
            "stale_section_ids": [],
        }

        # ── SectionGapReport ────────────────────────────────────────────────
        gap_families = [fam for fam in required_families if not (findings.get(fam) or "").strip()]
        section_gap_report = {
            "gap_families": gap_families,
            "gap_count": len(gap_families),
        }

        # ── SynthesisGuidance ───────────────────────────────────────────────
        synthesis_guidance: Dict[str, Any] = {
            "depth_profile": depth_profile,
            "gate_verdict": "PENDING",
            "gate_caveat": "",
            "degraded_packet_reason": "",
            "ordered_sections": required_families,
        }
        if jd_present:
            synthesis_guidance["jd_focal_angle"] = jd_context.get("jd_ref", "")
            synthesis_guidance["apps_rg_downstream_fields"] = {
                "jd_ref": jd_context.get("jd_ref"),
                "jd_content_hash": jd_context.get("jd_content_hash"),
                "responsibilities": jd_context.get("responsibilities", []),
            }

        # ── JD context block ────────────────────────────────────────────────
        bundle: Dict[str, Any] = {
            "briefing_coverage_matrix": briefing_coverage_matrix,
            "source_portfolio_summary": source_portfolio_summary,
            "claim_evidence_map": claim_evidence_map,
            "contradiction_matrix": contradiction_matrix,
            "freshness_report": freshness_report,
            "section_gap_report": section_gap_report,
            "synthesis_guidance": synthesis_guidance,
        }
        if jd_present:
            bundle["jd_context"] = dict(jd_context)

        return bundle

    def _evaluate_c0_pa_gate(
        self,
        *,
        c0_bundle: Dict[str, Any],
        depth_profile: str,
    ) -> tuple[str, str, str]:
        """Evaluate the C0 PA gate; return (verdict, caveat, degraded_reason).

        Verdict values: 'PASS', 'WEAK_WITH_CAVEATS', 'FAIL'.
        """
        profile_cfg = _DEPTH_PROFILES.get(
            depth_profile, _DEPTH_PROFILES["COMPANY_BRIEF_STANDARD"]
        )
        min_sources = profile_cfg["min_sources"]
        coverage_floor = profile_cfg["coverage_floor"]
        gate_weak_floor = profile_cfg["gate_weak_floor"]

        sps = c0_bundle.get("source_portfolio_summary", {})
        total_sources = sps.get("total_final_sources", 0)
        authoritative = sps.get("authoritative_anchor_present", False)

        bcm = c0_bundle.get("briefing_coverage_matrix", {})
        coverage_score = bcm.get("overall_coverage_score", 0.0)

        contradiction_matrix = c0_bundle.get("contradiction_matrix", {})
        unresolved_critical = contradiction_matrix.get("unresolved_critical", 0)

        freshness = c0_bundle.get("freshness_report", {})
        freshness_fail = freshness.get("gate_fail_triggered", False)

        cem = c0_bundle.get("claim_evidence_map", {})
        unsupported = cem.get("unsupported_direct_evidence_count", 0)

        # Hard-fail conditions
        if total_sources < min_sources:
            return (
                "FAIL",
                "",
                f"Insufficient sources: {total_sources} found, {min_sources} required for {depth_profile}.",
            )
        if unresolved_critical > 0:
            return ("FAIL", "", f"Unresolved critical contradictions: {unresolved_critical}.")
        if freshness_fail:
            return ("FAIL", "", "Freshness gate triggered.")

        # PASS
        if coverage_score >= coverage_floor and authoritative and unsupported == 0:
            return ("PASS", "", "")

        # WEAK_WITH_CAVEATS
        if coverage_score >= gate_weak_floor:
            caveats = []
            if coverage_score < coverage_floor:
                caveats.append(f"coverage {coverage_score:.0%} below floor {coverage_floor:.0%}")
            if not authoritative:
                caveats.append("no authoritative anchor")
            if unsupported > 0:
                caveats.append(f"{unsupported} unsupported claims")
            return ("WEAK_WITH_CAVEATS", "; ".join(caveats), "")

        return ("FAIL", "", f"Coverage {coverage_score:.0%} below weak floor {gate_weak_floor:.0%}.")

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
