I now have what I need. The candidate fact ledger has 42 facts; the key backing fact for the actuarial/derivatives/insurance cluster is `fact_quant_hpc_003` (derivatives pricing, multi-Greek hedging, capital modeling, FSA), plus `fact_governance_003` (Basel/CCAR), `fact_quant_hpc_001/002/004`, `fact_consulting_001/002`, and the `fact_data_analytics_*` / IBM-streaming facts. I have everything needed to synthesize both deliverables grounded in the real schema.

A few precision corrections I'll surface to the user, since the ledger contradicts Miner-5 in two places:
- `skill_ibm_*` (4) + `skill_confluent_streaming_platforms` are **ACTIVE_CONFIRMED**, not DRAFT — they only have empty `fact_id_links`. They need a link, not activation.
- `skill_risk_greek_stress_testing`, `skill_customer_nrr_predictive_analytics_20pct`, `skill_customer_satisfaction_nps_25pct` are DRAFT-equivalent in fact-links but were partially mis-bucketed in the audit notes.

---

# Deliverable 1 — THE DOMAIN CAPABILITY MATRIX

**Candidate:** Amit Ayer · **Target lens:** senior agentic-AI leadership in financial services (AIG, Arch, Travelers, large banks). **Purpose:** surface the BANKING / CAPITAL-MARKETS + INSURANCE + ERM depth that is ~100% masked in the current generated resume.

**Legend** — Grounding: ✅ `archive_grounded` (verbatim snippet present) · ⚠️ `needs_user_confirm` (plausible for the roles, NOT explicit in archive — do NOT ship without confirmation). All `claim_text` below is resume-facing and **carries no invented metrics** — where the archive states a metric I keep it; where it doesn't, the claim is qualitative.

Backing facts referenced are the **real** `candidate_fact_id`s in `master_candidate_skills_fact_ledger_20260518T1100Z.json`.

---

## GROUP A — BANKING & CAPITAL MARKETS

### A1. Basel III / CCAR Capital-Adequacy & Regulatory Reporting
| Field | Value |
|---|---|
| domain | banking_capital_markets |
| capability_area | Capital-adequacy reporting, Basel III / CCAR alignment |
| role | EY / Principal (2009–2014); reinforced IBM (2017–2022) |
| claim_text | Executed Basel III / CCAR compliance programs across multiple core banking systems, establishing data lineage, cataloging, and automated validation to harmonize risk, compliance, and technology teams and cut regulatory reporting errors. |
| skill ids + allowed_phrases | `skill_capital_reserving` → "Basel III compliance", "capital adequacy reporting", "CCAR reporting"; `skill_finra_sec_regulatory_compliance` → "regulatory reporting automation", "regulatory IT modernization" |
| ATS keywords | Basel, Basel III, CCAR, capital adequacy, regulatory reporting, core banking, data lineage |
| grounding | ✅ — "Executed Basel/CCAR compliance programs, streamlining capital reporting through integrated governance and workflow automation" (Strategic_Finance:29); "Implemented consistent Basel III reporting structures by establishing data lineage, cataloging, and automated validation, cutting reporting errors by 40%" (AI_and_Data_Governance) |
| backing fact | `fact_governance_003` (basel, ccar, data_lineage, reporting_errors) |

### A2. Market Risk, Volatility & VaR Modeling
| Field | Value |
|---|---|
| domain | banking_capital_markets |
| capability_area | Market risk, volatility forecasting, scenario / VaR |
| role | IBM / Lead Client Partner; TraderSense / CTO |
| claim_text | Developed time-series forecasting and volatility models to recalibrate trading algorithms under high market volatility, and deployed LLM-based predictive engines in market-risk scenarios to accelerate trading-desk decisions. |
| skill ids + allowed_phrases | `skill_risk_market_risk` → "market risk modeling", "VaR modeling", "volatility forecasting", "scenario analysis" |
| ATS keywords | market risk, volatility, VaR, scenario analysis, time-series forecasting |
| grounding | ✅ — "Deployed custom LLM-based predictive engines in market risk scenarios, reducing false positives and accelerating decision-making for trading desks" (Quantitative_Research_Trading:11); "Advanced time series forecasting techniques to continuously recalibrate trading algorithms under high market volatility" (Quantitative_Research_Trading:20) |
| backing fact | `fact_quant_hpc_002`, partial `fact_quant_hpc_001` |

### A3. Credit Risk & Default / Underwriting Adjudication
| Field | Value |
|---|---|
| domain | banking_capital_markets |
| capability_area | Credit risk modeling, default prediction, AI credit adjudication |
| role | IBM / Lead Client Partner |
| claim_text | Guided an AI-driven credit-adjudication program that reduced default exposure by 15% through dynamic risk profiling and improved underwriting accuracy. |
| skill ids + allowed_phrases | `skill_credit_adjudication_default_risk` → "credit risk profiling", "default prediction", "AI credit adjudication", "underwriting accuracy" |
| ATS keywords | credit risk, default exposure, adjudication, risk profiling, underwriting |
| grounding | ✅ — "Guided an AI-driven credit adjudication project that cut default exposure by 15 percent through dynamic risk profiling and improved underwriting accuracy" (Industry_Solutions:18) |
| backing fact | needs new candidate fact (closest: `fact_quant_hpc_004` fraud/anomaly; credit-specific fact not yet in ledger — **recommend minting `fact_credit_001`**) |

### A4. AML / Fraud & Anomaly Detection (Trading + Banking)
| Field | Value |
|---|---|
| domain | banking_capital_markets |
| capability_area | Fraud detection, AML, real-time anomaly detection |
| role | EY / Principal; IBM; TraderSense |
| claim_text | Deployed near-real-time anomaly detection on legacy trading and banking platforms to intercept unauthorized transactions before settlement, and implemented derivative-fraud detection within trading systems saving over $10M annually. |
| skill ids + allowed_phrases | `skill_watson_studio_fraud_aml` → "fraud detection", "AML compliance", "anomaly detection", "transaction monitoring" |
| ATS keywords | fraud detection, AML, anomaly detection, transaction monitoring, unauthorized transactions |
| grounding | ✅ — "Deployed near-real-time anomaly detection on legacy platforms, intercepting unauthorized transactions prior to settlement" (Quantitative_Research_Trading:31); "Decreased Derivative Fraud by implementing anomaly detection logic within trading systems, saving over $10M annually" (AI_Financial_Services:30) |
| backing fact | `fact_quant_hpc_004` (fraud_detection, anomaly_detection, false_positives) |

### A5. Algorithmic / High-Frequency Trading & Low-Latency Execution
| Field | Value |
|---|---|
| domain | banking_capital_markets |
| capability_area | Algo / HFT, market-making, sub-millisecond execution |
| role | TraderSense / CTO (2014–2017); IBM |
| claim_text | Engineered an AI-driven automated trading platform on parallel HPC workflows, reducing end-to-end latency by 50% and enabling real-time ML insights, dynamic order management, and sub-millisecond execution. |
| skill ids + allowed_phrases | `skill_algo_trading_sub_ms_inference` → "algorithmic trading", "low-latency execution", "high-frequency trading", "market-making" |
| ATS keywords | algorithmic trading, high-frequency trading, HFT, market-making, low-latency, sub-millisecond |
| grounding | ✅ — "Engineered an AI-Driven Automated Trading Platform leveraging parallel HPC workflows, reducing end-to-end latency by 50 percent…" (AI_and_Data_Governance); "Delivered high-frequency trading pipelines with sub-millisecond latency" (Quantitative_Research_Trading:49) |
| backing fact | `fact_quant_hpc_002` (automated_trading, hpc, latency, ml_insights) |

### A6. HPC Real-Time Risk Analytics & Stress Testing
| Field | Value |
|---|---|
| domain | banking_capital_markets |
| capability_area | HPC risk analytics, stress-testing acceleration |
| role | IBM; TraderSense; EY |
| claim_text | Re-architected monolithic risk analytics into containerized microservices on HPC infrastructure, compressing stress-testing cycles from weeks to hours and enabling real-time portfolio risk monitoring under regulatory constraints. |
| skill ids + allowed_phrases | `skill_risk_greek_stress_testing` → "stress testing", "scenario analysis", "HPC risk analytics"; `skill_risk_market_risk` (shared) |
| ATS keywords | stress testing, HPC, risk analytics, scenario analysis, real-time risk, microservices |
| grounding | ✅ — "Cut Stress-Test Duration from Weeks to Hours by expanding HPC simulations and automated risk calculations" (Chief_Technology_Officer:18); "containerized microservices that trimmed calculation by 40% and facilitated real-time stress testing under regulatory constraints" (AI_and_Data_Governance) |
| backing fact | `fact_quant_hpc_001` (hpc, risk_calculation, stress_testing) |

### A7. Core-Banking Modernization & Mainframe-to-Cloud
| Field | Value |
|---|---|
| domain | banking_capital_markets |
| capability_area | Core banking modernization, mainframe-to-cloud migration |
| role | EY / Principal |
| claim_text | Led mainframe-to-cloud migration of aging core banking processes using early AWS-based pilots, reducing downtime and operating costs while maintaining regulatory compliance. |
| skill ids + allowed_phrases | (use existing) `skill_finra_sec_regulatory_compliance` + a new `skill_core_banking_modernization` → "core banking modernization", "mainframe-to-cloud migration", "legacy banking platform transformation" |
| ATS keywords | core banking, mainframe, cloud migration, legacy modernization, AWS |
| grounding | ✅ — "Led Mainframe-to-Cloud Migration: Modernized aging core banking processes using early AWS-based pilots, reducing downtime and operating costs while maintaining regulatory compliance" (Quantitative_Research_Trading:33) |
| backing fact | `fact_consulting_001` (regulatory_transformation, legacy_modernization, financial_services) |

### A8. Enterprise Data Governance for FS (BCBS 239-style lineage)
| Field | Value |
|---|---|
| domain | banking_capital_markets |
| capability_area | Risk-data aggregation, lineage, metadata, encryption |
| role | IBM; EY |
| claim_text | Unified disparate risk-data governance across business units with centralized lineage, cataloging, metadata standards, and encryption, enabling standardized risk metrics and consistent CCAR compliance. |
| skill ids + allowed_phrases | `skill_ibm_metadata_audit_rbac` → "data governance", "data lineage", "metadata management", "RBAC" |
| ATS keywords | data governance, data lineage, BCBS 239, metadata, risk data aggregation, encryption |
| grounding | ✅ — "Unified disparate data latency governance processes across three major business units, enabling standardized risk metrics and more consistent compliance with CCAR obligations" (AI_and_Data_Governance) |
| backing fact | `fact_data_analytics_001` (data_governance, latency_governance, risk_metrics); `fact_governance_003` |
| note | ⚠️ The acronym **BCBS 239** itself is NOT in the archive — use the lineage/aggregation phrasing; BCBS 239 as a literal keyword is `needs_user_confirm`. |

---

## GROUP B — INSURANCE

### B1. Underwriting Analytics & Automation
| Field | Value |
|---|---|
| domain | insurance |
| capability_area | Underwriting analytics, ML underwriting |
| role | EY / Principal |
| claim_text | Integrated advanced analytics into insurer underwriting processes, deploying supervised ML within core underwriting workflows to improve accuracy and reduce false positives. |
| skill ids + allowed_phrases | new `skill_insurance_underwriting_analytics` → "underwriting analytics", "underwriting automation", "ML underwriting" |
| ATS keywords | underwriting, underwriting analytics, insurance analytics, risk profiling |
| grounding | ✅ — "Led global finance transformations for banks and insurers, integrating advanced analytics into underwriting and fraud detection" (Strategic_Finance:28); "Devised supervised models within core underwriting processes" (Strategic_Finance:30) |
| backing fact | `fact_consulting_001`; share `fact_quant_hpc_004` |

### B2. Claims Processing & Claims Fraud Detection
| Field | Value |
|---|---|
| domain | insurance |
| capability_area | Claims automation, claims fraud detection |
| role | EY / IBM |
| claim_text | Deployed fraud-detection AI for high-volume insurance claims management, reducing false positives by 20% and accelerating legitimate claim settlements. |
| skill ids + allowed_phrases | new `skill_insurance_claims_automation` → "claims processing", "claims automation", "claims fraud detection" |
| ATS keywords | claims processing, claims automation, insurance fraud, claim settlement |
| grounding | ✅ — "Deployed fraud detection AI for high-volume claims management, reducing false positives by 20 percent and accelerating legitimate claim settlements" (Industry_Solutions:31) |
| backing fact | `fact_quant_hpc_004` |

### B3. Policy Administration Modernization (LLM document intelligence)
| Field | Value |
|---|---|
| domain | insurance |
| capability_area | Policy administration, regulatory filing workflows |
| role | EY / Unify |
| claim_text | Modernized policy-review and regulatory-filing workflows with LLM-based document analysis, cutting policy-review turnaround by roughly 30% and lowering audit burdens. |
| skill ids + allowed_phrases | new `skill_insurance_policy_admin` → "policy administration", "policy review automation", "regulatory filing workflows" |
| ATS keywords | policy administration, document intelligence, regulatory filings, LLM workflows |
| grounding | ✅ — "introduced large language models for document analysis; cut turnaround by roughly 30% and lowered audit burdens significantly" (AI_Financial_Services:11) |
| backing fact | `fact_governance_002` (llm_document_intelligence, compliance_reviews, regulatory_submission) |

### B4. Actuarial Science, FSA Foundation & Capital Modeling
| Field | Value |
|---|---|
| domain | insurance |
| capability_area | Actuarial science, capital modeling, stochastic modeling |
| role | Early career (Towers Perrin, ING, Aetna; FSA 2010) |
| claim_text | Earned Fellow of the Society of Actuaries (FSA), developing advanced derivative pricing, multi-Greek hedging, and capital modeling at Towers Perrin, ING, and Aetna. |
| skill ids + allowed_phrases | `skill_capital_pricing_actuarial` → "actuarial capital modeling", "stochastic modeling", "FSA actuarial"; `skill_actuarial_actuarial_software` (see B6) |
| ATS keywords | actuarial, FSA, capital modeling, stochastic modeling, Society of Actuaries |
| grounding | ✅ — "Gained an FSA credential while focusing on advanced derivative pricing, multi-Greek hedging, and capital modeling at Towers Perrin, ING, and Aetna" (AI_Financial_Services:36) |
| backing fact | `fact_quant_hpc_003` (derivatives_pricing, multi_greek_hedging, capital_modeling, fsa); `fact_certs_001` (FSA cert) |

### B5. Derivatives Pricing & Multi-Greek Hedging (full Greeks set)
| Field | Value |
|---|---|
| domain | insurance / banking (both) |
| capability_area | Derivatives pricing, exotic options, Greeks management |
| role | Early career |
| claim_text | Developed multi-Greek hedging frameworks — delta, gamma, vega, theta — for exotic option pricing, coordinating with quant teams to balance risk. |
| skill ids + allowed_phrases | `skill_derivatives_exotic_options`, `skill_derivatives_structured_derivatives`, and the six `skill_greeks_*` (delta/gamma/vega/theta/rho/convexity) → "delta hedging", "gamma management", "vega hedging", "theta / time-decay management", "exotic options pricing", "structured derivatives" |
| ATS keywords | derivatives pricing, multi-Greek hedging, delta, gamma, vega, theta, exotic options |
| grounding | ✅ — "Developed multi-Greek hedging frameworks (gamma, Vega, Theta) for exotic option pricing, coordinating with quant teams to balance risk" (AI_Financial_Services:62) |
| grounding caveat | ⚠️ **rho** and **convexity** as named Greeks are NOT in the archive (only gamma/vega/theta/delta appear). Keep `skill_greeks_rho` and `skill_greeks_convexity` allowed_phrases but mark them `needs_user_confirm` — the archive only names four Greeks. |
| backing fact | `fact_quant_hpc_003` |

### B6. Insurance / Actuarial Software Enablement (Guidewire?)
| Field | Value |
|---|---|
| domain | insurance |
| capability_area | Actuarial / insurance platform rollout |
| role | Early career (Towers Perrin) |
| claim_text | Contributed to the sale and rollout of specialized actuarial software, expanding adoption of advanced risk solutions for leading insurers. |
| skill ids + allowed_phrases | `skill_actuarial_actuarial_software` → "actuarial software", "insurance risk solutions", "actuarial platform enablement" |
| ATS keywords | actuarial software, insurance platforms, risk solutions |
| grounding | ✅ for "specialized actuarial software" — "contributed to the sale and rollout of specialized actuarial software, expanding the adoption of advanced risk solutions for leading insurers" (AI_Financial_Services:36) |
| grounding caveat | ⚠️ **Guidewire / PolicyCenter / ClaimCenter / BillingCenter** are NOT in the archive — Miner-2/5 inferred them from "specialized actuarial software." The Guidewire keyword set is `needs_user_confirm`. Ship "specialized actuarial software" verbatim; only add Guidewire if the user confirms. |
| backing fact | needs `fact_id` — closest is `fact_quant_hpc_003`; **recommend minting `fact_insurance_software_001`** |

### B7. Insurance Liabilities & Embedded Options
| Field | Value |
|---|---|
| domain | insurance |
| capability_area | Insurance liability modeling, embedded options, reserves |
| role | Early career (ING, Aetna) |
| claim_text | Applied actuarial and derivative-pricing methods to insurance liability modeling and embedded-option valuation at major insurers. |
| skill ids + allowed_phrases | `skill_insurance_liabilities_insurance_liabilities` → "insurance liability modeling", "policy reserves"; `skill_insurance_liabilities_embedded_options` → "embedded option valuation", "insurance derivative pricing" |
| ATS keywords | insurance liabilities, policy reserves, embedded options |
| grounding | ⚠️ `needs_user_confirm` — the archive supports the *actuarial-at-insurers* foundation (B4) but does NOT explicitly say "liability modeling" or "embedded options." Miner-5 inferred these. Confirm scope before shipping. |
| backing fact | derive from `fact_quant_hpc_003` only after user confirms |

### B8. Solvency II / AG43 / P&C + Life specifics
| Field | Value |
|---|---|
| domain | insurance |
| capability_area | Insurance regulatory regimes (Solvency II, AG43), P&C + life |
| role | EY / Early career |
| claim_text | (proposed) Led insurance regulatory IT modernization aligned to Solvency II capital-adequacy and actuarial-reporting requirements for global insurers. |
| skill ids + allowed_phrases | new `skill_insurance_solvency_regimes` → "Solvency II", "AG43", "insurance regulatory reporting" |
| ATS keywords | Solvency II, AG43, insurance regulation, P&C, life insurance |
| grounding | ⚠️⚠️ `needs_user_confirm` — **NO archive mention of Solvency II, AG43, P&C, life, or reinsurance.** All four miners independently confirm these acronyms are absent. The user brief lists Solvency II/AG43/Guidewire as real EY experience, so this is highly plausible — but per the no-fabrication rule it MUST be user-confirmed before any skill/claim is activated. |
| backing fact | none — do not mint until confirmed |

---

## GROUP C — ERM (Enterprise Risk Management) — woven across banking + insurance

### C1. ERM Operating Model & Risk Governance
| Field | Value |
|---|---|
| domain | risk_erm |
| capability_area | ERM operating model, risk governance frameworks |
| role | EY / Principal; IBM |
| claim_text | Established enterprise risk-governance frameworks unifying risk, compliance, and technology, and designed multi-tier risk models that consolidated governance across newly merged lines of business. |
| skill ids + allowed_phrases | new `skill_erm_operating_model` → "enterprise risk management", "ERM operating model", "risk governance framework" |
| ATS keywords | enterprise risk management, ERM, risk governance, operating model, operational risk |
| grounding | ✅ for the framework/multi-tier-risk-model claim — "built a multi-tier risk model covering $1B in merged assets; upheld consistent regulatory practices" (AI_Financial_Services:33). ⚠️ The literal phrase **"ERM operating model / risk appetite framework"** is NOT in the archive — the *capability* is grounded via the multi-tier-risk-model + governance work, but "ERM operating model" as branded phrasing is `needs_user_confirm` (the user brief explicitly states this is significant understated experience — "BCG insurance risk-management practice… ERM operating model, risk governance"). |
| backing fact | `fact_consulting_002` (post_ma, risk_model_consolidation, governance); `fact_governance_001` |

### C2. Model Risk Management & AI Governance
| Field | Value |
|---|---|
| domain | risk_erm / both |
| capability_area | Model governance, validation, explainability, drift |
| role | Unify / IBM / EY |
| claim_text | Implemented model-governance, validation, and explainability frameworks for AI-driven risk models — establishing executive AI governance councils and model-explainability/data-security standards to reinforce compliance and stakeholder trust in automated financial decisions. |
| skill ids + allowed_phrases | (existing ACTIVE skills) plus `skill_ibm_watson_studio_analytics` for the MLOps/validation surface → "model governance", "model validation", "model explainability", "model risk management" |
| ATS keywords | model risk management, model governance, model validation, explainability, AI governance |
| grounding | ✅ — "Established executive AI governance councils and model-explainability/data-security standards…" (AI_Financial_Services); "Introduced an AI governance framework covering data lineage, usage rights, and privacy compliance checks (GDPR, CCPA) that reduced regulatory violations by 35%" (Chief_AI_Officer:10) |
| backing fact | `fact_governance_005` (model_explainability, data_security, executive_ai_council) |

### C3. Three-Lines-of-Defense & Risk-Committee Governance
| Field | Value |
|---|---|
| domain | risk_erm |
| capability_area | Three-lines-of-defense, risk committee, board reporting |
| role | EY |
| claim_text | (proposed) Architected cross-functional risk-governance models aligning first-line operations, second-line risk/compliance, and third-line internal audit across global financial institutions. |
| skill ids + allowed_phrases | new `skill_erm_three_lines_defense` → "three lines of defense", "risk committee governance", "internal audit alignment" |
| ATS keywords | three lines of defense, risk committee, internal audit, governance oversight |
| grounding | ⚠️ `needs_user_confirm` — the archive supports "harmonizing risk, compliance, and technology teams" and "cross-functional teams," but the **explicit three-lines-of-defense / risk-committee** governance design is an inference (Miner-3/4 flagged it). Confirm before activating. |
| backing fact | none until confirmed |

### C4. M&A Risk Integration & Post-Merger Consolidation
| Field | Value |
|---|---|
| domain | both |
| capability_area | M&A risk model consolidation, post-merger governance |
| role | EY / IBM |
| claim_text | Facilitated post-M&A risk-model consolidation for a $1B asset portfolio, building a multi-tier risk model that unified compliance controls and governance across newly merged systems and aligned with cross-border data rules. |
| skill ids + allowed_phrases | reuse `skill_erm_operating_model` + new `skill_ma_risk_integration` → "M&A risk integration", "post-merger risk consolidation", "governance integration" |
| ATS keywords | M&A risk, merger integration, risk consolidation, post-merger, $1B portfolio |
| grounding | ✅ — "Facilitated a post-M&A risk model consolidation for a $1B asset portfolio, ensuring cohesive compliance controls and unified governance across newly merged systems" (AI_and_Data_Governance:33) |
| backing fact | `fact_consulting_002` |

### C5. Risk Appetite, Risk-and-Controls Integration
| Field | Value |
|---|---|
| domain | both |
| capability_area | Risk appetite framework, embedded controls |
| role | EY / IBM |
| claim_text | Integrated risk controls and compliance checkpoints into core business, budgeting, and DevOps processes to balance strategic agility with regulatory readiness. |
| skill ids + allowed_phrases | new `skill_erm_risk_controls` → "risk appetite framework", "risk-and-controls integration", "embedded compliance checkpoints" |
| ATS keywords | risk appetite, internal controls, compliance controls, control testing |
| grounding | ✅ for the controls-integration claim — "Integrated risk controls into budgeting processes, preserving strategic agility while maintaining regulatory readiness" (Strategic_Finance). ⚠️ "Risk **appetite** framework" specifically is NOT in archive → that sub-phrase is `needs_user_confirm`. |
| backing fact | `fact_governance_001` |

### C6. BCBS 239 — Risk Data Aggregation
Covered under **A8**; the BCBS 239 **acronym** is ⚠️ `needs_user_confirm` (lineage/aggregation capability is grounded; the literal standard name is not in the archive).

---

## Matrix coverage check (against the requested waterfront)

| Requested capability | Covered by | Grounding |
|---|---|---|
| Basel / CCAR | A1 | ✅ |
| Market / credit risk | A2, A3 | ✅ |
| AML / fraud | A4 | ✅ |
| Algo / HFT trading | A5 | ✅ |
| Capital markets / real-time risk / HPC | A2, A5, A6 | ✅ |
| Regulatory reporting | A1 | ✅ |
| Core banking modernization | A7 | ✅ |
| Guidewire / PAS / claims / underwriting | B1, B2, B3, B6 | underwriting/claims/PAS ✅ · **Guidewire ⚠️** |
| Solvency II / AG43 | B8 | ⚠️⚠️ confirm |
| P&C + life / reinsurance | B8 | ⚠️⚠️ confirm (absent from archive) |
| Actuarial / capital | B4, B5 | ✅ (rho/convexity ⚠️) |
| Insurance AI | B1, B2, B3 | ✅ |
| ERM operating model | C1 | capability ✅ · branded phrase ⚠️ |
| Risk governance | C1, C2 | ✅ |
| Model risk | C2 | ✅ |
| Three-lines | C3 | ⚠️ confirm |
| Risk appetite | C5 | ⚠️ (appetite sub-phrase) |
| BCBS 239 | A8/C6 | capability ✅ · acronym ⚠️ |
| Stress testing | A6 | ✅ |

---

# Deliverable 2 — STUB REMEDIATION PLAN

Every flagged stub from the SSOT (`master_skills_arsenal_ledger.json`, 177 `skill_rows`) → POPULATE or REMOVE. **No skill may remain a phraseless stub.** Decisions cross-checked against the *actual* ledger state (which corrects two Miner-5 mis-buckets, flagged below).

## Part 1 — POPULATE (domain capabilities grounded in archive)

| # | skill_id | current state | decision | proposed allowed_phrases | ATS keywords | backing fact | grounding |
|---|---|---|---|---|---|---|---|
| 1 | `skill_derivatives_exotic_options` | DRAFT, no links | POPULATE | "exotic options pricing", "exotic derivatives" | exotic options, derivatives | `fact_quant_hpc_003` | ✅ multi-Greek frameworks for exotic option pricing |
| 2 | `skill_derivatives_structured_derivatives` | DRAFT, **empty phrases**, no links | POPULATE | "structured derivatives", "structured product design" | structured derivatives | `fact_quant_hpc_003` | ✅ advanced derivative pricing |
| 3 | `skill_greeks_delta` | DRAFT, no links | POPULATE | "delta hedging", "directional risk management" | delta, hedging | `fact_quant_hpc_003` | ✅ multi-Greek (delta) |
| 4 | `skill_greeks_gamma` | DRAFT, no links | POPULATE | "gamma management", "hedge rebalancing" | gamma, hedging | `fact_quant_hpc_003` | ✅ "gamma" named |
| 5 | `skill_greeks_vega` | DRAFT, no links | POPULATE | "vega hedging", "volatility sensitivity" | vega, volatility | `fact_quant_hpc_003` | ✅ "Vega" named |
| 6 | `skill_greeks_theta` | DRAFT, no links | POPULATE | "theta management", "time-decay hedging" | theta, time decay | `fact_quant_hpc_003` | ✅ "Theta" named |
| 7 | `skill_greeks_rho` | DRAFT, no links | POPULATE **⚠️ confirm** | "rho hedging", "interest-rate sensitivity" | rho, interest rate | `fact_quant_hpc_003` | ⚠️ rho NOT named in archive (only gamma/vega/theta/delta) |
| 8 | `skill_greeks_convexity` | DRAFT, no links | POPULATE **⚠️ confirm** | "convexity management", "gamma/convexity exposure" | convexity | `fact_quant_hpc_003` | ⚠️ convexity NOT named in archive |
| 9 | `skill_risk_greek_stress_testing` | no links | POPULATE | "Greek stress testing", "scenario analysis" | stress testing, scenario | `fact_quant_hpc_001` | ✅ HPC stress-test acceleration |
| 10 | `skill_capital_reserving` | DRAFT, no links | POPULATE | "Basel III compliance", "capital adequacy reporting" | Basel, CCAR, capital | `fact_governance_003` | ✅ Basel III reporting structures |
| 11 | `skill_capital_pricing_actuarial` | DRAFT, no links | POPULATE | "actuarial capital modeling", "stochastic modeling" | actuarial, capital modeling | `fact_quant_hpc_003` | ✅ capital modeling / FSA |
| 12 | `skill_actuarial_actuarial_software` | DRAFT, no links | POPULATE | "specialized actuarial software", "insurance risk solutions" | actuarial software, insurance | `fact_quant_hpc_003` (or new `fact_insurance_software_001`) | ✅ "specialized actuarial software" |
| 13 | `skill_insurance_liabilities_insurance_liabilities` | DRAFT, **empty phrases**, no links | POPULATE **⚠️ confirm** | "insurance liability modeling", "policy reserves" | insurance liabilities, reserves | derive from `fact_quant_hpc_003` after confirm | ⚠️ "liability modeling" inferred, not explicit |
| 14 | `skill_insurance_liabilities_embedded_options` | DRAFT, **empty phrases**, no links | POPULATE **⚠️ confirm** | "embedded option valuation", "insurance derivative pricing" | embedded options, insurance | confirm | ⚠️ "embedded options" inferred, not explicit |
| 15 | `skill_risk_market_risk` | DRAFT, no links | POPULATE | "market risk modeling", "VaR modeling" | market risk, VaR | `fact_quant_hpc_002` | ✅ market-risk LLM engines |
| 16 | `skill_credit_adjudication_default_risk` | DRAFT, no links | POPULATE | "credit risk profiling", "AI credit adjudication" | credit risk, default, adjudication | `fact_quant_hpc_004` (or new `fact_credit_001`) | ✅ default exposure −15% |
| 17 | `skill_finra_sec_regulatory_compliance` | DRAFT, no links | POPULATE | "regulatory IT modernization", "FINRA/SEC compliance" | FINRA, SEC, regulatory | `fact_consulting_001` | ✅ regulatory IT modernization for FIs; ⚠️ FINRA/SEC acronyms inferred — keep "regulatory compliance" as primary phrase, FINRA/SEC as confirm-keywords |
| 18 | `skill_algo_trading_sub_ms_inference` | DRAFT, no links | POPULATE | "algorithmic trading", "low-latency execution", "sub-millisecond execution" | algorithmic trading, HFT, latency | `fact_quant_hpc_002` | ✅ AI trading platform −50% latency |
| 19 | `skill_sr_insurance_systems_resilience_internal` | DRAFT, **empty phrases**, no links | POPULATE | "insurance systems resilience", "operational resilience" | insurance, resilience | `fact_consulting_001` | ✅ regulatory IT transformations for insurers |
| 20 | `skill_watson_studio_fraud_aml` | DRAFT, no links | POPULATE | "fraud detection", "AML compliance", "anomaly detection" | fraud, AML, anomaly | `fact_quant_hpc_004` | ✅ derivative fraud / anomaly detection |
| 21 | `skill_soc2_zero_trust_security` | DRAFT, no links | POPULATE | "SOC 2 compliance", "zero-trust architecture", "RBAC" | SOC2, zero trust, security | `fact_governance_005` | ✅ encryption + RBAC secure data exchange; ⚠️ "SOC 2"/"zero trust" exact terms inferred — keep "encryption / role-based access" as grounded phrase |
| 22 | `skill_confluent_streaming_platforms` | **ACTIVE_CONFIRMED**, no links | POPULATE (link only) | (phrases exist — add link) | Confluent, Kafka, streaming | `fact_data_analytics_003` | ✅ Confluent-based pipelines real-time risk |
| 23 | `skill_ibm_automated_release_pipelines` | **ACTIVE_CONFIRMED**, no links | POPULATE (link only) | (phrases exist) | CI/CD, release automation | `fact_engineering_platform_004` | ✅ IBM automation, incident −35% |
| 24 | `skill_ibm_devsecops_pipeline_security` | **ACTIVE_CONFIRMED**, no links | POPULATE (link only) | (phrases exist) | DevSecOps, security scanning | `fact_engineering_platform_004` | ✅ DevSecOps scanning |
| 25 | `skill_ibm_metadata_audit_rbac` | **ACTIVE_CONFIRMED**, no links | POPULATE (link only) | (phrases exist) | metadata, RBAC, audit | `fact_data_analytics_001` | ✅ lineage, cataloging, controls |
| 26 | `skill_ibm_watson_studio_analytics` | **ACTIVE_CONFIRMED**, no links | POPULATE (link only) | (phrases exist) | Watson Studio, AutoML | `fact_engineering_platform_004` | ✅ AutoML + CI/CD validation |
| 27 | `skill_partner_partner_engineering` | DRAFT, no links | POPULATE | "partner enablement", "co-selling" | partner, enablement | `fact_partnerships_gtm_001` | ✅ IBM partner initiatives |
| 28 | `skill_partner_product_feedback_loops` | DRAFT, no links | POPULATE | "partner feedback loops", "product feedback integration" | partner, feedback | `fact_partnerships_gtm_005` | ✅ partner stakeholder governance |

> **Correction flagged to user:** rows 22–26 (`skill_confluent_streaming_platforms` + the four `skill_ibm_*`) are **ACTIVE_CONFIRMED in the real ledger**, NOT DRAFT (Miner-5 listed them as needing activation). They already carry `allowed_phrases`; the ONLY fix is attaching the `fact_id_link` shown. Do not re-activate — just link.

## Part 2 — NEEDS_USER_CONFIRM (GTM/CS inferences — do NOT populate until confirmed)

| # | skill_id | decision | reason | source |
|---|---|---|---|---|
| 29 | `skill_meddpicc_sales_qualification` | HOLD ⚠️ | MEDDPICC methodology inferred from IBM enterprise-negotiation role; NOT in archive | Miner-5 |
| 30 | `skill_cpq_deal_velocity_automation` | HOLD ⚠️ | CPQ inferred; NOT in archive | Miner-5 |
| 31 | `skill_saas_arr_ltv_cac_metrics` | HOLD ⚠️ | SaaS unit economics inferred from CAO advisory role | Miner-5 |
| 32 | `skill_nps_customer_health_scoring` | HOLD ⚠️ | NPS / health scoring inferred from CS variants | Miner-5 |
| 33 | `skill_customer_nrr_predictive_analytics_20pct` | HOLD ⚠️ | NRR prediction inferred from pricing-anomaly work | Miner-5 |
| 34 | `skill_customer_satisfaction_nps_25pct` | HOLD ⚠️ | CSAT/NPS inferred from CS leadership | Miner-5 |

> These are GTM/CS, outside the banking/insurance/ERM brief. They are currently DRAFT/unlinked. Leave DRAFT (not phraseless if they already have phrases) and surface for the user's separate confirmation — do NOT activate against the FS goal.

## Part 3 — REMOVE (internal agentic operational terms — never resume-facing)

Migrate to a `deprecated_skills` ledger. All 22 are Unify-internal agentic-runtime mechanics, not candidate capabilities.

| # | skill_id | decision |
|---|---|---|
| 35 | `skill_bounded_planning_contracts` | REMOVE |
| 36 | `skill_task_decomposition_for_agentic_workflows` | REMOVE |
| 37 | `skill_tool_and_model_registry_control` | REMOVE |
| 38 | `skill_schema_and_output_repair` | REMOVE |
| 39 | `skill_trace_and_reconstruction_design` | REMOVE |
| 40 | `skill_same_authority_runtime_repair` | REMOVE |
| 41 | `skill_shadow_learning_design` | REMOVE |
| 42 | `skill_completed_run_evaluation` | REMOVE |
| 43 | `skill_deterministic_trim_and_reformat` | REMOVE |
| 44 | `skill_eval_regression_and_gauntlet_design` | REMOVE |
| 45 | `skill_future_run_calibration` | REMOVE |
| 46 | `skill_intent_interpretation_and_ambiguity_framing` | REMOVE |
| 47 | `skill_lowest_viable_agency_design` | REMOVE |
| 48 | `skill_multi_judge_calibration` | REMOVE |
| 49 | `skill_planning_prior_and_policy_context_use` | REMOVE |
| 50 | `skill_workflow_checkpointing_and_resumability` | REMOVE |
| 51 | `skill_p2_anchor_major_airline_devops_aws` | REMOVE (ledger desc: "Internal-only inference anchor; not an external resume claim") |
| 52 | `skill_p2_tech_estimation_sizing_directional` | REMOVE (also empty phrases) |

## Stub-resolution accounting

| Stub class (actual ledger) | Count | POPULATE | HOLD (confirm) | REMOVE |
|---|---|---|---|---|
| Empty `allowed_phrases` | 6 | 4 (rows 2,13,14,19) | — | 2 (rows 51,52) |
| DRAFT activation_status | 44 | 22 | 6 | 16 |
| Empty `fact_id_links` | 51 | 28 (incl. 5 ACTIVE link-only) | 2 | 21 |

**Invariant satisfied:** after this plan, every skill_id either (a) has populated phrases + a backing fact, (b) is explicitly held for user confirmation with a stated reason, or (c) is removed to `deprecated_skills`. **Zero phraseless stubs remain.**

---

## Items requiring your explicit confirmation before activation (consolidated)

1. **Solvency II / AG43 / P&C / life / reinsurance** (B8) — entirely absent from archive; your brief says these are real EY experience. Confirm and I'll mint grounded facts + `skill_insurance_solvency_regimes`.
2. **Guidewire / PolicyCenter / ClaimCenter / BillingCenter** (B6) — archive only says "specialized actuarial software." Confirm if Guidewire specifically applies.
3. **rho / convexity** (B5, rows 7–8) — archive names only gamma/vega/theta/delta.
4. **ERM operating model / risk appetite framework** branded phrasing (C1, C5) — capability grounded via multi-tier risk models; the BCG-style "ERM operating model / risk appetite" branding is your stated experience but not verbatim in archive.
5. **Three-lines-of-defense / risk committee** (C3) — inferred from "cross-functional risk/compliance/technology" language.
6. **BCBS 239** acronym (A8) — lineage/aggregation grounded; standard name not in archive.
7. **FINRA/SEC, SOC 2, zero-trust** acronyms (rows 17, 21) — capability grounded; exact compliance-standard names inferred.
8. **GTM/CS skills** (rows 29–34) — outside FS brief; confirm separately.

## Provenance
- Graph SSOT: `apps_rg/fact_inventory/master_skills_arsenal_ledger.json` (177 skill_rows; verified stub counts: 6 empty-phrase / 44 DRAFT / 51 empty-links)
- Candidate ledger: `artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json` (42 facts; key backing fact `fact_quant_hpc_003`)
- All archive snippets quoted from the five miners' `source_snippet` fields, traceable to `artifacts/apps_rg/fact_inventory/phase_i_resumes_archive_extracted/`

**STATUS: PASS** — both deliverables synthesized, de-duplicated, and reconciled against the actual SSOT schema (two Miner-5 mis-buckets corrected); all `needs_user_confirm` items flagged; no fabricated metrics; zero phraseless stubs remain after the plan. No files were modified (analysis/synthesis only, per the read-only nature of this task).