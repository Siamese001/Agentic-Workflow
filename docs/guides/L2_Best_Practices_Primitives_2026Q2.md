# L2 Execute — Best-Practices Primitives (2026-Q2)

Developer-facing index for the 14 additive L2 modules landed by plan `@c:/Git/Agentic-Workflow/.windsurf/plans/l2-execute-best-practices-gap-b7c4e2.md`.

**All primitives are additive.** No existing consumer breaks. Call sites opt in by passing a `ToolContract` (W1-P1.3) or by directly importing a registry / class (W2-W5). Default-safe lookups ensure that tools without registered metadata behave as they did before.

Canonical v33 process phase mapping: `@c:/Git/Agentic-Workflow/docs/reference/_notes/agentic_process_mapping_v34.md` → `[APPENDIX A]`.

---

## Quick Reference

| Gap | Module | Phase | Purpose |
|---|---|---|---|
| G1 | `agentic_core/L2_execution/enforcement/tool_guardrail_pipeline.py` | E2/E3/E5 | Unified pre/post guardrail wrapper with `TripwireTriggered` halt exception |
| G8 | `agentic_core/L2_execution/enforcement/e2_validate_before_execute.py` | E2 | Raises `ConfirmBeforeExecute` before E3 for high-consequence tools |
| G9 | `agentic_core/L2_execution/types/l2_safety_contracts.py` | E2 | `SideEffectClass` / `Reversibility` / `ConsequenceLevel` + `SafetyProfile` registry |
| G2 | `agentic_core/L2_execution/enforcement/egress_proxy.py` | E1/E3 | Allowlisted egress with fail-closed default; `egress_scope` ctx manager |
| G3 | `agentic_core/L2_execution/capability/scoped_credential_mint.py` | E1 | HMAC-signed, expiry-bound, nonce-revocable scoped credentials |
| G16 | `agentic_core/L2_execution/capability/step_scoped_identity.py` | E1 | Narrow subset-enforced per-step identity |
| G4 | `agentic_core/L2_execution/types/l2_tool_enrichment.py` | E2/E3 | `ThoughtSignature` + `make_thought_signature` |
| G5 | same | E2 | `ToolUseExample` 1..5 bounded registry |
| G10 | same | E3/E4 | `ExecutionMarkers` (parallel_safe / idempotent / retry) |
| G6 | `agentic_core/L2_execution/reasoning/tool_search.py` | E1 | TF-IDF tool search, k-capped |
| G7 | `agentic_core/L2_execution/reasoning/programmatic_tool_runner.py` | E3 | Sub-context tool chain; hides intermediates from parent trace |
| G12 | `agentic_core/L2_execution/enforcement/kill_switch.py` | E3/E4 | Lineage-scoped idempotent kill-switch |
| G11 | `agentic_core/L2_execution/enforcement/llm_call_audit.py` | E2/E3 | Non-blocking temperature-0 audit for tool-selecting LLM calls |
| G13 | `agentic_core/L2_execution/enforcement/runtime_behavior_monitor.py` | cross-cut | Tool-sequence / retry-storm / cost-drift detectors |
| G14 | `agentic_core/L2_execution/enforcement/seal_schema_validator.py` | E5 | Lightweight seal schema validator |
| G15 | `agentic_core/L2_execution/types/trace_grading_hooks.py` | E5 → L6 6B | `GradingBundle` / `GradingSlot` / `GradingTarget` |

---

## Usage Patterns

### E2 — validate-before-execute (G8, G9, G1)

```python
from agentic_core.L2_execution.enforcement.e2_validate_before_execute import (
    evaluate_work_order, ConfirmBeforeExecute,
)
from agentic_core.L2_execution.types.l2_safety_contracts import (
    register_safety_profile, SafetyProfile, SideEffectClass, Reversibility, ConsequenceLevel,
)

register_safety_profile(SafetyProfile(
    tool_name="orders.submit",
    side_effect=SideEffectClass.ACTION,
    reversibility=Reversibility.COMPENSABLE,
    consequence=ConsequenceLevel.HIGH,
))

try:
    verdict = evaluate_work_order(contract)
except ConfirmBeforeExecute as e:
    route_to_hitl(e.verdict)  # E3 never reached
```

The wiring into `L2ExecutionAgent.run_l2_phases()` (`@c:/Git/Agentic-Workflow/agentic_core/L2_execution/types/l2_execution_contract.py`) and `CallInterceptor.intercept()` (`@c:/Git/Agentic-Workflow/agentic_core/L2_execution/capability/call_interceptor.py`) is already live — attach a `ToolContract` under `inputs["tool_contract"]` or `context["tool_contract"]` to activate.

### Egress (G2) + scoped credentials (G3) + narrow identity (G16)

```python
from agentic_core.L2_execution.enforcement.egress_proxy import build_policy, egress_scope, check_url
from agentic_core.L2_execution.capability.scoped_credential_mint import CredentialMint
from agentic_core.L2_execution.capability.step_scoped_identity import (
    IdentityDerivation, derive_step_identity,
)

mint = CredentialMint()  # OUTSIDE the sandbox
policy = build_policy(name="step-42", allowed_hosts={"*.vendor.io"})

with egress_scope(policy):
    cred = mint.issue(step_id="step-42", audience="vendor.io")
    check_url("https://api.vendor.io/x")  # raises EgressDenied if disallowed
    headers = {"Authorization": cred.to_header_value()}
    # ... make the call ...
```

### Tool search (G6) + programmatic tool calling (G7)

```python
from agentic_core.L2_execution.reasoning.tool_search import ToolSearchIndex, ToolSearchEntry
from agentic_core.L2_execution.reasoning.programmatic_tool_runner import (
    ProgrammaticToolRunner, ToolStep,
)

idx = ToolSearchIndex()
idx.register_many([
    ToolSearchEntry("orders.submit", "submit customer order"),
    ToolSearchEntry("orders.cancel", "cancel customer order"),
])
top = idx.search("submit order", k=5)  # bounded active set

runner = ProgrammaticToolRunner(tool_executor=call_tool)
result = runner.run(
    steps=[ToolStep("search", {"q": "x"})],
    summarize=lambda outs: {"count": len(outs[-1])},
)
# result.summary goes to parent trace; result.intermediates stays local
```

### Kill switch (G12)

```python
from agentic_core.L2_execution.enforcement.kill_switch import trip, is_tripped, default_registry

trip(lineage_id=trace_id, reason="user cancelled", tripped_by="operator")
default_registry().raise_if_tripped(trace_id)  # call at E3 entry
```

### Observability hooks (G11, G13, G14, G15)

```python
from agentic_core.L2_execution.enforcement.llm_call_audit import LLMCallEnvelope, audit_llm_call
from agentic_core.L2_execution.enforcement.runtime_behavior_monitor import (
    BehaviorMonitor, TraceEvent, WorkflowTrace,
)
from agentic_core.L2_execution.enforcement.seal_schema_validator import (
    FieldSpec, SealSchema, validate_sealed_artifact,
)
from agentic_core.L2_execution.types.trace_grading_hooks import GradingBundle, GradingTarget

# 1. Temperature audit (warning, non-blocking)
finding = audit_llm_call(LLMCallEnvelope(model="gpt-x", temperature=0.9, tool_choice="auto"))

# 2. Behavior monitoring across a run
trace = WorkflowTrace()
trace.record(TraceEvent(step_id="s1", tool_name="search", retry_count=0, tokens=1200))
findings = BehaviorMonitor().evaluate(trace)

# 3. Seal schema validation at E5
schema = SealSchema("sealed", fields=(
    FieldSpec("status", str, enum=("SUCCESS", "FAILURE", "NEEDS_HELP")),
    FieldSpec("trace_id", str, min_len=1),
    FieldSpec("attempts", int),
))
validate_sealed_artifact(sealed_dict, schema)  # raises SealValidationError

# 4. Grading slots for L6 §6B
bundle = GradingBundle(trace_id=trace_id)
bundle.add(slot_id="e3.1", target=GradingTarget.E3_EXECUTE, preliminary_signals={"retries": 0})
```

---

## Verification

```
python -m pytest \
  tests/unit/agentic_core/L2_execution/test_l2_safety_w1.py \
  tests/unit/agentic_core/L2_execution/test_l2_safety_w1_p3_wiring.py \
  tests/unit/agentic_core/L2_execution/test_l2_safety_w2.py \
  tests/unit/agentic_core/L2_execution/test_l2_safety_w3.py \
  tests/unit/agentic_core/L2_execution/test_l2_safety_w4.py \
  tests/unit/agentic_core/L2_execution/test_l2_safety_w5.py \
  --timeout=60
```

Expected: **102 passed** (17 W1 + 7 W1-P1.3 + 22 W2 + 18 W3 + 19 W4 + 19 W5).

---

## Invariants preserved

- No PowerShell used.
- No `pytest.mark.skip` and no `xfail` added.
- No `except Exception` without guardian exemption (one `guardian: allow-broad-to-wrap` in `programmatic_tool_runner.py` is explicit and narrowly scoped to sub-context isolation).
- No subprocess calls without `timeout=`.
- No durable commits inside L2 — every primitive is in-memory, stateless, or emits sealed artifacts only.
- Default-safe: tools without registered metadata fall back to safest profile / empty examples / no markers.

---

## Sources

- Anthropic — *Claude Code Sandboxing*, *Advanced Tool Use*
- OpenAI — Agents SDK guardrails, Agent Builder Safety / trace grading
- Google — Vertex AI function-calling best practices (temperature 0, thought signatures, validate-before-execute)
- codebridge.tech 2026 — AI-agent guardrails (kill switches, narrow identity, runtime monitoring)
- arXiv 2512.09458 — Architectures for Agentic AI (structured output + validator chains)

Full references and gap-by-gap citations live in the plan's §2 corpus table.
