# SLO — apps_underwriting_ai (AI Underwriting Decision Pipeline)

> **Status:** TARGETS for the skeleton; real-domain SLOs will be tightened once feature-complete logic lands.
> **Owner:** see `CODEOWNERS`
> **Last reviewed:** 2026-05-02 (skeleton initial)

## Architecture Note

apps_underwriting_ai emits underwriting decisions. Its SLOs prioritize **decision auditability** and **gate compliance** over sub-second latency: every decision must trace back to evidence, even if generation takes seconds.

## Service Level Objectives (skeleton-stage; revisit at feature-complete)

| Dimension | p50 | p95 | p99 | Hard ceiling | Error budget |
|---|---:|---:|---:|---:|---:|
| **End-to-end pipeline** | 50ms | 250ms | 1s | 5s (skeleton) | 1% / 30d |
| **Stage 1 (initialize_evidence)** | <1ms | 5ms | 20ms | 100ms | 1% / 30d |
| **Stage 2 (reconcile_documents)** | <1ms | 10ms | 50ms | 500ms (skeleton) | 1% / 30d |
| **Stage 3 (derive_features)** | <1ms | 10ms | 50ms | 500ms (skeleton) | 1% / 30d |
| **Stage 4 (collect_evidence)** | <1ms | 5ms | 20ms | 200ms | 1% / 30d |
| **Stage 5 (assemble_decision)** | <1ms | 5ms | 20ms | 100ms | 1% / 30d |

> **Note:** skeleton-stage latencies are deterministic memory operations. Feature-complete latencies will be dominated by document parsing (stage 2) and feature derivation (stage 3) and will be revised at that time.

## Quality SLOs

| Dimension | Target |
|---|---|
| **Verdict-evidence binding** (every APPROVE has ≥1 evidence record) | 100% (gate) |
| **REFER-on-unresolved** (any unresolved reconciliation forces REFER) | 100% (gate) |
| **Trace-id propagation** (every decision packet carries trace_id) | 100% |
| **Artifact emission** (when `--artifact-dir` set, both decision.md + run_summary.json emit) | 100% |

## Cost Ceiling

| Workload | Per-call (USD) | Per-day budget |
|---|---:|---:|
| Skeleton pipeline (memory-only) | $0.000 | $0 |
| Feature-complete pipeline (LLM-assisted reconciliation) | TBD | TBD |

Real cost ceilings will be set when feature-complete logic lands.

## Freshness

- **Spec file** (`config/specs/agent_spec.underwriting.v1.0.0.yaml`) reviewed quarterly.
- **Domain contract YAMLs** (`config/domain_contract/`) reviewed monthly.

## Failure Modes (top-3 — see RUNBOOK.md for response)

1. **Insufficient evidence on a real applicant** → REFUSE to APPROVE, emit `INSUFFICIENT_EVIDENCE` verdict. Auditable.
2. **REFER cascade from unresolved reconciliation** → render with full reconciliation notes; do NOT silently approve.
3. **Stage exception** (any of the 5 stages raises) → fail-fast, emit observability event, no decision packet.

## Architectural Differentiation

apps_underwriting_ai is the first in-portfolio app with:
- **Two equivalent pipeline drivers** (imperative `UnderwritingEngine` + declarative `UnderwritingHopOrchestrator` over the same stage registry)
- **Frozen-dataclass evidence register** — append-only via `_append()`, no in-place mutation, simplifying audit reasoning
- **`DecisionVerdict` enum-bounded outputs** — only 4 verdicts permitted, deliberate for downstream pattern-matching

## Out of Scope (for THIS app's SLO at skeleton stage)

- Real actuarial scoring (real-domain, post-skeleton)
- Regulatory compliance checks (real-domain, post-skeleton)
- Risk-tier mapping (real-domain, post-skeleton)
- Document OCR (parsers/ — reserved package)

## Measurement Plan

- OTEL spans per-stage with `app=apps_underwriting_ai`, `stage_name`, `request_id` (when feature-complete).
- Decision audit log preserved indefinitely (regulatory auditability).
- Feature-complete-stage SLOs to be measured after real-domain logic lands.
