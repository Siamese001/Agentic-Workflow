# Career track taxonomy (operator-confirmed)

**Date:** 2026-05-19 (updated with year ranges + pillar assignments)  
**Plan:** [graph-skills-hardening-f3a8c1](../../.cursor/plans/graph-skills-hardening-f3a8c1.md)  
**Purpose:** Cluster multi-career experience into three proof-safe tracks for graph projection, C0.3 expansion, and section generation.

---

## Operator-confirmed metadata

| Track | `start_year` | `end_year` | Notes |
|-------|-------------:|-----------:|-------|
| `TRACK_ACTUARIAL_RISK_DERIVATIVES` | 2002 | 2010 | Foundation career |
| `TRACK_DATA_TECH_CLOUD_ML` | 2010 | 2022 | Career change (includes trading/HPC + partner GTM) |
| `TRACK_GENAI_AGENTIC` | 2022 | present | Specialization |

**Pillar assignments (confirmed):**
- `pillar_trading_hpc` → **TRACK_DATA_TECH_CLOUD_ML** (not track 1)
- Partner GTM pillars → **TRACK_DATA_TECH_CLOUD_ML** only (no fourth track)

---

## Three tracks

### 1. Actuarial / risk management / derivatives (2002–2010)

`TRACK_ACTUARIAL_RISK_DERIVATIVES` · `start_year=2002` · `end_year=2010`

Foundation career: stochastic modeling, derivatives, Greeks, insurance liabilities, enterprise risk, regulatory capital (Basel/CCAR themes).

**Graph epochs absorbed:**
- `epoch_actuarial_financial_engineering`
- `epoch_enterprise_risk_governance`

**Primary pillars:** actuarial foundation, derivatives, embedded options, Greeks/hedging, risk management, enterprise risk controls, regulatory governance, capital modeling.

---

### 2. Data / technology / Cloud / ML (career change) (2010–2022)

`TRACK_DATA_TECH_CLOUD_ML` · `start_year=2010` · `end_year=2022`

Career pivot into technology leadership: cloud/AWS, data platforms, ML engineering scale, **trading/HPC on cloud**, solutioning, **partner GTM / co-sell**, revenue/commercialization, executive operating model.

**Graph epochs absorbed:**
- `epoch_cloud_data_platform_engineering`
- `epoch_ai_platform_commercialization` (primary)
- `epoch_partner_gtm_revenue_leadership`

**Primary pillars:** cloud/data/AWS, **trading/HPC**, executive leadership, revenue/commercialization, revenue ops, presales/solutioning, **partner GTM**, co-sell/partner engineering, customer/stakeholder, strategic finance/SaaS metrics.

---

### 3. GenAI / Agentic (specialization) (2022–present)

`TRACK_GENAI_AGENTIC` · `start_year=2022` · `end_year=present`

Specialization on the platform career: governed agentic AI, deterministic routing, multi-agent orchestration, GraphRAG, policy gates, validation, replayable traces.

**Graph epochs absorbed:**
- `epoch_agentic_ai_runtime_architecture`

**Primary pillars:** agentic AI platforms (+ deep-agentic capability_domain skill rows).

**Bridge from track 2:** Commercialization/platform productization facts may appear in both track 2 and track 3 only when separate `fact_id_links` exist—never merged causally in prose.

---

## Career sequence (non-causal, synthesis only)

```text
TRACK_ACTUARIAL_RISK_DERIVATIVES  →  TRACK_DATA_TECH_CLOUD_ML  →  TRACK_GENAI_AGENTIC
```

Edge type: `career_sequence` (prompt/narrative ordering). **Not** proof of causation.

---

## Default JD track weights (starting point for W14)

| Target role flavor | Track 1 | Track 2 | Track 3 |
|--------------------|--------:|--------:|--------:|
| SVP / Head of AI Engineering | 0.10 | 0.25 | 0.65 |
| Chief AI Officer | 0.15 | 0.25 | 0.60 |
| Field CTO / Solutions | 0.05 | 0.45 | 0.50 |
| AI Governance / Risk officer | 0.40 | 0.30 | 0.30 |
| Partnerships / Alliances | 0.05 | 0.70 | 0.25 |

Weights select **which tracks contribute facts** to the allowed packet; they do not weaken X2/X1D.

---

## Implementation waves (plan)

| Wave | Deliverable |
|------|-------------|
| W11 | `career_track` nodes + remap epochs/pillars in `master_skills_arsenal_ledger.json` |
| W12 | Employment spine → track |
| W13 | Per-track skill activation (DRAFT→ACTIVE + fact links) |
| W14 | Track-weighted proof pool + C0.3 multi-hop |
| W15 | Track-balanced exec summary / competencies |

---

## Resolved (operator 2026-05-19)

| Question | Decision |
|----------|----------|
| Trading/HPC pillar | **Track 2** (`TRACK_DATA_TECH_CLOUD_ML`) |
| Partner GTM | **Track 2** only |
| Year ranges | Track 1: **2002–2010** · Track 2: **2010–2022** · Track 3: **2022–present** |
