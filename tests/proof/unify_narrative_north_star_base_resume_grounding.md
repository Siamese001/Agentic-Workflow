# Unify narrative north-star — base resume grounding (canonical fixture)

The canonical base résumé [`apps_rg/resume/base/amit_ayer_base_resume_v1.json`](../../apps_rg/resume/base/amit_ayer_base_resume_v1.json) includes `exp_unify_001.role_narrative` with substantiation for:

- platform roadmap
- core systems architecture
- commercialization
- production-grade generative AI Solution Accelerator
- consulting firm
- Fortune 500 financial institutions
- bespoke client delivery
- reusable IP
- enterprise lines of business

The narrative lane exposes this as synthetic fact id `unify_narrative_base_001` in `selected_fact_plan` / `ALLOWED_SOURCE_FACT_IDS` when that field is non-empty. If a different base JSON omits `role_narrative`, do not inject those claims; record a gap in `gap_notes` instead.
