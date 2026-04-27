"""
Phase 5 -- OTEL span contract for the runtime requirements proof.

Defines the canonical list of 26 runtime span names from the user spec, the
required + optional attribute schema, and a parent-graph that encodes
happens-before order. Provides a lightweight in-memory recorder so the
proof harness can emit a complete trace and serialize it to JSON without
depending on the heavy OpenTelemetry SDK.

The output JSON is OpenTelemetry-compatible (same field names where they
overlap with the OTEL data model). A future Phase-4 wiring step can swap
the recorder for the real SDK without changing the schema.
"""

from __future__ import annotations

import json
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 26 canonical runtime span names (verbatim from the user spec).
# ---------------------------------------------------------------------------

RUNTIME_SPAN_NAMES: Tuple[str, ...] = (
    # Request-level service entry span -- OTEL convention. Every stage span
    # is a descendant of this. The user spec lists the 26 runtime stage
    # spans but does not mandate the synthetic root; we add it because
    # "the trace tree must prove ordering" implies a tree, not a forest.
    "runtime.request",
    "u0.intake",
    "l1.plan",
    "l0.route_decision",
    "c0.0.preflight",
    "c0.1.retrieval_plan",
    "c0.2.fetch",
    "c0.2a.hydrate",
    "c0.3.graph_traverse",
    "c0.4.shape_rerank_stratify",
    "c0.5.final_evidence_contract",
    "c0.6.weak_support_refinement",
    "prompt_assembly.compile",
    "l3.workflow_start",
    "l3.step_dispatch",
    "l2.e1.prep",
    "l2.e2.valid",
    "l2.e3.exec",
    "l2.e4.heal",
    "l2.e5.seal",
    "exit.preflight",
    "exit.x1.gates",
    "exit.x2.aggregate",
    "exit.x3.disposition",
    "hitl.packetization",
    "uwg.commit_request",
    "uwg.commit_receipt",
    "l6.ingest",
    "l6.evaluate",
    "l6.rca_or_proposal",
    "l6.promotion_attempt",
)
# Note: spec listed 26-30 spans depending on optional ones counted; we
# include them all so any scenario can produce a complete trace.


# Required attribute keys per span (from the user spec).
REQUIRED_ATTRS: Tuple[str, ...] = (
    "trace_id",
    "span_id",
    "parent_span_id",
    "request_id",
    "run_id",
    "status",
    "reason_codes",
    "latency_ms",
)

# Attributes required only when known/applicable; their absence is allowed
# but a value of None must still be present so the contract is explicit.
CONDITIONAL_ATTRS: Tuple[str, ...] = (
    "route_id",
    "step_id",
    "gate_id",
    "policy_hash",
    "blueprint_hash",
    "replay_key",
    "contract_digest",
)

# Optional attributes recorded when the span produced cost-bearing work.
OPTIONAL_ATTRS: Tuple[str, ...] = (
    "tokens_in",
    "tokens_out",
    "cost_usd",
    "artifact_refs",
)

ALL_ATTRS: Tuple[str, ...] = REQUIRED_ATTRS + CONDITIONAL_ATTRS + OPTIONAL_ATTRS

ALLOWED_STATUSES: frozenset = frozenset(
    {"OK", "ERROR", "BLOCKED", "ABSTAINED", "REROUTED", "TIMEOUT"}
)


# Parent-graph: which span (if any) is the canonical parent of each span.
# A span_name -> parent_span_name map; root spans map to "" (no parent).
SPAN_PARENT_GRAPH: Dict[str, str] = {
    "runtime.request": "",
    "u0.intake": "runtime.request",
    "l1.plan": "runtime.request",
    "l0.route_decision": "runtime.request",
    "c0.0.preflight": "runtime.request",
    "c0.1.retrieval_plan": "c0.0.preflight",
    "c0.2.fetch": "c0.1.retrieval_plan",
    "c0.2a.hydrate": "c0.2.fetch",
    "c0.3.graph_traverse": "c0.2.fetch",
    "c0.4.shape_rerank_stratify": "c0.2.fetch",
    "c0.5.final_evidence_contract": "c0.4.shape_rerank_stratify",
    "c0.6.weak_support_refinement": "c0.5.final_evidence_contract",
    "prompt_assembly.compile": "l0.route_decision",
    "l3.workflow_start": "l0.route_decision",
    "l3.step_dispatch": "l3.workflow_start",
    "l2.e1.prep": "prompt_assembly.compile",
    "l2.e2.valid": "l2.e1.prep",
    "l2.e3.exec": "l2.e2.valid",
    "l2.e4.heal": "l2.e3.exec",
    "l2.e5.seal": "l2.e3.exec",
    "exit.preflight": "l2.e5.seal",
    "exit.x1.gates": "exit.preflight",
    "exit.x2.aggregate": "exit.x1.gates",
    "exit.x3.disposition": "exit.x2.aggregate",
    "hitl.packetization": "exit.x3.disposition",
    "uwg.commit_request": "exit.x3.disposition",
    "uwg.commit_receipt": "uwg.commit_request",
    "l6.ingest": "exit.x3.disposition",
    "l6.evaluate": "l6.ingest",
    "l6.rca_or_proposal": "l6.evaluate",
    "l6.promotion_attempt": "l6.rca_or_proposal",
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class RuntimeSpan:
    name: str
    span_id: str
    trace_id: str
    parent_span_id: str
    request_id: str
    run_id: str
    status: str
    reason_codes: List[str]
    latency_ms: float
    start_unix_ns: int
    end_unix_ns: int
    # Conditional / optional
    route_id: Optional[str] = None
    step_id: Optional[str] = None
    gate_id: Optional[str] = None
    policy_hash: Optional[str] = None
    blueprint_hash: Optional[str] = None
    replay_key: Optional[str] = None
    contract_digest: Optional[str] = None
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    cost_usd: Optional[float] = None
    artifact_refs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeTrace:
    """A single completed trace produced by the harness."""

    scenario: str
    trace_id: str
    request_id: str
    run_id: str
    spans: List[RuntimeSpan]
    started_at_unix_ns: int
    ended_at_unix_ns: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario": self.scenario,
            "trace_id": self.trace_id,
            "request_id": self.request_id,
            "run_id": self.run_id,
            "started_at_unix_ns": self.started_at_unix_ns,
            "ended_at_unix_ns": self.ended_at_unix_ns,
            "duration_ms": (self.ended_at_unix_ns - self.started_at_unix_ns) / 1_000_000.0,
            "span_count": len(self.spans),
            "spans": [s.to_dict() for s in self.spans],
        }


# ---------------------------------------------------------------------------
# Recorder
# ---------------------------------------------------------------------------

class RuntimeSpanRecorder:
    """Captures spans during a scenario run and finalizes them into a trace."""

    def __init__(
        self,
        scenario: str,
        request_id: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> None:
        self.scenario = scenario
        self.trace_id = uuid.uuid4().hex
        self.request_id = request_id or f"req-{uuid.uuid4().hex[:12]}"
        self.run_id = run_id or f"run-{uuid.uuid4().hex[:12]}"
        self._spans: List[RuntimeSpan] = []
        self._stack: List[str] = []  # span_id stack for parent resolution
        self._span_by_name: Dict[str, str] = {}  # name -> span_id, latest wins
        self._started_at: int = time.time_ns()

    def _resolve_parent(self, explicit_parent: Optional[str]) -> str:
        """Top-of-active-stack is the canonical parent unless caller overrides.

        Falls back to "" (root) when the stack is empty. SPAN_PARENT_GRAPH is
        informational only -- the actual parent is determined by lexical
        nesting of `with rec.span(...)` blocks.
        """
        if explicit_parent is not None:
            return explicit_parent
        if self._stack:
            return self._stack[-1]
        return ""

    @contextmanager
    def span(
        self,
        name: str,
        *,
        status: str = "OK",
        reason_codes: Optional[List[str]] = None,
        parent_span_id: Optional[str] = None,
        **attrs: Any,
    ) -> Iterator[str]:
        if name not in RUNTIME_SPAN_NAMES:
            raise ValueError(f"unknown runtime span name: {name}")
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"unknown span status: {status}")
        span_id = uuid.uuid4().hex[:16]
        parent_id = self._resolve_parent(parent_span_id)
        start = time.time_ns()
        # Push BEFORE yielding so any nested span sees us as parent.
        self._stack.append(span_id)
        self._span_by_name[name] = span_id
        try:
            yield span_id
            final_status = status
        except Exception:
            final_status = "ERROR"
            raise
        finally:
            # Pop our span_id; defensive against caller mutation.
            if self._stack and self._stack[-1] == span_id:
                self._stack.pop()
            end = time.time_ns()
            span = RuntimeSpan(
                name=name,
                span_id=span_id,
                trace_id=self.trace_id,
                parent_span_id=parent_id,
                request_id=self.request_id,
                run_id=self.run_id,
                status=final_status,
                reason_codes=list(reason_codes or []),
                latency_ms=(end - start) / 1_000_000.0,
                start_unix_ns=start,
                end_unix_ns=end,
                route_id=attrs.get("route_id"),
                step_id=attrs.get("step_id"),
                gate_id=attrs.get("gate_id"),
                policy_hash=attrs.get("policy_hash"),
                blueprint_hash=attrs.get("blueprint_hash"),
                replay_key=attrs.get("replay_key"),
                contract_digest=attrs.get("contract_digest"),
                tokens_in=attrs.get("tokens_in"),
                tokens_out=attrs.get("tokens_out"),
                cost_usd=attrs.get("cost_usd"),
                artifact_refs=list(attrs.get("artifact_refs") or []),
            )
            self._spans.append(span)

    def finalize(self) -> RuntimeTrace:
        return RuntimeTrace(
            scenario=self.scenario,
            trace_id=self.trace_id,
            request_id=self.request_id,
            run_id=self.run_id,
            spans=list(self._spans),
            started_at_unix_ns=self._started_at,
            ended_at_unix_ns=time.time_ns(),
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_trace(trace: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Return (ok, errors) for a trace dict produced by the recorder."""
    errors: List[str] = []
    spans = trace.get("spans", [])
    if not spans:
        errors.append("trace has zero spans")
        return False, errors

    span_ids = {s["span_id"] for s in spans}
    by_name: Dict[str, Dict[str, Any]] = {}
    for s in spans:
        # Required attrs presence
        for attr in REQUIRED_ATTRS:
            if attr not in s:
                errors.append(f"span {s.get('name','?')} missing required attr {attr}")
        # Conditional attrs must AT LEAST be present as keys (value may be None)
        for attr in CONDITIONAL_ATTRS:
            if attr not in s:
                errors.append(
                    f"span {s.get('name','?')} missing conditional attr key {attr}"
                )
        # Status vocabulary
        if s.get("status") not in ALLOWED_STATUSES:
            errors.append(
                f"span {s.get('name','?')} has unknown status {s.get('status')}"
            )
        # Span name in canonical list
        if s.get("name") not in RUNTIME_SPAN_NAMES:
            errors.append(f"unknown span name: {s.get('name')}")
        by_name[s["name"]] = s

    # Parent links resolve
    for s in spans:
        parent = s.get("parent_span_id", "")
        if parent and parent not in span_ids:
            errors.append(
                f"span {s['name']} parent_span_id={parent} does not resolve in this trace"
            )

    # All spans share trace_id, request_id, run_id. Use .get() so a span
    # that was already flagged for a missing required attr does not raise
    # KeyError here -- the missing-attr error has already been recorded.
    trace_ids = {s.get("trace_id") for s in spans if "trace_id" in s}
    request_ids = {s.get("request_id") for s in spans if "request_id" in s}
    run_ids = {s.get("run_id") for s in spans if "run_id" in s}
    if len(trace_ids) > 1:
        errors.append(f"multiple trace_ids in single trace: {trace_ids}")
    if len(request_ids) > 1:
        errors.append(f"multiple request_ids in single trace: {request_ids}")
    if len(run_ids) > 1:
        errors.append(f"multiple run_ids in single trace: {run_ids}")

    # Exactly one root (parent_span_id == "")
    roots = [s for s in spans if not s.get("parent_span_id")]
    if len(roots) != 1:
        errors.append(
            f"trace must have exactly one root span; found {len(roots)} "
            f"({[r['name'] for r in roots]})"
        )

    return (len(errors) == 0, errors)


def write_trace(trace: RuntimeTrace, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(trace.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Scenario-shape validators (Phase 7 anti-bypass uses these)
# ---------------------------------------------------------------------------

def validate_scenario_shape(trace: Dict[str, Any], scenario: str) -> Tuple[bool, List[str]]:
    """Return (ok, errors) for scenario-specific invariants.

    Each scenario in the user spec defines structural constraints that go
    beyond the generic trace contract: which spans MUST appear, which spans
    MUST NOT appear, which final-disposition status MUST hold. These checks
    catch bypass attempts that produce a generically-valid trace but
    mis-routed through the wrong scenario semantics.
    """
    errors: List[str] = []
    span_names = {s["name"] for s in trace["spans"]}
    by_name: Dict[str, Dict[str, Any]] = {}
    for s in trace["spans"]:
        by_name[s["name"]] = s

    if scenario == "A_grounded_read":
        forbidden = {
            "l3.workflow_start",
            "l3.step_dispatch",
            "uwg.commit_request",
            "uwg.commit_receipt",
            "c0.6.weak_support_refinement",
            "hitl.packetization",
        }
        leaked = forbidden & span_names
        if leaked:
            errors.append(f"scenario A leaked forbidden spans: {sorted(leaked)}")
        required = {"u0.intake", "l1.plan", "l0.route_decision", "exit.x3.disposition"}
        missing = required - span_names
        if missing:
            errors.append(f"scenario A missing required spans: {sorted(missing)}")

    elif scenario == "B_managed_workflow":
        required = {"l3.workflow_start", "l3.step_dispatch"}
        missing = required - span_names
        if missing:
            errors.append(f"scenario B missing required spans: {sorted(missing)}")
        # No commit_receipt -- proposal only, never committed
        if "uwg.commit_receipt" in span_names:
            errors.append(
                "scenario B leaked uwg.commit_receipt -- managed workflow proposes only"
            )

    elif scenario == "C_weak_evidence":
        if "c0.6.weak_support_refinement" not in span_names:
            errors.append("scenario C missing c0.6.weak_support_refinement")
        # The weak-support span must declare the WEAK_WITH_CAVEATS reason
        c5 = by_name.get("c0.5.final_evidence_contract")
        if c5 is not None:
            rc = c5.get("reason_codes") or []
            if not any("WEAK" in code for code in rc):
                errors.append(
                    "scenario C c0.5.final_evidence_contract missing WEAK reason_code"
                )

    elif scenario == "D_anti_bypass":
        if "hitl.packetization" not in span_names:
            errors.append("scenario D missing hitl.packetization span")
        if "uwg.commit_receipt" in span_names:
            errors.append(
                "scenario D leaked uwg.commit_receipt -- write must be blocked"
            )
        x3 = by_name.get("exit.x3.disposition")
        if x3 is None:
            errors.append("scenario D missing exit.x3.disposition")
        elif x3.get("status") != "BLOCKED":
            errors.append(
                f"scenario D exit.x3 status must be BLOCKED, got {x3.get('status')}"
            )

    elif scenario == "E_authorized_commit":
        # Positive UWG path: write authorization at x3, commit fires, l6
        # promotion_attempt records the candidate.
        required = {
            "uwg.commit_request",
            "uwg.commit_receipt",
            "l6.promotion_attempt",
            "l3.workflow_start",
        }
        missing = required - span_names
        if missing:
            errors.append(f"scenario E missing required commit-path spans: {sorted(missing)}")
        x3 = by_name.get("exit.x3.disposition")
        if x3 is not None:
            rc = x3.get("reason_codes") or []
            if not any("ALLOW_COMMIT" in code for code in rc):
                errors.append(
                    "scenario E exit.x3 reason_codes missing ALLOW_COMMIT marker"
                )
        receipt = by_name.get("uwg.commit_receipt")
        if receipt is not None and receipt.get("contract_digest") is None:
            errors.append(
                "scenario E uwg.commit_receipt missing contract_digest"
            )

    else:
        errors.append(f"unknown scenario name: {scenario}")

    return (len(errors) == 0, errors)


def validate_trace_full(trace: Dict[str, Any], scenario: str) -> Tuple[bool, List[str]]:
    """Run BOTH the generic contract validator AND the scenario shape checks."""
    ok1, errs1 = validate_trace(trace)
    ok2, errs2 = validate_scenario_shape(trace, scenario)
    return (ok1 and ok2, errs1 + errs2)
