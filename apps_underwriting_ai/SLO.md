# SLO — apps_underwriting_ai (Regulated-Industry Underwriting Engine)

> **Status:** TARGETS, not yet measured. Wave 4.3 (cost/latency telemetry rollup) closes the loop.
> **Owner:** see `CODEOWNERS`
> **Last reviewed:** 2026-04-29

## Architecture Note

apps_underwriting_ai is the **most regulated** app in the portfolio. Its SLOs are dominated by auditability and authority-limit enforcement, not raw latency. A late but provably-correct decision packet is far better than a fast but unauditable one.

This is also the strongest portfolio narrative for an SVP+ hiring panel: regulated decision systems with cryptographic evidence trails are exactly what fintech / insurance / healthcare hiring panels probe for.

## Service Level Objectives

| Dimension | p50 | p95 | p99 | Hard ceiling | Error budget |
|---|---:|---:|---:|---:|---:|
| **Single underwriting decision (request → packet)** | 8s | 30s | 90s | 300s (gate) | **0.5% / 30d** (tighter than peers) |
| **Document reconciliation pass** | 1.5s | 5s | 12s | 30s | 1% / 30d |
| **Feature derivation** | 2s | 7s | 18s | 45s | 1% / 30d |
| **Authority-limit validator** | 30ms | 120ms | 300ms | 1s | <0.5% / 30d |
| **Compliance validator** | 100ms | 350ms | 800ms | 3s | <0.5% / 30d |
| **Decision packet assembly** | 200ms | 700ms | 2.0s | 5s | <0.5% / 30d |

## Compliance & Audit SLOs (these are gates, not targets)

| Dimension | Target |
|---|---|
| **Forbidden-feature usage** (regulated features must not influence decision) | 0% (hard gate — `forbidden_feature_checker.py`) |
| **Authority-limit breach** (decision exceeds approver authority) | 0% (hard gate — `authority_limit_validator.py`) |
| **Stale-data acceptance** (data > policy max-age used in decision) | 0% (hard gate — `stale_data_validator.py`) |
| **Contradiction in evidence** (silently resolved) | 0% (hard gate — `contradiction_validator.py`) |
| **Document completeness** (all required docs present and parsed) | 100% (hard gate — `document_completeness_validator.py`) |
| **Decision packet replay parity** (full re-derivation matches) | 100% |
| **Audit log immutability** (all decisions write to append-only ledger) | 100% |

## Cost Ceiling

| Workload | Per-call (USD) | Per-day budget |
|---|---:|---:|
| Feature derivation (deterministic + LLM check) | $0.0024 | $24 |
| Document reconciliation (LLM-aided) | $0.004 | $20 |
| Decision packet assembly | $0.0008 | $4 |
| Total ceiling | — | **$50/day**, alert at 80% |

## Data Classification & Retention

| Class | Examples | Retention | Encryption-at-rest |
|---|---|---|---|
| **PII-Sensitive** | borrower SSN, DOB, address | 7 years (regulatory) | AES-256, KMS-managed |
| **PII-Standard** | borrower name, email | 7 years | AES-256 |
| **Decision artifacts** | features, rationale, evidence | 10 years (immutable) | AES-256 + signed |
| **Aggregate / non-PII** | model performance, audit roll-ups | indefinite | standard |

## Freshness

- **Authority-limit policy** must be ≤ 1 day old (auto-refresh from policy registry).
- **Forbidden-feature list** versioned; changes require ADR + 30-day grace period.
- **Document parse output** ≤ 24 hours from ingestion before re-parse required.

## Failure Modes (top-3 — see RUNBOOK.md for response)

1. **Authority-limit validator down** → REFUSE all decisions; do NOT fall back to "best-effort." Decisions without authority validation are non-binding by definition.
2. **Forbidden-feature checker emits a hit** → halt the run, freeze the request, route to compliance review. Never auto-resolve.
3. **Replay parity mismatch** → audit-grade incident; freeze the model; require manual recertification before resumption.

## Architectural Differentiation

apps_underwriting_ai is the only in-portfolio app with:
- **6 explicit domain validators** (authority, compliance, contradiction, stale-data, forbidden-feature, completeness)
- **14 type modules** (most domain-decomposed)
- **Decision-packet assembler** producing immutable, replayable artifacts
- **Evidence-register engine** with per-feature provenance

This is the strongest **"regulated AI decision system"** narrative in the portfolio. The THREAT_MODEL.md captures the security side.

## Out of Scope (for THIS app's SLO)

- Loan origination workflow (downstream)
- Customer-facing UI (separate)
- Model training / re-fitting (offline pipeline)

## How These Numbers Were Derived

- p50/p95: feature derivation (~3s) + reconciliation (~2s) + LLM check (~3s) ≈ 8s warm.
- 0.5% error budget: tighter than peers because regulated decisions imply zero-tolerance for silent failure.
- 300s hard ceiling: outer bound; in practice if decisioning takes >2min the request is escalated to manual underwriting.

## Measurement Plan (W4.3)

- Per-decision OTEL span with `app=apps_underwriting_ai`, `decision_id`, `latency_ms`, `validators_passed[]`, `evidence_count`, `replay_digest`.
- Replay-parity job nightly: re-derive 100% of prior-day decisions and assert match.
- Weekly compliance audit log digest; reviewed by a human compliance role (gap until role exists).
