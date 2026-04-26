# L5 Contracts — Deferred Scope (honest gaps after closure)

_This is the closing scope record for the L5 contracts package built
in this work cycle. The contracts package itself reports **0 UNCOVERED**
requirements in the coverage matrix (`coverage_matrix.md`), but that
is bounded by what a frozen-dataclass package can encode. The items
below are real work that lives **outside the contracts package** and
is captured here so it is not lost between sessions._

## What was actually finished

| Surface | Coverage |
|---|---|
| Named output registry | **819 / 819** doctrine names (`CONTRACT_REGISTRY`) |
| Per-status doctrine value sets | **51 / 51** `StrEnum`s in `_status_enums.py` (one field declared in two docs unioned) |
| Forbidden runtime dispositions | **24 / 24** tokens in `FORBIDDEN_RUNTIME_DISPOSITIONS` |
| Smoke + alignment + stress tests | **834** tests passing under xdist |
| Requirement coverage matrix | **561 / 561** rows classified, 0 UNCOVERED |
| Audit guard (no missed/no spurious) | Permanent in-process test |
| Matrix regression guard | Permanent in-process test |

## What is genuinely deferred

### 1. Per-packet field schemas

| Attribute | Value |
|---|---|
| Plan | `NEW:l5-contracts-field-schemas` |
| Coverage gap | ~98.7% of outputs (~787 / 819) carry only the generic envelope |
| Doctrine surface | Doctrine has **zero structured field-block syntax** — no `Fields:` headers, no pipe tables, no `payload:` sections that bind to specific output names. Confirmed via empty result of `extract_fields_blocks.py`. |
| Effort | ~20k tokens. Each output's field set must be hand-curated by reading the prose context that introduces it. |
| Honest verdict | The contracts package is intentionally an **envelope-only registry**. Field-by-field schemas are a different artifact — likely a JSON-Schema or Pydantic layer authored against the L5 enforcement plane's actual emit sites. Bulk extraction from the doctrine docs is not viable. |
| Suggested next move | Open a per-output schema curation pass driven by the L5 runtime emitter (item 2), not by re-parsing the docs. |

### 2. Runtime emitter for L5 enforcement plane

| Attribute | Value |
|---|---|
| Plan | `NEW:l5-runtime-emitter` |
| Coverage gap | 100% — no runtime emitter exists for any of the 819 contracts |
| Surface | `agentic_core/L5_safety/enforcement/` (out-of-scope for the contracts package by design) |
| Effort | ~25k tokens. Needs UWG/audit log integration, OTEL spans, and HITL adapters. |
| Honest verdict | The contracts package does not need to grow into a runtime — that violates the doctrine's own evidence-only invariant. The runtime emitter is its own subsystem. |
| Suggested next move | Identify the top 10 high-fan-in contracts (CENTRAL_DEPENDENCY archetype per ADG canonical invariants) and wire emitters at those call sites only, before generalizing. |

### 3. Causal sequencing harness

| Attribute | Value |
|---|---|
| Plan | `NEW:l5-causal-sequencing` |
| Coverage gap | 1 explicit CAUSAL row + many implicit "X must precede Y" requirements re-classified as RUNTIME_INVARIANT |
| Effort | ~8k tokens. Needs an ordering enforcer that observes emit timestamps and raises on out-of-order events. |
| Honest verdict | This belongs in the same shipping unit as item 2 (runtime emitter) — sequencing without an emitter is meaningless. |
| Suggested next move | Tackle as a follow-on phase of the runtime-emitter plan once contract emit sites exist. |

## What `STATUS_ENUM_REGISTRY` does NOT cover

The `replay_binding_status` doctrine field appears in two docs (00.2 and 00.6)
with different value sets. The extractor takes the **union** to be
conservative (a runtime may emit either set). If doctrine intends the
00.6 set as canonical, the 00.2 declaration should be amended.

Detected during extraction:
```
INFO: extending replay_binding_status value set with ['mismatched']
from 00.6_L5_Replay_Audit_and_Certification_Evidence_detailed.md:169
(first seen in 00.2_L5_Authority_Context_and_Registry_Binding_detailed.md:162)
```

This is logged but not auto-resolved. Doctrine review item.

## Reproduction commands

```
python tools/l5_contracts/extract_outputs.py
python tools/l5_contracts/extract_status_enums.py
python tools/l5_contracts/generate_contracts.py
python tools/l5_contracts/audit_coverage.py
python tools/l5_contracts/build_requirement_matrix.py
python -m pytest tests/agentic_core/L5_safety/contracts -q
```

All commands are deterministic and idempotent. Run-time: ~10 seconds total.
