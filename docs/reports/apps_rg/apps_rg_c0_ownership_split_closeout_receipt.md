# apps_rg C0 ownership split — closeout receipt

## STATUS: PARTIAL

Scoped apps_rg C0 ownership split is implemented with **21 hardened contract tests** (all PASS). Canonical section CLI ran with real `qwen_vllm` and emitted C0 room artifacts; product X3 was BLOCK (judge path), so this is not RELEASE_ELIGIBLE_PROOF.

## SCOPE_MATCH

- apps_rg section room is the default FEC authority; `merge_canonical_c0` / spine enrich off by default.
- Core binding limited to contracts, `EvidenceItem`/`FinalEvidenceContract`, and optional explicit `c0_retrieve_apps_rg` when `APPS_RG_SPINE_CHROMA_ENRICH=1`.
- C0.3 renamed to `c03_skills_graph_v1`; `canonical_c0_3_claimed=false` unless core GraphRAG runs.
- C0.6 fake receipt-only refine removed from room orchestration.
- Metrics `SupportTarget` uses proof prefixes only (`fact:`, `ledger:`, `proof_pool:`, `srfs:`).
- No `agentic_core` product logic changes.

## SCOPE_DRIFT

- [native_c03_skills_graph.py](apps_rg/runtime/native_c03_skills_graph.py): `canonical_c0_3_claimed` now false for native skills-graph FEC (aligns with ownership law).
- [test_native_c03_skills_graph.py](tests/unit/apps_rg/test_native_c03_skills_graph.py): executive-summary test uses direct `merge_native_c03_into_proof_pool_metadata` (resolver path for exec summary does not auto-enrich).

## FILES_CHANGED

- [c0_section_authority.py](apps_rg/runtime/c0/c0_section_authority.py)
- [c05_fec_packet.py](apps_rg/runtime/c0/c05_fec_packet.py)
- [evidence_room.py](apps_rg/runtime/c0/evidence_room.py)
- [c03_graph_expansion.py](apps_rg/runtime/c0/c03_graph_expansion.py)
- [c07_handoff_audit.py](apps_rg/runtime/c0/c07_handoff_audit.py)
- [c0_metrics_writer.py](apps_rg/runtime/bindings/c0_metrics_writer.py)
- [section_lane_c0_metrics.py](apps_rg/runtime/bindings/section_lane_c0_metrics.py)
- [native_c03_skills_graph.py](apps_rg/runtime/native_c03_skills_graph.py)
- [test_apps_rg_c0_ownership_split.py](tests/_apps_contract/test_apps_rg_c0_ownership_split.py)
- [test_c0_evidence_room.py](tests/unit/apps_rg/test_c0_evidence_room.py)
- [test_c0_evidence_room_generated_lanes_e2e.py](tests/_apps_contract/test_c0_evidence_room_generated_lanes_e2e.py)
- [test_c0_evidence_room_competencies_e2e.py](tests/_apps_contract/test_c0_evidence_room_competencies_e2e.py)
- [test_rg_w3_c0_metrics_artifact.py](tests/_apps_contract/test_rg_w3_c0_metrics_artifact.py)
- [test_native_c03_skills_graph.py](tests/unit/apps_rg/test_native_c03_skills_graph.py)

## COMMANDS_RUN

- `python -m pytest tests/unit/apps_rg/test_c0_evidence_room.py tests/_apps_contract/test_apps_rg_c0_ownership_split.py tests/unit/apps_rg/test_native_c03_skills_graph.py tests/_apps_contract/test_rg_w3_c0_metrics_artifact.py::TestSupportTargetMet tests/_apps_contract/test_c0_evidence_room_generated_lanes_e2e.py -q` → exit 0 (57 passed)
- `python -m apps_rg --section headline ...` (Brown & Brown targeting, `qwen_vllm`) → process exit 1, artifacts collected, `RUNTIME_GENERATION_STATUS: REAL_LLM`
- `git diff --name-only agentic_core` → empty

## TESTS_GATES

| Gate | Result |
|------|--------|
| [test_apps_rg_c0_ownership_split.py](../../tests/_apps_contract/test_apps_rg_c0_ownership_split.py) | PASS (21) |
| C0 evidence room unit + generated-lane e2e | PASS (bundled in prior run) |

## ARTIFACTS_WRITTEN

Runtime proof dir: [c0_ownership_split_proof](artifacts/apps_rg/runtime_proofs/headline/c0_ownership_split_proof)

| Artifact | Path |
|----------|------|
| C0.1 plan | [c01_retrieval_plan.json](artifacts/apps_rg/runtime_proofs/headline/c0_ownership_split_proof/c01_retrieval_plan.json) |
| C0.2 atoms | [c02_atoms.json](artifacts/apps_rg/runtime_proofs/headline/c0_ownership_split_proof/c02_atoms.json) |
| C0.2 vector query | [c02_vector_query.json](artifacts/apps_rg/runtime_proofs/headline/c0_ownership_split_proof/c02_vector_query.json) |
| Room receipt | [c0_evidence_room_receipt.json](artifacts/apps_rg/runtime_proofs/headline/c0_ownership_split_proof/c0_evidence_room_receipt.json) |
| FEC bridge | [final_evidence_contract_bridge.json](artifacts/apps_rg/runtime_proofs/headline/c0_ownership_split_proof/final_evidence_contract_bridge.json) |
| C0 metrics | [c0_metrics.json](artifacts/apps_rg/runtime_proofs/headline/c0_ownership_split_proof/c0_metrics.json) |
| Compiled prompt | [compiled_prompt_artifact.json](artifacts/apps_rg/runtime_proofs/headline/c0_ownership_split_proof/compiled_prompt_artifact.json) |
| X2 | [x2_gate_outputs.json](artifacts/apps_rg/runtime_proofs/headline/c0_ownership_split_proof/x2_gate_outputs.json) |
| X3 | [x3_disposition.json](artifacts/apps_rg/runtime_proofs/headline/c0_ownership_split_proof/x3_disposition.json) |

Runtime receipts confirm: `spine_chroma_enrich=false`, `canonical_c0_3_claimed=false`, `apps_rg_c03_skills_graph_used=true`, `core_c03_graph_rag_used=false`, `c0_authority_mode=ledger_graph_primary`.

## CANONICAL_RUNTIME_PROOF

```text
python -m apps_rg --section headline --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md --provider qwen_vllm --allow-non-allow-exit-zero --artifact-dir artifacts/apps_rg/runtime_proofs/headline/c0_ownership_split_proof
```

## PROOF_CLASSIFICATION

- **CONTRACT_TEST_PROOF**: PASS (57 tests)
- **LIVE_RUNTIME_PROOF**: PARTIAL — real LLM generation; X3 BLOCK on configured X1D judges
- **RELEASE_ELIGIBLE_PROOF**: not claimed

## EXPLICIT_NON_CLAIMS

- No release eligibility (X3 BLOCK on headline run).
- No live core GraphRAG on section room path.
- No spine enrichment authority unless `APPS_RG_SPINE_CHROMA_ENRICH=1`.
- No durable L4 write / UWG proof in this seam.

## FORBIDDEN_FILES_TOUCHED

- **no** — `git diff --name-only agentic_core` empty

## NEXT_BLOCKER

- For RELEASE_ELIGIBLE: rerun lane with all configured X1D judges model-backed PASS, or scope judge set for product proof.
- Optional: implement bounded C0.2 retry if C0.6 is required again (currently disabled).
