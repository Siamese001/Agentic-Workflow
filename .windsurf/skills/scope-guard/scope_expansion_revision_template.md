# Phase Revision Artifact — Scope Expansion

## Trigger

Scope expansion detected during phase execution. Decontamination completed.
This artifact documents the expansion and authorizes a revised scope before continuing.

---

## Original Scope Declaration

- **Phase**: N
- **Original N**: _
- **Original declared files**:
  1. `path/to/file1`
  2. `path/to/file2`

---

## Expansion Event

- **Detected at**: Wave N / Step N
- **Unexpected files found**:
  1. `path/to/unexpected_file` — reason it appeared: _
- **Decontamination executed**: YES / NO
- **Decontamination evidence**: see evidence file section "_"

---

## Revised Scope Declaration

- **Revised N**: _
- **Revised declared files**:
  1. `path/to/file1`   [original]
  2. `path/to/file2`   [original]
  3. `path/to/file3`   [added — justification: _]

**Justification for expansion** (required):
> _

---

## Authorization

- Revision documented in evidence file: `docs/reports/plans/<phase_evidence_file>.md`
- Proceeding only after this artifact is committed or recorded in evidence.

---

## Next Step

Resume phase execution with revised scope. Do NOT re-run completed waves.
