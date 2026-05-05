# apps_rg — AI Résumé Generator

Generates targeted résumés from a candidate profile + target-role description, using **grounded synthesis over the candidate's history** — not creative writing. Demonstrates per-domain agent specialization, ATS-coverage discipline, and anti-overfitting evaluation.

## Design Patterns at Work

- **52-Engine Specialist Composition** — `engines/` holds 52 small, single-responsibility engines (achievement_prioritizer, ats_coverage_engine, claim_grounder, length_governor, …). The orchestrator composes them; no engine knows about another. Adding a capability means adding an engine, not editing a monolith.
- **Grounded-Read Route (R3)** — `apps_rg` is a **read-side** app. It does **not** perform durable writes; it returns a generated résumé as a read-side artifact under `R3_grounded_read`. Spine claim asserted in `spine_manifest.yaml`; boundary tests enforce it.
- **No-Fabrication Invariant** — every claim in the output traces to an entry in the candidate profile. The evidence-density check flags any position where claims-per-position exceeds evidence support — anti-overfitting at runtime, not just at eval.
- **ATS Coverage Gate** — résumé must cover ≥ 80% of target-role keywords (configurable per industry). Below threshold → block emission, surface gap report.
- **HOP-Substrate Adapters** — `engines/hop_*.py` bridge to the shared `HopPipelineExecutor` (from `apps_shared/reasoning/orchestration/`) so `apps_rg` walks the same declarative pipeline shape as `apps_lic` and `apps_underwriting_ai`.
- **R1A / R1B Cache Layering** — exact-match cache (R1A) shorts non-novel runs; semantic cache (R1B) handles paraphrased target roles. Cache hits short-circuit before the engine grid.

## Quick Start

```bash
# Generate résumé for a target role
python -m apps_rg --candidate "candidate.yaml" --target-role "Senior ML Engineer" --industry technology

# Dry run — plan but don't emit
python -m apps_rg --candidate input/profile.yaml --target-role "Staff Engineer" --dry-run
```

## Pipeline

```
Candidate Profile + Target Role
    → ProfilePlanner / JdPlanner (apps_rg/L1_cognition/)
    → ResumeRequest decomposition (L1 query_planner)
    → L0 AgenticRouter dispatch (R3_grounded_read route)
    → R1A exact / R1B semantic cache check (cache/)
    → ResumeAssemblyEngine (52 specialist engines under engines/)
    → ATS Coverage gate + Anti-overfitting check (integrations/)
    → Renderer (Markdown / DOCX)
    → FEC populate + RunSummary
```

## Quality Gates

- **ATS coverage** — résumé must cover ≥ 80% of target-role keywords (configurable per industry)
- **Anti-overfitting** — evidence-density check; flags if claims-per-position exceed evidence support
- **Length bounds** — 1 page (junior) / 2 pages (senior); hard ceiling enforced at render
- **No-fabrication** — every claim must trace to an entry in the candidate profile

## Folder Structure

```
apps_rg/
├── L1_cognition/              # message_planner, profile_planner, jd_planner
├── config/                    # agent_spec_config, hop_pipeline, domain_contract YAMLs
├── engines/                   # 52 specialist engines (achievement_prioritizer, ats_coverage_engine, ...)
│                              # plus hop_*.py HOP-substrate adapters
├── enforcement/               # HardenedAnthropicExecutorStrategy
├── cache/                     # R1A exact / R1B semantic / chunk commit
├── chunking/                  # resume_chunker
├── cert/                      # FEC producer + cert init
├── integrations/              # anti_overfitting, ats_coverage, hop adapters
├── reasoning/                 # Orchestrators
├── utils/                     # anthropic_rag_entrypoint
├── __main__.py
├── bootstrap_runtime.py       # ADG bootstrap (graceful degrade if unavailable)
└── spine_manifest.yaml        # static spine-route claim (R3_grounded_read)
```

## Route Contract

`R3_grounded_read` — on-demand grounded synthesis. `apps_rg` does **not** perform durable writes; it returns a generated résumé as a read-side artifact. See `spine_manifest.yaml` for the canonical claim.

## Artifacts

Default emit directory `rg/`:

- `resume_<role>_<trace_id[:8]>.md` — generated résumé
- `resume_manifest_<trace_id[:8]>.json` — section + ATS-coverage manifest
- `run_summary_<trace_id[:8]>.json` — provenance + gate results

## Companion Docs

- `AGENTIC_SPINE.md` — spine alignment + route claim
- `RUNBOOK.md` — on-call decision tree and remediation procedures
- `SLO.md` — service level objectives and cost ceilings
- `SVP_ENGINEERING_REVIEW.md` — architectural review and SVP standards compliance
