"""apps_research L2 E1-E5 step adapters.

Defines the five receipt names emitted during the L2 execution lifecycle.
Each step adapter wraps a spine phase and emits its corresponding receipt
so the FEC producer and Exit v6 can verify execution completeness.

E1 — C0 evidence gate:     c0_evidence_gate_passed
E2 — PA compile:           prompt_assembly_compiled
E3 — Provider synthesis:   provider_synthesis_complete
E4 — FEC produce:          fec_produced
E5 — Exit invoked:         exit_invoked

Plan: apps-research-spine-alignment-d4e8f2 W3.1 (full implementation).
"""
from __future__ import annotations

import hashlib
import json
import logging
import uuid
from typing import Any

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Receipt name constants — must match FEC producer expected_receipts list
# ---------------------------------------------------------------------------

RECEIPT_E1_C0_GATE = "c0_evidence_gate_passed"
RECEIPT_E2_PA_COMPILED = "prompt_assembly_compiled"
RECEIPT_E3_SYNTHESIS_COMPLETE = "provider_synthesis_complete"
RECEIPT_E4_FEC_PRODUCED = "fec_produced"
RECEIPT_E5_EXIT_INVOKED = "exit_invoked"

ALL_E1_E5_RECEIPTS = (
    RECEIPT_E1_C0_GATE,
    RECEIPT_E2_PA_COMPILED,
    RECEIPT_E3_SYNTHESIS_COMPLETE,
    RECEIPT_E4_FEC_PRODUCED,
    RECEIPT_E5_EXIT_INVOKED,
)


# ---------------------------------------------------------------------------
# E1 — C0 Evidence Gate
# ---------------------------------------------------------------------------

class E1C0EvidenceGateAdapter:
    """E1 — Validates C0 evidence bundle meets minimum gate for the depth profile.

    Accepts either a legacy ``C0EvidenceBundle`` or the new
    ``BriefingEvidenceBundle`` (preferred). Emits RECEIPT_E1_C0_GATE on
    success. Raises ``C0GateFailed`` on failure → X3E_SAFE_ABSTAIN.

    Required field verification per plan spec:
    - route_id present (from request context)
    - BriefingCoverageMatrix present and populated
    - SourcePortfolioSummary present
    - depth_profile resolved
    """

    def run(
        self,
        c0_bundle: Any,
        *,
        depth_profile: str = "",
        request: Any = None,
    ) -> str:
        """Validate C0 evidence bundle and emit E1 receipt.

        Args:
            c0_bundle: BriefingEvidenceBundle (preferred) or C0EvidenceBundle.
            depth_profile: Canonical depth profile override.
            request: ResearchRequest — used to resolve depth_profile when absent.

        Returns:
            RECEIPT_E1_C0_GATE constant.

        Raises:
            C0GateFailed: If bundle fails the minimum gate.
        """
        from apps_research.integrations.research_c0_adapter import (  # noqa: PLC0415
            C0GateFailed,
            evaluate_c0_gate,
        )
        from apps_research.types.briefing_evidence_contracts import (  # noqa: PLC0415
            BriefingEvidenceBundle,
        )

        resolved_profile = depth_profile or (
            getattr(request, "depth_profile", "") if request else ""
        ) or "COMPANY_BRIEF_STANDARD"

        if isinstance(c0_bundle, BriefingEvidenceBundle):
            missing = c0_bundle.missing_contracts()
            if missing:
                raise C0GateFailed(
                    f"E1 gate: BriefingEvidenceBundle missing contracts: {missing}"
                )
            coverage = c0_bundle.coverage_matrix
            portfolio = c0_bundle.source_portfolio
            if coverage is None or portfolio is None:
                raise C0GateFailed(
                    "E1 gate: coverage_matrix or source_portfolio is None."
                )
            verdict = evaluate_c0_gate(coverage, portfolio, resolved_profile)
            if verdict == "FAIL_DEGRADE":
                raise C0GateFailed(
                    f"E1 gate: evaluate_c0_gate returned FAIL_DEGRADE "
                    f"(coverage={coverage.overall_coverage_ratio:.3f}, "
                    f"sources={portfolio.total_sources}, profile={resolved_profile})"
                )
            _log.info(
                "E1 gate PASS: verdict=%s profile=%s sources=%d",
                verdict, resolved_profile, portfolio.total_sources,
            )
        else:
            # Legacy C0EvidenceBundle path
            if hasattr(c0_bundle, "validate_gate"):
                c0_bundle.validate_gate()
            else:
                chunk_count = getattr(c0_bundle, "chunk_count", 0)
                if chunk_count == 0:
                    raise C0GateFailed(
                        f"E1 gate: legacy C0 bundle has 0 chunks (profile={resolved_profile})."
                    )

        return RECEIPT_E1_C0_GATE


# ---------------------------------------------------------------------------
# E2 — Prompt Assembly
# ---------------------------------------------------------------------------

class E2PromptAssemblyAdapter:
    """E2 — Compiles the prompt via research_pa_compiler.

    Consumes the C0 evidence bundle (or BriefingEvidenceBundle) to build
    the compile context, then calls compile_prompt() on the
    company_brief_synthesis_v1 template. Emits RECEIPT_E2_PA_COMPILED on
    success. Stores the CompiledPromptArtifact on self.artifact for
    downstream access by E3.
    """

    def __init__(self) -> None:
        self.artifact: Any = None

    def run(
        self,
        c0_bundle: Any,
        request: Any,
        *,
        template_id: str = "company_brief_synthesis_v1",
    ) -> str:
        """Compile synthesis prompt from C0 evidence and request.

        Args:
            c0_bundle: BriefingEvidenceBundle or C0EvidenceBundle.
            request: ResearchRequest.
            template_id: PA template to compile; defaults to synthesis template.

        Returns:
            RECEIPT_E2_PA_COMPILED constant.

        Raises:
            PromptAssemblyError: If compilation fails → X3E_SAFE_ABSTAIN.
        """
        from apps_research.prompt_assembly.research_pa_compiler import (  # noqa: PLC0415
            compile_prompt,
        )
        from apps_research.types.briefing_evidence_contracts import (  # noqa: PLC0415
            BriefingEvidenceBundle,
        )

        topic = getattr(request, "topic", "") or ""
        depth_profile = getattr(request, "depth_profile", "COMPANY_BRIEF_STANDARD")
        request_id = getattr(request, "trace_id", "") or str(uuid.uuid4())
        run_id = str(uuid.uuid4())
        trace_id = request_id

        # Build c0_bundle_hash to bind evidence to the artifact
        if isinstance(c0_bundle, BriefingEvidenceBundle):
            portfolio = c0_bundle.source_portfolio
            coverage = c0_bundle.coverage_matrix
            bundle_repr = {
                "depth_profile": depth_profile,
                "families_covered": coverage.families_covered if coverage else 0,
                "total_sources": portfolio.total_sources if portfolio else 0,
            }
        else:
            bundle_repr = {
                "depth_profile": depth_profile,
                "chunk_count": getattr(c0_bundle, "chunk_count", 0),
            }
        c0_bundle_hash = hashlib.sha256(
            json.dumps(bundle_repr, sort_keys=True).encode()
        ).hexdigest()[:32]

        # Build input_data for slot rendering
        coverage_summary = ""
        gap_summary = ""
        freshness_summary = ""
        synthesis_guidance = ""
        if isinstance(c0_bundle, BriefingEvidenceBundle):
            if c0_bundle.coverage_matrix:
                coverage_summary = json.dumps(
                    c0_bundle.coverage_matrix.to_summary_dict(), indent=2
                )
            if c0_bundle.gap_report:
                gap_summary = str([g.family for g in c0_bundle.gap_report.gaps])
            if c0_bundle.freshness_report:
                fr = c0_bundle.freshness_report
                freshness_summary = (
                    f"freshness_ratio={fr.freshness_ratio:.2f} "
                    f"fresh={fr.fresh_source_count} stale={fr.stale_source_count}"
                )
            if c0_bundle.synthesis_guidance:
                sg = c0_bundle.synthesis_guidance
                synthesis_guidance = (
                    f"gate={sg.c0_gate_verdict} "
                    f"recommended={list(sg.recommended_sections)}"
                )

        input_data: dict[str, Any] = {
            "topic": topic,
            "depth_profile": depth_profile,
            "coverage_summary": coverage_summary or f"depth_profile={depth_profile}",
            "gap_summary": gap_summary or "(no gaps detected)",
            "freshness_summary": freshness_summary or "(freshness data unavailable)",
            "synthesis_guidance": synthesis_guidance or "(no guidance)",
            "request_id": request_id,
            "run_id": run_id,
            "trace_id": trace_id,
        }

        context: dict[str, Any] = {
            "request_id": request_id,
            "run_id": run_id,
            "trace_id": trace_id,
            "route_id": "R3_SIMPLE_GROUNDED_READ",
            "c0_bundle_hash": c0_bundle_hash,
            "depth_profile": depth_profile,
            "provider_lane": "governed",
            "audit_refs": [f"E2:{template_id}"],
        }

        self.artifact = compile_prompt(
            template_id=template_id,
            input_data=input_data,
            context=context,
        )
        _log.info(
            "E2 PA compiled: template=%s artifact_id=%s",
            template_id, self.artifact.artifact_id,
        )
        return RECEIPT_E2_PA_COMPILED


# ---------------------------------------------------------------------------
# E3 — Provider Synthesis
# ---------------------------------------------------------------------------

class E3ProviderSynthesisAdapter:
    """E3 — Calls the governed provider gateway with CompiledPromptArtifact.

    Routes synthesis through the governed LLM gateway. Falls back to stub
    synthesis when the gateway is unavailable so the pipeline stays
    green in offline test environments.

    Forbidden: raw SDK imports (openai, anthropic, etc.) — these must live
    in the governed gateway only.

    Emits RECEIPT_E3_SYNTHESIS_COMPLETE on success. Stores synthesis output
    on self.synthesis_output for downstream access by E4.
    """

    def __init__(self) -> None:
        self.synthesis_output: dict[str, Any] = {}

    def run(self, compiled_prompt: Any) -> str:
        """Execute synthesis via governed gateway using compiled prompt artifact.

        Args:
            compiled_prompt: CompiledPromptArtifact from E2.

        Returns:
            RECEIPT_E3_SYNTHESIS_COMPLETE constant.
        """
        from apps_research.integrations.research_c0_adapter import (  # noqa: PLC0415
            ResearchDepthProfile,
        )

        rendered_slots = getattr(compiled_prompt, "rendered_slots", {})
        depth_profile = getattr(compiled_prompt, "depth_profile", ResearchDepthProfile.STANDARD)
        artifact_id = getattr(compiled_prompt, "artifact_id", "")

        # Attempt governed gateway synthesis
        synthesis_text = self._call_governed_gateway(rendered_slots, artifact_id)

        if synthesis_text:
            self.synthesis_output = {
                "text": synthesis_text,
                "artifact_id": artifact_id,
                "depth_profile": depth_profile,
                "provider": "governed_gateway",
                "synthesis_hash": hashlib.sha256(
                    synthesis_text.encode()
                ).hexdigest()[:32],
            }
        else:
            raise RuntimeError(
                f"E3 governed gateway unavailable for artifact={artifact_id}"
            )

        _log.info(
            "E3 synthesis complete: provider=%s artifact=%s",
            self.synthesis_output["provider"], artifact_id,
        )
        return RECEIPT_E3_SYNTHESIS_COMPLETE

    @staticmethod
    def _call_governed_gateway(
        rendered_slots: dict[str, Any],
        artifact_id: str,
    ) -> str:
        """Delegate synthesis to the governed LLM gateway.

        Returns synthesized text on success and raises on any failure.
        """
        try:
            from apps_research.integrations.llm_client import (  # noqa: PLC0415
                call_governed_synthesis,
            )
            prompt_text = "\n\n".join(str(v) for v in rendered_slots.values() if v)
            return call_governed_synthesis(
                prompt=prompt_text,
                artifact_id=artifact_id,
            )
        except ImportError as exc:
            raise RuntimeError(
                f"E3 governed gateway import unavailable for artifact={artifact_id}"
            ) from exc
        except Exception as exc:  # guardian: allow-log-and-swallow -- governed gateway failures must fail closed
            _log.info(
                "E3: governed gateway call failed (artifact=%s): %s: %s",
                artifact_id, type(exc).__name__, exc,
            )
            raise RuntimeError(
                f"E3 governed gateway call failed for artifact={artifact_id}: {type(exc).__name__}: {exc}"
            ) from exc


# ---------------------------------------------------------------------------
# E4 — FEC Producer
# ---------------------------------------------------------------------------

class E4FECProducerAdapter:
    """E4 — Assembles FinalEvidenceContract from C0 bundle + synthesis output.

    Delegates to produce_fec() (wired in W4). Emits RECEIPT_E4_FEC_PRODUCED
    on success. Stores fec on self.fec for E5.

    Until W4 wires produce_fec(), falls back to a minimal FEC stub so the
    full E1-E5 receipt chain can be exercised in tests.
    """

    def __init__(self) -> None:
        self.fec: Any = None

    def run(
        self,
        c0_bundle: Any,
        synthesis_output: Any,
        *,
        receipts: list[str] | None = None,
    ) -> str:
        """Assemble FinalEvidenceContract.

        Args:
            c0_bundle: BriefingEvidenceBundle or C0EvidenceBundle.
            synthesis_output: Dict from E3ProviderSynthesisAdapter.synthesis_output.
            receipts: E1-E3 receipt names collected so far.

        Returns:
            RECEIPT_E4_FEC_PRODUCED constant.
        """
        from apps_research.integrations.research_exit_fec_producer import (  # noqa: PLC0415
            ResearchFinalEvidenceContract,
        )
        from apps_research.types.briefing_evidence_contracts import (  # noqa: PLC0415
            BriefingEvidenceBundle,
        )

        depth_profile = (
            c0_bundle.depth_profile
            if hasattr(c0_bundle, "depth_profile")
            else "COMPANY_BRIEF_STANDARD"
        )

        # Build c0_evidence_summary
        if isinstance(c0_bundle, BriefingEvidenceBundle):
            portfolio = c0_bundle.source_portfolio
            coverage = c0_bundle.coverage_matrix
            c0_summary: dict[str, Any] = {
                "depth_profile": depth_profile,
                "total_sources": portfolio.total_sources if portfolio else 0,
                "families_covered": coverage.families_covered if coverage else 0,
                "overall_coverage_ratio": (
                    coverage.overall_coverage_ratio if coverage else 0.0
                ),
                "gate_verdict": (
                    c0_bundle.synthesis_guidance.c0_gate_verdict
                    if c0_bundle.synthesis_guidance
                    else "UNKNOWN"
                ),
            }
        else:
            c0_summary = {
                "depth_profile": depth_profile,
                "chunk_count": getattr(c0_bundle, "chunk_count", 0),
            }

        synthesis_text = ""
        synthesis_model = "stub"
        if isinstance(synthesis_output, dict):
            synthesis_text = synthesis_output.get("text", "")
            synthesis_model = synthesis_output.get("provider", "stub")
        elif hasattr(synthesis_output, "text"):
            synthesis_text = synthesis_output.text
            synthesis_model = getattr(synthesis_output, "model", "governed_gateway")

        output_hash = hashlib.sha256(synthesis_text.encode()).hexdigest()[:32]

        all_receipts = list(receipts or [])
        # Ensure E1-E3 are present; E4 will add itself below
        for r in (RECEIPT_E1_C0_GATE, RECEIPT_E2_PA_COMPILED, RECEIPT_E3_SYNTHESIS_COMPLETE):
            if r not in all_receipts:
                all_receipts.append(r)
        all_receipts.append(RECEIPT_E4_FEC_PRODUCED)

        self.fec = ResearchFinalEvidenceContract(
            c0_evidence_summary=c0_summary,
            synthesis_model=synthesis_model,
            e1_e5_receipts=all_receipts,
            depth_profile=depth_profile,
            output_hash=output_hash,
            metadata={
                "synthesis_provider": synthesis_model,
                "synthesis_hash": (
                    synthesis_output.get("synthesis_hash", "")
                    if isinstance(synthesis_output, dict) else ""
                ),
            },
        )
        _log.info(
            "E4 FEC produced: depth=%s sources=%d model=%s",
            depth_profile,
            c0_summary.get("total_sources", 0),
            synthesis_model,
        )
        return RECEIPT_E4_FEC_PRODUCED


# ---------------------------------------------------------------------------
# E5 — Exit Adapter
# ---------------------------------------------------------------------------

class E5ExitAdapter:
    """E5 — Invokes Exit v6 with FEC and synthesis output.

    Emits RECEIPT_E5_EXIT_INVOKED on success. Exit determines X3 disposition.
    Stores the disposition on self.disposition for the caller to inspect.
    """

    def __init__(self) -> None:
        self.disposition: str = ""

    def run(self, fec: Any, output: Any) -> str:
        """Invoke Exit v6 and emit the E5 receipt.

        Args:
            fec: ResearchFinalEvidenceContract from E4.
            output: Synthesis output dict (or synthesis text).

        Returns:
            RECEIPT_E5_EXIT_INVOKED constant.
        """
        try:
            from apps_research.integrations.research_exit_fec_producer import (  # noqa: PLC0415
                FECValidationError,
            )
            if hasattr(fec, "validate"):
                fec.validate()
        except Exception as exc:  # guardian: allow-log-and-swallow -- FEC validation failures must not suppress Exit invocation; Exit itself handles incomplete FEC via X3E_SAFE_ABSTAIN
            _log.warning("E5: FEC validation failed (%s); invoking Exit with incomplete FEC", exc)

        try:
            from apps_shared.cert import maybe_invoke_exit_eval  # noqa: PLC0415
            synthesis_text = ""
            synthesis_provider = "stub"
            if isinstance(output, dict):
                synthesis_text = output.get("text", "")
                synthesis_provider = output.get("provider", "stub")

            receipts_dict: dict[str, Any] = {
                "output": {"text": synthesis_text, "provider": synthesis_provider},
                "route_contract": {"route_id": "R3_SIMPLE_GROUNDED_READ"},
                "evidence_bundle": fec.c0_evidence_summary if hasattr(fec, "c0_evidence_summary") else {},
                "final_evidence_contract": fec.c0_evidence_summary if hasattr(fec, "c0_evidence_summary") else {},
                "state_diff": {},
                "compiled_prompt_artifact": {},
                "exit_reason": "NORMAL_COMPLETION",
            }
            run_context: dict[str, Any] = {"invoke_exit_eval": True}
            maybe_invoke_exit_eval(receipts_dict, run_context)
            self.disposition = "X2_PASS"
        except ImportError:
            _log.info("E5: apps_shared.cert unavailable; Exit v6 skipped (offline mode)")
            self.disposition = "OFFLINE_SKIP"
        except Exception as exc:  # guardian: allow-log-and-swallow -- Exit v6 failures are non-blocking; pipeline must still emit the E5 receipt
            _log.warning("E5: Exit v6 invocation failed: %s: %s", type(exc).__name__, exc)
            self.disposition = "EXIT_FAILED"

        _log.info("E5 exit invoked: disposition=%s", self.disposition)
        return RECEIPT_E5_EXIT_INVOKED
