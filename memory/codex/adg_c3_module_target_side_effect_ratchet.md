# ADG C3 Module-Target Side-Effect Ratchet Pattern

## ProceduralPattern:ADGC3ModuleTargetSideEffectRatchet

- Fixes C3 silent-write overcounting when ADG emits `writes_to` from a module node but emits `emits_side_effect` from an enclosed symbol back to that module as `dst_id`.
- Diagnostic query: compare C3 counts on `artifacts/adg/adg_indexed_<run_id>.sqlite` with `NOT EXISTS se.src_id = writer_id` versus `NOT EXISTS (se.src_id = writer_id OR se.dst_id = writer_id)`.
- Validation command: set `ADG_SNAPSHOT` to the released timestamped SQLite artifact, then run `python ops_scripts/ci/check_w4_silent_writes.py`; the gate should pass and tighten `ops_scripts/ci/baselines/wiring_silent_writes_ratchet.json` only when the revised count is below the previous floor.
- Guard: do not instrument product modules solely to clear C3 when the side-effect edge already targets the writer module; fix the gate semantics or extractor edge shape instead.
- Discovered: 2026-07-05; validated: 2026-07-05 against `adg_indexed_07042026_2305.sqlite`.
