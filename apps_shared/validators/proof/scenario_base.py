"""Shared scenario harness for apps_* runtime proof.

Drives the governed spine layer-by-layer. Each layer is REAL when the wiring
exists (imports succeed and the layer module returns a contract); marked
``NOT_IMPLEMENTED`` honestly otherwise. No fabrication.

# guardian: allow-cross-layer-imports -- proof/test harness; constructs
# full-trajectory scenarios that intentionally exercise L0 routing, L1
# cognition, and L2 execution. The 17 L_APP_core_bypass authority-boundary
# breaches in mv_authority_boundary_breaches are ALL attributed to this
# file and are the *purpose* of the harness — refactoring would defeat
# its function. Author-Gate approval: ADR-071 (2026-04-29).

A scenario is described by a :class:`ScenarioSpec`. :func:`run_app_scenario`
threads the spec through:

    U0 (intake) → L1 (plan) → L0 (route) → C0 (if grounding_required)
                  → Prompt Assembly (if dispatch_model)
                  → L3 (skip-validly for SINGLE_STEP) → L2 (bounded executor)
                  → Exit (NOT_IMPLEMENTED until wired) → UWG (skip)
                  → L6 (skip — observer only, after runtime boundary)

The output is a fully populated :class:`AppRunEvidencePacket` with span
inventory, contract inventory, and gate verdicts. The packet hash binds the
inventory references — manual edits will fail :func:`verify_packet_hash`.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import sys
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from apps_shared.validators.proof.proof_contracts import (
    AppRunEvidencePacket,
    ArtifactRecord,
    ContractRecord,
    GateVerdictRecord,
    SpanRecord,
    sha256_of,
    write_packet,
    write_records,
    CLASSIFICATION_PROOF_ARTIFACT,
)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe(obj: Any, depth: int = 6) -> Any:
    """Best-effort JSON-safe coerce — same shape as scripts/proof harness."""
    if depth < 0:
        return f"<truncated {type(obj).__name__}>"
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        out: dict[str, Any] = {}
        for f in dataclasses.fields(obj):
            try:
                out[f.name] = _safe(getattr(obj, f.name), depth - 1)
            except (AttributeError, TypeError, ValueError) as exc:
                out[f.name] = f"<unreadable: {exc!r}>"
        return out
    if isinstance(obj, dict):
        return {str(k): _safe(v, depth - 1) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set, frozenset)):
        return [_safe(x, depth - 1) for x in obj]
    if hasattr(obj, "name") and hasattr(obj, "value"):
        try:
            return f"{type(obj).__name__}.{obj.name}"
        except (AttributeError, TypeError):  # guardian: allow-silent-swallow -- enum-like object repr fallback to repr(obj) when name/value lookup fails
            pass
    return repr(obj)


# ---------------------------------------------------------------------------
# Scenario spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScenarioSpec:
    """Declarative description of a per-app proof scenario.

    The spec is the ONLY thing each per-app scenario module supplies. The
    spine traversal is identical across all apps — only the inputs and the
    app-specific assertions differ.
    """

    app_id: str
    scenario_id: str
    intake_body: str
    grounding_required: bool
    task_spec: str
    query_spec: str
    expected_layers: tuple[str, ...]  # which layers MUST be PASS for scenario to pass
    risk_class: str = "NORMAL"  # NORMAL | HIGH_IMPACT | INFRASTRUCTURE
    # Optional per-app extras — kept simple in W2; expanded in W3/W4
    extra_required_fields: tuple[str, ...] = ()
    extra_payload: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Scenario context
# ---------------------------------------------------------------------------


class ScenarioContext:
    """Per-run state carrier. Owns ids, span recorder, artifact directory."""

    def __init__(
        self,
        *,
        spec: ScenarioSpec,
        export_root: Path,
        adg_snapshot: Path,
        seed: str | None = None,
    ) -> None:
        self.spec = spec
        self.export_root = export_root
        self.adg_snapshot = adg_snapshot

        # Deterministic IDs derived from seed (default = scenario_id) so two
        # runs with the same seed produce identical content. W3 replay
        # validator depends on this.
        self.seed = seed or spec.scenario_id
        self._span_counter = 0  # incremented per emit_span for stable span_ids

        def _det(label: str, length: int = 16) -> str:
            digest = hashlib.sha256(f"{self.seed}|{label}".encode("utf-8")).hexdigest()
            return digest[:length]

        self._det = _det
        self.run_id = _det("run_id", 12)
        self.session_id = f"sess-{_det('session_id', 8)}"
        self.request_id_hint = f"rq-{_det('request_id', 8)}"
        self.trace_root = f"trace-{_det('trace_root', 32)}"
        self.trace_id = self.trace_root  # alias for span emission

        # Per-scenario artifact dir — every spec gets its own subdir under contracts/.
        #
        # BUG-FIX (2026-04-26): wipe the dir before each run. Without this,
        # repeated invocations with the same export_root accumulate stale
        # contract files (volatile fields like *_receipt_ref change between
        # runs, producing different content hashes → different filenames →
        # both files coexist). The replay validator's
        # ``_read_contract_payload`` uses ``sorted(...)[-1]`` and could pick
        # the wrong one. Wiping here keeps each run pinned to its own
        # contracts.
        self.scenario_dir = export_root / "contracts" / spec.app_id / spec.scenario_id
        if self.scenario_dir.exists():
            import shutil  # local import to avoid module-load cost when unused
            shutil.rmtree(self.scenario_dir, ignore_errors=True)  # guardian: allow-missing-hitl-on-irreversible -- proof export pins fresh scenario contracts subtree per run
        self.scenario_dir.mkdir(parents=True, exist_ok=True)

        self.spans: list[SpanRecord] = []
        self.contracts: list[ContractRecord] = []
        self.gates: list[GateVerdictRecord] = []
        self.artifacts: list[ArtifactRecord] = []
        self.layer_status: dict[str, str] = {}  # layer_name -> PASS|FAIL|SKIPPED|NOT_IMPLEMENTED

        # Carried objects between layers
        self.validated_request: Any = None
        self.plan_contract: Any = None
        self.route_contract: Any = None
        self.final_evidence_contract: Any = None
        self.compiled_envelope: Any = None
        self.sealed_artifact: Any = None
        self.runtime_boundary_ts: str | None = None
        self._exit_disposition: str | None = None
        self._otel_export_result: Any = None  # set by run_app_scenario

    # ------------------------------------------------------------ helpers

    def emit_span(
        self,
        *,
        layer: str,
        name: str,
        parent_span_id: str | None,
        status: str,
        started_at: str,
        ended_at: str,
        attrs: dict[str, Any] | None = None,
        contract_digest: str | None = None,
        gate_id: str | None = None,
    ) -> SpanRecord:
        self._span_counter += 1
        span = SpanRecord(
            trace_id=self.trace_id,
            span_id=self._det(f"span_{self._span_counter}_{layer}_{name}", 16),
            parent_span_id=parent_span_id,
            layer=layer,
            name=name,
            started_at=started_at,
            ended_at=ended_at,
            status=status,
            request_id=self.request_id_hint,
            run_id=self.run_id,
            app_id=self.spec.app_id,
            scenario_id=self.spec.scenario_id,
            contract_digest=contract_digest,
            gate_id=gate_id,
            attrs=attrs or {},
        )
        self.spans.append(span)
        return span

    def emit_contract(self, *, kind: str, payload: Any, span_id: str) -> ContractRecord:
        digest = sha256_of(_safe(payload))
        # Canonical artifact path: contracts/<app>/<scenario>/<kind>_<digest8>.json
        path = self.scenario_dir / f"{kind}_{digest[:8]}.json"
        path.write_text(
            json.dumps(_safe(payload), sort_keys=True, indent=2, default=str),
            encoding="utf-8",
        )
        rec = ContractRecord(
            contract_kind=kind,
            digest=digest,
            emitted_by_span_id=span_id,
            payload_path=str(path.relative_to(self.export_root)).replace("\\", "/"),
        )
        self.contracts.append(rec)
        return rec

    def register_contract(
        self, *, kind: str, payload: Any, span_id: str, existing_rel_path: str
    ) -> ContractRecord:
        """Register a contract that was ALREADY written to disk (e.g. by an app
        runtime driver). Computes the digest, appends a ``ContractRecord`` to
        ``self.contracts``, and returns it — but does NOT re-write the file
        under a digest-suffixed name.

        This avoids the W9 dedup pathology where every driver-emitted artifact
        was being copied to ``<kind>_<digest8>.json`` in addition to its
        canonical filename, doubling the contract count and confusing the
        contract inventory.
        """
        digest = sha256_of(_safe(payload))
        rec = ContractRecord(
            contract_kind=kind,
            digest=digest,
            emitted_by_span_id=span_id,
            payload_path=existing_rel_path.replace("\\", "/"),
        )
        self.contracts.append(rec)
        return rec

    def emit_gate(
        self,
        *,
        gate_id: str,
        verdict: str,
        span_id: str,
        reasons: tuple[str, ...] = (),
        evidence: tuple[str, ...] = (),
    ) -> GateVerdictRecord:
        rec = GateVerdictRecord(
            gate_id=gate_id,
            verdict=verdict,
            emitted_by_span_id=span_id,
            reason_codes=reasons,
            evidence_refs=evidence,
        )
        self.gates.append(rec)
        return rec

    # ------------------------------------------------------------ layers

    def run_u0(self) -> tuple[str, SpanRecord]:
        """U0 intake — real or NOT_IMPLEMENTED."""
        started = _utcnow_iso()
        try:
            from agentic_core.L0_routing.intake.envelope import RawIngressEnvelope
            from agentic_core.L0_routing.intake.pipeline import IntakePipeline, IntakePolicy
        except ImportError as exc:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="U0",
                name="u0.intake",
                parent_span_id=None,
                status="NOT_IMPLEMENTED",
                started_at=started,
                ended_at=ended,
                attrs={"reason": f"import failed: {exc}"},
            )
            self.layer_status["U0"] = "NOT_IMPLEMENTED"
            return "NOT_IMPLEMENTED", sp

        try:
            env = RawIngressEnvelope(
                transport="api",
                method="POST",
                content_type="application/json",
                source_channel=f"proof.{self.spec.app_id}",
                claimed_tenant_id="tenantA",
                claimed_workspace_id="wsA",
                claimed_user_id=f"proof-{self.spec.app_id}",
                auth_credential={"kind": "api_key", "token": "proof-token", "scopes": ["read"]},
                body_text=self.spec.intake_body,
                request_id_hint=self.request_id_hint,
                session_id_hint=self.session_id,
                upstream_traceparent=self.trace_root,
                region="us",
                locale="en-US",
                declared_modalities=("text",),
            )
            outcome = IntakePipeline(IntakePolicy()).run(env)
        except (RuntimeError, ValueError, TypeError, AttributeError) as exc:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="U0",
                name="u0.intake",
                parent_span_id=None,
                status="FAIL",
                started_at=started,
                ended_at=ended,
                attrs={"error": repr(exc), "trace": traceback.format_exc()},
            )
            self.layer_status["U0"] = "FAIL"
            return "FAIL", sp

        ended = _utcnow_iso()
        if outcome.accepted and outcome.validated is not None:
            self.validated_request = outcome.validated
            sp = self.emit_span(
                layer="U0",
                name="u0.intake",
                parent_span_id=None,
                status="PASS",
                started_at=started,
                ended_at=ended,
                attrs={
                    "request_id": outcome.validated.request_id,
                    "auth_verdict": str(outcome.validated.auth_verdict),
                },
            )
            self.emit_contract(kind="ValidatedRequest", payload=outcome.validated, span_id=sp.span_id)
            self.layer_status["U0"] = "PASS"
            return "PASS", sp
        # rejected — that IS a valid receipt for negative scenarios but FAIL for happy path
        sp = self.emit_span(
            layer="U0",
            name="u0.intake",
            parent_span_id=None,
            status="REJECTED",
            started_at=started,
            ended_at=ended,
            attrs={"rejected": _safe(outcome.rejected)},
        )
        self.layer_status["U0"] = "FAIL"
        return "FAIL", sp

    def run_l1(self, parent: SpanRecord | None) -> tuple[str, SpanRecord]:
        started = _utcnow_iso()
        try:
            from agentic_core.L1_cognition.bridges import validated_request_to_plan_contract
        except ImportError as exc:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="L1",
                name="l1.plan",
                parent_span_id=parent.span_id if parent else None,
                status="NOT_IMPLEMENTED",
                started_at=started,
                ended_at=ended,
                attrs={"reason": f"import failed: {exc}"},
            )
            self.layer_status["L1"] = "NOT_IMPLEMENTED"
            return "NOT_IMPLEMENTED", sp

        if self.validated_request is None:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="L1",
                name="l1.plan",
                parent_span_id=parent.span_id if parent else None,
                status="SKIPPED",
                started_at=started,
                ended_at=ended,
                attrs={"reason": "no validated_request from U0"},
            )
            self.layer_status["L1"] = "SKIPPED"
            return "SKIPPED", sp

        try:
            plan = validated_request_to_plan_contract(
                self.validated_request,
                grounding_required=self.spec.grounding_required,
                task_spec_override=self.spec.task_spec,
                query_spec_override=self.spec.query_spec,
            )
        except (RuntimeError, ValueError, TypeError, AttributeError) as exc:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="L1",
                name="l1.plan",
                parent_span_id=parent.span_id if parent else None,
                status="FAIL",
                started_at=started,
                ended_at=ended,
                attrs={"error": repr(exc)},
            )
            self.layer_status["L1"] = "FAIL"
            return "FAIL", sp

        ended = _utcnow_iso()
        self.plan_contract = plan
        sp = self.emit_span(
            layer="L1",
            name="l1.plan",
            parent_span_id=parent.span_id if parent else None,
            status="PASS",
            started_at=started,
            ended_at=ended,
            attrs={"task_spec": plan.task_spec, "grounding_required": plan.grounding_required},
        )
        self.emit_contract(kind="L1PlanContract", payload=plan, span_id=sp.span_id)
        self.layer_status["L1"] = "PASS"
        return "PASS", sp

    def run_l0(self, parent: SpanRecord | None) -> tuple[str, SpanRecord]:
        """L0 route — real V15 selector + adapter."""
        started = _utcnow_iso()
        try:
            from agentic_core.L0_routing.reasoning.v15_route_selector import (
                RouteSignalsV15,
                select_route_v15,
            )
            from agentic_core.L0_routing.reasoning.v15_to_c0_adapter import v15_to_route_contract
            from agentic_core.L0_routing.c0_retrieval.verdicts import SourceClass as C0SourceClass
            from agentic_core.L0_routing.types.route_contract_v15 import (
                AuthorityScope,
                CapabilityClass,
                FreshnessClassV15,
                SandboxClass,
                SideEffectClass,
                SupportTargetV15,
                WriteAuthority,
            )
        except ImportError as exc:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="L0",
                name="l0.route",
                parent_span_id=parent.span_id if parent else None,
                status="NOT_IMPLEMENTED",
                started_at=started,
                ended_at=ended,
                attrs={"reason": f"import failed: {exc}"},
            )
            self.layer_status["L0"] = "NOT_IMPLEMENTED"
            return "NOT_IMPLEMENTED", sp

        try:
            signals = RouteSignalsV15(
                ingress_ok=True,
                authority=AuthorityScope(
                    tenant_scope="tenantA",
                    acl_scope=("reader",),
                    region_scope="us",
                    capability_class=CapabilityClass.READ_ONLY,
                    side_effect_class=SideEffectClass.PURE,
                    sandbox_class=SandboxClass.NO_SANDBOX,
                    write_authority=WriteAuthority.NONE_UNTIL_UWG,
                ),
                policy_hash=f"ph-{self.spec.app_id}",
                blueprint_hash=f"bp-{self.spec.app_id}",
                snapshot_id=f"snap-{self.run_id}",
                trace_root=self.trace_root,
                route_span_id=self._det("v15_route_span_id", 16),
                replay_key=f"rrk-{self.run_id}",
                route_telemetry_event_id=self._det("v15_telemetry_event_id", 16),
                classifier_confidence=0.82,
                grounding_required=self.spec.grounding_required,
                support_target=SupportTargetV15.SOURCE_BACKED_SUMMARY,
                freshness_class=FreshnessClassV15.STATIC,
            )
            v15 = select_route_v15(signals)
            v15_signed = v15.sign(b"proof-harness-route-key")
            route = v15_to_route_contract(
                v15_signed,
                allowed_sources=(C0SourceClass.DOCS,),
                data_class="internal",
                route_replay_key=f"rrk-{self.run_id}",
                policy_hash=f"ph-{self.spec.app_id}",
                blueprint_hash=f"bp-{self.spec.app_id}",
            )
        except (RuntimeError, ValueError, TypeError, AttributeError) as exc:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="L0",
                name="l0.route",
                parent_span_id=parent.span_id if parent else None,
                status="FAIL",
                started_at=started,
                ended_at=ended,
                attrs={"error": repr(exc)},
            )
            self.layer_status["L0"] = "FAIL"
            return "FAIL", sp

        ended = _utcnow_iso()
        self.route_contract = route
        sp = self.emit_span(
            layer="L0",
            name="l0.route",
            parent_span_id=parent.span_id if parent else None,
            status="PASS",
            started_at=started,
            ended_at=ended,
            attrs={
                "route_id": route.route_id,
                "execution_form": route.execution_form,
                "hmac_present": bool(route.hmac_sig),
            },
        )
        self.emit_contract(kind="RouteContract", payload=route, span_id=sp.span_id)
        self.layer_status["L0"] = "PASS"
        return "PASS", sp

    def run_l3_skip(self, parent: SpanRecord | None) -> tuple[str, SpanRecord]:
        """L3 valid-skip for SINGLE_STEP routes (the common case)."""
        started = _utcnow_iso()
        rid = getattr(self.route_contract, "route_id", "") if self.route_contract else ""
        exec_form = getattr(self.route_contract, "execution_form", "") if self.route_contract else ""
        skip_ok = (rid.startswith("R3_") and "MANAGED" not in rid) or exec_form == "SINGLE_STEP"
        ended = _utcnow_iso()
        sp = self.emit_span(
            layer="L3",
            name="l3.skip" if skip_ok else "l3.dispatch",
            parent_span_id=parent.span_id if parent else None,
            status="SKIPPED_VALIDLY" if skip_ok else "NOT_IMPLEMENTED",
            started_at=started,
            ended_at=ended,
            attrs={"route_id": rid, "execution_form": exec_form},
        )
        self.layer_status["L3"] = "SKIPPED_VALIDLY" if skip_ok else "NOT_IMPLEMENTED"
        return self.layer_status["L3"], sp

    # ------------------------------------------------------------ W6 layers

    def _default_chunks(self) -> tuple[Any, ...]:
        """Two deterministic evidence chunks for C0 grounding.

        Uses the production CandidateChunk + HydrationManifest types so the
        chunk objects are byte-equal under :func:`sha256_of` for two runs
        with the same scenario_id. The text is intentionally aligned with
        canonical doctrine docs to match what L2's deterministic model
        will paraphrase.
        """
        from agentic_core.L0_routing.c0_retrieval import (
            CandidateChunk,
            HydrationManifest,
            RetrievalScores,
            SourceClass,
        )
        from agentic_core.L0_routing.c0_retrieval.verdicts import RetrievalLane

        def _mk(chunk_id: str, text: str, line_range: tuple[int, int], section: str) -> CandidateChunk:
            manifest = HydrationManifest(
                source_id="docs/reference/C0 Context Engine_detailed.md",
                file_path="docs/reference/C0 Context Engine_detailed.md",
                line_range=line_range,
                version="v1.0",
                tenant="tenantA",
                region="us",
                data_class="internal",
                retrieval_lane=RetrievalLane.DENSE,
                parent_chunk_id="",
                section=section,
            )
            return CandidateChunk(
                chunk_id=chunk_id,
                source_class=SourceClass.DOCS,
                text=text,
                manifest=manifest,
                scores=RetrievalScores(raw_score=0.85, normalized_score=0.85, rank=1),
                found_by_lanes=(RetrievalLane.SPARSE, RetrievalLane.DENSE),
            )

        return (
            _mk(
                "c0_doctrine_1",
                "C0 retrieves evidence; it does not answer. The contract carries "
                "verified_chunk_ids, a score breakdown, and a recommended_disposition.",
                (1, 20),
                "C0 ROLE",
            ),
            _mk(
                "c0_doctrine_2",
                "Routing and answering authority belong to L0/L1/L2/L3 per the spine.",
                (40, 60),
                "AUTHORITY",
            ),
        )

    def run_c0(self, parent: SpanRecord | None) -> tuple[str, SpanRecord]:
        """C0 grounding via the real dispatcher — only when grounding_required."""
        started = _utcnow_iso()
        if not self.spec.grounding_required or self.route_contract is None or self.plan_contract is None:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="C0",
                name="c0.skip",
                parent_span_id=parent.span_id if parent else None,
                status="SKIPPED",
                started_at=started,
                ended_at=ended,
                attrs={"reason": "grounding_required=False or upstream missing"},
            )
            self.layer_status["C0"] = "SKIPPED"
            return "SKIPPED", sp
        try:
            from agentic_core.L0_routing.c0_retrieval.candidate_pool import CandidateEvidencePool
            from agentic_core.L0_routing.c0_retrieval.dispatcher import run_c0
        except ImportError as exc:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="C0",
                name="c0.dispatch",
                parent_span_id=parent.span_id if parent else None,
                status="NOT_IMPLEMENTED",
                started_at=started,
                ended_at=ended,
                attrs={"reason": f"import failed: {exc}"},
            )
            self.layer_status["C0"] = "NOT_IMPLEMENTED"
            return "NOT_IMPLEMENTED", sp

        try:
            chunks = self._default_chunks()

            def fetch(plan, route):  # noqa: ANN001 -- callback shape fixed by C0
                return CandidateEvidencePool(
                    plan_id=plan.plan_id,
                    candidates=chunks,
                    lanes_used=tuple({l for c in chunks for l in c.found_by_lanes}),
                )

            def null_adj(_node_id, _allowed):  # noqa: ANN001
                return ()

            result = run_c0(
                route=self.route_contract,
                plan_contract=self.plan_contract,
                fetch=fetch,
                adjacency=null_adj,
                request_id=self.request_id_hint,
            )
        except (RuntimeError, ValueError, TypeError, AttributeError) as exc:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="C0",
                name="c0.dispatch",
                parent_span_id=parent.span_id if parent else None,
                status="FAIL",
                started_at=started,
                ended_at=ended,
                attrs={"error": repr(exc)},
            )
            self.layer_status["C0"] = "FAIL"
            return "FAIL", sp

        ended = _utcnow_iso()
        self.final_evidence_contract = result.contract
        sp = self.emit_span(
            layer="C0",
            name="c0.dispatch",
            parent_span_id=parent.span_id if parent else None,
            status="PASS",
            started_at=started,
            ended_at=ended,
            attrs={
                "support_score": round(result.contract.support_score, 4),
                "must_use_count": len(result.contract.must_use),
                "supporting_count": len(result.contract.supporting),
            },
        )
        self.emit_contract(kind="FinalEvidenceContract", payload=result.contract, span_id=sp.span_id)
        self.layer_status["C0"] = "PASS"
        return "PASS", sp

    def run_prompt_assembly(self, parent: SpanRecord | None) -> tuple[str, SpanRecord]:
        """Prompt Assembly orchestrator — only when C0 produced a contract."""
        started = _utcnow_iso()
        if self.final_evidence_contract is None or self.route_contract is None or self.plan_contract is None:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="PromptAssembly",
                name="pa.skip",
                parent_span_id=parent.span_id if parent else None,
                status="SKIPPED",
                started_at=started,
                ended_at=ended,
                attrs={"reason": "upstream contract missing"},
            )
            self.layer_status["PromptAssembly"] = "SKIPPED"
            return "SKIPPED", sp
        try:
            from agentic_core.prompt_governance import assemble_prompt
        except ImportError as exc:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="PromptAssembly",
                name="pa.assemble",
                parent_span_id=parent.span_id if parent else None,
                status="NOT_IMPLEMENTED",
                started_at=started,
                ended_at=ended,
                attrs={"reason": f"import failed: {exc}"},
            )
            self.layer_status["PromptAssembly"] = "NOT_IMPLEMENTED"
            return "NOT_IMPLEMENTED", sp

        try:
            compiled = assemble_prompt(
                final_contract=self.final_evidence_contract,
                route=self.route_contract,
                plan=self.plan_contract,
                request_id=self.request_id_hint,
            )
        except (RuntimeError, ValueError, TypeError, AttributeError) as exc:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="PromptAssembly",
                name="pa.assemble",
                parent_span_id=parent.span_id if parent else None,
                status="FAIL",
                started_at=started,
                ended_at=ended,
                attrs={"error": repr(exc)},
            )
            self.layer_status["PromptAssembly"] = "FAIL"
            return "FAIL", sp

        ended = _utcnow_iso()
        self.compiled_envelope = compiled
        status = "PASS" if compiled.is_dispatchable else "FAIL"
        sp = self.emit_span(
            layer="PromptAssembly",
            name="pa.assemble",
            parent_span_id=parent.span_id if parent else None,
            status=status,
            started_at=started,
            ended_at=ended,
            attrs={
                "manifest_hash": compiled.manifest_hash[:16],
                "dispatch_disposition": compiled.dispatch_disposition,
                "is_dispatchable": compiled.is_dispatchable,
            },
        )
        self.emit_contract(kind="PromptEnvelope", payload=compiled.envelope, span_id=sp.span_id)
        self.layer_status["PromptAssembly"] = status
        return status, sp

    def run_l2(self, parent: SpanRecord | None) -> tuple[str, SpanRecord]:
        """L2 bounded executor with a deterministic model invocation."""
        started = _utcnow_iso()
        if self.compiled_envelope is None:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="L2",
                name="l2.skip",
                parent_span_id=parent.span_id if parent else None,
                status="SKIPPED",
                started_at=started,
                ended_at=ended,
                attrs={"reason": "no compiled envelope"},
            )
            self.layer_status["L2"] = "SKIPPED"
            return "SKIPPED", sp
        try:
            from agentic_core.L2_execution.bounded_executor import ModelInvokeResult, execute
        except ImportError as exc:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="L2",
                name="l2.execute",
                parent_span_id=parent.span_id if parent else None,
                status="NOT_IMPLEMENTED",
                started_at=started,
                ended_at=ended,
                attrs={"reason": f"import failed: {exc}"},
            )
            self.layer_status["L2"] = "NOT_IMPLEMENTED"
            return "NOT_IMPLEMENTED", sp

        # Deterministic model: paraphrases the cited doctrine. Same seed +
        # same envelope = byte-equal output.
        synthesized = (
            f"For app={self.spec.app_id} task={self.spec.task_spec}: "
            "C0 retrieves evidence and the spine routes / answers per doctrine. "
            "This response is grounded in the cited C0 chunks."
        )

        def deterministic_model(_envelope: Any) -> Any:
            return ModelInvokeResult(
                output_text=synthesized,
                token_usage=96,
                model_id="proof_harness_stub",
                cost_usd=0.0,
                error=None,
            )

        try:
            sealed = execute(
                self.compiled_envelope,
                model_invoke=deterministic_model,
                request_id=self.request_id_hint,
                trace_id=self.trace_root,
                session_id=self.session_id,
                tenant="tenantA",
                principal_id=f"proof-{self.spec.app_id}",
                agent_class="L2BoundedExecutor",
                agent_version="1.0",
                max_attempts=1,
            )
        except (RuntimeError, ValueError, TypeError, AttributeError) as exc:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="L2",
                name="l2.execute",
                parent_span_id=parent.span_id if parent else None,
                status="FAIL",
                started_at=started,
                ended_at=ended,
                attrs={"error": repr(exc)},
            )
            self.layer_status["L2"] = "FAIL"
            return "FAIL", sp

        ended = _utcnow_iso()
        self.sealed_artifact = sealed
        sp = self.emit_span(
            layer="L2",
            name="l2.execute",
            parent_span_id=parent.span_id if parent else None,
            status="PASS" if not sealed.failure else "FAIL",
            started_at=started,
            ended_at=ended,
            attrs={
                "tokens": sealed.tokens_consumed,
                "attempts": len(sealed.invocation_records),
                "failure": bool(sealed.failure),
            },
        )
        self.emit_contract(
            kind="SealedArtifact",
            payload=sealed.to_exit_artifact_kwargs(),
            span_id=sp.span_id,
        )
        self.layer_status["L2"] = "PASS" if not sealed.failure else "FAIL"

        # W2: Real-app runtime driver hook. If a per-app driver is registered,
        # run it AFTER the spine's bounded executor has succeeded. The driver
        # invokes the app's actual engines and writes app-specific artifacts
        # (decision_packet, evidence_register, audit_trace, ...) under
        # ctx.scenario_dir. This converts spine-proof into app-proof per the
        # anti-cheat spec — without it, the spine alone can "look like it
        # ran" without actually exercising the app's code path.
        if not sealed.failure:
            try:
                from apps_shared.validators.proof.runtime_drivers import get_driver
                driver = get_driver(self.spec.app_id)
            except ImportError:
                driver = None
            if driver is not None:
                drv_started = _utcnow_iso()
                try:
                    artifacts = driver.invoke(self)
                except (
                    RuntimeError, ValueError, TypeError, AttributeError,
                    ImportError, KeyError, OSError,
                ) as exc:
                    drv_ended = _utcnow_iso()
                    self.emit_span(
                        layer="L2",
                        name=f"l2.driver.{self.spec.app_id}",
                        parent_span_id=sp.span_id,
                        status="FAIL",
                        started_at=drv_started,
                        ended_at=drv_ended,
                        attrs={"error": repr(exc), "driver_app_id": driver.app_id},
                    )
                    # Driver failure does not collapse L2 status — the spine
                    # still produced a sealed artifact. The verifier surfaces
                    # the absence of expected app-specific files in W7 tests.
                else:
                    drv_ended = _utcnow_iso()
                    drv_span = self.emit_span(
                        layer="L2",
                        name=f"l2.driver.{self.spec.app_id}",
                        parent_span_id=sp.span_id,
                        status="PASS",
                        started_at=drv_started,
                        ended_at=drv_ended,
                        attrs={
                            "driver_app_id": driver.app_id,
                            "artifact_count": len(artifacts),
                            "artifact_kinds": sorted(artifacts.keys()),
                        },
                    )
                    # W9 dedup: register driver-emitted artifacts as contracts
                    # WITHOUT rewriting them under digest-suffixed names. The
                    # driver already wrote each file with its trace-link
                    # envelope; ``register_contract`` just appends a
                    # ContractRecord pointing at the existing path.
                    for kind, rel_path in artifacts.items():
                        full = self.scenario_dir / rel_path
                        if not full.exists():
                            continue
                        try:
                            payload = json.loads(full.read_text(encoding="utf-8"))
                        except (OSError, json.JSONDecodeError):
                            continue
                        try:
                            rel_to_export = str(full.relative_to(self.export_root)).replace("\\", "/")
                        except ValueError:
                            rel_to_export = rel_path.replace("\\", "/")
                        self.register_contract(
                            kind=kind,
                            payload=payload,
                            span_id=drv_span.span_id,
                            existing_rel_path=rel_to_export,
                        )

        return self.layer_status["L2"], sp

    def run_exit(self, parent: SpanRecord | None) -> tuple[str, SpanRecord]:
        """Exit Eval — uses real evaluate_exit when L2 sealed an artifact."""
        started = _utcnow_iso()
        # Set runtime boundary timestamp — anything after this is L6.
        self.runtime_boundary_ts = _utcnow_iso()

        if self.sealed_artifact is None:
            # Without L2 there's no sealed artifact to evaluate. Emit a
            # NOT_APPLICABLE gate (placeholder) consistent with W2 behavior.
            ended = self.runtime_boundary_ts
            sp = self.emit_span(
                layer="Exit",
                name="exit.skip",
                parent_span_id=parent.span_id if parent else None,
                status="NOT_IMPLEMENTED",
                started_at=started,
                ended_at=ended,
                attrs={"reason": "no sealed artifact (no L2 invocation)"},
            )
            self.emit_gate(
                gate_id="exit.preflight",
                verdict="NOT_APPLICABLE",
                span_id=sp.span_id,
                reasons=("no_l2_sealed_artifact",),
            )
            self.layer_status["Exit"] = "NOT_IMPLEMENTED"
            return "NOT_IMPLEMENTED", sp

        try:
            from agentic_core.L5_safety.eval_spine.budget_envelope import BudgetEnvelope
            from agentic_core.L5_safety.eval_spine.exit_eval import (
                ExitEvalPolicy,
                SealedArtifact,
                evaluate_exit,
            )
        except ImportError as exc:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="Exit",
                name="exit.evaluate",
                parent_span_id=parent.span_id if parent else None,
                status="NOT_IMPLEMENTED",
                started_at=started,
                ended_at=ended,
                attrs={"reason": f"import failed: {exc}"},
            )
            self.layer_status["Exit"] = "NOT_IMPLEMENTED"
            return "NOT_IMPLEMENTED", sp

        try:
            sealed_kwargs = self.sealed_artifact.to_exit_artifact_kwargs()
            artifact = SealedArtifact(**sealed_kwargs)
            envelope = BudgetEnvelope(
                tokens_max=8000,
                latency_ms_max=5000,
                tool_calls_max=4,
                cost_usd_max=1.0,
            )
            policy = ExitEvalPolicy(
                policy_snapshot=f"proof_policy_{self.spec.app_id}",
                output_contract_ref=None,
                single_tool_names=(),
                expected_tools=frozenset(),
                required_tools=frozenset(),
                forbidden_tools=frozenset(),
            )
            result = evaluate_exit(artifact, envelope, policy)
            decision = result.exit_decision
        except (RuntimeError, ValueError, TypeError, AttributeError) as exc:
            ended = _utcnow_iso()
            sp = self.emit_span(
                layer="Exit",
                name="exit.evaluate",
                parent_span_id=parent.span_id if parent else None,
                status="FAIL",
                started_at=started,
                ended_at=ended,
                attrs={"error": repr(exc)},
            )
            self.layer_status["Exit"] = "FAIL"
            return "FAIL", sp

        ended = _utcnow_iso()
        sp = self.emit_span(
            layer="Exit",
            name="exit.evaluate",
            parent_span_id=parent.span_id if parent else None,
            status="PASS",
            started_at=started,
            ended_at=ended,
            attrs={
                "disposition": decision.disposition,
                "reason_code": decision.reason_code,
            },
        )
        self.emit_gate(
            gate_id="exit.evaluate",
            verdict=decision.disposition.upper() if decision.disposition else "UNKNOWN",
            span_id=sp.span_id,
            reasons=(decision.reason_code,) if decision.reason_code else (),
        )
        self.emit_contract(kind="ExitDecision", payload=decision, span_id=sp.span_id)
        # Update packet field
        # The decision.disposition is canonical; record it
        self.layer_status["Exit"] = "PASS"
        # Also stash the disposition for the packet builder
        self._exit_disposition = decision.disposition
        return "PASS", sp

    # ------------------------------------------------------------ packet build

    def build_packet(self) -> AppRunEvidencePacket:
        """Materialize all records to disk and return the evidence packet."""
        # Write per-record JSON sidecars
        traces_dir = self.export_root / "traces"
        contracts_idx_dir = self.export_root / "manifests"
        gates_dir = self.export_root / "gates"
        artifacts_dir = self.export_root / "artifacts"
        for d in (traces_dir, contracts_idx_dir, gates_dir, artifacts_dir):
            d.mkdir(parents=True, exist_ok=True)

        span_path = traces_dir / f"{self.spec.app_id}_trace.json"
        gate_path = gates_dir / f"{self.spec.app_id}_gate_verdicts.json"
        artifact_path = artifacts_dir / f"{self.spec.app_id}_artifact_inventory.json"
        contract_inv_path = self.scenario_dir / "contract_inventory.json"

        write_records(self.spans, span_path)
        write_records(self.contracts, contract_inv_path)
        write_records(self.gates, gate_path)
        write_records(self.artifacts, artifact_path)

        # Compute aggregate hashes for the packet
        route_digest = getattr(self.route_contract, "deterministic_route_digest", None) or getattr(
            self.route_contract, "route_id", None
        )
        evidence_hash = (
            sha256_of(_safe(self.final_evidence_contract))
            if self.final_evidence_contract is not None
            else None
        )
        prompt_hash = (
            getattr(self.compiled_envelope, "manifest_hash", None)
            if self.compiled_envelope is not None
            else None
        )

        packet = AppRunEvidencePacket(
            app_id=self.spec.app_id,
            scenario_id=self.spec.scenario_id,
            command=" ".join(sys.argv),
            cwd=os.getcwd(),
            process_id=os.getpid(),
            python_executable=sys.executable,
            git_commit_or_snapshot_ref=self.adg_snapshot.name,
            adg_snapshot_ref=str(self.adg_snapshot),
            request_id=self.request_id_hint,
            session_id=self.session_id,
            run_id=self.run_id,
            trace_root=self.trace_root,
            trace_id=self.trace_id,
            policy_hash=f"ph-{self.spec.app_id}",
            blueprint_hash=f"bp-{self.spec.app_id}",
            replay_key=f"rrk-{self.run_id}",
            input_hash=sha256_of(self.spec.intake_body),
            route_digest=route_digest,
            prompt_hash=prompt_hash,
            evidence_contract_hash=evidence_hash,
            sealed_artifact_hash=None,
            runtime_boundary_timestamp=self.runtime_boundary_ts,
            l6_start_timestamp=None,
            exit_disposition=self._exit_disposition or "NOT_IMPLEMENTED",
            artifact_inventory=[str(artifact_path.relative_to(self.export_root)).replace("\\", "/")],
            contract_inventory=[str(contract_inv_path.relative_to(self.export_root)).replace("\\", "/")],
            gate_verdict_inventory=[str(gate_path.relative_to(self.export_root)).replace("\\", "/")],
            span_inventory=[str(span_path.relative_to(self.export_root)).replace("\\", "/")],
            span_tree_ref=str(span_path.relative_to(self.export_root)).replace("\\", "/"),
        )

        # Determine PASS/FAIL based on expected_layers
        for layer in self.spec.expected_layers:
            status = self.layer_status.get(layer, "MISSING")
            if status not in ("PASS", "SKIPPED_VALIDLY"):
                packet.add_fail_reason(
                    "REQUIRED_LAYER_NOT_PASS",
                    f"layer={layer} status={status}",
                )
        packet.mark_pass_if_clean()
        return packet


# ---------------------------------------------------------------------------
# Top-level scenario runner
# ---------------------------------------------------------------------------


def run_app_scenario(
    spec: ScenarioSpec,
    *,
    export_root: Path,
    adg_snapshot: Path,
    customizer: Callable[[ScenarioContext], None] | None = None,
    seed: str | None = None,
) -> AppRunEvidencePacket:
    """Run one app's proof scenario.

    ``customizer`` is an optional hook a per-app scenario can use to add
    app-specific gate verdicts (e.g. apps_underwriting_ai HITL gate, apps_lic
    egress gate). It runs AFTER the layer pipeline but before packet build.

    ``seed`` controls deterministic ID derivation. When None, defaults to
    ``spec.scenario_id`` so every run with the same spec produces identical
    content (enables W3 replay validation).
    """
    ctx = ScenarioContext(
        spec=spec,
        export_root=export_root,
        adg_snapshot=adg_snapshot,
        seed=seed,
    )

    _, u0_span = ctx.run_u0()
    _, l1_span = ctx.run_l1(u0_span)
    _, l0_span = ctx.run_l0(l1_span)
    # W6: C0 + Prompt Assembly + L2 driven for grounded scenarios.
    _, c0_span = ctx.run_c0(l0_span)
    _, pa_span = ctx.run_prompt_assembly(c0_span)
    _, l3_span = ctx.run_l3_skip(pa_span)
    _, l2_span = ctx.run_l2(l3_span)
    _, _ = ctx.run_exit(l2_span)

    # W6.3 — optional OTEL SDK mirror (DISABLED unless SDK + endpoint set).
    # Emits BEFORE customizer so any customizer-emitted spans aren't held
    # back, but the result is recorded for the packet builder.
    try:
        from apps_shared.validators.proof.otel_export import maybe_export_spans

        ctx._otel_export_result = maybe_export_spans(ctx.spans)
    except (ImportError, RuntimeError, ValueError) as _otel_exc:
        ctx._otel_export_result = None

    if customizer is not None:
        # BUG-FIX (2026-04-26): the previous (RuntimeError, ValueError,
        # TypeError, AttributeError) tuple was too narrow. Customizers
        # invoke sandbox_writer / request_uwg_commit which can raise
        # ImportError (missing optional deps), OSError (filesystem), or
        # KeyError (payload shape). An uncaught exception here would crash
        # the entire proof_runner and fail all subsequent apps.
        try:
            customizer(ctx)
        except (
            RuntimeError, ValueError, TypeError, AttributeError,
            ImportError, OSError, KeyError,
        ) as exc:
            # Customizer failure is recorded as a span, not silently swallowed.
            ts = _utcnow_iso()
            ctx.emit_span(
                layer="customizer", name=f"{spec.app_id}.customizer",
                parent_span_id=None, status="FAIL",
                started_at=ts,
                ended_at=ts,
                attrs={"error": repr(exc)},
            )

    packet = ctx.build_packet()
    packet_path = ctx.scenario_dir / "evidence_packet.json"
    write_packet(packet, packet_path)
    return packet


__all__ = [
    "ScenarioSpec",
    "ScenarioContext",
    "run_app_scenario",
]
