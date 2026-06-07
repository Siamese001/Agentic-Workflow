
# P-Band burndown waves — execution discipline

When burning down **P0 → P1 → P2** (plan waves, `adg_p0_wave_plan`, `adg_violations`, or `artifacts/adg/` burndown outputs):

1. **Select** the next seam from the wave table, burndown row, or P-view — one scoped item per pass unless the user batches explicitly.
2. **Patch** the smallest change that clears the violation or satisfies the wave deliverable; no drive-by refactors.
3. **Prove** with the narrowest gate, regen slice, or test; report the repo evidence floor (`STATUS`, `FILES_CHANGED`, `COMMANDS_RUN`, `TESTS_GATES`).
4. **Omit** tutorial narration, restating the hotspot protocol, and generic “what P0 means” unless the user asked for explanation or status is **BLOCKED** / needs a decision.

**Unchanged obligations**: Author-Gate and `ask_user_question` when rules require; `WAVE_START` / `WAVE_COMPLETE` (and related lifecycle) when executing multi-wave plans; structured-reasoning (`SR_*`) before edits on T2/T3 per `sequential-thinking-enforcement.md`.

**Protocol detail**: `adg-analysis-procedures.md` §2 (hotspot analysis and wave ordering).
