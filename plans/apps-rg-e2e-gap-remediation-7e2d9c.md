---
slug: apps-rg-e2e-gap-remediation-7e2d9c
status: In Progress
plan_type: app_runtime_remediation
dod_exempt: false
supersedes: []
owner: Amit Ayer
created: 2026-06-08
updated: 2026-06-08
---

# apps_rg End-to-End Gap Remediation (AIG + Brown & Brown)

## Decision summary

Treat this as a **P0 system-path blocker**, not a resume-quality issue. The goal is deterministic,
truthful end-to-end generation from a clean checkout. Load-bearing decisions for this plan:

1. **Product success = canonical JSON resume + evidence receipts.** DOCX is an optional export
   smoke only — never a required artifact, CI gate, DoD item, or release blocker.
   (`docx_output_required()` already defaults `False`; this plan removes residual DOCX-required
   expectations.)
2. **Base resume is identity-only:** contact info, employer names, titles, locations, dates,
   current-role flag, and locked education/certs. It must **not** supply generated bullet prose,
   claim text, metrics, tone, seniority, or proof authority.
3. **Generated employer content (Unify, IBM, InsurTech, EY)** comes from graph / role-episode /
   proof-pool evidence and must prove **generate-N / select-X** behavior.
4. **Base-resume n-gram overlap is demoted to advisory/debug** (it is documented WARN-mode and is
   vestigial as a hard gate). Keep **exact/verbatim-copy blockers** and **hydration-operation
   blockers**.
5. **DOCX removal and base-resume-authority cleanup are part of this remediation**, not later polish.
6. **Product-mode tests are mandatory** and must run **without** `APPS_RG_TEST_HARNESS=1`.
7. **Whole-resume aggregation is mandatory.** `section_sealed_index` is inventory only; require a
   full-resume judge/quorum, cross-section overlap/dedup gates, and aggregate X2 / Exit evidence.
8. **Deterministic fallback from empty/invalid provider output must not count as product success.**
9. **C0.2 PASS requires selected evidence;** PASS-but-empty is invalid.
10. Skills/competencies are **graph-selected + ledger-proven** (C0.3 `augmented_skills_graph` +
    candidate fact ledger / proof pool); the base resume is never a source for them.

### Wave summary

| Wave | Focus | Status | Success criteria |
|---|---|---|---|
| W0 | Evidence freeze + reproduction fixtures | ✅ Completed | Failing AIG/Brown bundles preserved; fixture manifest proves `provider_attempted:false`, all 11 lanes blocked, exit-code mismatch — `tests/fixtures/e2e_gap_7e2d9c/` + guard `tests/unit/apps_rg/test_e2e_gap_7e2d9c_freeze.py` (13 passed) |
| W1 | Fresh checkout / fail-loud / exit codes | ✅ Completed | Clean checkout fails actionably; integrated CLI exits non-zero when all lanes block — `doctor --strict` (G1/G2, live exit 2: fact_vectors absent), `exit_code_from_whole_run_result` (G4, no more X3_BLOCK→0 mask), actionable C0.2 text (G5). 31 tests pass; `.env.example` present |
| W2 | C0.2 retrieval truth + instrumentation | ✅ Completed | G8 per-lane traces; G6 PASS-but-empty guard (status=PASS ⟹ selected_count>0); G9 embedding-dimension parity (384≠1024 loud); G7 filter-discards-all → bounded broad fallback + named reason; G11/G14 base-resume/JD tagged NON_PROOF_CONTEXT + `assert_base_resume_identity_only` lock. 79 product-mode tests green, 0 new failures |
| W3 | `fact_vectors` bootstrap from graph/proof-pool | ✅ Completed | `python -m apps_rg bootstrap fact-vectors --strict` builds 13 atoms from the tracked **candidate fact ledger** (NOT base resume — G14) across all generated lanes; idempotent (stable ids); manifest + checksum; strict fail-loud. **doctor flips exit 2→0** (fact_vectors present, live-proven). EY/InsurTech recorded locked-deterministic (constitutional floor). 7 tests. Note: C0.3 graph-expansion enrichment deferred (ledger build satisfies G2/G3/G10) |
| W4 | Exit / report / artifact / aggregation contract | 🔄 Partial | ✅ G16 aggregate disposition truth — a zero-authorized whole run now surfaces an explicit `X3_BLOCK` (not the ambiguous `X3A`→UNKNOWN the W0 fixture froze); `_failure_payload` X3A→X3_BLOCK too. ⏳ G17 run_report-always, G18 whole-resume aggregation gates, G19 aggregate-blocks-X3, G20 fallback-not-success → closeout (need a live integrated run now that C0.2 is unblocked) |
| W5 | Product-mode tests + vestigial artifact cleanup | 🔄 Partial | ✅ G12 base-resume n-gram is advisory/WARN (locked: high-overlap bullet still passes), ✅ G15 DOCX-not-required (locked: defaults False); G11 done (W2); all W0–W5 tests run product-mode (no `APPS_RG_TEST_HARNESS`). ⏳ G13 generate-N/select-X receipts + G21 CI product-mode job → need live integrated run |
| W6 | E2E live-run closeout — full AIG resume | 🔄 In progress | The live AIG run (JD + briefing) after W1–W5 unblocked dense C0.2 and surfaced the remaining blocker chain. **Success = `python -m apps_rg` for AIG produces `generated_resume.json` with the generated lanes authorized.** Covers the E2E-discovered gaps: **G22** sparse/BM25 index build (current blocker — all lanes block on `sparse UNAVAILABLE`), **G23** JD propagation to lanes, **G9b** stale alias `sentence-transformers/bge-m3-v1` in the L2_CACHE path, **G16b** core-spine terminal receipt still `X3A`, **G17** emit `run_report.json`, + any further blocker the iteration reveals. Fix · re-run · repeat until green |

### W6 — E2E gap register (discovered by the live AIG run, 2026-06-08)

| ID | Sev | Gap | Evidence | Status |
|---|---|---|---|---|
| G22 | CRITICAL | Sparse/BM25 lane independently mandatory but the BM25 sidecar for `fact_vectors` is not built → every generated lane blocks `sparse UNAVAILABLE:hits=0` | `full_resume_d69c149b4c7d` competencies `provider_response.json` | 🔄 active blocker |
| G9c | HIGH | `assert_collection_embedding_parity` applied truthiness to a numpy `peek()` array → `PRE_RUN:exception` on a populated collection | `full_resume_a0c41812fbd0` competencies pre-run | ✅ Fixed (`468bacc446`) |
| G23 | HIGH | `--jd <file>` does not propagate to lane generation (`DEFAULT_SSOT: no run-specific JD provided`) despite a loaded `jd_payload` | `aig_w4_validation2.log` | ⏳ pending |
| G9b | MEDIUM | Stale alias `sentence-transformers/bge-m3-v1` in the L2_CACHE / semantic-cache path → "using ChromaDB default EF" | both validation logs | ⏳ pending |
| G16b | MEDIUM | Core-spine terminal receipt still emits `X3A` (apps_rg payload fixed in G16, but the spine emission is deeper) | render_run_summary X3=`X3A` | ⏳ pending |
| G17b | MEDIUM | `run_report.json` not emitted → renderer cannot show narrative HOPs / per-section verdicts | render_run_summary | ⏳ pending |

## Current failure summary

A full live E2E (`external_claude` / `claude-sonnet-4-6`) in a fresh `apps_rg_e2e` worktree produced
**no resume for either target**:

- **AIG** (VP, Global Head of Agentic AI Solutions) — all 11 lanes `X3_BLOCK` /
  `REQUIRED_PROOF_ABSENT`; provider never called (`provider_attempted:false`).
- **Brown & Brown** (SVP IT Strategy & Innovation) — identical pattern.

The failure is **upstream of company-specific generation**: the mandatory C0.2 dense evidence lane
plus fresh-checkout/bootstrap gaps. The integrated CLI still exited `0` while `exit_status=error`.
Evidence: `artifacts/apps_rg/e2e_logs/{aig_run,aig_run2,aig_competencies_standalone,brown_run}.log`;
bundles `artifacts/apps_rg/runtime_proofs/full_resume_016f007993d4` (AIG),
`full_resume_da98b7f979f7` (Brown).

## Non-goals (until first green)

- Resume wording, layout, or visual quality tuning.
- New agent architecture.
- Multi-company generalization beyond the two failing fixtures.
- DOCX styling/formatting (DOCX is optional smoke only).

## Gap register (G1–G21)

Severity ∈ {CRITICAL, HIGH, MEDIUM}. "Wave" = remediation owner wave.

| ID | Sev | Wave | Gap | Acceptance evidence |
|---|---|---|---|---|
| G1 | HIGH | W1 | `.env` is gitignored/absent in a fresh checkout; no preflight/provisioning | `doctor --strict` on clean checkout exits non-zero with exact missing-key list |
| G2 | CRITICAL | W1+W3 | `data/cache/chromadb` gitignored → empty fresh checkout; `fact_vectors` missing → C0.2 "collection does not exist" on all 11 lanes | Clean checkout without `fact_vectors` exits non-zero with bootstrap suggestion; present after bootstrap |
| G3 | CRITICAL | W3 | No `fact_vectors` bootstrap/ingest CLI from tracked sources (`fact_vector_ingest.py` is a library) | `bootstrap fact-vectors --strict` builds the collection; CI clean-cache rebuild green |
| G4 | HIGH | W1 | Exit-code masking: integrated CLI exits `0` while `exit_status=error`/all lanes block (standalone `--section` exits 1) | All-lanes-blocked integrated run exits non-zero |
| G5 | MEDIUM | W1+W2 | Opaque, non-actionable C0.2 error text (generic `REQUIRED_PROOF_ABSENT`) | Error names cause (collection missing/empty / filter removed all hits / embedding mismatch / threshold) + remediation |
| G6 | CRITICAL | W2 | C0.2 returns **PASS-but-empty** (`dense_completed = status=="PASS" and bool(extra)`; `c02_product_hybrid_retrieval.py:209`) | No lane sets `dense_completed`/PASS with `selected_count=0`; zero evidence → EMPTY/BLOCKED/WEAK |
| G7 | CRITICAL | W2 | Section-scoped `where`/filter can discard 100% of candidate facts on a populated collection (`c0_binding.py:1301-1315`) | Regression fails if a where-filter removes 100% of raw candidates without a named reason; each required lane yields evidence or a precise non-PASS |
| G8 | HIGH | W2 | No C0.2 per-lane instrumentation (raw hit count, applied `where`, post-filter survivors, threshold, embedding id/dim) | Each lane emits a C0.2 trace with these fields; before/after traces attached to the fix PR |
| G9 | HIGH | W2+W3 | Embedding-function parity not enforced; stale alias `sentence-transformers/bge-m3-v1` silently falls back to ChromaDB default EF (dimension/relevance drift) | Mismatch fails loud with named remediation; no silent default-EF fallback |
| G10 | CRITICAL | W3 | `fact_vectors` under-populated/stale: **21 atoms** (the earlier "1,300" was a global count across 28 collections), skewed to exec_summary/headline/competencies; **no atoms for unify/ibm/insurtech/ey or narrative lanes** | Bootstrap recreates expected per-section strata counts from manifest covering all generated lanes |
| G11 | HIGH | W2+W5 | Base resume risks supplying generated bullet prose / claim text / metrics / tone / seniority / proof authority | Test: base-resume prose absent from generated-lane C0 evidence; base resume contributes identity only |
| G12 | MEDIUM | W5 | Base-resume n-gram overlap is a hard X2 gate (vestigial; documented WARN-mode in `bullet_ngram_overlap_x2.py`) | Demoted to advisory/debug; valid graph bullet not blocked; verbatim-copy + hydration-operation blockers retained |
| G13 | HIGH | W2+W5 | Generated employer content (Unify, IBM, InsurTech, EY) must source from graph/role-episode/proof-pool and prove generate-N/select-X; not proven E2E | generate-N/select-X receipts for all four employers |
| G14 | HIGH | W2+W3 | Skills/competencies must be graph-selected + ledger-proven (C0.3 `augmented_skills_graph` + ledger), never base resume | Competencies atoms trace to ledger/graph; none from base-resume prose |
| G15 | MEDIUM | W4+W5 | DOCX treated as required (renderer reports "Resume DOCX missing"; earlier DoD required it) | DOCX-not-required test; no DOCX CI gate; renderer/DoD require JSON + receipts, not DOCX |
| G16 | MEDIUM | W4 | Misleading aggregate disposition: top-level `X3A` while all lanes `X3_BLOCK` and no output | Aggregate X3 = block when zero lanes produce authorized output |
| G17 | MEDIUM | W4 | `run_report.json` not emitted on blocked runs; renderer defaults to `runs/` not `runtime_proofs/`; no canonical output root | Blocked run emits `run_report.json`; renderer discovers canonical root and fails non-zero if source JSON missing |
| G18 | HIGH | W4 | Whole-resume aggregation not enforced on product path; `section_sealed_index` is inventory only; full-resume judge/quorum + cross-section overlap/dedup + aggregate X2 never gated (unreached in failing run) | Aggregate artifacts produced and gated; `section_sealed_index` treated as inventory only |
| G19 | HIGH | W4 | No aggregate-failure → final-X3-block linkage | `aggregate-failure-blocks-final-X3` test passes |
| G20 | HIGH | W2+W4 | Deterministic fallback from empty/invalid provider output can count as product success | `empty-provider-output-does-not-fallback-to-success` test; fallback maps to non-success |
| G21 | CRITICAL | W5 | Product-mode tests missing; suite runs under `APPS_RG_TEST_HARNESS=1`, which sets `product_fail_closed_runtime()=False` and disables mandatory C0.2, live BGE, and live judges → CI green while product red | Mandatory product-mode test job runs **without** `APPS_RG_TEST_HARNESS`, exercising C0.2 + aggregation + exit codes |
| G22 | CRITICAL | W2+W3 | C0.2 **sparse/BM25** lane is *independently* mandatory (`APPS_RG_C0_SPARSE_ENABLED` setdefault, embedding_settings.py:201) but the BM25/sparse index is **unavailable** → blocks even if the dense lane is fixed. Reproduced across 6 companies. | `ey_bullets: "C0.2 sparse lane mandatory but BM25/sparse index unavailable … hits=0"`. Sparse index built/available; lanes report sparse hits or a named non-PASS; no lane blocks solely on sparse UNAVAILABLE |
| G23 | HIGH | W2 | JD/targeting **not propagated to lane generation** — the C0.2-bypass run logs "no run-specific JD provided; generic role profile" per lane despite `--jd` (normally masked by the C0.2 block) | `aig_bypass_c02.log`. A generated lane on a proof-eligible path threads the run JD into prompt/targeting; no `DEFAULT_SSOT` generic-role warning |
| G24 | MEDIUM | W1+W4 | Mandatory evidence can be **silently downgraded** on the product path: `os.environ.setdefault(...MANDATORY,"1")` (embedding_settings.py:200-204) does not override an exported `0`, and the printed `embedding_bootstrap` report hardcodes `"1"` (shows intended, not effective) | A per-gate mandatory downgrade on the product path fails loud / is refused without a harness or shortcut; config report shows **effective** values (bypass already receipts `r4_c0_bypass_receipt.json`) |
| G25 | MEDIUM | W1 | Per-lane standalone exit codes **inconsistent** (broadens G4): `--section executive_summary` exits 0 while `competencies`/`headline`/`ibm_bullets` exit 1, all `X3_BLOCK` | `matrix_summary.txt`. All standalone `--section` runs return non-zero on `X3_BLOCK`/`REQUIRED_PROOF_ABSENT` |
| G26 | HIGH | W2+W3 | **11 untriaged broad-exception "hygiene" antipatterns in apps_rg's remediation-critical paths** silently swallow the failures this plan aims to surface — and currently **block ADG regen** (P2 ratchet: MEDIUM ceiling 0, count 12) | ADG snapshot `06082026_1203`: broad `Exception`/`OSError`/`FileNotFoundError` catches in `runtime/providers/external_provider.py:187`, `runtime/c0/fact_vector_write_back.py:282`, `runtime/orchestration/section_lane_executor.py:93`, `runtime/bindings/u0_package_ingest.py` (×4), `runtime/c0/c02_semantic_cache_payload.py` (×2), `runtime/section_graph_skills_proof_pool.py:350`. Narrow each catch to a precise type or add a guardian justification; ADG MEDIUM ratchet returns to 0 |

## Remediation waves

### W0 — Evidence freeze
Lock the failure state before changing behavior.
- Preserve the AIG + Brown failing bundles; add `tests/fixtures/e2e_gap_7e2d9c/manifest.json`
  recording expected artifact paths, exit codes, and terminal dispositions.
- Fixture proves `provider_attempted:false`, all 11 lanes blocked, and the exit-code mismatch
  (integrated CLI exits 0 while internal status is error).

### W1 — Fresh checkout / fail-loud / exit codes  (G1, G2-preflight, G4, G5)
- Add a `doctor`/preflight that checks `.env` keys, `fact_vectors` presence, embedding model/dim,
  and provider config — each missing prerequisite produces a deterministic, named error.
- Add `.env.example` with required keys.
- **Exit-code propagation:** the integrated CLI must not return `0` when `exit_status=error` or all
  lanes block (match the standalone `--section` path, which already returns 1).
- Replace generic C0.2 text with actionable text (G5).
- **Merge gate:** W1 tests green before any C0.2 algorithm change.

### W2 — C0.2 retrieval truth + instrumentation  (G6, G7, G8, G9, G11, G14, G20-partial)
- Add per-lane C0.2 trace fields (raw hit count, applied `where`, post-filter survivors, threshold,
  embedding id/dim).
- Fix section-scoped filters so a populated collection cannot discard all relevant facts; add a
  bounded fallback from exact section metadata to broader section group **only** with a named reason.
- **Status rules:** zero selected evidence must be `EMPTY`/`BLOCKED`/`WEAK_WITH_CAVEATS`, never PASS;
  `dense_completed` cannot be true with `selected_count=0`.
- Enforce embedding parity (retire the stale alias; fail loud on mismatch).
- Enforce **base-resume identity-only** in C0: generated-lane evidence must not contain base-resume
  prose/claims; skills resolve via C0.3 graph + ledger.
- **Merge gate:** PR includes before/after C0.2 traces for both targets.

### W3 — `fact_vectors` bootstrap from graph/proof-pool sources  (G2-build, G3, G9, G10, G14)
- `bootstrap fact-vectors --strict` builds atoms from the **candidate fact ledger + section proof
  pool** (`apps_rg/runtime/c0/c02_evidence_fetch.py`), expanded via the **C0.3 augmented skills
  graph** (`apps_rg/runtime/c0/c03_graph_expansion.py` → `load_augmented_skills_graph`), ingested as
  section-tagged atoms via `apps_rg/runtime/c0/c02_fact_vector_ingest.py`. Covers **all generated
  lanes** (competencies, exec_summary, headline, unify, ibm, insurtech, ey + narratives).
- Build from **tracked source inputs**, not gitignored chromadb state; emit a manifest + checksums;
  idempotent; pre-run index receipt (a same-run write does not satisfy product PASS).
- **The base resume is NOT a source.** `fact_vector_ingest.py::ingest_candidate_profile`
  (base-resume chunker) must not feed `fact_vectors`.
- Optional first-run auto-build allowed only if explicitly configured; default is fail-loud with the
  bootstrap command.

### W4 — Exit / report / artifact / aggregation contract  (G15, G16, G17, G18, G19, G20)
- Aggregate disposition reflects lane outcomes (no `X3A`/allow when zero lanes authorized).
- Emit `run_report.json` for **every** terminal state (including blocked/preflight failures); pick a
  canonical output root and document compatibility; renderer fails non-zero if source JSON missing.
- Emit/validate the artifact manifest: canonical JSON resume + receipts (DOCX optional, **not**
  required).
- **Whole-resume aggregation gates (fail-closed):** deterministic assembly consumed sealed sections
  only; whole-resume LLM judge executed on the assembled resume; judge quorum met; cross-section
  overlap/dedup gates passed; section-ownership gates passed (credentials/certs ownership);
  cross-section consistency passed (titles, dates, metrics, seniority, claims). **Aggregate failure
  blocks final X3** (G19).
- **Empty/invalid provider output must not fall back to product success** (G20).

### W5 — Product-mode tests + vestigial artifact cleanup  (G11, G12, G13, G15, G21)
- Add a mandatory **product-mode** test job that runs **without** `APPS_RG_TEST_HARNESS=1` and
  exercises C0.2, aggregation, and exit codes.
- Demote base-resume n-gram overlap to advisory/debug; retain verbatim-copy + hydration-operation
  blockers.
- Remove residual DOCX-required expectations everywhere (renderer, DoD, docs).
- Base-resume authority cleanup: prove identity-only; prove generate-N/select-X for the four
  employers.

## Required artifacts (green run)

Required for a product-success run (all JSON unless noted):

- `generated_resume.json` — canonical JSON resume
- `run_report.json` — every terminal state
- `exit_disposition.json` — final Exit/X3 disposition (today: per-lane `x3_disposition.json` +
  `RUN_BUNDLE_INDEX.json`/`run_manifest.json`; W4 standardizes a run-root disposition)
- `artifact_manifest.json` — canonical artifact index
- Per-lane evidence — `l2_output.json`, `x2_gate_outputs.json`, `x3_disposition.json`, C0 evidence
- C0.2 traces — per-lane (hits / `where` / survivors / threshold / embedding id+dim)
- `section_sealed_index.json` — inventory only
- `x1d_full_resume_judge_outputs.json` — whole-resume judge
- `cross_section_x2_gate_outputs.json`
- `overlap_decisions.json`
- Aggregate X2 receipt (final-resume aggregate X2; canonical filename TBD, see Open decisions)
- **DOCX (`Amit_Ayer_Resume.docx`) — OPTIONAL export smoke only; never required.**

## Required tests

1. Product-mode C0.2 (no `APPS_RG_TEST_HARNESS`).
2. All-lanes-blocked → non-zero integrated exit.
3. Base-resume prose **absent** from generated-lane C0 evidence.
4. Hydration-operation failure **blocks**.
5. Verbatim base-resume copy **blocks**.
6. Valid graph bullet **not** blocked by base-resume n-gram (advisory only).
7. generate-N / select-X receipts for **all four** employers (Unify, IBM, InsurTech, EY).
8. DOCX-not-required (run succeeds with JSON + receipts, no DOCX).
9. Aggregate-failure-blocks-final-X3.
10. Empty-provider-output-does-not-fallback-to-success.
11. C0.2 **sparse/BM25** lane: index available → sparse hits or a named non-PASS (no `UNAVAILABLE` block).
12. JD **propagated to lane generation** (no `DEFAULT_SSOT` generic-role warning on a proof-eligible path).
13. No **silent mandatory-evidence downgrade** on the product path; config report shows effective values.
14. **Test-gap closure**: each high-risk uncovered/thin module in TG1 gains a product-mode test (a new ADG `covers` edge); the apps_rg suite runs with `--cov` + OTEL ingested so runtime depth is measurable.
15. **Per-lane standalone exit non-zero** on `X3_BLOCK` for every `--section` lane.

## ADG Test-Gap Augmentation (test hotspots)

> ADG Provenance: backend=sqlite, snapshot=`adg_indexed_06082026_1212.sqlite` (182,313 nodes /
> 1,072,457 edges; **ADG MCP reloaded onto it 2026-06-08** — `adg_health` confirms `adg_snapshot_id:
> 06082026_1212`). Queried the canonical SQLite directly. **Test-gap method:** ADG `covers` edges
> (test→module reachability — the runtime/test proxy) + risk MV `mv_hotspot_coverage_risk`. The static
> line-coverage/eval layers (`coverage_pct`, `mv_eval_coverage_by_path`, `mv_l2_phase_coverage`) are
> **depth signals that require a runtime ingest** (coverage.xml/OTEL) and are empty here — not a
> "untested" signal. `test_stubs` for mock debt.
> Regen note: the first 2026-06-08 regen was blocked at the P2 ratchet by **G26**'s 11 apps_rg
> exception-swallows; per Author-Gate sign-off the MEDIUM ceiling was re-baselined 0→12 (G26 still
> tracks the fixes) and the snapshot promoted with all 52 MVs. Rankings are within ~5% of the May-27
> snapshot — **stable** (same top modules + ordering).

**Method (corrected).** The static ADG does **not** model `tests/` — test execution is *runtime* — so the
static line-coverage layer (`coverage_pct`) is empty/`-1.0` and is **not** a test-gap signal. The correct
proxy is the ADG **`covers` edges** (test→module reachability; **27,378** edges this snapshot) plus the
runtime ADG. By that measure apps_rg is **well-covered overall: 435 / 541 files (80%) have ≥1 covering
test**, and **every top-risk hotspot is covered** — `c0_binding.py` has **45** covering tests,
`executive_summary_x2.py` **73**, `proof_pool_resolver.py` **40**. So *risk ≠ test gap*; the real gaps are
the **uncovered + thin** high-risk modules plus **missing runtime depth** (no coverage.xml / OTEL ingested).

| TG | Sev | Wave | Test gap (covers-edge / runtime proxy) | Acceptance |
|---|---|---|---|---|
| TG1 | HIGH | W2+W5 | **114 apps_rg files have ZERO covering test; 209 are thin (1–2)** (covers edges). Remediation-relevant uncovered/thin listed below | each listed high-risk uncovered/thin module gains a product-mode test (new `covers` edge) |
| TG2 | MEDIUM | W5 | **Runtime depth not ingested**: line-coverage % + OTEL eval/trace absent (`coverage_pct=-1.0`; `mv_eval_coverage_by_path` L_APP 0/224; `mv_l2_phase_coverage covered_by_test=0`) — *reachability ≠ depth* | run the apps_rg suite with `--cov` + OTEL and ingest into the ADG runtime proxy so depth/eval coverage is measurable |
| TG3 | MEDIUM | W5 | Mock/stub-heavy suite: **112** `test_stubs`, mostly without failure-config; C0.2/sparse/grounding tests = 1 stub each | critical-path stub tests gain product-mode + failure-path equivalents (G21) |

**Real test gaps — high-risk apps_rg modules with ZERO covering test (by risk):**

| Module (`apps_rg/`) | Risk | Viol | Maps to |
|---|---|---|---|
| `runtime/sections/competencies_lane_execution.py` | 136 | 19 | W2/W5 competencies lane |
| `runtime/sections/ibm_narrative_lane_execution.py` | 117 | 15 | W2/W5 IBM narrative |
| `runtime/validators/achv_bullet_synthesizer_validator.py` | 93 | 2 | W4 validator |
| `runtime/validators/{verb_canonicalizer,ats,content_quality}_validator.py` | 82–84 | 0 | W4 validators |
| `runtime/sections/role_episode_lane.py` | 81 | 10 | **W5 generate-N/select-X** |
| `fact_inventory/harden_augmented_skills_graph_ssot.py` | 77 | 12 | W3 C0.3 graph SSOT |
| `integrations/hops/_llm_client.py` | 61 | 9 | W2 provider client |

**High-risk but THINLY covered (1–2 covering tests) — strengthen:**

| Module (`apps_rg/`) | Risk | Covers | Maps to |
|---|---|---|---|
| `fact_inventory/p2_graph_skills_accelerated_closeout.py` | 188 | 1 | W3 graph skills |
| `runtime/sections/ibm_narrative_lane_runtime.py` | 118 | 1 | W2/W5 |
| `runtime/native_c03_skills_graph.py` | 85 | 2 | **W3 C0.3 skills graph** |
| `runtime/orchestration/r3r4_whole_run_orchestration.py` | 84 | 2 | **W4 whole-run aggregation** |
| `runtime/whole_run_exit.py` | 75 | 2 | **W4 Exit** |

> Many of the 114 uncovered are one-off `fact_inventory/apply_*.py` / `run_*.py` data-prep scripts (low
> product-runtime priority). W5 targets the **lanes, validators, C0.3 graph, and whole-run/Exit** modules
> above first. Re-measure via the `covers` edge count after adding each test.

## CI contract

Named required checks (assert **file existence + schema validity**, not process-exit wording; **no
DOCX gate**):

- `doctor-clean-checkout-fails-actionably`
- `bootstrap-fact-vectors-from-source`
- `c0-2-populated-collection-has-evidence-or-named-nonpass`
- `integrated-cli-fails-when-all-lanes-block`
- `blocked-run-emits-run-report`
- `aig-e2e-produces-json-and-receipts`
- `brown-brown-e2e-produces-json-and-receipts`
- `artifact-contract-validates-output-paths` (JSON resume, run_report, exit_disposition,
  artifact_manifest, aggregate receipts)
- `product-mode-tests-run-without-harness`
- `aggregate-review-gates` (full-resume judge/quorum + overlap/dedup + aggregate X2)

## PR sequencing

- **PR 1 — Fail-loud runtime shell:** W0 fixture freeze + W1 doctor/preflight + exit-code
  propagation. No retrieval changes.
- **PR 2 — C0.2 instrumentation:** W2 trace fields. No filter behavior change unless a test exposes
  an invariant violation.
- **PR 3 — C0.2 retrieval truth + base-resume authority:** section filter fix, status rules
  (no PASS-empty), embedding parity, identity-only enforcement, n-gram demotion.
- **PR 4 — `fact_vectors` bootstrap:** W3 CLI + manifest/checksum + CI clean-cache rebuild from
  graph/proof-pool sources.
- **PR 5 — Exit/report/artifact/aggregation contract:** W4 aggregate disposition, always-on run
  reports, canonical output root, artifact manifest, whole-resume aggregation gates,
  aggregate-failure-blocks-final-X3, fallback-not-success.
- **PR 6 — Product-mode tests + cleanup + closeout:** W5 product-mode job, DOCX-not-required
  cleanup, generate-N/select-X receipts, AIG + Brown green proof, evidence bundle linked here.

## Final Definition of Done

| # | Criterion | Verify |
|---|---|---|
| 1 | Clean checkout `doctor --strict` explains all missing prerequisites and exits non-zero | run on clean worktree |
| 2 | After documented provisioning + bootstrap, `doctor --strict` passes | run |
| 3 | AIG full run produces `generated_resume.json` + all required evidence/aggregate receipts (DOCX not required) | artifact manifest |
| 4 | Brown & Brown full run produces the same required artifacts | artifact manifest |
| 5 | No mandatory lane fails `REQUIRED_PROOF_ABSENT` when `fact_vectors` is populated | lane evidence |
| 6 | C0.2 cannot emit PASS with zero selected evidence | C0.2 traces + tests |
| 7 | Integrated CLI exits non-zero for blocked/error runs | `echo $?` |
| 8 | Blocked runs emit `run_report.json` + diagnostics | bundle |
| 9 | Whole-resume aggregation gates pass and aggregate failure blocks final X3 | aggregate receipts |
| 10 | Generated employer content (Unify/IBM/InsurTech/EY) proven generate-N/select-X from graph/role-episode/proof-pool; base-resume prose absent from generated lanes | receipts + C0 traces |
| 11 | Base-resume n-gram demoted to advisory; verbatim-copy + hydration-operation blockers retained | tests 4–6 |
| 12 | Product-mode tests green **without** `APPS_RG_TEST_HARNESS` | CI job |
| 13 | DOCX is optional export smoke only; no DOCX CI gate | CI config |
| 14 | Empty/invalid provider output never counts as product success | test 10 |
| 15 | This plan file updated with commands + evidence paths at closeout | git diff |

## Open decisions

- Canonical output root: `runtime_proofs/` vs `runs/`.
- Authoritative source files for candidate_profile / project_evidence / graph bootstrap.
- Do all 11 lanes require dense evidence, or may locked identity sections (education/certs/early
  career) use deterministic **identity** facts with cited provenance (never base-resume prose)?
- **EY & InsurTech:** reconcile decision #3 (generated employer bullets from graph/role-episode/
  proof-pool) with the legacy core rule that lists EY/InsurTech as "locked deterministic." Confirm:
  identity locked, bullets generated-from-evidence — and confirm EY/InsurTech have the graph/
  role-episode wiring (only **Unify + IBM** are confirmed wired in the repo today).
- Canonical embedding model id + dimension (bge-m3 / 1024) and the single embedding function.
- AIG/Brown as required PR checks vs nightly smoke.
- Canonical aggregate-X2 receipt filename.

## Immediate command shape

> Placeholders — `doctor` and `bootstrap` subcommands do not exist yet (W1/W3 introduce them); flags
> should match the repo CLI style. Behavior, not exact syntax, is the contract.

```
python -m apps_rg doctor --strict
python -m apps_rg bootstrap fact-vectors --strict
python -m apps_rg --target-company "AIG" --target-role "VP, Global Head of Agentic AI Solutions" \
  --target-level EXECUTIVE --jd <jd> --manual-brief <brief> --strict
python -m apps_rg --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" \
  --target-level EXECUTIVE --jd <jd> --manual-brief <brief> --strict
```

## ADG pre-execution gate

W2/W3/W4 touch the C0 lane and disposition aggregation (T2/T3). Per constitutional §5/§22, capture
`ADG_HOTSPOT_REPORT` + `ADG_GRAPH_LAYER_EVIDENCE` (blast radius for
`apps_rg/runtime/bindings/c0_binding.py` and `apps_rg/runtime/c0/c02_product_hybrid_retrieval.py`)
before code edits begin.
