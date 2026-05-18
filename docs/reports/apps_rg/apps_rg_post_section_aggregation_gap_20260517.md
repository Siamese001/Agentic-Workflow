# apps_rg post-section aggregation — read-only gap analysis (2026-05-17)

Read-only inventory: no app code edits; compares current `apps_rg` surfaces to the target governed aggregation design.

---

## EXECUTION PROOF

- **Report path:** `docs/reports/apps_rg/apps_rg_post_section_aggregation_gap_20260517.md`
- **agentic_core vs HEAD:** `git diff HEAD -- agentic_core` → empty (no core changes from this analysis).
- After adding this report, see **REPO NOTES** section in the operator response for fresh `git status --short`.

---

## CURRENT STATE (what exists today)

apps_rg has a **deterministic assembly and package-disposition pipeline** alongside section lanes:

1. **Section lanes** emit per-lane proof directories under `artifacts/apps_rg/runtime_proofs/<lane>/{real|mock}/<run_id>/`, including structured `l2_output.json`, `x2_gate_outputs.json`, optional X1D/judge payloads, **`x3_disposition.json`** (section-scoped disposition), plus prompt/runtime metadata (e.g. `run_id`, `prompt_hash` in lane artifacts — varies by lane module).

2. **`generated_lane_rollup`** aggregates **filesystem pointers**: each lane resolves to a **chosen** successful run independently (`latest_successful_real_run.json` / migration semantics). Rollup **`rollup_id` is derived at rollup generation time**, not shared per-orchestration `run_id` across lanes.

3. **`assemble_final_resume` (`runtime/assembly/final_resume_assembler.py`)** — **deterministic**, **no LLM**: reads rollup + `locked_copy_manifest.json` + canonical base resume JSON; verifies **base_resume sha256 matches** `locked_copy_manifest.base_resume_json_hash`; embeds **verbatim `l2_output.json` snapshots** for generated lanes and **locked copied text / invariants**; writes `final_resume.json`, assembly manifest, **final_resume_x2_gate_outputs**, receipt.

4. **`run_final_resume_x2_gates` (`runtime/assembly/final_resume_x2.py`)** — aggregate **structural/provenance X2**, not semantic cross-section quality: required sections present, canonical order, generated sections from rollup “accepted” pointers, equality of snapshots vs disk, locked copy equality, invariant preservation, hashes, disposition/artifact refs present, assembly directory free of stray provider/qwen/judge/docx spill.

5. **DOCX path** (`docx_manifest_*`, `docx_render_*`): deterministic manifests + gates that **`final_resume` → manifest → plaintext extraction** aligns (hashes, order, sections rendered); checks ** substring preservation ordered** for generated blocks and locked copy (not NLP overlap).

6. **`resume_package_x3` (`runtime/package/resume_package_x3.py`)** emits **whole-resume disposition** keyed as **`final_x3_code`**, with **`section_level_x3`** rollup of per-lane `x3_disposition`. Policy: deterministic failures → `X3_BLOCKED_DETERMINISTIC_GATES`; L6 handoff audit fatal → block; **all lanes `X3_ALLOW`** → package `X3_ALLOW`; else → `X3_REVIEW_SECTION_JUDGE_STATUS`. This is apps_rg **resume_package** disposition — **orthogonal naming** vs spine “Exit emits exactly one X3” requirements (docs in exit binding emphasize not conflating **00C GateVerdict / local helpers** vs terminal disposition).

**Second convergence path (integrated R4 recipe):**

- Canonical product entry **`python -m apps_rg`** invokes **integrated R4** (`run_integrated_r4_deterministic_pipeline` imported in `apps_rg/__main__.py`).
- Modular generation merges section outputs via **`modular_rg_output_builder.build_rg_output_from_modular_sections`** into **`rg_output` schema**, separate artifact grain from **`final_resume_assembly/`** offline stack per `apps_rg/l2_recipe/r4_generation_route.py`.

---

## ARCHITECTURE FINDINGS

| Question | Answer |
|----------|--------|
| Where does aggregation live? | **apps_rg**: `runtime/assembly/`, `runtime/render/`, `runtime/package/`; rollup in `runtime/reports/generated_lane_rollup.py`. |
| Deterministic vs model-driven? | **Deterministic composition** at assembly/package/DOCX manifest layers; orchestrated lanes may call providers upstream. Assembly sets `calls.provider_calls_made` / judges false. |
| Typed artifacts vs loose blobs? | **Partially typed**: manifests and gate records; **`l2_output_snapshot` is embedded raw JSON dict** inside `final_resume.json` — replayable paths/refs exist but **not a single sealed envelope type** akin to target `AggregatedResumePackage` / typed `FinalResumeDraft`. |
| Final aggregate gates? | **Structural X2 layers** (`final_resume_x2`, DOCX manifests/render plus package checks on downstream X2 all-pass); **no dedicated cross-section semantic gates** (overlap, repetition, redundancy, length, em-dash at document scope). |
| Final aggregate vs section X3? | **Separated in `resume_package_x3`** via `final_x3_code` vs nested `section_level_x3`; local vocabulary — **mapping to spine Exit X3 requires explicit governance** (risk of nomenclature conflation below). |
| Claim ledger preservation at aggregate? | Claim ledgers exist **within lane L2 payloads** where lanes emit them; assembler **does not merge or verify cross-section ledger coverage**. |

---

## GAP MATRIX (target requirement → classification)

Legend: **PRESENT** / **PARTIAL** / **ABSENT** / **UNKNOWN**

| # | Requirement | Status | Evidence (decisive paths) |
|---|-------------|--------|---------------------------|
| 1 | Deterministic apps_rg aggregation layer exists | **PRESENT** | `final_resume_assembler.py`, rollup, package eval |
| 2 | Aggregation is app-owned | **PRESENT** | Under `apps_rg/runtime/*` |
| 3 | Section artifacts collected via typed current-run registry/manifest | **PARTIAL** | `generated_lane_rollup.json` + per-file refs; no single typed sealed registry keyed by unified **orchestration** `run_id` |
| 4 | Same-run identity enforced (`run_id` coherence across included sections) | **ABSENT** | Rollup picks **latest_successful_real per lane**; lane `run_id`s are timestamps / independent pointers |
| 5 | JD / briefing / base resume digest consistency enforced at aggregate | **PARTIAL** | Base resume digest vs locked manifest (`final_resume_assembler`); JD/briefing digests **not** verified across all sections in assembler/package |
| 6 | Blocked sections cannot be included | **PARTIAL** | **Strong** package/lane checks on x3_codes and rollup counters; deterministic block codes; **`final_resume_x2` does not assert “every section x3≠BLOCK”** explicitly (inherits from rollup + lane policy) |
| 7 | Review sections explicitly handled | **PARTIAL** | Package `final_x3_code` distinguishes review vs deterministic block (`X3_REVIEW_SECTION_JUDGE_STATUS`) |
| 8 | Locked copy preserved / checked | **PRESENT** | `final_resume_x2`, assembler, DOCX substring gates |
| 9 | `FinalResumeDraft` canonical shape | **PARTIAL** | Exists as **`final_resume.json`** with `assembled_object_id`/`sections`; naming + schema differ from target |
| 10 | `AggregatedResumePackage` or equivalent | **PARTIAL** | `resume_package_manifest.json`, `resume_package_x3_disposition.json`, receipts — conceptual match, different contract names |
| 11 | Final render deterministic | **PRESENT** (offline stack assembly path) | No LLM in assembler / manifests per guarantees |
| 12 | Markdown / text / docx refs | **PARTIAL** | **DOCX** path + plaintext verification; **`apps_rg/outputs`** renderers serve other consumption shapes **not wired as target terminal package** |
| 13 | Cross-section overlap gate | **ABSENT** (aggregate scope) | No gate in `final_resume_x2` / `docx_render_x2` for semantic overlap beyond ordered substring stitching |
| 14 | Repetition density gate | **ABSENT** (aggregate scope) | Not found |
| 15 | Competency vs bullet duplication gate | **ABSENT** (aggregate scope) | Competencies intra-lane overlap heuristics only (implementation module `competencies_dispatch.py`; canonical CLI remains `python -m apps_rg --section competencies`) |
| 16 | Summary vs bullet redundancy gate | **ABSENT** (aggregate scope) | Section-local only if present |
| 17 | Claim ledger coverage survives aggregation | **PARTIAL** | Data **carried embedded** in L2 blobs; **no aggregate verification / merged ledger |
| 18 | JD/briefing proof boundary survives aggregation | **PARTIAL / UNKNOWN** | Enforced primarily **per-section X2**; package does not re-evaluate JD-as-proof prohibition document-wide |
| 19 | Companion-section proof boundary survives aggregation | **PARTIAL / UNKNOWN** | Narrative/companion linkage is lane-local |
| 20 | No-em-dash final document gate | **ABSENT** (aggregate DOCX plaintext scan) | Not in `docx_render_x2` gates reviewed |
| 21 | Resume length budget gate | **ABSENT** (aggregate) | Not found |
| 22 | Final aggregate X2 exists | **PRESENT** | `final_resume_x2`; DOCX manifest/render X2; package consumes them |
| 23 | Final aggregate X3 exists | **PARTIAL** | **`resume_package_x3` emits `final_x3_code`** — apps_rg **package** disposition **≠** asserted spine Exit singleton without bind contract |
| 24 | Section X3 vs aggregate X3 separate | **PRESENT / PARTIAL** | Clearly split in **`resume_package_x3`** structure; terminology risk vs core Exit naming |
| 25 | Replay/audit manifest exists | **PARTIAL** | Multi-layer manifests + hashes + receipt JSON; lacks unified **replay_key** binding all lanes + digests |
| 26 | No agentic_core dependency/leakage (aggregation seam) | **PARTIAL** | **Offline orchestrator avoids core** (`orchestrate_full_resume.py` header); **`apps_rg.__main__` integrated path imports agentic_core**; assembly modules themselves are apps_rg-local |

---

## RISKS (if unchanged)

1. **Pointer-based rollup**: “Latest successful” per lane can blend **runs from different times / inputs** unless operators guarantee fresh sequential orchestration — violates target **same run_id / digest plane**.

2. **No document-level semantics**: Assembler/DOCX gates prove **fidelity / order / hashing**, not **quality as one narrative** — duplicate headlines/summary bullets can pass.

3. **Nomenclature / authority coupling**: **`final_x3_code` is apps_rg package disposition** — consumers might conflate with **constitutional single spine X3 Exit** absent explicit binding docs.

4. **Dual outputs**: **`rg_output` (integrated)** vs **`final_resume.json` (offline proof)** — risk of divergence in what downstream calls “truth.”

---

## RECOMMENDED MINIMAL DESIGN (no implementation — apps_rg only)

Proposed layering (additive, spine-neutral):

| Piece | Proposal |
|-------|----------|
| **Unified orchestration fingerprint** | `apps_rg/runtime/aggregation/run_fingerprint.py` emitting `OrchestrationRunEnvelope` `{ run_id_orch, jd_digest, briefing_digest, base_resume_digest, rollup_id, created_at_utc }` written once per orchestration and echoed into **each lane’s `runtime_manifest.json`** and rollup. |
| **Typed registry** | `apps_rg/runtime/aggregation/section_sealed_index.py`: `SectionSealedPointer` refs + hashes + lane `x3` path + **`claim_ledger` sidecar refs** mandatory where lane emits ledger. |
| **Final draft contract** | `FinalResumeDraftV2` pydantic/dataclass mapping current `final_resume.json` sections + invariant that every generated section's **embedded `prompt_hash`/digest fields** equal envelope (where applicable). |
| **Package rename (optional)** | `AggregatedResumePackage` as alias/export wrapper over current `resume_package_manifest` content for taxonomy alignment only. |
| **Cross-section gates (deterministic)** | New module `apps_rg/runtime/aggregation/cross_section_x2.py`: em-dash scan on **assembled plaintext**; token/char budget; naive n-gram / repeated phrase thresholds; competency term set vs bullets set overlap; headline vs exec summary lexical overlap threshold; claim_id union ⊆ allowed base resume facts. |
| **Tests** | `tests/_apps_contract/test_cross_section_x2_negative_controls.py`; fingerprint mismatch fixtures; rollup rejection when lane digests diverge from envelope. |

---

## STATUS FOR THIS ANALYSIS TASK

Operator response block will include **STATUS**, **COMMANDS_RUN**, etc. This document is inventory-only.
