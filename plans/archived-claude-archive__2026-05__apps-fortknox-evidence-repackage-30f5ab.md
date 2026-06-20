---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-fortknox-evidence-repackage-30f5ab.md'
original_relative_path: '_archive\\2026-05\\apps-fortknox-evidence-repackage-30f5ab.md'
source_sha256: 2e323862923d4a5b77fab397aa4064d9142900fac5f1ca5cd5d28c0d69557206
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps Fort Knox Evidence Repackage — Close ChatGPT's Six Findings

> **Status:** Draft · **Slug:** `apps-fortknox-evidence-repackage-30f5ab` · **Owner:** Cursor Agent · **Related:** `apps-fort-knox-parity-c5d9a3.md`, ADR-080, constitutional §32
>
> **Trigger:** ChatGPT 2026-05-03 review of `certification/apps/` zip flagged six evidence-integrity gaps. None are app-behavior bugs; all are evidence-packaging / regeneration-lockstep gaps.

## 1. Goal

Bring the apps_* Fort Knox certification package to a state where the **signature envelope, the consolidated 100% runtime proof, and the requirements catalog metadata are all coherent against the current 45-row signoff report**, the package is reproducible from a clean tree (or a documented dirty-tree manifest), and the zip handed to a third-party reviewer contains the raw runtime payloads it currently only references by hash.

Out of scope: anything that changes app runtime behavior, app rubric weights, judge implementations, or grader semantics. Out of scope: cosign keyless / GitHub OIDC promotion (still tracked by parent plan §11 row D.5).

## 2. Verdict on ChatGPT's six findings (DIRECTLY OBSERVED)

| # | Finding | Status | Root cause | Wave |
|---|---|---|---|---|
| 1 | Signature signs 33 rows; current report has 45 rows | **CONFIRMED** | Sign step ran before W5 of `apps-runtime-domain-enforcement-a7e9d4` added 12 DOM rows; never re-signed. | W2 |
| 2 | `APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json` shows `row_total=33` | **CONFIRMED (but self-disclosed)** | Same generation lag. File honestly reports `final_signed_certification: false`. | W2 |
| 3 | `apps_e2e_requirements_source.json` declares `requirement_count: 33` but file has 45 rows | **CONFIRMED** | Manual `requirement_count` field not auto-derived from `len(requirements)`. | W1 |
| 4 | Raw runtime payloads missing from zip | **CONFIRMED for zip; FALSE for repo** — payloads verified on disk at `artifacts/apps_<x>/runs/<ts>/...`. | Zip-scoping rule excluded `artifacts/apps_*/`. | W4 |
| 5 | `git_dirty: true` in evidence | **CONFIRMED** | Run executed against a working tree with uncommitted edits. | W3 |
| 6 | Some apps show `static_dag_missing_entirely` in static DAG proof | **CONFIRMED & by-design** | SINGLE_STEP / terminal routes legitimately bypass L3 per L0/L3 doctrine. Documentation precision only. | W5 |

Findings 1, 2, 3 share a single root cause and resolve together once a "regenerate-then-sign" pipeline is enforced. 4 and 5 are packaging/cleanliness. 6 is documentation.

## 3. Files In Scope

- `certification/apps_e2e_requirements_source.json` (canonical; `certification/apps/source_inputs/` is a copy)
- `scripts/compile_apps_e2e_signoff.py`
- `tools/cert/apps_e2e/sign_apps_release.py` (or equivalent signer)
- `tools/cert/apps_e2e/verify_apps_release_signature.py`
- `tools/certification/generate_apps_100pct_runtime_proof.py`
- `ops_scripts/ci/check_apps_fortknox_signed_proof.py` (T7s.4 gate; tighten dirty-tree + lockstep checks)
- `tools/certification/package_apps_e2e_zip.py` (NEW — W4)
- `docs/architecture/adr/ADR-080-*.md` §11 binding matrix (status update only)

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.P1, W1.P2 | Auto-derive `requirement_count`; add lockstep regen check | ~4k | catalog file is the SSOT; `apps/source_inputs/` is a snapshot copy | ☐ Todo | `requirement_count == len(requirements)` enforced in compiler + CI gate |
| W2 | W2.P1, W2.P2, W2.P3 | Re-run compile → re-sign → re-consolidate against 45-row catalog | ~5k | sign key still valid; verifier passes | ☐ Todo | signature envelope reports `report_row_count: 45`, `report_sha256: c27e4cb…`, `merkle_root: 0a0811a3…`; consolidated proof reports `row_total: 45` |
| W3 | W3.P1, W3.P2 | Clean-tree gate or dirty-tree manifest discipline | ~3k | parent plan §11 already has `git_dirty` field | ☐ Todo | CI gate refuses to sign when `git_dirty=true` unless `DIRTY_TREE_ACK=<file-list>` envvar is set with explicit list captured into envelope |
| W4 | W4.P1, W4.P2 | Build a self-contained reviewer zip that includes raw runtime payloads | ~4k | payloads exist under `artifacts/apps_<x>/runs/<ts>/`; manifests already SHA-link them | ☐ Todo | `package_apps_e2e_zip.py --include-runtime` produces a zip whose every manifest `path` resolves inside the zip; reviewer can hash-verify offline |
| W5 | W5.P1 | Tighten static-DAG language so "missing" reads as "not required" | ~1k | doctrine already documents SINGLE_STEP bypass | ☐ Todo | static_l3_dag_proof writes `dag_required: false, reason: "execution_form=SINGLE_STEP"` instead of `static_dag_missing_entirely` for non-managed apps |
| W6 | W6.P1 | End-to-end re-verification + ADR-080 §11 binding-matrix update | ~2k | all prior waves green | ☐ Todo | full pipeline reproduces signed envelope from clean tree in a single command; 0 stale fields anywhere |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Auto-derive `requirement_count` | `scripts/compile_apps_e2e_signoff.py`; the catalog JSON itself (one-time recompute) | Two copies of the catalog (`certification/` and `certification/apps/source_inputs/`) — pick canonical, make the other a generated mirror | ~2k | ☐ Todo |
| W1.P2 | CI gate: catalog metadata lockstep | `ops_scripts/ci/check_apps_fortknox_signed_proof.py` (extend) | Need a check that `requirement_count == len(requirements)` AND `len(rows) == requirement_count` AND no orphan rows. Advisory→fail-closed via `APPS_FORTKNOX_LOCKSTEP_FAIL_CLOSED=1` | ~2k | ☐ Todo |
| W2.P1 | Recompile signoff report from 45-row catalog | `scripts/compile_apps_e2e_signoff.py` invocation | Need to re-run all 45 evidence-assertion verifications, not just compose. Must keep `git_commit` / `run_timestamp_utc` consistent across the three artifacts. | ~2k | ☐ Todo |
| W2.P2 | Re-sign current 45-row report | `tools/cert/apps_e2e/sign_apps_release.py` | Signer must read live `.sha256` sidecar and `.merkle.json`, not stale envelope. Output overwrites `apps_e2e_signoff_report.signature.json`. | ~1k | ☐ Todo |
| W2.P3 | Re-generate consolidated 100% proof | `tools/certification/generate_apps_100pct_runtime_proof.py` | Verify `row_total: 45`, `signature_verified: true` against the freshly written envelope, `live_signature_re_verify.passed: true`. | ~2k | ☐ Todo |
| W3.P1 | Clean-tree gate before sign | `ops_scripts/ci/check_apps_fortknox_signed_proof.py` (extend) | Refuse to sign when `git diff --quiet` fails. Bypass: `DIRTY_TREE_ACK=<comma-list>` env var; bypass list captured verbatim into envelope `dirty_tree_acknowledged_paths`. | ~2k | ☐ Todo |
| W3.P2 | Dirty-tree manifest persistence | signer + envelope schema | When bypass used, envelope grows `dirty_tree_manifest: {commit, paths, sha256_per_path, ack_reason}`. Verifier replays paths and confirms hashes. | ~1k | ☐ Todo |
| W4.P1 | Reviewer-bundle zip builder | `tools/certification/package_apps_e2e_zip.py` (NEW; SSOT folder routing → `tools/certification/`) | Walks every `*_artifact_manifest.json`, copies referenced paths into zip preserving structure, drops files whose hash mismatches the manifest, writes `INVENTORY.md`. | ~3k | ☐ Todo |
| W4.P2 | Reviewer-bundle smoke test | `tests/_apps_contract/test_reviewer_bundle_zip.py` (NEW) | Build a zip, unpack to temp dir, walk every manifest path and assert file present + sha256 matches. No external network. | ~1k | ☐ Todo |
| W5.P1 | Static-DAG message clarity | `tools/cert/apps_e2e/emit_static_l3_dag_proof.py` (or wherever the field is written) | Replace the `static_dag_missing_entirely` literal with structured `{dag_required: bool, reason: str}`. Old field aliased for one cycle. Update one consumer test. | ~1k | ☐ Todo |
| W6.P1 | Full pipeline re-verify + ADR-080 §11 update | `docs/architecture/adr/ADR-080-*.md` | Single make-target / runbook command rebuilds catalog stamp → compiler → signer → consolidator → reviewer-zip → verifier. Bind-matrix row "evidence repackage" added with completion status. | ~2k | ☐ Todo |

## 6. ADG_HOTSPOT_REPORT

This plan is **evidence-packaging only**, not source-refactoring. No new code in `agentic_core/L*/`. Hotspot table is therefore non-applicable per the spirit of constitutional §22 — the plan touches `tools/cert/apps_e2e/` and `tools/certification/` (L7 utility surface, not L0–L6). Recording explicitly so the §22 gate can confirm "no L0–L6 nodes touched, hotspot table waived".

## 7. ADG_GRAPH_LAYER_EVIDENCE

Same waiver as §6. The plan modifies certification scripts and one CI gate; it does not refactor production layers. No `mv_*` / semantic-edge / P-view evidence is required because no production layer is being restructured. (Constitutional §22 enforces this section for *T2/T3 refactoring* plans; this is a packaging/build-pipeline plan.)

## 8. Gap Register

| Gap | Detected | Disposition |
|---|---|---|
| Catalog `requirement_count` field manually written | ChatGPT review 2026-05-03 | W1.P1 — auto-derive |
| Signature envelope re-sign not part of compile pipeline | ChatGPT review 2026-05-03 | W2 — wire into single make-target |
| Reviewer zip omits raw payloads | ChatGPT review 2026-05-03 | W4 — new packager |
| Dirty-tree allowed silently | ChatGPT review 2026-05-03 | W3 — explicit ACK envvar |
| Static-DAG "missing" message ambiguous | ChatGPT review 2026-05-03 | W5 — structured field |
| **Cosign keyless / GitHub OIDC** | parent plan §11 row D.5 | **Out of scope** for this plan |

## 9. AG_QUEUE_SEED markers

```
AG_QUEUE_SEED: plan=apps-fortknox-evidence-repackage-30f5ab id=AG-CATALOG-SSOT depends_on= title=Choose canonical catalog: certification/apps_e2e_requirements_source.json vs certification/apps/source_inputs/apps_e2e_requirements_source.json
AG_QUEUE_SEED: plan=apps-fortknox-evidence-repackage-30f5ab id=AG-DIRTY-ACK-SHAPE depends_on=AG-CATALOG-SSOT title=Dirty-tree ACK shape — env-var path-list vs YAML manifest committed alongside envelope
AG_QUEUE_SEED: plan=apps-fortknox-evidence-repackage-30f5ab id=AG-ZIP-SCOPE depends_on= title=Reviewer-zip default scope — full runtime payloads (~hundreds of MB) vs payloads-on-request flag
AG_QUEUE_SEED: plan=apps-fortknox-evidence-repackage-30f5ab id=AG-DAG-FIELD-RENAME depends_on= title=Static-DAG field rename — keep static_dag_missing_entirely as alias for one cycle vs hard cut
```

## 10. Verification

Each wave concludes with this command sequence reproducing a coherent envelope from clean tree:

```
git status --porcelain                                    # must be empty
python scripts/compile_apps_e2e_signoff.py
python tools/cert/apps_e2e/sign_apps_release.py
python tools/certification/generate_apps_100pct_runtime_proof.py
python tools/cert/apps_e2e/verify_apps_release_signature.py    # exit 0
python tools/certification/package_apps_e2e_zip.py --include-runtime --out reviewer_bundle.zip
python ops_scripts/ci/check_apps_fortknox_signed_proof.py      # exit 0
```

Acceptance after W6: `APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json` reads `row_total: 45`, `row_signed_off: 45`, `signature_verified: true`, `live_signature_re_verify.passed: true`, `git_dirty: false` (or explicit ack list non-empty), `keyless_signature_present: false` (still — that is parent plan §11 D.5 territory and remains the only gap to **FINAL_SIGNED_CERTIFICATION**).

## 11. Non-Goals

- App runtime behavior changes
- Rubric / judge / grader logic changes
- C0 FEC producer wiring (closed by `apps-eval-harness-deferred-e4a1b7` and 5 per-app plans 2026-05-03)
- cosign keyless / GitHub OIDC promotion to `FINAL_SIGNED_CERTIFICATION`
- Real LLM-judge implementation backfill (BLOCKER backlog elsewhere)

## 12. References

- Parent plan: `.cursor/plans/apps-fort-knox-parity-c5d9a3.md`
- ADR-080 §11 binding matrix
- Constitutional §32 (Fort Knox certification integrity — apps_e2e arm)
- Skill `fortknox-evidence`
- ChatGPT review summary (this turn)
