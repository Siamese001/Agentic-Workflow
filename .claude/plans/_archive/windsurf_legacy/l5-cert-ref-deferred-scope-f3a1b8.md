# Plan — L5 Cert Ref Deferred Scope (post l5-cert-ref-emit-chain-threading-c4e7f1)

**Slug:** `l5-cert-ref-deferred-scope-f3a1b8`
**Tier:** T3 (cross-layer — apps_* caller wiring + semantic hardening + migration)
**Status:** In Progress
**Created:** 2026-05-09
**Parent plan:** `l5-cert-ref-emit-chain-threading-c4e7f1` (Completed 2026-05-09, commit `85892005de`)
**Purpose:** Planning only — no implementation. Captures all scope explicitly deferred from the parent plan.

---

## 1. Why This Plan Exists

The parent plan (`c4e7f1`) threaded `l5_certification_ref: str` through all 13 `agentic_core/` emit contracts and added structural presence checks. Five categories of follow-up work were explicitly excluded as non-goals or "deferred" and are captured here for future activation.

**This document is a backlog artifact. No wave executes until a follow-up session explicitly starts one.**

---

## 2. Deferred Scope Register

| ID | Source | Title | Category | Blocking? | Est. Tokens |
|---|---|---|---|---|---|
| DS-1 | Plan §8 + ADR §5 | `apps_*` caller pipeline glue — wire `l5_certification_ref` into each app's ingress/egress pipeline | App wiring | No (advisory gap) | ~25k |
| DS-2 | ADR §5 | Semantic validation — cert expiry, HMAC signature verification on `l5_certification_ref` | Security hardening | No | ~12k |
| DS-3 | ADR §5 | Remove legacy `CommitRequest.l5_certification_refs` (plural `Tuple[str,...]`) once all callers migrate to singular | Contract cleanup | No | ~4k |
| DS-4 | ADR §5 | Migrate existing serialized artifacts (`artifacts/certification/`, `certification/agentic_core/`) to include the new field | Artifact migration | No | ~8k |
| DS-5 | Plan §8 | Wire `l5_certification_ref` into `RuntimeExhaustBundle` shadow eval analytics paths beyond the dataclass field add | Observability depth | No | ~6k |
| DS-6 | Plan §8 | Add runtime certification claims per Constitutional §32 (requires its own Author-Gate, gated on ADR-080 Phase E) | Certification | No (gated) | ~TBD |
| DS-7 | Test failures (W1) | Fix remaining 5 W1/W2 test failures: `ValidatedRequest`, `L1PlanContract`, `RouteContract`, `FinalEvidenceContract` constructor args + `L2Executor.propagates_cert_ref` propagation test | Test repair | No (advisory) | ~3k |

---

## 3. Detailed Item Descriptions

### DS-1 — `apps_*` caller pipeline glue

**What:** Every `apps_*` app (apps_rg, apps_qna, apps_research, apps_rfp, apps_underwriting_ai, apps_eval, apps_lic, apps_architect, apps_exec, apps_repo_brief) needs to:
1. Obtain a valid `l5_certification_ref` at ingress (from L5 authority registry or request envelope).
2. Pass it through their internal pipeline to each layer's emit contract constructor.
3. Propagate it into the final `RuntimeExhaustBundle` for L6.

**Why deferred:** Each app's pipeline shape is distinct — this is per-app work, not a cross-cutting field add. Scope per app is ~2-3k tokens. 10 apps × ~2.5k = ~25k total.

**Prerequisite:** apps_rg spine path — superseded by `apps-rg-spine-only-unification-d8f4a2` (COMPLETE 2026-05-24); legacy plan `apps-rg-runtime-wiring-completion-d4e8a1` retired same date. Other apps depend on their own ingress wiring plans.

**Sequencing:** DS-1 can be split into 10 child plans, one per app. apps_rg is the reference implementation — complete it first.

---

### DS-2 — Semantic validation (cert expiry + HMAC)

**What:** `verify_certification_ref(ref)` currently accepts any non-empty string as structurally valid. Semantic checks deferred per ADR-100 §6:
- Cert expiry: look up `ref` in L5 registry and check `valid_until` timestamp.
- HMAC signature: verify `ref` was signed by the L5 authority key.
- Scope binding: verify `ref.scope` covers the requesting layer's operation.

**Why deferred:** Requires L5 registry to be populated with real certification records (currently stubs). Must not block rollout of the field-add phase.

**Prerequisite:** ADR-080 Phase E (runtime certification pipeline) must supply a live registry with real records. Phase E is gated on Phase D.5 closeout.

**Risk:** Until DS-2 lands, `l5_certification_ref` is an opaque token with no runtime enforcement — present but unvalidated semantically.

---

### DS-3 — Remove `CommitRequest.l5_certification_refs` (plural)

**What:** `CommitRequest` now has both:
- `l5_certification_refs: Tuple[str, ...] = ()` — legacy plural (kept for backward compat)
- `l5_certification_ref: str = ""` — new singular canonical form

The plural field should be removed once all callers confirm they use the singular form.

**Why deferred:** Requires an audit of all `CommitRequest` construction sites across `agentic_core/`, `apps_*`, and tests. No caller currently sets `l5_certification_refs` to a non-empty tuple (verified in W3), so removal is safe but requires audit evidence.

**Steps when activating:**
1. `grep -r "l5_certification_refs" --include="*.py"` to find all construction and read sites.
2. Confirm all sites use singular or ignore the field.
3. Remove plural field + `__post_init__` check on it.
4. Update CI gate `check_l5_cert_ref_on_emit_contracts.py` to also verify plural is gone.

---

### DS-4 — Serialized artifact migration

**What:** Existing serialized artifacts under `artifacts/certification/` and `certification/agentic_core/` were produced before the `l5_certification_ref` field existed. JSON deserializers that map these artifacts to the new dataclass shapes will receive the default empty string (backward-compat is read-side only per plan §8 design decision). A migration script could backfill the field in historical artifacts.

**Why deferred:** Historical artifacts are not used in CI or runtime paths — they are evidence bundles for the Fort Knox certification pipeline. Backfilling is optional audit hygiene, not a correctness issue.

**Prerequisite:** DS-2 (semantic validation) must land first — backfilled refs need to be semantically valid, not empty strings.

---

### DS-5 — `RuntimeExhaustBundle` shadow eval analytics depth

**What:** Beyond holding the `l5_certification_ref` field (already done in W3), the shadow eval analytics pipeline (`L6_observability/shadow_eval/`) should:
1. Include `l5_certification_ref` in shadow eval comparison logic (detect cert-ref drift between shadow and live runs).
2. Emit a `cert_ref_mismatch` OTEL span attribute when shadow ref ≠ live ref.
3. Surface cert ref in `L6_observability/shadow_eval/reports/` for audit.

**Why deferred:** Shadow eval analytics paths are a low-priority observability enhancement. The field is present; the analysis depth is optional.

---

### DS-6 — Runtime certification claims (Constitutional §32)

**What:** Constitutional §32 (Fort Knox certification discipline) requires its own Author-Gate before any `SIGNED_OFF` claim can be attached to a run. Threading `l5_certification_ref` is a prerequisite — the field must be present and semantically valid (DS-2) before a run can be declared L5-certified.

**Why deferred:** Gated on:
1. ADR-080 Phase E planning (runtime cert pipeline).
2. DS-2 semantic validation landing.
3. Separate Author-Gate `certification_claim` packet per constitutional §32.

**Note:** This is explicitly outside the scope of this plan per plan §8: "Adding runtime certification claims (Constitutional §32 — requires its own Author-Gate)."

---

### DS-7 — Fix 5 residual test failures from W1/W2

**What:** 5 tests remain failing from the W1/W2 test files (not W3/W4 regressions):

| Test | File | Root Cause |
|---|---|---|
| `test_validated_request_l5_cert_ref_defaults_empty` | `test_l5_cert_ref_w1.py` | `ValidatedRequest` constructor mismatch — required args not satisfied in test |
| `test_l1_plan_contract_runtime_l5_cert_ref_defaults_empty` | `test_l5_cert_ref_w1.py` | `L1PlanContract` constructor mismatch |
| `test_route_contract_runtime_l5_cert_ref_defaults_empty` | `test_l5_cert_ref_w1.py` | `RouteContract` constructor mismatch |
| `test_final_evidence_contract_l5_cert_ref_defaults_empty` | `test_l5_cert_ref_w1.py` | `FinalEvidenceContract` constructor mismatch |
| `test_l2_executor_propagates_cert_ref` | `test_l5_cert_ref_w2.py` | `L2Executor` propagation logic — ref not threaded into `SealedL2Artifact` from `CompiledPromptArtifact` |

**These are pre-existing test authoring errors, not production regressions.** W3 and W4 tests (29 tests) all pass. CI gate L5CR1 is green (18/18).

**Steps when activating:** Fix each test to construct the dataclass with all required fields correctly; for DS-7.5 wire `prompt_artifact.l5_certification_ref` into the `L2Executor.execute` return value.

---

## 4. Activation Prerequisites Summary

| DS | Prerequisite |
|---|---|
| DS-1 | apps_rg ingress wiring (`d4e8a1` W3) landed; per-app timing varies |
| DS-2 | ADR-080 Phase E live registry available |
| DS-3 | All `CommitRequest` callers audited; DS-1 done |
| DS-4 | DS-2 done (semantic refs needed for backfill) |
| DS-5 | None — optional observability enhancement |
| DS-6 | DS-2 done + Author-Gate `certification_claim` + Phase E planning |
| DS-7 | None — standalone test fixes, no production change |

---

## 5. Wave Structure (planning-only — to be detailed when activated)

| Wave | Scope | Est. Tokens | Status |
|---|---|---|---|
| W1 | DS-7 — fix 5 residual test failures | ~3k | ✅ DONE (commit d41d3ca7c7) |
| W2 | DS-1 — apps_rg caller glue (reference impl) | ~6k | ⏸ Waiting (gated on d4e8a1 W3) |
| W3 | DS-1 — remaining 9 apps caller glue | ~20k | ⏸ Waiting (gated on DS-1/W2) |
| W4 | DS-3 — remove plural field (post-audit) | ~4k | ⏸ Waiting (audit done; gated on DS-1) |
| W5 | DS-5 — shadow eval analytics depth | ~6k | ✅ DONE (commit 21081bfb66) |
| W6 | DS-2 — semantic validation (gated on Phase E) | ~12k | ⏸ Waiting (gated on ADR-080 Phase E) |
| W7 | DS-4 — serialized artifact migration | ~8k | ⏸ Waiting (gated on DS-2) |
| W8 | DS-6 — runtime certification claims (gated on §32 AG) | ~TBD | ⏸ Waiting (gated on DS-2 + §32 AG) |

---

## 6. Phase-Level Summary

| Phase ID | Title | Scope | Status |
|---|---|---|---|
| P1.1 | Fix W1 test constructors | `test_l5_cert_ref_w1.py` | ✅ Done |
| P1.2 | Fix W2 L2 propagation test | `test_l5_cert_ref_w2.py`, `l2_execution_contract.py` | ✅ Done |
| P2.1 | apps_rg l5_certification_ref glue at ingress | `apps_rg/__main__.py`, `apps_rg/...dispatch.py` | Not Started |
| P2.2 | apps_rg propagation through layer bindings | per-layer binding files in `agentic_core/runtime/entry/` | Not Started |
| P3.1–P3.9 | Per-app glue (apps_qna … apps_repo_brief) | `apps_*/` — one phase per app | Not Started |
| P4.1 | Audit `l5_certification_refs` plural caller sites | `grep` sweep + evidence doc | Not Started |
| P4.2 | Remove plural field + update gate | `L4_state/contracts/records.py`, `check_l5_cert_ref_on_emit_contracts.py` | Not Started |
| P5.1 | Shadow eval cert-ref drift detection | `L6_observability/shadow_eval/` | ✅ Done |
| P6.1 | Semantic validation helper upgrade | `L5_safety/contracts/verify.py` | Not Started |
| P6.2 | Registry lookup integration | `L5_safety/contracts/registry.py` | Not Started |
| P7.1 | Artifact backfill script | `ops_scripts/maintenance/backfill_l5_cert_ref.py` | Not Started |
| P8.1 | Author-Gate `certification_claim` packet | AG decision packet | Not Started |
| P8.2 | Runtime certification integration | `agentic_core/L5_safety/` + `runtime/` | Not Started |

---

## 7. Non-Goals (for this deferred plan too)

- Changing any contract field shape already landed in `c4e7f1`.
- Implementing a new L5 governance plane version (ADR-049/ADR-051 succession — separate plan).
- Any change to `agentic_core/L5_safety/contracts/egress.py` doctrine outputs.
- Re-running W0–W5 of the parent plan.

---

## 8. References

- Parent plan: `.windsurf/plans/l5-cert-ref-emit-chain-threading-c4e7f1.md` (Completed)
- ADR: `docs/architecture/adr/ADR-100-l5-cert-ref-emit-chain-threading.md` — §5 Deferred section
- ADR-080: runtime cert Phase D planning (DS-2/DS-6 gate)
- Constitutional §32: Fort Knox certification discipline (DS-6 gate)
- Plan `apps-rg-runtime-wiring-completion-d4e8a1`: apps_rg ingress wiring (DS-1 dependency)

---

PLAN_CREATED: slug=l5-cert-ref-deferred-scope-f3a1b8 path=.windsurf/plans/l5-cert-ref-deferred-scope-f3a1b8.md status=not_started tier=T3 layer=cross-cutting
