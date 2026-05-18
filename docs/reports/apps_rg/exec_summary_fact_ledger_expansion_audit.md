# Executive Summary Fact Ledger / SRFS Expansion Audit

Generated: 2026-05-18T19:17:30Z  
Proof run: `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260518_185251`  
X3: **X3_REVIEW_JUDGE_SOFT_FAIL** | Judges: Gemini 5.0, OpenAI 4.8, Anthropic 3.6 (threshold 4.0)  
X2: PASS

Companion machine inventory: `exec_summary_fact_ledger_expansion_audit.json`

---

## 1. Source map

| Role | Path |
|------|------|
| Master candidate skills/fact ledger | `artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json` |
| Role-family taxonomy | `apps_rg/config/domain_contract/master_role_family_taxonomy.yaml` |
| Base résumé fact store (locked) | `apps_rg/resume/base/amit_ayer_base_resume_v1.json` |
| Ledger loader / shape validation | `apps_rg/fact_inventory/candidate_fact_ledger.py` |
| SRFS selection (bounded) | `apps_rg/fact_inventory/selected_role_fact_set.py` |
| Runtime SRFS slice → `selected_fact_plan` | `apps_rg/runtime/sections/selected_role_fact_set.py` |
| Executive summary lane / judge packet | `apps_rg/runtime/sections/executive_summary_lane.py`, `apps_rg/runtime/judges/executive_summary_judge_packet.py` |
| X2 validators | `apps_rg/runtime/validators/executive_summary_x2.py` |
| Judge-safe prose repair | `apps_rg/runtime/sections/exec_summary_srfs_judge_safe.py` |
| Fact vector schema (C0 dense lane) | `apps_rg/config/domain_contract/fact_vectors_schema.yaml` |
| Active SRFS artifact (proof) | `artifacts/apps_rg/fact_inventory/selected_role_fact_set_20260518T181200Z_exec_summary_srfs_cli_proof.json` |

**allowed_fact_packet construction:** `executive_summary_lane` builds `selected_fact_plan` from the SRFS `executive_summary` slice via `slice_row_to_plan_fact` (HIGH confidence only). The judge packet’s `allowed_fact_packet` is that same list. Claim ledger canonicalization collapses `*_metric_*` derivatives to base `candidate_fact_id` when the base is in the slice.

**Schema today:** Ledger rows require `candidate_fact_id`, `claim_text`, `confidence`, `source_resume_variants`, `role_families_supported`. Optional: `capability_tags`, `metric_values`, `allowed_resume_use`, `risk_notes`, `domain_family`, `company`. There is **no** `allowed_phrases` / `blocked_phrases` / `support_level` field yet (proposed in W1).

---

## 2. Structural diagnosis (root cause)

**Headline consumes the richest agentic/runtime facts before executive_summary allocation.**

In `select_candidate_facts_for_role`, `_take_unique(high_sorted_global, 5)` runs for **headline** first, marking facts in `used_global`. `_allocate_exec_summary_facts` then walks the **remaining** pool with `max_per_domain_family=2`.

For the proof SRFS artifact:

| Section | Selected fact_ids |
|---------|-------------------|
| **headline** (5) | `fact_consulting_001`, `fact_engineering_platform_001`–`004` |
| **executive_summary** (7) | `fact_engineering_platform_005`, `006`, `fact_exec_002`, `fact_certs_001`, `fact_governance_003`, `fact_quant_hpc_001`, `002` |

Facts **001–004** contain deterministic routing, GraphRAG, sandboxed execution, evaluation gates, and lifecycle metrics — but they are **not** in the executive_summary `allowed_fact_packet`. The model’s S1 thesis therefore leans on `fact_engineering_platform_005` (“cloud-native microservices…”) which lacks “agentic” in `claim_text`, producing a generic opening (Anthropic finding). S5 falls back to meta phrasing (“with the executive platform record above”) because `fact_certs_001` is atomic and not bundled for synthesis.

This is a **selection-shape** problem, not missing ledger rows: `fact_engineering_platform_001` already exists at HIGH confidence with full agentic vocabulary.

---

## 3. Gap analysis (18 concepts)

| Concept | In ledger | In exec SRFS slice | Status |
|---------|-----------|-------------------|--------|
| governed agentic AI runtime | 001, 006 | 006 only | partial — weak S1 vocabulary |
| deterministic routing | 001 | — | ledger only (headline) |
| managed multi-step orchestration | 001 | — | ledger only |
| graph-aware retrieval / GraphRAG | 001, 002 | — | ledger only |
| vector retrieval | 003, 005 | 005 | exec slice |
| prompt assembly | 003 | — | ledger only |
| bounded / sandboxed execution | 001 | — | ledger only |
| policy enforcement | 001, 003 | — | ledger only |
| replayable traces | 001, 003 | — | ledger only |
| evaluation gates | 003, governance_003 | governance_003 | partial |
| human escalation / HITL | — | — | **missing** (base bullet implies governance; no ledger row) |
| reusable platform IP | 006 | 006 | exec slice |
| commercialization | 006 + GTM rows | 006 | exec slice |
| AI revenue / margin metrics | 006 | 006 | exec slice |
| ML org scale | 006, exec_002 | both | exec slice |
| AWS / Databricks credentials | 005, certs_001 | both | exec slice |
| FSA / actuarial / Basel / CCAR | governance_003, certs_001, analytics | governance_003, certs_001 | exec slice |
| regulated enterprise governance | multiple | governance_003 | partial |

---

## 4. Proposed support levels (constraint relaxation without weakening proof)

| Level | Rule |
|-------|------|
| **DIRECT** | Atomic `claim_text` allowed when `fact_id` is in section SRFS slice and cited in `claim_ledger`. |
| **METRIC_DIRECT** | Numeric tokens only as stated in `metric_values` / `claim_text`; cite owning `fact_id`. |
| **BUNDLE_SUPPORTED** | Synthesis sentence allowed only when **all** `supporting_fact_ids` are in the section slice and a registered bundle rule exists. |
| **DERIVED_SUPPORTED** | Approved semantic compression (e.g. integrated S5 credentials) with explicit derivation registry; no new entities. |
| **TARGETING_ONLY** | JD/briefing/target role may reorder emphasis; **never** in `source_fact_ids`. |
| **STYLE_ONLY** | Base résumé register hints; never proof. |
| **BLOCKED** | Emitted phrase fails X2/judge (e.g. “executive platform record above”, “applied depth”). |

X2 and judge thresholds stay unchanged; relaxation is **which facts/phrases are eligible**, not gate pass criteria.

---

## 5. Current ledger inventory (summary)

- **42** candidate facts in master ledger; **13** HIGH (external-selection eligible).
- **7** facts in executive_summary SRFS slice for proof run.
- Full per-row inventory (claim_text, evidence, tags, sections, judge issues): JSON `fact_inventory[]`.

**Executive_summary output facts (claim_ledger):** `fact_engineering_platform_005`, `006`, `fact_governance_003`, `fact_exec_002`, `fact_certs_001`.

**Judge issues (Anthropic 3.6, non-decisive):**

- S1 generic — no “agentic” in primary mechanism fact (005).
- S2 softened 40% metric available in `fact_governance_003`.
- S5 meta-narration / credential inventory on `fact_certs_001`.

---

## 6. Proposed new facts (DRAFT_INACTIVE — do not activate)

| fact_id | support_level | supporting_fact_ids | Purpose |
|---------|---------------|---------------------|---------|
| `fact_agentic_runtime_001` | BUNDLE_SUPPORTED | 001, 003 | Exec S1/S2 agentic runtime vocabulary |
| `fact_agentic_orchestration_001` | DERIVED_SUPPORTED | 001 | Orchestration + sandbox + HITL phrasing |
| `fact_graph_rag_001` | BUNDLE_SUPPORTED | 001, 002 | GraphRAG + dependency graph |
| `fact_ai_governance_runtime_001` | BUNDLE_SUPPORTED | 003, governance_003 | Gates + 40% auditability bundle |
| `fact_platform_commercialization_001` | METRIC_DIRECT | 006 | S4 commercialization without team duplicate |
| `fact_exec_scale_001` | METRIC_DIRECT | exec_002, 006 | S4 org scale canonical |
| `fact_quant_credential_001` | DERIVED_SUPPORTED | certs_001 | S5 integrated credentials (ban meta anchors) |
| `fact_cloud_data_platform_001` | DIRECT | 005 | S2 mechanism alias |

Each draft includes `allowed_phrases`, `forbidden_phrases_without_support`, `evidence_source` (base résumé bullets), and `risk_notes` in JSON.

---

## 7. Executive summary SRFS selection recommendation

**Principle:** Reserve agentic/runtime vocabulary for the executive_summary slice. Prevent headline from exclusively consuming `fact_engineering_platform_001`–`004`, or add `exec_summary_reserved_fact_ids` before headline `_take_unique`.

**Target composition (7–10 facts):**

1. **Architecture/runtime (2–3):** `fact_agentic_runtime_001` (draft) or promote **001**; `fact_cloud_data_platform_001` / **005**; optional `fact_graph_rag_001` (draft).
2. **Governance/evidence (1–2):** `fact_ai_governance_runtime_001` (draft) or **governance_003** (surface 40% in S2).
3. **Commercialization (1):** `fact_platform_commercialization_001` (draft) or **006**.
4. **Org scale (1):** `fact_exec_scale_001` (draft) or **exec_002**.
5. **Credential/quant (1):** `fact_quant_credential_001` (draft) for S5 synthesis, citing **certs_001** only.
6. **Targeting (non-proof):** JD + briefing as **TARGETING_ONLY** — emphasis only, never `source_fact_ids`.

**Selector changes (W2):**

- Reserve `fact_engineering_platform_001` (and optionally 003) for executive_summary when `ENGINEERING_PLATFORM` is top-2 role family.
- Relax `max_per_domain_family` for exec slice when a BUNDLE_SUPPORTED row is present.
- Deprioritize `fact_quant_hpc_*` in exec pool when agentic JD signals dominate (IBM lane facts remain for ibm_* sections).
- Cross-section dedup: headline may share capability_tags but must not lock out exec claim vocabulary.

**S5 template (judge-safe):** Integrate FSA + AWS + Databricks as credibility for governed agentic platform design in regulated financial services — cite `fact_certs_001`; forbid phrases in `exec_summary_srfs_judge_safe.py` (`platform record above`, `applied depth`, etc.).

---

## 8. Implementation waves

| Wave | Scope | Runtime change |
|------|--------|----------------|
| W1 | Add `support_level`, `allowed_phrases`, `blocked_phrases`, `bundle_rules` to ledger schema + contract tests | No |
| W2 | SRFS selector: `exec_summary_reserved_fact_ids` + headline/exec dedup | Yes |
| W3 | Human-confirm and activate DRAFT facts in master ledger | Yes (data) |
| W4 | DERIVED_SUPPORTED registry + X2 bundle gate (`supporting_fact_ids` ⊆ slice) | Yes |
| W5 | Re-run real exec_summary proof; target Anthropic ≥ 4.0 without threshold changes | No (verify) |

---

## 9. Constraints preserved

- No `agentic_core` changes
- No X2 / X3 / judge threshold weakening
- No JD or briefing as proof
- No mocks/stubs for proof claims
- No runtime generation patch in this audit
- Preserve canonical `source_fact_ids` (no invented experience)

---

## 10. Caveat

Master ledger `status` is `candidate_ledger_requires_human_confirmation`; HIGH rows use `allowed_resume_use: allowed_after_human_confirm`. Proposed facts are **DRAFT_INACTIVE**. This audit did not re-run generation or modify runtime lanes.
