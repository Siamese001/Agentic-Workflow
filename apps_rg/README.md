# apps_rg — AI Résumé Generator

Generates targeted résumés from a candidate profile + target-role description, using grounded synthesis over the candidate's history. Demonstrates per-domain agent specialization, ATS-coverage discipline, and anti-overfitting evaluation.

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
    → ProfilePlanner (apps_rg/L1_cognition/)
    → ResumeRequest decomposition (L1 query_planner)
    → L0 AgenticRouter dispatch (R3_grounded_read route)
    → ResumeAssemblyEngine (52 specialist engines under engines/)
    → ATS Coverage gate + Anti-overfitting check (integrations/)
    → Renderer (Markdown / DOCX)
```

## Route Contract

`R3_grounded_read` — on-demand grounded synthesis. apps_rg does **not** perform durable writes; it returns a generated résumé as a read-side artifact. See `spine_manifest.yaml` for the canonical claim.

## Folder Structure

```
apps_rg/
├── L1_cognition/              # message_planner, profile_planner
├── config/                    # agent_spec_config, hop_pipeline, domain_contract YAMLs
├── engines/                   # 52 specialist engines (achievement_prioritizer, ats_coverage_engine, etc.)
├── enforcement/               # HardenedanthropicexecutorStrategy
├── integrations/              # anti_overfitting, ats_coverage, hop adapters
├── reasoning/                 # Orchestrators
├── utils/                     # anthropic_rag_entrypoint
├── __main__.py                # CLI entrypoint
├── bootstrap_runtime.py       # ADG bootstrap (graceful degrade if unavailable)
└── spine_manifest.yaml        # Static spine-route claim (R3_grounded_read)
```

## Quality Gates

- **ATS coverage** — résumé must cover ≥ 80% of target-role keywords (configurable per industry).
- **Anti-overfitting** — evidence-density check; flags if claims-per-position exceed evidence support.
- **Length bounds** — 1 page (junior) / 2 pages (senior); hard ceiling enforced at render.
- **No-fabrication** — every claim must trace to an entry in the candidate profile.

## Artifacts

Default emit directory `rg/`:
- `resume_<role>_<trace_id[:8]>.md` — generated résumé
- `resume_manifest_<trace_id[:8]>.json` — section + ATS-coverage manifest
- `run_summary_<trace_id[:8]>.json` — provenance + gate results

## Companion Docs

- `RUNBOOK.md` — on-call decision tree and remediation procedures
- `SLO.md` — service level objectives and cost ceilings
- `SVP_ENGINEERING_REVIEW.md` — architectural review and SVP standards compliance
