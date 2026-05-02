"""Governed-run context manager.

Wraps the deterministic HOP pipeline in genuine spine receipts. Single
``run_id`` threads every artifact. Real wall-clock timings drive the
OTEL trace. No synthetic spans, no fabricated contracts.

Usage in apps_rg/__main__.py:

    with governed_run(target_company=..., target_role=..., cli_args=argv) as gr:
        with gr.span("L2_execute"):
            asyncio.run(_run())
        if args.target_company:
            with gr.span("post_pipeline"):
                _run_post_pipeline(args)
        gr.set_subprocess_exit_code(0)

The context manager:
  1. emits U0IntakeEnvelope on enter
  2. emits L1PlanContract on enter
  3. reads route_registry.yaml -> emits RouteContract on enter
  4. computes static DAG sha256 -> emits L3BypassReceipt on enter
  5. records OTEL spans during the body
  6. emits L2ExecutionReceipt on exit
  7. emits ExitReviewPacket with X3 disposition on exit
  8. emits RuntimeExhaustBundle AFTER exit (per spec, L6 observes after Exit)
  9. writes otel_runtime_trace.json
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import yaml

from apps_rg.runtime.contracts import (
    ExitReviewPacket,
    L1PlanContract,
    L1PlanStep,
    L2ExecutionReceipt,
    L3BypassReceipt,
    OtelRuntimeTrace,
    RouteContract,
    RuntimeExhaustBundle,
    U0IntakeEnvelope,
)
from apps_rg.runtime.otel_trace import StageTracer, _utc_iso

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTE_REGISTRY_PATH = REPO_ROOT / "apps_rg" / "config" / "route_registry.yaml"
L3_DAG_PATH = REPO_ROOT / "apps_rg" / "config" / "l3_dag.yaml"


def _sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )


def _hop_plan() -> list[L1PlanStep]:
    return [
        L1PlanStep(step_id="hop_0_intake",  name="HOP-0 Intake",         kind="ingest"),
        L1PlanStep(step_id="hop_1_extract", name="HOP-1 Extraction",     kind="transform"),
        L1PlanStep(step_id="hop_2_score",   name="HOP-2 Scoring",        kind="score"),
        L1PlanStep(step_id="hop_3_assemble", name="HOP-3 Resume Assembly", kind="render"),
        L1PlanStep(step_id="hop_4_narrative", name="HOP-4 Narrative Pass", kind="render", optional=True),
        L1PlanStep(step_id="hop_5_docx",    name="HOP-5 DOCX Export",    kind="render", optional=True),
    ]


class GovernedRun:
    """Live state of one governed apps_rg run."""

    def __init__(
        self,
        *,
        target_company: str | None,
        target_role: str | None,
        cli_args: list[str],
        run_dir: Path | None = None,
    ) -> None:
        self.run_id = f"apps_rg-run-{uuid.uuid4().hex[:16]}"
        self.request_id = self.run_id  # apps_rg has no upstream request system
        self.trace_root = self.run_id
        self.target_company = target_company
        self.target_role = target_role
        self.cli_args = list(cli_args)
        self.cli_args_digest = _sha256_text(" ".join(self.cli_args))

        # Run dir is set when known (post-`generate_resume.main()`). The
        # spine pre-emits to a staging dir until we can resolve the real
        # run dir from artifacts/apps_rg/runs/.
        self._run_dir = run_dir
        self._staging: dict[str, dict[str, Any]] = {}
        self._tracer = StageTracer(self.run_id, self.request_id, self.trace_root)
        self._stage_outcomes: dict[str, str] = {}
        self._subprocess_exit_code: int | None = None
        self._failed_stages: list[str] = []
        self._wall_start = time.time()

        # Contract IDs (assigned at construction so they are stable across emits)
        self._intake_id = f"U0-{uuid.uuid4().hex[:16]}"
        self._plan_id = f"L1-{uuid.uuid4().hex[:16]}"
        self._route_contract_id = f"L0-{uuid.uuid4().hex[:16]}"
        self._l3_bypass_id = f"L3B-{uuid.uuid4().hex[:16]}"
        self._l2_receipt_id = f"L2-{uuid.uuid4().hex[:16]}"
        self._exit_packet_id = f"X3-{uuid.uuid4().hex[:16]}"
        self._exhaust_id = f"L6-{uuid.uuid4().hex[:16]}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_run_dir(self, run_dir: Path) -> None:
        """Late-bound run dir resolution.

        ``generate_resume.main()`` creates ``artifacts/apps_rg/runs/<ts>/``
        internally. After it finishes we can resolve and rewrite the
        spine receipts there.
        """
        self._run_dir = run_dir

    def span(self, name: str, **attrs: Any):
        return self._tracer.span(name, run_id=self.run_id, **attrs)

    def mark_stage(self, stage_name: str, outcome: str) -> None:
        self._stage_outcomes[stage_name] = outcome
        if outcome != "ok":
            self._failed_stages.append(stage_name)

    def set_subprocess_exit_code(self, code: int) -> None:
        self._subprocess_exit_code = code

    # ------------------------------------------------------------------
    # Phase 1: pre-execution receipts (U0, L1, L0, L3-bypass)
    # ------------------------------------------------------------------

    def emit_pre_execution_contracts(self) -> None:
        intake = U0IntakeEnvelope(
            run_id=self.run_id,
            request_id=self.request_id,
            trace_root=self.trace_root,
            intake_id=self._intake_id,
            target_company=self.target_company,
            target_role=self.target_role,
            cli_args_digest=self.cli_args_digest,
            user_intent=self._user_intent(),
        )
        self._staging["u0_intake_envelope"] = intake.model_dump()

        plan = L1PlanContract(
            run_id=self.run_id,
            request_id=self.request_id,
            trace_root=self.trace_root,
            plan_id=self._plan_id,
            steps=_hop_plan(),
            grounding_required=False,
            prompt_assembly_required=False,
            plan_rationale=(
                "apps_rg is a deterministic HOP pipeline. Plan is hard-coded by route "
                "selection; no model-driven planning is required. Grounding and prompt "
                "assembly are handled internally by the narrative HOPs and do not require "
                "separate C0/PA stages at the spine level."
            ),
        )
        self._staging["l1_plan_contract"] = plan.model_dump()

        registry_data = self._read_route_registry()
        route_def = self._select_route(registry_data)
        dag_sha = _sha256_file(L3_DAG_PATH)

        route = RouteContract(
            run_id=self.run_id,
            request_id=self.request_id,
            trace_root=self.trace_root,
            route_contract_id=self._route_contract_id,
            route_id=route_def["route_id"],
            execution_form=route_def["execution_form"],
            route_reason=(
                f"L0 selected '{route_def['route_id']}' from "
                f"{ROUTE_REGISTRY_PATH.name}: deterministic HOP pipeline, "
                f"no managed workflow required."
            ),
            l3_required=bool(route_def.get("l3_required", False)),
            static_dag_ref=route_def.get("static_dag_ref"),
            static_dag_sha256=dag_sha,
            selected_capability=route_def.get("selected_capability", "apps_rg.resume_generation_v1"),
        )
        self._staging["route_contract"] = route.model_dump()

        bypass = L3BypassReceipt(
            run_id=self.run_id,
            request_id=self.request_id,
            trace_root=self.trace_root,
            l3_bypass_receipt_id=self._l3_bypass_id,
            route_contract_id=self._route_contract_id,
            execution_form=route_def["execution_form"],
            l3_bypass_reason=route_def.get("bypass_reason_when_invoked", "NO_MANAGED_WORKFLOW_REQUIRED"),
            static_dag_available=L3_DAG_PATH.exists(),
            static_dag_ref=str(L3_DAG_PATH.relative_to(REPO_ROOT)).replace("\\", "/")
                if L3_DAG_PATH.exists() else None,
            why_static_dag_not_used=(
                "Static L3 DAG documents the apps_rg HOP topology and is registered for "
                "audit, but runtime L3 orchestration is not required because the pipeline "
                "is a single-route deterministic sequence with no retries, branches, or "
                "joins. The bypass is justified by L0 RouteContract execution_form="
                f"{route_def['execution_form']}, l3_required=false."
            ),
        )
        self._staging["l3_bypass_receipt"] = bypass.model_dump()

    # ------------------------------------------------------------------
    # Phase 2: post-execution receipts (L2, Exit, L6)
    # ------------------------------------------------------------------

    def emit_post_execution_contracts(self, run_dir: Path) -> None:
        # Always work with an absolute path; callers may pass a relative one.
        run_dir = run_dir.resolve()
        self._run_dir = run_dir

        # Real artifact enumeration (post-pipeline)
        artifact_refs: list[str] = []
        artifact_sha: dict[str, str] = {}
        if run_dir.exists():
            for p in sorted(run_dir.rglob("*")):
                if not (p.is_file() and not p.name.startswith("_")):
                    continue
                try:
                    rel = str(p.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
                except ValueError:
                    rel = str(p).replace("\\", "/")
                if rel.endswith(".log"):
                    continue
                sha = _sha256_file(p)
                if sha:
                    artifact_refs.append(rel)
                    artifact_sha[rel] = sha

        wall_clock_s = time.time() - self._wall_start
        terminal_class = "ok" if not self._failed_stages else (
            "partial" if self._subprocess_exit_code == 0 else "fail"
        )

        l2 = L2ExecutionReceipt(
            run_id=self.run_id,
            request_id=self.request_id,
            trace_root=self.trace_root,
            l2_receipt_id=self._l2_receipt_id,
            route_contract_id=self._route_contract_id,
            terminal_class=terminal_class,  # type: ignore[arg-type]
            attempt_count=1,
            repair_count=0,
            output_artifact_refs=artifact_refs,
            pipeline_stages_executed=list(self._stage_outcomes.keys()),
            wall_clock_s=wall_clock_s,
        )
        self._staging["l2_execution_receipt"] = l2.model_dump()

        x3 = self._compute_x3()
        exit_pkt = ExitReviewPacket(
            run_id=self.run_id,
            request_id=self.request_id,
            trace_root=self.trace_root,
            exit_review_packet_id=self._exit_packet_id,
            route_contract_id=self._route_contract_id,
            x3_disposition=x3,
            disposition_reason=self._x3_reason(x3),
            subprocess_exit_code=self._subprocess_exit_code if self._subprocess_exit_code is not None else 0,
            failed_stages=list(self._failed_stages),
            sealed=True,
        )
        self._staging["exit_review_packet"] = exit_pkt.model_dump()

        # L6 exhaust observed AFTER exit (per spec)
        observed_at = _utc_iso(time.time())
        exhaust = RuntimeExhaustBundle(
            run_id=self.run_id,
            request_id=self.request_id,
            trace_root=self.trace_root,
            runtime_exhaust_bundle_id=self._exhaust_id,
            exit_review_packet_id=self._exit_packet_id,
            observed_after_exit_at_utc=observed_at,
            artifact_refs=artifact_refs,
            artifact_sha256_map=artifact_sha,
            metric_summary={
                "artifact_count": len(artifact_refs),
                "wall_clock_s": round(wall_clock_s, 2),
                "stage_count": len(self._stage_outcomes),
                "failed_stage_count": len(self._failed_stages),
            },
            sealed=True,
        )
        self._staging["runtime_exhaust_bundle"] = exhaust.model_dump()

        # Seal OTEL trace
        trace = self._tracer.seal()
        self._staging["otel_runtime_trace"] = trace.model_dump()

        # Persist all 7 + the trace to the real run dir
        for key, payload in self._staging.items():
            _write_json(run_dir / f"{key}.json", payload)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _user_intent(self) -> str:
        bits = []
        if self.target_role:
            bits.append(f"role={self.target_role}")
        if self.target_company:
            bits.append(f"company={self.target_company}")
        return "Generate tailored resume" + (f" ({', '.join(bits)})" if bits else "")

    def _read_route_registry(self) -> dict[str, Any]:
        if not ROUTE_REGISTRY_PATH.exists():
            raise RuntimeError(
                f"apps_rg route registry missing: {ROUTE_REGISTRY_PATH}. "
                "Cannot emit governance receipts without a registered route."
            )
        return yaml.safe_load(ROUTE_REGISTRY_PATH.read_text(encoding="utf-8"))

    def _select_route(self, registry: dict[str, Any]) -> dict[str, Any]:
        routes = registry.get("routes") or []
        if not routes:
            raise RuntimeError("route_registry.yaml has no routes defined")
        # Single-route registry today; future routes selected by capability match.
        return dict(routes[0])

    def _compute_x3(self) -> str:
        if self._subprocess_exit_code in (None, 0) and not self._failed_stages:
            return "EXIT_OK"
        if self._subprocess_exit_code == 0 and self._failed_stages:
            return "EXIT_PARTIAL"
        return "EXIT_FAIL"

    def _x3_reason(self, x3: str) -> str:
        if x3 == "EXIT_OK":
            return f"Subprocess exit=0 and all {len(self._stage_outcomes)} stages reported ok."
        if x3 == "EXIT_PARTIAL":
            return f"Subprocess exit=0 but {len(self._failed_stages)} stage(s) reported non-ok: {self._failed_stages}"
        return f"Subprocess exit={self._subprocess_exit_code}, failed stages: {self._failed_stages}"


@contextmanager
def governed_run(
    *,
    target_company: str | None,
    target_role: str | None,
    cli_args: list[str],
) -> Iterator[GovernedRun]:
    """Wrap the apps_rg pipeline in a real spine envelope.

    On exit (success or exception), receipts are sealed and written to
    the run dir. If the run dir is unknown (early failure), receipts are
    not written — the failure itself is honest evidence and a stub
    bundle would be misleading.
    """
    gr = GovernedRun(
        target_company=target_company,
        target_role=target_role,
        cli_args=cli_args,
    )
    gr.emit_pre_execution_contracts()
    exception_caught = False
    try:
        yield gr
    except Exception:
        exception_caught = True
        gr.mark_stage("entrypoint_exception", "fail")
        if gr._subprocess_exit_code is None:
            gr.set_subprocess_exit_code(1)
        raise
    finally:
        if gr._run_dir is not None:
            gr.emit_post_execution_contracts(gr._run_dir)
        elif exception_caught:
            # Nothing to seal into — leave a trail in the cert dir.
            fallback = REPO_ROOT / "artifacts" / "apps_rg" / "runs" / "_no_run_dir_resolved"
            fallback.mkdir(parents=True, exist_ok=True)
            gr.emit_post_execution_contracts(fallback)
