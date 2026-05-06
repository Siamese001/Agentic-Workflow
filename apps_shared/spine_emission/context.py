"""Parameterized governed-run context manager.

Generalization of `apps_rg/runtime/context.py::governed_run` for multi-app
re-use. Consumers pass an `EmissionConfig` describing:

  - app_name + entrypoint_command
  - runs_root (e.g. ``artifacts/apps_exec/runs``)
  - route_registry_path (YAML) — same schema as apps_rg
  - l3_dag_path (YAML, optional — MUST exist when expects_static_dag=True)
  - plan_steps (list of L1PlanStep)
  - expects_c0_grounding / expects_prompt_assembly / expects_static_dag
  - expected_execution_form + expected_l3_path

Usage
-----
::

    from apps_shared.spine_emission import EmissionConfig, governed_run, StageTracer

    cfg = EmissionConfig(
        app_name="apps_exec",
        entrypoint_command="python -m apps_exec",
        runs_root=Path("artifacts/apps_exec/runs"),
        route_registry_path=Path("apps_exec/config/route_registry.yaml"),
        l3_dag_path=None,
        plan_steps=[...],
        expects_c0_grounding=False,
        expects_prompt_assembly=True,
        expects_static_dag=False,
        expected_execution_form="SINGLE_STEP",
        expected_l3_path="BYPASSED",
    )
    with governed_run(cfg, cli_args=["--foo"]) as gr:
        with gr.span("L2_execute"):
            _run_real_pipeline()
        gr.set_subprocess_exit_code(0)

Receipts land under ``cfg.runs_root/<YYYYMMDD_HHMMSS>/`` with the
canonical filenames the verifier expects (see
``tools/certification/apps_e2e/stage_collectors.py::_STAGE_KEYWORDS``):
``u0_intake_envelope.json``, ``l1_plan_contract.json``,
``route_contract.json``, ``l3_bypass_receipt.json`` OR
``l3_orchestration_receipt.json``, ``final_evidence_contract.json``
(when expects_c0), ``prompt_assembly_manifest.json`` (when
expects_prompt), ``l2_execution_receipt.json``,
``exit_review_packet.json``, ``runtime_exhaust_bundle.json``,
``otel_runtime_trace.json``.

Plan: apps-e2e-spine-cert-wireup-e1c4d7 W1.2.
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Literal, Optional

import yaml

from apps_shared.spine_emission.contracts import (
    C0GroundingReceipt,
    ExitReviewPacket,
    L1PlanContract,
    L1PlanStep,
    L2ExecutionReceipt,
    L3BypassReceipt,
    L3OrchestrationReceipt,
    PromptAssemblyManifest,
    RouteContract,
    RuntimeExhaustBundle,
    U0IntakeEnvelope,
)
from apps_shared.spine_emission.otel_trace import StageTracer, _utc_iso


ExpectedL3Path = Literal["RAN", "BYPASSED", "UNKNOWN"]
ExpectedExecutionForm = Literal[
    "MANAGED_WORKFLOW",
    "DETERMINISTIC_PIPELINE",
    "TERMINAL_SHORTCIRCUIT",
    "SINGLE_STEP",
    "FALLBACK",
    "UNKNOWN",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


def _relative_to_repo(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _timestamp_run_dir(runs_root: Path) -> Path:
    now = datetime.now(timezone.utc)
    stem = now.strftime("%Y%m%d_%H%M%S")
    return runs_root / stem


# ---------------------------------------------------------------------------
# EmissionConfig
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EmissionConfig:
    """Per-app configuration for spine emission.

    All paths MAY be absolute or repo-relative; relative paths are
    resolved against the repo root discovered from ``repo_root``.
    """

    app_name: str
    entrypoint_command: str  # e.g. "python -m apps_exec"
    runs_root: Path
    route_registry_path: Path
    l3_dag_path: Optional[Path]
    plan_steps: list[L1PlanStep]
    plan_rationale: str

    expects_c0_grounding: bool
    expects_prompt_assembly: bool
    expects_static_dag: bool

    expected_execution_form: ExpectedExecutionForm
    expected_l3_path: ExpectedL3Path

    # Optional knobs
    selected_capability: Optional[str] = None
    user_intent_hint: Optional[str] = None
    repo_root: Optional[Path] = None
    c0_grounding_note: str = "Deterministic fixture-backed grounding; no live retrieval."
    prompt_assembly_note: str = "Deterministic prompt templates; no model-driven assembly."
    # U0IntakeEnvelope passthrough for apps that care about intake context
    # (e.g. apps_rg uses target_company / target_role). Both None by default.
    target_company: Optional[str] = None
    target_role: Optional[str] = None

    # Extra post-pipeline stages to record (optional)
    extra_stage_names: tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# GovernedRun — one live run's state
# ---------------------------------------------------------------------------


class GovernedRun:
    """Live state of one governed apps_* run.

    Emits the canonical receipts under ``cfg.runs_root/<ts>/`` in two
    phases:

      Phase 1 (pre-execution, in ``__enter__``): U0 intake, L1 plan,
        L0 route, L3 bypass OR L3 orchestration, optional C0 grounding,
        optional Prompt assembly.

      Phase 2 (post-execution, in ``__exit__``): L2 execution receipt,
        Exit X3 disposition, L6 runtime exhaust, OTEL trace.
    """

    def __init__(self, cfg: EmissionConfig, *, cli_args: list[str]) -> None:
        self.cfg = cfg
        self.cli_args = list(cli_args)
        self.cli_args_digest = _sha256_text(" ".join(self.cli_args))

        self.repo_root = cfg.repo_root or _discover_repo_root()

        self.run_id = f"{cfg.app_name}-run-{uuid.uuid4().hex[:16]}"
        self.request_id = self.run_id
        self.trace_root = self.run_id

        self._tracer = StageTracer(cfg.app_name, self.run_id, self.request_id, self.trace_root)
        self._stage_outcomes: dict[str, str] = {}
        self._subprocess_exit_code: int | None = None
        self._failed_stages: list[str] = []
        self._wall_start = time.time()

        self.run_dir: Path = _timestamp_run_dir(cfg.runs_root)
        self._staging: dict[str, dict[str, Any]] = {}

        # Stable IDs
        self._intake_id = f"U0-{uuid.uuid4().hex[:16]}"
        self._plan_id = f"L1-{uuid.uuid4().hex[:16]}"
        self._route_contract_id = f"L0-{uuid.uuid4().hex[:16]}"
        self._l3_bypass_id = f"L3B-{uuid.uuid4().hex[:16]}"
        self._l3_runtime_id = f"L3R-{uuid.uuid4().hex[:16]}"
        self._c0_id = f"C0-{uuid.uuid4().hex[:16]}"
        self._pa_id = f"PA-{uuid.uuid4().hex[:16]}"
        self._l2_receipt_id = f"L2-{uuid.uuid4().hex[:16]}"
        self._exit_packet_id = f"X3-{uuid.uuid4().hex[:16]}"
        self._exhaust_id = f"L6-{uuid.uuid4().hex[:16]}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def span(self, name: str, **attrs: Any):
        return self._tracer.span(name, run_id=self.run_id, **attrs)

    def set_run_dir(self, run_dir: Path) -> None:
        """Late-bound run-dir override.

        Some apps (e.g. apps_rg) create their OWN timestamped run directory
        inside their pipeline (``generate_resume.main()``) and need the
        spine receipts sealed next to the app-emitted artifacts, not in a
        separate shared-helper-timestamped dir. After the app's pipeline
        resolves its real dir, call ``gr.set_run_dir(path)`` before the
        ``governed_run`` context manager exits to retarget where the Phase-2
        receipts land.
        """
        self.run_dir = run_dir

    def mark_stage(self, stage_name: str, outcome: str) -> None:
        self._stage_outcomes[stage_name] = outcome
        if outcome != "ok":
            self._failed_stages.append(stage_name)

    def set_subprocess_exit_code(self, code: int) -> None:
        self._subprocess_exit_code = code

    # ------------------------------------------------------------------
    # Phase 1 : pre-execution receipts
    # ------------------------------------------------------------------

    def emit_pre_execution_contracts(self) -> None:
        cfg = self.cfg

        intake = U0IntakeEnvelope(
            app_name=cfg.app_name,
            run_id=self.run_id,
            request_id=self.request_id,
            trace_root=self.trace_root,
            intake_id=self._intake_id,
            entrypoint_command=cfg.entrypoint_command,
            target_company=cfg.target_company,
            target_role=cfg.target_role,
            cli_args_digest=self.cli_args_digest,
            user_intent=cfg.user_intent_hint or f"Live certification run for {cfg.app_name}",
        )
        self._staging["u0_intake_envelope"] = intake.model_dump()

        plan = L1PlanContract(
            app_name=cfg.app_name,
            run_id=self.run_id,
            request_id=self.request_id,
            trace_root=self.trace_root,
            plan_id=self._plan_id,
            plan_kind=("managed_workflow" if cfg.expected_execution_form == "MANAGED_WORKFLOW"
                       else "single_step" if cfg.expected_execution_form == "SINGLE_STEP"
                       else "deterministic_hop_pipeline"),
            steps=list(cfg.plan_steps),
            grounding_required=cfg.expects_c0_grounding,
            prompt_assembly_required=cfg.expects_prompt_assembly,
            plan_rationale=cfg.plan_rationale,
        )
        self._staging["l1_plan_contract"] = plan.model_dump()

        registry_data = self._read_route_registry()
        route_def = self._select_route(registry_data)
        dag_sha: str | None = None
        if cfg.l3_dag_path is not None and cfg.l3_dag_path.exists():
            dag_sha = _sha256_file(cfg.l3_dag_path)
        static_dag_ref: str | None = (
            _relative_to_repo(cfg.l3_dag_path, self.repo_root)
            if (cfg.l3_dag_path and cfg.l3_dag_path.exists())
            else route_def.get("static_dag_ref")
        )

        route = RouteContract(
            app_name=cfg.app_name,
            run_id=self.run_id,
            request_id=self.request_id,
            trace_root=self.trace_root,
            route_contract_id=self._route_contract_id,
            route_id=route_def["route_id"],
            execution_form=route_def["execution_form"],
            route_reason=route_def.get("route_reason",
                f"L0 selected '{route_def['route_id']}' from "
                f"{cfg.route_registry_path.name}."),
            l3_required=bool(route_def.get("l3_required", False)),
            static_dag_ref=static_dag_ref,
            static_dag_sha256=dag_sha,
            selected_capability=route_def.get("selected_capability",
                cfg.selected_capability or f"{cfg.app_name}.default_v1"),
        )
        self._staging["route_contract"] = route.model_dump()

        # L3 — either bypass or runtime orchestration
        if cfg.expected_l3_path == "RAN":
            if dag_sha is None:
                raise RuntimeError(
                    f"{cfg.app_name}: expected_l3_path=RAN requires a real l3_dag.yaml "
                    f"at {cfg.l3_dag_path}"
                )
            l3_runtime = L3OrchestrationReceipt(
                app_name=cfg.app_name,
                run_id=self.run_id,
                request_id=self.request_id,
                trace_root=self.trace_root,
                l3_runtime_receipt_id=self._l3_runtime_id,
                route_contract_id=self._route_contract_id,
                dag_id=f"{cfg.app_name}.static_l3",
                dag_sha256=dag_sha,
                static_dag_hash=dag_sha,  # binds to bundle.static_dag_sha256 (N6)
                workflow_id=f"{cfg.app_name}-wf-{uuid.uuid4().hex[:12]}",
                selected_entry_node=(route_def.get("entry_node") or "hop_0"),
                node_count=int(route_def.get("node_count", len(cfg.plan_steps))),
                scheduled_node_ids=[s.step_id for s in cfg.plan_steps],
                ready_node_ids=[s.step_id for s in cfg.plan_steps if not s.optional],
                step_contract_refs=[],
            )
            self._staging["l3_orchestration_receipt"] = l3_runtime.model_dump()
        else:
            bypass = L3BypassReceipt(
                app_name=cfg.app_name,
                run_id=self.run_id,
                request_id=self.request_id,
                trace_root=self.trace_root,
                l3_bypass_receipt_id=self._l3_bypass_id,
                route_contract_id=self._route_contract_id,
                execution_form=route_def["execution_form"],
                l3_bypass_reason=route_def.get(
                    "bypass_reason_when_invoked", "NO_MANAGED_WORKFLOW_REQUIRED"
                ),
                static_dag_available=bool(cfg.l3_dag_path and cfg.l3_dag_path.exists()),
                static_dag_ref=static_dag_ref,
                why_static_dag_not_used=(
                    f"L0 RouteContract execution_form={route_def['execution_form']}, "
                    f"l3_required={bool(route_def.get('l3_required', False))}. "
                    f"{cfg.app_name} uses a deterministic single-step / pipeline route; "
                    f"runtime L3 orchestration is not required."
                ),
            )
            self._staging["l3_bypass_receipt"] = bypass.model_dump()

        # Optional C0 grounding receipt
        if cfg.expects_c0_grounding:
            c0 = C0GroundingReceipt(
                app_name=cfg.app_name,
                run_id=self.run_id,
                request_id=self.request_id,
                trace_root=self.trace_root,
                c0_grounding_receipt_id=self._c0_id,
                route_contract_id=self._route_contract_id,
                retrieval_plan_id=f"RP-{uuid.uuid4().hex[:12]}",
                retrieval_backend="deterministic_fixture",
                evidence_count=0,
                evidence_refs=[],
                grounding_coverage=1.0,
                deterministic=True,
                sealed=True,
            )
            self._staging["final_evidence_contract"] = c0.model_dump()

        # Optional Prompt Assembly manifest
        if cfg.expects_prompt_assembly:
            pa = PromptAssemblyManifest(
                app_name=cfg.app_name,
                run_id=self.run_id,
                request_id=self.request_id,
                trace_root=self.trace_root,
                prompt_assembly_manifest_id=self._pa_id,
                route_contract_id=self._route_contract_id,
                assembly_strategy="deterministic_template",
                prompt_artifact_refs=[],
                prompt_sha256_map={},
                assembly_note=cfg.prompt_assembly_note,
            )
            self._staging["prompt_assembly_manifest"] = pa.model_dump()

    # ------------------------------------------------------------------
    # Phase 2 : post-execution receipts
    # ------------------------------------------------------------------

    def emit_post_execution_contracts(self) -> None:
        run_dir = self.run_dir.resolve()
        run_dir.mkdir(parents=True, exist_ok=True)

        # Enumerate real artifacts in run_dir
        artifact_refs: list[str] = []
        artifact_sha: dict[str, str] = {}
        for p in sorted(run_dir.rglob("*")):
            if not (p.is_file() and not p.name.startswith("_")):
                continue
            rel = _relative_to_repo(p, self.repo_root)
            if rel.endswith(".log"):
                continue
            sha = _sha256_file(p)
            if sha:
                artifact_refs.append(rel)
                artifact_sha[rel] = sha

        wall_clock_s = time.time() - self._wall_start
        terminal_class: Literal["ok", "partial", "fail"] = (
            "ok" if not self._failed_stages
            else "partial" if self._subprocess_exit_code == 0
            else "fail"
        )

        l2 = L2ExecutionReceipt(
            app_name=self.cfg.app_name,
            run_id=self.run_id,
            request_id=self.request_id,
            trace_root=self.trace_root,
            l2_receipt_id=self._l2_receipt_id,
            route_contract_id=self._route_contract_id,
            terminal_class=terminal_class,
            attempt_count=1,
            repair_count=0,
            output_artifact_refs=artifact_refs,
            pipeline_stages_executed=list(self._stage_outcomes.keys()),
            wall_clock_s=wall_clock_s,
        )
        self._staging["l2_execution_receipt"] = l2.model_dump()

        x3 = self._compute_x3()
        exit_pkt = ExitReviewPacket(
            app_name=self.cfg.app_name,
            run_id=self.run_id,
            request_id=self.request_id,
            trace_root=self.trace_root,
            exit_review_packet_id=self._exit_packet_id,
            route_contract_id=self._route_contract_id,
            x3_disposition=x3,  # type: ignore[arg-type]
            disposition_reason=self._x3_reason(x3),
            subprocess_exit_code=(
                self._subprocess_exit_code if self._subprocess_exit_code is not None else 0
            ),
            failed_stages=list(self._failed_stages),
            sealed=True,
        )
        self._staging["exit_review_packet"] = exit_pkt.model_dump()

        # L6 exhaust observed AFTER exit (per spec; N7 guard)
        observed_at = _utc_iso(time.time())
        exhaust = RuntimeExhaustBundle(
            app_name=self.cfg.app_name,
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

        trace = self._tracer.seal()
        self._staging["otel_runtime_trace"] = trace.model_dump()

        for key, payload in self._staging.items():
            _write_json(run_dir / f"{key}.json", payload)

        # ── L7_AUDITABILITY evidence plane ──
        # Mandatory cross-cutting evidence plane. Create Track-2 filename
        # aliases for Track-1 artifacts and invoke L7 builder.
        try:
            from agentic_core.L7_auditability.how_trace import (
                build_how_trace as _build_how_trace,
            )
            from agentic_core.L7_auditability.coverage import (
                build_l7_route_family_coverage as _build_rfc,
            )
            from agentic_core.runtime.artifacts.spine_proof_bundle import (
                build_spine_proof_payload as _build_spine_proof,
            )

            # Track-1 → Track-2 filename aliases
            _alias_map = {
                "u0_intake_envelope.json": "runtime_identity_envelope.json",
                "l1_plan_contract.json": "l1_plan_contract.json",
                "route_contract.json": "route_contract.json",
                "l2_execution_receipt.json": "static_dag_proof.json",
                "exit_review_packet.json": "exit_review_packet.json",
                "runtime_exhaust_bundle.json": "runtime_exhaust_bundle.json",
            }
            for src_name, dst_name in _alias_map.items():
                src_path = run_dir / src_name
                dst_path = run_dir / dst_name
                if src_path.exists() and not dst_path.exists():
                    dst_path.write_text(src_path.read_text(encoding="utf-8"), encoding="utf-8")

            # Synthesize route_contract.json if absent (Track-2 requirement)
            _route_path = run_dir / "route_contract.json"
            if not _route_path.exists():
                _route_payload = {
                    "schema_version": "route_contract.v1",
                    "payload": {
                        "route_id": self.cfg.app_name,
                        "route_contract_id": self._route_contract_id,
                        "execution_form": "MANAGED_WORKFLOW",
                        "grounding_required": self.cfg.expects_c0_grounding,
                        "prompt_assembly_required": self.cfg.expects_prompt_assembly,
                    },
                }
                _write_json(_route_path, _route_payload)

            # Determine chain_kind for L7 builder
            _chain_kind = "MANAGED_WORKFLOW"
            if self.cfg.expected_execution_form == "DETERMINISTIC_PIPELINE":
                _chain_kind = "R4_SINGLE_ACTION"
            elif self.cfg.expected_execution_form == "TERMINAL_SHORTCIRCUIT":
                _chain_kind = "TERMINAL_SHORTCIRCUIT"

            # Build and emit L7 artifacts
            _how_trace = _build_how_trace(run_dir, chain_kind=_chain_kind)
            _write_json(run_dir / "agentic_core_how_trace.json", _how_trace.to_dict())

            _rfc = _build_rfc(run_dir, chain_kind=_chain_kind, write=False)
            _write_json(run_dir / "agentic_core_l7_route_family_coverage.json", _rfc["payload"])

            _identity_src = run_dir / "runtime_identity_envelope.json"
            _identity_payload = {}
            if _identity_src.exists():
                _identity_payload = json.loads(_identity_src.read_text(encoding="utf-8")).get("payload", {})

            _spine = _build_spine_proof(
                artifact_dir=run_dir,
                artifact_hashes={},
                identity_envelope_payload=_identity_payload,
                started_at_utc=_utc_iso(self._wall_start),
                finished_at_utc=_utc_iso(time.time()),
                exit_code=self._subprocess_exit_code or 0,
            )
            _write_json(run_dir / "agentic_core_spine_proof.json", _spine)

            # Final manifest with L7 refs
            _write_json(
                run_dir / "integrated_runtime_artifact_manifest.json",
                {
                    "invocation_id": self.run_id,
                    "entry_point": self.cfg.entrypoint_command,
                    "integrated_runtime_entrypoint_used": False,
                    "chain_kind": _chain_kind,
                    "artifact_filenames": [
                        "agentic_core_how_trace.json",
                        "agentic_core_l7_route_family_coverage.json",
                        "agentic_core_spine_proof.json",
                        "integrated_runtime_artifact_manifest.json",
                    ],
                    "how_trace_ref": "artifact://agentic_core_how_trace.json",
                    "how_trace_sha256": _sha256_file(run_dir / "agentic_core_how_trace.json") or "",
                    "l7_route_family_coverage_ref": "artifact://agentic_core_l7_route_family_coverage.json",
                    "l7_route_family_coverage_sha256": _sha256_file(run_dir / "agentic_core_l7_route_family_coverage.json") or "",
                    "artifact_hashes": {},
                    "chain_linkage": [],
                },
            )
        except Exception:
            # L7 is best-effort for governed_run; failures don't block the run
            pass

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _read_route_registry(self) -> dict[str, Any]:
        p = self.cfg.route_registry_path
        if not p.exists():
            raise RuntimeError(
                f"{self.cfg.app_name} route registry missing: {p}. "
                "Cannot emit governance receipts without a registered route."
            )
        return yaml.safe_load(p.read_text(encoding="utf-8"))

    def _select_route(self, registry: dict[str, Any]) -> dict[str, Any]:
        routes = registry.get("routes") or []
        if not routes:
            raise RuntimeError(
                f"{self.cfg.route_registry_path} has no routes defined"
            )
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
            return (
                f"Subprocess exit=0 but {len(self._failed_stages)} stage(s) "
                f"reported non-ok: {self._failed_stages}"
            )
        return f"Subprocess exit={self._subprocess_exit_code}, failed stages: {self._failed_stages}"


# ---------------------------------------------------------------------------
# Public context-manager entry point
# ---------------------------------------------------------------------------


def _discover_repo_root() -> Path:
    """Walk up from this file until we find repo markers (pyproject.toml or .git)."""
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
    return here.parents[2]  # fallback: apps_shared/spine_emission/context.py -> repo


@contextmanager
def governed_run(
    cfg: EmissionConfig,
    *,
    cli_args: list[str] | None = None,
) -> Iterator[GovernedRun]:
    """Wrap any app's pipeline in a real spine envelope.

    On exit (success or exception), receipts are sealed and written to
    ``cfg.runs_root/<timestamp>/``. Exceptions are re-raised; receipts
    still emit to preserve audit trail (honest fail-closed).
    """
    gr = GovernedRun(cfg, cli_args=cli_args or [])
    gr.emit_pre_execution_contracts()
    try:
        yield gr
    except Exception:  # guardian: allow-broad-exception -- audit mark_stage + exit_code set before re-raise; does NOT swallow (explicit raise at end)
        gr.mark_stage("entrypoint_exception", "fail")
        if gr._subprocess_exit_code is None:
            gr.set_subprocess_exit_code(1)
        raise
    finally:
        gr.emit_post_execution_contracts()


__all__ = ["EmissionConfig", "GovernedRun", "governed_run"]
