"""CompanyBriefEngine — apps_research --mode company.

Produces a CompanyBrief conforming to apps_rg/schemas/company_research.schema.json.
Driven by SearXNG research (when available) plus a synthesizing LLM call.
Fails closed when grounding or synthesis dependencies cannot produce a real brief.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P1.2).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Final, List, Optional

from apps_research.engines.base_research_engine import BaseResearchEngine
from apps_research.integrations.llm_client import create_openai_sync_client

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
    describe_jd_retrieval_contract,
    decompose_coverage_families,
)
from apps_research.types.jd_intent_coverage import (
    infer_evidence_intents,
    required_families_for_intents,
)

# Plan §P1.4 — V2 retrieval pipeline behind feature flag.
_RETRIEVAL_V2_FLAG = "APPS_RESEARCH_RETRIEVAL_V2"
_COMPANY_BRIEF_PROVIDER_PROFILE: Final[Path] = (
    Path(__file__).resolve().parents[1]
    / "config"
    / "domain_contract"
    / "provider_profile.company_brief.v1.yaml"
)


class CompanyBriefProviderProfileError(RuntimeError):
    """Raised when apps_research company-brief provider profile is invalid."""


def _company_brief_primary_openai_model() -> str:
    """Resolve the runtime synthesis model from the provider-profile SSOT."""
    try:
        import yaml  # noqa: PLC0415

        data = yaml.safe_load(_COMPANY_BRIEF_PROVIDER_PROFILE.read_text(encoding="utf-8"))
    except ImportError as exc:
        raise CompanyBriefProviderProfileError(
            f"Cannot load apps_research provider profile SSOT: {_COMPANY_BRIEF_PROVIDER_PROFILE}"
        ) from exc
    except (AttributeError, OSError, TypeError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        raise CompanyBriefProviderProfileError(
            f"Cannot load apps_research provider profile SSOT: {_COMPANY_BRIEF_PROVIDER_PROFILE}"
        ) from exc
    lanes = (data or {}).get("approved_model_lanes") if isinstance(data, dict) else None
    primary = lanes.get("primary") if isinstance(lanes, dict) else None
    if not isinstance(primary, dict):
        raise CompanyBriefProviderProfileError(
            f"Missing approved_model_lanes.primary in {_COMPANY_BRIEF_PROVIDER_PROFILE}"
        )
    provider = str(primary.get("provider") or "").strip()
    model = str(primary.get("model") or "").strip()
    if provider != "external_openai":
        raise CompanyBriefProviderProfileError(
            "CompanyBriefEngine currently supports only approved_model_lanes.primary.provider="
            f"external_openai; got {provider!r} in {_COMPANY_BRIEF_PROVIDER_PROFILE}"
        )
    if not model:
        raise CompanyBriefProviderProfileError(
            f"Missing approved_model_lanes.primary.model in {_COMPANY_BRIEF_PROVIDER_PROFILE}"
        )
    return model


APPS_RESEARCH_BRIEF_MODEL: Final[str] = _company_brief_primary_openai_model()


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

    Treated as a synthesis-availability observation for company-brief
    synthesis. The calibration harness uses it to track parse-success
    rate and fallback ratio. Never raises.
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


class CompanyBriefUnavailableError(RuntimeError):
    """Raised when company brief synthesis cannot produce a real brief."""


def _resolved_gemini_max_output_tokens() -> int:
    """Canonical apps_research output-token budget for synthesis calls."""
    raw = os.environ.get("APPS_RESEARCH_MAX_OUTPUT_TOKENS", "").strip()
    if raw:
        try:
            return max(512, int(raw))
        except ValueError:
            pass
    return 4096


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

    # --- Search query templates (one per facet, decomposed; W1 Author-Gate B) -----
    _FACET_QUERIES = [
        ("overview", '{company} company overview tagline founding "core offerings"'),
        ("strategic_priorities", '{company} strategic priorities 2025 2026 announcements roadmap'),
        ("customer_profile", '{company} customers verticals industries case studies'),
        ("tech_stack_signals", '{company} technology stack platforms partners "we use"'),
        ("commercial_motion", '{company} commercial motion revenue sales partner-led product-led services-led'),
        ("partner_ecosystem", '{company} partners alliances co-sell ecosystem channel ISV GSI'),
        ("adoption_motion", '{company} adoption deployment implementation pilot production enablement'),
        ("leadership", '{company} leadership team CEO CTO executives'),
        ("competitive_set", '{company} competitors alternatives "vs"'),
        ("recent_moves", '{company} news 2025 acquisition partnership launch'),
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
            research_findings = self._run_research_v2(
                topic=topic,
                depth_profile=depth_profile,
                jd_context=jd_context,
            )
        else:
            research_findings = self._run_research_adaptive(
                topic=topic, depth_profile=depth_profile, jd_context=jd_context
            )
        retrieval_contract = describe_jd_retrieval_contract(jd_context or None)
        _sub_stages.append({
            "sub_stage_id": "research.fetch",
            "sub_stage_name": "Evidence Retrieval",
            "status": "PASS",
            "duration_ms": round((time.perf_counter() - _t_research) * 1000, 3),
            "meta": {
                "v2": _v2_enabled(),
                "query_families": list(research_findings.keys()),
                "jd_intents": retrieval_contract.get("intent_ids", []),
            },
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
            retrieval_contract=retrieval_contract,
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
        # apps_rg targeting brief: fail closed on a failing C0 support gate.
        # A brief produced before the gate result is only promoted to
        # company_brief_text when the gate did not fail; otherwise we surface
        # a sealed BLOCKED disposition and emit NO company_brief_text.
        targeting_disposition = str(synthesized.get("targeting_brief_disposition") or "").strip()
        if targeting_disposition:
            targeting_md = str(synthesized.get("apps_rg_targeting_brief_markdown") or "").strip()
            targeting_sidecar = synthesized.get("apps_rg_targeting_brief_sidecar") or {}
            gate_blocks = str(gate_verdict).upper() in {"FAIL", "EMPTY", "CONFLICTED"}
            if targeting_md and not gate_blocks and targeting_disposition == "SEALED":
                brief["apps_rg_targeting_brief_text"] = targeting_md
                brief["company_brief_text"] = targeting_md
                brief["targeting_brief_disposition"] = "SEALED"
            else:
                brief["targeting_brief_disposition"] = (
                    "BLOCKED" if gate_blocks else targeting_disposition
                )
                brief["targeting_brief_block_reason"] = (
                    f"c0_support_gate={gate_verdict}"
                    if gate_blocks
                    else str(synthesized.get("targeting_brief_block_reason") or "")
                )
                if synthesized.get("targeting_brief_violations"):
                    brief["targeting_brief_violations"] = list(
                        synthesized["targeting_brief_violations"]
                    )
            if targeting_sidecar:
                brief["apps_rg_targeting_brief_sidecar"] = dict(targeting_sidecar)
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

    def _run_research_v2(
        self,
        *,
        topic: str,
        depth_profile: str | None = None,
        jd_context: Dict[str, Any] | None = None,
        depth: str | None = None,
    ) -> Dict[str, str]:
        """V2 retrieval pipeline: plan coverage families -> retrieve -> rerank.

        Plan §P1.4 + §P2.4 (parallel dispatch). Uses a thread pool for
        per-sub-query retrieval (I/O-bound HTTP calls to SearXNG) so
        wall-clock scales sub-linearly with fan-out. Missing retrieval
        dependencies fail closed.
        """
        import concurrent.futures

        from apps_research.engines.query_decomposer import QueryPlan, decompose_coverage_families
        from apps_research.integrations.reranker_adapter import rerank
        from apps_research.integrations.search_retrieval import (
            apply_contextual_prefix,
            retrieve,
        )

        resolved_depth_profile = depth_profile or _resolve_depth_profile(depth or "standard")
        try:
            plans = decompose_coverage_families(topic, resolved_depth_profile, jd_context or None)
        except ValueError as exc:
            raise CompanyBriefUnavailableError(
                f"{topic}: v2 research decomposition failed: {exc}"
            ) from exc
        profile_cfg = _DEPTH_PROFILES.get(
            resolved_depth_profile, _DEPTH_PROFILES["COMPANY_BRIEF_STANDARD"]
        )
        max_queries = int(profile_cfg["max_queries"])
        if jd_context:
            required_targeting_families = [
                "company_basics",
                "competitive_landscape",
                "leadership_and_org",
                "recent_news_and_signals",
                *required_families_for_intents(infer_evidence_intents(jd_context)),
            ]
            planned_families = {plan.family for plan in plans}
            required_planned_count = len(
                {
                    family
                    for family in required_targeting_families
                    if family in planned_families
                }
            )
            max_queries = max(max_queries, required_planned_count)
        plans = plans[:max_queries]

        def _fetch(plan: QueryPlan) -> tuple[str, str]:
            try:
                docs = retrieve(plan.query, top_k=10)
            except (RuntimeError, ValueError) as exc:
                self.logger.info(
                    "[CompanyBriefEngine v2] retrieve skipped for family=%s: %s",
                    plan.family,
                    exc,
                )
                return plan.family, ""
            top = rerank(plan.query, docs, cutoff=5)
            # Plan §P4.5 — wrap each chunk with Anthropic contextual prefix
            # so the downstream synthesizer sees the same template audit
            # grep uses (<document>/<chunk_context>).
            chunks: list[str] = []
            for d in top:
                if not d.snippet:
                    continue
                chunk = f"- {d.title}: {d.snippet} ({d.url})"
                if d.url:
                    chunk = f"{chunk}\n{d.url}"
                chunks.append(
                    apply_contextual_prefix(
                        chunk,
                        doc_title=d.title,
                        surrounding_text=plan.query,
                    )
                )
            blob = "\n\n".join(chunks)
            return plan.family, blob

        findings: Dict[str, str] = {plan.family: "" for plan in plans}
        max_workers = max(1, min(5, len(plans)))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            for family, blob in pool.map(_fetch, plans):
                findings[family] = blob
        if not any((blob or "").strip() for blob in findings.values()):
            raise CompanyBriefUnavailableError(
                f"{topic}: v2 research returned no grounded findings"
            )
        return findings

    def _run_research(self, *, topic: str, depth: str) -> Dict[str, str]:
        """Best-effort SearXNG research per facet.

        Returns a dict {facet_name: text_blob}. Missing SearXNG configuration
        fails closed instead of substituting a synthetic brief.
        """
        findings: Dict[str, str] = {f: "" for f, _ in self._FACET_QUERIES}
        try:
            from apps_research.integrations.search_retrieval import retrieve
        except ImportError as exc:
            self.logger.warning(
                "[CompanyBriefEngine] search_retrieval unavailable; failing closed: %s",
                exc,
            )
            retrieve = None

        max_queries = {"shallow": 3, "standard": 6, "deep": 10}.get(depth, 6)

        for facet, q_template in self._FACET_QUERIES[:max_queries]:
            if retrieve is None:
                break
            query = q_template.format(company=topic)
            try:
                docs = retrieve(query, top_k=5)
                snippets = [d.snippet for d in docs if d.snippet]
                findings[facet] = "\n".join(snippets)[:4000]
            except Exception as exc:  # guardian: allow-broad-exception -- SearXNG HTTP errors are heterogeneous; per-facet fail-soft preserves partial brief
                self.logger.warning("[CompanyBriefEngine] SearXNG query failed (%s): %s", facet, exc)
        if not any((blob or "").strip() for blob in findings.values()):
            raise CompanyBriefUnavailableError(
                f"{topic}: SearXNG research returned no grounded findings"
            )
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

        The company brief path uses the pinned OpenAI model route for
        synthesis. When ``apps_rg_targeting_brief_enabled`` (env or
        jd_context), emits apps_rg targeting markdown per
        ``apps_rg_targeting_brief_v1.md``.
        """
        from apps_research.prompt_assembly.consumer_briefs import (  # noqa: PLC0415
            consumer_brief_template_id,
        )
        from apps_research.prompt_assembly.apps_rg_targeting_brief import (  # noqa: PLC0415
            apps_rg_targeting_brief_enabled,
        )

        consumer_template_id = consumer_brief_template_id(jd_context=jd_context)
        base_prompt = self._build_synthesis_prompt(topic=topic, findings=findings, jd_facets=jd_facets)
        base_synthesis = self._gemini_synthesize(prompt=base_prompt, topic=topic, jd_facets=jd_facets)
        if apps_rg_targeting_brief_enabled(jd_context=jd_context):
            targeting = self._synthesize_apps_rg_targeting_brief(
                topic=topic,
                findings=findings,
                jd_context=jd_context or {},
                jd_anchor=jd_anchor,
            )
            return {**base_synthesis, **targeting}
        if consumer_template_id in {
            "downstream_research_substrate_v1",
            "apps_lic_research_substrate_v1",
            "apps_exec_executive_brief_v1",
        }:
            consumer_keys = {
                "downstream_research_substrate_v1": (
                    "downstream_research_substrate_text",
                    "downstream_research_substrate_disposition",
                    "downstream_research_substrate_block_reason",
                ),
                "apps_lic_research_substrate_v1": (
                    "apps_lic_research_substrate_text",
                    "apps_lic_research_substrate_disposition",
                    "apps_lic_research_substrate_block_reason",
                ),
                "apps_exec_executive_brief_v1": (
                    "apps_exec_executive_brief_text",
                    "apps_exec_executive_brief_disposition",
                    "apps_exec_executive_brief_block_reason",
                ),
            }
            consumer_output_key, consumer_disposition_key, consumer_block_reason_key = (
                consumer_keys[consumer_template_id]
            )
            consumer = self._synthesize_consumer_brief(
                topic=topic,
                findings=findings,
                jd_context=jd_context or {},
                jd_anchor=jd_anchor,
                template_id=consumer_template_id,
                output_key=consumer_output_key,
                disposition_key=consumer_disposition_key,
                block_reason_key=consumer_block_reason_key,
            )
            return {**base_synthesis, **consumer}

        return base_synthesis

    def _gemini_synthesize(
        self,
        *,
        prompt: str,
        topic: str,
        jd_facets: List[str],
    ) -> Dict[str, Any]:
        """Synthesize via the pinned OpenAI model route.

        Uses the pinned apps_research briefing model. Returns the parsed
        synthesis dict on success and fails closed on transport, empty-response,
        or parse failure.
        """
        try:
            client = create_openai_sync_client()
        except Exception as exc:  # guardian: allow-broad-exception -- OpenAI client setup can fail for missing credentials or SDK issues
            raise CompanyBriefUnavailableError(
                f"{topic}: OpenAI client unavailable: {exc}"
            ) from exc

        model_name = APPS_RESEARCH_BRIEF_MODEL
        started = time.time()
        try:
            resp = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a research analyst producing structured company briefs. "
                            "Always answer with strict JSON matching the schema in the user prompt."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_completion_tokens=_resolved_gemini_max_output_tokens(),
            )
        except Exception as exc:  # guardian: allow-broad-exception -- OpenAI SDK raises heterogeneous transport/API errors; fail closed
            self.logger.info("[CompanyBriefEngine] openai model=%s failed: %s", model_name, exc)
            _emit_company_brief_marker(
                accepted=False,
                model_used=model_name,
                fallback_reason="openai_exception",
                latency_ms=(time.time() - started) * 1000.0,
            )
            raise CompanyBriefUnavailableError(
                f"{topic}: OpenAI synthesis failed for model={model_name}: {type(exc).__name__}: {exc}"
            ) from exc

        text = ""
        if getattr(resp, "choices", None):
            try:
                text = str(resp.choices[0].message.content or "").strip()
            except (AttributeError, IndexError, TypeError, ValueError):
                text = ""
        if not text:
            _emit_company_brief_marker(
                accepted=False,
                model_used=model_name,
                fallback_reason="openai_empty_response",
                latency_ms=(time.time() - started) * 1000.0,
            )
            raise CompanyBriefUnavailableError(
                f"{topic}: OpenAI synthesis returned empty response for model={model_name}"
            )

        parsed = self._parse_synthesis(text, topic=topic, jd_facets=jd_facets)
        _emit_company_brief_marker(
            accepted=True,
            model_used=model_name,
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
        gate_verdict: str = "",
        gate_reason: str = "",
    ) -> Dict[str, Any]:
        """Synthesize the apps_rg briefing packet as a sealed markdown artifact.

        The company is identified strictly from ``company_name`` (falls back to
        ``topic`` only when absent) so the JD/role never pollutes company
        identification. The JD is passed as relevance context only.

        """
        from apps_research.prompt_assembly.apps_rg_targeting_brief import (  # noqa: PLC0415
            build_targeting_brief_prompt,
            extract_jd_text,
            format_research_findings,
        )
        from apps_research.types.apps_rg_targeting_brief_contract import (  # noqa: PLC0415
            BriefStatus,
            assess_targeting_brief_semantics,
            normalize_targeting_brief_text,
            seal_targeting_brief,
        )
        from apps_research.integrations.apps_rg_handoff import (  # noqa: PLC0415
            x2_judge_receipt_passes,
        )

        company_name = str(jd_context.get("company_name") or "").strip() or topic
        jd_text = extract_jd_text(jd_context=jd_context, jd_anchor=jd_anchor)
        research_notes = format_research_findings(findings)
        model_name = APPS_RESEARCH_BRIEF_MODEL

        has_research = bool(research_notes.strip())
        gate_failed = str(gate_verdict).upper() in {"FAIL", "EMPTY", "CONFLICTED"}
        if not has_research or gate_failed:
            raise CompanyBriefUnavailableError(
                f"{company_name}: apps_rg targeting brief blocked: "
                f"{gate_reason or ('c0_support_gate_failed' if gate_failed else 'no_grounded_research_for_company')}"
            )

        prompt = build_targeting_brief_prompt(
            jd_text=jd_text,
            research_notes=research_notes,
            target_entity=company_name,
        )
        markdown = self._call_llm_plain_markdown(prompt).strip()

        if not markdown or markdown.upper().startswith("BLOCKED:"):
            raise CompanyBriefUnavailableError(
                f"{company_name}: apps_rg targeting brief synthesis returned "
                f"{markdown[:120] if markdown else 'synthesis_returned_empty'}"
            )

        normalized = normalize_targeting_brief_text(
            markdown,
            jd_text=jd_text,
            profile="apps_rg",
        )
        normalized = self._drop_unsupported_named_leadership_claims(
            normalized,
            research_notes=research_notes,
        )
        sealed = seal_targeting_brief(
            normalized,
            company_name=company_name,
            jd_text=jd_text,
            profile="apps_rg",
        )
        if not sealed.is_sealed:
            scrubbed = self._drop_jd_restatement_bullets(normalized, sealed.violations)
            if scrubbed != normalized:
                sealed = seal_targeting_brief(
                    scrubbed,
                    company_name=company_name,
                    jd_text=jd_text,
                    profile="apps_rg",
                )
        if not sealed.is_sealed:
            repaired = self._repair_apps_rg_targeting_brief_markdown(
                company_name=company_name,
                draft_markdown=normalized,
                jd_text=jd_text,
                research_notes=research_notes,
                gate_verdict=gate_verdict,
                gate_reason=gate_reason,
                violations=sealed.violations,
            )
            if repaired.strip() and repaired.strip() != normalized:
                repaired_normalized = normalize_targeting_brief_text(
                    repaired,
                    jd_text=jd_text,
                    profile="apps_rg",
                )
                repaired_normalized = self._drop_unsupported_named_leadership_claims(
                    repaired_normalized,
                    research_notes=research_notes,
                )
                sealed = seal_targeting_brief(
                    repaired_normalized,
                    company_name=company_name,
                    jd_text=jd_text,
                    profile="apps_rg",
                )
                if not sealed.is_sealed:
                    scrubbed = self._drop_jd_restatement_bullets(
                        repaired_normalized,
                        sealed.violations,
                    )
                    if scrubbed != repaired_normalized:
                        sealed = seal_targeting_brief(
                            scrubbed,
                            company_name=company_name,
                            jd_text=jd_text,
                            profile="apps_rg",
                        )
        if not sealed.is_sealed:
            violations = ",".join(sealed.violations) if sealed.violations else "none"
            raise CompanyBriefUnavailableError(
                f"{company_name}: apps_rg targeting brief rejected: "
                f"{sealed.block_reason or 'contract_validation_failed'}; violations={violations}"
            )
        semantic_assessment = assess_targeting_brief_semantics(
            sealed.company_brief_text,
            jd_text=jd_text,
            research_notes=research_notes,
            source_family_keys=tuple(findings.keys()),
            profile="apps_rg",
        )
        source_register = [
            {
                "family": family,
                "has_content": bool((blob or "").strip()),
                "char_count": len((blob or "").strip()),
            }
            for family, blob in sorted(findings.items(), key=lambda item: item[0])
        ]
        x2_judge_receipt = self._run_apps_rg_handoff_x2_judge(
            brief_text=sealed.company_brief_text,
            jd_text=jd_text,
            research_notes=research_notes,
            source_register=source_register,
        )
        if not x2_judge_receipt_passes(x2_judge_receipt):
            diagnostic_ref = self._persist_x2_blocked_receipt(
                company_name=company_name,
                brief_text=sealed.company_brief_text,
                jd_text=jd_text,
                x2_judge_receipt=x2_judge_receipt,
                source_register=source_register,
            )
            diagnostic_suffix = f"; diagnostic_ref={diagnostic_ref}" if diagnostic_ref else ""
            raise CompanyBriefUnavailableError(
                f"{company_name}: apps_rg targeting brief X2 judge failed: "
                f"{x2_judge_receipt.get('status', 'MISSING_RECEIPT')}; "
                f"reason={x2_judge_receipt.get('reason', 'missing_model_backed_pass')}"
                f"{diagnostic_suffix}"
            )
        return {
            "synthesis_template": "apps_rg_targeting_brief_synthesis_v1",
            "apps_rg_targeting_brief_markdown": sealed.company_brief_text,
            "apps_rg_targeting_brief_sidecar": self._build_targeting_brief_sidecar(
                company_name=company_name,
                brief_text=sealed.company_brief_text,
                jd_text=jd_text,
                research_notes=research_notes,
                findings=findings,
                gate_verdict=gate_verdict,
                gate_reason=gate_reason,
                model_name=model_name,
                semantic_override=semantic_assessment,
                x2_judge_receipt=x2_judge_receipt,
                source_register=source_register,
            ),
            "targeting_brief_disposition": BriefStatus.SEALED.value,
            "targeting_brief_char_count": sealed.char_count,
            "targeting_brief_bullet_count": sealed.bullet_count,
            "targeting_brief_section_count": sealed.section_count,
        }

    def _synthesize_consumer_brief(
        self,
        *,
        topic: str,
        findings: Dict[str, str],
        jd_context: Dict[str, Any],
        jd_anchor: Optional[Path],
        template_id: str,
        output_key: str,
        disposition_key: str,
        block_reason_key: str,
        gate_verdict: str = "",
        gate_reason: str = "",
    ) -> Dict[str, Any]:
        """Synthesize a compact downstream consumer brief."""
        from apps_research.prompt_assembly.consumer_briefs import (  # noqa: PLC0415
            build_consumer_brief_prompt,
            extract_jd_text,
            format_research_findings,
        )
        from apps_research.types.apps_rg_targeting_brief_contract import (  # noqa: PLC0415
            normalize_markdown_brief_text,
        )

        company_name = str(jd_context.get("company_name") or "").strip() or topic
        jd_text = extract_jd_text(jd_context=jd_context, jd_anchor=jd_anchor)
        research_notes = format_research_findings(findings)
        has_research = bool(research_notes.strip())
        gate_failed = str(gate_verdict).upper() in {"FAIL", "EMPTY", "CONFLICTED"}
        if not has_research or gate_failed:
            raise CompanyBriefUnavailableError(
                f"{company_name}: consumer brief blocked: "
                f"{gate_reason or ('c0_support_gate_failed' if gate_failed else 'no_grounded_research_for_company')}"
            )

        prompt = build_consumer_brief_prompt(
            template_id=template_id,
            jd_text=jd_text,
            research_notes=research_notes,
            target_entity=company_name,
        )
        text = self._call_llm_plain_markdown(prompt).strip()
        if not text or text.upper().startswith("BLOCKED:"):
            raise CompanyBriefUnavailableError(
                f"{company_name}: consumer brief synthesis returned "
                f"{text[:120] if text else 'synthesis_returned_empty'}"
            )

        brief_profile = "apps_lic" if template_id == "apps_lic_research_substrate_v1" else "apps_rg"
        text = normalize_markdown_brief_text(text, profile=brief_profile)
        return {
            "synthesis_template": template_id,
            "consumer_brief_template_id": template_id,
            "consumer_brief_output_key": output_key,
            output_key: text,
            "company_brief_text": text,
            disposition_key: "SEALED",
        }

    def _repair_apps_rg_targeting_brief_markdown(
        self,
        *,
        company_name: str,
        draft_markdown: str,
        jd_text: str,
        research_notes: str,
        gate_verdict: str,
        gate_reason: str,
        violations: tuple[str, ...],
    ) -> str:
        """Bounded second-pass repair for contract-invalid targeting drafts."""

        violation_text = ", ".join(violations[:8]) if violations else "contract_validation_failed"
        prompt = (
            "Repair this apps_rg targeting brief so it seals cleanly.\n"
            f"Company: {company_name}\n"
            f"Gate verdict: {gate_verdict or 'unknown'}\n"
            f"Gate reason: {gate_reason or 'none'}\n"
            f"Violations: {violation_text}\n\n"
            "Rules: preserve the same company and section structure; keep the metadata line; "
            "do not restate JD responsibilities or copy any 4-word JD phrase; keep bullets one "
            "level deep; wrap every line to 240 characters or less; remove citations, links, "
            "placeholders, and code fences; do not name specific executives unless the exact "
            "person name appears in the research notes; output markdown only.\n\n"
            f"JD (context only):\n{jd_text}\n\n"
            f"Research notes:\n{research_notes}\n\n"
            f"Draft to repair:\n{draft_markdown}\n"
        )
        repaired = self._call_llm_plain_markdown(prompt).strip()
        if repaired.upper().startswith("BLOCKED:"):
            return ""
        return repaired

    @staticmethod
    def _drop_jd_restatement_bullets(markdown: str, violations: tuple[str, ...]) -> str:
        """Remove bullet lines explicitly identified as JD restatements."""

        snippets = [
            value.split(":", 1)[1].strip().lower()
            for value in violations
            if value.startswith("jd_restatement_in_bullet_text:") and ":" in value
        ]
        if not snippets:
            return markdown

        kept_lines: list[str] = []
        for raw_line in str(markdown or "").splitlines():
            stripped = raw_line.strip()
            if stripped.startswith("- "):
                bullet = stripped[2:].strip().lower()
                if any(snippet and snippet in bullet for snippet in snippets):
                    continue
            kept_lines.append(raw_line)
        return "\n".join(kept_lines).strip()

    _UNSUPPORTED_LEADERSHIP_ROLE_RE = re.compile(
        r"\b(?:ceo|cto|cfo|coo|founder|co-founder|cofounder|president|"
        r"chief|executive|leadership|leader|strategic voice|stakeholder)\b",
        re.IGNORECASE,
    )
    _MARKDOWN_HEADER_RE = re.compile(r"^\s{0,3}#{1,6}\s+")
    _PERSON_NAME_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b")
    _NON_PERSON_NAME_PHRASES = {
        "Amazon Web Services",
        "Claude Partner Network",
        "Google Cloud",
        "Microsoft Azure",
    }

    @classmethod
    def _unsupported_person_names(cls, text: str, *, research_notes: str) -> list[str]:
        notes = str(research_notes or "").lower()
        out: list[str] = []
        for match in cls._PERSON_NAME_RE.finditer(str(text or "")):
            name = match.group(1).strip()
            if name in cls._NON_PERSON_NAME_PHRASES:
                continue
            if name.lower() in notes:
                continue
            if name not in out:
                out.append(name)
        return out

    @classmethod
    def _drop_unsupported_named_leadership_claims(
        cls,
        markdown: str,
        *,
        research_notes: str,
    ) -> str:
        """Remove named leadership claims when the retrieved notes do not contain the name."""

        kept_lines: list[str] = []
        for raw_line in str(markdown or "").splitlines():
            line = raw_line.rstrip()
            if cls._MARKDOWN_HEADER_RE.match(line):
                kept_lines.append(raw_line)
                continue
            if not cls._UNSUPPORTED_LEADERSHIP_ROLE_RE.search(line):
                kept_lines.append(raw_line)
                continue

            sentences = re.split(r"(?<=[.!?])\s+", line)
            kept_sentences: list[str] = []
            for sentence in sentences:
                unsupported = cls._unsupported_person_names(
                    sentence,
                    research_notes=research_notes,
                )
                if unsupported and cls._UNSUPPORTED_LEADERSHIP_ROLE_RE.search(sentence):
                    continue
                kept_sentences.append(sentence)

            rebuilt = " ".join(s.strip() for s in kept_sentences if s.strip()).strip()
            if rebuilt:
                kept_lines.append(rebuilt)
        return "\n".join(kept_lines).strip()

    def _build_targeting_brief_sidecar(
        self,
        *,
        company_name: str,
        brief_text: str,
        jd_text: str,
        research_notes: str,
        findings: Dict[str, str],
        gate_verdict: str,
        gate_reason: str,
        model_name: str,
        semantic_override: Any | None = None,
        x2_judge_receipt: dict[str, Any] | None = None,
        source_register: list[dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        """Build the structured sidecar carried from apps_research to apps_rg."""
        from apps_research.types.apps_rg_targeting_brief_contract import (  # noqa: PLC0415
            assess_targeting_brief_semantics,
            validate_targeting_brief_text,
        )
        from apps_research.integrations.apps_rg_handoff import (  # noqa: PLC0415
            APPS_RG_HANDOFF_GENERATION_PROVIDER,
            x2_judge_receipt_passes,
        )
        from apps_research.integrations.search_retrieval import retrieval_config_snapshot  # noqa: PLC0415

        semantics = semantic_override or assess_targeting_brief_semantics(
            brief_text,
            jd_text=jd_text,
            research_notes=research_notes,
            source_family_keys=tuple(findings.keys()),
            profile="apps_rg",
        )
        validation = validate_targeting_brief_text(
            brief_text,
            jd_text=jd_text,
            profile="apps_rg",
        )
        resolved_source_register = source_register or [
            {
                "family": family,
                "has_content": bool((blob or "").strip()),
                "char_count": len((blob or "").strip()),
            }
            for family, blob in sorted(findings.items(), key=lambda item: item[0])
        ]
        judge_receipt = dict(x2_judge_receipt or {})
        model_backed_x2_passed = x2_judge_receipt_passes(judge_receipt)
        digest = hashlib.sha256(brief_text.encode("utf-8")).hexdigest() if brief_text else ""
        retrieval_snapshot = retrieval_config_snapshot(query_families=list(findings.keys()))
        semantic_score = judge_receipt.get("score", semantics.score)
        judge_name = judge_receipt.get("judge_name", semantics.judge_name)
        judge_model = judge_receipt.get("judge_model", semantics.judge_model)
        handoff_eligible = bool(semantics.handoff_eligible and model_backed_x2_passed)
        blocked_reason = "ok"
        if not handoff_eligible:
            blocked_reason = (
                "x2_model_backed_judge_not_pass"
                if not model_backed_x2_passed
                else str(getattr(semantics, "reason", "") or "semantic_handoff_not_eligible")
            )
        return {
            "schema_version": "apps_research.apps_rg_targeting_brief_sidecar/v1",
            "company_name": company_name,
            "generation_provider": APPS_RG_HANDOFF_GENERATION_PROVIDER,
            "generation_model": model_name,
            "provider_call_attempted": True,
            "generation_token_budget": _resolved_gemini_max_output_tokens(),
            "judge_name": judge_name,
            "judge_model": judge_model,
            "briefing_semantic_score": semantic_score,
            "semantic_gate_mode": "model_backed_llm_judge",
            "handoff_eligible": handoff_eligible,
            "reason": blocked_reason,
            "x2_judge_receipt": judge_receipt,
            "deterministic_semantic_assessment": semantics.as_dict(),
            "role_archetype": semantics.role_archetype,
            "evidence_intents": list(semantics.evidence_intents),
            "required_sections_present": list(semantics.required_sections_present),
            "missing_sections": list(semantics.missing_sections),
            "source_families_present": list(semantics.source_families_present),
            "source_families_missing": list(semantics.source_families_missing),
            "signal_terms_present": list(semantics.signal_terms_present),
            "signal_terms_missing": list(semantics.signal_terms_missing),
            "retrieval_config": retrieval_snapshot,
            "source_register": resolved_source_register,
            "gate_verdict": gate_verdict,
            "gate_reason": gate_reason,
            "text_char_count": validation.char_count,
            "bullet_count": validation.bullet_count,
            "section_count": validation.section_count,
            "brief_text_sha256": digest,
        }

    def _run_apps_rg_handoff_x2_judge(
        self,
        *,
        brief_text: str,
        jd_text: str,
        research_notes: str,
        source_register: list[dict[str, Any]],
    ) -> dict[str, Any]:
        from apps_research.integrations.apps_rg_handoff import (  # noqa: PLC0415
            run_apps_rg_handoff_x2_judge,
        )

        return run_apps_rg_handoff_x2_judge(
            brief_text=brief_text,
            jd_text=jd_text,
            research_notes=research_notes,
            source_register=source_register,
        )

    def _persist_x2_blocked_receipt(
        self,
        *,
        company_name: str,
        brief_text: str,
        jd_text: str,
        x2_judge_receipt: dict[str, Any],
        source_register: list[dict[str, Any]],
    ) -> str:
        """Write fail-closed X2 diagnostics without authorizing handoff."""
        try:
            repo_root = Path(__file__).resolve().parents[2]
            out_dir = repo_root / "artifacts" / "apps_research" / "x2_judge_failures"
            out_dir.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256(
                f"{company_name}\n{brief_text}".encode("utf-8")
            ).hexdigest()[:12]
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            path = out_dir / f"{timestamp}_{digest}.json"
            payload = {
                "schema_version": "apps_research.x2_blocked_receipt.v1",
                "company_name": company_name,
                "emitted_at_utc": datetime.now(timezone.utc).isoformat(),
                "brief_text_sha256": hashlib.sha256(
                    str(brief_text or "").encode("utf-8")
                ).hexdigest(),
                "jd_text_sha256": hashlib.sha256(
                    str(jd_text or "").encode("utf-8")
                ).hexdigest(),
                "handoff_authorized": False,
                "x2_judge_receipt": dict(x2_judge_receipt or {}),
                "source_register": list(source_register or []),
            }
            path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            return str(path)
        except (OSError, TypeError, ValueError) as exc:
            self.logger.warning(
                "[CompanyBriefEngine] failed to persist X2 blocked receipt: %s",
                exc,
            )
            return ""

    def _call_llm_plain_markdown(self, prompt: str) -> str:
        """OpenAI route for plain-text targeting brief output."""
        text = self._gemini_synthesize_plain(prompt=prompt)
        return text

    def _gemini_synthesize_plain(self, *, prompt: str) -> str:
        try:
            client = create_openai_sync_client()
        except Exception as exc:  # guardian: allow-broad-exception -- OpenAI client setup can fail for missing credentials or SDK issues
            raise CompanyBriefUnavailableError(
                f"targeting brief OpenAI client unavailable: {exc}"
            ) from exc

        model_name = APPS_RESEARCH_BRIEF_MODEL
        try:
            resp = client.chat.completions.create(
                model=model_name,
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
                max_completion_tokens=_resolved_gemini_max_output_tokens(),
            )
        except Exception as exc:  # guardian: allow-broad-exception -- OpenAI SDK raises heterogeneous transport/API errors; fail closed
            self.logger.info(
                "[CompanyBriefEngine] targeting brief openai model=%s failed: %s",
                model_name,
                exc,
            )
            raise CompanyBriefUnavailableError(
                f"targeting brief OpenAI synthesis failed for model={model_name}: {type(exc).__name__}: {exc}"
            ) from exc
        if not getattr(resp, "choices", None):
            raise CompanyBriefUnavailableError(
                f"targeting brief OpenAI synthesis returned no choices for model={model_name}"
            )
        try:
            text = (resp.choices[0].message.content or "").strip()
        except (AttributeError, IndexError, TypeError, ValueError):
            raise CompanyBriefUnavailableError(
                f"targeting brief OpenAI synthesis returned malformed response for model={model_name}"
            )
        if not text:
            raise CompanyBriefUnavailableError(
                f"targeting brief OpenAI synthesis returned empty response for model={model_name}"
            )
        return text

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
            "Return strictly JSON with keys: company_archetype (string), company_dna (object), "
            "tagline, core_offerings (list[str]), strategic_priorities (list[str], min 2), "
            "verticals (list[str]), buyer_titles (list[str]), tech_stack_signals (list[str]), "
            "commercial_motion (list[str]), partner_ecosystem (list[str]), "
            "adoption_motion (list[str]), leadership (list of {name,title,background}), "
            "competitive_set (list[str]), recent_moves (list of {date,event,signal}), "
            "language_to_mirror (list[str], min 3), language_to_avoid (list[str]).\n"
            "company_dna should summarize the operating identity of the company in a few short "
            "fields: archetype, commercial_motion, partner_ecosystem, adoption_motion, "
            "operating_tension, and distinguishing_traits. Prefer specific language over "
            "generic AI-company prose."
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
        raise CompanyBriefUnavailableError(
            f"{topic}: structured synthesis JSON parse failed"
        )

    @staticmethod
    def _stub_synthesis(*, topic: str, jd_facets: List[str]) -> Dict[str, Any]:
        raise CompanyBriefUnavailableError(
            f"{topic}: stub synthesis disabled"
        )

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
        ``apps_research.integrations.search_retrieval.retrieve`` (the
        canonical SearXNG adapter) for the actual searches. Missing or empty
        retrieval fails closed; no curated company pack may stand in for
        grounded research.
        """
        plans = decompose_coverage_families(topic, depth_profile, jd_context or None)
        findings: Dict[str, str] = {p.family: "" for p in plans}

        try:
            from apps_research.integrations.search_retrieval import retrieve
        except ImportError as exc:
            self.logger.warning(
                "[CompanyBriefEngine] search_retrieval unavailable; failing closed: %s",
                exc,
            )
            retrieve = None

        profile_cfg = _DEPTH_PROFILES.get(depth_profile, _DEPTH_PROFILES["COMPANY_BRIEF_STANDARD"])
        max_queries = profile_cfg["max_queries"]

        for plan in plans[:max_queries]:
            if retrieve is None:
                break
            try:
                docs = retrieve(plan.query, top_k=5)
            except RuntimeError as exc:
                self.logger.warning(
                    "[CompanyBriefEngine] SearXNG unavailable for family=%s: %s",
                    plan.family,
                    exc,
                )
                continue
            except Exception as exc:  # guardian: allow-broad-exception -- per-family SearXNG HTTP errors heterogeneous; fail-soft preserves partial brief
                self.logger.warning(
                    "[CompanyBriefEngine] SearXNG query failed (family=%s): %s",
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
        if not any((blob or "").strip() for blob in findings.values()):
            raise CompanyBriefUnavailableError(
                f"{topic}: adaptive research returned no grounded findings"
            )
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
        retrieval_contract: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Build the 7-object C0 output bundle from research findings + synthesis."""
        from apps_research.integrations.search_retrieval import retrieval_config_snapshot  # noqa: PLC0415

        contract = retrieval_contract or describe_jd_retrieval_contract(jd_context or None)
        required_families = list(dict.fromkeys(
            list(_PROFILE_REQUIRED_FAMILIES.get(depth_profile, []))
            + list(contract.get("required_evidence_families", []))
        ))
        retrieval_snapshot = retrieval_config_snapshot(
            query_families=list(findings.keys())
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
        # non-empty content lines as citation-anchor proxies when the bundle
        # is only partially grounded.
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
            "jd_evidence_intents": list(contract.get("intent_ids", [])),
            "jd_required_evidence_families": list(contract.get("required_evidence_families", [])),
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
            "retrieval_config": retrieval_snapshot,
            "jd_retrieval_contract": contract,
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
            "company_archetype": synthesis.get("company_archetype"),
            "company_dna": synthesis.get("company_dna", {}) or {},
            "strategic_priorities": synthesis.get("strategic_priorities", []) or [],
            "customer_profile": {
                "verticals": synthesis.get("verticals", []) or [],
                "buyer_titles": synthesis.get("buyer_titles", []) or [],
                "typical_engagement_size": synthesis.get("typical_engagement_size"),
            },
            "tech_stack_signals": synthesis.get("tech_stack_signals", []) or [],
            "commercial_motion": synthesis.get("commercial_motion", []) or [],
            "partner_ecosystem": synthesis.get("partner_ecosystem", []) or [],
            "adoption_motion": synthesis.get("adoption_motion", []) or [],
            "leadership": synthesis.get("leadership", []) or [],
            "competitive_set": synthesis.get("competitive_set", []) or [],
            "recent_moves": synthesis.get("recent_moves", []) or [],
            "language_to_mirror": synthesis.get("language_to_mirror", []) or [],
            "language_to_avoid": synthesis.get("language_to_avoid", []) or [],
        }


__all__ = ["APPS_RESEARCH_BRIEF_MODEL", "CompanyBriefEngine"]
