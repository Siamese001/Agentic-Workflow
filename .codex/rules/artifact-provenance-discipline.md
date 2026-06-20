# Artifact Provenance Discipline — stub

> On-demand (plan `always-on-rule-surface-cut-c7f3a1`). ⚠️ Doctrine-only (no enforcing hook) — invariant preserved here.
> **Invariant (load-bearing):** before citing ANY JSON artifact as evidence for a specific run, VERIFY its identity fields (`run_id`, `emitted_at`, `request_id`, …) match that run. Never substitute a nearest-match artifact. If the target run did not emit the artifact, **state the absence** — never silently substitute one from another run or a `certification/integrated_runtime/` fixture. Cross-run citation requires explicit disclosure ("from run X, NOT the run under analysis") before any derived content. Ref: constitutional §20; RCA 2026-05-07.
