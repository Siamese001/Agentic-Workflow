# Certification Review Bundle

Staged 2026-05-03 for external (ChatGPT) review of static + runtime 100% certification proofs,
including Merkle roots and detached signatures.

## Directory Layout

Fort Knox paths were relocated off the repo root (2026-05-24). SSOT is centralized in
`tools/cert/cert_paths.py`.

### Compiler inputs (`data/certification/` — committed, never regenerated blindly)

| Path | Role |
|---|---|
| `data/certification/evidence_assertions.jsonl` | agentic_core arm evidence rows fed to `tools/cert/compile_requirement_signoff.py` |
| `data/certification/evidence_manifest.jsonl` | agentic_core producer manifest (who wrote which assertion) |
| `data/certification/apps_evidence_assertions.jsonl` | apps arm evidence rows fed to `tools/cert/compile_apps_e2e_signoff.py` |
| `data/certification/apps_domain_evidence_assertions.jsonl` | apps-domain assertions merged by `tools/cert/apps_e2e/merge_assertion_streams.py` |
| `data/certification/apps_negative_control_assertions.jsonl` | mutation/negative-control rows |
| `data/certification/requirements_source.json` | agentic_core RTC-REQ-* catalogue |
| `data/certification/apps_e2e_requirements_source.json` | apps APPS-REQ-* catalogue |
| `data/certification/requirement_signoff_schema.json` | schema the signed bundle validates against |
| `config/certification/schemas/` | JSON Schemas for signoff reports and evidence assertion shapes |

### Review-bundle outputs (auto-staged under `artifacts/certification/review/`)

| Path | Role |
|---|---|
| `artifacts/certification/review/agentic_core/` | Staged review mirror for agentic_core arm |
| `artifacts/certification/review/apps/` | Staged review mirror for apps arm |
| `docs/certification/README_REVIEW.md` | This file |

The two review-bundle subfolders are repopulated automatically on every write to any input
above or to any file under `artifacts/certification/` by `.codex/governance/scripts/post_write_cert_stage.py`,
which invokes `tools/certification/_stage_review_bundle.ps1`.

Constitutional §32 (Fort Knox integrity) governs both arms: compiler output MUST NOT be
hand-edited; claims emerge ONLY from the canonical compilers named below.

## Two Arms

### `agentic_core/` — agentic_core arm (RTC-REQ-*)

| Subfolder | Contents |
|---|---|
| `compiler_output/` | `final_requirement_signoff_report.{json,md,xlsx,sha256,merkle.json,signature.json}` + bundle verifier output + `HUNDRED_PERCENT_RUNTIME_PROOF.json` + Fort Knox packets + CI-gate binding / payload-hash / layer-boundary reports |
| `positive_controls/` | `positive_control_RTC-REQ-*.json` — canary `RTC-REQ-001` plus additional positive controls |
| `mutation_rejection/` | `fortknox_mutation_rejection_report.json` + sandbox inputs (`_mutation_*.json`) — proof that mutated evidence is rejected |
| `runtime_evidence/` | Per-RTC-REQ runtime evidence subdirectories (90 reqs) |
| `integrated_runtime/` | End-to-end integrated runtime proofs, replay bundles, path-proofs ledger, live-provider readiness + rubric stability |
| `e2e/` | `agentic_core_route_matrix.json` + `agentic_core_spine_proof.json` |
| `source_inputs/` | Compiler inputs: `evidence_assertions.jsonl`, `evidence_manifest.jsonl`, `requirements_source.json`, `requirement_signoff_schema.json`, `schemas/` |
| `scripts/` | `compile_requirement_signoff.py` (compiler), `verify_final_requirement_signoff_bundle.py` (verifier), `generate_100pct_runtime_proof.py` |

**Canary**: `RTC-REQ-001`. **Compiler**: `tools/cert/compile_requirement_signoff.py`.

### `apps/` — apps_e2e arm (APPS-REQ-*)

| Subfolder | Contents |
|---|---|
| `compiler_output/` | `apps_e2e_signoff_report.{json,sha256,merkle.json,signature.json}` + `APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json` + `apps_e2e_matrix.json` + `verifier_report.json` |
| `per_app_evidence/` | Per-app evidence folders: `apps_eval`, `apps_exec`, `apps_lic`, `apps_qna`, `apps_research`, `apps_rfp`, `apps_rg`, `apps_underwriting_ai` |
| `rg_e2e/` | Dedicated `apps_rg` e2e proofs + static L3 DAG proof |
| `mutation_rejection/` | `apps_mutation_rejection_report.json` |
| `source_inputs/` | `apps_evidence_assertions.jsonl`, `apps_domain_evidence_assertions.jsonl`, `apps_negative_control_assertions.jsonl`, `apps_e2e_requirements_source.json` |
| `scripts/` | `compile_apps_e2e_signoff.py` (compiler), `generate_apps_100pct_runtime_proof.py` (consolidator) |

**Canary**: `APPS-REQ-001`. **Compiler**: `scripts/compile_apps_e2e_signoff.py`.

## Integrity Verification (reviewer guide)

For each arm, the signed bundle ships four files:

1. `*.json` — canonical payload (signed content)
2. `*.sha256` — SHA-256 of the payload
3. `*.merkle.json` — Merkle tree leaves + root over per-requirement evidence
4. `*.signature.json` — detached signature over payload hash

Recompute hash → compare `*.sha256`. Rebuild Merkle root from `evidence_assertions.jsonl` rows
→ compare `*.merkle.json.root`. Validate signature with public key under `artifacts/keys/release_signer/`.

Positive controls (canaries) in `positive_controls/` prove the compiler rejects synthetic
bad inputs. Mutation-rejection reports prove evidence mutations are detected.

## Not Included (out of scope for this review)

- In-flight evidence rows under `artifacts/certification/csv_signoff_updates/`
- Semantic-cache certification bundle (`semantic_cache_*`) — parallel cert workstream
- `_mutation_sandbox/` raw scratch files
