"""ManagedWorkflowRunner — W5 generic L3 orchestration runner.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W5

Consumes a RouteContract with execution_form=MANAGED_WORKFLOW, resolves the
workflow manifest, topologically orders nodes, emits one L3ToL2StepContract per
node, calls an injected L2 executor, collects SealedSectionArtifact outputs, and
returns a SealedWorkflowPackage via SectionMergeEngine.

Scope invariants (non-negotiable):
  - Does NOT call models, providers, or tools.
  - Does NOT retrieve evidence.
  - Does NOT assemble prompts.
  - Does NOT write L4.
  - Does NOT emit X3.
  - Does NOT import apps_rg.integrations.hops or gates.
  - Does NOT hardcode resume section names in generic logic.
  - Does NOT hardcode provider names in generic logic.
  - Does NOT silently fall back to SINGLE_STEP on any error.
  - route_registry.yaml status remains registered_not_active in production;
    this runner operates only in test-enabled mode (W5 scope).
"""
from __future__ import annotations

import hashlib
import json
import logging
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

from agentic_core.runtime.contracts.l3_to_l2_step_contract import L3ToL2StepContract
from agentic_core.runtime.contracts.sealed_workflow_types import (
    SealedSectionArtifact,
    SealedWorkflowPackage,
)
from agentic_core.L3_orchestration.section_merge_engine import (
    NodeDescriptor,
    SectionMergeEngine,
    SectionMergeError,
)
from agentic_core.prompt_governance.managed_workflow_pa_resolver import (
    ManagedWorkflowPAResolver,
)

_log = logging.getLogger(__name__)

_EXECUTION_FORM_MANAGED = "MANAGED_WORKFLOW"

# Runtime gate ref placeholder — emitted when harness is not wired
_GATE_REF_UNKNOWN = "GATE_REF::UNKNOWN::NOT_EVALUATED"


# ── Public exception ─────────────────────────────────────────────────────────

class ManagedWorkflowRunnerError(Exception):
    """Raised by ManagedWorkflowRunner on any fail-closed path."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"ManagedWorkflowRunnerError: {reason}")


# ── Manifest helpers ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class _ResolvedNode:
    node_id: str
    node_type: str
    depends_on: tuple[str, ...]
    optional: bool
    node_order: int  # topo order assigned at resolution time


def _load_manifest_yaml(manifest_path: Path) -> Dict[str, Any]:
    try:
        import yaml  # type: ignore[import-untyped]
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        raise ManagedWorkflowRunnerError(
            f"Failed to parse workflow manifest {manifest_path}: {exc}"
        ) from exc


def _resolve_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def _compute_digest(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _topological_sort(nodes: List[Dict[str, Any]]) -> List[_ResolvedNode]:
    """Kahn's algorithm for topological ordering. Raises on cycle."""
    node_map: Dict[str, Dict[str, Any]] = {n["node_id"]: n for n in nodes}
    in_degree: Dict[str, int] = defaultdict(int)
    adj: Dict[str, List[str]] = defaultdict(list)

    for n in nodes:
        nid = n["node_id"]
        deps = n.get("depends_on") or []
        for dep in deps:
            adj[dep].append(nid)
            in_degree[nid] += 1

    queue: deque[str] = deque(
        nid for nid in node_map if in_degree[nid] == 0
    )
    order: List[str] = []
    while queue:
        nid = queue.popleft()
        order.append(nid)
        for successor in adj[nid]:
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                queue.append(successor)

    if len(order) != len(node_map):
        remaining = [nid for nid in node_map if nid not in order]
        raise ManagedWorkflowRunnerError(
            f"Cycle detected in workflow DAG — nodes involved: {remaining}. "
            "Cyclic dependencies fail closed."
        )

    result: List[_ResolvedNode] = []
    for idx, nid in enumerate(order):
        raw = node_map[nid]
        result.append(
            _ResolvedNode(
                node_id=nid,
                node_type=raw.get("node_type", ""),
                depends_on=tuple(raw.get("depends_on") or []),
                optional=bool(raw.get("optional", False)),
                node_order=idx,
            )
        )
    return result


# ── Stage receipt writer ──────────────────────────────────────────────────────

class _StageReceiptWriter:
    """Writes deterministic JSON receipts to *output_dir* when provided."""

    def __init__(self, output_dir: Optional[Path]) -> None:
        self._dir = output_dir

    def write(self, filename: str, payload: Dict[str, Any]) -> Optional[Path]:
        if self._dir is None:
            return None
        self._dir.mkdir(parents=True, exist_ok=True)
        target = self._dir / filename
        target.write_text(
            json.dumps(payload, indent=2, default=str), encoding="utf-8"
        )
        _log.debug("[runner] stage receipt written: %s", target)
        return target


# ── Runner ────────────────────────────────────────────────────────────────────

class ManagedWorkflowRunner:
    """Generic L3 orchestration runner for MANAGED_WORKFLOW routes.

    Usage (test-enabled mode only in W5):

        executor = lambda step: SealedSectionArtifact(node_id=step.node_id, ...)
        runner = ManagedWorkflowRunner(l2_executor=executor)
        package = runner.run(route_contract, output_dir=tmp_path)

    The *l2_executor* callable receives an L3ToL2StepContract and must return a
    SealedSectionArtifact. In W5 tests this is a stub; in future waves a real
    L2 binding will be injected.
    """

    # Injected executor type: (L3ToL2StepContract) -> SealedSectionArtifact
    _L2ExecutorType = Callable[[L3ToL2StepContract], SealedSectionArtifact]

    def __init__(
        self,
        l2_executor: "_L2ExecutorType",
        *,
        repo_root: Optional[Path] = None,
        pa_resolver: Optional["ManagedWorkflowPAResolver"] = None,
    ) -> None:
        self._executor = l2_executor
        self._repo_root = repo_root or _resolve_repo_root()
        self._merge_engine = SectionMergeEngine()
        self._pa_resolver = pa_resolver

    def run(
        self,
        route_contract: Any,
        *,
        output_dir: Optional[Path] = None,
    ) -> SealedWorkflowPackage:
        """Orchestrate a single managed workflow run.

        Args:
            route_contract: RouteContract with execution_form=MANAGED_WORKFLOW.
            output_dir: if provided, stage receipts are written here.

        Returns:
            SealedWorkflowPackage assembled from all node outputs.

        Raises:
            ManagedWorkflowRunnerError: on any fail-closed path.
        """
        receipts = _StageReceiptWriter(output_dir)
        run_id = getattr(route_contract, "run_id", "") or uuid.uuid4().hex[:16]
        trace_root = getattr(route_contract, "trace_id", "") or run_id

        # ── 1. Validate execution_form ────────────────────────────────────
        execution_form = getattr(route_contract, "execution_form", "")
        if execution_form.upper() != _EXECUTION_FORM_MANAGED:
            raise ManagedWorkflowRunnerError(
                f"ManagedWorkflowRunner requires execution_form={_EXECUTION_FORM_MANAGED!r}, "
                f"got {execution_form!r}. Non-managed routes must not reach L3 runner."
            )

        # ── 2. Validate workflow_ref ──────────────────────────────────────
        workflow_ref = getattr(route_contract, "workflow_ref", "")
        if not workflow_ref:
            raise ManagedWorkflowRunnerError(
                "workflow_ref is empty — RouteContract must carry a resolved "
                "workflow_ref before L3 runner is invoked."
            )

        workflow_manifest_ref = getattr(route_contract, "workflow_manifest_ref", "")
        route_contract_ref = getattr(route_contract, "request_id", "") or ""

        # ── 3. Resolve manifest from registry receipt ─────────────────────
        manifest_path, manifest_data, manifest_digest = (
            self._resolve_manifest(route_contract, workflow_ref, workflow_manifest_ref)
        )

        receipts.write(
            "06_L3_workflow_manifest_resolved.json",
            {
                "workflow_ref": workflow_ref,
                "workflow_manifest_ref": workflow_manifest_ref,
                "manifest_path": str(manifest_path) if manifest_path else "",
                "manifest_digest": manifest_digest,
                "node_count": len(manifest_data.get("nodes") or []),
                "resolved_at": datetime.now(tz=timezone.utc).isoformat(),
            },
        )

        # ── 4. Topological sort of nodes ──────────────────────────────────
        raw_nodes: List[Dict[str, Any]] = manifest_data.get("nodes") or []
        if not raw_nodes:
            raise ManagedWorkflowRunnerError(
                f"Workflow manifest for {workflow_ref!r} contains no nodes."
            )

        try:
            ordered_nodes = _topological_sort(raw_nodes)
        except ManagedWorkflowRunnerError:
            raise
        except Exception as exc:
            raise ManagedWorkflowRunnerError(
                f"DAG topological sort failed for {workflow_ref!r}: {exc}"
            ) from exc

        # ── 5. Execute nodes in topological order ─────────────────────────
        completed_artifacts: Dict[str, SealedSectionArtifact] = {}
        failed_nodes: list[str] = []

        for resolved_node in ordered_nodes:
            step = self._build_step_contract(
                resolved_node=resolved_node,
                route_contract=route_contract,
                workflow_ref=workflow_ref,
                workflow_manifest_ref=workflow_manifest_ref,
                run_id=run_id,
                trace_root=trace_root,
                completed_artifacts=completed_artifacts,
            )

            receipts.write(
                f"07_L3_to_L2_step_contract_{resolved_node.node_id}.json",
                step.as_dict(),
            )

            try:
                artifact = self._executor(step)
            except Exception as exc:
                if not resolved_node.optional:
                    raise ManagedWorkflowRunnerError(
                        f"L2 executor failed on critical node={resolved_node.node_id!r}: {exc}. "
                        "Critical node failure fails closed."
                    ) from exc
                _log.warning(
                    "[runner] optional node=%r executor failed (skipped): %s",
                    resolved_node.node_id,
                    exc,
                )
                failed_nodes.append(resolved_node.node_id)
                continue

            # Stamp artifact with consistent fields if executor returned minimal stub
            artifact = self._stamp_artifact(
                artifact,
                node_id=resolved_node.node_id,
                workflow_ref=workflow_ref,
                run_id=run_id,
                trace_root=trace_root,
                node_order=resolved_node.node_order,
            )

            completed_artifacts[resolved_node.node_id] = artifact

            receipts.write(
                f"12_L2_sealed_section_{resolved_node.node_id}.json",
                artifact.as_dict(),
            )

        # ── 6. Merge into SealedWorkflowPackage ───────────────────────────
        manifest_node_descriptors = [
            NodeDescriptor(
                node_id=n.node_id,
                optional=n.optional,
                node_order=n.node_order,
            )
            for n in ordered_nodes
        ]

        # Runtime gate refs: UNKNOWN when harness not wired
        gate_refs = getattr(route_contract, "route_gate_refs", ())
        if not gate_refs:
            gate_refs = (_GATE_REF_UNKNOWN,)

        try:
            package = self._merge_engine.merge(
                workflow_ref=workflow_ref,
                workflow_manifest_ref=workflow_manifest_ref,
                run_id=run_id,
                route_contract_ref=route_contract_ref,
                manifest_nodes=manifest_node_descriptors,
                artifacts=list(completed_artifacts.values()),
                merge_strategy_ref=str(
                    manifest_data.get("merge_strategy", {}).get("policy", "")
                ),
                trace_root=trace_root,
                dependency_graph_ref=json.dumps(
                    {n.node_id: list(n.depends_on) for n in ordered_nodes},
                    separators=(",", ":"),
                ),
                runtime_gate_refs=tuple(gate_refs),
            )
        except SectionMergeError as exc:
            raise ManagedWorkflowRunnerError(
                f"Section merge failed: {exc.reason}"
            ) from exc

        # Stamp failed nodes into package if any (rebuild with frozen dataclass)
        if failed_nodes:
            package = SealedWorkflowPackage(
                **{
                    **package.as_dict(),
                    "failed_node_refs": tuple(failed_nodes),
                    "sealed_sections": package.sealed_sections,
                }
            )

        receipts.write(
            "13_L3_sealed_workflow_package.json",
            package.as_dict(),
        )

        _log.info(
            "[runner] DONE workflow_ref=%r run_id=%r nodes=%d failed=%d digest=%s",
            workflow_ref,
            run_id,
            len(completed_artifacts),
            len(failed_nodes),
            package.merged_payload_digest[:16],
        )
        return package

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _resolve_manifest(
        self,
        route_contract: Any,
        workflow_ref: str,
        workflow_manifest_ref: str,
    ) -> tuple[Optional[Path], Dict[str, Any], str]:
        """Load manifest YAML from route_contract receipt or by convention."""
        registry_receipt_json = getattr(
            route_contract, "registry_resolution_receipt_ref", ""
        )
        manifest_path: Optional[Path] = None
        manifest_digest = ""

        if registry_receipt_json:
            try:
                receipt_data = json.loads(registry_receipt_json)
                wmp = receipt_data.get("workflow_manifest_path", "")
                if wmp:
                    manifest_path = self._repo_root / wmp
                    manifest_digest = receipt_data.get("manifest_digest", "")
            except (json.JSONDecodeError, TypeError):
                pass

        if manifest_path is None or not manifest_path.exists():
            raise ManagedWorkflowRunnerError(
                f"Cannot locate workflow manifest for workflow_ref={workflow_ref!r}. "
                "registry_resolution_receipt_ref must carry a valid workflow_manifest_path."
            )

        # Recompute digest and verify if receipt had one
        actual_digest = _compute_digest(manifest_path)
        if manifest_digest and actual_digest != manifest_digest:
            raise ManagedWorkflowRunnerError(
                f"Manifest digest mismatch for {manifest_path.name!r}: "
                f"receipt={manifest_digest[:16]}… actual={actual_digest[:16]}…"
            )

        manifest_data = _load_manifest_yaml(manifest_path)
        return manifest_path, manifest_data, actual_digest

    def _build_step_contract(
        self,
        *,
        resolved_node: _ResolvedNode,
        route_contract: Any,
        workflow_ref: str,
        workflow_manifest_ref: str,
        run_id: str,
        trace_root: str,
        completed_artifacts: Dict[str, SealedSectionArtifact],
    ) -> L3ToL2StepContract:
        dependency_refs = tuple(
            completed_artifacts[dep].artifact_id or dep
            for dep in resolved_node.depends_on
            if dep in completed_artifacts
        )
        step_input_refs = tuple(
            completed_artifacts[dep].payload_ref or completed_artifacts[dep].artifact_id or dep
            for dep in resolved_node.depends_on
            if dep in completed_artifacts
        )
        contract_id = (
            f"l3l2::{workflow_ref}::{resolved_node.node_id}::{uuid.uuid4().hex[:8]}"
        )
        replay_key = getattr(route_contract, "replay_key", "") or ""

        # ── W7: Resolve prompt artifact via injected PA resolver ──────────
        prompt_artifact_ref = ""
        prompt_artifact_digest = ""
        prompt_bom_ref = ""
        prompt_registry_ref = ""
        section_prompt_ref = ""
        authority_order: tuple[str, ...] = ()
        pa_is_valid = True
        pa_failure_reason = ""
        carried_prompt_refs: tuple[str, ...] = ()

        if self._pa_resolver is not None:
            prompt_profile_ref = getattr(route_contract, "prompt_profile_ref", "") or ""
            try:
                pa_artifact = self._pa_resolver.resolve(
                    prompt_profile_ref=prompt_profile_ref,
                    node_id=resolved_node.node_id,
                    workflow_ref=workflow_ref,
                    run_id=run_id,
                    trace_root=trace_root,
                    request_id=getattr(route_contract, "request_id", "") or "",
                    replay_key=replay_key,
                )
                prompt_artifact_ref = pa_artifact.as_prompt_ref()
                prompt_artifact_digest = pa_artifact.prompt_digest
                prompt_bom_ref = pa_artifact.prompt_bom_ref
                prompt_registry_ref = pa_artifact.prompt_registry_ref
                section_prompt_ref = pa_artifact.section_prompt_ref
                authority_order = pa_artifact.authority_order
                pa_is_valid = pa_artifact.is_valid
                pa_failure_reason = pa_artifact.failure_reason
                if prompt_artifact_ref:
                    carried_prompt_refs = (prompt_artifact_ref,)
            except Exception as exc:
                _log.warning(
                    "[runner] PA resolver raised for node=%s: %s",
                    resolved_node.node_id, exc,
                )
                pa_is_valid = False
                pa_failure_reason = str(exc)

        return L3ToL2StepContract(
            contract_id=contract_id,
            route_contract_ref=getattr(route_contract, "request_id", "") or "",
            workflow_ref=workflow_ref,
            workflow_manifest_ref=workflow_manifest_ref,
            workflow_id=workflow_ref,
            node_id=resolved_node.node_id,
            node_type=resolved_node.node_type,
            node_attempt=1,
            parent_node_refs=resolved_node.depends_on,
            dependency_refs=dependency_refs,
            step_input_refs=step_input_refs,
            carried_prompt_refs=carried_prompt_refs,
            run_id=run_id,
            trace_root=trace_root,
            runtime_gate_refs=(_GATE_REF_UNKNOWN,),
            replay_key=replay_key,
            prompt_artifact_ref=prompt_artifact_ref,
            prompt_artifact_digest=prompt_artifact_digest,
            prompt_bom_ref=prompt_bom_ref,
            prompt_registry_ref=prompt_registry_ref,
            section_prompt_ref=section_prompt_ref,
            authority_order=authority_order,
            pa_is_valid=pa_is_valid,
            pa_failure_reason=pa_failure_reason,
        )

    @staticmethod
    def _stamp_artifact(
        artifact: SealedSectionArtifact,
        *,
        node_id: str,
        workflow_ref: str,
        run_id: str,
        trace_root: str,
        node_order: int,
    ) -> SealedSectionArtifact:
        """Return artifact with identity fields ensured, preserving all other fields."""
        artifact_id = artifact.artifact_id or (
            f"ssa::{workflow_ref}::{node_id}::{uuid.uuid4().hex[:8]}"
        )
        content = artifact.sealed_content or artifact.payload_ref or ""
        content_digest = (
            artifact.content_digest
            or artifact.payload_digest
            or hashlib.sha256(content.encode()).hexdigest()
        )
        sealed_at = (
            artifact.sealed_at or datetime.now(tz=timezone.utc).isoformat()
        )
        # SealedSectionArtifact is frozen — reconstruct with overrides
        return SealedSectionArtifact(
            artifact_id=artifact_id,
            workflow_ref=artifact.workflow_ref or workflow_ref,
            node_id=artifact.node_id or node_id,
            run_id=artifact.run_id or run_id,
            app_context=artifact.app_context,
            sealed_content=artifact.sealed_content,
            content_digest=content_digest,
            payload_ref=artifact.payload_ref,
            payload_digest=artifact.payload_digest or content_digest,
            output_schema_ref=artifact.output_schema_ref,
            selected_candidate_id=artifact.selected_candidate_id,
            selection_receipt_ref=artifact.selection_receipt_ref,
            candidate_artifact_ref=artifact.candidate_artifact_ref,
            gate_result_refs=artifact.gate_result_refs,
            judge_result_refs=artifact.judge_result_refs,
            l2_trace_refs=artifact.l2_trace_refs,
            lane=artifact.lane,
            node_order=artifact.node_order if artifact.node_order else node_order,
            merge_order=artifact.merge_order if artifact.merge_order else node_order,
            trace_root=artifact.trace_root or trace_root,
            otel_span_ref=artifact.otel_span_ref,
            sealed_at=sealed_at,
            terminal_class=artifact.terminal_class or "success",
            decisive_reason=artifact.decisive_reason or "stub_executor",
        )


__all__ = ["ManagedWorkflowRunner", "ManagedWorkflowRunnerError"]
