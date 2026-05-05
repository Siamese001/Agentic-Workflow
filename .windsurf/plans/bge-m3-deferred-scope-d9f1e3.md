# Deferred Scope — BGE-M3 Gap Closure
**Parent plan**: `bge-m3-gap-closure-c8f3a2` (Completed 2026-05-05)
**Slug**: `bge-m3-deferred-scope-d9f1e3`
**Status**: In Progress
**W1 complete** (2026-05-05). W2-W4 blocked on external dependencies.

---

## Wave Structure

| Wave | Focus | Priority | Blocker |
|---|---|---|---|
| W1 | Git history large-file cleanup | P1 — BLOCKING push | ✅ DONE |
| W2 | ADR-056 multi-head flip (sparse + ColBERT) | P2 | ADR-056 must reach Accepted |
| W3 | apps_qna E2 — LLM judges | P3 | Model creds + human-labeled holdout |
| W4 | apps_qna E3 — Provider dispatch | P4 | Blocked on W3 (E2) |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Remove model binaries from git history | `git rebase -i` / `git filter-repo`; force-push | HTTP 500 on every push attempt | ~5k | ✅ Done |
| W1.P2 | Add models--BAAI--bge-m3/ to .gitignore | `.gitignore` | Prevent re-commit | ~1k | ✅ Done (pre-existing) |
| W2.P1 | Enable sparse + ColBERT heads in bge_runtime.py | `agentic_core/embeddings/bge_runtime.py` | Flag-gated behind `BGE_MULTI_HEAD=1` | ~15k | Not Started |
| W2.P2 | Extend PROVENANCE_ENFORCED_COLLECTIONS for multi-head | `agentic_core/embeddings/exceptions.py` | Requires ADR-056 amendment | ~5k | Not Started |
| W2.P3 | Update populate_apps_qna_index.py for sparse/ColBERT sidecars | `tools/indexing/populate_apps_qna_index.py` | Re-index required after code change | ~10k | Not Started |
| W3.P1 | Implement real LLM judge for apps_qna interview cards | `apps_qna/engines/judges/` (new) | Needs human-labeled holdout + Anthropic API key | ~25k | Not Started |
| W3.P2 | Spearman calibration gate for apps_qna judge | `ops_scripts/ci/check_apps_qna_judge_spearman.py` | Needs holdout from W3.P1 | ~8k | Not Started |
| W4.P1 | Provider dispatch routing for apps_qna | `apps_qna/engines/` dispatch layer | Blocked on E2 (W3) completion | ~20k | Not Started |

---

## Gap Register

### DS-1 (P1) — Git history contains 2x ~2.27 GiB model binaries

**Root cause**: Commit `3024082a32` (`infra(complete): apps_lic multi-touch infrastructure W1-W6`) accidentally included the HuggingFace cache directory `models--BAAI--bge-m3/snapshots/`.

**Files to remove**:
- `models--BAAI--bge-m3/snapshots/5617a9f61b028005a4858fdac845db406aefb181/pytorch_model.bin` (2.27 GiB)
- `models--BAAI--bge-m3/snapshots/9a0624b896d81da7492a910ffa53731274b6cf3d/model.safetensors` (2.27 GiB)
- `models--BAAI--bge-m3/.no_exist/5617a9f61b028005a4858fdac845db406aefb181/model.safetensors`
- `models--BAAI--bge-m3/snapshots/5617a9f61b028005a4858fdac845db406aefb181/sentencepiece.bpe.model`
- `models--BAAI--bge-m3/snapshots/5617a9f61b028005a4858fdac845db406aefb181/tokenizer.json` (1M line JSON)

**Fix**:
```bash
# Option A — git filter-repo (preferred, rewrites history cleanly)
pip install git-filter-repo
git filter-repo --path "models--BAAI--bge-m3/" --invert-paths
git push origin main --force

# Option B — BFG Repo Cleaner
bfg --delete-folders "models--BAAI--bge-m3" .
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push origin main --force
```

**After fix**: Add to `.gitignore`:
```
models--BAAI--*/
```

**Impact**: Currently blocks all `git push` attempts with HTTP 500. **Highest priority.**

---

### DS-2 (P2) — ADR-056 multi-head flip (sparse + ColBERT heads)

**Context**: `agentic_core/embeddings/bge_runtime.py` today only uses the dense head of BGE-M3 (1024-d). BGE-M3 natively provides three output heads: dense (1024-d), sparse (bag-of-words weighted), and ColBERT (token-level multi-vector).

**What needs to happen**:
1. ADR-056 must be promoted from Proposed → Accepted with a concrete schema for how sparse and ColBERT vectors are stored alongside dense.
2. `PROVENANCE_ENFORCED_COLLECTIONS` in `agentic_core/embeddings/exceptions.py` must be extended with entries for sparse/ColBERT collections.
3. `tools/indexing/populate_apps_qna_index.py` must emit sidecar files (e.g., `index_sparse.json`, `index_colbert.json`) alongside `index.json`.
4. `apps_qna/c0_adapter.py::_real_fetch` must be updated to fuse dense + sparse scores (late fusion).
5. `BGE_MULTI_HEAD=1` env var gates the feature; default stays `0` until ADR-056 is accepted.

**Blocked on**: ADR-056 decision (currently Proposed). Do not implement until ADR-056 reaches Accepted.

---

### DS-3 (P3) — apps_qna E2: Real LLM judge implementation

**Context**: The `apps_qna` eval harness currently has no real LLM-as-judge for interview card quality. The `NO_UNIMPL_JUDGES` gate in `check_app_domain_harness_parity.py` does not currently fire for apps_qna because no judge roster is declared.

**What needs to happen**:
1. Author a human-labeled holdout dataset (~50–100 question/answer pairs for interview cards).
2. Implement `apps_qna/engines/judges/interview_card_quality_judge.py` with `IS_STUB=False`, `IS_CALIBRATED=True`, Spearman ≥ 0.80 on holdout.
3. Add Spearman CI gate `ops_scripts/ci/check_apps_qna_judge_spearman.py`.
4. Register judge in `apps_qna/config/domain_contract/` rubric.

**Blocked on**: Anthropic/Gemini API key available in CI + human-labeled holdout data authored.

---

### DS-4 (P4) — apps_qna E3: Provider dispatch routing

**Context**: `apps_qna` currently has no provider dispatch layer. Responses are templated; LLM provider is not invoked per-query.

**What needs to happen**:
1. Implement `apps_qna/engines/dispatch/` provider selector routing query type → Anthropic / Gemini / stub.
2. Wire dispatch result into `FinalEvidenceContract` alongside C0 retrieval sources.
3. Add E3 integration tests to `tests/_apps_contract/`.

**Blocked on**: DS-3 (E2) completion — provider quality needs judge calibration first.

---

## Non-Goals for All Waves

- Do NOT modify `healing_contexts` data or seed packs.
- Do NOT promote ADR-055 or ADR-056 status without a separate decision.
- Do NOT implement any wave until explicitly requested by the user.
- Do NOT change the existing dense BGE-M3 retrieval path (W1 of parent plan) — it is live and working.

---

## References

- Parent plan: `.windsurf/plans/bge-m3-gap-closure-c8f3a2.md` (Completed)
- ADR-055: `docs/architecture/adr/ADR-055-embedding-model-enforcement.md`
- ADR-056: referenced in ADR-055 Surface Map section
- Commit with large files: `3024082a32`
- NEXT_STEP marker emitted: plan `bge-m3-gap-closure-c8f3a2` W4 response
