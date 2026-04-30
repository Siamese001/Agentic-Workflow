"""
L0→L2 Execution Orchestrator - Deterministic Layer Binding

Binds Assembly Stage, PathRouter, D0InjectionEngine, ConfCalibRiskGate,
CIDRegistry, ReEntryLoop, MetaLearningBus, and VigilanceDispatcher.
Remains deterministic, side-effect minimal, uses injected seams only.
"""

import hashlib
import json
import logging
from typing import Any

from agentic_core.L0_routing.enforcement.routing_contract import (
    ProposalCommitter,
    RoutingContext,
    RoutingContractError,
    create_and_commit_routing_contract,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    emit_determinism_digest,
    emit_replay_key,
)

Logger = logging.getLogger(__name__)


def _get_active_trace():
    from agentic_core.runtime.types.execution_trace import get_active_execution_trace  # noqa: PLC0415

    return get_active_execution_trace()


def _stable_request_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def _semantic_cache_enabled() -> bool:
    import os as _os  # noqa: PLC0415

    return _os.environ.get("SEMANTIC_CACHE_D2_ENABLED", "0").strip().lower() in {"1", "true", "yes"}


def _semantic_cache_promote_enabled() -> bool:
    import os as _os  # noqa: PLC0415

    return _os.environ.get("SEMANTIC_CACHE_PROMOTE_ENABLED", "0").strip().lower() in {"1", "true", "yes"}


def _exact_cache_d1_enabled() -> bool:
    """R1A exact-cache writeback gate. Matches EXACT_CACHE_D1_ENABLED in route_gates."""
    import os as _os  # noqa: PLC0415

    return _os.environ.get("EXACT_CACHE_D1_ENABLED", "0").strip().lower() in {"1", "true", "yes"}


def _get_routing_gateway():
    from agentic_core.L0_routing.reasoning.deterministic_routing_gateway import (
        get_routing_gateway,  # noqa: PLC0415
    )

    return get_routing_gateway()


class ExecutionOrchestrator:
    """
    Deterministic execution orchestrator binding all layers.

    Uses injected seams only, no direct dependencies.
    No wall-clock usage, no side effects beyond injected functions.
    """

    _L3_PATHS: frozenset = frozenset({"B", "C", "D"})

    def __init__(
        self,
        assembler,
        path_router,
        d0_engine,
        risk_gate,
        cid_registry,
        reentry_loop,
        vigilance_dispatcher,
        meta_bus,
        l3_orchestrator=None,
    ):
        """
        Initialize orchestrator with injected dependencies.

        Args:
            assembler: Assembly Stage instance
            path_router: PathRouter instance
            d0_engine: D0InjectionEngine instance
            risk_gate: ConfCalibRiskGate instance
            cid_registry: CIDRegistry instance
            reentry_loop: ReEntryLoop instance
            vigilance_dispatcher: VigilanceDispatcher instance
            meta_bus: MetaLearningBus instance
            l3_orchestrator: Optional L3 orchestrator for Paths B/C/D delegation.
                Must implement orchestrate(payload, route_mode, trace_id, ...) or
                a compatible synchronous interface.  When None, Paths B/C/D return
                without delegation (backwards-compatible default).
        """
        self.assembler = assembler
        self.path_router = path_router
        self.d0_engine = d0_engine
        self.risk_gate = risk_gate
        self.cid_registry = cid_registry
        self.reentry_loop = reentry_loop
        self.vigilance_dispatcher = vigilance_dispatcher
        self.meta_bus = meta_bus
        self.l3_orchestrator = l3_orchestrator

    def _delegate_to_l3(self, path, payload, cycle, risk) -> dict[str, Any]:
        """
        Delegate execution to L3 orchestrator for Paths B/C/D.

        Calls l3_orchestrator.orchestrate() when available.  Any exception is
        caught and returned as an error key so L0 routing remains unaffected.

        Returns:
            Result dict including orchestration sub-result or error metadata.
        """
        orchestration: dict[str, Any] = {}
        if self.l3_orchestrator is not None:
            try:
                result = self.l3_orchestrator.orchestrate(
                    payload,
                    route_mode=path.value,
                    trace_id=cycle.cid,
                    policy_hash="",
                    allowed_tools=(),
                )
                _completed = result.completed if isinstance(result.completed, bool) else False  # type: ignore[union-attr]
                _stage = result.stage if isinstance(result.stage, str) else "unknown"  # type: ignore[union-attr]
                try:
                    _signals = list(result.signals)  # type: ignore[union-attr]
                except AttributeError:
                    _signals = []
                _metadata = result.metadata if isinstance(result.metadata, dict) else {}  # type: ignore[union-attr]
                orchestration = {
                    "completed": _completed,
                    "stage": _stage,
                    "signals": _signals,
                    "metadata": _metadata,
                }
            except (ValueError, KeyError, AttributeError, TypeError, RuntimeError) as e:
                orchestration = {"error": f"L3 orchestration failed: {e}", "completed": False}
            except OSError as e:  # guardian: allow-broad-exception -- raises after constructing error orchestration context for caller telemetry
                orchestration = {"error": f"Critical L3 orchestration error: {e}", "completed": False}
                raise
        return {
            "path": path,
            "risk": risk,
            "cycle": cycle,
            "state": "success",
            "orchestration": orchestration,
        }

    def execute(self, intent_input: dict[str, Any]) -> dict[str, Any]:
        """
        Execute intent through all layers deterministically.

        Flow (no hidden state):
        1) Assemble → payload
        2) Route → path
        3) Render D0
        4) Evaluate risk
        5) Start ExecutionCycle
        6) Handle re-entry if risk disallowed
        7) Delegate to L3 for Paths B/C/D (when l3_orchestrator injected)
        8) Return structured result dict

        Args:
            intent_input: Input intent dictionary

        Returns:
            Structured result dict with path, risk, cycle, and state
        """
        _active = _get_active_trace()
        _trace_id = (
            _active.trace_id
            if _active and getattr(_active, "trace_id", None)
            else "no-trace:ExecutionOrchestrator.execute"
        )
        _trace_sig = hashlib.sha256(_trace_id.encode()).hexdigest()[:12]
        _emit_signs_execution_trace(_trace_id, _trace_sig, "seg_sig", 0)
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "ExecutionOrchestrator.execute")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        # v11 R1A/R1B short-circuit — run BEFORE path selection so an exact or
        # semantic cache hit returns immediately without running the router,
        # D0, risk gate, or L3. Uses the same canonical keys as check_route_gates
        # so writeback (below) and this read match byte-for-byte.
        _tenant_id = intent_input.get("tenant_id", "")
        _flow_class = intent_input.get("flow_class", None)
        _replay_mode = bool(intent_input.get("replay_mode", False))
        _namespace = intent_input.get("namespace", "default")
        _corpus_version = intent_input.get("corpus_version", "") or ""
        _policy_version = intent_input.get("policy_version", "") or getattr(_active, "policy_hash", "") or ""
        try:
            from agentic_core.L0_routing.reasoning.route_gates import (  # noqa: PLC0415
                check_route_gates as _check_route_gates,
            )

            _gate_result = _check_route_gates(
                intent_input,
                namespace=_namespace,
                tenant_id=_tenant_id,
                replay_mode=_replay_mode,
                flow_class=_flow_class,
                policy_hash=getattr(_active, "policy_hash", "") or "no-policy",
                trace_id=_trace_id,
                corpus_version=_corpus_version,
                policy_version=_policy_version,
            )
        except (
            ImportError,
            RuntimeError,
            ValueError,
        ) as _ge:  # guardian: allow-log-and-swallow -- cache gate is opportunistic; miss is safe
            Logger.debug("[L0-ORCH] route_gates check skipped: %s", _ge)
            _gate_result = None
        if _gate_result is not None:
            _contract, _cached_payload = _gate_result
            _route_label = _contract["selected_route"].value  # "R1A" or "R1B"
            Logger.info("[L0-ORCH] cache short-circuit route=%s namespace=%s", _route_label, _namespace)
            return {
                "path": None,
                "state": "cache_hit",
                "selected_route": _route_label,
                "result": _cached_payload,
                "contract": _contract,
            }

        payload = self.assembler.assemble(intent_input)
        path = self.path_router.select_path(payload)
        _get_routing_gateway().stamp_decision(path.value)
        _rtid = _active.trace_id if _active else f"no-trace:orchestrate:{path.value}"
        _rctx = RoutingContext(
            run_id=_rtid,
            router_id="ExecutionOrchestrator",
            request_hash=_stable_request_hash(intent_input),
            candidate_routes=["A", "B", "C", "D"],
            chosen_route=path.value,
            policy_hash=getattr(_active, "policy_hash", "") or "no-policy",
            policy_version="1.0",
        )
        try:
            _committer = ProposalCommitter()
            create_and_commit_routing_contract(_rctx)
        except RoutingContractError as _rce:  # routing contract creation failure non-blocking
            Logger.error("execution_orchestrator: routing contract failed: %s", _rce)
            return {
                "path": path,
                "state": "routing_contract_error",
                "error": str(_rce),
            }
        d0_injections = self.d0_engine.render_d0(payload.d0_injections)
        risk = self.risk_gate.evaluate(payload_like=payload, d0_injections=d0_injections)
        cycle = self.cid_registry.new_cycle(f"execute_{path.value}")
        if not risk.allow:
            if self.reentry_loop.should_retry(cycle):
                cycle = self.reentry_loop.advance(cycle)
                return {"path": path, "risk": risk, "cycle": cycle, "state": "retry"}
            else:
                return {"path": path, "risk": risk, "cycle": cycle, "state": "blocked"}
        if path.value in self._L3_PATHS:
            _l3_result = self._delegate_to_l3(path, payload, cycle, risk)
            # R1A + R1B writeback on Path-D success. Keys are the canonical
            # forms used by check_route_gates so a subsequent identical call
            # hits the gate above and short-circuits before select_path.
            if (
                path.value == "D"
                and not _replay_mode
                and _l3_result.get("state") == "success"
                and isinstance(_l3_result.get("orchestration"), dict)
                and _l3_result["orchestration"].get("completed") is True
            ):
                from agentic_core.L0_routing.reasoning.route_gates import (  # noqa: PLC0415
                    canonical_request_hash as _canonical_request_hash,
                )

                # D2 key: canonical JSON string of the request (matches check_d2)
                _d2_context = json.dumps(intent_input, sort_keys=True, separators=(",", ":"), default=str)
                # D1 key: SHA-256 hash of canonical JSON (matches check_d1)
                _d1_key = _canonical_request_hash(intent_input)
                if _semantic_cache_enabled():
                    self._populate_d2_cache(
                        _d2_context,
                        _namespace,
                        _tenant_id,
                        _l3_result,
                        corpus_version=_corpus_version,
                        policy_version=_policy_version,
                    )
                # R1A — O(1) SHA-256 lookup, fires first on next call.
                self._populate_d1_cache(_d1_key, _l3_result)
            return _l3_result
        return {"path": path, "risk": risk, "cycle": cycle, "state": "success"}

    def _populate_d2_cache(
        self,
        payload_key: str,
        namespace: str,
        tenant_id: str,
        l3_result: dict[str, Any],
        *,
        corpus_version: str = "",
        policy_version: str = "",
    ) -> None:
        """Write L3-success result into the semantic cache (L1 always; L2 when gated feedback qualifies).

        Called only after a successful Path-D execution with ``completed=True`` orchestration.
        All failures are caught and debug-logged — caching is an optimization, never a hard dep.
        """
        try:
            from agentic_core.L4_state.utils.memory.semantic_cache_manager import (  # noqa: PLC0415
                CriticalInfrastructureError,
                SemanticCacheManager,
            )

            _mgr = SemanticCacheManager.get_instance()
            _orch = l3_result["orchestration"]
            _meta = _orch.get("metadata", {}) if isinstance(_orch.get("metadata"), dict) else {}
            _path_obj = l3_result.get("path")
            _path_val = _path_obj.value if _path_obj is not None and hasattr(_path_obj, "value") else "D"
            _learn_payload = {
                "path": _path_val,
                "state": l3_result.get("state"),
                "orchestration": _orch,
                "embedding_model_id": "bge-m3-v1",
            }
            _mgr.learn(
                payload_key,
                namespace,
                _learn_payload,
                tenant_id=tenant_id,
                corpus_version=corpus_version,
                policy_version=policy_version,
            )
        except CriticalInfrastructureError as _e:  # ADR-079 / W4 P4.3: strict-mode infra failure must not fail the request — orchestration already succeeded
            Logger.critical(
                "[L0-ORCH] D2 semantic cache learn skipped (STRICT-mode infra unavailable): %s",
                _e,
            )
            return
        except (
            ImportError,
            RuntimeError,
            ValueError,
            TypeError,
            AttributeError,
        ) as _e:  # guardian: allow-return-none-swallow -- D2 semantic cache learn is opportunistic: orchestration already succeeded; cache learn failure must not fail the request
            Logger.debug("[L0-ORCH] D2 semantic cache learn skipped: %s", _e)
            return
        # Optional L2 promotion — gated and quality-checked.
        if not _semantic_cache_promote_enabled():
            return
        _evidence = _meta.get("evidence_ids") if isinstance(_meta, dict) else None
        _grounded = bool(_meta.get("grounding_complete", False)) if isinstance(_meta, dict) else False
        try:
            _feedback = float(_meta.get("feedback_score", 0.0) or 0.0) if isinstance(_meta, dict) else 0.0
        except (TypeError, ValueError):
            _feedback = 0.0
        if not (_evidence and _grounded and _feedback >= _mgr.promotion_threshold):
            return
        try:
            import asyncio as _asyncio  # noqa: PLC0415

            _promote_payload = {
                **_learn_payload,
                "evidence_ids": list(_evidence),
                "grounding_complete": True,
            }
            _asyncio.run(
                _mgr.promote_to_long_term(
                    payload_key,
                    namespace,
                    _promote_payload,
                    _feedback,
                    tenant_id=tenant_id,
                    corpus_version=corpus_version,
                    policy_version=policy_version,
                ),
            )
        except (
            RuntimeError,
            ValueError,
            TypeError,
        ) as _pe:  # guardian: allow-log-and-swallow -- L2 promotion is a background quality optimization; promotion failure is non-fatal to the current request
            Logger.debug("[L0-ORCH] D2 semantic cache promote skipped: %s", _pe)

    def _populate_d1_cache(self, payload_key: str, l3_result: dict[str, Any]) -> None:
        """R1A writeback — deposit the successful deterministic answer into
        L1ExactCache so future identical requests short-circuit at D1.

        Gated by EXACT_CACHE_D1_ENABLED (default off). Always opportunistic:
        all failures are debug-logged and never propagate. Mirrors the D1
        key derivation used by ``check_d1_exact_cache`` (SHA-256 of the
        canonical request string).
        """
        if not _exact_cache_d1_enabled():
            return
        try:
            from agentic_core.L4_state.utils.memory.l1_exact_cache import (  # noqa: PLC0415
                get_global_l1_cache,
            )

            cache = get_global_l1_cache()
            # L1ExactCache.set stores a plain string. Serialize the L3 result
            # deterministically so retrieval is byte-for-byte identical.
            _orch = l3_result.get("orchestration") or {}
            _path_obj = l3_result.get("path")
            _path_val = _path_obj.value if _path_obj is not None and hasattr(_path_obj, "value") else None
            _serializable = {
                "path": _path_val,
                "state": l3_result.get("state"),
                "orchestration": _orch,
            }
            cache.set(
                payload_key,
                json.dumps(_serializable, sort_keys=True, default=str, separators=(",", ":")),
            )
        except (
            ImportError,
            AttributeError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as _e:  # guardian: allow-log-and-swallow -- D1 exact cache writeback is opportunistic; failure must not fail the request
            Logger.debug("[L0-ORCH] D1 exact cache writeback skipped: %s", _e)

    def plan_execution_with_impact_analysis(self, changed_files: list[str]) -> dict[str, Any]:
        """R6: Plan execution order based on ADG blast radius.

        Uses pre-built reverse dependency index instead of full codebase scan.
        Speedup: 50-500x over full scan.
        """
        try:
            from agentic_core.adg.runtime.query_engine import get_runtime_query_engine

            query_engine = get_runtime_query_engine()
            blast = query_engine.compute_blast_radius(changed_files)
            sorted_modules = sorted(blast.items(), key=lambda x: x[1])
            return {
                "modules": [m for m, _ in sorted_modules],
                "depths": dict(sorted_modules),
                "changed_files": changed_files,
                "total_impacted": len(blast),
            }
        except (ImportError, RuntimeError) as exc:  # ADG impact analysis unavailable
            Logger.warning("[L0-ORCH] ADG impact analysis unavailable: %s", exc)
            return {
                "modules": changed_files,
                "changed_files": changed_files,
                "total_impacted": len(changed_files),
            }
