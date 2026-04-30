# apps_* runtime-mode scorecard

**Methodology**: AST scan of every `apps_*/` package (excluding tests/fixtures). Detects (a) imports of canonical authority-class contracts FROM `agentic_core`, (b) domain-runtime markers (engines/integrations/router/CLI/wizard), and (c) infrastructure imports (UWG/ledger/BGE). Classifies per the five-bucket taxonomy in `docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md`.

**Authority-class contracts**: `CommitRequest`, `CompiledPromptArtifact`, `ExitReviewPacket`, `FinalEvidenceContract`, `GateVerdict`, `L1PlanContract`, `MutationIntent`, `PromptEnvelope`, `RetrievalPlan`, `RouteContract`, `RuntimeExhaustBundle`, `SealedArtifact`, `StateDiffCandidate`, `ValidatedRequest`

| App | Files | Spine % (legacy) | Contracts | Distinct contracts | Claims runtime | Runtime Mode |
|---|---:|---:|---:|---|:---:|---|
| `apps_eval` | 59 | 29.9% | 0 | ΓÇö | Γ£ô | ≡ƒƒá PARTIAL_SPINE_STATIC_ONLY |
| `apps_exec` | 54 | 48.1% | 0 | ΓÇö | Γ£ô | ≡ƒƒá PARTIAL_SPINE_STATIC_ONLY |
| `apps_lic` | 90 | 60.6% | 0 | ΓÇö | Γ£ô | ≡ƒƒá PARTIAL_SPINE_STATIC_ONLY |
| `apps_qna` | 42 | 5.1% | 0 | ΓÇö | Γ£ô | ≡ƒƒá PARTIAL_SPINE_STATIC_ONLY |
| `apps_research` | 54 | 44.2% | 0 | ΓÇö | Γ£ô | ≡ƒƒá PARTIAL_SPINE_STATIC_ONLY |
| `apps_rfp` | 53 | 26.5% | 0 | ΓÇö | Γ£ô | ≡ƒƒá PARTIAL_SPINE_STATIC_ONLY |
| `apps_rg` | 171 | 57.7% | 1 | `PromptEnvelope` | Γ£ô | Γ£à APP_OVERLAY_STATIC_EVIDENCE |
| `apps_shared` | 194 | 54.1% | 1 | `SealedArtifact` | Γ£ô | Γ£à APP_OVERLAY_STATIC_EVIDENCE |
| `apps_underwriting_ai` | 68 | 21.1% | 0 | ΓÇö | Γ£ô | ≡ƒƒá PARTIAL_SPINE_STATIC_ONLY |

## Runtime-mode legend

- Γ£à **APP_OVERLAY_VALID** ΓÇö imports ΓëÑ1 canonical authority contract from `agentic_core`. Delegates to the spine.
- ∩┐╜ **APP_STANDALONE_FORBIDDEN** ΓÇö claims a domain runtime (engines/integrations/router/CLI) AND imports zero canonical contracts AND zero spine edges. Shadow runtime.
- ≡ƒƒá **PARTIAL_SPINE_STATIC_ONLY** ΓÇö claims domain runtime AND imports spine infrastructure (UWG/ledger/BGE), BUT no authority-class contracts. Static-only spine touch.
- Γ¥ö **UNKNOWN_NEEDS_RUNTIME_TRACE** ΓÇö does not claim a domain runtime; static analysis cannot decide. Runtime trace required.
- ∩┐╜ **CORE_ONLY_VALID** ΓÇö reserved for non-`apps_*` paths.

## Per-app classification evidence

- ≡ƒƒá **`apps_eval`** ΓåÆ PARTIAL_SPINE_STATIC_ONLY
  - claims domain runtime AND imports spine infrastructure (UWG/ledger/BGE), BUT zero canonical contract imports; static-only spine touch, runtime authority is local to the app -- not valid as overlay
  - claims runtime via: engines directory present, integrations directory present, package entrypoint present
- ≡ƒƒá **`apps_exec`** ΓåÆ PARTIAL_SPINE_STATIC_ONLY
  - claims domain runtime AND imports spine infrastructure (UWG/ledger/BGE), BUT zero canonical contract imports; static-only spine touch, runtime authority is local to the app -- not valid as overlay
  - claims runtime via: engines directory present, integrations directory present, package entrypoint present
- ≡ƒƒá **`apps_lic`** ΓåÆ PARTIAL_SPINE_STATIC_ONLY
  - claims domain runtime AND imports spine infrastructure (UWG/ledger/BGE), BUT zero canonical contract imports; static-only spine touch, runtime authority is local to the app -- not valid as overlay
  - claims runtime via: engines directory present, integrations directory present, package entrypoint present, control-plane module present
- ≡ƒƒá **`apps_qna`** ΓåÆ PARTIAL_SPINE_STATIC_ONLY
  - claims domain runtime AND imports spine infrastructure (UWG/ledger/BGE), BUT zero canonical contract imports; static-only spine touch, runtime authority is local to the app -- not valid as overlay
  - claims runtime via: integrations directory present, router subpackage present, package entrypoint present, interactive wizard present
- ≡ƒƒá **`apps_research`** ΓåÆ PARTIAL_SPINE_STATIC_ONLY
  - claims domain runtime AND imports spine infrastructure (UWG/ledger/BGE), BUT zero canonical contract imports; static-only spine touch, runtime authority is local to the app -- not valid as overlay
  - claims runtime via: engines directory present, integrations directory present, package entrypoint present
- ≡ƒƒá **`apps_rfp`** ΓåÆ PARTIAL_SPINE_STATIC_ONLY
  - claims domain runtime AND imports spine infrastructure (UWG/ledger/BGE), BUT zero canonical contract imports; static-only spine touch, runtime authority is local to the app -- not valid as overlay
  - claims runtime via: engines directory present, integrations directory present, package entrypoint present
- Γ£à **`apps_rg`** ΓåÆ APP_OVERLAY_STATIC_EVIDENCE
  - no spine_manifest.yaml; imports 1 canonical contract(s) (PromptEnvelope); declare a manifest to enable route-typed validation
  - contracts: PromptEnvelope
  - claims runtime via: engines directory present, integrations directory present, package entrypoint present
- Γ£à **`apps_shared`** ΓåÆ APP_OVERLAY_STATIC_EVIDENCE
  - no spine_manifest.yaml; imports 1 canonical contract(s) (SealedArtifact); declare a manifest to enable route-typed validation
  - contracts: SealedArtifact
  - claims runtime via: integrations directory present
- ≡ƒƒá **`apps_underwriting_ai`** ΓåÆ PARTIAL_SPINE_STATIC_ONLY
  - claims domain runtime AND imports spine infrastructure (UWG/ledger/BGE), BUT zero canonical contract imports; static-only spine touch, runtime authority is local to the app -- not valid as overlay
  - claims runtime via: engines directory present, integrations directory present
