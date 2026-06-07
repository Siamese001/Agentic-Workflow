# Case Study — Submitted-Document Evidence Sufficiency Gate

> **Honesty boundary.** This is a **production-grade / client-style** implementation
> built and tested against **synthetic** documents. The code is structured the way
> a deployed gate would be (deterministic core, immutable contract handoff, fail-closed
> behavior, audit fields), but it has **not** been deployed against real customers and
> makes **no** real binding credit or insurance decisions. Every document value in the
> fixtures is fabricated; there is no real PII.

---

## 1. One-paragraph project summary

I implemented the submitted-document evidence sufficiency gate for an AI-assisted
underwriting workflow. The gate sat between intake and decision assembly. It converted
synthetic submitted documents into a deterministic `FinalEvidenceContract` containing
document coverage, extracted evidence spans, contradiction flags, missing-evidence flags,
and a support score. Downstream rationale generation and decision-packet assembly were
forced to consume this contract, which prevented unsupported explanations and allowed the
system to fail closed when evidence was incomplete or internally contradictory.

---

## 2. Business problem

- **Underwriters receive incomplete and inconsistent document packets.** Real intake is
  messy: a tax return arrives but the bank statement does not; a credit report says one
  thing and the bank statement implies another. Someone has to decide whether there is
  *enough* document-backed evidence to even attempt a decision.
- **AI assistants sound confident even when the evidence is weak.** A language model will
  happily produce a fluent, authoritative-sounding rationale for an approval that the
  underlying documents do not support. In a regulated workflow that is a liability, not a
  feature.
- **Regulated workflows need traceability, deterministic fallback, and human-review
  triggers.** Every field that influences a decision must trace back to a specific
  submitted document. When evidence is insufficient or contradictory, the system must
  degrade to a safe state and route to a human — never paper over the gap with prose.

The gate exists to answer one question deterministically and auditably: *does this packet
have enough document-backed evidence to proceed, and is it internally consistent?*

---

## 3. Exact workflow boundaries

**In scope**
- Submitted-document inspection and document-class normalization
- Required/optional evidence coverage check
- Deterministic extraction of fields from submitted document dicts
- Deterministic per-span evidence IDs
- Cross-document contradiction detection
- Support scoring and `PASS / WEAK_WITH_CAVEATS / FAIL` state
- Emission of the immutable `FinalEvidenceContract`
- The downstream constraint that the PA compiler / LLM firewall consume only the contract

**Out of scope (deliberately)**
- Real policy issuance or binding decisions
- Real actuarial pricing / risk-tier models
- Real customer PII
- Open-web enrichment or any external API call
- Durable state writes (the gate writes nothing)
- Automatic binding decision-making
- Model training

---

## 4. Architecture (ASCII)

```
SubmittedDocuments  (synthetic dicts: document_class + flat fields)
        │
        ▼
UnderwritingC0Adapter            ← the gate (deterministic, fail-closed)
   ├─ classify document classes
   ├─ coverage check (required / optional)
   ├─ field-span extraction (submitted fields only)
   ├─ deterministic evidence IDs
   ├─ support-score calculation
   └─ contradiction detection
        │
        ▼
FinalEvidenceContract            ← the central, immutable artifact
   (c0_state, evidence_ids, support_score, contradiction_flags, …)
        │
        ▼
PA Compiler  →  LLM Firewall     ← consume the contract as the evidence allowlist;
   (binds verdict_hash +            verdict + reason codes hashed & locked before any
    reason_codes_hash)              LLM call; deterministic citation allowlist rejects
                                    fabricated evidence IDs; LLM writes prose only
        │
        ▼
DecisionPacket  →  Exit / Readiness review
   (rationale can cite only valid evidence IDs; fail-closed states documented)
```

> **Wiring note (honest seam).** The firewall public seam
> (`UnderwritingLLMFirewall.gate`) accepts a `FinalEvidenceContract` dict and the focused
> tests prove citation allowlisting at that seam. `DecisionPacketAssembler.assemble` now
> accepts an optional `c0_bundle=` so a caller can pass the real contract through; when it is
> omitted, the assembler uses a firewall-valid **legacy fallback bundle that carries no
> evidence IDs** (so no LLM evidence citation can be accepted). End-to-end auto-wiring of the
> C0 contract into the full pipeline remains a documented integration seam.

---

## 5. Data contract walkthrough — every `FinalEvidenceContract` field

| Field | Plain-English meaning |
|---|---|
| `c0_mode` | Always `SUBMITTED_DOCUMENT_EVIDENCE_ONLY`. Declares the only evidence source the gate is allowed to use. |
| `c0_state` | `PASS`, `WEAK_WITH_CAVEATS`, or `FAIL`. The headline disposition. |
| `open_web_blocked` | Always `True`. A hard invariant: the gate never reaches the internet. |
| `evidence_contract_id` | Deterministic `fec-…` SHA-256 ID derived from a canonical representation of the submitted document **values** (normalized class + field names + field values) + policy hash. Same packet → same ID; **change any submitted field value → the ID changes** (auditability). |
| `evidence_ids` | List of per-span IDs (e.g. `ev-BANK_STA-<hash>`). One per extracted field. Each ID is value-aware and disambiguated by a document ordinal, so duplicate documents don't collide. The audit anchor. |
| `document_coverage_map` | `{document_class: present?}` — which classes were found in the packet. |
| `extracted_span_map` | `{evidence_id: {field_name, value, document_class, confidence, weight}}`. The actual extracted evidence, each keyed by its own ID. |
| `contradiction_flags` | List of triggered contradiction rule IDs (e.g. `INCOME_BALANCE_MISMATCH`). |
| `missing_evidence_flags` | Structured flags: `MISSING_DOC:<CLASS>` for an absent required class, `MISSING_FIELD:<CLASS>.<field>` for a present class missing a required field. |
| `support_score` | Float in `[0,1]`. Transparent weighted sum of coverage + extracted-span coverage. |
| `evidence_sufficiency` | `sufficient` / `partial` / `insufficient` — the human-readable twin of `c0_state`. |
| `demo_policy_hash` | Hash of the demo policy profile this evidence is bound to. |
| `document_count` | Number of submitted documents processed. |
| `required_classes_present` | Subset of the 3 required classes that were found. |
| `optional_classes_present` | Subset of the 4 optional classes that were found. |

Required classes: `BANK_STATEMENT`, `TAX_RETURN`, `CREDIT_REPORT`.
Optional classes: `EMPLOYMENT_VERIFICATION`, `PROPERTY_APPRAISAL`, `BUSINESS_FINANCIALS`, `IDENTITY_DOCUMENT`.

---

## 6. Scoring logic

`support_score` is a transparent weighted sum — no learned model, no hidden state — so an
underwriter can re-derive it by hand:

```
required_coverage = (required classes present / 3)              → weight 0.60
optional_coverage = (optional classes present / 4)              → weight 0.20
span_coverage     = (extracted required-field weight / max)     → weight 0.20

support_score = required_coverage * 0.60
              + optional_coverage * 0.20
              + span_coverage     * 0.20
```

`PASS` requires **all** of:
- all required document classes present (`BANK_STATEMENT`, `TAX_RETURN`, `CREDIT_REPORT`)
- all **required fields** for those classes extracted (e.g. `CREDIT_REPORT.derogatory_mark_count`)
- no contradiction flags
- `support_score >= 0.80`
- `open_web_blocked is True`

Thresholds:

| Condition | Resulting state |
|---|---|
| all required classes present AND all required fields extracted AND no contradictions AND `score >= 0.80` | `PASS` (`sufficient`) |
| malformed/non-list input, OR a missing required class with `support_score < 0.40` | `FAIL` (`insufficient`) |
| anything else: a missing required **field**, a missing required doc with moderate score, or any contradiction | `WEAK_WITH_CAVEATS` (`partial`) |

Missing-evidence flags are structured: `MISSING_DOC:<CLASS>` for an absent required class and
`MISSING_FIELD:<CLASS>.<field>` for a present class whose required field was not extracted.
A document class being present is **not** enough — its required fields must be extracted too,
so a `CREDIT_REPORT` with no `derogatory_mark_count` cannot reach `PASS`.

The weights are tuned so that a complete required packet clears `PASS`, while *any* missing
required class makes `PASS` unreachable on coverage alone — required-document coverage
contributes 0.60, so missing one drops the ceiling below 0.80.

Implementation: `_compute_support_score_breakdown` returns every intermediate term plus the
final score, so the value is fully explainable in audit and in interview.

---

## 7. Contradiction detection

All rules are deterministic threshold checks (no ML), so an underwriter can re-derive every
flag by hand. Two of the three are **cross-document** consistency checks; one is an
**intra-document** consistency check within a single `CREDIT_REPORT`.

| Rule ID | Scope | Fields (source docs) | Fires when |
|---|---|---|---|
| `INCOME_BALANCE_MISMATCH` | cross-document | `annual_gross_income` (TAX_RETURN) vs `average_monthly_balance` (BANK_STATEMENT) | annual income > 20× the average monthly balance — high declared income with near-empty accounts |
| `EMPLOYMENT_INCOME_CONFLICT` | cross-document | `employment_status` (EMPLOYMENT_VERIFICATION) vs `annual_gross_income` (TAX_RETURN) | status `UNEMPLOYED` with declared income > 0 |
| `CREDIT_SCORE_DEROGATORY_MISMATCH` | intra-document (CREDIT_REPORT) | `credit_score` vs `derogatory_mark_count` (both from CREDIT_REPORT) | score ≥ 720 with ≥ 3 derogatory marks — a "clean" score that carries heavy derogatories |

A contradiction never produces a clean `PASS` — at best the packet is `WEAK_WITH_CAVEATS`.

---

## 8. Failure modes

| Failure | Behavior |
|---|---|
| **Malformed input** (non-list, junk entries, missing `document_class`) | Never raises. Returns a `FAIL` contract with `evidence_sufficiency=insufficient` and all required classes flagged missing. |
| **Missing required docs** | `missing_evidence_flags` populated; `PASS` is unreachable; state is `FAIL` or `WEAK_WITH_CAVEATS` by score. |
| **Weak support score** | `WEAK_WITH_CAVEATS` — proceeds with caveats, routes to human review. |
| **Contradictory evidence** | `contradiction_flags` populated; `PASS` impossible. |
| **LLM tries to invent evidence** | Two deterministic guards: (1) `verdict` + `reason_codes` are hashed pre-call and re-checked post-call; (2) a citation allowlist scans the rationale for `ev-…` IDs and rejects any not in `evidence_ids`. On either, the deterministic rationale is served. Fabricated evidence IDs never enter the served rationale. |
| **Malformed / open-web bundle reaches firewall** | The firewall validates the bundle before any LLM call: a non-dict bundle or one missing `evidence_ids` → `invalid_c0_bundle` fallback; `open_web_blocked` not `True` → `open_web_not_blocked` fallback; wrong `c0_mode` → `invalid_c0_mode` fallback. |
| **Downstream verdict-reuse attempt** | Verdict/reason codes are owned by the deterministic scorer and hashed into the artifact; the semantic cache must not reuse verdicts, and the firewall rejects any post-compile mutation. |

---

## 9. Production controls

- **No open-web retrieval** — `open_web_blocked=True` is a hard invariant on every contract; the firewall also rejects any bundle whose `open_web_blocked` is not `True`.
- **Evidence IDs** — every extracted field carries a deterministic, value-aware `ev-…` ID; the firewall's **deterministic citation allowlist** rejects any rationale that cites an ID absent from the contract.
- **Deterministic hashes** — `evidence_contract_id` and the PA artifact hashes are reproducible; same input → same IDs; any changed submitted value changes the contract ID.
- **Fail-closed state** — bad input yields a `FAIL` contract, never an exception, never a silent "proceed". Non-list input and junk entries are handled deterministically, not via the internal-error path.
- **Immutable contract handoff** — the contract is the only thing downstream stages may read; they do not mutate it.
- **LLM rationale firewall** — `verdict` + `reason_codes` are hashed before the LLM call and re-checked after; a **deterministic** post-call citation allowlist (plain string matching, *not* a second LLM judge) blocks fabricated evidence IDs. The LLM owns prose only.
- **Audit-friendly receipt fields** — coverage map, span map, flags, score, and policy hash are all on the contract.
- **Synthetic-data boundary** — fixtures are fully synthetic; no real PII; no real binding decision. Production-grade / client-style, not a real client deployment.

---

## 10. Testing strategy

Anchor suite: `tests/apps_underwriting_ai/test_c0_evidence_sufficiency_gate.py`
(plus the pre-existing governance suite `tests/governance/test_apps_underwriting_ai_c0.py`
and firewall suite `tests/governance/test_apps_underwriting_ai_llm_firewall.py`).

| Test | Why it matters |
|---|---|
| full packet → `PASS` | Proves the happy path actually clears the threshold, not just "doesn't crash". |
| missing `BANK_STATEMENT` → `MISSING_DOC` flag, not `PASS` | Proves a missing required class blocks `PASS`. |
| missing `TAX_RETURN` → `MISSING_DOC` flag, not `PASS` | Same invariant on a different required class. |
| income/balance mismatch → `INCOME_BALANCE_MISMATCH` | Proves cross-document contradiction detection fires. |
| high score + derogatories → `CREDIT_SCORE_DEROGATORY_MISMATCH` | Proves the intra-document contradiction rule fires and blocks `PASS`. |
| malformed input → `FAIL`, no raise; non-list → `FAIL`; non-dict `fields` → no crash | Proves fail-closed behavior — the single most important safety property — without the internal-error flag. |
| determinism → identical IDs across runs | Proves the contract is reproducible (audit + caching depend on it). |
| changed field value → changed `evidence_contract_id` | Proves the ID binds to the actual submitted evidence (auditability). |
| falsy values (`0`, `False`) extracted | Proves `0` derogatory marks isn't silently dropped — a real underwriting value. |
| span map only contains submitted schema fields | Proves the gate never infers/hallucinates fields (`invented_external_risk_score` is dropped). |
| `open_web_blocked` always `True` | Proves the no-internet invariant across all states (parametrized over all fixtures). |
| firewall accepts known-ID rationale; rejects fabricated-ID rationale; falls back on bad/open-web bundle | Proves the deterministic citation allowlist + bundle validation actually work. |

Anchor file: `tests/apps_underwriting_ai/test_c0_evidence_sufficiency_gate.py` (20 tests).

---

## 11. Interview talk track

### 90-second answer — "Tell me about a GenAI/agentic AI system you built."

> I built the evidence sufficiency gate for an AI-assisted underwriting workflow. The core
> problem is that underwriters get incomplete, inconsistent document packets, and a language
> model will confidently explain a decision the documents don't actually support. So I built
> a deterministic gate that sits between intake and decision assembly. It inspects the
> submitted documents, checks that the required classes — bank statement, tax return, credit
> report — are present, extracts fields from those documents only, assigns a deterministic
> evidence ID to every extracted field, computes a transparent support score, and runs
> cross-document contradiction checks. The output is an immutable `FinalEvidenceContract`
> with a `PASS / WEAK_WITH_CAVEATS / FAIL` state. Everything downstream — including the LLM
> that writes the human-readable rationale — is forced to consume that contract. The LLM
> owns the prose and nothing else: the verdict and reason codes are hashed before the call
> and re-checked after, so the model can't change the decision or invent evidence. The whole
> thing fails closed: malformed input returns a `FAIL` contract instead of throwing, and it
> never touches the open web. It's built on synthetic documents, but it's structured the way
> a real client deployment would be — deterministic core, auditable contract, human-review
> triggers.

### 5-minute deep dive

- **Problem.** Regulated underwriting needs traceability and a deterministic fallback. The
  risk with GenAI here isn't bad grammar — it's a fluent rationale for an unsupported
  approval. I needed a layer that decides, deterministically, whether there's enough
  document-backed evidence to proceed at all.
- **Architecture.** `SubmittedDocuments → UnderwritingC0Adapter → FinalEvidenceContract →
  PA compiler / LLM firewall → DecisionPacket / Exit`. The contract is the seam: it's the
  only thing downstream may read, and it's immutable.
- **Key design decisions.** (1) Deterministic core — coverage, scoring, contradictions are
  all hand-derivable threshold logic, no model. (2) The LLM is scoped to rationale prose;
  verdict and reason codes are owned by a deterministic scorer and hashed into the prompt
  artifact. (3) Every extracted field gets a deterministic evidence ID so the rationale can
  only cite real evidence. (4) Hard `open_web_blocked` invariant.
- **Failure handling.** Fail closed everywhere: malformed input → `FAIL` contract (no
  exception); missing required docs → `PASS` unreachable; contradictions → never a clean
  `PASS`; LLM tamper → deterministic rationale fallback.
- **Testing.** A focused suite covering the happy path, each missing-required case, both
  contradiction rules, malformed input, determinism, the no-open-web invariant, the
  no-inferred-fields invariant, and an adversarial firewall test that proves a model can't
  smuggle a fabricated evidence ID into the served rationale.
- **What changed after hardening.** I made the contract ID value-aware (changing a submitted
  value now changes the ID), fixed falsy-value extraction (`0` / `False` were being dropped),
  made `PASS` require required *fields* not just required document *classes*, cleaned up
  malformed-input handling so junk is deterministic rather than an internal-error flag, made
  the support score explainable, and turned the "LLM can't invent evidence" claim into a
  proven property via a deterministic citation allowlist plus adversarial tests.
- **What I'd do next.** Real document parsing (OCR/extraction with confidence calibration),
  a per-field provenance UI for underwriters, and drift monitoring on the coverage and
  contradiction-rate distributions.

---

## 12. Deep interviewer questions & answers

**Q1. Why did you keep this deterministic?**
Because in a regulated workflow the decision must be reproducible and auditable. A
deterministic gate means the same packet always yields the same contract and the same IDs,
which auditors and caches both depend on. A model in this position would make the behavior
non-reproducible and the failure modes unbounded.

**Q2. Why not let the LLM decide?**
The LLM is good at prose, not at being held accountable. If the model owned the verdict,
there'd be no way to guarantee the explanation matches the evidence, and no clean fallback.
I scoped the LLM to the rationale paragraph and locked the verdict + reason codes with a hash
the firewall re-checks.

**Q3. How did you prevent hallucinated evidence?**
Two layers, both deterministic. First, the gate only extracts fields that are literally
present in the submitted documents — it never infers, and a test asserts the span map
contains only submitted schema field names and values (an `invented_external_risk_score`
field is dropped). Second, every extracted field has a deterministic evidence ID, and the
firewall runs a **deterministic citation allowlist** — plain string matching for the `ev-…`
ID shape, *not* a second LLM judge — that rejects any rationale citing an ID absent from
`evidence_ids`. The firewall test proves a model trying to cite `ev-FAKE-deadbeef99` gets its
output rejected and the deterministic rationale served instead.

**Q4. What did `PASS` vs `WEAK_WITH_CAVEATS` mean?**
`PASS` means all three required classes present, no contradictions, and support score ≥ 0.80
— safe to proceed. `WEAK_WITH_CAVEATS` means there's usable evidence but something is off — a
contradiction, or a missing required class with a middling score — so it proceeds only with
caveats and a human-review trigger.

**Q5. What happened if docs were missing?**
Missing required classes are listed in `missing_evidence_flags`, and `PASS` becomes
unreachable because required-document coverage is 60% of the score. Depending on the residual
score it lands in `FAIL` or `WEAK_WITH_CAVEATS`.

**Q6. What happened if evidence contradicted itself?**
A contradiction rule fires (e.g. `INCOME_BALANCE_MISMATCH`), the flag goes on the contract,
and the state can never be a clean `PASS`. The flags travel downstream so the rationale and
the human reviewer both see exactly which check failed.

**Q7. How did you make it auditable?**
Every extracted field is an evidence span with its own deterministic ID, the contract carries
the coverage map, the span map, the flags, the score, and the bound policy hash, and the
`evidence_contract_id` is a reproducible hash of the input. You can reconstruct *why* a state
was emitted entirely from the contract.

**Q8. How did you test determinism?**
I run the same fixture twice and assert identical `evidence_contract_id`, identical
`evidence_ids`, identical score, and identical `to_dict()`. If anything non-deterministic
crept in (dict ordering, time, randomness) that test breaks.

**Q9. How would this integrate with a human underwriter?**
`WEAK_WITH_CAVEATS` and `FAIL` are the human-in-the-loop triggers. The underwriter gets the
contract — the missing flags, the contradiction flags, the per-field evidence with IDs — so
they're reviewing structured evidence, not re-reading raw PDFs.

**Q10. What metrics would you monitor in production?**
State distribution (`PASS / WEAK / FAIL` rates), contradiction-rate per rule, missing-class
rates per required class, support-score distribution, firewall fallback rate, and
immutability-violation count (which should be ~0; a spike means something upstream is
mutating locked fields).

**Q11. How would you handle drift?**
Watch the coverage and contradiction-rate distributions over time. A rising contradiction
rate could mean a parser regression or a real change in applicant behavior; a shifting
score distribution could mean my thresholds need recalibration. I'd version the policy hash
so I can attribute drift to a specific config.

**Q12. What was the hardest bug/risk?**
Three subtle ones surfaced during hardening. (1) The contract ID originally hashed only
document *classes*, so two packets with different field values could collide — I made it hash
the canonical field values, with a test that proves changing income changes the ID. (2)
Extraction used `doc.get(field) or ...`, which silently dropped `0` and `False` — both valid
underwriting values (zero derogatory marks!); I added an explicit presence check. (3) The LLM
channel: it's easy to "lock the verdict" in a docstring and not in code. The real fix was
hashing verdict + reason codes into the artifact pre-call and re-checking post-call, **plus** a
deterministic citation allowlist, **plus** adversarial tests that mutate the locked list and
cite a fake evidence ID and assert the fallback. Without those tests the guarantees are just
comments.

**Q13. How would you deploy this safely?**
Behind a feature flag, in shadow mode first — emit the contract and compare its state to the
existing manual triage without affecting outcomes. Once the state distribution matches
expectations, promote it to a blocking gate with the `FAIL`/`WEAK` paths wired to the
human queue.

**Q14. What would you not automate?**
The binding decision. The gate decides *evidence sufficiency*, not approval. Anything that
issues a real policy or extends real credit stays with a human (or a separately governed,
separately audited decision system). The gate's job is to make sure that human is looking at
sufficient, consistent, traceable evidence.

**Q15. How would you extend it beyond synthetic docs?**
Replace the flat-field fixtures with a real document-parsing stage (OCR + structured
extraction) that emits the same span shape with calibrated confidences, keep the contract
and firewall exactly as-is, and add provenance metadata (page/bounding-box) to each evidence
span so the ID links back to a location in the source document.

---

## Where the code lives

- Gate: `apps_underwriting_ai/integrations/underwriting_c0_adapter.py`
- Contract: `FinalEvidenceContract` (same file)
- Firewall: `apps_underwriting_ai/integrations/underwriting_llm_firewall.py`
- PA compiler: `apps_underwriting_ai/prompt_assembly/underwriting_pa_compiler.py`
- Fixtures: `apps_underwriting_ai/fixtures/c0_*_documents.yaml`
- Tests: `tests/apps_underwriting_ai/test_c0_evidence_sufficiency_gate.py`
